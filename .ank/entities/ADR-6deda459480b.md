---
id: ADR-6deda459480b
type: adr
slug: donn-es-stock-es-brutes-conversions-uniquement-l
title: Données stockées brutes, conversions uniquement à l'ingest
created: 2026-10-05T08:20:38Z
author: seanl@sean-laptop
status: accepted
scope:
  - core/**
  - hosts/**
  - proto/**
  - pc/mote/ingest/**
constraint: |
  Le casque stocke poses et profondeur telles que fournies par la source, avec leur convention déclarée. Conversions de repère et linéarisation de profondeur se font uniquement à l'ingest.
ratified: dccd27fd092b
verified:
  - by: seanl@sean-laptop
    at: 2026-10-05T08:24:52Z
schema: 4
version: 2
---

- **Contexte** : les conventions de repère (Unity main gauche, OpenXR, OpenGL, OpenCV) sont une source d'erreur fréquente ; les notes de migration de SRC-1 en témoignent. `[SOURCE]` Le même raisonnement vaut pour la profondeur non linéaire.
- **Décision** : le core stocke les poses et la profondeur telles que fournies par l'hôte, avec une énumération déclarant la convention d'origine. Conversions de repère et linéarisation se font à l'ingest, avec test de validation (9.4). `[DECISION]`
- **Alternatives** : convertir à bord (une erreur devient irréversible dans les données).
- **Remise en cause si** : jamais pour le principe ; seule la liste des conventions prises en charge évolue.
