//! SP-4 (jetable) : le minimum du futur mote-core, pour mesurer sur le Quest 3S ce que coûte le chemin nominal.
//!
//! L'hôte Unity pousse des paires RGBA (ADR-7a16 : tout en push, aucun callback). Le core copie la paire, la met en
//! file, l'encode en JPEG (libjpeg-turbo, ADR-86d6) sur ses threads et l'écrit dans un MCAP (ADR-5955) : canaux
//! `/cam/left/frame` et `/cam/right/frame`, messages `mote.v1.ImageFrame`, chunks zstd. Il chronomètre chaque étape et
//! le temps CPU de ses propres threads.
//!
//! API C : `sp4_open`, `sp4_push_pair`, `sp4_stats_json`, `sp4_close`, `sp4_bench_encode`, `sp4_process_cpu_s`.
//! Statuts : 0 OK,
//! 1 argument invalide, 2 E/S, 3 file pleine (paire perdue), 4 hors séquence, 5 interne.

pub mod v1 {
    include!(concat!(env!("OUT_DIR"), "/mote.v1.rs"));
}

use std::collections::BTreeMap;
use std::ffi::{c_char, CStr};
use std::fs::File;
use std::io::BufWriter;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::mpsc::{sync_channel, Receiver, SyncSender, TrySendError};
use std::sync::{Arc, Mutex};
use std::thread::JoinHandle;
use std::time::Instant;

use prost::Message;

pub const OK: i32 = 0;
pub const ERR_INVALID_ARG: i32 = 1;
pub const ERR_IO: i32 = 2;
pub const ERR_BUSY: i32 = 3;
pub const ERR_STATE: i32 = 4;
pub const ERR_INTERNAL: i32 = 5;

static FDS: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/mote_v1.fds"));

/// Temps CPU du thread appelant (s). Linux et Android ; 0 ailleurs (tests sur PC Windows).
pub fn thread_cpu_s() -> f64 {
    cpu_clock(
        #[cfg(unix)]
        libc::CLOCK_THREAD_CPUTIME_ID,
        #[cfg(not(unix))]
        0,
    )
}

/// Temps CPU de tout le processus (s), Unity compris.
pub fn process_cpu_s() -> f64 {
    cpu_clock(
        #[cfg(unix)]
        libc::CLOCK_PROCESS_CPUTIME_ID,
        #[cfg(not(unix))]
        0,
    )
}

#[cfg(unix)]
fn cpu_clock(id: libc::clockid_t) -> f64 {
    let mut ts = libc::timespec { tv_sec: 0, tv_nsec: 0 };
    // SAFETY : ts est un timespec valide, possédé par cette fonction.
    if unsafe { libc::clock_gettime(id, &mut ts) } != 0 {
        return 0.0;
    }
    ts.tv_sec as f64 + ts.tv_nsec as f64 * 1e-9
}

#[cfg(not(unix))]
fn cpu_clock(_id: i32) -> f64 {
    0.0
}

/// Encode une image RGBA serrée (pas de marge de ligne) en JPEG.
pub fn encode_jpeg(rgba: &[u8], width: u32, height: u32, quality: i32) -> Result<Vec<u8>, String> {
    let mut c = turbojpeg::Compressor::new().map_err(|e| e.to_string())?;
    c.set_quality(quality).map_err(|e| e.to_string())?;
    c.set_subsamp(turbojpeg::Subsamp::Sub2x2).map_err(|e| e.to_string())?;
    let img = turbojpeg::Image {
        pixels: rgba,
        width: width as usize,
        pitch: width as usize * 4,
        height: height as usize,
        format: turbojpeg::PixelFormat::RGBA,
    };
    c.compress_to_vec(img).map_err(|e| e.to_string())
}

struct Job {
    pair_id: u64,
    t_ns: i64,
    width: u32,
    height: u32,
    left: Vec<u8>,
    right: Vec<u8>,
}

#[derive(Default)]
struct Stats {
    pushed: u64,
    encoded: u64,
    dropped: u64,
    errors: u64,
    push_ms: Vec<f32>,
    encode_ms: Vec<f32>,
    write_ms: Vec<f32>,
    jpeg_bytes: u64,
    jpeg_images: u64,
    core_cpu_s: f64,
    last_error: String,
}

