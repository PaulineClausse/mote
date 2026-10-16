//! API C du core (SPEC-fdb8, ADR-7a16) : handles opaques, tout en push, aucun callback vers l'hôte. Ce fichier est
//! la source de `include/mote.h`. Chaque fonction vérifie ses pointeurs et `struct_size`, copie ce qu'elle garde et
//! ne laisse jamais une panique traverser la frontière C.
#![allow(non_camel_case_types)]
// Les fonctions extern "C" déréférencent les pointeurs de l'hôte : leur contrat est celui de SPEC-fdb8.
#![allow(clippy::missing_safety_doc)]

use std::ffi::{c_char, c_void, CStr};
use std::mem::size_of;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::path::PathBuf;
use std::time::Duration;

use mote_core as core;

/// Version de l'ABI : `mote_config.abi_version` doit la porter.
pub const MOTE_ABI_VERSION: u32 = 1;

// Valeurs écrites en littéraux : cbindgen n'évalue pas une constante d'une autre crate. Les assertions plus bas
// les gardent égales à celles du core.
/// `mote_config.codec`.
pub const MOTE_CODEC_JPEG: u32 = 1;
pub const MOTE_CODEC_RAW_RGBA: u32 = 2;
/// `mote_config.flags` : désactive la sélection.
pub const MOTE_FLAG_RECORD_ALL: u32 = 1 << 0;

const _: () = assert!(MOTE_CODEC_JPEG == core::CODEC_JPEG);
const _: () = assert!(MOTE_CODEC_RAW_RGBA == core::CODEC_RAW_RGBA);
const _: () = assert!(MOTE_FLAG_RECORD_ALL == core::FLAG_RECORD_ALL);

#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum mote_status {
    MOTE_OK = 0,
    MOTE_ERR_INVALID_ARG = 1,
    /// fichier local
    MOTE_ERR_IO = 2,
    /// file d'encodage pleine, paire perdue
    MOTE_ERR_BUSY = 3,
    /// appel hors séquence (ex. push avant start)
    MOTE_ERR_STATE = 4,
    MOTE_ERR_INTERNAL = 5,
}

use mote_status::*;

impl From<core::Error> for mote_status {
    fn from(e: core::Error) -> Self {
        match e {
            core::Error::InvalidArg => MOTE_ERR_INVALID_ARG,
            core::Error::Io => MOTE_ERR_IO,
            core::Error::Busy => MOTE_ERR_BUSY,
            core::Error::State => MOTE_ERR_STATE,
            core::Error::Internal => MOTE_ERR_INTERNAL,
        }
    }
}

/// Contexte d'une session, opaque pour l'hôte.
pub struct mote_ctx {
    core: core::Core,
}

#[repr(C)]
pub struct mote_config {
    pub struct_size: u32,
    /// MOTE_ABI_VERSION
    pub abi_version: u32,
    /// obligatoire (ADR-012)
    pub local_dir: *const c_char,
    /// "hôte:port", NULL = pas de flux live
    pub server_addr: *const c_char,
    /// jeton partagé, requis si server_addr
    pub auth_token: *const c_char,
    /// appareil, versions, espace de tracking
    pub session_info_json: *const c_char,
    /// MOTE_CODEC_*
    pub codec: u32,
    /// 0 = défaut (90)
    pub jpeg_quality: u32,
    pub kf_min_translation_m: f32,
    pub kf_min_rotation_rad: f32,
    pub kf_min_sharpness: f32,
    /// écart gauche/droite maximal accepté
    pub pair_max_dt_ns: i64,
    /// MOTE_FLAG_*
    pub flags: u32,
    // Réglages du flux live (WP-14), ajoutés en fin de structure : un hôte compilé sans eux passe un struct_size
    // plus petit et obtient les défauts. 0 = défaut ; les défauts viennent de SP-5 (Wi-Fi 6, 5 GHz) et se règlent
    // selon le réseau.
    /// borne de la file live en octets ; 0 = 64 Mio
    pub live_queue_bytes: u64,
    /// délai de connexion ; 0 = 3000 ms
    pub connect_timeout_ms: u32,
    /// premier délai de reconnexion, doublé à chaque échec ; 0 = 500 ms
    pub reconnect_min_ms: u32,
    /// délai de reconnexion maximal ; 0 = 5000 ms
    pub reconnect_max_ms: u32,
    /// regroupement des demandes de rattrapage ; 0 = 500 ms
    pub resend_batch_ms: u32,
}

