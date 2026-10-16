"""Ligne de commande `mote` (SPEC-834a) : `mote ingest --replay`, `mote export`, `mote train`. Les autres
sous-commandes (eval, validate) viendront avec leurs work packages."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import mote


def _listen(a: argparse.Namespace) -> Path | None:
    """Reçoit une session du casque (SPEC-9df2) ; renvoie le MCAP côté PC une fois la session complète."""
    from mote.ingest.live import LiveConfig, serve
    host, _, port = a.listen.rpartition(":")
    token = a.token or os.environ.get("MOTE_TOKEN", "")
    if not token:
        print("mote ingest : jeton requis (--token ou variable MOTE_TOKEN), le même que celui du casque",
              file=sys.stderr)
        return None
    cfg = LiveConfig(host=host or "0.0.0.0", port=int(port), token=token,
                     sessions_dir=a.sessions or a.out.parent / "sessions",
                     resend_after_s=a.resend_after, idle_timeout_s=a.idle_timeout)
    try:
        return serve(cfg)
    except TimeoutError as e:
        print(f"mote ingest : {e}", file=sys.stderr)
        return None


def _ingest(a: argparse.Namespace) -> int:
    if bool(a.replay) == bool(a.listen):
        print("mote ingest : --replay <fichier.mcap> ou --listen [hôte:]port, l'un des deux", file=sys.stderr)
        return 2
    source = a.replay or _listen(a)
    if source is None:
        return 4
    from mote.ingest.replay import ingest_replay
    try:
        s = ingest_replay(source, a.out)
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


def _train(a: argparse.Namespace) -> int:
    from mote.train.launch import train
    try:
        ckpt = train(a.dataset, a.runs or a.dataset / "runs", method=a.method, iterations=a.iterations,
                     device=a.device)
    except RuntimeError as e:
        print(f"mote train : {e}", file=sys.stderr)
        return 4
    print(ckpt)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mote", description=f"mote {mote.__version__}, côté PC")
    sub = ap.add_subparsers(dest="cmd", required=True)
    pi = sub.add_parser("ingest", help="MCAP -> répertoire de dataset")
    pi.add_argument("--replay", type=Path, help="fichier MCAP à rejouer (hors ligne)")
    pi.add_argument("--listen", metavar="[HÔTE:]PORT", help="reçoit le flux live du casque (SPEC-9df2)")
    pi.add_argument("--token", help="jeton partagé avec le casque (sinon la variable MOTE_TOKEN)")
    pi.add_argument("--sessions", type=Path, help="où écrire le MCAP reçu (défaut : <out>/../sessions)")
    pi.add_argument("--resend-after", type=float, default=2.0, metavar="S",
                    help="délai avant de redemander un message manquant (défaut 2 s ; plus long sur réseau chargé)")
    pi.add_argument("--idle-timeout", type=float, default=0.0, metavar="S",
                    help="abandon après S secondes sans rien recevoir (défaut 0 : attendre)")
    pi.add_argument("--out", type=Path, required=True, help="répertoire de dataset, vide ou absent")
    pi.set_defaults(fn=_ingest)
    pe = sub.add_parser("export", help="dataset -> nerfstudio et/ou COLMAP")
    pe.add_argument("dataset", type=Path)
    pe.add_argument("--format", choices=("nerfstudio", "colmap", "all"), default="all")
    pe.add_argument("--out", type=Path, help="par défaut <dataset>/export")
    pe.set_defaults(fn=_export)
    pt = sub.add_parser("train", help="dataset -> entraînement nerfstudio, dans son propre environnement (ADR-976d)")
    pt.add_argument("dataset", type=Path)
    pt.add_argument("--method", default="splatfacto", help="méthode ns-train (défaut : splatfacto)")
    pt.add_argument("--iterations", type=int, default=30000)
    pt.add_argument("--device", default="cuda", choices=("cuda", "cpu", "mps"))
    pt.add_argument("--runs", type=Path, help="par défaut <dataset>/runs")
    pt.set_defaults(fn=_train)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
