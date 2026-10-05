#!/usr/bin/env python3
"""Hold-out par blocs temporels contigus (SPEC 13.1 point 3). Outil de spike jetable.

Lit la liste des images d'un export COLMAP (dossier images/ ou images.txt), regroupe gauche et
droite ensemble (clé de paire = nom sans 'left'/'right'), ordonne dans le temps (ordre lexical des
noms, qui portent un horodatage), puis tient à part `--block` paires consécutives toutes les
`--period` paires (défaut 5 sur 40 = 12,5 %, dans la fourchette 10 à 15 %).

Écrit dans --out-dir : train_list.txt, test_list.txt (une image par ligne, nom de fichier relatif à
images/, format lu par le dataparser COLMAP de nerfstudio : à confirmer sur la version figée,
VERSIONS.md), holdout.json (noms, blocs) et affiche le décompte.
Les mêmes noms doivent être exclus du SfM REF seulement si on veut un REF « honnête » pour la
géométrie : par défaut REF utilise toutes les images (alignement des poses), voir PROTOCOL.md.
"""
import argparse
import json
import re
import sys
from pathlib import Path

EXTS = {".png", ".jpg", ".jpeg"}


def pair_key(name: str) -> str:
    return re.sub(r"(left|right)[_\-]?", "", Path(name).stem, flags=re.I)


def split(names, block=5, period=40, offset=None):
    groups = {}
    for n in names:
        groups.setdefault(pair_key(n), []).append(n)
    keys = sorted(groups)
    off = period // 2 if offset is None else offset      # évite de commencer par un bloc de test
    test_keys = {k for i, k in enumerate(keys) if (i - off) % period < block and i >= off}
    test = [n for k in keys if k in test_keys for n in groups[k]]
    train = [n for k in keys if k not in test_keys for n in groups[k]]
    return train, test, keys, test_keys


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", required=True, type=Path, help="dossier images/ de l'export COLMAP")
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--block", type=int, default=5)
    ap.add_argument("--period", type=int, default=40)
    a = ap.parse_args(argv)
    names = sorted(p.relative_to(a.images).as_posix() for p in a.images.rglob("*") if p.suffix.lower() in EXTS)
    if not names:
        raise SystemExit(f"aucune image dans {a.images}")
    train, test, keys, test_keys = split(names, a.block, a.period)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    (a.out_dir / "train_list.txt").write_text("\n".join(train) + "\n")
    (a.out_dir / "test_list.txt").write_text("\n".join(test) + "\n")
    (a.out_dir / "holdout.json").write_text(json.dumps(
        {"block": a.block, "period": a.period, "n_pairs": len(keys), "n_test_pairs": len(test_keys),
         "test": test}, indent=1))
    print(f"{len(keys)} paires, {len(test_keys)} tenues à part "
          f"({100 * len(test_keys) / len(keys):.1f} %), {len(train)} images train, {len(test)} images test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
