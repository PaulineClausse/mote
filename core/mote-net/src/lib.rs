//! Transport live et rattrapage (ADR-c36f, SPEC-9df2) : trames préfixées par leur taille sur une connexion TCP
//! ouverte par le casque, file live bornée, rattrapage depuis le fichier MCAP local (ADR-d5f3).

mod client;
mod frame;
mod queue;

pub use client::{
    EventSink, Net, NetConfig, NetStats, EVENT_LIVE_DROPPED, EVENT_NET_CONNECTED,
    EVENT_NET_DISCONNECTED,
};
pub use frame::{body_from_bytes, droppable, envelope, read_frame, write_frame, MAX_FRAME};
pub use mote_proto::v1;
pub use queue::{Item, LiveQueue};
