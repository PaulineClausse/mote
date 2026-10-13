# /// script
# requires-python = ">=3.10"
# dependencies = ["protobuf==7.35.1"]   # le runtime que demande le code généré par grpcio-tools 1.84.0
# ///
"""Test croisé de mote.v1 : chaque message est sérialisé en Rust (prost) et relu en Python, champs identiques.

  uv run proto/roundtrip_test.py

1. `cargo run --example write_fixtures` (crate proto/rust) écrit un `<nom>.bin` par message, tous champs renseignés.
2. Chaque fichier est relu avec le code Python généré (pc/mote/v1/mote_pb2.py) et comparé au même message construit
   ici, champ à champ ; le réencodage Python doit redonner les mêmes octets.
3. Couverture : chaque message du schéma a son fichier, chaque variante de Envelope.body aussi, et aucun champ n'est
   laissé à sa valeur par défaut (un champ oublié des deux côtés passerait sinon inaperçu).

Toute valeur changée ici doit l'être aussi dans proto/rust/examples/write_fixtures.rs.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pc"))
from mote.v1 import mote_pb2 as pb  # noqa: E402


def pose(k: float) -> pb.Pose3:
    return pb.Pose3(px=-1.5 * k, py=0.1 * k, pz=2.25 * k, qx=0.5, qy=-0.5, qz=0.5, qw=-0.5)


def expected() -> dict:
    hello = pb.Hello(session_id="s-é1", auth_token="jeton", schema_version=1)
    session_info = pb.SessionInfo(
        schema_version=1, session_id="20261007_120820", start_unix_ns=1_791_367_700_123_456_789,
        start_t_ns=123_456_789_012, device_model="Quest 3S", os_build="v83 ✓", sdk_versions='{"mruk":"207.0.0"}',
        host_kind="unity", core_version="0.1.0", tracking_space="Stage", config_json='{"fps":10}')
    image = pb.ImageFrame(
        pair_id=18_000_000_000_000_000_001, t_ns=123_456_789_012, src_time_ns=-42, src_domain=pb.UNIX,
        width=1280, height=1280, codec=pb.JPEG, data=bytes([0xff, 0xd8, 0x00, 0x80, 0xfe, 0xff, 0xd9]),
        convention=pb.UNITY, world_from_camera=pose(1.0), exposure_ns=8_333_333, iso=400, blur_score=12.5)
    intrinsics = pb.CameraIntrinsics(
        width=1280, height=1280, fx=868.68, fy=868.7, cx=642.0, cy=640.6, model=pb.OPENCV,
        dist=[0.1, -0.02, 0.001, -0.0005, 0.0], convention=pb.OPENXR, hmd_from_camera=pose(0.01))
    pose_sample = pb.PoseSample(t_ns=123_456_789_013, src_time_ns=987_654_321, src_domain=pb.XR_RUNTIME,
                                convention=pb.UNITY, world_from_hmd=pose(2.0), predicted=True)
    depth = pb.DepthFrame(
        t_ns=123_456_789_014, src_time_ns=555, src_domain=pb.MONOTONIC, width=320, height=320,
        encoding=pb.F32_RAW, data=bytes(range(256)), convention=pb.OPENXR, world_from_depth=pose(-1.0),
        fov_left_tan=-1.25, fov_right_tan=1.0, fov_top_tan=0.75, fov_down_tan=-0.875,
        near_z=0.1, far_z=float("inf"), min_depth=0.2, max_depth=4.5, src_predicted_display_time_ns=600)
    event = pb.Event(t_ns=7, type=pb.RECENTER, detail="origine déplacée")
    stats = pb.Stats(t_ns=8, pairs_pushed=100, pairs_kept=90, pairs_dropped=10, bytes_written=5_000_000_000,
                     bytes_sent=4_999_999_999, net_mbps=87.5, encode_ms_avg=6.25, live_queue_fill=0.5)
    session_end = pb.SessionEnd(channels=[pb.ChannelEnd(channel="/cam/left/frame", last_seq=465),
                                          pb.ChannelEnd(channel="/pose/hmd", last_seq=10_000)])
    resend = pb.ResendRequest(channel="/depth/left", first_seq=10, last_seq=20)
    out = {
        "Pose3": pose(1.0), "PoseSample": pose_sample, "ImageFrame": image, "CameraIntrinsics": intrinsics,
        "DepthFrame": depth, "Event": event, "Stats": stats, "SessionInfo": session_info,
        "ChannelEnd": session_end.channels[0], "SessionEnd": session_end, "Hello": hello,
        "ResendRequest": resend, "Control": pb.Control(resend=resend),
    }
    bodies = {"hello": hello, "session_info": session_info, "image": image, "intrinsics": intrinsics,
              "pose": pose_sample, "depth": depth, "event": event, "stats": stats, "session_end": session_end}
    for name, body in bodies.items():
        env = pb.Envelope(channel="/test", seq=3)
        getattr(env, name).CopyFrom(body)
        out[f"Envelope.{name}"] = env
    return out


def unset_fields(m, path: str = "") -> list[str]:
    """Champs laissés à leur valeur par défaut, récursivement ; dans un oneof, il suffit d'une variante."""
    missing = []
    for f in m.DESCRIPTOR.fields:
        name = f"{path}{f.name}"
        oneof = f.containing_oneof
        if oneof is not None and not oneof.name.startswith("_"):     # vrai oneof (pas un champ « optional »)
            if m.WhichOneof(oneof.name) is None and f is oneof.fields[0]:
                missing.append(f"{path}{oneof.name}")
            if m.WhichOneof(oneof.name) == f.name:
                missing += unset_fields(getattr(m, f.name), name + ".")
            continue
        v = getattr(m, f.name)
        if f.is_repeated:
            if not len(v):
                missing.append(name)
            elif f.message_type is not None:
                for i, sub in enumerate(v):
                    missing += unset_fields(sub, f"{name}[{i}].")
        elif f.message_type is not None:
            missing += unset_fields(v, name + ".") if m.HasField(f.name) else [name]
        elif f.has_presence:
            if not m.HasField(f.name):
                missing.append(name)
        elif v == f.default_value:
            missing.append(name)
    return missing


