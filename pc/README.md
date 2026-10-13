# pc

Paquet Python `mote` : ingest, entraînement, évaluation, outils (ADR-8d03, SPEC-834a). Prérequis :
[`uv`](https://docs.astral.sh/uv/), Python 3.11 ou plus.

## Commandes

```sh
uv run --project pc mote ingest --replay session.mcap --out dataset/   # MCAP -> dataset (WP-07)
uv run --project pc mote export dataset/                                # -> dataset/export/{nerfstudio,colmap}
```

`mote export --format nerfstudio|colmap|all --out <dossier>`.

- `transforms.json` : à donner à `ns-train splatfacto --data <dossier>/nerfstudio`.
- `colmap/sparse/0` : modèle texte, avec les images dans `<dataset>/images`.

## Répertoire de dataset (`mote ingest`)

| Fichier | Contenu |
|---|---|
| `images/<left\|right>/<pair_id>.jpg` | le JPEG d'origine, octet pour octet (`.png` pour une session `RAW_RGBA`) |
| `frames.jsonl` | une ligne par image, dans l'ordre de capture (champs ci-dessous) |
| `session.json` | SessionInfo, segments, images écartées et pourquoi, empreinte du MCAP, conversion appliquée |

Chaque ligne de `frames.jsonl` contient :
- l'image : `file`, `camera`, `pair_id`, `seq`, `codec`, `width`, `height`, `blur_score`, `exposure_ns`, `iso` ;
- le temps : `t_ns` (horloge mote), `src_time_ns`, `src_domain` ;
- les intrinsèques ramenées à la taille de l'image : `fx`, `fy`, `cx`, `cy`, `model`, `dist` ;
- la pose : `world_from_camera` (4 x 4, repère canonique) et `pose_source` (`frame` ou `hmd_interp`) ;
- le découpage : `segment`.

Repère canonique (SPEC-64c5 §9.4) : monde main droite et métrique ; caméras OpenCV (x droite, y bas, z avant).

- **Conversion depuis Unity** (`unity-flipz/v0`) : c'est la formule de §9.4, la même que SRC-3, avec laquelle SP-0 a
  validé H-01. Elle reste une hypothèse jusqu'au test de reprojection sur cible connue (SP-2, WP-08).
- **Recentrage** : la session est découpée à chaque `RECENTER`, et seul le plus long segment est gardé.
- **Image sans pose** : sa pose est interpolée sur `/pose/hmd`, puis composée avec les extrinsèques de la caméra.

Deux ingests du même MCAP donnent des répertoires identiques bit à bit (NFR-07).

## Tests

```sh
uv run --project pc --group dev pytest pc                      # 16 tests, MCAP d'exemple pc/tests/data/
uv run --project pc --group dev --with pycolmap pytest pc      # + relecture du modèle par COLMAP (pycolmap)
MOTE_TEST_NERFSTUDIO=1 uv run --project pc --group dev pytest pc/tests/test_nerfstudio_load.py
```

Le dernier test charge l'export avec le parseur de nerfstudio 1.1.5, dans un environnement à part.
nerfstudio 1.1.5 exige protobuf ≤ 3.20.3, et le code généré de `mote.v1` exige ≥ 7.35.1 : ils ne peuvent pas partager
un environnement (TASK-239e).

Le MCAP d'exemple se régénère avec `uv run --project pc python pc/tests/make_sample.py`. Il est versionné, et ce sont
ces octets que les tests lisent.
