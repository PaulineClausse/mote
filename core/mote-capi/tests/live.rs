//! Critère de WP-14 (TASK-f326), de bout en bout : le core diffuse une session vers `mote ingest --listen` (Python,
//! pc/) à travers un proxy TCP qui coupe le réseau 10 s en cours de session. La session PC finale doit contenir
//! exactement les mêmes triplets (canal, seq, contenu) que le MCAP du casque.

mod common;

use std::collections::BTreeMap;
use std::ffi::CString;
use std::io::{Read, Write};
use std::net::{Shutdown, TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::ptr;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use common::*;
use mote::*;
use mote_proto::v1;
use mote_proto::Message as _;

const TOKEN: &str = "jeton-de-test";
/// Durée de la coupure exigée par le critère.
const CUT: Duration = Duration::from_secs(10);

fn free_port() -> u16 {
    TcpListener::bind("127.0.0.1:0")
        .unwrap()
        .local_addr()
        .unwrap()
        .port()
}

/// Proxy TCP entre le casque et le PC. Pendant une coupure, il cesse de relayer et garde les nouvelles connexions
/// sans les lire, comme un réseau qui ne transmet plus : l'émetteur finit par bloquer et sa file live déborde. À la
/// fin de la coupure, il ferme tout ce qui a été ouvert, et le casque se reconnecte.
struct Proxy {
    port: u16,
    cut: Arc<AtomicBool>,
    open: Arc<Mutex<Vec<TcpStream>>>,
}

impl Proxy {
    fn start(upstream: u16) -> Proxy {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let port = listener.local_addr().unwrap().port();
        let cut = Arc::new(AtomicBool::new(false));
        let open: Arc<Mutex<Vec<TcpStream>>> = Arc::default();
        let (c, o) = (cut.clone(), open.clone());
        thread::spawn(move || {
            for client in listener.incoming() {
                let Ok(client) = client else { continue };
                o.lock().unwrap().push(client.try_clone().unwrap());
                if c.load(Ordering::SeqCst) {
                    continue; // tenue ouverte, jamais lue
                }
                let Ok(server) = TcpStream::connect(("127.0.0.1", upstream)) else {
                    continue;
                };
                o.lock().unwrap().push(server.try_clone().unwrap());
                pipe(
                    client.try_clone().unwrap(),
                    server.try_clone().unwrap(),
                    c.clone(),
                );
                pipe(server, client, c.clone());
            }
        });
        Proxy { port, cut, open }
    }

    fn set_cut(&self, on: bool) {
        self.cut.store(on, Ordering::SeqCst);
        if !on {
            for s in self.open.lock().unwrap().drain(..) {
                let _ = s.shutdown(Shutdown::Both);
            }
        }
    }
}

fn pipe(mut from: TcpStream, mut to: TcpStream, cut: Arc<AtomicBool>) {
    thread::spawn(move || {
        let mut buf = vec![0u8; 1 << 16];
        loop {
            while cut.load(Ordering::SeqCst) {
                thread::sleep(Duration::from_millis(20));
            }
            let Ok(n) = from.read(&mut buf) else { break };
            if n == 0 || to.write_all(&buf[..n]).is_err() {
                break;
            }
        }
        let _ = to.shutdown(Shutdown::Both);
    });
}

/// `mote ingest --listen`, lancé par uv depuis pc/.
fn start_ingest(port: u16, dir: &Path) -> Option<Child> {
    let pc = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../pc");
    let child = Command::new("uv")
        .current_dir(&pc)
        .args(["run", "python", "-m", "mote", "ingest"])
        .arg("--listen")
        .arg(format!("127.0.0.1:{port}"))
        .args([
            "--token",
            TOKEN,
            "--resend-after",
            "0.5",
            "--idle-timeout",
            "120",
        ])
        .arg("--sessions")
        .arg(dir.join("sessions"))
        .arg("--out")
        .arg(dir.join("dataset"))
        .env("PYTHONUTF8", "1")
        .stdout(Stdio::null())
        .spawn()
        .ok()?;
    let t0 = Instant::now();
    while TcpStream::connect(("127.0.0.1", port)).is_err() {
        assert!(
            t0.elapsed() < Duration::from_secs(120),
            "mote ingest ne répond pas"
        );
        thread::sleep(Duration::from_millis(200));
    }
    Some(child)
}

/// Canal -> seq -> contenu, pour tout le fichier.
fn triples(path: &Path) -> BTreeMap<(String, u32), Vec<u8>> {
    let buf = std::fs::read(path).unwrap();
    mcap::MessageStream::new(&buf)
        .unwrap()
        .map(|m| {
            let m = m.unwrap();
            ((m.channel.topic.clone(), m.sequence), m.data.into_owned())
        })
        .collect()
}

fn only_mcap(dir: &Path) -> PathBuf {
    session_file(dir)
}

#[test]
fn coupure_de_10_s_et_session_pc_identique() {
    let dir = tmp("live");
    let ingest_port = free_port();
    let Some(mut ingest) = start_ingest(ingest_port, &dir) else {
        eprintln!("uv introuvable : test ignoré");
        return;
    };
    let proxy = Proxy::start(ingest_port);

    let local = dir.join("casque");
    let mut s = session(&local);
    let addr = CString::new(format!("127.0.0.1:{}", proxy.port)).unwrap();
    let token = CString::new(TOKEN).unwrap();
    s.cfg.server_addr = addr.as_ptr();
    s.cfg.auth_token = token.as_ptr();
    // Réglages du transport, ici serrés pour un test court : file live de 4 Kio, pour qu'elle déborde pendant
    // la coupure, et reconnexion rapide.
    s.cfg.live_queue_bytes = 4096;
    s.cfg.reconnect_min_ms = 100;
    s.cfg.reconnect_max_ms = 500;
    s.cfg.resend_batch_ms = 100;

    let px = vec![90u8; (W * H * 4) as usize];
    // Profondeur de 64 Kio par carte (deux cartes toutes les 100 ms) : assez pour remplir les tampons du système
    // pendant la coupure.
    let dpx = vec![7u8; 64 << 10];
    let dist = [0.0; 4];
    let mut ctx: *mut mote_ctx = ptr::null_mut();
    unsafe {
        assert_eq!(mote_create(&s.cfg, &mut ctx), mote_status::MOTE_OK);
        assert_eq!(mote_start(ctx), mote_status::MOTE_OK);
        for cam in 0..2 {
            assert_eq!(
                mote_set_intrinsics(ctx, &intrinsics(cam, &dist)),
                mote_status::MOTE_OK
            );
        }
        // Scan de 2 + 10 + 2 s : poses à 100 Hz, une paire et deux cartes de profondeur toutes les 100 ms.
        let t0 = Instant::now();
        let total = Duration::from_secs(2) + CUT + Duration::from_secs(2);
        let mut k: i64 = 0;
        let mut cut_done = false;
        while t0.elapsed() < total {
            let el = t0.elapsed();
            if !cut_done && el >= Duration::from_secs(2) && !proxy.cut.load(Ordering::SeqCst) {
                proxy.set_cut(true);
            }
            if el >= Duration::from_secs(2) + CUT && proxy.cut.load(Ordering::SeqCst) {
                proxy.set_cut(false);
                cut_done = true;
            }
            let t = mote_now_ns();
            assert_eq!(
                mote_push_hmd_pose(ctx, t, t, 1, 1, &pose(), 0),
                mote_status::MOTE_OK
            );
            if k % 10 == 0 {
                let mut kept = 0;
                let st = mote_push_pair(ctx, &frame(&px, t), &frame(&px, t), &mut kept);
                assert_eq!(st, mote_status::MOTE_OK);
                for eye in 0..2 {
                    assert_eq!(
                        mote_push_depth(ctx, &depth(eye, &dpx, t)),
                        mote_status::MOTE_OK
                    );
                }
            }
            k += 1;
            thread::sleep(Duration::from_millis(10));
        }
        assert!(cut_done, "la coupure n'a pas eu lieu");
        assert_eq!(mote_stop(ctx), mote_status::MOTE_OK);
        eprintln!("live : stop à {:.1} s", t0.elapsed().as_secs_f32());

        // Après stop, le casque continue de servir le rattrapage jusqu'à la session complète côté PC.
        let t1 = Instant::now();
        let status = loop {
            if let Some(st) = ingest.try_wait().unwrap() {
                break st;
            }
            assert!(
                t1.elapsed() < Duration::from_secs(60),
                "session PC incomplète après 60 s"
            );
            thread::sleep(Duration::from_millis(200));
        };
        assert!(status.success(), "mote ingest a échoué : {status}");
        eprintln!(
            "live : session PC complète {:.1} s après stop",
            t1.elapsed().as_secs_f32()
        );

        let mut events = Vec::new();
        let mut ev: mote_event = std::mem::zeroed();
        ev.struct_size = std::mem::size_of::<mote_event>() as u32;
        let mut has = 1;
        while has == 1 {
            assert_eq!(
                mote_poll_event(ctx, &mut ev, &mut has),
                mote_status::MOTE_OK
            );
            if has == 1 {
                let d = std::ffi::CStr::from_ptr(ev.detail.as_ptr())
                    .to_string_lossy()
                    .into_owned();
                events.push((ev.r#type, d));
            }
        }
        let t2 = Instant::now();
        mote_destroy(ctx);
        eprintln!("live : destroy en {:.1} s", t2.elapsed().as_secs_f32());

        // Coupure vue par le casque.
        assert!(
            events.iter().any(|(t, _)| *t == 7),
            "NET_DISCONNECTED attendu : {events:?}"
        );
        assert!(
            events.iter().filter(|(t, _)| *t == 8).count() >= 2,
            "deux NET_CONNECTED attendus"
        );
        // File live pleine pendant la coupure : seuls des images et des profondeurs ont été retirées.
        let dropped: Vec<&String> = events
            .iter()
            .filter(|(t, _)| *t == 6)
            .map(|(_, d)| d)
            .collect();
        assert!(
            !dropped.is_empty(),
            "la file live de 4 Kio aurait dû déborder pendant 10 s de coupure"
        );
        for d in &dropped {
            let ch = d.split(' ').next().unwrap();
            assert!(
                matches!(
                    ch,
                    "/cam/left/frame" | "/cam/right/frame" | "/depth/left" | "/depth/right"
                ),
                "LIVE_DROPPED sur {ch}"
            );
        }
    }

    let source = triples(&only_mcap(&local));
    let received = triples(&only_mcap(&dir.join("sessions")));
    assert_eq!(source.len(), received.len(), "nombre de messages");
    let differ: Vec<_> = source
        .iter()
        .filter(|(k, v)| received.get(*k) != Some(v))
        .map(|(k, _)| k)
        .take(5)
        .collect();
    assert!(
        differ.is_empty(),
        "triplets différents ou absents côté PC : {differ:?}"
    );
    // Le flux a bien porté des retraits, rattrapés depuis le fichier local.
    let ev_bytes: Vec<&Vec<u8>> = source
        .iter()
        .filter(|((t, _), _)| t == "/events")
        .map(|(_, v)| v)
        .collect();
    assert!(ev_bytes
        .iter()
        .any(|b| v1::Event::decode(&b[..]).unwrap().r#type == 6));
    let _ = std::fs::remove_dir_all(dir);
}
