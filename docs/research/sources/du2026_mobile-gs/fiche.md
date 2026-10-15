---
citekey: du2026_mobile-gs
mineru_doc: f696f61
type: conférence   # ICLR 2026 (arXiv 2603.11531)
statut: fiche complète
tags: [3dgs, mobile, snapdragon-8-gen-3, vulkan, sans-tri, order-independent, compression, quantification-vectorielle, distillation-sh, élagage, mlp, énergie, throttling-thermique]
---

# Mobile-GS: Real-time Gaussian Splatting for Mobile Devices

**Référence :** Xiaobiao Du (UTS), Yida Wang (Li Auto), Kun Zhan (Li Auto), Xin Yu (Adelaide University) (2026). *Mobile-GS: Real-time Gaussian Splatting for Mobile Devices.* Published as a conference paper at **ICLR 2026**. arXiv [2603.11531](https://arxiv.org/abs/2603.11531) · projet : xiaobiaodu.github.io/mobile-gs-project (`doc:f696f61/tier:standard/page:1`)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Pour tenir sur GPU de smartphone, Mobile-GS **supprime le tri** (et le rasteriseur à tuiles) au profit d'un **mélange order-independent pondéré par la profondeur et l'échelle**, compense les artefacts de transparence par un **petit MLP d'opacité dépendante de la vue**, et compresse le modèle (SH d'ordre 1 distillées, quantification vectorielle neuronale + Huffman, élagage opacité×échelle) : **127 FPS « à froid » / 74 FPS en régime thermique stable, 4,6 Mo, 0,83 W**, mesurés sur un **vrai téléphone Snapdragon 8 Gen 3** (Vulkan), en **mono** et à résolution ~1600×1063 (Mip-NeRF 360) (`page:1`, `page:8`, `page:19`).

## Problème traité
- Sur mobile, le coût du 3DGS vient surtout du **tri** (Fig. 2 : 3,1–4,9 ms de tri sur ~7–11 ms par frame ; sans tri, 3DGS passe par ex. de 134 à 857 FPS sur Bicycle — plateforme de la Fig. 2 non précisée, probablement desktop) et du stockage (centaines de Mo) (`page:2`).
- Les méthodes légères (Scaffold-GS, Mini-Splatting, C3DGS…) gardent le mélange alpha trié ; les méthodes sans tri existantes (SortFreeGS, GES) restent trop lourdes en stockage/latence pour l'embarqué (`page:2–3`).

## Méthode / contributions — ce qui est changé
| Brique | Changement | Réf. |
|---|---|---|
| **Tri / compositing** | **Suppression du tri et du rendu à tuiles** : chaque Gaussienne calcule sa contribution aux pixels couverts en parallèle, accumulées par sommes commutatives ; C = (1−T)·Σcᵢαᵢwᵢ / Σαᵢwᵢ + T·c_bg, avec T = Π(1−αⱼ) (transmittance globale, aussi indépendante de l'ordre) | `page:4`, Eq. 2, Fig. 3 |
| Poids | wᵢ = φᵢ² + φᵢ/dᵢ² + exp(s_max/dᵢ) : favorise les Gaussiennes **proches et grandes** ; φᵢ prédit par MLP | `page:5`, Eq. 3 |
| **Opacité dépendante de la vue** | MLP 3 couches (256-128-64) prenant direction caméra→Gaussienne, échelle, rotation, SH → opacité oᵢ et φᵢ ; corrige la « transparence » des surfaces occultées | `page:5`, `page:15` |
| **Représentation couleur** | Distillation SH ordre 3 → **ordre 1** (3×4 coeffs) depuis un professeur **Mini-Splatting**, + perte de profondeur invariante d'échelle | `page:6` |
| **Compression** | Quantification vectorielle par sous-vecteurs (5 groupes, K-means, codebook 2¹⁰) + Huffman ; SH factorisées en diffus/vue-dépendant décodées par 2 MLP 16 bits (une seule fois à l'inférence) | `page:6`, `page:15` |
| **Élagage** | Votes cumulés sur candidats à faible opacité **et** faible échelle (quantile τ = 0,2, intervalle 1000 it., seuil 0,6, seulement pendant les 25K premières it.) → 0,56 M → 0,47 M Gaussiennes | `page:6–7`, `page:10`, `page:15` |
| **Shader / déploiement** | Implémentation **Vulkan** (« Vulkan 2.0 » écrit dans le texte) sur mobile ; entraînement CUDA/PyTorch sur RTX 3090, 60K it., multi-view training (MVGS) | `page:7` |

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| **Appareil** | « mobile device equipped with the **Snapdragon 8 Gen 3** GPU » — modèle de téléphone **non nommé** ; **mesure réelle** | `page:1`, `page:8` |
| Résolution | **1600 × 1063** (Bicycle, Fig. 1) ; résolution du Tableau 2 non explicitée (Mip-NeRF 360, PSNR identique) | `page:1` |
| FPS mobile (à froid) | **127 FPS** moyen Mip-NeRF 360 ; 116 FPS sur Bicycle ; vs 3DGS* 8, Mini-Splatting* 12, Speedy-Splat 19, LocoGS-S 17, SortFreeGS* 24 | **mono** (`page:1`, `page:8`, Table 2) |
| FPS mobile (régime stable) | **74 FPS** après équilibre thermique (3DGS 3, Speedy-Splat 10, SortFreeGS 18) | `page:19`, Table 12 |
| Puissance | **0,83 W** (préproc 0,17 + MLP 0,24 + raster 0,42) vs 3DGS* 5,89 W (dont tri 2,09 W) et SortFreeGS* 4,03 W | Qualcomm Trepn Profiler, opérateurs Vulkan, Mip-NeRF 360 (`page:19`, Table 13) |
| Qualité (desktop) | Mip-360 **27,12 / 0,807 / 0,235** ; T&T 23,09 / 0,831 / 0,208 ; DB **29,93 / 0,906 / 0,243** (3DGS : 27,21/0,815/0,214 ; 23,14/0,841/0,183 ; 29,41/0,903/0,243) | PSNR/SSIM/LPIPS (`page:8`, Table 1) |
| Qualité (mobile) | PSNR 27,12 (Mip-360) | Table 2 (`page:8`) |
| FPS desktop | **1125 / 1179 / 1132 FPS** (Mip-360 / T&T / DB) ; « 1098 FPS » en Fig. 1 | RTX 3090 (Table 3) ou « RTX 3090 Ti » (Fig. 1) — incohérence du texte (`page:1`, `page:8`) |
| Temps de frame (décomposition) | ~0,9–1,05 ms : MLP 0,23–0,25 · préproc 0,14–0,27 · raster 0,51–0,62 ms (Fig. 6, plateforme non précisée, vraisemblablement desktop) | `page:9` |
| Stockage | **4,6 Mo** (Mip-360), 2,5 Mo (T&T), 4,6 Mo (DB) vs 3DGS 839,9 / 371,5 / 697,3 Mo | `page:8` |
| Nb de Gaussiennes | 0,47 M (Mip-360, τ = 0,2) ; 0,34 M → 141 FPS mobile et 26,47 dB (τ = 0,4) ; 0,18 M → 164 FPS, 25,85 dB (τ = 0,6) | `page:10`, Tables 4–5 |
| Entraînement | **1,5 h** (vs 3DGS* 0,5 h, Mini-Splatting* 0,4 h) sur RTX 3090 ; nécessite un professeur pré-entraîné | `page:7`, `page:8` |
| Ablation sans tri | Avec alpha-blending trié : 27,26 dB mais 684 FPS (vs 1125) ; sans MLP vue-dépendant : 26,68 dB (−0,44) | desktop (`page:8`, Table 3) |
| Latence | **Non rapportée** (hors temps de frame desktop) | — |
| Mémoire GPU à l'exécution | Non rapportée (seulement stockage) | — |
| Étude utilisateurs | 30 volontaires, vidéos, préférence pour Mobile-GS vs 3DGS quantifié et LocoGS-S (valeurs seulement en figure) | `page:18` |

## Stéréo / VR
- Les **casques AR** sont cités comme cible dans l'introduction (`page:2`), mais **aucune évaluation stéréo, casque ou XR** ; tout est mono sur téléphone.
- Pas de discussion du popping ; le rendu sans tri l'élimine structurellement (pas d'ordre qui « saute ») mais introduit une erreur de composition indépendante de la vue qui n'est pas mesurée en VR (hypothèse).
- Stéréo (P2) : sans tri, il n'y a plus de tri à mutualiser ; ce qui resterait partageable entre yeux = décodage des attributs (fait une seule fois), culling, et éventuellement le MLP d'opacité (qui dépend de la direction caméra→Gaussienne, donc différent par œil mais quasi identique pour les Gaussiennes lointaines) (hypothèse).

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | **Seule référence de la base mesurant 3DGS sur un vrai SoC mobile Qualcomm** avec FPS à chaud et puissance — proche de la classe matérielle d'un casque autonome (Quest 3 = XR2 Gen 2, *hors papier, à vérifier*). Vulkan comme API de déploiement |
| 2. Gaussiennes 3D depuis SfM, covariance | Distillation depuis Mini-Splatting, élagage opacité×échelle, SH ordre 1 : recette de modèle léger |
| 3. Rendu rapide, visibilité, casque XR | Rendu **sans tri** + MLP d'opacité : alternative radicale au tri (StopThePop) ; supprime aussi le rasteriseur à tuiles |
| 4. Évaluation | Bonne pratique à reprendre : **FPS à froid vs régime thermique stable** et puissance par opérateur (Trepn) |

## Pour (vis-à-vis de notre problématique)
- Mesures **réelles sur mobile**, y compris après **throttling thermique** (74 FPS stables) — le chiffre le plus honnête de notre corpus pour de l'embarqué (`page:19`).
- Qualité ≈ 3DGS (−0,09 dB Mip-360, +0,52 dB DB) avec **4,6 Mo** et **0,83 W** : compatible avec la mémoire et le budget thermique d'un casque autonome (`page:8`, `page:19`).
- Supprimer le tri supprime aussi la source du popping et le goulot bande passante identifié par [Neo](../oh2025_neo-on-device/fiche.md).

## Contre / limites
- **Mono, ~1,7 Mpx** : une stéréo Quest 3 native (2 × 2064×2208 ≈ 9,1 Mpx) représente ~5,4× plus de pixels ; même 1080p par œil ≈ 2,4× plus (calcul personnel). La rasterisation représente la moitié ou plus du temps de frame (Fig. 6) → extrapolation grossière (hypothèse) : ~30 FPS stables en stéréo 1080p/œil, ~15 FPS en natif Quest 3, **sous 72 Hz**.
- Le SoC évalué (Snapdragon 8 Gen 3, téléphone) n'est pas celui d'un casque ; aucune mesure sur XR2.
- Rendu **approximatif** (pas de vraie composition avant-arrière) : artefacts de transparence sur géométrie superposée, atténués mais pas supprimés par le MLP (`page:5`, `page:9`) ; non évalué en grand FOV ni en stéréo (incohérences inter-yeux possibles).
- **Entraînement 1,5 h** + professeur Mini-Splatting + desktop obligatoire ; pas de généralisation inter-scènes (`page:17`).
- Incohérences de rapport : GPU desktop « 3090 Ti » vs « 3090 » ; SortFreeGS* 24 FPS (Table 2) vs 18 FPS (Table 8), GES 18 vs 24 (`page:8`, `page:16`) ; résolution mobile hors Fig. 1 non donnée ; code « publié à l'acceptation ».

## Idées à creuser pour une approche novatrice
- *Hypothèse* : **Mobile-GS stéréo sur Quest 3** (Vulkan/OpenXR natif) — mesurer FPS à froid/à chaud et puissance, en rendant les deux yeux en une passe (multiview) ; c'est un test de faisabilité direct de notre étape 3 sans ASIC.
- *Hypothèse (P2)* : en rendu sans tri, les sommes Σcαw et Σαw sont additives → pour le contenu lointain (disparité < 1 px), une même accumulation pourrait être **décalée** vers l'autre œil ; seul le proche serait recomposé par œil.
- *Hypothèse (P1)* : hybride « proche trié (casque, StopThePop) / lointain sans tri (moins sensible aux erreurs d'ordre) », ou l'inverse selon qui porte le coût — le sans-tri est justement le plus faux là où les surfaces se superposent en profondeur (proche).
- *Hypothèse (P3)* : le seuil d'élagage τ offre un bouton continu qualité↔FPS mesuré (τ 0,2→0,6 : 127→164 FPS, 27,12→25,85 dB) ; utilisable comme variable de décision d'un modèle QoS/QoE.
- *Hypothèse* : vérifier la **cohérence stéréo** du MLP d'opacité vue-dépendant (deux directions de vue par Gaussienne) — risque de « rivalité binoculaire » si les opacités divergent entre yeux.

## Citations clés
> « we first identify alpha blending as the primary computational bottleneck, since it relies on the time-consuming Gaussian depth sorting process » (`doc:f696f61/tier:standard/page:1`)

> « our proposed method eliminates the tile-based rendering and the 3D Gaussian sorting process typically required for accurate alpha blending » (`doc:f696f61/tier:standard/page:4`)

> « objects that are spatially occluded or partially overlapped may exhibit undesired transparency effects » (`doc:f696f61/tier:standard/page:5`)

> « our Mobile-GS can still achieve 74 Steady-state FPS » (`doc:f696f61/tier:standard/page:19`)

## Liens
- Papiers liés :
  - [Oh 2025, Neo](../oh2025_neo-on-device/fiche.md) : même diagnostic (le tri est le goulot embarqué) mais solution inverse (amortir le tri par réutilisation temporelle, ASIC simulé).
  - [Han 2026, WebSplatter](../han2026_websplatter/fiche.md) : même SoC (Snapdragon 8 Gen 3, Redmi K70 Pro) en navigateur, 3DGS classique trié : ~30 FPS sur 1 M splats → ordre de grandeur de comparaison.
  - [Fan 2023, LightGaussian](../fan2023_lightgaussian/fiche.md) (distillation SH, baseline), [Lee 2023, Compact3D](../lee2023_compact3d/fiche.md) (baseline « C3DGS (Lee et al., 2024) »), [Hanson 2024, Speedy-Splat](../hanson2024_speedy-splat/fiche.md) (baseline, 19 FPS mobile).
  - [Radl 2024, StopThePop](../radl2024_stopthepop/fiche.md) : cité pour le popping du tri ; philosophie opposée (trier mieux vs ne plus trier).
  - [Tu 2025, VRSplat](../tu2025_vrsplat/fiche.md) : aussi basé sur Mini-Splatting, mais tout sur RTX 4090.
  - [Kerbl 2023, 3DGS](../kerbl2023_3dgs/fiche.md).
