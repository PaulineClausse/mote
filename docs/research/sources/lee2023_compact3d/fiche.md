---
citekey: lee2023_compact3d
mineru_doc: c7b9e5b
type: prépublication (arXiv) — venue non indiquée dans le texte
statut: fiche complète
tags: [3dgs, compression, masque-appris, hash-grid, instant-ngp, quantification-vectorielle, r-vq, huffman, stockage, memoire-gpu, representation, xr-a-evaluer]
---

# Compact 3D Gaussian Representation for Radiance Field

**Référence :** Lee, J. C., Rho, D., Sun, X., Ko, J. H., Park, E. (2023). Compact 3D Gaussian Representation for Radiance Field. Prépublication arXiv:2311.13681v2 (15 fév. 2024). La venue n'est pas indiquée dans le texte. Sungkyunkwan University / KT. https://arxiv.org/abs/2311.13681
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Page projet :** https://maincold2.github.io/c3dgs/ (p. 1)

## En une phrase

Méthode intégrée à l'entraînement, en trois volets (p. 1, 6) :
1. un **masque binaire appris** sur le volume et l'opacité élimine les Gaussiennes redondantes pendant tout l'entraînement ;
2. la couleur dépendante de la vue passe des SH à un **champ neuronal** (hash grid Instant-NGP + petit MLP) ;
3. l'échelle et la rotation passent par une **quantification vectorielle résiduelle** (R-VQ).

Résultat sur Mip-NeRF 360 avec une A100 : 746 Mo → 48,8 Mo (×15), puis 29,1 Mo avec post-traitement (×25), pour 120 → 128 fps et −0,38 dB.

## Problème traité

- 3DGS a besoin de millions de Gaussiennes, souvent plus d'1 Go par scène réelle (p. 2). La densification laisse beaucoup de redondance : ×2,42 Gaussiennes pour une performance similaire sur Bonsai (p. 4, Fig. 3).
- Chaque Gaussienne stocke ses attributs sans exploiter la redondance spatiale. 48 des 59 paramètres sont des SH (p. 5).
- Les NeRF échouent au temps réel « on handheld devices or low-end GPUs » (p. 2). C'est la motivation affichée, mais sans mesure sur ces appareils.

## Méthode / contributions

**Masque de volume appris (p. 4, éq. 1-3).**
- Un paramètre m_n par Gaussienne donne un masque binaire M_n = 𝟙[σ(m_n) > ε], appris par straight-through estimator. Ce masque multiplie **à la fois l'échelle et l'opacité**.
- Une perte L_m = moyenne de σ(m) est pondérée par λ_m = 5e-4 pour les scènes réelles (p. 11).
- Contrairement à 3DGS, le masquage continue pendant **tout** l'entraînement, ce qui réduit aussi la mémoire GPU à l'entraînement (p. 4).
- Masquer à la fois sur le volume et sur l'opacité fait mieux que chacun des deux seul (p. 11, Tab. 6).

**Géométrie par R-VQ (p. 4-5, éq. 4-6).**
- L = 6 étages de codebooks de C = 64 entrées pour l'échelle et la rotation (p. 11).
- Ils ne sont appris que pendant les **1000 dernières itérations**, avec une initialisation K-means (p. 5).

**Couleur par champ neuronal (p. 5, éq. 7-8).**
- La position est contractée comme dans mip-NeRF 360 puis passe dans une hash grid (16 niveaux de 16 à 4096, 2 canaux, table de 2¹⁹ entrées pour les scènes réelles). Suit un MLP à 2 couches de 64 canaux qui prend aussi en entrée la direction de vue (p. 11).
- La sortie correspond à des SH de degré 0, convertis en RGB (p. 5).

**Inférence rapide (p. 11, §7).**
- Au test, les features de grille (indépendantes de la vue) et les indices de codebook sont **pré-calculés**.
- **Il reste un petit MLP à évaluer par Gaussienne et par direction de vue**, à chaque image.

