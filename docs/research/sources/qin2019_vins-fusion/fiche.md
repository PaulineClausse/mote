---
citekey: qin2019_vins-fusion
mineru_doc: 062e34d
type: prépublication arXiv   # 7 p., jamais publiée en conférence/revue sous cette forme ; papier « système » derrière le code VINS-Fusion
statut: fiche complète
tags: [vio, vins-fusion, stéréo, imu, optimisation-fenêtre-glissante, graphe-de-facteurs, préintégration-imu, marginalisation, ceres, euroc, okvis, odométrie-locale, multi-capteurs, hkust]
---

# A General Optimization-based Framework for Local Odometry Estimation with Multiple Sensors (VINS-Fusion)

**Référence :** Tong Qin, Jie Pan, Shaozu Cao, Shaojie Shen (2019). *A General Optimization-based Framework for Local Odometry Estimation with Multiple Sensors.* Prépublication arXiv [1901.03638](https://arxiv.org/abs/1901.03638) (v1, 11 janvier 2019), 7 p., HKUST Aerial Robotics Group (Hong Kong University of Science and Technology). Pas de DOI. Code public : https://github.com/HKUST-Aerial-Robotics/VINS-Fusion (`doc:062e34d/tier:standard/page:1`). Papier compagnon, **non ingéré dans la base** : Qin, Cao, Pan, Shen, *A General Optimization-based Framework for Global Pose Estimation with Multiple Sensors*, arXiv 1901.03642 (fusion « globale » avec GPS, annoncée ici comme travail futur, `page:6`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Estimateur d'odométrie locale 6-DoF par optimisation en fenêtre glissante (bundle adjustment sur ~10 images clés, marginalisation par complément de Schur, solveur Ceres) où **chaque capteur est un « facteur » générique** sommé dans une même fonction de coût, démontré avec trois suites visuelles-inertielles (stéréo seule, mono + IMU, stéréo + IMU) sur EuRoC et en extérieur ; les configurations avec IMU surpassent OKVIS sur la plupart des séquences, la stéréo seule dérive et échoue sur les séquences difficiles (`page:1`, `page:5`).

## Problème traité
- Les estimateurs d'état classiques sont conçus pour **un capteur ou une suite de capteurs précise** (vision seule [1]–[5], VIO [6]–[12], LiDAR [13]) et ne se portent pas d'une plateforme à l'autre : stéréo sur véhicule terrestre, mono + IMU sur téléphone, stéréo + IMU sur drone (`page:1`).
- Besoin pratique de **basculer entre combinaisons de capteurs** sur une même plateforme et de **gérer la panne d'un capteur** (retirer le capteur inactif, en ajouter un autre rapidement) (`page:1`, `page:4`).
- Les méthodes à filtre (EKF/MSCKF) linéarisent tôt et sont sensibles à la synchronisation temporelle (une mesure en retard ne peut pas être propagée en arrière) ; les méthodes par optimisation sont plus précises et le « bundle » sert de tampon naturel pour les mesures désordonnées, au prix de la complexité de calcul, d'où la fenêtre glissante avec marginalisation (`page:2`).
- Le papier cible explicitement les applications **VR/AR** parmi ses motivations, et rappelle que l'IMU « is necessary for low-latency pose feedback in real-time applications » (`page:1`).

## Méthode / contributions
- **Graphe de poses à facteurs génériques** : chaque nœud = état à un instant (position, orientation, vitesse…), chaque arête = un facteur dérivé d'une mesure, qui contraint 1, 2 ou plusieurs états (facteur IMU : deux états consécutifs ; facteur landmark visuel : tous les états qui l'observent) (`page:2`). L'estimation est posée comme un MLE à bruits gaussiens → moindres carrés non linéaires (norme de Mahalanobis), c'est-à-dire un bundle adjustment (eq. 2–3, `page:3`).
- **Vecteur d'état** (eq. 1) : poses $(\mathbf{p}_k, \mathbf{R}_k)$ du corps dans le repère monde, + états caméra (profondeur inverse $\lambda_l$ de chaque feature dans sa première image), + états IMU (vitesse, biais accéléro, biais gyro) **omis si l'IMU est absente**. Extrinsèques capteur→corps **calibrées hors ligne et supposées connues** ; le corps est l'IMU (ou la caméra gauche sans IMU) (`page:3`).
- **Facteur caméra** : coins Shi-Tomasi [22] suivis par KLT [23] ; en stéréo, le suiveur apparie aussi gauche↔droite. Résidu de reprojection d'une feature depuis sa première observation vers les images suivantes (eq. 4), valable **dans le temps (gauche→gauche) et dans l'espace (gauche→droite)** ; modèle de projection $\pi_c$ générique (pinhole, omnidirectionnel…) ; covariance constante en pixels issue de la calibration intrinsèque (`page:3`, `page:4`).
- **Facteur IMU** : préintégration sur variété [11, 12] entre deux images (position, vitesse, rotation relatives + propagation de covariance incluant les biais), bruits blancs gaussiens, biais en marche aléatoire ; résidu eq. 5 avec gravité connue (norme ≈ 9,81) (`page:4`).
- **Autres facteurs** : odomètre de roue, LiDAR, radar « can be added into our system without much effort » tant qu'ils s'écrivent en résidu générique ; seuls caméra et IMU sont formulés dans le papier (`page:4`).
- **Optimisation** : linéarisation Gauss-Newton / Levenberg-Marquardt (eq. 6–7), mise à jour sur variété, résolu avec **Ceres Solver** [24] (`page:4`).
- **Marginalisation** par complément de Schur (eq. 8–9) : fenêtre de **dix images clés** ; à l'arrivée d'une nouvelle image clé, les facteurs visuels et inertiels liés à la première image sont marginalisés en un a priori $(\mathbf{H}_p, \mathbf{b}_p)$, et le problème devient un MAP (eq. 10) (`page:4`).
- **Panne capteur** : « we just remove factors of the inactive sensor and add new factors from other alternative sensors » (`page:4`).
- Contributions revendiquées : cadre général multi-capteurs ; démonstration détaillée avec trois suites visuelles-inertielles ; évaluation datasets + réel ; **code open source** (`page:1`, `page:2`).
- **Non couvert** : pas de fermeture de boucle, pas de relocalisation, pas de carte persistante, pas d'initialisation décrite, pas de calibration en ligne — c'est une **odométrie locale** ; la fusion globale (GPS) est renvoyée au travail futur / papier compagnon 1901.03642 (`page:6`).

