---
citekey: tosi2024_nerf-gs-slam-survey
mineru_doc: 2751f35
type: survey   # prépublication arXiv 2402.13255v3 (27 mars 2025), 25 p., 80 systèmes recensés
statut: fiche complète
tags: [survey, slam, nerf-slam, 3dgs-slam, rgb-d, monoculaire, tracking-couplé, tracking-découplé, tracker-externe, orb-slam3, droid-slam, dpvo, photo-slam, monogs, splatam, gs-slam, gs-icp-slam, fermeture-de-boucle, bundle-adjustment, ate, psnr, replica, tum-rgbd, scannet, rtx-3090, temps-réel, piste-mote]
---

# How NeRFs and 3D Gaussian Splatting are Reshaping SLAM: a Survey

**Référence :** Fabio Tosi, Youmin Zhang, Ziren Gong, Erik Sandström, Stefano Mattoccia, Martin R. Oswald, Matteo Poggi (2024). *How NeRFs and 3D Gaussian Splatting are Reshaping SLAM: a Survey.* Université de Bologne / Rock Universe / ETH Zurich / Université d'Amsterdam. Prépublication arXiv [2402.13255](https://arxiv.org/abs/2402.13255), v3 du 27 mars 2025, 25 p. (`doc:2751f35/tier:standard/page:1`). Venue de publication finale : non rapportée dans le PDF. Pas de code (survey) ; liste de ressources associée : github.com/DoongLi/awesome-Implicit-NeRF-SLAM (`page:2`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Premier survey consacré aux SLAM denses dont la carte est un champ de radiance (NeRF ou 3DGS) : 80 systèmes publiés entre iMAP (ICCV 2021) et ECCV/IROS 2024, une taxonomie par capteur (RGB-D / RGB / LiDAR) et par type de couplage tracking–cartographie, et des tableaux croisés (ATE sur TUM RGB-D, ScanNet, Replica ; reconstruction et PSNR sur Replica ; mémoire GPU et FPS sur RTX 3090) dont la conclusion principale est que les systèmes **découplés** à tracker externe classique (ORB-SLAM3, DROID-SLAM, DPVO) avec BA global / fermeture de boucle dominent en précision de trajectoire, tandis que le tracking **par rendu différentiable 3DGS** gagne en qualité d'image mais reste bruité et très lent (`page:2`, `page:15`, `page:19`, `page:20`).

## Problème traité
- Les SLAM « classiques » (KinectFusion, ORB-SLAM, ElasticFusion…) sont temps réel et scalables mais souffrent des changements d'illumination, des zones peu texturées et des représentations discrètes (nuages de points/surfels, voxels, octrees) : cartes creuses, résolution limitée, impossibilité d'extrapoler dans les zones non observées (`page:1`, `page:2`).
- NeRF (2020) et 3DGS (2023) apportent une surface continue, moins de mémoire (pour NeRF), un meilleur traitement du bruit et le remplissage des trous, mais ont été conçus **hors ligne avec poses connues (COLMAP)** ; les variantes « sans poses » (iNeRF, NeRF--, BARF) traitent un lot d'images d'un coup et ne sont pas séquentielles, donc pas temps réel (`page:2`, `page:4`).
- Aucun survey ne couvrait ces SLAM « champ de radiance » ; les auteurs en recensent 80 en trois ans, avec une date butoir ECCV/IROS 2024 (`page:2`).
- Deux stratégies héritées de BundleFusion structurent l'analyse : **frame-to-frame** (temps réel, poses raffinées ensuite par fermeture de boucle ou BA global) et **frame-to-model** (poses estimées contre le modèle 3D reconstruit, sans optimisation ultérieure, moins scalable) ; ce qui recoupe la distinction **découplé** (tracking et mapping dans deux cadres séparés) / **couplé** (une seule représentation pour les deux) (`page:2`, `page:3`).

## Contenu / taxonomie
**Organisation du survey** : II. fond théorique (NeRF, SDF/TSDF, 3DGS, équations 1–11), datasets et métriques ; III. taxonomie des systèmes ; IV. tableaux comparatifs ; V. discussion (`page:2`).

### Taxonomie (Table I, `page:7`)
| Axe | Catégories | Exemples |
|---|---|---|
| **Capteur** | RGB-D (III-A, 59 entrées de la Table I) · RGB mono/stéréo (III-B) · LiDAR (III-C) | — |
| **Représentation de la carte** | NeRF-style : MLP seul (iMAP), grilles hiérarchiques + MLP (NICE-SLAM), hash grid (Co-SLAM, GO-SLAM), plans de features (ESLAM), points neuronaux (Point-SLAM, Loopy-SLAM), Plenoxels · **3DGS-style : « 3D Gaussians / Density »** | III-A2 (RGB-D 3DGS) : MonoGS, Photo-SLAM, SplaTAM, GS-SLAM, GS-ICP SLAM, HF-GS SLAM, CG-SLAM, MM3DGS-SLAM, RTG-SLAM ; III-B2 (RGB 3DGS) : MonoGS++ ; III-C2 (LiDAR 3DGS) : LIV-GaussMap, MM-Gaussian ; sémantique 3DGS : SGS-SLAM, NEDS-SLAM, GS3LAM ; dynamique : DG-SLAM |
| **Géométrie** | Density, Occupancy, SDF, TSDF | — |
| **Tracking** | Frame-to-model · Frame-to-frame · **Tracker externe** (ORB-SLAM2/3, DROID, DPVO, G-ICP, SuperPoint+SuperGlue, SIFT, HF-Net, Kiss-ICP) · Global BA · Loop Closure | voir tableau « Qui fait le tracking ? » ci-dessous |
| **Entrées supplémentaires** | Stéréo, **IMU** (MM3DGS-SLAM, OpenWorld-SLAM, NVINS, LIV-GaussMap), événements (EN-SLAM) | `page:7`, `page:10`, `page:12`, `page:13`, `page:14` |
| **Stratégies avancées** | Sous-cartes (MeSLAM, MIPS-Fusion, NGEL-SLAM, Loopy-SLAM, NEWTON…), scènes dynamiques, incertitude, sémantique | `page:10`–`page:12` |
| **Priors externes** | profondeur mono (DPT, ZoeDepth, Omnidata, Depth Anything), flot (GMFlow), segmentation (SAM, Mask2Former), place recognition (NetVLAD) | `page:7` |

