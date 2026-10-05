#!/usr/bin/env python3
"""Exécute une commande, la chronomètre (mur + CPU enfant) et ajoute une ligne à un journal JSON.

  python run_timed.py --log out/timings.json --label colmap_mapper -- colmap mapper --database_path ...

Sert au SfM REF (SC-03) et à l'entraînement splatfacto. Code de sortie = celui de la commande.
Le journal est une liste JSON : label, argv, wall_s, exit_code, start (UTC ISO), host.
"""
import argparse
import datetime
import json
import platform
import subprocess
import sys
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, type=Path)
    ap.add_argument("--label", required=True)
    ap.add_argument("--dry-run", action="store_true", help="affiche la commande sans l'exécuter")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd:
        ap.error("commande manquante après --")
    if a.dry_run:
        print("DRY-RUN", a.label, ":", " ".join(cmd))
        return 0
    start = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    t0 = time.perf_counter()
    try:
        code = subprocess.call(cmd)
    except FileNotFoundError:
        print(f"commande introuvable : {cmd[0]} (voir VERSIONS.md)", file=sys.stderr)
        code = 127
    wall = time.perf_counter() - t0
    rows = json.loads(a.log.read_text()) if a.log.exists() else []
    rows.append({"label": a.label, "argv": cmd, "wall_s": round(wall, 2), "exit_code": code,
                 "start": start, "host": platform.node()})
    a.log.parent.mkdir(parents=True, exist_ok=True)
    a.log.write_text(json.dumps(rows, indent=1))
    print(f"[{a.label}] {wall:.1f} s, exit {code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
