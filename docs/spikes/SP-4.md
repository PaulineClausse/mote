# SP-4 : le core tourne sur le casque

Statut : terminé. Méthode et règle fixées avant les mesures (2026-10-13), mesures du 2026-10-14 · Auteur :
claude-agent@mote-session · Tâche : TASK-2b19

Contexte :
- **H-05** : la lecture CPU des images (`GetColors`, signalée coûteuse `[DOC]`) et l'encodage JPEG logiciel
  (libjpeg-turbo, NEON) tiennent dans le budget du casque, sans gêner le tracking.
- **ADR-5955** (ADR-004) : sessions en MCAP. Le fonctionnement de la crate Rust sur Android arm64 est `[A VERIFIER]`.
- **NFR-05** : un budget CPU pour le core reste à fixer.

Configuration nominale : deux caméras en 1280 x 1280, 10 paires/s, JPEG q90.

## 1. Verdict (à remplir en dernier)

Mesuré sur Quest 3S le 2026-10-14, `libsp4core.so` (Rust) chargé par Unity dans QRC, 10 paires/s de 1280 x 1280.

- **GetColors, une paire 1280 x 1280** : 15,85 ms (p50), 17,80 ms (p95), 36,87 ms (max), sur le thread principal.
  L'affichage tombe de 72 à 62 images/s et 17 % des images sont ratées, avant même le core. La relecture GPU
  asynchrone ne coûte que 5,81 ms (p50) au thread principal par paire, copie et push compris, avec 3 frames de latence.
- **Encodage JPEG q90 d'une paire** : 23,6 ms sur un cœur en encodage pur (11,8 ms par image synthétique). Sur
  images réelles pendant la capture : 15,3 ms par image (p50), 16,6 ms (p95), soit 30,6 ms de CPU par paire,
  environ 15 ms de temps réel sur les deux threads du core.
- **Charge CPU à 10 paires/s**, relecture asynchrone : threads du core à 30,5 % d'un cœur ; processus entier à
  118,5 % d'un cœur contre 72,0 % au repos caméras actives, sur 6 cœurs. Aucune paire perdue, aucune alerte thermique.
- **MCAP écrit sur le casque, lu sur PC** : oui. Les deux MCAP du passage (553 et 764 Mo, chunks zstd) sont relus par
  `verify_mcap.py` avec `mote_pb2` : 2 398 et 3 596 images décodées, séquences contiguës, `/session/end` présent.
- **Budget NFR-05** : threads du core ≤ **40 % d'un cœur** en configuration nominale ; appel `mote_push_*` d'une paire
  ≤ **10 ms** sur le thread de l'hôte. Calcul et écart en §4.3.
- **H-05 : validée avec réserve.** Le core et l'encodage logiciel tiennent. `GetColors` sur le thread principal ne
  tient pas : l'hôte doit lire les images par `AsyncGPUReadback`, et avec elle tous les critères de §2 tiennent.
- **ADR-004 : confirmé.** La crate `mcap` tourne sur Android arm64 ; le plan B n'est pas nécessaire.
- **Conséquences pour WP-02 à WP-06** :
  - WP-02 : la chaîne du spike suffit (cargo-ndk, NDK r27c, API 32, libjpeg-turbo compilé avec NEON) ; le `.so`
    fait 1,7 Mo et ne dépend que de libc et libdl.
  - WP-03 : l'API en push, copie puis file de 8 paires, n'a perdu aucune paire. La copie d'une paire RGBA coûte
    4,3 ms en moyenne à l'hôte : pas besoin d'API sans copie pour tenir le budget.
  - WP-04 : deux threads d'encodage suffisent à 10 paires/s. Une image réelle fait 207 Ko en moyenne en q90, soit
    33,9 Mbit/s sans sélection de paires : chiffre d'entrée pour SP-5 et WP-14.
  - WP-05 : l'écriture MCAP coûte 1,5 ms par image ; le format n'est pas un goulot.
  - WP-06 : lecture par `AsyncGPUReadback` obligatoire, horodatage pris à la demande et non au callback (la sonde le
    fait ainsi), 3 frames de latence à absorber. Ne pas utiliser `GetColors`, voir aussi l'anomalie de taille en §4.3.

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
    `GetColors` (60 s, 10 paires/s), `Nominal` (120 s, 10 paires/s), `Async` (180 s, 10 paires/s), selon
    `sp4_config.json`.
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

