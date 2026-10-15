---
citekey: huang2024_2dgs
mineru_doc: f3091d6
type: conférence
statut: fiche complète
tags: [2dgs, surfels, gaussian-splatting, geometrie, reconstruction-de-surface, maillage, tsdf, normales, profondeur, occlusion-ar, rasterisation-par-tuiles, piste-P5]
---

# 2D Gaussian Splatting for Geometrically Accurate Radiance Fields

**Référence :** Huang, B., Yu, Z., Chen, A., Geiger, A., Gao, S. (2024). *2D Gaussian Splatting for Geometrically Accurate Radiance Fields*. SIGGRAPH Conference Papers '24, Denver, CO, USA, ACM. DOI [10.1145/3641519.3657428](https://doi.org/10.1145/3641519.3657428) (p. 1). arXiv:2403.17888 (v3, 22 fév. 2025) : https://arxiv.org/abs/2403.17888
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Projet :** https://surfsplatting.github.io (p. 1)

## En une phrase

On « aplatit » les Gaussiennes 3D en **disques gaussiens 2D orientés** (surfels) dans l'espace 3D. Leur rendu par **intersection rayon-splat exacte en perspective**, intégrée dans le rasteriseur par tuiles de 3DGS, et deux régularisations (distorsion de profondeur, cohérence des normales) donnent une **géométrie cohérente entre vues** et des **maillages** par fusion TSDF. La qualité d'image reste légèrement inférieure à 3DGS (p. 1, 5, 7).

## Problème traité

- Les Gaussiennes 3D volumétriques sont mal adaptées aux surfaces minces. 3DGS ne modélise pas de normales. Sa rasterisation n'est pas cohérente d'une vue à l'autre : le plan d'intersection évalué change avec le point de vue (Fig. 2). L'approximation affine de la projection n'est exacte qu'au centre de la Gaussienne. Résultat : profondeurs bruitées et surfaces reconstruites médiocres (p. 3, Fig. 5 et 7).
- Les méthodes de surface implicites (SDF) donnent de bonnes surfaces, mais coûtent très cher : Neuralangelo demande 128 heures-GPU pour une scène T&T (p. 3).
- Pour la XR, c'est le verrou « **géométrie exploitable** » : occlusion réel/virtuel en AR/MR, collisions, physique, maillage pour un moteur de jeu.

## Méthode / contributions

**Primitive (p. 4, éq. 4-6, Fig. 3).**
- Un disque se définit par son centre p_k, deux vecteurs tangents t_u et t_v, et deux échelles (s_u, s_v). La **normale est explicite** : t_w = t_u × t_v. On a R = [t_u, t_v, t_w] et S diagonale à dernier terme nul (covariance de rang 2).
- Le point local s'écrit P(u,v) = p_k + s_u t_u u + s_v t_v v = H(u,v,1,1)ᵀ, et on évalue 𝒢(u) = exp(−(u²+v²)/2).
- Comme dans 3DGS, chaque disque porte une opacité α et une couleur SH.
- L'initialisation part du **nuage SfM épars** et de la seule supervision photométrique. Contrairement aux surfels antérieurs, il ne faut ni nuage dense ni normales vérité terrain (p. 4).

**Splatting exact en perspective (p. 4-5, éq. 7-11).**
- On ne projette pas la Gaussienne de façon affine (EWA). Pour chaque pixel, on calcule l'**intersection explicite rayon-splat**. Le rayon est l'intersection des plans homogènes h_x = (−1,0,0,x) et h_y = (0,−1,0,y), transformés dans l'espace uv du disque par (WH)ᵀ, **sans inversion de matrice**. Une formule fermée donne ensuite (u,v) (éq. 10), puis la profondeur z (éq. 7).
- **Cas dégénérés** (disque vu par la tranche) : un filtre passe-bas en espace objet borne 𝒢̂(x) = max{𝒢(u(x)), 𝒢((x−c)/σ)}, avec σ = √2/2 (p. 5, éq. 11).
- **Rasterisation** : « a similar rasterization process as in 3DGS » (p. 5). On calcule une boîte englobante en espace écran, on trie **par la profondeur du centre** et on répartit **en tuiles**, puis on fait un α-blending front-to-back avec arrêt à saturation (éq. 12). **Le pipeline par tuiles est donc conservé.** Seule change l'évaluation par paire pixel-splat, qui devient une intersection rayon-plan au lieu d'une conique 2D.

