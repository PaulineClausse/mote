#!/usr/bin/env python3
"""Tests de align_sim3.py sur poses synthétiques à erreur injectée connue.

Lancer :  python docs/spikes/sp0/test_align_sim3.py     (numpy seulement, sans pytest)
ou        python -m pytest docs/spikes/sp0/test_align_sim3.py
"""
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import align_sim3 as A  # noqa: E402


def make_trajectory(n=300, seed=0):
    """Trajectoire de caméra type scan de pièce : boucle ~3 m, hauteur 1,5 m, regard vers le centre."""
    rng = np.random.default_rng(seed)
    th = np.linspace(0, 2 * math.pi, n, endpoint=False)
    pos = np.stack([3 * np.cos(th), 3 * np.sin(th), 1.5 + 0.3 * np.sin(3 * th)], axis=1)
    poses = np.empty((n, 4, 4))
    for i in range(n):
        z = -pos[i] / np.linalg.norm(pos[i])          # axe optique vers le centre
        z[2] = 0.1 * rng.standard_normal()
        z /= np.linalg.norm(z)
        x = np.cross([0, 0, 1.0], z)
        x /= np.linalg.norm(x)
        y = np.cross(z, x)
        poses[i] = np.eye(4)
        poses[i, :3, :3] = np.stack([x, y, z], axis=1)
        poses[i, :3, 3] = pos[i]
    return poses


def apply_sim3(poses, s, r, t):
    out = poses.copy()
    out[:, :3, 3] = (s * (r @ poses[:, :3, 3].T)).T + t
    out[:, :3, :3] = r @ poses[:, :3, :3]
    return out


GT_S = 2.37
GT_R = A.axis_angle_to_rot([0.3, -0.5, 0.8], math.radians(70))
GT_T = np.array([1.2, -4.0, 0.7])


def test_exact_recovery_no_noise():
    ref = make_trajectory()
    # est est la trajectoire REF passée par l'inverse du Sim(3) : l'alignement doit tout annuler
    inv_r = GT_R.T
    est = apply_sim3(ref, 1 / GT_S, inv_r, -inv_r @ GT_T / GT_S)
    res = A.align_and_score(est, ref)
    assert abs(res["scale"] - GT_S) < 1e-9, res["scale"]
    assert res["translation_error"]["max"] < 1e-9, res["translation_error"]
    assert res["rotation_error_deg"]["max"] < 1e-6, res["rotation_error_deg"]


def test_injected_translation_and_rotation_error_recovered():
    ref = make_trajectory(n=600, seed=1)
    rng = np.random.default_rng(42)
    sigma_t = 0.02                      # 2 cm par axe -> RMSE attendu = sigma * sqrt(3) = 3,46 cm
    rot_deg = 0.8                       # angle exact par pose, axe aléatoire
    est = ref.copy()
    est[:, :3, 3] += sigma_t * rng.standard_normal((len(ref), 3))
    for i in range(len(est)):
        axis = rng.standard_normal(3)
        est[i, :3, :3] = A.axis_angle_to_rot(axis, math.radians(rot_deg)) @ est[i, :3, :3]
    inv_r = GT_R.T
    est = apply_sim3(est, 1 / GT_S, inv_r, -inv_r @ GT_T / GT_S)     # repère et échelle arbitraires

    res = A.align_and_score(est, ref)
    expected_rmse = sigma_t * math.sqrt(3)
    assert abs(res["scale"] - GT_S) / GT_S < 0.01, res["scale"]
    assert abs(res["translation_error"]["rmse"] - expected_rmse) / expected_rmse < 0.05, \
        (res["translation_error"]["rmse"], expected_rmse)
    assert abs(res["rotation_error_deg"]["mean"] - rot_deg) < 0.05, res["rotation_error_deg"]
    assert abs(res["rotation_error_deg"]["rmse"] - rot_deg) < 0.05, res["rotation_error_deg"]


