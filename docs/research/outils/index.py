"""Régénère INDEX.md à partir des fiches de lecture.

Usage : python outils/index.py

Lit le frontmatter (type, statut, tags) et le titre de chaque sources/*/fiche.md,
regroupe par axe (champ `axe` du frontmatter, sinon colonne `axe` de
outils/corpus_arxiv.tsv, sinon « fournis »).
"""
import csv
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXES = {
    "fournis": "Références fournies avec le sujet",
    "survey": "Surveys — cartographie du domaine (étape 1)",
    "representation": "Représentation & entraînement (étape 2)",
    "rendu": "Rendu rapide, visibilité, LOD (étape 3)",
    "xr": "3DGS spécifique VR/XR et embarqué (étape 3)",
    "streaming": "Streaming & rendu edge/déporté (étape 3)",
    "application": "Applications XR, jumeaux numériques, moteurs (étapes 1 & 4)",
    "localisation": "Localisation des poses : SLAM / VIO temps réel, casque (étape 2, piste mote)",
}


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.split("#")[0].strip()
    return fm


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    axe_of = {}
    with open(os.path.join(ROOT, "outils", "corpus_arxiv.tsv"), encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            axe_of[row["citekey"]] = row["axe"]

    groups = {k: [] for k in AXES}
    for d in sorted(glob.glob(os.path.join(ROOT, "sources", "*"))):
        key = os.path.basename(d)
        fiche = os.path.join(d, "fiche.md")
        if os.path.exists(fiche):
            with open(fiche, encoding="utf-8") as f:
                txt = f.read()
            fm = frontmatter(txt)
            t = re.search(r"^# (.+)$", txt, re.M)
            title = t.group(1).strip() if t else key
            statut = fm.get("statut", "?")
            tags = fm.get("tags", "").strip("[]")
            link = f"[fiche](sources/{key}/fiche.md)"
            axe = fm.get("axe") or axe_of.get(key, "fournis")
        else:
            title, statut, tags, link = "(PDF à récupérer)", "manquant", "", f"[dossier](sources/{key}/)"
            axe = axe_of.get(key, "fournis")
        if axe not in AXES:
            sys.exit(f"{key} : axe inconnu « {axe} », choisir parmi {', '.join(AXES)}")
        groups[axe].append((key, title, statut, tags, link))

    out = ["# Index de la base de connaissance", "",
           "Généré par `python docs/research/outils/index.py`, ne pas éditer à la main.", ""]
    total = 0
    for axe, label in AXES.items():
        rows = groups.get(axe, [])
        if not rows:
            continue
        out += [f"## {label}", "", "| Citekey | Titre | Statut | Tags | |", "|---|---|---|---|---|"]
        for key, title, statut, tags, link in rows:
            out.append(f"| `{key}` | {title} | {statut} | {tags} | {link} |")
            total += 1
        out.append("")
    out.insert(3, f"{total} sources.\n")
    with open(os.path.join(ROOT, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"INDEX.md : {total} sources")


if __name__ == "__main__":
    main()
