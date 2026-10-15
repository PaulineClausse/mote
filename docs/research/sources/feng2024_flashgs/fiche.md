---
citekey: feng2024_flashgs
mineru_doc: 172ea4d
type: conférence   # prépublication arXiv ; l'en-tête « Conference'17 » est un gabarit, venue non indiquée
statut: fiche complète
tags: [3dgs, rasterisation, cuda, optimisation-gpu, intersection-tuile, haute-resolution, grandes-scenes, 4k, temps-reel, sans-perte-qualite]
---

# FlashGS: Efficient 3D Gaussian Splatting for Large-scale and High-resolution Rendering

**Référence :** Feng, G.†, Chen, S.†, Fu, R.\*, Liao, Z., Wang, Y., Liu, T., Pei, Z., Li, H., Zhang, X., Dai, B. (2024). FlashGS: Efficient 3D Gaussian Splatting for Large-scale and High-resolution Rendering. Prépublication arXiv [2408.07967](https://arxiv.org/abs/2408.07967) (v2, 19 août 2024), Shanghai AI Laboratory. Venue non indiquée : l'en-tête « Conference'17, July 2017, Washington, DC » est un gabarit ACM (p. 1).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Code :** https://github.com/InternLandMark/FlashGS (bibliothèque CUDA appelable depuis Python, p. 1, 11)

## En une phrase

Réécriture du rasteriseur 3DGS, **sans changer le modèle ni la qualité** : rayon effectif tenant compte de l'opacité, test d'intersection exact ellipse/tuile, fusion preprocess+duplicate, ordonnancement adaptatif par warp, préchargement à deux niveaux, optimisations mémoire et assembleur. Résultat sur **RTX 3090** : 7,2× en moyenne sur 11 configurations, jusqu'à 30,53×, et > 100 fps même en 4K ou sur Rubble 4608×3456 (p. 11).

## Problème traité

- En grande scène ou en haute résolution, le nombre et la taille des Gaussiennes augmentent, et 3DGS perd le temps réel sur un GPU grand public (p. 1).
- La compression et le pruning (LightGaussian, EAGLES, Scaffold-GS) réduisent la mémoire sans gain de vitesse significatif (p. 1, 3). GScore propose un accélérateur matériel dédié, conçu pour les GPU mobiles (p. 1, 3).
- Profil de 3DGS sur MatrixCity (A100/V100) : renderCUDA ≈ 60 % du temps, SortPairs + DuplicateWithKeys ≈ 20 %, preprocess < 10 % (Fig. 3, p. 4).
- **Observation 1 : redondance géométrique** (Fig. 4-5, p. 4-5). Trois causes :
  - (I) le rayon « 3σ » ignore l'opacité, alors que 65,1 % des Gaussiennes de MatrixCity-smallcity ont une opacité centrale < 0,35 (Fig. 6) ;
  - (II) la boîte englobante est le carré du cercle de rayon égal au demi-grand axe, donc surestimée pour les ellipses aplaties ;
  - (III) toutes les tuiles de la boîte sont assignées, même celles que l'ellipse ne touche pas.
- **Observation 2 : déséquilibre calcul/mémoire.** Preprocess et duplicate sont limités par la bande passante, le rendu par le calcul, d'où une sous-utilisation du GPU (p. 5).

## Méthode / contributions

### Ce qui change par rapport au rasteriseur de Kerbl 2023 ([fiche](../kerbl2023_3dgs/fiche.md))

La structure (tuiles, clés tuile+profondeur, tri radix CUB, blending front-to-back avec arrêt précoce) est conservée. Les changements portent sur la **quantité de paires Gaussienne-tuile** et sur l'**implémentation GPU** :

| Étape | 3DGS 2023 | FlashGS |
|---|---|---|
| Rayon du splat | r = 3√λ_max (p. 6, éq. 1) | r = √(2 ln(α₀/τ) λ) avec τ = 1/255 (éq. 2-3), utilisé quand α₀ ≤ 0,35, sinon 3σ (p. 6) |
| Boîte englobante | carré tangent au cercle englobant | **rectangle tangent à l'ellipse** (p. 7) |
| Assignation aux tuiles | toutes les tuiles de la boîte | **test exact ellipse/rectangle** (Algo. 3) : centre dans la tuile, ou l'intersection ellipse/droite de chaque bord recouvre ce bord (Fig. 9, p. 7) |
| Coût du test | — | forme algébrique sans division ni racine : (e₁ ≤ 0 ‖ e₁² ≤ Δ) && (e₂ ≥ 0 ‖ e₂² ≤ Δ) (éq. 7, p. 9) |
| Kernels | preprocessCUDA puis duplicateWithKeys séparés | **fusionnés** : l'intersection exacte (calcul) est entrelacée avec les écritures globales (mémoire) (p. 8, Algo. 4) |
| Ordonnancement | 1 thread par Gaussienne | **adaptatif** : 1 thread si une seule tuile, sinon un warp coopère, l'ellipse dépassant rarement 32 tuiles (p. 9, Fig. 11) |
| Filtrage | test par pixel de l'opacité dans le rendu | test d'opacité (> 1/255) et de near plane (z > 0,2) **déplacés dans le preprocess**, ce qui réduit la divergence de warp (p. 8, 10) |
| Rendu (renderCUDA) | chargements globaux dépendants (index puis attributs) | **préchargement logiciel à 2 niveaux** : index à i+2, attributs à i+1, calcul à i (Fig. 12, p. 10) ; lots de tâches par thread pour exposer la CSE (p. 10) |
| Mémoire | allocations dynamiques, paramètres en mémoire globale | matrices en **mémoire constante** (passage de grands paramètres, CUDA 12.1 ; ≈ 5 contre ≈ 500 cycles), **allocation statique** faite à l'avance (p. 10) |
| Instructions | exp naïf | exponentielle réécrite en log/FMA, base 2 avec `ex2.approx.ftz.f32` (SFU) (p. 10) |

- Le tri radix n'est pas modifié. Il accélère parce qu'il y a beaucoup moins de paires à trier (p. 11-12).
- **Rendu seul.** Le résumé parle de rasterisation différentiable (p. 1), mais seules les performances de rendu (forward) sont évaluées ; l'entraînement et la passe backward ne sont pas mesurés (non rapporté).

## Résultats chiffrés

Matériel : **RTX 3090** (desktop, 24 GB GDDR6X) pour la plupart des tests ; **A100 80 GB** pour la sensibilité et la mémoire (p. 10, 13). Modèles 3DGS entraînés 30K itérations (p. 11). Les temps sont des temps de **rasterisation par image, mono-vue**. Le tableau 1 annonce des « corresponding FPS » mais ne donne que des ms ; les fps ci-dessous sont **calculés par nous** (1000/ms). La définition exacte de « 4k » n'est pas donnée (non rapporté).

| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| Temps moyen 1080p, FlashGS / 3DGS (ms) | Truck 2,22 / 8,21 ; Train 1,93 / 7,82 ; Playroom 1,44 / 6,83 ; DrJohnson 1,63 / 9,11 ; MatrixCity 3,22 / 20,90 | RTX 3090 (Tab. 1, p. 11) |
| → fps moyens 1080p (calcul) | FlashGS ≈ 311-694 ; 3DGS ≈ 48-146 | idem |
| Accélération moyenne 1080p | 3,76 / 4,20 / 4,92 / 6,18 / 6,56× (min 2,19×, max 14,99×) | idem |
| Temps moyen 4K, FlashGS / 3DGS (ms) | Truck 3,46 / 24,19 ; Train 3,32 / 12,82 ; Playroom 2,72 / 10,74 ; DrJohnson 2,99 / 28,74 ; MatrixCity 4,90 / 66,55 | RTX 3090 (Tab. 1) |
| → fps moyens 4K (calcul) | FlashGS ≈ 204-368 ; 3DGS ≈ 15-93 | idem |
| Accélération moyenne 4K | 7,01 / 7,48 / 7,86 / 9,99 / 13,64× (max 30,53× sur MatrixCity) | idem |
| Pire image (ms, FlashGS / 3DGS) | 1080p : max 4,95 / 40,74 ; 4K : max 7,25 / 140,52 (MatrixCity) | idem |
| Rubble 4608×3456 | 6,19 / 44,11 ms en moyenne (7,41×) ; pire image 9,32 ms, soit **107,3 fps** | RTX 3090 (Tab. 1, p. 11) |
| Synthèse des auteurs | 7,2× en moyenne sur les 11 configurations ; 8,6× sur les 7 cas grands ou haute résolution ; 2,29× à 30,53× selon l'image ; « always > 100FPS » | p. 11 |
| A100 | 1,43× plus lent que la 3090 (FP32 19,5 contre 35,6 TFLOPS) ; 123,8-423,7 fps en moyenne (2,36-8,08 ms) | p. 12 ; Tab. 1 |
| Répartition du temps | FlashGS : preprocess 19,6 %, tri 29,1 %, rendu 47,6 % ; 3DGS : 13,2 / 25,4 / 59,6 % | 6 images représentatives (Fig. 13, p. 11) |
| Paires tuile-Gaussienne rendues | −68 % à −96 % ; instructions par tuile −67 % à −71 % ; accès mémoire globale en preprocess −43 % à −87 % | Fig. 14-15, p. 12 |
| Qualité | PSNR **31,52** identique à 3DGS (accélération 8,57×) | MatrixCity 1080p, image 800 (p. 12) ; aucun pruning ni quantification |
| Mémoire | 6,83 GB (statique) contre 13,45 GB pour 3DGS après rendu, soit −49,2 % ; gsplat 9,83-10,75 GB | MatrixCity image 800, A100 (Tab. 2, p. 13) |
| Paires clé-valeur | 3 436 142 contre 56 148 670 (3DGS) | idem |
| Comparaison à GScore | 3,87× le gain revendiqué par GScore (1,86×, qui n'est pas testé directement) | p. 11 |
| Entraînement | non concerné (modèles 3DGS standard, 30K itérations) ; durée non rapportée | — |
| Latence, stéréo, casque, GPU mobile | non rapportés | — |

**Incohérences internes à signaler :**
- Le résumé annonce « 4x acceleration over mobile consumer GPUs » (p. 1), mais les tests sont faits sur RTX 3090 et A100 et la moyenne du corps du texte est de 7,2× (p. 11).
- Le texte donne « 12,18× » en moyenne pour MatrixCity-4K, contre 13,64 dans le tableau 1 (p. 11).
- La section 6.5 renvoie à un « Table 2 » qui correspond en fait au tableau 1 (p. 12).

## Pertinence pour notre sujet

| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Bibliothèque CUDA/Python open source, point de départ possible pour un moteur de rendu desktop ou edge. CUDA seulement : pas de Vulkan/OpenXR ni de GPU mobile. |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | Aucun apport (modèle 3DGS inchangé). Montre toutefois que les Gaussiennes **peu opaques et aplaties** sont celles qui coûtent le plus cher au rendu (p. 4-5). |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | **Cœur du papier.** L'intersection exacte ellipse/tuile tient compte de l'anisotropie du splat, sans perte de qualité. Le gain augmente avec la résolution (p. 12), ce qui est favorable aux résolutions casque. |
| 4. Évaluation (fps, latence, qualité, coût) | Protocole utile : temps moyen **et pire image** par dataset et par résolution, profils d'instructions et de mémoire. Il manque la latence, le rendu stéréo et l'énergie. |

## Pour (vis-à-vis de notre problématique)

- **1080p largement dépassé.** 1,44-3,22 ms en moyenne, soit ≈ 311-694 fps (calcul), et 4,95 ms au pire, soit ≈ 200 fps, sur RTX 3090 (Tab. 1). Notre cible ≥ 30 fps en 1080p est dépassée d'un ordre de grandeur sur GPU desktop.
- **Résolution casque (hypothèse de calcul, non mesurée).** 2 × 2064×2208 ≈ 9,1 Mpx par image, à peu près le nombre de pixels d'une 4K UHD (8,3 Mpx, si « 4k » = 3840×2160). En 4K, FlashGS tient 2,72-4,90 ms en moyenne et 7,25 ms au pire (Tab. 1). Deux vues de 4,56 Mpx chacune tiendraient donc a priori dans 90 Hz (11,1 ms) sur une 3090, en mono-GPU et sans mutualisation. 3DGS d'origine, lui, n'y arrive pas sur MatrixCity (66,55 ms en 4K).
- **Gain croissant avec la résolution et la taille de scène** (7-13,6× en 4K contre 3,8-6,6× en 1080p) : c'est exactement le régime XR (p. 12).
- **Aucune perte de qualité** (PSNR identique) et **aucun réentraînement** : c'est une accélération « gratuite » du rendu, cumulable a priori avec la compression ou le LOD (hypothèse).
- **Pire image maîtrisée** (max 9,32 ms sur Rubble) et **mémoire statique et prévisible** (6,83 GB, −49 %) : c'est utile pour garantir une fréquence d'image stable (QoS).
- **Décomposition preprocess/tri/rendu fournie** (Fig. 13). Elle permet de chiffrer ce qu'une mutualisation stéréo (P2) pourrait économiser (voir Idées).

## Contre / limites

- **Aucune évaluation XR.** Rendu mono, pas de stéréo, pas de latence motion-to-photon, pas de casque. Les fps sont implicites (ms seulement).
- **GPU desktop et data-center uniquement** (RTX 3090, A100), code CUDA. L'extrapolation vers un GPU de casque autonome (Adreno, Mali, API Vulkan) n'est pas faite ; les optimisations PTX, SFU et mémoire constante sont spécifiques à NVIDIA.
- **Qualité vérifiée sur une seule image** (PSNR MatrixCity image 800, p. 12). Il n'y a ni SSIM ni LPIPS, ni évaluation sur les autres scènes. L'argument « il n'enlève que des faux positifs » est plausible, mais la troncature à α = 1/255 (éq. 3) supprime aussi de vraies contributions faibles, en principe déjà ignorées par 3DGS (p. 14 de Kerbl 2023).
- **Pas de nouveauté sur le tri** : le tri global par tuile est conservé. Le popping dû au tri reste présent (voir [radl2024_stopthepop](../radl2024_stopthepop/fiche.md)).
- Le **gain est faible en petite scène simple** : si chaque Gaussienne ne touche qu'une tuile, l'intersection exacte n'apporte rien (p. 12).
- **Incohérences de rédaction** (4× contre 7,2×, 12,18 contre 13,64, renvoi de tableau erroné) et venue non identifiée : c'est une prépublication, pas un article revu par les pairs à notre connaissance.
- Le rendu 3DGS entraîné reste coûteux en mémoire (6,83 GB sur MatrixCity), hors de portée d'un casque autonome.

## Idées à creuser pour une approche novatrice

Toutes ces pistes sont des **hypothèses**, non testées dans le papier.

- **H1 — Intersection exacte stéréo (P2).** Le preprocess (19,6 %) et le tri (29,1 %) représentent ≈ 49 % du temps FlashGS (Fig. 13). On calculerait une fois pour les deux yeux la projection, le rayon et les SH (vue cyclope), puis l'intersection exacte par œil sur une grille de tuiles commune ou décalée. Le gain de P2 serait **borné par ces ≈ 49 %**. À mesurer contre deux passes FlashGS indépendantes.
- **H2 — FlashGS + coupe LOD** ([kerbl2024_hierarchical-3dgs](../kerbl2024_hierarchical-3dgs/fiche.md)). Les nœuds internes fusionnés sont grands, anisotropes et à falloff élevée, donc probablement les plus redondants en AABB. L'intersection exacte devrait y gagner davantage, ce qui compenserait le surcoût du LOD (weights 1,5-4 ms). À vérifier.
- **H3 — Budget QoS au pire cas (P3).** On utiliserait le nombre de paires tuile-Gaussienne après intersection exacte, plutôt que le nombre de Gaussiennes, comme variable de coût dans le modèle d'optimisation. Il est plus directement proportionnel au temps de tri et de rendu (p. 6).
- **H4 — Portage des principes sur GPU mobile.** Rayon dépendant de l'opacité, rectangle serré et test exact sont indépendants de CUDA. On les porterait en compute shader Vulkan sur un casque autonome pour mesurer le gain, en comparaison avec [tu2025_vrsplat](../tu2025_vrsplat/fiche.md) et [oh2025_neo-on-device](../oh2025_neo-on-device/fiche.md).
- **H5 — Côté edge (P1).** Un serveur edge équipé d'une RTX de classe 3090 et de FlashGS rendrait la périphérie ou les couches lointaines en 4K à > 200 fps (calcul), ce qui libère du budget pour plusieurs utilisateurs. À coupler au streaming.

## Citations clés

> « The empirical findings demonstrate that FlashGS consistently achieves an average 4x acceleration over mobile consumer GPUs, coupled with reduced memory consumption. » (`doc:172ea4d/tier:standard/page:1/block:7`)

> « As shown in Figure 8, the precise intersection algorithm can reduce the number of Gaussians involved in subsequent computations » (`doc:172ea4d/tier:standard/page:6/block:7`)

> « We can always achieve > 100FPS rendering on RTX 3090, even for high-resolution and large-scale datasets. In the slowest frame in Rubble of all datasets, we achieve 107.3 FPS. » (`doc:172ea4d/tier:standard/page:11/block:7`)

> « The result shows that FlashGS does not change the quality, keeping 31.52 PSNR with 8.57× speedup. » (`doc:172ea4d/tier:standard/page:12/block:13`)

> « FlashGS allocates less memory than 3DGS and gsplat, up to 49.2% reduction. » (`doc:172ea4d/tier:standard/page:13/block:9`)

## Liens

- **Papiers liés :**
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) : rasteriseur de référence, dont FlashGS garde la structure et élimine les paires redondantes.
  - [kerbl2024_hierarchical-3dgs](../kerbl2024_hierarchical-3dgs/fiche.md) : LOD orthogonal, combinable a priori (H2).
  - [hanson2024_speedy-splat](../hanson2024_speedy-splat/fiche.md), [mallick2024_taming-3dgs](../mallick2024_taming-3dgs/fiche.md) : autres travaux d'accélération ou de réduction du rasteriseur, à comparer (intersection précise et pruning).
  - [fan2023_lightgaussian](../fan2023_lightgaussian/fiche.md), [lee2023_compact3d](../lee2023_compact3d/fiche.md) : compression, que FlashGS juge peu efficace pour la vitesse (p. 1, 3). Approches complémentaires.
  - [radl2024_stopthepop](../radl2024_stopthepop/fiche.md) : tri et popping, non traités ici.
  - [tu2025_vrsplat](../tu2025_vrsplat/fiche.md), [franke2024_vr-splatting](../franke2024_vr-splatting/fiche.md) : rendu 3DGS en VR, pour vérifier la transposition stéréo et casque.
- **Travaux cités à suivre :** GScore (Lee et al., ASPLOS 2024, accélérateur matériel pour GPU mobile), gsplat (Ye & Kanazawa 2023), DISTWAR (Durvasula 2023), MatrixCity (Li 2023), Grendel (Zhao 2024, entraînement multi-GPU).
