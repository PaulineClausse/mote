#!/usr/bin/env python3
"""Tests de depthlib.py sur données synthétiques, sans casque : python test_depthlib.py (numpy seul)."""
from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import depthlib as dl  # noqa: E402


def raw_of(z, near, far):
    """Inverse de la linéarisation : la valeur brute [0, 1] du tampon de profondeur OpenGL pour une distance z."""
    if math.isinf(far):
        ndc = 1.0 - 2.0 * near / z
    else:
        ndc = (far + near) / (far - near) - 2.0 * far * near / ((far - near) * z)
    return (ndc + 1.0) / 2.0


def wall(dist, W=64, H=48, tans=(1.0, 1.2, 0.9, 1.1), near=0.1, far=math.inf, tilt_deg=0.0):
    """Carte brute d'un mur plan à `dist` m devant la caméra, incliné de `tilt_deg` autour de l'axe vertical."""
    K = dl.intrinsics(W, H, *tans)
    u, v = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
    rx, ry = (u - K["cx"]) / K["fx"], (v - K["cy"]) / K["fy"]
    t = math.radians(tilt_deg)
    n = np.array([math.sin(t), 0.0, math.cos(t)])                 # normale du mur, repère OpenCV
    z = dist / (n[0] * rx + n[1] * ry + n[2])                      # intersection rayon (rx, ry, 1) * z avec n.p = dist
    return np.vectorize(lambda zz: raw_of(zz, near, far))(z).astype(np.float32)


def test_linearize_roundtrip():
    for far in (math.inf, 50.0):
        z = np.array([0.25, 0.5, 1.0, 2.0, 3.0, 4.5])
        d = np.array([raw_of(x, 0.1, far) for x in z], dtype=np.float32)
        back = dl.linearize(d, 0.1, far)
        assert np.allclose(back, z, rtol=1e-3), (far, back)
    out = dl.linearize(np.array([0.0, 1.0, -0.1, np.nan], dtype=np.float32), 0.1, math.inf)
    assert np.isnan(out).all()                                     # hors de ]0, 1[ : invalide
    assert np.isinf(dl.parse_float("Infinity")) and np.isinf(dl.parse_float("∞")) and dl.parse_float("0,5") == 0.5


def test_intrinsics_follow_tangents():
    K = dl.intrinsics(100, 50, 1.0, 3.0, 1.0, 1.0)                # champ deux fois plus large à droite
    assert K["fx"] == 25.0 and K["cx"] == 25.0 and K["fy"] == 25.0 and K["cy"] == 25.0
    # le bord gauche de l'image regarde à x/z = -tan_gauche, le bord droit à +tan_droite
    assert (0 - K["cx"]) / K["fx"] == -1.0 and (100 - K["cx"]) / K["fx"] == 3.0


def test_wall_distance_and_tilt():
    for dist in (0.5, 1.0, 2.0, 3.0):
        for tilt in (0.0, 15.0):
            d = wall(dist, tilt_deg=tilt)
            r = dl.wall_measure(d, 0.1, math.inf, (1.0, 1.2, 0.9, 1.1), crop=0.5)
            assert abs(r["dist"] - dist) < 2e-3 * dist, (dist, tilt, r)
            assert abs(r["tilt_deg"] - tilt) < 0.5, (dist, tilt, r)
            assert r["rms"] < 1e-3 and r["valid"] > 0.99


def test_wall_ignores_outliers_and_holes():
    d = wall(2.0)
    d[10:14, 20:40] = 0.0                                          # trous
    d[30:33, 10:50] = raw_of(0.8, 0.1, math.inf)                   # un objet devant le mur
    r = dl.wall_measure(d, 0.1, math.inf, (1.0, 1.2, 0.9, 1.1), crop=1.0)
    assert abs(r["dist"] - 2.0) < 0.01, r
    assert 0.95 < r["valid"] < 0.99 and r["inliers"] < r["valid"] - 0.03, r   # trous : invalides ; objet : rejeté


def test_stationary_segments():
    t = np.arange(0, 40, 0.1)
    x = np.where(t < 10, 0.0, np.where(t < 12, (t - 10) * 0.5, np.where(t < 25, 1.0, np.where(t < 27, 1.0 + (t - 25) * 0.5, 2.0))))
    x = x + 0.002 * np.sin(7 * t)                                  # balancement de tête
    pos = np.stack([x, np.zeros_like(t), np.zeros_like(t)], 1)
    segs = dl.stationary_segments(t, pos, max_speed=0.05, min_s=3.0)
    assert len(segs) == 3, segs
    assert abs(segs[0][0] - 0.0) < 1.0 and abs(segs[1][0] - 12.0) < 1.0 and abs(segs[2][1] - 39.9) < 1.0, segs


def test_session_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        s = Path(d)
        (s / "left_depth").mkdir()
        rows = ["timestamp_ms,ovr_timestamp,create_pose_location_x,create_pose_location_y,create_pose_location_z,"
                "create_pose_rotation_x,create_pose_rotation_y,create_pose_rotation_z,create_pose_rotation_w,"
                "fov_left_angle_tangent,fov_right_angle_tangent,fov_top_angle_tangent,fov_down_angle_tangent,"
                "near_z,far_z,width,height"]
        for k in range(3):
            ts = 1791367700000 + 200 * k
            wall(1.0).tofile(s / "left_depth" / f"{ts}.raw")
            rows.append(f"{ts},{100 + 0.2 * k},0,1.6,{0.1 * k},0,0,0,1,1,1.2,0.9,1.1,0.1,Infinity,64,48")
        (s / "left_depth_descriptors.csv").write_text("\n".join(rows) + "\n")
        frames = dl.load_frames(s, "left")
        assert len(frames) == 3 and frames[1]["t"] == 100.2 and math.isinf(frames[0]["far"])
        assert frames[2]["pos"].tolist() == [0.0, 1.6, 0.2]
        assert dl.load_raw(s, "left", frames[0]).shape == (48, 64)


def test_world_points_unity_pose():
    # caméra à (0, 1.6, 0) regardant +Z Unity ; un point à 2 m droit devant est à z = 2 en Unity, z = -2 en main droite
    z = np.full((3, 3), 2.0, np.float32)
    K = dl.intrinsics(3, 3, 1.0, 1.0, 1.0, 1.0)
    p = dl.world_points(z, K, np.array([0.0, 1.6, 0.0]), np.array([0.0, 0.0, 0.0, 1.0]))
    centre = p[4]
    assert np.allclose(centre, [0.0, 1.6, -2.0]), centre
    haut = p[1]                                                    # ligne 0 = haut de l'image : y monde plus grand
    assert haut[1] > 1.6


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)}/{len(tests)} tests passent")
