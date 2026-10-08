---
id: LOG-8df6b0279b0e
type: log
title: "Vérifié sans GPU : env d'entraînement Windows sans compilation (gsplat pt21cu118), ns-train exact A"
created: 2026-10-08T13:14:53Z
author: claude-agent@mote-session
scope:
  - docs/spikes/sp0/gpu/**
about: TASK-734f1f6cab3f
seq: 1
schema: 4
version: 1
---

 et AREF jusqu'à la 1re itération (listes lues), options ns-render/ns-eval, tag tensorboard, test_train 5/5, train_all.ps1 -DryRun sous PS 5.1. Bug trouvé et corrigé : en-têtes images.txt en cp1252 illisibles par nerfstudio. Non vérifié : entraînement réel sur GPU.
