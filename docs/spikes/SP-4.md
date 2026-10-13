# SP-4 : le core tourne sur le casque

Statut : brouillon. Méthode et règle fixées avant les mesures · Date : 2026-10-13 · Auteur : claude-agent@mote-session
· Tâche : TASK-2b19

Contexte :
- **H-05** : la lecture CPU des images (`GetColors`, signalée coûteuse `[DOC]`) et l'encodage JPEG logiciel
  (libjpeg-turbo, NEON) tiennent dans le budget du casque, sans gêner le tracking.
- **ADR-5955** (ADR-004) : sessions en MCAP. Le fonctionnement de la crate Rust sur Android arm64 est `[A VERIFIER]`.
- **NFR-05** : un budget CPU pour le core reste à fixer.

Configuration nominale : deux caméras en 1280 x 1280, 10 paires/s, JPEG q90.

## 1. Verdict (à remplir en dernier)

- GetColors, une paire 1280 x 1280 : ___ ms (p50), ___ ms (p95).
- Encodage JPEG q90 d'une paire : ___ ms.
- Charge CPU à 10 paires/s : ___
- MCAP écrit sur le casque, lu sur PC : ___
- Budget NFR-05 : ___
- H-05 : ___
- ADR-004 : ___ (confirmé / plan B)
- Conséquences pour WP-02 à WP-06 : ___

## 2. Règle, écrite avant de regarder les chiffres

Phases (§3) : `Baseline` (caméras actives, rien lu), `GetColors` (lecture seule), `Nominal` (lecture + core), et `Async` (relecture GPU asynchrone + core, ajoutée après le premier passage, voir plus bas).

- **H-05 validée** si, en phase `Nominal` :
  - la fréquence d'affichage reste au moins à 98 % de celle de `Baseline` ;
  - la part d'images ratées (intervalle de plus de 1,5 fois la période d'affichage) ne dépasse pas celle de
    `Baseline` de plus de 0,5 point ;
  - les paires perdues par saturation du core restent sous 1 % (NFR-02) ;
  - tout ce qui est poussé est encodé ou compté perdu, sans erreur ;
  - le statut thermique Android reste sous 3 (sévère) pendant les 3 minutes.
- **Validée avec réserve** si seul l'affichage décroche, et s'il décroche déjà en phase `GetColors`, avant le core. La
  cause est alors la lecture CPU de l'hôte, à remplacer par une relecture GPU asynchrone, pas le core.
- **Invalidée** sinon.
- **ADR-004 confirmé** si le MCAP écrit sur le casque se relit sur PC avec le code Python de `mote.v1` : tous les
  messages décodés, séquences contiguës, `/session/end` cohérent, JPEG décodés à la bonne taille. Sinon, plan B de
  l'ADR (journal maison chunké, converti à l'ingest).
- **Budget NFR-05** :
  - pour les threads du core en configuration nominale, le CPU mesuré, majoré de 25 % et arrondi aux 5 % d'un cœur
    supérieurs ;
  - pour l'appel `mote_push_*` d'une paire sur le thread de l'hôte, le maximum mesuré, arrondi au demi-ms supérieur
    (1 ms au moins).

Date de fixation de la règle : 2026-10-13, avant toute mesure.

**Écart, après le premier passage (2026-10-13).** Ce passage a montré deux choses. D'abord, `GetColors` coûte 15,5 ms par paire sur le thread principal : l'affichage tombe de 71,9 à 62 images/s, avec 17 % de frames ratées, dès la phase `GetColors`. Ensuite, la sonde n'a poussé **aucune paire** au core : elle écartait les paires sur une taille de tableau qu'elle ne journalisait pas. Le core n'a donc pas été mesuré. Deux changements :
- la sonde prend la taille sur la texture et journalise ses écarts ;
- une phase `Async` est ajoutée (relecture GPU asynchrone, puis push au core). C'est le remède que la règle prévoit ; les mêmes critères lui sont appliqués.

