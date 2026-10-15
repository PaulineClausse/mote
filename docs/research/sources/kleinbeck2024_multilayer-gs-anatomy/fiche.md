---
citekey: kleinbeck2024_multilayer-gs-anatomy
mineru_doc: 3efd049
type: article de revue   # arXiv v1 oct. 2024 ; IEEE TVCG 2025 selon Li 2025 (non indiqué dans le texte)
statut: fiche complète
tags: [3dgs, vr, unity, unitygaussiansplatting, multicouche, élagage, compression, k-means, tri-partagé-stéréo, quest-3-natif, varjo-aero, rtx-4090, macbook-m3, médical, path-tracing, code-public]
---

# Multi-Layer Gaussian Splatting for Immersive Anatomy Visualization

**Référence :** Constantin Kleinbeck, Hannah Schieber, Klaus Engel, Ralf Gutjahr, Daniel Roth (TUM University Hospital ; Siemens Healthineers) (2024). *Multi-Layer Gaussian Splatting for Immersive Anatomy Visualization.* arXiv [2410.16978](https://arxiv.org/abs/2410.16978) (v1, 22 oct. 2024). Le texte ne donne pas de venue ; [Li 2025](../li2025_rf-xr-survey/fiche.md) le cite comme IEEE TVCG 2025 (`doc:3efd049/tier:standard/page:1`). Code : github.com/roth-hex-lab/Multi-Layer-Anatomy-GS-Unity-Rendering ; données et modèles : osf.io/tuwh5 (`page:9/block:15`, `page:12`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Des images de scanners CT rendues par path tracing servent à entraîner un 3DGS **multicouche** : os, puis muscles, puis tissus, chaque couche étant entraînée par-dessus les précédentes figées. Les couches tiennent dans un seul .ply, avec un élagage des Gaussiennes « inactives » et une compression des SH par K-means entre couches. Le tout est rendu dans **Unity 2022.3 via une extension de UnityGaussianSplatting (Aras P.)**, avec une option de **tri partagé entre les deux yeux**. Temps mesurés : 2,5–3,6 ms sur Varjo Aero + RTX 4090, **10,2–26,6 ms en natif sur Quest 3**, 4,5–6,4 ms sur MacBook M3 Pro (`page:4`, `page:5/block:15`, `page:6/block:4`, `page:7/block:4`).

## Problème traité
- Le path tracing volumique de données CT est réaliste mais trop coûteux en temps réel, surtout sur un casque autonome. Les volumes pèsent de centaines de MB à des dizaines de GB (`page:1`, `page:2`).
- Un 3DGS classique est **statique** : fonction de transfert figée, pas de coupe propre, et mélanger plusieurs 3DGS entraînés séparément produit des artefacts (tri global) (`page:2`).

## Méthode / contributions
- **Génération des images** : path tracer open source (nihofm/volren), Monte Carlo, phase Henyey-Greenstein, éclairage par environnement HDR. Vérité terrain à 4096 échantillons par pixel et 100 rebonds. 512 images en 1600×1600 par scène, une sur 8 pour le test (`page:4`, `page:6/block:13`, `page:12`).
- **Nuage initial sans SfM** : on lance des rayons de l'extérieur vers le volume et on crée un point au premier seuil d'opacité ≥ 0,2 de la fonction de transfert. On obtient ≈ 100 000 points, exportés au format COLMAP (`page:4`, `page:6/block:16`).
- **Entraînement en couches** : les couches déjà optimisées sont **gelées** (hors de l'optimiseur) mais participent au rendu et à la perte. Chaque nouvelle couche n'encode que la différence. La couche d'appartenance est un attribut du .ply (`page:4`).
- **Canal alpha** : fond de couleur aléatoire à chaque itération et alpha inclus dans la perte, ce qui donne moins d'artefacts et moins de Gaussiennes (`page:4`, `page:8/block:6`).
- **Élagage « inactif »** : on suit l'activité moyenne 2·p + 0,1·c + 0,1·s sur dR = 100 itérations. On retire une Gaussienne si elle est ≤ T, avec T₀ = 0,015 et une décroissance ×0,975 après chaque test. Cela supprime les Gaussiennes cachées par les couches basses (`page:5/block:4` à `block:10`).
- **Rendu Unity** (`page:5/block:15`, `block:16`, `page:6/block:3`, `block:4`) :
  - **Unity 2022.3**, extension du paquet **UnityGaussianSplatting d'Aras P.** (github.com/aras-p/UnityGaussianSplatting) ;
  - HLSL + compute shaders avec **wave operations** : **pas de CUDA**, mais incompatible avec OpenGL et les appareils anciens ;
  - import du .ply → compression → buffers GPU. Tri continu selon la caméra. **Seules les couches actives sont sur le GPU**, les autres restent en RAM ;
  - compression : quantification du plugin. Les SH, ≈ 3/4 de la taille, sont compressés par **K-means sur 16k variantes, en partageant les clusters entre couches** ;
  - **tri partagé stéréo** : « en VR ce tri doit être fait deux fois ». Les auteurs testent un tri **commun aux deux yeux** (depuis le centre des yeux), qui « divise par deux le temps de tri ». L'écart de tri entre les yeux ne concerne surtout que les splats très proches ;
  - deux algorithmes de tri : AMD FidelityFX Parallel Sort (FFXPS) et DeviceRadixSort (dérivé de OneSweep). DeviceRadixSort est **≈ 2× plus rapide**, mais pose des problèmes de compatibilité sur mobile (transpilation des shaders par Unity). Le texte ne dit pas lequel est utilisé sur Quest 3.

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| Temps de rendu, PC (Tab. 3) | GS multicouche Unity : **1,3 ± 0,4 ms** (faible compression) · 1,4 ± 0,4 ms (forte compression) · 1,7 ± 0,4 ms (reconstruction HQ) | scène Leg, **2000×2000 px × 2** (« exemplary VR device »), **RTX 4090**, `page:7/block:2` |
| Comparaison (Tab. 3) | path tracer 1024 spp : 7116 ± 2251 ms · 1 spp + débruitage OIDN : 66,0 ms (19,9 brut) · DVR : 17,9 ms | idem |
| Temps sur casque (Tab. 4) | **Varjo Aero** (PC-VR, RTX 4090) : 2,5–3,6 ms · **Meta Quest 3 natif** : **10,2–26,6 ms** · MacBook M3 Pro : 4,5–6,4 ms | scène Leg, « à la **résolution native** » de chaque appareil, **valeurs numériques de résolution non données**, `page:7/block:4` |
| Détail Tab. 4 (Sort / HQ) | Sort ✓ HQ ✗ : 2,6 / **17,6** / 4,8 · Sort ✗ HQ ✗ : 2,5 / **10,2** / 4,5 · Sort ✓ HQ ✓ : 3,6 / **26,6** / 6,4 · Sort ✗ HQ ✓ : 3,4 / **16,3** / 6,0 ms (Varjo / Quest 3 / MacBook) | colonne « Sort » non définie ; selon le texte, ✗ = tri au centre des yeux et/ou tri moins fréquent (interprétation), `page:7/block:4`, `block:9` |
| Gain du tri partagé (calcul de ma part) | **Quest 3 : −42 % (défaut), −39 % (HQ)** · Varjo/4090 : −4 à −6 % · MacBook : −6 % | Tab. 4 |
| fps équivalents (calcul de ma part) | 4090 à 2000²×2 : ≈ 590–770 fps · Varjo/4090 : ≈ 280–400 fps · **Quest 3 : ≈ 38–98 fps** · MacBook : ≈ 155–220 fps | 1000 / temps de rendu. Ce n'est **pas** un temps de frame complet ni un motion-to-photon |
| Stéréo | **Réelle** : deux vues (2000×2000 × 2) et mesures sur casque. La définition exacte du « rendering time » (GPU seul ou frame complète) n'est pas donnée ; ± 1 écart-type sur les vues de test, pas de percentiles | `page:6/block:8`, `page:7` |
| Pire cas | GS : ≈ 1,6× le temps moyen ; volume rendering : > 4× (gros plans) | `page:7/block:9` |
| Qualité (Tab. 3) | HQ + faible compression : PSNR **37,66** / SSIM 0,969 / LPIPS 0,054 · faible compression : 35,46 / 0,964 / 0,062 · forte compression : 35,26 / 0,963 / 0,063 · (PT 1024 spp : 42,40 / 0,988 / 0,020 ; PT 1 spp + débruitage : 26,66 ; DVR : 24,26) | Leg, référence : path tracing 4096 spp, `page:7/block:2` |
| Qualité par couche, avant Unity (Tab. S7) | PSNR 30,4–38,6 ; les couches hautes sont moins bonnes (ex. Leg : 38,6 / 35,9 / 30,4) | défaut 3DGS, `page:13` |
| Taille des scènes (Tab. 1) | Leg multicouche : 57k → 122k → **137k Gaussiennes** · Fullbody : 99k → 138k → **196k** · Synthétique 3 couches : 166k. Les versions standalone cumulées font 184k / 262k / 291k | `page:6/block:2`. **Coquille dans l'original** : « Combined (1379k) » pour Leg, à lire 137k |
| HQ | densify_grad_threshold = 0,0001, percent_dense = 0,005 : **2 à 4× plus de Gaussiennes** (nombre exact non donné ; .ply ×1,9 à ×2,0) | `page:6/block:16`, Tab. S6 `page:13` |
| Taille disque (Tab. 2 / S6) | Leg : DICOM 304,7 MB → .ply 34,4 MB → Unity défaut 12,8 MB → **clustering 5,8 MB** · Lower Body : 1585,1 → 23,0 → 8,6 → 4,5 MB · Fullbody : 87,4 → 49,3 → 18,2 → 7,6 MB ; jusqu'à **−99,7 %** | `page:6/block:12`, `page:13` |
| Multicouche vs standalone | combiné : Leg 34,4/5,8 MB contre 46,6/10,7 MB ; Fullbody 49,3/7,6 contre 66,3/13,1 MB (avant/après clustering) | `page:6/block:2` |
| vs CLNeRF (Tab. 5) | Leg : 35,48 dB contre 39,95 (LPIPS 0,040 contre 0,042) · Fullbody : 37,38 contre 35,85 dB | sous-ensemble réduit, `page:8` |
| Entraînement | **Durée non rapportée** ; GPU d'entraînement non précisé | — |
| VRAM | Non rapportée (seules les couches actives sont sur le GPU) | `page:5/block:15` |
| Latence motion-to-photon, énergie, thermique | **Non mesurées** | — |
| Pipelines Unity | built-in vs URP : pas de différence significative ; compatibilité limitée du plugin selon les casques mobiles et les pipelines | `page:7/block:9` |

### Vérification du chiffre attribué par Li 2025
[Li 2025](../li2025_rf-xr-survey/fiche.md) résume ce papier par « RTX 4090, > 100 fps, 2064 × 2208 px per eye, VR HMD ». **On ne le retrouve pas tel quel dans le texte** :
- le texte ne donne **jamais** la valeur 2064×2208. C'est la résolution par œil du Quest 3 selon [Nebula](../zhu2025_nebula/fiche.md) ;
- sur RTX 4090, les mesures sont à **2000×2000 × 2** (Tab. 3 : 1,3–1,7 ms) ou sur **Varjo Aero** à sa résolution native, non chiffrée (Tab. 4 : 2,5–3,6 ms). Dans les deux cas, on est largement au-dessus de 100 fps (≈ 280–770 fps) ;
- sur **Quest 3** (2064×2208 probable), le rendu est **natif**, sans RTX 4090, et donne 10,2–26,6 ms, soit **≈ 38–98 fps, donc < 100 fps** ;
- conclusion : Li mélange la résolution du Quest 3 et le GPU du PC-VR. La ligne de §2 de `options.md` est à corriger : PC-VR 4090 ≈ 280–400 fps sur Varjo Aero, et **Quest 3 natif stéréo 38–98 fps**, sur une scène de ≈ 137k Gaussiennes.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | **Référence directe pour l'environnement Unity** : Unity 2022.3 + UnityGaussianSplatting, compute HLSL sans CUDA, portable sur Varjo, Quest 3 et Mac ; code public |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | Initialisation sans SfM, depuis la surface du volume (non transposable à la photo). Entraînement en couches gelées, élagage inactif, alpha. Covariance standard |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | Tri partagé entre les deux yeux ; activation sélective des couches (seules les actives sur le GPU) ; compression SH K-means entre couches ; choix FFXPS/DeviceRadixSort |
| 4. Évaluation (fps, latence, qualité, coût) | **Seul papier de la base à mesurer du 3DGS stéréo en natif sur Quest 3**, dans Unity, avec comparaison PC-VR et Mac. Pas de motion-to-photon, d'énergie, de percentiles ni de FLIP |

## Pour (vis-à-vis de notre problématique)
- **Mesure stéréo native sur casque autonome (Quest 3)** : 10,2 ms, soit ≈ 98 fps, avec tri partagé et reconstruction par défaut. Au-dessus du seuil de 30 fps du sujet et proche des 72–90 Hz visés, **mais sur une petite scène** (`page:7/block:4`).
- **Chaîne Unity reproductible** : même plugin qu'Aras ([Mirocha](../mirocha2025_beyond-dt/fiche.md), [Warsinke](../warsinke2026_gs-mesh-dt-vr/fiche.md), [Shukhratov](../shukhratov2025_capture-interact-unity/fiche.md)), sans CUDA, built-in ou URP, code public (`page:5/block:15`, `page:7/block:9`).
- **Tri partagé stéréo en logiciel sur GPU standard**, avec un gain mesuré de ≈ 40 % sur Quest 3. Le tri pèse donc lourd sur GPU mobile. Sur 4090, le gain est marginal (≈ 5 %), ce qui confirme l'enseignement n°2 sur desktop.
- **Couches = levier de budget** : les couches désactivées ne sont pas sur le GPU. C'est un bouton discret pour P3′ et une structure utile au jumeau numérique (P5).
- Compression par clustering des SH entre couches : 5,8 MB au lieu de 34,4 MB sans perte visible de PSNR (35,46 contre 35,26 dB) ni de temps (`page:6/block:2`, `page:7/block:2`).

## Contre / limites
- **Scènes minuscules** (57k–196k Gaussiennes, objet isolé sur fond transparent), contre 1–5 M pour une scène photogrammétrique ([Kerbl 2023](../kerbl2023_3dgs/fiche.md)). Les temps Quest 3 ne s'extrapolent pas aux scènes Mip-NeRF 360.
- Données **synthétiques issues de path tracing** : poses parfaites, pas de SfM, pas de photos réelles.
- **Protocole de mesure sous-spécifié** : pas de définition du « rendering time », pas de résolution chiffrée, pas de percentiles, pas de motion-to-photon, d'énergie ou de régime thermique. La colonne « Sort » de la Tab. 4 n'est pas définie.
- Le tri partagé est jugé « à compromis visuels mineurs » **sans mesure d'erreur** (`page:7/block:9`).
- Lent sur Quest 3 en HQ (26,6 ms ≈ 38 fps, sous 72 Hz). Les auteurs parlent de « performance bottlenecks » sur casque autonome (`page:7/block:9`, `page:9/block:6`).
- Le plugin a une compatibilité limitée selon les casques mobiles et les pipelines de rendu. DeviceRadixSort pose problème sur mobile (`page:6/block:4`, `page:7/block:9`).
- Les couches hautes augmentent le nombre de Gaussiennes affichées, puisque les couches basses restent nécessaires (`page:9/block:6`). Pas d'anti-popping (StopThePop) ni de Mip-Splatting (« minimal improvements », `page:7/block:11`).
- Les auteurs le disent : il est **difficile de prévoir et de régler le nombre de Gaussiennes** produit par l'entraînement (`page:8/block:15`).

## Réutilisable pour nous
- **Pour P6 (banc de mesure)** :
  - reprendre leur dépôt Unity comme **baseline** : même plugin, mêmes options de tri (FFXPS/DeviceRadixSort, par œil/partagé), trois plateformes (PC-VR 4090, Quest 3 natif, Mac) ;
  - compléter ce qui manque : scènes réelles (Mip-NeRF 360, T&T), temps de frame p50/p95 (outils OVR Metrics/Perfetto côté Quest, hypothèse), motion-to-photon, énergie et thermique, FLIP temporel ;
  - reproduire leur Tab. 4 sur la scène Leg (osf.io/tuwh5) comme **point de contrôle**.
- **Pour le choix de l'environnement** : cela confirme Unity 2022.3/6 + UnityGaussianSplatting pour le PC-VR et le Quest 3 natif, sans CUDA. Pour contrôler le rasteriseur (LOD, fovéa), il faut modifier les compute shaders HLSL du plugin, comme ici, plutôt qu'un plugin CUDA qui ne tournerait pas sur Quest.
- **Pour P3′** : leviers directement exposés dans Unity : activation des couches, tri partagé, fréquence de tri, niveau de compression, reconstruction HQ ou défaut.
- **Pour P5** : les auteurs proposent eux-mêmes les « mechanical visualizations, industrial scans » comme travail futur (`page:9/block:8`). Couches = carter / mécanisme interne / zone surlignée, avec coupe interactive.

## Verdict vis-à-vis de nos pistes
- **P6** : **partiellement réalisée, donc risque pour la nouveauté à préciser**. Le constat de §2 de `options.md` (« aucun papier ne mesure du 3DGS stéréo natif sur casque autonome ») est **faux au sens strict** : ce papier le fait sur Quest 3, en Unity. Mais la scène est petite, le protocole minimal, sans motion-to-photon, énergie ni FLIP. P6 reste nouvelle si elle porte sur **des scènes réelles à ≥ 1 M Gaussiennes** et sur **la chaîne de mesure complète**.
- **P2 résiduelle** : **encore réduite**. Un tri partagé logiciel sur GPU standard, en Unity, existe déjà ici (≈ −40 % sur Quest 3), sans mesure d'erreur. Il reste : partager aussi la projection et le prétraitement, et **quantifier l'erreur stéréo**. Le gain élevé sur Quest 3 **contredit en partie** l'idée que P2 aurait un gain limité : sur GPU mobile, le tri n'est pas négligeable.
- **P3′** : éclairée (leviers discrets disponibles, difficulté de prédire le nombre de Gaussiennes), non réalisée : aucun pilotage en ligne.
- **P5** : éclairée. La structure en couches est un bon candidat pour un jumeau numérique à sous-ensembles activables. Elle ne pilote pas de données industrielles.
- **P1′, P4** : sans objet. Les couches pourraient être streamées à la demande, mais rien n'est proposé.

## Idées à creuser pour une approche novatrice
- *Hypothèse :* **mesurer le coût du tri sur Quest 3 en fonction du nombre de Gaussiennes** (137k → 1–3 M), par œil ou partagé, FFXPS ou DeviceRadixSort. On saurait si le tri partagé reste à ≈ −40 % ou si la rastérisation redevient dominante (lien avec l'enseignement n°2).
- *Hypothèse :* **tri partagé + erreur mesurée** : quantifier l'erreur par FLIP entre tri par œil et tri partagé, selon la distance aux splats proches. Rafraîchir le tri partagé à fréquence réduite et le déclencher par le mouvement de tête serait un levier de P3′.
- *Hypothèse :* **couches pour P5** : décor 3DGS statique (couche 1) plus sous-ensembles de machine en couches activables. Les couches inactives restent en RAM, ce qui sert de budget mémoire GPU pour P3′.
- *Hypothèse :* utiliser leurs couches comme unités de **streaming progressif** (P4 résiduelle), à comparer à [LapisGS](../shi2024_lapisgs/fiche.md), où les couches sont des niveaux de détail et non des contenus.

## Citations clés
> « In VR, this sorting must be performed twice—once for each eye. […] We explore an optimization in which the sorting is shared between both eyes, effectively halving the sorting time per frame. » (`doc:3efd049/tier:standard/page:6/block:4`)

> « standalone immersive devices like the Quest 3 show performance bottlenecks […] sorting Gaussians for the eye center only, rather than both eyes, and reducing sorting frequency can enhance frame rates with minor visual compromises » (`doc:3efd049/tier:standard/page:7/block:9`)

> « we extend an open-source GS rendering package for Unity […] implemented platform-agnostically in HLSL and compute shaders […] Notably, the implementation does not rely on CUDA. » (`doc:3efd049/tier:standard/page:5/block:15`)

## Liens
- Papiers liés :
  - [Li 2025 (survey RF-XR)](../li2025_rf-xr-survey/fiche.md) : source du chiffre « > 100 fps à 2064×2208 », ici corrigé ;
  - [Shukhratov 2025](../shukhratov2025_capture-interact-unity/fiche.md), [Warsinke 2026](../warsinke2026_gs-mesh-dt-vr/fiche.md), [Mirocha 2025](../mirocha2025_beyond-dt/fiche.md) : autres usages de UnityGaussianSplatting ;
  - [Nebula (Zhu 2025)](../zhu2025_nebula/fiche.md) : mutualisation stéréo complète (ASIC) ; résolution Quest 3 2064×2208 ;
  - [VRSplat (Tu 2025)](../tu2025_vrsplat/fiche.md) : PC-VR Quest 3 filaire sur 4090, stéréo simulée ;
  - [FoV-NeRF (Deng 2021)](../deng2021_fov-nerf/fiche.md) : mutualisation stéréo périphérique par translation ;
  - [Mobile-GS (Du 2026)](../du2026_mobile-gs/fiche.md) : mesure mobile mono en régime thermique ;
  - [LapisGS (Shi 2024)](../shi2024_lapisgs/fiche.md) : couches de détail, contre couches de contenu ici ;
  - la compression SH par K-means suit « Compact3D » de Navaneet et al. (réf. [38], `page:6/block:3`), 🔎 absent de la base. Ce n'est **pas** le papier homonyme de Lee et al. ([lee2023_compact3d](../lee2023_compact3d/fiche.md)), qui utilise lui aussi une quantification vectorielle, plus une grille de hachage ;
  - [Mallick 2024 (Taming)](../mallick2024_taming-3dgs/fiche.md) : budget exact de Gaussiennes, qui répond à la difficulté signalée ici ;
  - [Kerbl 2024 (Hierarchical 3DGS)](../kerbl2024_hierarchical-3dgs/fiche.md) : chunks hiérarchiques, cités comme proches.
