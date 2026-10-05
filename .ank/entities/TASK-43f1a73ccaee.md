---
id: TASK-43f1a73ccaee
type: task
slug: wp-08-conversion-de-rep-res-et-validation
title: "WP-08 : conversion de repères et validation"
created: 2026-10-05T08:20:47Z
author: seanl@sean-laptop
status: open
scope:
  - pc/mote/ingest/**
  - pc/mote/tools/**
blocked_by: [TASK-552bc1025408, TASK-643e138c394f]
done_criteria: |
  Des tests unitaires couvrent la conversion Unity vers repère canonique puis vers OpenGL sur des cas connus et en aller-retour ; mote validate calcule l'erreur de reprojection d'une cible connue et sort en erreur au-delà du seuil fixé par SP-2 ; sur la session de référence de SP-2 l'erreur est sous ce seuil ; un test vérifie le découpage en segments aux événements RECENTER.
criteria_by: creator
schema: 4
version: 1
---

Jalon M2. Aucune formule de conversion n'est acceptée sans le test de reprojection.