/// Taille de `mote_config` avant les réglages du flux live : la plus petite acceptée.
const MOTE_CONFIG_V1_SIZE: usize = std::mem::offset_of!(mote_config, live_queue_bytes);

/// q = x,y,z,w
#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct mote_pose {
    pub p: [f64; 3],
    pub q: [f64; 4],
}

#[repr(C)]
pub struct mote_frame {
    pub struct_size: u32,
    /// horloge mote
    pub t_ns: i64,
    pub src_time_ns: i64,
    /// TimeDomain
    pub src_domain: u32,
    pub width: u32,
    pub height: u32,
    pub stride: u32,
    /// RGBA8888
    pub rgba: *const c_void,
    pub has_pose: u32,
    /// PoseConvention
    pub convention: u32,
    pub world_from_camera: mote_pose,
    pub has_exposure: u32,
    pub exposure_ns: i64,
    pub iso: u32,
}

#[repr(C)]
pub struct mote_intrinsics {
    pub struct_size: u32,
    /// 0 gauche, 1 droite
    pub camera: u32,
    pub width: u32,
    pub height: u32,
    pub fx: f64,
    pub fy: f64,
    pub cx: f64,
    pub cy: f64,
    /// DistortionModel
    pub model: u32,
    pub dist: *const f64,
    pub dist_len: u32,
    pub has_extrinsics: u32,
    pub convention: u32,
    pub hmd_from_camera: mote_pose,
}

#[repr(C)]
pub struct mote_depth {
    pub struct_size: u32,
    /// 0 gauche, 1 droite
    pub eye: u32,
    pub t_ns: i64,
    pub src_time_ns: i64,
    pub src_domain: u32,
    pub width: u32,
    pub height: u32,
    /// DepthEncoding
    pub encoding: u32,
    pub data: *const c_void,
    pub data_len: u64,
    pub convention: u32,
    pub world_from_depth: mote_pose,
    /// tangentes
    pub fov_l: f32,
    pub fov_r: f32,
    pub fov_t: f32,
    pub fov_d: f32,
    /// far_z peut valoir +infini
    pub near_z: f32,
    pub far_z: f32,
    pub min_depth: f32,
    pub max_depth: f32,
}

#[repr(C)]
pub struct mote_stats {
    pub struct_size: u32,
    pub pairs_pushed: u64,
    pub pairs_kept: u64,
    pub pairs_dropped: u64,
    pub bytes_written: u64,
    pub bytes_sent: u64,
    pub net_mbps: f32,
    pub encode_ms_avg: f32,
    pub live_queue_fill: f32,
    pub net_connected: u32,
}

#[repr(C)]
pub struct mote_event {
    pub struct_size: u32,
    pub t_ns: i64,
    /// EventType
    pub r#type: u32,
    pub detail: [c_char; 128],
}

/// Exécute `f` sans laisser une panique traverser la frontière C.
fn guard(f: impl FnOnce() -> Result<(), mote_status>) -> mote_status {
    match catch_unwind(AssertUnwindSafe(f)) {
        Ok(Ok(())) => MOTE_OK,
        Ok(Err(s)) => s,
        Err(_) => MOTE_ERR_INTERNAL,
    }
}

/// Référence vers une structure de l'hôte : non nulle, et au moins aussi grande que la version 1 de la structure
/// (ABI : les champs s'ajoutent en fin de structure).
unsafe fn arg<'a, T>(p: *const T, struct_size: impl Fn(&T) -> u32) -> Result<&'a T, mote_status> {
    let r = p.as_ref().ok_or(MOTE_ERR_INVALID_ARG)?;
    if (struct_size(r) as usize) < size_of::<T>() {
        return Err(MOTE_ERR_INVALID_ARG);
    }
    Ok(r)
}

unsafe fn ctx_ref<'a>(ctx: *mut mote_ctx) -> Result<&'a core::Core, mote_status> {
    ctx.as_ref().map(|c| &c.core).ok_or(MOTE_ERR_INVALID_ARG)
}

/// Chaîne C optionnelle, UTF-8 ; une chaîne vide vaut absence.
unsafe fn opt_str(p: *const c_char) -> Result<Option<String>, mote_status> {
    if p.is_null() {
        return Ok(None);
    }
    let s = CStr::from_ptr(p)
        .to_str()
        .map_err(|_| MOTE_ERR_INVALID_ARG)?;
    Ok((!s.is_empty()).then(|| s.to_owned()))
}

