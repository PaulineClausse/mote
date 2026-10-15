---
citekey: engel2023_project-aria
mineru_doc: 4a94d35
type: rapport technique (arXiv, cs.HC)   # description d'un dispositif de recherche + services de perception
statut: fiche complète
tags: [project-aria, meta-reality-labs, vio, vi-slam, open-loop, closed-loop, imu-1khz, cameras-monochromes, global-shutter, fisheye, calibration-usine, calibration-en-ligne, nuage-semi-dense, mps, horodatage, egocentrique, ar-glasses, piste-mote, quest-3s]
---

# Project Aria: A New Tool for Egocentric Multi-Modal AI Research

**Référence :** Jakob Engel, Kiran Somasundaram, Michael Goesele, Albert Sun, Alexander Gamino, Andrew Turner, … , Raul Mur-Artal, … , Kevin Eckenhoff, … , Tassos Mourikis, Thomas Whelan, … , Mingfei Yan, Carl Ren, Renzo De Nardi, Richard Newcombe (Meta Reality Labs Research) (2023). *Project Aria: A New Tool for Egocentric Multi-Modal AI Research.* Rapport technique, arXiv [2308.13561](https://arxiv.org/abs/2308.13561) v3 (cs.HC, 1 oct. 2023), 10 p. Pas de DOI, pas de venue avec comité de lecture. Code public : outils `projectaria_tools` (C++/Python, `pip install projectaria_tools`) sur https://github.com/facebookresearch/projectaria_tools ; documentation https://facebookresearch.github.io/projectaria_tools/ ; **les algorithmes de perception (MPS) sont propriétaires et exécutés sur les serveurs Meta**, seules leurs sorties sont publiques (`doc:4a94d35/tier:standard/page:1`, `page:6`, `page:9`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Description par Meta Reality Labs des lunettes de recherche Project Aria (deux caméras SLAM monochromes global-shutter 640×480 à 150° HFOV, deux IMU à 800 Hz et 1 kHz, caméra RGB, capteurs calibrés en usine et horodatés sur une horloge commune) et des **Machine Perception Services** qui en recalculent hors ligne les trajectoires 6DoF : une odométrie **open loop à 1 kHz, causale et « real-time-compatible », dérive ≤ 0,4 % de la distance parcourue**, et une trajectoire **closed loop à 1 kHz, RMSE global ≤ 1,5 cm à l'échelle d'une pièce**, accompagnées d'une calibration en ligne et d'un nuage de points semi-dense (`page:3`, `page:6`, `page:7`).

## Problème traité
- Le papier n'est pas un papier de méthode : il décrit un **outil** (matériel + logiciel + services) destiné à fournir à la recherche des données égocentriques « ecologically valid », multi-modales, telles qu'on les attend des futures lunettes AR « all-day wearable » (`page:1`, `page:2`).
- Le constat de départ : les modèles de vision et d'IA entraînés sur le web (DALL·E 2, GPT-4, SAM, CLIP, DINOv2…) « fare comparatively poorly at tasks that involve egocentric data or require structured reasoning and understanding in 3D/4D space » parce que les données égocentriques naturelles n'existent pas sur le web (`page:2`).
- Pour notre axe, l'intérêt est ailleurs : c'est la **seule publication Meta** qui donne des chiffres sur la chaîne capteurs → VIO → SLAM que la même organisation embarque, sous une autre forme, dans les casques Quest (voir le [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md)). Le papier affirme lui-même que ses trajectoires sont produites par un « state-of-the-art VIO and SLAM system – similar to what can be expected on future AR and VR HMD's » (`page:6`).

## Méthode / contributions
### Capteurs (section 2.1, `page:3` ; schéma Fig. 6, `page:5`)
- **Caméras « Mono Scene » (SLAM)** : deux caméras **monochromes, global shutter**, une de chaque côté, **150° HFOV** (× 120° VFOV d'après la Fig. 6), objectifs fisheye **F-Theta**, **640 × 480 px**, orientées vers l'extérieur « to maximize peripheral vision while allowing for some stereo overlap » ; déclarées comme supports du Visual SLAM, avec LSD-SLAM, MSCKF et ORB-SLAM2 cités en références (`page:3`). **Cadence non rapportée** dans le papier (réglée par les « recording profiles », `page:3`, `page:4`).
- **Caméra RGB « POV »** : une seule, **rolling shutter**, 110° HFOV, fisheye F-Theta, jusqu'à **2880 × 2880 px** (8 MP, Fig. 6), à gauche, inclinée d'environ 4° vers le sol (`page:3`, `page:5`). Donc, comme sur Quest, la caméra couleur n'est **pas** une caméra de tracking.
- **Caméras d'eye-tracking** : deux, monochromes, global shutter, 80° DFOV, 320 × 240 px (`page:3`).
- **IMU** : deux unités, une par côté. **Gauche : 800 Hz, saturation 4 g / 500 °/s ; droite : 1000 Hz, 8 g / 1000 °/s.** Modèles volontairement différents « so that their higher-order error behaviors are more likely to be uncorrelated » (`page:3`).
- Autres : 7 microphones (24 bits, jusqu'à 48 kHz), magnétomètre 10 Hz (0,1 µT), baromètre/thermomètre 50 Hz (0,66 Pa / 0,005 °C), GNSS GPS + Galileo 1 Hz, scans Wi-Fi/Bluetooth RSSI à 0,1 Hz (`page:3`).
- **Contraintes** : pas de stabilisation optique ni d'autofocus (« introduces new challenges ») ; l'appareil « is not designed to handle on-device computation workloads » ; 75 g environ, 1–2 h d'autonomie avec le profil nominal ; enregistrer tous les capteurs à leur maximum « is not feasible due to power and bandwidth limitations » (`page:2`, `page:4`). Mémoire : 4 Go RAM, 128 Go UFS, batterie 2,5 Wh (Fig. 6, `page:5`).

### Rigidité et calibration (section 2.3, `page:4`)
- Tous les capteurs sont montés sur un **cadre en magnésium** ; deux grappes rigides gauche/droite, le pont de nez étant la partie la moins rigide (`page:4`).
- **Calibration d'usine** : intrinsèques et extrinsèques de chaque capteur « computed at manufacturing time » ; **calibration en ligne** fournie en plus par MPS « that account for the small deformations/changes that might occur while wearing the glasses » (`page:4`).
- Ampleur mesurée des déformations : retirer les lunettes après port provoque « around **25 arcmin** instantaneous rotational deformation between the left and right Mono Scene cameras (corresponding to roughly **1.5 pixel** shift in the images) » (`page:7`). La Fig. 9 montre une rotation inter-caméras d'environ 15–20 arcmin en main, ~25 arcmin statique, ~40–50 arcmin portée sur la tête (lecture du graphique, `page:7`). Causes citées : température, vieillissement, forces externes (`page:7`).

### Temps et synchronisation (section 2.4, `page:4`)
- Tous les capteurs sont horodatés sur **une horloge locale unique** du dispositif, « essential to combine different modalities » (`page:4`).
- Multi-appareils : timecode **SMPTE LTC** pour une précision élevée, ou **TicSync** sur Wi-Fi pour une précision moindre ; dans les deux cas chaque mesure porte un timestamp local et un timestamp aligné (`page:4`). Aucune valeur de précision d'horodatage chiffrée : **non rapporté**.

### Enregistrement et outils (section 3, `page:6`)
- Application compagnon mobile ; **profils d'enregistrement** qui fixent capteurs actifs, cadence, résolution, format RAW/JPEG (`page:6`).
- Conteneur **VRS** (format ouvert Meta pour flux de capteurs AR) ; toolkit open source `projectaria_tools` (lecture VRS, calibration, lecture des sorties MPS) (`page:6`).

### Machine Perception Services (section 4, `page:6`–`page:7`)
- **Post-traitement sur les serveurs Meta**, algorithmes « proprietary », annoncés avec « superior accuracy and robustness on the recorded data compared to current off-the-shelf open source solutions » (sans comparaison chiffrée) ; les auteurs « expect these capabilities to be provided in a similar form on any future AR device » (`page:6`).
- **Trajectoires (4.1)** : VIO + SLAM utilisant caméras, IMU, GNSS, Wi-Fi et baromètre, en tirant parti « of precise knowledge of the sensor models, timing, and rigidity » ; robuste aux mouvements rapides, à l'éclairage faible ou dynamique, aux occultations partielles des caméras (`page:6`). Deux sorties :
  - **open loop** : odométrie **1 kHz**, « computed strictly causally with a real-time-compatible method », dérive de translation accumulée « no more than **0.4 %** of the distance traveled, and usually significantly less » (`page:6`) ;
  - **closed loop** : trajectoire 1 kHz optimisée hors ligne, repère unique, possibilité de traiter conjointement plusieurs enregistrements dans un repère commun (Fig. 8 : 18 enregistrements d'un même logement), « typical global RMSE translation error of no more than **1.5 cm** in room-scale scenarios » (`page:6`, `page:7`).
- **Calibration en ligne (4.2)** : intrinsèques et extrinsèques **variant dans le temps** des caméras et des IMU, estimées dans MPS (`page:7`).
- **Nuage semi-dense (4.3)** : pistes calculées **causalement** ; nouveaux points créés dans les régions à fort gradient, suivis dans le temps et **entre caméras gauche/droite** par photocohérence affine-invariante de patchs locaux ; les observations 2D ayant servi à trianguler chaque point sont fournies ; le nuage est replacé dans le repère des trajectoires closed loop (`page:7`). Méthode de type « direct / semi-dense » (héritage LSD-SLAM, dont Engel est l'auteur, `page:3`, `page:10`).
- **Regard (4.4)** : rayon 3D par image, erreur médiane 1,5° après calibration personnalisée (`page:7`).

### Applications (section 6, `page:8`–`page:9`)
- **Cartographie long terme et relocalisation (6.1)** : localisation 6DoF « a base requirement for AR/VR world-locked rendering » ; carte construite à partir de **275 enregistrements (175 h) sur 15 mois** dans un bâtiment en construction, pour étudier la relocalisation sous forts changements d'environnement (`page:8`).
- **Reconstruction de scène (6.2)** : Fig. 12 compare deux NeRF (Nerfstudio) à partir d'Aria + poses MPS : enregistrement « carefully curated, hand-held » couvrant bien l'espace vs activité naturelle ; « The resulting difference in quality is clearly visible » (`page:8`). Aucune métrique.
- Hand tracking UmeTrack + nuage MPS pour détecter le contact main/objet (points à 8 cm de la main) (`page:9`).

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| Caméras SLAM | 2 × monochrome global shutter, **640 × 480**, 150° HFOV (× 120° VFOV), fisheye F-Theta, orientées vers l'extérieur avec recouvrement stéréo partiel | `page:3`, `page:5` ; **cadence non rapportée** (profils) |
| Caméra RGB | 1 × rolling shutter, 110° HFOV, ≤ 2880 × 2880 (8 MP), 4° vers le sol | `page:3`, `page:5` |
| IMU | gauche **800 Hz** (4 g, 500 °/s) ; droite **1000 Hz** (8 g, 1000 °/s), modèles différents | `page:3` |
| Autres capteurs | magnéto 10 Hz, baro 50 Hz, GNSS 1 Hz, Wi-Fi/BT 0,1 Hz, 7 micros ≤ 48 kHz | `page:3` |
| Fréquence des poses | **1 kHz** pour l'open loop comme pour la closed loop | `page:6` |
| Dérive open loop (VIO causal) | **≤ 0,4 % de la distance parcourue**, « usually significantly less » | `page:6` ; conditions/dataset non précisés |
| ATE / RMSE closed loop | **≤ 1,5 cm** RMSE de translation global, « typical », à l'échelle d'une pièce | `page:7` ; vérité terrain non précisée |
| Erreur de rotation | **non rapportée** (ni open ni closed loop) | — |
| Déformation inter-caméras | ~25 arcmin ≈ 1,5 px lors du retrait des lunettes ; 15–50 arcmin selon la phase (Fig. 9) | `page:7` |
| Temps par image / latence | **non rapporté** (MPS est un post-traitement serveur ; aucun temps de calcul) | — |
| CPU / mémoire du calcul | **non rapporté** ; dispositif « not designed to handle on-device computation workloads » | `page:2` |
| Matériel du dispositif | ~75 g, 4 Go RAM, 128 Go UFS, batterie 2,5 Wh, 1–2 h d'enregistrement nominal | `page:2`, `page:5` |
| Calibration | usine (intrinsèques + extrinsèques) + en ligne (caméras et IMU, variant dans le temps) | `page:4`, `page:7` |
| Regard | erreur médiane 1,5° après calibration personnalisée | `page:7` |
| Carte long terme | 275 enregistrements, 175 h, 15 mois | `page:8` |
| Qualité de reconstruction (NeRF) | **aucune métrique** (comparaison visuelle, Fig. 12) | `page:8` |
| Comparaison aux SLAM ouverts | « superior accuracy and robustness » **autodéclarée, sans chiffres** | `page:6` |

## Ce que ça dit du tracking du Quest
Rapprochement avec ce que le [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) a établi (VI-SLAM, 4 caméras monochromes + IMU « every millisecond », carte persistante, relocalisation, prédiction, DSP) :

| Élément | Project Aria (ce papier) | Quest 3 / 3S (Insight, sources 2019–2024) | Transposable ? |
|---|---|---|---|
| Caméras de tracking | 2 × mono global shutter 640×480, 150° fisheye, grappes rigides sur cadre magnésium (`page:3`, `page:4`) | 4 × mono/IR, résolution ~400×400 non confirmée, 2 avant + 2 bas | Même famille (monochrome, grand angle, global shutter très probable) ; le Quest a deux caméras de plus donc un recouvrement plus riche. Hypothèse |
| IMU | 2 IMU, 800 Hz et 1 kHz, modèles distincts pour décorréler les erreurs (`page:3`) | cadence « every millisecond » → 1 kHz présumé ; nombre et modèle inconnus | La cadence de pose 1 kHz = cadence IMU dans les deux cas : la pose publiée est une **propagation inertielle** entre deux corrections visuelles |
| Horodatage | horloge unique du dispositif, timestamps alignés pour toutes les modalités (`page:4`) | non documenté | Pour mote : la question ouverte reste la synchronisation entre la pose de tracking et l'image passthrough RGB (Q-03/Q-11) ; Aria montre que Meta sait horodater toutes les modalités sur une horloge commune, donc le problème est de l'ordre de l'API, pas du matériel |
| Calibration | usine + en ligne ; 25 arcmin ≈ 1,5 px de déformation lors du port (`page:4`, `page:7`) | extrinsèques d'usine implicites ; calibration en ligne non documentée | Un casque est plus rigide que des lunettes mais plus lourd : les déformations thermiques/mécaniques existent aussi ; une pose MRUK transformée vers la caméra RGB par des extrinsèques d'usine hérite de ce type d'erreur (ordre de grandeur pixel) |
| Estimateur temps réel | « VIO and SLAM system », open loop causal « real-time-compatible », dérive ≤ 0,4 % (`page:6`) | VI-SLAM Insight, carte persistante, relocalisation, prédiction | Le chiffre 0,4 % est la **meilleure borne publique** sur la dérive d'un VIO Meta ; mais Aria n'exécute pas ce VIO sur l'appareil (post-traitement), donc rien sur le budget CPU/DSP |
| Optimisation globale | closed loop hors ligne, ≤ 1,5 cm RMSE, multi-sessions, fermeture de boucle (`page:6`, `page:7`) | relocalisation sur carte persistante en temps réel, pas de bundle adjustment hors ligne connu | La pose Quest est probablement entre l'open loop et la closed loop : odométrie corrigée par relocalisation, sans optimisation globale a posteriori (hypothèse du dossier) |
| Nuage de points | semi-dense causal, stéréo gauche/droite, observations 2D fournies (`page:7`) | landmarks « high-contrast pixels » (Hesch 2019), non exposés par l'API | Même logique (points à fort gradient, triangulation) ; sur Quest le nuage n'est pas accessible, d'où le recours à COLMAP/SfM ou aux Gaussiennes initialisées autrement |
| Équipe / lignée algorithmique | co-auteurs : Mur-Artal (ORB-SLAM), Mourikis (MSCKF), Eckenhoff (OpenVINS multi-caméras), Engel (LSD-SLAM), Whelan, Newcombe (`page:1`) | équipe Zurich (Zurich Eye) + 13th Lab (dossier) | Les algorithmes ouverts de la base ([ORB-SLAM3](../campos2021_orb-slam3/fiche.md), [OpenVINS](../geneva2020_openvins/fiche.md), [Eckenhoff 2019](../eckenhoff2019_multicam-vins/fiche.md)) sont écrits par les mêmes personnes que la pile Meta : **ce sont les bons proxys** |

**Implication pour la qualité des poses que mote récupère** : si le tracking Quest est de la même famille, la pose exposée par MRUK est (i) une pose inertielle à 1 kHz entre deux mises à jour visuelles, (ii) localement très précise (dérive < 0,4 % sur Aria, soit < 4 mm par mètre parcouru, cohérent avec les 4–6 mm médians du spike SP-0), (iii) **sans garantie d'optimisation globale** : la cohérence entre vues éloignées dans le temps dépend de la relocalisation, pas d'un bundle adjustment. Le raffinement des poses à l'entraînement (H-01) sert donc surtout à absorber les petits résidus locaux et les erreurs d'extrinsèques/de synchronisation RGB, et pas une dérive macroscopique (`page:6`, `page:7`).

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Description Meta la plus détaillée d'une pile capteurs + VIO + SLAM « similar to what can be expected on future AR and VR HMD's » (`page:6`) : spécifications des caméras et IMU (`page:3`), calibration usine/en ligne (`page:4`, `page:7`), horodatage (`page:4`), trajectoires open/closed loop (`page:6`). Cadre les hypothèses du dossier Insight |
| 2. Poses pour 3DGS (piste mote, H-01) | Donne les deux bornes de qualité : 0,4 % de dérive (odométrie causale) et 1,5 cm RMSE (optimisée) (`page:6`, `page:7`). Montre aussi, sur NeRF, que la **trajectoire de capture** (balayage soigné vs activité naturelle) pèse plus que la précision des poses (`page:8`). Le nuage semi-dense MPS est l'analogue du nuage SfM d'initialisation de 3DGS |
| 3. Temps réel et contraintes embarquées | Faible : le VIO est « real-time-compatible » mais exécuté hors ligne sur serveur ; aucune donnée CPU/GPU/DSP, temps par image ou latence (`page:2`, `page:6`). Rappelle seulement les contraintes de puissance et de bande passante qui limitent cadence et résolution (`page:4`) |
| 4. Évaluation (métriques, protocoles, datasets) | Deux métriques réutilisables : dérive relative en % de la distance (open loop) et RMSE de translation global (closed loop) ; mais vérité terrain, datasets et protocole **non décrits**. Aria Pilot Dataset et MPS inclus dans les jeux publics (`page:2`, `page:6`) : source de trajectoires 1 kHz + nuages pour tester un entraînement 3DGS à poses « casque » |

## Pour (vis-à-vis de notre problématique)
- Seule source Meta avec des **chiffres de dérive et d'erreur** pour une pile VIO/SLAM de la famille Insight (`page:6`, `page:7`) ; comble partiellement le « jamais publié » du dossier Insight.
- Spécifications capteurs précises et transposables (monochrome, global shutter, grand angle, IMU 800/1000 Hz, calibration usine) (`page:3`, `page:4`).
- Décrit explicitement la distinction **open loop (causal, temps réel) / closed loop (optimisé)**, utile pour nommer ce que mote reçoit et ce que COLMAP calcule.
- Quantifie un effet souvent négligé : la **déformation mécanique** d'un dispositif porté (25 arcmin ≈ 1,5 px) et la nécessité d'une calibration en ligne (`page:7`).
- Jeux de données et outils ouverts (VRS, `projectaria_tools`, Aria Pilot Dataset) avec trajectoires et nuages MPS : banc d'essai possible sans Quest.
- Les auteurs sont ceux des SLAM ouverts de la base (ORB-SLAM, MSCKF, OpenVINS) (`page:1`) : légitime l'usage de ces systèmes comme proxys du tracking Quest.

## Contre / limites
- **Aucune description algorithmique** du VIO/SLAM (filtre ou optimisation, nombre de points, fenêtre, fermeture de boucle) ; algorithmes « proprietary », serveurs Meta (`page:6`).
- Chiffres **non étayés** : pas de dataset, pas de vérité terrain, pas de protocole, pas d'écart-type ; « typical », « usually significantly less » (`page:6`, `page:7`). Comparaison aux solutions open source purement déclarative.
- Pas d'erreur de rotation, pas de latence, pas de temps de calcul, pas de consommation.
- Aria ≠ Quest : 2 caméras SLAM au lieu de 4, pas de calcul embarqué, VIO exécuté hors ligne ; la transposition reste une hypothèse.
- Cadence des caméras SLAM **non rapportée** dans le papier (seulement « recording profiles »).
- La partie reconstruction (NeRF, Fig. 12) est qualitative, sans métrique ni comparaison de poses (`page:8`).
- Papier daté 2023 (v3) ; les services MPS ont évolué depuis (voir la documentation citée dans le dossier Insight).

## Idées à creuser pour mote
- *Hypothèse (H-01)* : modéliser la pose Quest comme une trajectoire « open loop » : erreur locale ≈ dérive × distance (0,4 % → ~4 mm/m) + bruit ; vérifier sur SP-0 si l'erreur médiane croît avec la distance parcourue depuis le début de la capture, ce qui distinguerait dérive et bruit.
- *Protocole* : évaluer les poses Quest avec les **deux** métriques d'Aria (dérive relative en % de la distance, RMSE global après alignement) plutôt qu'une seule erreur médiane.
- *Extrinsèques et synchronisation* : mesurer l'équivalent du « 25 arcmin ≈ 1,5 px » sur Quest (pose MRUK → caméra RGB) : un décalage de l'ordre du pixel est exactement ce qu'un raffinement de poses à l'entraînement 3DGS peut absorber ; un décalage temporel pose/image (rolling shutter RGB, comme sur Aria) est plus difficile.
- *Banc d'essai de remplacement* : entraîner un 3DGS à partir des trajectoires MPS (closed loop vs open loop) de l'Aria Pilot Dataset pour chiffrer, indépendamment du Quest, la perte liée à des poses odométriques non optimisées.
- *Trajectoire de capture* : l'écart NeRF « curated vs natural » (`page:8`) suggère de guider l'utilisateur de mote (couverture, vitesse) plutôt que de chercher à améliorer encore les poses.
- *Nuage d'initialisation* : le nuage semi-dense causal d'Aria (points à fort gradient suivis entre caméras) est ce qu'il faudrait extraire du casque à la place de COLMAP ; sur Quest il n'est pas exposé, mais une version légère (suivi de coins sur les images passthrough + poses casque) est envisageable côté PC.

## Citations clés
> « Device trajectories are generated by a state-of-the-art VIO and SLAM system – similar to what can be expected on future AR and VR HMD's – followed by offline post-processing and refinement. » (`doc:4a94d35/tier:standard/page:6`)

> « The open loop trajectory is a high frequency (1 kHz) odometry estimation, computed strictly causally with a real-time-compatible method. The accumulated translation drift of this open loop trajectory is no more than 0.4% of the distance traveled, and usually significantly less. » (`doc:4a94d35/tier:standard/page:6`)

> « Closed loop trajectories have a typical global RMSE translation error of no more than 1.5 cm in room-scale scenarios. » (`doc:4a94d35/tier:standard/page:7`)

> « Figure 9 shows an example where taking off the device after wearing causes around 25 arcmin instantaneous rotational deformation between the left and right Mono Scene cameras (corresponding to roughly 1.5 pixel shift in the images). » (`doc:4a94d35/tier:standard/page:7`)

> « Specifically, it is not designed to handle on-device computation workloads. » (`doc:4a94d35/tier:standard/page:2`)

## Liens
- Dossier : [Oculus Insight / Quest 3 et 3S](../../supports/meta2019_oculus-insight-quest/dossier.md) — ce papier en est la « description publique la plus proche » ; les hypothèses de transposition y sont consignées.
- Papiers liés :
  - [ORB-SLAM](../murartal2015_orb-slam/fiche.md), [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — Mur-Artal est co-auteur d'Aria ; ORB-SLAM2 cité comme exemple de Visual SLAM (`page:3`).
  - [OpenVINS](../geneva2020_openvins/fiche.md), [Eckenhoff 2019 multi-caméras](../eckenhoff2019_multicam-vins/fiche.md) — Eckenhoff et Mourikis (MSCKF, cité `page:3`) co-auteurs : lignée filtre MSCKF.
  - [Kuo 2020 multi-cam SLAM](../kuo2020_multicam-slam/fiche.md) — configuration multi-caméras à recouvrement partiel, comme Aria/Quest.
  - [VINS-Mono](../qin2018_vins-mono/fiche.md), [VINS-Fusion](../qin2019_vins-fusion/fiche.md), [Basalt](../usenko2020_basalt/fiche.md), [Kimera](../rosinol2020_kimera/fiche.md) — estimateurs ouverts à comparer aux bornes 0,4 % / 1,5 cm.
  - [Delmerico 2018](../delmerico2018_vio-benchmark/fiche.md) — métriques de dérive et de RMSE pour situer les chiffres Aria.
  - [Navion](../suleiman2019_navion/fiche.md), [Nagy 2020](../nagy2020_faster-than-fast/fiche.md) — contraintes embarquées qu'Aria ne traite pas.
  - [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — mesure indépendante de la précision des casques, complément des chiffres autodéclarés de Meta.
  - [Tosi 2024 NeRF/GS SLAM survey](../tosi2024_nerf-gs-slam-survey/fiche.md), [Photo-SLAM](../huang2024_photo-slam/fiche.md) — chaînes SLAM → radiance field, suite logique de la Fig. 12.
  - [3DGS](../kerbl2023_3dgs/fiche.md) — le nuage semi-dense MPS est l'analogue du nuage SfM d'initialisation.
  - [VRSplat](../tu2025_vrsplat/fiche.md) — côté rendu sur Quest 3 ; Aria couvre le côté capture/poses.
