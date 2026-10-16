---
id: LOG-b0e2a0e0461f
type: log
title: "Plan et lectures. Trame : taille u32 big-endian (ordre réseau) puis Envelope ou Control ; > 64 Mo ="
created: 2026-10-16T10:10:37Z
author: claude-agent@mote-session
scope:
  - core/mote-net/**
  - pc/mote/ingest/**
about: TASK-f3264225d2f8
seq: 1
schema: 4
version: 1
---

 erreur de protocole (constante de protocole, SPEC-9df2). Hello = première Envelope (channel vide, seq 0, body hello). Contenu comparé = octets du message protobuf du canal (les mêmes que la donnée MCAP). File live bornée en octets ; si une entrée ne tient pas, les ImageFrame/DepthFrame les plus anciens sont retirés (LIVE_DROPPED chacun) ; les autres canaux ne sont jamais retirés, quitte à dépasser la borne. Rattrapage v1 : relecture séquentielle du MCAP local par lots (pas d'index), demandes non encore sur disque réessayées au lot suivant. Le client réseau vit de start à destroy : après stop, il continue à servir les demandes. Réglables (casque, champs ajoutés en fin de mote_config, 0 = défaut) : live_queue_bytes, reconnect_min_ms, reconnect_max_ms, connect_timeout_ms, resend_batch_ms ; (PC, options de mote ingest) : délai de relance des demandes, délai d'inactivité. Défauts tirés de SP-5, documentés. Clause 4 (débit nominal mesuré sur casque) : demande le casque et une vraie session, à faire avec l'utilisateur.
