#!/usr/bin/env python3
"""Tests de stream.py, sans GPU ni torch : python test_stream.py"""
from __future__ import annotations

import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stream as st  # noqa: E402

T0 = 1_791_367_700_000_000


def session(d: Path, n_pairs: int = 50, fps: float = 5.0, test_every: int = 10) -> Path:
    """Paires LEFT/RIGHT à `fps`, une paire de test toutes les `test_every`. Les noms sont donnés dans le désordre."""
    nd = d / "nsdata"
    (nd / "headset" / "sparse" / "0").mkdir(parents=True)
    (nd / "headset" / "sparse" / "0" / "cameras.txt").write_text(
        "# cams\n1 PINHOLE 1280 1280 868.68 868.68 642.0 640.6\n2 PINHOLE 1280 1280 868.7 868.7 640.0 640.0\n")
    lines, train, test = ["# images"], [], []
    for k in reversed(range(n_pairs)):
        ts = T0 + int(k / fps * 1e6)
        for cid, eye in ((1, "LEFT"), (2, "RIGHT")):
            name = f"{eye}_{ts}.png"
            lines += [f"{len(lines)} 1 0 0 0 {k * 0.01} 0 0 {cid} {name}", ""]
            (test if k % test_every == test_every - 1 else train).append(name)
    (nd / "headset" / "sparse" / "0" / "images.txt").write_text("\n".join(lines) + "\n")
    (nd / "train_list.txt").write_text("\n".join(train) + "\n")
    (nd / "test_list.txt").write_text("\n".join(test) + "\n")
    return nd


def test_load_order_and_split():
    with tempfile.TemporaryDirectory() as d:
        views, cams = st.load_session(session(Path(d)))
        assert len(views) == 100 and cams[1].fx == 868.68 and cams[2].cx == 640.0
        assert [v.t for v in views] == sorted(v.t for v in views)            # ordre de capture
        assert views[0].t == 0.0 and abs(views[-1].t - 49 / 5) < 1e-9
        assert Counter(v.split for v in views) == {"train": 90, "test": 10}
        assert views[0].qvec == (1.0, 0.0, 0.0, 0.0) and views[2].tvec == (0.01, 0.0, 0.0)


def test_stream_arrival_and_coverage():
    with tempfile.TemporaryDirectory() as d:
        views, _ = st.load_session(session(Path(d)))
        s = st.Stream(views, margin_s=2.0)
        assert abs(s.duration_s - 9.8) < 1e-9
        assert s.n_arrived(0.0) == 2                                          # la première paire, à t = 0
        assert s.n_arrived(1.0) == 2 * 5 + 2 - 0                              # paires 0..5, aucune de test
        assert s.n_arrived(100.0) == 90
        assert s.covered_test(3.7) == []                                      # 1re paire de test à 1,8 s, couverte à 3,8 s
        assert s.covered_test(3.8) == [0, 1]
        assert len(s.covered_test(100.0)) == 10
        fast = st.Stream(views, speed=2.0)
        assert fast.n_arrived(0.5) == s.n_arrived(1.0) and abs(fast.duration_s - 4.9) < 1e-9
        off = st.Stream(views, offline=True)
        assert off.n_arrived(0.0) == 90 and len(off.covered_test(0.0)) == 10 and off.duration_s == 0.0


def test_samplers():
    with tempfile.TemporaryDirectory() as d:
        views, _ = st.load_session(session(Path(d)))
        s = st.Stream(views)
        for strat in st.STRATEGIES:
            assert st.Sampler(s, strat).pick(-1.0) is None                    # rien d'arrivé
        n = s.n_arrived(9.8)
        recent_lo = next(i for i, v in enumerate(s.train) if v.t >= 9.8 - 2.0)
        ws = st.Sampler(s, "window", seed=1, window_s=2.0)
        win = Counter(ws.pick(9.8) for _ in range(2000))
        assert min(win) >= recent_lo and max(win) < n
        us = st.Sampler(s, "uniform", seed=1)
        uni = [us.pick(9.8) for _ in range(2000)]
        assert min(uni) == 0 and max(uni) == n - 1
        rec = st.Sampler(s, "recent", seed=1, window_s=2.0, p_recent=0.5)
        frac = sum(rec.pick(9.8) >= recent_lo for _ in range(4000)) / 4000
        expected = 0.5 + 0.5 * (n - recent_lo) / n
        assert abs(frac - expected) < 0.04, (frac, expected)
        assert st.Sampler(st.Stream(views, offline=True), "window", seed=1).pick(0.0) is not None
        try:
            st.Sampler(s, "nope")
        except ValueError:
            pass
        else:
            raise AssertionError("stratégie inconnue acceptée")


def test_first_reaching():
    curve = [{"psnr": None, "n_test": 0}, {"psnr": 22.0, "n_test": 2}, {"psnr": 19.0, "n_test": 6},
             {"psnr": 20.5, "n_test": 6, "stream_s": 30}]
    assert st.first_reaching(curve, 20.0)["stream_s"] == 30                  # 2 vues seulement : ignoré
    assert st.first_reaching(curve, 20.0, min_views=1)["psnr"] == 22.0
    assert st.first_reaching(curve, 25.0) is None


if __name__ == "__main__":
    tests = [test_load_order_and_split, test_stream_arrival_and_coverage, test_samplers, test_first_reaching]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)}/{len(tests)} tests passent")
