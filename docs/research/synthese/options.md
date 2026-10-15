# Synthèse — options techniques et pistes novatrices

Document vivant, mis à jour à chaque nouvelle fiche. Dernière mise à jour : 2026-09-29, après **35 fiches** et une vérification d'antériorité ([anteriorite_p3_p6.md](anteriorite_p3_p6.md)).

Documents associés : [note_encadrant.md](note_encadrant.md) (cadrage, 1 page) · [plan_environnement.md](plan_environnement.md) (étape 1, Quest 3 + PC de l'école) · [faisabilite_quest3.md](faisabilite_quest3.md) (budget réaliste sur Quest 3) · [comparatif_methodes.md](comparatif_methodes.md) (tableau chiffré des méthodes et chaîne recommandée) · [piste_R0_microbench_smolgs.md](piste_R0_microbench_smolgs.md) (piste P7 en réserve).

**Légende :** ✅ l'information vient d'une fiche de la base (lien donné) · 🔎 papier cité mais **pas encore dans la base**, donc à sourcer.
Navigation : [INDEX.md](../INDEX.md) liste toutes les fiches.

## 1. Contraintes

| Contrainte | Valeur | Origine |
|---|---|---|
| Fréquence | ≥ 30 fps | sujet |
| Résolution | 1080p | sujet (par œil ou total ? à clarifier) |
| Entrée | photos multiples ou vidéo | sujet |
| Coût | calcul optimisé pour la XR, sans entraînement neuronal lourd | sujet |
| Seuils XR usuels | ≥ 60 fps, latence < 20 ms | ✅ [Kamdjou, Table 2](../sources/kamdjou2024_xr-dt-iiot/fiche.md) (la table contient des coquilles) |
| Résolution native d'un casque actuel | Quest 3 : 2064×2272 par œil (VRSplat), 2064×2208 (Nebula) ; Vive Pro Eye : 2016×2240 | ✅ [VRSplat](../sources/tu2025_vrsplat/fiche.md), [Nebula](../sources/zhu2025_nebula/fiche.md), [VR-Splatting](../sources/franke2024_vr-splatting/fiche.md) |
| Fréquence cible des casques | 72 Hz (≈ 14 ms en stéréo) à 90 Hz (≈ 11 ms) | ✅ VRSplat, VR-Splatting |

**Conclusion :** « ≥ 30 fps en 1080p » est une cible **déjà atteinte, et largement, sur GPU desktop** (§2). La vraie difficulté est de rendre **en stéréo, à la résolution et à la fréquence d'un casque, avec une faible latence**, idéalement sur un casque autonome. C'est sur ce point que la base montre un vide, surtout pour des **scènes réelles de taille réaliste**.

## 2. Ce que la base mesure (performances publiées par plateforme)

| Plateforme | Méthode | Performance | Résolution / vue | Mesure | Source |
|---|---|---|---|---|---|
| GPU desktop, mono | 3DGS | 134 à 197 fps (A6000) | natif dataset | réelle | ✅ [Kerbl 2023](../sources/kerbl2023_3dgs/fiche.md) |
| | StopThePop | ≈ 201 fps (4090) | 1080p | réelle | ✅ [Radl 2024](../sources/radl2024_stopthepop/fiche.md) |
| | FlashGS | 311 à 694 fps (3090), ×3,8 à ×6,6 vs 3DGS | 1080p | réelle | ✅ [Feng 2024](../sources/feng2024_flashgs/fiche.md) |
| | Speedy-Splat | 898 fps en moyenne (A5000), ×6,7 | non rapportée | réelle | ✅ [Hanson 2024](../sources/hanson2024_speedy-splat/fiche.md) |
| | LightGaussian | 144 → 237 fps, ×15 plus compact | non rapportée | réelle | ✅ [Fan 2023](../sources/fan2023_lightgaussian/fiche.md) |
| | Hierarchical 3DGS | 31 à 46 fps au réglage fin, 103 à 150 fps au réglage grossier (A6000), sur de très grandes scènes | non rapportée | réelle | ✅ [Kerbl 2024](../sources/kerbl2024_hierarchical-3dgs/fiche.md) |
| | Octree-GS (LOD explicite) | 56 à 57 fps contre 12 à 14 pour 3DGS (A100, MatrixCity) | 2K | réelle | ✅ [Ren 2024](../sources/ren2024_octree-gs/fiche.md) |
| | Reducing Memory Footprint | 178 → 284 fps ; disque ×26 à ×35 (A6000) ; **WebGL sur téléphone : 16 → 45 fps** | non rapportée | réelle | ✅ [Papantonakis 2024](../sources/papantonakis2024_reduced-memory/fiche.md) |
| **PC-VR, stéréo** | VRSplat | 8,1 à 12,4 ms en stéréo (4090 + Quest 3), dans le budget de 72 Hz | 2064×2272 | stéréo **simulée** (temps mono × 2) | ✅ [Tu 2025](../sources/tu2025_vrsplat/fiche.md) |
| | VR-Splatting (fovéal, eye-tracking) | 10,9 ms (4090 + Vive Pro Eye), dans le budget de 90 Hz | 2016×2240 | réelle | ✅ [Franke 2024](../sources/franke2024_vr-splatting/fiche.md) |
| | VR-GS (physique) | 24 à 161 fps (4090 + Quest Pro) | non rapportée | réelle | ✅ [Jiang 2024](../sources/jiang2024_vr-gs/fiche.md) |
| | Multi-layer GS (Unity, tri partagé entre les yeux) | 1,3 à 1,7 ms en stéréo 2×2000² (4090) ; 2,5 à 3,6 ms (Varjo Aero) | 2000×2000 par œil / natif | réelle, petites scènes (57k à 196k Gaussiennes) | ✅ [Kleinbeck 2024](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md) (le chiffre « > 100 fps en 2064×2208 » attribué par Li 2025 est erroné) |
| | FoV-NeRF (NeRF fovéal) | 21,5 ms en stéréo, ≈ 46 fps (3090 + Vive Pro Eye) | 1440×1600 par œil | réelle | ✅ [Deng 2021](../sources/deng2021_fov-nerf/fiche.md) |
| **Casque autonome, stéréo** | Multi-layer GS (Unity, Aras) | **10,2 à 26,6 ms, soit ≈ 38 à 98 fps, sur Quest 3 en natif** ; le tri partagé entre les yeux fait gagner ≈ 40 % | résolution native Quest 3 | **réelle**, petites scènes (57k à 196k Gaussiennes) | ✅ [Kleinbeck 2024](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md) |
| **Mobile réel** | Mobile-GS (sans tri) | 127 fps au démarrage, **74 fps en régime thermique stable**, 0,83 W | ≈ 1600×1063, mono | réelle (Snapdragon 8 Gen 3) | ✅ [Du 2026](../sources/du2026_mobile-gs/fiche.md) |
| | WebSplatter (WebGPU) | ≈ 30 fps (Snapdragon 8 Gen 3), ≈ 26 fps (iPhone 15 Pro Max) | non rapportée, mono | réelle | ✅ [Han 2026](../sources/han2026_websplatter/fiche.md) |
| | A3FR (fovéal) | 18 à 26 fps (Orin NX **émulé**) | 1080p, mono | émulée | ✅ [Xin 2025](../sources/xin2025_a3fr-foveated/fiche.md) |
| **Accélérateur matériel (ASIC)** | Nebula | 70,1 fps **en stéréo** | 2064×2208 | **simulée** (RTL) | ✅ [Zhu 2025](../sources/zhu2025_nebula/fiche.md) |
| | Neo | 99 fps | 2560×1440, mono | **simulée** (cycle-accurate) | ✅ [Oh 2025](../sources/oh2025_neo-on-device/fiche.md) |
| **Edge + pixels** | ECO-GS | latence garantie < 60 ms, +1,3 dB vs tout local | mono, client PC | réseau **simulé** | ✅ [Wan 2025](../sources/wan2025_edge-collab-gs/fiche.md) |
| | NeARportation (NeRF déporté, vidéo VP8 par œil) | 35 à 40 fps, **latence aller-retour de 100 à 400 ms** | full HD stéréo, afficheur autostéréoscopique | réseau **réel** (Wi-Fi) | ✅ [Hiroi 2022](../sources/hiroi2022_nearportation/fiche.md) |

**Le trou dans la littérature :** un seul papier mesure du 3DGS stéréo natif sur casque autonome ([Kleinbeck 2024](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md), Quest 3, 38 à 98 fps), et seulement sur des **scènes-jouets de 57k à 196k Gaussiennes**. Les scènes réelles en comptent de 0,3 à 6 M. Aucun papier ne mesure la **latence motion-to-photon réelle** en 3DGS. Les autres résultats sont sur PC-VR (4090), en mono sur téléphone, ou en simulation matérielle. Le seul rendu déporté mesuré sur un vrai réseau (NeARportation, en NeRF) atteint 100 à 400 ms, soit 5 à 20 fois le seuil XR. ✅ constat convergent de [Li 2025](../sources/li2025_rf-xr-survey/fiche.md), [Mobile-GS](../sources/du2026_mobile-gs/fiche.md), [Nebula](../sources/zhu2025_nebula/fiche.md) et [Warsinke 2026](../sources/warsinke2026_gs-mesh-dt-vr/fiche.md).

## 3. Enseignements transverses

1. **Le coût suit le nombre de Gaussiennes rendues, pas la taille du fichier.** Compact3D réduit le disque de 95 % mais la VRAM de seulement 5 à 19 %. La fovéation par pixels (A3FR) plafonne parce que le prétraitement et le tri restent entiers (≈ 37 % du temps). ✅ [Lee 2023](../sources/lee2023_compact3d/fiche.md), [Xin 2025](../sources/xin2025_a3fr-foveated/fiche.md)
2. **Une fois le tri optimisé, le rendu par pixel (donc par œil) domine.** Avec StopThePop, le tri global ne pèse plus que ≈ 6 % du temps et le rendu 72 %. Neo en logiciel ne gagne que ×1,1. Sur GPU desktop, c'est la rastérisation qui limite. **Nuance sur GPU mobile** : partager le tri entre les deux yeux fait gagner ≈ 40 % sur Quest 3, contre 4 à 6 % sur 4090. ✅ [Radl 2024](../sources/radl2024_stopthepop/fiche.md), [Oh 2025](../sources/oh2025_neo-on-device/fiche.md), [Han 2026](../sources/han2026_websplatter/fiche.md), [Kleinbeck 2024](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md)
3. **Le popping est un défaut majeur en VR** (rotation de tête, amplifié par les lentilles). Les deux systèmes VR de référence reposent sur StopThePop. ✅ [Tu 2025](../sources/tu2025_vrsplat/fiche.md), [Franke 2024](../sources/franke2024_vr-splatting/fiche.md)
4. **L'aliasing aux changements d'échelle** (l'utilisateur s'approche ou se penche) est corrigé par Mip-Splatting sans coût de rendu revendiqué. ✅ [Yu 2023](../sources/yu2023_mip-splatting/fiche.md)
5. **L'entraînement n'est plus le verrou principal.** Taming 3DGS descend à 7-11 min au lieu de 28-43 min, avec 5× moins de Gaussiennes et < 10 GB de VRAM. 3DGS à 7K itérations prend 4 à 7 min. La chaîne capture → Unity tient en ≈ 10 min. ✅ [Mallick 2024](../sources/mallick2024_taming-3dgs/fiche.md), [Kerbl 2023](../sources/kerbl2023_3dgs/fiche.md), [Shukhratov 2025](../sources/shukhratov2025_capture-interact-unity/fiche.md)
6. **Les leviers de réglage qualité/coût existent, mais aucun n'est piloté en ligne par un objectif** :
   - le seuil de granularité τ de Hierarchical 3DGS ;
   - le budget B de Taming ;
   - les taux d'élagage de LightGaussian et Speedy-Splat ;
   - les couches de LapisGS ;
   - le seuil τ* et la fenêtre w de Nebula ;
   - le niveau de LOD par distance d'Octree-GS (sans bouton global) ;
   - les couches activables de Multi-layer GS.

   ✅ fiches correspondantes. Kerbl 2024 cite explicitement le LOD dynamique « à budget de ressources » comme travail futur. Les précédents formels (FoV-NeRF, ECO-GS, Liu 2025) optimisent **hors ligne** ou **côté radio** seulement.
7. **Deux familles de leviers, à ne pas confondre.** La quantification réduit le disque et la bande passante **sans changer le fps**. L'élagage et le LOD changent le fps. Dans l'éq. 1 de Kamdjou, la compression est donc une variable réseau/mémoire, et le LOD ou le budget une variable de temps d'image. ✅ [Papantonakis 2024](../sources/papantonakis2024_reduced-memory/fiche.md)
8. **Le rendu 100 % déporté en pixels ne tient pas la latence XR** sur un vrai réseau (100 à 400 ms pour NeARportation). Il faut du rendu local, au moins pour la fovéa, et de la reprojection. ✅ [Hiroi 2022](../sources/hiroi2022_nearportation/fiche.md)

## 4. Options par axe

### A. Représentation et entraînement (étape 2)

| Option | Pour | Contre | Sources |
|---|---|---|---|
| **A1. 3DGS original** (initialisation SfM, Σ = R S Sᵀ Rᵀ, densification adaptative) | Référence ; sans SfM : −5,6 dB | 270 à 734 MB, 1 à 5 M de Gaussiennes, > 20 GB de VRAM à l'entraînement, popping | ✅ [Kerbl 2023](../sources/kerbl2023_3dgs/fiche.md) |
| **A2. Entraînement sous budget** (Taming) | 7 à 11 min, budget exact de Gaussiennes, qualité ≈ 3DGS | LPIPS dégradé sous budget serré, budget fixé à la main | ✅ [Mallick 2024](../sources/mallick2024_taming-3dgs/fiche.md) |
| **A3. Compression / élagage** (Reducing Memory Footprint, LightGaussian, Compact3D, Speedy-Splat) | **Papantonakis : ×26 à ×35, format 3DGS standard, fps ×1,6 à ×1,9, LPIPS +0,002 à +0,010, démontré sur téléphone en WebGL.** LightGaussian (×15) est un post-traitement de modèles existants | Papantonakis demande de ré-entraîner ; Compact3D n'est pas compatible avec un rasteriseur standard (MLP) ; LPIPS +0,02 à +0,07 pour LightGaussian et Speedy-Splat | ✅ [Papantonakis](../sources/papantonakis2024_reduced-memory/fiche.md), [Fan](../sources/fan2023_lightgaussian/fiche.md), [Lee](../sources/lee2023_compact3d/fiche.md), [Hanson](../sources/hanson2024_speedy-splat/fiche.md) |
| **A3′. Compression neuronale extrême** (Smol-GS) | **5,9 MB** sur Mip-360 (÷125 par rapport à 3DGS, ÷5 par rapport à Papantonakis), PSNR 27,76 ; plus rapide que 3DGS sur H200 (210 contre 139 fps), sans doute par compaction (≈ 1 M Gaussiennes sur Garden) ; **format de transport idéal pour P4/P1′** | LPIPS 0,248 contre 0,214 pour 3DGS ; **4 MLP par splat et par vue** (couleur, opacité, **rotation, échelle**), donc format non standard, coût doublé en stéréo, non portable tel quel sur Quest ; testé sur H200 uniquement | ✅ [Wang 2025](../sources/wang2025_smol-gs/fiche.md) |
| **A4. Anti-aliasing** (Mip-Splatting) | +4 dB en zoom avant ou arrière, pas de surcoût au rendu | Aucune mesure de fps | ✅ [Yu 2023](../sources/yu2023_mip-splatting/fiche.md) |
| **A5. Géométrie : 2DGS / hybride maillage** | Chamfer 0,80 contre 1,96 ; permet collisions et occlusion en MR | −0,17 dB ; fps non rapportés ; maillage extrait hors ligne | ✅ [Huang 2024](../sources/huang2024_2dgs/fiche.md), [Jiang 2024](../sources/jiang2024_vr-gs/fiche.md) |
| **A6. Représentation mobile sans tri** (Mobile-GS) | 74 fps stables sur téléphone, 4,6 MB | Entraînement de 1,5 h avec un modèle professeur ; MLP d'opacité dépendant de la vue (risque en stéréo) | ✅ [Du 2026](../sources/du2026_mobile-gs/fiche.md) |
| **A7. Initialisation LiDAR/SLAM** | Échelle et géométrie « digne d'un jumeau numérique » | Matériel dédié | ✅ [Mirocha 2025](../sources/mirocha2025_beyond-dt/fiche.md) |

### B. Rendu et intégration XR (étape 3)

| Option | Pour | Contre | Sources |
|---|---|---|---|
| **B1. PC-VR + rasteriseur CUDA optimisé** (StopThePop, AccuTile, FlashGS) | 72 à 90 Hz atteints sur 4090 (VRSplat, VR-Splatting) ; code public | GPU haut de gamme filaire ; stéréo parfois simulée | ✅ [Tu](../sources/tu2025_vrsplat/fiche.md), [Franke](../sources/franke2024_vr-splatting/fiche.md), [Radl](../sources/radl2024_stopthepop/fiche.md), [Feng](../sources/feng2024_flashgs/fiche.md) |
| **B2. Unity + plugin** (UnityGaussianSplatting d'Aras P.) | Écosystème OpenXR, interaction, maillages ; utilisé par 3 papiers | Moins de contrôle ; pas d'ombres dynamiques | ✅ [Mirocha](../sources/mirocha2025_beyond-dt/fiche.md), [Warsinke](../sources/warsinke2026_gs-mesh-dt-vr/fiche.md), [Shukhratov](../sources/shukhratov2025_capture-interact-unity/fiche.md) |
| **B3. Natif sur casque autonome** (Unity + Aras, HLSL compute) | Aucun réseau ; **38 à 98 fps en stéréo sur Quest 3** (Kleinbeck), code public ; le tri partagé entre les yeux fait gagner ≈ 40 % | Scènes-jouets seulement (≤ 196k Gaussiennes) ; au mieux 74 fps mono sur téléphone pour les scènes réelles (Mobile-GS) | ✅ [Kleinbeck 2024](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md), [Du 2026](../sources/du2026_mobile-gs/fiche.md) |
| **B4. WebGPU / WebXR** | Multi-appareils, code disponible | ≈ 30 fps mono sur téléphone ; WebXR non testé | ✅ [Han 2026](../sources/han2026_websplatter/fiche.md) |
| **B5. Rendu fovéal** (fixe ou par eye-tracking) | VRSplat : fovéation fixe en une passe ; VR-Splatting : 90 Hz | Eye-tracking requis ; la fovéation par pixels plafonne (A3FR) | ✅ [Tu](../sources/tu2025_vrsplat/fiche.md), [Franke](../sources/franke2024_vr-splatting/fiche.md), [Xin](../sources/xin2025_a3fr-foveated/fiche.md) |
| **B6. LOD hiérarchique** (Hierarchical 3DGS) | Bouton continu τ en pixels, réponse en fps mesurée ; anti-popping entre niveaux | +69 % de mémoire par Gaussienne ; plus lent que 3DGS sans réduction ; pensé pour le PC et les scènes de plusieurs km | ✅ [Kerbl 2024](../sources/kerbl2024_hierarchical-3dgs/fiche.md) |
| **B6′. LOD par octree** (Octree-GS, variante 3D explicite) | Niveaux cumulatifs avec fondu d'opacité ; rasteriseur standard ; ×4 en fps sur MatrixCity | Pas de bouton global (à ajouter : ΔL) ; 418 MB ; fps non rapportés sur les datasets usuels | ✅ [Ren 2024](../sources/ren2024_octree-gs/fiche.md) |
| **B7. Collaboratif cloud/casque par Δcut** | 19× moins de bande passante que la vidéo H.265, stéréo partagée | Nécessite un ASIC simulé ; < 10 fps sur un GPU mobile seul | ✅ [Zhu 2025](../sources/zhu2025_nebula/fiche.md) |
| **B8. Edge + pixels avec contrôleur** | Modèle d'optimisation formel, solveur temps réel | 60 ms de latence, pas de reprojection, réseau simulé | ✅ [Wan 2025](../sources/wan2025_edge-collab-gs/fiche.md) |
| **B9. Streaming progressif par couches** (LapisGS) | Dégradation gracieuse, transitions sans popping | Pas de réseau ni de fps mesurés ; LPIPS pleine résolution moins bon que 3DGS | ✅ [Shi 2024](../sources/shi2024_lapisgs/fiche.md) |
| **B10. Fovéal perceptuel + stéréo en périphérie** (FoV-NeRF) | Bornes chiffrées 20°/45°/110° ; périphérie rendue une fois depuis le point milieu des yeux puis décalée (−20 %) ; périphérie dépendante de la seule tête | NeRF : les gains par pixel ne se transposent pas tels quels au 3DGS | ✅ [Deng 2021](../sources/deng2021_fov-nerf/fiche.md) |

### C. Évaluation (étape 4)

- **Datasets :** Mip-NeRF 360, Tanks & Temples, Deep Blending ✅.
- **Protocole « grand champ de vision »** de VRSplat : focale ÷3, résolution ×3, crop central ✅ [Tu](../sources/tu2025_vrsplat/fiche.md).
- **Qualité :** PSNR, SSIM, LPIPS, plus **FLIP temporel** pour le popping ✅ [Radl](../sources/radl2024_stopthepop/fiche.md), et **JOD FovVideoVDP** pour le fovéal ✅ [Franke](../sources/franke2024_vr-splatting/fiche.md).
- **Protocole de latence** : horodatage de la pose renvoyé avec l'image, pour décomposer rendu et réseau sur une seule horloge ✅ [Hiroi 2022](../sources/hiroi2022_nearportation/fiche.md) (à compléter par une vraie mesure motion-to-photon, capteur et affichage compris).
- **Baseline casque autonome** : dépôt public Unity + scène Leg de Kleinbeck, sur Quest 3 ✅ [Kleinbeck 2024](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md).
- **Performance :** temps de frame **stéréo réel** (p50/p95), fps par œil, VRAM, nombre de Gaussiennes rendues et de paires tuile-Gaussienne ✅ [Feng](../sources/feng2024_flashgs/fiche.md), énergie et régime thermique stable ✅ [Du](../sources/du2026_mobile-gs/fiche.md), **latence motion-to-photon** (jamais mesurée dans la base). **Ajouts du 2026-09-29** (rapport runtime, voir P7) :
  - **p99** du temps d'image et images perdues, pas seulement p50/p95 ;
  - runs **thermiques longs** (15, 30 et 60 min) ;
  - **imputation de la qualité en trois temps** : 3DGS d'origine → modèle réduit rendu hors ligne → rendu sur casque.
- **Utilisateurs :** SUS ✅ [Jiang](../sources/jiang2024_vr-gs/fiche.md) ; UEQ-S, IPQ, CSQ-VR ✅ [Warsinke](../sources/warsinke2026_gs-mesh-dt-vr/fiche.md), avec un plan contrôlé (même lieu dans chaque condition, ce que Warsinke ne fait pas).

## 5. Pistes novatrices : réévaluation

> **Mise à jour du 2026-09-29, vérification d'antériorité web 2025–2026** (détail : [anteriorite_p3_p6.md](anteriorite_p3_p6.md) ; les papiers concernés ne sont 🔎 **pas encore dans la base**).
> - **P3′** : la formule « aucun travail ne pilote en ligne le rendu 3DGS » n'est **plus défendable telle quelle**. Deux travaux le font déjà en partie :
>   - 🔎 **MoQSplat** (MMSP 2026, arXiv 2609.18624). Le code régule le budget de splats sur le temps de rendu (cible 24 fps, seuils 40 / 30 ms), ce qui est vérifié dans le README. C'est **mono-levier, sur desktop, et absent de l'article** ;
>   - 🔎 **GaussAnything** (arXiv 2609.13859). Boucle sur Pico 4 Ultra, mais elle règle le débit de mises à jour, pas le coût de rendu.
>
>   Ce qui reste nouveau : **boucle fermée côté casque autonome, en stéréo, multi-leviers, avec une cible motion-to-photon ou énergie, formalisée par l'éq. 1 de Kamdjou**.
> - **P6** : l'antériorité directe est 🔎 **Ghanbari, Amirpour, Timmerer, IEEE VCIP 2026** : 180 conditions sur Quest 3 réel (*render scale* × densité × distance), mesurées avec OVR Metrics. La page de l'article a été vérifiée. Ils trouvent que **la résolution domine le coût GPU** et que **la densité n'agit qu'à l'approche du budget**. Ils ne donnent **ni nombre absolu de splats, ni motion-to-photon, ni qualité**. P6 reste nouvelle si elle porte sur des scènes réelles à budgets explicites, avec motion-to-photon et qualité.
> - **Budget réaliste sur Quest 3 natif** ([faisabilite_quest3.md](faisabilite_quest3.md)) : Meta recommande ≤ 150k ; les chiffres annoncés montent à ≈ 400–500k à 72 Hz (ninjamode, Gracia). **1 à 3 M Gaussiennes rendues par image à 72 Hz ne sont pas plausibles** avec les renderers publics. L'objectif se formule en **Gaussiennes rendues par image (≤ 0,3–0,5 M)** sur une scène qui peut en contenir davantage.
> - **Concurrent le plus probable** : l'équipe ATHENA/AAU (Timmerer et al.), qui publie en 2026 sur Quest 3, les budgets de splats et l'ABR 3DGS.

| # | Piste d'origine | Statut | Antériorité dans la base | Ce qui reste nouveau |
|---|---|---|---|---|
| **P3′** | **Contrôleur QoS/QoE côté casque** qui pilote en ligne LOD, budget, compression et fovéa pour tenir la fréquence stéréo | **Ouverte : la plus sûre** | [ECO-GS](../sources/wan2025_edge-collab-gs/fiche.md) : contrôleur formel, mais côté radio, bascule binaire, sans fps ni ressources du casque. [Kerbl 2024](../sources/kerbl2024_hierarchical-3dgs/fiche.md) : cité comme travail futur. [Kamdjou](../sources/kamdjou2024_xr-dt-iiot/fiche.md) : éq. 1 jamais instanciée. [Liu 2025](../sources/liu2025_robotic-mr-gs-crosslayer/fiche.md) : prédécesseur d'ECO-GS, lui aussi côté radio et planifié hors ligne. [FoV-NeRF](../sources/deng2021_fov-nerf/fiche.md) : optimisation latence/qualité hors ligne | Instancier l'éq. 1 de Kamdjou **en ligne** avec :<br>• des variables continues (τ de Hierarchical 3DGS ou ΔL d'Octree-GS, budget de Taming, couches de LapisGS, rayon fovéal) ;<br>• des contraintes côté casque (motion-to-photon ≤ 20 ms, fps stéréo, GPU, énergie) ;<br>• un solveur temps réel appris par imitation (idée d'ECO-GS) ;<br>• **objectif : le p99 du temps d'image, pas la moyenne** ;<br>• une **composante anticipative** : baisser la charge *avant* une rotation rapide, d'après la vitesse de la tête, en plus de la boucle fermée (idée du rapport runtime). |
| **P6** *(nouvelle)* | **Banc de mesure de référence sur casque réel** : 3DGS stéréo sur Quest 3 natif et en PC-VR, avec fps par œil, motion-to-photon, énergie, FLIP temporel | **Ouverte, mais à cadrer** | [Kleinbeck 2024](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md) mesure déjà du stéréo natif sur Quest 3, sur des scènes-jouets et sans motion-to-photon, énergie ni percentiles | Mesurer sur des **scènes réelles** (0,5 à 3 M de Gaussiennes), toute la chaîne (p50/p95, motion-to-photon, énergie et thermique, FLIP temporel), avec les méthodes de la base (compression, LOD, tri partagé). C'est l'étape 4 du sujet et le prérequis de P3′ |
| **P1′** | **Partage casque/edge par région** : Gaussiennes streamées rendues localement pour la fovéa et le proche, pixels edge pour la périphérie et le lointain, composition par profondeur, sur un casque **sans accélérateur** | Ouverte, risque modéré | ECO-GS : hybride local/edge en bascule binaire sur l'image entière. VR-Splatting : fovéal hybride, mais local. Nebula : découpage par étape du pipeline | Le découpage spatial avec composition par profondeur. [FoV-NeRF](../sources/deng2021_fov-nerf/fiche.md) fournit la frontière naturelle : fovéa par œil, dépendante du regard, rendue sur le casque ; périphérie unique, dépendante de la tête, rendue en edge. [NeARportation](../sources/hiroi2022_nearportation/fiche.md) montre que le tout-pixels ne tient pas la latence. À vérifier : 🔎 Q-VR (ASPLOS'21) et EDC, qui font du collaboratif fovéal pour les maillages |
| **P5** | **Jumeau numérique gaussien hybride piloté par des données industrielles** (décor 3DGS statique, pièces articulées pilotées par OPC-UA) | Partiellement réalisée | VR-GS : hybride maillage/Gaussiennes pour la physique. Warsinke : jumeau 3DGS et jumeau maillage séparés | Le pilotage par données industrielles et le budget de performance casque. Apport applicatif, aligné avec CESI LINEACT |
| **P2** | Mutualisation stéréo | **Réalisée** (3 formes) | [Nebula](../sources/zhu2025_nebula/fiche.md) : ASIC simulé. [Kleinbeck](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md) : tri partagé logiciel sous Unity, −42 % sur Quest 3. [FoV-NeRF](../sources/deng2021_fov-nerf/fiche.md) : périphérie partagée par translation (NeRF). VRSplat la cite comme travail futur | Seulement la **mesure de l'erreur stéréo** (désocclusions, popping différent entre les yeux), qu'aucun des trois ne fait. À intégrer dans P6 plutôt que comme piste à part |
| **P7** *(en réserve)* | **Runtime natif Rust/Vulkan sur Quest 3**, piloté par le GPU, avec Smol-GS comme format compact et décodage partiel | En réserve : à activer sur déclencheur ([plan](plan_environnement.md), « Piste R ») | [SqueezeMe](https://arxiv.org/abs/2412.15171) : pipeline Vulkan maison sur Quest 3, où le décodeur est le goulot (≈ 180k Gaussiennes). Moteurs existants : Meta Spatial SDK (≤ 150k conseillés), 🔎 WallGS. [Smol-GS](../sources/wang2025_smol-gs/fiche.md) : MLP dépendants de la vue, **donc pas de cache de décodage entre images, 2 décodages en stéréo**, et un octree qui n'est pas un LOD | Un décodage Smol-GS **sur casque** n'a jamais été mesuré. Le micro-benchmark R0 dit en 1 à 2 jours si la piste vaut le coup. Critique complète : [note_critique.md](../supports/rapport2026_smol-gs-quest3-runtime/note_critique.md) |
| **P4** | Streaming progressif de splats | **Largement réalisée** | Nebula (Δcut), LapisGS (couches), 🔎 SRBF-Gaussian, 🔎 LTS (MMSys 2025), 🔎 Sun et al. (EMS 2024) | La combinaison Δcut par visibilité et couches LapisGS sur une trace réseau réelle, à vérifier contre LTS et Sun et al. En dynamique, [3DGStream](../sources/sun2024_3dgstream/fiche.md) implique ≈ 1 à 1,9 Gbit/s (estimation), ce qui plaide contre le streaming de splats pour les scènes animées |

### Recommandation

**Cœur de la contribution : P6 + P3′**, avec **P1′** comme extension si le temps le permet.

1. **P6** répond directement à l'étape 4. Le vide est réel mais plus étroit qu'annoncé : Kleinbeck a ouvert la voie sur Quest 3 avec des scènes-jouets, mais pas sur des scènes réelles ni sur toute la chaîne de latence. Son dépôt public sert de point de départ. P6 fournit aussi les mesures dont P3′ a besoin.
2. **P3′** répond directement à la problématique (« ni entraînement coûteux, ni qualité sacrifiée pour la vitesse »). Elle relie tous les leviers existants dans un cadre formel issu du laboratoire (éq. 1 de Kamdjou), ce qui rend la contribution défendable. Elle n'exige pas de matériel spécifique.
3. **P1′** apporte un volet système (casque + edge) cohérent avec le contexte IIoT et edge de Kamdjou, mais demande une infrastructure réseau.

**Chaîne de traitement recommandée** (détail et chiffres : [comparatif_methodes.md](comparatif_methodes.md)) :
- **Constat :** aucune méthode de la base ne descend sous 0,5 M Gaussiennes sans perte perceptible. L'écart de LPIPS va de +0,021 (Mobile-GS) à +0,074 (Speedy-Splat). C'est la tension centrale du sujet.
- **Réduction hors ligne :** **Taming 3DGS** est l'outil central. C'est le seul qui donne un budget exact au format standard, et il s'entraîne en 11 min. Il fournit les paliers 150k / 300k / 500k de P6. En option, la compression façon Papantonakis (+0,009 de LPIPS seulement) pour le disque.
- **Rendu :** Unity + aras-p, avec les idées de SnugBox/AccuTile (×2 sans perte) et le tri partagé entre les yeux (−42 % sur Quest 3) portées en HLSL.
- **Réglage en ligne (P3′) :** les leviers viennent des **niveaux de détail** (τ de Hierarchical 3DGS, niveaux d'Octree-GS, couches de LapisGS), qui agissent à chaque image, alors que la réduction agit une fois hors ligne. **Décision du 2026-09-29 : P3′ v1 = paliers Taming, le LOD viendra en v2.** Le contrôleur v1 choisit à chaque image parmi des actions discrètes : **palier** (150k / 300k / 500k) × *render scale* × tri partagé on/off. Il vise le **p99** du temps d'image. Voir [plan_environnement.md](plan_environnement.md), « P3′ v1 ».
- **Hors chaîne :** Smol-GS, Compact3D et Mobile-GS, parce qu'ils sortent du format standard. Mobile-GS reste le meilleur candidat si l'on abandonne un jour le rendu trié.

**Environnement conseillé (étape 1)** ✅ [fiches applications](../sources/warsinke2026_gs-mesh-dt-vr/fiche.md), [Mirocha](../sources/mirocha2025_beyond-dt/fiche.md) :
- Unity 6 + OpenXR / XR Interaction Toolkit, avec UnityGaussianSplatting comme première référence ;
- puis **modifier les compute shaders HLSL** du plugin pour contrôler le rasteriseur (LOD, budget, fovéa). Un plugin CUDA ne tournerait pas sur Quest 3 ✅ [Kleinbeck](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md) ;
- base de départ : le dépôt public de Kleinbeck (Unity 2022.3 + Aras, tri partagé, testé sur Quest 3) ;
- en parallèle, VRSplat (SIBR + OpenXR, code public) comme référence de performance ;
- matériel : **Quest 3** (filaire sur RTX 4090, puis natif).

## 6. Questions ouvertes à trancher avec l'encadrant

1. La cible est-elle un **casque autonome** (Quest 3 natif) ou du **PC-VR** ? Le §2 montre que « 30 fps 1080p » est déjà acquis sur PC.
2. 1080p **par œil** ou total ? 30 fps est-il un minimum, alors que les casques demandent 72 à 90 Hz ?
3. Scènes statiques seulement, ou dynamiques (voir Cao 2025) ?
4. Dispose-t-on d'une infrastructure edge (5G, Wi-Fi 6E, serveur GPU) pour P1′ ?

## Papiers à ajouter

| Priorité | Papier | Pourquoi | Accès |
|---|---|---|---|
| 1 | 🔎 LTS (MMSys 2025) ; Sun et al., allocation de débit pour streaming 3DGS (EMS 2024) | Antériorité de P4 | à chercher |
| 1 | 🔎 Q-VR (ASPLOS'21), EDC | Antériorité de P1′ (collaboratif fovéal) | à chercher |
| 1 | 🔎 SRBF-Gaussian (IEEE VR 2025) ; FoV-GS (TVCG 2025) | Streaming dépendant du viewport ; fovéal 3DGS | IEEE, payant |
| 2 | 🔎 GSCore (ASPLOS 2024) | Profilage des goulots sur mobile | ACM |
| 2 | 🔎 Mini-Splatting ; Optimal Projection | Bases de VRSplat | arXiv |
| — | Uzun 2025 ; Cao 2025 | Références du sujet | payant (Springer, IEEE) |
| **0** | 🔎 **MoQSplat** (arXiv 2609.18624) + README du dépôt ; 🔎 **GaussAnything** (arXiv 2609.13859) | Boucles les plus proches de P3′ | arXiv |
| **0** | 🔎 **Ghanbari et al., VCIP 2026** (Quest 3) | Antériorité directe de P6 | pas encore en ligne, à surveiller |
| 1 | 🔎 **Milef et al., CLOD-3DGS** (CGF 2025, 10.1111/cgf.70069) | Vérifier ce que recouvre leur « budget-based rendering » | Wiley |
| 1 | 🔎 Atlas (2609.02352), PowerGS (2509.21702), Splats under Pressure (2604.07177), Mono→Stereo reprojection (2609.30741) | Leviers et modèles de coût pour P3′ | arXiv |

La deuxième vague (3DGStream, Octree-GS, NeARportation, FoV-NeRF, Reducing Memory Footprint, Multi-layer GS, Liu 2025) est intégrée.

**Erreurs de sources repérées :**
- Li 2025 attribue à Kleinbeck « > 100 fps en 2064×2208 sur 4090 », ce qui mélange deux configurations.
- Li 2025 présente un seuil de < 20 ms, cité par NeARportation, que ce papier ne mesure pas (il mesure 100 à 400 ms).
- Octree-GS (Tab. III) compare des fps mesurés sur A100 et sur A6000.

## Axe ajouté le 2026-10-08 : localisation des poses (SLAM / VIO)

La piste mote remplace COLMAP par les poses du casque. L'état de l'art correspondant (Oculus Insight, ORB-SLAM3, VINS, OpenVINS, Kimera, Basalt, DROID-SLAM/DPVO, multi-caméras, accélération GPU/DSP/ASIC, précision mesurée des casques, SLAM à carte 3DGS) est synthétisé dans [localisation_poses.md](localisation_poses.md) ; les fiches sont dans INDEX.md, section « Localisation des poses ».