struct Mcap {
    writer: mcap::Writer<BufWriter<File>>,
    channels: [u16; 2],
    seq: [u32; 2],
}

pub struct Sp4 {
    tx: Option<SyncSender<Job>>,
    workers: Vec<JoinHandle<()>>,
    stats: Arc<Mutex<Stats>>,
    mcap: Arc<Mutex<Option<Mcap>>>,
    next_pair: AtomicU64,
    t_open: Instant,
    cpu_open: f64,
    path: PathBuf,
}

fn pct(xs: &[f32], q: f64) -> f64 {
    if xs.is_empty() {
        return 0.0;
    }
    let mut v = xs.to_vec();
    v.sort_by(|a, b| a.total_cmp(b));
    v[((v.len() - 1) as f64 * q).round() as usize] as f64
}

fn mean(xs: &[f32]) -> f64 {
    if xs.is_empty() { 0.0 } else { xs.iter().map(|&x| x as f64).sum::<f64>() / xs.len() as f64 }
}

impl Sp4 {
    pub fn open(dir: PathBuf, quality: i32, threads: usize, queue_pairs: usize) -> Result<Sp4, String> {
        std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
        let path = dir.join(format!("sp4_{}.mcap", std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0)));
        let file = BufWriter::with_capacity(1 << 20, File::create(&path).map_err(|e| e.to_string())?);
        let mut writer = mcap::WriteOptions::new()
            .compression(Some(mcap::Compression::Zstd))
            .profile("")
            .create(file)
            .map_err(|e| e.to_string())?;
        let mut ch = |topic: &str, schema: &str| -> Result<u16, String> {
            let sid = writer.add_schema(schema, "protobuf", FDS).map_err(|e| e.to_string())?;
            writer.add_channel(sid, topic, "protobuf", &BTreeMap::new()).map_err(|e| e.to_string())
        };
        let channels = [ch("/cam/left/frame", "mote.v1.ImageFrame")?, ch("/cam/right/frame", "mote.v1.ImageFrame")?];
        let info_ch = ch("/session/info", "mote.v1.SessionInfo")?;
        let info = v1::SessionInfo {
            schema_version: 1,
            session_id: path.file_stem().map(|s| s.to_string_lossy().into_owned()).unwrap_or_default(),
            host_kind: "unity-sp4".into(),
            core_version: concat!("sp4core ", env!("CARGO_PKG_VERSION")).into(),
            config_json: format!(r#"{{"jpeg_quality":{quality},"threads":{threads},"queue_pairs":{queue_pairs}}}"#),
            ..Default::default()
        };
        writer
            .write_to_known_channel(
                &mcap::records::MessageHeader { channel_id: info_ch, sequence: 0, log_time: 0, publish_time: 0 },
                &info.encode_to_vec(),
            )
            .map_err(|e| e.to_string())?;

        let (tx, rx) = sync_channel::<Job>(queue_pairs.max(1));
        let rx = Arc::new(Mutex::new(rx));
        let stats = Arc::new(Mutex::new(Stats::default()));
        let mcap = Arc::new(Mutex::new(Some(Mcap { writer, channels, seq: [0, 0] })));
        let workers = (0..threads.max(1))
            .map(|k| {
                let (rx, stats, mcap) = (rx.clone(), stats.clone(), mcap.clone());
                std::thread::Builder::new()
                    .name(format!("sp4-enc-{k}"))
                    .spawn(move || worker(rx, stats, mcap, quality))
                    .expect("thread")
            })
            .collect();
        Ok(Sp4 { tx: Some(tx), workers, stats, mcap, next_pair: AtomicU64::new(0), t_open: Instant::now(),
                 cpu_open: process_cpu_s(), path })
    }

