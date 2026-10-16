---
id: TASK-9f0f06e2dcf0
type: task
slug: constantes-du-core-r-glables-par-mote-config
title: Constantes du core réglables par mote_config
created: 2026-10-16T10:37:33Z
author: claude-agent@mote-session
status: open
scope:
  - core/mote-core/**
  - core/mote-capi/**
blocked_by: []
done_criteria: |
  La capacité de la file d'encodage, celle de la file d'écriture, la période de fermeture forcée des chunks et de /stats, et la largeur de mesure de la netteté se règlent par des champs ajoutés en fin de mote_config (0 = défaut actuel, documenté) ; un test par réglage montre qu'une valeur non par défaut change le comportement observable par l'API C ; un hôte compilé avec l'ancien struct_size obtient les défauts.
criteria_by: creator
schema: 4
version: 1
---

Consigne du projet (2026-10-16) : aucune valeur dépendant de l'environnement (matériel, réseau, conditions de capture) ne doit être figée ; nos mesures ne fixent que des défauts documentés, que d'autres chercheurs ajustent à leurs conditions.

Constantes concernées, livrées par WP-03, WP-05 et WP-09 : ENCODE_QUEUE_CAPACITY (4 paires, dimensionnée pour 1280x1280 RGBA), WRITE_QUEUE_CAPACITY (1024), FLUSH_PERIOD (1 s : borne la perte en cas de mort du processus et cadence /stats), SHARPNESS_WIDTH (320 px : échelle du score de netteté, donc de kf_min_sharpness). EVENT_QUEUE_CAPACITY (256) peut rester fixe : elle ne dépend que de la fréquence de polling de l'hôte, à documenter. Les réglages du transport sont faits par WP-14.
