//! Critère de WP-05 (TASK-3159) : le fichier MCAP de session, tel que l'API C le laisse dans local_dir.

mod common;

use std::collections::{BTreeMap, BTreeSet};
use std::ffi::CString;
use std::io::{BufRead, BufReader};
use std::process::{Command, Stdio};
use std::ptr;
use std::time::Duration;

use common::*;
use mcap::read::Options;
use mote::*;
use mote_proto::v1;
use mote_proto::Message as _;

/// Canaux de SPEC-64c5 §9.1.
const CHANNELS: [&str; 11] = [
    "/session/info",
    "/cam/left/frame",
    "/cam/right/frame",
    "/cam/left/intrinsics",
    "/cam/right/intrinsics",
    "/pose/hmd",
    "/depth/left",
    "/depth/right",
    "/events",
    "/stats",
    "/session/end",
];

struct Read {
    /// Canal -> (nom du schéma, encodage du schéma, encodage des messages).
    channels: BTreeMap<String, (String, String, String)>,
    /// Canal -> seq dans l'ordre du fichier, et les messages bruts.
    seqs: BTreeMap<String, Vec<u32>>,
    data: BTreeMap<String, Vec<Vec<u8>>>,
    /// Le flux s'est arrêté sur une erreur (fichier tronqué).
    truncated: bool,
}

/// Lecture linéaire, sans index : c'est ce qui reste possible sur un fichier dont l'écriture a été interrompue.
fn read(path: &std::path::Path) -> Read {
    let buf = std::fs::read(path).unwrap();
    let mut r = Read {
        channels: BTreeMap::new(),
        seqs: BTreeMap::new(),
        data: BTreeMap::new(),
        truncated: false,
    };
    let opts = Options::IgnoreEndMagic.into();
    for m in mcap::MessageStream::new_with_options(&buf, opts).unwrap() {
        let m = match m {
            Ok(m) => m,
            Err(_) => {
                r.truncated = true;
                break;
            }
        };
        let topic = m.channel.topic.clone();
        let schema = m.channel.schema.as_ref().expect("canal sans schéma");
        r.channels.insert(
            topic.clone(),
            (
                schema.name.clone(),
                schema.encoding.clone(),
                m.channel.message_encoding.clone(),
            ),
        );
        r.seqs.entry(topic.clone()).or_default().push(m.sequence);
        r.data.entry(topic).or_default().push(m.data.into_owned());
    }
    r
}

/// Canaux déclarés dans le résumé du fichier, messages ou non.
fn declared_channels(path: &std::path::Path) -> BTreeSet<String> {
    let buf = std::fs::read(path).unwrap();
    let summary = mcap::Summary::read(&buf).unwrap().expect("pas de résumé");
    summary.channels.values().map(|c| c.topic.clone()).collect()
}

fn assert_contiguous(r: &Read) {
    for (topic, seqs) in &r.seqs {
        let want: Vec<u32> = (0..seqs.len() as u32).collect();
        assert_eq!(seqs, &want, "seq de {topic} non contigus à partir de 0");
    }
}

/// Pousse une session complète : deux intrinsèques, `pairs` paires, des poses, la profondeur des deux yeux, un
/// événement de l'hôte.
unsafe fn push_session(ctx: *mut mote_ctx, pairs: usize, poses: usize) {
    let dist = [0.1, -0.05, 0.0, 0.0];
    for cam in 0..2 {
        assert_eq!(
            mote_set_intrinsics(ctx, &intrinsics(cam, &dist)),
            mote_status::MOTE_OK
        );
    }
    let px = vec![100u8; (W * H * 4) as usize];
    let dpx = [0u8; 64];
    let t0 = mote_now_ns();
    for k in 0..pairs as i64 {
        let t = t0 + k * 200_000_000;
        let mut kept = 0;
        assert_eq!(
            mote_push_pair(ctx, &frame(&px, t), &frame(&px, t), &mut kept),
            mote_status::MOTE_OK
        );
        assert_eq!(kept, 1);
        for eye in 0..2 {
            assert_eq!(
                mote_push_depth(ctx, &depth(eye, &dpx, t)),
                mote_status::MOTE_OK
            );
        }
    }
    for k in 0..poses as i64 {
        let t = t0 + k * 10_000_000;
        assert_eq!(
            mote_push_hmd_pose(ctx, t, t / 1000, 5, 1, &pose(), 0),
            mote_status::MOTE_OK
        );
    }
    let d = CString::new("recentrage").unwrap();
    assert_eq!(mote_push_event(ctx, 3, d.as_ptr()), mote_status::MOTE_OK);
}

