---
citekey: li2025_rf-xr-survey
mineru_doc: 9b5726e
type: survey
statut: fiche complète
tags: [survey, revue-systematique, PRISMA, XR, NeRF, 3DGS, fovea, remote-rendering, compression, streaming, Unity, benchmark-XR]
---

# Radiance Fields in XR: A Survey on How Radiance Fields are Envisioned and Addressed for XR Research

**Référence :** Ke Li, Mana Masuda, Susanne Schmidt, Shohei Mori (2025). *Radiance Fields in XR: A Survey on How Radiance Fields are Envisioned and Addressed for XR Research*. Manuscrit au gabarit IEEE TVCG (« © 2025 IEEE »), venue finale non indiquée dans le texte. arXiv:2508.04326v2 — https://arxiv.org/abs/2508.04326
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Revue systématique (PRISMA) qui mesure l'écart entre les papiers NeRF/3DGS qui « envisagent » la XR et ceux qui l'« adressent » réellement (benchmark sur casque ou étude utilisateur), et qui recense matériel, fps et résolutions des systèmes XR existants.

## Problème traité
- Des centaines de papiers RF citent la XR comme motivation, mais très peu l'évaluent en conditions XR réelles. À CVPR 2024, 203 papiers RF, dont 68 mentionnent la XR. À IEEE VR 2024 + ISMAR 2024, seulement 11 contributions RF, dont 5 traitent réellement une question XR (`doc:9b5726e/tier:standard/page:1`).
- Trois questions : RQ1, comment la RF est envisagée pour la XR ; RQ2, ce qui est déjà implémenté et évalué en XR ; RQ3, les verrous restants (`doc:9b5726e/tier:standard/page:2`).

## Méthode / contributions
- **Corpus** : ACM DL + IEEE Xplore (recherche du 26/02/2025), plus IEEE VR 2025. Après dédoublonnage : 1 305 papiers « RF-Mentioned », filtrés par mots-clés XR puis à la main. Au final, **365 XR-Mentioned**, dont **66 XR-Addressed** (24 « XR-Study », 42 « XR-Showcase ») et 299 « XR-Envisioned » (`doc:9b5726e/tier:standard/page:2`, `page:3`).
- **Taxonomie en 9 thèmes** (Fig. 2) : optimisation, capture dynamique, recalage spatial, génération, édition, multimodal, benchmarking, rendu centré utilisateur, expériences interactives (`doc:9b5726e/tier:standard/page:3`).
- **Analyse des tendances** : les communautés CV/CG/MM *envisagent*, les communautés XR/HCI *implémentent*. Le thème « Optimization Techniques » compte 94 papiers envisagés mais seulement 8 adressés (`doc:9b5726e/tier:standard/page:4`, `page:8/block:12`). Code ouvert : 34,8 % des XR-Addressed contre 62,5 % des XR-Envisioned (`page:4`).
- **Matériel supplémentaire** : tableau matériel/fps/résolution/afficheur/moteur des 20 systèmes « Interactive Experiences » (Table S1), et comparaison maillage / 3DGS / NeRF sur tout le pipeline XR (Table S2) (`doc:9b5726e/tier:standard/page:13`).

## Résultats chiffrés
Le survey ne mesure rien lui-même. Les chiffres ci-dessous sont **rapportés** depuis les papiers cités.

| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| FPS | NeRF téléprésence VR (Tran et al.) : 30 fps **stéréo** à 512×512 | 2 × RTX 6000, un GPU par œil (`page:5/block:4`) |
| FPS | Tele-Aloha (3DGS) : 30 fps à 2048×2048 | RTX 4090, écran autostéréoscopique (`page:5/block:4`) |
| FPS | Patient holoporté (3DGS, [cao2025](../cao2025_rt-fvhp/fiche.md)) : 400 fps en 1080p | RTX 6000, HoloLens 2 + PC, shader 3DGS custom sous Unity (`page:5/block:4`, `page:13`) |
| FPS | Téléopération robot : 151 fps (3DGS) contre 0,9 fps (NeRF) à 1024×1024 | RTX 4090, casque VR/AR, streaming TCP/ROS (`page:13`) |
| FPS | Reality Fusion : 30–35 fps à 1536×1440 **par œil**, 727 019 Gaussiennes | RTX 3090, casque VR, plugin CUDA 3DGS natif (`page:13`) |
| FPS | Multi-layer 3DGS (anatomie) : > 100 fps à 2064×2208 **par œil** | RTX 4090, casque VR, UnityGaussianSplatting (`page:13`) |
| FPS | [VR-GS](../jiang2024_vr-gs/fiche.md) : 30–120 fps selon le nombre de sommets/Gaussiennes | RTX 4090, casque VR, plugin CUDA pour Unity (`page:13`) |
| FPS | NeARportation (NeRF déporté) : 35–40 fps en full HD stéréo | client-serveur bidirectionnel, afficheur AR (`page:6/block:10`) |
| FPS | VR-NeRF : double 2K HDR à 36 Hz | multi-GPU (`page:6/block:10`) |
| FPS | Re-ReND (NeRF → maillage + light field) : 72 fps | casque VR autonome (`page:8/block:13`) |
| Qualité (PSNR / SSIM / LPIPS) | NeRF et 3DGS : PSNR > 25 et SSIM > 0,8 sur scènes complexes (ordre de grandeur) | générique, sans dataset précisé (`page:13`) |
| Temps d'entraînement / préparation | 3DGS : 2–5 min avec CUDA (idem instant-ngp) | Table S2, sans GPU précisé (`page:13`) |
| Mémoire / taille du modèle | non rapporté (seulement qualitatif : la compression est « un défi majeur » pour la 3DGS) | `page:8/block:14` |
| Latence | Seuil < 20 ms cité comme **objectif** pour le rendu neuronal déporté | d'après NeARportation (`page:6/block:12`, `page:7/block:2`). ⚠️ La source primaire **mesure 100–400 ms** aller-retour : voir [fiche Hiroi 2022](../hiroi2022_nearportation/fiche.md) |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | **Très fort.** Carte des 66 travaux évalués en XR, trois modes d'intégration (NeRF → maillage ; plugin natif CUDA streamé vers le frame buffer ; plugin Unity 3DGS avec tri parallèle), usage fréquent de DLSS/super-résolution (`page:5/block:3`). Existence de ports WebGL/Vulkan et de plugins Unity/Unreal (`page:13`, `page:14`). |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | Faible. Rappelle seulement le pipeline SfM → nuage épars → optimisation (`page:2`, `page:13`). |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | Moyen. Recense le rendu fovéal (FoV-NeRF, VRS-NeRF, VPRF, FoV-GS) et le pipeline VR de Tu et al. (Mini-Splatting + StopThePop + projection optimale + fovéal) (`page:6/block:3`, `page:6/block:10`). Identifie le **tri** comme limite de passage à l'échelle de la 3D/4DGS (`page:9/block:1`). |
| 4. Évaluation (fps, latence, qualité, coût) | **Fort.** Liste des métriques XR : fps, latence (ms), résolution en px ou en PPD, SSIM/PSNR/LPIPS, RTL < 20 ms, tests psychophysiques pour le fovéal, SSQ et SUS (`page:6/block:12`, `page:7/block:1`). Utile pour justifier notre protocole. |

## Pour (vis-à-vis de notre problématique)
- Seul survey qui ne retient que des travaux **évalués sur casque**. La Table S1 donne une base de comparaison matériel/fps/résolution directement réutilisable dans notre état de l'art.
- Montre que la cible ≥ 30 fps en 1080p est déjà atteinte sur PC desktop (400 fps en 1080p, > 100 fps par œil en 2064×2208). La difficulté se situe donc côté **casque autonome/mobile** et côté **stéréo + latence**, ce qui cadre notre contribution.
- Confirme le manque de frameworks de benchmark XR standardisés (Unity/OpenXR) (`page:7/block:2`, `page:7/block:3`). Une contribution méthodologique d'évaluation serait donc bienvenue.

## Contre / limites
- Aucun chiffre mesuré par les auteurs. Les fps proviennent de papiers hétérogènes (mono/stéréo, écran 2D/casque, scènes différentes), donc non comparables entre eux.
- Couverture limitée : ICCV/CVPR seulement pour la CV (pas d'ECCV, pas d'ateliers) (`page:9`). Beaucoup de travaux 3DGS récents (hors ACM/IEEE, arXiv) manquent.
- Le corpus mélange NeRF et 3DGS. La partie propre à la 3DGS temps réel sur casque est mince (le pipeline de Tu et al. n'est qu'un poster).
- Pas de discussion quantitative de l'énergie, de la thermique ni de la mémoire sur casque autonome.

## Idées à creuser pour une approche novatrice
- *Hypothèse :* la Table S1 montre que les systèmes 3DGS en VR sont tous rendus sur un PC (RTX 3090/4090/6000). Un rendu 3DGS **partagé casque/edge** (P1) comblerait un vide réel. La « prédiction de mouvement de tête et du regard pour le rendu neuronal déporté » est citée comme opportunité ouverte (`page:7/block:3`), ce qui soutient P1.
- *Hypothèse :* FoV-NeRF applique un **décalage de disparité** aux images périphériques au lieu de rendre deux images séparées (`page:6/block:3`). Cela **éclaire P2** (mutualisation stéréo), qui n'est vue ici qu'en NeRF et en périphérie. L'appliquer au tri/à la projection 3DGS semble non couvert par ce survey.
- *Hypothèse :* SRBF-Gaussian transmet sélectivement les couleurs utiles au viewport pour le streaming 3DGS, et FSVFG fait du streaming LoD (`page:8/block:14`). **P4 est partiellement réalisée** (streaming 3DGS dépendant du viewport), donc risque pour la nouveauté. Il faudrait lire SRBF-Gaussian avant de positionner P4, par exemple sur le couplage avec un budget QoE (P3).
- *Hypothèse :* le survey recommande des représentations **hybrides maillage + RF** pour la physique, les collisions et l'éclairage dynamique (`page:5/block:9`), et la Table S2 donne l'interactivité 3DGS comme « moyenne ». Cela **appuie P5** sans la réaliser.
- *Hypothèse :* construire un mini-banc de mesure Unity/OpenXR (fps par œil, p95, RTL, PPD) répondrait directement au manque signalé (`page:7/block:3`).

