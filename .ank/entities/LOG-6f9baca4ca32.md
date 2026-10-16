---
id: LOG-6f9baca4ca32
type: log
title: "Clauses : (1) mote.h expose toutes les fonctions et structures de SPEC-fdb8, vérifié par un test C"
created: 2026-10-16T06:40:21Z
author: claude-agent@mote-session
scope:
  - core/mote-capi/**
  - core/mote-core/**
about: TASK-85d8e3ebe692
seq: 1
schema: 4
version: 1
---

 qui touche chaque champ ; (2) create→start→set_intrinsics→push_pair→push_hmd_pose→push_depth→push_event→stop→destroy tous MOTE_OK ; (3) push avant start = MOTE_ERR_STATE ; (4) file d'encodage pleine = MOTE_ERR_BUSY + pairs_dropped+1 ; (5) create sans local_dir = MOTE_ERR_INVALID_ARG. Choix non tranchés par la spec : file d'encodage de 4 paires (~52 Mo en RGBA 1280x1280) ; les étages encodeur/écrivain sont des traits branchés par WP-04/05, injectables en test pour bloquer l'encodeur et remplir la file de façon déterministe ; les enums anonymes (MOTE_CODEC_*, MOTE_FLAG_*) deviennent des #define via cbindgen.
