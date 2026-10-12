---
id: LOG-b0b4037d5da3
type: log
title: "Kit écrit dans docs/spikes/sp6/ (commit 385edee) : incremental.py (gsplat 1.4.0 direct, horloge ="
created: 2026-10-12T09:34:09Z
author: claude-agent@mote-session
scope:
  - docs/spikes/**
about: TASK-45ec0c122e98
seq: 1
schema: 4
version: 1
---

 temps d'entraînement hors évaluations, semis de 500 gaussiennes par vue arrivée à profondeur aléatoire 0,3-4 m, DefaultStrategy sans arrêt, raffinement de pose par vue), stratégies uniform/recent/window, hors ligne avec éval toutes les 200 it., demi-résolution. test_stream 4/4 ; test_loop OK sur CPU avec rendu gsplat simulé (torch 2.1.2 cpu, gsplat 1.4.0) : semis, densification (1400 -> 4004 gaussiennes), flux, résumé. Règle fixée dans SP-6.md §2 avant mesure. Reste : run_sp6.ps1 sur le PC NVIDIA, puis remplir SP-6.md.
