"""Chaîne d'extraction MinerU -> base de connaissance.

Usage :
    python docs/research/outils/ingest.py <chemin.pdf> <citekey> [--kind sources|supports] [--tier standard]

Produit dans <kind>/<citekey>/ :
    source.pdf   copie du PDF d'origine          (gitignoré)
    paper.md     markdown MinerU (pages entières, marqueurs de page conservés)
    images/      figures exportées en PNG          (gitignoré)
    mineru.json  sortie structurée MinerU (blocs + bbox) (gitignoré)
    fiche.md     squelette de fiche de lecture (créé seulement s'il n'existe pas)

Prérequis : `mineru server start` (serveur local, tier standard).
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARSED = os.path.join(os.path.expanduser("~"), ".mineru", "doclib", "parsed")
IMG_LINK = re.compile(r"\]\((doc:([0-9a-f]+)/tier:(\w+)/page:(\d+)/block:(\d+))\)")


def mineru(*args, check=True):
    r = subprocess.run(["mineru", *args], capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        sys.exit(f"mineru {' '.join(args)} a échoué :\n{r.stdout}\n{r.stderr}")
    return r


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("citekey")
    ap.add_argument("--kind", default="sources", choices=["sources", "supports"])
    ap.add_argument("--tier", default="standard")
    ap.add_argument("--wait", default="1800")
    a = ap.parse_args()

    out = os.path.join(ROOT, a.kind, a.citekey)
    os.makedirs(os.path.join(out, "images"), exist_ok=True)
    src = os.path.join(out, "source.pdf")
    if os.path.abspath(a.pdf) != os.path.abspath(src):
        shutil.copy2(a.pdf, src)

    # 1. Parse complet (ou cache) -> métadonnées
    r = mineru("parse", src, "--pages", "all", "--tier", a.tier, "--wait", a.wait, "--json", check=False)
    info = json.loads(r.stdout)
    if "error" in info:
        sys.exit(f"Erreur MinerU : {info['error']['code']} — {info['error'].get('user_action')}")
    parse = info["parse"]
    print(f"[parse] {parse['short_id']} tier={parse['tier']} pages={parse['page_range']} cache={parse['cache_hit']}")

    # 2. Markdown
    md_path = os.path.join(out, "paper.md" if a.kind == "sources" else "slides.md")
    mineru("parse", src, "--pages", "all", "--tier", a.tier, "--output", md_path)
    with open(md_path, encoding="utf-8") as f:
        md = f.read()

    # 3. Export des figures + réécriture des liens
    def repl(m):
        loc, _, _, page, block = m.groups()
        name = f"{a.citekey}_p{page}_b{block}.png"
        dst = os.path.join(out, "images", name)
        if not os.path.exists(dst):
            mineru("read", loc, "--format", "image", "--output", dst)
        return f"](images/{name})"

    md, n = IMG_LINK.subn(repl, md)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[images] {n} figures exportées")

    # 4. JSON structuré (le plus récent pour ce tier)
    sha = parse["sha256"]
    cands = sorted(glob.glob(os.path.join(PARSED, sha[:2], sha, parse["tier"], "*.json")), key=os.path.getmtime)
    if cands:
        shutil.copy2(cands[-1], os.path.join(out, "mineru.json"))
        print("[json] mineru.json copié")

    # 5. Squelette de fiche
    fiche = os.path.join(out, "fiche.md")
    if a.kind == "sources" and not os.path.exists(fiche):
        tpl = os.path.join(ROOT, "outils", "fiche_template.md")
        with open(tpl, encoding="utf-8") as f:
            txt = f.read().replace("{{citekey}}", a.citekey).replace("{{doc_id}}", parse["short_id"])
        with open(fiche, "w", encoding="utf-8") as f:
            f.write(txt)
        print("[fiche] squelette créé")
    print(f"OK -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
