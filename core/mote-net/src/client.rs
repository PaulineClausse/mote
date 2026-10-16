//! Client du flux live (SPEC-9df2) : le casque ouvre la connexion, envoie `Hello`, puis les trames de la file live ;
//! il lit les `Control` du PC et sert les demandes de rattrapage depuis le fichier MCAP local, en priorité inférieure
//! au live. En cas de coupure, il retente avec un délai croissant et renvoie `Hello` avec le même identifiant de
//! session. Le scan continue pendant la coupure : la file live se vide de ses images les plus anciennes.

use std::collections::{BTreeMap, BTreeSet, VecDeque};
use std::io::{self, BufWriter, Read, Write};
use std::net::{Shutdown, TcpStream, ToSocketAddrs};
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering};
use std::sync::{Arc, Condvar, Mutex, MutexGuard};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use mote_proto::v1::{self, control, envelope::Body};
use mote_proto::Message;

use crate::frame::{body_from_bytes, envelope, write_frame, MAX_FRAME};
use crate::queue::{Item, LiveQueue};

/// `EventType` de mote.v1 émis par le client.
pub const EVENT_LIVE_DROPPED: u32 = 6;
pub const EVENT_NET_DISCONNECTED: u32 = 7;
pub const EVENT_NET_CONNECTED: u32 = 8;

/// Réglages du transport. Les défauts viennent de SP-5 (Wi-Fi 6 en 5 GHz, 200 Mbit/s en moyenne, 154 au minimum sur
/// 10 s) et ne valent que pour un réseau comparable : chaque champ se règle par `mote_config`.
#[derive(Clone, Debug)]
pub struct NetConfig {
    /// « hôte:port » du PC.
    pub addr: String,
    pub auth_token: String,
    pub session_id: String,
    pub schema_version: u32,
    /// Fichier MCAP local, source du rattrapage.
    pub mcap_path: PathBuf,
    /// Borne de la file live, en octets.
    pub live_queue_bytes: usize,
    pub connect_timeout: Duration,
    /// Délai avant la première tentative de reconnexion, doublé à chaque échec jusqu'à `reconnect_max`.
    pub reconnect_min: Duration,
    pub reconnect_max: Duration,
    /// Regroupement des demandes de rattrapage avant une relecture du fichier.
    pub resend_batch: Duration,
}

impl NetConfig {
    /// 64 Mio : environ 5 s du pire cas estimé (100 Mbit/s, SPEC-234a §6.2) pendant une coupure ou un creux.
    pub const DEFAULT_LIVE_QUEUE_BYTES: usize = 64 << 20;
    pub const DEFAULT_CONNECT_TIMEOUT: Duration = Duration::from_secs(3);
    pub const DEFAULT_RECONNECT_MIN: Duration = Duration::from_millis(500);
    pub const DEFAULT_RECONNECT_MAX: Duration = Duration::from_secs(5);
    pub const DEFAULT_RESEND_BATCH: Duration = Duration::from_millis(500);
}

/// Événements du client, remis au core (file de `mote_poll_event`, et `/events` tant que la session est ouverte).
pub type EventSink = Arc<dyn Fn(u32, String) + Send + Sync>;

#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct NetStats {
    pub bytes_sent: u64,
    pub net_mbps: f32,
    pub live_queue_fill: f32,
    pub connected: bool,
}

struct State {
    live: LiveQueue,
    /// Trames de rattrapage prêtes, servies quand le live est vide.
    resend: VecDeque<Vec<u8>>,
    resend_bytes: usize,
    /// Demandes reçues, par canal : seq voulus.
    wanted: BTreeMap<String, BTreeSet<u64>>,
}

struct Inner {
    cfg: NetConfig,
    state: Mutex<State>,
    ready: Condvar,
    shutdown: AtomicBool,
    connected: AtomicBool,
    bytes_sent: AtomicU64,
    mbps_bits: AtomicU32,
    events: EventSink,
    /// Connexion courante, pour la fermer à l'arrêt.
    stream: Mutex<Option<TcpStream>>,
}

fn lock<T>(m: &Mutex<T>) -> MutexGuard<'_, T> {
    m.lock().unwrap_or_else(|e| e.into_inner())
}

pub struct Net {
    inner: Arc<Inner>,
    threads: Mutex<Vec<JoinHandle<()>>>,
}

