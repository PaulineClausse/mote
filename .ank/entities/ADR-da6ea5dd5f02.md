---
id: ADR-da6ea5dd5f02
type: adr
slug: python-et-pytorch-pour-l-entra-nement
title: Python et PyTorch pour l'entraînement
created: 2026-10-05T08:20:38Z
author: seanl@sean-laptop
status: accepted
scope:
  - pc/mote/train/**
constraint: |
  L'entraînement s'appuie sur nerfstudio splatfacto (hors ligne) et gsplat (boucle incrémentale). Pas de dépendance au code 3DGS d'origine Inria.
ratified: 132644f93543
verified:
  - by: seanl@sean-laptop
    at: 2026-10-05T08:24:51Z
schema: 4
version: 2
---

- **Contexte** : les bibliothèques d'entraînement 3DGS (gsplat, nerfstudio) sont en PyTorch et CUDA. `[CONNU]`
- **Décision** : baseline et entraînements hors ligne avec nerfstudio `splatfacto` et son camera optimizer ; boucle d'entraînement incrémental personnalisée sur gsplat pour le live. `[HYPOTHESE]`
- **Alternatives** : implémentation native du 3DGS, hors de portée raisonnable en v1.
- **Remise en cause si** : l'incrémental n'atteint pas NFR-04 avec ces bibliothèques.
