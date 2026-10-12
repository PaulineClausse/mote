#!/usr/bin/env python3
"""SP-6 : agrège les runs d'incremental.py (un JSON par run) en un tableau par configuration et un summary.json.

  python summarize.py --runs <dossier des JSON> [--target-s 60]

Configuration = hors ligne ou stratégie, résolution, raffinement de pose, remise des opacités. Moyenne ± écart-type
sur les graines. Verdict RISK-09 : la meilleure configuration en flux atteint-elle 20 dB sur les vues déjà couvertes
en `--target-s` secondes au plus après le début du flux (critère de WP-15) ?
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path


def key_of(r: dict) -> str:
    a = r["args"]
    k = "hors ligne" if a["offline"] else a["strategy"]
    k += f" 1/{a['downscale']}" if a["downscale"] > 1 else ""
    k += "" if a["pose_opt"] else " sans pose"
    k += "" if a["reset_every"] == 3000 else f" reset {a['reset_every'] or 'jamais'}"
    k += "" if a.get("ssim", "torchmetrics") == "torchmetrics" else f" ssim {a['ssim']}"
    k += " img GPU" if a.get("images_on_gpu") else ""
    return k


def ms(xs: list) -> dict:
    vals = [x for x in xs if x is not None]
    return {"mean": statistics.fmean(vals) if vals else None,
            "std": statistics.stdev(vals) if len(vals) > 1 else 0.0 if vals else None,
            "n": len(vals), "of": len(xs)}


def fmt(m: dict, nd: int = 1) -> str:
    if m["mean"] is None:
        return f"jamais (0/{m['of']})"
    s = f"{m['mean']:.{nd}f} ± {m['std']:.{nd}f}"
    return s if m["n"] == m["of"] else f"{s} ({m['n']}/{m['of']})"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--target-s", type=float, default=60.0)
    a = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(a.runs.glob("*.json"))
            if p.name != "summary.json"]
    if not runs:
        print(f"aucun run dans {a.runs}")
        return 2
    groups: dict[str, list] = {}
    for r in runs:
        groups.setdefault(key_of(r), []).append(r)
    rows = {}
    for k, rs in groups.items():
        rows[k] = {"offline": rs[0]["args"]["offline"], "seeds": sorted(r["args"]["seed"] for r in rs),
                   **{f: ms([r[f] for r in rs]) for f in
                      ("t20_s", "t20_step", "it_per_s", "psnr_end_of_stream", "psnr_final", "n_gauss_final")}}
    stream_rows = {k: v for k, v in rows.items() if not v["offline"] and v["t20_s"]["n"] == v["t20_s"]["of"]}
    best = min(stream_rows, key=lambda k: stream_rows[k]["t20_s"]["mean"]) if stream_rows else None
    verdict = None
    if best:
        t = stream_rows[best]["t20_s"]["mean"]
        verdict = {"best": best, "t20_s": t, "target_s": a.target_s,
                   "risk09": "levé" if t <= a.target_s else "confirmé"}
    out = {"gpu": runs[0]["gpu"], "resolution_full": runs[0]["resolution"],
           "stream_duration_s": next((r["stream_duration_s"] for r in runs if not r["args"]["offline"]), None),
           "configs": rows, "verdict": verdict}
    (a.runs / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"\nGPU : {out['gpu']} ; durée du flux : {out['stream_duration_s']} s\n")
    print("configuration         | graines | 20 dB (s)       | 20 dB (it.)     | it/s          | PSNR fin du flux | PSNR final   | gaussiennes")
    print("----------------------|---------|-----------------|-----------------|---------------|------------------|--------------|------------")
    for k, v in sorted(rows.items(), key=lambda kv: (not kv[1]["offline"], kv[0])):
        print(f"{k:<21} | {len(v['seeds']):>7} | {fmt(v['t20_s']):<15} | {fmt(v['t20_step'], 0):<15} | "
              f"{fmt(v['it_per_s']):<13} | {fmt(v['psnr_end_of_stream'], 2):<16} | {fmt(v['psnr_final'], 2):<12} | "
              f"{fmt(v['n_gauss_final'], 0)}")
    if verdict:
        print(f"\nmeilleure stratégie en flux : {best}, 20 dB à {verdict['t20_s']:.1f} s "
              f"-> RISK-09 {verdict['risk09']} (cible {a.target_s:.0f} s)")
    else:
        print("\naucune stratégie en flux n'atteint 20 dB sur toutes ses graines -> RISK-09 confirmé")
    print(f"résumé : {a.runs / 'summary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
