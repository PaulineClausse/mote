#!/usr/bin/env python3
"""SP-4 : tableaux de SP-4.md à partir des journaux de la sonde (sp4_phases.jsonl, sp4_seconds.csv). Python seul.

  python docs/spikes/sp4/analyze_sp4.py <dossier sp4 récupéré du casque>

Applique la règle de SP-4.md §2 : verdict sur H-05 et budget proposé pour NFR-05.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

PHASES = ("Baseline", "GetColors", "Nominal")


def f(x, nd=1):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}".replace(".", ",")


def load(d: Path) -> tuple[dict, list[dict]]:
    phases: dict = {}
    for line in (d / "sp4_phases.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if "phase" in r:
                phases[r["phase"]] = {**phases.get(r["phase"], {}), **r}
    seconds = list(csv.DictReader((d / "sp4_seconds.csv").open(encoding="utf-8", newline="")))
    return phases, seconds


def verdict(ph: dict) -> tuple[list[str], dict]:
    """Règle de SP-4.md §2. Renvoie les lignes de verdict et les grandeurs utiles au budget."""
    base, nom = ph.get("Baseline"), ph.get("Nominal")
    core = (ph.get("Close") or {}).get("core") or (nom or {}).get("core") or {}
    if not base or not nom or not core:
        return ["Verdict impossible : phases Baseline, Nominal ou statistiques du core manquantes."], {}
    fps_ok = nom["fps"] >= 0.98 * base["fps"]
    missed_b = base["missed"] / max(1, base["frames"])
    missed_n = nom["missed"] / max(1, nom["frames"])
    missed_ok = missed_n <= missed_b + 0.005
    lost = core["pairs_dropped"] / max(1, core["pairs_pushed"])
    lost_ok = lost < 0.01
    kept_up = core["pairs_encoded"] + core["pairs_dropped"] == core["pairs_pushed"] and core.get("errors", 0) == 0
    thermal_ok = nom.get("thermal_status", -1) < 3
    gc = ph.get("GetColors", {})
    gc_drop = gc and (gc["fps"] < 0.98 * base["fps"] or gc["missed"] / max(1, gc["frames"]) > missed_b + 0.005)
    checks = [("fréquence d'affichage tenue (≥ 98 % de la référence)", fps_ok,
               f"{f(nom['fps'])} contre {f(base['fps'])} images/s"),
              ("images ratées pas plus nombreuses (+0,5 point au plus)", missed_ok,
               f"{f(100 * missed_n, 2)} % contre {f(100 * missed_b, 2)} %"),
              ("paires perdues par saturation < 1 % (NFR-02)", lost_ok, f"{f(100 * lost, 2)} %"),
              ("le core suit (tout ce qui est poussé est encodé ou compté perdu, sans erreur)", kept_up,
               f"{core['pairs_encoded']} encodées, {core['pairs_dropped']} perdues, {core['pairs_pushed']} poussées"),
              ("pas d'alerte thermique sévère (statut < 3)", thermal_ok, f"statut {nom.get('thermal_status')}")]
    ok = all(c[1] for c in checks)
    only_display = not fps_ok or not missed_ok
    if ok:
        v = "**validée**"
    elif lost_ok and kept_up and thermal_ok and only_display and gc_drop:
        v = ("**validée avec réserve** : la baisse d'affichage apparaît dès la phase GetColors, avant le core ; "
             "c'est la lecture CPU de l'hôte qu'il faut changer (AsyncGPUReadback), pas le core")
    else:
        v = "**invalidée**"
    lines = [f"- {'oui' if c[1] else 'NON'} : {c[0]} ({c[2]})" for c in checks] + ["", f"H-05 : {v}."]
    core_pct = 100 * core["core_cpu_s"] / max(1e-3, core["wall_s"])
    return lines, {"core_pct": core_pct, "push_ms_max": core["push_ms_max"], "push_ms_avg": core["push_ms_avg"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dir", type=Path)
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    ph, seconds = load(a.dir)
    out = []
    b = (ph.get("Bench") or {}).get("bench")
    if b:
        out += ["### Encodage pur (images synthétiques 1280 x 1280, un thread)", "",
                f"{b['n']} images, JPEG q{b['quality']} : médiane {f(b['ms_p50'])} ms, p95 {f(b['ms_p95'])} ms par "
                f"image, {f(b['kb_avg'], 0)} Ko en moyenne ; soit {f(2 * b['ms_p50'])} ms par paire sur un cœur.", ""]
    out += ["### Phases", "", "| Phase | durée (s) | images/s | affichage (Hz) | intervalle p50 / p99 (ms) | "
            "images ratées | CPU du processus (% d'un cœur) | GetColors par paire p50 / p95 / max (ms) | thermique |",
            "|---|---|---|---|---|---|---|---|---|"]
    for name in PHASES:
        p = ph.get(name)
        if not p:
            continue
        gc = (f"{f(p['getcolors_ms_p50'], 2)} / {f(p['getcolors_ms_p95'], 2)} / {f(p['getcolors_ms_max'], 2)}"
              if p.get("getcolors_pairs") else "-")
        out.append(f"| {name} | {f(p['wall_s'], 0)} | {f(p['fps'])} | {f(p['refresh_hz'], 0)} | "
                   f"{f(p['dt_p50_ms'], 2)} / {f(p['dt_p99_ms'], 2)} | {p['missed']} ({f(100 * p['missed'] / max(1, p['frames']), 2)} %) | "
                   f"{f(p['process_cpu_pct'])} sur {p['cores']} cœurs | {gc} | {p.get('thermal_status')} |")
    core = (ph.get("Close") or {}).get("core") or (ph.get("Nominal") or {}).get("core")
    if core:
        out += ["", "### Core pendant la phase nominale", "",
                "| Mesure | valeur |", "|---|---|",
                f"| paires poussées / encodées / perdues | {core['pairs_pushed']} / {core['pairs_encoded']} / {core['pairs_dropped']} |",
                f"| copie dans sp4_push_pair (thread principal), moyenne / max | {f(core['push_ms_avg'], 2)} / {f(core['push_ms_max'], 2)} ms |",
                f"| encodage JPEG par image, p50 / p95 / max | {f(core['encode_ms_p50'])} / {f(core['encode_ms_p95'])} / {f(core['encode_ms_max'])} ms |",
                f"| écriture MCAP par image, moyenne | {f(core['write_ms_avg'], 2)} ms |",
                f"| JPEG moyen | {f(core['jpeg_kb_avg'], 0)} Ko |",
                f"| CPU des threads du core | {f(core['core_cpu_s'])} s sur {f(core['wall_s'])} s, soit "
                f"{f(100 * core['core_cpu_s'] / max(1e-3, core['wall_s']))} % d'un cœur |"]
    lines, g = verdict(ph)
    out += ["", "### Verdict selon la règle (SP-4.md §2)", ""] + lines
    if g:
        budget = 5 * math.ceil(1.25 * g["core_pct"] / 5)
        out += ["", f"Budget NFR-05 proposé : threads du core ≤ {budget} % d'un cœur en configuration nominale "
                f"(mesuré {f(g['core_pct'])} %, marge de 25 %, arrondi aux 5 % supérieurs) ; appel `mote_push_*` d'une "
                f"paire ≤ {f(max(1.0, math.ceil(2 * g['push_ms_max']) / 2), 1)} ms sur le thread de l'hôte (max mesuré "
                f"{f(g['push_ms_max'], 2)} ms, arrondi au demi-ms supérieur)."]
    if seconds:
        hot = [r for r in seconds if r["thermal_status"] not in ("", "-1", "0")]
        out += ["", f"Journal par seconde : {len(seconds)} lignes ; secondes avec un statut thermique non nul : {len(hot)}."]
    text = "\n".join(out)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
