---
id: LOG-cd6a99ed8a09
type: log
title: "Mesure : test live, stop à 14,0 s, session PC complète 1,0 s après stop, mais mote_destroy 120,0 s"
created: 2026-10-16T10:31:53Z
author: claude-agent@mote-session
scope:
  - core/mote-net/**
  - pc/mote/ingest/**
about: TASK-f3264225d2f8
seq: 2
schema: 4
version: 1
---

 ; thread lecteur des Control joint en 120,0 s. Hypothèse 1 (into_inner en échec saute le shutdown) réfutée : avec un shutdown inconditionnel par un double de la socket, toujours 120 s. Hypothèse 2 : sous Windows, shutdown sur un handle dupliqué ne débloque pas un recv en cours ; correction : lecture avec délai de 200 ms et accumulation des octets.
