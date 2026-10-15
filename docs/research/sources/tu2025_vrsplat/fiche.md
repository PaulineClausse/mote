---
citekey: tu2025_vrsplat
mineru_doc: e1e39fd
type: article de revue   # Proc. ACM Comput. Graph. Interact. Tech. (PACMCGIT)
statut: fiche complète
tags: [3dgs, vr, rendu-fovéal, popping, stopthepop, optimal-projection, mini-splatting, meta-quest-3, rtx-4090, étude-utilisateurs, stéréo, culling]
---

# VRSplat: Fast and Robust Gaussian Splatting for Virtual Reality

**Référence :** Xuechang Tu, Lukas Radl, Michael Steiner, Markus Steinberger, Bernhard Kerbl, Fernando de la Torre (2025). *VRSplat: Fast and Robust Gaussian Splatting for Virtual Reality.* Proc. ACM Comput. Graph. Interact. Tech. 8(1), 22 p. DOI [10.1145/3728311](https://doi.org/10.1145/3728311) · arXiv [2505.10144](https://arxiv.org/abs/2505.10144) · code : github.com/Cekavis/VRSplat (`doc:e1e39fd/tier:standard/page:1`, `page:15`)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Système de rendu 3DGS pour casque VR qui combine un modèle compact (Mini-Splatting), le tri hiérarchique par pixel de StopThePop (anti-popping) et l'Optimal Projection (anti-distorsion grand FOV), rendus abordables grâce à un rasteriseur **fovéal fixe en une seule passe** et à un culling par masque de visibilité OpenXR : ≥ 72 FPS stéréo sur Meta Quest 3 filaire + RTX 4090 (`page:1`, `page:2`).

## Problème traité
Trois défauts de 3DGS amplifiés en VR par le grand FOV, les micro-mouvements de tête et la haute résolution des HMD (`page:1`, `page:2`) :
1. **Popping** : le tri global par z de vue change pendant les rotations ; trier par distance ‖o−μ‖ (choix des viewers VR actuels, ex. MetalSplatter) déplace le popping vers les translations (`page:5`).
2. **Erreur de projection** : l'approximation affine locale (EWA, Zwicker 2001) n'est exacte qu'au centre de l'image ; en bordure d'un grand FOV elle produit Gaussiennes allongées (« god rays ») et nuages flottants, **différents entre œil gauche et œil droit** (floaters qui cassent la stéréo) (`page:5`, `page:11`).
3. **Débit** : trop de primitives (densification heuristique) pour tenir 72 FPS à résolution native (`page:5`).

## Méthode / contributions
- **Backbone compact** : Mini-Splatting (jusqu'à ~10× moins de Gaussiennes), choisi aussi pour sa distribution plus uniforme qui équilibre la charge par tuile. Méthode déclarée agnostique au modèle d'entrée (`page:3`, `page:6`).
- **Fine-tuning 5K itérations** (de 30K à 35K, sans densification) avec le rasteriseur StopThePop + Optimal Projection : le modèle doit réapprendre l'ordre de tri (−1,5 dB sans fine-tuning, récupéré après 5K it.) (`page:6`, `page:9`, `page:12`).
- **Optimal Projection intégrée au culling par tuile de StopThePop** : le maximum de contribution par tuile est calculé sur le plan tangent propre à chaque Gaussienne (tuiles projetées = quadrilatères convexes, max sur ≤ 2 arêtes, éq. 4), puis reprojeté en espace écran pour l'évaluation de profondeur par tuile (`page:7`).
- **Rendu fovéal en une passe** : partition en tuiles 32×32 ; au centre, chaque tuile est subdivisée en 4 sous-tuiles 16×16 (pleine résolution) ; en périphérie, blocs de 256 threads où chaque thread traite 2×2 pixels (demi-résolution). Assignation Gaussienne/tuile faite sur les tuiles 32×32 (moins de paires), le surcoût au centre étant absorbé par le culling hiérarchique de StopThePop. Tuiles hybrides en bordure avec masque de mélange continu ; périphérie : upsampling plus proche voisin + flou gaussien 3×3 contre l'aliasing (`page:8`, `page:9`).
- **Fovéation fixe, sans eye-tracking** : région centrale = moitié de l'image, 10 % de bande de transition ; le mapping des tuiles est **précalculé une fois par œil** et réutilisé à chaque frame car le Quest 3 n'a pas d'eye-tracking (`page:8`, `page:9`).
- **Culling par masque de visibilité HMD (OpenXR)** : bitfield par tuile + summed-area table pour compter exactement les tuiles visibles couvertes par chaque splat avant d'allouer le buffer de tri → −11 % de tuiles, −6 % de paires Gaussienne/tuile (`page:9`).
- Baseline « deux passes fovéales » optimisée (centre à pleine résolution avec frustum serré, périphérie basse résolution, bande de transition rendue deux fois) fournie pour comparaison (`page:17`, `page:18`).

## Résultats chiffrés
| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| Matériel | Meta Quest 3 **filaire** (tethered) sur desktop NVIDIA **RTX 4090**, CUDA 12.6, framework SIBR + OpenXR | `page:9`, `page:14` |
| Résolution | **2064 × 2272 par œil** (résolution native demandée par le Quest 3) ; 4615 tuiles 32×32 dont 1085 haute rés., 2921 basse rés., 102 hybrides, 507 invisibles | `page:9`, `page:13`, `page:14` |
| Cible | **72 FPS ≈ 14 ms** par frame stéréo | `page:14` |
| Temps de frame stéréo (Ours) | 8,14 ms (Deep Blending) · 12,36 ms (Mip-NeRF 360 indoor) · 10,47 ms (outdoor) · 9,22 ms (T&T) ; par scène 7,88 ms (DrJ) à **14,11 ms (Counter, > budget)** | 2 images 2064×2272 ; **timings mono doublés** pour simuler la stéréo, trajectoire interpolée, moyenne sur 4 runs (`page:13`, `page:14`, `page:15`) |
| Ablation temps (moyenne Mip-360 indoor) | 3DGS 8,06 · Mini-Splatting 6,24 · MS+StopThePop 14,48 · Ours sans fovéation 20,48 · Ours deux passes 15,01 · **Ours 12,36 ms** | idem (`page:14`) |
| Gain fovéation 1 passe | ≈ 1,6–1,8× vs sans fovéation (ex. Bicycle 15,92 → 10,14 ms) ; ≈ 1,2× vs deux passes (12,39 → 10,14 ms) | `page:15` |
| Qualité protocole standard | Mip-360 : PSNR 27,29 / SSIM 0,823 / LPIPS 0,212 ; T&T : 22,90 / 0,836 / 0,197 ; DB : 30,33 / 0,912 / 0,242 (Ours z) — ≈ Mini-Splatting, légèrement < 3DGS sur T&T (23,73) | focale d'origine (`page:21`) |
| Qualité protocole « grand FOV » | Mip-360 27,29 dB vs 3DGS 26,82 / Mini-Splatting(z) 24,77 ; **T&T 22,90 vs 3DGS 17,11** ; DB 30,33 vs 26,19 | focale ÷3, résolution ×3, crop central pixel-exact (`page:11`, `page:12`, `page:18`) |
| FLIP (ablation fine-tuning) | 0,150 (5K it.) vs 0,146 Mini-Splatting ; sans fine-tuning 0,184 | moyenne toutes scènes (`page:18`) |
| Nb de Gaussiennes | 0,19 M (Train) à 1,00 M (Stump) vs 1,05–5,95 M pour 3DGS (Truck : ÷12 → ×2,11 plus rapide ; Counter : ÷3 → ×1,15) | `page:14`, `page:15` |
| Temps d'entraînement | Non rapporté en minutes ; fine-tuning = 5K itérations, « petite fraction » de la reconstruction initiale | `page:6`, `page:9` |
| Mémoire / taille | Non rapporté (seulement nb de Gaussiennes) | — |
| Latence | **Non rapportée** (ni motion-to-photon, ni latence d'affichage) | — |
| Étude utilisateurs | **25 participants** (23–57 ans ; 9 n'avaient jamais utilisé de casque), Quest 3, comparaisons par paires Ours vs Mini-Splatting (z) et Ours vs Mini-Splatting (Dist), 4 scènes (Bonsai, Bicycle, Dr Johnson, Truck), Likert 5 points, ~90 s par condition, 20–30 min par session, tests de Wilcoxon | `page:9`, `page:10`, `page:18` |
| Résultats étude | vs MS(z) : préférence t=18,0 p<0,001, artefacts t=0,0 p<0,001, qualité n.s. (p=0,62) ; vs MS(Dist) : préférence t=61,0 p<0,001, artefacts t=15,0 p<0,001, qualité t=121,0 p<0,03 ; 6/25 cybermalaise léger, 20/25 « très » à « complètement » satisfaits | `page:10`, `page:18` |

## Artefacts VR identifiés et traitement
| Artefact | Cause | Traitement |
|---|---|---|
| Popping (rotations/translations de tête) | tri global par primitive | tri hiérarchique par pixel **StopThePop** + fine-tuning (`page:6`) |
| Gaussiennes allongées / nuages en périphérie, incohérents entre yeux | approximation affine locale, grand FOV | **Optimal Projection** (Huang et al. 2024) intégrée au culling (`page:7`) |
| Aliasing en périphérie basse résolution | demi-résolution | flou gaussien 3×3 après upsampling (`page:9`) |
| Discontinuité fovéa/périphérie | changement de résolution | tuiles hybrides + masque de mélange continu (`page:8`, `page:9`) |
| Flicker résiduel | tri hiérarchique approximatif dans géométries complexes | **non résolu** ; pistes : LOD robuste ou rendu volumique exact / ray tracing (jugé trop cher) (`page:15`) |

Réutilisations : **StopThePop** = cœur du rasteriseur (tri + culling hiérarchique, co-auteurs communs Radl/Steiner/Steinberger/Kerbl) ; **Mip-Splatting** seulement cité parmi les travaux « artifact-free » (`page:3`), **non utilisé** ; **Speedy-Splat** non cité ; RTGS (Lin et al. 2024, fovéation par LOD entraîné sur mobile) décrit comme complémentaire (`page:4`).

## Stéréo (piste P2) — verdict
- Les deux yeux sont **rendus indépendamment** : les timings sont ceux d'une vue **multipliés par deux** (`page:13`) ; seul le mapping fovéal est précalculé par œil (`page:8`).
- Les auteurs listent explicitement comme **travail futur** : « monocular rendering and stereoscopic reuse of distant content, and the fusion of stereo rendering passes » (`page:15`).
- **Verdict P2 : non réalisée par VRSplat, et identifiée par les auteurs eux-mêmes comme ouverte** → piste confirmée mais visible (concurrence probable du même groupe TU Graz/CMU). Attention : avec StopThePop le tri est **par pixel/tuile**, donc un tri unique partagé n'est pas trivial ; le partage réaliste porte sur le pré-traitement par Gaussienne (culling, SH/couleur, covariance 3D) et sur le contenu lointain (disparité faible).

## Fovéation / edge (piste P1) — verdict
- Fovéation **fixe** (pas d'eye-tracking), **locale sur un même GPU**, **un seul modèle** rendu à deux résolutions ; pas de rendu déporté ni de split casque/edge : le « casque » n'est qu'un afficheur filaire, tout est calculé sur la RTX 4090 (`page:9`).
- Aucun critère de profondeur/distance pour partitionner (partition purement en espace écran).
- **Verdict P1 : non réalisée** ; VRSplat fournit la brique « fovéation en une passe dans un rasteriseur à tuiles » mais pas le partage casque/edge par visibilité. Casque autonome : **non traité**.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Référence centrale : chaîne SIBR + OpenXR + Quest 3 filaire + RTX 4090 ; cible 72 FPS/14 ms stéréo ; revue RTGS, VR-GS, FoV-NeRF, VR-NeRF (`page:3`, `page:4`) |
| 2. Gaussiennes 3D depuis SfM, covariance anisotrope | Réutilise Mini-Splatting ; fine-tuning court adapté au rasteriseur ; montre que l'ordre de tri appris doit correspondre à celui du rendu (`page:6`) |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | **Cœur** : projection anisotrope exacte (Optimal Projection), culling par tuile, masque de visibilité HMD, fovéation 1 passe |
| 4. Évaluation (fps, latence, qualité, coût) | Protocole « grand FOV » reproductible ; étude utilisateurs 25 p. ; **pas de latence ni de coût énergétique** |

## Pour (vis-à-vis de notre problématique)
- Seul papier à la fois ≥ 72 FPS stéréo à résolution native Quest 3 (2 × 4,69 Mpx, soit > 2× la surface 1080p par œil) **et** sans popping ni floaters stéréo-incohérents.
- Chiffres détaillés par étape et par scène, code public : baseline directement reproductible.
- Protocole d'évaluation grand FOV qui met en évidence les erreurs invisibles en évaluation standard (T&T : 17,1 → 22,9 dB).
- Approche agnostique au modèle d'entrée : compatible avec d'autres compressions/élagages (LightGaussian, Taming 3DGS…).

## Contre / limites
- **GPU desktop RTX 4090** : aucun résultat sur casque autonome ou mobile ; marge faible (Counter 14,11 ms > 14 ms ; Bonsai non plus rapide que 3DGS à cause du tri par pixel) (`page:14`, `page:15`).
- Stéréo **simulée** par doublement des timings mono pour les mesures (`page:13`).
- Aucune mesure de latence, de mémoire, d'énergie.
- Fovéation fixe large (moitié de l'image) : gain limité par rapport à un eye-tracking.
- Flicker résiduel du tri hiérarchique approximatif (`page:15`).
- Étude utilisateurs sans comparaison directe à 3DGS vanilla (`page:11`).

## Idées à creuser pour une approche novatrice
- *Hypothèse (P2)* : partager entre les deux yeux les étapes par Gaussienne (culling frustum union, évaluation SH, covariance 3D) et ne dupliquer que la projection/tri par tuile ; rendre une seule fois le contenu lointain (disparité < 1 px) — c'est exactement le « future work » des auteurs, à attaquer vite.
- *Hypothèse (P1)* : remplacer la partition écran fixe de VRSplat par une partition **profondeur × excentricité** : casque = tuiles centrales/proches, edge = périphérie/lointain, en réutilisant le mapping de tuiles précalculé par œil comme contrat de composition.
- *Hypothèse (P3)* : piloter la taille de la région centrale (actuellement 50 % + 10 %) et le seuil de culling par un contrôleur QoS pour garantir 14 ms même sur les scènes type Counter/Bonsai.
- *Hypothèse* : porter la fovéation 1 passe + masque de visibilité sur un rasteriseur mobile (cf. [NEO](../oh2025_neo-on-device/fiche.md), [Mobile-GS](../du2026_mobile-gs/fiche.md)) pour tester la faisabilité sur casque autonome.
- *Hypothèse* : réutiliser le protocole « grand FOV » (focale ÷3, résolution ×3) comme métrique standard de notre évaluation (étape 4).

## Citations clés
> « VRSplat is the first, systematically evaluated 3DGS approach capable of supporting modern VR applications, achieving 72+ FPS while eliminating popping and stereo-disrupting floaters. » (`doc:e1e39fd/tier:standard/page:2`)

> « The images were rendered in the resolution as requested by the Meta Quest 3, i.e. 2064×2272, and timings were doubled to recreate the stereoscopic setting. » (`doc:e1e39fd/tier:standard/page:13`)

> « Consumer-grade HMDs, like the Meta Quest 3, often do not provide eye tracking, thus we can precompute this mapping once for each eye and re-use it across frames. » (`doc:e1e39fd/tier:standard/page:8`)

> « There are also areas for optimization in our VR rendering pipeline, such as monocular rendering and stereoscopic reuse of distant content, and the fusion of stereo rendering passes to maximize synergy effects. » (`doc:e1e39fd/tier:standard/page:15`)

## Liens
- Papiers liés :
  - [StopThePop](../radl2024_stopthepop/fiche.md) — rasteriseur trié réutilisé tel quel (tri + culling hiérarchique).
  - [VR-Splatting](../franke2024_vr-splatting/fiche.md) — alternative concurrente : fovéation par eye-tracking, hybride 3DGS/points neuronaux, 90 Hz.
  - [3DGS](../kerbl2023_3dgs/fiche.md) — baseline et rasteriseur d'origine.
  - [Mip-Splatting](../yu2023_mip-splatting/fiche.md) — cité, non utilisé (VRSplat traite l'aliasing périphérique par un flou 3×3).
  - [Speedy-Splat](../hanson2024_speedy-splat/fiche.md) — non cité ; son culling serré serait complémentaire.
  - [VR-GS](../jiang2024_vr-gs/fiche.md) — VRSplat se présente comme remplaçant « drop-in » de son rendu.
  - [A3FR (fovéal)](../xin2025_a3fr-foveated/fiche.md), [Hierarchical 3DGS](../kerbl2024_hierarchical-3dgs/fiche.md) (LOD cité comme remède au flicker), [LightGaussian](../fan2023_lightgaussian/fiche.md), [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md) (réduction de primitives citées).
  - [Edge collaboratif GS](../wan2025_edge-collab-gs/fiche.md) — pour la partie P1 non couverte ici.
