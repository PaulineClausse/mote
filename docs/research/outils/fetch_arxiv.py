"""Récupère des papiers arXiv, les ajoute à references.bib et lance la chaîne MinerU.

Usage :
    python docs/research/outils/fetch_arxiv.py                  # tout outils/corpus_arxiv.tsv
    python docs/research/outils/fetch_arxiv.py 2505.10144 tu2025_vrsplat rendu   # un papier

Avec un seul papier, l'axe (voir AXES dans index.py) est ajouté au manifeste
outils/corpus_arxiv.tsv s'il n'y est pas encore.

Les papiers déjà présents (sources/<citekey>/paper.md) sont ignorés.
"""
import csv
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Mozilla/5.0 (cesi-ir research knowledge base)"


def curl(url, out=None):
    args = ["curl", "-sL", "--fail", "-A", UA, url]
    if out:
        args += ["-o", out]
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl {url} -> code {r.returncode}")
    return r.stdout.decode("utf-8") if not out else None


def metadata(arxiv_id):
    x = curl(f"https://export.arxiv.org/api/query?id_list={arxiv_id}")
    e = x.split("<entry>")[1]
    title = " ".join(re.search(r"<title>(.*?)</title>", e, re.S).group(1).split())
    authors = re.findall(r"<name>(.*?)</name>", e)
    year = re.search(r"<published>(\d{4})", e).group(1)
    return title, authors, year


def bib_entry(key, arxiv_id, title, authors, year):
    return (f"@misc{{{key},\n  author = {{{' and '.join(authors)}}},\n  title  = {{{title}}},\n"
            f"  year   = {{{year}}},\n  eprint = {{{arxiv_id}}},\n  archivePrefix = {{arXiv}},\n"
            f"  url    = {{https://arxiv.org/abs/{arxiv_id}}}\n}}\n")


def fetch(arxiv_id, key):
    if os.path.exists(os.path.join(ROOT, "sources", key, "paper.md")):
        print(f"= {key} déjà présent")
        return
    title, authors, year = metadata(arxiv_id)
    print(f"+ {key} : {title}")
    pdf = os.path.join(ROOT, "inbox", f"{key}.pdf")
    if not os.path.exists(pdf):
        curl(f"https://arxiv.org/pdf/{arxiv_id}", pdf)
    bib = os.path.join(ROOT, "references.bib")
    with open(bib, encoding="utf-8") as f:
        known = f"{{{key}," in f.read()
    if not known:
        with open(bib, "a", encoding="utf-8") as f:
            f.write("\n" + bib_entry(key, arxiv_id, title, authors, year))
    r = subprocess.run([sys.executable, os.path.join(ROOT, "outils", "ingest.py"), pdf, key])
    if r.returncode == 0:
        os.remove(pdf)  # la copie de référence est sources/<key>/source.pdf
    time.sleep(3)  # politesse envers l'API arXiv


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    tsv = os.path.join(ROOT, "outils", "corpus_arxiv.tsv")
    with open(tsv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    if len(sys.argv) in (3, 4):
        arxiv_id, key = sys.argv[1], sys.argv[2]
        if len(sys.argv) == 4 and key not in {r["citekey"] for r in rows}:
            with open(tsv, "a", encoding="utf-8", newline="") as f:
                f.write(f"{arxiv_id}\t{key}\t{sys.argv[3]}\n")
        fetch(arxiv_id, key)
        return
    for row in rows:
        try:
            fetch(row["arxiv_id"], row["citekey"])
        except Exception as ex:
            print(f"! {row['citekey']} : {ex}")


if __name__ == "__main__":
    main()
