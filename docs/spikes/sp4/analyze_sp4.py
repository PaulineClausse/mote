#!/usr/bin/env python3
"""SP-4 : tableaux de SP-4.md à partir des journaux de la sonde (sp4_phases.jsonl, sp4_seconds.csv). Python seul.

  python docs/spikes/sp4/analyze_sp4.py <dossier sp4 récupéré du casque>

Applique la règle de SP-4.md §2 à la phase Nominal (GetColors sur le thread principal + core), puis les mêmes critères à
la phase Async (relecture GPU asynchrone + core), le remède que la règle prévoit. Refuse de conclure quand le core n'a
reçu aucune paire. Budget proposé pour NFR-05.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

PHASES = ("Baseline", "GetColors", "Nominal", "Async")


def f(x, nd=1):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}".replace(".", ",")


def load(d: Path) -> tuple[dict, list[dict], list[dict]]:
    phases: dict = {}
    events: list[dict] = []
    for line in (d / "sp4_phases.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if "phase" in r and "event" not in r:
                phases[r["phase"]] = {**phases.get(r["phase"], {}), **r}
            else:
                events.append(r)
    seconds = list(csv.DictReader((d / "sp4_seconds.csv").open(encoding="utf-8", newline="")))
    return phases, seconds, events


def core_of(ph: dict, name: str) -> dict:
    """Statistiques du core d'une phase ; l'ancienne sonde les mettait dans une ligne Close (phase Nominal)."""
    c = (ph.get(name) or {}).get("core")
    if not c and name == "Nominal":
        c = (ph.get("Close") or {}).get("core")
    return c or {}


def checks_for(ph: dict, name: str) -> tuple[list, dict] | None:
    """Critères de SP-4.md §2 pour une phase avec core. None si la phase manque ou si le core n'a rien reçu."""
    base, p, core = ph.get("Baseline"), ph.get(name), core_of(ph, name)
    if not base or not p or not core or core.get("pairs_pushed", 0) == 0:
        return None
    missed_b = base["missed"] / max(1, base["frames"])
    missed_p = p["missed"] / max(1, p["frames"])
    lost = core["pairs_dropped"] / max(1, core["pairs_pushed"])
    kept_up = core["pairs_encoded"] + core["pairs_dropped"] == core["pairs_pushed"] and core.get("errors", 0) == 0
    checks = [("fréquence d'affichage tenue (≥ 98 % de la référence)", p["fps"] >= 0.98 * base["fps"],
               f"{f(p['fps'])} contre {f(base['fps'])} images/s"),
              ("images ratées pas plus nombreuses (+0,5 point au plus)", missed_p <= missed_b + 0.005,
               f"{f(100 * missed_p, 2)} % contre {f(100 * missed_b, 2)} %"),
              ("paires perdues par saturation < 1 % (NFR-02)", lost < 0.01, f"{f(100 * lost, 2)} %"),
              ("le core suit (tout ce qui est poussé est encodé ou compté perdu, sans erreur)", kept_up,
               f"{core['pairs_encoded']} encodées, {core['pairs_dropped']} perdues, {core['pairs_pushed']} poussées"),
              ("pas d'alerte thermique sévère (statut < 3)", p.get("thermal_status", -1) < 3,
               f"statut {p.get('thermal_status')}")]
    return checks, core


def verdict(ph: dict) -> tuple[list[str], dict]:
    """Règle de SP-4.md §2 sur Nominal ; remède vérifié sur Async. Renvoie les lignes et les grandeurs du budget."""
    base = ph.get("Baseline")
    nom = checks_for(ph, "Nominal")
    if not base or nom is None:
        pushed = core_of(ph, "Nominal").get("pairs_pushed", 0)
        why = ("aucune paire poussée au core en phase Nominal (voir les compteurs not_created / bad_size et "
               "l'événement « size »)" if ph.get("Nominal") and pushed == 0 else
               "phases Baseline ou Nominal, ou statistiques du core, manquantes")
        lines = [f"Verdict impossible sur la phase Nominal : {why}."]
    else:
        checks, _ = nom
        ok = all(c[1] for c in checks)
        display_only = not (checks[0][1] and checks[1][1]) and all(c[1] for c in checks[2:])
        gc = ph.get("GetColors", {})
        missed_b = base["missed"] / max(1, base["frames"])
        gc_drop = bool(gc) and (gc["fps"] < 0.98 * base["fps"] or gc["missed"] / max(1, gc["frames"]) > missed_b + 0.005)
        if ok:
            v = "**validée**"
        elif display_only and gc_drop:
            v = ("**validée avec réserve** : la baisse d'affichage apparaît dès la phase GetColors, avant le core ; "
                 "c'est la lecture CPU de l'hôte qu'il faut changer (relecture GPU asynchrone), pas le core")
        else:
            v = "**invalidée**"
        lines = ["Phase Nominal (GetColors sur le thread principal + core) :", ""]
        lines += [f"- {'oui' if c[1] else 'NON'} : {c[0]} ({c[2]})" for c in checks] + ["", f"H-05 : {v}."]
    asy = checks_for(ph, "Async")
    if asy is not None:
        checks, _ = asy
        ok = all(c[1] for c in checks)
        lines += ["", "Phase Async (relecture GPU asynchrone + core), le remède prévu par la règle :", ""]
        lines += [f"- {'oui' if c[1] else 'NON'} : {c[0]} ({c[2]})" for c in checks]
        lines += ["", "Remède : " + ("**confirmé**, tous les critères tiennent avec la relecture asynchrone." if ok else
                                     "**non confirmé**, voir les critères en échec.")]
    elif ph.get("Async"):
        lines += ["", "Phase Async : aucune paire poussée au core (voir les compteurs et l'événement « size »)."]
    cores = [c for c in (core_of(ph, "Nominal"), core_of(ph, "Async")) if c.get("pairs_pushed")]
    if not cores:
        return lines, {}
    pct = max(100 * c["core_cpu_s"] / max(1e-3, c["wall_s"]) for c in cores)
    push_max = max(c["push_ms_max"] for c in cores)
    return lines, {"core_pct": pct, "push_ms_max": push_max}


