//! Cœur de mote : sélection des paires, files et orchestration (ADR-7a16). Aucun accès au matériel ni au moteur :
//! l'hôte pousse tout par l'API C de `mote-capi`. Le reste arrive avec WP-03.

pub mod clock;
