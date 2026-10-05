# mote : Spécification technique

Version du document : 0.4 (document de contexte ; le normatif est dans ank)
Date : 2026-10-05
Statut : ADR et specs proposés dans ank, en attente de ratification ; spikes prêts à démarrer (section 14.1).

---

## 0. Méta-informations sur ce document

### 0.1 Objet

Ce document spécifie **mote**, un système de capture d'environnement sur casque Meta Quest 3S, destiné à alimenter une reconstruction 3D Gaussian Splatting (3DGS) en quasi temps réel, avec un second passage de haute qualité en différé. Il consigne le contexte, les raisons des choix, les sources consultées, l'approche retenue, les décisions d'architecture et de technologies, les risques et les questions ouvertes.

### 0.2 Légende des niveaux de confiance

Chaque affirmation non triviale porte un tag. Le réviseur doit prioritairement challenger les tags les plus faibles.

| Tag | Signification |
|---|---|
| `[SOURCE]` | Lu dans une source citée en section 4 (README, article, dataset card). Le code source des dépôts n'a PAS été lu. |
| `[DOC]` | Lu dans la documentation officielle Meta (pages listées en 4.3), le 2026-10-05. Les pages ont été lues à travers un outil de résumé automatique : relire la page d'origine avant de s'appuyer sur un chiffre précis. |
| `[CONNU]` | Connaissance générale de l'auteur du document, non vérifiée pendant la rédaction. |
| `[HYPOTHESE]` | Choix de travail ou valeur cible proposée, à valider par une mesure ou un spike. |
| `[A VERIFIER]` | Point factuel incertain sur lequel une décision pourrait reposer. À confirmer dans la documentation officielle Meta ou par test sur casque. |
| `[DECISION]` | Décision d'architecture prise (voir section 8), révisable via un ADR. |

### 0.3 Instructions pour l'agent réviseur

1. Relever les contradictions internes, les exigences non testables, les chiffres sans méthode de mesure.
2. Pour chaque `[A VERIFIER]`, proposer la méthode de vérification la moins chère (lecture doc, test sur casque, lecture de code).
3. Vérifier la matrice de traçabilité (section 15.2) : chaque exigence (FR, NFR) doit être couverte par un composant, un work package et un jalon. Lire les entités ank citées (section 0.5) : elles font partie du périmètre de la review.
4. Vérifier que chaque décision (ADR) a des alternatives documentées et un critère de remise en cause.
5. Signaler les trous restants : gestion d'erreurs, versions du SDK, licences, sécurité.
6. Ne pas réécrire le document : produire une liste d'écarts classés par gravité, puis valider le découpage de la section 15.

### 0.4 Conventions

- Identifiants stables, chacun avec un préfixe unique :

| Préfixe | Objet |
|---|---|
| `G-` | objectifs |
| `NG-` | non-objectifs |
| `SC-` | critères de succès |
| `SRC-` | sources (section 4) |
| `H-` | hypothèses |
| `FR-` / `NFR-` | exigences fonctionnelles / non fonctionnelles |
| `ADR-` | décisions |
| `SP-` | spikes |
| `M` | jalons |
| `WP-` | work packages |
| `RISK-` | risques |
| `Q-` | questions ouvertes |

- Unités : SI, temps en nanosecondes entières (`t_ns`), distances en mètres, angles en radians sauf mention contraire.
- Nommage des transformations : `a_from_b` désigne la transformation qui amène un point exprimé dans le repère `b` vers le repère `a`. Exemple : `world_from_camera` est la pose de la caméra dans le monde (c2w).
- « Live » désigne un aperçu exploitable pendant le scan, pas le rendu final.
- « Paire » désigne les deux images gauche et droite d'un même instant. La paire est l'unité de capture, de sélection et d'évaluation.
- « Configuration nominale » : voir 6.2.

### 0.5 Où se trouve quoi

Ce document porte le contexte : problème, objectifs, sources, hypothèses, plan, risques, questions ouvertes. Tout ce qui est normatif vit dans le corpus ank du dépôt (`.ank/`), consulté par la CLI :

| Contenu | Où | Commande |
|---|---|---|
| Décisions d'architecture | ADR ank (table en section 8) | `ank find --type adr`, `ank show <id>` |
| Exigences, architecture, formats, API, protocoles, évaluation | specs ank (sections 6, 7, 9, 10, 11, 13) | `ank find --type spec`, `ank show <id>` |
| Spikes et work packages | tâches ank (section 15.1) | `ank graph`, `ank context` |

Une règle n'est écrite qu'à un seul endroit. Les sections 6 à 11, 13 et 15.1 gardent leur numéro pour que les renvois restent valides, mais ne contiennent plus qu'un pointeur.

### 0.6 Journal des modifications

**0.4 (2026-10-05)** : découpage dans ank. Les ADR, les exigences, l'architecture, le modèle de données, l'API C, le pipeline PC, le protocole d'évaluation et un nouveau protocole de transport deviennent des entités ank ; spikes et work packages deviennent des tâches. Ce document est allégé en conséquence.

**0.3 (2026-10-05)**, confrontation à la documentation officielle Meta (SP-1 en grande partie réalisé, détail en 4.3) :
- Confirmé : caméras passthrough sur Quest 3 et 3S, 1280x1280 à partir de Horizon OS v83, accès simultané aux deux caméras, pose par frame, profondeur supportée sur 3S et livrée en texture GPU.
- Corrigé : les intrinsèques MRUK ne contiennent pas de distorsion ; le timestamp MRUK est un `DateTime` (nouvelle base de temps `UNIX`) ; exposition et ISO ne sont pas exposés par MRUK (FR-06 devient conditionnelle) ; la lecture CPU des images (`GetColors`) est signalée comme coûteuse (RISK-14) ; le plan lointain de la profondeur peut être infini (9.5).
- Reste non documenté, donc à mesurer : base de temps exacte, type d'obturateur, synchronisation gauche/droite, distorsion résiduelle, résolution et cadence de la profondeur, écarts Quest 3 / 3S.

