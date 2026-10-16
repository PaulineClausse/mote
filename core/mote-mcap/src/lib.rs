//! Écriture du fichier MCAP de session (ADR-5955) : canaux typés protobuf, chunks zstd, index. Le fichier local est
//! la source de vérité de la session (ADR-d5f3) : chaque canal numérote ses messages par un seq contigu à partir de
//! 0, porté par le champ `sequence` du message MCAP (SPEC-64c5 §9.1).

use std::fs::File;
use std::io::{self, BufWriter, Seek, SeekFrom, Write};
use std::path::Path;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

use mcap::records::MessageHeader;
use mcap::{Compression, WriteOptions};
use prost::Message;

pub use mote_proto::v1;

/// FileDescriptorSet de mote.proto, schéma de chaque canal.
pub const FILE_DESCRIPTOR_SET: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/mote.fds"));

/// Canaux de SPEC-64c5 §9.1.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Channel {
    SessionInfo,
    LeftFrame,
    RightFrame,
    LeftIntrinsics,
    RightIntrinsics,
    HmdPose,
    LeftDepth,
    RightDepth,
    Events,
    Stats,
    SessionEnd,
}

impl Channel {
    pub const ALL: [Channel; 11] = [
        Channel::SessionInfo,
        Channel::LeftFrame,
        Channel::RightFrame,
        Channel::LeftIntrinsics,
        Channel::RightIntrinsics,
        Channel::HmdPose,
        Channel::LeftDepth,
        Channel::RightDepth,
        Channel::Events,
        Channel::Stats,
        Channel::SessionEnd,
    ];

    pub fn topic(self) -> &'static str {
        match self {
            Channel::SessionInfo => "/session/info",
            Channel::LeftFrame => "/cam/left/frame",
            Channel::RightFrame => "/cam/right/frame",
            Channel::LeftIntrinsics => "/cam/left/intrinsics",
            Channel::RightIntrinsics => "/cam/right/intrinsics",
            Channel::HmdPose => "/pose/hmd",
            Channel::LeftDepth => "/depth/left",
            Channel::RightDepth => "/depth/right",
            Channel::Events => "/events",
            Channel::Stats => "/stats",
            Channel::SessionEnd => "/session/end",
        }
    }

    /// Nom complet du message protobuf du canal.
    pub fn schema(self) -> &'static str {
        match self {
            Channel::SessionInfo => "mote.v1.SessionInfo",
            Channel::LeftFrame | Channel::RightFrame => "mote.v1.ImageFrame",
            Channel::LeftIntrinsics | Channel::RightIntrinsics => "mote.v1.CameraIntrinsics",
            Channel::HmdPose => "mote.v1.PoseSample",
            Channel::LeftDepth | Channel::RightDepth => "mote.v1.DepthFrame",
            Channel::Events => "mote.v1.Event",
            Channel::Stats => "mote.v1.Stats",
            Channel::SessionEnd => "mote.v1.SessionEnd",
        }
    }

    fn index(self) -> usize {
        Channel::ALL.iter().position(|c| *c == self).unwrap()
    }
}

/// Fichier sous-jacent, qui suit sa longueur : la taille du fichier une fois le tampon vidé.
struct Counted {
    file: BufWriter<File>,
    pos: u64,
    len: Arc<AtomicU64>,
}

impl Write for Counted {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
        let n = self.file.write(buf)?;
        self.pos += n as u64;
        self.len.fetch_max(self.pos, Ordering::Relaxed);
        Ok(n)
    }

    fn flush(&mut self) -> io::Result<()> {
        self.file.flush()
    }
}

impl Seek for Counted {
    fn seek(&mut self, from: SeekFrom) -> io::Result<u64> {
        self.pos = self.file.seek(from)?;
        Ok(self.pos)
    }
}

/// Un fichier de session ouvert. `finish` écrit `/session/end` puis le résumé ; un processus tué avant laisse les
/// chunks déjà fermés lisibles par une lecture linéaire.
pub struct SessionWriter {
    mcap: mcap::Writer<Counted>,
    /// Identifiant MCAP et prochain seq de chaque canal, dans l'ordre de `Channel::ALL`.
    ids: [u16; 11],
    next_seq: [u64; 11],
    len: Arc<AtomicU64>,
}

fn mcap_err(e: mcap::McapError) -> io::Error {
    match e {
        mcap::McapError::Io(e) => e,
        e => io::Error::other(e),
    }
}

