//! Étages branchés derrière les files du core : l'encodeur (`JpegEncoder`, WP-04) et l'écriture du fichier de
//! session (`McapWriter`, WP-05).

use std::io;
use std::path::PathBuf;
use std::sync::mpsc::Receiver;
use std::sync::Arc;

use mote_codec::Jpeg;
use mote_net::Net;

use crate::types::{Config, EncodedFrame, EncodedPair, Event, Frame, Pair, Record, CODEC_JPEG};

/// Ce que le core fixe au démarrage d'une session et transmet à l'écriture.
pub struct SessionStart {
    pub id: String,
    pub start_unix_ns: i64,
    pub start_t_ns: i64,
    /// Fichier de session, `<local_dir>/<id>.mcap`.
    pub path: PathBuf,
    /// Flux live, si `server_addr` est configuré.
    pub live: Option<Live>,
}

/// Côté écriture du flux live : chaque message écrit localement est ensuite mis en file live (SPEC-9df2).
pub struct Live {
    pub net: Arc<Net>,
    /// Événements du client réseau, à écrire dans `/events`.
    pub events: Receiver<Event>,
    /// Remet un événement à l'hôte (`mote_poll_event`).
    pub notify: Arc<dyn Fn(Event) + Send + Sync>,
}

/// Encode une paire retenue. Tourne sur le thread d'encodage.
pub trait Encoder: Send + 'static {
    fn encode(&mut self, pair: Pair) -> EncodedPair;
}

/// Écrit ce qui sort des files, sur le thread d'écriture, dans l'ordre d'arrivée.
pub trait Writer: Send + 'static {
    /// Appelé par `start`, avant toute écriture ; une erreur fait échouer `start`.
    fn open(&mut self, _config: &Config, _session: SessionStart) -> io::Result<()> {
        Ok(())
    }
    fn write(&mut self, record: Record) -> io::Result<()>;
    /// Appelé au moins une fois par seconde : rend ce qui précède durable face à la mort du processus.
    fn flush(&mut self) -> io::Result<()> {
        Ok(())
    }
    /// Octets écrits jusqu'ici.
    fn bytes_written(&self) -> u64 {
        0
    }
    /// Appelé une fois les files vidées, à `stop`.
    fn finish(&mut self) -> io::Result<()>;
}

/// Laisse les images en RGBA brut : codec `RAW_RGBA`, réservé aux sessions de référence (ADR-86d6).
pub struct RawEncoder;

impl Encoder for RawEncoder {
    fn encode(&mut self, pair: Pair) -> EncodedPair {
        EncodedPair::raw(pair)
    }
}

/// JPEG par libjpeg-turbo (ADR-86d6) ; la gauche et la droite sont encodées en parallèle, sur deux threads.
pub struct JpegEncoder {
    left: Jpeg,
    right: Jpeg,
}

impl JpegEncoder {
    pub fn new(quality: u32) -> Result<Self, mote_codec::Error> {
        Ok(JpegEncoder {
            left: Jpeg::new(quality)?,
            right: Jpeg::new(quality)?,
        })
    }
}

/// Une image encodée en JPEG ; si libjpeg-turbo échoue, l'image est gardée en RGBA brut (codec déclaré tel quel)
/// plutôt que perdue : le fichier local est la source de vérité (ADR-d5f3).
fn jpeg_or_raw(jpeg: &mut Jpeg, mut f: Frame) -> EncodedFrame {
    match jpeg.encode(&f.rgba, f.width, f.height) {
        Ok(data) => {
            f.rgba = Vec::new();
            EncodedFrame {
                codec: CODEC_JPEG,
                data,
                source: f,
            }
        }
        Err(_) => EncodedPair::raw_frame(f),
    }
}

impl Encoder for JpegEncoder {
    fn encode(&mut self, pair: Pair) -> EncodedPair {
        let Pair { id, left, right } = pair;
        let (l, r) = (&mut self.left, &mut self.right);
        let (left, right) = std::thread::scope(|s| {
            let left = s.spawn(move || jpeg_or_raw(l, left));
            let right = jpeg_or_raw(r, right);
            (left.join().expect("thread d'encodage"), right)
        });
        EncodedPair { id, left, right }
    }
}

/// N'écrit rien.
pub struct NullWriter;

impl Writer for NullWriter {
    fn write(&mut self, _record: Record) -> io::Result<()> {
        Ok(())
    }

    fn finish(&mut self) -> io::Result<()> {
        Ok(())
    }
}