**RGB vs RGB-D** : le RGB seul souffre de l'ambiguïté d'échelle et de l'absence de prior géométrique (convergence plus lente) ; d'où la sous-catégorie « aided supervision » (III-B3) où un tracker externe + des priors de profondeur/normales disambiguïsent l'optimisation (iMODE avec ORB-SLAM2 sur CPU, Hi-SLAM et NeRF-SLAM avec DROID, NeRF-VO avec DPVO, MGS-SLAM = DPVO + profondeur MVS + 3DGS) (`page:13`, `page:14`). **Stéréo** : seuls GO-SLAM (mono/stéréo/RGB-D) et Photo-SLAM (mono/stéréo/RGB-D) sont donnés comme stéréo-compatibles (`page:7`, `page:8`).

**Fermeture de boucle et BA global** : coûteux car les grilles de features ne tolèrent pas une correction de poses — il faut réallouer la grille et réentraîner toute la carte ; les méthodes frame-to-model (iMAP, NICE-SLAM) n'en ont donc pas, les frame-to-frame (GO-SLAM) exécutent le BA global dans un thread d'arrière-plan « although at a slower computational speed compared to real-time rates » (`page:20`). Les 3DGS-SLAM de la Table II/IV n'ont **ni BA global ni fermeture de boucle**, sauf ceux qui héritent d'un tracker externe (MGS-SLAM via DPVO + BA, DG-SLAM via DROID + BA) (`page:15`).

### Qui fait le tracking ? — 3DGS **au service du tracking** vs **poses d'un tracker classique**
| Système (venue) | Entrées | Où viennent les poses | BA / LC | Pages |
|---|---|---|---|---|
| **MonoGS** (CVPR 2024) | RGB-D ou RGB | **Couplé, frame-to-model** : « The tracking phase adopts a direct optimization scheme against the 3D Gaussians » ; fenêtre de keyframes par covisibilité, élagage des Gaussiennes instables | non / non | `page:9`, `page:15` |
| **SplaTAM** (CVPR 2024) | RGB-D | **Couplé** : « Camera Tracking, minimizing re-rendering errors » (rendu différentiable silhouette/couleur/profondeur) | non / non | `page:9`, `page:15` |
| **GS-SLAM** (CVPR 2024) | RGB-D | **Couplé** : tracking coarse-to-fine itératif contre la carte de Gaussiennes, expansion adaptative | non / non | `page:9`, `page:15` |
| **CG-SLAM** (ECCV 2024) | RGB-D | **Couplé** : champ de Gaussiennes « uncertainty-aware », dérivées de pose analysées dans le splatting EWA | non / non | `page:10`, `page:15` |
| **HF-GS SLAM** (IROS 2024) | RGB-D | Couplé (le survey ne décrit que la densification guidée par la perte de rendu et la régularisation anti-oubli) | non / non | `page:10`, `page:15` |
| **RTG-SLAM** (SIGGRAPH 2024) | RGB-D | Non détaillé par le survey (Gaussiennes opaques/transparentes, ajout à la volée, stables/instables) | non / non | `page:10`, `page:15` |
| **MM3DGS-SLAM** (IROS 2024) | RGB-D ou RGB **+ IMU** | Couplé hybride : « combined tracking loss incorporating depth measurements and IMU pre-integration » ; keyframes par covisibilité + NIQE | non rapporté | `page:7`, `page:10` |
| **GS-ICP SLAM** (ECCV 2024) | RGB-D | **Tracker géométrique externe G-ICP** sur les centres/covariances des Gaussiennes (échange bidirectionnel carte ↔ ICP) | non / non | `page:9`, `page:10`, `page:15` |
| **Photo-SLAM** (CVPR 2024) | RGB-D, **mono, stéréo** | **Découplé : ORB-SLAM3 comme tracker externe** (Table I) ; carte « hyper primitives » = features ORB + rotation/échelle/densité/SH ; densification géométrique et apprentissage par pyramide gaussienne avec perte photométrique | colonnes BA/LC illisibles dans la Table I aplatie ; non rapporté | `page:7`, `page:9`, `page:17` |
| **MonoGS++** (BMVC 2024) | RGB | **Découplé : DPVO** fournit poses initiales et points 3D qui amorcent les Gaussiennes ; insertion guidée par régularisation planaire | non / non | `page:7`, `page:13`, `page:15` |
| **MGS-SLAM** (RAL 2024) | RGB | **Découplé : odométrie visuelle creuse (DPVO) + profondeur MVS** supervisant la carte 3DGS | BA global ✓ / non | `page:7`, `page:14`, `page:15` |
| **DG-SLAM** (NeurIPS 2024) | RGB-D dynamique | **Découplé : DROID** + « hybrid camera tracking » | BA global ✓ / non | `page:7`, `page:12`, `page:15` |
| LIV-GaussMap / MM-Gaussian (RAL/IROS 2024) | LiDAR + IMU + caméra / LiDAR + caméra | Recalage de nuages (Kiss-ICP pour MM-Gaussian), relocalisation ; Gaussiennes issues des voxels LiDAR | non rapporté | `page:7`, `page:14` |

