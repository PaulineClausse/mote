---
citekey: delmerico2018_vio-benchmark
mineru_doc: 77fa4da
type: conférence   # IEEE ICRA 2018 (benchmark)
statut: fiche complète
tags: [vio, benchmark, euroc, msckf, okvis, rovio, vins-mono, svo, msf, gtsam, embarqué, arm, odroid, up-board, intel-nuc, cpu, mémoire, temps-par-image, ate-rmse, erreur-odométrique, drone, snapdragon-xr2, piste-mote]
---

# A Benchmark Comparison of Monocular Visual-Inertial Odometry Algorithms for Flying Robots

**Référence :** Jeffrey Delmerico, Davide Scaramuzza (2018). *A Benchmark Comparison of Monocular Visual-Inertial Odometry Algorithms for Flying Robots.* Proc. IEEE International Conference on Robotics and Automation (ICRA 2018), Brisbane, pp. 2502–2509. DOI 10.1109/ICRA.2018.8460664 (non imprimé dans le PDF, à vérifier) · pas d'arXiv · PDF : http://rpg.ifi.uzh.ch/docs/ICRA18_Delmerico.pdf · code du benchmark : non publié (les résultats sont « présentés comme benchmark ») ; implémentations évaluées : msckf_mono (github.com/daniilidis-group/msckf_mono), okvis_ros (github.com/ethz-asl/okvis_ros), rovio (github.com/ethz-asl/rovio), VINS-Mono (github.com/HKUST-Aerial-Robotics/VINS-Mono), ethzasl_msf (github.com/ethz-asl/ethzasl_msf), SVO 2 (rpg.ifi.uzh.ch/svo2.html), GTSAM (bitbucket.org/gtborg/gtsam) ; l'intégration SVO+GTSAM n'est **pas** publique (`doc:77fa4da/tier:standard/page:1`, `page:3`). Robotics and Perception Group, Univ. de Zurich / ETH (`page:1`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Benchmark de six pipelines VIO monoculaires open source (MSCKF, OKVIS, ROVIO, VINS-Mono avec/sans fermeture de boucle, SVO+MSF, SVO+GTSAM) sur les 11 séquences EuRoC et **quatre plateformes de calcul** (laptop i7, Intel NUC, Up Board Atom, ODROID XU4 ARM big.LITTLE), en mesurant précision (RMSE ATE, erreur odométrique), temps par image, charge CPU et mémoire : « there is no free lunch in visual state estimation » — la précision et la robustesse se paient en calcul, et sur ARM certaines configurations ne tournent plus du tout (`page:1`, `page:6`, `page:8`).

## Problème traité
- La littérature compare les VIO « almost always [...] on powerful desktop or laptop computers with abundant computational resources », alors qu'un drone (et, pour nous, un casque) n'a qu'un calculateur embarqué contraint en puissance et en masse (`page:1`).
- Les comparaisons existantes sont partielles : VINS-Mono vs OKVIS sur quelques séquences EuRoC seulement ; OKVIS vs une implémentation privée de MSCKF sur données privées ; ROVIO jamais comparé ; SVO+GTSAM comparé sur données non publiques (`page:2`).
- « no existing work considers the additional dimension of computational constraints in their evaluation » (`page:2`).
- Hors périmètre : les SLAM purement visuels (ORB-SLAM, LSD-SLAM), car « we focus this benchmark on visual-inertial methods » ; pas d'exploration de l'espace des paramètres (pas de cadre type SLAMBench pour le VIO) — les auteurs ont fait régler chaque pipeline **par ses auteurs** (Leutenegger, Bloesch, Qin, Daniilidis) (`page:2`, `page:8`).

