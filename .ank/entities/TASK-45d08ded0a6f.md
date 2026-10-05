---
id: TASK-45d08ded0a6f
type: task
slug: sp-0a-protocole-et-scripts-de-sp-0
title: "SP-0a : protocole et scripts de SP-0"
created: 2026-10-05T09:18:41Z
author: seanl@sean-laptop
status: in_progress
scope:
  - docs/spikes/sp0/**
blocked_by: []
done_criteria: |
  docs/spikes/sp0/ contient : un protocole de capture et d'export (SRC-1 non modifié, SRC-3) exécutable pas à pas ; la liste des versions d'outils requises (Unity, nerfstudio, COLMAP, Python, CUDA) ; un script d'alignement Sim(3) qui sort l'erreur de translation et de rotation entre deux jeux de poses, avec un test sur des poses synthétiques où l'erreur connue est retrouvée ; un script qui calcule PSNR, SSIM et LPIPS sur des vues tenues à l'écart ; les commandes d'entraînement splatfacto et de SfM COLMAP chronométré ; une trame de docs/spikes/SP-0.md couvrant chaque élément du done_criteria de SP-0.
criteria_by: creator
schema: 4
version: 2
---

Préparation de SP-0 (SPEC.md 14.1, hypothèse H-01), pour que la session casque ne serve qu'à capturer. Rien ici n'exige le casque. Aucun code mote : ce sont des outils de spike jetables, hors de core/, hosts/ et pc/.

Contenu attendu : le protocole de capture avec SRC-1 non modifié (scène, trajectoire, durée, éclairage, conseils SRC-2 repris de SPEC) ; la chaîne d'export avec SRC-3 vers le format attendu par nerfstudio et par COLMAP ; l'entraînement splatfacto option A sur les poses du casque ; le SfM COLMAP complet chronométré ; l'alignement Sim(3) des poses du casque sur celles du SfM, avec les erreurs de translation et de rotation ; le calcul PSNR, SSIM et LPIPS sur des vues tenues à l'écart ; la trame de docs/spikes/SP-0.md, dont les cases restent à remplir avec les mesures.