def test_drift_is_visible():
    """Une dérive linéaire le long du chemin (0 -> 10 cm) doit remonter dans les tiers et la pente."""
    ref = make_trajectory(n=300, seed=2)
    est = ref.copy()
    ramp = np.linspace(0, 0.10, len(ref))
    est[:, :3, 3] += np.outer(ramp, [1.0, 0.0, 0.0])
    res = A.align_and_score(est, ref)
    # après alignement la dérive est en partie absorbée : on exige l'ordre de grandeur, pas l'égalité
    assert 0.01 < res["translation_error"]["rmse"] < 0.10, res["translation_error"]
    assert res["drift"]["path_length_ref"] > 15
    # une erreur sans dérive (bruit blanc) donne des tiers homogènes, la dérive non
    th = res["drift"]["translation_rmse_by_third"]
    est2 = ref.copy()
    est2[:, :3, 3] += 0.03 * np.random.default_rng(3).standard_normal((len(ref), 3))
    th2 = A.align_and_score(est2, ref)["drift"]["translation_rmse_by_third"]
    assert max(th) / min(th) > 1.5, th
    assert max(th2) / min(th2) < 1.3, th2


def test_reflection_is_not_silently_accepted():
    """Un repère main gauche contre main droite (Unity vs COLMAP) ne s'aligne pas par Sim(3) :
    le résidu doit être grand, pas masqué."""
    ref = make_trajectory()
    est = ref.copy()
    est[:, 2, 3] *= -1                  # miroir en z (inversion de chiralité des positions)
    res = A.align_and_score(est, ref)
    assert res["translation_error"]["rmse"] > 0.2, res["translation_error"]


def test_colmap_images_txt_roundtrip():
    """Écrire un images.txt (w2c) depuis des c2w connus, relire, retrouver les c2w."""
    ref = make_trajectory(n=5, seed=4)
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "images.txt"
        lines = ["# Image list with two lines of data per image:"]
        for i, c2w in enumerate(ref):
            r_wc = c2w[:3, :3].T
            t = -r_wc @ c2w[:3, 3]
            # quaternion depuis r_wc
            w = math.sqrt(max(0, 1 + np.trace(r_wc))) / 2
            q = np.array([w, (r_wc[2, 1] - r_wc[1, 2]) / (4 * w),
                          (r_wc[0, 2] - r_wc[2, 0]) / (4 * w), (r_wc[1, 0] - r_wc[0, 1]) / (4 * w)])
            lines.append(f"{i + 1} {' '.join(f'{v:.12f}' for v in q)} "
                         f"{' '.join(f'{v:.12f}' for v in t)} 1 sub/frame_{i:04d}.png")
            lines.append("" if i % 2 else "10.0 20.0 -1")      # ligne de points 2D vide ou non
        p.write_text("\n".join(lines) + "\n")
        got = A.read_poses(p)
    assert sorted(got) == [f"frame_{i:04d}.png" for i in range(5)]
    for i in range(5):
        assert np.allclose(got[f"frame_{i:04d}.png"], ref[i], atol=1e-8)


def test_cli_end_to_end_json():
    ref = make_trajectory(n=40, seed=5)
    est = apply_sim3(ref, 1 / GT_S, GT_R.T, -GT_R.T @ GT_T / GT_S)
    with tempfile.TemporaryDirectory() as d:
        paths = []
        for name, poses in (("est", est), ("ref", ref)):
            p = Path(d) / f"{name}.json"
            p.write_text(json.dumps({"frames": [
                {"file_path": f"images/f{i:03d}.png", "transform_matrix": m.tolist()}
                for i, m in enumerate(poses)]}))
            paths.append(p)
        out = Path(d) / "o.json"
        assert A.main(["--est", str(paths[0]), "--ref", str(paths[1]), "--out", str(out)]) == 0
        res = json.loads(out.read_text())
    assert res["translation_error"]["max"] < 1e-8 and abs(res["scale"] - GT_S) < 1e-8


if __name__ == "__main__":
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {name}: {e}")
    print(f"{len(tests) - failed}/{len(tests)} tests passent")
    sys.exit(1 if failed else 0)