impl Net {
    pub fn start(cfg: NetConfig, events: EventSink) -> Net {
        let inner = Arc::new(Inner {
            state: Mutex::new(State {
                live: LiveQueue::new(cfg.live_queue_bytes),
                resend: VecDeque::new(),
                resend_bytes: 0,
                wanted: BTreeMap::new(),
            }),
            cfg,
            ready: Condvar::new(),
            shutdown: AtomicBool::new(false),
            connected: AtomicBool::new(false),
            bytes_sent: AtomicU64::new(0),
            mbps_bits: AtomicU32::new(0),
            events,
            stream: Mutex::new(None),
        });
        let send = {
            let inner = inner.clone();
            thread::Builder::new()
                .name("mote-net".into())
                .spawn(move || connection_loop(&inner))
                .expect("thread réseau")
        };
        let resend = {
            let inner = inner.clone();
            thread::Builder::new()
                .name("mote-resend".into())
                .spawn(move || resend_loop(&inner))
                .expect("thread de rattrapage")
        };
        Net {
            inner,
            threads: Mutex::new(vec![send, resend]),
        }
    }

    /// Met une trame en file live, après son écriture locale. Renvoie les trames retirées, pour `LIVE_DROPPED`.
    pub fn push(&self, channel: &str, seq: u64, body: Body) -> Vec<(String, u64)> {
        let item = Item {
            channel: channel.to_owned(),
            seq,
            bytes: envelope(channel, seq, body),
        };
        let dropped = lock(&self.inner.state).live.push(item);
        self.inner.ready.notify_all();
        dropped.into_iter().map(|i| (i.channel, i.seq)).collect()
    }

    pub fn stats(&self) -> NetStats {
        NetStats {
            bytes_sent: self.inner.bytes_sent.load(Ordering::Relaxed),
            net_mbps: f32::from_bits(self.inner.mbps_bits.load(Ordering::Relaxed)),
            live_queue_fill: lock(&self.inner.state).live.fill(),
            connected: self.inner.connected.load(Ordering::Relaxed),
        }
    }

    /// Arrête les threads et ferme la connexion ; sans effet la seconde fois.
    pub fn close(&self) {
        self.inner.shutdown.store(true, Ordering::Relaxed);
        if let Some(s) = lock(&self.inner.stream).as_ref() {
            let _ = s.shutdown(Shutdown::Both);
        }
        self.inner.ready.notify_all();
        let threads: Vec<_> = lock(&self.threads).drain(..).collect();
        for t in threads {
            let _ = t.join();
        }
    }
}

impl Drop for Net {
    fn drop(&mut self) {
        self.close();
    }
}

fn connect(cfg: &NetConfig) -> io::Result<TcpStream> {
    let mut last = io::Error::new(io::ErrorKind::NotFound, "adresse introuvable");
    for a in cfg.addr.to_socket_addrs()? {
        match TcpStream::connect_timeout(&a, cfg.connect_timeout) {
            Ok(s) => return Ok(s),
            Err(e) => last = e,
        }
    }
    Err(last)
}

/// Attend `d`, ou moins si l'arrêt est demandé.
fn sleep_unless_shutdown(inner: &Inner, d: Duration) {
    let end = Instant::now() + d;
    while !inner.shutdown.load(Ordering::Relaxed) {
        let now = Instant::now();
        if now >= end {
            return;
        }
        thread::sleep((end - now).min(Duration::from_millis(50)));
    }
}