**Post-traitement « +PP » (p. 6).**
- Quantification min-max 8 bits de l'opacité et de la hash grid.
- Élagage des paramètres de hash inférieurs à 0,1.
- Codage de Huffman des valeurs quantifiées et des indices R-VQ.
- La position et l'opacité sont stockées en FP16 (p. 6).

## Résultats chiffrés

**Matériel :** « Ours » et 3DGS* (ré-évalué) sur **NVIDIA A100**. Le 3DGS « publié » provient d'une A6000 (p. 6, légende Tab. 1). **Rendu mono**, résolution non précisée (protocole standard des datasets). 30K itérations (p. 6).

### Tableau comparatif au 3DGS original (chiffres rapportés DANS CE papier)

| Dataset | Méthode | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Entraînement | FPS ↑ | Stockage ↓ | Nb Gaussiennes |
|---|---|---|---|---|---|---|---|---|
| Mip-NeRF 360 | 3DGS (publié, A6000) | 27,21 | 0,815 | 0,214 | 41 min 33 s | 134 | 734 Mo | — |
| Mip-NeRF 360 | 3DGS* (A100) | 27,46 | 0,812 | 0,222 | 24 min 07 s | 120 | 746 Mo | 3 161 131 (moy.) |
| Mip-NeRF 360 | **Ours** | 27,08 | 0,798 | 0,247 | 33 min 06 s | **128** | **48,8 Mo** | **1 388 162** |
| Mip-NeRF 360 | **Ours+PP** | 27,03 | 0,797 | 0,247 | — | — | **29,1 Mo** | — |
| Tanks & Temples | 3DGS (publié) | 23,14 | 0,841 | 0,183 | 26 min 54 s | 154 | 411 Mo | — |
| Tanks & Temples | 3DGS* | 23,71 | 0,845 | 0,178 | 13 min 51 s | 160 | 432 Mo | 1 831 627 |
| Tanks & Temples | **Ours / +PP** | 23,32 | 0,831 | 0,201 / 0,202 | 18 min 20 s | **185** | **39,4 / 20,9 Mo** | **836 296** |
| Deep Blending | 3DGS (publié) | 29,41 | 0,903 | 0,243 | 36 min 02 s | 137 | 676 Mo | — |
| Deep Blending | 3DGS* | 29,46 | 0,900 | 0,247 | 21 min 52 s | 132 | 663 Mo | 2 810 698 |
| Deep Blending | **Ours / +PP** | **29,79** / 29,73 | 0,901 / 0,900 | 0,258 | 27 min 33 s | **181** | **43,2 / 23,8 Mo** | **1 058 679** |
| NeRF-Synthetic | 3DGS (publié) | 33,32 | — | — | 6 min 14 s | 359 | 68,1 Mo | — |
| NeRF-Synthetic | **Ours / +PP** | 33,33 / 32,88 | 0,968 | 0,034 | 8 min 04 s | **545** | **5,55 / 2,67 Mo** | 120 470 |

Sources : Tab. 1-3 p. 6 ; nombres de Gaussiennes Tab. 9-11 p. 13-14. **Note d'extraction :** les en-têtes de colonnes du Tab. 3 sont décalés dans le texte MinerU (« Train Time | Storage FPS | FPS »). L'attribution retenue (68,1 Mo = stockage, 6 min 14 s = entraînement) découle de la cohérence des unités.