Lecture pour mote : **le schéma « poses d'un tracker classique → 3DGS côté carte » existe déjà dans la littérature (Photo-SLAM/ORB-SLAM3, MonoGS++/DPVO, MGS-SLAM/DPVO, GS-ICP/ICP)** et c'est ce schéma que le survey désigne comme le plus précis en trajectoire ; mote remplace simplement le tracker logiciel par le VI-SLAM du casque.

### Datasets et métriques (`page:5`, `page:6`)
- **TUM RGB-D** : 39 séquences Kinect 640×480 à 30 Hz, vérité terrain par motion capture à 8 caméras à 100 Hz ; « sparse depth sensor information and high motion blur » (`page:5`, `page:15`).
- **ScanNet** : 2,5 M d'images, 1513 scans, 707 espaces, iPad + structure sensor ; **poses dérivées de BundleFusion, « may not be as accurate as alternatives such as TUM RGB-D »** (`page:5`, `page:20`).
- **Replica** : 18 scènes ; les séquences SLAM sont **synthétiques** (rendues depuis les maillages), « lack real-world characteristics like specular highlights, autoexposure, blur » (`page:5`).
- Datasets VI mentionnés sans résultats : EuRoC MAV (stéréo + IMU, vérité terrain millimétrique), ETH3D-SLAM (VI mono/stéréo/RGB-D), 7-scenes (`page:6`).
- Métriques : **ATE RMSE (cm), translation seule, après alignement** ; Acc./Comp./Comp. Ratio (seuil 5 cm), L1-Depth ; PSNR/SSIM/LPIPS ; mIoU (`page:6`).

## Résultats chiffrés
Tous les chiffres ci-dessous sont **compilés par le survey depuis les papiers d'origine** (protocole commun, « cross-verified », `page:15`), sauf la Table XI mesurée par les auteurs sur **une NVIDIA RTX 3090** (`page:15`, `page:18`).

### ATE RMSE (cm) — TUM RGB-D, Table II (`page:15`)
| Méthode | Tracker / BA / LC | fr1/desk | fr2/xyz | fr3/office | Moy. |
|---|---|---|---|---|---|
| *RGB-D* | | | | | |
| ORB-SLAM2 (baseline classique) | — / BA / LC | 1,6 | 0,4 | 1,0 | **1,0** |
| BAD-SLAM | — / BA / LC | 1,7 | 1,1 | 1,7 | 1,5 |
| Kintinuous | — | 3,7 | 2,9 | 3,0 | 3,2 |
| GS-SLAM | couplé | 3,3 | 1,3 | 6,6 | 3,7 |
| SplaTAM | couplé | 3,4 | 1,2 | 5,2 | 3,3 |
| HF-GS SLAM | couplé | 3,4 | – | 5,1 | – |
| GS-ICP SLAM | G-ICP | 2,7 | 1,8 | 2,7 | 2,4 |
| CG-SLAM | couplé | 2,4 | 1,2 | 2,5 | 2,0 |
| MonoGS | couplé | 1,5 | 1,6 | 1,7 | 1,6 |
| RTG-SLAM | — | 1,7 | 0,4 | 1,1 | 1,1 |
| GO-SLAM (NeRF) | DROID / BA / LC | 1,5 | 0,6 | 1,3 | 1,1 |
| NGEL-SLAM (NeRF) | **ORB3** / BA / LC | 1,5 | 0,5 | 1,0 | 1,0 |
| Q-SLAM, ONeK-SLAM (NeRF) | DROID ; SIFT | 1,4 ; 1,5 | 0,5 ; 0,3 | 1,1 ; 1,1 | 1,0 ; 1,0 |
| *RGB* | | | | | |
| ORB-SLAM2 | — / BA / LC | 1,9 | 0,6 | 2,4 | 1,6 |
| DROID-SLAM | — / BA | 1,8 | 0,5 | 2,8 | 1,7 |
| **MonoGS (mono)** | couplé | 4,2 | 4,8 | 4,4 | **4,4** |
| MGS-SLAM | DPVO / BA | 2,3 | 0,4 | 3,0 | 1,9 |
| Orbeez-SLAM (NeRF) | ORB2 | 1,9 | 0,3 | 1,0 | 1,1 |
| **MonoGS++** | **DPVO** | 1,8 | 0,4 | 0,4 | **0,9** |

Photo-SLAM **n'apparaît dans aucun tableau d'ATE** du survey (seulement en PSNR, Table VI). Lecture : en RGB-D, les 3DGS couplés (3,3–3,7 cm) restent 3× derrière ORB-SLAM2 (1,0) ; en mono, passer de MonoGS (couplé, 4,4) à MonoGS++ (poses DPVO, 0,9) divise l'erreur par ~5 (`page:15`).

