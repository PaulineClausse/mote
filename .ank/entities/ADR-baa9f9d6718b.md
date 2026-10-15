---
id: ADR-baa9f9d6718b
type: adr
slug: aper-u-live-initialis-par-la-profondeur-du-casqu
title: Aperçu live initialisé par la profondeur du casque (option B)
created: 2026-10-15T06:51:19Z
author: claude-agent@mote-session
status: proposed
scope:
  - pc/mote/train/**
constraint: |
  L'entraînement live sème ses gaussiennes à partir des cartes de profondeur du casque rétroprojetées, au fil de leur arrivée, et ne recourt au semis aléatoire qu'en l'absence de profondeur.
schema: 4
version: 1
---

Contexte : SP-7 (docs/spikes/SP-7.md, 2026-10-14), sur S1 rejouée en flux, `uniform` en demi-résolution, 3 graines.
Avec la profondeur du casque rétroprojetée (option B de SPEC 11.3) au lieu du semis aléatoire (option A) :
PSNR moyen du flux 26,58 contre 23,42 dB (+3,17), PSNR final 27,76 contre 23,61 dB (+4,15). La règle de SP-7 donne
« neutre », sur le seul critère de fin de flux, dont la baisse vient de la remise des opacités de gsplat tombée juste
avant la mesure (analyse par graine en §4.2). Le coût réel est au démarrage : environ 1,9 dB de moins à 10 et 15 s,
20 dB atteints à 20 s au lieu de 11,7 s.

Décision : l'aperçu live part de la profondeur. Le but est d'aller vite puis d'avoir une bonne qualité : quelques
secondes de retard au démarrage valent 3 à 5 dB d'aperçu pendant tout le reste du scan.

Conséquences :
- WP-15 sème les gaussiennes depuis les cartes de profondeur au fil de leur arrivée (le banc de SP-6 avec
  `--init-npz` en donne le modèle) ; le semis aléatoire reste le repli quand aucune profondeur n'est arrivée.
- WP-10 et WP-14 portent déjà la profondeur jusqu'à l'ingest et dans la file live (DepthFrame) ; son débit, environ
  33 Mbit/s avant zstd (SP-3), est à tenir dans NFR-03 avec les images.
- À traiter dans WP-15 : filtrer les reflets dans les vitres, visibles dans le nuage de SP-7 (§4.1) ; réduire le
  creux du démarrage ; rendre la mesure de fin de flux robuste à la remise des opacités.
- Une variante non mesurée, semer d'abord en aléatoire puis ajouter la profondeur, peut remplacer cette décision si
  WP-15 montre qu'elle fait mieux : elle passera par une nouvelle ADR.
