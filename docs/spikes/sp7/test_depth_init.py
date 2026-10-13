# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "pillow>=10", "matplotlib>=3.8"]
# ///
"""Tests de depth_init.py sur une scène synthétique, sans casque ni GPU : uv run docs/spikes/sp7/test_depth_init.py

Un mur plan (z = 0 en Unity), des caméras qui reculent face à lui (identité en rotation, Unity) ; la profondeur et les
images RGB sont prises de la même pose. Le jeu commun est exprimé dans un repère tourné de 30° et décalé : l'alignement
doit le retrouver, et tous les points doivent retomber sur le mur dans ce repère.
"""
from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sp3"))
import depth_init as di  # noqa: E402
from test_depthlib import wall  # noqa: E402

HEADER = ("timestamp_ms,ovr_timestamp,create_pose_location_x,create_pose_location_y,create_pose_location_z,"
          "create_pose_rotation_x,create_pose_rotation_y,create_pose_rotation_z,create_pose_rotation_w,"
          "fov_left_angle_tangent,fov_right_angle_tangent,fov_top_angle_tangent,fov_down_angle_tangent,"
          "near_z,far_z,width,height")
T0_US = 1_791_367_700_000_000
ANG = math.radians(30)
R_SIM = np.array([[math.cos(ANG), 0, math.sin(ANG)], [0, 1, 0], [-math.sin(ANG), 0, math.cos(ANG)]])
T_SIM = np.array([0.5, -0.2, 1.0])
COLORS = {"LEFT": (200, 40, 40), "RIGHT": (40, 40, 200)}


def rot_to_qvec(m: np.ndarray) -> tuple:
    """(w, x, y, z), méthode de Shepperd : robuste aux rotations de 180° (w = 0)."""
    t = m[0, 0] + m[1, 1] + m[2, 2]
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        return (0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s)
    i = int(np.argmax([m[0, 0], m[1, 1], m[2, 2]]))
    j, k = (i + 1) % 3, (i + 2) % 3
    s = math.sqrt(1.0 + m[i, i] - m[j, j] - m[k, k]) * 2
    q = [0.0, 0.0, 0.0]
    q[i] = 0.25 * s
    q[j] = (m[j, i] + m[i, j]) / s
    q[k] = (m[k, i] + m[i, k]) / s
    return ((m[k, j] - m[j, k]) / s, *q)


def make(root: Path) -> tuple[Path, Path, list[float]]:
    nsdata, session = root / "nsdata", root / "session"
    (nsdata / "images").mkdir(parents=True)
    (nsdata / "headset" / "sparse" / "0").mkdir(parents=True)
    W = H = 64
    (nsdata / "headset" / "sparse" / "0" / "cameras.txt").write_text(f"1 PINHOLE {W} {H} 32 32 32 32\n")
    lines, train, test, test_t = [], [], [], []
    rows = {"left": [HEADER], "right": [HEADER]}
    k = 0
    for i, t in enumerate(np.arange(0.0, 4.0, 0.2)):
        dist = 1.0 + 0.4 * t                                          # recule de 0,4 m/s
        # pose caméra Unity : (0, 1.6, -dist), regarde +Z ; canonique (OpenCV) puis repère du jeu commun
        x, y = 0.4 * math.sin(1.5 * t), 1.6 + 0.1 * math.cos(t)       # trajectoire non rectiligne
        C_rh = np.array([x, y, dist])                                 # Z inversé
        R_cv = np.diag([1.0, -1.0, -1.0]) @ np.eye(3)                 # S I S diag(1,-1,-1) = diag(1,-1,-1)
        R_c2w = R_SIM @ np.diag([1.0, 1.0, -1.0]) @ np.eye(3) @ np.diag([1.0, 1.0, -1.0]) @ np.diag([1.0, -1.0, -1.0])
        C = R_SIM @ C_rh + T_SIM
        R_w2c = R_c2w.T
        tvec = -R_w2c @ C
        for eye in ("LEFT", "RIGHT"):
            ts = T0_US + int(round(t * 1e6)) + (0 if eye == "LEFT" else 1)
            name = f"{eye}_{ts}.png"
            Image.new("RGB", (W, H), COLORS[eye]).save(nsdata / "images" / name)
            q = rot_to_qvec(R_w2c)
            lines += [f"{len(lines) // 2 + 1} {q[0]} {q[1]} {q[2]} {q[3]} {tvec[0]} {tvec[1]} {tvec[2]} 1 {name}", ""]
            (test if i % 5 == 4 else train).append(name)
            if i % 5 == 4:
                test_t.append(t)
        # cartes de profondeur aux mêmes instants, poses Unity
        for e, eye in (("left", "LEFT"), ("right", "RIGHT")):
            (session / f"{e}_depth").mkdir(parents=True, exist_ok=True)
            ts_ms = (T0_US + int(round(t * 1e6))) // 1000
            wall(dist, W=32, H=32, tans=(1.0, 1.0, 1.0, 1.0)).tofile(session / f"{e}_depth" / f"{ts_ms}.raw")
            rows[e].append(f"{ts_ms},{100 + t:.3f},{x},{y},{-dist},0,0,0,1,1,1,1,1,0.1,Infinity,32,32")
        k += 1
    (nsdata / "headset" / "sparse" / "0" / "images.txt").write_text("\n".join(lines) + "\n")
    (nsdata / "train_list.txt").write_text("\n".join(train) + "\n")
    (nsdata / "test_list.txt").write_text("\n".join(test) + "\n")
    for e in rows:
        (session / f"{e}_depth_descriptors.csv").write_text("\n".join(rows[e]) + "\n", encoding="utf-8")
    return session, nsdata, test_t


