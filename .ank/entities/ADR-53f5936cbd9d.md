---
id: ADR-53f5936cbd9d
type: adr
slug: s-lection-des-paires-bord-avant-encodage
title: Sélection des paires à bord, avant encodage
created: 2026-10-05T08:20:38Z
author: seanl@sean-laptop
status: accepted
scope:
  - core/mote-core/**
constraint: |
  La sélection des keyframes se fait dans le core avant encodage, par seuils de mouvement et de netteté, de façon atomique par paire gauche/droite. Un mode tout enregistrer reste disponible.
ratified: 17d1915d5964
verified:
  - by: seanl@sean-laptop
    at: 2026-10-05T08:24:53Z
schema: 4
version: 2
---

- **Contexte** : encoder et transmettre toutes les paires coûte du CPU et du débit pour peu de gain.
- **Décision** : une paire est retenue si le déplacement ou la rotation depuis la dernière paire retenue dépasse un seuil, et si le score de netteté des deux images dépasse un seuil (variance du Laplacien sur luminance sous-échantillonnée). Décision atomique par paire, seuils configurables. Le mouvement est évalué avec la pose par frame de l'image gauche. `[DECISION]`
- **Alternatives** : tout envoyer et trier côté PC (débit trop élevé).
- **Conséquences** : les paires rejetées sont définitivement perdues. Un mode « tout enregistrer » (toutes les paires, encodées en JPEG) reste disponible pour les sessions de référence.
- **Remise en cause si** : les rejets à bord privent mesurablement l'entraînement de vues utiles (comparaison avec une session « tout enregistrer »).
