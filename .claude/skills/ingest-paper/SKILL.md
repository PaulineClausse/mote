---
name: ingest-paper
description: Add a research paper (arXiv id or PDF) to the mote knowledge base in docs/research — MinerU parse, BibTeX, reading note, index. Use when asked to ingest, add, or read a paper for mote, or when code needs a reference that is not yet in docs/research/INDEX.md.
---

The procedure, the conventions and the list of axes are in `docs/research/README.md`, section "Ajouter un papier". Read that section, then follow it step by step. In short:

1. Check that the paper is not already there: `rg -i "<title words>" docs/research/INDEX.md`.
2. If `mineru server status` says it is not running, start it with `mineru server start`.
3. Ingest the paper. For arXiv: `python docs/research/outils/fetch_arxiv.py <arxiv_id> <citekey> <axe>`. For a local PDF: `python docs/research/outils/ingest.py <pdf> <citekey>`, then add the BibTeX entry by hand. Either way it can take several minutes, so run it in the background.
4. Fill `docs/research/sources/<citekey>/fiche.md` from `paper.md`. Write it in French, like the existing notes, and give a `page:N` locator for every figure and quote. Do not invent numbers: if the paper does not give one, say so.
5. Run `python docs/research/outils/index.py` to regenerate the index, and update the relevant `synthese/` note if a conclusion changes.
6. `source.pdf`, `images/` and `mineru.json` are gitignored, so do not try to commit them.
