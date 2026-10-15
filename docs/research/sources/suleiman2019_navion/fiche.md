---
citekey: suleiman2019_navion
mineru_doc: 34a8c9b
type: article de revue   # IEEE Journal of Solid-State Circuits (JSSC)
statut: fiche complète
tags: [vio, asic, accélérateur-matériel, facteur-graphe, fenêtre-glissante, préintégration-imu, stéréo, euroc, virgule-fixe, compression-mémoire, basse-consommation, nano-drone, co-design-algo-matériel, mit, dsp-vs-asic, piste-mote]
---

# Navion: A 2-mW Fully Integrated Real-Time Visual-Inertial Odometry Accelerator for Autonomous Navigation of Nano Drones

**Référence :** Amr Suleiman, Zhengdong Zhang, Luca Carlone, Sertac Karaman, Vivienne Sze (2019). *Navion: A 2-mW Fully Integrated Real-Time Visual-Inertial Odometry Accelerator for Autonomous Navigation of Nano Drones.* IEEE Journal of Solid-State Circuits 54(4), pp. 1106–1119. DOI [10.1109/JSSC.2018.2886342](https://doi.org/10.1109/JSSC.2018.2886342) · pas d'arXiv (PDF MIT) · code : **aucun code public** ; site du projet http://navion.mit.edu/ (vidéo de démonstration) (`doc:34a8c9b/tier:standard/page:1`, `page:10`). Extension de l'article RSS 2017 « Visual-inertial odometry on chip » (prototype FPGA) et de la présentation Hot Chips 2018 (`page:2`, `page:12`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Premier ASIC qui intègre **tout** un pipeline VIO (frontend stéréo + préintégration IMU + backend facteur-graphe à fenêtre glissante, sans DRAM externe) : gravé en 65 nm, il traite EuRoC (752×480 stéréo) à 20 fps pour **2 mW** en moyenne (24 mW au maximum, 171 fps / 52 kHz IMU), avec une erreur de trajectoire de 0,28 % de la distance parcourue contre 0,22 % pour le même algorithme en flottant sur CPU — soit 684× moins d'énergie par keyframe qu'un ARM Cortex-A15 et 1582× moins qu'un Xeon (`page:1`, `page:2`, `page:10`, `page:12`).

## Problème traité
- Les VIO de l'état de l'art (optimisation non linéaire) « requires relatively powerful CPUs and/or GPUs » ; le budget de calcul d'un nano-drone stable est « around 100mW », « an order of magnitude lower than the power dissipation of embedded CPUs » ; le plus petit drone commercial à VIO (Qualcomm, Snapdragon 801) pèse 250 g et consomme ≈ 3 W (`page:1`).
- Les accélérateurs existants simplifient le problème (marqueurs connus, Yoon 2013), dépendent de traitement d'image et de stockage **hors puce** (Hong 2015) ou n'implémentent qu'une partie du pipeline (Li 2018) ; le danger inverse est l'accélérateur câblé pour une seule tâche sans flexibilité (`page:1`, `page:2`).
- Difficulté spécifique au VIO par facteur-graphe : « large irregularly structured memories and heterogeneous computation flow » — graphe qui change de structure à chaque keyframe (marginalisation), mémoires de pistes de features de longueur variable, système linéaire O(N²) en mémoire et O(N³) en temps avec N keyframes (`page:1`, `page:4`).
- Les auteurs citent explicitement la VR/AR portable comme application : le VIO sans fermeture de boucle sort la pose « at significantly higher throughput », « critical to reduce the motion sickness of a consumer using AR/VR devices » (`page:1`).

## Méthode / contributions
### Algorithme accéléré (co-design algo/matériel, pipeline de Forster/Carlone 2015–2017)
- **Vision frontend (VFE)**, stéréo ou mono, à keyframes : suivi Lucas-Kanade pyramidal (FT) sur toutes les images ; détection de coins Shi-Tomasi sur grille (FD), undistort & rectify (UR), stereo matching par template le long de la ligne épipolaire (SM) et vérification géométrique (GV) **uniquement aux keyframes**. RANSAC « informed by the rotation estimate produced by gyroscope integration » : méthode 2 points pour le mono et 1 point pour le stéréo au lieu du 5 points (`page:2`, `page:3`). Choix du suivi plutôt que de l'appariement de descripteurs (SIFT/ORB, ORB-SLAM) pour éviter le calcul, le stockage et le matching des descripteurs (`page:4`).
- **IMU frontend (IFE)** : préintégration sur variété (Forster et al.) qui résume toutes les mesures inertielles (100 Hz à 1 kHz) entre deux keyframes en une seule mesure relative (ΔR, Δv, Δp), sans ré-intégration quand l'état est mis à jour (`page:2`, `page:3`).
- **Backend (BE)** : lisseur à retard fixe (fixed-lag smoother) MAP sur un **horizon glissant de 20 keyframes max**, facteur-graphe avec trois types de facteurs (vision = pistes de features, IMU = préintégration, marginalisation), Gauss-Newton sur variété avec linéarisation → H∆x = ε, solveur Cholesky + substitution, marginalisation, « retract ». **Une seule itération de Gauss-Newton** par keyframe grâce à l'initialisation IMU (`page:4`). Capacité : 20 KF × 15 variables (position, orientation, vitesse, 6 biais IMU) → H de 300×300 ; jusqu'à 4000 facteurs de vision, 200 features suivies par image, âge max d'une piste = 10 KF (`page:4`, `page:7`).
- Justification du facteur-graphe contre l'EKF : l'EKF résume les pistes entre deux KF adjacents (âge ≈ 2), erreur moyenne « 3× higher » sur EuRoC — 0,52 m pour ROVIO contre 0,16 m pour leur méthode (`page:4`). Sans fermeture de boucle ni relocalisation : « VIO does not have loop closure, which happens at much lower frequency and can be off-loaded to the cloud » (`page:1`).

### Architecture et précision numérique
- Puce autonome, **aucun stockage externe** : images (deux bus 8 bits, 752×480 max) et IMU (bus 32 bits, simple précision) en entrée, trajectoire + carte éparse en sortie. Frontend et backend **découplés sur deux domaines d'horloge** (62,5 MHz VFE, 83,3 MHz IFE+BE), reliés par une interface mémoire simple ; plus de **250 paramètres programmables** (calibration caméra/IMU, complexité du pipeline) (`page:5`, `page:9`).
- **Précision mixte** : VFE en **virgule fixe** (« for lower power and smaller area ») ; IFE et BE en **double précision** avec unité arithmétique dédiée (85 registres double précision partagés). « Using single precision does not provide sufficient numerical precision » : le VIO étant en boucle ouverte, l'incertitude et le conditionnement du système linéaire croissent avec le temps ; la double précision double la taille des mémoires du BE/IFE mais est jugée indispensable (`page:5`).
- Répartition : VFE = 53 % de la surface, 439,4 kB de SRAM (dominés par 4 frame buffers) ; IFE = 2,4 % de la surface, ≈ 1 % de la puissance ; BE = 412,6 kB de SRAM (`page:5`).
- Deux modes : **KF** (tout actif, FT/FD/UR/SM en parallèle, puis RANSAC mono et stéréo en série, puis BE) et **non-KF** (seul FT actif, reste clock-gaté, image droite non lue), en moyenne **3,8× plus rapide** (`page:5`, `page:6`).

### Optimisations mémoire et débit (section IV)
- **Compression d'image avec perte** pour les 4 frame buffers : troncature à 5 bits/pixel (+6 % d'erreur VIO pour −38 % de mémoire ; au-delà, erreur > 2× à 1 bit) puis quantification binaire par blocs 4×4 (26 bits par bloc : 16 bits + seuil 5 bits + minimum 5 bits) ; surcoût 4 kgates (0,8 %) et un line buffer de 1,4 kB ; **mémoire ÷4,4, puissance ÷4,9**. Les images compressées servent à FT et SM mais **pas à FD** (sensible aux artefacts de blocs) (`page:6`, `page:7`).
- **Sparsité non structurée des pistes de features** (88 % de la mémoire du graphe) : au lieu de 962 kB pour le pire cas (40 000 entrées × 3 doubles), mémoire à deux étages (pointeurs 12 bits vers une mémoire dense de 4000 observations) → **÷5,4**, un cycle de latence en plus (`page:7`).
- **Sparsité structurée de H** : symétrie (÷2) + motif fixe de non-zéros (38 % de chaque triangle, dépend du rapport âge des pistes / horizon) → **÷5,2** (134 kB) ; en sautant les zéros, le solveur linéaire est **7,2× plus rapide** et le BE jusqu'à 2,5× à 20 KF (`page:7`, `page:8`).
- **Ré-ordonnancement** : pré-détection des features pour casser la dépendance FD ← FT/RANSAC → VFE 43–55 % plus rapide pour 77 kB (10 %) de line buffers ; linéarisation des facteurs IMU démarrée dès la sortie de l'IFE, en parallèle du VFE → BE 4–19 % plus rapide, sans surcoût. Remarque des auteurs : ce parallélisme existe aussi en logiciel, mais « firing up multiple cores can significantly increase power consumption » (`page:8`).
- Bilan : SRAM totale **3471,7 → 854 kB (÷4,1)** ; frame buffers 1410 → 317,6 kB, facteur-graphe 1012 → 205,6 kB, solveur linéaire 882,4 → 163,5 kB (Table I, `page:8`). Bande passante externe réduite 9× jusqu'au minimum de 0,34 MB/image (`page:2`, `page:5`).
- **Adaptation à l'environnement** : nombre de features et taille d'horizon réglés par séquence pour viser 0,35 % d'erreur (35 features / horizon 10 sur les séquences faciles, jusqu'à 150 features / horizon 15 sur MH 4, MH 5, V2 3) → énergie ÷2,5 en moyenne (`page:2`, `page:10`, `page:11`).

