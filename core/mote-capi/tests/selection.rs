//! Critère de WP-09 (TASK-7454) : sélection des paires, vue par l'hôte (out_kept, événements) et dans le fichier.

mod common;

use std::ptr;

use common::*;
use mote::*;
use mote_proto::v1;
use mote_proto::Message as _;

const SW: u32 = 64;
const SH: u32 = 48;

/// Damier 4x4 noir et blanc : très net.
fn sharp() -> Vec<u8> {
    let mut px = Vec::new();
    for y in 0..SH {
        for x in 0..SW {
            let v = if (x / 4 + y / 4) % 2 == 0 { 0 } else { 255 };
            px.extend_from_slice(&[v, v, v, 255]);
        }
    }
    px
}

/// Gris uniforme : aucun détail.
fn blurry() -> Vec<u8> {
    vec![128; (SW * SH * 4) as usize]
}

fn at(px: &[u8], t_ns: i64, p: [f64; 3], q: [f64; 4]) -> mote_frame {
    mote_frame {
        width: SW,
        height: SH,
        stride: SW * 4,
        world_from_camera: mote_pose { p, q },
        ..frame(px, t_ns)
    }
}

/// Rotation de `a` radians autour de y.
fn yaw(a: f64) -> [f64; 4] {
    [0.0, (a / 2.0).sin(), 0.0, (a / 2.0).cos()]
}

const ID: [f64; 4] = [0.0, 0.0, 0.0, 1.0];

struct Run {
    ctx: *mut mote_ctx,
    dir: std::path::PathBuf,
    t: i64,
}

impl Run {
    fn start(
        name: &str,
        translation: f32,
        rotation: f32,
        sharpness: f32,
        flags: u32,
    ) -> (Run, Session) {
        let dir = tmp(name);
        let mut s = session(&dir);
        s.cfg.kf_min_translation_m = translation;
        s.cfg.kf_min_rotation_rad = rotation;
        s.cfg.kf_min_sharpness = sharpness;
        s.cfg.flags = flags;
        s.cfg.codec = MOTE_CODEC_RAW_RGBA;
        let mut ctx = ptr::null_mut();
        unsafe {
            assert_eq!(mote_create(&s.cfg, &mut ctx), mote_status::MOTE_OK);
            assert_eq!(mote_start(ctx), mote_status::MOTE_OK);
        }
        (
            Run {
                ctx,
                dir,
                t: 1_000_000_000,
            },
            s,
        )
    }

    /// Pousse une paire synchronisée ; renvoie out_kept.
    fn push(&mut self, l: &[u8], r: &[u8], p: [f64; 3], q: [f64; 4]) -> u32 {
        self.t += 100_000_000;
        let mut kept = 7;
        let st = unsafe {
            mote_push_pair(
                self.ctx,
                &at(l, self.t, p, q),
                &at(r, self.t, p, q),
                &mut kept,
            )
        };
        assert_eq!(st, mote_status::MOTE_OK);
        kept
    }

    /// Arrête la session ; renvoie les ImageFrame gauche et droite du fichier.
    fn finish(self) -> (Vec<v1::ImageFrame>, Vec<v1::ImageFrame>) {
        unsafe {
            assert_eq!(mote_stop(self.ctx), mote_status::MOTE_OK);
            mote_destroy(self.ctx);
        }
        let buf = std::fs::read(session_file(&self.dir)).unwrap();
        let (mut l, mut r) = (Vec::new(), Vec::new());
        for m in mcap::MessageStream::new(&buf).unwrap() {
            let m = m.unwrap();
            match m.channel.topic.as_str() {
                "/cam/left/frame" => l.push(v1::ImageFrame::decode(&m.data[..]).unwrap()),
                "/cam/right/frame" => r.push(v1::ImageFrame::decode(&m.data[..]).unwrap()),
                _ => {}
            }
        }
        let _ = std::fs::remove_dir_all(&self.dir);
        (l, r)
    }
}

#[test]
fn mouvement_retenu_si_et_seulement_si_un_seuil_est_depasse() {
    // 10 cm ou 0,2 rad depuis la dernière paire retenue ; netteté sans seuil.
    let (mut run, _s) = Run::start("sel-motion", 0.10, 0.2, 0.0, 0);
    let px = sharp();
    let kept: Vec<u32> = [
        ([0.0, 1.6, 0.0], ID),           // première paire : rien à quoi comparer
        ([0.05, 1.6, 0.0], ID),          // 5 cm
        ([0.09, 1.6, 0.0], ID),          // 9 cm de la retenue
        ([0.12, 1.6, 0.0], ID),          // 12 cm : retenue, nouvelle référence
        ([0.20, 1.6, 0.0], ID),          // 8 cm de la nouvelle référence
        ([0.12, 1.6, 0.0], yaw(0.15)),   // 0,15 rad
        ([0.12, 1.6, 0.0], yaw(0.25)),   // 0,25 rad : retenue
        ([0.12, 1.6, 0.0], yaw(0.25)),   // immobile
        ([0.12, 1.6, 0.0], yaw(0.10)),   // 0,15 rad dans l'autre sens
        ([0.12, 1.6, -0.15], yaw(0.25)), // 15 cm en z : retenue
    ]
    .iter()
    .map(|(p, q)| run.push(&px, &px, *p, *q))
    .collect();
    assert_eq!(kept, [1, 0, 0, 1, 0, 0, 1, 0, 0, 1]);
    let (l, r) = run.finish();
    assert_eq!(
        (l.len(), r.len()),
        (4, 4),
        "le fichier ne contient que les paires retenues"
    );
}

