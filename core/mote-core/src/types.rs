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
    /// Netteté mesurée par la sélection (`ImageFrame.blur_score` : plus grand = plus net).
    pub blur_score: f32,
}

/// Une image telle que l'hôte la passe, lue dans son buffer sans copie : `stride` octets par ligne.
#[derive(Clone, Copy, Debug)]
pub struct FrameView<'a> {
    pub t_ns: i64,
    pub src_time_ns: i64,
    pub src_domain: u32,
    pub width: u32,
    pub height: u32,
    pub stride: usize,
    /// Au moins `stride * (height - 1) + width * 4` octets.
    pub rgba: &'a [u8],
    pub world_from_camera: Option<ConventionPose>,
    pub exposure_ns: Option<i64>,
    pub iso: u32,
}

impl FrameView<'_> {
    /// Copie l'image en RGBA compact, sans le padding de `stride`.
    pub fn to_frame(&self, blur_score: f32) -> Frame {
        let row = self.width as usize * 4;
        let mut rgba = Vec::with_capacity(row * self.height as usize);
        for y in 0..self.height as usize {
            let start = y * self.stride;
            rgba.extend_from_slice(&self.rgba[start..start + row]);
        }
        Frame {
            t_ns: self.t_ns,
            src_time_ns: self.src_time_ns,
            src_domain: self.src_domain,
            width: self.width,
            height: self.height,
            rgba,
            world_from_camera: self.world_from_camera,
            exposure_ns: self.exposure_ns,
            iso: self.iso,
            blur_score,
        }
    }
}

/// Paire stéréo retenue, en attente d'encodage.
#[derive(Clone, Debug)]
pub struct Pair {
    /// Identique pour la gauche et la droite (`ImageFrame.pair_id`).
    pub id: u64,
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
    pub id: u64,
    pub left: EncodedFrame,
    pub right: EncodedFrame,
}

impl EncodedPair {
    /// La paire telle quelle, en RGBA brut.
    pub fn raw(pair: Pair) -> Self {
        EncodedPair {
            id: pair.id,
            left: Self::raw_frame(pair.left),
            right: Self::raw_frame(pair.right),
        }
    }

    /// Une image telle quelle, en RGBA brut.
    pub fn raw_frame(mut f: Frame) -> EncodedFrame {
        EncodedFrame {
            codec: CODEC_RAW_RGBA,
            data: std::mem::take(&mut f.rgba),
            source: f,
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
    /// En boîte : une paire est bien plus grosse que les autres records.
    Pair(Box<EncodedPair>),
    Stats(Stats),
}

/// Compteurs de supervision (`mote_get_stats`, canal `/stats`).
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Stats {
    pub t_ns: i64,
    pub pairs_pushed: u64,
    pub pairs_kept: u64,
    pub pairs_dropped: u64,
    pub bytes_written: u64,
    pub bytes_sent: u64,
    pub net_mbps: f32,
    pub encode_ms_avg: f32,
    pub live_queue_fill: f32,
    pub net_connected: bool,
}
