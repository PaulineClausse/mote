#!/usr/bin/env python3
"""SP-6 : PSNR des vues couvertes en fonction du temps de flux, moyenné sur les graines, une colonne par configuration.

  python curves.py --runs <dossier des JSON> [--step-s 10]

Pour chaque instant t (multiple de --step-s), on prend dans chaque run la dernière évaluation faite à t ou avant,
puis la moyenne sur les graines. Sortie en tableau Markdown, à coller dans SP-6.md.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from summarize import key_of  # noqa: E402


def at(curve: list[dict], t: float) -> dict | None:
    pts = [c for c in curve if c["stream_s"] <= t + 1e-6]
    return pts[-1] if pts else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--step-s", type=float, default=10.0)
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):                   # absent quand la sortie est capturée (tests)
            s.reconfigure(encoding="utf-8", errors="replace")
    groups: dict[str, list] = {}
    for p in sorted(a.runs.glob("*.json")):
        if p.name == "summary.json":
            continue
        r = json.loads(p.read_text(encoding="utf-8"))
        if not r["args"]["offline"]:
            groups.setdefault(key_of(r), []).append(r)
    if not groups:
        print(f"aucun run en flux dans {a.runs}")
        return 2
    keys = sorted(groups)
    end = max(c["stream_s"] for rs in groups.values() for r in rs for c in r["curve"])
    print("| t (s) | vues test couvertes | " + " | ".join(keys) + " |")
    print("|---|---|" + "---|" * len(keys))
    t = a.step_s
    while t <= end + 1e-6:
        cells, n_test = [], None
        for k in keys:
            pts = [at(r["curve"], t) for r in groups[k]]
            ps = [p["psnr"] for p in pts if p and p["psnr"] is not None]
            n_test = max([p["n_test"] for p in pts if p] + ([n_test] if n_test is not None else []), default=None)
            cells.append(f"{statistics.fmean(ps):.2f}" if ps else "-")
        print(f"| {t:.0f} | {n_test if n_test is not None else '-'} | " + " | ".join(cells) + " |")
        t += a.step_s
    return 0


if __name__ == "__main__":
    sys.exit(main())
