---
citekey: qin2018_vins-mono
mineru_doc: 1f44f92
type: article de revue   # IEEE Transactions on Robotics 34(4), 2018 ; version ingérée = arXiv 1708.03852v1 (13 août 2017)
statut: fiche complète
tags: [vio, vi-slam, monoculaire, imu, pré-intégration, fenêtre-glissante, marginalisation, initialisation, relocalisation, dbow2, pose-graph-4dof, fermeture-de-boucle, euroc, okvis, tango, ios, drone, temps-réel, cpu, localisation-poses, piste-mote]
---

# VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator

**Référence :** Tong Qin, Peiliang Li, Shaojie Shen (2018). *VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator.* IEEE Transactions on Robotics, vol. 34, n° 4, p. 1004–1020. DOI [10.1109/TRO.2018.2853729](https://doi.org/10.1109/TRO.2018.2853729) (DOI non présent dans la version arXiv ingérée) · arXiv [1708.03852](https://arxiv.org/abs/1708.03852) (v1, 13 août 2017, 17 p.) · code : PC/ROS github.com/HKUST-Aerial-Robotics/VINS-Mono et iOS github.com/HKUST-Aerial-Robotics/VINS-Mobile (`doc:1f44f92/tier:standard/page:1`). Affiliation : Dept. ECE, Hong Kong University of Science and Technology (`page:1`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Système complet d'odométrie visuelle-inertielle **monoculaire** (une caméra + un IMU bas coût) à couplage serré par optimisation non linéaire sur fenêtre glissante, avec initialisation robuste à la volée, calibration extrinsèque caméra-IMU et biais IMU en ligne, relocalisation à couplage serré via DBoW2 et graphe de poses global à **4 DOF** (x, y, z, lacet) ; validé sur EuRoC contre OKVIS, sur 5,62 km de campus, en boucle fermée sur drone (dérive 0,29 %) et porté sur iPhone face à Google Tango, le tout en open source (`page:1`, `page:2`, `page:13`, `page:14`).

## Problème traité
- Une caméra monoculaire seule ne récupère pas l'échelle métrique ; l'ajout d'un IMU rend observables l'échelle, le roulis et le tangage, et comble les pertes de suivi visuel (« illumination change, texture-less area, or motion blur ») (`page:1`).
- Mais le VINS monoculaire est « highly nonlinear » et pose quatre difficultés : (1) **initialisation** sans état connu — « acceleration excitation is needed to make metric scale observable », donc le système ne peut pas démarrer d'un état stationnaire ; (2) **calibration extrinsèque** caméra-IMU ; (3) **traitement de l'IMU** haute fréquence (biais, pré-intégration) ; (4) **dérive long terme**, qui exige fermeture de boucle, relocalisation et optimisation globale dans un budget de calcul borné (`page:1`).
- Constat sur l'état de l'art : les méthodes par optimisation (OKVIS, VI-ORB-SLAM) sont précises mais « few graph-based can achieve real-time performance on resource-constrained platforms, such as mobile phones » ; l'initialisation de VI-ORB-SLAM peut prendre « longer than 10 seconds » pour converger en échelle (`page:2`, `page:3`).

## Méthode / contributions
Pipeline multi-thread (Fig. 2) : prétraitement → initialisation → VIO à fenêtre glissante + relocalisation → graphe de poses 4 DOF ; « Each module has different running rates and real-time guarantees » (`page:3`).
- **Front-end visuel** : suivi KLT des points existants, détection de nouveaux coins (Shi-Tomasi) pour maintenir **100–300 points** par image avec séparation minimale uniforme ; points dé-distordus et projetés sur la **sphère unité** ; rejet d'aberrants RANSAC sur matrice fondamentale. Sélection de keyframes sur deux critères : parallaxe moyenne **compensée en rotation** par intégration courte du gyroscope (pour ne pas confondre rotation pure et translation), et nombre de points suivis sous un seuil (`page:4`).
- **Pré-intégration IMU avec correction de biais** : extension de la formulation sur variété des auteurs [7] en ajoutant la correction a posteriori des biais (accéléromètre et gyroscope modélisés en marche aléatoire) ; termes α, β, γ exprimés dans le repère b_k, covariance et jacobiens propagés récursivement ; si le biais change peu, correction au **premier ordre** (éq. 12) sans re-propagation ; intégration point-milieu dans le code (`page:4`, `page:5`, `page:6`).
- **Initialisation à couplage lâche** : SfM visuel pur dans la fenêtre (cinq points si > 30 points suivis et > 20 px de parallaxe compensée, triangulation, PnP, BA global), puis alignement visuel-inertiel : calibration du biais gyroscope (éq. 15), puis résolution linéaire de vitesses, gravité et **échelle s** (éq. 18–20), raffinement de la gravité à 2 DOF sur son plan tangent (|g| ≈ 9,81 m/s² connu), rotation du repère c_0 vers le monde aligné sur la gravité. Le biais accéléromètre est volontairement ignoré à l'initialisation (couplé à la gravité, inobservable sur une fenêtre courte) (`page:6`, `page:7`).
- **VIO à couplage serré** : état = n keyframes × (p, v, q, b_a, b_g) + extrinsèques caméra-IMU (p_c^b, q_c^b) + m profondeurs inverses ; coût MAP = prior de marginalisation + résidus IMU pré-intégrés (norme de Mahalanobis) + résidus visuels sous norme de **Huber** (éq. 22–23) ; résolu avec **Ceres Solver** (`page:7`, `page:8`).
- **Résidu visuel sur sphère unité** (éq. 25) : projeté sur le plan tangent (2 DOF), valable pour « wide-angle, fisheye or omnidirectional cameras » (`page:8`).
- **Marginalisation** (Fig. 7) : si l'avant-dernière image est une keyframe, on marginalise la plus ancienne (mesures → prior par complément de Schur) ; sinon on jette ses mesures visuelles mais on **garde ses mesures IMU** pré-intégrées, pour préserver la parcimonie et garder des keyframes spatialement séparées (parallaxe, excitation accélérométrique). Les auteurs admettent la fixation précoce des points de linéarisation : « small drifting is acceptable for VIO » (`page:8`, `page:9`).
- **Trois cadences de sortie** : (a) VIO complet à la cadence des keyframes ; (b) **BA mouvement seul** (poses et vitesses des derniers états IMU, profondeurs/extrinsèques/biais constants) pour sortie à la cadence caméra (~30 Hz) : « more than 50 ms » pour le VIO complet sur calculateur embarqué contre « about 5 ms » pour le BA mouvement seul ; (c) **propagation avant IMU** du dernier état VIO pour une sortie à la cadence IMU, utilisée en retour d'état du drone (`page:9`).
- **Détection d'échec et récupération** : trop peu de points suivis, discontinuité de position/rotation entre deux sorties, grand saut de biais ou d'extrinsèques → retour à l'initialisation et **nouveau segment** de graphe de poses (`page:9`).
- **Relocalisation à couplage serré** : DBoW2 sur **500 coins BRIEF supplémentaires** (image brute jetée, descripteurs gardés) ; pas besoin de descripteurs invariants en rotation (ORB) car roulis et tangage sont observables ; rejet d'aberrants en deux étapes (2D-2D fondamentale RANSAC, 3D-2D PnP RANSAC) ; les correspondances retrouvées entrent **directement dans le coût du VIO** (éq. 26), les poses des images de boucle étant constantes, avec contraintes multi-vues si plusieurs boucles (`page:9`, `page:10`, `page:11`).
- **Graphe de poses 4 DOF** : roulis/tangage observables → dérive seulement en (x, y, z, lacet) ; arêtes séquentielles (relatives du VIO, sans norme robuste) et arêtes de boucle (norme de Huber) ; optimisé dans un thread séparé, de façon asynchrone avec la relocalisation ; base de keyframes sous-échantillonnée (keyframes avec boucle conservées, les autres retirées proportionnellement à leur densité spatiale) (`page:11`).

## Résultats chiffrés
| Métrique | Valeur | Conditions (dataset, capteurs, matériel) |
|---|---|---|
| ATE / RMSE sur EuRoC | **Non rapporté en chiffres** : seulement des courbes (Fig. 11–14) ; « VINS-Mono with loop closure has the smallest translation error » ; en VIO pur, « both VINS-Mono and OKVIS have similar accuracy » ; OKVIS meilleur en roulis/tangage (attribué à l'approximation au 1er ordre de la pré-intégration) | EuRoC MH_03_medium et MH_05_difficult ; caméra gauche seule (Aptina MT9V034 global shutter, WVGA mono, 20 FPS), IMU ADIS16448 200 Hz, vérité VICON/Leica ; 100 premières sorties jetées, 150 suivantes pour l'alignement (`page:11`, `page:12`) |
| Robustesse | Initialise « quickly » sur V1_03_difficult (mouvements agressifs, zones sans texture, changements d'éclairage) ; aucun chiffre | EuRoC (`page:12`) |
| Dérive, parcours mixte intérieur/extérieur | OKVIS : [13,80 ; −5,26 ; 7,23] m = **2,36 %** ; VINS sans boucle : [−5,47 ; 2,76 ; −0,29] m = **0,88 %** ; VINS avec boucle : **[−0,032 ; 0,09 ; −0,07] m** ; pas de vérité terrain (alignement visuel Google Maps) | > 700 m, ~10 min, caméra mvBlueFOX-MLC200w 752×480 à 20 Hz + IMU DJI A3 (ADXL278/ADXRS290) 100 Hz, tenu à la main (`page:13`) |
| Très grande échelle | 5,62 km, 710 m × 240 m × 60 m de dénivelé, 1 h 34 ; « almost drift-free » visuellement, aucun chiffre | VI-Sensor Skybotix, images 25 Hz, IMU 200 Hz ; base de keyframes limitée à **2000** ; Intel **i7-4790 @ 3,60 GHz** (`page:13`, `page:14`) |
| Temps par module (Table I) | Thread 1 : détecteur de points **15 ms**, suivi KLT **5 ms**, à **25 Hz** ; Thread 2 : optimisation de fenêtre **50 ms** à **10 Hz** ; Thread 3 : détection de boucle **100 ms**, graphe de poses **130 ms** (cadence non donnée) | i7-4790, jeu campus ; table MinerU extraite sous forme de ligne aplatie en pied de page (`page:14`) |
| Latence VIO vs mouvement seul | VIO complet « more than 50 ms » sur calculateur embarqué ; BA mouvement seul « about 5 ms » → sortie ~30 Hz ; propagation IMU → **100 Hz** sur le drone | (`page:9`, `page:14`) |
| Drone en boucle fermée | 61,97 m, dérive finale [0,08 ; 0,09 ; 0,13] m = **0,29 %** (0,18 m en norme, Fig. 22) ; boucle fermée **désactivée** | fisheye 190° (modèle MEI), i7-5500U @ 3,00 GHz, vérité OptiTrack, « 8 » de 1,0 m de rayon × 4 tours (`page:14`, `page:15`) |
| Mobile (VINS-Mobile) | ~264 m, retour au point de départ avec graphe 4 DOF ; Tango saute en lacet à l'ouverture d'une porte, mais « Tango is more accurate than our implementation especially for local state estimates » ; aucune métrique | iPhone 7 Plus, 640×480 à 30 Hz, IMU InvenSense MP67B 100 Hz, vs Lenovo Phab 2 Pro (Tango, fisheye global shutter) ; iOS ≥ iPhone 6s (`page:2`, `page:14`, `page:15`) |
| Mémoire / CPU % | Non rapporté (seulement : images brutes jetées, descripteurs BRIEF gardés ; base de keyframes bornée) | (`page:9`, `page:11`) |
| Points par image | 100–300 pour le VIO ; + 500 coins BRIEF pour la boucle | (`page:4`, `page:9`) |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Référence canonique du **VIO par optimisation à fenêtre glissante** (famille OKVIS/VINS/Basalt), à opposer aux filtres MSCKF/SR-ISWF ; architecture multi-thread à cadences différentes (front-end 25 Hz, VIO 10 Hz, boucle/graphe asynchrones) qui est le schéma générique des piles embarquées (`page:2`, `page:3`, `page:14`) |
| 2. Poses pour 3DGS (piste mote, H-01) | Donne les ordres de grandeur de la **dérive d'un VIO sans carte** (0,88 % de la distance, soit ~5 m sur 700 m) et de ce que la fermeture de boucle ramène (< 0,1 m) ; montre que les poses « temps réel » sont issues de **trois estimateurs différents** (VIO complet, BA mouvement seul, propagation IMU) de précision décroissante — à savoir laquelle MRUK expose. Les poses VIO sont déjà **métriques et alignées sur la gravité** (contrairement à COLMAP), ce qui simplifie l'étape SfM → 3DGS (`page:7`, `page:9`, `page:13`) |
| 3. Temps réel, contraintes embarquées | Chiffres par module sur CPU desktop et constat qu'un VIO complet dépasse 50 ms sur embarqué ; port iPhone 7 Plus en 640×480 ; aucun GPU ni DSP utilisé (tout CPU, Ceres) (`page:9`, `page:14`) |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole EuRoC (caméra gauche, alignement sur 150 sorties après 100 jetées), dérive finale en % de la longueur, vérité OptiTrack pour le drone ; mais **pas de tableau ATE/RMSE**, pas de latence mesurée, pas de CPU % (`page:12`, `page:13`, `page:14`) |

## Ce que ça dit du tracking du Quest
- **Ressemblances structurelles** avec Oculus Insight (voir [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md)) : VI-SLAM à landmarks épars (coins suivis par KLT ≈ « high-contrast pixels, such as window corners » d'Insight), fusion IMU serrée avec biais estimés en ligne, fermeture de boucle/relocalisation par reconnaissance de lieu, **thread dédié haute fréquence** pour la sortie à la cadence IMU (propagation avant, Sect. VI-F ≈ pose « every millisecond » d'Insight), et sorties asynchrones (carte/graphe en arrière-plan) (`page:3`, `page:9`, `page:11`).
- **Différences** : VINS-Mono est **monoculaire** (une caméra, 20–30 Hz, IMU 100–200 Hz) alors que le Quest fusionne 4 caméras monochromes + IMU ~1 kHz : le Quest n'a pas le problème d'échelle non observable au démarrage ni le besoin d'excitation en accélération (`page:1`) ; VINS-Mono n'a **pas de carte persistante** réutilisable entre sessions (base DBoW2 de descripteurs BRIEF bornée à 2000 keyframes, graphe de poses recréé par segment après échec) alors qu'Insight garde une carte de pièce persistante (`page:9`, `page:11`, `page:14`) ; pas de prédiction de pose pour masquer la latence d'affichage (la propagation IMU sert au contrôle du drone, pas au rendu) ; **tout sur CPU** (Ceres), aucun DSP/SIMD (`page:8`).
- **Implications pour la qualité des poses que mote récupère** : (1) un VIO par optimisation de ce type a une erreur **locale** faible mais une dérive **globale** en (x, y, z, lacet) seulement — roulis et tangage sont ancrés par la gravité (`page:11`) ; sur une capture 3DGS de quelques dizaines de mètres en salle, la dérive attendue d'un VIO sans boucle de l'ordre de 0,3–0,9 % de la distance (`page:13`, `page:14`) est **cohérente avec les 4–6 mm médians du spike SP-0** sur quelques mètres ; (2) les poses **sautent** lors d'une relocalisation ou d'une optimisation de graphe (le passé est corrigé rétroactivement) : si mote enregistre les poses au fil de l'eau, deux images prises de part et d'autre d'une fermeture de boucle sont dans des repères légèrement différents, ce que le raffinement de poses à l'entraînement (H-01) doit absorber ; (3) la pose « caméra » issue d'un BA mouvement seul ou d'une propagation IMU est **plus lissée mais moins précise** que celle du VIO complet — vérifier ce que MRUK publie et à quelle cadence (`page:9`).

## Pour (vis-à-vis de notre problématique)
- Système **complet et ouvert** (PC/ROS et iOS), base de nombreux estimateurs ultérieurs (VINS-Fusion, et la lignée OKVIS/Basalt/OpenVINS pour la comparaison) ; référence de fait pour « ce qu'un VIO embarqué sait faire » (`page:1`, `page:2`).
- Donne des **chiffres de dérive explicites** en % de la distance avec et sans fermeture de boucle, directement comparables à l'écart Quest/COLMAP de SP-0 (`page:13`, `page:14`).
- Décrit précisément la **hiérarchie de sorties temps réel** (VIO 10 Hz, BA mouvement seul 30 Hz, propagation IMU 100 Hz+) et leurs coûts : grille de lecture pour les poses MRUK (`page:9`, `page:14`).
- Résidu sur sphère unité et modèle MEI : compatible avec les caméras **fisheye grand angle** des casques (`page:8`, `page:14`).
- Démonstration AR mobile face à Tango : montre dès 2017 qu'un VIO académique tient sur un téléphone (`page:14`, `page:15`).

## Contre / limites
- **Monoculaire** : échelle inobservable sans excitation, initialisation fragile, « weakly observable or even degenerate conditions » admises en conclusion ; peu représentatif d'un casque multi-caméras (`page:1`, `page:16`).
- **Aucune métrique ATE/RMSE chiffrée** sur EuRoC (courbes seulement) ; comparaison contre un seul concurrent (OKVIS) ; expériences grande échelle sans vérité terrain (Google Maps) (`page:12`, `page:13`).
- Timings uniquement sur **CPU desktop i7** ; le coût sur mobile n'est pas chiffré (« more than 50 ms » sans précision) ; pas de mesure de latence, de CPU % ni de mémoire (`page:9`, `page:14`).
- Pas de **carte persistante** multi-sessions ; relocalisation seulement intra-session (`page:9`, `page:11`).
- Marginalisation à point de linéarisation fixé → sous-optimalité admise par les auteurs ; OKVIS meilleur en roulis/tangage (`page:9`, `page:12`).
- Local : « Tango is more accurate than our implementation especially for local state estimates » — un système industriel calibré (global shutter + IMU synchrone) bat le VIO académique localement, ce qui plaide pour la confiance dans les poses du Quest (`page:15`).
- Version ingérée = **arXiv v1 (2017)** ; la version T-RO 2018 peut différer (numérotation de pages, éventuels chiffres ajoutés).

## Idées à creuser pour mote
- *Hypothèse (H-01)* : traiter les poses Quest comme des **arêtes séquentielles** d'un VIO (précises localement, dérive globale en 4 DOF) et ne raffiner à l'entraînement 3DGS que (x, y, z, lacet) par keyframe, en gardant roulis/tangage fixés par la gravité — réduction du nombre de paramètres libres et prior physique (`page:11`).
- *Hypothèse* : détecter les **sauts de relocalisation** dans le flux de poses MRUK (critère de « large discontinuity in position or rotation between last two estimator outputs », `page:9`) et segmenter la capture en segments à repère cohérent, puis les aligner (Sim(3) ou SE(3)) avant l'entraînement, comme VINS-Mono crée un nouveau segment de graphe après échec.
- *Hypothèse* : sélectionner les images de capture avec le **critère de keyframe de VINS-Mono** (parallaxe compensée en rotation > seuil, nombre de points suivis) plutôt qu'à cadence fixe : évite les images en rotation pure, peu utiles à 3DGS (`page:4`, `page:6`).
- *Hypothèse (évaluation)* : rejouer SP-0 avec un VIO ouvert (VINS-Mono ou VINS-Fusion sur les flux Aria/EuRoC) comme **troisième référence** entre Quest et COLMAP, et rapporter la dérive en % de la distance comme ici (`page:13`).
- *Hypothèse* : exploiter l'**alignement gravité** des poses VIO (z monde = gravité) pour initialiser l'orientation de la scène 3DGS et le plan du sol sans estimation supplémentaire (`page:7`).

## Citations clés
> « For monocular VINS, it is well known that acceleration excitation is needed to make metric scale observable. This implies that monocular VINS estimators cannot start from a stationary condition, but rather launch from an unknown moving state. » (`doc:1f44f92/tier:standard/page:1`)

> « In contrast to the full tightly-coupled monocular VIO, which may cause more than 50ms on state-of-the-art embedded computers, the motion-only visual-inertial bundle adjustment only takes about 5ms to compute. This enables the low-latency camera-rate pose estimation that is particularly beneficial for drone and AR applications. » (`doc:1f44f92/tier:standard/page:9`)

> « Since our visual-inertial setup renders roll and pitch angles fully observable, the accumulated drift only occurs in four degrees-of-freedom (x, y, z and yaw angle). To this end, we ignore estimating the drift-free roll and pitch states, and only perform 4-DOF pose graph optimization. » (`doc:1f44f92/tier:standard/page:11`)

> « The final dirft of VINS-Mono without loop closure is [-5.47, 2.76. -0.29]m, which occupies 0.88% with respect to the total trajectory length, smaller than OKVIS 2.36%. With loop correction. the final drift is bounded to [-0.032, 0.09, - 0.07]m, which is trivial compared to the total trajectory length. » (`doc:1f44f92/tier:standard/page:13`)

> « Admittedly, Tango is more accurate than our implementation especially for local state estimates. However, this experiment shows that the proposed method can run on general mobile devices and have the potential ability to compare specially engineered devices. » (`doc:1f44f92/tier:standard/page:15`, `page:16`)

## Liens
- Papiers liés :
  - [VINS-Fusion](../qin2019_vins-fusion/fiche.md) — successeur stéréo/multi-capteurs du même groupe, même formulation d'optimisation.
  - [ORB-SLAM](../murartal2015_orb-slam/fiche.md) — comparé pour la fermeture de boucle (7 DOF Sim(3) vs 4 DOF ici) et pour l'initialisation VI-ORB-SLAM > 10 s (`page:3`).
  - [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — VI-SLAM multi-cartes avec carte persistante, ce que VINS-Mono n'a pas.
  - [OpenVINS](../geneva2020_openvins/fiche.md), [Basalt](../usenko2020_basalt/fiche.md), [Kimera](../rosinol2020_kimera/fiche.md) — estimateurs ouverts concurrents (filtre MSCKF vs optimisation) ; OKVIS [16] est la baseline directe de ce papier (`page:12`).
  - [Benchmark VIO](../delmerico2018_vio-benchmark/fiche.md) — comparaison indépendante de VINS-Mono sur plateformes embarquées, à utiliser pour les chiffres ATE absents ici.
  - [Project Aria](../engel2023_project-aria/fiche.md) — VIO Meta « open loop » / « closed loop », la description publique la plus proche du tracking Quest.
  - [Multi-cam VINS](../eckenhoff2019_multicam-vins/fiche.md), [Multi-cam SLAM](../kuo2020_multicam-slam/fiche.md) — extension au cas 4 caméras du casque.
  - [Navion](../suleiman2019_navion/fiche.md) — accélération matérielle d'un VIO de même famille.
  - [Revue VIN](../huang2019_vin-review/fiche.md) — pour situer la formulation.
  - [Dossier Oculus Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) — ce qu'on sait du VI-SLAM du Quest.
  - [3DGS](../kerbl2023_3dgs/fiche.md) — consommateur des poses ; [Photo-SLAM](../huang2024_photo-slam/fiche.md), [Survey NeRF/GS-SLAM](../tosi2024_nerf-gs-slam-survey/fiche.md) — couplage SLAM ↔ 3DGS.
  - [VRSplat](../tu2025_vrsplat/fiche.md) — côté rendu sur Quest 3.
