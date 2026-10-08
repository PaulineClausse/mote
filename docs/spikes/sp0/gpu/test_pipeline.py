#!/usr/bin/env python3
"""Tests sans GPU ni COLMAP : python test_pipeline.py

Fabrique un export (poses du casque) et un REF synthétiques, REF = Sim(3) connu du casque, renommé
left/… right/… comme le fait images_by_eye, avec un second petit modèle et un essai de mapper échoué
dans timings.json ; vérifie le choix du modèle, l'échelle, les erreurs en mètres, ref_flat, le temps du SfM,
la découverte des sessions, les liens par œil, un passage de pipeline.py en --dry-run, et un passage réel avec un
faux colmap dont l'appariement tombe en panne une fois (reprise, temps complets, résumé).
"""
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import align_sim3  # noqa: E402
import pipeline  # noqa: E402
import post_ref  # noqa: E402


def rot_to_quat(r):
    w = math.sqrt(max(0.0, 1 + r[0, 0] + r[1, 1] + r[2, 2])) / 2
    x = math.copysign(math.sqrt(max(0.0, 1 + r[0, 0] - r[1, 1] - r[2, 2])) / 2, r[2, 1] - r[1, 2])
    y = math.copysign(math.sqrt(max(0.0, 1 - r[0, 0] + r[1, 1] - r[2, 2])) / 2, r[0, 2] - r[2, 0])
    z = math.copysign(math.sqrt(max(0.0, 1 - r[0, 0] - r[1, 1] + r[2, 2])) / 2, r[1, 0] - r[0, 1])
    return w, x, y, z


