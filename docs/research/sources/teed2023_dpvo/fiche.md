---
citekey: teed2023_dpvo
mineru_doc: c6ac8e3
type: conférence   # NeurIPS 2023 (version lue : arXiv 2208.04726v2)
statut: fiche complète
tags: [odométrie-visuelle, vo-monoculaire, deep-vo, patches-épars, bundle-adjustment-différentiable, droid-slam, dso, tartanair, euroc, tum-rgbd, icl-nuim, rtx-3090, mémoire-gpu, fps, sans-imu, sans-fermeture-de-boucle, piste-mote]
---

# Deep Patch Visual Odometry (DPVO)

**Référence :** Zachary Teed\*, Lahav Lipson\*, Jia Deng (2023). *Deep Patch Visual Odometry.* NeurIPS 2023 (Advances in Neural Information Processing Systems 36). Version lue : arXiv [2208.04726v2](https://arxiv.org/abs/2208.04726), 23 mai 2023 (\* contribution égale, Princeton University). Code public : [github.com/princeton-vl/DPVO](https://github.com/princeton-vl/DPVO) (`doc:c6ac8e3/tier:standard/page:1`). DOI : non rapporté dans la version arXiv.
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
DPVO est une odométrie visuelle **monoculaire** apprise de bout en bout qui remplace le flot optique **dense** de DROID-SLAM par le suivi d'un petit nombre de **patches épars** (48–96 par image, tirés au hasard) via un opérateur récurrent couplé à un bundle adjustment différentiable : à précision supérieure sur TartanAir, EuRoC, TUM-RGBD et ICL-NUIM, il tourne à 60 FPS avec 4,9 Go de GPU (ou 120 FPS / 2,5 Go) sur RTX 3090, contre 40 FPS / 8,7 Go pour le frontend de DROID-SLAM (`page:1`, `page:2`, `page:8`).

## Problème traité
- Les VO/SLAM classiques (ORB-SLAM, DSO) manquent de robustesse : objets mobiles, pertes de suivi, mauvaise convergence ; sur le test TartanAir « Classical methods such as DSO and ORB-SLAM fail on more than 80% of the sequences » (`page:1`, `page:7`).
- Les VO apprises (DROID-SLAM) corrigent la robustesse par du **flot dense** entre paires d'images, mais au prix d'un coût de calcul « impractical for resource-constrained devices » : en mode VO (sans backend) DROID-SLAM fait en moyenne 40 FPS sur RTX 3090 avec 8,7 Go de mémoire GPU, et ralentit jusqu'à 11 FPS pendant les mouvements rapides car il crée plus de keyframes (`page:2`, `page:11`).
- Hypothèse implicite à réfuter : le flot dense serait nécessaire comme redondance contre les mauvais appariements. DPVO montre que des patches épars bien conçus font **mieux et plus vite** : « patch-based correspondence improves both efficiency and robustness over dense flow » (`page:2`).

## Méthode / contributions
- **Représentation par patches** (héritée de DSO) : chaque patch est un tableau homogène 4 × p² (x, y, 1, profondeur inverse d) à **profondeur constante** (plan fronto-parallèle dans l'image source), reprojeté dans les autres images par K T_j T_i⁻¹ K⁻¹ (éq. 1–2). Contrairement à DSO, les résidus ne sont pas photométriques mais prédits par un réseau qui gère lui-même le rejet des outliers (`page:2`, `page:3`).
- **Graphe de patches bipartite** (patches ↔ images) : chaque patch est relié aux images situées à moins de r indices de sa source, donc à au plus (2r − 1) images, ce qui **borne la latence pire cas** ; le graphe est dynamique (ajout/suppression de frames et patches) (`page:3`, `page:6`).
- **Extraction de features** : deux ResNets jumeaux (matching avec instance norm, D = 128 ; contexte sans normalisation, D = 384) à 1/4 de résolution + pyramide à 1/8 ; réseau « half the size » de celui de DROID-SLAM, mais résolution de sortie 1/4 au lieu de 1/8, permis par la parcimonie (`page:3`, `page:13`). Les patches sont **tirés au hasard** (centroïdes aléatoires), ce qui bat SIFT, ORB, SuperPoint et le gradient d'image en ablation (`page:3`, `page:8`).
- **Corrélation calculée à la volée** (pas de volume de corrélation précalculé comme DROID) : produit scalaire entre les features du patch et une grille 7 × 7 autour de sa reprojection, sur les deux niveaux de pyramide, en CUDA (éq. 4) (`page:4`, `page:12`).
- **Opérateur de mise à jour récurrent** sur les arêtes du graphe : corrélation → **convolution temporelle 1D** le long de la trajectoire du patch (voisins j−1, j+1) → **agrégation softmax** (message passing : par patch et par image, nécessaire car les patches épars n'ont pas la convolution spatiale du flot dense) → bloc de transition (2 unités résiduelles à portes + LayerNorm) → **factor head** : 2 MLP qui prédisent une révision 2D du flot δ ∈ ℝ² et une confiance Σ ∈ (0,1)² (`page:4`, `page:5`).
- **Bundle adjustment différentiable** : objectif de Mahalanobis (éq. 6) résolu par **2 itérations de Gauss-Newton** sur les poses et les profondeurs inverses, complément de Schur, gradients rétropropagés ; couche « functionally identical » à celle de DROID-SLAM mais en version éparse CUDA, facteur d'amortissement fixé à 10⁻⁴ au lieu d'être prédit (`page:5`, `page:12`).
- **Entraînement** 100 % synthétique sur TartanAir : séquences de 15 images (8 d'initialisation + 7 ajoutées une à une), flot inter-images échantillonné entre 16 et 72 px, 18 itérations déroulées, perte L = 10 L_pose + 0,1 L_flow (pose : alignement Umeyama puis erreur relative Log SE(3) sur toutes les paires), **240k itérations, batch 1, 3,5 jours sur une seule RTX 3090**, AdamW lr 8e-5 ; mêmes augmentations que DROID-SLAM (`page:5`, `page:6`, `page:11`).
- **Système VO** (Python + C++/CUDA pour BA et visualisation) : initialisation sur 8 images avec flot moyen ≥ 8 px et 12 itérations ; nouvelle image initialisée par **modèle à vitesse constante**, profondeur initiale = médiane des patches des 3 images précédentes ; à chaque image **1 itération de l'opérateur + 2 itérations de BA**, poses libres sur les 10 dernières keyframes seulement ; keyframing : les 3 dernières images sont toujours keyframes, la keyframe t−4 est supprimée si le flot entre t−5 et t−3 est < 64 px (`page:6`).
- Deux configurations : **Default** = 96 patches / fenêtre 10 images ; **Fast** = 48 patches / fenêtre 7 images. La précision sature au-delà de 96 patches (`page:6`, `page:12`, `page:13`). (La section « Related Work » parle de 64 patches par image, `page:2` : incohérence mineure du papier.)
- **Pas de fermeture de boucle, pas de relocalisation, pas d'IMU** : VO pure, optimisation locale seulement (comparée en priorité à DROID-VO, le frontend de DROID-SLAM) (`page:2`, `page:7`).

## Résultats chiffrés
| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| Matériel | **NVIDIA RTX 3090** (entraînement et inférence) ; mémoire mesurée par nvidia-smi | `page:2`, `page:5`, `page:8` |
| Fréquence moyenne | **Default : 60 FPS** (≈ 17 ms par image) ; **Fast : 120 FPS** ; DROID-VO : 40 FPS | EuRoC (vidéo 20 FPS, une image sur deux sautée comme DROID-SLAM) (`page:2`, `page:7`, `page:11`) |
| Stabilité de la fréquence | Default ≥ 48 FPS et Fast ≥ 98 FPS sur 95 % des images ; « rarely drops below 50fps » ; DROID-VO descend à **11 FPS** (écart 8,9×) ; FLOPs constants par image | Fig. 8, Fig. A (`page:7`, `page:8`, `page:11`) |
| Accélération vs DROID-VO | Default : 1,5× en moyenne, 4,3× au pire (5ᵉ percentile) ; Fast : 3× en moyenne, 8,9× au pire | `page:2`, `page:8` |
| Mémoire GPU | **DROID-VO 8,7 Go · DPVO Default 4,9 Go (57 %) · DPVO Fast 2,5 Go (29 %)** | EuRoC, nvidia-smi (`page:2`, `page:8`) |
| ATE TartanAir test (ECCV 2020 SLAM, 16 séq., alignement d'échelle) | ORB-SLAM3\* 14,38 · COLMAP\* 12,50 · DSO 7,32 · DROID-SLAM\* 0,33 · DROID-VO 0,58 · **DPVO Default 0,21** · Fast 0,28 (\* = optimisation globale / fermeture de boucle) ; −40 % vs DROID-SLAM, −64 % vs DROID-VO ; COLMAP met **2 jours** sur les 16 séquences et produit des reconstructions cassées | Tab. 1, médiane de 5 runs ; unité non précisée dans la légende (fenêtre d'erreur [0, 1] m en Fig. 7) (`page:6`, `page:7`) |
| AUC TartanAir validation (32 séq.) | **0,80 vs 0,71** pour DROID-SLAM, 4× plus rapide | fenêtre d'erreur [0, 1] m, 3 runs (`page:6`, `page:7`) |
| ATE EuRoC (11 séq., m) | TartanVO 0,680 · SVO 0,294 · DSO 0,601 · DROID-VO 0,186 · **DPVO Default 0,105** · Fast 0,129 ; −43 % vs DROID-VO ; pire séquence V203 : 0,211 (Default) / 0,310 (Fast) | Tab. 2, monoculaire, médiane de 5 runs (`page:7`) |
| ATE TUM-RGBD freiburg1 (9 séq., m) | DROID-VO 0,098 · **DPVO Default 0,089** (−9 %) · Fast 0,097 ; ORB-SLAM3 échoue sur 5/9 séquences (360, floor, room, rpy, teddy), DSO sur teddy ; pire séquence room : 0,394 | Tab. 3, vidéo 30 FPS, flou de bougé, médiane de 5 runs (`page:7`, `page:8`) |
| ATE ICL-NUIM (8 séq., m) | ORB-SLAM2\* N/A · DROID-SLAM\* 0,189 · DROID-VO 0,215 · SVO 0,136 · DSO 0,270 · DPVO Default 0,097 · **Fast 0,093** (−51 % vs DROID-SLAM, −32 % vs SVO) ; Office Room 3 reste à 0,635 / 0,593 | Tab. A, synthétique, murs blancs, 30 FPS (`page:11`, `page:12`) |
| Dérive | Non rapportée en % de distance (seul l'ATE après alignement Sim(3) est donné) | `page:11` |
| Latence | Non rapportée explicitement ; temps de traitement ≈ 17 ms par image (Default) ; pire cas borné par (2r − 1) images par patch ; visualiseur Pangolin ≈ +10 % | `page:6`, `page:11`, `page:12` |
| CPU / énergie / résolution d'image | Non rapportés | — |
| Temps d'entraînement | 240k itérations, **3,5 jours sur 1 RTX 3090**, batch 1 | TartanAir (`page:5`) |
| Ablations (TartanAir val.) | patches p × p > points 1 × 1 ; retirer la conv 1D ou l'agrégation softmax dégrade ; centroïdes aléatoires > SIFT / ORB / SuperPoint / gradient | Fig. 9, 3 runs, sans augmentation (`page:8`) |

## Ce que ça dit du tracking du Quest
- **Même famille d'idée que les landmarks d'Insight, mais apprise** : Insight suit des « high-contrast pixels » choisis à la main et les triangule en landmarks ; DPVO suit lui aussi un petit nombre de primitives éparses (48–96 patches par image) mais tirées **au hasard**, décrites par des features apprises, avec un rejet d'outliers appris via les confiances Σ (`page:3`, `page:5`, `page:8`). Le résultat d'ablation « random > SIFT/ORB/SuperPoint » (`page:8`) suggère que la sélection fine de coins, cœur des pipelines classiques, compte moins que la qualité de l'appariement et de la fenêtre d'optimisation.
- **Ce que DPVO n'a pas et que le casque a** : (i) **aucun IMU** — DPVO est monoculaire pur, donc **sans échelle métrique ni direction de gravité** : toutes ses ATE sont calculées **après alignement par similitude** (Sim(3), bibliothèque EVO) (`page:11`) ; le Quest (4 caméras + IMU) fournit directement des poses métriques ; (ii) **aucune carte persistante, fermeture de boucle ni relocalisation** : DPVO ne compare qu'à DROID-VO et assume l'absence de corrections globales (`page:2`, `page:7`), là où Insight relocalise sur une carte de pièce ; (iii) **pas de prédiction de pose à 1 kHz** : DPVO sort une pose par image traitée, initialisée par vitesse constante (`page:6`).
- **Budget de calcul** : DPVO tient dans 2,5–4,9 Go de VRAM et une RTX 3090 (`page:8`), avec des noyaux CUDA maison (corrélation, BA) (`page:4`, `page:12`) ; Insight tourne sur un SoC mobile avec « one order of magnitude less compute » (dossier Insight) et un DSP. Rien dans le papier ne porte sur CPU, mobile ou embarqué ; le financement Qualcomm est seulement mentionné dans les remerciements (`page:8`). DPVO est donc un **substitut PC** du tracking du casque, pas un candidat embarqué en l'état.
- **Implication pour les poses que mote récupère** : la vraie force transférable est la **constance du temps par image** (FLOPs constants, keyframing a posteriori, `page:7`, `page:11`), propriété que doit aussi avoir un tracker de casque. Côté précision, les ATE monoculaires de DPVO (≈ 5–40 cm sur EuRoC/TUM après alignement, `page:7`, `page:8`) restent **très au-dessus** de l'erreur médiane 4–6 mm mesurée en SP-0 entre poses Quest et COLMAP : une VO monoculaire apprise ne battrait pas le VI-SLAM du casque sur la précision absolue, mais pourrait servir de **raffinement local ou de contrôle indépendant** à partir de la vidéo RGB (voir idées).

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Référence pour la branche « VO apprise éparse » : chaîne features CNN → corrélation → opérateur récurrent → BA différentiable, en version patch plutôt que dense ; situe DSO, ORB-SLAM, DROID-SLAM, BA-Net, TartanVO (`page:2`, `page:3`). Explique pourquoi le dense est cher (8,7 Go, 40→11 FPS) (`page:2`, `page:11`) |
| 2. Poses pour 3DGS (piste mote, H-01) | Montre qu'un BA différentiable **épars** suffit pour des poses meilleures que COLMAP sur TartanAir (0,21 vs 12,50, COLMAP = 2 jours vs temps réel, `page:7`) : argument en faveur de poses « capteur + raffinement » plutôt que SfM complet. Mais sans échelle ni gravité (`page:11`) : à coupler avec les poses Quest comme prior |
| 3. Temps réel et contraintes embarquées | Chiffres précis fps / VRAM / stabilité (60 FPS, 4,9 Go ; 120 FPS, 2,5 Go ; ≥ 48 FPS sur 95 % des images, `page:2`, `page:7`, `page:8`) ; design borné en latence ((2r − 1) images par patch, `page:6`). **Aucun résultat CPU/mobile/DSP** : non rapporté |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole réutilisable : ATE après alignement Sim(3) (EVO), **médiane de 5 runs** (méthode stochastique), distinction SLAM\* (boucle) vs VO, AUC sur fenêtre [0, 1] m, distribution des fps (5ᵉ percentile) plutôt que moyenne seule, mémoire par nvidia-smi (`page:6`, `page:7`, `page:8`, `page:11`) |

## Pour (vis-à-vis de notre problématique)
- Seul VO appris de la base à donner **à la fois** précision, fps moyen, fps pire cas et mémoire GPU, avec deux points de fonctionnement (Default/Fast) qui chiffrent le compromis patches ↔ vitesse (`page:6`, `page:8`, `page:13`).
- Bat DROID-SLAM complet (avec fermeture de boucle) sur TartanAir test et ICL-NUIM tout en étant une VO locale (`page:7`, `page:12`) : un bon frontend compte plus que le backend sur des séquences courtes, ce qui est le régime d'une capture mote (quelques minutes).
- Entraîné uniquement sur du synthétique, généralise au réel (EuRoC, TUM-RGBD) (`page:2`, `page:11`) ; code public PyTorch + CUDA (`page:1`).
- Temps par image **quasi constant** quel que soit le mouvement (`page:7`, `page:11`) : propriété clé pour un pipeline quasi temps réel.
- Remplace COLMAP comme baseline classique sur TartanAir et documente son coût (2 jours, reconstructions cassées, `page:7`) — même constat que notre SP-0 (COLMAP 55–138 min).

## Contre / limites
- **Monoculaire sans IMU** : échelle et gravité indéterminées, ATE uniquement après alignement Sim(3) (`page:11`) ; inutilisable seul pour des poses métriques de casque.
- **Pas de carte, pas de relocalisation, pas de fermeture de boucle** : dérive long terme non évaluée, dérive en % de distance non rapportée (`page:2`).
- **GPU desktop obligatoire** (RTX 3090, noyaux CUDA maison pour corrélation et BA, `page:4`, `page:12`) ; aucun chiffre CPU, GPU portable, mobile ou DSP ; la motivation « resource-constrained devices » (`page:2`) n'est pas testée. Sur notre portable Iris Xe sans CUDA : **ne tourne pas** ; sur le PC GPU emprunté : oui (2,5–4,9 Go VRAM).
- Résultats stochastiques (patches aléatoires) : médiane de 5 runs, pas d'écart-type ni de taux d'échec rapporté (`page:6`).
- Échecs résiduels sur séquences dures : V203 0,21–0,31 m, room 0,39 m, Office Room 3 0,59–0,64 m (`page:7`, `page:8`, `page:12`).
- Keyframing « sub-optimal (in terms of speed) » quand la caméra est lente ou immobile (`page:11`) — cas fréquent d'un utilisateur de casque qui s'arrête.
- Résolution d'image, latence bout en bout, consommation : non rapportés.

## Idées à creuser pour mote
- *Hypothèse (H-01, raffinement des poses)* : utiliser le BA différentiable épars de DPVO comme **raffineur de poses Quest sur PC** : initialiser T avec les poses MRUK (au lieu du modèle à vitesse constante, `page:6`), fixer l'échelle/gravité par les poses casque, et ne laisser bouger que de petites corrections + profondeurs des patches. Coût attendu ≈ 17 ms/image sur GPU (`page:11`) contre 33–86 s de COLMAP en SP-0, dans le même ordre que l'acquisition.
- *Hypothèse (contrôle indépendant)* : faire tourner DPVO Fast (2,5 Go, 120 FPS) sur la vidéo passthrough RGB et comparer sa trajectoire alignée Sim(3) à celle du casque, comme second juge en plus de COLMAP (SP-0) ; les séquences où les deux divergent signaleraient des zones de dérive Quest.
- *Hypothèse (initialisation 3DGS)* : les patches de DPVO donnent une reconstruction éparse (Fig. 6, B, C, `page:6`, `page:11`, `page:12`) avec confiances : candidat de nuage initial pour 3DGS à la place des points SfM, à tester contre le nuage de la scène mesh Quest.
- *Protocole* : adopter « médiane de 5 runs + 5ᵉ percentile des fps + VRAM nvidia-smi » (`page:6`, `page:8`) pour nos propres mesures de pipeline.
- *Question ouverte* : la borne (2r − 1) images par patch et les FLOPs constants (`page:6`, `page:7`) sont-ils compatibles avec une exécution sur GPU portable (6–8 Go VRAM) ? À mesurer, le papier ne le dit pas.

## Citations clés
> « DPVO disproves this assumption, showing that it is possible to get the best accuracy and efficiency by exploiting the advantages of sparse patch-based matching over dense flow. » (`doc:c6ac8e3/tier:standard/page:1`)

> « in VO mode (without the backend), it averages 40FPS on an RTX-3090 using 8.7GB GPU memory, which can be impractical for resource-constrained devices. » (`doc:c6ac8e3/tier:standard/page:2`)

> « On an RTX-3090, it averages 60FPS using only 4.9GB of memory, with a minimum frame rate of 48FPS. It can run at 120FPS on the EuRoC dataset [2] using 2.5GB while still outperforming prior work on average. » (`doc:c6ac8e3/tier:standard/page:2`)

> « Our frame rates are practically near constant, since our method uses a constant number of FLOPS per-frame, unlike prior methods which slow down and make more keyframes during fast motion. » (`doc:c6ac8e3/tier:standard/page:6`, `page:7`)

> « We compare results using the ATE (average trajectory error) metric […] after aligning the two trajectories using a similarity transformation, to account for the scale and SE(3) gauge freedoms. » (`doc:c6ac8e3/tier:standard/page:11`)

## Liens
- Papiers liés :
  - [DROID-SLAM](../teed2021_droid-slam/fiche.md) — parent direct : DPVO = « sparsified variant of DROID-SLAM in VO mode » (`page:3`), même couche BA, mêmes données d'entraînement ; comparé en frontend (DROID-VO) et en SLAM complet.
  - [ORB-SLAM](../murartal2015_orb-slam/fiche.md), [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — baselines classiques indirectes ; échecs sur TartanAir et 5/9 séquences TUM (`page:7`, `page:8`).
  - [VINS-Mono](../qin2018_vins-mono/fiche.md), [VINS-Fusion](../qin2019_vins-fusion/fiche.md), [OpenVINS](../geneva2020_openvins/fiche.md), [Basalt](../usenko2020_basalt/fiche.md) — ce que DPVO n'a pas : fusion IMU, échelle métrique, gravité.
  - [Kimera](../rosinol2020_kimera/fiche.md) — VIO + backend avec fermeture de boucle, à opposer à la VO locale pure.
  - [Benchmark VIO (Delmerico 2018)](../delmerico2018_vio-benchmark/fiche.md), [Navion](../suleiman2019_navion/fiche.md) — pour les contraintes embarquées que DPVO ne traite pas.
  - [Photo-SLAM](../huang2024_photo-slam/fiche.md), [Survey NeRF/GS SLAM](../tosi2024_nerf-gs-slam-survey/fiche.md) — le pont VO/SLAM → 3DGS.
  - [3DGS](../kerbl2023_3dgs/fiche.md) — consommateur des poses ; [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md) pour le budget d'entraînement sur PC.
  - [Project Aria](../engel2023_project-aria/fiche.md), [Précision positionnelle VR (Banaszczyk 2024)](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — ce que Meta publie du VIO et la précision mesurée des casques.
  - Dossier [Oculus Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) — référence pour la section « Ce que ça dit du tracking du Quest ».