fn connection_loop(inner: &Arc<Inner>) {
    let cfg = &inner.cfg;
    let mut delay = cfg.reconnect_min;
    while !inner.shutdown.load(Ordering::Relaxed) {
        let stream = match connect(cfg) {
            Ok(s) => s,
            Err(_) => {
                sleep_unless_shutdown(inner, delay);
                delay = (delay * 2).min(cfg.reconnect_max);
                continue;
            }
        };
        let _ = stream.set_nodelay(true);
        let (Ok(reader), Ok(ctl)) = (stream.try_clone(), stream.try_clone()) else {
            continue;
        };
        *lock(&inner.stream) = stream.try_clone().ok();
        // `close` a pu passer entre la connexion et l'enregistrement de la socket : la fermer ici aussi.
        if inner.shutdown.load(Ordering::Relaxed) {
            let _ = ctl.shutdown(Shutdown::Both);
            break;
        }
        let hello = envelope(
            "",
            0,
            Body::Hello(v1::Hello {
                session_id: cfg.session_id.clone(),
                auth_token: cfg.auth_token.clone(),
                schema_version: cfg.schema_version,
            }),
        );
        let mut out = BufWriter::new(stream);
        if write_frame(&mut out, &hello)
            .and_then(|_| out.flush())
            .is_err()
        {
            sleep_unless_shutdown(inner, delay);
            delay = (delay * 2).min(cfg.reconnect_max);
            continue;
        }
        inner.connected.store(true, Ordering::Relaxed);
        (inner.events)(EVENT_NET_CONNECTED, cfg.addr.clone());
        delay = cfg.reconnect_min;

        let alive = Arc::new(AtomicBool::new(true));
        let read = {
            let (inner, alive) = (inner.clone(), alive.clone());
            thread::spawn(move || control_loop(&inner, reader, &alive))
        };
        send_loop(inner, &mut out, &alive);
        alive.store(false, Ordering::Relaxed);
        inner.connected.store(false, Ordering::Relaxed);
        // Fermer par un double de la socket, quoi qu'il arrive au vidage du tampon : sinon le lecteur des Control
        // reste bloqué sur une connexion que le pair ne ferme pas.
        let _ = ctl.shutdown(Shutdown::Both);
        drop(out);
        *lock(&inner.stream) = None;
        let _ = read.join();
        if !inner.shutdown.load(Ordering::Relaxed) {
            (inner.events)(EVENT_NET_DISCONNECTED, cfg.addr.clone());
        }
        sleep_unless_shutdown(inner, delay);
    }
}

/// Envoie le live, puis le rattrapage quand le live est vide, jusqu'à une erreur ou l'arrêt.
fn send_loop(inner: &Inner, out: &mut BufWriter<TcpStream>, alive: &AtomicBool) {
    let mut window_start = Instant::now();
    let mut window_bytes = 0u64;
    loop {
        if inner.shutdown.load(Ordering::Relaxed) || !alive.load(Ordering::Relaxed) {
            return;
        }
        let next = {
            let mut st = lock(&inner.state);
            if st.live.is_empty() && st.resend.is_empty() {
                st = inner
                    .ready
                    .wait_timeout(st, Duration::from_millis(200))
                    .unwrap_or_else(|e| e.into_inner())
                    .0;
            }
            match st.live.pop() {
                Some(i) => Some((Some(i.clone()), i.bytes)),
                None => st.resend.pop_front().map(|b| {
                    st.resend_bytes -= b.len();
                    (None, b)
                }),
            }
        };
        let Some((item, bytes)) = next else {
            let _ = out.flush();
            continue;
        };
        let sent = write_frame(out, &bytes).and_then(|_| {
            // Vider le tampon dès que la file est vide : le live ne doit pas attendre la trame suivante.
            if lock(&inner.state).live.is_empty() {
                out.flush()
            } else {
                Ok(())
            }
        });
        if sent.is_err() {
            // La trame n'est peut-être pas partie : elle reste en tête (le PC ignore les doublons).
            if let Some(i) = item {
                lock(&inner.state).live.push_front(i);
            }
            return;
        }
        let n = bytes.len() as u64 + 4;
        inner.bytes_sent.fetch_add(n, Ordering::Relaxed);
        window_bytes += n;
        let el = window_start.elapsed();
        if el >= Duration::from_secs(1) {
            let mbps = window_bytes as f32 * 8.0 / 1e6 / el.as_secs_f32();
            inner.mbps_bits.store(mbps.to_bits(), Ordering::Relaxed);
            window_start = Instant::now();
            window_bytes = 0;
        }
    }
}

