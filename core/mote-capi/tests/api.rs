//! Critère de WP-03 (TASK-85d8), testé par les fonctions extern "C" telles que l'hôte les appelle.

mod common;

use std::ffi::CString;
use std::mem::size_of;
use std::ptr;
use std::sync::mpsc;

use common::*;
use mote::*;

#[test]
fn sequence_complete_sans_erreur() {
    let dir = tmp("seq");
    let s = session(&dir);
    let mut ctx: *mut mote_ctx = ptr::null_mut();
    unsafe {
        assert_eq!(mote_create(&s.cfg, &mut ctx), mote_status::MOTE_OK);
        assert!(!ctx.is_null());
        assert_eq!(mote_start(ctx), mote_status::MOTE_OK);

        let dist = [0.1, -0.05, 0.0, 0.0];
        let intr = mote_intrinsics {
            struct_size: size_of::<mote_intrinsics>() as u32,
            camera: 0,
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
        };
        assert_eq!(mote_set_intrinsics(ctx, &intr), mote_status::MOTE_OK);

        let px = vec![128u8; (W * H * 4) as usize];
        let t = mote_now_ns();
        let (l, r) = (frame(&px, t), frame(&px, t + 1_000_000));
        let mut kept = 7u32;
        assert_eq!(mote_push_pair(ctx, &l, &r, &mut kept), mote_status::MOTE_OK);
        assert_eq!(kept, 1);

        assert_eq!(
            mote_push_hmd_pose(ctx, t, t / 1000, 5, 1, &pose(), 0),
            mote_status::MOTE_OK
        );

        let depth_px = [0u8; 4 * 4 * 4];
        let depth = mote_depth {
            struct_size: size_of::<mote_depth>() as u32,
            eye: 0,
            t_ns: t,
            src_time_ns: t,
            src_domain: 3,
            width: 4,
            height: 4,
            encoding: 1,
            data: depth_px.as_ptr().cast(),
            data_len: depth_px.len() as u64,
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
        };
        assert_eq!(mote_push_depth(ctx, &depth), mote_status::MOTE_OK);

        let detail = CString::new("perte de tracking").unwrap();
        assert_eq!(
            mote_push_event(ctx, 1, detail.as_ptr()),
            mote_status::MOTE_OK
        );

        assert_eq!(mote_stop(ctx), mote_status::MOTE_OK);
        let st = stats(ctx);
        assert_eq!(
            (st.pairs_pushed, st.pairs_kept, st.pairs_dropped),
            (1, 1, 0)
        );
        mote_destroy(ctx);
    }
    let _ = std::fs::remove_dir_all(dir);
}

#[test]
fn push_avant_start_renvoie_err_state() {
    let s = session(&tmp("state"));
    let mut ctx: *mut mote_ctx = ptr::null_mut();
    unsafe {
        assert_eq!(mote_create(&s.cfg, &mut ctx), mote_status::MOTE_OK);
        let px = vec![0u8; (W * H * 4) as usize];
        let (l, r) = (frame(&px, 1_000), frame(&px, 2_000));
        let mut kept = 0u32;
        assert_eq!(
            mote_push_pair(ctx, &l, &r, &mut kept),
            mote_status::MOTE_ERR_STATE
        );
        assert_eq!(
            mote_push_hmd_pose(ctx, 1, 1, 1, 1, &pose(), 0),
            mote_status::MOTE_ERR_STATE
        );
        let d = CString::new("x").unwrap();
        assert_eq!(
            mote_push_event(ctx, 1, d.as_ptr()),
            mote_status::MOTE_ERR_STATE
        );
        mote_destroy(ctx);
    }
}

#[test]
fn create_sans_local_dir_renvoie_invalid_arg() {
    let mut s = session(&tmp("nodir"));
    s.cfg.local_dir = ptr::null();
    let mut ctx: *mut mote_ctx = ptr::null_mut();
    unsafe {
        assert_eq!(
            mote_create(&s.cfg, &mut ctx),
            mote_status::MOTE_ERR_INVALID_ARG
        );
    }
    assert!(ctx.is_null());
}

struct Blocking {
    gate: mpsc::Receiver<()>,
    entered: mpsc::Sender<()>,
}

impl mote_core::Encoder for Blocking {
    fn encode(&mut self, pair: mote_core::Pair) -> mote_core::EncodedPair {
        let _ = self.entered.send(());
        let _ = self.gate.recv(); // rend la main quand le test lâche son émetteur
        mote_core::EncodedPair::raw(pair)
    }
}

#[test]
fn file_d_encodage_pleine_renvoie_busy_et_compte_la_perte() {
    let dir = tmp("busy");
    let s = session(&dir);
    // Encodeur bloqué jusqu'à ce que le test le libère : la file se remplit sans dépendre de l'ordonnanceur.
    let (release, gate) = mpsc::channel::<()>();
    let (entered_tx, entered) = mpsc::channel::<()>();
    let encoder = Blocking {
        gate,
        entered: entered_tx,
    };
    let mut ctx: *mut mote_ctx = ptr::null_mut();
    unsafe {
        assert_eq!(
            mote::create_with_encoder(&s.cfg, Box::new(encoder), &mut ctx),
            mote_status::MOTE_OK
        );
        assert_eq!(mote_start(ctx), mote_status::MOTE_OK);
        let px = vec![0u8; (W * H * 4) as usize];
        let mut kept = 0u32;
        let mut t = 1_000_000;
        let mut push = |kept: &mut u32| {
            t += 10_000_000;
            mote_push_pair(ctx, &frame(&px, t), &frame(&px, t), kept)
        };
        // Une paire occupe l'encodeur, puis la file se remplit jusqu'à sa capacité.
        assert_eq!(push(&mut kept), mote_status::MOTE_OK);
        entered.recv().unwrap();
        for _ in 0..mote_core::ENCODE_QUEUE_CAPACITY {
            assert_eq!(push(&mut kept), mote_status::MOTE_OK);
        }
        assert_eq!(push(&mut kept), mote_status::MOTE_ERR_BUSY);
        assert_eq!(kept, 0);
        let st = stats(ctx);
        assert_eq!(st.pairs_dropped, 1);
        assert_eq!(st.pairs_pushed, mote_core::ENCODE_QUEUE_CAPACITY as u64 + 2);

        let mut ev: mote_event = std::mem::zeroed();
        ev.struct_size = size_of::<mote_event>() as u32;
        let mut has = 0u32;
        assert_eq!(
            mote_poll_event(ctx, &mut ev, &mut has),
            mote_status::MOTE_OK
        );
        assert_eq!((has, ev.r#type), (1, 4)); // PAIR_DROPPED_BUSY

        drop(release);
        assert_eq!(mote_stop(ctx), mote_status::MOTE_OK);
        mote_destroy(ctx);
    }
    let _ = std::fs::remove_dir_all(dir);
}