    /// Copie la paire (le buffer n'est lu que pendant l'appel) et la met en file. ERR_BUSY si la file est pleine.
    #[allow(clippy::too_many_arguments)]
    pub fn push_pair(&self, t_ns: i64, left: &[u8], right: &[u8], width: u32, height: u32, stride: u32) -> i32 {
        let Some(tx) = &self.tx else { return ERR_STATE };
        let row = width as usize * 4;
        let stride = if stride == 0 { row } else { stride as usize };
        let need = stride * (height as usize - 1) + row;
        if width == 0 || height == 0 || stride < row || left.len() < need || right.len() < need {
            return ERR_INVALID_ARG;
        }
        let t0 = Instant::now();
        let copy = |src: &[u8]| -> Vec<u8> {
            if stride == row {
                src[..row * height as usize].to_vec()
            } else {
                let mut v = Vec::with_capacity(row * height as usize);
                for y in 0..height as usize {
                    v.extend_from_slice(&src[y * stride..y * stride + row]);
                }
                v
            }
        };
        let job = Job {
            pair_id: self.next_pair.fetch_add(1, Ordering::Relaxed),
            t_ns, width, height, left: copy(left), right: copy(right),
        };
        let push_ms = t0.elapsed().as_secs_f32() * 1000.0;
        let r = tx.try_send(job);
        let mut s = self.stats.lock().unwrap();
        s.pushed += 1;
        s.push_ms.push(push_ms);
        match r {
            Ok(()) => OK,
            Err(TrySendError::Full(_)) => { s.dropped += 1; ERR_BUSY }
            Err(TrySendError::Disconnected(_)) => ERR_INTERNAL,
        }
    }

    pub fn stats_json(&self) -> String {
        let s = self.stats.lock().unwrap();
        let wall = self.t_open.elapsed().as_secs_f64();
        format!(
            concat!("{{\"wall_s\":{:.3},\"pairs_pushed\":{},\"pairs_encoded\":{},\"pairs_dropped\":{},\"errors\":{},",
                    "\"push_ms_avg\":{:.3},\"push_ms_max\":{:.3},\"encode_ms_avg\":{:.3},\"encode_ms_p50\":{:.3},",
                    "\"encode_ms_p95\":{:.3},\"encode_ms_max\":{:.3},\"write_ms_avg\":{:.3},\"jpeg_kb_avg\":{:.1},",
                    "\"core_cpu_s\":{:.3},\"process_cpu_s\":{:.3},\"mcap\":\"{}\",\"last_error\":\"{}\"}}"),
            wall, s.pushed, s.encoded, s.dropped, s.errors,
            mean(&s.push_ms), pct(&s.push_ms, 1.0), mean(&s.encode_ms), pct(&s.encode_ms, 0.5),
            pct(&s.encode_ms, 0.95), pct(&s.encode_ms, 1.0), mean(&s.write_ms),
            if s.jpeg_images > 0 { s.jpeg_bytes as f64 / s.jpeg_images as f64 / 1024.0 } else { 0.0 },
            s.core_cpu_s, process_cpu_s() - self.cpu_open,
            self.path.display().to_string().replace('\\', "/"), s.last_error.replace('"', "'"),
        )
    }

    /// Vide la file, termine le MCAP (canal /session/end compris). Renvoie le chemin du fichier.
    pub fn close(&mut self) -> Result<PathBuf, String> {
        self.tx.take();
        for w in self.workers.drain(..) {
            w.join().map_err(|_| "thread d'encodage en panique".to_string())?;
        }
        let Some(mut m) = self.mcap.lock().unwrap().take() else { return Err("déjà fermé".into()) };
        let sid = m.writer.add_schema("mote.v1.SessionEnd", "protobuf", FDS).map_err(|e| e.to_string())?;
        let end_ch = m.writer.add_channel(sid, "/session/end", "protobuf", &BTreeMap::new()).map_err(|e| e.to_string())?;
        let end = v1::SessionEnd {
            channels: ["/cam/left/frame", "/cam/right/frame"].iter().zip(m.seq)
                .filter(|(_, n)| *n > 0)
                .map(|(c, n)| v1::ChannelEnd { channel: c.to_string(), last_seq: n as u64 - 1 })
                .collect(),
        };
        m.writer
            .write_to_known_channel(
                &mcap::records::MessageHeader { channel_id: end_ch, sequence: 0, log_time: 0, publish_time: 0 },
                &end.encode_to_vec(),
            )
            .map_err(|e| e.to_string())?;
        m.writer.finish().map_err(|e| e.to_string())?;
        Ok(self.path.clone())
    }
}

