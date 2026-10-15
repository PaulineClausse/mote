---
citekey: jiang2024_vr-gs
mineru_doc: 294b63f
type: conférence   # préprint arXiv v2 (cs.HC), 12 p. ; venue non indiquée dans le texte
statut: fiche complète
tags: [3DGS, VR, physique, XPBD, hybride-maillage-gaussiennes, cage-tétraédrique, collisions, ombres-dynamiques, shadow-map, segmentation, inpainting, Unity, plugin-CUDA, Quest-Pro, RTX-4090, étude-utilisateurs, SUS, stéréo]
---

# VR-GS: A Physical Dynamics-Aware Interactive Gaussian Splatting System in Virtual Reality

**Référence :** Jiang, Y., Yu, C., Xie, T., Li, X., Feng, Y., Wang, H., Li, M., Lau, H., Gao, F., Yang, Y., Jiang, C. (2024). VR-GS: A Physical Dynamics-Aware Interactive Gaussian Splatting System in Virtual Reality. Préprint arXiv [2401.16663](https://arxiv.org/abs/2401.16663) (v2, 4 mai 2024 ; venue non indiquée dans le texte).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Un système VR (Unity + plugin CUDA, Quest Pro, RTX 4090) qui rend des scènes 3DGS reconstruites depuis des vidéos et les rend **physiquement interactives** : chaque objet segmenté est enveloppé dans une **cage tétraédrique non rendue**, simulée en XPBD (déformations, collisions), qui déforme les Gaussiennes par un plongement à deux niveaux. S'y ajoutent des ombres dynamiques par shadow map, de 24 à 161 fps selon la scène.

## Problème traité
- La création et l'édition de contenus 3D interactifs sont coûteuses et réservées aux experts (p. 1).
- NeRF est trop lent pour l'interaction et difficile à déformer. Le 3DGS est explicite, donc déformable. Mais la simulation par Gaussienne (PhysGaussian, MPM) est trop lente pour la VR (p. 2-3).
- Le 3DGS « cuit » les ombres dans les harmoniques sphériques : elles ne suivent plus un objet déplacé (p. 5). C'est la limite relevée par [Mirocha](../mirocha2025_beyond-dt/fiche.md).

## Méthode / contributions
- **Préparation hors ligne des assets (p. 4)** :
  - **Segmentation** : 3 attributs RGB appris en plus par Gaussienne, supervisés par des masques 2D (Cheng et al. 2023). Perte `L = (1−λ)L1 + λ L_SSIM + λ_seg L_seg`, avec λ = 0,2 et λ_seg = 0,1 (éq. 3, p. 4).
  - **Inpainting 3D** : guidé par LaMa (2D), sous la zone libérée quand on retire un objet (p. 4, Fig. 5).
  - **Maillage de simulation** : remplissage interne (PhysGaussian) → centres des Gaussiennes → VDB → marching cubes → TetGen. Ce maillage **n'est pas rendu**, il sert seulement de support à la dynamique (p. 4).
- **Simulation (p. 5)** : **XPBD** avec contraintes d'énergie de déformation (FEM) et amortissement ; paramètres physiques (E, ν, ρ) réglés à la main, en moins de 10 itérations d'essai.
- **Plongement à deux niveaux (p. 5, Fig. 3-4)** : chaque Gaussienne est enfermée dans un tétraèdre local serré. Les sommets de ce tétraèdre sont plongés dans la cage globale. Puis `μ = Σ w_i x_i`, `Σ = F Σ0 Fᵀ` (éq. 5). Cela supprime les artefacts « en pointes » du plongement naïf.
- **Ombres dynamiques (p. 5)** : shadow map calculée avec la même rasterisation 3DGS (profondeur depuis la lumière, test de visibilité par Gaussienne). La lumière est positionnable par l'utilisateur.
- **Interactions** : déformation, collisions entre objets et avec le décor (Ring Toss, Table Brick). Des **objets maillés Blender** (anneaux, briques) sont insérés dans une scène GS (p. 7) ; leur mode de rendu (maillage ou conversion en GS) n'est pas précisé. **Personnage GS animé** par un maillage de surface rigué via Mixamo, utilisé comme condition aux limites (« Just Dance », p. 7).
- **Implémentation (p. 6)** : **prototype Unity avec un plugin implémenté en CUDA**. Casque **Meta Quest Pro** + manettes. PC : **Intel i9-14900KF, 32 Go, NVIDIA RTX 4090**. Le mode de connexion du casque (Link/Air Link) n'est pas précisé.

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| FPS (système complet : simulation + rendu des 2 yeux) | Fox **161,2** ; Horse 115,4 ; Bear 76,9 ; Box Moving 73,8 ; Table Brick 41,4 ; Ring Toss 37,7 ; Animal Crossing 34,7 ; Just Dance 33,9 ; Toy Collection **24,3** | Table 1, p. 7 ; RTX 4090 + Quest Pro. **Résolution de rendu non rapportée** |
| Stéréo | **Œil gauche et œil droit rendus séparément.** Le rendu stéréo prend la majeure partie du temps de frame (≈ 86-97 % pour Fox, Horse, Box Moving), la simulation de ≈ 3 % à ≈ 47 % (Animal Crossing) | Fig. 13, p. 12 (lecture du graphique, valeurs approximatives) |
| Taille des scènes | 0,30 M (Fox) à **2,53 M** (Bear) Gaussiennes ; 1 434 à 46 428 sommets de cage ; 1-50 itérations XPBD par sous-pas | Table 1, p. 7 |
| Cage conseillée | 10 k à 30 k sommets (compromis fps / fidélité physique) | p. 6, Fig. 12 |
| Vitesse de simulation | VR-GS 0,017 / 0,022 / 0,021 contre PhysGaussian 0,112 / 0,219 / 0,39 et PAC-NeRF 0,750 / 0,813 / 0,625 (Stool / Chair / Materials) | Tableau p. 6, Δt_frame = 1/25 s, Δt_step = 10⁻⁴ s ; unité non précisée (vraisemblablement s par frame) |
| Qualité (PSNR / SSIM / LPIPS) | **non rapporté** (comparaison visuelle seulement, Fig. 7) | — |
| Temps capture → VR | ≈ **2 h 30** pour Toy Collection : mise en scène 20 min ; vidéo + COLMAP 60 min (dont COLMAP ≈ 40) ; segmentation 2 min ; inpainting 5 min ; entraînement 3DGS 30 000 itérations ≈ **30 min sur une RTX 4090** ; remplissage + VDB + TetGen < 10 min ; réglage Unity 20 min | p. 7 |
| Mémoire / VRAM | non rapporté | — |
| Latence (mesurée) | non rapporté ; seulement une note subjective « latency » (M7) ≈ 4,1/5, la plus faible et la plus dispersée des notes système | Fig. 14, p. 12 (lecture du graphique) |

**Étude utilisateurs (p. 7-8)** : **10 participants** (2 professionnels VFX, 8 novices). Tutoriel vidéo de 10 min, puis deux tâches :
- tâche 1 (30 min) : Ring Toss et Toy Collection, interaction physique contre interaction par simple transformation, en carré latin ;
- tâche 2 (30 min) : édition libre.

Mesures : **SUS**, Likert 7 points (immersion / réalisme), notes 1-5 par fonctionnalité, entretien semi-directif de 20 min. Résultats :
- **physique 6,1 contre transformation 4,8** (t apparié, p = 0,0227) ;
- facilité d'usage 4,6/5, satisfaction 4,8/5 ;
- **SUS = 83,5**, « excellent » selon Bangor et al. (p. 8).

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | **Unity + plugin natif CUDA** : cette architecture garde le contrôle du rasteriseur (shadow map, déformation par frame) tout en profitant de l'écosystème XR de Unity (p. 6). Même famille que les « plugin CUDA pour Unity » recensés par [Li 2025](../li2025_rf-xr-survey/fiche.md) |
| 2. Gaussiennes depuis SfM | Pipeline standard COLMAP → 3DGS (30 k itérations), enrichi d'une segmentation par Gaussienne (p. 4, 7). La mise à jour de la covariance par `F Σ0 Fᵀ` est une manipulation directe de la covariance anisotrope (éq. 5) |
| 3. Rendu, casque XR | Rendu stéréo naïf (2 passes complètes, Fig. 13) ; aucune optimisation de visibilité ; ombres dynamiques par shadow map compatible 3DGS. Les auteurs signalent eux-mêmes des problèmes de latence probables pour de grandes scènes dynamiques en « 2K » (p. 8) |
| 4. Évaluation | fps par scène avec décomposition du temps de frame (Fig. 13) ; protocole SUS + Likert + carré latin ; aucune métrique image |

## Pour (vis-à-vis de notre problématique)
- **Hybride maillage + Gaussiennes déjà démontré en VR** : maillage invisible pour la physique et les collisions, Gaussiennes pour l'apparence (p. 3-5). C'est exactement la séparation « géométrie fonctionnelle / apparence » de P5.
- **Animation de Gaussiennes pilotée par un maillage externe** (rig Mixamo, p. 7) : le mécanisme pour faire bouger des pièces 3DGS à partir de données cinématiques (par exemple des angles d'axes lus en OPC-UA) existe déjà.
- **Ombres dynamiques** cohérentes avec la rasterisation 3DGS (p. 5) : cela lève en partie la limite « éclairage figé » de [Mirocha](../mirocha2025_beyond-dt/fiche.md).
- **La décomposition du temps de frame (Fig. 13) montre que le rendu stéréo domine** : c'est un argument quantitatif direct pour **P2** (mutualisation stéréo). VR-GS ne mutualise rien entre les deux yeux.
- Temps capture → VR d'environ 2 h 30, dont 30 min d'entraînement (p. 7) : une base de comparaison réaliste.

## Contre / limites
- **Résolution par œil non rapportée**, pas de VRAM, pas de latence mesurée, pas de PSNR : on ne peut pas vérifier le critère « ≥ 30 fps en 1080p ».
- **RTX 4090** obligatoire (desktop haut de gamme) : rien sur casque autonome. Deux scènes sur neuf sont à ≤ 34,7 fps et Toy Collection tombe à **24,3 fps** (Table 1), sous notre seuil et très loin des ≥ 60 fps recommandés par [Kamdjou](../kamdjou2024_xr-dt-iiot/fiche.md).
- Pas de reprojection, de fovéation ni de culling par œil ; rendu stéréo séquentiel.
- Paramètres physiques réglés à la main (p. 5, 8) ; physique élastique seulement (pas de fluides ni de tissus).
- Étude utilisateurs petite (n = 10), sans questionnaire de présence ni de cybercinétose. Seule la note « latency » est un indicateur (subjectif) de confort.

## Idées à creuser pour une approche novatrice
- **Hypothèse (P5, cœur)** : remplacer l'entrée « utilisateur + XPBD » de VR-GS par un **flux de données industrielles**. Des variables OPC-UA (positions d'axes, états) piloteraient directement la cage ou un squelette rigide par pièce, en cinématique pure (plus simple et plus rapide que XPBD). Seules les Gaussiennes des pièces mobiles seraient mises à jour (éq. 5), le décor 3DGS restant statique.
- **Hypothèse (P2)** : sur la base de la Fig. 13, mutualiser projection et tri entre les deux yeux dans un pipeline de type VR-GS. Le gain attendu serait important, puisque le rendu stéréo pèse jusqu'à ≈ 90 % du temps de frame dans les scènes peu simulées.
- **Hypothèse (P3)** : faire varier dynamiquement la résolution de la cage (10-30 k sommets, p. 6) et le nombre de Gaussiennes selon un budget de temps de frame, pour garantir un plancher de fps.
- **Hypothèse** : réutiliser la segmentation par Gaussienne (éq. 2-3) pour étiqueter automatiquement les pièces mobiles d'une machine et les associer à des variables OPC-UA.

## Citations clés
> « we construct a tetrahedral cage for each segmented GS kernel group and embed these kernel groups into corresponding meshes. The deformed mesh, driven by XPBD, subsequently guides the deformation of the GS kernels. » (`doc:294b63f/tier:standard/page:2`)
> « These meshes will not be rendered during the interaction but only serve as the media of dynamics. » (`doc:294b63f/tier:standard/page:4`)
> « Our prototype, developed in Unity with a CUDA-implemented plugin, is tested using a Quest Pro Head-Mounted Display (HMD) [...] and an NVIDIA GeForce RTX 4090 GPU. » (`doc:294b63f/tier:standard/page:6`)
> « rendering high-fidelity Gaussian kernels in VR is computationally demanding. As a result, rendering generative dynamics in a large scene with 2K resolution might lead to potential latency issues » (`doc:294b63f/tier:standard/page:8`)
> Table 1 (fps par démo) : `doc:294b63f/tier:standard/page:7` ; Fig. 13 (décomposition œil gauche / œil droit / simulation) : `doc:294b63f/tier:standard/page:12`

## Liens
- [Kerbl 2023](../kerbl2023_3dgs/fiche.md) : 3DGS de base (30 k itérations, rasteriseur CUDA).
- [Mirocha 2025](../mirocha2025_beyond-dt/fiche.md) : limite « pas d'ombres dynamiques », partiellement résolue ici par shadow map.
- [Warsinke 2026](../warsinke2026_gs-mesh-dt-vr/fiche.md) : autre étude utilisateurs VR 3DGS (UEQ-S / IPQ / CSQ-VR). Les deux protocoles sont complémentaires.
- [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) : architecture DT + OPC-UA dans laquelle un VR-GS « piloté par données » s'insérerait (P5).
- [Tu 2025 (VRSplat)](../tu2025_vrsplat/fiche.md) et [Franke 2024](../franke2024_vr-splatting/fiche.md) : rendu 3DGS VR optimisé (fovéation, stéréo), complémentaire au pipeline naïf de VR-GS.
- [Huang 2024 (2DGS)](../huang2024_2dgs/fiche.md) : une géométrie de surface plus propre pourrait donner de meilleures cages ou collisions que les centres de Gaussiennes.
