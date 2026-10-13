---
id: LOG-c24c8c99d78f
type: log
title: "Correction : isValid n'est finalement pas stocké (l'hôte ne pousse que les cartes valides) ; seul"
created: 2026-10-13T07:50:27Z
author: claude-agent@mote-session
scope:
  - proto/**
  - pc/mote/v1/**
about: TASK-db5daba59eec
seq: 3
schema: 4
version: 1
---

 predictedDisplayTime est ajouté (DepthFrame champ 18). Test croisé vert : 22 messages (13 types + 9 variantes d'Envelope), réencodage identique ; vérifié qu'il échoue sur une valeur divergente et sur un champ oublié.
