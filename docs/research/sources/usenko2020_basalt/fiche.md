---
citekey: usenko2020_basalt
mineru_doc: a9d3337
type: article de revue   # IEEE Robotics and Automation Letters (RA-L) 2020, version arXiv 1904.06504v3
statut: fiche complète
tags: [vio, vi-slam, basalt, fenêtre-glissante, marginalisation, first-estimate-jacobians, non-linear-factor-recovery, bundle-adjustment, klt, orb, euroc, stéréo, imu, cpu-only, temps-réel, gravité, piste-mote]
---

# Visual-Inertial Mapping with Non-Linear Factor Recovery (système « Basalt »)

**Référence :** Vladyslav Usenko, Nikolaus Demmel, David Schubert, Jörg Stückler, Daniel Cremers (2020). *Visual-Inertial Mapping with Non-Linear Factor Recovery.* IEEE Robotics and Automation Letters (RA-L), 2020 (selon le brief ; le paper.md ne porte que l'en-tête « arXiv:1904.06504v3 [cs.CV] 30 May 2020 », `page:1`). arXiv [1904.06504](https://arxiv.org/abs/1904.06504) · code et vidéo : https://vision.in.tum.de/research/vslam/basalt (`page:2`). TUM (Usenko, Demmel, Schubert, Cremers) et MPI Tübingen (Stückler) (`page:1`). DOI : non rapporté dans le paper.md.
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Système VIO stéréo + IMU à **deux couches** : une odométrie en fenêtre glissante (KLT + bundle adjustment visuel-inertiel + marginalisation avec first-estimate Jacobians) qui tourne à ~7,8 ms par image sur CPU, et une couche de **mapping global** qui, au lieu de ré-intégrer l'IMU entre keyframes, **récupère des facteurs non linéaires** (pose relative + roll-pitch) à partir du prior de marginalisation du VIO et les combine à un BA par points ORB avec fermeture de boucle implicite ; meilleure ATE sur la majorité des séquences EuRoC, pour le VIO comme pour le mapping (`page:1`, `page:2`, `page:8`).

## Problème traité
- Le VIO classique optimise localement une petite fenêtre d'images et d'IMU : « This approach, however, is inevitably prone to drift in the estimates » (`page:1`).
- Pour une carte globalement cohérente, le BA ne garde que des keyframes espacées dans le temps ; or l'information inertielle « quickly degrades with the duration of the intervals and after several seconds of integration, it typically contains only little useful information » (`page:1`). Les systèmes qui préintègrent l'IMU entre keyframes (VI ORB-SLAM [19]) doivent limiter l'écart à **0,5 s en BA local et 3 s en BA global**, et estimer vitesses et biais à chaque keyframe, mal contraints par la vision seule (`page:2`).
- Un BA naïf sur toutes les images à cadence caméra serait « computationally infeasible » (`page:1`).
- Question : comment transférer l'information visuelle-inertielle accumulée à haute cadence par le VIO vers une optimisation globale à basse cadence, sans vitesses ni biais dans l'état global, tout en gardant la carte alignée sur la gravité ?

## Méthode / contributions
**Couche 1 — VIO en fenêtre glissante (Sec. IV)**
- **Suivi KLT** : coins FAST détectés sur une grille (cellules de 50 px, un point par cellule vide), suivis par flot optique épars pyramidal, approche inverse-compositionnelle, warp estimé dans **SE(2)** par patch, norme LSSD (locally-scaled SSD) invariante à l'échelle d'intensité (moins coûteuse que ZNCC) ; filtrage des outliers par suivi aller-retour (`page:3`, `page:7`). Résultat : **80–120 points suivis** à tout instant sur EuRoC (`page:7`).
- **État optimisé** s = {s_k, s_f, s_l} : poses IMU de *n* vieilles keyframes (pose seule), poses + vitesses + biais des *m* images récentes, et landmarks (`page:3`). Réglage : **7 keyframes + 3 états temporels** (`page:7`). Seules les keyframes hébergent des landmarks ; une nouvelle keyframe est créée si **< 70 %** des points KLT sont reliés à la carte locale (`page:4`, `page:7`).
- **Landmarks** relatifs à la keyframe hôte, paramétrés par un vecteur unitaire (projection stéréographique à 2 paramètres, éq. 7, sans trigonométrie) + **distance inverse** ; la formulation reste stable quand d → 0 (`page:4`).
- **Erreurs** : reprojection (éq. 8) + **préintégration IMU** à la Forster et al. [8] avec biais fixés sur l'intervalle et correction linéaire (éq. 10–21) + prior de marginalisation (éq. 22), résolu par Gauss-Newton (`page:4`, `page:5`).
- **Marginalisation partielle** par complément de Schur sur le Markov blanket linéarisé (éq. 23–25) ; deux cas : on marginalise la plus vieille non-keyframe (en abandonnant ses facteurs de reprojection comme cible) ou, si une nouvelle keyframe est créée, les vitesses/biais de celle-ci plus une vieille keyframe et ses landmarks (`page:5`, Fig. 5 `page:6`). **First-estimate Jacobians** [10] pour préserver les espaces nuls (yaw, position absolue) du prior (`page:5`).
- Les auteurs revendiquent que ce VIO « outperforms the state-of-the-art methods in terms of trajectory accuracy on the majority of the evaluated sequences », grâce à la combinaison soignée « patch tracking, landmark representation, first-estimate Jacobians, marginalization scheme » (`page:2`).

**Couche 2 — Mapping visuel-inertiel par récupération de facteurs non linéaires (Sec. V)**
- Quand une keyframe sort de la fenêtre VIO, on sauvegarde la linéarisation de son Markov blanket, on marginalise tout sauf les **poses de keyframes**, ce qui donne un facteur dense reliant toutes les keyframes de la fenêtre (Fig. 6, `page:6`).
- **NFR** (Mazuran et al. [15]) : approximation de la gaussienne dense N(µ_o, H_o⁻¹) par un graphe de facteurs épars, en minimisant la divergence KL (éq. 27) ; solution fermée pour les matrices d'information H_i = ({J_r Σ_o J_rᵀ}_i)⁻¹ si J_r est de rang plein (éq. 30) (`page:6`, `page:7`).
- Facteurs définis : **pose relative** SE(3) entre la keyframe retirée et chaque autre keyframe (éq. 31), **roll-pitch** (éq. 32, composantes xy de la direction de gravité dans le repère keyframe), position absolue (éq. 33) et yaw (éq. 34). Les deux derniers (4 DoF inobservables du VIO) ne portent que le prior initial et sont **abandonnés** ; seuls pose relative + roll-pitch entrent dans l'énergie globale (éq. 35) (`page:7`).
- **BA global** : points **ORB** détectés et appariés entre keyframes (distincts des points KLT pour avoir des observations statistiquement indépendantes) + facteurs récupérés (éq. 26) ; fermetures de boucle « implicitly » par appariement de keypoints ; l'état global ne contient que les poses de keyframes et les nouveaux landmarks, **sans vitesses ni biais** (`page:6`).
- Résultat qualitatif : carte globalement cohérente **alignée sur la gravité**, et poses de keyframes récupérées même sur les segments où aucun appariement ORB n'est possible (`page:7`, Fig. 1 `page:1`).

## Résultats chiffrés
| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| Dataset | **EuRoC** [5] uniquement, 10 séquences MH 01–05, V1 01–03, V2 01–02 ; **V2 03 exclue** (> 400 images manquantes sur une caméra) | `page:7`, `page:8` |
| Métrique | **RMS ATE** en mètres après alignement sur la vérité terrain | `page:7` |
| ATE VIO stéréo (proposé) | MH 01 **0,07** · MH 02 0,06 · MH 03 0,07 · MH 04 0,13 · MH 05 0,11 · V1 01 0,04 · V1 02 0,05 · V1 03 0,10 · V2 01 0,04 · V2 02 0,05 m | Table I, `page:8` |
| VIO concurrents (ATE m) | VI DSO mono : 0,06 / 0,04 / 0,12 / 0,13 / 0,12 / 0,06 / 0,07 / 0,10 / 0,04 / 0,06 · OKVIS stéréo : 0,23 / 0,15 / 0,23 / 0,32 / 0,36 / 0,04 / 0,08 / 0,13 / 0,10 / 0,17 · **VINS-Fusion stéréo** : 0,24 / 0,18 / 0,23 / 0,39 / 0,19 / 0,10 / 0,10 / 0,11 / 0,12 / 0,10 · VINS-Fusion mono : 0,18 / 0,09 / 0,17 / 0,21 / 0,25 / 0,06 / 0,09 / 0,18 / 0,06 / 0,11 · IS-VIO stéréo : 0,06 / 0,06 / 0,10 / 0,24 / 0,19 / 0,06 / 0,10 / 0,26 / 0,08 / 0,21 | Table I, `page:8` |
| Bilan VIO | meilleur sur **8 séquences sur 10** ; plus proche concurrent VI DSO meilleur sur 5 (ex æquo comptés) | `page:7` |
| ATE mapping stéréo KF (proposé) | MH 01 0,08 · MH 02 0,06 · MH 03 0,05 · MH 04 **0,10** · MH 05 **0,08** · V1 01 0,04 · V1 02 0,02 · V1 03 0,03 · V2 01 0,03 · V2 02 **0,02** m | Table I, `page:8` |
| Mapping concurrents | VI ORB-SLAM mono KF : 0,07 / 0,08 / 0,09 / **0,22** / 0,08 / 0,03 / 0,03 / **X** / 0,03 / 0,04 · VI SLAM [12] stéréo KF : 0,11 / 0,09 / 0,19 / 0,27 / 0,23 / 0,04 / 0,05 / 0,11 / 0,10 / 0,18 | Table I, `page:8` |
| Ablation facteurs | BA pur (ORB seul) : 0,09 / 0,08 / 0,05 / 0,27 / 0,16 / 0,04 / 0,03 / **X** / 0,04 / 0,04 · BA + facteurs à poids identité : 0,08 / 0,07 / **X** / 0,34 / 0,15 / 0,04 / 0,03 / 0,56 / 0,05 / 0,04 → les poids récupérés par NFR apportent précision **et** robustesse (deux échecs évités) | Table I, `page:8` |
| Fréquence / temps par image (VIO) | **7,83 ms** en moyenne par image stéréo (max 9,4 ms sur MH 02, min 5,5 ms sur V1 03) ; une pose par image suivie | Intel **E5-1620, 4 cœurs / 8 threads**, implémentation « highly parallel », CPU seul, pas de GPU (`page:8`) |
| Keyframes | **11,5 %** des images en moyenne deviennent keyframes | `page:8` |
| Temps mapping | **52,8 ms par keyframe** = extraction de facteurs 3,6 + détection de keypoints 6,4 + appariement/triangulation 23,1 + optimisation (10 itérations) 19,7 | Table II, `page:8` |
| Séquence complète | MH 05 : 2 273 images stéréo, 114 s → **19,2 s de VIO + 9,7 s de mapping**, « around 4x faster than real-time playback » (≈ 20 Hz caméra, calculé : 2273/114) | `page:8` |
| Taille de l'état global | **2,5× plus petit** qu'une intégration IMU naïve (pas de vitesses ni de biais) | `page:8` |
| Dérive | non rapportée en tant que telle (seule l'ATE après alignement) | — |
| Mémoire | non rapportée | — |
| Latence | non rapportée (temps de calcul seulement) | — |
| TUM-VI, ROVIO, VINS-Mono | **non rapportés dans ce papier** (comparaison limitée à VI DSO, OKVIS, VINS-Fusion, IS-VIO, VI SLAM [12], VI ORB-SLAM) | `page:8` |

## Ce que ça dit du tracking du Quest
- **Même famille d'estimateur que ce qu'on suppose pour Insight** : VI-SLAM à landmarks épars, fenêtre glissante avec marginalisation (fixed-lag smoother) plutôt que filtre, IMU préintégrée, keyframes et carte globale optimisée en arrière-plan. Le papier décrit explicitement la raison de préférer le lissage au filtre (relinéarisation possible, `page:2`), argument qui vaut aussi pour un casque. Le dossier Insight ne dit pas si Meta utilise un filtre ou une fenêtre glissante : Basalt est le candidat « optimisation » de la comparaison.
- **Architecture deux couches = ce que fait un casque** : VIO à cadence caméra pour la pose immédiate (ici 7,8 ms/image), et carte globale/fermeture de boucle à cadence keyframe (11,5 % des images) en tâche asynchrone. C'est le schéma « odométrie locale + carte persistante corrigée en arrière-plan » d'Insight et des trajectoires open loop / closed loop de Project Aria (voir [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md)).
- **Différences** : Basalt est **stéréo 2 caméras + 1 IMU** (le multi-caméras est renvoyé en travaux futurs, `page:8`), sans relocalisation explicite ni carte persistante entre sessions (fermeture de boucle implicite par ORB seulement, `page:6`), sans prédiction de pose pour masquer la latence, sans DSP (CPU x86 4 cœurs). Le Quest ajoute 4 caméras monochromes, une carte persistante et une prédiction à 1 kHz.
- **Ce que ça implique pour la pose que mote récupère** : (1) la pose temps réel d'un VIO de ce type est une pose **fenêtre glissante avec linéarisation figée** (first-estimate Jacobians) : localement très précise (4–13 cm ATE sur des séquences de 100+ m avec un drone, Table I `page:8`) mais qui dérive sans fermeture de boucle (`page:5`) ; (2) roll et pitch sont **observables** grâce à la gravité (facteurs roll-pitch, `page:7`), yaw et position absolue ne le sont pas : le repère MRUK est arbitraire en yaw/translation mais aligné sur la gravité ; (3) la pose de keyframe après BA global est meilleure que la pose VIO (MH 04 : 0,13 → 0,10 m ; V1 03 : 0,10 → 0,03 m, `page:8`) : si le casque ré-optimise sa carte en arrière-plan, les poses « vues » par mote à l'instant t et celles de la carte finale peuvent différer de quelques cm.
- **Mise en garde** : le lien « Basalt conçu pour un matériel de type casque » et l'évaluation sur **TUM-VI** (rig stéréo + IMU tenu en main) ne figurent **pas** dans ce papier ; ils viennent du papier du dataset TUM-VI (Schubert et al., IROS 2018, non ingéré). Ne pas citer cette fiche pour cela.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Référence de base pour « VIO par fenêtre glissante avec marginalisation » ; formulation complète et compacte (préintégration, Schur, FEJ, NFR) utile pour expliquer en quoi Insight diffère d'un filtre MSCKF ; comparaison chiffrée avec OKVIS, VINS-Fusion, VI DSO, VI ORB-SLAM sur EuRoC (`page:8`) |
| 2. Poses pour 3DGS (piste mote, H-01) | Donne un **ordre de grandeur** de ce qu'un VIO open-source atteint sans GPU : 4–13 cm ATE sur drone, 2–10 cm après BA global (`page:8`), à mettre en regard des 4–6 mm médians Quest vs COLMAP de SP-0 (pièce, mouvement humain lent). Montre que l'alignement gravité est gratuit en VI (utile pour initialiser le repère 3DGS) et que le raffinement global des keyframes change les poses de plusieurs cm : argument pour le raffinement de poses à l'entraînement |
| 3. Temps réel et contraintes embarquées | 7,83 ms/image stéréo + 52,8 ms/keyframe sur un Xeon 4 cœurs, sans GPU (`page:8`) : borne CPU réaliste pour un VIO d'optimisation ; état global 2,5× plus petit grâce à NFR = levier de coût directement transférable à un casque ; aucune mesure mobile/ARM/DSP |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole standard : RMS ATE après alignement, EuRoC 10 séquences, séparation VIO (toutes les images) / mapping (keyframes), ablation des facteurs (`page:7`, `page:8`) ; exclusion documentée de V2 03 ; timings normalisés par keyframe (Table II) — modèle pour comparer les poses Quest à une vérité terrain |

## Pour (vis-à-vis de notre problématique)
- Code **open source** avec vidéo (`page:2`), base de nombreux travaux ultérieurs ; VIO stéréo CPU seul, temps réel ×4 (`page:8`).
- Démonstration propre qu'une **compression probabiliste** de l'information VIO (facteurs NFR pondérés) bat à la fois la préintégration IMU entre keyframes (VI ORB-SLAM) et le pose-graph à poids identité (`page:8`).
- Explique la structure d'observabilité d'un VI-SLAM (roll/pitch observables, yaw/position non, `page:7`) : directement utile pour interpréter le repère des poses MRUK.
- Table I lisible et complète (10 séquences, 13 méthodes) : réutilisable telle quelle comme tableau d'état de l'art du rapport.

## Contre / limites
- **Un seul dataset (EuRoC, drone)**, pas de séquence tenue en main ni de casque dans ce papier ; TUM-VI et le rig type HMD ne sont pas évalués ici (`page:7`).
- Pas de VINS-Mono, ROVIO, ni de méthode à relocalisation dans la comparaison (`page:8`).
- Pas de mesure de **latence**, de **mémoire**, d'énergie ; CPU desktop (E5-1620) seulement (`page:8`).
- Pas de carte persistante, pas de relocalisation entre sessions, pas de multi-caméras (travaux futurs, `page:8`).
- Robustesse du mapping dépendante des appariements ORB (un échec « X » du BA pur sur V1 03, `page:8`) ; fermeture de boucle implicite non détaillée.
- Le nom « Basalt » n'apparaît que dans l'URL du code (`page:2`).

## Idées à creuser pour mote
- *Hypothèse (H-01)* : utiliser Basalt comme **estimateur de référence ouvert** sur les séquences mote (images passthrough + IMU Quest si accessible, sinon sur un rig stéréo équivalent) pour situer les poses MRUK entre « VIO open-source » et « COLMAP », en plus de SP-0.
- *Hypothèse* : exploiter la structure NFR comme **pondération des poses** dans l'entraînement 3DGS : les matrices d'information H_ij (éq. 30, `page:7`) donnent une incertitude par pose ; le raffinement de poses à l'entraînement pourrait être contraint par ces facteurs (pose relative + roll-pitch) plutôt que libre.
- *Hypothèse* : comme la couche globale de Basalt ré-optimise les keyframes de plusieurs cm (`page:8`), prévoir dans mote un mécanisme qui **ré-ingère les poses corrigées** (si MRUK les expose) plutôt que de figer la pose au moment de la capture.
- *Hypothèse* : critère de sélection de keyframes de Basalt (< 70 % de points reliés, `page:7`) comme critère de **sélection des images** envoyées au PC d'entraînement 3DGS (11,5 % des images suffisent au mapping, `page:8`).
- Vérifier dans les fiches [kuo2020_multicam-slam](../kuo2020_multicam-slam/fiche.md) et [eckenhoff2019_multicam-vins](../eckenhoff2019_multicam-vins/fiche.md) comment l'extension multi-caméras annoncée en travaux futurs (`page:8`) est réalisée, pour se rapprocher des 4 caméras du Quest.

## Citations clés
> « Commonly, the optimization of camera trajectory and map is performed locally on a small window of recent camera frames and IMU measurements. This approach, however, is inevitably prone to drift in the estimates. » (`doc:a9d3337/tier:standard/page:1`)

> « Unlike other state-of-the-art systems that use preintegrated IMU measurements also for mapping, we subsume high-frame rate visual-inertial information in non-linear factors extracted from the marginalization prior of the VIO layer. This results not only in a smaller optimization problem but also in better pose estimates in the resulting gravity aligned map. » (`doc:a9d3337/tier:standard/page:2`)

> « Since yaw and absolute position are 4 unobservable states of the VIO, the only information we have there comes from the initial prior on the start pose. As we do not need this information for the global map we drop yaw and absolute position factors, and only take relative pose and roll-pitch factors for the map optimization. » (`doc:a9d3337/tier:standard/page:7`)

> « For the VIO the average time per frame on the EuRoC sequences is 7.83 ms (largest: 9.4 ms on MH 02; smallest: 5.5 ms in V1 03). On average 11.5% of the frames are selected as keyframes and proceed to the mapping stage. » (`doc:a9d3337/tier:standard/page:8`)

> « Integrating information from other sensor modalities or extending the system for multi-camera settings are interesting directions for future research. » (`doc:a9d3337/tier:standard/page:8`)

## Liens
- Papiers liés :
  - [VINS-Fusion](../qin2019_vins-fusion/fiche.md) — comparé directement en Table I (mono et stéréo), et cité pour l'optimisation 4 DoF (roll/pitch fixés) dont Basalt se distingue par des facteurs probabilistes (`page:2`, `page:8`).
  - [VINS-Mono](../qin2018_vins-mono/fiche.md) — même famille (fenêtre glissante + marginalisation + préintégration) ; non comparé ici.
  - [ORB-SLAM](../murartal2015_orb-slam/fiche.md) / [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — VI ORB-SLAM [19] est la baseline de mapping battue sur MH 04/05 ; ORB-SLAM3 (postérieur) reprend la préintégration entre keyframes.
  - [OpenVINS](../geneva2020_openvins/fiche.md) — alternative filtre MSCKF ; le §II de Basalt explique la limite des filtres (point de linéarisation figé, `page:2`).
  - [Kimera](../rosinol2020_kimera/fiche.md) — autre VIO d'optimisation + pose-graph ; comparer les stratégies de marginalisation.
  - [Multi-camera SLAM](../kuo2020_multicam-slam/fiche.md), [Multi-camera VINS](../eckenhoff2019_multicam-vins/fiche.md) — extension multi-caméras annoncée en travaux futurs (`page:8`).
  - [Benchmark VIO](../delmerico2018_vio-benchmark/fiche.md) — comparaison indépendante des mêmes systèmes (OKVIS, VINS, ROVIO…) sur matériel embarqué.
  - [Project Aria](../engel2023_project-aria/fiche.md) — VIO embarqué Meta, trajectoires open loop / closed loop analogues aux couches VIO / mapping de Basalt.
  - [Dossier Oculus Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) — ce que le Quest fait réellement, pour la section « tracking du Quest ».
  - [3DGS](../kerbl2023_3dgs/fiche.md) — consommateur des poses ; H-01 (raffinement des poses à l'entraînement).
  - [Survey NeRF/GS-SLAM](../tosi2024_nerf-gs-slam-survey/fiche.md), [Photo-SLAM](../huang2024_photo-slam/fiche.md) — SLAM dont le front-end est de même nature, couplé au rendu neural.