## Résultats chiffrés
| Métrique | Valeur | Conditions (dataset, capteurs, matériel) |
|---|---|---|
| Capteurs EuRoC | Stéréo Aptina MT9V034 **global shutter, 752 × 480 monochrome, 20 FPS** ; IMU ADIS16448 **200 Hz** synchronisée ; vérité terrain VICON + Leica MS50 | EuRoC MAV, 11 séquences, longueurs 36,34 m (V2_01) à 130,58 m (MH_03) (`page:5`) |
| ATE RMSE [m], **stéréo seule** | 0,20 (V2_02) à 0,78 (MH_04) ; **échec (x) sur V1_03 et V2_03** (« movement is too aggressive for visual tracking to survive ») ; moyenne sur les 9 séquences réussies ≈ 0,42 (calcul fait par nous à partir du tableau I) | Table I, alignement Horn (`page:5`) |
| ATE RMSE [m], **mono + IMU** | **0,06** (V1_01, V2_01) à 0,26 (V2_03) ; moyenne 11 séquences ≈ 0,15 (calcul fait par nous) ; bat OKVIS sur 10/11 séquences (perd MH_01 : 0,18 vs 0,16) | Table I (`page:5`) |
| ATE RMSE [m], **stéréo + IMU** | 0,10 (V1_01, V1_02, V2_02) à 0,39 (MH_04) ; moyenne ≈ 0,19 (calcul fait par nous) ; bat OKVIS sur 8/11 séquences (perd MH_01 0,24 vs 0,16 ; MH_04 0,39 vs 0,34 ; V1_01 0,10 vs 0,09) | Table I (`page:5`) |
| ATE RMSE [m], **OKVIS** (baseline stéréo + IMU) | 0,09 (V1_01) à 0,47 (MH_05) ; moyenne ≈ 0,23 (calcul fait par nous) | Table I (`page:5`) |
| Cas marquant | MH_05 (97,32 m) : stéréo 0,50 / mono+IMU 0,25 / **stéréo+IMU 0,19** / OKVIS 0,47 ; V1_03 (78,77 m) : stéréo x / 0,18 / **0,11** / 0,24 | Table I (`page:5`) |
| RPE (erreur de pose relative, KITTI [26]) | Tracés seulement (Fig. 4 MH_05, Fig. 5 V2_02, Fig. 8 extérieur), **aucune valeur numérique** dans le texte | `page:5`, `page:6` |
| Dérive | Qualitative : en stéréo seule « position and rotation drift obviously grown along with distance » ; l'IMU « can effectively suppress drifts in roll and pitch angles » grâce à l'observation de la gravité | `page:5` |
| Expérience extérieure | Suite maison : stéréo mvBlueFOX-MLC200w **20 Hz** + contrôleur DJI A3 (IMU **200 Hz** + GPS) ; GPS pris comme vérité terrain ; capteur tenu à la main, deux tours en marchant | Fig. 6, `page:6` |
| ATE RMSE [m], extérieur (Table II) | outdoor1 (223,70 m) : stéréo 1,85 / mono+IMU 0,71 / stéréo+IMU **0,52** · outdoor2 (229,91 m) : 2,35 / 0,56 / **0,43** · outdoor3 (232,13 m) : 2,59 / **0,65** / 0,75 | `page:6` |
| Fréquence de sortie (Hz) | **Non rapportée** (seulement cadence des caméras 20 Hz et IMU 200 Hz) | — |
| Temps par image / latence | **Non rapportés** | — |
| CPU / mémoire / matériel d'exécution | **Non rapportés** (ni plateforme de calcul, ni nombre de threads) | — |
| Taille de la fenêtre | 10 images clés (« ten spacial camera frames ») | `page:4` |

