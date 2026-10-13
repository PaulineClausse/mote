//! Sérialise un exemplaire de chaque message mote.v1, tous champs renseignés, un fichier `<nom>.bin` par message.
//! Relu par `proto/roundtrip_test.py`, qui construit les mêmes valeurs en Python et compare champ à champ.
//!
//!   cargo run --example write_fixtures -- <dossier>
//!
//! Toute valeur changée ici doit l'être aussi dans `expected()` de roundtrip_test.py.

use std::path::PathBuf;

use mote_proto::v1::*;
use mote_proto::Message;

fn pose(k: f64) -> Pose3 {
    Pose3 { px: -1.5 * k, py: 0.1 * k, pz: 2.25 * k, qx: 0.5, qy: -0.5, qz: 0.5, qw: -0.5 }
}

fn hello() -> Hello {
    Hello { session_id: "s-é1".into(), auth_token: "jeton".into(), schema_version: 1 }
}

fn session_info() -> SessionInfo {
    SessionInfo {
        schema_version: 1,
        session_id: "20261007_120820".into(),
        start_unix_ns: 1_791_367_700_123_456_789,
        start_t_ns: 123_456_789_012,
        device_model: "Quest 3S".into(),
        os_build: "v83 ✓".into(),
        sdk_versions: r#"{"mruk":"207.0.0"}"#.into(),
        host_kind: "unity".into(),
        core_version: "0.1.0".into(),
        tracking_space: "Stage".into(),
        config_json: r#"{"fps":10}"#.into(),
    }
}

fn image() -> ImageFrame {
    ImageFrame {
        pair_id: 18_000_000_000_000_000_001, // au-delà de i64::MAX
        t_ns: 123_456_789_012,
        src_time_ns: -42,
        src_domain: TimeDomain::Unix as i32,
        width: 1280,
        height: 1280,
        codec: ImageCodec::Jpeg as i32,
        data: vec![0xff, 0xd8, 0x00, 0x80, 0xfe, 0xff, 0xd9], // octets non UTF-8, zéro compris
        convention: PoseConvention::Unity as i32,
        world_from_camera: Some(pose(1.0)),
        exposure_ns: Some(8_333_333),
        iso: Some(400),
        blur_score: 12.5,
    }
}

fn intrinsics() -> CameraIntrinsics {
    CameraIntrinsics {
        width: 1280,
        height: 1280,
        fx: 868.68,
        fy: 868.7,
        cx: 642.0,
        cy: 640.6,
        model: DistortionModel::Opencv as i32,
        dist: vec![0.1, -0.02, 0.001, -0.0005, 0.0],
        convention: PoseConvention::Openxr as i32,
        hmd_from_camera: Some(pose(0.01)),
    }
}

fn pose_sample() -> PoseSample {
    PoseSample {
        t_ns: 123_456_789_013,
        src_time_ns: 987_654_321,
        src_domain: TimeDomain::XrRuntime as i32,
        convention: PoseConvention::Unity as i32,
        world_from_hmd: Some(pose(2.0)),
        predicted: true,
    }
}

fn depth() -> DepthFrame {
    DepthFrame {
        t_ns: 123_456_789_014,
        src_time_ns: 555,
        src_domain: TimeDomain::Monotonic as i32,
        width: 320,
        height: 320,
        encoding: DepthEncoding::F32Raw as i32,
        data: (0..=255u8).collect(),
        convention: PoseConvention::Openxr as i32,
        world_from_depth: Some(pose(-1.0)),
        fov_left_tan: -1.25,
        fov_right_tan: 1.0,
        fov_top_tan: 0.75,
        fov_down_tan: -0.875,
        near_z: 0.1,
        far_z: f32::INFINITY, // SPEC-64c5 §9.5 : far_z peut valoir +infini
        min_depth: 0.2,
        max_depth: 4.5,
        src_predicted_display_time_ns: Some(600),
    }
}

fn event() -> Event {
    Event { t_ns: 7, r#type: EventType::Recenter as i32, detail: "origine déplacée".into() }
}

fn stats() -> Stats {
    Stats {
        t_ns: 8,
        pairs_pushed: 100,
        pairs_kept: 90,
        pairs_dropped: 10,
        bytes_written: 5_000_000_000, // au-delà de u32
        bytes_sent: 4_999_999_999,
        net_mbps: 87.5,
        encode_ms_avg: 6.25,
        live_queue_fill: 0.5,
    }
}

fn session_end() -> SessionEnd {
    SessionEnd {
        channels: vec![
            ChannelEnd { channel: "/cam/left/frame".into(), last_seq: 465 },
            ChannelEnd { channel: "/pose/hmd".into(), last_seq: 10_000 },
        ],
    }
}

fn envelope(body: envelope::Body) -> Envelope {
    Envelope { channel: "/test".into(), seq: 3, body: Some(body) }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let dir = PathBuf::from(std::env::args().nth(1).ok_or("usage : write_fixtures <dossier>")?);
    std::fs::create_dir_all(&dir)?;
    use envelope::Body;
    let all: Vec<(&str, Vec<u8>)> = vec![
        ("Pose3", pose(1.0).encode_to_vec()),
        ("PoseSample", pose_sample().encode_to_vec()),
        ("ImageFrame", image().encode_to_vec()),
        ("CameraIntrinsics", intrinsics().encode_to_vec()),
        ("DepthFrame", depth().encode_to_vec()),
        ("Event", event().encode_to_vec()),
        ("Stats", stats().encode_to_vec()),
        ("SessionInfo", session_info().encode_to_vec()),
        ("ChannelEnd", session_end().channels[0].encode_to_vec()),
        ("SessionEnd", session_end().encode_to_vec()),
        ("Hello", hello().encode_to_vec()),
        ("ResendRequest", ResendRequest { channel: "/depth/left".into(), first_seq: 10, last_seq: 20 }.encode_to_vec()),
        ("Control", Control { body: Some(control::Body::Resend(ResendRequest {
            channel: "/depth/left".into(), first_seq: 10, last_seq: 20 })) }.encode_to_vec()),
        ("Envelope.hello", envelope(Body::Hello(hello())).encode_to_vec()),
        ("Envelope.session_info", envelope(Body::SessionInfo(session_info())).encode_to_vec()),
        ("Envelope.image", envelope(Body::Image(image())).encode_to_vec()),
        ("Envelope.intrinsics", envelope(Body::Intrinsics(intrinsics())).encode_to_vec()),
        ("Envelope.pose", envelope(Body::Pose(pose_sample())).encode_to_vec()),
        ("Envelope.depth", envelope(Body::Depth(depth())).encode_to_vec()),
        ("Envelope.event", envelope(Body::Event(event())).encode_to_vec()),
        ("Envelope.stats", envelope(Body::Stats(stats())).encode_to_vec()),
        ("Envelope.session_end", envelope(Body::SessionEnd(session_end())).encode_to_vec()),
    ];
    for (name, bytes) in &all {
        std::fs::write(dir.join(format!("{name}.bin")), bytes)?;
    }
    println!("{} messages écrits dans {}", all.len(), dir.display());
    Ok(())
}
