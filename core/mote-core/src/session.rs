//! Cycle de vie d'une session : créée, démarrée, arrêtée. Deux files bornées et deux threads : l'encodage des
//! paires retenues, puis l'écriture de tout ce que l'hôte pousse. Toutes les méthodes prennent `&self` et sont
//! appelables depuis n'importe quel thread (SPEC-fdb8).

use std::collections::VecDeque;
use std::fmt;
use std::sync::atomic::{AtomicU32, AtomicU64, Ordering};
use std::sync::mpsc::{self, Receiver, RecvTimeoutError, SyncSender, TrySendError};
use std::sync::{Arc, Mutex, MutexGuard};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use mote_net::{Net, NetConfig};

use crate::clock;
use crate::mcap_writer::{session_id, McapWriter};
use crate::selection::{sharpness, Selector};
use crate::stages::{Encoder, JpegEncoder, Live, RawEncoder, SessionStart, Writer};
use crate::types::*;

/// Paires retenues en attente d'encodage. Une paire RGBA de 1280x1280 pèse environ 13 Mo : la file en garde 4,
/// au-delà la paire est perdue et comptée (NFR-02).
pub const ENCODE_QUEUE_CAPACITY: usize = 4;
/// Messages en attente d'écriture (poses, profondeur, événements, paires encodées).
pub const WRITE_QUEUE_CAPACITY: usize = 1024;
/// Événements en attente de `poll_event` ; au-delà, les plus anciens sont oubliés.
pub const EVENT_QUEUE_CAPACITY: usize = 256;
/// Période de `/stats` et de la fermeture forcée du chunk en cours : borne ce qu'une mort du processus fait perdre.
pub const FLUSH_PERIOD: Duration = Duration::from_secs(1);

#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    InvalidArg,
    Io,
    /// File pleine, donnée perdue.
    Busy,
    /// Appel hors séquence.
    State,
    /// Échec interne (initialisation de l'encodeur).
    Internal,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        fmt::Debug::fmt(self, f)
    }
}

impl std::error::Error for Error {}

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Default)]
struct Counters {
    pairs_pushed: AtomicU64,
    pairs_kept: AtomicU64,
    pairs_dropped: AtomicU64,
    bytes_written: AtomicU64,
    next_pair_id: AtomicU64,
    /// Moyenne glissante du temps d'encodage d'une paire, en ms (bits d'un f32).
    encode_ms_avg: AtomicU32,
}

struct Shared {
    counters: Counters,
    events: Mutex<VecDeque<Event>>,
    write_error: Mutex<bool>,
    /// Client du flux live, de `start` à la destruction du core : il sert le rattrapage après `stop`.
    net: Mutex<Option<Arc<Net>>>,
}

impl Shared {
    fn stats(&self) -> Stats {
        let c = &self.counters;
        let net = lock(&self.net)
            .as_ref()
            .map(|n| n.stats())
            .unwrap_or_default();
        Stats {
            t_ns: clock::now_ns(),
            pairs_pushed: c.pairs_pushed.load(Ordering::Relaxed),
            pairs_kept: c.pairs_kept.load(Ordering::Relaxed),
            pairs_dropped: c.pairs_dropped.load(Ordering::Relaxed),
            bytes_written: c.bytes_written.load(Ordering::Relaxed),
            encode_ms_avg: f32::from_bits(c.encode_ms_avg.load(Ordering::Relaxed)),
            bytes_sent: net.bytes_sent,
            net_mbps: net.net_mbps,
            live_queue_fill: net.live_queue_fill,
            net_connected: net.connected,
        }
    }

    /// Remet un événement à l'hôte (`mote_poll_event`) ; au-delà de la capacité, les plus anciens sont oubliés.
    fn notify(&self, e: Event) {
        let mut q = lock(&self.events);
        if q.len() == EVENT_QUEUE_CAPACITY {
            q.pop_front();
        }
        q.push_back(e);
    }
}

struct Running {
    pairs: SyncSender<Pair>,
    records: SyncSender<Record>,
    threads: [JoinHandle<()>; 2],
}

enum State {
    Created {
        encoder: Box<dyn Encoder>,
        writer: Box<dyn Writer>,
    },
    Running(Running),
    Stopped,
}