Lecture du tableau I : la **stéréo + IMU n'est pas toujours la meilleure** ; les auteurs l'attribuent au fait qu'elle « requires more accurate calibration than the case of a monocular camera with an IMU. Inaccurate intrinsic and extrinsic calibration will introduce more noise into the system » (`page:5`).

## Ce que ça dit du tracking du Quest
- **Même famille d'estimateur, périmètre plus étroit.** VINS-Fusion est un VIO par optimisation en fenêtre glissante : BA sur 10 images clés + a priori marginalisé (`page:4`). Oculus Insight est décrit par Meta comme un VI-SLAM à landmarks avec **carte persistante, relocalisation et mises à jour asynchrones** (cf. [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md)) ; VINS-Fusion n'a ici **ni carte, ni fermeture de boucle, ni relocalisation** — il correspond à la couche « odométrie locale » du casque, l'équivalent de la trajectoire *open loop* d'Aria. Sa dérive croît donc avec la distance (`page:5`), ce que la carte du casque est censée corriger.
- **Le rôle de l'IMU est exactement celui qu'invoque Meta.** Le papier montre numériquement ce que Meta affirme sans chiffre : la vision seule échoue sur les mouvements agressifs (V1_03, V2_03) et dérive ; l'IMU « bridg[es] the gap when visual tracks fail due to illumination change, textureless area, or motion blur » et rend roll/pitch observables par la gravité (`page:5`). Sur un casque, les mouvements rapides de tête sont la norme : l'IMU est la raison pour laquelle le tracking survit aux rotations rapides.
- **Capteurs très comparables.** EuRoC = caméras **monochromes global shutter 752 × 480 à 20 FPS** + IMU 200 Hz (`page:5`) ; Quest = 4 caméras monochromes/IR basse résolution + IMU (cadence « every millisecond » selon Meta, soit ~1 kHz, non documentée). La différence de cadence IMU (200 Hz vs ~1 kHz) ne change pas la formulation : la préintégration absorbe « multiple IMU measurements existing between two frames » (`page:4`).
- **Multi-caméras.** Le facteur caméra est « universal for both left camera and right camera » ; il suffit d'une extrinsèque $\mathbf{T}_b^c$ par caméra (`page:3`, `page:4`). Les 4 caméras du Quest s'écrivent donc naturellement comme 4 facteurs de reprojection dans ce cadre (sans que le papier traite de caméras asynchrones ou à faible recouvrement, cf. [Kuo 2020](../kuo2020_multicam-slam/fiche.md), [Eckenhoff 2019](../eckenhoff2019_multicam-vins/fiche.md)).
- **Sensibilité à la calibration.** La stéréo + IMU ne gagne que si intrinsèques/extrinsèques sont précises (`page:5`). Le Quest bénéficie d'une calibration d'usine (et probablement en ligne, non documentée) ; mote récupère une pose corps→caméra RGB passthrough via des extrinsèques d'usine : la même source d'erreur (extrinsèques) pèse directement sur les poses « caméra » que mote utilise.
- **Latence et prédiction : hors champ.** Le papier mentionne la pose « low-latency » comme motivation (`page:1`) mais ne rapporte **aucun temps de calcul, aucune fréquence de sortie, aucune latence**, et ne traite pas la prédiction de pose ; rien sur le DSP ou le multithreading. Sur ces points, il ne dit rien du Quest.
- **Implication pour la qualité des poses mote** : les poses MRUK sont au mieux celles d'un VIO de cette classe + corrections de carte. Ordre de grandeur de référence : **6–27 cm d'ATE RMSE** sur 36–131 m de trajectoire EuRoC pour une VIO sans carte (`page:5`) ; à l'échelle d'une pièce (quelques mètres, SP-0), l'erreur locale est bien plus faible, et c'est la **cohérence locale inter-images** (RPE), non l'ATE globale, qui compte pour un 3DGS.

