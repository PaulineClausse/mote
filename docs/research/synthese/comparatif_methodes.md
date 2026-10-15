# Comparatif des méthodes de la base

*2026-09-29, 35 fiches. Tous les chiffres viennent des fiches (lien dans la colonne Source). « Ours » dans une fiche = la méthode du papier lui-même.*

**Lecture pour notre problème :** sur Quest 3, la limite est le **nombre de Gaussiennes rendues par image** (≈ 0,3–0,5 M au mieux, voir [faisabilite_quest3.md](faisabilite_quest3.md)) et le *fill-rate*. Les critères qui comptent sont donc, dans l'ordre :
1. le nombre de Gaussiennes ;
2. un format lisible par un rasteriseur 3DGS standard (UnityGaussianSplatting) ;
3. la perte de qualité perçue (LPIPS) ;
4. la taille sur disque, qui compte peu.

⚠️ **Comparaisons entre papiers indicatives** : GPU différents, et baselines 3DGS ré-entraînées différemment (PSNR de 27,21 à 27,55 selon le papier). La colonne **ΔLPIPS** compare chaque méthode **à la baseline 3DGS de son propre papier** : c'est la mesure la plus comparable.

## Famille 1 : réduire le nombre de Gaussiennes (le levier n°1 pour le Quest)

Mip-NeRF 360, moyenne des scènes :