| Métrique | Valeur | Conditions |
|---|---|---|
| FPS | +7 % (Mip-NeRF 360), +16 % (T&T), +37 % (DB), +52 % (Synthetic) contre 3DGS* | A100, mono (p. 6) |
| FPS par scène | Bicycle 63,81 → 76,41. **Plus lent** sur Counter (146,40 → 119,52) et Kitchen (122,07 → 114,24) | p. 13, Tab. 9 |
| Qualité | ΔPSNR −0,38 dB, ΔSSIM −0,014, ΔLPIPS +0,025 (Mip-NeRF 360) ; **+0,33 dB** sur DB | calcul depuis Tab. 1-2 |
| Entraînement | **+37 %** sur Mip-NeRF 360 (24 → 33 min) | A100 (p. 6) |
| **Mémoire GPU à l'inférence** | Bicycle 9,4 → 7,6 Go ; Bonsai 8,7 → 8,3 ; DrJohnson 7,5 → 6,5 ; Playroom 6,4 → 5,6 Go | p. 12, Tab. 8 |
| Répartition du stockage (Mip-NeRF 360) | 3DGS 746 Mo, dont couleur 606,9 Mo. Ours 48,8 Mo, dont hash 25,2 Mo et MLP 0,016 Mo. +PP 29,1 Mo (hash 7,4 Mo) | p. 7, Tab. 5 |
| Latence | non rapportée | — |

**Ablation (Tab. 4, p. 7), Playroom.**
- 3DGS : 2,34 M Gaussiennes, 553 Mo, 154 fps.
- Masque seul : 967 K, 228 Mo, **254 fps**.
- + couleur neuronale : 770 K, 59 Mo, **210 fps**.
- Final : 778 K, 38 Mo, 206 fps.

**Le champ neuronal couleur coûte environ 17 % de fps** par rapport au masque seul. Sur Bonsai, le résultat final (196 fps) est même sous 3DGS (200 fps).

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Motivation « handheld devices or low-end GPUs » (p. 2), mais aucune mesure sur ces appareils. |
| 2. Gaussiennes 3D depuis SfM, covariance anisotrope | Montre que l'échelle et la rotation se compriment bien par R-VQ, car la plupart des Gaussiennes partagent des formes similaires (p. 7-8, Fig. 7). Le masque agit sur l'échelle, donc sur la covariance. |
| 3. Rendu rapide, visibilité, casque XR | Réduit N d'un facteur 2,3 environ. Mais la couleur exige un **MLP par Gaussienne et par vue** : ce n'est plus le pipeline 3DGS standard. |
| 4. Évaluation | Rapporte **la VRAM d'inférence** (rare) et le temps d'entraînement, par scène. |

## Pour (vis-à-vis de notre problématique)
- **Bande passante / stockage** : ×15 à ×25, par exemple Bicycle 1,4 Go → 63 Mo (p. 12). C'est très favorable au transfert edge → casque (P4) et au stockage embarqué.
- **Nombre de Gaussiennes divisé par 2,3 environ**, mesuré par scène (p. 13). Le coût de tri et de rasterisation baisse d'autant, surtout sur les grandes scènes : Bicycle +20 % fps.
- Seul papier du groupe qui **mesure la mémoire GPU au rendu**. C'est un indicateur clé pour un casque autonome.
- Qualité conservée, voire meilleure, sur Deep Blending (intérieur), un cas proche des jumeaux numériques d'intérieur.

## Contre / limites
- **Casque autonome, mémoire** : la VRAM d'inférence ne baisse que de 5 à 19 % (9,4 → 7,6 Go sur Bicycle) alors que le stockage baisse d'environ 95 %. **La taille disque n'est pas le goulot de la VRAM.** Les tampons du rasteriseur et les features pré-calculées dominent vraisemblablement (notre interprétation, non analysée dans le papier). 5,6 à 8,3 Go restent élevés pour un casque autonome.
- **Coût de décodage** : les features de hash pré-calculées reconstituent 32 valeurs par Gaussienne (16 niveaux × 2 canaux, notre calcul). Il faut en plus un MLP par Gaussienne et par image, **à doubler en stéréo** puisque la direction de vue diffère par œil. Le décodage Huffman s'ajoute au chargement. Rien de cela n'est mesuré séparément.
- **Incompatible avec un rasteriseur 3DGS standard** : il faut un pipeline personnalisé (hash grid + MLP + codebooks). Les viewers WebGL, Unity ou casque existants ne le lisent pas tel quel.
- Gain en fps faible et irrégulier : +7 % en moyenne sur Mip-NeRF 360, régression sur certaines scènes. L'entraînement est plus long (+29 à +37 %).
- Mesures sur A100 uniquement, en mono, sans résolution explicite, sans latence ni énergie.

