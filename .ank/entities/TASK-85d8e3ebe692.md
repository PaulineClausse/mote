---
id: TASK-85d8e3ebe692
type: task
slug: wp-03-api-c-et-squelette-du-core
title: "WP-03 : API C et squelette du core"
created: 2026-10-05T08:20:45Z
author: seanl@sean-laptop
status: open
scope:
  - core/mote-capi/**
  - core/mote-core/**
blocked_by: [TASK-db5daba59eec, TASK-85b569bb73e6]
done_criteria: |
  mote.h expose toutes les fonctions et structures de la spec API C ; un test exécuté sur PC enchaîne create, start, set_intrinsics, push_pair, push_hmd_pose, push_depth, push_event, stop, destroy sans erreur ; un push avant start renvoie MOTE_ERR_STATE ; une file d'encodage pleine renvoie MOTE_ERR_BUSY et incrémente pairs_dropped ; create sans local_dir renvoie MOTE_ERR_INVALID_ARG.
criteria_by: creator
schema: 4
version: 1
---

Jalon M1. Cycle de vie, files bornées, threads ; les modules codec, MCAP et réseau sont branchés par WP-04, WP-05 et WP-14.
