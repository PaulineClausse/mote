---
id: ADR-86d665f9dac4
type: adr
slug: pas-de-stockage-brut-jpeg-logiciel-bord
title: Pas de stockage brut ; JPEG logiciel à bord
created: 2026-10-05T08:20:36Z
author: seanl@sean-laptop
status: accepted
scope:
  - core/mote-codec/**
  - core/mote-core/**
constraint: |
  Les images retenues sont encodées en JPEG logiciel (libjpeg-turbo) dans le core. RAW_RGBA est réservé aux sessions de référence en enregistrement local. Pas d'encodage vidéo matériel en v1.
ratified: 89094a2fb579
verified:
  - by: seanl@sean-laptop
    at: 2026-10-05T08:24:49Z
schema: 4
version: 2
---

- **Contexte** : le brut RGBA dépasse 1 Gbit/s en configuration nominale (6.2). Les exports de SRC-2 prennent plusieurs minutes. `[SOURCE]`
- **Décision** : sélection des paires, puis encodage JPEG de qualité élevée par libjpeg-turbo (NEON) sur des threads du core. `[DECISION]` Un codec `RAW_RGBA` existe pour de courtes sessions de référence, en enregistrement local uniquement (validation de H-03).
- **Alternatives** : HEVC all-intra par MediaCodec (gain de débit, mais contrôle de qualité dépendant du matériel et chemin zéro-copie incompatible avec la sélection avant encodage ; reporté, NG-08) ; vidéo inter-frame (artefacts d'inter-prédiction pénalisants pour le 3DGS) ; PNG (lent, volumineux).
- **Conséquences** : charge CPU à mesurer (H-05) ; à quelques paires par seconde, aucun chemin zéro-copie n'est nécessaire.
- **Remise en cause si** : H-03 est invalidée (repli sur q95) ou H-05 est invalidée (réduction de cadence, puis étude de l'encodage matériel).