pub struct Core {
    config: Config,
    selector: Mutex<Selector>,
    state: Mutex<State>,
    shared: Arc<Shared>,
}

/// Un thread de l'hôte qui panique en tenant un verrou ne doit pas rendre le core inutilisable.
fn lock<T>(m: &Mutex<T>) -> MutexGuard<'_, T> {
    m.lock().unwrap_or_else(|e| e.into_inner())
}

impl Core {
    /// Session avec les étages par défaut : JPEG ou RGBA brut selon `codec`, fichier MCAP dans `local_dir`.
    pub fn new(config: Config) -> Result<Self> {
        let encoder: Box<dyn Encoder> = match config.codec {
            CODEC_JPEG => {
                Box::new(JpegEncoder::new(config.jpeg_quality).map_err(|_| Error::Internal)?)
            }
            CODEC_RAW_RGBA => Box::new(RawEncoder),
            _ => return Err(Error::InvalidArg),
        };
        Ok(Self::with_stages(
            config,
            encoder,
            Box::new(McapWriter::new()),
        ))
    }

    pub fn with_stages(config: Config, encoder: Box<dyn Encoder>, writer: Box<dyn Writer>) -> Self {
        Core {
            selector: Mutex::new(Selector::new(&config)),
            config,
            state: Mutex::new(State::Created { encoder, writer }),
            shared: Arc::new(Shared {
                counters: Counters::default(),
                events: Mutex::new(VecDeque::new()),
                write_error: Mutex::new(false),
                net: Mutex::new(None),
            }),
        }
    }

    pub fn config(&self) -> &Config {
        &self.config
    }

    /// Crée le répertoire local et lance les threads d'encodage et d'écriture.
    pub fn start(&self) -> Result<()> {
        let mut state = lock(&self.state);
        if !matches!(*state, State::Created { .. }) {
            return Err(Error::State);
        }
        std::fs::create_dir_all(&self.config.local_dir).map_err(|_| Error::Io)?;
        let State::Created {
            encoder,
            mut writer,
        } = std::mem::replace(&mut *state, State::Stopped)
        else {
            unreachable!()
        };
        let start_t_ns = clock::now_ns();
        let start_unix_ns = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_or(0, |d| d.as_nanos() as i64);
        let id = session_id(start_unix_ns);
        let path = self.config.local_dir.join(format!("{id}.mcap"));
        let live = self.start_net(&id, &path);
        let session = SessionStart {
            id,
            start_unix_ns,
            start_t_ns,
            path,
            live,
        };
        // Un échec d'ouverture laisse la session arrêtée : un contexte par session.
        if writer.open(&self.config, session).is_err() {
            if let Some(net) = lock(&self.shared.net).take() {
                net.close();
            }
            return Err(Error::Io);
        }
        let (pairs, pairs_rx) = mpsc::sync_channel(ENCODE_QUEUE_CAPACITY);
        let (records, records_rx) = mpsc::sync_channel(WRITE_QUEUE_CAPACITY);
        let encode = {
            let (shared, records) = (self.shared.clone(), records.clone());
            thread::Builder::new()
                .name("mote-encode".into())
                .spawn(move || encode_loop(encoder, pairs_rx, records, &shared))
                .map_err(|_| Error::Io)?
        };
        let write = {
            let shared = self.shared.clone();
            thread::Builder::new()
                .name("mote-write".into())
                .spawn(move || write_loop(writer, records_rx, &shared))
                .map_err(|_| Error::Io)?
        };
        *state = State::Running(Running {
            pairs,
            records,
            threads: [encode, write],
        });
        Ok(())
    }

