---
id: TASK-fe5c9db9677c
type: task
slug: wp-18-entra-nement-final-tests-de-charge-et-de-t
title: "WP-18 : entraînement final, tests de charge et de tenue thermique"
created: 2026-10-05T08:20:51Z
author: seanl@sean-laptop
status: open
scope:
  - pc/mote/train/**
  - docs/**
blocked_by: [TASK-723928dd249b, TASK-d955a00873d6, TASK-034afe61a3e4]
done_criteria: |
  mote train --final refuse de démarrer sur une session incomplète puis entraîne sur toutes les keyframes ; un rapport versionné sous docs/ donne le résultat de SC-02, SC-03 et SC-04 sur au moins deux scènes, la charge CPU du casque comparée au budget NFR-05, et le constat d'une session de 3 minutes sans alerte thermique ni baisse de fréquence d'affichage (NFR-06).
criteria_by: creator
schema: 4
version: 1
---

Jalon M5. Demande le casque.