La règle elle-même ne change pas : le verdict sur H-05 porte sur `Nominal`, et `Async` dit si le remède suffit. L'analyse refuse désormais de conclure quand le core n'a reçu aucune paire.

## 3. Méthode

Outils : `docs/spikes/sp4/` (README.md).

- **Le core** : `sp4core`, Rust, un `.so` arm64 de 1,7 Mo. Il dépend seulement de libc et libdl. Construit avec
  cargo-ndk, NDK r27c, API 32. libjpeg-turbo y est compilé depuis ses sources avec le SIMD NEON
  (`WITH_SIMD = 1`, intrinsèques NEON).
  - API C en push (ADR-7a16) : `sp4_open`, `sp4_push_pair` (copie de la paire puis mise en file), `sp4_stats_json`,
    `sp4_close`, `sp4_bench_encode`.
  - Deux threads encodent en JPEG q90 (4:2:0) et écrivent dans un MCAP :
    - canaux `/cam/left/frame` et `/cam/right/frame` en `mote.v1.ImageFrame`, plus `/session/info` et `/session/end` ;
    - schémas protobuf auto-décrits, chunks zstd ;
    - file de 8 paires ; une paire refusée quand la file est pleine est comptée perdue.
- **L'hôte** : QuestRealityCapture v1.5.0 (SRC-1), qui configure déjà les deux `PassthroughCameraAccess` de MRUK en
  1280 x 1280.
  - Une sonde (`Sp4Probe.cs`) y est injectée. Elle active les caméras, plafonnées à 10 images/s.
  - Elle enchaîne les phases seule : chauffe (20 s), encodage pur (40 images synthétiques), `Baseline` (60 s),
    `GetColors` (60 s, 10 paires/s), `Nominal` (180 s, 10 paires/s).
  - `GetColors` est chronométré sur le thread principal, pour les deux yeux ensemble.
  - L'APK a un identifiant à part : l'original n'est pas touché.
- **Mesures** :
  - fréquence d'affichage par `Time.unscaledDeltaTime`, comparée à `OVRPlugin.systemDisplayFrequency` ;
  - CPU de tout le processus par `CLOCK_PROCESS_CPUTIME_ID`, en pourcentage d'un cœur ;
  - CPU des threads du core par `CLOCK_THREAD_CPUTIME_ID` ;
  - statut thermique par `PowerManager.getCurrentThermalStatus`.
- **Lecture sur PC** : `verify_mcap.py` (crate `mcap` côté casque, paquet Python `mcap` côté PC, `mote_pb2` de
  WP-01).

Vérifications sans casque :
- tests du core sous Linux : aller-retour MCAP, file pleine, stride ;
- un MCAP écrit par le core et relu sous Windows par `verify_mcap.py` : 40 images, conforme ;
- tests de la règle (`test_analyze_sp4.py`).

## 4. Résultats

### 4.1 Encodage pur

___

### 4.2 Phases (affichage, CPU, GetColors, thermique)

___

### 4.3 Core en configuration nominale

___

### 4.4 MCAP relu sur PC

___

## 5. Lecture et limites

- `GetColors` est appelé sur le thread principal, comme le ferait un hôte naïf. MRUK recommande `AsyncGPUReadback`
  pour éviter ce coût ; si la réserve de §2 joue, c'est la piste.
- La sonde tourne dans QRC sans que QRC enregistre. Le coût d'un vrai hôte mote (pose du casque, profondeur, UI de
  couverture) n'y est pas.
- Le CPU du processus inclut Unity, le rendu et MRUK. Seul celui des threads du core est imputable au core.
- Pas de sélection de paires (WP-09) : 10 paires/s sont toutes encodées, c'est le pire cas.
- Les images sont stockées telles que `GetColors` les rend, peut-être retournées verticalement : sans effet sur les
  temps, à régler dans l'hôte.
