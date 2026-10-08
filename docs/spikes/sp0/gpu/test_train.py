#!/usr/bin/env python3
"""Tests sans GPU ni nerfstudio de train.py : python test_train.py

Appariement gauche/droite par horodatage, jeu commun A / AREF (mêmes images, paires complètes, listes),
agrégation du bench (écart A - AREF, règle de SP-0.md §2, seuils proposés) et commandes en --dry-run.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import post_ref  # noqa: E402
import train  # noqa: E402
from test_pipeline import make_session  # noqa: E402


def session(d: Path) -> Path:
    s = d / "S9"
    est, _ = make_session(s)
    post_ref.summarize(s, s / "est_txt" / "images.txt", s / "ref" / "sparse", s / "timings.json",
                       extra={"session": "S9", "kind": "raw", "source": str(d / "raw")})
    (s / "export" / "images").mkdir(parents=True)
    for n in est:
        (s / "export" / "images" / n).write_bytes(b"png")
    return s


def test_pair_keys_by_timestamp():
    names = ["LEFT_1000000.png", "RIGHT_1000001.png", "LEFT_1200000.png", "RIGHT_1227800.png",
             "LEFT_1400000.png", "RIGHT_1600000.png"]
    keys, method = train.pair_keys(names, None)
    assert method == "horodatage"
    assert keys["LEFT_1000000.png"] == keys["RIGHT_1000001.png"]          # 1 µs d'écart (S1)
    assert keys["LEFT_1200000.png"] == keys["RIGHT_1227800.png"]          # 27,8 ms (S1, maximum)
    assert "LEFT_1400000.png" not in keys and "RIGHT_1600000.png" not in keys   # 200 ms : pas une paire


def test_prepare_common_set():
    with tempfile.TemporaryDirectory() as d:
        s = session(Path(d))
        info = train.prepare(s, s / "export" / "images", None, block=2, period=10)
        nd = s / "nsdata"
        a = train.post_ref.image_records(nd / "headset" / "sparse" / "0" / "images.txt")
        r = train.post_ref.image_records(nd / "ref" / "sparse" / "0" / "images.txt")
        na = sorted(h.split()[9] for h, _ in a)
        nr = sorted(h.split()[9] for h, _ in r)
        assert na == nr, "A et AREF doivent voir exactement les mêmes images"
        assert all("/" not in n for n in nr)
        assert sorted(p.name for p in (nd / "images").iterdir()) == na
        train_l = (nd / "train_list.txt").read_text(encoding="utf-8").split()
        test_l = (nd / "test_list.txt").read_text(encoding="utf-8").split()
        assert not set(train_l) & set(test_l) and sorted(train_l + test_l) == na
        assert (nd / "val_list.txt").read_text(encoding="utf-8") == (nd / "validation_list.txt").read_text(encoding="utf-8") == \
            (nd / "test_list.txt").read_text(encoding="utf-8")
        for lst in (train_l, test_l):                                    # gauche et droite ensemble
            assert sorted(n.replace("LEFT_", "").replace("RIGHT_", "") for n in lst if n.startswith("LEFT")) == \
                sorted(n.replace("RIGHT_", "") for n in lst if n.startswith("RIGHT"))
        assert info["n_pairs"] * 2 == len(na) and info["n_test_pairs"] > 0
        assert "points3D" not in (nd / "headset" / "sparse" / "0" / "points3D.txt").read_text(encoding="utf-8").split("\n", 1)[1]


def test_bench_rule():
    with tempfile.TemporaryDirectory() as d:
        s = Path(d) / "S9"
        s.mkdir()
        runs = {"A": {f"seed{k}": {"psnr": p, "ssim": 0.8, "lpips": 0.2, "train_s": 1200, "t20_s": 300}
                      for k, p in enumerate((24.0, 24.4, 24.2))},
                "AREF": {f"seed{k}": {"psnr": p, "ssim": 0.82, "lpips": 0.18, "train_s": 1250, "t20_s": None}
                         for k, p in enumerate((25.5, 25.6, 25.7))}}
        b = train.bench(s, runs)
        assert abs(b["delta_psnr_A_minus_AREF"] - (24.2 - 25.6)) < 1e-9
        assert b["rule_sp0_psnr"] == "intermediaire"
        assert b["proposals"]["sc01_psnr_db"] == 20.0 and b["proposals"]["sc02_gain_db"] == 1.0
        assert b["variants"]["AREF"]["t20_s"]["n"] == 0
        assert json.loads((s / "bench.json").read_text(encoding="utf-8"))["session"] == "S9"
        t = train.table([b])
        assert "A - AREF : -1.40 dB" in t and "24.20 ± 0.20" in t


def test_psnr_curve():
    """Lecture tensorboard (seulement si tensorboard est là, c'est-à-dire dans le venv d'entraînement)."""
    try:
        from torch.utils.tensorboard import SummaryWriter
    except ImportError:
        print("  (tensorboard absent : test sauté)")
        return
    with tempfile.TemporaryDirectory() as d:
        w = SummaryWriter(d)
        for step, p in ((0, 8.0), (2000, 17.5), (4000, 20.4), (6000, 22.0)):
            w.add_scalar(train.PSNR_TAG, p, step)
        w.close()
        curve = train.psnr_curve(Path(d))
        assert [c["step"] for c in curve] == [0, 2000, 4000, 6000], curve
        assert train.first_above(curve, 20.0)["step"] == 4000
        assert train.first_above(curve, 30.0) is None


def test_dry_run_commands():
    with tempfile.TemporaryDirectory() as d:
        session(Path(d))
        p = subprocess.run([sys.executable, str(HERE / "train.py"), "--work", d, "--seeds", "0", "1",
                            "--period", "10", "--block", "2", "--dry-run"],
                           capture_output=True, text=True, encoding="utf-8")
        out = p.stdout + p.stderr
        assert p.returncode == 0, out
        assert out.count("ns-train") == 4, out                          # 2 variantes x 2 graines
        for k in ("--colmap-path headset/sparse/0", "--colmap-path ref/sparse/0", "--load-3D-points False",
                  "--pipeline.model.camera-optimizer.mode SO3xR3", "--max-num-iterations 30000",
                  "--machine.seed 1", "--image-format png", "--lpips-net vgg", "--vis tensorboard"):
            assert k in out, (k, out)


if __name__ == "__main__":
    tests = [test_pair_keys_by_timestamp, test_prepare_common_set, test_bench_rule, test_psnr_curve,
             test_dry_run_commands]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)}/{len(tests)} tests passent")
