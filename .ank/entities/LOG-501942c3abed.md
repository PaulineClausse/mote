---
id: LOG-501942c3abed
type: log
title: "Fait : paquet pc/ (pyproject, uv), mote ingest --replay et mote export. Images : JPEG d'origine"
created: 2026-10-13T09:04:39Z
author: claude-agent@mote-session
scope:
  - pc/**
about: TASK-643e138c394f
seq: 1
schema: 4
version: 1
---

 octet pour octet (décodé pour vérification, pas de réencodage), RAW_RGBA en PNG. Poses canoniques par la formule de SPEC-64c5 §9.4 (= SRC-3), identifiant unity-flipz/v0, validation laissée à WP-08 ; interpolation sur /pose/hmd composée avec hmd_from_camera ; plus long segment entre RECENTER gardé ; intrinsèques ramenées à la taille de l'image. Tests sur pc/tests/data/sample_session.mcap (49 Ko) : 16 + pycolmap relit le modèle COLMAP + nerfstudio 1.1.5 charge transforms.json (processus à part). Découvert : nerfstudio 1.1.5 exige protobuf <= 3.20.3, mote_pb2 >= 7.35.1 -> TASK-239e.
