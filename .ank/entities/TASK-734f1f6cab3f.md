---
id: TASK-734f1f6cab3f
type: task
slug: sp-0-bench-3dgs-en-une-commande-poses-du-casque
title: "SP-0 : bench 3DGS en une commande, poses du casque contre poses COLMAP"
created: 2026-10-08T13:01:59Z
author: claude-agent@mote-session
status: in_progress
scope:
  - docs/spikes/sp0/gpu/**
blocked_by: []
done_criteria: |
  docs/spikes/sp0/gpu/ contient un script PowerShell qui, en une commande sur le PC NVIDIA, installe l'environnement d'entraînement (nerfstudio, gsplat précompilé, LPIPS) sans compilation, prépare pour chaque session un jeu commun aux deux sources de poses (mêmes images, même hold-out par paires), entraîne splatfacto option A sur les poses du casque et sur les poses REF COLMAP avec plusieurs graines, rend le hold-out en PNG, calcule PSNR, SSIM et LPIPS VGG, relève le temps d'entraînement et le temps pour atteindre 20 dB, et écrit une comparaison par session ; le README documente la commande ; un test du post-traitement et un dry-run tournent sans GPU.
criteria_by: creator
schema: 4
version: 2
---

Suite de TASK-c19c : benchmark A (poses du casque) contre A sur poses REF (PROTOCOL.md §7-§8, GPU_RUN.md §3-§5), pour la règle de décision de SP-0.md §2 (écart de PSNR A - REF).