#[test]
fn nettete_des_deux_images_requise_et_decision_par_paire() {
    // Tout mouvement passe (seuils nuls, chaque paire bouge) ; netteté minimale 10.
    let (mut run, _s) = Run::start("sel-sharp", 0.0, 0.0, 10.0, 0);
    let (s, b) = (sharp(), blurry());
    let mut x = 0.0;
    let mut push = |l: &[u8], r: &[u8]| {
        x += 0.5;
        run.push(l, r, [x, 1.6, 0.0], ID)
    };
    let kept = [
        push(&s, &s),
        push(&s, &b),
        push(&b, &s),
        push(&b, &b),
        push(&s, &s),
    ];
    assert_eq!(kept, [1, 0, 0, 0, 1]);
    let (l, r) = run.finish();
    assert_eq!((l.len(), r.len()), (2, 2), "jamais une image seule");
    for (fl, fr) in l.iter().zip(&r) {
        assert_eq!(fl.pair_id, fr.pair_id);
        assert!(
            fl.blur_score >= 10.0 && fr.blur_score >= 10.0,
            "blur_score porte la netteté mesurée"
        );
    }
}

#[test]
fn record_all_retient_tout() {
    let (mut run, _s) = Run::start("sel-all", 0.10, 0.2, 10.0, MOTE_FLAG_RECORD_ALL);
    let (s, b) = (sharp(), blurry());
    let kept = [
        run.push(&s, &s, [0.0, 1.6, 0.0], ID),
        run.push(&s, &s, [0.0, 1.6, 0.0], ID), // immobile
        run.push(&b, &b, [0.0, 1.6, 0.0], ID), // flou
        run.push(&s, &b, [0.0, 1.6, 0.0], ID),
    ];
    assert_eq!(kept, [1, 1, 1, 1]);
    let (l, r) = run.finish();
    assert_eq!((l.len(), r.len()), (4, 4));
}

#[test]
fn paire_desynchronisee_rejetee_avec_evenement() {
    for flags in [0, MOTE_FLAG_RECORD_ALL] {
        let (run, s) = Run::start("sel-unsync", 0.0, 0.0, 0.0, flags);
        let px = sharp();
        let max_dt = s.cfg.pair_max_dt_ns;
        let t = 5_000_000_000;
        let mut kept = 7;
        let (l, r) = (
            at(&px, t, [0.0; 3], ID),
            at(&px, t + max_dt + 1, [0.0; 3], ID),
        );
        unsafe {
            assert_eq!(
                mote_push_pair(run.ctx, &l, &r, &mut kept),
                mote_status::MOTE_OK
            );
            assert_eq!(kept, 0, "flags={flags}");
            let mut ev: mote_event = std::mem::zeroed();
            ev.struct_size = std::mem::size_of::<mote_event>() as u32;
            let mut has = 0;
            assert_eq!(
                mote_poll_event(run.ctx, &mut ev, &mut has),
                mote_status::MOTE_OK
            );
            assert_eq!(
                (has, ev.r#type),
                (1, 5),
                "PAIR_REJECTED_UNSYNC, flags={flags}"
            );
            // À l'écart limite, la paire passe.
            let r = at(&px, t + max_dt, [1.0, 0.0, 0.0], ID);
            assert_eq!(
                mote_push_pair(run.ctx, &l, &r, &mut kept),
                mote_status::MOTE_OK
            );
            assert_eq!(kept, 1, "flags={flags}");
        }
        let (l, r) = run.finish();
        assert_eq!((l.len(), r.len()), (1, 1));
    }
}

#[test]
fn bornes_mouvement_strict_nettete_large() {
    // 0,125 m est exact en f32 comme en f64 : la translation tombe pile sur le seuil. Netteté minimale nulle :
    // une image uniforme (netteté 0) l'atteint.
    let (mut run, _s) = Run::start("sel-bornes", 0.125, 10.0, 0.0, 0);
    let b = blurry();
    let kept = [
        run.push(&b, &b, [0.0, 1.6, 0.0], ID),
        run.push(&b, &b, [0.125, 1.6, 0.0], ID), // pile sur le seuil : ne le dépasse pas
        run.push(&b, &b, [0.25, 1.6, 0.0], ID),  // 0,25 m de la retenue
    ];
    assert_eq!(kept, [1, 0, 1]);
    run.finish();
}
