//! Données poussées par l'hôte, copiées par le core (SPEC-fdb8 : les buffers de l'hôte ne sont lus que pendant
//! l'appel). Les valeurs d'enum (`src_domain`, `convention`, `model`, `encoding`, type d'événement) sont celles de
//! mote.v1, transmises telles quelles.

use std::path::PathBuf;

/// Code de `mote_config.codec`.
pub const CODEC_JPEG: u32 = 1;
pub const CODEC_RAW_RGBA: u32 = 2;
/// `mote_config.flags` : désactive la sélection, toutes les paires sont retenues.
pub const FLAG_RECORD_ALL: u32 = 1;

/// `EventType` de mote.v1 émis par le core lui-même.
pub const EVENT_PAIR_DROPPED_BUSY: u32 = 4;
pub const EVENT_PAIR_REJECTED_UNSYNC: u32 = 5;

/// Configuration d'une session, validée par l'API C.
#[derive(Clone, Debug)]
pub struct Config {
    pub local_dir: PathBuf,
    pub server_addr: Option<String>,
    pub auth_token: Option<String>,
    pub session_info_json: Option<String>,
    pub codec: u32,
    pub jpeg_quality: u32,
    pub kf_min_translation_m: f32,
    pub kf_min_rotation_rad: f32,
    pub kf_min_sharpness: f32,
    /// Écart gauche/droite maximal ; 0 ou moins désactive le contrôle.
    pub pair_max_dt_ns: i64,
    pub flags: u32,
}

/// Position (m) et rotation (x, y, z, w).
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Pose {
    pub p: [f64; 3],
    pub q: [f64; 4],
}

/// Pose avec sa convention (`PoseConvention`).
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ConventionPose {
    pub convention: u32,
    pub pose: Pose,
}

/// Une image, en RGBA8888 compact (`width * 4` octets par ligne).
#[derive(Clone, Debug)]
pub struct Frame {
    pub t_ns: i64,
    pub src_time_ns: i64,
    pub src_domain: u32,
    pub width: u32,
    pub height: u32,
    pub rgba: Vec<u8>,
    pub world_from_camera: Option<ConventionPose>,
    pub exposure_ns: Option<i64>,
    pub iso: u32,
}

/// Paire stéréo retenue, en attente d'encodage.
#[derive(Clone, Debug)]
pub struct Pair {
    pub left: Frame,
    pub right: Frame,
}

/// Image encodée selon `codec` ; les métadonnées de la frame source sont conservées.
#[derive(Clone, Debug)]
pub struct EncodedFrame {
    pub codec: u32,
    pub data: Vec<u8>,
    pub source: Frame,
}

#[derive(Clone, Debug)]
pub struct EncodedPair {
    pub left: EncodedFrame,
    pub right: EncodedFrame,
}

impl EncodedPair {
    /// La paire telle quelle, en RGBA brut : ce que produit le core tant que WP-04 n'a pas branché le JPEG.
    pub fn raw(pair: Pair) -> Self {
        let wrap = |mut f: Frame| EncodedFrame {
            codec: CODEC_RAW_RGBA,
            data: std::mem::take(&mut f.rgba),
            source: f,
        };
        EncodedPair {
            left: wrap(pair.left),
            right: wrap(pair.right),
        }
    }
}

#[derive(Clone, Debug)]
pub struct Intrinsics {
    pub camera: u32,
    pub width: u32,
    pub height: u32,
    pub fx: f64,
    pub fy: f64,
    pub cx: f64,
    pub cy: f64,
    pub model: u32,
    pub dist: Vec<f64>,
    pub hmd_from_camera: Option<ConventionPose>,
}

#[derive(Clone, Debug)]
pub struct HmdPose {
    pub t_ns: i64,
    pub src_time_ns: i64,
    pub src_domain: u32,
    pub world_from_hmd: ConventionPose,
    pub predicted: bool,
}

#[derive(Clone, Debug)]
pub struct Depth {
    pub eye: u32,
    pub t_ns: i64,
    pub src_time_ns: i64,
    pub src_domain: u32,
    pub width: u32,
    pub height: u32,
    pub encoding: u32,
    pub data: Vec<u8>,
    pub world_from_depth: ConventionPose,
    /// Tangentes gauche, droite, haut, bas.
    pub fov: [f32; 4],
    pub near_z: f32,
    pub far_z: f32,
    pub min_depth: f32,
    pub max_depth: f32,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Event {
    pub t_ns: i64,
    pub kind: u32,
    pub detail: String,
}

/// Ce que l'étage d'écriture reçoit, dans l'ordre d'arrivée.
#[derive(Clone, Debug)]
pub enum Record {
    Intrinsics(Intrinsics),
    HmdPose(HmdPose),
    Depth(Depth),
    Event(Event),
    Pair(EncodedPair),
}
