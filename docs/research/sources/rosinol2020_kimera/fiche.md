---
citekey: rosinol2020_kimera
mineru_doc: b2c27e2
type: conférence   # IEEE ICRA 2020 ; version ingérée = arXiv 1910.02490v3 (4 mars 2020), 8 p.
statut: fiche complète
tags: [vio, vi-slam, stéréo, imu, pré-intégration, gtsam, isam2, fenêtre-glissante, smart-factors, pose-graph, pcm, fermeture-de-boucle, dbow2, maillage-delaunay, maillage-dense, tsdf, voxblox, sémantique, euroc, temps-réel, cpu, multithread, open-source, ros, localisation-poses, piste-mote]
---

# Kimera: an Open-Source Library for Real-Time Metric-Semantic Localization and Mapping

**Référence :** Antoni Rosinol, Marcus Abate, Yun Chang, Luca Carlone (2020). *Kimera: an Open-Source Library for Real-Time Metric-Semantic Localization and Mapping.* IEEE International Conference on Robotics and Automation (ICRA), 2020. arXiv [1910.02490](https://arxiv.org/abs/1910.02490) (v3, 4 mars 2020, 8 p.) · DOI non présent dans la version arXiv ingérée · code : github.com/MIT-SPARK/Kimera · vidéo : youtube.com/watch?v=-5XxXRABXJs (`doc:b2c27e2/tier:standard/page:1`). Affiliation : Laboratory for Information & Decision Systems (LIDS), MIT ; financement ARL DCIST, MIT Lincoln Laboratory, fondation « la Caixa » (`page:1`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Bibliothèque C++ open source de SLAM visuel-inertiel **métrique-sémantique** en quatre modules découplés — Kimera-VIO (stéréo + IMU, lisseur à fenêtre glissante iSAM2/GTSAM), Kimera-RPGO (graphe de poses robuste aux fausses boucles), Kimera-Mesher (maillage 3D par Delaunay en < 20 ms) et Kimera-Semantics (maillage global TSDF annoté) — qui tourne **en temps réel sur CPU**, fournit une pose à la cadence de l'IMU (> 200 Hz) et atteint les meilleures erreurs ATE sur EuRoC parmi les VIO ouverts comparés (`page:1`, `page:2`, `page:5`, `page:6`).

## Problème traité
- Les bibliothèques VIO/SLAM existantes (ORB-SLAM, VINS-Mono, OKVIS, ROVIO) ne fournissent que des poses et des points épars ; les systèmes de reconstruction métrique-sémantique (SLAM++, SemanticFusion, Mask-fusion, Voxblox++) exigent presque tous une caméra **RGB-D** et un **GPU**, alternent suivi et cartographie, et travaillent en voxels/surfels (`page:1`, `page:2`, Table I).
- Kimera vise à unifier VIO, optimisation de graphe de poses, maillage et sémantique 3D dans une seule pile **RGB + inertiel** (donc utilisable en intérieur et extérieur), **CPU seulement**, **robuste avec un minimum de réglage** (rejet d'outliers de bout en bout), et modulaire : « The modules can be run in isolation or in combination, hence Kimera can easily fall back to a state-of-the-art VIO or a full SLAM system » (`page:1`, `page:2`).
- Deux systèmes jugés les plus proches : XIVO (VIO EKF + carte d'objets) et Voxblox++ (RGB-D + odométrie roues + cartes maplab pré-construites) ; Kimera s'en distingue par (i) un VIO par optimisation très précis, (ii) un PGO robuste, (iii) un maillage léger (`page:2`).

## Méthode / contributions
### Architecture modulaire en 4 threads (Fig. 2)
Entrées : paires stéréo + IMU haute cadence ; sorties : (i) état à la cadence IMU, (ii) trajectoire globalement cohérente, (iii) plusieurs maillages (local rapide, global sémantique). « Kimera is heavily parallelized and uses four threads to accommodate inputs and outputs at different rates (e.g., IMU, frames, keyframes) » (`page:2`) :
1. **Thread 1 — front-end Kimera-VIO** : images stéréo + IMU → pistes de points et IMU pré-intégré ; publie aussi les **estimations d'état à la cadence IMU** (`page:2`).
2. **Thread 2 — back-end Kimera-VIO + Kimera-Mesher** : états optimisés et maillages per-frame / multi-frame à **faible latence (< 20 ms)** (`page:2`).
3. **Thread 3 — Kimera-RPGO** (plus lent) : détection de boucles, rejet d'outliers, trajectoire globale (`page:2`).
4. **Thread 4 — Kimera-Semantics** (plus lent) : stéréo dense + labels 2D → maillage métrique-sémantique global, calé sur les poses de Kimera-VIO (`page:2`, `page:3`).

### Kimera-VIO (stéréo + IMU, fenêtre glissante GTSAM)
- Estimateur MAP à keyframes de Forster et al. [45], en **lissage complet ou à retard fixe** (fixed-lag) selon l'horizon choisi ; « we typically use the latter to bound the estimation time » ; étendu au mono et au stéréo (`page:3`).
- **Front-end** : pré-intégration IMU sur variété ; coins **Shi-Tomasi** suivis par **Lucas-Kanade**, appariement stéréo gauche-droite, vérification géométrique mono (RANSAC 5 points) et stéréo (RANSAC 3 points), avec option RANSAC 2 points / 1 point en utilisant la rotation IMU. Détection, appariement stéréo et vérification ne se font **qu'aux keyframes** ; aux images intermédiaires, suivi seulement (`page:3`).
- **Back-end** : à chaque keyframe, facteurs IMU pré-intégrés + **facteurs de vision « structureless »** (smart factors) ajoutés à un lisseur à retard fixe résolu par **iSAM2 dans GTSAM** ; les points 3D sont triangulés par DLT puis éliminés analytiquement de l'état ; points dégénérés (derrière la caméra, parallaxe insuffisante) et outliers (grande erreur de reprojection) retirés avant élimination ; états hors horizon **marginalisés** (`page:3`).

### Kimera-RPGO (graphe de poses robuste)
- Détection de boucles par **DBoW2** (sac de mots), puis vérification géométrique mono + stéréo ; des outliers subsistent à cause de l'**aliasing perceptuel** (deux pièces identiques à deux étages) (`page:3`).
- Rejet d'outliers par **PCM** (Pairwise Consistent Measurement set maximization), adapté du multi-robot au cas mono-robot **en ligne** : arêtes d'odométrie (Kimera-VIO) et boucles stockées séparément ; (i) **test de cohérence avec l'odométrie** (la composition le long du cycle odométrie + boucle doit donner l'identité, test du χ²) ; (ii) test de cohérence par paires avec les boucles précédentes ; matrice d'adjacence construite **incrémentalement** (une ligne/colonne par nouvelle boucle) ; **clique maximale** [61] = plus grand ensemble cohérent ; optimisation Gauss-Newton dans GTSAM (`page:3`, `page:4`).

### Kimera-Mesher (maillage 3D rapide à partir des landmarks du VIO)
- **Maillage per-frame** : triangulation de **Delaunay 2D** sur les points suivis du keyframe courant, rétro-projetée en 3D avec les positions 3D estimées par le back-end ; option de texturer le maillage avec les labels 2D (`page:4`).
- **Maillage multi-frame** : fusion des maillages per-frame sur l'**horizon glissant du VIO** ; structure = liste de sommets + liste de triplets d'indices ; à chaque nouveau maillage on ajoute les sommets/triangles manquants, on **met à jour la position 3D de tous les sommets selon les dernières estimations du back-end**, puis on retire les sommets sortis de l'horizon. Si des surfaces planes sont détectées, des **facteurs de régularité** [47] sont ajoutés au back-end VIO → **couplage serré VIO ↔ maillage** (`page:4`).

### Kimera-Semantics (maillage global volumique)
- À chaque keyframe : **stéréo dense** (semi-global matching) → nuage 3D → **bundled raycasting** Voxblox (option « fast ») → TSDF → **marching cubes** (`page:4`).
- Annotation sémantique : labels 2D par pixel (réseau profond ou MRF, au choix) attachés aux points 3D, vecteur de probabilités par faisceau de rayons, mise à jour bayésienne par voxel restreinte à la distance de troncature (pas de mise à jour de l'étiquette « vide ») ; maillage « significantly more accurate than the multi-frame mesh […] but slower to compute (≈ 0.1s) » (`page:4`).

### Outils
Intégration continue Jenkins (compilation, tests unitaires, **évaluation automatique de Kimera-VIO et Kimera-RPGO sur EuRoC avec evo**), notebooks Jupyter (qualité des pistes, erreurs de pré-intégration), évaluation de la reconstruction 3D avec Open3D ; fonctionnement hors ligne sur datasets ou en ligne sous **ROS** (`page:2`, `page:4`).

## Résultats chiffrés
| Métrique | Valeur | Conditions (dataset, matériel) |
|---|---|---|
| ATE RMSE — Kimera-VIO (fixed-lag) | **0,05–0,35 m** selon séquence (MH_1 0,11 · MH_2 0,10 · MH_3 0,16 · MH_4 0,24 · MH_5 0,35 · V1_1 0,05 · V1_2 0,08 · V1_3 0,07 · V2_1 0,08 · V2_2 0,10 · V2_3 0,21) vs OKVIS 0,09–0,47 · MSCKF 0,10–1,13 · ROVIO 0,10–0,52 · VINS-Mono 0,08–0,32 | EuRoC, alignement **SE(3)** (pas Sim(3)), Kimera en **stéréo** vs concurrents **mono** (valeurs reprises de Delmerico 2018 [77] et de VINS-Mono [24]) (`page:5`, Table II) |
| ATE RMSE — Kimera-VIO (full smoothing) | 0,04–0,27 m (MH_1 0,04 · MH_4 0,27 · V1_1 0,06 · V2_3 0,19) vs SVO-GTSAM 0,03–0,16 avec **3 échecs** (V1_3, V2_2, V2_3) | EuRoC (`page:5`, Table II) |
| ATE RMSE — Kimera-RPGO (boucles) | **0,05–0,24 m** (MH_1 0,08 · MH_5 0,24 · V1_1 0,05 · V2_3 0,19) vs VINS-Mono avec boucle 0,06–**1,39** m (V2_3) | EuRoC, α = 0,001 (`page:5`, Table II) |
| Robustesse au seuil DBoW2 α | PGO sans PCM : 0,05 (α=10) → **1,74 m** (α=0,1) → 1,59 m (α=0,01 ; 0,001) ; Kimera-RPGO : **0,05 · 0,05 · 0,05 · 0,045 · 0,049 m** | EuRoC V1_01 (`page:5`, Table III) |
| Dérive VIO | **< 0,2 %** : 4 cm sur une trajectoire de 32 m (ATE 0,04 m) | simulateur Unity photoréaliste (MIT Lincoln Lab) (`page:6`) |
| Précision maillage global (Kimera-Semantics) | RMSE 0,353–0,480 m (V1_01 0,364 · V1_02 0,384 · V1_03 0,353 · V2_01 0,480 · V2_02 0,432 · V2_03 0,411) ; texte : « average error of 0.35 − 0.48m » | EuRoC V1/V2 vs nuage vérité terrain, échantillonnage 10³ points/m², ICP (CloudCompare) avec seuil 1,0 m, métrique de complétude (`page:5`, Table IV) |
| Précision maillage multi-frame (Kimera-Mesher) | RMSE 0,374–0,530 m ; **jusqu'à +24 %** d'erreur vs maillage global (V1_01 +24 %, V1_03 +21 %, V2_03 +22 %, mais V1_02 −2 % et V2_01 −3 %) pour « two orders of magnitude less time » | idem, horizon VIO élargi (full smoothing) pour obtenir un maillage complet (`page:5`, Table IV) |
| Reconstruction en simulation (Table V) | RMSE maillage 0,079 m (poses GT + profondeur GT) · **0,131 m** (poses Kimera-VIO + profondeur GT) · 0,215 m (poses Kimera-VIO + stéréo dense) ; mIoU 80,10 / 80,03 / **57,23 %** ; Acc 94,68 / 94,50 / 80,74 % | simulateur Unity, labels 2D vérité terrain ; la perte principale vient de la **stéréo dense** sur murs sans texture, pas du VIO (`page:6`) |
| **IMU front-end** | **≈ 40 µs** par pré-intégration → états à cadence IMU **> 200 Hz** | `page:6`, Fig. 5 |
| **Vision front-end** | bimodal : **4,5 ms** en moyenne par image (suivi seul) ; **45 ms** en moyenne par keyframe (détection + stéréo + vérification) | `page:6`, Fig. 5 (points jusqu'à ≈ 60–65 ms pour les keyframes) |
| **Back-end VIO** | **< 40 ms** par optimisation iSAM2 | `page:6`, Fig. 5 (médiane ≈ 22 ms sur le graphique) |
| **Kimera-Mesher** | per-frame **< 5 ms** ; multi-frame **15 ms** en moyenne ; latence annoncée < 20 ms | `page:2`, `page:6`, Fig. 5 |
| **Kimera-RPGO** | **55 ms** en moyenne sur EuRoC, dépend de la taille du graphe | `page:6`, Fig. 5 (dispersion ≈ 30–90 ms) |
| **Kimera-Semantics** | **≈ 0,1 s** par keyframe pour fusionner une image de profondeur dense **720 × 480** | simulateur (`page:4`, `page:6`) |
| Matériel | « runs in real-time on a CPU » ; **modèle de CPU, fréquence, nombre de cœurs, mémoire : non rapportés** ; aucun GPU | `page:1`, `page:2`, `page:6` |
| Cadence caméras / IMU | non rapportée explicitement (seulement « IMU rate (> 200Hz) ») | `page:6` |
| Latence capteur → pose | non rapportée (seule la latence des maillages < 20 ms est donnée) | `page:2` |

## Pertinence pour notre sujet
| Axe | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Modèle canonique d'un **VI-SLAM à fenêtre glissante par optimisation** (pré-intégration IMU + smart factors + iSAM2) avec graphe de poses robuste en arrière-plan ; Table I situe 13 systèmes ouverts par capteur / back-end / représentation (`page:2`, `page:3`). Architecture à **quatre threads à cadences différentes** (IMU, image, keyframe, boucle) = la même logique « asynchrone » que décrit Meta pour Insight. |
| 2. Poses pour 3DGS (piste mote, H-01) | Chiffres de référence sur ce qu'un VIO ouvert donne : ATE 0,05–0,35 m sur EuRoC (SE(3)), dérive < 0,2 % (4 cm / 32 m) en simulation ; **poses optimisées uniquement aux keyframes**, poses à cadence IMU issues du front-end (propagation) (`page:2`, `page:3`, `page:5`, `page:6`). Les corrections de Kimera-RPGO sont rétroactives → des poses enregistrées au fil de l'eau changent de repère après une boucle. |
| 3. Temps réel et contraintes embarquées | Budget détaillé par module (40 µs / 4,5 ms / 45 ms / < 40 ms / 15 ms / 55 ms / 0,1 s) **tout sur CPU**, sans GPU ni DSP (`page:6`). Montre qu'un maillage dense de scène (Delaunay sur landmarks + fusion TSDF) tient dans le budget d'un SLAM CPU. |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole ATE RMSE EuRoC avec alignement SE(3) (justifié par l'observabilité de l'échelle avec IMU), accuracy/complétude de maillage par ICP, mIoU/Acc sémantiques ; évaluation **automatisée en CI** avec evo + Open3D (`page:4`, `page:5`, `page:6`). Attention : comparaison **stéréo vs mono** et chiffres concurrents **repris** d'autres papiers (`page:5`). |

## Ce que ça dit du tracking du Quest
- **Ressemblances structurelles** avec Oculus Insight (voir [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md)) : (1) VI-SLAM à landmarks épars — coins Shi-Tomasi suivis par KLT ≈ « high-contrast pixels, such as window corners » d'Insight (`page:3`) ; (2) **pose à la cadence IMU** fournie par un thread front-end séparé (≈ 40 µs par pré-intégration, > 200 Hz) ≈ la pose « every millisecond » d'Insight, dont l'IMU a aussi son propre thread prioritaire (`page:2`, `page:6`) ; (3) **carte et optimisation globale en arrière-plan** à cadence plus lente (RPGO ≈ 55 ms, Semantics ≈ 0,1 s), découplées du chemin critique, comme les « mises à jour de carte asynchrones » d'Insight (`page:2`, `page:6`) ; (4) reconnaissance de lieu (DBoW2) + rejet d'outliers = brique de **relocalisation** robuste à l'aliasing perceptuel (`page:3`, `page:4`) ; (5) **tout sur CPU**, multithread, comme Insight sur le SoC mobile (`page:1`, `page:2`).
- **Différences** : Kimera est **stéréo synchronisé** (2 caméras, baseline fixe) alors que le Quest fusionne **4 caméras monochromes** grand angle à chevauchement partiel ; pas de **carte persistante entre sessions** dans le papier (RPGO optimise la trajectoire de la session ; la persistance n'est pas rapportée) ; **aucune prédiction** de pose pour masquer la latence d'affichage (sortie à cadence IMU pour le contrôle robot, pas pour le rendu) ; aucun DSP/SIMD mentionné ; cible robotique (évitement d'obstacles, planification) et non XR (`page:2`, `page:6`).
- **Le maillage dense temps réel ressemble à la « scène » du Quest 3** : Kimera produit en < 20 ms un maillage local triangulé sur les landmarks du VIO, mis à jour à chaque keyframe quand les poses sont réoptimisées, puis un maillage global TSDF + marching cubes à ≈ 0,1 s par keyframe (`page:2`, `page:4`, `page:6`). C'est, à l'échelle robotique, la même décomposition que l'on suppose sur le Quest 3 (tracking rapide + scene mesh volumique plus lent, obtenu avec le projecteur de profondeur selon le dossier Insight). La leçon de Kimera-Semantics est que **la profondeur dense, pas les poses, limite la qualité du maillage** : RMSE 0,131 m avec poses VIO + profondeur GT contre 0,215 m avec stéréo dense ; mIoU 80 → 57 % (`page:6`).
- **Implications pour les poses que mote récupère** : (1) un VIO de cette famille a une dérive de l'ordre de 0,1–0,2 % de la distance (4 cm / 32 m) — sur les quelques mètres d'une capture 3DGS en salle, cela donne un ordre de grandeur **compatible avec les 4–6 mm médians du spike SP-0** ; (2) seules les poses **de keyframe** sont optimisées ; les poses d'images intermédiaires sont suivies/propagées, donc moins précises : il faut savoir si MRUK publie la pose « optimisée » ou la pose « propagée/prédite » et à quelle cadence ; (3) les corrections rétroactives du graphe de poses (fermeture de boucle, marginalisation) créent des **sauts** entre images prises avant/après : le raffinement de poses de H-01 doit absorber ces discontinuités ; (4) les landmarks 3D sont **éliminés de l'état** (smart factors) et ne sont que des sous-produits du front-end — ne pas attendre d'un VIO de ce type un nuage épars de qualité SfM (`page:3`, `page:4`, `page:6`).

## Pour (vis-à-vis de notre problématique)
- Un des rares papiers qui donne **le budget temps par module** d'un VI-SLAM complet (front-end, back-end, mesher, PGO, fusion dense) et la cadence associée (IMU, image, keyframe) (`page:6`).
- Meilleure ou égale précision ATE que OKVIS, MSCKF, ROVIO, VINS-Mono sur EuRoC, sans aucun échec ; RPGO insensible au seuil de boucle (0,045–0,05 m pour α de 10 à 0,001) (`page:5`).
- Montre qu'un **maillage dense de la scène** (local + global) est un sous-produit naturel du VIO sur CPU — directement comparable à ce que fait le Quest 3 (scene mesh) et exploitable comme initialisation/contrainte géométrique d'un 3DGS.
- Modularité : « can easily fall back to a state-of-the-art VIO » — permet de tester poses VIO seules, VIO + PGO, ou VIO + maillage (`page:1`).
- Open source, ROS, CI avec évaluation automatique (evo, Open3D) : reproductible pour une comparaison poses Quest vs Kimera sur nos propres séquences (`page:4`).

## Contre / limites
- **Matériel d'évaluation non décrit** (CPU, cœurs, mémoire) : les temps ne sont pas transposables à un SoC XR2 sans mesure (`page:6`).
- Comparaison Table II **biaisée** : Kimera en stéréo, concurrents en mono, chiffres concurrents repris d'autres papiers, alignement SE(3) différent du Sim(3) de [77] (`page:5`).
- Pas de chiffre de latence capteur → pose, ni de consommation ; pas d'évaluation sur plateforme embarquée (`page:6`).
- Pas de relocalisation inter-sessions ni de carte persistante rapportées ; pas de prédiction de pose ; stéréo synchronisé uniquement (pas de multi-caméras asynchrones comme sur casque) (`page:3`).
- Maillages évalués avec un seuil ICP de **1,0 m** et des erreurs de 0,35–0,53 m sur EuRoC : précision loin de ce qu'un 3DGS demande ; la stéréo dense échoue sur les murs sans texture (`page:5`, `page:6`).
- Semantics évalué avec des **labels 2D vérité terrain** en simulation seulement (`page:6`).

## Idées à creuser pour mote
- *Hypothèse (H-01, poses)* : rejouer les captures mote (images RGB passthrough + poses MRUK) dans Kimera-VIO ne sera pas possible sans les caméras de tracking, mais **Kimera-RPGO** peut servir seul : prendre les poses Quest comme arêtes d'odométrie, ajouter des boucles détectées par DBoW2 sur les images RGB, et mesurer si la trajectoire Quest est déjà « globalement cohérente » (résidu des cycles odométrie + boucle, test χ² de PCM) — un indicateur de dérive sans COLMAP (`page:3`, `page:4`).
- *Hypothèse (initialisation 3DGS)* : remplacer le nuage SfM de COLMAP par le **scene mesh du Quest 3** (équivalent du maillage multi-frame/global de Kimera) : échantillonner les Gaussiennes sur la surface du maillage, à la manière de l'échantillonnage à 10³ points/m² utilisé pour l'évaluation (`page:5`) ; comparer à l'initialisation aléatoire et à COLMAP.
- *Hypothèse (keyframes)* : n'alimenter l'entraînement 3DGS qu'avec les images **de keyframe** du casque (quand on peut les identifier) ou, à défaut, pondérer les images par la « fraîcheur » de leur pose, puisque Kimera montre que seules les poses de keyframe sont optimisées par le back-end (`page:3`).
- *Hypothèse (budget)* : utiliser la répartition de Kimera (front-end 4,5 ms/image, back-end < 40 ms, mesher 15 ms, PGO 55 ms) comme **grille d'ordres de grandeur** pour estimer ce que le XR2 Gen 2 consacre au tracking, et donc la marge disponible pour une capture mote (encodage, envoi) sans dégrader le tracking (`page:6`).
- *Hypothèse (évaluation)* : reprendre le protocole « poses GT vs poses VIO, profondeur GT vs stéréo » de Table V pour isoler, dans mote, la part d'erreur due aux poses Quest de celle due à la couverture/densité des vues : entraîner un 3DGS avec poses COLMAP, poses Quest, et poses Quest raffinées, à images identiques (`page:6`).

## Citations clés
> « Kimera is designed with modularity in mind and has four key components: a visual-inertial odometry (VIO) module for fast and accurate state estimation, a robust pose graph optimizer for global trajectory estimation, a lightweight 3D mesher module for fast mesh reconstruction, and a dense 3D metric-semantic reconstruction module. » (`doc:b2c27e2/tier:standard/page:1`)

> « Kimera is heavily parallelized and uses four threads to accommodate inputs and outputs at different rates (e.g., IMU, frames, keyframes). » (`doc:b2c27e2/tier:standard/page:2`)

> « The IMU front-end requires around 40 µs for preintegration, hence can generate state estimates at IMU rate (> 200Hz). The vision front-end module shows a bimodal distribution since, for every frame, we just perform feature tracking (which takes an average of 4.5ms), while, at keyframe rate, we perform feature detection, stereo matching, and geometric verification, which, combined, take an average of 45ms. Kimera-Mesher is capable of generating per-frame 3D meshes in less than 5ms, while building the multi-frame mesh takes 15ms on average. The back-end solves the factorgraph optimization in less than 40ms. » (`doc:b2c27e2/tier:standard/page:6`)

> « Using Kimera-VIO also results in negligible loss in performance since our VIO has a small drift (< 0.2%, 4cm for a 32m long trajectory). Certainly, the biggest drop in performance is due to the use of dense stereo. » (`doc:b2c27e2/tier:standard/page:6`)

> « Kimera-Mesher produces a more noisy mesh (up to 24% error increase), but requires two orders of magnitude less time to compute. » (`doc:b2c27e2/tier:standard/page:5`)

## Liens
- Papiers liés :
  - [VINS-Mono](../qin2018_vins-mono/fiche.md) — comparé dans Table II (mono, Ceres) ; même famille d'optimisation à fenêtre glissante ; Kimera reprend ses chiffres auto-rapportés (`page:5`).
  - [VINS-Fusion](../qin2019_vins-fusion/fiche.md) — concurrent stéréo/IMU listé en Table I (`page:2`).
  - [ORB-SLAM](../murartal2015_orb-slam/fiche.md), [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — SLAM à keyframes avec DBoW2 ; ORB-SLAM3 ajoute la carte persistante multi-sessions absente ici.
  - [OpenVINS](../geneva2020_openvins/fiche.md) — alternative par filtre MSCKF ; [Basalt](../usenko2020_basalt/fiche.md) — autre VIO par optimisation avec marginalisation.
  - [Benchmark VIO](../delmerico2018_vio-benchmark/fiche.md) — source [77] des chiffres OKVIS/MSCKF/ROVIO/SVO-GTSAM de Table II, et référence pour les temps sur plateformes embarquées (`page:5`).
  - [Navion](../suleiman2019_navion/fiche.md) — accélérateur matériel d'un VIO à smart factors/pré-intégration de la même lignée (Forster/Carlone).
  - [Revue VIN](../huang2019_vin-review/fiche.md) — pour situer lissage complet vs fenêtre glissante vs filtre.
  - [Multi-cam VINS](../eckenhoff2019_multicam-vins/fiche.md), [Multi-cam SLAM](../kuo2020_multicam-slam/fiche.md) — ce qu'il faut ajouter pour passer du stéréo synchronisé aux 4 caméras du casque.
  - [Project Aria](../engel2023_project-aria/fiche.md) — VIO Meta « open loop » / « closed loop » : équivalent industriel de Kimera-VIO / Kimera-RPGO.
  - [Dossier Oculus Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) — ce qu'on sait du VI-SLAM du Quest.
  - [Photo-SLAM](../huang2024_photo-slam/fiche.md), [Survey NeRF/GS-SLAM](../tosi2024_nerf-gs-slam-survey/fiche.md) — SLAM qui produisent directement une carte 3DGS, successeurs logiques du couple VIO + mesher.
  - [3DGS](../kerbl2023_3dgs/fiche.md) — consommateur des poses et du nuage/maillage initial ; [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md) — pour le budget d'entraînement côté PC.
  - [VRSplat](../tu2025_vrsplat/fiche.md) — côté rendu sur Quest 3 ; [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — mesure indépendante de la précision des poses de casque.