    /// Démarre le client du flux live si `server_addr` est configuré. Ses événements vont à l'hôte et, par un
    /// canal, à l'écriture de `/events`.
    fn start_net(&self, session_id: &str, path: &std::path::Path) -> Option<Live> {
        let addr = self.config.server_addr.clone()?;
        let n = &self.config.net;
        let cfg = NetConfig {
            addr,
            auth_token: self.config.auth_token.clone().unwrap_or_default(),
            session_id: session_id.to_owned(),
            schema_version: 1,
            mcap_path: path.to_owned(),
            live_queue_bytes: n.live_queue_bytes,
            connect_timeout: n.connect_timeout,
            reconnect_min: n.reconnect_min,
            reconnect_max: n.reconnect_max,
            resend_batch: n.resend_batch,
        };
        let (tx, rx) = mpsc::channel::<Event>();
        let tx = Mutex::new(tx);
        let shared = self.shared.clone();
        let sink = Arc::new(move |kind: u32, detail: String| {
            let e = Event {
                t_ns: clock::now_ns(),
                kind,
                detail,
            };
            shared.notify(e.clone());
            let _ = lock(&tx).send(e);
        });
        let net = Arc::new(Net::start(cfg, sink));
        *lock(&self.shared.net) = Some(net.clone());
        let shared = self.shared.clone();
        Some(Live {
            net,
            events: rx,
            notify: Arc::new(move |e| shared.notify(e)),
        })
    }

    /// Vide les files, attend la fin de l'écriture. Une erreur d'écriture survenue pendant la session sort ici.
    /// Le flux live continue de servir le rattrapage jusqu'à la destruction du core.
    pub fn stop(&self) -> Result<()> {
        let running = {
            let mut state = lock(&self.state);
            if !matches!(*state, State::Running(_)) {
                return Err(Error::State);
            }
            let State::Running(r) = std::mem::replace(&mut *state, State::Stopped) else {
                unreachable!()
            };
            r
        };
        let Running {
            pairs,
            records,
            threads,
        } = running;
        // L'encodeur garde son propre émetteur vers l'écriture : fermer les paires d'abord, puis l'écriture se
        // termine quand l'encodeur a fini.
        drop(pairs);
        drop(records);
        for t in threads {
            if t.join().is_err() {
                *lock(&self.shared.write_error) = true;
            }
        }
        if *lock(&self.shared.write_error) {
            return Err(Error::Io);
        }
        Ok(())
    }

    /// Paire appariée par l'hôte. La sélection lit les buffers de l'hôte ; seule une paire retenue est copiée et
    /// mise en file d'encodage. Renvoie `true` si elle l'est.
    pub fn push_pair(&self, left: &FrameView, right: &FrameView) -> Result<bool> {
        let sender = self.pairs_sender()?;
        let c = &self.shared.counters;
        c.pairs_pushed.fetch_add(1, Ordering::Relaxed);
        let dt = (left.t_ns - right.t_ns).abs();
        if self.config.pair_max_dt_ns > 0 && dt > self.config.pair_max_dt_ns {
            self.emit(EVENT_PAIR_REJECTED_UNSYNC, format!("dt={dt}ns"));
            return Ok(false);
        }
        let (sl, sr) = (sharpness(left), sharpness(right));
        let pose = left.world_from_camera.map(|p| p.pose);
        // Le verrou couvre la décision et la mise en file : deux threads de l'hôte ne retiennent pas deux paires
        // contre la même référence.
        let mut selector = lock(&self.selector);
        if !selector.wants(pose.as_ref(), sl, sr) {
            return Ok(false);
        }
        let id = c.next_pair_id.fetch_add(1, Ordering::Relaxed);
        let pair = Pair {
            id,
            left: left.to_frame(sl),
            right: right.to_frame(sr),
        };
        match sender.try_send(pair) {
            Ok(()) => {
                selector.kept(pose.as_ref());
                c.pairs_kept.fetch_add(1, Ordering::Relaxed);
                Ok(true)
            }
            Err(TrySendError::Full(p)) => {
                drop(selector);
                c.pairs_dropped.fetch_add(1, Ordering::Relaxed);
                self.emit(EVENT_PAIR_DROPPED_BUSY, format!("t_ns={}", p.left.t_ns));
                Err(Error::Busy)
            }
            Err(TrySendError::Disconnected(_)) => Err(Error::State),
        }
    }

    pub fn set_intrinsics(&self, i: Intrinsics) -> Result<()> {
        self.record(Record::Intrinsics(i))
    }

    pub fn push_hmd_pose(&self, p: HmdPose) -> Result<()> {
        self.record(Record::HmdPose(p))
    }