#[test]
fn apres_stop_le_fichier_porte_les_canaux_de_la_spec_et_des_seq_contigus() {
    // MOTE_KEEP_SESSION_DIR garde le fichier pour la vérification Python (mote-mcap/tests/check_session.py).
    let keep = std::env::var_os("MOTE_KEEP_SESSION_DIR").map(std::path::PathBuf::from);
    let dir = keep.clone().unwrap_or_else(|| tmp("mcap"));
    let _ = std::fs::remove_dir_all(&dir);
    let s = session(&dir);
    let mut ctx: *mut mote_ctx = ptr::null_mut();
    unsafe {
        assert_eq!(mote_create(&s.cfg, &mut ctx), mote_status::MOTE_OK);
        assert_eq!(mote_start(ctx), mote_status::MOTE_OK);
        push_session(ctx, 3, 50);
        assert_eq!(mote_stop(ctx), mote_status::MOTE_OK);
        let st = stats(ctx);
        mote_destroy(ctx);

        let path = session_file(&dir);
        assert_eq!(
            st.bytes_written,
            std::fs::metadata(&path).unwrap().len(),
            "bytes_written = taille du fichier"
        );
        assert_eq!(
            declared_channels(&path),
            CHANNELS.iter().map(|c| c.to_string()).collect()
        );

        let r = read(&path);
        assert!(!r.truncated, "fichier complet illisible jusqu'au bout");
        for (topic, (schema, enc, msg_enc)) in &r.channels {
            assert!(schema.starts_with("mote.v1."), "{topic} : schéma {schema}");
            assert_eq!(
                (enc.as_str(), msg_enc.as_str()),
                ("protobuf", "protobuf"),
                "{topic}"
            );
        }
        assert_contiguous(&r);
        let count = |t: &str| r.seqs.get(t).map_or(0, |s| s.len());
        assert_eq!(count("/session/info"), 1);
        assert_eq!(
            (count("/cam/left/frame"), count("/cam/right/frame")),
            (3, 3)
        );
        assert_eq!(
            (
                count("/cam/left/intrinsics"),
                count("/cam/right/intrinsics")
            ),
            (1, 1)
        );
        assert_eq!((count("/depth/left"), count("/depth/right")), (3, 3));
        assert_eq!(count("/pose/hmd"), 50);
        assert_eq!(count("/events"), 1);
        assert!(count("/stats") >= 1, "au moins un /stats, écrit à l'arrêt");
        assert_eq!(count("/session/end"), 1);

        let info = v1::SessionInfo::decode(&r.data["/session/info"][0][..]).unwrap();
        assert_eq!(info.schema_version, 1);
        assert_eq!(info.device_model, "Quest 3S");
        assert_eq!(info.tracking_space, "local_floor");
        assert_eq!(path.file_stem().unwrap().to_str().unwrap(), info.session_id);

        let left = v1::ImageFrame::decode(&r.data["/cam/left/frame"][1][..]).unwrap();
        let right = v1::ImageFrame::decode(&r.data["/cam/right/frame"][1][..]).unwrap();
        assert_eq!(
            left.pair_id, right.pair_id,
            "gauche et droite d'une paire partagent pair_id"
        );
        assert_eq!((left.width, left.height), (W, H));

        // /session/end annonce le dernier seq de chaque canal qui a des messages, sauf lui-même.
        let end = v1::SessionEnd::decode(&r.data["/session/end"][0][..]).unwrap();
        let announced: BTreeMap<String, u64> = end
            .channels
            .into_iter()
            .map(|c| (c.channel, c.last_seq))
            .collect();
        let expected: BTreeMap<String, u64> = r
            .seqs
            .iter()
            .filter(|(t, _)| t.as_str() != "/session/end")
            .map(|(t, s)| (t.clone(), s.len() as u64 - 1))
            .collect();
        assert_eq!(announced, expected);
    }
    if keep.is_none() {
        let _ = std::fs::remove_dir_all(dir);
    }
}