def test_helpers():
    z = np.full((6, 6), 2.0)
    z[:, 3:] = 3.0                                                     # marche de 1 m
    m = di.edge_mask(z, 0.03)
    assert not m[:, 2].any() and not m[:, 3].any() and m[:, 0].all() and m[:, 5].all()
    src = np.random.default_rng(0).normal(size=(50, 3))
    s, R, t = di.umeyama(src, 1.5 * src @ R_SIM.T + T_SIM)
    assert abs(s - 1.5) < 1e-9 and np.allclose(R, R_SIM) and np.allclose(t, T_SIM)
    xyz = np.array([[0.01, 0, 0], [0.02, 0, 0], [0.5, 0, 0]])
    keep = di.first_per_voxel(xyz, np.array([2.0, 1.0, 3.0]), voxel=0.1)
    assert keep.tolist() == [1, 2]                                     # le premier vu de chaque voxel, par t


def test_build_on_synthetic_wall():
    with tempfile.TemporaryDirectory() as d:
        session, nsdata, test_t = make(Path(d))
        r = di.build(session, nsdata, stride=2, voxel=0.01, holdout_margin=0.05, match_s=0.06, log=lambda *_: None)
        al = r["align"]
        assert abs(al["scale"] - 1) < 1e-6 and abs(al["rotation_deg"] - 30) < 1e-3 and al["residual_median_m"] < 1e-6, al
        n = R_SIM @ np.array([0.0, 0.0, 1.0])                          # normale du mur dans le repère du jeu commun
        off = r["xyz"] @ n - T_SIM @ n
        assert np.abs(off).max() < 2e-3, np.abs(off).max()             # tous les points sur le mur
        assert r["n_frames"] == 2 * (20 - len(set(test_t)))                 # cartes prises au hold-out exclues
        assert set(map(tuple, np.round(r["rgb"] * 255).astype(int))) <= {COLORS["LEFT"], COLORS["RIGHT"]}
        assert np.all(np.diff(r["t"]) >= 0) and r["t"].min() >= 0      # ordre de première vue, pour le flux
        out = Path(d) / "out"
        assert di.main(["--session", str(session), "--nsdata", str(nsdata), "--out", str(out), "--stride", "2",
                        "--voxel", "0.01", "--holdout-margin", "0.05"]) == 0
        for f in ("init.npz", "init.ply", "init_views.png", "init.json"):
            assert (out / f).exists(), f
        with np.load(out / "init.npz") as z:
            assert z["xyz"].shape[1] == 3 and len(z["xyz"]) == len(z["rgb"]) == len(z["t"]) > 100


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)}/{len(tests)} tests passent")
