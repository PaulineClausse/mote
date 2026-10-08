---
id: LOG-64abd8cc3def
type: log
title: "S1 capturée (20261007_120820) : 122 s, 4,8 fps (config 5 fps prise en compte), 589 paires, étendue"
created: 2026-10-07T10:27:21Z
author: claude-agent@mote-session
scope:
  - docs/spikes/**
about: TASK-e4477480ec8d
seq: 14
schema: 4
version: 1
---

 2,0 x 2,9 m, retour au départ 27 cm, arrêt propre. Bureau plutôt vide (murs blancs, fenêtres), une personne visible : plus proche de la scène 2 du protocole. discrepancy: make_holdout.py apparie gauche/droite par nom, or 174 paires sur 589 ont des horodatages gauche/droite décalés (en général 1 µs, au plus 27,8 ms) : 763 « paires » au lieu de 589. Ajout d'une option --pairs (mruk_stereo_pairs.csv), comportement par défaut inchangé : 589 paires, 75 tenues à part, 1028 train / 150 test. GPU_RUN.md écrit pour l'entraînement sur le PC NVIDIA de l'école ; kit sp0_s1 (1,9 Go) préparé hors dépôt. REF S1 en cours (extraction 401 s).
