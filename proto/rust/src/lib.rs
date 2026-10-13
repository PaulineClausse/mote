//! Types du schéma protobuf `mote.v1` (ADR-956c), générés par prost au build depuis `proto/mote/v1/mote.proto`.

pub mod v1 {
    include!(concat!(env!("OUT_DIR"), "/mote.v1.rs"));
}

pub use prost::Message;