## Contenu / protocole
### Algorithmes comparés (Sec. II, `page:2`–`page:3`)
| Pipeline (nom dans les figures) | Famille | Front-end | Back-end | Remarques du papier |
|---|---|---|---|---|
| MSCKF (`msckf`) | filtre EKF, tightly-coupled | suivi de points | EKF multi-états sans position 3D des points dans l'état ; implémentation issue d'un EKF pour caméras à événements [29] adaptée aux caméras standard | « forms the basis of many modern, proprietary VIO systems » ; le plus ancien (2007) (`page:3`) |
| OKVIS (`okvis`) | optimisation fenêtre glissante, tightly-coupled | Harris multi-échelle + BRISK | Ceres, marginalisation des keyframes | « not optimized for monocular VIO », meilleur en stéréo (`page:3`) |
| ROVIO (`rovio`) | EKF, tightly-coupled, direct | FAST + patches multi-niveaux, erreur photométrique en innovation | EKF robot-centrique | conçu monoculaire (`page:3`) |
| VINS-Mono (`vinsmono` / `vinsmonolc`) | optimisation fenêtre glissante, tightly-coupled | coins Shi-Tomasi | pré-intégration IMU, initialisation loosely-coupled, relocalisation, **graphe de poses 4DoF + fermeture de boucle** (évalué avec et sans) | version PC ROS **et iOS** (`page:3`) |
| SVO+MSF (`svomsf`) | **loosely-coupled** | SVO (semi-direct, FAST + alignement photométrique) | MSF (EKF générique, SVO vu comme capteur de pose) | échelle non observable : **initialisée avec la vérité terrain** (`page:3`, `page:6`) |
| SVO+GTSAM (`svogtsam`) | full smoothing | SVO | iSAM2 + facteurs IMU pré-intégrés | intégration non publique (`page:3`) |

### Plateformes matérielles (Sec. III.A, `page:5`)
| Plateforme | CPU | RAM | Puissance | Taille / masse | ISA / SIMD |
|---|---|---|---|---|---|
| Laptop (Lenovo ThinkPad W540, référence) | Intel Core i7-4810MQ, 4 cœurs HT, 2,80 GHz | 32 Go | 47 W nominal | « not feasible for deployment on a flying robot » | x86-64 / SSE |
| Intel NUC | Core i7-5557U, 2 cœurs HT, 3,10 GHz | 16 Go | 28 W | 10 × 10 cm | x86-64 / SSE |
| Up Board | Intel Atom x5-Z8350, 4 cœurs sans HT, 1,44 GHz | 4 Go | 12 W | 8,5 × 5,6 cm, 78 g | x86-64 / SSE |
| **ODROID XU4** | Samsung Exynos 5422 : 4 × ARM Cortex-A15 2,0 GHz + 4 × Cortex-A7 1,5 GHz (**big.LITTLE**) | 2 Go | 10 W | 8,3 × 5,8 cm, 59 g | **ARM 32 bits / NEON** |

