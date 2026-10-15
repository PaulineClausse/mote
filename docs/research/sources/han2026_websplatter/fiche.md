---
citekey: han2026_websplatter
mineru_doc: 16eea1a
type: article (préprint arXiv, cs.GR)   # venue non indiquée dans le texte
statut: fiche complète
tags: [3dgs, web, webgpu, navigateur, multi-appareils, tri-radix, wait-free, rasterisation-matérielle, culling, mobile, snapdragon-8-gen-3, iphone, apple-silicon, mémoire]
---

# WebSplatter: Enabling Cross-Device Efficient Gaussian Splatting in Web Browsers via WebGPU

**Référence :** Yudong Han, Weichen Bi, Yun Ma (Institute for AI, Peking University), Chao Xu, Xiaodan Ye, Zilong Dong (Tongyi Lab, Alibaba) (2026). *WebSplatter: Enabling Cross-Device Efficient Gaussian Splatting in Web Browsers via WebGPU.* Préprint arXiv [2602.03207](https://arxiv.org/abs/2602.03207) (cs.GR, 3 fév. 2026) ; venue non indiquée. Code : anonymous.4open.science/r/webgs (`doc:16eea1a/tier:standard/page:1`)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Visualiseur 3DGS **WebGPU** (TypeScript + WGSL, ~6 600 lignes) conçu pour tourner partout : **tri radix GPU « wait-free »** (scan de Blelloch hiérarchique, sans attente inter-workgroups, donc sans blocage sur les GPU dont l'ordonnancement n'est pas garanti), **rasterisation par le pipeline matériel** (un quad instancié par splat, taille calée sur l'opacité) et culling AABB écran ; 1,06× à 4,5× plus rapide que les viewers web open source, **mesuré sur 10 appareils réels** (RTX 3070 → Snapdragon 865), mais en **mono**, **sans résolution indiquée**, sans métrique de qualité et sans XR (`page:1`, `page:5`, `page:6`).

## Problème traité
- WebGL n'a pas de compute shaders → le tri est fait sur CPU (JS/WASM), ce qui ne passe pas à l'échelle (`page:1`, `page:9`).
- Les portages WebGPU existants reprennent du code CUDA/Vulkan qui suppose un ordre d'ordonnancement des workgroups (spin-wait sur un drapeau atomique global) : sur Apple M1 cela dégénère en attente active (tri 458 ms), et sur mobile les pics mémoire font planter le navigateur (`page:1`, `page:3–4`, `page:7`).

## Méthode / contributions
- **Pipeline hybride compute/render** (`page:3`, Fig. 1) :
  1. *Pré-processing* (compute) : projection, AABB de l'ellipse 2D, **culling écran**, axes de l'ellipse compressés en 2×u32 (demi-flottants), profondeur en f32, SH → couleur **RGBA8 empaquetée sur 32 bits** (moins de bande passante) (`page:3`).
  2. *Tri* (compute) : **tri radix LSD 4 passes × 8 bits** sur la profondeur (en espace vue) ; chaque passe = histogramme local → **scan de Blelloch hiérarchique** (une dispatch par niveau, barrières intra-workgroup seulement) → scatter. Travail O(N), mémoire auxiliaire O(N/wg), **aucune attente inter-workgroups** (`page:4`). Tri **global par splat** (pas de paires tuile/splat).
  3. *Rasterisation* (render) : **pas de rasteriseur à tuiles** — un quad (2 triangles) instancié par Gaussienne, dessiné arrière→avant avec blending matériel ; rayon r = √ln(255·σ) (coupure à α = 1/255), Gaussiennes σ < 1/255 éliminées ; coordonnées locales interpolées par le matériel, e^(−a) évalué dans le fragment shader (`page:4`).
- Justification explicite : sur portables/mobiles à bande passante limitée, générer et trier le buffer ⟨tuile, splat⟩ des implémentations CUDA est **le** goulot → le pipeline matériel évite ce coût (`page:4`).

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| **Nature des mesures** | **Mesures réelles** dans le navigateur (Chrome, sauf Safari/Firefox indiqués), V-Sync activé, temps GPU instrumentés (timestamp queries), **médiane** du temps de frame (pré-proc + tri + rendu) | `page:5`, `page:11` |
| Résolution | **Non rapportée** (« fixed resolution and camera position » sans valeur) | `page:6` |
| Mono / stéréo | **Mono** ; aucune évaluation stéréo, WebXR ou casque | — |
| RTX 3070 (desktop) | garden (5,8 M splats) **9,5 ms ≈ 105 FPS** (Firefox 11,4 ms) ; baselines 14,4–88,8 ms | `page:5`, Table 1 |
| MacBook Air M4 | garden 63,7 ms (≈ 16 FPS) ; Safari 68,6 ms ; van gogh (0,34 M) 11,7 ms (≈ 86 FPS) | Tables 1, 3 |
| MacBook Pro M1 | garden 112,0 ms (≈ 9 FPS) ; baseline W1 510,8 ms (×4,5) | Table 1 |
| Lenovo MX350 / Intel NUC iGPU | garden 164,3 / 151,2 ms (≈ 6–7 FPS) | Table 1 |
| **Redmi K70 Pro (Snapdragon 8 Gen 3)** | bicycle-c (1,06 M) **33,6 ms ≈ 30 FPS** ; van gogh 29,0 ms (≈ 35 FPS) ; truck (2,5 M) 52,7 ms (≈ 19 FPS) ; train 76,4 ms ; bonsai 52,9 ms ; baseline WebGPU W1 : 39,5 ms (crash sur truck) | Tables 1, 3 ; FPS = 1000/ms, calcul personnel |
| iPhone 15 Pro Max (Safari) | bicycle-c 38,5 ms (≈ 26 FPS) | Table 1 |
| Oppo Find X2 (Snapdragon 865) | bicycle-c 105,2 ms (≈ 9,5 FPS) ; baseline W2 4553,6 ms | Table 1 |
| Décomposition | RTX 3070 : 13/24/63 % (pré-proc/tri/rendu) ; K70 Pro : 10/29/**61 %** ; MX350 : 47/28/25 % → **jamais sort-bound** ; haut de gamme et mobile récent **render-bound** | `page:6`, Table 2 |
| Tri seul | RTX 3070 2,3 ms (vs 55,8 ms CPU antimatter15) ; K70 Pro 9,7 ms ; M1 19,0 ms (vs 458,4 ms spin-wait) | `page:7–8`, Table 4 |
| Stabilité | MacBook Air M4 garden : écart-type 22,3 ms, P99 116,9 ms | `page:5` |
| Ablation (M4, garden) | sans culling écran : +5,8 % (63,7 → 67,4 ms) ; sans rayon adaptatif à l'opacité : **+15 %** (→ 73,2 ms), rendu +18,8 % (overdraw) | `page:8`, Table 5 |
| Mémoire | Pic VRAM garden, RTX 3070 : **1,20 Go** (W1 1,90 ; W2 > 2,80 ; WebGL S2 1,19 ; S1 0,83) ; seul viewer à ne planter sur aucun appareil | `page:6`, `page:8` |
| Qualité | **Aucune métrique** (PSNR/SSIM/LPIPS absents) ; comparaison visuelle côte à côte avec CUDA officiel sur garden, « comparable » | `page:6–7`, Fig. 3 |
| Latence / énergie | **Non rapportées** (hors P99 du temps de frame) | — |
| Entraînement | Hors sujet (lit des PLY 3DGS standard) | `page:5` |

## Utilisable pour WebXR sur Quest ?
- Le papier **ne parle ni de WebXR, ni de casque, ni de Quest** ; seule une référence au titre évocateur (Rodríguez et al. 2025, « WebGPU-Based 3D Engine for Real-Time Rendering and XR Applications ») apparaît (`page:10`).
- Navigateurs couverts : Chrome (WebGPU depuis v113), Safari 26 (iOS/macOS), Firefox 141 (Windows, instable) (`page:5`). Le navigateur Quest (Chromium) et le couplage WebXR + WebGPU ne sont **pas évalués** (disponibilité à vérifier hors papier).
- Ordre de grandeur (hypothèse, extrapolation personnelle) : le meilleur mobile testé (Snapdragon 8 Gen 3, a priori plus puissant que le XR2 Gen 2 du Quest 3 — *hors papier, à vérifier*) fait **~30 FPS mono** sur une scène de ~1 M splats à résolution téléphone non précisée, et le système y est **render-bound à 61 %**. Une stéréo à 2064×2208/œil multiplierait la charge de rendu → **loin de 72 Hz** sans réduction drastique de résolution/splats.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Donne l'état réel du **web 3DGS** multi-appareils (4 viewers de référence : antimatter15/splat, GaussianSplats3D, web-splat, gaussian-splatting-webgpu) et des supports WebGPU navigateurs (`page:5`, `page:11`) ; piste de déploiement « zéro installation » |
| 2. Gaussiennes 3D depuis SfM | Rien (consomme des PLY) |
| 3. Rendu rapide, visibilité, casque XR | Tri radix wait-free portable ; rasterisation matérielle par quads ; rayon adaptatif à l'opacité (−15 % de temps) ; culling écran ; empaquetage RGBA8 |
| 4. Évaluation | Mesures réelles multi-appareils avec décomposition par étape ; mais pas de résolution, pas de qualité, pas de latence |

## Pour (vis-à-vis de notre problématique)
- **Seules mesures multi-appareils réelles** de notre base, incluant deux téléphones récents : fixe un plancher réaliste (~30 FPS mono pour ~1 M splats sur Snapdragon 8 Gen 3) (`page:5`).
- Confirme **sur mobile réel** que, une fois le tri porté sur GPU, le coût dominant est la **rasterisation** (51,8–62,6 % sur appareils haut de gamme, 61 % sur K70 Pro, jusqu'à 84 % sur petite scène) — cohérent avec le constat post-StopThePop de la base et en tension avec la thèse « tri = goulot » de [Neo](../oh2025_neo-on-device/fiche.md) et [Mobile-GS](../du2026_mobile-gs/fiche.md) (`page:6`).
- Pipeline matériel (quads + blending) = approche naturellement portable vers WebXR/OpenGL ES/Vulkan de casque ; robustesse mémoire (1,20 Go) pertinente pour un casque.

## Contre / limites
- **Résolution absente**, **qualité non chiffrée**, **mono**, pas de XR : impossible de répondre directement à « ≥ 30 fps stéréo 1080p sur casque ».
- Tri **global par profondeur du centre** + blending matériel : même approximation que 3DGS/viewers web → popping en rotation (cf. [StopThePop](../radl2024_stopthepop/fiche.md)) non traité ; pas d'Optimal Projection pour grand FOV.
- Gains modestes sur mobile (×1,18 vs meilleur baseline sur K70 Pro) ; le ×4,5 vient surtout du pathologique spin-wait sur M1 (`page:5`).
- Non évalué par les pairs (préprint) ; le résumé dit 1,2–4,5×, la conclusion 1,06–2,26× (`page:1`, `page:9`).

## Idées à creuser pour une approche novatrice
- *Hypothèse (P2)* : avec un **tri global par splat** (et non par tuile), un **seul tri pour les deux yeux** est trivial à mettre en œuvre en triant par distance au point cyclopéen (milieu des yeux) ; l'erreur d'ordre entre yeux est faible pour les objets lointains. À mesurer : Δ d'ordre / popping vs deux tris, gain = ~29 % du temps (part du tri sur K70 Pro) × 1 œil.
- *Hypothèse* : **prototype WebXR + WebGPU sur Quest 3** en réutilisant WebSplatter (code disponible) — premier point de mesure réel « casque autonome » de notre étude, avec rendu multiview et fovéation fixe (tailles de quads réduites en périphérie).
- *Hypothèse (P4)* : le web est le cadre naturel du **streaming progressif de splats** (LOD envoyés au fil de l'eau, cf. [LapisGS](../shi2024_lapisgs/fiche.md)) ; WebSplatter fournit la brique de rendu, pas le streaming.
- *Hypothèse (P3)* : le rayon adaptatif r = √ln(255·σ) pourrait être rendu dépendant d'un budget (seuil α relevé en périphérie ou sous charge) → contrôle continu de l'overdraw, principal coût mesuré.

## Citations clés
> « WebSplatter introduces a wait-free hierarchical radix sort that circumvents the lack of global atomics in WebGPU, ensuring deterministic execution across diverse hardware. » (`doc:16eea1a/tier:standard/page:1`)

> « Tile-based methods, common in CUDA implementations, build and process a large buffer of ⟨tile, splat⟩ pairs [...] On heterogeneous devices such as laptops and mobile phones, limited bandwidth makes this step a major bottleneck. » (`doc:16eea1a/tier:standard/page:4`)

> « Meanwhile, WebSplatter never becomes sort-bound across all tested hardware. » (`doc:16eea1a/tier:standard/page:6`)

## Liens
- Papiers liés :
  - [Du 2026, Mobile-GS](../du2026_mobile-gs/fiche.md) : même SoC Snapdragon 8 Gen 3, natif Vulkan, sans tri, modèle compressé : 127 FPS à froid / 74 FPS stables vs ~30 FPS ici (3DGS non compressé, navigateur).
  - [Oh 2025, Neo](../oh2025_neo-on-device/fiche.md) : thèse inverse (tri = goulot bande passante) — mais sur ASIC simulé où la rasterisation est déjà accélérée.
  - [Radl 2024, StopThePop](../radl2024_stopthepop/fiche.md), [Feng 2024, FlashGS](../feng2024_flashgs/fiche.md) : cités comme accélérations CUDA natives (`page:9`).
  - [Shi 2024, LapisGS](../shi2024_lapisgs/fiche.md) : streaming progressif, complément naturel d'un viewer web.
  - [Kerbl 2023, 3DGS](../kerbl2023_3dgs/fiche.md), [Lee 2023, Compact3D](../lee2023_compact3d/fiche.md) (cité pour la compression).