/// Lit les trames `Control` du PC jusqu'à la fin de la connexion, l'arrêt, ou la fin de l'envoi (`alive`). La
/// lecture se fait avec un délai, et les octets s'accumulent jusqu'à former une trame : sous Windows, fermer un double
/// de la socket ne débloque pas un `recv` en cours, d'où ce test régulier plutôt qu'une lecture bloquante.
fn control_loop(inner: &Inner, mut stream: TcpStream, alive: &AtomicBool) {
    let _ = stream.set_read_timeout(Some(Duration::from_millis(200)));
    let mut buf: Vec<u8> = Vec::new();
    let mut chunk = [0u8; 4096];
    'read: while !inner.shutdown.load(Ordering::Relaxed) && alive.load(Ordering::Relaxed) {
        match stream.read(&mut chunk) {
            Ok(0) => break,
            Ok(n) => buf.extend_from_slice(&chunk[..n]),
            Err(e)
                if matches!(
                    e.kind(),
                    io::ErrorKind::WouldBlock | io::ErrorKind::TimedOut
                ) =>
            {
                continue
            }
            Err(_) => break,
        }
        while buf.len() >= 4 {
            let len = u32::from_be_bytes([buf[0], buf[1], buf[2], buf[3]]) as usize;
            if len > MAX_FRAME {
                break 'read;
            }
            if buf.len() < 4 + len {
                break;
            }
            let frame: Vec<u8> = buf.drain(..4 + len).skip(4).collect();
            let Ok(c) = v1::Control::decode(&frame[..]) else {
                break 'read;
            };
            if let Some(control::Body::Resend(r)) = c.body {
                if r.last_seq < r.first_seq || r.last_seq - r.first_seq > 1 << 24 {
                    continue;
                }
                let mut st = lock(&inner.state);
                st.wanted
                    .entry(r.channel)
                    .or_default()
                    .extend(r.first_seq..=r.last_seq);
                drop(st);
                inner.ready.notify_all();
            }
        }
    }
    alive.store(false, Ordering::Relaxed);
    inner.ready.notify_all();
}

/// Sert les demandes de rattrapage par lots : relit le fichier local et met en file les messages demandés. Ceux qui
/// ne sont pas encore sur disque restent demandés jusqu'au lot suivant, et sont abandonnés une fois le fichier
/// terminé s'il ne les contient pas.
fn resend_loop(inner: &Inner) {
    const MAGIC: &[u8] = b"\x89MCAP0\r\n";
    while !inner.shutdown.load(Ordering::Relaxed) {
        {
            let st = lock(&inner.state);
            if st.wanted.is_empty() {
                let _ = inner.ready.wait_timeout(st, Duration::from_millis(200));
                continue;
            }
        }
        sleep_unless_shutdown(inner, inner.cfg.resend_batch);
        let wanted = std::mem::take(&mut lock(&inner.state).wanted);
        let Ok(buf) = std::fs::read(&inner.cfg.mcap_path) else {
            lock(&inner.state).wanted = wanted;
            continue;
        };
        let complete = buf.len() >= 2 * MAGIC.len() && buf.ends_with(MAGIC);
        let mut found: BTreeMap<String, BTreeSet<u64>> = BTreeMap::new();
        let opts = mcap::read::Options::IgnoreEndMagic.into();
        let Ok(stream) = mcap::MessageStream::new_with_options(&buf, opts) else {
            lock(&inner.state).wanted = wanted;
            continue;
        };
        for m in stream {
            let Ok(m) = m else { break };
            let topic = &m.channel.topic;
            let seq = m.sequence as u64;
            if !wanted.get(topic).is_some_and(|s| s.contains(&seq)) {
                continue;
            }
            let Some(body) = body_from_bytes(topic, &m.data) else {
                continue;
            };
            let bytes = envelope(topic, seq, body);
            // Contre-pression sur ce seul thread : la file de rattrapage reste sous la borne du live.
            loop {
                let mut st = lock(&inner.state);
                if st.resend_bytes + bytes.len() <= inner.cfg.live_queue_bytes
                    || st.resend.is_empty()
                {
                    st.resend_bytes += bytes.len();
                    st.resend.push_back(bytes);
                    break;
                }
                drop(st);
                if inner.shutdown.load(Ordering::Relaxed) {
                    return;
                }
                inner.ready.notify_all();
                thread::sleep(Duration::from_millis(20));
            }
            inner.ready.notify_all();
            found.entry(topic.clone()).or_default().insert(seq);
        }
        if !complete {
            let mut st = lock(&inner.state);
            for (topic, seqs) in wanted {
                let done = found.get(&topic);
                let rest: BTreeSet<u64> = seqs
                    .into_iter()
                    .filter(|s| !done.is_some_and(|d| d.contains(s)))
                    .collect();
                if !rest.is_empty() {
                    st.wanted.entry(topic).or_default().extend(rest);
                }
            }
        }
    }
}
