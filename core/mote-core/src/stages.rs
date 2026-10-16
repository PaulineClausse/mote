//! Étages branchés derrière les files du core : l'encodeur (WP-04) et l'écriture du fichier de session (WP-05,
//! `McapWriter`).

use std::io;

use crate::types::{Config, EncodedPair, Pair, Record};

/// Encode une paire retenue. Tourne sur le thread d'encodage.
pub trait Encoder: Send + 'static {
    fn encode(&mut self, pair: Pair) -> EncodedPair;
}

/// Écrit ce qui sort des files, sur le thread d'écriture, dans l'ordre d'arrivée.
pub trait Writer: Send + 'static {
    /// Appelé par `start`, avant toute écriture ; une erreur fait échouer `start`.
    fn open(&mut self, _config: &Config) -> io::Result<()> {
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

/// Laisse les images en RGBA brut, jusqu'au JPEG de WP-04.
pub struct RawEncoder;

impl Encoder for RawEncoder {
    fn encode(&mut self, pair: Pair) -> EncodedPair {
        EncodedPair::raw(pair)
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