## Citations clés
> « 3D/4DGS still relies on fast sorting operations, which limits scalability as the number of Gaussian increases » (`doc:9b5726e/tier:standard/page:9/block:1`)

> « For remote streaming, it is also crucial to minimize round trip latency (RTL)↓ to below 20 ms » (`doc:9b5726e/tier:standard/page:6/block:12`)

> « Implement head and gaze motion prediction for remote neural rendering frameworks to mitigate perceived latency. » (`doc:9b5726e/tier:standard/page:7/block:3`)

> « 3DGS performance varies with the number of Gaussians and sorting efficiency. » (`doc:9b5726e/tier:standard/page:14`)

## Papiers cités à ajouter à la base
Références telles que données dans la bibliographie du survey, hors dossiers existants :
1. **R. Fan, J. Wu, X. Shi, L. Zhao, Q. Ma, L. Wang (2025).** *Fov-gs: Foveated 3d gaussian splatting for dynamic scenes.* IEEE TVCG 31:2975–2985 [7]. Rendu fovéal 3DGS avec séparation statique/dynamique (P1, P5).
2. **D. Zhang, Z. Liang, Z. Cao, D. Wang, F. Wang (2025).** *SRBF-Gaussian: Streaming-optimized 3D Gaussian splatting.* IEEE VR 2025 [86]. Streaming 3DGS dépendant du viewport, risque direct pour P4.
3. **Y. Hiroi, Y. Itoh, J. Rekimoto (2022).** *NeARportation: A remote real-time neural rendering framework.* ACM VRST 2022 [11]. Rendu déporté stéréo, full HD 35–40 fps, RTL (P1, B5).
4. **C. Kleinbeck, H. Schieber, K. Engel, R. Gutjahr, D. Roth (2025).** *Multi-layer Gaussian splatting for immersive anatomy visualization.* IEEE TVCG [23]. > 100 fps par œil sous Unity, bonne référence B2.
5. **M. G. Kim, S. Jeong, S. Park, J. Han (2024).** *Superpixel-guided sampling for compact 3D Gaussian splatting.* ACM VRST 2024 [22]. Compacité avec benchmarks mémoire sur appareils VR.
6. **N. Deng, Z. He, J. Ye, B. Duinkharjav, P. Chakravarthula, X. Yang, Q. Sun (2021).** *FoV-NeRF: Foveated neural radiance fields for virtual reality.* IEEE TVCG 28 [4]. Décalage de disparité stéréo en périphérie (P2).
7. **H. Kim, I.-K. Lee (2024).** *Is 3DGS useful?: Comparing the effectiveness of recent reconstruction methods in VR.* IEEE ISMAR 2024 [21]. Étude utilisateur 3DGS en VR.
8. **L. Xu et al. (2023).** *VR-NeRF: High-fidelity virtualized walkable spaces.* ACM SIGGRAPH Asia 2023 [80]. Référence haut de gamme (double 2K à 36 Hz, LoD par mip-mapping).
9. **K. Li, R. Bacher, S. Schmidt, W. Leemans, F. Steinicke (2024).** *Reality Fusion: Robust real-time immersive mobile robot teleoperation with volumetric visual data fusion.* IEEE/RSJ IROS 2024 [26]. 3DGS + nuages de points en VR, 1536×1440 par œil.
10. **D. Yin, J. Shi, M. Zhang, Z. Huang, J. Liu, F. Dong (2024).** *FSVFG: Towards immersive full-scene volumetric video streaming with adaptive feature grid.* ACM MM 2024 [82]. Streaming LoD (P4, version NeRF).

Remarque : Tu, Kerbl, De la Torre, *Fast and robust 3D Gaussian splatting for virtual reality* (SIGGRAPH Asia Posters 2024) [70] est le précurseur de [VRSplat](../tu2025_vrsplat/fiche.md), déjà dans la base.

## Liens
- Papiers liés : [Kerbl 2023](../kerbl2023_3dgs/fiche.md) (3DGS de référence [20]) · [VR-GS](../jiang2024_vr-gs/fiche.md) [18] · [Cao 2025](../cao2025_rt-fvhp/fiche.md) (patient holoporté, 400 fps en 1080p) [2] · [VRSplat](../tu2025_vrsplat/fiche.md) (suite de [70]) · [StopThePop](../radl2024_stopthepop/fiche.md) · [VR-Splatting](../franke2024_vr-splatting/fiche.md) et [A3FR](../xin2025_a3fr-foveated/fiche.md) (fovéal 3DGS, à comparer à FoV-GS) · [LapisGS](../shi2024_lapisgs/fiche.md) (streaming, à comparer à SRBF-Gaussian) · [Qiu 2024](../qiu2024_3dgs-xr-survey/fiche.md) (survey XR concurrent, cité [48] pour son étude SUS) · [Chen 2024](../chen2024_3dgs-survey/fiche.md) (survey 3DGS général) · [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) (seuils de latence edge).