/// Réglages du flux live, ou leurs défauts si l'hôte ne les connaît pas (struct_size plus petit) ou passe 0.
fn net_settings(c: &mote_config) -> Result<core::NetSettings, mote_status> {
    let mut n = core::NetSettings::default();
    if (c.struct_size as usize) < size_of::<mote_config>() {
        return Ok(n);
    }
    let ms = |v: u32, d: Duration| {
        if v == 0 {
            d
        } else {
            Duration::from_millis(v as u64)
        }
    };
    if c.live_queue_bytes != 0 {
        n.live_queue_bytes =
            usize::try_from(c.live_queue_bytes).map_err(|_| MOTE_ERR_INVALID_ARG)?;
    }
    n.connect_timeout = ms(c.connect_timeout_ms, n.connect_timeout);
    n.reconnect_min = ms(c.reconnect_min_ms, n.reconnect_min);
    n.reconnect_max = ms(c.reconnect_max_ms, n.reconnect_max);
    n.resend_batch = ms(c.resend_batch_ms, n.resend_batch);
    if n.reconnect_min > n.reconnect_max {
        return Err(MOTE_ERR_INVALID_ARG);
    }
    Ok(n)
}

unsafe fn config(cfg: *const mote_config) -> Result<core::Config, mote_status> {
    let c = cfg.as_ref().ok_or(MOTE_ERR_INVALID_ARG)?;
    if (c.struct_size as usize) < MOTE_CONFIG_V1_SIZE {
        return Err(MOTE_ERR_INVALID_ARG);
    }
    if c.abi_version != MOTE_ABI_VERSION {
        return Err(MOTE_ERR_INVALID_ARG);
    }
    let local_dir = opt_str(c.local_dir)?.ok_or(MOTE_ERR_INVALID_ARG)?;
    let server_addr = opt_str(c.server_addr)?;
    let auth_token = opt_str(c.auth_token)?;
    if server_addr.is_some() && auth_token.is_none() {
        return Err(MOTE_ERR_INVALID_ARG);
    }
    if c.codec != MOTE_CODEC_JPEG && c.codec != MOTE_CODEC_RAW_RGBA {
        return Err(MOTE_ERR_INVALID_ARG);
    }
    let jpeg_quality = match c.jpeg_quality {
        0 => 90,
        q @ 1..=100 => q,
        _ => return Err(MOTE_ERR_INVALID_ARG),
    };
    let session_info_json = opt_str(c.session_info_json)?;
    if core::session_meta(session_info_json.as_deref()).is_none() {
        return Err(MOTE_ERR_INVALID_ARG);
    }
    Ok(core::Config {
        local_dir: PathBuf::from(local_dir),
        server_addr,
        auth_token,
        session_info_json,
        codec: c.codec,
        jpeg_quality,
        kf_min_translation_m: c.kf_min_translation_m,
        kf_min_rotation_rad: c.kf_min_rotation_rad,
        kf_min_sharpness: c.kf_min_sharpness,
        pair_max_dt_ns: c.pair_max_dt_ns,
        flags: c.flags,
        net: net_settings(c)?,
    })
}

fn pose(convention: u32, p: &mote_pose) -> core::ConventionPose {
    core::ConventionPose {
        convention,
        pose: core::Pose { p: p.p, q: p.q },
    }
}

/// Vue sur une image de l'hôte, valide le temps de l'appel ; le core ne copie que les paires retenues.
unsafe fn frame<'a>(f: *const mote_frame) -> Result<core::FrameView<'a>, mote_status> {
    let f = arg(f, |f| f.struct_size)?;
    let row = f.width as usize * 4;
    if f.rgba.is_null() || f.width == 0 || f.height == 0 || (f.stride as usize) < row {
        return Err(MOTE_ERR_INVALID_ARG);
    }
    let rgba = std::slice::from_raw_parts(
        f.rgba.cast::<u8>(),
        f.stride as usize * (f.height as usize - 1) + row,
    );
    Ok(core::FrameView {
        t_ns: f.t_ns,
        src_time_ns: f.src_time_ns,
        src_domain: f.src_domain,
        width: f.width,
        height: f.height,
        stride: f.stride as usize,
        rgba,
        world_from_camera: (f.has_pose != 0).then(|| pose(f.convention, &f.world_from_camera)),
        exposure_ns: (f.has_exposure != 0).then_some(f.exposure_ns),
        iso: f.iso,
    })
}

