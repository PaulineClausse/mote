# Base de recherche (3DGS temps réel pour la XR, localisation SLAM/VIO)

Les papiers que l'on cite depuis le code de mote. Chaque papier est parsé en markdown avec MinerU et résumé dans une fiche de lecture. La base vient du projet de recherche CESI (`Documents/CESI/IR`) et vit maintenant ici : on ingère les nouveaux papiers dans ce dossier.

## Par où commencer

- [INDEX.md](INDEX.md) : toutes les sources classées par axe, avec titre, statut et tags.
- [synthese/localisation_poses.md](synthese/localisation_poses.md) : l'axe SLAM/VIO et ce que la littérature recommande pour mote.
- [synthese/options.md](synthese/options.md) : la matrice comparative des approches 3DGS et les pistes.
- [synthese/comparatif_methodes.md](synthese/comparatif_methodes.md) : le tableau chiffré des méthodes.
- [sujet/problematique.md](sujet/problematique.md) : le sujet et les cibles chiffrées.
- [references.bib](references.bib) : la bibliographie BibTeX. Chaque clé est le nom d'un dossier de `sources/`.

## Organisation

```
research/
├── INDEX.md                   généré par outils/index.py, ne pas éditer
├── references.bib
├── sujet/, synthese/          notes de synthèse
├── sources/<citekey>/
│   ├── fiche.md               fiche de lecture : frontmatter (citekey, mineru_doc, axe, tags)
│   ├── paper.md               texte intégral MinerU, marqueurs de page conservés
│   └── source.pdf, images/, mineru.json   local seulement (gitignorés)
├── supports/                  slides, dossiers web, présentations HTML
├── inbox/                     déposer ici un PDF à ingérer (gitignoré)
└── outils/
    ├── fetch_arxiv.py         arXiv : PDF + BibTeX + ingest.py, en une commande
    ├── ingest.py              PDF local -> sources/<citekey>/
    ├── index.py               régénère INDEX.md
    ├── corpus_arxiv.tsv       manifeste arXiv (arxiv_id, citekey, axe)
    └── fiche_template.md      gabarit de fiche
```

Les PDF, les figures et les `mineru.json` ne sont pas dans git, car ils pèsent environ 900 Mo. Sur un clone neuf, les liens `source.pdf` et les figures de `paper.md` ne mènent donc à rien. Il suffit de relancer `fetch_arxiv.py` ou `ingest.py` pour les recréer. `cao2025_rt-fvhp` et `uzun2025_gs-alive-xr` n'ont pas de fiche, car leur PDF est payant.

## Trouver une référence

- Par thème : `rg -l "piste-mote" docs/research/sources/*/fiche.md` (les tags sont dans le frontmatter).
- Par notion : `rg -i "préintégration" docs/research/sources --glob fiche.md`, puis `paper.md` pour le texte exact.
- Une citation dans une fiche a la forme `` `doc:<mineru_doc>/tier:standard/page:N` ``, ou `` `page:N` `` en abrégé. Une fois le papier ingéré sur la machine, on la relit avec `mineru read "doc:<id>/tier:standard/page:N"`.

## Ajouter un papier

Il faut le CLI `mineru`, son serveur démarré (`mineru server start`), `curl` et Python 3. Toutes les commandes se lancent depuis la racine du repo.

1. **Choisir la citekey**, de la forme `premierauteurAnnée_motclé` en minuscules (par exemple `kerbl2023_3dgs`). Vérifier qu'elle n'existe pas déjà : `ls docs/research/sources`.
2. **Choisir l'axe** parmi `survey`, `representation`, `rendu`, `xr`, `streaming`, `application` et `localisation` (voir `AXES` dans `outils/index.py`).
3. **Ingérer le papier.**
   - Pour un papier arXiv :
     ```
     python docs/research/outils/fetch_arxiv.py <arxiv_id> <citekey> <axe>
     ```
     La commande télécharge le PDF, ajoute l'entrée BibTeX et la ligne du manifeste, puis lance `ingest.py`.
   - Pour un PDF local :
     ```
     python docs/research/outils/ingest.py <chemin.pdf> <citekey>
     ```
     Ajouter ensuite l'entrée BibTeX à la main dans `references.bib` (sur le modèle de `geneva2020_openvins`). Ajouter `--kind supports` s'il s'agit de slides ou d'un cours.

   Un gros PDF peut prendre plusieurs minutes. S'il est déjà parsé, MinerU le sert depuis son cache.
4. **Remplir `sources/<citekey>/fiche.md`.** Le squelette est créé par `ingest.py`. Il faut renseigner `axe`, `type`, `tags` (ajouter `piste-mote` si le papier touche mote) et passer `statut: fiche complète`. Chaque chiffre est cité avec sa page (`` `page:N` ``), lue dans `paper.md`. Les fiches existantes, par exemple `sources/teed2023_dpvo/fiche.md`, montrent le niveau de détail attendu.
5. **Régénérer l'index :** `python docs/research/outils/index.py`.
6. Si le papier change une conclusion, mettre à jour la synthèse concernée dans `synthese/`.
7. Commiter `fiche.md`, `paper.md`, `references.bib`, `INDEX.md` et, s'il a changé, `corpus_arxiv.tsv`.

## Citer depuis le code

On cite par citekey et par page, et on pointe vers la fiche :

```rust
// Patches tirés au hasard plutôt que des features détectées
// (teed2023_dpvo, page 8 ; docs/research/sources/teed2023_dpvo/fiche.md).
```