**Régularisations (p. 5, éq. 13-16).**
- **Distorsion de profondeur** L_d = Σ ω_i ω_j |z_i − z_j|, inspirée de Mip-NeRF360, calculée sur la profondeur d'intersection **différentiable**. Elle concentre les splats le long du rayon. Elle est calculée en une seule passe avant grâce à des sommes cumulées, en espace NDC (near 0,2, far 1000) (annexe A, p. 9).
- **Cohérence des normales** L_n = Σ ω_i (1 − n_iᵀ N). On aligne la normale des splats sur la normale N obtenue par différences finies de la profondeur au point médian, là où l'opacité cumulée atteint 0,5 (p. 5, éq. 14-15).
- Perte totale : L = L_c + α L_d + β L_n, avec α = 1000 pour une scène bornée, 100 pour une scène non bornée, et β = 0,05 (p. 5).

**Implémentation (p. 5).** Kernels CUDA construits sur le code de 3DGS. Le renderer produit aussi des cartes de profondeur, de normales et de distorsion. La densification adaptative de 3DGS est conservée : gradient du centre 3D projeté, seuil 0,0002, élagage des disques d'opacité < 0,05 toutes les 3000 itérations. **Une seule GPU RTX 3090** (le texte écrit « GTX RTX3090 »).

**Extraction de maillage (p. 5).** On rend les cartes de profondeur des vues d'entraînement (**profondeur médiane**), on les fusionne par **TSDF** (Open3D, voxel de 0,004, troncature de 0,02), puis on extrait le maillage. C'est un post-traitement **hors ligne**.

## Résultats chiffrés

Matériel : **RTX 3090** (GPU de bureau) pour toutes les expériences (p. 5). Sur DTU, les images sont sous-échantillonnées de 1600×1200 à **800×600** (p. 6). La résolution utilisée pour Mip-NeRF360 et T&T n'est pas précisée.

