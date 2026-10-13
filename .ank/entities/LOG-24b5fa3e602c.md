---
id: LOG-24b5fa3e602c
type: log
title: "Premier passage SP-4 (casque, 6 min) : encodage pur 11,9 ms/image 1280² q90 (23,7 ms/paire sur un"
created: 2026-10-13T14:21:09Z
author: claude-agent@mote-session
scope:
  - docs/spikes/**
about: TASK-2b1911018f4b
seq: 3
schema: 4
version: 1
---

 cœur) ; Baseline 71,9 images/s (0,09 % ratées) ; GetColors sur le thread principal 15,5 ms/paire -> 61,9 images/s, 16,9 % ratées, dès la phase GetColors ; thermique 0. Mais 0 paire poussée au core en phase Nominal : la sonde écartait les paires (taille du tableau GetColors différente de CurrentResolution, probablement), sans le journaliser ; le verdict automatique « avec réserve » n'est pas valable pour le core. MCAP écrit sur le casque (info + end seulement) relu sur PC : la crate MCAP fonctionne sur Android. Corrections : taille prise sur la texture, écarts journalisés, phase de relecture asynchrone ajoutée (remède prévu par la règle), analyse qui refuse de conclure sans paire poussée.
