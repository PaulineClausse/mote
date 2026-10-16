---
id: LOG-41383faf0d7b
type: log
title: "Écarts connus après l'élargissement du périmètre : ADR-86d6 (JPEG à bord) n'est pas tenu tant que"
created: 2026-10-16T07:36:32Z
author: claude-agent@mote-session
scope:
  - core/mote-mcap/**
  - core/mote-core/**
  - core/mote-capi/**
about: TASK-31590ab8146d
seq: 4
schema: 4
version: 1
---

 WP-04 (TASK-ec26) n'a pas branché l'encodeur : les images sont écrites en RAW_RGBA, codec déclaré tel quel dans ImageFrame. ADR-53f5 (sélection avant encodage) attend WP-09 (TASK-7454) : toute paire synchronisée est retenue. Rien de nouveau introduit par WP-05, mais c'est désormais sur disque.