| Méthode | Gaussiennes | Taille | PSNR / SSIM / LPIPS | **ΔLPIPS** vs sa baseline | FPS desktop (GPU) | Entraînement | Format standard ? | Réglage du budget | Source |
|---|---|---|---|---|---|---|---|---|---|
| **3DGS** (référence) | 3,2–3,3 M en moyenne ; **1,0 à 6,1 M** selon la scène | 734 Mo | 27,21 / 0,815 / 0,214 | — | 134 (A6000) | 41 min | oui | aucun | [Kerbl 2023](../sources/kerbl2023_3dgs/fiche.md), [INRIA](../donnees/inria_pretrained/README.md) |
| **Taming 3DGS** | **0,63 M** (÷ 5,3) | ≈ 150 Mo *(estim.)* | 27,31 / 0,801 / 0,252 | +0,037 | non rapporté | **11 min** (A4500) | **oui, sous condition** ⚠️ : désactiver le mode haute opacité ou convertir l'opacité à l'export (voir la [fiche](../sources/mallick2024_taming-3dgs/fiche.md)) | **budget exact B** | [Mallick 2024](../sources/mallick2024_taming-3dgs/fiche.md) |
| **Speedy-Splat** | **0,28 M** (÷ 10,6) | non rapportée | 26,94 / 0,782 / 0,296 | **+0,074** | ×6,5 (A5000) | 15,7 min | oui | taux d'élagage | [Hanson 2024](../sources/hanson2024_speedy-splat/fiche.md) |
| **Mobile-GS** | **0,47 M** | **4,6 Mo** | 27,12 / 0,807 / 0,235 | +0,021 | 1125 (3090) ; **74 fps stables sur téléphone**, mono | 1,5 h + modèle professeur | **non** (sans tri + MLP d'opacité) | seuil d'élagage τ | [Du 2026](../sources/du2026_mobile-gs/fiche.md) |
| **Smol-GS** | ≈ 1 M (Garden, lu sur figure) | **5,9 Mo** | **27,76** / 0,807 / 0,248 | +0,034 | 210 (H200) | 27 min (H200) | **non** (4 MLP par vue) | λ_o (à l'entraînement) | [Wang 2025](../sources/wang2025_smol-gs/fiche.md) |
| **Reducing Memory Footprint** (Papantonakis) | 1,46 M (÷ 2,3) | 29 Mo | 27,10 / 0,809 / 0,226 | **+0,009** | 284 (A6000) ; **45 fps** sur téléphone (WebGL) | 25 min | oui, après décodage au chargement | profils Low / High | [Papantonakis 2024](../sources/papantonakis2024_reduced-memory/fiche.md) |
| **Compact3D** (Lee) | 1,39 M | 48,8 Mo | 27,08 / 0,798 / 0,247 | +0,025 | 128 (A100) | 33 min | **non** (couleur par grille de hachage + MLP) | masque appris | [Lee 2023](../sources/lee2023_compact3d/fiche.md) |
| **LightGaussian** | ≈ ⅓ de la base (élagage ≈ 66 %, nombre absolu non rapporté) | 45 Mo | 27,13 / 0,806 / 0,237 | +0,020 | 237 (A6000) | post-traitement | oui, après décodage | taux d'élagage | [Fan 2023](../sources/fan2023_lightgaussian/fiche.md) |

### Ce que ce tableau dit
- **Aucune méthode ne descend sous 0,5 M sans perte de qualité notable.** Les trois qui y arrivent (Taming, Mobile-GS, Speedy-Splat) coûtent entre +0,021 et +0,074 de LPIPS.
- **Taming est l'outil central de notre chaîne** : c'est le seul **budget exact** au **format standard**, et le plus rapide à entraîner. Il produit directement les paliers 150k / 300k / 500k de P6.
- **Mobile-GS a le meilleur compromis Gaussiennes/qualité** (0,47 M, +0,021) et il est **le seul mesuré sur un vrai SoC Qualcomm**. Mais il faut son propre rendu sans tri, et son MLP d'opacité dépend de la vue : même risque en stéréo que Smol-GS.
- **Papantonakis perd le moins de qualité** (+0,009) au format standard, mais il reste à 1,46 M : il faut le combiner avec autre chose pour tenir sur Quest.
- **Speedy-Splat élague le plus** (0,28 M) au prix du LPIPS. Ses deux astuces de rasteriseur (SnugBox, AccuTile) donnent déjà **×2 sans aucune perte** et se réutilisent indépendamment de l'élagage.
- **Smol-GS et Compact3D gagnent sur le disque**, pas sur le nombre de Gaussiennes affichées. Hors sujet pour le Quest, sauf comme format de transport (voir [piste_R0](piste_R0_microbench_smolgs.md)).

## Famille 2 : niveaux de détail (rendre moins selon le point de vue)

| Méthode | Principe | Chiffres | Intérêt pour nous | Source |
|---|---|---|---|---|
| **Hierarchical 3DGS** | Arbre de Gaussiennes agrégées ; seuil τ en pixels choisi à chaque image | 31–46 fps au réglage fin → 103–150 fps au réglage grossier (A6000, très grandes scènes) | **Bouton continu τ** : levier idéal pour P3′. +69 % de mémoire par Gaussienne | [Kerbl 2024](../sources/kerbl2024_hierarchical-3dgs/fiche.md) |
| **Octree-GS** | Niveaux cumulatifs dans un octree, fondu d'opacité entre niveaux | 56–57 contre 12–14 fps pour 3DGS (A100, MatrixCity) | Rasteriseur standard ; pas de bouton global (à ajouter) | [Ren 2024](../sources/ren2024_octree-gs/fiche.md) |
| **LapisGS** | Couches progressives (du grossier au fin) | pas de fps | Couches activables = levier discret ; streaming | [Shi 2024](../sources/shi2024_lapisgs/fiche.md) |
| **Multi-layer GS** (Kleinbeck) | Couches de contenu activables | 10,2–26,6 ms sur Quest 3 (≤ 196k) | Seule mesure native Quest 3 de la base | [Kleinbeck 2024](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md) |

La famille 1 agit **hors ligne** (un modèle plus petit), la famille 2 **à chaque image** (on choisit ce qu'on affiche). **P3′ a besoin de la famille 2** pour avoir des leviers à régler en direct.

## Famille 3 : rendre plus vite le même modèle (rasteriseurs)

| Méthode | Gain | Coût | Source |
|---|---|---|---|
| **StopThePop** | Tri par pixel : supprime le *popping*, ≈ 201 fps en 1080p (4090) | Légèrement plus lent que 3DGS | [Radl 2024](../sources/radl2024_stopthepop/fiche.md) |
| **FlashGS** | ×3,8 à ×6,6 (311–694 fps, 3090) | CUDA uniquement | [Feng 2024](../sources/feng2024_flashgs/fiche.md) |
| **SnugBox + AccuTile** (Speedy-Splat) | ×2 **sans perte** | Aucun | [Hanson 2024](../sources/hanson2024_speedy-splat/fiche.md) |
| **Tri partagé entre les yeux** | −42 % sur Quest 3, −4 à −6 % sur 4090 | Erreur stéréo non mesurée | [Kleinbeck 2024](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md) |
| **Fovéation** (VRSplat, VR-Splatting) | 72–90 Hz en PC-VR (4090) | Eye-tracking pour VR-Splatting | [Tu 2025](../sources/tu2025_vrsplat/fiche.md), [Franke 2024](../sources/franke2024_vr-splatting/fiche.md) |

⚠️ FlashGS et StopThePop sont en **CUDA** : ils ne tournent pas sur Quest. Ce sont leurs *idées* qu'on peut porter en HLSL.

## Chaîne recommandée (à valider sur le casque)

```
Photos → SfM (COLMAP)
   → Taming 3DGS, budget exact (150k / 300k / 500k)        [famille 1, format standard]
   → (option) réduction des SH et quantification façon Papantonakis   [disque ÷ 5-10, qualité quasi intacte]
   → UnityGaussianSplatting sur Quest 3
        + SnugBox/AccuTile, tri partagé entre les yeux       [famille 3, portés en HLSL]
        + niveaux de détail pilotés par P3′                   [famille 2]
```

Smol-GS, Mobile-GS et Compact3D restent **hors de cette chaîne** parce qu'ils sortent du format standard. Ils servent de points de comparaison, et Mobile-GS est le meilleur candidat si on quitte un jour le rendu trié.