def write_images_txt(path: Path, poses: dict, prefix_by_eye=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Image list with two lines of data per image:", "# fake"]
    for i, (name, c2w) in enumerate(sorted(poses.items()), 1):
        r_wc = c2w[:3, :3].T
        t = -r_wc @ c2w[:3, 3]
        n = f"{'left' if name.startswith('LEFT') else 'right'}/{name}" if prefix_by_eye else name
        lines += [" ".join(map(str, [i, *rot_to_quat(r_wc), *t, 1 if name.startswith("LEFT") else 2, n])), ""]
    path.write_text("\n".join(lines) + "\n")
    for f in ("cameras.txt", "points3D.txt"):
        (path.parent / f).write_text("# vide\n")


def trajectory(n=60, seed=0):
    rng = np.random.default_rng(seed)
    poses = {}
    for k in range(n):
        a = 2 * math.pi * k / n
        c = np.array([1.5 * math.cos(a), 0.1 * math.sin(3 * a), 2.0 * math.sin(a)])
        r = align_sim3.axis_angle_to_rot([0, 1, 0], a + 0.3) @ align_sim3.axis_angle_to_rot(rng.normal(size=3), 0.1)
        for eye, off in (("LEFT", -0.032), ("RIGHT", 0.032)):
            m = np.eye(4)
            m[:3, :3] = r
            m[:3, 3] = c + r @ np.array([off, 0, 0])
            poses[f"{eye}_{1000000 + 200000 * k}.png"] = m
    return poses


def make_session(root: Path, scale=4.8, noise_m=0.004):
    est = trajectory()
    s_ref = np.eye(4)
    s_ref[:3, :3] = scale * align_sim3.axis_angle_to_rot([0.2, 1, 0.1], 0.7)
    s_ref[:3, 3] = [0.5, -2.0, 3.0]
    rng = np.random.default_rng(1)
    ref = {}
    for i, (n, m) in enumerate(sorted(est.items())):
        if i % 10 == 3:                                    # 10 % non recalées par REF
            continue
        r = np.eye(4)
        r[:3, :3] = s_ref[:3, :3] / scale @ m[:3, :3]
        r[:3, 3] = s_ref[:3, :3] @ (m[:3, 3] + rng.normal(scale=noise_m, size=3)) + s_ref[:3, 3]
        ref[n] = r
    write_images_txt(root / "est_txt" / "images.txt", est)
    write_images_txt(root / "ref" / "sparse" / "0" / "images.txt", dict(list(ref.items())[:4]), True)
    write_images_txt(root / "ref" / "sparse" / "1" / "images.txt", ref, True)
    rows = [{"label": "colmap_feature_extractor", "wall_s": 30.0, "exit_code": 0},
            {"label": "colmap_matcher", "wall_s": 120.0, "exit_code": 0},
            {"label": "colmap_mapper", "wall_s": 999.0, "exit_code": 1},
            {"label": "colmap_mapper", "wall_s": 90.0, "exit_code": 0}]
    (root / "timings.json").write_text(json.dumps(rows))
    return est, ref


def test_summary():
    with tempfile.TemporaryDirectory() as d:
        s = Path(d) / "S9"
        est, ref = make_session(s)
        r = post_ref.summarize(s, s / "est_txt" / "images.txt", s / "ref" / "sparse", s / "timings.json",
                               extra={"session": "S9"})
        assert r["ref_model"] == "1", r["ref_model"]
        assert r["n_images"] == 120 and r["ref_registered"] == 108, (r["n_images"], r["ref_registered"])
        assert r["ref_is_reference"] and abs(r["ref_registered_fraction"] - 0.9) < 1e-9
        for w in ("all", "left", "right"):
            a = r["align"][w]
            assert abs(a["scale"] - 4.8) < 0.05, (w, a["scale"])
            med = a["translation_error_m"]["median"]
            assert 0.001 < med < 0.01, (w, med)                  # bruit injecté de 4 mm par axe
            assert a["rotation_error_deg"]["median"] < 0.5, (w, a["rotation_error_deg"])   # rotation exacte, Sim(3) ajusté sur des centres bruités
        assert r["align"]["left"]["n_common"] == 54 and "drift_ratio_last_first" in r["align"]["left"]
        assert "drift_rmse_by_third_m" not in r["align"]["all"]
        assert r["sfm_time"]["total_s"] == 240.0, r["sfm_time"]
        flat = align_sim3.read_poses(s / "ref_flat" / "sparse" / "0" / "images.txt")
        assert set(flat) == set(ref)
        assert "left/" not in (s / "ref_flat" / "sparse" / "0" / "images.txt").read_text()
        assert json.loads((s / "summary.json").read_text())["session"] == "S9"
        assert "S9" in post_ref.table([r])


def test_discover_and_links():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "a" / "20261007_101500").mkdir(parents=True)
        (d / "a" / "20261007_101500" / "hmd_poses.csv").write_text("x")
        ex = d / "kit" / "data"
        (ex / "distorted" / "sparse" / "0").mkdir(parents=True)
        (ex / "distorted" / "sparse" / "0" / "images.bin").write_bytes(b"")
        (ex / "images").mkdir()
        for n in ("LEFT_1.png", "RIGHT_1.png", "LEFT_2.png"):
            (ex / "images" / n).write_bytes(b"png")
        found = {n: k for n, _, k in pipeline.discover(d)}
        assert found == {"20261007_101500": "raw", "data": "export"}, found
        assert pipeline.link_by_eye(ex / "images", d / "by_eye") == 3
        assert sorted(p.name for p in (d / "by_eye" / "left").iterdir()) == ["LEFT_1.png", "LEFT_2.png"]
        assert pipeline.link_by_eye(ex / "images", d / "by_eye") == 3     # relance : rien ne casse


def test_dry_run():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "in" / "20261008_090000").mkdir(parents=True)
        (d / "in" / "20261008_090000" / "hmd_poses.csv").write_text("x")
        p = subprocess.run([sys.executable, str(HERE / "pipeline.py"), "--data", str(d / "in"),
                            "--work", str(d / "out"), "--tools", str(d / "tools"), "--dry-run"],
                           capture_output=True, text=True, encoding="utf-8")
        out = p.stdout + p.stderr
        assert p.returncode == 0, out
        for k in ("export-colmap", "--interval 2", "feature_extractor", "single_camera_per_folder 1",
                  "use_gpu 1", "exhaustive_matcher", "mapper", "model_converter"):
            assert k in out, (k, out)
        assert not (d / "tools" / "downloads").exists()


