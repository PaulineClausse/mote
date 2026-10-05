---
id: TASK-db5daba59eec
type: task
slug: wp-01-sch-mas-protobuf-mote-v1
title: "WP-01 : schémas protobuf mote.v1"
created: 2026-10-05T08:20:44Z
author: seanl@sean-laptop
status: open
scope:
  - proto/**
blocked_by: [TASK-ab7642fc3e78, TASK-e4477480ec8d]
done_criteria: |
  proto/ contient le schéma mote.v1 avec tous les messages de la spec du modèle de données ; une commande documentée génère le code Rust (prost) et Python ; un test sérialise chaque type de message en Rust et le relit en Python avec des champs identiques.
criteria_by: creator
schema: 4
version: 1
---

Jalon M1. Intégrer les corrections issues de SP-1 avant de figer les champs.
