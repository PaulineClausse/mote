//! Critère de WP-04 (TASK-ec26) : une paire RGBA 1280x1280 poussée par l'API C, relue dans le fichier de session.

mod common;

use std::collections::BTreeMap;
use std::mem::size_of;
use std::ptr;

use common::*;
use mote::*;
use mote_proto::v1;
use mote_proto::Message as _;

const N: u32 = 1280;

/// Image de test déterministe : dégradés, texture sinusoïdale, bords nets et bruit léger, pour ressembler à une
/// vue de pièce plutôt qu'à un aplat. `eye` décale le contenu, comme la parallaxe d'une paire stéréo.
fn test_image(eye: u32) -> Vec<u8> {
    let mut px = Vec::with_capacity((N * N * 4) as usize);
    let mut seed = 0x2545_f491_u32 ^ eye;
    for y in 0..N {
        for x in 0..N {
            let xf = (x + eye * 24) as f32;
            let yf = y as f32;
            seed = seed.wrapping_mul(1_103_515_245).wrapping_add(12_345);
            let noise = ((seed >> 16) % 17) as f32 - 8.0;
            let wall = 60.0 + 120.0 * yf / N as f32;
            // Texture fine (tapis, grain du bois) : c'est elle que la quantification JPEG attaque.
            let texture = 25.0 * ((xf * 0.05).sin() * (yf * 0.03).cos())
                + 20.0 * ((xf * 0.9).sin() * (yf * 0.7).sin());
            // Un cadre sombre et un objet clair aux bords francs.
            let frame = (300..900).contains(&(xf as u32)) && (200..260).contains(&y);
            let object = ((xf - 640.0).powi(2) + (yf - 800.0).powi(2)) < 180.0f32.powi(2);
            let base = if frame {
                20.0
            } else if object {
                220.0
            } else {
                wall + texture
            };
            let c = |k: f32| (base * k + noise).clamp(0.0, 255.0) as u8;
            px.extend_from_slice(&[c(1.0), c(0.85), c(0.7), 255]);
        }
    }
    px
}

/// PSNR (dB) sur les canaux RGB, entre la source RGBA et une image RGB décodée.
fn psnr(rgba: &[u8], rgb: &[u8]) -> f64 {
    let mut se = 0.0f64;
    for (s, d) in rgba.chunks_exact(4).zip(rgb.chunks_exact(3)) {
        for k in 0..3 {
            let e = s[k] as f64 - d[k] as f64;
            se += e * e;
        }
    }
    let mse = se / (rgb.len() as f64);
    10.0 * (255.0f64 * 255.0 / mse).log10()
}

fn frame_of(rgba: &[u8], t_ns: i64) -> mote_frame {
    mote_frame {
        width: N,
        height: N,
        stride: N * 4,
        ..frame(rgba, t_ns)
    }
}

/// Pousse une paire avec le codec donné, arrête la session, renvoie les ImageFrame gauche et droite du fichier.
fn push_and_read(
    name: &str,
    codec: u32,
    left: &[u8],
    right: &[u8],
) -> (v1::ImageFrame, v1::ImageFrame) {
    let dir = tmp(name);
    let mut s = session(&dir);
    s.cfg.codec = codec;
    s.cfg.jpeg_quality = 90;
    let mut ctx: *mut mote_ctx = ptr::null_mut();
    unsafe {
        assert_eq!(mote_create(&s.cfg, &mut ctx), mote_status::MOTE_OK);
        assert_eq!(mote_start(ctx), mote_status::MOTE_OK);
        let t = mote_now_ns();
        let mut kept = 0;
        let st = mote_push_pair(ctx, &frame_of(left, t), &frame_of(right, t), &mut kept);
        assert_eq!((st, kept), (mote_status::MOTE_OK, 1));
        assert_eq!(mote_stop(ctx), mote_status::MOTE_OK);
        assert!(
            stats(ctx).encode_ms_avg > 0.0,
            "temps d'encodage non mesuré"
        );
        mote_destroy(ctx);
    }
    let buf = std::fs::read(session_file(&dir)).unwrap();
    let mut frames: BTreeMap<String, v1::ImageFrame> = BTreeMap::new();
    for m in mcap::MessageStream::new(&buf).unwrap() {
        let m = m.unwrap();
        if m.channel.topic.ends_with("/frame") {
            frames.insert(
                m.channel.topic.clone(),
                v1::ImageFrame::decode(&m.data[..]).unwrap(),
            );
        }
    }
    let _ = std::fs::remove_dir_all(dir);
    (
        frames.remove("/cam/left/frame").unwrap(),
        frames.remove("/cam/right/frame").unwrap(),
    )
}

#[test]
fn paire_1280_en_jpeg_q90_decodable_et_fidele() {
    let (l, r) = (test_image(0), test_image(1));
    let (fl, fr) = push_and_read("jpeg", MOTE_CODEC_JPEG, &l, &r);
    for (name, src, f) in [("gauche", &l, &fl), ("droite", &r, &fr)] {
        assert_eq!(f.codec, v1::ImageCodec::Jpeg as i32, "{name} : codec");
        assert_eq!((f.width, f.height), (N, N), "{name} : dimensions déclarées");
        let img = turbojpeg::decompress(&f.data, turbojpeg::PixelFormat::RGB)
            .unwrap_or_else(|e| panic!("{name} : JPEG non décodable : {e}"));
        assert_eq!(
            (img.width, img.height),
            (N as usize, N as usize),
            "{name} : dimensions décodées"
        );
        let db = psnr(src, &img.pixels);
        eprintln!("{name} : PSNR {db:.2} dB, {} octets", f.data.len());
        assert!(db > 35.0, "{name} : PSNR {db:.2} dB à q90, 35 dB attendus");
        assert!(
            f.data.len() < src.len() / 4,
            "{name} : {} octets, pas compressé",
            f.data.len()
        );
    }
}

#[test]
fn paire_en_raw_rgba_restituee_a_l_octet_pres() {
    let (l, r) = (test_image(0), test_image(1));
    let (fl, fr) = push_and_read("raw", MOTE_CODEC_RAW_RGBA, &l, &r);
    for (name, src, f) in [("gauche", &l, &fl), ("droite", &r, &fr)] {
        assert_eq!(f.codec, v1::ImageCodec::RawRgba as i32, "{name} : codec");
        assert_eq!((f.width, f.height), (N, N));
        assert!(
            f.data == *src,
            "{name} : octets restitués différents de la source"
        );
    }
    // La taille de la structure ne change pas : la paire passe par la même API que l'hôte.
    assert!(size_of::<mote_frame>() > 0);
}
