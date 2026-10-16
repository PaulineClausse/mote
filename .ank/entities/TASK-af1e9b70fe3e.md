---
id: TASK-af1e9b70fe3e
type: task
slug: ingest-images-raw-rgba-crites-en-rgb-comme-les-j
title: "Ingest : images RAW_RGBA écrites en RGB, comme les JPEG"
created: 2026-10-16T08:58:55Z
author: claude-agent@mote-session
status: done
scope:
  - pc/mote/ingest/**
  - pc/tests/**
blocked_by: []
done_criteria: |
  Un test de régression ingère une session contenant des images JPEG et RAW_RGBA et vérifie que toutes les images du dataset sont en RGB à 3 canaux, aux dimensions de la source, les pixels RAW_RGBA restitués sans perte ; le dataparser nerfstudio charge et empile ces images sans erreur.
criteria_by: creator
method: diagnose
proof:
  - type: commit
    ref: "6482485"
    criteria: 36ae8eeac965
    via: submitted
schema: 4
version: 3
---

Constaté pendant TASK-239e (2026-10-16) : `ns-train nerfacto` sur la session d'exemple (pc/tests/data/sample_session.mcap) échoue au chargement, `torch.stack` refusant `[48, 64, 3]` contre `[48, 64, 4]`. L'ingest (pc/mote/ingest/replay.py) écrit les images RAW_RGBA en PNG RGBA à 4 canaux, et les JPEG restent à 3 canaux.

Depuis WP-04, le casque produit du RAW_RGBA pour les sessions de référence (ADR-86d6) : le cas arrive en vrai. L'alpha des caméras ne porte rien (toujours 255) ; écrire le PNG en RGB garde l'image sans perte.

Le test test_nerfstudio_load.py (WP-07) ne le voyait pas : il vérifie le dataparser (chemins, poses, intrinsèques), pas le chargement des pixels.