### ATE RMSE (cm) — ScanNet (6 scènes), Table III (`page:15`)
| Méthode | Tracker / BA / LC | 0000 | 0059 | 0106 | 0169 | 0181 | 0207 | Moy. |
|---|---|---|---|---|---|---|---|---|
| SplaTAM | couplé | 12,83 | 10,10 | 17,72 | 12,08 | 11,10 | 7,46 | 11,88 |
| NEDS-SLAM (3DGS sém.) | couplé | 12,34 | – | – | 11,21 | 10,35 | 6,56 | – |
| CG-SLAM | couplé | 7,09 | 7,46 | 8,88 | 8,16 | 11,60 | 5,34 | 8,08 |
| DG-SLAM | DROID / BA | 7,9 | 11,5 | 8,0 | 8,3 | 7,3 | 8,2 | 8,6 |
| NICE-SLAM (NeRF) | couplé | 8,64 | 12,25 | 8,09 | 10,28 | 12,93 | 5,59 | 9,63 |
| GO-SLAM (NeRF) | DROID / BA / LC | 5,35 | 7,52 | 7,03 | 7,74 | 6,84 | 4,78 | 6,54 |
| MoD-SLAM (NeRF) | DROID / LC | 5,27 | 7,44 | 6,73 | 6,48 | 6,14 | 5,31 | **6,23** |
| DROID-SLAM RGB-D (BA) | — | 5,36 | 7,72 | 7,06 | 8,01 | 6,97 | – | – |

MonoGS, GS-SLAM, GS-ICP, Photo-SLAM : non rapportés sur ScanNet. Les erreurs à 6–12 cm reflètent aussi la vérité terrain BundleFusion (`page:5`, `page:20`).

### ATE RMSE (cm) — Replica (8 scènes), Table IV (`page:16`)
Le tableau est aplati par MinerU ; les lignes ci-dessous ont été réassociées en recalculant les moyennes (toutes cohérentes à ±0,01).
| Méthode | Tracker / BA / LC | R0 | R1 | R2 | O0 | O1 | O2 | O3 | O4 | Moy. |
|---|---|---|---|---|---|---|---|---|---|---|
| *RGB-D* | | | | | | | | | | |
| NICE-SLAM (NeRF) | couplé | 1,69 | 2,04 | 1,55 | 0,99 | 0,90 | 1,39 | 3,97 | 3,08 | 1,95 |
| MonoGS | couplé | 0,76 | 0,37 | 0,23 | 0,66 | 0,72 | 0,30 | 0,19 | 1,46 | 0,58 |
| Point-SLAM (NeRF) | couplé | 0,61 | 0,41 | 0,37 | 0,38 | 0,48 | 0,54 | 0,72 | 0,63 | 0,52 |
| GS-SLAM | couplé | 0,48 | 0,53 | 0,33 | 0,52 | 0,41 | 0,59 | 0,46 | 0,70 | 0,50 |
| GS3LAM (3DGS sém.) | couplé | 0,27 | 0,25 | 0,28 | 0,67 | 0,21 | 0,33 | 0,30 | 0,65 | 0,37 |
| SplaTAM | couplé | 0,31 | 0,40 | 0,29 | 0,47 | 0,27 | 0,29 | 0,32 | 0,55 | 0,36 |
| NEDS-SLAM (3DGS sém.) | couplé | – | – | – | – | – | – | – | – | 0,35 |
| GO-SLAM (NeRF) | DROID / BA / LC | 0,32 | 0,30 | 0,39 | 0,39 | 0,46 | 0,34 | 0,29 | 0,29 | 0,34 |
| MoD-SLAM (NeRF) | DROID / LC | – | – | – | – | – | – | – | – | 0,33 |
| Loopy-SLAM (NeRF) | — / LC | 0,24 | 0,24 | 0,28 | 0,26 | 0,40 | 0,29 | 0,22 | 0,35 | 0,29 |
| CG-SLAM | couplé | 0,29 | 0,27 | 0,25 | 0,33 | 0,14 | 0,28 | 0,31 | 0,29 | 0,27 |
| HF-GS SLAM | couplé | 0,19 | 0,34 | 0,16 | 0,21 | 0,26 | 0,23 | 0,21 | 0,38 | 0,25 |
| **GS-ICP SLAM** | G-ICP | 0,15 | 0,16 | 0,11 | 0,18 | 0,12 | 0,17 | 0,16 | 0,21 | **0,16** |
| *RGB* | | | | | | | | | | |
| DROID-SLAM | — / BA | – | – | – | – | – | – | – | – | 0,42 |
| NICER-SLAM (NeRF) | couplé | 1,36 | 1,60 | 1,14 | 2,12 | 3,23 | 2,12 | 1,42 | 2,01 | 1,88 |
| GO-SLAM (NeRF) | DROID / BA / LC | – | – | – | – | – | – | – | – | 0,39 |
| MoD-SLAM (NeRF) | DROID / LC | 0,28 | 0,29 | 0,30 | 0,40 | 0,45 | 0,50 | 0,31 | 0,27 | 0,35 |
| MGS-SLAM | DPVO / BA | 0,36 | 0,35 | 0,32 | 0,35 | 0,28 | 0,26 | 0,32 | 0,34 | 0,32 |
| **MonoGS++** | **DPVO** | 0,20 | 0,17 | 0,22 | 0,29 | 0,13 | 0,42 | 0,20 | 0,42 | **0,26** |

Commentaire du survey : sur Replica (images synthétiques propres) les 3DGS obtiennent les meilleurs scores (CG-SLAM, HF-GS, GS-ICP) mais « This suggests that these approaches struggle with noise and work best in simpler situations, showing less reliability in complex conditions » (`page:16`, `page:17`). MonoGS mono n'est pas rapporté sur Replica ; Photo-SLAM absent.

