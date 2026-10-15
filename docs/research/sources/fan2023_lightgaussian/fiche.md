---
citekey: fan2023_lightgaussian
mineru_doc: 803219b
type: conférence
statut: fiche complète
tags: [3dgs, compression, pruning, quantification-vectorielle, distillation, spherical-harmonics, stockage, fps, representation, streaming, xr-a-evaluer]
---

# LightGaussian: Unbounded 3D Gaussian Compression with 15x Reduction and 200+ FPS

**Référence :** Fan, Z., Wang, K., Wen, K., Zhu, Z., Xu, D., Wang, Z. (2024). LightGaussian: Unbounded 3D Gaussian Compression with 15x Reduction and 200+ FPS. *38th Conference on Neural Information Processing Systems (NeurIPS 2024)* (p. 1). arXiv:2311.17245 (v6, 12 nov. 2024). https://arxiv.org/abs/2311.17245
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Page projet :** https://lightgaussian.github.io (p. 1)

## En une phrase

Post-traitement d'un modèle 3DGS déjà entraîné en trois étapes (p. 1, 6) :
1. **élagage** des Gaussiennes de faible « significance globale », suivi d'une **ré-adaptation** ;
2. **distillation** des SH du degré 3 au degré 2, avec des vues pseudo-générées ;
3. **quantification vectorielle** des SH les moins significatifs.

Résultat sur Mip-NeRF 360 avec une A6000 : 782 Mo → 45 Mo (×15) et 144 → 237 fps, pour −0,27 dB de PSNR.

## Problème traité

- Un modèle 3DGS de scène non bornée pèse souvent plus d'1 Go, par exemple 1,4 Go pour Bicycle (p. 2). La densification heuristique sur-paramètre la scène, ce qui gonfle à la fois le stockage et le temps de rendu (p. 2).
- Les SH occupent **81,3 %** des dimensions d'attributs, soit 45 + 3 flottants sur 59 par Gaussienne (p. 5, p. 15).
- Élaguer sur l'opacité seule détruit les détails fins : 27,2 → 25,3 dB (p. 4, Fig. 3).

## Méthode / contributions

**Gaussian Pruning & Recovery (réduction de N).**
- On calcule un score global GS_j = Σ_pixels 𝟙(intersection) · σ_j · T · γ(Σ_j) sur toutes les vues d'entraînement. Ce score combine le nombre de rayons touchés, l'opacité, la transmittance et un volume normalisé, γ = (min(V/V_max90, 1))^β avec β = 0,1 (p. 4-5, éq. 3-4 ; p. 7).
- On élague les Gaussiennes de rang faible, puis on fait une **co-adaptation** de 5000 itérations sans densification (p. 5).
- Le taux d'élagage est d'environ 66 % (p. 9, Tab. 6). La qualité chute nettement à partir de 70 % (p. 10).

**SH Distillation (réduction de F).**
- Le modèle élève (student) passe en SH de degré 2, soit 21 éléments de moins par Gaussienne (p. 7).
- Il est supervisé par le modèle maître (teacher) en L2 sur des vues pseudo-générées : t_pseudo = t_train + 𝒩(0, σ²), avec σ = 0,1 (p. 5, éq. 5-6 ; p. 7).

**Vector Quantization.**
- Un codebook K-means de **8192 entrées** est appliqué **seulement aux SH**, et seulement sur les 60 % de Gaussiennes les moins significatives. Suivent 5000 itérations de fine-tuning (p. 5-7).
- Position, forme, rotation, opacité et SH significatifs sont stockés en **float16** (p. 6).
- Quantifier tous les attributs fait chuter le PSNR à 23,11 dB, ce qui explique ce choix restrictif (p. 7, Tab. 4).

**Implémentation.** PyTorch avec le rasteriseur différentiable de 3DGS. **Toutes les mesures sont faites sur une NVIDIA A6000** (p. 7). La méthode se généralise à Scaffold-GS (p. 8).

## Résultats chiffrés

**Matériel :** GPU desktop NVIDIA A6000 (p. 6-7). **Rendu mono.** **Résolution de rendu non précisée** : protocole des datasets Mip-NeRF 360 et T&T, sans valeur explicite dans le texte. **Nombre absolu de Gaussiennes non rapporté** ; seul le taux d'élagage l'est (≈ 66 %).

### Tableau comparatif au 3DGS original (chiffres rapportés DANS CE papier, Tab. 1 p. 6)