**0.2 (2026-10-05)**, suite à une première relecture :
- Le projet s'appelle **mote** (ancien nom de travail : QSCAN). Composants, paquet protobuf et API renommés.
- Préfixes d'identifiants dédoublonnés : `SC-` (critères de succès), `SRC-` (sources), `SP-` (spikes), auparavant tous notés `S`.
- L'acquisition (caméras, poses, profondeur) est faite par l'hôte Unity via MRUK et poussée au core ; le core n'accède plus au matériel (ADR-002, ADR-011). L'accès Camera2 natif, l'hôte natif et HEVC passent en v2.
- JPEG logiciel seul en v1 ; l'hypothèse du chemin zéro-copie vers MediaCodec est abandonnée (ADR-003).
- Modèle de temps refondu autour de `CLOCK_MONOTONIC` et de la pose par frame (9.3).
- Le MCAP du casque devient la source de vérité ; le flux live est en best effort avec rattrapage (ADR-012).
- Ingest PC en Python au lieu de Rust (ADR-007).
- Profondeur stockée brute, linéarisée à l'ingest (9.5).
- Protocole d'évaluation durci (hold-out par blocs, optimisation des poses de test) ; SfM complet distingué de l'option C (référence REF).
- Plan réordonné : validation de l'hypothèse centrale H-01 avec les outils existants avant tout développement (SP-0), hôte Unity dès M1.
- Ajouts : enveloppe de transport, sécurité du transport, événements de recentrage, matrice de traçabilité.

---

## 1. Contexte et problème

### 1.1 Situation de départ

Une première tentative a été réalisée : capture avec les caméras du Quest, estimation des poses de caméras et du nuage de points avec COLMAP, envoi des données à un PC, reconstruction 3D avec NeRF.

### 1.2 Problème constaté

COLMAP (extraction et matching de features, puis SfM) prend un temps considérable. Il empêche tout retour rapide pendant le scan et rallonge le cycle essai/erreur.

### 1.3 Idée directrice

Le casque effectue déjà un suivi de position et d'orientation (tracking inside-out) en temps réel, en échelle métrique. Les poses de caméras peuvent donc être fournies par le casque, ce qui supprime l'étape la plus coûteuse de COLMAP (estimation des poses). Reste à traiter l'initialisation géométrique (nuage de points), le raffinement des poses, et l'acheminement des données vers l'entraînement 3DGS avec une latence faible.

### 1.4 Pourquoi un logiciel de capture dédié

- Meta ne propose pas d'export des données brutes de capture ni des PLY entraînés pour son application de capture (Hyperscape Capture) `[SOURCE]` (SRC-5).
- Les outils communautaires existants (SRC-1, SRC-2) sont conçus pour enregistrer sur le disque du casque puis exporter, avec des images brutes volumineuses et un export lent `[SOURCE]`. Notre cas d'usage est un flux vers un entraînement incrémental, ce qui impose une autre couche de stockage et de transport.
- Ces outils restent la meilleure base pour l'acquisition : mote réutilise leur approche d'accès au matériel et ne remplace que ce qui se trouve en aval (ADR-001, ADR-011).

---

## 2. Objectifs, non-objectifs, critères de succès

### 2.1 Objectifs

- **G-01** Capturer un environnement intérieur avec un Quest 3S : paires d'images des caméras passthrough, poses, intrinsèques, profondeur, avec horodatage cohérent.
- **G-02** Se passer de COLMAP pour l'estimation des poses (utiliser le tracking du casque) tout en permettant un raffinement des poses à l'entraînement.
- **G-03** Guider l'opérateur pendant le scan par deux retours distincts : un aperçu 3DGS quasi live affiché sur le PC, et un retour de couverture affiché dans le casque (calculé à bord, sans dépendre du splat).
- **G-04** Produire à la fin un splat final de haute qualité par un second entraînement plus long sur les mêmes données.
- **G-05** Conserver chaque session dans un format ouvert, rejouable, pour comparer des stratégies d'initialisation et d'entraînement à données identiques.
- **G-06** Livrer un core natif réutilisable (API C), indépendant du moteur et du matériel, consommé en v1 par Unity.
- **G-07** Rester ouvert et vendor-agnostic côté PC : formats ouverts, outils open source, pas de dépendance à un service cloud.

### 2.2 Non-objectifs (v1)

- **NG-01** Rendu du splat sur le casque, et renvoi au casque d'une carte de couverture issue de l'entraînement (v1.5 ou v2).
- **NG-02** Support Quest 2, Quest Pro ou autres casques (l'API caméra passthrough ciblée n'est disponible que sur Quest 3 et 3S `[SOURCE]`).
- **NG-03** Scan multi-utilisateurs ou multi-casques simultanés.
- **NG-04** Reconstruction de scènes dynamiques (personnes en mouvement) : on les traite comme bruit à éviter.
- **NG-05** Garantie de précision métrologique. L'échelle est métrique via le tracking, sans promesse de tolérance.
- **NG-06** Publication sur le store Meta (distribution par sideload en v1).
- **NG-07** Hôte natif (NativeActivity + OpenXR) et accès caméra direct par Camera2 NDK. L'API C est conçue pour les permettre, ils ne sont pas livrés en v1.
- **NG-08** Encodage vidéo matériel (HEVC all-intra par MediaCodec).

### 2.3 Critères de succès globaux

Les seuils chiffrés sont des `[HYPOTHESE]` à calibrer sur les résultats de SP-0.

