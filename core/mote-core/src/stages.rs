//! Étages branchés derrière les files du core : l'encodeur (WP-04) et l'écriture du fichier de session (WP-05).
//! WP-03 n'en fournit que des versions neutres.

use std::io;

use crate::types::{EncodedPair, Pair, Record};

/// Encode une paire retenue. Tourne sur le thread d'encodage.
pub trait Encoder: Send + 'static {
    fn encode(&mut self, pair: Pair) -> EncodedPair;
}

/// Écrit ce qui sort des files. Tourne sur le thread d'écriture ; renvoie le nombre d'octets écrits.
pub trait Writer: Send + 'static {
    fn write(&mut self, record: Record) -> io::Result<u64>;
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

/// N'écrit rien, jusqu'au MCAP de WP-05.
pub struct NullWriter;

impl Writer for NullWriter {
    fn write(&mut self, _record: Record) -> io::Result<u64> {
        Ok(0)
    }

    fn finish(&mut self) -> io::Result<()> {
        Ok(())
    }
}