/// Taille visée d'un chunk avant compression. Un message plus gros forme son propre chunk.
pub const CHUNK_SIZE: u64 = 1 << 20;

impl SessionWriter {
    /// Crée le fichier (jamais d'écrasement), déclare tous les canaux et écrit `/session/info`.
    /// Renvoie aussi le seq de `/session/info` (0), pour le flux live.
    pub fn create(
        path: &Path,
        info: &v1::SessionInfo,
        log_time_ns: i64,
    ) -> io::Result<(Self, u64)> {
        let file = File::create_new(path)?;
        let len = Arc::new(AtomicU64::new(0));
        let out = Counted {
            file: BufWriter::new(file),
            pos: 0,
            len: len.clone(),
        };
        let mut mcap = WriteOptions::new()
            .profile("")
            .library(concat!("mote-core ", env!("CARGO_PKG_VERSION")))
            .compression(Some(Compression::Zstd))
            .chunk_size(Some(CHUNK_SIZE))
            .create(out)
            .map_err(mcap_err)?;
        let mut ids = [0u16; 11];
        let mut schemas: Vec<(&str, u16)> = Vec::new();
        for c in Channel::ALL {
            let schema_id = match schemas.iter().find(|(n, _)| *n == c.schema()) {
                Some((_, id)) => *id,
                None => {
                    let id = mcap
                        .add_schema(c.schema(), "protobuf", FILE_DESCRIPTOR_SET)
                        .map_err(mcap_err)?;
                    schemas.push((c.schema(), id));
                    id
                }
            };
            ids[c.index()] = mcap
                .add_channel(schema_id, c.topic(), "protobuf", &Default::default())
                .map_err(mcap_err)?;
        }
        let mut w = SessionWriter {
            mcap,
            ids,
            next_seq: [0; 11],
            len,
        };
        let info_seq = w.write(Channel::SessionInfo, log_time_ns, info)?;
        Ok((w, info_seq))
    }

    /// Écrit un message sur son canal, avec le seq suivant, et renvoie ce seq. `log_time_ns` est l'horloge mote.
    pub fn write(
        &mut self,
        channel: Channel,
        log_time_ns: i64,
        msg: &impl Message,
    ) -> io::Result<u64> {
        let i = channel.index();
        let seq = self.next_seq[i];
        let sequence = u32::try_from(seq).map_err(|_| io::Error::other("seq au-delà de u32"))?;
        let header = MessageHeader {
            channel_id: self.ids[i],
            sequence,
            log_time: log_time_ns.max(0) as u64,
            publish_time: log_time_ns.max(0) as u64,
        };
        self.mcap
            .write_to_known_channel(&header, &msg.encode_to_vec())
            .map_err(mcap_err)?;
        self.next_seq[i] = seq + 1;
        Ok(seq)
    }

    /// Ferme le chunk en cours et le transmet au système : ce qui précède survit à la mort du processus.
    pub fn flush(&mut self) -> io::Result<()> {
        self.mcap.flush().map_err(mcap_err)
    }

    /// Longueur du fichier, tampons compris.
    pub fn bytes_written(&self) -> u64 {
        self.len.load(Ordering::Relaxed)
    }

    /// Dernier seq de chaque canal qui a des messages, hors `/session/end`.
    pub fn session_end(&self) -> v1::SessionEnd {
        v1::SessionEnd {
            channels: Channel::ALL
                .iter()
                .filter(|c| **c != Channel::SessionEnd && self.next_seq[c.index()] > 0)
                .map(|c| v1::ChannelEnd {
                    channel: c.topic().to_owned(),
                    last_seq: self.next_seq[c.index()] - 1,
                })
                .collect(),
        }
    }

    /// Écrit `/session/end`, le résumé et l'index, puis ferme le fichier.
    pub fn finish(mut self, log_time_ns: i64) -> io::Result<Finished> {
        let end = self.session_end();
        let end_seq = self.write(Channel::SessionEnd, log_time_ns, &end)?;
        self.mcap.finish().map_err(mcap_err)?;
        let mut out = self.mcap.into_inner();
        out.file.flush()?;
        out.file.get_ref().sync_all()?;
        Ok(Finished {
            len: self.len.load(Ordering::Relaxed),
            end,
            end_seq,
        })
    }
}

/// Ce que la fermeture du fichier rend : sa taille finale, et le `/session/end` écrit, pour le flux live.
pub struct Finished {
    pub len: u64,
    pub end: v1::SessionEnd,
    pub end_seq: u64,
}