| Dataset | Méthode | FPS ↑ | Taille ↓ | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
|---|---|---|---|---|---|---|
| Mip-NeRF 360 | 3D-GS (valeurs publiées) | 134 | 734 Mo | 27,21 | 0,815 | 0,214 |
| Mip-NeRF 360 | 3D-GS* (ré-entraîné, A6000) | 144 | 782 Mo | 27,40 | 0,813 | 0,217 |
| Mip-NeRF 360 | **LightGaussian** | **237** | **45 Mo** | 27,13 | 0,806 | 0,237 |
| Mip-NeRF 360 | Compact 3D-GS [Lee] (tel que reporté) | 128 | 48 Mo | 27,08 | 0,798 | 0,247 |
| Tanks & Temples | 3D-GS (valeurs publiées) | 154 | 411 Mo | 23,14 | 0,841 | 0,183 |
| Tanks & Temples | 3D-GS* (ré-entraîné) | 106 | 433 Mo | 23,66 | 0,845 | 0,178 |
| Tanks & Temples | **LightGaussian** | **357** | **25 Mo** | 23,44 | 0,832 | 0,202 |
| Blender (synth.) | 3D-GS | 310 | 52,38 Mo | 33,716 | 0,969 | 0,0334 |
| Blender (synth.) | **LightGaussian** | **411** | **7,84 Mo** (tableau ; 7,89 dans le texte) | 32,725 | 0,965 | 0,0370 |

Sources : Tab. 1 p. 6 ; Blender p. 16 et Tab. 7 p. 17. **Incohérence interne :** le texte annonce pour T&T « 380MB to 22MB » (p. 8), alors que le tableau donne 433 Mo → 25 Mo.

| Métrique | Valeur | Conditions |
|---|---|---|
| FPS | 144 → 237 (Mip-NeRF 360) ; 106 → 357 (T&T) ; 156 → 302 (Room) | A6000, mono (p. 6-7) |
| Qualité | ΔPSNR −0,27 dB, ΔSSIM −0,007, ΔLPIPS +0,020 (Mip-NeRF 360, contre 3D-GS*) | calculé depuis Tab. 1 p. 6 |
| Temps de compression | non rapporté en temps. En itérations : 5000 (co-adaptation) + distillation (« few steps ») + 5000 (VQ) | p. 5-6, p. 15 |
| Taille | ×15 en moyenne sur Mip-NeRF 360, ×17 sur T&T (notre calcul 433/25) | p. 6 |
| Mémoire GPU au rendu | non rapportée | — |
| Latence | non rapportée | — |

**Ablation Room (Tab. 2, p. 7).**

| Étape | FPS | Taille | PSNR / SSIM / LPIPS |
|---|---|---|---|
| Baseline | 156,21 | 365 Mo | 31,34 / 0,917 / 0,221 |
| + élagage | 308,10 | 123 Mo | 30,67 / 0,910 / 0,234 |
| + co-adaptation | 304,64 | 123 Mo | 31,64 / 0,918 / 0,228 |
| + SH degré 2 + distillation | 302,89 | 81 Mo | 31,48 / 0,917 / 0,231 |
| + VQ + fine-tuning (final) | 302,01 | 21 Mo | 31,40 / 0,916 / 0,232 |

**Le gain en fps vient presque entièrement de l'élagage**, alors que la réduction de taille vient des SH et de la VQ.

**Autres résultats.**
- Le FP16 seul fait passer de 80,99 Mo à 36,51 Mo (p. 7, Tab. 4).
- Réduction des SH (Tab. 6, p. 9) : avec le degré 2 et la distillation, 353 Mo → 140 Mo pour 192 → 243 fps, SSIM 0,927 → 0,926. Avec le degré 1 et la distillation, on obtient 88,9 Mo, SSIM 0,923.
- Scaffold-GS + élagage de 80 % des Gaussiennes neuronales : 152 → 178 fps, 173,6 → 112,6 (unité non précisée, vraisemblablement Mo) (p. 8, Tab. 5).

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | VR et AR ne sont citées qu'en motivation (p. 2, p. 10). Aucune mesure sur casque. |
| 2. Gaussiennes 3D depuis SfM, covariance anisotrope | Montre la forte redondance de la densification : ≈ 66 % des Gaussiennes sont élaguables sans perte (p. 9). La covariance (échelle, rotation) est gardée en FP16 car elle est sensible à la VQ (p. 7). |
| 3. Rendu rapide, visibilité, casque XR | Le score GS est un **critère d'importance par Gaussienne fondé sur la visibilité** (rayons touchés × transmittance). Le rasteriseur 3DGS est inchangé et les fps augmentent de 1,6 à 3,4×. |
| 4. Évaluation | Protocole fps + taille + PSNR/SSIM/LPIPS sur Mip-NeRF 360, T&T et Blender. **Ni VRAM, ni latence, ni matériel mobile.** |

## Pour (vis-à-vis de notre problématique)
- **Compatible avec le rasteriseur standard.** Le rendu utilise le rasteriseur 3DGS (p. 7). Une fois les codes VQ décodés (un simple lookup), on retrouve un nuage 3DGS standard avec des SH de degré 2. Les viewers casque, WebGL ou Unity existants sont donc utilisables. La lecture du format est notre analyse ; le papier ne décrit pas de viewer.
- **Casque autonome.**
  - *Mémoire* : 2,9 fois moins de Gaussiennes (−66 %) et des SH de degré 2 réduisent aussi l'empreinte en VRAM après décodage (notre inférence ; la VRAM n'est pas mesurée).
  - *Bande passante* : 45 Mo au lieu de 782 Mo, soit environ 3,6 s au lieu d'environ 63 s à 100 Mbit/s (notre calcul). C'est décisif pour charger une scène depuis l'edge (P4).
  - *Coût de décodage* : faible, car il s'agit d'un lookup de codebook et d'une conversion FP16 → FP32 au chargement, sans réseau à l'exécution.