### Reconstruction — Replica, Table V (`page:16`)
| Méthode | L1-Depth (cm) ↓ | Acc. (cm) ↓ | Comp. (cm) ↓ | Comp. Ratio (%) ↑ |
|---|---|---|---|---|
| COLMAP (référence) | – | 8,69 | 12,12 | 67,62 |
| TSDF fusion | 7,57 | 1,60 | 3,49 | 86,08 |
| NICE-SLAM | 3,53 | 2,85 | 3,00 | 89,33 |
| SplaTAM | 0,72 | – | – | – |
| HF-GS SLAM | 0,52 | – | – | – |
| NEDS-SLAM | 0,47 | – | – | – |
| Point-SLAM | 0,44 | 1,41 | 3,10 | 88,89 |
| Loopy-SLAM | **0,35** | – | – | – |
| CG-SLAM | – | **1,01** | 2,84 | 88,51 |
| MGS-SLAM (RGB) | 7,77 | 7,51 | 3,64 | 82,71 |

Les 3DGS-SLAM ne rapportent en général **pas** Acc./Comp. (pas d'extraction de maillage directe, `page:20`) ; GO-SLAM, très bon en tracking, est faible en cartographie (L1 4,68) (`page:16`, `page:17`).

### Rendu — PSNR (dB) sur les **vues d'entraînement** de Replica, Table VI (`page:17`)
| Méthode | R0 | R1 | R2 | O0 | O1 | O2 | O3 | O4 | Moy. |
|---|---|---|---|---|---|---|---|---|---|
| *RGB-D* | | | | | | | | | |
| NICE-SLAM (NeRF) | 22,12 | 22,47 | 24,52 | 29,07 | 30,34 | 19,66 | 22,23 | 24,94 | 24,42 |
| ESLAM (NeRF) | – | – | – | – | – | – | – | – | 27,80 |
| SplaTAM | 32,86 | 33,89 | 35,25 | 38,26 | 39,17 | 31,97 | 29,70 | 31,81 | 34,11 |
| GS-SLAM | 31,56 | 32,86 | 32,59 | 38,70 | 41,17 | 32,36 | 32,03 | 32,92 | 34,27 |
| NEDS-SLAM | 35,23 | 34,86 | 35,16 | 37,53 | 39,71 | 32,68 | 31,07 | 31,82 | 34,76 |
| Point-SLAM (NeRF) | 32,40 | 34,08 | 35,50 | 38,26 | 39,16 | 33,99 | 33,48 | 33,49 | 35,17 |
| Loopy-SLAM (NeRF) | – | – | – | – | – | – | – | – | 35,47 |
| HF-GS SLAM | 33,06 | 35,74 | 37,21 | 41,12 | 41,11 | 33,56 | 33,21 | 34,48 | 36,19 |
| GS3LAM | 33,67 | 35,80 | 35,96 | 40,28 | 41,21 | 34,30 | 34,27 | 34,59 | 36,26 |
| MonoGS | 34,83 | 36,43 | 37,49 | 39,95 | 42,09 | 36,24 | 36,70 | 36,07 | 37,50 |
| **GS-ICP SLAM** | 35,37 | 37,80 | 38,50 | 43,13 | 43,26 | 36,93 | 36,90 | 38,75 | **38,83** |
| *RGB* | | | | | | | | | |
| NICER-SLAM (NeRF) | 25,33 | 23,92 | 26,12 | 28,54 | 25,86 | 21,95 | 26,13 | 25,47 | 25,41 |
| MGS-SLAM | 29,91 | 31,06 | 31,49 | 35,51 | 34,25 | 30,83 | 31,86 | 34,38 | 32,41 |
| **Photo-SLAM** | – | – | – | – | – | – | – | – | **33,30** |
| **MonoGS++** | 33,75 | 36,47 | 37,01 | 42,31 | 43,05 | 36,11 | 36,34 | 37,28 | **37,79** |

**SSIM et LPIPS : définis (`page:6`) mais non tabulés** par le survey ; seul le PSNR est donné. Le survey note un gain « of over 10dB in PSNR » des méthodes 3DGS / points neuronaux sur les grilles de NICE-SLAM, et partage la réserve de SplaTAM : évaluer sur les vues d'entraînement « may introduce biases due to high model capacity and potential overfitting » (`page:17`).

### Performance mesurée par les auteurs — Replica room0, **RTX 3090**, Table XI (`page:19`)
| Méthode | Encodage | Mémoire GPU pic (GB) | FPS moyen (séquence entière / nb d'images) |
|---|---|---|---|
| iMAP | MLP | 6,44 | 0,13 |
| **SplaTAM** | 3D Gaussians | **18,54** | **0,14** |
| Point-SLAM | points neuronaux + MLP | 7,11 | 0,23 |
| NICE-SLAM | grille hiér. + MLP | 4,70 | 0,61 |
| Vox-Fusion | voxels épars + MLP | 21,22 | 0,74 |
| ESLAM | plans de features + MLP | 13,04 | 4,62 |
| Co-SLAM | hash grid + MLP | 3,56 | 7,97 |
| GO-SLAM | hash grid + MLP (tracker DROID) | 18,50 | 8,36 |
| DIM-SLAM (RGB) | grille hiér. + MLP | 4,78 | 3,14 |
| Orbeez-SLAM (RGB, tracker ORB2) | voxels + MLP | 7,55 | 17,70 |
| NeRF-SLAM (RGB, tracker DROID) | hash grid + MLP | 9,38 | **20,00** |

**MonoGS, Photo-SLAM, GS-SLAM, GS-ICP, CG-SLAM : non mesurés** dans Table XI (seul SplaTAM représente le 3DGS). **FPS de tracking et FPS de mapping séparés : non rapportés** (un seul FPS global). Verdict des auteurs : « SplaTAM, despite its high efficiency at rendering images, is however much slower at processing both tracking and mapping simultaneously » (`page:18`) et « most of them are still unsatisfactory in terms of hardware and runtime requirements, making them not yet ready for real-time applications » (`page:19`).

### Synthèse
| Métrique | Valeur | Conditions |
|---|---|---|
| ATE meilleure RGB-D TUM | 1,0 cm : ORB-SLAM2, NGEL-SLAM (ORB3), Q-SLAM (DROID), ONeK ; meilleur 3DGS couplé : MonoGS 1,6 ; SplaTAM 3,3 ; GS-SLAM 3,7 | Table II, 3 séquences (`page:15`) |
| ATE meilleure RGB TUM | MonoGS++ (DPVO) 0,9 cm vs MonoGS couplé 4,4 ; ORB-SLAM2 1,6 | `page:15` |
| ATE Replica | GS-ICP 0,16 ; HF-GS 0,25 ; CG-SLAM 0,27 ; SplaTAM 0,36 ; MonoGS 0,58 ; MonoGS++ (RGB) 0,26 | synthétique, 8 scènes (`page:16`) |
| ATE ScanNet | SplaTAM 11,88 ; CG-SLAM 8,08 ; MoD-SLAM 6,23 (meilleur) | vérité terrain BundleFusion (`page:15`) |
| PSNR Replica (vues d'entraînement) | GS-ICP 38,83 ; MonoGS 37,50 ; MonoGS++ 37,79 (RGB) ; Photo-SLAM 33,30 (RGB) ; SplaTAM 34,11 ; NICE-SLAM 24,42 | `page:17` |
| SSIM / LPIPS | non rapportés (définis seulement) | `page:6` |
| FPS | SplaTAM 0,14 ; GO-SLAM 8,36 ; NeRF-SLAM 20 ; MonoGS/Photo-SLAM non mesurés | RTX 3090, Replica room0 (`page:19`) |
| Mémoire GPU | SplaTAM 18,54 GB ; Co-SLAM 3,56 GB ; GO-SLAM 18,50 GB | idem |
| Temps par image / latence | non rapportés (seulement FPS moyen) | — |
| Dérive, erreur de rotation | non rapportées (ATE = translation seule, `page:6`) | — |
| CPU / embarqué | non rapporté ; seule mention : « resource-constrained devices » comme obstacle (`page:20`) | — |

## Ce que ça dit du tracking du Quest
- **Le survey ne mentionne ni Oculus Insight, ni les casques, ni le multi-caméra** : son périmètre est le SLAM dont la *carte* est un champ de radiance. Les seuls systèmes à IMU recensés sont MM3DGS-SLAM (pré-intégration IMU dans la perte de tracking 3DGS, `page:10`), OpenWorld-SLAM et NVINS (NeRF + VIO fusionnés dans un cadre bayésien, `page:12`) et LIV-GaussMap (LiDAR-inertiel-visuel, `page:14`). Rien sur la prédiction de pose, la carte persistante multi-sessions, le DSP ou le multi-caméra.
- En revanche, **la taxonomie du survey place exactement Insight** : c'est un tracker **frame-to-frame, creux (points de contraste suivis puis triangulés), découplé, avec carte persistante, relocalisation et fermeture de boucle** — le rôle que jouent ORB-SLAM3 dans Photo-SLAM / NGEL-SLAM / vMAP, DROID dans GO-SLAM, DPVO dans MonoGS++ (`page:7`, `page:9`, `page:11`, `page:13`). Le survey décrit ce rôle comme celui qui donne les meilleures trajectoires : « decoupled methods using external trackers such as ORB3 and DROID, along with advanced strategies such as Global BA and LC, emerge as top performers » (`page:15`) et « decoupled methods, which separate the mapping and tracking processes, tend to achieve better tracking performance compared to coupled approaches » (`page:20`).
- Différences avec les trackers externes du survey : (1) ces trackers consomment **les mêmes images** que la carte 3DGS, alors qu'Insight suit avec 4 caméras monochromes grand angle et que mote entraîne le 3DGS sur la caméra couleur passthrough — l'extrinsèque caméra couleur ↔ repère de tracking et la synchronisation temporelle deviennent une source d'erreur que le survey n'évalue pas ; (2) ORB-SLAM3 / DROID tournent sur le PC d'évaluation, Insight sur le SoC du casque avec un budget calcul fixe ; (3) ORB-SLAM3 et DROID exposent BA global et fermeture de boucle *réinjectables* dans la carte, Insight expose seulement les poses déjà corrigées (sauts de relocalisation possibles, non observés en SP-0).
- Implication pour la qualité des poses récupérées par mote : les systèmes « poses externes → 3DGS » du survey atteignent 0,26–0,9 cm d'ATE (MonoGS++, Table II/IV) avec des trackers purement visuels ; une pose VI-SLAM casque (SP-0 : ≈ 4–6 mm / 0,3–0,5° contre COLMAP) est du même ordre que l'ATE des meilleurs systèmes découplés du survey, mais **le survey ne contient aucune donnée reliant l'erreur de pose à la qualité du 3DGS** (pas d'ablation « poses bruitées »), donc H-01 n'est ni confirmée ni infirmée ici — seulement rendue plausible par analogie.
- Point de vigilance repris du survey : utiliser des poses d'un système fermé comme pseudo-vérité terrain pose le même problème que ScanNet (poses BundleFusion « may not be as accurate », `page:5`, `page:20`) ; l'ATE est **translation seule** (`page:6`), alors que pour un 3DGS l'erreur angulaire compte au moins autant.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Carte complète du champ « SLAM à champ de radiance » (80 systèmes, Table I `page:7`) ; vocabulaire frame-to-frame vs frame-to-model, couplé vs découplé (`page:2`, `page:3`) ; place des trackers classiques (ORB-SLAM3, DROID, DPVO) comme fournisseurs de poses pour une carte NeRF/3DGS ; rien sur Insight lui-même |
| 2. Poses pour 3DGS (piste mote, H-01) | Preuve empirique que le découplage « tracker classique → carte 3DGS » bat le tracking par rendu différentiable : MonoGS 4,4 → MonoGS++ 0,9 cm sur TUM mono (`page:15`) ; 3DGS couplés « struggle with noise » (`page:17`) ; Photo-SLAM (ORB-SLAM3) et MonoGS++ (DPVO) rendent mieux que tous les NeRF-SLAM RGB (`page:17`). Manque : aucune mesure de la sensibilité du 3DGS à l'erreur de pose |
| 3. Temps réel et contraintes embarquées | Table XI : SplaTAM 0,14 FPS / 18,5 GB sur RTX 3090 (`page:19`) ; « current 3DGS-style methods still struggle to efficiently handle simultaneous tracking and mapping processing » (`page:20`) ; coût 3DGS-SLAM « significantly higher than NeRF-based methods … especially on resource-constrained devices » (`page:20`). Justifie de ne **pas** faire de tracking 3DGS sur le casque et de n'y garder que le VI-SLAM natif |
| 4. Évaluation | Protocoles standard : ATE RMSE translation alignée (`page:6`), TUM (mocap 100 Hz), Replica synthétique, ScanNet (GT BundleFusion) ; PSNR sur vues d'entraînement contesté (`page:17`) ; appel à des benchmarks en ligne avec protocole de vues nouvelles (`page:20`). Fournit les baselines chiffrées (Tables II–VI, XI) auxquelles comparer mote |

## Pour (vis-à-vis de notre problématique)
- Seule synthèse qui aligne sur un même protocole les ATE/PSNR de MonoGS, SplaTAM, GS-SLAM, GS-ICP, CG-SLAM, HF-GS, MonoGS++, MGS-SLAM, Photo-SLAM, avec les baselines ORB-SLAM2 / DROID-SLAM (`page:15`–`page:17`).
- Conclusion explicite et répétée en faveur du schéma mote (tracker découplé + BA/LC → carte) : `page:15`, `page:16`, `page:20`.
- Tableau I donne pour chaque système les modalités (RGB-D / mono / stéréo / IMU), le tracker externe et le lien code : outil de sélection de baselines reproductibles (`page:7`).
- Mesures de mémoire/FPS faites par les auteurs sur un GPU unique (RTX 3090), donc comparables entre elles (`page:19`).
- Discussion lucide des limites 3DGS pour le SLAM : dépendance à l'initialisation, croissance incontrôlée des Gaussiennes dans les zones non vues, mémoire, pas de maillage direct, coût calcul (`page:19`, `page:20`).

## Contre / limites
- **Chiffres compilés, non reproduits** (sauf Table XI) : protocoles légèrement différents d'un papier à l'autre, reconnus par les auteurs (« Evaluation Inconsistencies », `page:20`).
- Table XI ne contient **qu'un seul 3DGS (SplaTAM)** ; MonoGS, Photo-SLAM, GS-ICP, RTG-SLAM (qui revendiquent le temps réel) ne sont pas mesurés ; pas de FPS tracking vs mapping séparés, pas de latence.
- **SSIM/LPIPS absents** des tableaux ; PSNR mesuré sur les vues d'entraînement (`page:17`).
- ATE = translation seule, pas d'erreur de rotation ni de dérive relative (RPE) (`page:6`).
- Aucune analyse « qualité des poses d'entrée → qualité de la carte » : la question centrale de H-01 n'est pas traitée.
- Rien sur les casques, le multi-caméra, l'IMU haute fréquence, l'embarqué (CPU/DSP) ; les trackers externes étudiés sont tous logiciels sur PC.
- Table IV et VI aplaties dans le markdown MinerU (lignes réassociées par recalcul des moyennes, cf. ci-dessus) ; colonne « tracker » de la Table IV illisible, remplacée par la Table I ; page 3 (théorie NeRF) corrompue par la mise en page deux colonnes, sans perte pour la fiche.
- Date butoir ECCV/IROS 2024 : manquent les 3DGS-SLAM 2025 (y compris ceux à poses de casque).

## Idées à creuser pour mote
- *Positionnement* : décrire mote dans les termes du survey — « découplé, frame-to-frame, tracker externe = VI-SLAM du casque, carte 3DGS, BA global et LC délégués au casque » — et le comparer directement à Photo-SLAM (ORB-SLAM3 → 3DGS) et MonoGS++ (DPVO → 3DGS), ses deux plus proches voisins (`page:9`, `page:13`).
- *Expérience manquante au survey, à faire en SP-1* : rejouer une séquence TUM/Replica ou une capture Quest avec les poses casque **bruitées artificiellement** (σ translation 2–20 mm, σ rotation 0,1–1°) et mesurer PSNR/LPIPS du 3DGS avec et sans raffinement de poses — c'est la courbe « erreur de pose → qualité 3DGS » qui tranche H-01.
- *Baseline chiffrée* : viser sur TUM fr1/desk-type un ATE ≤ 1,0 cm (ORB-SLAM2 / NGEL-SLAM, `page:15`) pour les poses Quest réalignées, et un PSNR ≥ 33 dB (Photo-SLAM RGB, `page:17`) pour la carte.
- *Mémoire / débit* : SplaTAM à 18,5 GB et 0,14 FPS (`page:19`) montre que l'optimisation conjointe est le goulot ; mote supprime le tracking côté PC, donc la quasi-totalité du budget GPU va au mapping — mesurer le FPS de mapping seul, que le survey ne donne pas.
- *Évaluation* : adopter l'ATE RMSE aligné (`page:6`) **plus** une erreur angulaire, et évaluer le rendu sur des vues tenues hors entraînement (recommandation `page:17`, `page:20`) ; utiliser EuRoC/ETH3D-SLAM (VI, vérité terrain mm) cités `page:6` pour qualifier un VI-SLAM si l'on veut comparer Insight à ORB-SLAM3/VINS sur données publiques.
- *Fermeture de boucle* : le survey explique pourquoi les cartes à grilles ne survivent pas à une correction de poses (`page:20`) ; avec un 3DGS explicite, une correction de boucle reçue du casque peut être appliquée par déformation des centres de Gaussiennes (sous-cartes à la Loopy-SLAM, `page:11`) — piste pour les captures longues.

## Citations clés
> « One notable observation, however, is that decoupled methods using external trackers such as ORB3 and DROID, along with advanced strategies such as Global BA and LC, emerge as top performers. » (`doc:2751f35/tier:standard/page:15`)

> « Additionally, promising results are evident for methods utilizing 3D Gaussian Splatting, with the best results among all achieved with CG-SLAM, HF-GS SLAM and GS-ICP SLAM. This suggests that these approaches struggle with noise and work best in simpler situations, showing less reliability in complex conditions. » (`doc:2751f35/tier:standard/page:16`, `page:17`)

> « We can notice how SplaTAM, despite its high efficiency at rendering images, is however much slower at processing both tracking and mapping simultaneously. » (`doc:2751f35/tier:standard/page:18`)

> « Finally, despite their advantages in fast image rendering, current 3DGS-style methods still struggle to efficiently handle simultaneous tracking and mapping processing, preventing their effective use in real-time applications. » (`doc:2751f35/tier:standard/page:20`)

> « Overall, decoupled methods, which separate the mapping and tracking processes, tend to achieve better tracking performance compared to coupled approaches. By allowing the tracking module to focus solely on camera pose estimation without the added complexity of simultaneously updating the map representation, decoupled methods can achieve more accurate and robust tracking. » (`doc:2751f35/tier:standard/page:20`)

## Liens
- Papiers liés :
  - [Photo-SLAM](../huang2024_photo-slam/fiche.md) — le système « ORB-SLAM3 → 3DGS » le plus proche de mote ; PSNR RGB 33,30 (`page:17`), absent des tableaux d'ATE.
  - [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) et [ORB-SLAM](../murartal2015_orb-slam/fiche.md) — trackers externes de Photo-SLAM, NGEL-SLAM, vMAP, DN-SLAM ; ORB-SLAM2 = baseline 1,0 cm sur TUM (`page:15`).
  - [DROID-SLAM](../teed2021_droid-slam/fiche.md) — tracker de GO-SLAM, MoD-SLAM, Q-SLAM, Hi-SLAM, NeRF-SLAM, DG-SLAM ; meilleurs ATE ScanNet (`page:15`).
  - [DPVO](../teed2023_dpvo/fiche.md) — tracker de MonoGS++, MGS-SLAM, NeRF-VO ; MonoGS++ = meilleur RGB sur TUM et Replica (`page:15`, `page:16`).
  - [Kimera](../rosinol2020_kimera/fiche.md) — NeRF-SLAM (Rosinol, Leonard, Carlone, `page:25`) en est le prolongement : DROID + Instant-NGP, 20 FPS sur RTX 3090 (`page:19`).
  - [VINS-Mono](../qin2018_vins-mono/fiche.md), [VINS-Fusion](../qin2019_vins-fusion/fiche.md), [Basalt](../usenko2020_basalt/fiche.md), [SLAM multi-caméras](../kuo2020_multicam-slam/fiche.md), [revue VIN](../huang2019_vin-review/fiche.md) — ce que le survey ne couvre pas : la couche VI-SLAM qui, dans mote, remplace ORB-SLAM3/DROID.
  - [Project Aria](../engel2023_project-aria/fiche.md) et [dossier Oculus Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) — le « tracker externe » réel de mote.
  - [3DGS](../kerbl2023_3dgs/fiche.md) — représentation de base (éq. 8–11, `page:4`, `page:5`) ; [survey 3DGS de Chen & Wang](../chen2024_3dgs-survey/fiche.md) — cité [69] comme référence 3DGS (`page:5`).
  - [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md) — réponse au problème de croissance incontrôlée des Gaussiennes et de mémoire soulevé `page:19`, `page:20`.
  - [VRSplat](../tu2025_vrsplat/fiche.md) — côté rendu casque ; le survey ne traite pas la XR.
  - [Précision de positionnement VR](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — mesure de la qualité des poses casque, donnée absente du survey.
