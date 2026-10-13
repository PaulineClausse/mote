#!/usr/bin/env python3
"""Tests de summarize.py et curves.py, sans GPU ni torch : python test_summarize.py"""
from __future__ import annotations

import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import curves  # noqa: E402
import summarize as su  # noqa: E402


def row(t20, t20_std, end):
    return {"t20_s": {"mean": t20, "std": t20_std, "n": 3, "of": 3},
            "psnr_end_of_stream": {"mean": end, "std": 0.3, "n": 3, "of": 3}}


def test_pick_best_follows_the_rule():
    # la règle de SP-6.md §2 : le plus tôt à 20 dB ; à moins d'un écart-type, le meilleur PSNR en fin de flux
    rows = {"recent 1/2": row(15.0, 0.0, 20.62), "uniform 1/2": row(15.0, 0.0, 21.09), "uniform": row(16.7, 2.9, 20.08)}
    assert su.pick_best(rows) == "uniform 1/2"                               # égalité : départage par la fin du flux
    rows = {"a": row(15.0, 0.0, 19.0), "b": row(16.7, 2.9, 21.0)}
    assert su.pick_best(rows) == "b"                                          # 1,7 s d'écart < 2,9 : départage
    rows = {"a": row(15.0, 0.0, 19.0), "b": row(25.0, 2.9, 21.0)}
    assert su.pick_best(rows) == "a"                                          # hors d'un écart-type : le plus tôt
    assert su.pick_best({}) is None


def run(strategy, seed, curve):
    return {"args": {"offline": False, "strategy": strategy, "downscale": 1, "pose_opt": True, "reset_every": 3000,
                     "seed": seed}, "curve": curve}


def test_curves_counts_zero_covered_views():
    # 0 vue couverte n'est pas « inconnu » : la colonne doit dire 0, et le compte vient de la courbe elle-même
    with tempfile.TemporaryDirectory() as d:
        for seed in (0, 1):
            (Path(d) / f"a_s{seed}.json").write_text(json.dumps(run("recent", seed, [
                {"stream_s": 5, "n_test": 0, "psnr": None}, {"stream_s": 10, "n_test": 2, "psnr": 28.0}])))
            (Path(d) / f"b_s{seed}.json").write_text(json.dumps(run("uniform", seed, [
                {"stream_s": 5, "n_test": 0, "psnr": None}])))
        buf = io.StringIO()
        with redirect_stdout(buf):
            assert curves.main(["--runs", d, "--step-s", "5"]) == 0
        lines = buf.getvalue().splitlines()
        assert lines[2] == "| 5 | 0 | - | - |", lines[2]
        assert lines[3] == "| 10 | 2 | 28.00 | - |", lines[3]


if __name__ == "__main__":
    tests = [test_pick_best_follows_the_rule, test_curves_counts_zero_covered_views]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)}/{len(tests)} tests passent")