## Idées à creuser pour une approche novatrice
- *Hypothèse (P2) :* mutualiser l'évaluation couleur entre les deux yeux. Les directions de vue gauche et droite diffèrent peu pour les Gaussiennes lointaines : on pourrait n'évaluer le MLP qu'une fois au-delà d'une distance seuil. Ce serait une brique concrète de P2 pour les représentations à couleur neuronale.
- *Hypothèse :* « **baker** » le champ neuronal en SH de degré faible après l'entraînement. On garderait les avantages du masque et de la R-VQ tout en revenant au rasteriseur standard. Ce serait une variante hybride avec [fan2023_lightgaussian](../fan2023_lightgaussian/fiche.md).
- *Hypothèse (P3) :* λ_m règle continûment le compromis nombre de Gaussiennes / qualité (p. 11, Tab. 6 ; Fig. 8). Entraîner plusieurs niveaux (plusieurs λ_m) fournirait des LOD pilotables par un modèle QoS. Le papier **n'effectue pas** ce pilotage.
- *Hypothèse (P4) :* streamer d'abord la géométrie (positions FP16 + indices R-VQ, environ 20 Mo selon le Tab. 5), puis la hash grid, qui est partagée et compacte (7,4 Mo après PP).
- *À vérifier :* mesurer la VRAM et le coût du MLP sur GPU mobile. Voir [du2026_mobile-gs](../du2026_mobile-gs/fiche.md) et [oh2025_neo-on-device](../oh2025_neo-on-device/fiche.md).

## Citations clés
> « we consistently show over 25× reduced storage and enhanced rendering speed, while maintaining the quality of the scene representation, compared to 3DGS » (`doc:c7b9e5b/tier:standard/page:1/block:9`)

> « NeRFs often fail to achieve real-time rendering on handheld devices or low-end GPUs » (`doc:c7b9e5b/tier:standard/page:2/block:1`)

> « we consistently mask out along with the entire training process, reducing unessential Gaussians effectively and ensuring efficient computation with low GPU memory throughout the training phase » (`doc:c7b9e5b/tier:standard/page:4/block:16`)

> « This allows our method to simply process a small MLP for generating view-dependent colors during testing » (`doc:c7b9e5b/tier:standard/page:11/block:5`)

> « Our method consistently reduces the GPU memory requirements by a safe margin » (`doc:c7b9e5b/tier:standard/page:12/block:8`)

## Liens
- Papiers liés :
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) : base.
  - [fan2023_lightgaussian](../fan2023_lightgaussian/fiche.md) : concurrent direct. Il reprend nos chiffres dans son Tab. 1 (128 fps / 48 Mo) et fait mieux en fps.
  - [yu2023_mip-splatting](../yu2023_mip-splatting/fiche.md) : même groupe (anti-aliasing).
  - [hanson2024_speedy-splat](../hanson2024_speedy-splat/fiche.md), [mallick2024_taming-3dgs](../mallick2024_taming-3dgs/fiche.md) : réduction ou budget de Gaussiennes.
  - [shi2024_lapisgs](../shi2024_lapisgs/fiche.md) : streaming progressif (P4).
  - [du2026_mobile-gs](../du2026_mobile-gs/fiche.md), [oh2025_neo-on-device](../oh2025_neo-on-device/fiche.md) : contraintes mémoire sur appareil.
  - [tu2025_vrsplat](../tu2025_vrsplat/fiche.md) : rendu stéréo VR, où le coût par vue du MLP compte.
