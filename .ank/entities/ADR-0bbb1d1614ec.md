---
id: ADR-0bbb1d1614ec
type: adr
slug: aper-u-live-sur-les-poses-du-casque-recalage-des
title: Aperçu live sur les poses du casque, recalage des poses réservé à la passe finale
created: 2026-10-12T08:54:42Z
author: claude-agent@mote-session
status: proposed
scope:
  - pc/mote/train/**
constraint: |
  L'entraînement live n'attend ni SfM ni recalage global des poses : il s'entraîne sur les poses du casque, avec au plus un raffinement de pose par gradient pendant l'entraînement ; tout recalage des poses (options C, D, REF) n'a lieu que dans l'entraînement final.
schema: 4
version: 1
---

Contexte : SP-0 (docs/spikes/SP-0.md, 2026-10-12). Sur S1, les poses du casque sont au centimètre et sans dérive.
Le splat sur poses du casque atteint 25,40 dB contre 26,81 dB sur poses COLMAP (-1,40 dB, poursuite conditionnelle
selon la règle de SP-0 §2). L'aperçu atteint 20 dB au plus tard en ~42 s sur une RTX 3070, alors que le seul SfM
de référence prend 138 min.

Décision : le mode live (NFR-04, SC-01) vise la vitesse et prend les poses du casque telles quelles ; la perte de
~1,4 dB n'y compte pas. La qualité (SC-02) est l'affaire de l'entraînement final, après capture, qui recale les poses.

Conséquences : WP-15 n'intègre aucun SfM dans la boucle live ; WP-17 (options C et D) devient prioritaire pour la
passe finale ; le risque principal du live est l'entraînement incrémental, dérisqué par SP-6 et SP-7.