    pub fn push_depth(&self, d: Depth) -> Result<()> {
        self.record(Record::Depth(d))
    }

    /// Événement de l'hôte (tracking, recentrage) : écrit dans la session.
    pub fn push_event(&self, kind: u32, detail: String) -> Result<()> {
        self.record(Record::Event(Event {
            t_ns: clock::now_ns(),
            kind,
            detail,
        }))
    }

    pub fn stats(&self) -> Stats {
        self.shared.stats()
    }

    /// Événement émis par le core : remis à l'hôte par `poll_event` et écrit dans `/events` (au mieux : une file
    /// d'écriture pleine le perd du fichier, pas de l'hôte).
    fn emit(&self, kind: u32, detail: String) {
        let e = Event {
            t_ns: clock::now_ns(),
            kind,
            detail,
        };
        self.shared.notify(e.clone());
        let _ = self.record(Record::Event(e));
    }

    /// Prochain événement émis par le core, le plus ancien d'abord.
    pub fn poll_event(&self) -> Option<Event> {
        lock(&self.shared.events).pop_front()
    }

    fn pairs_sender(&self) -> Result<SyncSender<Pair>> {
        match &*lock(&self.state) {
            State::Running(r) => Ok(r.pairs.clone()),
            _ => Err(Error::State),
        }
    }

    fn record(&self, r: Record) -> Result<()> {
        let sender = match &*lock(&self.state) {
            State::Running(run) => run.records.clone(),
            _ => return Err(Error::State),
        };
        sender.try_send(r).map_err(|e| match e {
            TrySendError::Full(_) => Error::Busy,
            TrySendError::Disconnected(_) => Error::State,
        })
    }
}

impl Drop for Core {
    fn drop(&mut self) {
        let _ = self.stop();
        if let Some(net) = lock(&self.shared.net).take() {
            net.close();
        }
    }
}

fn encode_loop(
    mut encoder: Box<dyn Encoder>,
    pairs: Receiver<Pair>,
    out: SyncSender<Record>,
    shared: &Shared,
) {
    let avg = &shared.counters.encode_ms_avg;
    for pair in pairs {
        let t0 = Instant::now();
        let encoded = encoder.encode(pair);
        let ms = t0.elapsed().as_secs_f32() * 1e3;
        let prev = f32::from_bits(avg.load(Ordering::Relaxed));
        let next = if prev == 0.0 {
            ms
        } else {
            0.9 * prev + 0.1 * ms
        };
        avg.store(next.to_bits(), Ordering::Relaxed);
        // Envoi bloquant : la contre-pression reste entre threads du core, jamais sur l'hôte.
        if out.send(Record::Pair(Box::new(encoded))).is_err() {
            return;
        }
    }
}

/// Écrit les records dans l'ordre d'arrivée ; chaque `FLUSH_PERIOD`, un `/stats` puis la fermeture du chunk en
/// cours. À l'arrêt, un dernier `/stats` puis `finish`. Après une erreur, plus rien n'est écrit et `stop` la renvoie.
fn write_loop(mut writer: Box<dyn Writer>, records: Receiver<Record>, shared: &Shared) {
    let mut ok = true;
    let mut last_flush = Instant::now();
    loop {
        match records.recv_timeout(FLUSH_PERIOD.saturating_sub(last_flush.elapsed())) {
            Ok(r) if ok => ok = writer.write(r).is_ok(),
            Ok(_) | Err(RecvTimeoutError::Timeout) => {}
            Err(RecvTimeoutError::Disconnected) => break,
        }
        if ok && last_flush.elapsed() >= FLUSH_PERIOD {
            ok = writer.write(Record::Stats(shared.stats())).is_ok() && writer.flush().is_ok();
            last_flush = Instant::now();
        }
        shared
            .counters
            .bytes_written
            .store(writer.bytes_written(), Ordering::Relaxed);
    }
    ok = ok && writer.write(Record::Stats(shared.stats())).is_ok() && writer.finish().is_ok();
    shared
        .counters
        .bytes_written
        .store(writer.bytes_written(), Ordering::Relaxed);
    if !ok {
        *lock(&shared.write_error) = true;
    }
}