/// Crée une session avec un encodeur fourni par l'appelant Rust (tests, futurs étages), et l'écriture MCAP par
/// défaut. Hors de mote.h.
pub unsafe fn create_with_encoder(
    cfg: *const mote_config,
    encoder: Box<dyn core::Encoder>,
    out: *mut *mut mote_ctx,
) -> mote_status {
    create(cfg, out, |c| {
        Ok(core::Core::with_stages(
            c,
            encoder,
            Box::new(core::McapWriter::new()),
        ))
    })
}

unsafe fn create(
    cfg: *const mote_config,
    out: *mut *mut mote_ctx,
    make: impl FnOnce(core::Config) -> core::Result<core::Core>,
) -> mote_status {
    guard(|| {
        let out = out.as_mut().ok_or(MOTE_ERR_INVALID_ARG)?;
        *out = std::ptr::null_mut();
        let core = make(config(cfg)?)?;
        *out = Box::into_raw(Box::new(mote_ctx { core }));
        Ok(())
    })
}

/// Horloge mote (CLOCK_MONOTONIC), utilisable avant mote_create.
#[no_mangle]
pub extern "C" fn mote_now_ns() -> i64 {
    mote_core::clock::now_ns()
}

#[no_mangle]
pub unsafe extern "C" fn mote_create(
    cfg: *const mote_config,
    out: *mut *mut mote_ctx,
) -> mote_status {
    create(cfg, out, core::Core::new)
}

#[no_mangle]
pub unsafe extern "C" fn mote_start(ctx: *mut mote_ctx) -> mote_status {
    guard(|| Ok(ctx_ref(ctx)?.start()?))
}

/// vide les files, écrit SessionEnd, ferme le fichier
#[no_mangle]
pub unsafe extern "C" fn mote_stop(ctx: *mut mote_ctx) -> mote_status {
    guard(|| Ok(ctx_ref(ctx)?.stop()?))
}

/// Arrête la session si elle tourne et libère le contexte. NULL est accepté.
#[no_mangle]
pub unsafe extern "C" fn mote_destroy(ctx: *mut mote_ctx) {
    if !ctx.is_null() {
        let _ = catch_unwind(AssertUnwindSafe(|| drop(Box::from_raw(ctx))));
    }
}

#[no_mangle]
pub unsafe extern "C" fn mote_set_intrinsics(
    ctx: *mut mote_ctx,
    intr: *const mote_intrinsics,
) -> mote_status {
    guard(|| {
        let core = ctx_ref(ctx)?;
        let i = arg(intr, |i| i.struct_size)?;
        if i.camera > 1 {
            return Err(MOTE_ERR_INVALID_ARG);
        }
        let dist = match (i.dist.is_null(), i.dist_len) {
            (_, 0) => Vec::new(),
            (true, _) => return Err(MOTE_ERR_INVALID_ARG),
            (false, n) => std::slice::from_raw_parts(i.dist, n as usize).to_vec(),
        };
        Ok(core.set_intrinsics(core::Intrinsics {
            camera: i.camera,
            width: i.width,
            height: i.height,
            fx: i.fx,
            fy: i.fy,
            cx: i.cx,
            cy: i.cy,
            model: i.model,
            dist,
            hmd_from_camera: (i.has_extrinsics != 0)
                .then(|| pose(i.convention, &i.hmd_from_camera)),
        })?)
    })
}

#[no_mangle]
pub unsafe extern "C" fn mote_push_pair(
    ctx: *mut mote_ctx,
    left: *const mote_frame,
    right: *const mote_frame,
    out_kept: *mut u32,
) -> mote_status {
    guard(|| {
        if let Some(k) = out_kept.as_mut() {
            *k = 0;
        }
        let core = ctx_ref(ctx)?;
        let (l, r) = (frame(left)?, frame(right)?);
        let kept = core.push_pair(&l, &r)?;
        if let Some(k) = out_kept.as_mut() {
            *k = kept as u32;
        }
        Ok(())
    })
}

