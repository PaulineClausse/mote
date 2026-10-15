---
citekey: nagy2020_faster-than-fast
mineru_doc: bb8e8aa
type: conférence   # IEEE/RSJ IROS 2020
statut: fiche complète
tags: [vio, frontend, fast, non-maxima-suppression, klt, lucas-kanade, gpu, cuda, warp-shuffle, jetson-tx2, embarqué, euroc, ice-ba, vilib, accélération-gpu-dsp-simd, grille-de-cellules]
---

# Faster than FAST: GPU-Accelerated Frontend for High-Speed VIO

**Référence :** Balazs Nagy, Philipp Foehn, Davide Scaramuzza (2020). *Faster than FAST: GPU-Accelerated Frontend for High-Speed VIO.* IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS 2020), 8 p. arXiv [2003.13493v3](https://arxiv.org/abs/2003.13493) (3 août 2020) · DOI IEEE non imprimé dans le PDF (IEEE Xplore : 10.1109/IROS45743.2020.9340851, à vérifier) · code public : **vilib**, [github.com/uzh-rpg/vilib](https://github.com/uzh-rpg/vilib) (`doc:bb8e8aa/tier:standard/page:1`). Auteurs du Robotics and Perception Group (Univ. Zurich / ETH Zurich), même groupe que SVO et que le benchmark VIO de Delmerico (`page:1`, `page:8`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Portage CUDA du **frontend** d'un VIO (détection de coins FAST + non-maximum suppression (NMS) + suivi KLT) qui exploite les primitives de communication intra-warp des GPU NVIDIA (shuffle, réduction par registres) pour fusionner détection, NMS et sélection d'une feature par cellule en un seul passage : > 1000 fps de détection + suivi sur un **Jetson TX2** embarqué, et ∼200 fps pour un VIO métrique complet (frontend GPU + backend ICE-BA sur CPU) sur EuRoC (`page:1`, `page:7`).

## Problème traité
- Le VIO reste « computationally expensive and introduces significant latency », latence qui en VR/AR « introduc[es] motion sickness » ; les caméras du commerce dépassent 100 fps mais « many algorithms and implementations are not able to handle visual information at this rate » (`page:1`).
- Dans un pipeline VIO, les étapes qui touchent directement les pixels (détection, NMS, suivi) sont parallélisables, et « non-maxima suppression and the subsequent feature selection are prominent contributors to the overall image processing latency » (`page:1`).
- Les implémentations GPU existantes de FAST (OpenCV, ArrayFire) s'arrêtent dès que le quota de features est atteint et « neither of them guarantees spatial feature distribution » ; les algorithmes de NMS rapides (Neubeck, Pham) ne garantissent pas non plus de répartition spatiale et « possibly output a large set of feature candidates » (`page:2`). Or la répartition uniforme des features améliore la stabilité du VIO (grille de cellules de SVO, une feature par cellule) (`page:3`).
- Les trackers KLT GPU antérieurs utilisent une affectation **un thread par feature**, ce qui n'exploite le GPU que pour de grands nombres de features, alors qu'un VIO n'en suit que 50–200 (`page:5`, `page:6`).
- Choix d'architecture : parmi les trois plateformes hétérogènes embarquées (CPU+DSP « restricted in its set of tasks », CPU+FPGA « increases development time », CPU+GPU « cost-efficient » et adapté à l'image), le papier choisit CPU+GPU et cherche « a feasible work-sharing between the CPU and a GPU » (`page:1`).

