---
citekey: kerbl2024_hierarchical-3dgs
mineru_doc: 18f9541
type: article de revue
statut: fiche complète
tags: [3dgs, lod, hierarchie, grandes-scenes, chunks, streaming-cpu-gpu, temps-reel, budget-rendu, piste-P3, piste-P1, piste-P4]
---

# A Hierarchical 3D Gaussian Representation for Real-Time Rendering of Very Large Datasets

**Référence :** Kerbl, B.\*, Meuleman, A.\*, Kopanas, G., Wimmer, M., Lanvin, A., Drettakis, G. (2024). A Hierarchical 3D Gaussian Representation for Real-Time Rendering of Very Large Datasets. *ACM Transactions on Graphics* 43(4), art. 62 (SIGGRAPH 2024). DOI [10.1145/3658160](https://doi.org/10.1145/3658160) · arXiv [2406.12080](https://arxiv.org/abs/2406.12080) (\* contribution égale, p. 1)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Code / données :** https://repo-sam.inria.fr/fungraph/hierarchical-3d-gaussians/ (p. 1, 8)

## En une phrase

Une hiérarchie (BVH binaire) de Gaussiennes 3D, dont les nœuds internes sont eux-mêmes des Gaussiennes fusionnées puis ré-optimisées, permet un LOD continu piloté par une **granularité cible en pixels** (τ_ε), avec interpolation parent→enfants contre le popping, un entraînement par **chunks** indépendants et un streaming CPU→GPU des nœuds : rendu de scènes urbaines de plusieurs km à 30+ fps (τ = 3 px) ou ≈ 60 fps (τ = 6 px) sur A6000 (p. 1, 5, 11).

## Problème traité

- La mémoire de 3DGS explose avec la taille de la scène : même un GPU haut de gamme ne peut plus rendre, et l'entraînement coûte encore plus (p. 2). Sur leur système, Campus et BigCity ne tournent pas avec le rendu 3DGS d'origine ; Wayve dépasse une RTX 4090 et SmallCity une RTX 4080 (p. 11).
- Les captures de grande taille (casque vélo à 5-6 GoPro, véhicule) sont **beaucoup plus éparses** que les jeux de données radiance field classiques (p. 2, 7).
- Un LOD utilisable en interactif doit réunir trois choses : (i) une structure multi-niveaux, (ii) une politique de sélection de niveau par vue, (iii) des transitions sans artefacts (p. 3).

## Méthode / contributions

**1. Hiérarchie (Sec. 4.1, p. 4-5).**
- Chaque nœud est une Gaussienne 3DGS complète (μ, Σ, SH, opacité), pour garder **la même routine de rasterisation** pour feuilles et nœuds internes.
- Fusion de N enfants par minimisation de la divergence KL (Goldberger & Roweis 2004) : μ = Σ wᵢ μᵢ, Σ = Σ wᵢ (Σᵢ + (μᵢ−μ)(μᵢ−μ)ᵀ) (éq. 3-4). Poids wᵢ′ = oᵢ √|Σ′ᵢ|, calculés en pratique avec la surface de l'ellipsoïde (éq. 8). Les SH sont moyennées avec les mêmes poids (éq. 9).
- L'opacité fusionnée devient une **« falloff »** qui peut dépasser 1, pour imiter la décroissance plus lente d'un groupe de Gaussiennes blendées ; α est borné à 1 au blending (p. 4, Fig. 2).
- Construction : BVH AABB descendante (étendue = 3× la taille stockée), coupe binaire à la médiane sur l'axe le plus long, puis fusion ascendante des feuilles vers la racine (p. 5).

**2. Sélection de la coupe (Sec. 4.2, p. 5).**
- **Granularité ε(n)** = taille projetée à l'écran de la plus grande dimension de la boîte englobant les feuilles du nœud (Fig. 3). La coupe prend les nœuds dont ε(n) < τ_ε alors que leur parent ne vérifie pas le critère. Exemple donné : 1 pixel.
- Comme la boîte d'un parent n'est jamais plus petite que celle d'un enfant, la coupe se calcule en temps linéaire, ou en **temps constant par nœud** en parallèle. Soit tous les enfants, soit le parent sont choisis.
- C'est donc un critère **en pixels écran**, et non en distance (Fig. 6, p. 6). Il dépend de la résolution et du champ de vision (déduction de notre part).

**3. Transition entre niveaux, contre le popping (p. 5-6).**
- Poids d'interpolation t_n = (τ_ε − ε(n)) / (ε(p) − ε(n)) (éq. 10). Position, couleur et SH sont interpolées linéairement ; échelle et rotation séparément (lerp, pas slerp).
- **Appariement d'orientation** : on réinterprète les axes de chaque enfant pour minimiser sa rotation relative au parent, par recherche exhaustive, afin d'éviter des rotations parasites pendant l'interpolation (Fig. 4).
- Opacité : au début de la transition, les K enfants ont α′ = 1 − (1 − α_p)^(1/K), de sorte que leur blending égale exactement le parent (éq. 11-12). On interpole ensuite α(t) = t·αᵢ + (1−t)·α′ (éq. 13).
- Ablation : sans interpolation (ni à l'entraînement ni à l'évaluation), le PSNR sur un chunk Wayve tombe à 25,21 / 24,73 / 23,44 dB pour τ₁/τ₂/τ₃, contre 25,25 / 25,03 / 24,49 avec (p. 12 ; Tab. 2).

**4. Optimisation et compaction de la hiérarchie (Sec. 5, p. 6-7).**
- Les nœuds internes sont optimisés en rendant **toujours en pleine résolution** avec une granularité cible tirée au hasard (τ = τ_max^ξ τ_min^(1−ξ)), plutôt qu'en sous-échantillonnant les images, ce qui flouterait (Fig. 5, 7). Les feuilles sont gelées (stop-gradient). Le gradient de α′ (éq. 12) est dérivé à la main (p. 8).
- Filtre anti-aliasing EWA de Mip-Splatting (voir [yu2023_mip-splatting](../yu2023_mip-splatting/fiche.md)), nécessaire car la hiérarchie opère à plusieurs échelles (p. 7).
- Compaction : on supprime les nœuds rarement choisis, en partant de τ_min = 3 px puis en doublant jusqu'à τ_max = la moitié de la résolution de l'image (p. 7).

**5. Grandes scènes par chunks (Sec. 6, p. 7-8).**
- Chunks de 50×50 m (à pied) à 100×100 m (véhicule). On commence par un échafaudage grossier sur toute la scène (SfM, sans densification ni déplacement des positions) et une skybox de 100 000 Gaussiennes (p. 7).
- Chaque chunk est entraîné indépendamment, donc en parallèle. Densification sur le **maximum** du gradient écran au lieu de la moyenne ; régularisation par profondeur monoculaire (DPT) recalée sur les points SfM ; exposition par image (affine 3×4) (p. 8, annexe C).
- Consolidation : on supprime les primitives hors chunk plus proches d'un autre chunk et on crée une racine globale (p. 8).

**6. Rendu temps réel (p. 8).** La coupe est mise à jour **toutes les 2 images** ; les nœuds plus détaillés sont transférés de la RAM CPU vers le GPU ; un nettoyage a lieu toutes les 100 images. L'étape cut/expand est **asynchrone** par rapport au rendu (p. 11).

### Ce qui change par rapport au rasteriseur de Kerbl 2023 ([fiche](../kerbl2023_3dgs/fiche.md))

| Élément | 3DGS 2023 | Hierarchical 3DGS |
|---|---|---|
| Tuiles 16×16, clés tuile+profondeur, tri radix global, blending front-to-back | oui | **inchangés** (étapes preprocess / duplicate / tile ranges / alpha-blend conservées, Tab. 4 p. 11) |
| Ensemble rendu | toutes les Gaussiennes visibles | une **coupe** de la hiérarchie (étape cut/expand, asynchrone, 7,7-24,2 ms, Tab. 4) |
| Préprocessing | 1 Gaussienne = 1 jeu d'attributs | charge **parent + enfant** pour interpoler, soit deux fois plus de données (p. 11) |
| Nouvelle étape « weights » | — | calcul des t_n chaque image, **1,5-4 ms** (p. 11) |
| Alpha-blend | α = o·G, borné à 0,99 | calcul de α′ avec une instruction `pow` coûteuse (p. 11) ; falloff > 1 et activation valeur absolue ; gradient d'opacité annulé quand α est borné (p. 8-9) |
| Anti-aliasing | aucun | filtre EWA de Mip-Splatting (p. 7) |
| Mémoire / résidence | tout sur GPU | nœuds en RAM CPU, transfert à la demande (p. 8) ; 284 octets/Gaussienne en théorie, 400 dans l'implémentation (+69 %) (p. 11) |

## Résultats chiffrés

Rendu et fps : **NVIDIA A6000** (desktop), mono-vue, viewer SIBR modifié (p. 8, 10). Entraînement : **V100 32 GB** (p. 10). Images d'entrée : GoPro HERO6 en **1444×1080** (p. 8). La **résolution de rendu des mesures de fps n'est pas explicitement donnée** (non rapporté). Rendu stéréo, casque, latence : non rapportés.

| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| FPS scène complète, τ₁ = 3 px | 46 / 40 / 32 / 31 | SmallCity / Wayve / Campus / BigCity ; trajectoires vidéo ; A6000 ; 9,44M / 12,4M / 21,6M / 17,6M Gaussiennes rendues (66 / 34 / 33 / 19 % des feuilles) (Tab. 5, p. 11) |
| FPS scène complète, τ₂ = 6 px | 78 / 65 / 62 / 56 | 5,64M / 6,39M / 10,2M / 8,21M Gaussiennes (39 / 17 / 16 / 8 %) (Tab. 5) |
| FPS scène complète, τ₃ = 15 px | 150 / 125 / 133 / 103 | 2,26M / 2,10M / 3,01M / 2,68M Gaussiennes (16 / 6 / 5 / 3 %) (Tab. 5) |
| Résumé des auteurs | « 30+ FPS » en moyenne à τ₁, « ≈ 60 FPS » à τ₂ | toutes les trajectoires (p. 11) |
| Gaussiennes transférées CPU→GPU | 1 536 à 9 314 par image en moyenne | selon scène et τ (Tab. 5) |
| FPS sur un seul chunk | 3DGS 72-125 ; Ours (leaves) 39-70 ; Ours opt τ₁ 64-86 ; τ₂ 80-110 ; τ₃ 104-159 | 4 scènes, A6000 (Tab. 2, p. 10) |
| Temps par étape, un chunk (ms) | alpha-blend 3DGS 2,73-8,96 → τ₂ 3,00-3,98 ; weights 3,05-3,55 ; cut/expand 7,65-10,48 à τ₂ (asynchrone) | Tab. 4, p. 11 |
| Qualité PSNR / LPIPS / SSIM (un chunk) | SmallCity : 3DGS 25,34 / 0,337 / 0,776 ; leaves 26,62 / 0,259 / 0,820 ; opt τ₂ 26,29 / 0,275 / 0,810 ; opt τ₃ 25,68 / 0,324 / 0,786 (non optimisée τ₃ : 23,04) | Tab. 2, p. 10 ; test = 1 image sur 50 par caméra (p. 10) |
| Qualité, BigCity (un chunk) | 3DGS 21,48 / 0,445 / 0,721 ; leaves 23,10 / 0,348 / 0,769 ; opt τ₂ 23,05 / 0,359 / 0,762 | Tab. 2 |
| Qualité Mip-NeRF 360 (un chunk) | PSNR 3DGS 29,11 / ours 28,96 ; hiérarchie basique/optimisée : τ₁ 28,86/28,87, τ₂ 28,05/28,52, τ₃ 24,82/27,25 | p. 10 |
| Mill 19 contre Mega-NeRF | Building PSNR 21,52 contre 20,93 ; Rubble 24,64 contre 24,06 (images ÷4) | Tab. 3, p. 10 ; 3 h sur 2 ou 4 V100 contre 27-30 h sur 8 V100 pour Mega-NeRF (p. 11) |
| Temps d'entraînement | environ 1 h chacun pour le grossier, un chunk et l'optimisation de la hiérarchie, sur 1 V100 ; pic mémoire 2-5 / 8-10 / 11-16 GB | p. 10 ; chunks de 2 à 8M feuilles ; 4 / 11 / 22 / 46 chunks (p. 9) |
| Calibration | extraction + appariement ≈ 1 h + 2 h pour 40K images ; mapper hiérarchique 110 min (2 Xeon Gold 6240) ; BA par chunk 30 min à 5 h (V100 16 GB) | annexe B, p. 14-15 |
| Taille disque | 6 / 17 / 27 / 88 GB, soit ≈ 68 % de plus que 3DGS non hiérarchique | p. 10 |
| Latence | non rapportée (seuls les fps moyens et les ms par étape sont donnés) | — |

## Pertinence pour notre sujet

| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Référence LOD pour 3DGS (TOG/SIGGRAPH 2024) ; code et données publics. Aucun élément XR (stéréo, casque, latence). |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | Fusion de covariances anisotropes par KL (éq. 3-4) ; densification sur le maximum du gradient et profondeur monoculaire pour les captures éparses (p. 8, Tab. 6). |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | **Brique LOD de P3** : coupe en granularité pixels, interpolation lisse, streaming des nœuds. La sélection est par vue, sans visibilité ni occlusion (le culling par visibilité ou distance est laissé en perspective, p. 13). |
| 4. Évaluation (fps, latence, qualité, coût) | Tableau #Gaussiennes rendues → fps (Tab. 5) et décomposition par étape (Tab. 4), réutilisables pour un **modèle de coût**. Pas de latence ni de mesure du popping. |

## Pour (vis-à-vis de notre problématique)

- **Bouton qualité/coût continu et en pixels.** τ_ε règle directement le nombre de Gaussiennes rendues : de 66 % à 16 % des feuilles sur SmallCity, et le fps passe de 46 à 150 (Tab. 5). C'est exactement le levier dont P3 a besoin.
- **Les auteurs envisagent eux-mêmes un pilotage par budget.** Ils écrivent que remplacer la granularité fixe par une sélection dynamique « would allow to produce optimal quality at a given resource budget », et laissent cela en travaux futurs (p. 13).
- **Hiérarchie optimisée = meilleure qualité à budget égal.** À τ₃, le PSNR passe de 23,04 à 25,68 sur SmallCity (Tab. 2) et de 24,82 à 27,25 sur Mip-NeRF 360 (p. 10). Une LOD agressive reste donc acceptable.
- **Transitions lisses** (interpolation + α′) : moins de popping qu'un LOD discret, ce qui compte pour le confort en casque.
- **Mémoire GPU bornée par la coupe**, pas par la scène : RAM CPU + transfert à la demande de 1,5k à 9k Gaussiennes par image (Tab. 5). C'est le seul moyen montré ici de dépasser la VRAM (4080/4090 saturées, p. 11).
- **Sélection de coupe massivement parallèle** (temps constant par nœud) et asynchrone (p. 5, 11) : elle se découple de la boucle de rendu.
- Rasteriseur 3DGS conservé : compatible avec les accélérations orthogonales comme [FlashGS](../feng2024_flashgs/fiche.md) ou [Speedy-Splat](../hanson2024_speedy-splat/fiche.md) (hypothèse, non testé).

## Contre / limites

- **Fps insuffisants pour la VR tels quels.** 31-46 fps à τ₁ et 56-78 fps à τ₂, en **mono**, sur une A6000, à une résolution non précisée (Tab. 5). Un casque demande 72-90 Hz et deux vues. Il faudrait τ₃ (103-150 fps) avec une perte de qualité (BigCity opt τ₃ PSNR 22,82 contre 23,10 pour les feuilles, Tab. 2), ou un rasteriseur plus rapide.
- **Surcoût fixe du LOD.** Étape weights de 1,5-4 ms par image, preprocess plus lourd (2× les données), `pow` dans le blending (p. 11). Sans réduction (« leaves »), c'est **plus lent que 3DGS** : 39-70 fps contre 72-125 (Tab. 2).
- **Mise à jour de coupe toutes les 2 images + transfert CPU→GPU** (p. 8). Lors d'une rotation de tête rapide, la coupe et les nœuds peuvent être en retard d'au moins une image (hypothèse : risque de trous ou de détail tardif, non évalué). La latence n'est pas mesurée.
- **Pas de stéréo.** La granularité dépend de la vue ; deux yeux signifient deux coupes, ou une coupe commune à définir (non traité).
- **Popping du tri 3DGS non résolu.** Le tri par tuile d'origine est conservé ; l'interpolation traite seulement le changement de niveau. Voir [radl2024_stopthepop](../radl2024_stopthepop/fiche.md).
- **Mémoire et stockage.** 400 octets/Gaussienne (+69 %), disque +68 % (6-88 GB) (p. 10-11) : c'est à l'opposé d'un casque autonome.
- **Préparation lourde.** Environ 3 h de GPU V100 par chunk (grossier + chunk + hiérarchie), plus des heures de calibration COLMAP (p. 10, annexe B).
- **Artefacts dus aux captures éparses** et aux distracteurs mal retirés, comme les voitures qui s'arrêtent ; extrapolation de vue limitée (p. 10, 12). En VR, l'utilisateur sort de la trajectoire de capture.
- Domaine d'évaluation : scènes urbaines extérieures, pas d'intérieur industriel.

## Idées à creuser pour une approche novatrice

Toutes ces pistes sont des **hypothèses**, non testées dans le papier.

- **H1 — τ_ε piloté par QoS (P3).** On boucle τ_ε sur le temps d'image mesuré, ou sur un modèle de coût appris à partir de la relation #Render → fps (Tab. 5 : quasi inverse). On étend ensuite à un optimiseur multi-objectif fps/latence/énergie/réseau. **Risque pour la nouveauté** : le « budget de ressources » est explicitement annoncé en travaux futurs (p. 13). Notre apport doit donc porter sur le modèle d'optimisation QoS/QoE (edge, réseau, confort), pas seulement sur « LOD à budget ».
- **H2 — τ_ε fovéal et par œil.** On remplace le τ_ε global par τ_ε(excentricité) : 3 px en fovéa, 15 px en périphérie. On calcule **une seule coupe « cyclope »** pour les deux yeux avec le τ le plus fin des deux, ce qui relie P2 à P3. On mesurerait le gain de fps et les écarts binoculaires. À comparer à [franke2024_vr-splatting](../franke2024_vr-splatting/fiche.md) et [xin2025_a3fr-foveated](../xin2025_a3fr-foveated/fiche.md).
- **H3 — Coupe prédictive pour la tête (VR).** On calcule la coupe et les transferts pour la pose prédite à t + latence (prédiction de pose du casque), en élargissant le frustum. On mesurerait le taux de nœuds manquants lors de rotations rapides.
- **H4 — Découpage edge/casque par niveau (P1 + P4).** Les niveaux grossiers (τ élevé, peu de Gaussiennes) resteraient résidents sur le casque. Les nœuds fins proches seraient streamés depuis l'edge, sur le modèle du transfert CPU→GPU actuel (1,5k-9k Gaussiennes par image) transposé au réseau. Voir [shi2024_lapisgs](../shi2024_lapisgs/fiche.md) et [wan2025_edge-collab-gs](../wan2025_edge-collab-gs/fiche.md).
- **H5 — Hiérarchie + compression.** On combinerait les nœuds internes avec la quantification ou le pruning ([lee2023_compact3d](../lee2023_compact3d/fiche.md), [fan2023_lightgaussian](../fan2023_lightgaussian/fiche.md)) pour annuler les +69 % par Gaussienne.

## Citations clés

> « We introduce a hierarchy of 3D Gaussians that preserves visual quality for very large scenes, while offering an efficient Level-of-Detail (LOD) solution for efficient rendering of distant content with effective level selection and smooth transitions between levels. » (`doc:18f9541/tier:standard/page:1/block:8`)

> « We find the cut by identifying the nodes whose projected bounding box is smaller than a given target granularity 𝜏𝜖 on screen, e.g., 1 pixel. » (`doc:18f9541/tier:standard/page:5/block:8`)

> « We update the cut every 2 frames to add details by transferring nodes to the GPU from CPU RAM, and run cleanup every 100 frames. » (`doc:18f9541/tier:standard/page:8/block:7`)

> « All paths yielded 30+ FPS on average for the high-quality setting, 𝜏1, and ≈60 FPS at our medium setting, 𝜏2. » (`doc:18f9541/tier:standard/page:11/block:11`)

> « Instead of a fixed granularity, adding dynamic LOD selection to our prototype would allow to produce optimal quality at a given resource budget. » (`doc:18f9541/tier:standard/page:13/block:3`)

## Liens

- **Papiers liés :**
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) : rasteriseur de base, repris tel quel (tuiles, tri, blending) et étendu par la coupe et l'interpolation.
  - [yu2023_mip-splatting](../yu2023_mip-splatting/fiche.md) : filtre EWA utilisé pour l'anti-aliasing multi-échelle (p. 7).
  - [feng2024_flashgs](../feng2024_flashgs/fiche.md) : accélération orthogonale du rasteriseur (intersection précise), cumulable a priori avec la coupe LOD.
  - [radl2024_stopthepop](../radl2024_stopthepop/fiche.md) : popping dû au tri, que cette hiérarchie ne traite pas.
  - [shi2024_lapisgs](../shi2024_lapisgs/fiche.md), [wan2025_edge-collab-gs](../wan2025_edge-collab-gs/fiche.md) : streaming par couches et edge, pour H4 (P1/P4).
  - [franke2024_vr-splatting](../franke2024_vr-splatting/fiche.md), [tu2025_vrsplat](../tu2025_vrsplat/fiche.md), [xin2025_a3fr-foveated](../xin2025_a3fr-foveated/fiche.md) : VR et fovéation, pour H2.
  - [kamdjou2024_xr-dt-iiot](../kamdjou2024_xr-dt-iiot/fiche.md) : cadre QoS/QoE pour H1.
- **Travaux cités à suivre :** SMERF (Duckworth 2023, grandes scènes streamables), Block-NeRF (Tancik 2022), Mega-NeRF (Turki 2022), Nanite (Karis 2021, LOD virtualisé), QSplat (Rusinkiewicz & Levoy 2000), Sequential Point Trees (Dachsbacher 2003).
