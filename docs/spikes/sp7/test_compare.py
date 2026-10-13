#!/usr/bin/env python3
"""Tests de compare.py (règle de SP-7.md §2) sur des JSON synthétiques : python test_compare.py"""
from __future__ import annotations

import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compare  # noqa: E402


def run_json(init: bool, seed: int, psnr_shift: float, t20: float, final: float, offline: bool = False) -> dict:
    curve = []
    for k in range(0, 37):
        t = 5.0 * k
        curve.append({"stream_s": t, "step": 100 * k, "n_test": 0 if t < 15 else 20,
                      "psnr": None if t < 15 else 20.0 + psnr_shift + 0.01 * seed, "n_gauss": 1000})
    return {"args": {"offline": offline, "strategy": "uniform", "downscale": 1 if offline else 2,
                     "init_npz": "init.npz" if init else None, "seed": seed},
            "stream_duration_s": 122.5, "curve": curve, "t20_s": t20, "t20_step": 300, "it_per_s": 40.0,
            "psnr_end_of_stream": 21.0 + psnr_shift, "psnr_final": final, "n_gauss_final": 800000}


def verdict(rows: list[dict]) -> str:
    with tempfile.TemporaryDirectory() as d:
        for i, r in enumerate(rows):
            (Path(d) / f"r{i}.json").write_text(json.dumps(r), encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            assert compare.main(["--runs", d]) == 0
        return buf.getvalue()


def test_recommended_when_psnr_gains():
    t = verdict([run_json(False, s, 0.0, 15.0, 21.4) for s in range(3)]
                + [run_json(True, s, 0.8, 15.0, 21.5) for s in range(3)])
    assert "**recommandée pour le live**" in t and "écart de PSNR moyen du flux 0,80 dB" in t, t


def test_recommended_when_20db_earlier():
    t = verdict([run_json(False, s, 0.0, 30.0 + s, 21.4) for s in range(3)]
                + [run_json(True, s, 0.1, 15.0, 21.4) for s in range(3)])
    assert "**recommandée pour le live**" in t and "20 dB plus tôt" in t, t


def test_neutral_and_discouraged():
    t = verdict([run_json(False, s, 0.0, 15.0, 21.4) for s in range(3)]
                + [run_json(True, s, 0.2, 15.0, 21.4) for s in range(3)])
    assert "**neutre**" in t, t
    t = verdict([run_json(False, s, 0.0, 15.0, 21.4) for s in range(3)]
                + [run_json(True, s, 0.3, 15.0, 20.9) for s in range(3)])       # final dégradé de 0,5 dB
    assert "**déconseillée pour le live**" in t, t


def test_offline_table():
    t = verdict([run_json(False, s, 0, 34.0, 25.0, offline=True) for s in range(3)]
                + [run_json(True, s, 0, 20.0, 25.3, offline=True) for s in range(3)])
    assert "### offline" in t and "| profondeur | 3 | 20,0 ± 0,0 |" in t and "Pas de paire" in t, t


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)}/{len(tests)} tests passent")
