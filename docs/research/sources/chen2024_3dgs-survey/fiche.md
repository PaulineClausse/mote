---
citekey: chen2024_3dgs-survey
mineru_doc: c459485
type: survey
statut: fiche complète
tags: [survey, 3DGS, principes, rasterisation-tuiles, compression, LOD, anti-aliasing, popping, ray-tracing, benchmark, SLAM]
---

# A Survey on 3D Gaussian Splatting

**Référence :** Guikun Chen, Wenguan Wang (2024 ; version v9 du 9 avril 2026). *A Survey on 3D Gaussian Splatting*. Manuscrit soumis à ACM (41 pages, revue exacte non indiquée dans le texte), Zhejiang University. arXiv:2401.03890 — https://arxiv.org/abs/2401.03890
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Premier survey général de la 3DGS, avec principes du rendu et de l'optimisation, taxonomie des extensions (entrées éparses, mémoire, photoréalisme, optimisation, attributs, hybrides, nouveaux rendus, noyaux), applications et tableaux de performance compilés. La XR n'y est qu'une motivation.

## Problème traité
- NeRF est coûteux en calcul et difficile à éditer. La 3DGS remplace le ray-marching par une rastérisation de Gaussiennes explicites, pertinente pour les applications sensibles à la latence comme la VR (`doc:c459485/tier:standard/page:2`).
- Le survey structure la période fondatrice (2023–2024) et maintient deux dépôts GitHub (Awesome3DGS, 3DGS-Benchmarks) (`doc:c459485/tier:standard/page:2`, `page:3`).

## Méthode / contributions
- **Principes (§3)**, très utiles pour l'étape 2/3 (`doc:c459485/tier:standard/page:5`–`page:8`) :
  - attributs μ, α, Σ, SH ; culling du frustum ; projection Σ' = J W Σ Wᵀ Jᵀ, avec J le jacobien de l'approximation affine de la projection (EWA) ;
  - α-blending trié par profondeur ; tuiles 16×16 ; duplication des Gaussiennes par tuile ; clé de tri = ID de tuile (bits hauts) + profondeur (bits bas) ; tuile = bloc CUDA, pixel = thread, mémoire partagée ;
  - Σ = R S Sᵀ Rᵀ, via un quaternion et une échelle pour garantir une matrice semi-définie positive ; gradients dérivés à la main ;
  - initialisation SfM ou aléatoire (« good initialization is essential ») ; densification clone/split sur gradient positionnel ; élagage par α ou taille ; remise à zéro périodique de l'opacité.
- **Directions (§4)** : entrées éparses (régularisation contre feed-forward, Table S2) ; **mémoire** (réduire le nombre de Gaussiennes ou compresser leurs attributs) ; photoréalisme (aliasing, réflexions, flou) ; optimisation (régularisation, densification, sans COLMAP) ; attributs sémantiques/langage/4D ; hybrides MLP/grilles ; **nouveaux rendus** (ray tracing, EVER) ; **ingénierie du noyau** (surfels, Beta, convexes, rastérisation bi-échelle sans tri) (`page:8`–`page:13`).
- **Applications (§5)** : robotique/SLAM, scènes dynamiques, génération/édition, avatars, endoscopie, **grandes scènes (LOD)**, physique (`page:13`–`page:19`).
- **Benchmarks (§6)** compilés depuis les papiers : localisation et cartographie sur Replica, dynamique sur D-NeRF, avatars sur ZJU-MoCap, chirurgie sur EndoNeRF (`page:19`–`page:21`, `page:40`–`page:41`).

## Résultats chiffrés
Tous les chiffres sont **compilés** depuis les papiers originaux. Il n'y a **pas** de tableau vitesse/qualité sur Mip-NeRF 360 / T&T pour la synthèse de vues statique : le benchmark « statique » est Replica (SLAM).

| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| FPS | GSSLAM : 769 fps ; NICE-SLAM 0,54 ; Vox-Fusion 2,17 ; Point-SLAM 1,33 | Replica, fps mesurés sur **RTX 4090**, résolution non précisée, mono (Table S5, `page:40`) |
| FPS | EndoGaussian : 195,09 fps ; EndoNeRF / EndoSurf : 0,04 fps | EndoNeRF, **RTX 4090** (Table S8, `page:41`) |
| Qualité (PSNR / SSIM / LPIPS) | Replica : Gaussian-SLAM 38,90 / 0,99 / 0,07 ; GSSLAM 37,50 / 0,96 / 0,07 ; SplaTAM 34,11 / 0,97 / 0,10 | Table S5 (`page:40`) |
| Qualité (PSNR / SSIM / LPIPS) | D-NeRF : D-3DGS 39,51 / 0,99 / 0,01 ; 3DGS statique 23,19 / 0,93 / 0,08 | Table S6 (`page:40`) |
| Qualité | ZJU-MoCap : GART 32,22 dB (+1,21 dB face à Instant-NVR) | Table S7 (`page:40`, `page:21`) |
| Temps d'entraînement / préparation | non rapporté en valeurs ; GSSLAM est « environ 578 fois plus rapide » que Point-SLAM à précision comparable | `page:20` |
| Mémoire / taille du modèle | Compression typique : facteurs 10–20× (`page:9/block:8`). Une scène de 2,7 km² demande plus de 20 M de Gaussiennes, à la limite d'une A100 40 GB (`page:18/block:3`). EndoGaussian : 2 GB contre 19 GB pour EndoNeRF (`page:41`) | — |
| Latence | non rapporté | — |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Carte générale et bibliographie de 350 références. Table S3 : datasets de référence, dont Tanks&Temples (14 scènes), Deep Blending (19), Mip-NeRF 360 (9) (`page:39`). Rien sur l'environnement matériel XR. |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | **Fort.** Formulation claire de Σ = RSSᵀRᵀ, Σ' = JWΣWᵀJᵀ, de la densification et de l'élagage (`page:6`–`page:8`). Pistes sans COLMAP (`page:11`) et feed-forward (`page:21`) si l'on veut réduire le coût d'entraînement. |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | **Moyen-fort.** Pipeline tuilé détaillé (`page:7`). Explique que le tri par centres provoque des artefacts temporels quand la caméra bouge, et renvoie à l'OIT pondérée (sans tri) (`page:12/block:5`). LOD pour grandes scènes : n'envoyer que les Gaussiennes essentielles, Octree-GS, hiérarchie (`page:18/block:4`). |
| 4. Évaluation (fps, latence, qualité, coût) | Faible-moyen. Métriques PSNR/SSIM/LPIPS standard. Avertit que PSNR, VRAM et stockage varient fortement selon l'implémentation et les hyperparamètres (`page:19`). |

## Pour (vis-à-vis de notre problématique)
- Meilleure référence pédagogique pour rédiger la partie « principes » (étapes 2 et 3) du rapport : équations, tuiles, clé de tri, mémoire partagée.
- Section mémoire (`page:9/block:7`, `page:9/block:8`) : les deux familles de compression (réduire N ou compresser les attributs) et un verrou explicite, **le déploiement sur appareils edge** avec un budget mémoire serré.
- Section LOD (`page:18/block:4`) : cadre direct pour P3 (budget de Gaussiennes).
- Mention explicite des limites du tri par centres (popping), qui relie StopThePop / EVER à notre problème VR (rotations de tête).

## Contre / limites
- XR quasi absente. Seules des mentions générales de VR/AR (intro `page:2`, priors physiques `page:22`) ; aucune section stéréo, fovéal, casque ou latence. [VR-GS](../jiang2024_vr-gs/fiche.md) n'est cité que comme référence générale.
- Pas de benchmark vitesse/qualité sur Mip-NeRF 360, T&T ou Deep Blending, ni de comparaison mémoire/fps des méthodes compactes : les auteurs renvoient à leur dépôt GitHub (`page:19`).
- Les fps compilés (769 fps GSSLAM, 195 fps EndoGaussian) portent sur des scènes SLAM/endoscopiques sur RTX 4090, en mono, sans résolution indiquée. Ils ne sont pas transposables à 2 × 1080p sur casque.
- La couverture reste « période fondatrice 2023–2024 » malgré la v9 de 2026 (`page:2`).

## Idées à creuser pour une approche novatrice
- *Hypothèse :* la clé de tri tuile+profondeur est calculée **par vue** (`page:7`). En VR, les deux yeux ont des frustums très proches. Mutualiser culling, projection et tri (P2), avec une correction d'ordre locale inspirée de l'OIT pondérée (`page:12/block:5`), n'est **pas traité** par ce survey. P2 reste donc a priori ouverte ici, à vérifier dans VRSplat, StopThePop et les travaux stéréo.
- *Hypothèse :* le LOD « n'envoyer au rastériseur que les Gaussiennes essentielles » (`page:18/block:4`), combiné à la compression (`page:9/block:7`), fournit les briques de **P3**. La nouveauté possible serait de piloter ce budget par un critère QoS/QoE formel ([Kamdjou](../kamdjou2024_xr-dt-iiot/fiche.md)), ce qu'aucune méthode citée ne fait.
- *Hypothèse :* le survey signale le déploiement edge sous budget mémoire comme défi ouvert (`page:9/block:8`). Cela justifie **P4** : charger progressivement les Gaussiennes compressées par ordre d'importance plutôt que streamer de la vidéo. P4 n'est pas réalisée ici.
- *Hypothèse :* les primitives alignées sur la surface (2DGS, surfels) et les couplages maillage/Gaussiennes (GaMeS, GaussianMesh ; `page:16`) sont des briques pour **P5** : statique en 3DGS, dynamique en maillage avec des occlusions cohérentes.
- *Hypothèse :* la rastérisation bi-échelle « standard + splatting sans tri » [294] (`page:13`) pourrait fournir la partie lointaine peu coûteuse d'un rendu partagé (**P1**).