- **SC-01** Une capture de 1 à 3 minutes dans une pièce produit, pendant le scan, un aperçu atteignant un PSNR d'au moins 20 dB sur les vues de validation déjà couvertes, dans le délai de NFR-04.
- **SC-02** Le splat final de la meilleure option d'initialisation dépasse la baseline A d'au moins 1 dB de PSNR sur le hold-out, à itérations égales.
- **SC-03** Le temps de pré-traitement (de la fin du scan au début de l'entraînement final) est inférieur d'un ordre de grandeur au temps d'un SfM complet sur la même session (référence REF, section 13.3, chronométrée).
- **SC-04** La même session rejouée avec les options A à E (section 11.3) donne des métriques comparables (PSNR, SSIM, LPIPS) selon le protocole de la section 13.

---

## 3. Enseignements de la tentative précédente

| Constat | Conséquence pour mote |
|---|---|
| COLMAP trop lent | Poses issues du tracking du casque ; COLMAP relégué à un rôle offline (option C, référence REF) |
| Pipeline séquentiel capture, puis COLMAP, puis NeRF | Pipeline en flux : capture, ingest, entraînement incrémental |
| Données difficiles à rejouer | Format de session unique, ouvert, indexé (MCAP) ; tout ce qui est retenu par la sélection à bord est conservé durablement (ADR-012) |
| Pas de métriques de comparaison | Protocole d'évaluation figé dès le départ (section 13) |

---

## 4. Sources et état de l'art

Toutes les URLs ci-dessous ont été consultées pendant la préparation de ce document. Seuls les READMEs et pages web ont été lus, pas le code source.

### 4.1 Outils de capture Quest existants

**SRC-1. QuestRealityCapture** (t-34400), https://github.com/t-34400/QuestRealityCapture
- Application Unity de journalisation pour Quest 3 et 3S, firmware v74+ requis, licence MIT, release v1.5.0 (18 juin 2026), Unity 6000.4.5f1. `[SOURCE]`
- Enregistre poses HMD et contrôleurs, images des deux caméras passthrough, métadonnées de caméra, cartes de profondeur. `[SOURCE]`
- Deux backends caméra : **MRUK** (par défaut, `PassthroughCameraAccess`, frames RGBA32 brutes, pose caméra horodatée par frame, intrinsèques en JSON, appariement stéréo par timestamp le plus proche) et **NativeCamera2** (hérité, YUV_420_888 brut via Camera2 NDK). `[SOURCE]`
- Pour des frames 1280x1280, un fichier `.rgba` fait 6 553 600 octets. `[SOURCE]`
- Profondeur : fichiers `.float32` bruts avec descripteurs CSV (pose de création, tangentes de FOV, near/far, largeur, hauteur). `[SOURCE]`
- Poses : `hmd_poses.csv` avec colonnes `unix_time, ovr_timestamp, pos_x..z, rot_x..w`. `[SOURCE]`
- Fréquences de sauvegarde par défaut : caméra 10 fps, profondeur 10 fps, poses 30 fps. `[SOURCE]`
- Retour visuel dans le casque : couverture de profondeur, trajectoire, marqueurs de discontinuité de tracking. `[SOURCE]`
- Problème connu : crash natif Unity possible à la fermeture après usage de la caméra MRUK, fichiers déjà écrits. `[SOURCE]`
- Note de migration : les poses des anciens logs ont subi un prétraitement vers l'espace Unity, conversion documentée `(x,y,z) vers (x,y,-z)` et quaternion `(x,y,z,w) vers (-x,-y,z,w)` pour retrouver les valeurs brutes Camera2. `[SOURCE]` Indique que les conventions de repère des poses caméra sont un piège réel.

**SRC-2. OpenQuestCapture** (samuelm2), https://github.com/samuelm2/OpenQuestCapture
- Fork conceptuel de SRC-1, Unity 6000.2.9f1, licence MIT, Quest 3 et 3S. `[SOURCE]`
- Capture YUV des deux caméras, caractéristiques Camera2 (pose, intrinsèques, infos capteur), profondeur et descripteurs, fps par défaut 3. `[SOURCE]`
- Visualisation temps réel de la couverture de profondeur : couleur selon l'angle de prise (blanc = frontal, couleurs vives = rasant). `[SOURCE]`
- Conseils de capture : bon éclairage constant, mouvements lents, captures de 1 à 3 minutes. `[SOURCE]`
- L'export zip prend plusieurs minutes (point d'amélioration cité par l'auteur). `[SOURCE]`
- Sous-module `QuestCameraLib` (bibliothèque caméra, probablement Kotlin d'après le script `rebuild_kotlin_library.ps1`), code non lu. `[SOURCE]`
- Chaîne aval : dépôt compagnon `quest-3d-reconstruction`, script `e2e_quest_to_colmap.py` (YUV vers RGB, reconstruction, export modèle COLMAP), tone mapping CLAHE + gamma pour scènes avec fenêtres. `[SOURCE]`

**SRC-3. metaquest-3d-reconstruction** (t-34400), https://github.com/t-34400/metaquest-3d-reconstruction
- Conversion, génération de profondeur stéréo, export COLMAP, reconstruction TSDF. Workflows : datasets legacy et MRUK, profondeur native Quest, profondeur **FoundationStereo** et **Fast-FoundationStereo**, export COLMAP. `[SOURCE]`
- Dossier `examples` présent, contenu non inspecté. `[A VERIFIER]`

**SRC-4. QuestRoomScan / QuestInfiniteScan**, https://github.com/AdrianoVM/QuestRoomScan et https://github.com/fladirm/QuestInfiniteScan
- Reconstruction de pièce temps réel sur Quest 3 : TSDF GPU, maillage Surface Nets, texturage passthrough, détection d'objets, MRUK. `[SOURCE]`
- Pipeline Gaussian Splat : capture de keyframes JPEG gatées par le mouvement avec poses (`keyframes/images/*.jpg` et `keyframes/frames.jsonl`), entraînement sur un serveur PC, téléchargement du PLY entraîné, rendu sur le casque. `[SOURCE]`
- Pertinent comme référence d'architecture « casque, serveur PC, retour casque ». Code non lu.

**SRC-5. Article radiancefields.com**, https://radiancefields.com/openquestcapture-for-quest-3-and-3s-capture
- Contexte : Meta n'offre pas d'export des données brutes ni des PLY de Hyperscape Capture ; OpenQuestCapture comble ce manque ; chaîne possible vers Postshot ou Lichtfeld Studio, ou service cloud vid2scene. `[SOURCE]`

**SRC-6. Dataset Hugging Face Meta Quest Ego**, https://huggingface.co/datasets/Oceanveo/meta-quest-ego
- 14 épisodes courts, vidéos stéréo 1280x1280, poses HMD, calibrations caméra, flux de tracking avec landmarks de mains. Accès soumis à conditions (gated). `[SOURCE]` Utile pour voir un format réel de poses et de calibration, pas pour entraîner un splat d'environnement.

### 4.2 Reconstruction 3D et modèles feed-forward

- **NoPoSplat** https://github.com/cvg/NoPoSplat : prédiction de Gaussiennes depuis images sans poses, convention de caméra OpenCV c2w (X droite, Y bas, Z avant). `[SOURCE]`
- **AnySplat** https://github.com/thinhlpg/AnySplat : 3DGS feed-forward depuis vues non contraintes, têtes pour Gaussiennes, profondeur et poses. `[SOURCE]`
- **VGGT, MASt3R, MASt3R-SLAM** : modèles feed-forward de pointmaps et poses. `[CONNU]` Licences des poids à vérifier avant tout usage non académique. `[A VERIFIER]`
- **nerfstudio splatfacto** et **gsplat** : implémentations d'entraînement 3DGS, camera optimizer (mode `SO3xR3`) pour raffiner les poses. `[CONNU]`
- Le 3DGS original (Inria) est sous licence non commerciale. `[CONNU]` Éviter comme dépendance si un usage commercial est envisageable. `[A VERIFIER]`

### 4.3 Documentation officielle Meta

Pages consultées le 2026-10-05 (SP-1). Tout ce qui suit est tagué `[DOC]` sauf mention contraire.

**Caméras passthrough (Passthrough Camera API, PCA)**
- Disponible sur Quest 3 et Quest 3S, à partir de Horizon OS v74. Construite sur l'API Android Camera2. Le passthrough doit être activé dans l'application.
- Deux caméras RGB frontales (gauche, droite). Format interne YUV420, cadence 60 Hz, latence de capture annoncée de 20 à 40 ms.
- Résolutions : 1280x960 au maximum jusqu'à v81 ; 1280x1280 (et d'autres formats intermédiaires) à partir de v83.
- Coût annoncé : environ 1 à 2 % de GPU par caméra diffusée, environ 45 Mo de mémoire.
- Permission `horizonos.permission.HEADSET_CAMERA`. Non supportée dans le XR Simulator.
- Les images sont classées « Device User Data » par la politique d'usage des données de Meta (voir 18.2).

**Composant MRUK `PassthroughCameraAccess`** (MRUK v81 ou plus récent)
- Une instance par caméra ; deux instances donnent l'accès simultané à la gauche et à la droite.
- `Timestamp` (type `DateTime`) : timestamp de la dernière image. `GetCameraPose()` : pose monde de la caméra à ce timestamp. `IsUpdatedThisFrame` signale une nouvelle image.
- `Intrinsics` : `FocalLength`, `PrincipalPoint`, `SensorResolution`, `LensOffset` (pose du capteur par rapport au casque). **Aucun coefficient de distorsion.**
- `GetTexture()` donne la texture GPU ; `GetColors()` renvoie un `NativeArray<Color32>` pour le traitement CPU, avec l'avertissement que la méthode est coûteuse.
- `MaxFramerate` réglable (60 par défaut, la cadence réelle peut varier), `RequestedResolution`, `GetSupportedResolutions()`.

**Accès Camera2 natif**
- Permissions `android.permission.CAMERA` et `horizonos.permission.HEADSET_CAMERA`, `minSdk` 34. Clés constructeur `com.meta.extra_metadata.position` (0 gauche, 1 droite) et `com.meta.extra_metadata.camera_source` (0 pour le passthrough).
- La configuration expose la position et la rotation de l'objectif par rapport au centre du casque, mais la page indique que les exemples de calcul de pose « suivront ». Cela conforte le report de cette voie en v2 (NG-07).

**Profondeur d'environnement (Depth API, extension `XR_META_environment_depth`)**
- Supportée sur Quest 3 et Quest 3S (page Unity « Depth API overview »). La page Unity « XR.Oculus », plus ancienne, dit « Quest 3 uniquement ». Le passthrough est requis.
- Cartes de profondeur par œil, livrées dans une swapchain lisible, donc en texture GPU ; côté Unity, une `RenderTexture` utilisable en rendu ou en compute shader. Aucune API CPU.
- Résolution à interroger à l'exécution (`xrGetEnvironmentDepthSwapchainStateMETA`) ; ni résolution ni cadence ne sont documentées.
- Descripteur par œil : pose de création, FOV, `nearZ`, `farZ`, instant de création (`createTime`), `minDepth`, `maxDepth`. La pose est exprimée dans l'espace de référence demandé par l'application.
- `nearZ` et `farZ` sont les plans d'une projection OpenGL et servent à convertir les valeurs en distances métriques. `farZ` peut être infini ; la doc donne alors le quadrant bas-droit de la matrice de projection : `[[-1, -2*nearZ], [-1, 0]]`.
- Portée minimale fiable : environ 0,2 m. Suppression des mains optionnelle, selon l'appareil. Un surcoût existe dès que la profondeur est activée, même sans lecture.

**Non documenté dans les pages lues** (reste `[A VERIFIER]`, par test) :
- base de temps exacte du `Timestamp` MRUK et instant visé dans l'exposition ;
- type d'obturateur, synchronisation matérielle gauche/droite ;
- distorsion résiduelle des images (la doc ne dit pas qu'elles sont rectifiées) ;
- exposition et ISO par image ;
- format et normalisation des valeurs de profondeur, résolution, cadence ;
- différences de qualité de profondeur entre Quest 3 et 3S ;
- requête de la pose du casque à un instant passé depuis Unity ; comportement au recentrage.

Complément de source secondaire (UploadVR, non officiel) : la profondeur est calculée par disparité entre les deux caméras de tracking, à faible résolution, utilisable jusqu'à 4 ou 5 m environ ; le Quest 3S n'a pas le projecteur de profondeur du Quest 3 mais deux illuminateurs infrarouges. `[SOURCE]`

Pages :
- https://developers.meta.com/horizon/documentation/spatial-sdk/spatial-sdk-pca-overview/
- https://developers.meta.com/horizon/documentation/unity/unity-pca-documentation/
- https://developers.meta.com/horizon/reference/mruk/v83/class_meta_x_r_passthrough_camera_access/
- https://developers.meta.com/horizon/documentation/unity/unity-pca-migration-from-webcamtexture/
- https://developers.meta.com/horizon/documentation/native/android/pca-native-documentation/
- https://developers.meta.com/horizon/documentation/native/android/mobile-depth/
- https://developers.meta.com/horizon/documentation/unity/unity-depthapi-overview/
- https://developers.meta.com/horizon/documentation/unity/unity-depthapi-xr-oculus/

---

## 5. Hypothèses techniques clés

| ID | Hypothèse | Tag | Comment la valider |
|---|---|---|---|
| H-01 | Les poses fournies par le casque (par frame via MRUK) suffisent à entraîner un 3DGS correct, avec raffinement de poses à l'entraînement. **Hypothèse centrale : tout le projet en dépend.** | `[HYPOTHESE]` | SP-0 : capture avec SRC-1 tel quel, entraînement, comparaison avec les poses d'un SfM complet |
| H-02 | La profondeur du Quest 3S est exploitable pour initialiser un nuage de points | `[A VERIFIER]` | SP-3. L'API est supportée sur 3S `[DOC]`, mais sa qualité n'est pas documentée ; on la suspecte moindre que sur Quest 3, qui possède un projecteur de profondeur `[SOURCE]` |
| H-03 | Un JPEG q90 dégrade peu la qualité du splat par rapport au brut | `[HYPOTHESE]` | Comparaison PSNR brut / JPEG q90 / JPEG q95 sur une session de référence enregistrée en `RAW_RGBA` |
| H-04 | La pose par frame fournie par MRUK correspond à l'instant de capture à quelques millisecondes près. La doc dit que `GetCameraPose()` renvoie la pose au timestamp de l'image `[DOC]`, sans donner de précision. | `[A VERIFIER]` | SP-2 : test de reprojection avec mouvement contrôlé |
| H-05 | La lecture CPU des images (`GetColors`, signalée coûteuse `[DOC]`) et l'encodage JPEG logiciel (libjpeg-turbo, NEON) de la configuration nominale tiennent dans le budget du casque sans gêner le tracking | `[HYPOTHESE]` | SP-4 : mesure des temps de lecture et d'encodage, et de la charge |
| H-06 | Le Wi-Fi 6 en 5 GHz soutient 100 Mbit/s en continu entre casque et PC | `[HYPOTHESE]` | SP-5 : mesure de débit soutenu en conditions réelles |
| H-07 | Une init par rétroprojection de la profondeur accélère la convergence et réduit les floaters par rapport à l'init aléatoire | `[HYPOTHESE]` | Comparaison A vs B (section 13) |
| H-08 | L'auto-exposition variable des caméras passthrough crée des incohérences de couleur, atténuables par une optimisation d'exposition par vue à l'entraînement, sans connaître l'exposition réelle (non exposée par MRUK `[DOC]`) | `[HYPOTHESE]` | Comparer l'entraînement avec et sans optimisation d'exposition par vue |
| H-09 | Les deux caméras passthrough sont suffisamment synchrones pour former des paires stéréo exploitables (option E). L'accès simultané est documenté `[DOC]`, la synchronisation ne l'est pas. | `[A VERIFIER]` | SP-2 (distribution des écarts de timestamps gauche/droite) |
| H-10 | L'obturateur des caméras (rolling ou global, non documenté) et la durée d'exposition n'introduisent pas d'erreur supérieure à celle visée par NFR-01 aux vitesses de scan recommandées | `[A VERIFIER]` | SP-2 (résidus de reprojection selon la vitesse) |
| H-11 | Les images fournies sont assez proches d'un modèle sténopé pour être utilisées sans coefficients de distorsion (MRUK n'en fournit pas `[DOC]`) | `[A VERIFIER]` | SP-2 : résidus de reprojection selon la distance au centre de l'image ; sinon calibration damier |

---

## 6. Exigences

Les exigences fonctionnelles (FR-01 à FR-20), non fonctionnelles (NFR-01 à NFR-08), la configuration nominale et les ordres de grandeur de débit sont dans la spec ank `SPEC-234a`.

---

## 7. Architecture

La vue d'ensemble, la table des composants et les frontières entre hôte, core et PC sont dans la spec ank `SPEC-3d2a`.

En une phrase : l'hôte Unity acquiert (caméras, poses, profondeur via MRUK) et pousse tout au core Rust, qui sélectionne les paires, encode en JPEG, écrit le fichier MCAP de session et le diffuse au PC, où un paquet Python fait l'ingest, l'entraînement et l'évaluation.

---

## 8. Décisions d'architecture (ADR)

Les ADR vivent dans ank, chacun avec sa contrainte, son contexte, ses alternatives et son critère de remise en cause. Les numéros ci-dessous sont ceux que le reste de ce document et les corps des entités utilisent.

| Numéro | Identifiant ank | Décision |
|---|---|---|
| ADR-001 | `ADR-801b` | Nouveau code, en réutilisant l'acquisition des outils existants |
| ADR-002 | `ADR-7a16` | Core natif à API C entièrement en push |
| ADR-003 | `ADR-86d6` | Pas de stockage brut ; JPEG logiciel à bord |
| ADR-004 | `ADR-5955` | MCAP comme format de fichier de session |
| ADR-005 | `ADR-956c` | Protobuf pour les schémas de messages |
| ADR-006 | `ADR-c36f` | Transport TCP, trames préfixées par leur taille |
| ADR-007 | `ADR-8d03` | Rust pour le core, Python pour tout le PC |
| ADR-008 | `ADR-da6e` | Python et PyTorch pour l'entraînement |
| ADR-009 | `ADR-6ded` | Données stockées brutes, conversions uniquement à l'ingest |
| ADR-010 | `ADR-53f5` | Sélection des paires à bord, avant encodage |
| ADR-011 | `ADR-6921` | Acquisition par l'hôte Unity via MRUK en v1 |
| ADR-012 | `ADR-d5f3` | Le MCAP du casque est la source de vérité, le flux live est en best effort |

---

## 9. Modèle de données et formats

Canaux MCAP (9.1), schéma protobuf `mote.v1` (9.2), modèle de temps (9.3), conventions de repère (9.4), profondeur (9.5) et versionnage (9.6) sont dans la spec ank `SPEC-64c5`. Les numéros de sous-section y sont conservés.

Le protocole de transport, le rattrapage et la sécurité du flux sont dans la spec ank `SPEC-9df2`.

---

## 10. API C du core

L'API C (`mote.h`) et ses règles d'usage sont dans la spec ank `SPEC-fdb8`.

---

## 11. Pipeline PC

Ingest (11.1), compensation d'exposition (11.2), options d'initialisation A à E (11.3), entraînement (11.4) et retour à l'opérateur (11.5) sont dans la spec ank `SPEC-834a`. Les numéros de sous-section y sont conservés.

---

## 12. Protocole de capture (opérateur)

Repris des conseils documentés par SRC-2 et à valider sur nos scènes : `[SOURCE]` `[HYPOTHESE]`
- Éclairage constant et suffisant, éviter les contre-jours forts.
- Mouvements lents et réguliers, éviter les rotations rapides sur place (flou, parallaxe insuffisante, erreur de synchronisation amplifiée).
- Couvrir chaque surface sous plusieurs angles, y compris des angles rasants et frontaux.
- Durée visée : 1 à 3 minutes par scène.
- Éviter les objets mobiles et les surfaces très réfléchissantes ou transparentes.
- Garder un recouvrement important entre vues successives.
- Ne pas recentrer le casque pendant un scan (9.4).

---

## 13. Évaluation et métriques

Le protocole de comparaison (13.1), les métriques (13.2) et la référence REF (13.3) sont dans la spec ank `SPEC-6438`.

---

## 14. Plan de réalisation

### 14.1 Spikes (réduction d'incertitude, avant tout développement)

SP-0 conditionne tout le reste : s'il invalide H-01, le projet est à repenser avant d'écrire du code.

| ID | Question | Moyen | Critère de sortie |
|---|---|---|---|
| SP-0 | H-01 : les poses du casque suffisent-elles ? | Capture avec SRC-1 non modifié, export avec SRC-3, entraînement splatfacto (option A), REF sur la même capture | Splat A et métriques, erreur de tracking chiffrée, seuils de SC-01 et SC-02 calibrés, décision de poursuite |
| SP-1 | Que dit la documentation officielle Meta ? (4.3) | Lecture. **Fait le 2026-10-05** à travers un outil de résumé ; reste à relire les pages d'origine pour les chiffres, et le code C# de MRUK pour la base de temps (Q-11) et la requête de pose (Q-13) | Q-01 tranchée ; Q-02, Q-03, Q-11 à Q-13 converties en tests (SP-2, SP-3) |
| SP-2 | Précision de la synchronisation image/pose, conventions de repère, synchronisation gauche/droite | Capture SRC-1 avec cible connue et mouvement contrôlé, script de reprojection | NFR-01 mesurée, formule de conversion validée (test 9.4), H-04, H-09 et H-10 tranchées |
| SP-3 | Qualité de la profondeur sur Quest 3S, linéarisation, coût de la relecture GPU | Dump de profondeur et rétroprojection visualisée | H-02 tranchée, formule confirmée, coût mesuré |
| SP-4 | Le core tourne-t-il sur le casque ? | `.so` Rust minimal chargé par Unity : encodage JPEG d'une paire, écriture MCAP | Temps d'encodage et charge CPU mesurés (H-05), crate MCAP validée sur Android (ADR-004), budget NFR-05 fixé |
| SP-5 | Débit réseau soutenu | Test de charge casque vers PC en TCP | H-06 tranchée, ADR-006 confirmé |

### 14.2 Jalons

| Jalon | Contenu | Critère de sortie |
|---|---|---|
| M0 | Spikes SP-0 à SP-5 ; versions figées (Unity, Meta XR SDK, MRUK, firmware, NDK, Rust) | Rapport de spikes, ADR et hypothèses mis à jour |
| M1 | Squelette bout en bout hors ligne : hôte Unity (acquisition MRUK, push), core (JPEG, MCAP local), `mote ingest --replay`, export nerfstudio | Une session MCAP du casque donne un splat A sur le PC |
| M2 | Sélection des paires, profondeur, événements, statistiques ; conversion de repères validée ; options A et B ; évaluation automatique | Splats A et B comparés selon la section 13 ; NFR-02 et NFR-07 vérifiées |
| M3 | Flux live, authentification, ingest en réception, rattrapage | Session PC complète après coupure (NFR-08) ; NFR-03 vérifiée |
| M4 | Entraînement incrémental, aperçu live sur PC, UI de couverture dans le casque | NFR-04 et SC-01 atteints |
| M5 | Options C, D, E ; entraînement final ; rapports automatiques ; tests de charge et de tenue thermique | Tableau de résultats par option ; SC-02 à SC-04, NFR-05 et NFR-06 vérifiés |

Hors v1 : hôte natif et accès Camera2 (NG-07), HEVC (NG-08), retour du splat ou de sa couverture vers le casque (NG-01).

---

## 15. Work packages et traçabilité

### 15.1 Tâches

Spikes et work packages sont des tâches ank, avec leur périmètre, leur critère de fin et leurs dépendances. `ank graph` donne l'ordre, `ank find --status open` ce qui reste.

| Référence | Tâche ank | Intitulé | Jalon |
|---|---|---|---|
| SP-0 | `TASK-e447` | voir 14.1 | M0 |
| SP-1 | `TASK-ab76` | voir 14.1 | M0 |
| SP-2 | `TASK-552b` | voir 14.1 | M0 |
| SP-3 | `TASK-eea1` | voir 14.1 | M0 |
| SP-4 | `TASK-2b19` | voir 14.1 | M0 |
| SP-5 | `TASK-1227` | voir 14.1 | M0 |
| WP-01 | `TASK-db5d` | Schémas protobuf mote.v1 | M1 |
| WP-02 | `TASK-85b5` | Toolchain Rust Android et PC | M1 |
| WP-03 | `TASK-85d8` | API C et squelette du core | M1 |
| WP-04 | `TASK-ec26` | Encodage JPEG | M1 |
| WP-05 | `TASK-3159` | Écriture MCAP locale | M1 |
| WP-06 | `TASK-0131` | Hôte Unity : acquisition MRUK et push | M1 |
| WP-07 | `TASK-643e` | Ingest hors ligne, dataset et exports | M1 |
| WP-08 | `TASK-43f1` | Conversion de repères et validation | M2 |
| WP-09 | `TASK-7454` | Sélection des paires et score de netteté | M2 |
| WP-10 | `TASK-5128` | Profondeur, de l'hôte à l'ingest | M2 |
| WP-11 | `TASK-2b0e` | Événements de tracking et statistiques | M2 |
| WP-12 | `TASK-2098` | Initialisations A et B, entraînement de base | M2 |
| WP-13 | `TASK-80c2` | Évaluation et rapports | M2 |
| WP-14 | `TASK-f326` | Transport live, authentification et rattrapage | M3 |
| WP-15 | `TASK-7239` | Entraînement incrémental et aperçu live | M4 |
| WP-16 | `TASK-d955` | UI de couverture dans le casque | M4 |
| WP-17 | `TASK-034a` | Initialisations C, D, E et référence REF | M5 |
| WP-18 | `TASK-fe5c` | Entraînement final, tests de charge et de tenue thermique | M5 |

### 15.2 Matrice de traçabilité

| Exigence | Composant | WP | Jalon |
|---|---|---|---|
| FR-01, FR-02, FR-06 | hôte Unity | WP-06 | M1 |
| FR-03 | hôte Unity, ingest | WP-10 | M2 |
| FR-04 | core | WP-09 | M2 |
| FR-05 | core | WP-04, WP-10 | M1, M2 |
| FR-07 | hôte Unity | WP-16 | M4 |
| FR-08, FR-10, FR-20 | core, ingest | WP-14 | M3 |
| FR-09 | core | WP-05 | M1 |
| FR-11 | ingest | WP-08 | M2 |
| FR-12 | train | WP-12, WP-17 | M2, M5 |
| FR-13 | train | WP-15 | M4 |
| FR-14 | train | WP-18 | M5 |
| FR-15 | tools | WP-07 | M1 |
| FR-16 | eval | WP-13 | M2 |
| FR-17 | core | WP-03 | M1 |
| FR-18 | proto | WP-01 | M1 |
| FR-19 | hôte Unity, core | WP-11 | M2 |
| NFR-01 | hôte Unity | SP-2, WP-08 | M0, M2 |
| NFR-02 | core | WP-09, WP-11 | M2 |
| NFR-03 | core | WP-14 | M3 |
| NFR-04 | train | WP-15 | M4 |
| NFR-05, NFR-06 | core, hôte Unity | SP-4, WP-18 | M0, M5 |
| NFR-07 | ingest, eval | WP-07, WP-13 | M2 |
| NFR-08 | core, ingest | WP-14 | M3 |

---

## 16. Risques

| ID | Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|---|
| RISK-01 | Dérive ou erreur du tracking du casque dégrade le splat | Moyenne | Élevé | SP-0 avant tout développement, raffinement de poses à l'entraînement, recalage hors ligne (C ou D), mesure d'erreur (13.3) |
| RISK-02 | Décalage image/pose non maîtrisé | Moyenne | Élevé | Pose par frame MRUK (ADR-011), SP-2 précoce, conservation des timestamps d'origine |
| RISK-03 | Conventions de repère erronées | Élevée | Élevé | ADR-009, test de validation obligatoire (9.4), stockage brut |
| RISK-04 | Profondeur Quest 3S de qualité insuffisante | Moyenne | Moyen | Option E (stéréo), option A en repli |
| RISK-05 | MRUK ne fournit pas ce qu'on attend sur 3S (résolution, cadence, pose par frame) ou coûte trop cher en accès aux frames | Faible | Élevé | SP-0 et SP-2 utilisent déjà MRUK via SRC-1 ; repli sur Camera2 (NG-07) avec reconstruction de la pose |
| RISK-06 | Charge CPU ou thermique sur le casque (encodage, tracking, caméras, relecture de profondeur) | Moyenne | Moyen | Sélection avant encodage, SP-4, réduction de cadence, encodage matériel en dernier recours |
| RISK-07 | Débit Wi-Fi insuffisant ou instable | Moyenne | Moyen | Flux best effort avec rattrapage (ADR-012), routeur dédié 5 GHz |
| RISK-08 | Changements fréquents du SDK Meta, de MRUK et du firmware | Élevée | Moyen | Versions figées (M0), tests de non-régression sur casque ; SRC-1 a déjà dû migrer de Camera2 vers MRUK `[SOURCE]` |
| RISK-09 | L'entraînement incrémental ne tient pas la cible live | Moyenne | Moyen | Résolution réduite en live, nombre de vues limité, GPU dédié |
| RISK-10 | Licences (poids de modèles feed-forward, 3DGS original) | Moyenne | Moyen | Revue de licences avant intégration, préférer gsplat/nerfstudio |
| RISK-11 | Paires gauche/droite insuffisamment synchrones pour l'option E | Moyenne | Faible | SP-2 ; l'option E est alors écartée, les autres options n'en dépendent pas |
| RISK-12 | Crash à la fermeture après usage de la caméra MRUK, signalé chez SRC-1 `[SOURCE]` | Moyenne | Faible | `mote_stop` vide et ferme le fichier avant l'arrêt des caméras ; test de fermeture |
| RISK-13 | Recentrage ou perte de tracking en cours de scan | Moyenne | Moyen | Événements dédiés, découpage en segments (9.4), consigne opérateur (section 12) |
| RISK-14 | La lecture CPU des images par `GetColors()` est trop coûteuse en configuration nominale `[DOC]` | Moyenne | Moyen | SP-4 ; replis : relecture asynchrone de la texture GPU, sous-échantillonnage pour la sélection et lecture pleine résolution des seules paires retenues, baisse de cadence |
| RISK-15 | Distorsion résiduelle non modélisée (pas de coefficients fournis `[DOC]`) | Moyenne | Moyen | SP-2 (H-11), calibration damier, ou optimisation de la distorsion à l'entraînement |

---

## 17. Questions ouvertes

- **Q-02** Quelles sont la résolution et la cadence réelles de la profondeur sur 3S ? Non documentées, à lire à l'exécution. (SP-3) Côté caméras : 1280x1280 à 60 Hz au plus `[DOC]`, à confirmer sur 3S par `GetSupportedResolutions()`. (SP-0)
- **Q-03** Les coefficients de distorsion ne sont pas exposés par MRUK `[DOC]`. Les images sont-elles rectifiées, ou faut-il une calibration damier ? (SP-2, H-11)
- **Q-06** Quelle stratégie d'entraînement incrémental retenir ? (revue de littérature, expériences en M4)
- **Q-07** Faut-il viser une v1.5 avec retour du splat ou de sa couverture vers le casque ? (décision produit)
- **Q-08** Matériel PC cible (GPU, VRAM) pour le live ? (inventaire)
- **Q-09** Contraintes de distribution : usage interne ou publication ? (décision produit, impact sur les licences)
- **Q-11** Quelle horloge se cache derrière le `DateTime` du `Timestamp` MRUK, et à quel instant de l'exposition se réfère-t-il ? Non documenté. (lecture du code C# de MRUK, SP-2)
- **Q-12** Obturateur rolling ou global sur les caméras passthrough ? Les deux caméras sont-elles synchronisées matériellement ? Non documenté. (SP-2)
- **Q-13** Peut-on interroger la pose du casque à un instant passé donné depuis Unity, pour remplacer l'interpolation par une requête exacte ? Rien trouvé dans la doc publique ; MRUK le fait en interne pour `GetCameraPose()`. (lecture du code C# de MRUK)
- **Q-14** Quelle différence de qualité de profondeur entre Quest 3 et 3S ? Non documenté par Meta. (SP-3, idéalement sur les deux casques)

Questions closes : Q-01 (caméras passthrough et profondeur sont supportées sur Quest 3S `[DOC]`), Q-04 (chemin zéro-copie vers MediaCodec, sans objet depuis ADR-003), Q-05 (reformulée en Q-11), Q-10 (intégrée à SP-4).

---

## 18. Licences, conformité, sécurité

### 18.1 Licences

- QuestRealityCapture et OpenQuestCapture : MIT. Conserver la mention de copyright pour tout extrait réutilisé (ADR-001). `[SOURCE]`
- Meta XR SDK, MRUK : les deux projets rappellent de respecter les licences de Meta lors de la redistribution. `[SOURCE]` À relire avant toute distribution.
- gsplat, nerfstudio, libjpeg-turbo, bibliothèques MCAP : licences permissives. `[CONNU]` À confirmer avant intégration. `[A VERIFIER]`
- Poids des modèles feed-forward (VGGT, MASt3R, etc.) : licences potentiellement non commerciales. `[A VERIFIER]`
- Dataset Meta Quest Ego : accès gated, conditions à respecter. `[SOURCE]`

### 18.2 Sécurité du transport et données

- Un scan d'intérieur peut contenir des informations sensibles ou des personnes. Le flux et les fichiers sont à traiter comme des données privées.
- Les images des caméras passthrough sont des « Device User Data » au sens de la politique d'usage des données développeur de Meta `[DOC]` : à relire avant toute distribution (Q-09).
- Les règles de sécurité du flux (jeton partagé, absence de chiffrement en v1, TLS avant tout réseau non maîtrisé) sont dans la spec ank `SPEC-9df2`.
- Définir une politique de conservation et de suppression des sessions, sur le casque (où les fichiers s'accumulent, ADR-012) comme sur le PC.

---

## 19. Glossaire

- **3DGS** : 3D Gaussian Splatting, représentation de scène par un ensemble de Gaussiennes 3D optimisées par rendu différentiable.
- **COLMAP** : outil de Structure-from-Motion et Multi-View Stereo.
- **c2w** : matrice caméra vers monde (`world_from_camera`).
- **HMD** : casque (head-mounted display).
- **MCAP** : format de conteneur de données horodatées multi-canaux.
- **MRUK** : Mixed Reality Utility Kit de Meta.
- **Keyframe** : image retenue pour la reconstruction ; dans mote, les keyframes vont par paires.
- **Paire** : images gauche et droite d'un même instant.
- **Hold-out** : vues exclues de l'entraînement et réservées à l'évaluation.
- **Rattrapage** : renvoi, depuis le fichier du casque, des messages absents du flux live.
- **REF** : SfM complet servant de référence de mesure (13.3).
- **Floaters** : artefacts de Gaussiennes isolées flottant dans le volume.
- **Sim(3)** : transformation de similarité (rotation, translation, échelle).
- **TSDF** : Truncated Signed Distance Function, fusion volumétrique de profondeur.

---

## 20. Annexes

### 20.1 Arborescence de dépôt proposée

```
mote/
  SPEC.md                   contexte (ce document)
  .ank/                     ADR, specs et tâches (via la CLI ank)
  proto/                    schémas protobuf
  core/                     workspace Rust
    mote-core/              sélection, files, orchestration
    mote-codec/             JPEG
    mote-mcap/              écriture MCAP
    mote-net/               transport live et rattrapage
    mote-capi/              API C + header généré
  hosts/
    unity/                  package UPM (C#)
  pc/
    mote/                   paquet Python
      ingest/
      train/
      eval/
      tools/
  docs/
    spikes/                 rapports SP-0 à SP-5
```

### 20.2 Liste de vérification du réviseur

- Chaque `[A VERIFIER]` a une méthode et un responsable.
- Chaque FR/NFR figure dans la matrice 15.2.
- Les chiffres ont une méthode de mesure.
- Aucune formule de conversion de repère n'est considérée comme acquise.
- Les décisions ADR ont des critères de remise en cause réalistes.
- Les work packages sont indépendants dans la mesure du possible, et leurs dépendances sont explicites.
- Les risques ont une mitigation concrète.

### 20.3 Références

- https://github.com/t-34400/QuestRealityCapture
- https://github.com/samuelm2/OpenQuestCapture
- https://github.com/t-34400/metaquest-3d-reconstruction
- https://github.com/AdrianoVM/QuestRoomScan
- https://github.com/fladirm/QuestInfiniteScan
- https://radiancefields.com/openquestcapture-for-quest-3-and-3s-capture
- https://huggingface.co/datasets/Oceanveo/meta-quest-ego
- https://github.com/cvg/NoPoSplat
- https://github.com/thinhlpg/AnySplat
