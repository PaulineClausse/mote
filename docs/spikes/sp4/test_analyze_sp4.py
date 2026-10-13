#!/usr/bin/env python3
"""Tests de analyze_sp4.py sur des journaux synthétiques de la sonde : python test_analyze_sp4.py"""
from __future__ import annotations

import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze_sp4 as an  # noqa: E402

SECONDS_HEADER = ("phase,t_s,frames,refresh_hz,dt_p50_ms,dt_max_ms,missed,process_cpu_pct,cores,getcolors_ms_avg,"
                  "getcolors_ms_max,pairs,push_ms_avg,busy,thermal_status")


def phase(name, fps, missed, frames, gc=None, **kw):
    p = {"phase": name, "wall_s": frames / fps, "frames": frames, "fps": fps, "refresh_hz": 72, "dt_p50_ms": 13.9,
         "dt_p99_ms": 15.0, "missed": missed, "process_cpu_pct": 80.0, "cores": 6, "getcolors_pairs": 0,
         "getcolors_ms_p50": 0, "getcolors_ms_p95": 0, "getcolors_ms_max": 0, "pairs_pushed": 0, "pairs_busy": 0,
         "thermal_status": 0}
    if gc:
        p.update(getcolors_pairs=600, getcolors_ms_p50=gc, getcolors_ms_p95=gc * 1.5, getcolors_ms_max=gc * 3)
    p.update(kw)
    return p


def core(pushed=1800, dropped=0, encoded=None, cpu=30.0, wall=180.0):
    return {"wall_s": wall, "pairs_pushed": pushed, "pairs_encoded": pushed - dropped if encoded is None else encoded,
            "pairs_dropped": dropped, "errors": 0, "push_ms_avg": 1.2, "push_ms_max": 2.3, "encode_ms_avg": 14.0,
            "encode_ms_p50": 13.5, "encode_ms_p95": 18.0, "encode_ms_max": 30.0, "write_ms_avg": 0.4,
            "jpeg_kb_avg": 410.0, "core_cpu_s": cpu, "process_cpu_s": 300.0, "mcap": "x", "last_error": ""}


def run(rows: list[dict]) -> str:
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "sp4_phases.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        (Path(d) / "sp4_seconds.csv").write_text(SECONDS_HEADER + "\nNominal,1.0,72,72,13.9,15,0,80,6,3,5,10,1.2,0,1\n",
                                                 encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            assert an.main([d]) == 0
        return buf.getvalue()


BENCH = {"phase": "Bench", "bench": {"width": 1280, "height": 1280, "n": 40, "quality": 90, "ms_p50": 12.0,
                                     "ms_p95": 15.0, "ms_avg": 12.5, "kb_avg": 400.0, "cpu_s": 0.5}}


def test_validated_and_budget():
    t = run([BENCH, phase("Baseline", 72.0, 10, 4320), phase("GetColors", 71.9, 12, 4314, gc=3.0),
             phase("Nominal", 71.8, 30, 12924, gc=3.2, core=core()), {"phase": "Close", "status": 0, "core": core()}])
    assert "H-05 : **validée**." in t, t
    assert "soit 24,0 ms par paire sur un cœur" in t, t
    # 30 s de CPU sur 180 s = 16,7 % ; x 1,25 = 20,8 -> 25 % ; push max 2,3 ms -> 2,5 ms
    assert "≤ 25 % d'un cœur" in t and "≤ 2,5 ms" in t, t


def test_display_drop_from_getcolors_is_a_reserve():
    t = run([phase("Baseline", 72.0, 10, 4320), phase("GetColors", 60.0, 400, 3600, gc=25.0),
             phase("Nominal", 60.0, 1200, 10800, gc=25.0, core=core())])
    assert "**validée avec réserve**" in t and "relecture GPU asynchrone" in t, t


def test_no_pair_pushed_means_no_verdict():
    # premier passage réel (2026-10-13) : la sonde n'a rien poussé au core ; l'analyse ne doit pas conclure
    empty = core(pushed=0, encoded=0, cpu=0.0)
    t = run([phase("Baseline", 71.9, 4, 4314), phase("GetColors", 61.9, 628, 3714, gc=15.5),
             phase("Nominal", 62.0, 1877, 11160, gc=15.8), {"phase": "Close", "status": 0, "core": empty}])
    assert "Verdict impossible sur la phase Nominal : aucune paire poussée" in t and "H-05 :" not in t, t
    assert "Budget NFR-05" not in t, t


def test_async_remedy_confirmed():
    t = run([phase("Baseline", 72.0, 10, 4320), phase("GetColors", 62.0, 700, 3720, gc=15.5),
             phase("Nominal", 62.0, 2000, 7440, gc=15.8, core=core(pushed=1200)),
             phase("Async", 71.8, 30, 12924, gc=1.2, core=core(pushed=1800, cpu=36.0),
                   latency_frames_p50=3, latency_frames_max=5),
             {"event": "size", "phase": "Nominal", "mode": "sync", "len_left": 1638400, "len_right": 1638400,
              "width": 1280, "height": 1280, "texture": [1280, 1280], "current_resolution": [1280, 1280]}])
    assert "**validée avec réserve**" in t and "Remède : **confirmé**" in t, t
    assert "latence médiane 3 frames" in t and "Diagnostic Nominal (sync)" in t, t
    assert "### Core, phase Async" in t and "≤ 25 % d'un cœur" in t, t           # 36 s / 180 s = 20 % -> 25 %


def test_lost_pairs_invalidate():
    t = run([phase("Baseline", 72.0, 10, 4320), phase("GetColors", 72.0, 10, 4320, gc=3.0),
             phase("Nominal", 72.0, 30, 12960, core=core(dropped=60))])
    assert "NON : paires perdues" in t and "H-05 : **invalidée**." in t, t


def test_missing_phase():
    t = run([phase("Baseline", 72.0, 10, 4320)])
    assert "Verdict impossible" in t, t


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)}/{len(tests)} tests passent")