## Pertinence pour notre sujet
| Axe | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Référence de la famille « VIO par optimisation en fenêtre glissante » (avec OKVIS [8], VINS-Mono [12], Basalt) face aux filtres MSCKF (OpenVINS) ; formalisme graphe de facteurs générique, marginalisation Schur, Ceres (`page:2`–`page:4`). Explique sans chiffre de calcul ce que fait la couche odométrique du casque. |
| 2. Poses pour 3DGS (piste mote, H-01) | Fournit un ordre de grandeur de la précision d'un VIO ouvert sur caméras monochromes + IMU : ATE 0,06–0,27 m sur EuRoC (`page:5`), 0,43–0,75 m sur ~230 m en extérieur (`page:6`). Montre que l'IMU supprime la dérive roll/pitch, mais que position et yaw dérivent sans carte → justifie le raffinement des poses à l'entraînement (H-01) et l'usage de la carte persistante du casque. Les poses sont exprimées **au corps (IMU)** ; mote doit appliquer les extrinsèques vers la caméra RGB (`page:3`). |
| 3. Temps réel et contraintes embarquées | **Rien de chiffré** (ni Hz, ni ms, ni CPU). Apports structurels seulement : fenêtre bornée à 10 images clés pour borner la complexité (`page:4`), optimisation ≈ coût quadratique sans bornage (`page:2`). Pour les coûts réels, voir [Delmerico 2018](../delmerico2018_vio-benchmark/fiche.md), [Navion](../suleiman2019_navion/fiche.md). |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole standard réutilisable : EuRoC MAV (11 séquences, VICON/Leica), ATE RMSE après alignement Horn [28], RPE à la KITTI [26] (`page:5`) ; expérience réelle avec GPS comme vérité terrain (`page:6`). Pas de métrique de jitter, de latence ni de qualité d'image. |

