---
id: LOG-966db98abc53
type: log
title: "released: Bloqué par TASK-af1e : l'ingest écrit les RAW_RGBA en RGBA 4 canaux, nerfstudio ne peut"
created: 2026-10-16T08:59:01Z
author: claude-agent@mote-session
scope:
  - pc/**
  - proto/**
about: TASK-239e7d8657ac
seq: 1
schema: 4
version: 1
---

 pas entraîner la session d'exemple. Constaté : l'environnement séparé (uv, nerfstudio 1.1.5, protobuf 3.20.3, torch 2.14 CPU) s'installe en ~1 min et ns-train nerfacto démarre sur CPU sous Windows avec PYTHONUTF8=1 ; l'échec vient du chargement des images.