FAKE_COLMAP = r"""
import os, shutil, sys
from pathlib import Path
a = sys.argv[1:]
opt = lambda k: Path(a[a.index(k) + 1])
if a == ["-h"]:
    print("COLMAP 4.2.1 -- Structure-from-Motion and Multi-View Stereo (Commit fake with CUDA)")
elif a[:2] == ["feature_extractor", "-h"]:
    print("  --FeatureExtraction.use_gpu arg (=1)")
elif a[0] == "feature_extractor":
    opt("--database_path").write_text("db")
elif a[0] == "exhaustive_matcher":
    flag = Path(os.environ["FAKE_FAIL_ONCE"])
    if flag.exists():
        flag.unlink()
        sys.exit("matcher: panne simulee")
elif a[0] == "mapper":
    shutil.copytree(os.environ["FAKE_REF"], opt("--output_path"), dirs_exist_ok=True)
elif a[0] == "model_converter":
    src, dst = opt("--input_path"), opt("--output_path")
    if not (src / "images.txt").exists():
        src = Path(os.environ["FAKE_EST"])
    if src != dst:
        for f in src.glob("*.txt"):
            shutil.copy(f, dst / f.name)
"""


def test_full_run_with_fake_colmap():
    """Chemin réel sans GPU : faux colmap, appariement en panne au premier passage, puis reprise."""
    import os
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        fix = d / "fixture"
        est, ref = make_session(fix)
        kit = d / "in" / "S9"                                         # export SRC-3 déjà fait
        (kit / "distorted" / "sparse" / "0").mkdir(parents=True)
        (kit / "distorted" / "sparse" / "0" / "images.bin").write_bytes(b"")
        (kit / "images").mkdir()
        for n in est:
            (kit / "images" / n).write_bytes(b"png")
        (d / "fake_colmap.py").write_text(FAKE_COLMAP)
        if os.name == "nt":
            exe = d / "colmap.cmd"
            exe.write_text(f'@"{sys.executable}" "{d / "fake_colmap.py"}" %*\n')
        else:
            exe = d / "colmap"
            exe.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{d / "fake_colmap.py"}" "$@"\n')
            exe.chmod(0o755)
        (d / "fail_once").write_text("")
        env = dict(os.environ, COLMAP=str(exe), FAKE_REF=str(fix / "ref" / "sparse"),
                   FAKE_EST=str(fix / "est_txt"), FAKE_FAIL_ONCE=str(d / "fail_once"))
        cmd = [sys.executable, str(HERE / "pipeline.py"), "--data", str(d / "in"), "--work", str(d / "out"),
               "--tools", str(d / "tools"), "--allow-cpu"]
        run = lambda: subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8")
        p1 = run()
        assert p1.returncode == 1 and "panne simulee" in p1.stdout, p1.stdout + p1.stderr
        assert (d / "out" / "S9" / ".steps" / "feature_extractor").exists()
        p2 = run()
        out = p2.stdout + p2.stderr
        assert p2.returncode == 0, out
        assert "appariement interrompu" in out and "S9" in out, out
        rows = json.loads((d / "out" / "S9" / "timings.json").read_text())
        assert [r["label"] for r in rows].count("colmap_feature_extractor") == 2, rows
        assert all("--FeatureExtraction.use_gpu" in r["argv"] and r["argv"][-1] == "1"
                   for r in rows if r["label"] == "colmap_feature_extractor")
        summ = json.loads((d / "out" / "S9" / "summary.json").read_text())
        assert summ["ref_model"] == "1" and summ["sift_gpu"] and summ["kind"] == "export"
        assert set(summ["sfm_time"]["steps_s"]) == {"colmap_feature_extractor", "colmap_matcher", "colmap_mapper"}
        assert abs(summ["align"]["all"]["scale"] - 4.8) < 0.05
        assert len(list((d / "out" / "S9" / "ref" / "images_by_eye" / "left").iterdir())) == 60
        assert json.loads((d / "out" / "summary_all.json").read_text())[0]["session"] == "S9"
        p3 = run()                                                    # tout est fait : rien ne se relance
        assert p3.returncode == 0 and "colmap_mapper :" not in p3.stdout, p3.stdout


if __name__ == "__main__":
    tests = [test_summary, test_discover_and_links, test_dry_run, test_full_run_with_fake_colmap]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)}/{len(tests)} tests passent")
