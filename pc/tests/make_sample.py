"""Écrit tests/data/sample_session.mcap, la session d'exemple versionnée des tests de l'ingest (WP-07).

  uv run --project pc python pc/tests/make_sample.py

Le fichier est versionné : les tests lisent ces octets-là, pas une régénération (l'encodeur JPEG de Pillow peut changer).
Contenu, tout en convention Unity (ce que l'hôte stocke, ADR-6ded) :
- /session/info, /session/end ;
- /cam/{left,right}/intrinsics : déclarées en 128 x 96 alors que les images font 64 x 48 (mise à l'échelle) ;
  extrinsèques hmd_from_camera à ±3,2 cm ;
- /pose/hmd à 100 Hz sur 2 s, casque qui avance en x et tourne autour de y ;
- /cam/{left,right}/frame : 8 paires à 5 Hz (t = 0,1 ; 0,3 ; ... ; 1,5 s), JPEG 64 x 48, pose par image ;
  exceptions : la gauche de la paire 3 sans pose (interpolée à l'ingest), la droite de la paire 7 en RAW_RGBA ;
- /events : RECENTER à t = 0,2 s, donc deux segments ; le plus long (paires 1 à 7) est gardé.
"""
from __future__ import annotations

import io
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from google.protobuf import descriptor_pb2  # noqa: E402
from mcap.writer import CompressionType, Writer  # noqa: E402
from PIL import Image  # noqa: E402

from mote.v1 import mote_pb2 as pb  # noqa: E402

OUT = HERE / "data" / "sample_session.mcap"
T0 = 1_000_000_000_000                       # horloge mote (ns)
W, H = 64, 48
OFFSET = {"left": -0.032, "right": 0.032}


def hmd_pose(t: float) -> pb.Pose3:
    """Le casque avance en x de 0,5 m/s, à 1,6 m de haut, et tourne autour de y de 0,2 rad/s."""
    a = 0.2 * t
    return pb.Pose3(px=0.5 * t, py=1.6, pz=0.0, qx=0.0, qy=math.sin(a / 2), qz=0.0, qw=math.cos(a / 2))


def camera_pose(t: float, eye: str) -> pb.Pose3:
    """world_from_camera = world_from_hmd * hmd_from_camera (décalage en x local, sans rotation)."""
    h = hmd_pose(t)
    a = 0.2 * t
    dx = OFFSET[eye]
    # rotation autour de y appliquée au décalage (dx, 0, 0) : (dx cos a, 0, -dx sin a)
    return pb.Pose3(px=h.px + dx * math.cos(a), py=h.py, pz=h.pz - dx * math.sin(a),
                    qx=h.qx, qy=h.qy, qz=h.qz, qw=h.qw)


def image(k: int, eye: str) -> Image.Image:
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        for x in range(W):
            px[x, y] = ((x * 4 + k * 20) % 256, (y * 5) % 256, 200 if eye == "left" else 60)
    return img


def fds() -> bytes:
    fdp = descriptor_pb2.FileDescriptorProto()
    pb.DESCRIPTOR.CopyToProto(fdp)
    return descriptor_pb2.FileDescriptorSet(file=[fdp]).SerializeToString()


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = fds()
    with OUT.open("wb") as f:
        w = Writer(f, compression=CompressionType.ZSTD)
        w.start(profile="", library="mote-tests")
        schemas: dict[str, int] = {}
        channels: dict[str, int] = {}
        seq: dict[str, int] = {}

        def put(topic: str, msg, t_ns: int) -> None:
            name = f"mote.v1.{type(msg).__name__}"
            if name not in schemas:
                schemas[name] = w.register_schema(name=name, encoding="protobuf", data=data)
            if topic not in channels:
                channels[topic] = w.register_channel(topic=topic, message_encoding="protobuf", schema_id=schemas[name])
            n = seq.get(topic, 0)
            w.add_message(channel_id=channels[topic], log_time=t_ns, publish_time=t_ns, sequence=n,
                          data=msg.SerializeToString())
            seq[topic] = n + 1

        put("/session/info", pb.SessionInfo(
            schema_version=1, session_id="sample", start_unix_ns=1_791_367_700_000_000_000, start_t_ns=T0,
            device_model="Quest 3S", host_kind="unity", core_version="tests", tracking_space="Stage"), T0)
        for eye in ("left", "right"):
            put(f"/cam/{eye}/intrinsics", pb.CameraIntrinsics(
                width=2 * W, height=2 * H, fx=100.0, fy=100.0, cx=64.0, cy=48.0, model=pb.PINHOLE,
                convention=pb.UNITY, hmd_from_camera=pb.Pose3(px=OFFSET[eye], qw=1.0)), T0)
        events = [(0.2, pb.Event(t_ns=T0 + 200_000_000, type=pb.RECENTER, detail="test"))]
        frames = [(0.1 + 0.2 * k, k) for k in range(8)]
        poses = [round(0.01 * i, 2) for i in range(201)]
        # messages entrelacés par ordre de temps, comme les écrirait le core
        timeline = ([(t, 0, ("pose", t)) for t in poses] + [(t, 1, ("event", e)) for t, e in events]
                    + [(t, 2, ("pair", k)) for t, k in frames])
        for t, _, (kind, v) in sorted(timeline, key=lambda x: (x[0], x[1])):
            t_ns = T0 + round(t * 1e9)
            if kind == "pose":
                put("/pose/hmd", pb.PoseSample(t_ns=t_ns, src_time_ns=round(t * 1e9) + 5, src_domain=pb.XR_RUNTIME,
                                               convention=pb.UNITY, world_from_hmd=hmd_pose(t)), t_ns)
            elif kind == "event":
                put("/events", v, t_ns)
            else:
                for eye in ("left", "right"):
                    f_ = pb.ImageFrame(pair_id=v, t_ns=t_ns, src_time_ns=1_791_367_700_000_000_000 + t_ns - T0,
                                       src_domain=pb.UNIX, width=W, height=H, convention=pb.UNITY, blur_score=1.5)
                    img = image(v, eye)
                    if v == 7 and eye == "right":
                        f_.codec = pb.RAW_RGBA
                        f_.data = img.convert("RGBA").tobytes()
                    else:
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=90)
                        f_.codec, f_.data = pb.JPEG, buf.getvalue()
                    if not (v == 3 and eye == "left"):
                        f_.world_from_camera.CopyFrom(camera_pose(t, eye))
                    put(f"/cam/{eye}/frame", f_, t_ns)
        end = pb.SessionEnd(channels=[pb.ChannelEnd(channel=c, last_seq=n - 1) for c, n in sorted(seq.items())])
        put("/session/end", end, T0 + 2_000_000_000)
        w.finish()
    print(f"{OUT} : {OUT.stat().st_size} octets, {sum(seq.values())} messages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