### Données et protocole (Sec. III.B–C, `page:5`–`page:6`)
- EuRoC MAV : 11 séquences (Machine Hall MH01–05, Vicon Room V101–103, V201–203), stéréo WVGA monochrome à **20 Hz** + IMU à **200 Hz** ; **seules la caméra gauche et l'IMU** sont utilisées ; vérité terrain Leica MS50 (MH) ou Vicon (V) (`page:5`).
- Ubuntu 16.04 + ROS Kinetic (14.04/Indigo pour OKVIS et VINS-Mono sur ODROID) ; données **rejouées en temps réel** pour simuler le flux capteur d'un robot (`page:5`, `page:6`).
- Paramètres recommandés par les auteurs de chaque pipeline, identiques sur toutes les séquences, **sauf dégradations imposées par le matériel** : OKVIS sur Up Board/ODROID keypoints 400 → 200, fenêtre 5 → 3 keyframes, trames liées IMU 3 → 2 ; ROVIO sur ODROID 25 → 10 features, et **aucune configuration ne converge sur Up Board** ; VINS-Mono 150 → 100 features sur Up Board/ODROID, et **fermeture de boucle impossible sur ODROID** (`page:6`).
- Compilation au niveau d'optimisation maximal, SSE/NEON « wherever possible » (`page:6`).
- Mesures : pose enregistrée après chaque mise à jour image ; temps « from receiving the image to updating the pose » ; CPU (% d'un cœur) et mémoire (% de la RAM) échantillonnés à 1 Hz ; en cas d'échec d'initialisation, relance et premier essai réussi conservé (`page:6`).
- Métriques : (1) **RMSE de position après alignement sim(3)** (Umeyama) sur toute la trajectoire (Table I) ; (2) **erreur odométrique KITTI** (translation et lacet) sur des segments de {7, 14, 21, 28, 35} m, bornés par la plus courte trajectoire (Vicon Room 2, 36 m) (`page:4`, `page:6`).

## Résultats chiffrés
### Table I — RMSE ATE (m) après alignement sim(3), toutes les combinaisons (`page:5`)
Ordre des colonnes par plateforme : svomsf / msckf / okvis / rovio / vinsmono / vinsmonolc / svogtsam. « × » = échec. (Table reconstruite depuis le texte du PDF ; la mise en gras/bleu du papier n'a pas pu être récupérée.)

| Séq. | Laptop | Intel NUC | Up Board | ODROID |
|---|---|---|---|---|
| MH01 | 0,14 / 0,42 / 0,16 / 0,21 / 0,27 / 0,07 / 0,05 | 0,22 / 0,43 / 0,16 / 0,21 / 0,27 / 0,07 / 0,08 | 0,29 / 0,48 / 0,20 / × / 0,20 / 0,18 / 0,12 | 0,22 / 0,47 / 0,15 / 0,36 / 0,13 / × / 0,15 |
| MH02 | 0,20 / 0,45 / 0,22 / 0,25 / 0,12 / 0,05 / 0,03 | 0,20 / 0,43 / 0,20 / 0,25 / 0,12 / 0,05 / 0,05 | 0,31 / 0,40 / 0,22 / × / 0,18 / 0,19 / 0,05 | 0,24 / 0,63 / 0,20 / 0,23 / 0,08 / × / 0,05 |
| MH03 | 0,48 / 0,23 / 0,24 / 0,25 / 0,13 / 0,08 / 0,12 | 0,60 / 0,25 / 0,24 / 0,25 / 0,13 / 0,05 / 0,12 | 0,66 / 0,45 / 0,37 / × / 0,17 / 0,09 / 0,10 | 0,52 / 0,47 / × / 0,58 / 0,58 / × / 0,12 |
| MH04 | 1,38 / 0,37 / 0,34 / 0,49 / 0,23 / 0,12 / 0,13 | 1,82 / 0,61 / 0,23 / 0,49 / 0,23 / 0,10 / 0,24 | 2,02 / 0,67 / 0,44 / × / 0,12 / 0,15 / 0,24 | 2,28 / 0,64 / 0,42 / 0,81 / 0,12 / × / × |
| MH05 | 0,51 / 0,48 / 0,47 / 0,52 / 0,35 / 0,09 / 0,16 | 0,93 / 0,48 / 0,56 / 0,52 / 0,34 / 0,11 / 0,16 | 0,87 / 0,48 / × / × / 0,35 / 0,26 / 0,13 | 1,12 / 0,48 / 0,62 / 0,78 / 0,21 / × / 0,12 |
| V101 | 0,40 / 0,34 / 0,09 / 0,10 / 0,07 / 0,04 / 0,07 | 0,39 / 0,29 / 0,09 / 0,10 / 0,07 / 0,04 / 0,12 | 0,36 / 0,25 / 0,13 / × / 0,05 / 0,05 / 0,08 | 0,43 / 0,21 / 0,09 / 0,15 / 0,11 / × / 0,07 |
| V102 | 0,63 / 0,20 / 0,20 / 0,10 / 0,10 / 0,06 / 0,11 | 0,63 / 0,20 / 0,18 / 0,10 / 0,10 / 0,05 / 0,16 | 0,78 / 0,22 / 0,22 / × / 0,12 / 0,08 / 0,10 | 0,81 / 0,21 / × / 0,24 / 0,11 / × / 0,14 |
| V103 | × / 0,67 / 0,24 / 0,14 / 0,13 / 0,11 / × | × / 0,67 / 0,20 / 0,14 / 0,13 / 0,12 / × | × / 0,63 / 0,30 / × / 0,10 / 0,08 / × | × / 1,52 / × / 0,20 / 0,11 / × / × |
| V201 | 0,20 / 0,10 / 0,13 / 0,12 / 0,08 / 0,06 / 0,07 | 0,17 / 0,11 / 0,12 / 0,12 / 0,08 / 0,06 / 0,08 | 0,33 / 0,17 / 0,18 / × / 0,08 / 0,05 / 0,13 | 0,15 / 0,25 / 0,11 / 0,15 / 0,08 / × / 0,15 |
| V202 | 0,37 / 0,16 / 0,16 / 0,14 / 0,08 / 0,06 / × | 0,37 / 0,16 / 0,17 / 0,14 / 0,08 / 0,05 / × | 0,59 / 0,18 / 0,30 / × / 0,08 / 0,05 / × | 0,46 / 0,19 / 0,26 / 0,17 / 0,06 / × / × |
| V203 | × / 1,13 / 0,29 / 0,14 / 0,21 / 0,09 / × | × / 1,13 / 0,24 / 0,14 / 0,21 / 0,09 / × | × / 1,86 / 0,38 / × / 0,17 / 0,09 / × | × / 1,09 / × / 0,23 / 0,16 / × / × |

### Synthèse de la Table I (moyennes / médianes calculées par nous sur les séquences réussies, `page:5`)
| Pipeline | Laptop : moy. / méd. (échecs) | NUC | Up Board | ODROID |
|---|---|---|---|---|
| svomsf | 0,48 / 0,40 m (2/11 : V103, V203) | 0,59 / 0,39 (2) | 0,69 / 0,59 (2) | 0,69 / 0,46 (2) |
| msckf | 0,41 / 0,37 (**0**) | 0,43 / 0,43 (0) | 0,53 / 0,45 (0) | 0,56 / 0,47 (0) |
| okvis | 0,23 / 0,22 (0) | 0,22 / 0,20 (0) | 0,27 / 0,26 (1) | 0,26 / 0,20 (**4**) |
| rovio | 0,22 / 0,14 (0) | 0,22 / 0,14 (0) | **× (11/11)** | 0,36 / 0,23 (0) |
| vinsmono | 0,16 / 0,13 (0) | 0,16 / 0,13 (0) | 0,15 / 0,12 (0) | 0,16 / 0,11 (0) |
| vinsmonolc | **0,075 / 0,07** (0) | **0,072 / 0,06** (0) | 0,115 / 0,09 (0) | **× (11/11)** |
| svogtsam | 0,092 / 0,09 (3 : V103, V202, V203) | 0,126 / 0,12 (3) | 0,119 / 0,11 (3) | 0,114 / 0,12 (4) |

Lecture : (i) VINS-Mono **sans** fermeture de boucle garde la même précision (≈ 0,16 m) du laptop à l'ODROID malgré la réduction 150 → 100 features ; (ii) la fermeture de boucle divise l'ATE par ≈ 2 (0,16 → 0,075 m) sur laptop/NUC mais est **impossible sur ARM** ; (iii) SVO+GTSAM est souvent le meilleur « sans boucle » (MH01–MH03, MH05, V201 sur laptop) mais échoue sur 3–4 séquences par plateforme ; (iv) SVO+MSF se dégrade de 0,48 à 0,69 m sur les cartes embarquées (`page:5`, `page:7`).

### Erreur odométrique (Figs. 2–3, lecture approximative des boxplots, `page:4`)
| Métrique (segments 7 → 35 m) | Laptop (médiane ≈) | ODROID (médiane ≈) |
|---|---|---|
| Translation, vinsmonolc / svogtsam / vinsmono | ≈ 0,10–0,15 m à 7 m ; ≈ 0,15–0,25 m à 35 m | vinsmono ≈ 0,15–0,25 m ; svogtsam ≈ 0,1–0,2 m |
| Translation, okvis / rovio | ≈ 0,15–0,2 m à 7 m ; ≈ 0,3 m à 35 m | okvis ≈ 0,2–0,3 m ; rovio ≈ 0,25–0,45 m |
| Translation, svomsf / msckf | ≈ 0,4 m à 7 m ; ≈ 0,6 m à 35 m (IQR jusqu'à > 1 m) | ≈ 0,4–0,8 m |
| Lacet, meilleures méthodes | ≈ 0,3–0,5° à 7 m ; ≈ 0,8–1,5° à 35 m | ≈ 0,3–1° (svogtsam, okvis, vinsmono) |
| Lacet, svomsf / msckf | ≈ 1–2° à 7 m, 2–3° à 35 m | svomsf sur Up Board : médiane ≈ 3–5° |

### Coût de calcul (Figs. 1, 4, 5, 6 — lecture approximative des médianes, `page:1`, `page:7`)
| Pipeline | CPU (% d'un cœur) Laptop / NUC / Up / ODROID | Mémoire (% RAM) Laptop 32 Go / NUC 16 Go / Up 4 Go / ODROID 2 Go | Temps par image (ms) Laptop / NUC / Up / ODROID |
|---|---|---|---|
| svomsf | ≈ 50 / 20 / 125 / 85 | ≈ 6 / 6 / 32 / 20 | ≈ 5 / 5 / 35 / 20 |
| msckf | ≈ 115 / 100 / 170 / 215 (whiskers > 350 sur ODROID) | ≈ 7 / 6 / 26 / 12 | ≈ 20 / 20 / 45 / 45 |
| okvis | ≈ 180 / 175 / 180 / 175 | ≈ 6 / 6 / 26 / 17 | ≈ 25 / 25 / 90 (jusqu'à 175) / **≈ 340 (IQR 190 → > 400)** |
| rovio | ≈ 105 / 100 / — / 105 | ≈ 7 / 8 / — / 12 | ≈ 20 / 20 / — / 40 |
| vinsmono | ≈ 120 / 100 / 215 / 240 | ≈ 6 / 6 / 26 / 18 | ≈ 55 / 60 / **≈ 135 (jusqu'à > 400)** / ≈ 140 (jusqu'à 260) |
| vinsmonolc | ≈ 140 (30 → 250) / 120 (→ 235) / 235 (→ 335) / — | ≈ 8 / 9 / 45 (→ 62) / — | ≈ 55 / 60 / ≈ 135 (→ > 400) / — |
| svogtsam | ≈ 150 / 130 / 145 (15 → 295) / 185 | ≈ 8 / 9 / 48 (→ 75) / 30 (→ 55) | **≈ 5 / 5 / 25 / 15** (front-end et back-end découplés) |

Points saillants, dans le texte : OKVIS reste précis sur les cartes embarquées « despite low update rates there due to long per-frame processing times » — tolérance attribuée aux trajectoires lentes d'EuRoC (`page:6`) ; ROVIO a une consommation « tightly bounded and consistent » mais diverge sur Up Board car « the update rate was too slow with the low clock rate » (`page:6`, `page:7`) ; VINS-Mono est « the most consistently accurate and robust across all of the hardware platforms » au prix d'une « potentially prohibitive level of resource usage » (`page:6`) ; SVO+MSF est le plus efficace mais le moins précis et exige l'initialisation manuelle de l'échelle (`page:7`) ; SVO+GTSAM est le plus précis « for many of the platform-dataset combinations » sans boucle, avec temps par image bas mais CPU/mémoire élevés et instabilités numériques du back-end (`page:7`) ; la baisse de CPU du laptop au NUC montre que SVO+MSF, SVO+GTSAM et VINS-Mono « are sensitive to CPU clock speed » (un thread intensif) (`page:7`).

| Métrique récapitulative | Valeur | Conditions |
|---|---|---|
| Matériel | 4 plateformes, 10 W (ODROID) à 47 W (laptop) | `page:5` |
| Fréquence capteurs | images 20 Hz, IMU 200 Hz, rejoué en temps réel | `page:5`, `page:6` |
| ATE RMSE, meilleure config | **0,03 m** (svogtsam, MH02, laptop) ; vinsmonolc 0,04–0,12 m sur laptop | `page:5` |
| ATE RMSE sur ARM (ODROID), meilleur disponible | vinsmono 0,06–0,58 m (moy. 0,16), svogtsam 0,05–0,15 m (7/11 séquences) | `page:5` |
| Temps par image sur ARM | ≈ 15 ms (svogtsam) à ≈ 340 ms (okvis) ; vinsmono ≈ 140 ms soit ≈ 7 Hz effectifs pour un flux à 20 Hz | `page:7` (lecture figure) |
| CPU sur ARM | ≈ 85 % (svomsf) à ≈ 240 % d'un cœur (vinsmono) | `page:7` (lecture figure) |
| Mémoire sur ARM (2 Go) | ≈ 12–30 % | `page:7` (lecture figure) |
| Latence capteur → pose, consommation (W) par algorithme, GPU/DSP | **non rapporté** (seul le temps de traitement par image est mesuré ; aucune plateforme n'utilise GPU ou DSP) | — |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Carte des familles de VIO (EKF type MSCKF vs optimisation fenêtre glissante type VINS/OKVIS vs loosely-coupled) avec leurs implémentations ouvertes ; montre que la fermeture de boucle (ce que fait la carte persistante d'Insight) est ce qui ramène l'ATE sous 10 cm (`page:3`, `page:5`) |
| 2. Poses pour 3DGS (piste mote, H-01) | Ordres de grandeur : un VIO monoculaire open source de 2018, bien réglé, donne **5–15 cm** d'ATE RMSE et ≈ 0,1–0,2 m / 0,5–1,5° d'erreur odométrique à 7–35 m sur un laptop (`page:4`, `page:5`) — soit 10 à 30× l'erreur médiane mesurée en SP-0 (4–6 mm / 0,3–0,5°) ; attention aux métriques différentes (RMSE globale sim(3) sur 36–130 m de vol vs médiane par pose contre COLMAP à l'échelle d'une pièce) |
| 3. Temps réel et contraintes embarquées | **Fiche de référence de l'axe** : sur ARM Cortex-A15 (32 bits, NEON, 2 Go), les pipelines précis tombent à 7 Hz effectifs (vinsmono) ou 3 Hz (okvis), ROVIO diverge sur Atom 1,44 GHz, la fermeture de boucle est impossible ; les paramètres (features, fenêtre) doivent être réduits (`page:6`, `page:7`) |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole réutilisable : EuRoC 11 séquences, ATE RMSE après sim(3) + erreur odométrique KITTI sur segments, CPU/mémoire à 1 Hz, temps par image, rejeu temps réel, paramètres fixés par les auteurs (`page:5`, `page:6`) |

## Ce que ça dit du tracking du Quest
- **Point commun** : Oculus Insight est un VI-SLAM tightly-coupled tournant sur un SoC ARM mobile (Snapdragon XR2 Gen 2 : 2 × Cortex-A715 + 4 × Cortex-A510, voir le [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md)) ; l'ODROID XU4 (Exynos 5422, 4 × A15 + 4 × A7 big.LITTLE, NEON, 2 Go) est le **seul point ARM de la littérature de benchmark VIO** et joue ici le rôle d'ancêtre (2014) du XR2 (`page:5`). Les leçons transposables : (a) sur ARM, ce qui cède en premier n'est pas la précision par pose mais **la cadence et la robustesse** (vinsmono garde ≈ 0,16 m d'ATE mais passe de ≈ 55 à ≈ 140 ms par image) ; (b) les pipelines à **un thread intensif** sont « sensitive to CPU clock speed » (`page:7`) — ce qui explique l'insistance de Meta sur le multithreading, l'asynchronisme et le « Quest-specific DSP tuning » ; (c) la fermeture de boucle / carte persistante est le premier module sacrifié quand le calcul manque (impossible sur ODROID, `page:6`), alors que c'est précisément ce qui divise l'ATE par 2 (`page:5`).
- **Différences** : Insight utilise **4 caméras** grand angle et un IMU à **1 kHz** (ici une seule caméra WVGA à 20 Hz et un IMU à 200 Hz, `page:5`) ; il maintient une carte persistante avec relocalisation (équivalent de `vinsmonolc`, non de `vinsmono`) ; il prédit la pose quelques ms en avant (aucune prédiction ni latence mesurée ici) ; il est budgété pour cohabiter avec le rendu (le papier mesure des charges de 100–240 % d'un cœur pour le seul VIO, `page:7`, ce qui serait incompatible avec un casque sans DSP ou sans réduction drastique du coût par image). Le papier n'évalue aucun GPU ni DSP (« non rapporté »).
- **Implication pour les poses que mote récupère** : le Quest se situe, par architecture, dans la case « optimisation + fermeture de boucle sur ARM » que ce benchmark n'a **pas** réussi à faire tourner en 2018 ; les ~4–6 mm de SP-0 sont donc cohérents avec un système qui a résolu, par le matériel (multi-caméras, IMU 1 kHz, DSP) et une décennie de SoC, ce que les pipelines ouverts de 2018 ne pouvaient pas offrir sur ARM. Mais la précision « à la ROVIO/VINS sans boucle » (≈ 10–20 cm d'ATE sur des trajectoires de 36–130 m) reste la référence pour la **dérive en odométrie pure**, à surveiller dès que la relocalisation du casque n'opère plus (zones nouvelles, faible texture, lumière faible).

## Pour (vis-à-vis de notre problématique)
- Seul papier de la base qui met **la même métrique de précision et les mêmes séquences** en face de quatre budgets de calcul, dont un ARM NEON 32 bits à 10 W : il fournit l'échelle « précision vs coût » que les papiers d'algorithmes ne donnent pas (`page:1`, `page:5`, `page:7`).
- Tableau complet (28 colonnes × 11 séquences) de l'ATE RMSE avec les échecs explicités, et paramètres **réglés par les auteurs des algorithmes** (`page:2`, `page:5`, `page:6`).
- Protocole d'évaluation entièrement spécifié (alignement sim(3), erreur odométrique KITTI par segments, CPU/mémoire à 1 Hz, rejeu temps réel) réutilisable pour mesurer un SLAM ouvert face aux poses Quest (`page:6`).
- Diagnostics qualitatifs utiles : sensibilité à la fréquence d'horloge, divergence d'un EKF direct quand la cadence tombe, coût de la fermeture de boucle (`page:6`, `page:7`).

## Contre / limites
- **Monoculaire uniquement** et EuRoC « low-speed trajectories » (`page:6`) : ne couvre ni le multi-caméras ni les mouvements de tête rapides d'un casque ; les SLAM visuels (ORB-SLAM) sont exclus (`page:2`).
- Matériel de 2014–2015 (Exynos 5422, Atom x5), pas de GPU ni de DSP ; aucune mesure de latence capteur → pose ni de consommation par algorithme (`page:5`, `page:6`).
- Résultats de coût de calcul uniquement sous forme de **boxplots** (Figs. 4–6, `page:7`) : les valeurs ci-dessus sont des lectures de figure, pas des chiffres du texte.
- SVO+MSF initialisé avec la vérité terrain (échelle) ; SVO+GTSAM non reproductible (intégration non publique) ; versions logicielles différentes sur ODROID (Ubuntu 14.04) (`page:3`, `page:5`, `page:6`).
- Un seul essai réussi par combinaison (relance en cas d'échec d'initialisation) : pas de variance inter-essais (`page:6`).
- Pas d'exploration de paramètres : « a full design-space exploration [...] can have a dramatic effect on algorithm performance » (`page:2`).
- Métrique ATE RMSE globale peu adaptée à la question 3DGS (erreur relative entre vues voisines) ; l'erreur odométrique sur 7 m est le proxy le plus proche, mais n'est donnée que graphiquement (`page:4`).

## Idées à creuser pour mote
- *Hypothèse (évaluation)* : reproduire le protocole (ATE sim(3) + erreur odométrique par segments de 1–7 m) sur les trajectoires Quest de SP-0, pour exprimer la qualité des poses casque dans la même grammaire que ce benchmark et que [Project Aria](../engel2023_project-aria/fiche.md) (dérive en % de distance).
- *Hypothèse (H-01)* : utiliser les niveaux d'erreur « vinsmono sans boucle » (≈ 0,15 m / 1° sur 7–35 m) comme borne de **dégradation contrôlée** des poses d'entrée d'un 3DGS : injecter ce bruit sur des poses COLMAP et mesurer à partir de quel niveau le raffinement de poses à l'entraînement ne récupère plus la qualité.
- *Hypothèse (embarqué)* : si un SLAM ouvert doit un jour tourner **sur** le Quest (plutôt que de lire les poses MRUK), choisir un estimateur dont le temps par image reste bas sur ARM grâce au découplage front-end/back-end (SVO+GTSAM : ≈ 15 ms sur ODROID) ou un filtre type MSCKF/[OpenVINS](../geneva2020_openvins/fiche.md), et accepter de perdre la fermeture de boucle ; comparer avec la cadence 1 kHz annoncée par Meta.
- *Hypothèse (comparaison)* : la carte « précision vs CPU » de la Fig. 1 (`page:1`) donne un gabarit pour positionner les poses Quest (coût nul pour nous, précision SP-0) face aux estimateurs ouverts sur PC — argument pour la piste mote (poses casque + raffinement) contre « SLAM ouvert sur PC ».
- *Hypothèse (robustesse)* : les séquences où tout échoue sur ARM (V103, V203 : mouvements rapides, faible éclairage) sont les conditions à tester en priorité sur le Quest 3S (cf. tracking faible lumière, [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md)).

## Citations clés
> « It is not clear from existing results in the literature, however, which VIO algorithms perform well under the accuracy, latency, and computational constraints of a flying robot with onboard state estimation. » (`doc:77fa4da/tier:standard/page:1`)

> « Unlike the other systems, the ODROID uses a 32-bit architecture, but can make use of the NEON SIMD instruction set, while the 64-bit systems can use SSE instructions. » (`doc:77fa4da/tier:standard/page:5`)

> « The performance of VINS-Mono was the most consistently accurate and robust across all of the hardware platforms. Enabling loop closure further improved the results, although this was not possible with the constrained computation available on the ODROID. This superior performance comes at the cost of a potentially prohibitive level of resource usage. » (`doc:77fa4da/tier:standard/page:6`)

> « Even with reduced parameter settings, the filter diverged quickly on all trials on this platform, suggesting that the update rate was too slow with the low clock rate of the Up Board's CPU, despite its otherwise sufficient computing resources. » (`doc:77fa4da/tier:standard/page:7`)

> « there is no free lunch in visual state estimation. Accuracy and robustness can be improved with additional computation, but on systems with limited resources, finding the right balance between the competing requirements can be challenging. » (`doc:77fa4da/tier:standard/page:8`)

## Liens
- Papiers liés :
  - [VINS-Mono](../qin2018_vins-mono/fiche.md) — pipeline le plus précis et robuste du benchmark ; sa fermeture de boucle est ce qui ramène l'ATE sous 10 cm (`page:5`, `page:6`).
  - [VINS-Fusion](../qin2019_vins-fusion/fiche.md) — successeur multi-capteurs (non évalué ici).
  - [OpenVINS](../geneva2020_openvins/fiche.md) — filtre MSCKF moderne ; la famille MSCKF est ici la plus robuste (0 échec) mais la moins précise des tightly-coupled (`page:5`, `page:6`).
  - [ORB-SLAM](../murartal2015_orb-slam/fiche.md), [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — exclus du benchmark (non inertiels en 2018) ; ORB-SLAM3 comble ce manque.
  - [Basalt](../usenko2020_basalt/fiche.md), [Kimera](../rosinol2020_kimera/fiche.md) — estimateurs postérieurs, à positionner sur la même grille précision/coût.
  - [Faster than FAST](../nagy2020_faster-than-fast/fiche.md), [Navion](../suleiman2019_navion/fiche.md) — réponses matérielles (GPU, ASIC) au coût du front-end que ce benchmark mesure sur CPU seul.
  - [Huang 2019 (revue VIN)](../huang2019_vin-review/fiche.md) — taxonomie filtre/optimisation complémentaire de la Sec. II.
  - [Project Aria](../engel2023_project-aria/fiche.md) — VIO embarqué Meta avec dérive en % de distance, comparaison la plus proche du Quest.
  - [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — mesure de la précision du tracking des casques VR avec vérité terrain.
  - [Dossier Oculus Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) — ce que Meta dit de son VI-SLAM (multithreading, DSP).
  - [3DGS](../kerbl2023_3dgs/fiche.md), [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md) — consommateurs des poses ; voir aussi [Tosi 2024 (survey NeRF/GS-SLAM)](../tosi2024_nerf-gs-slam-survey/fiche.md) et [Photo-SLAM](../huang2024_photo-slam/fiche.md) pour le couplage SLAM → GS.