fn worker(rx: Arc<Mutex<Receiver<Job>>>, stats: Arc<Mutex<Stats>>, mcap: Arc<Mutex<Option<Mcap>>>, quality: i32) {
    loop {
        let job = match rx.lock().unwrap().recv() {
            Ok(j) => j,
            Err(_) => return, // émetteur fermé : fin
        };
        let cpu0 = thread_cpu_s();
        let mut enc_ms = [0f32; 2];
        let mut wr_ms = [0f32; 2];
        let mut bytes = 0u64;
        let mut err = None;
        for (eye, rgba) in [&job.left, &job.right].into_iter().enumerate() {
            let t0 = Instant::now();
            let jpeg = match encode_jpeg(rgba, job.width, job.height, quality) {
                Ok(j) => j,
                Err(e) => { err = Some(e); break; }
            };
            enc_ms[eye] = t0.elapsed().as_secs_f32() * 1000.0;
            bytes += jpeg.len() as u64;
            let msg = v1::ImageFrame {
                pair_id: job.pair_id, t_ns: job.t_ns, width: job.width, height: job.height,
                codec: v1::ImageCodec::Jpeg as i32, data: jpeg, ..Default::default()
            }
            .encode_to_vec();
            let t1 = Instant::now();
            let mut g = mcap.lock().unwrap();
            if let Some(m) = g.as_mut() {
                let header = mcap::records::MessageHeader {
                    channel_id: m.channels[eye], sequence: m.seq[eye],
                    log_time: job.t_ns.max(0) as u64, publish_time: job.t_ns.max(0) as u64,
                };
                if let Err(e) = m.writer.write_to_known_channel(&header, &msg) {
                    err = Some(e.to_string());
                    break;
                }
                m.seq[eye] += 1;
            }
            drop(g);
            wr_ms[eye] = t1.elapsed().as_secs_f32() * 1000.0;
        }
        let cpu = thread_cpu_s() - cpu0;
        let mut s = stats.lock().unwrap();
        s.core_cpu_s += cpu;
        match err {
            Some(e) => { s.errors += 1; s.last_error = e; }
            None => {
                s.encoded += 1;
                s.encode_ms.extend_from_slice(&enc_ms);
                s.write_ms.extend_from_slice(&wr_ms);
                s.jpeg_bytes += bytes;
                s.jpeg_images += 2;
            }
        }
    }
}

/// Image de test : dégradés et bruit, pour un temps d'encodage proche d'une vraie scène.
pub fn synthetic_rgba(width: u32, height: u32, seed: u32) -> Vec<u8> {
    let mut v = Vec::with_capacity((width * height * 4) as usize);
    let mut x = seed.wrapping_mul(2_654_435_761).wrapping_add(1);
    for j in 0..height {
        for i in 0..width {
            x ^= x << 13; x ^= x >> 17; x ^= x << 5;
            let n = (x & 31) as u32;
            v.extend_from_slice(&[((i * 255 / width) + n) as u8, ((j * 255 / height) + n) as u8,
                                  (((i + j) & 255) as u32 / 2 + n) as u8, 255]);
        }
    }
    v
}

// ------------------------------------------------------------------------------------------------ API C

fn write_cstr(s: &str, buf: *mut c_char, cap: usize) -> i32 {
    let bytes = s.as_bytes();
    if !buf.is_null() && cap > 0 {
        let n = bytes.len().min(cap - 1);
        // SAFETY : l'appelant garantit `cap` octets inscriptibles à `buf`.
        unsafe {
            std::ptr::copy_nonoverlapping(bytes.as_ptr(), buf as *mut u8, n);
            *buf.add(n) = 0;
        }
    }
    bytes.len() as i32
}

/// Ouvre une session : `dir` (UTF-8) reçoit `sp4_<unix>.mcap`. NULL en cas d'échec.
#[no_mangle]
pub extern "C" fn sp4_open(dir: *const c_char, jpeg_quality: u32, threads: u32, queue_pairs: u32) -> *mut Sp4 {
    if dir.is_null() {
        return std::ptr::null_mut();
    }
    // SAFETY : chaîne C terminée par zéro fournie par l'hôte.
    let dir = unsafe { CStr::from_ptr(dir) }.to_string_lossy().into_owned();
    let q = if jpeg_quality == 0 { 90 } else { jpeg_quality as i32 };
    match Sp4::open(PathBuf::from(dir), q, threads.max(1) as usize, queue_pairs.max(1) as usize) {
        Ok(s) => Box::into_raw(Box::new(s)),
        Err(_) => std::ptr::null_mut(),
    }
}