- **Gain en fps réel et important** : +65 % sur Mip-NeRF 360, ×3,4 sur T&T. Il laisse une marge pour la stéréo (2 vues) et pour ≥ 30 fps sur un GPU mobile bien moins puissant qu'une A6000.
- Post-traitement : on part d'un modèle 3DGS existant sans ré-entraîner depuis zéro (≈ 10K itérations au total).

## Contre / limites
- **Mesures seulement sur GPU desktop A6000**, en mono. Aucune résolution explicite ne permet de vérifier la contrainte 1080p. Rien sur casque, mobile, VRAM ou énergie.
- Perte de qualité perceptuelle non négligeable sur les scènes réelles : LPIPS +0,020 sur Mip-NeRF 360 et +0,024 sur T&T. Les SH de degré 2 réduisent les reflets spéculaires, une légère variation de luminosité est visible (p. 6, Fig. 4).
- Le temps de compression n'est pas chiffré, et il faut d'abord un modèle 3DGS complet : l'entraînement n'est pas accéléré.
- Le score GS dépend des **vues d'entraînement**. Les Gaussiennes peu vues pendant la capture risquent d'être élaguées, même si elles comptent pour des points de vue VR hors distribution (notre remarque).
- Incohérences mineures de chiffres entre le texte et les tableaux (T&T 380/22 contre 433/25 Mo ; Blender 7,89 contre 7,84 Mo).
- Élagage statique, avec un seul niveau : pas de LOD, pas de progressivité.

## Idées à creuser pour une approche novatrice
- *Hypothèse (P3) :* le **score GS trié forme naturellement un ordre d'importance**. En tronquant la liste à k Gaussiennes, on obtient un budget ajustable en continu. Un contrôleur QoS/QoE pourrait choisir k selon le fps mesuré sur le casque. Le papier donne déjà la courbe qualité/fps en fonction du taux d'élagage (p. 9, Fig. 6a). **Il éclaire P3 sans la réaliser**, puisque le taux reste fixe et hors ligne.
- *Hypothèse (P4) :* **streaming progressif ordonné par GS**. On envoie d'abord les 34 % les plus significatifs avec des SH de degré 0, puis les Gaussiennes restantes et les bandes SH supérieures. À comparer avec [shi2024_lapisgs](../shi2024_lapisgs/fiche.md).
- *Hypothèse (P1) :* recalculer le score GS **depuis la pose courante** (visibilité en ligne) pour répartir les Gaussiennes entre casque (forte significance, fovéa) et edge.
- *Hypothèse :* combiner avec le filtre de [yu2023_mip-splatting](../yu2023_mip-splatting/fiche.md). L'élagage réduit le coût, et le filtre garantit la qualité aux changements d'échelle.

## Citations clés
> « LightGaussian achieves an average 15× compression rate while boosting FPS from 144 to 237 within the 3D-GS framework » (`doc:803219b/tier:standard/page:1/block:9`)

> « a typical unbounded 360-degree scene in 3D-GS [7] may require over 1GB of storage (e.g., 1.4GB for the Bicycle scene) » (`doc:803219b/tier:standard/page:2/block:2`)

> « a substantial 81.3 percent of the feature dimension is occupied by Spherical Harmonics (SH) coefficients » (`doc:803219b/tier:standard/page:5/block:7`)

> « All performance evaluations are conducted on an A6000 GPU » (`doc:803219b/tier:standard/page:7/block:8`)

> « we note a marked decline in rendering quality when the pruning ratio reaches 70% » (`doc:803219b/tier:standard/page:10/block:1`)

## Liens
- Papiers liés :
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) : représentation compressée, rasteriseur réutilisé.
  - [lee2023_compact3d](../lee2023_compact3d/fiche.md) : concurrent direct, comparé au Tab. 1 (masque appris + champ neuronal couleur).
  - [yu2023_mip-splatting](../yu2023_mip-splatting/fiche.md) : même groupe (anti-aliasing, orthogonal).
  - [hanson2024_speedy-splat](../hanson2024_speedy-splat/fiche.md), [mallick2024_taming-3dgs](../mallick2024_taming-3dgs/fiche.md) : élagage et budget de Gaussiennes.
  - [kerbl2024_hierarchical-3dgs](../kerbl2024_hierarchical-3dgs/fiche.md) : LOD.
  - [shi2024_lapisgs](../shi2024_lapisgs/fiche.md) : streaming progressif (P4).
  - [du2026_mobile-gs](../du2026_mobile-gs/fiche.md), [oh2025_neo-on-device](../oh2025_neo-on-device/fiche.md), [han2026_websplatter](../han2026_websplatter/fiche.md) : déploiement mobile, web ou embarqué, où la taille compte.
  - [chen2024_3dgs-survey](../chen2024_3dgs-survey/fiche.md) : panorama de la compression.
