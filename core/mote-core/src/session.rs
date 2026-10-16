//! Cycle de vie d'une session : créée, démarrée, arrêtée. Deux files bornées et deux threads : l'encodage des
//! paires retenues, puis l'écriture de tout ce que l'hôte pousse. Toutes les méthodes prennent `&self` et sont
//! appelables depuis n'importe quel thread (SPEC-fdb8).

use std::collections::VecDeque;
use std::fmt;
use std::sync::atomic::{AtomicU32, AtomicU64, Ordering};
use std::sync::mpsc::{self, Receiver, SyncSender, TrySendError};
use std::sync::{Arc, Mutex, MutexGuard};
use std::thread::{self, JoinHandle};
use std::time::Instant;

use crate::clock;
use crate::stages::{Encoder, NullWriter, RawEncoder, Writer};
use crate::types::*;

/// Paires retenues en attente d'encodage. Une paire RGBA de 1280x1280 pèse environ 13 Mo : la file en garde 4,
/// au-delà la paire est perdue et comptée (NFR-02).
pub const ENCODE_QUEUE_CAPACITY: usize = 4;
/// Messages en attente d'écriture (poses, profondeur, événements, paires encodées).
pub const WRITE_QUEUE_CAPACITY: usize = 1024;
/// Événements en attente de `poll_event` ; au-delà, les plus anciens sont oubliés.
pub const EVENT_QUEUE_CAPACITY: usize = 256;

#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    InvalidArg,
    Io,
    /// File pleine, donnée perdue.
    Busy,
    /// Appel hors séquence.
    State,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        fmt::Debug::fmt(self, f)
    }
}

impl std::error::Error for Error {}

pub type Result<T> = std::result::Result<T, Error>;

/// Compteurs de supervision (`mote_get_stats`).
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Stats {
    pub pairs_pushed: u64,
    pub pairs_kept: u64,
    pub pairs_dropped: u64,
    pub bytes_written: u64,
    pub bytes_sent: u64,
    pub net_mbps: f32,
    pub encode_ms_avg: f32,
    pub live_queue_fill: f32,
    pub net_connected: bool,
}

#[derive(Default)]
struct Counters {
    pairs_pushed: AtomicU64,
    pairs_kept: AtomicU64,
    pairs_dropped: AtomicU64,
    bytes_written: AtomicU64,
    /// Moyenne glissante du temps d'encodage d'une paire, en ms (bits d'un f32).
    encode_ms_avg: AtomicU32,
}

struct Shared {
    counters: Counters,
    events: Mutex<VecDeque<Event>>,
    write_error: Mutex<bool>,
}

impl Shared {
    fn emit(&self, kind: u32, detail: impl Into<String>) {
        let mut q = lock(&self.events);
        if q.len() == EVENT_QUEUE_CAPACITY {
            q.pop_front();
        }
        q.push_back(Event {
            t_ns: clock::now_ns(),
            kind,
            detail: detail.into(),
        });
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
    state: Mutex<State>,
    shared: Arc<Shared>,
}

/// Un thread de l'hôte qui panique en tenant un verrou ne doit pas rendre le core inutilisable.
fn lock<T>(m: &Mutex<T>) -> MutexGuard<'_, T> {
    m.lock().unwrap_or_else(|e| e.into_inner())
}

impl Core {
    /// Session avec les étages par défaut.
    pub fn new(config: Config) -> Self {
        Self::with_stages(config, Box::new(RawEncoder), Box::new(NullWriter))
    }

    pub fn with_stages(config: Config, encoder: Box<dyn Encoder>, writer: Box<dyn Writer>) -> Self {
        Core {
            config,
            state: Mutex::new(State::Created { encoder, writer }),
            shared: Arc::new(Shared {
                counters: Counters::default(),
                events: Mutex::new(VecDeque::new()),
                write_error: Mutex::new(false),
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
        let State::Created { encoder, writer } = std::mem::replace(&mut *state, State::Stopped)
        else {
            unreachable!()
        };
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

    /// Vide les files, attend la fin de l'écriture. Une erreur d'écriture survenue pendant la session sort ici.
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

    /// Paire appariée par l'hôte. Renvoie `true` si elle est retenue et mise en file d'encodage.
    pub fn push_pair(&self, left: Frame, right: Frame) -> Result<bool> {
        let sender = self.pairs_sender()?;
        let c = &self.shared.counters;
        c.pairs_pushed.fetch_add(1, Ordering::Relaxed);
        let dt = (left.t_ns - right.t_ns).abs();
        if self.config.pair_max_dt_ns > 0 && dt > self.config.pair_max_dt_ns {
            self.shared
                .emit(EVENT_PAIR_REJECTED_UNSYNC, format!("dt={dt}ns"));
            return Ok(false);
        }
        // Sélection des paires : WP-09. D'ici là, toute paire synchronisée est retenue.
        match sender.try_send(Pair { left, right }) {
            Ok(()) => {
                c.pairs_kept.fetch_add(1, Ordering::Relaxed);
                Ok(true)
            }
            Err(TrySendError::Full(p)) => {
                c.pairs_dropped.fetch_add(1, Ordering::Relaxed);
                self.shared
                    .emit(EVENT_PAIR_DROPPED_BUSY, format!("t_ns={}", p.left.t_ns));
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
        let c = &self.shared.counters;
        Stats {
            pairs_pushed: c.pairs_pushed.load(Ordering::Relaxed),
            pairs_kept: c.pairs_kept.load(Ordering::Relaxed),
            pairs_dropped: c.pairs_dropped.load(Ordering::Relaxed),
            bytes_written: c.bytes_written.load(Ordering::Relaxed),
            encode_ms_avg: f32::from_bits(c.encode_ms_avg.load(Ordering::Relaxed)),
            ..Stats::default()
        }
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
        if out.send(Record::Pair(encoded)).is_err() {
            return;
        }
    }
}

fn write_loop(mut writer: Box<dyn Writer>, records: Receiver<Record>, shared: &Shared) {
    let mut failed = false;
    for r in records {
        if failed {
            continue;
        }
        match writer.write(r) {
            Ok(n) => {
                shared
                    .counters
                    .bytes_written
                    .fetch_add(n, Ordering::Relaxed);
            }
            Err(_) => failed = true,
        }
    }
    if writer.finish().is_err() || failed {
        *lock(&shared.write_error) = true;
    }
}
