---
citekey: wang2025_smol-gs
mineru_doc: d6bdbe6
type: preprint   # arXiv 2512.00850 v3 (18 juin 2026), mention « Preprint », pas de venue indiquée
statut: fiche complète
tags: [3dgs, compression, octree, codage-entropique, codage-arithmétique, mlp, splats-neuronaux, encodage-positionnel, compaction, 3dgs-zip, mip-nerf-360, h200, streaming, code-public]
---

# Smol-GS: Compact Representations for Abstract 3D Gaussian Splatting

**Référence :** Haishan Wang, Mohammad Hassan Vali, Arno Solin (ELLIS Institute Finland, Aalto University) (2025). *Smol-GS: Compact Representations for Abstract 3D Gaussian Splatting.* arXiv [2512.00850](https://arxiv.org/abs/2512.00850) (v1 30 nov. 2025, v3 18 juin 2026), preprint. Projet : [aaltoml.github.io/Smol-GS](https://aaltoml.github.io/Smol-GS) · code : [github.com/AaltoML/Smol-GS](https://github.com/AaltoML/Smol-GS) (`doc:d6bdbe6/tier:standard/page:1`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Smol-GS compresse un 3DGS d'environ **×125 à ×150** : 5,86 MB au lieu de 734 MB sur Mip-NeRF 360, avec un PSNR supérieur (27,76 contre 27,21 dB) mais un **LPIPS moins bon** (0,248 contre 0,214). Pour cela :
- les positions sont codées dans un **octree d'occupation + Huffman** ;
- les SH sont remplacées par des **features de 8 dimensions par splat**, quantifiées et codées arithmétiquement ;
- **quatre petits MLP décodent à chaque vue** la couleur, l'opacité, la rotation et l'échelle.

Le papier revendique 210 fps contre 139 pour 3DGS sur **H200** (`page:1`, `page:8`).

## Problème traité
- Un 3DGS pèse des centaines de MB à quelques GB (`page:1`).
- Les deux familles de compression ont chacune leurs limites (`page:1`, `page:2`, `page:3`) :
  - le **traitement du signal** (quantification vectorielle, codebooks) n'exploite pas les corrélations spatiales ;
  - les approches **anchor-offset** (Scaffold-GS, HAC++, ContextGS, HEMGS) ajoutent des offsets transparents et des heuristiques, et **évitent de compresser les coordonnées**.

## Méthode / contributions
1. **Coordonnées → octree d'occupation** (`page:4`, Fig. 4 `page:5`) :
   - la boîte englobante est subdivisée récursivement, et seules les cases non vides sont redivisées ;
   - chaque division émet un octet d'occupation en ordre de Morton, puis un **codage Huffman** est appliqué ;
   - à la profondeur R = 16, la coordonnée devient le centre de la case la plus fine (éq. 1). **On garde au plus un splat par case**, les autres sont élagués ;
   - selon les auteurs, une quantification à 16 bits par axe est « imperceptible » (Fig. A9, `page:15`).
2. **Encodage positionnel issu de l'octree** : le code de Morton de la case (3R bits) passe par MLP_oct (`page:4`).
3. **Splats neuronaux** (`page:4`, `page:5`) :
   - chaque splat porte x, une feature f ∈ ℝ⁸ et un « scaling controller » s ∈ ℝ³ ;
   - à chaque rendu, f* = [f, **direction de vue**, **distance caméra–splat**, MLP_oct(f_oct)] (éq. 2) ;
   - quatre MLP prédisent **opacité, couleur, rotation et échelle** (éq. 3), avec l'échelle bornée par s via une sigmoïde ;
   - la covariance vaut Σ = R S Sᵀ Rᵀ (éq. 4) et la rastérisation est celle de 3DGS (éq. 5–6).
   - ⇒ **toute la géométrie (Σ) et l'apparence dépendent de la vue.**
4. **Compression des features** : quantification à pas appris, prédite par une grille de hachage (InstantNGP) + MLP_h, avec un a priori gaussien. Le terme NLL sert de proxy du débit, puis un codage arithmétique est appliqué. C'est l'héritage de HAC (`page:5`, `page:6`).
5. **Entraînement en 5 étapes, 35k itérations** (`page:6`, Fig. 5) : échauffement → densification (0,5k–15k) → **compaction** (15k–20k, régularisation L1 de l'opacité + élagage) → compression de f (20k–30k) → compression de x (30k–35k).
6. **Architecture des MLP** (Tab. A6, `page:15`) :
   - MLP_o, MLP_c, MLP_r et MLP_s ont chacun une entrée de dimension 20 (8 + 8 + 4), **3 couches, 128 neurones cachés** ;
   - MLP_h : 3 couches, 128 cachés ; MLP_oct : 3 couches, 64 cachés.

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| Taille, Mip-NeRF 360 (Tab. 2) | **Smol-GS-base 5,86 MB** · small 4,87 MB · HAC++ 8,74 · HEMGS 12,54 · ContextGS 13,30 · Reducing3DGS (Papantonakis) 29,0 · **3DGS 734** | chiffres des baselines repris du benchmark 3DGS.zip, `page:8` |
| Qualité, Mip-NeRF 360 (Tab. 2) | base **27,76 / 0,807 / 0,248** · small 27,61 / 0,801 / 0,258 · 3DGS 27,21 / 0,815 / **0,214** · HAC++ 27,60 / 0,803 / 0,253 · Reducing3DGS 27,10 / 0,809 / 0,226 | PSNR / SSIM / LPIPS, `page:8` |
| T&T / Deep Blending (Tab. 2) | base 24,25 / 0,843 / 0,199 / **4,78 MB** · 30,12 / 0,905 / 0,262 / **2,86 MB** (3DGS : 411 et 676 MB) | `page:8` |
| Répartition de la taille (Tab. 1) | Mip-360 : x 1,19 · **f 2,75** · s 1,75 · MLP 0,16 MB | `page:7` |
| Ablations de compression (Tab. 4) | sans Huffman 7,04 MB · sans quantification des coordonnées 10,79 · sans quantification des features 23,71 MB, pour une qualité quasi inchangée | Mip-360, `page:8` |
| **FPS (Tab. 3)** | Smol-GS **210,0** / 3DGS 139,3 / HAC++ 128,0 (Mip-360) · 399,9 / 178,8 / 149,8 (DB) · 223,3 / 218,9 / 102,7 (T&T) | **NVIDIA H200 141 GB** (`page:14`) ; résolution non indiquée ; mono ; mesure réelle, `page:8` |
| **Nombre de Gaussiennes** | Garden : pic **≈ 3,8 M** en fin de densification, puis **≈ 1 M** après compaction (lu sur la Fig. 5) ; **aucun tableau par scène** | `page:6` (lecture graphique) |
| Entraînement | **≈ 26,6 min / scène** (35k it.) | H200, `page:14` |
| Encodage / décodage | 0,8–3,7 s / 1,4–5,5 s par scène (base) | H200, Tab. A11/A13, `page:20`–`21` |
| Réglages taille/qualité (Tab. A9) | λ_o de 1e-7 à 5e-7 : 10,31 → 4,03 MB, LPIPS 0,231 → 0,270 (Mip-360) | `page:17` |
| Latence, VRAM au rendu, énergie, stéréo | **Non rapportées** | — |

**Incohérence interne :** la configuration par défaut (R = 16, n_f = 8, λ_o = 3e-7, λ_q = 5e-4) vaut **27,69 dB / 5,896 MB** dans les ablations (Tab. A7–A10), contre 27,76 dB / 5,860 MB dans la Tab. 2 (`page:16`–`17` contre `page:8`). L'écart est faible, mais il faut citer la Tab. 2 en le précisant.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | État de l'art 2026 de la **compression 3DGS** : taille minimale au benchmark 3DGS.zip, devant HAC++. Code PyTorch sur la base INRIA, donc CUDA : à entraîner sur le PC de l'école |
| 2. Gaussiennes 3D depuis SfM, covariance | Initialisation SfM classique, mais **covariance prédite par MLP selon la vue** (rotation et échelle), ce qui s'écarte de la covariance anisotrope fixe du sujet. L'étape de **compaction** (≈ 3,8 M → 1 M sur Garden) est une recette de réduction du nombre de Gaussiennes |
| 3. Rendu rapide, casque XR | Rastérisation 3DGS standard **précédée de 4 MLP par splat et par vue**. Aucun test en stéréo, sur mobile ou en VR |
| 4. Évaluation | Protocole 3DGS.zip (taille zip + PSNR/SSIM/LPIPS), comparable à 10 baselines. Pas de fps sur matériel grand public |

## Pour (vis-à-vis de notre problématique)
- **Taille record** : environ 6 MB par scène Mip-360, soit **5× moins que Papantonakis** (29 MB) et 1,5× moins que HAC++, à PSNR supérieur (`page:8`). Une scène entière se transmet en moins d'une seconde sur un lien de quelques dizaines de Mbit/s (calcul de ma part).
- **Plus rapide que 3DGS sur GPU serveur** (×1,5 sur Mip-360, ×2,2 sur DB) malgré les MLP. Ce gain vient probablement surtout du **nombre de splats réduit** par la compaction (≈ 1 M contre **5,83 M** pour le modèle 3DGS pré-entraîné de l'INRIA sur Garden, lu dans l'en-tête `.ply`, [donnees/inria_pretrained](../../donnees/inria_pretrained/README.md) : ÷ 5,8 ; *le lien de cause reste inféré*), plus que de la représentation elle-même, contrairement à ce que suggèrent les auteurs (`page:8`, `page:9`).
- **Moins d'artefacts** visuels que 3DGS sur les murs, le ciel et les reflets, d'après les auteurs (Fig. 2, 7) : les features apprises modélisent mieux les matériaux que les SH d'ordre 3.
- **Bouton continu taille ↔ qualité** (λ_o) documenté : jusqu'à 4 MB contre 10 MB (Tab. A9).
- Code public.

## Contre / limites
- **LPIPS moins bon que 3DGS** (0,248 contre 0,214 sur Mip-360 ; 0,199 contre 0,183 sur T&T). **C'est le critère perceptif qui compte en VR**, et le PSNR supérieur ne le compense pas. Reducing3DGS a un LPIPS de 0,226 : meilleur, pour 29 MB.
- **Pas un format 3DGS standard** : les MLP sont évalués **à chaque image, pour chaque splat, selon la direction de vue et la distance**. Conséquences :
  - incompatible tel quel avec UnityGaussianSplatting (il faudrait porter 4 MLP dans les compute shaders HLSL) ;
  - en **stéréo**, la direction de vue diffère d'un œil à l'autre, donc **deux évaluations par splat** et un tri qui ne se partage plus exactement. C'est le même risque que le MLP d'opacité de [Mobile-GS](../du2026_mobile-gs/fiche.md) ;
  - *estimation personnelle* : 4 MLP de 20 → 128 → 128 → {1, 3, 4, 3}, soit ≈ **7,7·10⁴ multiplications-additions par splat visible et par œil** (en supposant que « 3 couches » désigne 3 couches linéaires). Avec ≈ 0,5 M splats visibles, cela fait ≈ 38 GMAC par œil et par image, donc ≈ 5,5 TMAC/s en stéréo à 72 Hz. C'est **incompatible avec le budget d'un Quest 3**, sauf à précalculer (*à mesurer, pas à affirmer*).
- **La covariance dépend de la vue** (MLP_r et MLP_s) : la forme des splats change quand la tête bouge. Le risque de popping ou de scintillement en VR n'est pas étudié. Il faudrait le mesurer par FLIP temporel.
- Seul matériel testé : un **H200**. Pas de résolution indiquée pour les fps, pas de VRAM au rendu, pas de latence.
- **Entraînement lourd** : pic à ≈ 3,8 M Gaussiennes (Fig. 5), 27 min sur H200, un entraînement par scène. Les auteurs le reconnaissent (« time-consuming », `page:9`). L'octree est **sensible aux éditions** et mal adapté aux grandes scènes (`page:9`).
- Pas de venue à ce jour ; incohérence entre la Tab. 2 et les ablations (voir plus haut).

## Réutilisable pour nous
- **Pour P4 / P1′ (streaming casque ↔ edge)** : Smol-GS est le **meilleur format de transport** connu de la base. Une scène complète en 3 à 11 MB se transmet une seule fois, puis se décode (1,4 à 5,5 s sur H200) **sur l'edge ou sur le PC**, qui la convertit en 3DGS standard avant de l'envoyer au casque ou de la rendre en pixels.
- **Pour l'étape 2 et P3′** : l'étape de **compaction** (L1 sur l'opacité + élagage, `page:6`) produit des modèles d'environ 1 M Gaussiennes à qualité conservée. C'est une autre façon d'obtenir des modèles « dimensionnés casque », à comparer avec le budget exact de [Taming](../mallick2024_taming-3dgs/fiche.md).
- **Pour l'axe A3 d'`options.md`** : c'est le nouveau point extrême de la frontière taille/qualité. Il confirme l'enseignement n°7 : la compression agit sur le disque et le réseau, et ne change le fps que par le nombre de splats.
- **Pour l'évaluation** : reprendre le protocole 3DGS.zip (taille du zip) quand on rapporte la mémoire.

## Verdict vis-à-vis de nos pistes
- **P6 (banc de mesure sur casque)** : sans objet directement, puisque le format n'est pas rendu nativement par notre chaîne Unity. Il pourrait devenir un point de comparaison « format neuronal » si on le porte en HLSL, ce qui n'est pas prioritaire.
- **P3′ (contrôleur QoS/QoE)** : λ_o est un bouton **hors ligne** (à l'entraînement), pas un levier runtime. Pas de menace pour P3′.
- **P4 (streaming progressif)** : **renforce la piste**, car la taille minimale réduit le coût de transmission de la scène complète. Il ne propose en revanche ni couches ni progressivité, ce qui laisse de la place face à [LapisGS](../shi2024_lapisgs/fiche.md) et Nebula.
- **P1′ (partage casque/edge)** : format candidat pour la liaison edge → casque, si le décodage est fait sur l'edge.
- **P2, P5** : sans objet.

## Idées à creuser pour une approche novatrice
- *Hypothèse* : **« cuire » Smol-GS en 3DGS standard**. On évalue les MLP pour un ensemble de directions et on ajuste des SH d'ordre 1 à 3 par splat. Rotation et échelle sont figées à une distance de référence. On obtiendrait un .ply d'environ 1 M Gaussiennes lisible par aras-p. À mesurer : la perte de LPIPS due au figement de la covariance.
- *Hypothèse* : **Smol-GS comme format de transport + compaction pilotée par le budget casque**. On entraîne avec un λ_o choisi pour que le modèle décodé tienne dans ≤ 0,5 M Gaussiennes rendues, puis on streame le zip.
- *Hypothèse* : vérifier si le **gain en fps sur H200 tient à nombre de splats égal**, en comparant Smol-GS et 3DGS compactés au même nombre. Cela départagerait l'effet « représentation » de l'effet « compaction ».

## Citations clés
> « The rendering speed of Smol-GS-base surpasses both vanilla 3DGS and the anchor-based HAC++ » (`doc:d6bdbe6/tier:standard/page:8`)

> « Smol-GS requires training for each scene, which is time-consuming and limits its scalability to large-scale applications. The positional encoding relies on the octree hierarchy, which is sensitive to splat edits and suboptimal for large-scale scenes. » (`doc:d6bdbe6/tier:standard/page:9`)

> « Given the camera center x_c during rendering, the augmented feature f* is constructed by concatenating the splat feature f with viewing information and positional encoding » (`doc:d6bdbe6/tier:standard/page:4`)

## Liens
- Papiers liés :
  - [Papantonakis 2024 (Reducing Memory Footprint)](../papantonakis2024_reduced-memory/fiche.md) : baseline « Reducing3DGS », 29 MB, format standard, LPIPS meilleur ;
  - [Lee 2023 (Compact3D)](../lee2023_compact3d/fiche.md) : baseline « Compact3DGS », 48,8 MB ;
  - [Fan 2023 (LightGaussian)](../fan2023_lightgaussian/fiche.md) : réf. [11], quantification vectorielle ;
  - [Mallick 2024 (Taming)](../mallick2024_taming-3dgs/fiche.md) : réf. [13], budget exact, autre voie de compaction ;
  - [Du 2026 (Mobile-GS)](../du2026_mobile-gs/fiche.md) : autre représentation à MLP dépendant de la vue, même risque en stéréo ;
  - [Jiang 2024 (VR-GS)](../jiang2024_vr-gs/fiche.md) : cité comme application VR (réf. [36]) ;
  - [Shi 2024 (LapisGS)](../shi2024_lapisgs/fiche.md), [Zhu 2025 (Nebula)](../zhu2025_nebula/fiche.md) : streaming progressif, complémentaire ;
  - 🔎 HAC / HAC++ (arXiv 2501.12255), ContextGS, HEMGS (arXiv 2411.18473), Scaffold-GS, benchmark 3DGS.zip : absents de la base.
