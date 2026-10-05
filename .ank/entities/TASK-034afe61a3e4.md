---
id: TASK-034afe61a3e4
type: task
slug: wp-17-initialisations-c-d-e-et-r-f-rence-ref
title: "WP-17 : initialisations C, D, E et référence REF"
created: 2026-10-05T08:20:50Z
author: seanl@sean-laptop
status: open
scope:
  - pc/mote/train/**
  - pc/mote/tools/**
  - docs/**
blocked_by: [TASK-43f1a73ccaee, TASK-80c22942d8eb]
done_criteria: |
  mote train --init C, --init D et --init E s'exécutent sur la session de référence et produisent chacune un splat ; une commande exécute le SfM complet REF et rapporte l'erreur de tracking (translation, rotation, dérive) et son temps ; mote eval produit un tableau de résultats par option A à E, versionné sous docs/.
criteria_by: creator
schema: 4
version: 1
---

Jalon M5. Vérifier les licences des poids avant d'intégrer un modèle feed-forward (option D).
