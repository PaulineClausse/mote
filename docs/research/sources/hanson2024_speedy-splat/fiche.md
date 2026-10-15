---
citekey: hanson2024_speedy-splat
mineru_doc: c4fa061
type: conférence
statut: fiche complète
tags: [3dgs, acceleration-rendu, tile-intersection, bounding-box, pruning, hessienne, compression, entrainement-rapide, rendu-temps-reel, p3-budget]
---

# Speedy-Splat: Fast 3D Gaussian Splatting with Sparse Pixels and Sparse Primitives

**Référence :** Hanson, A., Tu, A., Lin, G., Singla, V., Zwicker, M., Goldstein, T. (2024). Speedy-Splat: Fast 3D Gaussian Splatting with Sparse Pixels and Sparse Primitives. University of Maryland, College Park. arXiv [2412.00578](https://arxiv.org/abs/2412.00578) (version v3 du 14 août 2025, p. 1). Le texte n'indique pas de venue.
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Projet :** https://speedysplat.github.io (p. 1)

> Type « conférence » mis par défaut : le texte MinerU ne mentionne pas de venue, à vérifier.

## En une phrase

Deux leviers orthogonaux sur le coût du rendu 3DGS, qui est proportionnel à (nombre de Gaussiennes) × (pixels traités par Gaussienne). (1) Localiser exactement chaque Gaussienne dans les tuiles, avec SnugBox et AccuTile : 1,99× plus rapide **sans changer l'image**. (2) Élaguer pendant l'entraînement par un score hessien bon marché (Soft Pruning à 80 %, puis Hard Pruning à 30 %). En moyenne sur 13 scènes et sur RTX A5000 : **6,71× plus de fps** (134 → 898), **10,6× moins de Gaussiennes** (2,93 M → 0,28 M) et un entraînement **1,47× plus rapide**, au prix d'une baisse de qualité modérée (p. 2, 7).

## Problème traité

- Deux inefficacités de 3DGS sont identifiées (p. 4).
  - La **borne de tuile est trop conservatrice**. 3DGS prend le carré circonscrit au cercle de rayon ⌈3√λ_max⌉ (éq. 8). Ce calcul ignore l'opacité σ_i, alors que l'extension réelle est fixée par le seuil α < 1/255 (p. 4, Fig. 2).
  - Les modèles sont **fortement surparamétrés**.
- Motivation affichée : VR, systèmes en réseau et streaming multi-vues. « Real-time rendering on resource-constrained edge devices, such as mobile phones, has yet to be achieved » (p. 1).
- Peu de travaux de compression visent directement la vitesse de rendu (p. 1).

## Méthode / contributions

**Rappel du pipeline 3DGS instrumenté (Tab. 1 p. 3 ; §3.2 p. 3).** Les étapes sont : Preprocess (projection EWA, comptage des tuiles), InclusiveSum (préfixe pour l'allocation), duplicateWithKeys (clés tuile + profondeur), RadixSort, identifyTileRanges, Render (par pixel, α = σ·g, rejet si α ≤ 1/255, éq. 5-7). **Le tri et le blending restent ceux de 3DGS** : ordre global par profondeur du centre, sans tri par pixel.

**1. SnugBox, boîte englobante serrée (§4.1.1, p. 4).**
- L'extension exacte est l'ellipse t = a·x_d² + 2b·x_d·y_d + c·y_d², avec t = 2 log(255·σ_i) et Σ₂D⁻¹ = [[a, b], [b, c]] (éq. 9-14). **Elle dépend de l'opacité** : une Gaussienne peu opaque a une empreinte plus petite.
- La boîte alignée aux axes s'obtient analytiquement en annulant ∂y_d/∂x_d (éq. 15-16), puis par symétrie en x. Le coût est constant : l'algorithme est appelé 2 fois, dans Preprocess et dans duplicateWithKeys.
- Résultat : **1,82×** en moyenne, sans effet sur l'image.

**2. AccuTile, tuiles exactement intersectées (§4.1.2, Algo. 1 p. 5-6 ; preuve en annexe A.1 p. 11).**
- On part de la boîte SnugBox et on parcourt le **plus petit côté** (lignes ou colonnes de tuiles).
- Pour chaque ligne, on calcule le min et le max de l'ellipse. Seuls deux nouveaux points d'intersection sont nécessaires par itération, car le bord est partagé avec la ligne suivante. On garde les extrema de SnugBox s'ils tombent dans la ligne ; sinon la monotonie impose que l'extremum soit sur le bord.
- Le comptage est proportionnel au plus petit côté, et le traitement au nombre de tuiles.
- Résultat : **1,99×** cumulé, toujours sans perte (Tab. 1-2).

**3. Score d'élagage efficace (§4.2.1, p. 6).**
- On part de PUP 3D-GS : U_i = log|∇_{μ,s} I · ∇_{μ,s} Iᵀ|, soit une Hessienne 6×6 par Gaussienne. Il coûte N × 36 en mémoire et casse le flux de gradients par pixel (p. 5-6).
- On le reparamétrise par la valeur projetée g_i(p), qui est scalaire : Ũ_i = (∇_{g_i} I)². Ce gradient est déjà calculé dans le backward du Render, il suffit de le mettre au carré et de l'agréger. La mémoire passe à ∝ N (**36× moins**), ce qui rend le score utilisable pendant l'entraînement.

**4. Soft Pruning (§4.2.2, p. 6).** On élague **80 %** des Gaussiennes juste avant chacun des trois resets d'opacité (itérations 6000, 9000, 12000), pendant la densification.

**5. Hard Pruning (§4.2.3, p. 7).** Après la densification, on élague **30 %** des Gaussiennes toutes les 3000 itérations à partir de l'itération 15000. Les itérations suivantes servent de fine-tuning. Le couple (80 %, 30 %) est choisi empiriquement par un balayage (Fig. 7, annexe A.2 p. 12).

**Ce qui change par rapport au rasteriseur de [Kerbl 2023](../kerbl2023_3dgs/fiche.md).** Seules les **bornes Gaussienne → tuile** changent, ainsi que le nombre de primitives. Le tri radix global, les tuiles 16×16, le blending front-to-back et l'arrêt précoce sont inchangés. Le popping de 3DGS est donc conservé tel quel, puisqu'il n'y a pas de tri par pixel. Comparé au **tile-based culling de [StopThePop](../radl2024_stopthepop/fiche.md)** (test par tuile candidate avec load balancing), AccuTile ne parcourt pas toutes les tuiles candidates (annexe A.4, p. 13).

## Résultats chiffrés

Matériel : **NVIDIA RTX A5000 (desktop)**. Les fps sont mesurés par événements CUDA **autour du seul forward de rendu**, moyenne de 3 exécutions × 20 rendus du jeu de test (p. 3, 7). Les **fps sont mono-vue**. La **résolution de rendu n'est pas indiquée** (on suppose celle du jeu de test standard de 3DGS : non rapporté). Scènes : 9 M360, 2 T&T (train, truck), 2 DB (drjohnson, playroom), avec les poses COLMAP fournies (p. 7).

| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| FPS moyen (cumulatif) | 134 → SnugBox 244 (1,82×) → AccuTile 267 (1,99×) → Soft 420 (3,14×) → **Hard 898 (6,71×)** | 13 scènes, A5000 (Tab. 2, p. 7) |
| Temps de frame par étape | Baseline 7,478 ms (dont Render 4,483, Sort 1,551, Dup. 0,570, Preproc. 0,665) → final **1,114 ms** (Render 0,619, Sort 0,215, Preproc. 0,091) | Tab. 1, p. 3 |
| Accélération rendu par dataset | M360 **6,51×** ; T&T **6,30×** ; DB **7,46×** | Tab. 3 p. 8 ; Tab. 5-6 p. 12 |
| FPS par scène (extrêmes) | bicycle 71 → 662 (9,25×) ; garden 91 → 640 (7,03×) ; bonsai 201 → 978 (4,87×) ; train 200 → 1392 ; drjohnson 126 → 1122 (8,91×) | Tab. 12, p. 14 |
| Nombre de Gaussiennes | 2,93 M → 1,64 M (Soft) → **0,28 M** (10,6×). M360 10,6× ; T&T 10,1× ; DB 11,1× | Tab. 2-3, 5-6 |
| Qualité M360 PSNR / SSIM / LPIPS | 27,55 / 0,814 / 0,222 → AccuTile 27,57 / 0,814 / 0,221 → **final 26,94 / 0,782 / 0,296** | Tab. 3, p. 8 (3D-GS ré-entraîné) |
| Qualité T&T | 23,70 / 0,849 / 0,178 → final **23,45 / 0,821 / 0,241** | Tab. 5, p. 12 |
| Qualité DB | 29,09 / 0,886 / 0,288 → final **29,32 / 0,887 / 0,311** | Tab. 6, p. 12 |
| Pire perte PSNR par scène | kitchen 31,49 → 29,91 (−1,58 dB) ; bonsai −1,13 ; counter −0,86. Scènes en gain : drjohnson +0,32 et playroom +0,14 | Tab. 9, p. 14 |
| LPIPS par scène | garden 0,122 → 0,213 ; treehill 0,346 → 0,463 | Tab. 11, p. 14 |
| Temps d'entraînement | 23,2 → **15,7 min** (1,47×) en moyenne. M360 1,45× ; T&T 1,58× ; DB 1,57× | Tab. 2, 3, 5, 6 (A5000) |
| Entraînement par scène | bicycle 31,9 → 19,7 min ; train 11,1 → 7,2 min | Tab. 13, p. 14 |
| Mémoire | Seule la compression en **nombre de Gaussiennes** est rapportée (10,6×). Taille en MB et VRAM non rapportées. Score d'élagage : 36× moins de mémoire que PUP | p. 6-7 |
| Contre PUP 3D-GS (même pipeline, 88,44 % élagués) | PSNR 26,87 contre 26,21 ; LPIPS 0,284 contre 0,273 ; FPS 345,5 contre 378,6 | Tab. 4, p. 8 |
| AccuTile contre culling de StopThePop | Frame 3,660 ms contre 4,051 ms (baseline 7,457). Preprocess StopThePop 0,811 contre 0,659 ms. AccuTile plus rapide sur les 13 scènes | Tab. 7-8, p. 13. Le test StopThePop est fait **sans** le seuil α « paddé », ce qui le favorise en aval selon les auteurs |
| Latence / stéréo / casque / mobile | **Non rapportés** | — |

Incohérence notée : la Fig. 1 (truck) annonce une accélération d'entraînement de 1,38× (p. 1), alors que la Tab. 13 donne 1,61× pour truck (p. 14).

## Pertinence pour notre sujet

| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Il sert de référence pour les « accélérations de rendu » et donne un tableau comparatif utile de 9 méthodes d'élagage (Tab. 3, 5, 6 : LightGaussian, Compact, EAGLES, Mini-Splatting, PUP…). La VR est mentionnée comme motivation seulement. |
| 2. Gaussiennes 3D depuis SfM, covariance anisotrope | Il intègre l'élagage **pendant** l'entraînement (Soft et Hard) au calendrier de densification de 3DGS, avec un score hessien qui ne coûte que O(N). L'entraînement devient 1,47× plus court. |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | **SnugBox et AccuTile sont plug-and-play, sans perte, et donnent environ 2×.** L'ellipse dépend de l'opacité, ce qui en fait un vrai culling « visibility-aware » au niveau des tuiles. On peut l'appliquer à tout rasteriseur à tuiles, y compris un portage casque. Rien sur le tri ni sur le popping. |
| 4. Évaluation (fps, latence, qualité, coût) | Protocole de timing par étape (CUDA events) réutilisable. Il manque la résolution, la latence bout-en-bout, la VRAM, la taille disque et la mesure par œil. |

## Pour (vis-à-vis de notre problématique)

- **Marge de fps énorme sur GPU desktop « moyen de gamme pro »** (A5000) : 640 fps minimum par scène après élagage (Tab. 12). Même la pire scène de base (bicycle, 71 fps) passe à 662 fps. Pour une stéréo 2 × 1080p à 90 Hz, la marge semble très large, mais c'est une hypothèse : la résolution n'est pas donnée.
- **Gains sans perte immédiatement transférables** : AccuTile donne environ 2× sans ré-entraînement ni changement d'image (Tab. 3 : PSNR 27,57 contre 27,55). Ces bornes s'appliquent aussi à la seconde vue en stéréo.
- **10× moins de Gaussiennes**, soit a priori environ 10× moins de mémoire modèle (hypothèse : seul le nombre est rapporté). C'est précisément ce qu'exige un casque autonome.
- L'**entraînement plus court** (15,7 min en moyenne) va dans le sens du verrou « entraînement coûteux » du sujet.
- Le **score d'élagage est un sous-produit du backward**, donc peu coûteux. Il pourrait servir de mesure d'importance par Gaussienne pour un LOD ou un streaming (P3, P4).

## Contre / limites

- **Qualité dégradée par le Hard Pruning**, surtout en perceptuel : LPIPS 0,222 → 0,296 sur M360 (+33 %), SSIM 0,814 → 0,782, et jusqu'à −1,58 dB sur kitchen (Tab. 3, 9). Les auteurs le reconnaissent (p. 8). Le score reste un peu inférieur à celui de PUP (Tab. 4).
- **Aucune évaluation XR** : pas de stéréo, de latence, de casque ni de mobile. La **résolution de rendu n'est pas précisée**, et les fps ne mesurent que le forward du rasteriseur (p. 7). Ce sont donc des fps « noyau », pas des fps applicatifs.
- **Le popping n'est pas traité** : le tri global de 3DGS est conservé. De plus, moins de Gaussiennes veut dire des Gaussiennes plus grandes, et [StopThePop](../radl2024_stopthepop/fiche.md) montre que cela **aggrave** le popping sous 3DGS (Opacity Decay, Tab. 3 de StopThePop). Le risque en VR n'est pas évalué ici (hypothèse).
- Les ratios d'élagage (80 %, 30 %) sont fixes et **indépendants de la scène et du point de vue**. Il n'y a pas de LOD ni d'adaptation dynamique.
- Une seule plateforme GPU (A5000, CUDA).

## Idées à creuser pour une approche novatrice

Toutes les pistes ci-dessous sont des **hypothèses**, non testées dans le papier.

- **H1 — P3 (budget piloté par la QoS).** Le score Ũ_i = (∇_{g_i} I)² fournit un classement d'importance quasi gratuit. On pourrait remplacer les ratios fixes par un **budget N_max dérivé de la cible fps/QoE**, via le modèle QoS/QoE de [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md), et produire plusieurs niveaux emboîtés (0,28 M, 1,64 M, 2,9 M) pour un LOD. À comparer au budget constructif de [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md).
- **H2 — P2 (stéréo) et AccuTile.** L'ellipse exacte se calcule par œil à coût constant. Pour mutualiser, on calculerait une fois l'union des empreintes gauche/droite dans un repère d'écran commun (les deux écrans étant rectifiés), puis on dupliquerait les clés.
  - Après Speedy-Splat, le Sort pèse encore 19 % du temps de frame (0,215 sur 1,114 ms) et le Render 56 % (Tab. 1, notre calcul). Le partage du tri garde donc un intérêt, contrairement au cas de StopThePop, où le tri n'est plus que 6 %.
- **H3 — Combinaison StopThePop + AccuTile + élagage.** Il faudrait vérifier si le tri hiérarchique de StopThePop reste cohérent (FLIP₇) avec 10× moins de Gaussiennes, et si AccuTile remplace avantageusement son tile culling (3,66 contre 4,05 ms). [VRSplat](../tu2025_vrsplat/fiche.md) fait une combinaison proche avec Mini-Splatting, à comparer.
- **H4 — P4 (streaming progressif).** On enverrait d'abord les Gaussiennes survivantes du Hard Pruning (≈ 10 % du total), puis le complément dans l'ordre du score. La qualité intermédiaire est connue grâce à la courbe cumulative des Tab. 9-11.
- **H5 — Culling fovéal.** Le seuil t = 2 log(255·σ) pourrait être relevé en périphérie (seuil α plus élevé), ce qui rétrécirait les ellipses et réduirait les paires Gaussienne-tuile hors fovéa (P1). À comparer à RTGS [19], cité p. 2 (élagage + fovéation sur mobile, pas dans la base).

## Citations clés

> « Efficient rendering is essential in applications such as virtual reality, networked systems, and multi-view streaming. Real-time rendering on resource-constrained edge devices, such as mobile phones, has yet to be achieved » (`doc:c4fa061/tier:standard/page:1/block:14`)

> « We find the existing algorithm to be overly conservative » (`doc:c4fa061/tier:standard/page:2/block:2`)

> « This approach neglects opacity σ_i in its calculation and generally overestimates the Gaussian extent » (`doc:c4fa061/tier:standard/page:4/block:10`)

> « On average, rendering speed is accelerated by 6.71×, model size is reduced by 10.6×, and training speed is improved by 1.4× across all evaluated scenes » (`doc:c4fa061/tier:standard/page:2/block:4`)

> « All experiments are conducted on an Nvidia RTXA5000 GPU » (`doc:c4fa061/tier:standard/page:7/block:11`)

> « A limitation of Speedy-Splat is that it produces slightly lower image quality than 3D-GS. » (`doc:c4fa061/tier:standard/page:8`, §6)

## Liens

- **Papiers liés :**
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) : rasteriseur de base, dont seules les bornes de tuiles sont modifiées ici.
  - [radl2024_stopthepop](../radl2024_stopthepop/fiche.md) : tile culling exact comparé à AccuTile (annexe A.4). Complémentaire, puisqu'il traite le tri et le popping que Speedy-Splat ignore.
  - [feng2024_flashgs](../feng2024_flashgs/fiche.md) : intersection Gaussienne-tuile similaire à StopThePop, selon les auteurs (p. 2).
  - [fan2023_lightgaussian](../fan2023_lightgaussian/fiche.md), [lee2023_compact3d](../lee2023_compact3d/fiche.md) : méthodes d'élagage et de compression comparées (Tab. 3). LightGaussian : 2,94× de compression, 1,76× en fps sur M360.
  - [mallick2024_taming-3dgs](../mallick2024_taming-3dgs/fiche.md) : budget de Gaussiennes fixé par l'utilisateur, alternative au pruning (H1).
  - [tu2025_vrsplat](../tu2025_vrsplat/fiche.md) : un autre groupe (X. Tu et l'équipe de StopThePop, sans lien avec A. Tu) combine la réduction de primitives (Mini-Splatting, jusqu'à 10×) et le tri de StopThePop pour la VR (> 72 fps, RTX 4090 → Quest 3, d'après son résumé p. 1). C'est le pendant « VR » de H3.
  - [oh2025_neo-on-device](../oh2025_neo-on-device/fiche.md), [du2026_mobile-gs](../du2026_mobile-gs/fiche.md) : rendu sur appareil contraint, là où l'élagage 10× est le plus utile.
