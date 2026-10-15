---
citekey: huang2024_photo-slam
mineru_doc: eb406be
type: conférence   # CVPR 2024 ; le PDF ingéré est la version arXiv 2311.16728v2 (8 avril 2024)
statut: fiche complète
tags: [slam, 3dgs, gaussian-splatting, orb-slam3, hyper-primitives, tracking-découplé, densification-géométrique, pyramide-gaussienne, monoculaire, stéréo, rgb-d, replica, tum-rgbd, euroc, jetson-agx-orin, rtx-4090, temps-réel, embarqué, loop-closure, poses-pour-3dgs, piste-mote]
---

# Photo-SLAM: Real-time Simultaneous Localization and Photorealistic Mapping for Monocular, Stereo, and RGB-D Cameras

**Référence :** Huajian Huang (HKUST), Longwei Li (Sun Yat-sen Univ.), Hui Cheng (Sun Yat-sen Univ.), Sai-Kit Yeung (HKUST) (2024). *Photo-SLAM: Real-time Simultaneous Localization and Photorealistic Mapping for Monocular, Stereo, and RGB-D Cameras.* Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR 2024). arXiv [2311.16728v2](https://arxiv.org/abs/2311.16728) (8 avril 2024) · DOI : non rapporté dans le PDF (version arXiv) · code et page projet : [huajianup.github.io/research/Photo-SLAM/](https://huajianup.github.io/research/Photo-SLAM/) (`doc:eb406be/tier:standard/page:1`)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Un SLAM « hybride » où un **tracker géométrique classique (ORB-SLAM3 : points ORB, BA par graphe de facteurs, fermeture de boucle)** fournit poses et points épars dans des threads séparés, pendant qu'un thread de « photorealistic mapping » transforme ces points en **hyper primitives** (Gaussiennes 3D portant aussi leur descripteur ORB) et les optimise par 3DGS, avec une densification pilotée par les points 2D non triangulés et un entraînement progressif par pyramide gaussienne ; résultat : tracking à ~42 Hz sur RTX 4090 et ~18 Hz sur Jetson AGX Orin, rendu à ~900–1000 FPS, PSNR 33–35 dB sur Replica avec 4–6 Go de GPU (`page:1`, `page:2`, `page:6`).

## Problème traité
- Les SLAM « neuronaux » (iMAP, Nice-SLAM, ESLAM, Co-SLAM, Point-SLAM, Go-SLAM) optimisent conjointement poses et représentation implicite par échantillonnage de rayons : « so resource-hungry that they cannot run on portable devices, which deviates from the original intention of SLAM » (`page:1`). Ils ont besoin d'une profondeur (RGB-D, flot dense, estimateur mono) pour converger, et d'une zone bornée pour normaliser l'échantillonnage, ce qui limite la scalabilité (`page:1`, `page:2`).
- L'optimisation conjointe pose + géométrie implicite est « still ill-conditioned » (`page:3`).
- Le passage à un rendu 3DGS ne suffit pas : « it does not enable the generation of high-fidelity rendering for online incremental mapping, in particular in monocular scenarios » (`page:2`), d'où les deux contributions (densification géométrique, apprentissage par pyramide).
- Objectif : localisation précise + cartographie photoréaliste **en ligne**, mono / stéréo / RGB-D, intérieur et extérieur, sur plateforme embarquée (`page:2`).

## Méthode / contributions

### Architecture : quatre threads découplés autour d'une carte d'hyper primitives
- Quatre composants, **chacun dans un thread parallèle** : localisation, cartographie géométrique explicite, cartographie photoréaliste implicite, fermeture de boucle ; tous partagent la carte d'hyper primitives (Fig. 2b) (`page:2`, `page:3`).
- **Hyper primitive** = point 3D P ∈ R³ + descripteur ORB o ∈ R²⁵⁶ + rotation r ∈ SO(3) + échelle s ∈ R³ + densité σ ∈ R + coefficients SH ∈ R¹⁶ (`page:3`). Une seule structure sert donc à la fois de landmark SLAM (via ORB) et de Gaussienne 3D (via r, s, σ, SH).
- Implémentation entièrement C++ / CUDA, assemblée à partir d'ORB-SLAM3, du rasteriseur 3DGS et de LibTorch (`page:2`, `page:5`).

### Tracking et géométrie : ORB-SLAM3 tel quel, aucun rendu dans la boucle
- Initialisation : triangulation à partir de correspondances 2D-2D entre images adjacentes, puis tracking par correspondances 2D-3D (`page:3`).
- **Localisation** : BA « motion-only » sur (R, t) par Levenberg–Marquardt, minimisant l'erreur de reprojection des points ORB avec coût robuste de Huber (éq. 1) (`page:3`).
- **Cartographie géométrique** : BA local sur les points covisibles P_L et les keyframes K_L, keyframes voisines K_F fixées (éq. 2) ; crée incrémentalement des hyper primitives éparses (`page:3`).
- **Fermeture de boucle** : correction des keyframes locales et des hyper primitives par une transformation de similarité ; « With corrected camera poses, the photorealistic mapping component can further get rid of the ghosting caused by odometry drifts » (`page:5`).
- Point essentiel pour nous : la pose **n'est jamais raffinée par le rendu**. Le thread photoréaliste optimise uniquement P, r, s, σ et SH par la perte photométrique L1 + SSIM (éq. 4, λ = 0,2) ; les poses des keyframes sont des entrées fixes de la rasterisation (éq. 3) (`page:4`, `page:5`).

### Initialisation des Gaussiennes depuis les points ORB et densification géométrique
- Les Gaussiennes naissent **directement des points triangulés** par le thread géométrique ; le thread photoréaliste « progressively optimizes and densifies hyper primitives » (`page:3`).
- Densification classique (split / clone sur gradient de perte élevé, comme 3DGS) **plus** une densification géométrique : constat expérimental que « less than 30% of 2D geometric feature points of frames are active and have corresponding 3D points, especially for non-RGB-D scenarios » (Fig. 4) (`page:4`). Les points 2D « inactifs » (détectés mais non triangulés) marquent des régions texturées : à chaque création de keyframe, des hyper primitives **temporaires** sont créées à partir d'eux (`page:4`).
- Profondeur de ces points inactifs : RGB-D → projection directe avec la profondeur ; **monoculaire → interpolation de la profondeur des points actifs voisins** ; stéréo → appariement stéréo (`page:4`).

### Entraînement progressif par pyramide gaussienne (GP learning)
- Revue des schémas progressifs (NSVF/DVGO : résolution de grille croissante ; NGLoD : encodeurs multiples ; Neuralangelo : activation progressive des niveaux de hash ; BungeeNeRF : images multi-résolution explicites, « not universal since multi-resolution images are not available for most scenarios ») (Fig. 3) (`page:4`, `page:5`).
- Proposition : construire une pyramide gaussienne de l'image cible ; au début, supervision par le niveau le plus grossier n ; au fil des itérations, densification **et** descente d'un niveau jusqu'à l'image pleine résolution (éq. 5) (`page:5`). Trois niveaux (n = 2) par défaut, choisis d'après la résolution des jeux de test (`page:5`).
- Effet revendiqué : « GP learning significantly improves the performance of photorealistic mapping particularly for monocular cameras » (`page:5`) ; sans GP, les primitives densifiées sans profondeur précise « have inaccurate positions » et deviennent des « encumbrances » (`page:8`).

## Résultats chiffrés
Protocole : RTX 4090 24 Go + i9-13900K + 64 Go pour toutes les méthodes (code officiel) ; « Ours (Laptop) » = RTX 3080 Ti Laptop 16 Go + i9-12900HX + 32 Go ; « Ours (Jetson) » = Jetson AGX Orin Developer Kit ; chaque séquence exécutée **5 fois** et moyennée ; rendu à **1200 × 680** (`page:5`, `page:6`).

| Métrique | Valeur | Conditions |
|---|---|---|
| ATE RMSE (Replica, mono) | **Ours 1,091 cm** (STD 0,892) · Laptop 0,713 · Jetson 1,235 ; ORB-SLAM3 3,942 ; DROID-SLAM 0,725 ; Go-SLAM 71,054 ; Nice-SLAM* (sans profondeur) ≈ 99,9 | moyenne 8 scènes, Table 1 (`page:6`) |
| ATE RMSE (Replica, RGB-D) | **Ours 0,604 cm** (STD 0,298) · Laptop 0,590 · Jetson 0,581 ; ORB-SLAM3 1,833 ; DROID-SLAM 0,634 ; ESLAM 0,568 ; Go-SLAM 0,571 ; Point-SLAM 0,596 ; Co-SLAM 1,158 | Table 1 (`page:6`) |
| ATE RMSE (TUM, mono) | fr1-desk 1,539 / fr2-xyz 0,984 / fr3-office 1,257 cm (ORB-SLAM3 : 1,534 / 0,720 / 1,400 ; DROID-SLAM : 78,2 / 36,1 / 154,4) | Table 2 (`page:7`) |
| ATE RMSE (TUM, RGB-D) | 2,603 / 0,346 / 1,001 cm (Jetson : 4,571 / 0,360 / 1,874) | Table 2 (`page:7`) |
| ATE RMSE (EuRoC, stéréo) | MH-01 4,109 · MH-02 4,441 · V1-01 8,821 · V2-01 26,609 cm (ORB-SLAM3 : 4,379 / 4,525 / 8,940 / 26,904) ; PSNR 13,95–17,07 dB | Table 3 (`page:7`) |
| Erreur de rotation | colonne « Rotation RMSE » : ex. office0 mono desktop 0,00369, RGB-D 0,00307 (unité non précisée) | Table 8 (`page:13`) |
| Dérive | non mesurée séparément ; fermeture de boucle active (pic de temps de tracking à la détection de boucle) | `page:5`, `page:11` |
| Qualité (Replica, mono) | **PSNR 33,302 / SSIM 0,926 / LPIPS 0,078** ; Jetson 29,284 / 0,883 / 0,139 ; Orbeez-SLAM 23,246 ; Go-SLAM 21,172 | Table 1 (`page:6`) |
| Qualité (Replica, RGB-D) | **34,958 / 0,942 / 0,059** ; Point-SLAM 34,632 / 0,927 / 0,083 ; ESLAM 30,594 ; Co-SLAM 30,246 ; Orbeez 32,516 | Table 1 (`page:6`) |
| Qualité (TUM, mono) | PSNR 20,972 / 21,072 / 19,591 (fr1 / fr2 / fr3) | Table 2 (`page:7`) |
| **Tracking FPS** | Replica mono : **41,646** (desktop) · 19,974 (laptop) · **18,315 (Jetson)** ; RGB-D : 42,485 / 20,597 / 17,926 ; ORB-SLAM3 seul 58,749 (mono) / 52,209 (RGB-D) ; ESLAM 6,687 ; Co-SLAM 14,575 ; Point-SLAM 0,345 | Table 1 (`page:6`) |
| Tracking FPS (TUM) | fr1-desk mono 57,78 (desktop) / 28,33 (laptop) / 28,27 (Jetson) ; fr3-office mono 81,58 / 38,93 / 36,70 ; RGB-D fr3-office 43,65 / 19,64 / 18,04 | Table 6 (`page:12`) |
| Tracking FPS (EuRoC stéréo) | desktop 44,8–48,9 ; laptop 25,0–27,6 ; Jetson 21,3–23,9 | Table 7 (`page:12`) |
| Stabilité du tracking | « more than 40 frames per second » ; ≈ 6× plus rapide qu'ESLAM et 3× que Co-SLAM ; Go-SLAM prend « about 1 second » par image lors des optimisations globales ; Photo-SLAM a le temps moyen et l'écart-type minimaux, pics à la fermeture de boucle | Fig. 12, office0 RGB-D (`page:11`) |
| **Rendu FPS** | Replica mono **911,262** (desktop) · 353,504 (laptop) · **95,057 (Jetson)** ; RGB-D 1084,017 / 396,082 / 116,395 ; « about three hundred times faster » que ESLAM / Go-SLAM ; Nice-SLAM 0,611, ESLAM 2,626, Co-SLAM 3,745 | 1200×680, Table 1 (`page:6`) |
| Rendu FPS (TUM, EuRoC) | TUM fr1-desk mono 2016,7 / 1105,1 / 340,5 ; EuRoC Jetson 93,8–106,0, desktop 595–835 | Tables 6–7 (`page:12`) |
| Temps de reconstruction (« Operation Time ») | **< 2 min** (desktop), < 5 min (laptop, Jetson) ; Nice-SLAM > 10 min, Point-SLAM > 2 h | Replica, Table 1 (`page:6`) |
| **Mémoire GPU** | **6 Go (mono) / 5 Go (RGB-D)** desktop ; **4 Go** sur laptop et **sur Jetson** ; ORB-SLAM3 0 Go (CPU) ; Nice-SLAM 12 Go ; ESLAM 21 Go ; Go-SLAM 22–24 Go ; Point-SLAM 24 Go | Table 1 (`page:6`) |
| Taille du modèle | Replica mono 31,419 Mo / RGB-D 35,211 Mo ; TUM 4,6–21,4 Mo ; EuRoC 27,8–123,5 Mo (Jetson plus petit : 27,8–43,4 Mo) | Tables 5–7 (`page:12`) |
| CPU | non rapporté (seule la charge GPU est mesurée) | — |
| Latence capteur → pose | non rapportée (seul le temps de traitement par image, Fig. 12) | `page:11` |
| Ablation Geo / GP (Replica mono) | défaut (Geo + GP n=2) PSNR 33,302 / 911,3 FPS / 31,4 Mo ; sans Geo 31,274 (−2,028) ; sans GP 20,002 / 353 FPS / 44,1 Mo ; ni l'un ni l'autre 22,913 ; GP n=1 30,903 ; n=3 31,563 (dégradation, « possibly due to overfitting low-level features ») | Table 4 (`page:8`) |
| Ablation Geo / GP (RGB-D) | défaut 34,958 ; sans Geo 33,296 (−1,662) ; sans GP 33,696 ; ni l'un ni l'autre 32,551 | Table 4 (`page:8`) |
| **3DGS hors ligne sur les poses Photo-SLAM** (même durée d'entraînement) | init 100 pts aléatoires : PSNR 27,844, 745 FPS, 36 Mo ; 10 000 pts aléatoires : 34,555, 484 FPS, 144 Mo ; **init depuis la carte d'hyper primitives : 37,055 / SSIM 0,962 / LPIPS 0,032**, 448 FPS, 219 Mo ; Photo-SLAM mono 33,302 / RGB-D 34,958 | Replica, Table 5 (`page:12`) |

Lecture : (a) la précision de pose est **celle d'ORB-SLAM3** (écarts de quelques mm sur TUM/EuRoC, dans un sens ou l'autre ; sur Replica mono 1,09 vs 3,94 cm, écart non expliqué par les auteurs) (`page:6`, `page:7`) ; (b) le coût du mapping photoréaliste **divise par ~1,4 la cadence de tracking** d'ORB-SLAM3 sur desktop (58,7 → 41,6 Hz), sans doute par contention GPU/CPU (non analysé) ; (c) sur Jetson, le tracking tombe à ~18 Hz sur Replica, ~28–37 Hz sur TUM (`page:6`, `page:12`).

## Comparaison avec les SLAM 3DGS qui utilisent le rendu pour le tracking (MonoGS, SplaTAM)
- **Le papier ne cite ni MonoGS (Matsuki et al., CVPR 2024) ni SplaTAM (Keetha et al., CVPR 2024)**, contemporains (vérifié dans paper.md : aucune occurrence) ; les baselines « à rendu » sont les SLAM NeRF (Nice-SLAM, ESLAM, Co-SLAM, Point-SLAM, Go-SLAM, Orbeez-SLAM) (`page:5`). La comparaison ci-dessous est donc architecturale (connaissance hors papier, à vérifier dans [Tosi 2024](../tosi2024_nerf-gs-slam-survey/fiche.md)).
- Différence de principe : MonoGS et SplaTAM estiment la pose en **minimisant l'erreur photométrique à travers le rasteriseur différentiable** (la carte 3DGS est à la fois modèle et instrument de mesure), donc chaque image coûte des dizaines d'itérations de rendu + rétropropagation ; Photo-SLAM garde l'erreur de reprojection ORB (éq. 1), découplée du rendu, et le rendu ne sert qu'à apprendre l'apparence (`page:3`, `page:4`). C'est exactement le camp « Graph Solver » de la taxonomie de la Fig. 2a (`page:2`).
- Conséquences mesurées dans le papier (contre les SLAM NeRF, mais l'argument s'étend) : tracking à 40+ Hz et 4–6 Go contre 2–20 Hz et 12–24 Go ; temps de traitement par image stable sans pics d'optimisation globale (`page:6`, `page:11`). Robustesse revendiquée des features classiques : « the classical method still has advantages in terms of robustness and generalization » (`page:6`).
- Prix à payer : (i) pas de raffinement de pose par la photométrie, donc la qualité de carte plafonne par la précision d'ORB-SLAM3 et dépend de la fermeture de boucle pour éliminer le ghosting (`page:5`) ; (ii) dépendance à la texture (ORB) : scènes EuRoC pauvres en texture → PSNR 14–17 dB seulement (`page:7`) ; (iii) le 3DGS hors ligne **initialisé depuis la même carte** gagne encore +3,75 dB (37,06 vs 33,30) à durée égale (`page:12`), signe que le mapping en ligne reste sous-optimisé.
- Ordre de grandeur dans la base pour SplaTAM : PSNR Replica 34,11 (RGB-D) selon [Chen 2024, survey 3DGS](../chen2024_3dgs-survey/fiche.md) (`doc:c459485/tier:standard/page:40`, Table S5), comparable aux 34,96 de Photo-SLAM RGB-D (`page:6`) mais avec un tracking par rendu bien plus lent (chiffres non rapportés dans la base : à compléter via Tosi 2024).

## Ce que ça dit du tracking du Quest
- **Même famille qu'Insight pour la géométrie** : landmarks épars détectés comme points à fort contraste, suivis, triangulés, BA local sur keyframes, carte persistante avec reconnaissance de lieu et correction de boucle — Photo-SLAM reprend tout cela d'ORB-SLAM3 (`page:3`, `page:5`). La différence majeure : **aucun IMU** (modes mono / stéréo / RGB-D purement visuels, pas de mode VI d'ORB-SLAM3 utilisé), **une ou deux caméras** au lieu de quatre, **pas de prédiction de pose** ni de cadence à 1 kHz ; la cadence est celle des images (18–82 Hz selon plateforme et séquence) (`page:6`, `page:12`). Insight, avec IMU et 4 caméras grand angle, est a priori plus robuste aux mouvements rapides et au manque de texture que le mode mono de Photo-SLAM.
- **Schéma de calcul comparable au casque** : tracking sur CPU (ORB-SLAM3 « runs faster without the requirement of GPU », 0 Go de GPU en Table 1) et mapping lourd déporté sur GPU dans un thread asynchrone (`page:6`). Sur Jetson AGX Orin (SoC embarqué classe tablette/robot), tout tient à 18–37 Hz de tracking et 4 Go de GPU (`page:6`, `page:12`) ; le Quest 3/3S (XR2 Gen 2, 8 Go partagés, DSP) n'exécute que la partie tracking, le mapping photoréaliste restant sur PC dans le schéma mote.
- **Ce que la fermeture de boucle implique pour mote** : Photo-SLAM corrige rétroactivement keyframes **et** Gaussiennes par similarité quand une boucle est détectée, ce qui supprime le ghosting (`page:5`). Insight fait l'équivalent sur sa carte interne, mais MRUK n'expose ni les événements de relocalisation ni les corrections de keyframes passées : si la pose d'une image déjà envoyée au PC est corrigée côté casque, mote ne le saura pas. À surveiller dans les captures (sauts de pose), cf. [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md).
- **Qualité de pose suffisante** : avec une ATE de ~0,6–1,1 cm (Replica) à 1–2,6 cm (TUM) issue d'un tracker géométrique sans raffinement photométrique, Photo-SLAM obtient 33–35 dB sur Replica et 19–23 dB sur TUM (`page:6`, `page:7`). Le SP-0 mote mesure 4–6 mm / 0,3–0,5° de médiane contre COLMAP (mémoire projet), soit un ordre de grandeur comparable ou meilleur : H-01 est cohérente avec ce papier, à la nuance près que la médiane n'est pas la RMSE et que COLMAP n'est pas une vérité terrain.
- **Ce qui manque côté Quest** : Photo-SLAM tire ses Gaussiennes initiales et sa densification des **points ORB** (actifs et inactifs) du tracker (`page:3`, `page:4`) ; MRUK ne livre que des poses, pas de landmarks ni de descripteurs. Mote devra recréer cette géométrie initiale autrement (voir idées).

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Taxonomie « graph solver vs neural solver » et « explicit vs implicit » (Fig. 2a) ; place ORB-SLAM3 comme tracker de référence et montre que DROID-SLAM dérive fortement sur TUM (78–154 cm) et EuRoC (`page:2`, `page:7`) ; architecture à threads asynchrones proche d'Insight (`page:3`) |
| 2. Poses pour 3DGS (piste mote, H-01) | **Preuve que des poses de tracker géométrique, non raffinées par le rendu, suffisent à un 3DGS en ligne de 33–35 dB** (`page:6`) ; comparaison directe 3DGS hors ligne sur ces mêmes poses : 27,8 → 34,6 → 37,1 dB selon l'initialisation des points (`page:12`), ce qui quantifie l'importance du nuage initial, pas seulement des poses |
| 3. Temps réel et contraintes embarquées | Chiffres desktop / laptop / Jetson : tracking 42 / 20 / 18 Hz, rendu 911 / 354 / 95 FPS, GPU 6 / 4 / 4 Go (`page:6`) ; tracking CPU seul pour ORB-SLAM3 (`page:6`) ; pas de mesure CPU, énergie ou latence |
| 4. Évaluation (métriques, protocoles, datasets) | ATE RMSE + STD, PSNR/SSIM/LPIPS, tracking FPS, rendering FPS, mémoire GPU, taille Mo ; 5 runs moyennés ; Replica / TUM RGB-D / EuRoC / ZED 2 extérieur (`page:5`) ; protocole « 3DGS hors ligne à durée égale sur les poses du SLAM » réutilisable tel quel pour mote (`page:11`, `page:12`) |

## Pour (vis-à-vis de notre problématique)
- Architecture **exactement celle de mote** : tracker géométrique séparé → poses + points → 3DGS asynchrone, sans rendu dans la boucle de tracking (`page:3`, `page:4`).
- Mono / stéréo / RGB-D dans le même système, dont un mode **stéréo extérieur à main levée** (ZED 2) (`page:5`, `page:7`, `page:8`) : proche d'une capture passthrough binoculaire.
- Seul SLAM photoréaliste du comparatif à tourner sur plateforme embarquée (Jetson AGX Orin) en temps réel, avec chiffres par scène (`page:6`, `page:12`, `page:13`).
- Code public C++/CUDA basé sur ORB-SLAM3 + 3DGS (`page:1`, `page:5`) : baseline reproductible pour rejouer nos captures Quest exportées et comparer « poses Quest » vs « poses ORB-SLAM3 » à mapping identique.
- Protocole Table 5 (3DGS hors ligne, poses fixées, trois initialisations de points) : directement transposable à l'évaluation H-01 (`page:12`).

## Contre / limites
- **Pas de raffinement de pose à l'entraînement** (seuls P, r, s, σ, SH sont optimisés, `page:4`) : la seconde moitié de H-01 (« raffinement des poses à l'entraînement ») n'est pas testée ici.
- Pas d'IMU, pas de multi-caméra, pas de prédiction : moins proche d'Insight que le mode VI d'ORB-SLAM3 ou que les VIO de la base.
- Dépendance aux points ORB pour initialiser et densifier (`page:4`) : non transposable tel quel à MRUK qui ne fournit pas de landmarks ; scènes peu texturées (EuRoC) → 14–17 dB (`page:7`).
- Qualité en ligne inférieure de 3,75 dB au 3DGS hors ligne sur la même carte (`page:12`) ; GP à 4 niveaux dégrade (sur-apprentissage, `page:8`) : réglage dépendant de la résolution.
- Mapping pénalise le tracking (58,7 → 41,6 Hz sur desktop ; 18 Hz sur Jetson Replica) sans analyse de la contention (`page:6`).
- Table 1 du PDF partiellement cassée par MinerU (cellules fusionnées, `page:6`), Table 8 idem (`page:13`) ; valeurs ci-dessus reconstituées par alignement des colonnes, à vérifier sur le PDF en cas de doute. Rotation RMSE sans unité (`page:13`). Pas de latence, de CPU ni d'énergie.
- Résolution de rendu 1200×680 (`page:6`), loin des 2064×2208 par œil du Quest 3.

## Idées à creuser pour mote
- *Hypothèse (H-01, nuage initial)* : Table 5 montre qu'à poses fixées, l'initialisation des points fait passer un 3DGS de 27,8 à 37,1 dB (`page:12`). Pour mote, remplacer les points ORB absents de MRUK par : (a) un nuage épars calculé sur PC par appariement de features entre images Quest à poses connues (triangulation sans SfM, donc en secondes) ; (b) le maillage de scène / profondeur du Quest 3 (projecteur IR) quand disponible, cf. [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) ; (c) sur Quest 3S sans projecteur, une profondeur monoculaire.
- *Hypothèse (densification géométrique)* : reproduire la règle « points 2D texturés sans 3D → Gaussiennes temporaires avec profondeur interpolée des voisins » (`page:4`) à partir de détecteurs de coins sur les images passthrough, puisque la pose est connue.
- *Hypothèse (GP learning)* : l'entraînement progressif par pyramide (3 niveaux) est indépendant du tracker et peu coûteux ; à tester dans notre pipeline 3DGS « quasi temps réel » comme accélérateur de convergence, en recalant n sur notre résolution (`page:5`, `page:8`).
- *Hypothèse (protocole)* : adopter le protocole « 3DGS hors ligne, poses fixées, durée fixée » de Table 5 pour comparer poses Quest / ORB-SLAM3 / COLMAP sur les mêmes images (`page:12`), et rapporter tracking FPS, mémoire GPU et taille Mo comme ici (`page:5`).
- *Hypothèse (corrections de boucle)* : implémenter côté PC l'équivalent de la correction par similarité des keyframes et des Gaussiennes (`page:5`) déclenchée par la détection d'un saut de pose Quest (relocalisation), puisque MRUK ne signale pas les corrections de carte.
- *Hypothèse (embarqué)* : les 4 Go de GPU et 18–37 Hz sur Jetson AGX Orin (`page:6`, `page:12`) donnent une borne pour un futur « mapping sur casque » ; le Quest (8 Go partagés, Adreno) est en dessous, ce qui conforte le découpage casque = tracking / PC = mapping.
- *Hypothèse (comparatif)* : rejouer MonoGS / SplaTAM (tracking par rendu) et Photo-SLAM (tracking ORB) sur une même capture Quest exportée, pour chiffrer le gain de robustesse/temps d'un tracker géométrique vs photométrique — le papier ne le fait pas.

## Citations clés
> « Specifically, we simultaneously exploit explicit geometric features for localization and learn implicit photometric features to represent the texture information of the observed environment. » (`doc:eb406be/tier:standard/page:1`)

> « Each component runs in a parallel thread and jointly maintains a hyper primitives map. » (`doc:eb406be/tier:standard/page:3`)

> « Experimentally, less than 30% of 2D geometric feature points of frames are active and have corresponding 3D points, especially for non-RGB-D scenarios [...] Therefore, we actively create additional temporary hyper primitives based on the inactive 2D feature points once the keyframe is created for photorealistic mapping. » (`doc:eb406be/tier:standard/page:4`)

> « Compared to learning-based methods, e.g., DROID-SLAM [34] and Go-SLAM [44], ORB-SLAM3 runs faster without the requirement of GPU and has higher accuracy regarding localization. It is shown that the classical method still has advantages in terms of robustness and generalization. » (`doc:eb406be/tier:standard/page:6`)

> « Without inputting fine-grained point clouds, 3DG needs more time for optimization such that the rendering quality decreases. » (`doc:eb406be/tier:standard/page:12`)

## Liens
- Papiers liés :
  - [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — tracker réutilisé tel quel (motion-only BA, BA local, fermeture de boucle) ; Photo-SLAM n'utilise pas son mode visuel-inertiel.
  - [ORB-SLAM (2015)](../murartal2015_orb-slam/fiche.md) — origine des features ORB et de la structure keyframes / covisibilité.
  - [DROID-SLAM](../teed2021_droid-slam/fiche.md) — baseline « neural solver » ; dérive forte sur TUM/EuRoC dans ce papier (`page:7`).
  - [DPVO](../teed2023_dpvo/fiche.md) — alternative légère côté apprentissage, non citée ici.
  - [3DGS](../kerbl2023_3dgs/fiche.md) — rasteriseur et densification split/clone repris ; comparaison hors ligne en Table 5.
  - [Tosi 2024, survey NeRF/GS-SLAM](../tosi2024_nerf-gs-slam-survey/fiche.md) — pour situer Photo-SLAM face à MonoGS / SplaTAM / Gaussian-SLAM.
  - [Chen 2024, survey 3DGS](../chen2024_3dgs-survey/fiche.md) — chiffres SplaTAM / Gaussian-SLAM sur Replica.
  - [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md) — budget de primitives, complémentaire à la densification géométrique.
  - [VRSplat](../tu2025_vrsplat/fiche.md) — côté rendu casque ; Photo-SLAM rend à 1200×680, pas à résolution HMD.
  - [Project Aria](../engel2023_project-aria/fiche.md), [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — précision des poses casque à comparer aux ATE de ce papier.
  - [Dossier Oculus Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) — ce que le Quest fait à la place des threads localisation / géométrie.