def main() -> int:
    exp = expected()
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["cargo", "run", "--quiet", "--manifest-path", str(ROOT / "proto" / "rust" / "Cargo.toml"),
                        "--example", "write_fixtures", "--", d], check=True)
        written = {p.stem: p.read_bytes() for p in Path(d).glob("*.bin")}

    failures = []
    types = set(pb.DESCRIPTOR.message_types_by_name)
    covered = {name.split(".")[0] for name in exp}
    if types - covered:
        failures.append(f"messages du schéma sans exemplaire : {sorted(types - covered)}")
    variants = {f.name for f in pb.Envelope.DESCRIPTOR.oneofs_by_name["body"].fields}
    tested = {name.split(".", 1)[1] for name in exp if name.startswith("Envelope.")}
    if variants - tested:
        failures.append(f"variantes de Envelope.body sans exemplaire : {sorted(variants - tested)}")
    if set(written) != set(exp):
        failures.append(f"fichiers Rust {sorted(set(written) ^ set(exp))} : écrits d'un seul côté")

    for name in sorted(set(written) & set(exp)):
        want = exp[name]
        got = type(want)()
        got.ParseFromString(written[name])
        problems = []
        if unset_fields(want):
            problems.append(f"champs non renseignés : {unset_fields(want)}")
        if got != want:
            problems.append(f"champs différents :\n  Rust   : {got}\n  Python : {want}")
        if not problems and got.SerializeToString(deterministic=True) != written[name]:
            problems.append("le réencodage Python ne redonne pas les octets de Rust")
        print(("ok    " if not problems else "ECHEC ") + name)
        failures += [f"{name} : {p}" for p in problems]

    for f in failures:
        print(f, file=sys.stderr)
    print(f"{len(exp)} messages, {len(failures)} échec(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