## Citations clés
> « the assumptions that Gaussians do not overlap and can be sorted accurately using only centers are often violated in practice, leading to temporal artifacts when camera movement changes sorting order » (`doc:c459485/tier:standard/page:12/block:5`)

> « One practical challenge is deploying 3D GS on edge devices, where tight memory budgets can limit how much of a large scene can be stored or loaded locally. » (`doc:c459485/tier:standard/page:9/block:8`)

> « Current implementations involve feeding only the essential Gaussians to the rasterizer [147], or designing explicit LoD structures like the Octree [209] and hierarchy [112]. » (`doc:c459485/tier:standard/page:18/block:4`)

## Papiers cités à ajouter à la base
Références telles que données dans la bibliographie du survey, hors dossiers existants :
1. **Rachel Albert, Anjul Patney, David Luebke, Joohwan Kim (2017).** *Latency requirements for foveated rendering in virtual reality.* ACM Trans. Applied Perception 14(4) [4]. Contrainte de latence pour le fovéal et le rendu partagé (P1).
2. **Anjul Patney et al. (2016).** *Towards foveated rendering for gaze-tracked virtual reality.* ACM TOG 35(6) [192]. Référence perceptive du fovéal.
3. **Kerui Ren, Lihan Jiang, Tao Lu, Mulin Yu, Linning Xu, Zhangkai Ni, Bo Dai (2024).** *Octree-gs: Towards consistent real-time rendering with lod-structured 3d gaussians.* arXiv:2403.17898 [209]. LOD (P3).
4. **Panagiotis Papantonakis, Georgios Kopanas, Bernhard Kerbl, Alexandre Lanvin, George Drettakis (2024).** *Reducing the Memory Footprint of 3D Gaussian Splatting.* I3D 2024 [188]. Compact, orienté web/mobile.
5. **Simon Niedermayr, Josef Stumpfegger, Rüdiger Westermann (2024).** *Compressed 3d gaussian splatting for accelerated novel view synthesis.* CVPR 2024 [183].
6. **Yihang Chen, Qianyi Wu, Jianfei Cai, Mehrtash Harandi, Weiyao Lin (2024).** *HAC: Hash-grid Assisted Context for 3D Gaussian Splatting Compression.* ECCV 2024 [31].
7. **Guangchi Fang, Bing Wang (2024).** *Mini-Splatting: Representing Scenes with a Constrained Number of Gaussians.* arXiv:2403.14166 [49]. Budget de Gaussiennes, utilisé dans le pipeline VR de Tu et al.
8. **Alexander Mai et al. (2024).** *Ever: Exact volumetric ellipsoid rendering for real-time view synthesis.* arXiv:2410.01804 [166]. Supprime le popping.
9. **Keyang Ye, Tianjia Shao, Kun Zhou (2025).** *When gaussian meets surfel: Ultra-fast high-fidelity radiance field rendering.* ACM TOG 44(4) [294]. Rastérisation + splatting sans tri.
10. **Morgan McGuire, Louis Bavoil (2013).** *Weighted blended order-independent transparency.* JCGT 2(4) [169]. Base d'un compositing sans tri (P2).
11. **Milena T. Bagdasarian et al. (2025).** *3dgs.zip: A survey on 3d gaussian splatting compression methods.* Computer Graphics Forum 44 [10]. Survey compression avec tableaux comparatifs.

## Liens
- Papiers liés : [Kerbl 2023](../kerbl2023_3dgs/fiche.md) [111] · [Hierarchical 3DGS](../kerbl2024_hierarchical-3dgs/fiche.md) [112] · [Mip-Splatting](../yu2023_mip-splatting/fiche.md) [303] · [2DGS](../huang2024_2dgs/fiche.md) [85] · [StopThePop](../radl2024_stopthepop/fiche.md) [205] · [LightGaussian](../fan2023_lightgaussian/fiche.md) [48] · [Compact 3DGS (Lee et al.)](../lee2023_compact3d/fiche.md) [124] · [VR-GS](../jiang2024_vr-gs/fiche.md) [103] · [Li 2025](../li2025_rf-xr-survey/fiche.md) et [Qiu 2024](../qiu2024_3dgs-xr-survey/fiche.md) (surveys orientés XR) · [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) (cadre QoS/QoE pour P3).
