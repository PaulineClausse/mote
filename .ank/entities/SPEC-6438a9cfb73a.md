---
id: SPEC-6438a9cfb73a
type: spec
slug: protocole-d-valuation-et-m-triques
title: Protocole d'évaluation et métriques
created: 2026-10-05T08:20:41Z
author: seanl@sean-laptop
status: accepted
scope:
  - pc/mote/eval/**
  - pc/mote/train/**
ratified: 6e7bef57a843
verified:
  - by: seanl@sean-laptop
    at: 2026-10-05T08:24:57Z
schema: 4
version: 2
---

### 13.1 Protocole de comparaison

1. Enregistrer une ou plusieurs sessions de référence (MCAP), rejouées pour toutes les options.
2. Mêmes hyperparamètres et même nombre d'itérations pour toutes les options, sauf pour l'init.
3. **Hold-out par blocs** : 10 à 15 % des paires, tenues à part par blocs temporels contigus (par exemple 5 paires consécutives toutes les 40), gauche et droite ensemble. Des vues isolées entourées de voisines d'entraînement quasi identiques gonfleraient les métriques.
4. Les paires du hold-out sont exclues de l'entraînement **et** de toutes les initialisations (B à E).
5. **Poses de test** : les poses d'entraînement étant raffinées, les poses du hold-out le sont aussi avant mesure, Gaussiennes gelées, avec un budget d'itérations identique pour toutes les options. Les métriques sans cette étape sont rapportées à côté.
6. Au moins deux scènes de nature différente (petite pièce encombrée, grand espace plus vide).
7. Au moins trois graines d'entraînement par configuration ; les écarts entre options ne sont interprétés que s'ils dépassent la dispersion entre graines (NFR-07).

### 13.2 Métriques

- Qualité : PSNR, SSIM, LPIPS sur le hold-out.
- Temps : prétraitement, délai jusqu'au premier aperçu conforme à SC-01, temps d'entraînement final.
- Géométrie (par rapport à REF) : erreur de pose après alignement Sim(3), nombre de points d'init utiles.
- Système : débit réseau, charge CPU du casque, paires perdues, latence bout en bout (NFR).

### 13.3 Référence REF et erreur de tracking

REF est un SfM complet (COLMAP `mapper`, sans poses imposées) exécuté sur les keyframes d'une session. Il fournit :
- l'erreur du tracking du casque : poses du casque comparées aux poses REF après alignement Sim(3), en translation, en rotation, et en dérive sur la durée ;
- le temps de référence de l'ancien pipeline pour SC-03.