Passage du 2026-10-14, environ 8 minutes, casque porté en regardant la pièce. Sortie de `run_sp4.ps1`, dossier
`runs\20261014_085138` sur le PC NVIDIA.

### 4.1 Encodage pur

40 images synthétiques 1280 x 1280, JPEG q90, un thread : médiane 11,8 ms, p95 13,8 ms par image, 749 Ko en moyenne,
soit 23,6 ms par paire sur un cœur. Le bruit synthétique se comprime mal, d'où des fichiers plus gros que sur images
réelles.

### 4.2 Phases (affichage, CPU, GetColors, thermique)

| Phase | durée (s) | images/s | intervalle p50 / p99 (ms) | images ratées | CPU du processus (% d'un cœur, 6 cœurs) | thread principal par paire p50 / p95 / max (ms) | paires poussées | thermique |
|---|---|---|---|---|---|---|---|---|
| Baseline | 60 | 72,0 | 13,88 / 15,02 | 0,02 % | 72,0 | - | 0 | 0 |
| GetColors | 60 | 62,0 | 14,08 / 27,98 | 17,07 % | 70,5 | 15,85 / 17,80 / 36,87 | 0 | 0 |
| Nominal | 120 | 42,1 | 14,15 / 56,15 | 27,88 % | 163,9 | 14,94 / 16,45 / 21,04 | 1 199 | 0 |
| Async | 180 | 72,0 | 13,88 / 15,49 | 0,16 % | 118,5 | 5,81 / 9,48 / 14,72 | 1 798 | 0 |

Affichage à 72 Hz partout. Aucune paire écartée (pas d'image, taille, file, erreur) dans aucune phase. Aucune seconde
avec un statut thermique non nul sur les 433 secondes journalisées. En `Nominal` et en `GetColors`, la colonne du
thread principal mesure `GetColors` seul ; la copie du push s'y ajoute en `Nominal` (§4.3). En `Async`, elle compte la
demande et les deux callbacks, copie et push compris ; latence de relecture : 3 frames (médiane et max).

Application de la règle de §2 :

| Critère | Nominal | Async |
|---|---|---|
| affichage ≥ 98 % de Baseline | non (42,1 / 72,0) | oui (72,0 / 72,0) |
| images ratées ≤ Baseline + 0,5 point | non (27,88 %) | oui (0,16 %) |
| paires perdues < 1 % (NFR-02) | oui (0 %) | oui (0 %) |
| le core suit, sans erreur | oui | oui |
| thermique < 3 | oui (0) | oui (0) |

Seul l'affichage décroche en `Nominal`, et il décroche déjà en `GetColors` : H-05 est **validée avec réserve**.
`Async`, le remède prévu, passe tous les critères.

### 4.3 Core en configuration nominale

| Mesure | Nominal (sync, voir l'anomalie) | Async |
|---|---|---|
| paires poussées / encodées / perdues | 1 199 / 1 199 / 0 | 1 798 / 1 798 / 0 |
| taille poussée | 1280 x 5120 | 1280 x 1280 |
| copie dans `sp4_push_pair`, moyenne / max | 29,31 / 34,07 ms | 4,29 / 9,72 ms |
| encodage JPEG par image, p50 / p95 / max | 42,1 / 43,3 / 50,7 ms | 15,3 / 16,6 / 21,8 ms |
| écriture MCAP par image, moyenne | 1,77 ms | 1,52 ms |
| JPEG moyen | 300 Ko | 207 Ko |
| CPU des threads du core | 83,5 % d'un cœur | 30,5 % d'un cœur |

**Anomalie de taille en `Nominal`.** `GetColors` a rendu un `NativeArray<Color32>` de 6 553 600 éléments, alors que la
texture et `CurrentResolution` valent 1280 x 1280, soit 1 638 400 pixels. La sonde prend la largeur sur la texture et
déduit la hauteur du tableau : elle a donc poussé des images de 1280 x 5120, quatre fois la surface nominale. Les JPEG
du MCAP `Nominal` se décodent bien à cette taille annoncée. Le surcroît se comprime bien (300 Ko pour quatre fois la
surface, contre 207 Ko), ce qui suggère trois quarts de remplissage ; la première paire extraite par
`verify_mcap.py` (`first_pair_Nominal`) permet de le voir. La relecture asynchrone rend bien 1280 x 1280. Les
chiffres du core en `Nominal` mesurent donc une charge quatre fois trop lourde : ils ne décrivent pas la
configuration nominale. Cela explique aussi une partie de la chute d'affichage en `Nominal`, où la copie de 29 ms
s'ajoute à `GetColors` sur le thread principal.

**Budget NFR-05, et écart.** La règle prend la configuration nominale : deux caméras 1280 x 1280, 10 paires/s, q90.
Seule la phase `Async` la réalise ; c'est elle qui sert au calcul.
- Threads du core : 30,5 % mesuré, majoré de 25 % (38,1 %), arrondi aux 5 % supérieurs : **40 % d'un cœur**.
- Appel `mote_push_*` d'une paire : max mesuré 9,72 ms, arrondi au demi-ms supérieur : **10 ms**.

`analyze_sp4.py` calcule le budget sur la phase `Nominal` et propose 105 % d'un cœur et 34,5 ms. Ces valeurs
correspondent à des images quatre fois trop grandes ; elles restent une borne haute si l'hôte devait un jour pousser
1280 x 5120, ce que rien ne justifie.

### 4.4 MCAP relu sur PC

| | Nominal | Async |
|---|---|---|
| fichier | `sp4_1791959832.mcap`, 552,8 Mo, 619 chunks zstd | `sp4_1791959952.mcap`, 763,5 Mo, 664 chunks zstd |
| `/cam/left/frame`, messages / dernier seq | 1 199 / 1 198 | 1 798 / 1 797 |
| `/cam/right/frame`, messages / dernier seq | 1 199 / 1 198 | 1 798 / 1 797 |
| `/session/info`, `/session/end` | 1 et 1 | 1 et 1 |
| JPEG décodés à la taille annoncée | 2 398, 300 Ko en moyenne | 3 596, 207 Ko en moyenne |
| durée couverte, débit d'images | 120,0 s, 49,2 Mbit/s | 180,0 s, 33,9 Mbit/s |
| conforme | oui | oui |

Les deux fichiers portent `sp4core 0.1.0` et sa configuration (`jpeg_quality` 90, 2 threads, file de 8 paires). Ils
ont été écrits sur le casque, rapatriés par `adb pull` et relus sous Windows par le code Python de `mote.v1` :
**ADR-004 confirmé**.

## 5. Lecture et limites

- `GetColors` est appelé sur le thread principal, comme le ferait un hôte naïf. MRUK recommande `AsyncGPUReadback`
  pour éviter ce coût ; la réserve de §2 a joué et la phase `Async` montre que la piste suffit.
- Le coût de `GetColors` est peut-être gonflé par son tableau quatre fois trop grand (§4.3). La conclusion ne change
  pas : la relecture asynchrone tient, il n'y a pas de raison de revenir à `GetColors`.
- Un seul passage, de 8 minutes : la tenue thermique sur une session longue relève de WP-18.
- La sonde tourne dans QRC sans que QRC enregistre. Le coût d'un vrai hôte mote (pose du casque, profondeur, UI de
  couverture) n'y est pas.
- Le CPU du processus inclut Unity, le rendu et MRUK. Seul celui des threads du core est imputable au core.
- Pas de sélection de paires (WP-09) : 10 paires/s sont toutes encodées, c'est le pire cas.
- Les images sont stockées telles que `GetColors` les rend, peut-être retournées verticalement : sans effet sur les
  temps, à régler dans l'hôte.
