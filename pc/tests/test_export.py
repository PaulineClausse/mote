import json
from pathlib import Path

import pytest

from mote import geometry as g
from mote.ingest.replay import ingest_replay
from mote.tools.export import export_colmap, export_nerfstudio

SAMPLE = Path(__file__).resolve().parent / "data" / "sample_session.mcap"
POINT = [0.4, 1.5, -2.0]          # un point devant les caméras, repère canonique (monde main droite)


@pytest.fixture(scope="module")
def dataset(tmp_path_factory) -> Path:
    d = tmp_path_factory.mktemp("ds") / "dataset"
    ingest_replay(SAMPLE, d)
    return d


def project_cv(c2w, fx, fy, cx, cy, x):
    w2c = g.invert_rigid(c2w)
    p = [sum(w2c[i][k] * x[k] for k in range(3)) + w2c[i][3] for i in range(3)]
    return fx * p[0] / p[2] + cx, fy * p[1] / p[2] + cy, p[2]


def test_nerfstudio_transforms(dataset, tmp_path):
    path = export_nerfstudio(dataset, tmp_path / "ns")
    t = json.loads(path.read_text(encoding="utf-8"))
    frames = [json.loads(line) for line in (dataset / "frames.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(t["frames"]) == len(frames) == 14
    for fr, src in zip(t["frames"], frames):
        assert (path.parent / fr["file_path"]).exists()
        for k in ("fl_x", "fl_y", "cx", "cy", "w", "h"):
            assert k in fr
        # caméra OpenGL de nerfstudio : x droite, y haut, regard -z ; même pixel que la caméra OpenCV
        gl = fr["transform_matrix"]
        w2c = g.invert_rigid(gl)
        p = [sum(w2c[i][k] * POINT[k] for k in range(3)) + w2c[i][3] for i in range(3)]
        u, v = fr["fl_x"] * p[0] / -p[2] + fr["cx"], fr["fl_y"] * -p[1] / -p[2] + fr["cy"]
        u2, v2, z = project_cv(src["world_from_camera"], src["fx"], src["fy"], src["cx"], src["cy"], POINT)
        assert z > 0 and abs(u - u2) < 1e-9 and abs(v - v2) < 1e-9
    assert t["camera_model"] == "OPENCV" and t.get("ply_file_path") is None


def parse_colmap(d: Path):
    cams = {}
    for line in (d / "cameras.txt").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            cid, model, w, h, *params = line.split()
            cams[int(cid)] = (model, int(w), int(h), [float(x) for x in params])
    imgs = []
    lines = [ln for ln in (d / "images.txt").read_text(encoding="utf-8").splitlines() if not ln.startswith("#")]
    for head, pts in zip(lines[0::2], lines[1::2]):
        iid, qw, qx, qy, qz, tx, ty, tz, cid, name = head.split()
        imgs.append((int(iid), (float(qx), float(qy), float(qz), float(qw)), [float(tx), float(ty), float(tz)],
                     int(cid), name, pts))
    return cams, imgs


def test_colmap_text_model(dataset, tmp_path):
    d = export_colmap(dataset, tmp_path / "colmap")
    assert (d / "points3D.txt").exists()
    cams, imgs = parse_colmap(d)
    frames = [json.loads(line) for line in (dataset / "frames.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(imgs) == 14 and len(cams) == 2                          # une caméra par œil et par intrinsèques
    for (iid, q, t, cid, name, pts), src in zip(imgs, frames):
        model, w, h, params = cams[cid]
        assert model == "PINHOLE" and (w, h) == (64, 48) and name == src["file"].removeprefix("images/")
        assert pts == ""
        w2c = g.pose_matrix(tuple(t), q)                               # COLMAP : monde -> caméra, OpenCV
        c2w = g.invert_rigid(w2c)
        u, v, _ = project_cv(c2w, *params, POINT)
        u2, v2, _ = project_cv(src["world_from_camera"], src["fx"], src["fy"], src["cx"], src["cy"], POINT)
        assert abs(u - u2) < 1e-6 and abs(v - v2) < 1e-6


def test_pycolmap_reads_the_model(dataset, tmp_path):
    """Lu par COLMAP lui-même (pycolmap), si installé : `uv run --project pc --group dev --with pycolmap pytest`."""
    pycolmap = pytest.importorskip("pycolmap")
    rec = pycolmap.Reconstruction(str(export_colmap(dataset, tmp_path / "colmap")))
    assert rec.num_images() == 14 and rec.num_cameras() == 2 and rec.num_points3D() == 0
    frames = [json.loads(line) for line in (dataset / "frames.jsonl").read_text(encoding="utf-8").splitlines()]
    centers = sorted((img.name, list(img.projection_center())) for img in rec.images.values())
    want = sorted((f["file"].removeprefix("images/"), [f["world_from_camera"][i][3] for i in range(3)]) for f in frames)
    for (n1, c1), (n2, c2) in zip(centers, want):
        assert n1 == n2 and all(abs(a - b) < 1e-9 for a, b in zip(c1, c2))


def test_exports_are_deterministic(dataset, tmp_path):
    a = export_nerfstudio(dataset, tmp_path / "a").read_bytes()
    b = export_nerfstudio(dataset, tmp_path / "b").read_bytes()
    assert a == b
    ca, cb = export_colmap(dataset, tmp_path / "ca"), export_colmap(dataset, tmp_path / "cb")
    assert all((ca / f).read_bytes() == (cb / f).read_bytes() for f in ("cameras.txt", "images.txt", "points3D.txt"))
