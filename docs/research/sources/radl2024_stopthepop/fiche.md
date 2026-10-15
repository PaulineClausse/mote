---
citekey: radl2024_stopthepop
mineru_doc: 94df417
type: article de revue
statut: fiche complète
tags: [3dgs, rasterisation, tri-par-pixel, popping, coherence-de-vue, tile-culling, load-balancing, k-buffer, flip, etude-utilisateur, rendu-temps-reel, vr-motivation, p2-stereo]
---

# StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering

**Référence :** Radl, L.\*, Steiner, M.\*, Parger, M., Weinrauch, A., Kerbl, B., Steinberger, M. (2024). StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering. *ACM Transactions on Graphics* 43(4), art. 64, juillet 2024. DOI [10.1145/3658187](https://doi.org/10.1145/3658187). arXiv [2402.00525](https://arxiv.org/abs/2402.00525) (p. 1). \*contribution égale.
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Code :** https://github.com/r4dl/StopThePop (p. 1, 11)

## En une phrase

Le papier remplace le tri global par profondeur du centre (source du popping en rotation) par un tri **par pixel** approché via une hiérarchie de files triées (tuile 4×4 → 2×2 → pixel) en mémoire partagée et registres, avec culling exact par tuile. Coût : seulement +4 % en moyenne par rapport à 3DGS en Full HD sur RTX 4090. Avec l'« Opacity Decay », il faut ~50 % de Gaussiennes en moins, ce qui donne un rendu 1,6× plus rapide que 3DGS et une cohérence de vue nettement meilleure (p. 1, 9, 11).

## Problème traité

- 3DGS trie les splats selon la profondeur en espace vue du **centre** μ projeté sur l'axe de vue v : t_i = μ_iᵀv. Cet ordre ne dépend pas du rayon (p. 3, éq. 2). Il est donc **stable en translation mais pas en rotation**. Quand la caméra tourne, l'ordre relatif de deux Gaussiennes peut s'inverser le long d'un même rayon, et la couleur saute : c'est le **popping** (Fig. 2, p. 2).
- Les auteurs citent explicitement la VR : ce popping est « very irritating and immersion-breaking, e.g. during head rotation in a virtual reality setting » (p. 2).
- 3DGS « triche » : l'optimisation exploite ce popping pour simuler des effets dépendants de la vue près des vues d'entraînement (Fig. 4 p. 4, Fig. 12 p. 15).
- Un tri complet par rayon supprime le popping mais coûte **> 100×** le temps de rendu de 3DGS (Tab. 1, p. 5).

## Méthode / contributions

**Profondeur par rayon (p. 4, éq. 4 ; annexe A p. 13).** On blende chaque Gaussienne au point de contribution maximale le long du rayon r(t) = o + t·d : t_opt = dᵀΣ⁻¹(μ − o) / (dᵀΣ⁻¹d). Cette profondeur est **indépendante de la rotation de la caméra**, mais dépend de sa **position** o (Fig. 3, p. 3). Stabilité numérique : les entrées de S⁻¹ sont bornées à 10³, ce qui épaissit les Gaussiennes très plates (p. 4). L'approximation 2D EWA (Zwicker 2002) de 3DGS est conservée : seul l'ordre de blending change (p. 5).

**Pipeline complet, comparé à Kerbl 2023 (Fig. 7, p. 6).**

| Étape | 3DGS ([Kerbl 2023](../kerbl2023_3dgs/fiche.md)) | StopThePop |
|---|---|---|
| Borne 2D | Cercle de rayon 3·√λ_max, facteur fixe t_O = 3 | t_O = √(2 log(α/ε_O)), dépend de l'opacité α et est ≤ 3,329. Les auteurs montrent que t_O = 3 était **trop petit** pour ε_O = 1/255 (annexe B.2, p. 13) |
| Tuiles touchées | Toutes les tuiles 16×16 du rectangle englobant | **Culling exact par tuile** : on calcule le point x̂ de la tuile qui maximise G₂ (sur l'un des deux bords les plus proches si μ₂ est hors tuile, Algo. 1 p. 13) et on rejette si G₂(x̂)·α < 1/255. Sur Garden, −44 % de Gaussiennes par tuile (Fig. 6, p. 5) |
| Clé de tri | ID de tuile + profondeur du centre (vue) | ID de tuile + t_opt évalué au rayon passant par x̂ (**profondeur par tuile**, p. 6) |
| Équilibrage de charge | Aucun, un thread par Gaussienne | 2 phases. Un thread seul si la Gaussienne couvre ≤ 32 tuiles, sinon le travail est réparti sur le warp (ballot et shuffle). Preprocess et Duplicate jusqu'à **10× plus rapides** en gros plan et en haute résolution (p. 6 ; annexe B.4 p. 14) |
| Tri global | Radix sort CUB | Inchangé. Un tri partitionné par tuile a été testé (coût de tri divisé par plus de 2), mais les atomiques mangent le gain, donc il n'a pas été retenu (annexe B.3, p. 13) |
| Blending | Parcours front-to-back de la liste de la tuile dans l'ordre global | **Tri hiérarchique dans un seul kernel.** File 4×4 de 64 éléments (16 threads, tri Batcher + fusion), puis 4 files 2×2 de 8 éléments, puis une file par pixel de 4 éléments en registres (tri par insertion). Culling à chaque niveau (t_opt = ∞ si rejeté) ; le blending n'a lieu qu'au débordement de la file pixel. Fenêtre de tri effective de **25 à 72** éléments (p. 6-7) |
| Arrêt précoce | Saturation de α | Conservé : le kernel unique évite de passer par la mémoire globale entre niveaux (p. 6) |
| Backward | Back-to-front, réutilise l'ordre global | **Front-to-back** avec reconstitution par soustraction et division (éq. 6-7). Même routine que le forward, tris stables, pas de stockage des ordres par pixel (p. 7). Entraînement **+3 %** seulement (p. 11) |

- Ordre intermédiaire : un simple resorting par fenêtre (k-buffer sans fusion) de 16 à 24 éléments supprime déjà l'essentiel du popping, mais coûte 2 à 6× plus (Tab. 1, p. 5). La hiérarchie partage l'effort de tri entre rayons voisins (p. 5).
- La profondeur par tuile seule, sans resorting par pixel, crée des artefacts aux bords de tuile (Fig. 5, p. 5).
- **Opacity Decay** (p. 7) : on remplace le reset d'opacité de 3DGS par α ← 0,9995·α toutes les 50 itérations. On obtient environ 2× moins de Gaussiennes, mais plus grandes, ce qui aggrave le popping sous 3DGS.
- **Métrique de popping** (p. 8, annexe C p. 14) : on warpe l'image F_i vers F_{i+t} par flot optique RAFT, puis on calcule FLIP entre l'image warpée et l'image rendue. On masque les occlusions (Ruder 2016), on retire 20 px de bord et on soustrait le minimum par pixel. t = 1 mesure le court terme, t = 7 le long terme ; FLIP₇ est jugé plus fiable. MSE ne détecte pas le popping (Fig. 9, p. 10).

## Résultats chiffrés

Matériel des timings : **NVIDIA RTX 4090 (desktop), CUDA 11.8, rendu Full HD (1080p), mono-vue**, sur une trajectoire interpolée entre toutes les poses COLMAP (30 images par pose), moyenne de 4 exécutions (p. 9, 15). La qualité est mesurée sur 13 scènes : Mip-NeRF360, T&T, Deep Blending (p. 7). La résolution d'évaluation de la qualité n'est pas précisée (on suppose qu'elle suit Kerbl 2023).

| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| Temps de frame moyen | 3DGS **4,797 ms** ; StopThePop **4,986 ms** (+4 %) | Moyenne sur les 13 scènes, ~2,98 M Gaussiennes, 1080p, RTX 4090 (Tab. 5, p. 9) |
| FPS équivalents | ≈ 208 (3DGS) / ≈ 201 (StopThePop), soit 1000/ms, **notre calcul** | Idem, mono-vue |
| Avec Opacity Decay | 3DGS 2,276 ms ; StopThePop **2,976 ms** (≈ 336 fps, notre calcul) ; ~1,54 M Gaussiennes | Tab. 5 p. 9. « 1,6× plus rapide que 3DGS » = 4,797 / 2,976 (p. 1, 11) |
| Décomposition (StopThePop) | Preprocess 0,649 · Duplicate 0,437 · Sort **0,301** · Render **3,599** ms | Contre 3DGS : 0,451 · 0,567 · **1,645** · **2,134** ms (Tab. 5, p. 9) |
| Ratio par scène | 0,76 (Train) à 1,32 (Bonsai) ; moyenne des ratios 1,07 | Tab. 10, p. 16. Plus rapide que 3DGS quand les Gaussiennes sont grandes ou anisotropes (T&T, DB) |
| Pire scène | Garden 7,247 ms, soit ≈ 138 fps (notre calcul) | Tab. 9 p. 16 (3DGS : 6,034 ms) |
| Entrées de tri | Bonsai 4,36 M → 1,72 M ; Train 10,2 M → 2,85 M | Tab. 7, p. 11 |
| Tri complet par pixel | 142× (Train) et 180× (Bonsai) le temps de 3DGS | Tab. 1, p. 5 |
| Qualité PSNR / SSIM / LPIPS / FLIP | DB 29,86 / 0,904 / 0,234 / 0,127 (3DGS : 29,46 / 0,900 / 0,247 / 0,131) | Tab. 2, p. 8 |
| | M360 Indoor 30,62 / 0,921 / 0,186 / 0,099 (3DGS : 30,98 / 0,922 / 0,189 / 0,094) | Tab. 2 |
| | M360 Outdoor 24,60 / 0,728 / 0,235 / 0,167 (3DGS : 24,59 / 0,727 / 0,240 / 0,167) | Tab. 2 |
| | T&T 23,21 / 0,843 / 0,173 / 0,216 (3DGS : 23,71 / 0,845 / 0,178 / 0,199) | Tab. 2. Baisse attribuée à la « triche » de 3DGS (p. 8) |
| Popping FLIP₇ ↓ | DB 0,0114 → **0,0059** ; M360-In 0,0134 → 0,0077 ; M360-Out 0,0148 → 0,0122 ; T&T 0,0286 → **0,0113** | 3DGS → StopThePop, 3 trajectoires par scène (Tab. 3, p. 8). FLIP₁ M360-Out : 0,0083 contre 0,0085, légèrement moins bon |
| Popping, Opacity Decay | FLIP₇ T&T 3DGS 0,0315 contre 0,0114 ; StopThePop quasi inchangé | Tab. 3 |
| Étude utilisateur | 18 participants. StopThePop préféré dans 54,3 % des cas, égalité 33,3 %, 3DGS 12,4 % ; s_mean = 0,42 ; Wilcoxon p < 0,0001 | Vidéos côte à côte **sur écran**, pas en casque (p. 9 ; annexe D p. 15) |
| Erreur de profondeur E_depth | 0,552 → 0,388 en moyenne | Points COLMAP (Tab. 4, p. 9) |
| Temps d'entraînement | +3 % par rapport à 3DGS (valeur absolue non rapportée) | p. 11 |
| Mémoire | −50 % avec Opacity Decay (via le nombre de Gaussiennes) ; en MB : non rapporté | p. 1, 11 |
| Latence / stéréo / casque | **Non rapportés** | — |

## Pertinence pour notre sujet

| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Référence incontournable sur le popping, motivée explicitement par la rotation de tête en VR (p. 2). Code public basé sur le rasteriseur CUDA de 3DGS. Il sert de brique de base à [VRSplat (tu2025)](../tu2025_vrsplat/fiche.md), qui reprend son rasteriseur hiérarchique. |
| 2. Gaussiennes 3D depuis SfM, covariance anisotrope | Change peu la représentation. Trois points utiles : l'entraînement doit se faire **avec le même tri** que le rendu, sinon 3DGS apprend à « tricher » (p. 4, 8) ; Σ⁻¹ est utilisée directement (bornage de S⁻¹) ; l'Opacity Decay remplace le reset d'opacité et divise le nombre de Gaussiennes par 2. |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | **Cœur de l'étape 3.** Il apporte un culling exact par tuile, des bornes 2D dépendantes de l'opacité, un équilibrage de charge par warp et un tri hiérarchique par pixel. On y voit que le coût se déplace du tri global (−82 %) vers le kernel de rendu (+69 %) (Tab. 5). Aucun portage casque ni rendu stéréo. |
| 4. Évaluation (fps, latence, qualité, coût) | **Métrique de popping FLIP_t** réutilisable telle quelle sur des trajectoires de tête réelles, avec protocole d'étude utilisateur et métrique E_depth. Il manque la latence, la mesure par œil et l'évaluation en casque. |

## Pour (vis-à-vis de notre problématique)

- **Rendu Full HD à environ 200 fps mono sur RTX 4090** (Tab. 5), et ≥ 138 fps sur la pire scène (Tab. 9). Il y a une marge large au-dessus de 30 fps à 1080p, même en rendant deux passes stéréo naïves. Hypothèse, non mesurée : environ 70 fps par paire d'yeux sur la pire scène.
- **Supprime l'artefact le plus gênant en VR**, le popping en rotation de tête, pour un coût marginal (+4 %). Le gain est prouvé à la fois par une métrique (FLIP₇ divisé par 2,5 sur T&T) et par une étude utilisateur significative.
- **Robuste à moins de Gaussiennes** : avec l'Opacity Decay, on a deux fois moins de primitives sans hausse du popping, donc moins de mémoire (utile pour un casque autonome) et 1,6× plus de fps.
- Le **tile culling exact et le load balancing** accélèrent sensiblement les cas « grosses Gaussiennes proches » (gros plans, haute résolution, p. 6), typiques de la VR où l'utilisateur s'approche des objets.
- Le surcoût d'entraînement est négligeable (+3 %).

## Contre / limites

- **Aucune évaluation XR** : pas de stéréo, de casque, de latence, ni de GPU mobile. Les mesures sont faites uniquement sur RTX 4090 en CUDA (p. 9). Le kernel repose sur des primitives CUDA de niveau warp (shuffle, ballot, mémoire partagée), dont le portage vers Vulkan ou un GPU mobile de casque est non trivial (hypothèse).
- **Le kernel de rendu devient le goulot** : Render passe de 2,134 à 3,599 ms, soit 72 % du temps de frame (Tab. 5). C'est justement la partie par pixel, donc **par œil**.
- Plus lent que 3DGS sur les scènes à petites Gaussiennes uniformes (M360 Indoor, Bonsai 1,32×, Tab. 10).
- Le **resorting ne garantit pas l'ordre exact** : du popping ou du scintillement reste possible dans des configurations géométriques complexes. Le recouvrement entre Gaussiennes le long du rayon est toujours ignoré (p. 11).
- Qualité légèrement inférieure sur T&T et M360 Indoor (PSNR −0,5 et −0,36 dB, Tab. 2), selon les auteurs parce que la « triche » de 3DGS disparaît.
- Pas d'antialiasing propre : [Mip-Splatting](../yu2023_mip-splatting/fiche.md) est seulement cité (p. 3).
- Le modèle doit être entraîné avec ce renderer : appliquer StopThePop à un modèle entraîné en tri global dégrade le résultat (Fig. 4, p. 4). [VRSplat](../tu2025_vrsplat/fiche.md) le confirme pour Mini-Splatting.

## Idées à creuser pour une approche novatrice

Toutes les pistes ci-dessous sont des **hypothèses**, non testées dans le papier.

- **H1 — P2 (tri stéréo partagé) : ce que dit la décomposition.**
  - Dans StopThePop, le tri global ne représente plus que 0,301 ms sur 4,986 ms, soit **6 %**. Dans 3DGS, il en représente 1,645 sur 4,797, soit **34 %** (Tab. 5, notre calcul). Mutualiser uniquement le tri entre les yeux rapporterait donc peu sur StopThePop.
  - Le vrai coût est le kernel hiérarchique par pixel (72 %). Ses files 4×4, 2×2 et pixel dépendent des rayons de chaque œil, avec o différent, donc elles **ne sont pas partageables telles quelles**.
  - Piste à tester : partager Preprocess (Σ⁻¹, SH évaluées depuis un œil « cyclope ») et la liste triée par tuile, puis laisser à chaque œil sa propre hiérarchie de resorting. Justification : la hiérarchie ne demande qu'un ordre « presque trié » en entrée (principe du k-buffer, p. 3, 5). La fenêtre de 25 à 72 éléments corrigerait la parallaxe inter-oculaire d'environ 6 cm.
  - À mesurer : l'erreur de tri δ (Tab. 1), FLIP₇ par œil et le gain en ms.
- **H2 — Cohérence binoculaire.** t_opt est invariant en rotation et ne dépend que de la position (Fig. 3). Deux yeux décalés par une translation obtiennent chacun un ordre « correct » pour leur position. Avec 3DGS, l'ordre t = (μ − o)·v est identique pour deux yeux à axes parallèles, mais il **diffère si les écrans du casque sont inclinés** (canted displays), ce qui peut produire un popping binoculaire (notre raisonnement). Il faudrait définir une métrique FLIP gauche/droite après reprojection par disparité, sur le modèle de FLIP_t.
- **H3 — Métrique d'évaluation XR.** On pourrait reprendre FLIP₁ et FLIP₇ sur des trajectoires de tête enregistrées en casque (rotations rapides à 90 Hz, à la place des trajectoires interpolées COLMAP). Ce serait une contribution d'évaluation directe pour notre étape 4.
- **H4 — Culling par tuile et fovéation (P1).** Le test exact G₂(x̂)·α < ε_O par tuile pourrait prendre un **seuil ε_O variable selon l'excentricité** (fovéal ou périphérique). La hiérarchie de files pourrait aussi être raccourcie en périphérie (file pixel de 2 au lieu de 4), ce qui réduirait le coût du Render là où le popping se perçoit moins. À comparer à [VR-Splatting (franke2024)](../franke2024_vr-splatting/fiche.md) et [A3FR (xin2025)](../xin2025_a3fr-foveated/fiche.md).
- **H5 — Opacity Decay et budget (P3).** L'Opacity Decay divise N par 2 sans hausse du popping. On pourrait le combiner avec un élagage plus agressif ([Speedy-Splat](../hanson2024_speedy-splat/fiche.md), jusqu'à 10×) et vérifier si la cohérence tient encore. Cela fournirait un axe « budget de Gaussiennes » pour P3.

## Citations clés

> « Such view inconsistencies due to popping can be very irritating and immersion-breaking, e.g. during head rotation in a virtual reality setting. » (`doc:94df417/tier:standard/page:2/block:6`)

> « Our results indicate that a full per-pixel sorted renderer for Gaussian splats eliminates all popping artifacts but reduces rendering speed by 100×. Our hierarchical renderer is virtually indistinguishable from a full per-pixel sorted renderer, but only adds an overhead of 4% compared to the original 3DGS. » (`doc:94df417/tier:standard/page:2/block:13`)

> « Our pipeline achieves an overall sorting window of 25-72 elements. » (`doc:94df417/tier:standard/page:6`, légende Fig. 7)

> « All timings were measured for Full HD rendering and averaged over 4 runs, where we used an NVIDIA RTX 4090 with CUDA 11.8. » (`doc:94df417/tier:standard/page:9/block:15`)

> « our approach can reduce memory by 2× and render times by 1.6× compared to 3DGS in this configuration, while reducing popping artifacts » (`doc:94df417/tier:standard/page:11/block:13`)

> « resorting does not guarantee the right blend order, and thus could still lead to popping or flickering for very complex geometric relationships » (`doc:94df417/tier:standard/page:11/block:14`)

## Liens

- **Papiers liés :**
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) : rasteriseur de référence modifié ici. La section « Popping » de sa fiche (guard band, tri par tuile) est exactement le problème que StopThePop résout pour la partie tri.
  - [tu2025_vrsplat](../tu2025_vrsplat/fiche.md) : mêmes auteurs en partie (Radl, Steiner, Steinberger, Kerbl). VRSplat reprend le rasteriseur hiérarchique de StopThePop, y ajoute Mini-Splatting et Optimal Projection, et note que StopThePop « introduces significant overhead » dans un contexte VR. C'est la suite directe côté casque.
  - [hanson2024_speedy-splat](../hanson2024_speedy-splat/fiche.md) : il compare son AccuTile au tile-based culling de StopThePop (2,038× contre 1,841× d'accélération, Tab. 7 de Speedy-Splat).
  - [feng2024_flashgs](../feng2024_flashgs/fiche.md) : intersection précise Gaussienne-tuile similaire, d'après Speedy-Splat (p. 2 de celui-ci).
  - [franke2024_vr-splatting](../franke2024_vr-splatting/fiche.md) et [xin2025_a3fr-foveated](../xin2025_a3fr-foveated/fiche.md) : fovéation (H4).
  - [yu2023_mip-splatting](../yu2023_mip-splatting/fiche.md) : antialiasing, orthogonal et combinable.
  - [mallick2024_taming-3dgs](../mallick2024_taming-3dgs/fiche.md) : même équipe (Kerbl, Steinberger), budget de Gaussiennes.