/// Pousse une paire RGBA8888. `stride` 0 = lignes serrées. Les buffers ne sont lus que pendant l'appel.
#[no_mangle]
pub extern "C" fn sp4_push_pair(ctx: *mut Sp4, t_ns: i64, left: *const u8, right: *const u8, width: u32,
                                height: u32, stride: u32) -> i32 {
    if ctx.is_null() || left.is_null() || right.is_null() || width == 0 || height == 0 {
        return ERR_INVALID_ARG;
    }
    let row = if stride == 0 { width * 4 } else { stride } as usize;
    let len = row * height as usize;
    // SAFETY : l'hôte garantit `stride * height` octets lisibles par buffer pendant l'appel ; ctx vient de sp4_open.
    let (l, r, s) = unsafe { (std::slice::from_raw_parts(left, len), std::slice::from_raw_parts(right, len), &*ctx) };
    s.push_pair(t_ns, l, r, width, height, stride)
}

/// Statistiques en JSON dans `buf` (`cap` octets, terminé par zéro). Renvoie la longueur complète du JSON.
#[no_mangle]
pub extern "C" fn sp4_stats_json(ctx: *mut Sp4, buf: *mut c_char, cap: u32) -> i32 {
    if ctx.is_null() {
        return -ERR_INVALID_ARG;
    }
    // SAFETY : ctx vient de sp4_open et n'est pas encore fermé.
    write_cstr(&unsafe { &*ctx }.stats_json(), buf, cap as usize)
}

/// Termine le MCAP et libère le contexte. Écrit les statistiques finales dans `buf` si non NULL.
#[no_mangle]
pub extern "C" fn sp4_close(ctx: *mut Sp4, buf: *mut c_char, cap: u32) -> i32 {
    if ctx.is_null() {
        return ERR_INVALID_ARG;
    }
    // SAFETY : ctx vient de sp4_open ; on en reprend la propriété.
    let mut s = unsafe { Box::from_raw(ctx) };
    let r = s.close();
    let json = s.stats_json();
    write_cstr(&json, buf, cap as usize);
    match r { Ok(_) => OK, Err(_) => ERR_IO }
}

/// Temps CPU cumulé de tout le processus (s), Unity compris : la sonde en tire la charge pendant chaque phase.
#[no_mangle]
pub extern "C" fn sp4_process_cpu_s() -> f64 {
    process_cpu_s()
}

/// Encodage pur, sur le thread appelant, de `n` images synthétiques : temps médian, p95 et taille moyenne en JSON.
#[no_mangle]
pub extern "C" fn sp4_bench_encode(width: u32, height: u32, n: u32, jpeg_quality: u32, buf: *mut c_char,
                                   cap: u32) -> i32 {
    let q = if jpeg_quality == 0 { 90 } else { jpeg_quality as i32 };
    let imgs: Vec<Vec<u8>> = (0..4).map(|k| synthetic_rgba(width, height, k)).collect();
    let (mut ms, mut bytes) = (Vec::new(), 0usize);
    let cpu0 = thread_cpu_s();
    for k in 0..n.max(1) as usize {
        let t0 = Instant::now();
        match encode_jpeg(&imgs[k % 4], width, height, q) {
            Ok(j) => bytes += j.len(),
            Err(e) => return write_cstr(&format!("{{\"error\":\"{}\"}}", e.replace('"', "'")), buf, cap as usize),
        }
        ms.push(t0.elapsed().as_secs_f32() * 1000.0);
    }
    let json = format!(
        "{{\"width\":{width},\"height\":{height},\"n\":{},\"quality\":{q},\"ms_p50\":{:.3},\"ms_p95\":{:.3},\"ms_avg\":{:.3},\"kb_avg\":{:.1},\"cpu_s\":{:.3}}}",
        ms.len(), pct(&ms, 0.5), pct(&ms, 0.95), mean(&ms), bytes as f64 / ms.len() as f64 / 1024.0,
        thread_cpu_s() - cpu0);
    write_cstr(&json, buf, cap as usize)
}
