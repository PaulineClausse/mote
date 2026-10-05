---
id: ADR-59559af1a8bb
type: adr
slug: mcap-comme-format-de-fichier-de-session
title: MCAP comme format de fichier de session
created: 2026-10-05T08:20:36Z
author: seanl@sean-laptop
status: proposed
scope:
  - core/mote-mcap/**
  - pc/mote/ingest/**
constraint: |
  Les sessions sont stockées en MCAP (canaux typés protobuf, chunks zstd, index), sur le casque comme sur le PC. Le flux réseau n'est pas du MCAP.
schema: 4
version: 1
---

- **Contexte** : plusieurs flux horodatés hétérogènes à enregistrer et à rejouer.
- **Décision** : MCAP pour les fichiers de session, sur le casque et sur le PC, avec canaux typés par schémas protobuf, compression zstd par chunks, index. Le flux réseau n'est pas du MCAP : il transporte les mêmes messages protobuf dans une enveloppe (ADR-006). `[DECISION]` Propriétés du format `[CONNU]` (conteneur ouvert issu de la robotique, bibliothèques Rust, C++, Python, Go, visualisation avec Foxglove) ; fonctionnement de la crate Rust sur Android arm64 `[A VERIFIER]`.
- **Alternatives** : dossier de fichiers + CSV/JSON (format de SRC-1 et SRC-2, peu indexé), rosbag2 (dépend de l'écosystème ROS), format maison (pas d'outillage).
- **Remise en cause si** : la crate MCAP pose problème sur Android (SP-4) ; plan B : journal maison minimal chunké sur le casque, converti en MCAP par l'ingest.