## Méthode / contributions
### Ce qui est porté sur GPU, et comment
| Brique | Sur GPU ? | Mécanisme CUDA utilisé | Pages |
|---|---|---|---|
| Upload image hôte → GPU, pyramide d'images (chaque niveau = moitié de résolution) | oui (copies comptées dans les temps) | copies mémoire, kernels de sous-échantillonnage | `page:6`, `page:7` |
| Détection FAST (CCRF/CRF, segment test sur cercle de Bresenham r=3, 16 pixels, bordure 3 px, seuil ε, arc de N pixels) | oui | **table de correspondance (LUT) de 8 Ko** : les 16 comparaisons forment un index 16 bits ; la validité des 2^16 combinaisons est stockée sur 2^16 bits (entiers 4 octets, 11 bits d'adresse + 5 bits de sélection) → supprime la divergence if/else du modèle SIMT ; trois scores implémentés (SAD-B, SAD-A, MT) | `page:4`, `page:5` |
| Non-maximum suppression + sélection d'une feature par cellule (NMS + NMS-C) | oui, **fusionnées en une seule étape** | carte de réponses découpée en cellules de largeur 32·w (un warp = 32 threads = un segment de ligne de cellule), hauteur 2^(l−1)·h ; chaque thread garde en **registres** son maximum de colonne après suppression en spirale (Förstner) dans le voisinage de Moore ; puis **réduction warp-level par shuffle-down** vers le thread 0, et réduction en mémoire partagée si M warps traitent une cellule ; une seule grille pour tous les niveaux de pyramide (cellules virtuellement réduites au niveau k, positions remontées en (2^l x, 2^l y)) ; bords de cellules alignés sur les lignes de cache L1 | `page:3`, `page:4` |
| Suivi KLT (Lucas-Kanade inverse compositionnel approximé, pyramidal, modèle translation + illumination affine q = [t_x, t_y, α, β]) | oui | **un warp entier par feature** (au lieu d'un thread par feature) : patchs 16×16 en haute résolution, 8×8 en basse, traités collaborativement par les 32 threads ; réduction « butterfly » intra-warp à chaque itération pour sommer U^T·r ; même nombre d'itérations et même niveau de pyramide pour tout le warp → pas de divergence, accès mémoire coalescés | `page:5`, `page:6` |
| Download de la grille de features GPU → hôte | oui (compté) | copie mémoire | `page:6`, `page:7` |
| Backend VIO (bundle adjustment) | **non**, reste sur CPU | ICE-BA [33], « CPU targetted » | `page:7` |

- **Principe directeur** : utiliser la mémoire la plus rapide à chaque niveau de la hiérarchie (registres entre threads d'un warp, mémoire partagée entre warps d'un bloc, mémoire globale entre blocs — Table I), possible depuis l'architecture Kepler qui permet aux threads d'un warp de lire les registres des autres (`page:3`).
- **Contribution 1** : NMS « selects local response maxima, imposes spatial feature distribution, and extracts features simultaneously » (`page:1`), ce qui rend inutile l'étape de sélection ultérieure ; différence avec Neubeck/Pham : suppression d'abord par thread en parallèle, puis réduction des candidats restants dans la cellule (`page:4`).
- **Contribution 2** : détecteur FAST GPU multi-scores avec LUT compressée bit à bit (8 Ko, meilleur taux de hit cache L1 que la LUT 64 Ko d'ArrayFire) (`page:5`).
- **Contribution 3** : tracker KLT avec affectation feature → warp, « the novelty of our approach lies in the thread-to-feature assignment » (`page:6`).
- **Intégration** : frontend GPU + backend ICE-BA (CPU), 70 features suivies, fenêtre de bundle adjustment local réduite à 15 images ; re-détection déclenchée quand le nombre de pistes passe sous 30 % de la cible (`page:7`).

## Résultats chiffrés
Plateformes : **NVIDIA Jetson TX2** (Tegra X2, GPU « embedded », CUDA 6.2, 256 cœurs, 1300 MHz, 665,6 GFLOP/s simple précision, 59,7 Go/s) en mode max-N, et portable **Intel i7-6700HQ + GeForce 960M** (640 cœurs, 1176 MHz, 1505,28 GFLOP/s, 80 Go/s) (`page:6`). Données : EuRoC Machine Hall, MH 01 (3 682 images) pour NMS/détection/suivi, MH 01–05 pour le VIO (`page:6`). Résolution d'image non rapportée dans le papier (EuRoC = 752×480 à 20 Hz d'après le dataset lui-même, information externe au papier).

| Métrique | Valeur | Conditions | Pages |
|---|---|---|---|
| NMS seule (GPU, vs Förstner spiral) | TX2 : 3×3 **141,36 µs** vs 294,03 ; 5×5 338,03 vs 696,57 ; 7×7 604,94 vs 1 207 ; 9×9 929,82 vs 1 772 µs → **≈ 2×** sur TX2 ; 960M : 73,78 vs 96,81 ; 158,93 vs 245,96 ; 288,39 vs 441,59 ; 450,08 vs 661,90 µs (≈ 1,3–1,5×) | FAST ε=10, N=10, grille 32×32 (l=1, w=1, h=32) | `page:6` |
| Kernel CRF FAST, LUT bit vs byte | TX2 : SAD-B 298,7 vs 317,3 µs ; SAD-A 334,9 vs 348,4 ; MT 784,3 vs 815,1 µs ; hit L1 83,9 → 89,9 % (SAD-B), 84,0 → 91,8 % (MT) ; 960M : 135,9 / 155,1 / 374,8 µs, hit L1 68,6 → 77,4 % | kernel seul | `page:6` |
| **Détection FAST complète** (upload + pyramide + CRF + NMS + download inclus) | TX2 : **Ours SAD-B 1,11 ms**, SAD-A 1,14, MT 1,59 ms vs OpenCV CPU (MT) 4,78 ms, OpenCV CUDA 2,73 ms, ArrayFire CUDA 1,47 ms, ArrayFire CPU 60,83 ms ; 960M : Ours 0,28 / 0,30 / 0,52 ms vs OpenCV CPU 2,23, OpenCV CUDA 1,09, ArrayFire CUDA 0,51, KFAST CPU (SIMD x86) 0,63 ms | résolution native, un seul niveau (concurrents mono-échelle) ; KFAST et ArrayFire OpenCL non exécutables sur TX2 | `page:7` |
| Gain détection GPU vs CPU | TX2 : **4,3×** vs OpenCV CPU (4,78/1,11) ; **2,5×** vs OpenCV CUDA ; 960M : 8× vs OpenCV CPU, 2,3× vs KFAST SIMD | calcul à partir de la Table V | `page:7` |
| **Suivi KLT, 100 features** (re-détection à 30) | TX2 : **Ours 0,90 ms** (trans.+offset), 0,96 (trans. seule), 1,01 ms (4 paramètres) vs OpenCV CPU 1,88 ms, OpenCV CUDA **3,96 ms** ; 960M : Ours 0,28–0,38 ms vs OpenCV CPU 1,38, OpenCV CUDA 0,74 ms → « a factor of 2× and more » | translation seule converge plus lentement (plus d'itérations) | `page:7` |
| Fréquence frontend atteignable | « over 1000fps throughput » détection + suivi sur TX2 (`page:1`, `page:2`) ; cohérent avec ≈ 0,9–1,1 ms par image pour le suivi, la détection n'étant relancée que sous 30 % de pistes (interprétation, non chiffrée ainsi par les auteurs) | TX2 | `page:1`, `page:7` |
| Répartition du temps de détection (upload / pyramide / CRF / NMS / download) | seulement en figure (Fig. 6, image), valeurs non rapportées dans le texte | l = 2 | `page:6`, `page:7` |
| **VIO complet, temps par image** (frontend + ICE-BA) | TX2 : Ours **4,67 / 4,93 / 6,41 / 6,10 / 5,87 ms** (MH 01–05) vs original 11,64 / 12,90 / 12,91 / 12,90 / 12,85 ms ; 960M : Ours 1,56 / 1,74 / 2,54 / 2,51 / 2,06 ms vs 4,11 / 4,28 / 4,77 / 4,63 / 4,64 ms ; **accélération moyenne 2,25×** | 70 features, LBA 15 images | `page:7`, `page:8` |
| Fréquence VIO | « ∼200fps » sur TX2 (moyenne calculée : 5,6 ms ≈ 179 fps ; 4,67 ms ≈ 214 fps sur MH 01) ; ≈ 400–640 fps sur 960M (calcul) | débit, pas latence capteur → pose | `page:7`, `page:8` |
| **Précision (RMSE translation relative)** | TX2 : Ours 0,86 / 0,90 / 1,40 / 1,85 / 1,19 % vs original 1,08 / 0,71 / 0,40 / 0,81 / 0,50 % ; 960M : 1,00 / 0,55 / 0,74 / 2,14 / 1,68 % vs 0,68 / 0,71 / 0,53 / 0,83 / 1,36 % ; « average accuracy loss of 0.47% » (écart absolu de pourcentage ; en moyenne l'erreur passe d'≈ 0,76 % à ≈ 1,23 %, calcul) | MH 04/05 dégradées par mouvements rapides et scènes sombres | `page:7`, `page:8` |
| ATE absolue, dérive, latence capteur → pose | **non rapportées** | — | — |
| CPU / mémoire / énergie | **non rapportés** (ni charge CPU, ni mémoire, ni watts) | — | — |
| Conformité | aucune fausse détection vs FAST original ; sortie = sous-ensemble bien réparti (Fig. 5) | scores SAD-A et MT | `page:6` |

## Ce que ça dit du tracking du Quest
- **Même famille de frontend.** Ce que Meta décrit d'Insight — « high-contrast pixels, such as window corners » suivis d'image en image, pyramides calculées sélectivement, fusion IMU (dossier Insight, §2.2) — est exactement le schéma coins + suivi différentiel + grille de cellules du papier (FAST → NMS par cellule → KLT), hérité de SVO (`page:3`). Nagy et al. donnent donc un **ordre de grandeur crédible du coût par caméra** d'un tel frontend sur une puce embarquée : ≈ 1 ms de détection et ≈ 1 ms de suivi pour 100 features sur un GPU de 256 cœurs (`page:7`).
- **Différences.** (i) Mono-caméra EuRoC vs 4 caméras monochromes sur Quest : il faudrait multiplier le frontend par 4 (ou traiter les 4 images en un seul lancement de kernels), ce que le papier ne traite pas ; (ii) le papier ne fait qu'une odométrie (ICE-BA, fenêtre glissante de 15 images) sans carte persistante ni relocalisation, alors qu'Insight maintient une carte et des landmarks à long terme ; (iii) l'IMU n'intervient que dans le backend ICE-BA, pas dans le frontend (les travaux [25], [26] avec initialisation KLT par IMU sont cités mais **non repris**, `page:2`) ; Insight, lui, utilise l'IMU à 1 kHz pour la prédiction ; (iv) pas de prédiction ni d'extrapolation de pose ; (v) l'accélération GPU du papier repose sur CUDA/NVIDIA, alors que Meta ne déclare que du « Quest-specific DSP tuning » (dossier Insight, §2.4) — le choix d'architecture est différent : le papier range justement CPU+DSP parmi les options « restricted in its set of tasks » (`page:1`).
- **Implication pour les poses que mote récupère.** Le papier montre que (a) le frontend n'est **pas** le goulot si on le parallélise : 5–6 ms par image de VIO complet sur TX2 (`page:8`), donc la cadence des caméras (et non le calcul) borne la fréquence des mises à jour visuelles ; (b) un frontend sparse à 70–100 features bien réparties suffit à ≈ 1 % d'erreur relative de translation sur EuRoC, mais que la précision **se dégrade** (0,47 point en moyenne, jusqu'à ×2,3 sur MH 04 TX2) quand on optimise le frontend pour la vitesse (`page:8`) ; (c) la qualité chute sur les séquences sombres et rapides (MH 04/05) (`page:7`), ce qui est cohérent avec ce qu'on attend du Quest dans les pièces peu éclairées — à garder en tête pour le protocole de capture mote. Les erreurs relatives de ~1 % sur quelques mètres sont d'un autre ordre que les 4–6 mm médians mesurés sur SP-0 : un VIO « pur » à cette vitesse ne suffirait pas à H-01 ; Insight y ajoute la carte persistante, la relocalisation et 4 caméras, ce qui explique probablement l'écart.

## Transposition au casque (GPU Adreno, DSP Hexagon) — analyse, hors papier
Le papier ne parle ni d'Adreno, ni de Hexagon, ni de Snapdragon : tout ce qui suit est une projection faite pour mote.
- **Ce qui se transpose directement** : la LUT 8 Ko (indépendante du matériel), la grille de cellules alignée sur la taille de groupe de threads, l'affectation « un groupe de threads par feature » pour KLT, et la fusion NMS + sélection par cellule. Sur Adreno (OpenCL / Vulkan compute), les équivalents des shuffles de warp sont les opérations de sous-groupe (Vulkan subgroup / OpenCL `cl_khr_subgroups`) ; la largeur des wavefronts Adreno (64 ou 128 fibres selon la génération, information externe) change la taille des cellules 32·w et des patchs 16×16 / 8×8 (`page:3`, `page:5`).
- **Ce qui change en faveur du casque** : sur un SoC mobile à mémoire unifiée, les étapes Upload/Download comptées dans les temps du papier (`page:6`, `page:7`) disparaissent ou deviennent des coûts de cohérence de cache ; en revanche la bande passante mémoire est plus faible que les 59,7 Go/s du TX2 (`page:6`), et le papier note que « the speed improvement for the embedded computer is more pronounced, as there's a higher performance penalty for memory interactions » (`page:8`) — l'argument joue donc plutôt en faveur d'une accélération GPU sur casque.
- **DSP Hexagon (HVX, SIMD large)** : la voie SIMD existe dans le papier sous la forme de **KFAST** (x86 vectorisé), qui atteint 0,63 ms sur i7 contre 0,52 ms pour le GPU 960M avec le même score MT (`page:7`) : l'écart CPU-SIMD / GPU est faible sur la détection ; le DSP est en plus isolé des pics de charge du rendu, ce qui explique probablement le choix de Meta. La partie KLT (quelques dizaines de patchs 16×16, réductions) est elle aussi vectorisable.
- **Le GPU du casque est déjà pris par le rendu** : contrairement au TX2 du papier dédié au VIO, l'Adreno du Quest rend deux yeux à 72–120 Hz ; un frontend GPU entrerait en concurrence avec le rendu (et avec un éventuel splatting local). C'est la raison principale pour laquelle la transposition « naïve » n'est pas celle de Meta ; non discuté dans le papier.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Référence de l'axe pour le **frontend** (détection + NMS + suivi) et son coût réel sur plateforme embarquée ; taxonomie des 3 architectures hétérogènes (CPU+DSP, CPU+FPGA, CPU+GPU) (`page:1`) ; revue des détecteurs (Harris, Shi-Tomasi, FAST, FAST-ER, ORB, KFAST), des NMS (Förstner, Neubeck, Pham) et des trackers (matching, filtre, différentiel) (`page:2`) |
| 2. Poses pour 3DGS (piste mote, H-01) | Indirect : donne l'ordre de grandeur de précision d'un VIO sparse rapide (≈ 1 % RMSE relative sur EuRoC) et montre l'arbitrage vitesse/précision (`page:8`) ; confirme que la répartition uniforme des features importe pour la stabilité (`page:3`) — argument pour un critère de « couverture » des images dans le protocole de capture |
| 3. Temps réel et contraintes embarquées (CPU/GPU/DSP) | **Cœur** : chiffres détaillés détection/NMS/suivi/VIO sur Jetson TX2 vs portable, gains 2–4× vs OpenCV CPU/CUDA, ∼200 fps VIO, méthode de travail « from the GPU hardware's perspective » (`page:1`, `page:6`–`page:8`) |
| 4. Évaluation (métriques, protocoles, datasets) | EuRoC MH 01–05, RMSE de translation relative, temps moyen par image, conformité vs détecteur de référence, comparaison à des implémentations publiques (`page:6`, `page:7`, `page:8`) ; renvoie au benchmark Delmerico 2018 pour expliquer MH 04/05 (`page:7`) |

## Pour (vis-à-vis de notre problématique)
- Seul papier de l'axe à **chiffrer étape par étape** le coût d'un frontend VIO sur GPU embarqué, avec comparaison aux implémentations publiques (OpenCV CPU/CUDA, ArrayFire, KFAST) sur deux matériels (`page:7`).
- Code public (vilib, CUDA) : reproductible sur le PC GPU emprunté à l'école ; utilisable tel quel comme frontend d'un VIO de référence sur les flux Quest si on y accède un jour.
- Enseignement transférable au-delà de CUDA : pour un VIO qui suit 50–200 features, la parallélisation doit être **intra-feature** (un groupe de threads par patch), pas inter-features (`page:5`, `page:6`).
- Montre que l'accélération GPU paie **davantage sur l'embarqué** que sur le portable (pénalité mémoire) (`page:8`).
- Conformité vérifiée avec le FAST original (aucun faux positif) : l'optimisation ne change pas la nature des features (`page:6`).

## Contre / limites
- **Débit ≠ latence** : tout est en temps moyen par image ; aucune mesure de latence capteur → pose, ni de gigue, ni de prédiction (`page:7`, `page:8`).
- **Perte de précision** non négligeable sur le VIO complet : 0,47 point en moyenne, MH 04 TX2 0,81 → 1,85 % (`page:8`) ; les auteurs l'attribuent aux scènes sombres/rapides sans analyse (`page:7`).
- Mono-caméra, pas de carte persistante, pas de relocalisation, IMU absente du frontend : très loin de l'architecture complète d'Insight.
- **100 % CUDA/NVIDIA** (warps de 32, shuffles Kepler+, SIMT) ; aucune mention de mobile GPU, DSP ou OpenCL mobile — rien sur l'énergie, pourtant cruciale sur casque.
- Résolution d'image, nombre de niveaux de pyramide dans le VIO, et répartition du temps (Fig. 6, Fig. 7) non donnés dans le texte, seulement en figures.
- Backend ICE-BA réglé (LBA réduit à 15 images) pour la vitesse ; la comparaison « original vs ours » ne sépare pas l'effet du frontend de celui du réglage (`page:7`).
- Pas de comparaison à ORB-SLAM, VINS ou OpenVINS sur la précision.

## Idées à creuser pour mote
- *Hypothèse* : utiliser vilib comme **frontend de référence** d'un VIO PC (vilib + ICE-BA ou + OpenVINS) pour rejouer un enregistrement de capture mote et comparer la trajectoire à celle du casque et à COLMAP ; cela chiffrerait « ce qu'un VIO ouvert rapide donne » face aux 4–6 mm de SP-0.
- *Hypothèse* : le critère « une feature par cellule, grille uniforme » (`page:3`) peut servir de **score de qualité d'image** côté mote : rejeter ou signaler les images de capture où trop de cellules sont vides (surfaces unies, flou), car elles dégraderont à la fois le tracking et le 3DGS.
- *Hypothèse* : les séquences sombres/rapides dégradent le VIO (`page:7`) → imposer dans le protocole de capture mote un éclairage minimum et une vitesse angulaire bornée, mesurables depuis les poses MRUK.
- *Hypothèse* : pour un 3DGS entraîné sur PC, le **raffinement de poses** (H-01) pourrait réutiliser les 50–200 features KLT bien réparties comme contraintes géométriques légères (reprojection) plutôt qu'un COLMAP complet.
- *Hypothèse* : si un jour un frontend local est écrit sur casque (accès aux flux caméras), viser la variante **DSP/SIMD** plutôt que GPU, le GPU étant réservé au rendu ; la LUT 8 Ko et la fusion NMS + cellule (`page:4`) se portent sans dépendance CUDA.

## Citations clés
> « Especially non-maxima suppression and the subsequent feature selection are prominent contributors to the overall image processing latency. Our work first revisits the problem of non-maxima suppression for feature detection specifically on GPUs, and proposes a solution that selects local response maxima, imposes spatial feature distribution, and extracts features simultaneously. » (`doc:bb8e8aa/tier:standard/page:1`)

> « There are three popular heterogeneous architectures: (i) the first one uses a central processing unit (CPU) with a digital signal processor (DSP), and therefore it is restricted in its set of tasks; (ii) the second one combines a CPU with programmable logic (e.g. FPGA), which is versatile but increases development time; (iii) the third solution is the combination of a CPU with a GPU, which is not only cost-efficient but also excels in image processing tasks since GPUs are built for highly parallel tasks. » (`doc:bb8e8aa/tier:standard/page:1`)

> « The problems are approached from the viewpoint of VIO algorithms, where one generally does not track a high number of features (only 50-200), and these sparse features are also scattered throughout the image, which means that they are scattered in memory. [...] To address both of these concerns, one entire warp is launched for processing one feature. » (`doc:bb8e8aa/tier:standard/page:5`)

> « We summarize our findings in Table. VII, which shows an average speedup factor of 2.25× of the combined front- and back-end on both platforms, with an average accuracy loss of 0.47%. » (`doc:bb8e8aa/tier:standard/page:7`)

> « The speed improvement for the embedded computer is more pronounced, as there's a higher performance penalty for memory interactions than in the case of the laptop GPU. » (`doc:bb8e8aa/tier:standard/page:8`)

## Liens
- Dossier Insight : [Ce que fait le Quest avec ses caméras et son IMU](../../supports/meta2019_oculus-insight-quest/dossier.md) — « Quest-specific DSP tuning », 4 caméras + IMU 1 kHz, à confronter au choix CPU+GPU du papier.
- Papiers liés :
  - [Delmerico 2018, benchmark VIO](../delmerico2018_vio-benchmark/fiche.md) — même groupe ; cité (`page:7`) pour expliquer la dégradation sur MH 04/05 ; référence pour les contraintes CPU/mémoire des estimateurs ouverts.
  - [Navion (Suleiman 2019)](../suleiman2019_navion/fiche.md) — l'autre extrême de l'axe « accélération » : VIO sur ASIC dédié, à comparer au GPU embarqué.
  - [ORB-SLAM (Mur-Artal 2015)](../murartal2015_orb-slam/fiche.md) — cité comme pipeline à matching de features (`page:2`), approche opposée au suivi KLT.
  - [VINS-Mono](../qin2018_vins-mono/fiche.md), [VINS-Fusion](../qin2019_vins-fusion/fiche.md), [OpenVINS](../geneva2020_openvins/fiche.md), [Basalt](../usenko2020_basalt/fiche.md) — frontends FAST/KLT sur CPU que vilib pourrait remplacer.
  - [Kimera](../rosinol2020_kimera/fiche.md) — frontend KLT CPU également.
  - [Multi-caméras : Kuo 2020](../kuo2020_multicam-slam/fiche.md), [Eckenhoff 2019](../eckenhoff2019_multicam-vins/fiche.md) — pour l'extension à 4 caméras absente du papier.
  - [Project Aria (Engel 2023)](../engel2023_project-aria/fiche.md) — VIO embarqué Meta documenté, point de comparaison matériel.
  - [Huang 2019, revue VIN](../huang2019_vin-review/fiche.md) — cadre général des frontends/backends.
  - [DROID-SLAM](../teed2021_droid-slam/fiche.md), [DPVO](../teed2023_dpvo/fiche.md) — alternatives GPU « apprises » (frontend dense/patchs), à opposer à ce frontend GPU classique.
  - [3DGS (Kerbl 2023)](../kerbl2023_3dgs/fiche.md), [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md), [VRSplat](../tu2025_vrsplat/fiche.md) — côté rendu : même logique « from the GPU hardware's perspective » (tuiles, warps, réductions) appliquée au splatting.
