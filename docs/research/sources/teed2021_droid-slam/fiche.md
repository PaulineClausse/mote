---
citekey: teed2021_droid-slam
mineru_doc: 0e15f20
type: conférence   # NeurIPS 2021
statut: fiche complète
tags: [slam, slam-dense, deep-slam, bundle-adjustment, dba, raft, gru, monoculaire, stéréo, rgb-d, sans-imu, euroc, tartanair, tum-rgbd, eth3d, gpu, rtx-3090, ate, orb-slam3, poses-pour-3dgs, piste-mote]
---

# DROID-SLAM: Deep Visual SLAM for Monocular, Stereo, and RGB-D Cameras

**Référence :** Zachary Teed, Jia Deng (2021). *DROID-SLAM: Deep Visual SLAM for Monocular, Stereo, and RGB-D Cameras.* 35th Conference on Neural Information Processing Systems (NeurIPS 2021), Princeton University. arXiv [2108.10869v2](https://arxiv.org/abs/2108.10869) (2 févr. 2022) · DOI : non rapporté dans le papier · code : [github.com/princeton-vl/DROID-SLAM](https://github.com/princeton-vl/DROID-SLAM) (`doc:0e15f20/tier:standard/page:1`)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
SLAM visuel **dense et appris de bout en bout**, purement caméra (mono, stéréo ou RGB-D, **jamais d'IMU**), qui remplace l'extraction/appariement de points par des volumes de corrélation à la RAFT et raffine itérativement poses et profondeurs par pixel au moyen d'une couche **Dense Bundle Adjustment (DBA)** différentiable ; entraîné une seule fois sur TartanAir synthétique en monoculaire, il réduit l'ATE d'ORB-SLAM3 de 43 % en mono (2,2 cm de moyenne sur EuRoC, zéro échec) et de 71 % en stéréo (2,4 cm vs 8,4 cm), mais au prix de **deux RTX 3090** pour tenir 20 fps et de 24 Go de mémoire GPU pour les longues séquences (`page:1`, `page:2`, `page:8`, `page:9`, `page:13`).

## Problème traité
- Les SLAM classiques à optimisation par moindres carrés (ORB-SLAM3, DSO…) sont précis mais « lack the robustness demanded for many real-world applications » : pertes de suivi, divergence de l'optimisation, accumulation de dérive (`page:1`).
- Les SLAM/VO appris existants (DeepV2D, BA-Net, DeepFactors, TartanVO…) sont parfois plus robustes mais « fall far short of the accuracy of their classical counterparts on common benchmarks » ; ils ne couvrent que 2 à une douzaine d'images, sans fermeture de boucle ni BA global (`page:1`, `page:3`).
- Entrées considérées : uniquement des images (« visual SLAM, where sensor recordings come in the form of images captured from a monocular, stereo, or RGB-D camera ») ; l'IMU n'est mentionnée que comme capacité d'ORB-SLAM3, jamais utilisée ici (`page:1`).
- Les auteurs se placent entre les méthodes indirectes (points + descripteurs, erreur de reprojection) et directes (erreur photométrique) : ils utilisent toute l'image sans détection de points, mais minimisent une erreur **géométrique** de reprojection, « an easier optimization problem » qui évite les pyramides d'images (`page:3`).

## Méthode / contributions
- **État** : pour chaque image t, une pose G_t ∈ SE(3) et une carte d'**inverse de profondeur dense** d_t ∈ R^{H×W} ; un **graphe de trames** (V, E) de co-visibilité, reconstruit dynamiquement, avec ajout d'arêtes longue portée pour la fermeture de boucle (`page:3`, `page:4`).
- **Extraction de caractéristiques (RAFT)** : deux réseaux (feature + context), 6 blocs résiduels, 3 sous-échantillonnages, cartes à **1/8 de la résolution** ; dimension D = 128 (feature) et 256 (context) (`page:4`, `page:15`). Pour chaque arête (i, j), un **volume de corrélation 4D** toutes-paires (éq. 1), moyenné en une **pyramide à 4 niveaux**, interrogé par un opérateur de lookup à rayon r avec interpolation bilinéaire (`page:4`).
- **Opérateur de mise à jour** : ConvGRU 3×3 ; à chaque itération, les poses/profondeurs courantes donnent un champ de correspondance dense p_ij (éq. 3) qui sert à indexer les corrélations ; le flot induit par le mouvement et le résidu du BA précédent sont injectés en entrée ; un contexte global (moyenne spatiale de l'état caché) permet de rejeter les correspondances fausses dues aux objets mobiles (`page:4`, `page:5`). Le GRU prédit une **révision de flot** r_ij et une **carte de confiance** w_ij, un **facteur d'amortissement λ par pixel** (softplus) et un masque 8×8 d'upsampling de la profondeur (`page:5`).
- **Couche Dense Bundle Adjustment (DBA)** : minimise sur tout le graphe la distance de Mahalanobis entre correspondances révisées p*_ij et reprojections (éq. 4, Σ_ij = diag w_ij) ; un pas de **Gauss-Newton** avec paramétrisation locale, résolu par **complément de Schur** : la Hessienne est bloc-diagonale sur les profondeurs (C diagonale, inversée trivialement), λ ajouté au bloc profondeur (éq. 5). La couche est dans le graphe de calcul et on rétropropage à travers elle (`page:5`). Deux différences revendiquées vs BA-Net : profondeur **par pixel** (pas de base de profondeurs apprise) et erreur **géométrique** plutôt que photométrique (`page:2`).
- **Entraînement** : PyTorch + LieTorch ; les deux premières poses sont fixées aux vérités terrain pour supprimer la jauge (6 ddl + échelle) ; clips de **7 images** échantillonnés pour un flot moyen entre 8 et 96 px et un recouvrement > 50 % ; perte = flot induit + pose (Log_SE3), pondérée γ = 0,9 sur les itérations ; **250 k pas, batch 4, 384 × 512, 15 itérations déroulées, 1 semaine sur 4 RTX 3090**, uniquement TartanAir monoculaire (`page:5`, `page:6`, `page:7`).
- **Système SLAM à deux threads** : frontend (extraction, sélection de keyframes, BA local) et backend (BA global sur tout l'historique) asynchrones (`page:6`).
  - *Initialisation* : accumuler 12 images en ne gardant une image que si le flot > 16 px ; arêtes entre keyframes à ≤ 3 pas ; 10 itérations (`page:6`).
  - *Frontend* : nouvelle image reliée à ses 3 plus proches voisines (flot moyen), pose initialisée par un modèle de mouvement linéaire, puis suppression de la keyframe la plus redondante (ou la plus ancienne) (`page:6`).
  - *Backend* : graphe reconstruit à chaque itération à partir d'une matrice N × N de flot entre keyframes, arêtes ajoutées par flot croissant avec suppression des voisines à distance de Chebyshev ≤ 2 ; graphes de « thousands of frames and edges », volumes de corrélation recalculés à la volée (implémentation « memory efficient » de RAFT) (`page:6`).
  - *Inférence* : noyau CUDA sur mesure exploitant la structure bloc-creuse + Cholesky creux sur le bloc caméra réduit ; BA complet sur keyframes seulement, poses des non-keyframes par **BA mouvement-seul** ; évaluation sur la trajectoire complète (`page:7`).
- **Stéréo et RGB-D sans réentraînement** : RGB-D = terme supplémentaire pénalisant l'écart à la profondeur mesurée (profondeur toujours variable car le capteur est bruité) ; stéréo = même système avec deux fois plus d'images et pose relative gauche/droite fixée dans la DBA, arêtes inter-caméras (`page:7`).
- **Ablations** (validation TartanAir) : gain de la stéréo et de l'optimisation globale ; 5 keyframes retenues pour l'odométrie ; le contexte global aide ; **entraîner sans DBA (flot seul + BA au test) rend le système « unstable and prone to failure »** (`page:13`, `page:14`).

## Résultats chiffrés
| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| ATE EuRoC **mono** (11 séq.) | **0,022 m** en moyenne, 0 échec ; ORB-SLAM3 0,016–0,138 m, échoue sur V203 ; DSM 0,126 ; odométrie seule (sans BA global) 0,186 m | −82 % vs méthodes sans échec, −43 % vs ORB-SLAM3 sur ses 10/11 séquences réussies ; 320 × 512, une image sur deux (`page:8`, `page:9`) |
| ATE EuRoC **stéréo** | **0,024 m** moyenne ; ORB-SLAM3 0,084 (0,521 sur V203) ; VINS-Fusion 0,20–0,78 m ; SVO 0,159 | −71 % vs ORB-SLAM3 ; réseau entraîné en mono (`page:13`) |
| ATE TUM-RGBD freiburg1 (9 séq., **mono**) | **0,038 m** moyenne, 9/9 suivies ; ORB-SLAM3 réussit 4/9 (0,009–0,210) ; DeepFactors 0,233 ; DeepV2D 0,375 | −83 % vs DeepFactors, −90 % vs DeepV2D ; 240 × 320, une image sur deux (`page:9`) |
| TartanAir mono « Hard » (8 séq.) | ATE moy. **0,24** vs TartanVO 1,92, DeepV2D 5,03 ; ORB-SLAM échoue sur 2/8 | 8× / 20× moins d'erreur (`page:7`, `page:8`) |
| TartanAir, compétition ECCV 2020 | score **0,129 (mono) / 0,047 (stéréo)** vs SuperGlue+SuperPoint+COLMAP 0,340 / 0,119, VOLDOR+COLMAP 0,440 / 0,177, OV²SLAM 0,510 / 0,182 | RPE normalisée sur segments 5–40 m ; −62 % / −60 % ; les 2 premiers (COLMAP) sont « 40x slower than real-time », DROID 16× plus rapide qu'eux (`page:8`) |
| ETH3D-SLAM RGB-D | AUC **340,42 (train) / 207,79 (test)** vs BAD-SLAM 280,05 / 153,47, ORB-SLAM2 156,10 / 104,28 ; **30/32** séquences suivies vs 19/32 | sans fine-tuning, +35 % sur le 2e (`page:2`, `page:9`) |
| Fréquence (fps caméra) | **20 fps** EuRoC (320 × 512, une image sur deux) ; **30 fps** TUM-RGBD (240 × 320, une image sur deux) ; **8 fps** TartanAir (« unable to run in real-time ») | **2 × RTX 3090** : GPU 1 = tracking + BA local, GPU 2 = BA global + fermeture de boucle (`page:9`) |
| Temps par image | non rapporté (seulement les fps moyens ci-dessus) | — |
| Dérive | non chiffrée séparément ; ATE odométrie seule 0,186 m vs 0,022 m avec BA global sur EuRoC | (`page:8`) |
| Mémoire GPU | frontend : **8 Go** ; TUM-RGBD complet sur une **1080Ti** ; EuRoC, TartanAir, ETH3D (jusqu'à **5 000 images**) : **24 Go** (le backend stocke les cartes de caractéristiques de toutes les images) | « memory and resource requirements are currently the biggest limitation » (`page:9`) |
| CPU | non rapporté | — |
| Entraînement | 250 k pas, batch 4, 384 × 512, clips de 7 images, 15 itérations ; **1 semaine sur 4 RTX 3090** | TartanAir mono uniquement (`page:7`) |
| Latence | non rapportée | — |
| Qualité de la carte dense | **non évaluée** (« outside the scope of this work », domaine du MVS) | (`page:7`) |

## Ce que ça dit du tracking du Quest
- **Rien en commun sur les capteurs** : DROID-SLAM est caméra-seul, sans IMU, donc sans l'intégration inertielle à 1 kHz, la prédiction de pose et l'échelle métrique que donne un VI-SLAM. En mono il ne récupère la trajectoire qu'« up to a similarity transform » (`page:6`) ; en stéréo l'échelle vient de la baseline fixée dans la DBA (`page:7`, `page:13`). Oculus Insight obtient échelle et gravité de l'IMU et exploite 4 caméras monochromes grand angle ; DROID-SLAM gère nativement la stéréo (pose relative fixée, arêtes inter-caméras) mais le papier ne traite ni de plus de deux caméras ni de caméras à faible recouvrement (`page:7`).
- **Points communs structurels** : frontend/backend asynchrones (suivi local + BA global en arrière-plan), sélection de keyframes, fermeture de boucle par arêtes longue portée, BA mouvement-seul pour les images intermédiaires — c'est l'architecture « carte mise à jour en arrière-plan + localisation temps réel » que Meta décrit pour Insight, mais ici la carte est un ensemble de cartes de profondeur denses par keyframe, pas des landmarks épars (`page:4`, `page:6`, `page:7`).
- **Budget de calcul incompatible avec un casque** : 2 GPU desktop pour 20 fps à 320 × 512, 8–24 Go de mémoire, alors qu'Insight tourne sur un SoC mobile avec un ordre de grandeur de calcul en moins et un DSP (dossier Insight). Aucun chiffre CPU/latence n'est donné (`page:9`).
- **Robustesse aux cas difficiles** (TUM-RGBD : rolling shutter, flou de bougé, fortes rotations, où ORB-SLAM3 échoue 5/9) : DROID suit tout. Ce sont exactement les situations qu'un casque rencontre ; Insight les traite par l'IMU, DROID par l'apprentissage et la densité (`page:8`, `page:9`).
- **Implication pour mote** : les poses MRUK sortent d'un VI-SLAM épars temps réel ; DROID-SLAM montre qu'un BA dense sur PC peut atteindre ~2 cm d'ATE sur EuRoC sans IMU (`page:8`), soit un ordre de grandeur **au-dessus** de l'écart mesuré en SP-0 entre Quest et COLMAP (4–6 mm). Il n'est donc pas un meilleur « juge » que COLMAP pour nos poses ; il est surtout un candidat de **raffinement dense** de poses initialisées par le casque.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Référence du SLAM dense appris (2021) ; contraste net avec les VI-SLAM épars du casque : pas d'IMU, pas de landmarks, pas de DSP ; architecture frontend/backend comparable (`page:6`) |
| 2. Poses pour 3DGS (piste mote, H-01) | Produit par keyframe pose + **profondeur dense + confiance** (`page:5`, Fig. 5 `page:13`) : initialisation possible du nuage 3DGS sans COLMAP ; la DBA (Gauss-Newton, Schur, λ par pixel) est un **opérateur de raffinement de poses** réutilisable, exactement la brique « raffinement à l'entraînement » de H-01. Précision mono/stéréo 2,2–2,4 cm ATE sur EuRoC (`page:8`, `page:13`) |
| 3. Temps réel et contraintes embarquées | Contre-exemple : 2 × RTX 3090, 8–24 Go, 20 fps à 320 × 512 ; impossible sur casque ou sur notre portable Iris Xe ; nécessite le PC GPU emprunté (`page:9`) |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole ATE [m] sur EuRoC (11 séq. mono + stéréo), TUM-RGBD freiburg1, TartanAir (RPE normalisée 5–40 m), ETH3D (AUC erreur × taux d'échec) ; distinction « odométrie seule » vs « SLAM complet » (`page:7`–`page:9`, `page:13`) ; reconstruction dense **non** évaluée (`page:7`) |

## Pour (vis-à-vis de notre problématique)
- Un seul modèle, entraîné une fois en mono sur synthétique, généralise à 4 datasets réels et 3 modalités sans réentraînement (`page:2`).
- Zéro échec sur TartanAir, EuRoC, TUM-RGBD ; 30/32 sur ETH3D — robustesse supérieure à ORB-SLAM3 sur les séquences agressives (`page:2`, `page:9`).
- Sort une profondeur dense par keyframe avec carte de confiance : utile pour initialiser des Gaussiennes là où COLMAP ne donne que des points épars (`page:5`, `page:13`).
- Couche DBA différentiable formalisée (éq. 4–5, Jacobiens en annexe C) : transposable comme terme de raffinement de poses dans un entraînement 3DGS (`page:5`, `page:14`).
- Code public, noyau CUDA et Cholesky creux fournis (`page:1`, `page:7`).

## Contre / limites
- **Aucune fusion IMU** : pas d'échelle métrique en mono, pas de prédiction basse latence, pas de robustesse aux images sans texture ; incomparable au pipeline du casque sur ce point (`page:1`, `page:6`).
- **Matériel** : 2 GPU RTX 3090 pour 20 fps, 24 Go pour les séquences de 5 000 images, 8 fps sur TartanAir ; les auteurs eux-mêmes citent la mémoire et les ressources comme « the biggest limitation » (`page:9`).
- Résolution d'entrée réduite (320 × 512 ou 240 × 320) et **une image sur deux** sautée pour tenir les fps rapportés (`page:9`).
- Fréquence annoncée en « fps (camera hz) » moyens ; pas de latence, pas de temps par image, pas de CPU (`page:9`).
- Qualité de la carte dense jamais mesurée ; seule la trajectoire est évaluée (`page:7`).
- Entraînement coûteux : 1 semaine sur 4 RTX 3090 (`page:7`).
- Comparaison ORB-SLAM3 faite en visuel pur (sans IMU) ; la version visuelle-inertielle d'ORB-SLAM3, plus proche du casque, n'est pas dans les tableaux (`page:8`, `page:13`).
- Évalué sur caméras à 1 ou 2 vues ; rien sur les rigs multi-caméras à faible recouvrement type casque.

## Idées à creuser pour mote
- *Hypothèse (H-01, raffinement)* : initialiser DROID-SLAM avec les poses Quest (modèle de mouvement linéaire remplacé par la pose MRUK, premières poses fixées comme pour la jauge, `page:6`) et ne faire tourner que le **backend** (BA global dense) hors ligne sur le PC GPU : mesurer si l'ATE vs COLMAP descend sous les 4–6 mm de SP-0, et à quel coût (minutes vs 55–138 min de COLMAP).
- *Hypothèse* : utiliser les **cartes de profondeur dense + confiance** par keyframe comme initialisation des Gaussiennes (position, échelle) au lieu du nuage SfM, en masquant les pixels à faible confiance.
- *Hypothèse* : réécrire la DBA (éq. 4–5) comme terme de perte géométrique dans l'entraînement 3DGS, en parallèle du terme photométrique, pour le raffinement des poses casque.
- *Protocole* : reprendre la distinction « odométrie seule / SLAM complet » (0,186 m vs 0,022 m, `page:8`) pour quantifier ce que le BA global apporte par rapport aux poses brutes du casque sur nos captures.
- *Contrainte matérielle* : tester sur le PC GPU de l'école ; vérifier la mémoire (8 Go frontend minimum, 24 Go pour les séquences longues) avant de capturer des séquences longues. Pour une version légère sur GPU unique, voir le successeur [DPVO](../teed2023_dpvo/fiche.md).

## Citations clés
> « DROID-SLAM consists of recurrent iterative updates of camera pose and pixelwise depth through a Dense Bundle Adjustment layer. » (`doc:0e15f20/tier:standard/page:1`)

> « On EuRoC [2], with monocular input, we reduce error by 82% among methods with zero failures, and by 43% over ORB-SLAM3 considering only the 10 out of 11 sequences it succeeds on. With stereo input, we reduce error by 71% over ORB-SLAM3. » (`doc:0e15f20/tier:standard/page:2`)

> « Our system can run in real-time with 2 3090 GPUs. Tracking and local BA is run on the first GPU, while global BA and loop closure is run on the second. On EuRoC, we average 20fps (camera hz) by downsampling to 320 × 512 resolution and skipping every other frame. » (`doc:0e15f20/tier:standard/page:9`)

> « The SLAM frontend can be run on GPUs with 8GB of memory. […] Results on EuRoC, TartanAir and ETH-3D (where video can be up to 5000 frames) requires a GPU with 24GB memory. While memory and resource requirements are currently the biggest limitation of our system, we believe these can be drastically reduced by culling redundant computation and more efficient representations. » (`doc:0e15f20/tier:standard/page:9`)

> « We find that the SLAM system is unstable and prone to failure if the DBA is not used during training. » (`doc:0e15f20/tier:standard/page:13`)

## Liens
- Papiers liés :
  - [DPVO](../teed2023_dpvo/fiche.md) — successeur léger des mêmes auteurs (patchs épars au lieu de BA dense), répond directement à la limite mémoire/GPU.
  - [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — baseline classique principale (EuRoC mono/stéréo, TUM-RGBD) ; DROID la bat en visuel pur mais ne compare pas sa variante inertielle.
  - [ORB-SLAM](../murartal2015_orb-slam/fiche.md) — baseline des tableaux TartanAir et EuRoC.
  - [VINS-Fusion](../qin2019_vins-fusion/fiche.md) — présent dans le tableau stéréo EuRoC (`page:13`), nettement moins précis ici que DROID.
  - [Kimera](../rosinol2020_kimera/fiche.md) — cité parmi les SLAM indirects (`page:3`).
  - [VINS-Mono](../qin2018_vins-mono/fiche.md), [OpenVINS](../geneva2020_openvins/fiche.md), [Basalt](../usenko2020_basalt/fiche.md) — estimateurs visuels-inertiels du même axe, pour la comparaison « avec / sans IMU ».
  - [Benchmark VIO](../delmerico2018_vio-benchmark/fiche.md) — protocoles EuRoC et contraintes embarquées.
  - [Project Aria](../engel2023_project-aria/fiche.md) — VIO/SLAM Meta le plus proche du Quest, pour situer DROID par rapport à la pile du casque.
  - [Survey NeRF/GS-SLAM](../tosi2024_nerf-gs-slam-survey/fiche.md), [Photo-SLAM](../huang2024_photo-slam/fiche.md) — SLAM couplés à des représentations neuronales / Gaussiennes, suite logique de la DBA dense.
  - [3DGS](../kerbl2023_3dgs/fiche.md) — consommateur des poses ; la profondeur dense DROID peut remplacer le nuage SfM d'initialisation.
  - [Dossier Oculus Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) — ce que fait réellement le casque.