#[no_mangle]
pub unsafe extern "C" fn mote_push_hmd_pose(
    ctx: *mut mote_ctx,
    t_ns: i64,
    src_time_ns: i64,
    src_domain: u32,
    convention: u32,
    world_from_hmd: *const mote_pose,
    predicted: u32,
) -> mote_status {
    guard(|| {
        let core = ctx_ref(ctx)?;
        let p = world_from_hmd.as_ref().ok_or(MOTE_ERR_INVALID_ARG)?;
        Ok(core.push_hmd_pose(core::HmdPose {
            t_ns,
            src_time_ns,
            src_domain,
            world_from_hmd: pose(convention, p),
            predicted: predicted != 0,
        })?)
    })
}

#[no_mangle]
pub unsafe extern "C" fn mote_push_depth(
    ctx: *mut mote_ctx,
    depth: *const mote_depth,
) -> mote_status {
    guard(|| {
        let core = ctx_ref(ctx)?;
        let d = arg(depth, |d| d.struct_size)?;
        if d.eye > 1 || d.data.is_null() || d.data_len == 0 {
            return Err(MOTE_ERR_INVALID_ARG);
        }
        let data = std::slice::from_raw_parts(d.data.cast::<u8>(), d.data_len as usize).to_vec();
        Ok(core.push_depth(core::Depth {
            eye: d.eye,
            t_ns: d.t_ns,
            src_time_ns: d.src_time_ns,
            src_domain: d.src_domain,
            width: d.width,
            height: d.height,
            encoding: d.encoding,
            data,
            world_from_depth: pose(d.convention, &d.world_from_depth),
            fov: [d.fov_l, d.fov_r, d.fov_t, d.fov_d],
            near_z: d.near_z,
            far_z: d.far_z,
            min_depth: d.min_depth,
            max_depth: d.max_depth,
        })?)
    })
}

#[no_mangle]
pub unsafe extern "C" fn mote_push_event(
    ctx: *mut mote_ctx,
    r#type: u32,
    detail: *const c_char,
) -> mote_status {
    guard(|| {
        let core = ctx_ref(ctx)?;
        // Un détail non UTF-8 n'empêche pas d'enregistrer l'événement.
        let detail = if detail.is_null() {
            String::new()
        } else {
            CStr::from_ptr(detail).to_string_lossy().into_owned()
        };
        Ok(core.push_event(r#type, detail)?)
    })
}

#[no_mangle]
pub unsafe extern "C" fn mote_get_stats(ctx: *mut mote_ctx, out: *mut mote_stats) -> mote_status {
    guard(|| {
        let core = ctx_ref(ctx)?;
        let o = out.as_mut().ok_or(MOTE_ERR_INVALID_ARG)?;
        if (o.struct_size as usize) < size_of::<mote_stats>() {
            return Err(MOTE_ERR_INVALID_ARG);
        }
        let s = core.stats();
        *o = mote_stats {
            struct_size: size_of::<mote_stats>() as u32,
            pairs_pushed: s.pairs_pushed,
            pairs_kept: s.pairs_kept,
            pairs_dropped: s.pairs_dropped,
            bytes_written: s.bytes_written,
            bytes_sent: s.bytes_sent,
            net_mbps: s.net_mbps,
            encode_ms_avg: s.encode_ms_avg,
            live_queue_fill: s.live_queue_fill,
            net_connected: s.net_connected as u32,
        };
        Ok(())
    })
}

/// Prochain événement émis par le core ; `*out_has_event` vaut 0 si la file est vide.
#[no_mangle]
pub unsafe extern "C" fn mote_poll_event(
    ctx: *mut mote_ctx,
    out: *mut mote_event,
    out_has_event: *mut u32,
) -> mote_status {
    guard(|| {
        let core = ctx_ref(ctx)?;
        let o = out.as_mut().ok_or(MOTE_ERR_INVALID_ARG)?;
        let has = out_has_event.as_mut().ok_or(MOTE_ERR_INVALID_ARG)?;
        if (o.struct_size as usize) < size_of::<mote_event>() {
            return Err(MOTE_ERR_INVALID_ARG);
        }
        *has = 0;
        let Some(e) = core.poll_event() else {
            return Ok(());
        };
        o.t_ns = e.t_ns;
        o.r#type = e.kind;
        o.detail = [0; 128];
        // Tronqué à 127 octets sur une frontière de caractère, toujours terminé par NUL.
        let mut n = e.detail.len().min(127);
        while !e.detail.is_char_boundary(n) {
            n -= 1;
        }
        for (d, b) in o.detail.iter_mut().zip(&e.detail.as_bytes()[..n]) {
            *d = *b as c_char;
        }
        *has = 1;
        Ok(())
    })
}