## Pour (vis-à-vis de notre problématique)
- Code open source, largement utilisé : baseline VIO stéréo + IMU **directement exécutable sur PC** pour comparer une trajectoire ouverte à celle du casque (`page:1`).
- Démonstration numérique claire du bénéfice de l'IMU (survie aux mouvements agressifs V1_03/V2_03, dérive roll/pitch supprimée) — argument pour faire confiance au tracking inertiel du casque plutôt qu'à une SfM purement visuelle sur des images de tête (`page:5`).
- Formalisme extensible : tout capteur modélisable en résidu (y compris, pour nous, des contraintes photométriques 3DGS ou des poses casque comme facteurs a priori) (`page:4`).
- Les capteurs d'EuRoC (monochrome global shutter basse résolution + IMU) ressemblent aux caméras de tracking du Quest : les résultats sont transférables en ordre de grandeur (`page:5`).

## Contre / limites
- **Aucune mesure de performance** : pas de fréquence de sortie, temps par image, CPU, mémoire, latence, plateforme (`page:5`, `page:6`). Impossible d'en tirer un budget embarqué.
- **Odométrie locale uniquement** : pas de fermeture de boucle, relocalisation ni carte ; la dérive n'est pas quantifiée en fonction de la distance (RPE seulement en figures, `page:5`, `page:6`).
- Vérité terrain extérieure = **GPS** (précision métrique), donc Table II peu discriminante (`page:6`).
- Extrinsèques et intrinsèques supposées connues et calibrées hors ligne, pas de calibration en ligne (`page:3`) ; la configuration stéréo + IMU y est sensible (`page:5`).
- Initialisation, sélection d'images clés, gestion des outliers, synchronisation effective des horloges : non décrits (le papier renvoie à VINS-Mono [12] pour la préintégration, `page:4`).
- Papier court (7 p.), jamais revu par les pairs sous cette forme ; les apports méthodologiques sont minces par rapport à VINS-Mono (le cadre « général » est surtout une généralisation d'implémentation).

## Idées à creuser pour mote
- *Hypothèse (mesure)* : faire tourner VINS-Fusion stéréo + IMU **sur un dataset de type EuRoC** et sur nos propres captures (si on obtient des images de tracking + IMU, ce que Quest n'expose pas) pour situer la pose MRUK entre « VIO ouverte sans carte » et « COLMAP » ; à défaut, utiliser EuRoC comme borne haute de l'erreur attendue d'un VIO (0,06–0,27 m ATE, `page:5`).
- *Hypothèse (H-01)* : la carte persistante du casque corrige la dérive de position/yaw que ce papier met en évidence ; vérifier sur SP-0 que l'erreur Quest vs COLMAP **ne croît pas avec la distance parcourue** (test direct de « odométrie + carte » vs « odométrie seule »).
- *Hypothèse (raffinement de poses)* : reprendre le formalisme « facteur générique » : poses casque = facteur a priori (covariance à estimer), résidu photométrique 3DGS = facteur image ; l'optimisation conjointe poses/Gaussiennes devient un BA à facteurs hétérogènes, à la VINS-Fusion (`page:3`, `page:4`).
- *Hypothèse (extrinsèques)* : comme la stéréo + IMU se dégrade avec une mauvaise calibration (`page:5`), estimer ou raffiner l'extrinsèque corps→caméra RGB passthrough du Quest dans l'entraînement 3DGS (un seul paramètre rigide partagé par toutes les vues), plutôt que de corriger chaque pose indépendamment.
- *Hypothèse (évaluation)* : adopter le couple ATE RMSE (Horn) + RPE KITTI du papier (`page:5`) comme métriques de poses de mote, en ajoutant le jitter image-à-image et l'impact sur PSNR/LPIPS du 3DGS, absents ici.

## Citations clés
> « Every sensor is treated as a general factor in our framework. Factors which share common state variables are summed together to build the optimization problem. » (`doc:062e34d/tier:standard/page:1`)

> « The IMU can measure acceleration and angular velocity at a high frequency, which is necessary for low-latency pose feedback in real-time applications. » (`doc:062e34d/tier:standard/page:1`)

> « To be specific, we keep ten spacial camera frames in our system. When a new keyframe comes, we marginalize out the visual and inertial factors, which are related with states of the first frame. » (`doc:062e34d/tier:standard/page:4`)

> « The stereo-only case fails in V1 03 difficult and V2 03 difficult sequences, where the movement is too aggressive for visual tracking to survive. Methods which involves the IMU work successfully in all sequences. It is a good case to show that the IMU can dramatically improve motion tracking performance by bridging the gap when visual tracks fail due to illumination change, textureless area, or motion blur. » (`doc:062e34d/tier:standard/page:5`)

> « Stereo cameras with an IMU didn't always perform best, because it requires more accurate calibration than the case of a monocular camera with an IMU. Inaccurate intrinsic and extrinsic calibration will introduce more noise into the system. » (`doc:062e34d/tier:standard/page:5`)

## Liens
- Papiers liés :
  - [VINS-Mono](../qin2018_vins-mono/fiche.md) — prédécesseur direct (réf. [12]) : préintégration IMU, marginalisation, initialisation ; VINS-Fusion en généralise le code à la stéréo et au multi-capteurs (`page:4`).
  - [ORB-SLAM](../murartal2015_orb-slam/fiche.md), [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — alternative avec carte persistante, relocalisation et fermeture de boucle, ce que VINS-Fusion n'a pas (réf. [4], [10]).
  - [OpenVINS](../geneva2020_openvins/fiche.md) — approche filtre MSCKF (réf. [6], [7]), avec calibration en ligne, à opposer à l'optimisation en fenêtre glissante (`page:2`).
  - [Basalt](../usenko2020_basalt/fiche.md), [Kimera](../rosinol2020_kimera/fiche.md) — autres VIO par optimisation ; OKVIS [8] est la baseline comparée ici (`page:5`).
  - [Kuo 2020](../kuo2020_multicam-slam/fiche.md), [Eckenhoff 2019](../eckenhoff2019_multicam-vins/fiche.md) — extension aux multi-caméras arbitraires (le facteur caméra « universel » de VINS-Fusion en est le point de départ, `page:3`).
  - [Delmerico 2018](../delmerico2018_vio-benchmark/fiche.md) — benchmark VIO embarqué qui fournit les temps de calcul absents ici ; [Navion](../suleiman2019_navion/fiche.md), [Nagy 2020](../nagy2020_faster-than-fast/fiche.md) — contraintes CPU/ASIC/SIMD.
  - [Huang 2019 (revue VIN)](../huang2019_vin-review/fiche.md) — situe filtres vs optimisation.
  - [Project Aria](../engel2023_project-aria/fiche.md) — VIO embarqué Meta (open loop) et SLAM hors ligne (closed loop), équivalent industriel de la séparation local/global de VINS-Fusion et de son papier compagnon.
  - [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — mesures de précision du tracking de casques VR, à comparer aux ATE EuRoC.
  - [3DGS](../kerbl2023_3dgs/fiche.md), [Tosi 2024 (survey NeRF/GS-SLAM)](../tosi2024_nerf-gs-slam-survey/fiche.md), [Photo-SLAM](../huang2024_photo-slam/fiche.md) — côté consommateur des poses : SLAM couplé à une représentation gaussienne.
- Support : [dossier Oculus Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) — ce que Meta publie sur le tracking Quest.