## Résultats chiffrés
| Métrique | Valeur | Conditions (dataset, résolution, matériel) |
|---|---|---|
| Matériel | ASIC **65 nm CMOS**, 4,0 × 5,0 mm² (cœur 3,54 × 4,54 mm²), 2043 kgates (≈ 2 M NAND2), **854 kB SRAM**, 1 V ; 59,1 GOPS / 5,7 GFLOPS crête | Fig. 10 (`page:8`, `page:9`) |
| Fréquences d'horloge | VFE 62,5 MHz ; IFE+BE 83,3 MHz (deux domaines d'horloge) | config. maximale (`page:9`) |
| Entrées / paramètres max | stéréo 752×480 ; IMU jusqu'à **52 kHz** ; 200 features suivies / image (1824 détectées) ; horizon 20 KF, âge 10, 4000 pistes ; LK 3 niveaux, fenêtre 15×15, 30 it./niveau ; template stéréo 51×5, recherche 421×5 | Table II (`page:5`, `page:9`) |
| Fréquence (Hz) | tracking **28–171 fps** selon la séquence (moyenne 71) ; **pose/carte mises à jour au rythme des KF : 16–90 fps** (moyenne 19 fps KF total) ; avec adaptation : 142 fps tracking, 49 fps KF | EuRoC, paramètres max, 1 V (`page:8`, `page:10`, `page:12`) |
| Temps par image | non rapporté en ms dans le texte ; seulement répartition : non-KF 3,8× plus rapide que KF ; BE = 65 % en linéarisation des facteurs vision, 25 % solveur linéaire ; linéarisation IMU < 2 ms (Fig. 12 = image) | `page:6`, `page:9`, `page:10` |
| Précision (EuRoC, 11 séquences, moyenne de 5 runs) | erreur de trajectoire **23,25 cm = 0,28 %** de la longueur de vol (≈ 83 m) pour Navion contre **16,98 cm = 0,22 %** pour le même logiciel sur Xeon/ARM ; +6,27 cm « mainly due to lossy image compression and fixed point arithmetic in V FE » ; la littérature VO va de 0,1 à 2 % | Table III, protocole = écart à la vérité terrain le long de tout le vol, normalisé par la longueur (`page:10`) |
| Dérive / ATE / RMSE | non rapporté sous forme ATE RMSE standard ; pas de fermeture de boucle (la dérive est l'erreur ci-dessus) ; erreur par séquence seulement en figure (Fig. 15) | `page:10`, `page:11` |
| Puissance | **24 mW** moyenne à débit max ; **18 mW** à distance fixe entre KF (5 cm/KF) ; **6 mW** à 20 fps ; avec adaptation : 22 / 7 / **2 mW** | 1 V, EuRoC, Table V (`page:11`, `page:12`) |
| Énergie / comparaison CPU | **2,3 mJ/KF** (Navion) vs 1573,2 mJ/KF (ARM Cortex-A15, 2,4 W, 19 fps tracking, 2 fps KF) vs 3638,6 mJ/KF (Intel Xeon E5-2667, 27,9 W, 63 fps tracking, 12 fps KF) → **684× / 1582×** ; puissance CPU = calcul seul, hors idle et DRAM | Table III (`page:2`, `page:10`) |
| Comparaison GPU | **non rapporté** (aucune mesure GPU ; seule mention : les VIO temps réel « requires relatively powerful CPUs and/or GPUs ») | `page:1` |
| Répartition puissance / surface | BE = 40 % de la puissance (actif aux KF seulement) ; SRAM = 77 % de la surface mais 21 % de la puissance (bancs clock-gatés, 5–9× d'économie) ; FT = plus gros poste du VFE ; dans le BE, moitié FSM/contrôle, un quart unité arithmétique | Fig. 11 (`page:9`) |
| Mémoire | 854 kB SRAM après ÷4,1 (3471,7 kB avant) ; **aucune DRAM** | Table I (`page:8`) |
| Latence | **non rapportée** (ni capteur→pose, ni motion-to-photon) | — |
| Démonstrateur | puce + carte Xilinx ZC-706 (Zynq-7000, 2 × Cortex-A9) qui streame images/IMU et affiche la trajectoire en temps réel | `page:10` |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Description compacte et pédagogique du pipeline VIO « optimisation » (frontend KLT + préintégration + fixed-lag smoother) que l'on retrouve dans VINS/Basalt/Kimera ; chiffre repère EKF vs facteur-graphe (ROVIO 0,52 m vs 0,16 m, `page:4`). Montre ce qu'un VIO **sans carte persistante ni fermeture de boucle** peut donner : 0,22–0,28 % de dérive. Premier auteur passé chez **Facebook Reality Labs** (`page:13`). |
| 2. Poses pour 3DGS (piste mote, H-01) | Ordre de grandeur de la dérive d'un VIO pur : 0,28 % → ≈ 3 cm sur une capture de 10 m, bien au-dessus des 4–6 mm médians mesurés sur le Quest en SP-0, ce qui suggère que le casque bénéficie de sa carte/relocalisation. Les poses optimisées ne sortent qu'**aux keyframes** (16–90 fps) ; entre deux KF il n'y a que du suivi 2D (`page:6`, `page:8`) : une image capturée hors KF n'a pas de pose raffinée. |
| 3. Temps réel et contraintes embarquées (CPU/GPU/DSP) | Cœur de la fiche : budget 100 mW d'un nano-drone, 2,4 W pour un ARM A15 à seulement 2 KF/s, 3 W pour un Snapdragon 801 (`page:1`, `page:10`). Choix de précision transférables à un DSP : virgule fixe acceptable dans le frontend image (+0,06 pt d'erreur), **double précision obligatoire** dans le solveur (`page:5`, `page:10`). Compression d'images 5 bits/4×4 et sparsité de H réutilisables en logiciel. |
| 4. Évaluation (métriques, protocoles, datasets) | EuRoC 11 séquences, erreur normalisée par la distance (%), 5 runs par séquence à cause de RANSAC, même configuration logiciel/puce ; énergie en mJ/KF comme métrique de comparaison matérielle (`page:10`). Modes de débit comparables : max, distance fixe 5 cm/KF, cadence capteur 20 fps (`page:11`). |

## Ce que ça dit du tracking du Quest
- **Ressemblances** : même famille algorithmique que ce que décrit Meta pour Insight (points de fort contraste suivis d'image en image, triangulés, fusion IMU, états à haute cadence) ; Navion montre qu'un tel pipeline tient dans quelques mW et quelques centaines de kB si on le fige en silicium. L'IMU est consommée à bien plus que 1 kHz (52 kHz possibles, `page:8`) et sert aussi à **guider le RANSAC** par la rotation gyroscopique (`page:3`) — astuce que n'importe quel VI-SLAM de casque peut employer.
- **Différences** : Navion est une **odométrie pure** : pas de carte persistante, pas de relocalisation, pas de fermeture de boucle (renvoyée « to the cloud », `page:1`), pas de prédiction de pose pour le rendu, deux caméras au lieu des 4 caméras monochromes du Quest, sortie de pose seulement aux keyframes. Insight est à l'inverse un SLAM avec carte et reconnaissance de lieu ; ce que Navion mesure (0,28 % de dérive) est donc une **borne supérieure plausible** de ce que fait le casque en l'absence de relocalisation, pas une description du Quest.
- **ASIC vs DSP** : le Quest tourne Insight sur le SoC Snapdragon (CPU multithread + « Quest-specific DSP tuning » sur Hexagon, selon le [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md)), pas sur un ASIC VIO dédié. Navion rappelle le prix de ce choix : l'ARM A15 consomme 2,4 W pour le même algorithme (`page:10`) et un SoC mobile ≈ 3 W (`page:1`). Un DSP vectoriel en virgule fixe se situe entre les deux ; Navion indique où placer la virgule fixe (frontend) et où la refuser (backend double précision, `page:5`). Les « roughly one order of magnitude less compute » qu'évoque Meta s'obtiennent probablement par les mêmes leviers : keyframes, préintégration, frontend fixe, sparsité (hypothèse, non documentée par Meta).
- **Implication pour mote** : la qualité des poses que MRUK renvoie dépend (i) de la fréquence des keyframes du SLAM casque, (ii) de la relocalisation sur la carte persistante, (iii) de la précision numérique du backend — trois paramètres **non publiés** par Meta. Navion donne les ordres de grandeur pour raisonner : à 0,28 % sans carte, une boucle de 20 m dériverait de ≈ 5–6 cm ; les 4–6 mm de SP-0 ne sont compatibles qu'avec un système qui referme ses boucles ou relocalise. À vérifier en SP suivant : la dérive Quest sur un aller-retour long **sans** revisiter la zone de départ.

## Pour (vis-à-vis de notre problématique)
- Seule référence de la base qui donne des chiffres **mesurés sur silicium** (puissance, surface, mémoire, fréquence) pour un VIO complet ; permet de situer CPU embarqué / SoC / ASIC sur une même échelle (mJ/KF, `page:10`).
- Co-design explicite : chaque choix algorithmique (suivi vs descripteurs, facteur-graphe vs EKF, préintégration, une itération GN, horizon 20) est justifié par son coût mémoire/temps (`page:4`, `page:5`).
- Quantifie l'effet de la précision réduite sur l'erreur (+0,06 pt de dérive pour compression + virgule fixe, `page:10`) et de la taille d'horizon / du nombre de features sur l'énergie (÷2,5, `page:11`), utile pour discuter les compromis d'un casque.
- Blocs réutilisables identifiés par les auteurs : préintégration IMU, solveur linéaire, détection/suivi, rectification, stéréo (`page:2`, `page:12`).

## Contre / limites
- **Pas de SLAM** : ni carte persistante, ni relocalisation, ni fermeture de boucle ; impossible de juger la précision à long terme comme sur un casque (`page:1`).
- Comparaisons **CPU uniquement** (Xeon, ARM A15) ; aucun GPU, aucun DSP, aucun SoC mobile moderne mesurés ; les puissances CPU excluent idle et DRAM (`page:10`).
- Métrique d'erreur maison (écart le long de la trajectoire, normalisé par la distance) et non l'ATE RMSE habituelle ; résultats par séquence seulement sous forme de figures (Fig. 15, 16) ; pas d'erreur de rotation, pas de jitter, pas de latence (`page:10`, `page:11`).
- Résolution 752×480, 200 features, 2 caméras : loin des 4 caméras d'un Quest ; aucun résultat hors EuRoC (vol de drone, pas de mouvement de tête).
- Technologie 65 nm et puce de recherche : pas de code public, pas de reproductibilité logicielle directe (seul le pipeline Forster/Carlone est disponible dans d'autres implémentations).
- La virgule fixe du frontend « coûte » 6,27 cm d'erreur moyenne : non négligeable à l'échelle de précision qu'exige un 3DGS (`page:10`).

## Idées à creuser pour mote
- *Hypothèse* : mesurer la **dérive du Quest en boucle ouverte** (trajet long sans revisite, puis retour) pour comparer aux 0,22–0,28 % de Navion et distinguer la part « odométrie » de la part « relocalisation » dans les 4–6 mm de SP-0.
- *Hypothèse* : la pose MRUK à une image donnée est-elle une pose de keyframe optimisée ou une propagation IMU entre keyframes ? Navion montre que seul le backend (16–90 fps) produit des poses raffinées (`page:8`) ; si le Quest fait pareil, choisir les images de capture **aux instants de keyframe** (ou pondérer les poses par leur « fraîcheur ») pourrait améliorer H-01.
- *Hypothèse* : réutiliser le réglage « distance fixe entre keyframes (5 cm/KF) » (`page:11`) comme critère de sélection d'images pour l'entraînement 3DGS (densité d'échantillonnage spatiale plutôt que temporelle).
- *Hypothèse* : le raffinement de poses à l'entraînement 3DGS (H-01) joue le rôle de la fermeture de boucle absente du VIO ; une évaluation « poses VIO pur + raffinement » vs « poses SLAM » serait un bon test de robustesse.
- Pour le rapport : utiliser Table III comme illustration unique de l'échelle énergétique CPU → ASIC quand on explique pourquoi un casque autonome dépend d'un SoC spécialisé (DSP) plutôt que d'un CPU générique.

## Citations clés
> « Compared to a full-SLAM system [5, 6], VIO does not have loop closure, which happens at much lower frequency and can be off-loaded to the cloud. As a result, a VIO system can output the estimated motion at significantly higher throughput, which is critical for autonomous navigation of fast moving robots/drones/vehicles, and also critical to reduce the motion sickness of a consumer using AR/VR devices. » (`doc:34a8c9b/tier:standard/page:1`)

> « Navion uses double precision arithmetic in the BE and IFE to ensure robustness of the VIO system. [...] Using single precision does not provide sufficient numerical precision for the underlying VIO algorithm from [23]. This is due to the fact that the VIO pipeline is an open-loop system. » (`doc:34a8c9b/tier:standard/page:5`)

> « Navion's average trajectory error increases by 6.27 cm, over an average flight length of 83 m in EuRoC dataset. Hence, the normalized error increases from 0.22% to 0.28%. This 0.06 percentage point error increase is mainly due to lossy image compression and fixed point arithmetic in V FE. » (`doc:34a8c9b/tier:standard/page:10`)

> « Navion consumes 684× and 1582× less energy than ARM A15 and Intel Xeon CPUs respectively. » (`doc:34a8c9b/tier:standard/page:10`)

> « When configured to process EuRoC dataset at the sensor rate of 20 fps, the chip consumes only an average of 2mW at 1V. » (`doc:34a8c9b/tier:standard/page:12`)

## Liens
- Dossier casque : [Oculus Insight / Quest 3](../../supports/meta2019_oculus-insight-quest/dossier.md) — CPU + DSP Hexagon, pas d'ASIC ; carte persistante et relocalisation absentes de Navion.
- Papiers liés :
  - [Delmerico 2018 (benchmark VIO)](../delmerico2018_vio-benchmark/fiche.md) — cité par Navion pour le facteur 3× EKF vs optimisation (`page:4`) ; comparaison des mêmes algorithmes sur CPU embarqués.
  - [Nagy 2020 (Faster than FAST)](../nagy2020_faster-than-fast/fiche.md) — accélération du frontend sur GPU embarqué, l'autre voie que l'ASIC.
  - [Huang 2019 (revue VIN)](../huang2019_vin-review/fiche.md) — taxonomie filtre vs optimisation dans laquelle Navion se range côté fixed-lag smoother.
  - [VINS-Mono](../qin2018_vins-mono/fiche.md), [Basalt](../usenko2020_basalt/fiche.md), [Kimera](../rosinol2020_kimera/fiche.md) — fenêtre glissante + préintégration, mêmes bases (Forster et al.) que le backend de Navion ; Kimera partage Carlone.
  - [OpenVINS](../geneva2020_openvins/fiche.md) — l'approche filtre (MSCKF) que Navion écarte.
  - [ORB-SLAM](../murartal2015_orb-slam/fiche.md) — approche par descripteurs explicitement écartée (`page:4`).
  - [Project Aria](../engel2023_project-aria/fiche.md) — VIO embarqué Meta avec chiffres de dérive open loop (< 0,4 %) à comparer aux 0,28 % de Navion.
  - [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — mesure externe de la précision du tracking des casques.
  - [3DGS](../kerbl2023_3dgs/fiche.md), [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md), [VRSplat](../tu2025_vrsplat/fiche.md) — côté consommateur des poses ; budget de calcul du rendu à mettre en regard du budget du tracking.
