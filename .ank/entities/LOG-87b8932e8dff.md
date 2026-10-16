---
id: LOG-87b8932e8dff
type: log
title: "Hypothèse confirmée : avec .convert('RGB') avant l'écriture du PNG, 14 images RGB (13 JPEG, 1 PNG),"
created: 2026-10-16T09:00:23Z
author: claude-agent@mote-session
scope:
  - pc/mote/ingest/**
  - pc/tests/**
about: TASK-af1e9b70fe3e
seq: 2
schema: 4
version: 1
---

 et le test nerfstudio (InputDataset puis torch.stack) passe ; sans, il échoue sur [48, 64, 3] contre [48, 64, 4]. Régression : test_all_images_are_rgb_like_the_jpegs et test_nerfstudio_load.py (MOTE_TEST_NERFSTUDIO=1), vus rouges avant le correctif. pc/ n'a pas de CI : preuve par exécution locale (17 passés, 2 sautés ; nerfstudio 1 passé).
