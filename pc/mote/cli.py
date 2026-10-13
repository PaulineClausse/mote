"""Ligne de commande `mote` (SPEC-834a) : `mote ingest --replay`, `mote export`. Les autres sous-commandes (train,
eval, validate) viendront avec leurs work packages."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import mote


def _ingest(a: argparse.Namespace) -> int:
    if not a.replay:
        print("mote ingest : seul le mode --replay <fichier.mcap> existe pour l'instant (réception live : WP-14)",
              file=sys.stderr)
        return 2
    from mote.ingest.replay import ingest_replay
    try:
        s = ingest_replay(a.replay, a.out)
    except FileExistsError as e:
        print(f"mote ingest : {e}", file=sys.stderr)
        return 3
    print(json.dumps({k: s[k] for k in ("images", "kept_segment", "complete", "dropped")}, ensure_ascii=False))
    if not s["complete"]:
        print("attention : session incomplète (seq manquants ou pas de /session/end), voir session.json",
              file=sys.stderr)
    return 0


def _export(a: argparse.Namespace) -> int:
    from mote.tools.export import export_colmap, export_nerfstudio
    out = a.out or a.dataset / "export"
    if a.format in ("nerfstudio", "all"):
        print(export_nerfstudio(a.dataset, out / "nerfstudio"))
    if a.format in ("colmap", "all"):
        print(export_colmap(a.dataset, out / "colmap" / "sparse" / "0"))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mote", description=f"mote {mote.__version__}, côté PC")
    sub = ap.add_subparsers(dest="cmd", required=True)
    pi = sub.add_parser("ingest", help="MCAP -> répertoire de dataset")
    pi.add_argument("--replay", type=Path, help="fichier MCAP à rejouer (hors ligne)")
    pi.add_argument("--out", type=Path, required=True, help="répertoire de dataset, vide ou absent")
    pi.set_defaults(fn=_ingest)
    pe = sub.add_parser("export", help="dataset -> nerfstudio et/ou COLMAP")
    pe.add_argument("dataset", type=Path)
    pe.add_argument("--format", choices=("nerfstudio", "colmap", "all"), default="all")
    pe.add_argument("--out", type=Path, help="par défaut <dataset>/export")
    pe.set_defaults(fn=_export)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