| Métrique | Valeur | Conditions |
|---|---|---|
| **FPS de rendu** | **non rapporté**. Le papier affirme seulement « real-time rendering » (p. 1, 2), sans chiffre, sans comparaison au 3DGS et sans résolution | — |
| Chamfer DTU (↓) | 2DGS-30k **0,80** ; 2DGS-15k 0,83 ; 3DGS 1,96 ; SuGaR 1,33 ; NeuS 0,84 ; VolSDF 0,86 | Tab. 1 et 3, p. 6 |
| Temps de reconstruction DTU | 2DGS **10,9 min** (30k) / 5,5 min (15k) ; 3DGS 11,2 min ; SuGaR environ 1 h ; SDF > 12 h | RTX 3090, Tab. 1 et 3, p. 6 |
| Stockage DTU | 2DGS **52 MB** ; 3DGS 113 MB ; SuGaR 1 247 MB | Tab. 3, p. 6 |
| PSNR DTU (vues d'entraînement) | 2DGS 34,52 (30k) ; 3DGS 35,76 ; SuGaR 34,57 | Tab. 3, p. 6 |
| F1 Tanks&Temples (↑) | 2DGS **0,32** ; 3DGS 0,09 ; SuGaR 0,19 ; Neuralangelo 0,50 (> 24 h) ; NeuS 0,38 | Tab. 2, p. 6 |
| Temps T&T | 2DGS 15,5 min ; 3DGS 14,3 min | Tab. 2, p. 6 |
| NVS Mip-NeRF360, extérieur (PSNR/SSIM/LPIPS) | 2DGS 24,34 / 0,717 / 0,246 ; 3DGS 24,64 / 0,731 / 0,234 | 30k itérations, Tab. 4, p. 7 |
| NVS Mip-NeRF360, intérieur | 2DGS 30,40 / 0,916 / 0,195 ; 3DGS 30,41 / 0,920 / 0,189 | Tab. 4, p. 7 |
| NVS Mip-NeRF360, moyenne sur 9 scènes | 2DGS 27,03 / 0,805 / 0,223 ; 3DGS 27,20 / 0,815 / 0,214 | Tab. 9, p. 10 |
| PSNR NeRF-Synthetic (sans régularisation) | 2DGS 33,07 ; 3DGS 33,32 | Tab. 7, p. 10 |
| PSNR T&T | 2DGS 25,56 ; 3DGS 25,33 | Tab. 8, p. 10 |
| Ablations DTU (Chamfer moyen) | complet 0,83 ; sans cohérence des normales 1,24 ; sans distorsion 0,88 ; profondeur moyenne au lieu de médiane 0,94 ; SPSR au lieu de TSDF 1,07 | 15k itérations, Tab. 5, p. 7 |
| Rasteriseur exact ou affine | 2DGS en approximation affine + TSDF 1,08 ; notre rasteriseur + TSDF (moyenne) 0,88 ; (médiane) 0,80 | Tab. 6, p. 10 |
| Nombre de Gaussiennes, VRAM, latence | non rapportés | — |

## Pertinence pour notre sujet

| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | C'est la référence « surfels gaussiens » face à SuGaR et NeuSG (p. 3). Il n'y a aucun volet XR. |
| 2. Gaussiennes depuis SfM, covariance anisotrope | Variante de la covariance : rang 2 (disque) au lieu de 3, normale explicite, même initialisation SfM éparse et même densification que 3DGS (p. 4-5). C'est une alternative directe pour l'étape 2 si la géométrie compte. |
| 3. Rendu rapide, visibilité, casque XR | Le rasteriseur **par tuiles avec tri global** de 3DGS est conservé (p. 5). Le splatting exact en perspective supprime l'erreur affine, ce qui compte pour les grands FOV des casques (hypothèse de notre part). Le rendu fournit **profondeur et normales cohérentes**, utiles pour l'occlusion AR. En revanche, **aucun fps n'est mesuré**. |
| 4. Évaluation | Ajoute des métriques géométriques (Chamfer, F1) à reprendre si l'on vise un jumeau numérique. Il manque fps, latence et VRAM. |

## Pour (vis-à-vis de notre problématique)

- **Géométrie exploitable pour la XR.** Profondeur et normales cohérentes entre vues (Fig. 8), avec un Chamfer DTU divisé par environ 2,5 par rapport à 3DGS (0,80 contre 1,96) et un F1 T&T de 0,32 contre 0,09 (Tab. 1-2). C'est une base crédible pour l'occlusion réel/virtuel en MR et pour des collisions via le maillage TSDF (hypothèse d'usage : non testée dans le papier).
- **Pont naturel vers P5 (hybride).** Une même optimisation produit un rendu splat photoréaliste **et** un maillage. On peut donc envisager splat pour l'apparence et maillage pour la physique et l'interaction.
- **Coût d'entraînement équivalent à 3DGS** : 10,9 contre 11,2 min sur DTU, 15,5 contre 14,3 min sur T&T, sur RTX 3090. C'est environ 100 fois plus rapide que les SDF (p. 7).
- **Modèle plus compact** sur DTU : 52 MB contre 113 MB (Tab. 3).
- **Compatible avec l'architecture de rendu 3DGS** (tuiles, tri, blending). Les optimisations de rasteriseur (tri, culling, stéréo) sont donc a priori transposables.

## Contre / limites

- **Aucun chiffre de vitesse de rendu** : ni fps, ni comparaison au 3DGS, ni résolution. L'affirmation « real-time » n'est pas quantifiée. Pour notre critère ≥ 30 fps en 1080p, c'est **à mesurer nous-mêmes**.
- **Surcoût probable par paire pixel-splat.** Il faut calculer (WH)ᵀh_x et (WH)ᵀh_y, deux divisions et le max du filtre passe-bas, contre une simple évaluation de conique. Hypothèse de notre part, non quantifiée dans le papier.
- **Qualité d'image légèrement inférieure** à 3DGS : −0,17 dB PSNR, −0,010 SSIM et +0,009 LPIPS en moyenne sur Mip-NeRF360 (Tab. 9). Sur DTU, −1,24 dB en vues d'entraînement (Tab. 3). Les régularisations imposent un compromis entre image et géométrie, avec risque de sur-lissage (p. 8).
- **Surfaces semi-transparentes** (verre) mal gérées et **trous dans les zones très lumineuses** (Fig. 12, p. 8 et 13). C'est gênant en milieu industriel (vitres, métal brillant).
- La densification favorise les zones riches en texture plutôt qu'en géométrie (p. 8).
- Le **maillage est hors ligne** (fusion TSDF de toutes les vues d'entraînement). Il n'y a ni maillage dynamique, ni évaluation de la qualité visuelle ou du coût de rendu du maillage lui-même.
- Tri par la profondeur du centre (p. 5), donc le popping de 3DGS demeure probablement (hypothèse ; cf. [StopThePop](../radl2024_stopthepop/fiche.md)).

## Idées à creuser pour une approche novatrice

- **H1 (P5) — Jumeau numérique hybride à géométrie unique.** On entraînerait une scène en 2DGS, on extrairait le maillage TSDF comme proxy de collision et d'occlusion, et on rendrait l'apparence en splats. On mesurerait l'écart splat/maillage à l'endroit où des objets dynamiques (maillages de machines) entrent dans la scène.
- **H2 (MR) — Occlusion par profondeur médiane.** On utiliserait la profondeur médiane 2DGS rendue par œil comme depth buffer pour composer du contenu virtuel ou réel en passthrough. Il faudrait comparer la stabilité temporelle de cette profondeur à celle de la profondeur 3DGS pendant les mouvements de tête. À vérifier : fps et coût du rendu de profondeur.
- **H3 (P2) — Stéréo exacte en perspective.** L'intersection rayon-splat étant exacte par pixel, on pourrait partager le tri et les boîtes englobantes entre les deux yeux et ne recalculer que h_x et h_y par œil. C'est à tester face à la mutualisation stéréo en 3DGS.
- **H4 (P3) — Budget ou LOD sur les disques.** On combinerait 2DGS et un budget de primitives à la [Taming](../mallick2024_taming-3dgs/fiche.md) pour borner la mémoire tout en gardant la géométrie. On mesurerait la dégradation du Chamfer en fonction du budget, puisque les petits budgets pourraient trouer les surfaces.
- **H5 — Benchmark fps 2DGS contre 3DGS** au même nombre de primitives, en 1080p stéréo sur GPU de bureau puis mobile. Cela comblerait le manque principal du papier et servirait directement notre étape 4.

## Citations clés

> « Our key idea is to collapse the 3D volume into a set of 2D oriented planar Gaussian disks. Unlike 3D Gaussians, 2D Gaussians provide view-consistent geometry while modeling surfaces intrinsically. » (`doc:f3091d6/tier:standard/page:1`)

> « We follow a similar rasterization process as in 3DGS [...] 2D Gaussians are sorted based on the depth of their center and organized into tiles based on their bounding boxes. » (`doc:f3091d6/tier:standard/page:5`)

> « our regularization often involves a trade-off between image quality and geometry, and can potentially lead to over-smoothing in certain regions. » (`doc:f3091d6/tier:standard/page:8`)

## Liens

- **Papiers liés :**
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) : base du code et du rasteriseur par tuiles réutilisé ; baseline de toutes les comparaisons.
  - [yu2023_mip-splatting](../yu2023_mip-splatting/fiche.md) : même équipe (Yu, Chen, Geiger), cité pour l'anti-aliasing (p. 2).
  - [radl2024_stopthepop](../radl2024_stopthepop/fiche.md) : tri par pixel, pertinent puisque 2DGS trie encore par le centre.
  - [mallick2024_taming-3dgs](../mallick2024_taming-3dgs/fiche.md) : budget de primitives, combinable (H4).
  - [warsinke2026_gs-mesh-dt-vr](../warsinke2026_gs-mesh-dt-vr/fiche.md), [jiang2024_vr-gs](../jiang2024_vr-gs/fiche.md) : à croiser pour P5 (Gaussiennes et maillage en VR / jumeau numérique).
- **Options du projet :** [../../synthese/options.md](../../synthese/options.md), pistes P5 et P3.