/// Processus enfant du test suivant : ouvre une session, pousse `POSES` poses, attend qu'elles soient écrites, le
/// signale sur stdout, puis continue à pousser jusqu'à être tué. Ne fait rien hors de ce rôle.
#[test]
#[ignore]
fn enfant_tue_en_cours_de_session() {
    let Some(dir) = std::env::var_os("MOTE_KILL_CHILD_DIR") else {
        return;
    };
    let s = session(std::path::Path::new(&dir));
    let mut ctx: *mut mote_ctx = ptr::null_mut();
    unsafe {
        assert_eq!(mote_create(&s.cfg, &mut ctx), mote_status::MOTE_OK);
        assert_eq!(mote_start(ctx), mote_status::MOTE_OK);
        push_session(ctx, 2, POSES);
        // Deux périodes d'écriture : tout ce qui précède est dans un chunk fermé.
        std::thread::sleep(Duration::from_millis(2500));
        println!("ECRIT");
        use std::io::Write;
        std::io::stdout().flush().unwrap();
        loop {
            let t = mote_now_ns();
            let _ = mote_push_hmd_pose(ctx, t, t, 1, 1, &pose(), 0);
            std::thread::sleep(Duration::from_millis(5));
        }
    }
}

const POSES: usize = 200;

#[test]
fn processus_tue_les_chunks_deja_ecrits_restent_lisibles() {
    let dir = tmp("kill");
    let mut child = Command::new(std::env::current_exe().unwrap())
        .args([
            "enfant_tue_en_cours_de_session",
            "--exact",
            "--ignored",
            "--nocapture",
            "--test-threads=1",
        ])
        .env("MOTE_KILL_CHILD_DIR", &dir)
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    // libtest préfixe la sortie du nom du test : on cherche le mot, avec un délai pour ne jamais bloquer.
    let out = BufReader::new(child.stdout.take().unwrap());
    let (tx, rx) = std::sync::mpsc::channel();
    std::thread::spawn(move || {
        let found = out
            .lines()
            .map_while(Result::ok)
            .any(|l| l.contains("ECRIT"));
        let _ = tx.send(found);
    });
    let signalled = rx.recv_timeout(Duration::from_secs(60)).unwrap_or(false);
    child.kill().unwrap();
    assert!(signalled, "l'enfant n'a pas signalé l'écriture");
    child.wait().unwrap();

    let path = session_file(&dir);
    let r = read(&path);
    assert_contiguous(&r);
    let count = |t: &str| r.seqs.get(t).map_or(0, |s| s.len());
    assert_eq!(count("/session/info"), 1);
    assert_eq!(
        (
            count("/cam/left/intrinsics"),
            count("/cam/right/intrinsics")
        ),
        (1, 1)
    );
    assert_eq!(
        (count("/cam/left/frame"), count("/cam/right/frame")),
        (2, 2)
    );
    assert!(
        count("/pose/hmd") >= POSES,
        "{} poses relues, {POSES} écrites avant la mort",
        count("/pose/hmd")
    );
    assert_eq!(
        count("/session/end"),
        0,
        "pas de fin de session sur un processus tué"
    );
    let _ = std::fs::remove_dir_all(dir);
}
