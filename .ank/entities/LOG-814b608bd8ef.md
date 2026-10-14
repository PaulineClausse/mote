---
id: LOG-814b608bd8ef
type: log
title: "Second passage SP-4 (2026-10-14, 8 min) : GetColors 15,85 ms p50/paire, affichage 72->62 dès"
created: 2026-10-14T06:55:53Z
author: claude-agent@mote-session
scope:
  - docs/spikes/**
about: TASK-2b1911018f4b
seq: 5
schema: 4
version: 1
---

 GetColors ; Async tient tous les critères (72 Hz, 0,16 % ratées, 0 perte, core 30,5 % d'un cœur, encodage 15,3 ms/image) ; MCAP Nominal et Async relus conformes. Anomalie : GetColors rend 4x les pixels, la sonde a poussé 1280x5120 en Nominal ; budget NFR-05 calculé sur Async (40 % d'un cœur, 10 ms), pas sur les 105 %/34,5 ms d'analyze_sp4.py. H-05 validée avec réserve, ADR-004 confirmé.
