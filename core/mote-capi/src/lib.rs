//! API C du core (SPEC-fdb8, ADR-7a16) : handles opaques, tout en push, aucun callback vers l'hôte. Ce fichier est
//! la source de `include/mote.h`. WP-02 n'en pose que le socle ; le reste de l'API arrive avec WP-03.

/// Version de l'ABI : `mote_config.abi_version` doit la porter.
pub const MOTE_ABI_VERSION: u32 = 1;

/// Horloge mote (CLOCK_MONOTONIC), utilisable avant mote_create.
#[no_mangle]
pub extern "C" fn mote_now_ns() -> i64 {
    mote_core::clock::now_ns()
}
