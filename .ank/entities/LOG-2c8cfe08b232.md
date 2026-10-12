---
id: LOG-2c8cfe08b232
type: log
title: "Bench GPU fait (RTX 3070, nerfstudio 1.1.5). Premier passage faussé : ns-render dataset rend des"
created: 2026-10-12T08:54:04Z
author: claude-agent@mote-session
scope:
  - docs/spikes/**
about: TASK-e4477480ec8d
seq: 20
schema: 4
version: 1
---

 vues sans rapport avec le hold-out (~9 dB) ; métriques refaites sur les rendus de ns-eval (0db6691). S1 : A 25,40 ± 0,14 dB, A sur poses REF 26,81 ± 0,08 dB, écart -1,40 dB -> poursuite conditionnelle selon §2 ; S0 -0,28 dB. 20 dB à l'itération 2000 (~42 s). Décision validée par l'équipe : live sur poses du casque, recalage réservé à la passe finale. Réserves : poses de test non raffinées ; AREF porte aussi les intrinsèques et la distorsion du REF.
