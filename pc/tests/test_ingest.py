import json
import math
import sys
from pathlib import Path

import pytest
from PIL import Image

from mote import geometry as g
from mote.ingest.replay import ingest_replay
from mote.session import missing_seqs, read_session

HERE = Path(__file__).resolve().parent
SAMPLE = HERE / "data" / "sample_session.mcap"
sys.path.insert(0, str(HERE))
import make_sample  # noqa: E402


def frames(d: Path) -> list[dict]:
    return [json.loads(line) for line in (d / "frames.jsonl").read_text(encoding="utf-8").splitlines()]


def tree(d: Path) -> dict[str, bytes]:
    return {p.relative_to(d).as_posix(): p.read_bytes() for p in sorted(d.rglob("*")) if p.is_file()}


@pytest.fixture(scope="module")
def out(tmp_path_factory) -> Path:
    d = tmp_path_factory.mktemp("ds") / "dataset"
    ingest_replay(SAMPLE, d)
    return d


def test_sample_is_complete():
    s = read_session(SAMPLE)
    assert missing_seqs(s) == {} and len(s.images) == 16 and len(s.poses) == 201


def test_two_runs_are_bit_identical(out, tmp_path):
    other = tmp_path / "again"
    ingest_replay(SAMPLE, other)
    assert tree(out) == tree(other)


def test_longest_segment_is_kept(out):
    fr = frames(out)
    assert [(f["pair_id"], f["camera"]) for f in fr] == [(k, c) for k in range(1, 8) for c in ("left", "right")]
    assert {f["segment"] for f in fr} == {1}
    info = json.loads((out / "session.json").read_text(encoding="utf-8"))
    assert info["kept_segment"] == 1 and info["dropped"]["other_segments"] == 2
    assert [s["images"] for s in info["segments"]] == [2, 14]
    assert info["pose_conversion"] == g.POSE_CONVERSION and info["source"]["file"] == "sample_session.mcap"


def test_images_are_written_and_decodable(out):
    s = read_session(SAMPLE)
    raw = {(m.msg.pair_id, m.topic.split("/")[2]): m.msg for m in s.images}
    for f in frames(out):
        p = out / f["file"]
        src = raw[(f["pair_id"], f["camera"])]
        img = Image.open(p)
        img.load()
        assert img.size == (f["width"], f["height"]) == (64, 48)
        if f["codec"] == "JPEG":
            assert p.suffix == ".jpg" and p.read_bytes() == src.data          # JPEG d'origine, sans réencodage
        else:
            assert p.suffix == ".png" and img.convert("RGBA").tobytes() == src.data   # RAW_RGBA sans perte


def test_intrinsics_are_scaled_to_the_image(out):
    f = frames(out)[0]
    assert (f["fx"], f["fy"], f["cx"], f["cy"]) == (50.0, 50.0, 32.0, 24.0)    # 128 x 96 déclaré, 64 x 48 reçu
    assert f["model"] == "PINHOLE" and f["dist"] == []


def test_poses_are_canonical_and_interpolated(out):
    for f in frames(out):
        t = (f["t_ns"] - make_sample.T0) / 1e9
        p = make_sample.camera_pose(t, f["camera"])
        want = g.unity_to_canonical(g.pose_matrix((p.px, p.py, p.pz), (p.qx, p.qy, p.qz, p.qw)))
        got = f["world_from_camera"]
        assert all(abs(got[i][j] - want[i][j]) < 1e-9 for i in range(4) for j in range(4)), f["file"]
        assert f["pose_source"] == ("hmd_interp" if (f["pair_id"], f["camera"]) == (3, "left") else "frame")


def test_refuses_a_non_empty_dataset(out):
    with pytest.raises(FileExistsError):
        ingest_replay(SAMPLE, out)


def test_interpolation_between_samples(tmp_path):
    # même session, mais la pose du casque n'est connue que toutes les 50 ms : l'image gauche de la paire 3
    # (t = 0,7 s) tombe pile, celle-ci doit donc rester exacte ; on vérifie ensuite un instant intermédiaire.
    from mote.ingest.replay import interpolate_hmd
    from mote.v1 import mote_pb2 as pb
    samples = [pb.PoseSample(t_ns=k * 50_000_000, convention=pb.UNITY, world_from_hmd=make_sample.hmd_pose(k * 0.05))
               for k in range(5)]
    m = interpolate_hmd(samples, 75_000_000, max_gap_ns=100_000_000)
    p = make_sample.hmd_pose(0.075)
    want = g.pose_matrix((p.px, p.py, p.pz), (p.qx, p.qy, p.qz, p.qw))
    assert all(abs(m[i][j] - want[i][j]) < 1e-9 for i in range(4) for j in range(4))
    assert interpolate_hmd(samples, 75_000_000, max_gap_ns=10_000_000) is None       # trou trop long
    assert interpolate_hmd(samples, 500_000_000, max_gap_ns=100_000_000) is None      # hors de la plage
    assert not math.isnan(m[0][3])
