//! Données de test partagées : une session telle qu'un hôte la pousserait par l'API C.
#![allow(dead_code)]

use std::ffi::CString;
use std::mem::size_of;
use std::path::{Path, PathBuf};
use std::ptr;

use mote::*;

pub const W: u32 = 8;
pub const H: u32 = 4;

/// Configuration et chaînes qu'elle référence, gardées en vie ensemble.
pub struct Session {
    _dir: CString,
    _info: CString,
    pub cfg: mote_config,
}

pub fn session(dir: &Path) -> Session {
    let dir = CString::new(dir.to_str().unwrap()).unwrap();
    let info = CString::new(
        r#"{"device_model":"Quest 3S","os_build":"test","sdk_versions":{"mruk":"77"},"host_kind":"tests","tracking_space":"local_floor"}"#,
    )
    .unwrap();
    let cfg = mote_config {
        struct_size: size_of::<mote_config>() as u32,
        abi_version: MOTE_ABI_VERSION,
        local_dir: dir.as_ptr(),
        server_addr: ptr::null(),
        auth_token: ptr::null(),
        session_info_json: info.as_ptr(),
        codec: MOTE_CODEC_JPEG,
        jpeg_quality: 0,
        kf_min_translation_m: 0.0,
        kf_min_rotation_rad: 0.0,
        kf_min_sharpness: 0.0,
        pair_max_dt_ns: 5_000_000,
        flags: MOTE_FLAG_RECORD_ALL,
    };
    Session {
        _dir: dir,
        _info: info,
        cfg,
    }
}

/// Répertoire de session neuf, sous le répertoire temporaire.
pub fn tmp(name: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!("mote-capi-{name}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    d
}

pub fn pose() -> mote_pose {
    mote_pose {
        p: [0.0, 1.6, 0.0],
        q: [0.0, 0.0, 0.0, 1.0],
    }
}

pub fn frame(rgba: &[u8], t_ns: i64) -> mote_frame {
    mote_frame {
        struct_size: size_of::<mote_frame>() as u32,
        t_ns,
        src_time_ns: t_ns / 1000,
        src_domain: 5,
        width: W,
        height: H,
        stride: W * 4,
        rgba: rgba.as_ptr().cast(),
        has_pose: 1,
        convention: 1,
        world_from_camera: pose(),
        has_exposure: 0,
        exposure_ns: 0,
        iso: 0,
    }
}

pub fn intrinsics(camera: u32, dist: &[f64]) -> mote_intrinsics {
    mote_intrinsics {
        struct_size: size_of::<mote_intrinsics>() as u32,
        camera,
        width: W,
        height: H,
        fx: 5.0,
        fy: 5.0,
        cx: 4.0,
        cy: 2.0,
        model: 2,
        dist: dist.as_ptr(),
        dist_len: dist.len() as u32,
        has_extrinsics: 1,
        convention: 1,
        hmd_from_camera: pose(),
    }
}

pub fn depth(eye: u32, data: &[u8], t_ns: i64) -> mote_depth {
    mote_depth {
        struct_size: size_of::<mote_depth>() as u32,
        eye,
        t_ns,
        src_time_ns: t_ns,
        src_domain: 3,
        width: 4,
        height: 4,
        encoding: 1,
        data: data.as_ptr().cast(),
        data_len: data.len() as u64,
        convention: 2,
        world_from_depth: pose(),
        fov_l: 1.0,
        fov_r: 1.0,
        fov_t: 1.0,
        fov_d: 1.0,
        near_z: 0.1,
        far_z: f32::INFINITY,
        min_depth: 0.0,
        max_depth: 1.0,
    }
}

pub fn stats(ctx: *mut mote_ctx) -> mote_stats {
    let mut s: mote_stats = unsafe { std::mem::zeroed() };
    s.struct_size = size_of::<mote_stats>() as u32;
    assert_eq!(unsafe { mote_get_stats(ctx, &mut s) }, mote_status::MOTE_OK);
    s
}

/// Seul fichier `.mcap` du répertoire de session.
pub fn session_file(dir: &Path) -> PathBuf {
    let files: Vec<_> = std::fs::read_dir(dir)
        .unwrap()
        .map(|e| e.unwrap().path())
        .filter(|p| p.extension().is_some_and(|e| e == "mcap"))
        .collect();
    assert_eq!(
        files.len(),
        1,
        "un fichier .mcap attendu dans {}, trouvé {files:?}",
        dir.display()
    );
    files.into_iter().next().unwrap()
}