def core_table(name: str, core: dict, p: dict) -> list[str]:
    return [f"### Core, phase {name}", "",
            "| Mesure | valeur |", "|---|---|",
            f"| paires poussées / encodées / perdues | {core['pairs_pushed']} / {core['pairs_encoded']} / {core['pairs_dropped']} |",
            f"| copie dans sp4_push_pair (thread principal), moyenne / max | {f(core['push_ms_avg'], 2)} / {f(core['push_ms_max'], 2)} ms |",
            f"| encodage JPEG par image, p50 / p95 / max | {f(core['encode_ms_p50'])} / {f(core['encode_ms_p95'])} / {f(core['encode_ms_max'])} ms |",
            f"| écriture MCAP par image, moyenne | {f(core['write_ms_avg'], 2)} ms |",
            f"| JPEG moyen | {f(core['jpeg_kb_avg'], 0)} Ko |",
            f"| CPU des threads du core | {f(core['core_cpu_s'])} s sur {f(core['wall_s'])} s, soit "
            f"{f(100 * core['core_cpu_s'] / max(1e-3, core['wall_s']))} % d'un cœur |",
            f"| MCAP | `{Path(core.get('mcap', '')).name}` |", ""]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dir", type=Path)
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    ph, seconds, events = load(a.dir)
    out = []
    b = (ph.get("Bench") or {}).get("bench")
    if b:
        out += ["### Encodage pur (images synthétiques 1280 x 1280, un thread)", "",
                f"{b['n']} images, JPEG q{b['quality']} : médiane {f(b['ms_p50'])} ms, p95 {f(b['ms_p95'])} ms par "
                f"image, {f(b['kb_avg'], 0)} Ko en moyenne ; soit {f(2 * b['ms_p50'])} ms par paire sur un cœur.", ""]
    out += ["### Phases", "", "| Phase | durée (s) | images/s | affichage (Hz) | intervalle p50 / p99 (ms) | "
            "images ratées | CPU du processus (% d'un cœur) | lecture, thread principal, par paire p50 / p95 / max (ms) | "
            "paires poussées | écartées (pas d'image / taille / file / erreurs) | thermique |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in PHASES:
        p = ph.get(name)
        if not p:
            continue
        gc = (f"{f(p['getcolors_ms_p50'], 2)} / {f(p['getcolors_ms_p95'], 2)} / {f(p['getcolors_ms_max'], 2)}"
              if p.get("getcolors_pairs") else "-")
        rej = f"{p.get('not_created', '-')} / {p.get('bad_size', '-')} / {p.get('skipped', '-')} / {p.get('errors', '-')}"
        out.append(f"| {name} | {f(p['wall_s'], 0)} | {f(p['fps'])} | {f(p['refresh_hz'], 0)} | "
                   f"{f(p['dt_p50_ms'], 2)} / {f(p['dt_p99_ms'], 2)} | {p['missed']} ({f(100 * p['missed'] / max(1, p['frames']), 2)} %) | "
                   f"{f(p['process_cpu_pct'])} sur {p['cores']} cœurs | {gc} | {p.get('pairs_pushed', '-')} | {rej} | "
                   f"{p.get('thermal_status')} |")
    asy = ph.get("Async")
    if asy and asy.get("latency_frames_p50") is not None:
        out += ["", f"Relecture asynchrone : latence médiane {asy['latency_frames_p50']} frames, max "
                f"{asy['latency_frames_max']} ; la colonne « lecture » compte la demande et les deux callbacks (copie "
                f"de l'image gauche et push compris)."]
    out.append("")
    for name in ("Nominal", "Async"):
        c = core_of(ph, name)
        if c:
            out += core_table(name, c, ph.get(name, {}))
    for e in events:
        if e.get("event") == "size":
            out.append(f"Diagnostic {e.get('phase')} ({e.get('mode')}) : tableau {e.get('len_left')} / {e.get('len_right')} "
                       f"pixels, retenu {e.get('width')} x {e.get('height')}, texture {e.get('texture')}, "
                       f"CurrentResolution {e.get('current_resolution')}.")
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
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
