---
id: SPEC-9df25a840ea4
type: spec
slug: protocole-de-transport-rattrapage-et-s-curit-du
title: Protocole de transport, rattrapage et sécurité du flux
created: 2026-10-05T08:20:42Z
author: seanl@sean-laptop
status: accepted
scope:
  - core/mote-net/**
  - pc/mote/ingest/**
references: [ADR-c36f30450585, ADR-d5f319e603c8]
ratified: 05a6f41ae541
verified:
  - by: seanl@sean-laptop
    at: 2026-10-05T08:24:58Z
schema: 4
version: 2
---

Détaille ADR-006 (transport) et ADR-012 (source de vérité). Les messages cités sont définis dans la spec du modèle de données.

### Connexion

- Le casque ouvre une connexion TCP vers `server_addr`. Chaque trame est un entier de taille suivi d'un message protobuf : `Envelope` du casque vers le PC, `Control` du PC vers le casque. Une trame de plus de 64 Mo est une erreur de protocole et ferme la connexion.
- La première trame est `Hello` (identifiant de session, jeton, version de schéma). Le serveur ferme la connexion si le jeton ne correspond pas au sien ou si la version de schéma n'est pas prise en charge.
- En cas de coupure, le casque retente la connexion et renvoie `Hello` avec le même identifiant de session. Le scan continue pendant la coupure.

### Numérotation

- Chaque canal numérote ses messages par un `seq` contigu à partir de 0, attribué à l'écriture dans le MCAP local. `Envelope.seq` et le champ `sequence` du MCAP portent la même valeur.
- Un message n'est émis sur le réseau qu'après avoir été remis à l'écriture locale.

### Flux live

- La file d'émission est bornée. Quand elle est pleine, les `ImageFrame` et `DepthFrame` les plus anciens en sont retirés ; chaque retrait produit un événement `LIVE_DROPPED`. Les messages retirés restent dans le fichier local.
- `SessionInfo`, `CameraIntrinsics`, `PoseSample`, `Event`, `Stats` et `SessionEnd` ne sont jamais retirés.

### Rattrapage

- L'ingest suit les `seq` reçus par canal. Pour chaque trou, il envoie `ResendRequest` (canal, premier et dernier `seq`).
- Le casque sert ces demandes depuis son fichier local, en priorité inférieure au flux live pendant le scan, puis sans limite après l'arrêt.
- `SessionEnd` annonce le dernier `seq` de chaque canal. La session PC est complète quand tous les `seq` annoncés sont présents ; elle contient alors les mêmes messages que celle du casque (mêmes canaux, `seq` et contenus), dans un ordre de fichier qui peut différer.
- L'entraînement live utilise ce qui est arrivé ; l'entraînement final attend la session complète.

### Sécurité

- v1 : réseau local de confiance, jeton partagé configuré des deux côtés, flux non chiffré. L'adresse du serveur est saisie dans la configuration du casque ; pas de découverte automatique.
- Le chiffrement TLS est requis avant tout usage sur un réseau non maîtrisé.
- Flux et fichiers contiennent des images d'intérieurs : données privées, soumises à une politique de conservation sur le casque comme sur le PC.
