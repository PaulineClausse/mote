//! Cœur de mote : sélection des paires, files et orchestration (ADR-7a16). Aucun accès au matériel ni au moteur :
//! l'hôte pousse tout par l'API C de `mote-capi`. Les étages d'encodage (WP-04) et d'écriture (WP-05) se branchent
//! derrière les files par les traits de `stages`.

pub mod clock;
mod session;
mod stages;
mod types;

pub use session::{
    Core, Error, Result, Stats, ENCODE_QUEUE_CAPACITY, EVENT_QUEUE_CAPACITY, WRITE_QUEUE_CAPACITY,
};
pub use stages::{Encoder, NullWriter, RawEncoder, Writer};
pub use types::*;
