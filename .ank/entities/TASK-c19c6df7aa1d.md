---
id: TASK-c19c6df7aa1d
type: task
slug: sp-0-script-en-une-commande-pour-le-ref-colmap-s
title: "SP-0 : script en une commande pour le REF COLMAP sur le PC NVIDIA"
created: 2026-10-08T12:43:56Z
author: claude-agent@mote-session
status: done
scope:
  - docs/spikes/sp0/gpu/**
blocked_by: []
done_criteria: |
  docs/spikes/sp0/gpu/ contient un script PowerShell qui, en une commande sur un PC Windows avec GPU NVIDIA, installe ce qui manque (COLMAP CUDA, SRC-3, Python), exporte chaque session brute du casque avec les poses du casque, calcule le SfM COLMAP complet chronométré sur GPU, choisit le modèle qui recale le plus d'images, aligne en Sim(3) les poses du casque sur ce modèle (deux yeux, gauche, droite, en mètres) et écrit un résumé par session ; un README documente cette commande ; un mode --DryRun et un test du post-traitement tournent sans GPU.
criteria_by: creator
proof:
  - type: commit
    ref: 0d4e981
    criteria: 4d55bc849378
    via: submitted
schema: 4
version: 3
---

Préparation de l'annexe REF de GPU_RUN.md pour la tour NVIDIA : rien à toucher entre la copie des sessions et la lecture des résultats. Outils de spike jetables, pas du code mote.
