#!/usr/bin/env python3
"""SP-7 : profondeur contre aléatoire, à partir des JSON d'incremental.py, et verdict selon la règle de SP-7.md §2.

  python compare.py --runs <dossier des JSON>

Groupes : hors ligne et flux, initialisation aléatoire ou profondeur (`args.init_npz`), même stratégie et même
résolution dans chaque comparaison. Python seul.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

GAIN_DB = 0.5        # écart de PSNR moyen en flux qui décide (SP-7.md §2)
FINAL_TOL_DB = 0.3   # dégradation tolérée du PSNR final


def f(x, nd=2):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}".replace(".", ",")


def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return math.nan, math.nan, 0
    return statistics.fmean(xs), statistics.stdev(xs) if len(xs) > 1 else 0.0, len(xs)


def fmt(xs, nd=2):
    m, s, n = ms(xs)
    return "-" if n == 0 else f"{f(m, nd)} ± {f(s, nd)}"


def stream_mean(r: dict, t_from: float = 20.0) -> float | None:
    """PSNR moyen des évaluations du flux de t_from à la fin du flux, au moins 4 vues couvertes."""
    end = r["stream_duration_s"]
    ps = [c["psnr"] for c in r["curve"]
          if c["psnr"] is not None and c["n_test"] >= 4 and t_from <= c["stream_s"] <= end]
    return statistics.fmean(ps) if ps else None


def load(runs: Path) -> dict:
    groups: dict = {}
    for p in sorted(runs.glob("*.json")):
        if p.name in ("summary.json",):
            continue
        r = json.loads(p.read_text(encoding="utf-8"))
        a = r["args"]
        mode = "offline" if a["offline"] else f"flux {a['strategy']} 1/{a['downscale']}"
        init = "profondeur" if a.get("init_npz") not in (None, "None") else "aléatoire"
        groups.setdefault(mode, {}).setdefault(init, []).append(r)
    return groups


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", type=Path, required=True)
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    groups = load(a.runs)
    out = []
    verdict = None
    for mode, by_init in sorted(groups.items()):
        out += [f"### {mode}", "",
                "| Initialisation | graines | 20 dB (s) | 20 dB (it.) | PSNR moyen du flux, 20 s et plus (dB) | "
                "PSNR fin du flux (dB) | PSNR final (dB) | it/s | gaussiennes finales |",
                "|---|---|---|---|---|---|---|---|---|"]
        for init in ("aléatoire", "profondeur"):
            rs = by_init.get(init, [])
            if not rs:
                continue
            off = mode == "offline"
            out.append(f"| {init} | {len(rs)} | {fmt([r['t20_s'] for r in rs], 1)} | {fmt([r['t20_step'] for r in rs], 0)} | "
                       f"{'-' if off else fmt([stream_mean(r) for r in rs])} | "
                       f"{'-' if off else fmt([r['psnr_end_of_stream'] for r in rs])} | "
                       f"{fmt([r['psnr_final'] for r in rs])} | {fmt([r['it_per_s'] for r in rs], 1)} | "
                       f"{fmt([r['n_gauss_final'] for r in rs], 0)} |")
        out.append("")
        if mode.startswith("flux") and "aléatoire" in by_init and "profondeur" in by_init:
            ra, rd = by_init["aléatoire"], by_init["profondeur"]
            dm = ms([stream_mean(r) for r in rd])[0] - ms([stream_mean(r) for r in ra])[0]
            de = ms([r["psnr_end_of_stream"] for r in rd])[0] - ms([r["psnr_end_of_stream"] for r in ra])[0]
            df = ms([r["psnr_final"] for r in rd])[0] - ms([r["psnr_final"] for r in ra])[0]
            ta, sa, _ = ms([r["t20_s"] for r in ra])
            td, sd, _ = ms([r["t20_s"] for r in rd])
            earlier = (not math.isnan(ta) and not math.isnan(td) and ta - td > max(sa, sd, 1e-9))
            if (dm >= GAIN_DB or earlier) and de >= 0 and df >= -FINAL_TOL_DB:
                v = "**recommandée pour le live**"
            elif dm <= -GAIN_DB or df < -FINAL_TOL_DB:
                v = "**déconseillée pour le live**"
            else:
                v = "**neutre** : pas de gain suffisant pour son coût (flux de profondeur, rétroprojection)"
            verdict = (f"Option B en {mode} : écart de PSNR moyen du flux {f(dm)} dB, fin du flux {f(de)} dB, "
                       f"final {f(df)} dB, 20 dB {'plus tôt' if earlier else 'pas plus tôt'} "
                       f"({f(td, 1)} contre {f(ta, 1)} s) : {v}.")
    out += ["### Verdict selon la règle (SP-7.md §2)", "", verdict or "Pas de paire aléatoire / profondeur en flux.", ""]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
