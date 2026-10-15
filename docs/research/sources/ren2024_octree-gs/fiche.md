---
citekey: ren2024_octree-gs
mineru_doc: 6d07bd7
type: article de revue   # en-tête IEEE TPAMI sur la v2 arXiv (17 oct. 2024)
statut: fiche complète
tags: [3dgs, lod, octree, ancres, scaffold-gs, grandes-scenes, temps-reel, stabilite-fps, stockage, piste-P3, piste-P4, brique-P3-prime]
---

# Octree-GS: Towards Consistent Real-time Rendering with LOD-Structured 3D Gaussians

**Référence :** Ren, K.\*, Jiang, L.\*, Lu, T., Yu, M., Xu, L., Ni, Z., Dai, B. (2024). Octree-GS: Towards Consistent Real-time Rendering with LOD-Structured 3D Gaussians. En-tête *IEEE Transactions on Pattern Analysis and Machine Intelligence* sur la v2 arXiv (p. 1). arXiv [2403.17898](https://arxiv.org/abs/2403.17898) (\* contribution égale). Shanghai AI Lab, SJTU, USTC, Brown, CUHK, Tongji.
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Page projet :** https://city-super.github.io/octree-gs/ (p. 1)

## En une phrase

Les Gaussiennes sont émises par des **ancres rangées dans un octree** (une couche = un niveau de LOD). À chaque vue, on sélectionne les ancres dont le niveau est inférieur à un niveau cible calculé depuis la **distance caméra-ancre** plus un **biais appris par ancre**. Les niveaux sont **cumulatifs** (LOD K = niveaux 0 à K), avec un fondu d'opacité entre niveaux voisins. Résultat : ≥ 30 fps stables en 2K sur MatrixCity (A100), là où 3DGS, Scaffold-GS et Hierarchical-GS tombent à 7-25 fps (p. 2, 5, 10).

## Problème traité

- 3DGS et ses variantes (Scaffold-GS, Mip-Splatting, 2D-GS) ne font qu'un **filtrage par frustum**. Toutes les Gaussiennes visibles sont rendues quelle que soit leur taille projetée. En vue éloignée d'une grande scène, le nombre de primitives explose et le fps s'effondre (p. 1, Fig. 1).
- Sans LOD, toutes les Gaussiennes « se concurrencent » pour toutes les échelles, ce qui dégrade aussi la qualité multi-échelle (p. 1).
- Les LOD concurrents ont des défauts selon les auteurs (p. 3) :
  - CityGaussian : seuils de distance manuels, effets stroboscopiques aux changements de niveau ;
  - Hierarchical-GS : LOD construit en post-traitement, entraînement en plusieurs étapes, plus long ;
  - dans les deux cas, **chaque niveau représente toute la scène**, ce qui gonfle le stockage.

## Méthode / contributions

**1. Ancres en octree (Sec. IV-A, p. 4-5).**
- Reprend les **ancres de Scaffold-GS** : chaque ancre porte k Gaussiennes placées par des offsets appris (éq. 3). Dans Scaffold-GS, opacité, échelle, rotation et couleur sont **décodées par des MLP** à partir de la feature de l'ancre, de la distance et de la direction de vue (éq. 4, p. 4).
- Nombre de couches K = round(log₂(d_max/d_min)) + 1, calculé depuis les distances caméras-points SfM (éq. 5). Ancres initialisées aux centres des voxels de chaque couche, de taille δ/2^L (éq. 6).
- **Générique** : une ancre peut émettre des Gaussiennes 3D explicites (« Our-3D-GS »), des 2D-GS (« Our-2D-GS ») ou des Gaussiennes neuronales Scaffold-GS (« Our-Scaffold-GS ») (p. 4, 8).

**2. Sélection du niveau (Sec. IV-A3, p. 5).**
- L'idéal serait l'empreinte en pixels ; en pratique, on prend la **distance d_ij** entre la vue i et l'ancre j, supposée proportionnelle à l'empreinte à intrinsèques constants. Un facteur focal s corrige les intrinsèques variables.
- Niveau cible : L̂_ij = ⌊Φ(log₂(d_max/(d_ij·s))) + ΔL_j⌋ (éq. 7), où Φ borne dans [0, K−1] et ΔL_j est un **biais appris par ancre**. Il ajoute du détail là où la distance seule ne suffit pas (arêtes vives, Fig. 13).
- Une ancre est rendue si L_j ≤ L̂_ij. Le LOD est **cumulatif**.
- **Transitions** : les ancres du niveau L̂_ij + 1 sont aussi rendues, avec une opacité multipliée par la partie fractionnaire L*_ij − L̂_ij. On obtient un fondu linéaire par morceaux entre niveaux, « éliminant l'aliasing de LOD » (p. 5).

**3. Densification et élagage adaptés au LOD (Sec. IV-B, p. 5).**
- Croissance « next-level » : une Gaussienne à fort gradient devient une ancre au niveau L+1 si ∇g > τ_g·2^(β(L+1)) (τ_g = 0,0002, β = 0,2). Le biais ΔL augmente de ε = 0,01 si le gradient de l'ancre est élevé.
- Élagage sur l'opacité moyenne et sur la **« view-frequency »** (probabilité d'être sélectionnée dans les vues d'entraînement, seuil τ_v). Cela supprime les floaters des ancres fines trop peu vues (Fig. 4).

**4. Entraînement progressif (Sec. IV-C, p. 5-6).** On active un niveau de plus toutes les N itérations, en commençant à ⌊K/2⌋, avec N_{i−1} = ω N_i (ω = 1,5). Les niveaux se séparent mieux : LOD 0 = contenu grossier, niveaux élevés = hautes fréquences (Fig. 3).

**5. Embedding d'apparence** (GLO) par ancre, donné en entrée au MLP couleur, pour les scènes « in the wild » (p. 6).

## Résultats chiffrés

**Matériel : une NVIDIA A100 80 GB** pour toutes les expériences (p. 9). **Rendu mono.** Résolution de rendu donnée **seulement pour le Tab. V (« 2k »)**. Rien sur la stéréo, le casque, la latence, l'énergie ou la VRAM au rendu. Dans les tableaux, « #GS(k) » = **nombre moyen de Gaussiennes sélectionnées par vue** et « Mem » = **taille des fichiers d'ancres sur disque** (p. 7). **Aucun fps n'est rapporté pour Mip-NeRF 360, T&T et Deep Blending.**

| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| FPS, trajectoires T1/T2/T3 | Our-3D-GS **57,1 / 56,9 / 56,1** ; Our-Scaffold-GS **40,9 / 35,2 / 40,3** ; 3DGS 13,8 / 11,7 / 13,5 ; Scaffold-GS 6,7 / 7,4 / 8,0 ; Hierarchical-GS 9,1 / 8,5 / 8,9 (τ₃ = 15 px : 24,3 / 25,3 / 24,8) | MatrixCity, **2K**, A100 (Tab. V, p. 10) |
| FPS, SmallCity | Our-3D-GS 130 ; Our-Scaffold-GS 89 ; Hierarchical-GS 58 (τ₁ 86, τ₂ 110, τ₃ 159) ; 3DGS 99 | Tab. III, p. 9. **Attention** : les chiffres concurrents sont **repris du papier Hierarchical-GS** (A6000), ceux d'Octree-GS viennent de l'A100. Comparaison de fps non homogène. |
| Qualité Mip-NeRF 360 (PSNR / SSIM / LPIPS, #GS, disque) | Our-Scaffold-GS 28,05 / 0,819 / 0,214, 657k, 139,6 Mo ; Our-3D-GS 27,65 / 0,815 / 0,220, 504k, 418,6 Mo ; 3DGS 27,54 / 0,815 / 0,216, 937k, 786,7 Mo ; Scaffold-GS 27,90 / 0,815 / 0,220, 666k, 197,5 Mo | Tab. I, p. 7 |
| Qualité T&T | Our-Scaffold-GS 24,68 / 0,866 / 0,153, 443k, 88,5 Mo ; Our-3D-GS 24,17 / 0,858 / 0,161, 424k, 383,9 Mo ; 3DGS 23,91 / 0,852 / 0,172, 765k, 430,1 Mo | Tab. I |
| Qualité Deep Blending | Our-Scaffold-GS 30,49 / 0,912 / 0,241, 112k, 71,7 Mo ; Our-3D-GS 29,65 / 0,901 / 0,257, 79k, 180,0 Mo ; 3DGS 29,46 / 0,903 / 0,242, 398k, 705,6 Mo | Tab. I |
| Grandes scènes (Block All, MatrixCity) | Our-Scaffold-GS 27,31 / 0,849 / 0,229, 344k, 1 648,6 Mo ; Our-3D-GS 26,86 / 0,833 / 0,260, 218k, 3 205,1 Mo ; Hierarchical-GS 26,00 / 0,803 / 0,306, 492k, 4 874,2 Mo | Tab. II, p. 8 |
| Multi-échelle BungeeNeRF (#GS scale-1 → scale-4) | 3DGS 522k → 5 821k ; Our-3D-GS 411k → 938k ; Our-Scaffold-GS 486k → 2 167k | Tab. IV, p. 10 |
| Temps d'entraînement (Mip-NeRF 360, 40k itér.) | Our-2D-GS 20 min, Our-3D-GS 21 min, Our-Scaffold-GS 23 min ; 3D-GS 34 min, Scaffold-GS 29 min, Mip-Splatting 46 min. Hierarchical-GS : 38 min pour la 1ʳᵉ étape, 69 min au total, contre « 35 minutes » pour Our-Scaffold-GS (dataset de cette seconde comparaison non précisé) | A100, p. 10-11 |
| Ablation (Mip-NeRF 360) | sans view-frequency : 765k, 244,4 Mo, 27,74 dB ; complet : 657k, 139,6 Mo, 28,05 dB | Tab. VII, p. 12 |
| Latence / VRAM au rendu / coût de la sélection | non rapportés | — |

## Pertinence pour notre sujet

| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Référence LOD « en une passe d'entraînement ». VR/AR citées seulement en motivation (p. 1). Code public (page projet). |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | Initialisation de l'octree depuis les points SfM (éq. 5-6). Fonctionne aussi en initialisation aléatoire : 25,93 → 26,41 dB contre Scaffold-GS (p. 11). |
| 3. Rendu rapide, visibilité, casque XR | LOD par distance, cumulatif, avec fondu d'opacité. Il réduit les Gaussiennes rendues par vue (Tab. I-IV) et **stabilise** le fps quand on s'éloigne (Fig. 9). Le rasteriseur 3DGS n'est pas modifié (p. 4). |
| 4. Évaluation (fps, latence, qualité, coût) | Protocole « trajectoires » (zoom, orbite, orbite multi-échelle, Fig. 9) et courbe fps = f(distance). Utile pour P6. |

## LOD Octree-GS contre LOD Hierarchical 3DGS, du point de vue de P3′

Comparaison avec [kerbl2024_hierarchical-3dgs](../kerbl2024_hierarchical-3dgs/fiche.md). Les chiffres HGS viennent de sa fiche.

| Critère | Octree-GS | Hierarchical 3DGS |
|---|---|---|
| Structure | Octree d'ancres ; niveaux **cumulatifs** (le grossier fait partie du rendu fin) | BVH binaire ; nœuds internes = Gaussiennes fusionnées ; une **coupe** remplace les enfants par le parent |
| Critère de sélection | **Distance** caméra-ancre + biais appris ΔL (éq. 7) | **Taille projetée en pixels** ε(n) < τ_ε |
| Bouton exposé | **Aucun bouton de qualité exposé** dans le papier. Le LOD vise un fps « constant », pas un réglage. On pourrait en créer un via s ou un décalage global de L* (hypothèse, non testé) | **τ_ε en pixels**, continu et monotone ; courbe fps/#Gaussiennes mesurée à 3 réglages. Les auteurs annoncent eux-mêmes un « budget de ressources » en travaux futurs |
| Transitions | Fondu d'opacité par la partie fractionnaire de L* : peu coûteux | Interpolation parent-enfant de tous les attributs + α′ (`pow`) : étape « weights » de 1,5-4 ms par image |
| Surcoût mémoire | Aucun nœud dupliqué. Disque **inférieur** à 3DGS (Tab. I-II) | +69 % par Gaussienne, disque +68 % |
| Résidence | Tout sur GPU (A100 80 GB) ; pas d'out-of-core | RAM CPU + streaming des nœuds, coupe mise à jour toutes les 2 images |
| Entraînement | Une seule étape, 21-23 min (Mip-NeRF 360) | 3 étapes, environ 3 h de V100 par chunk |
| Rasteriseur | Standard pour Our-3D-GS. **MLP par ancre et par vue** pour Our-Scaffold-GS | Standard, étendu par l'interpolation |

**Verdict pour un pilotage en ligne (P3′) :**
- **Le bouton le plus facile à piloter est τ_ε de Hierarchical 3DGS** : sa sémantique est explicite (pixels, donc liée à la résolution par œil et à la fovéa), sa réponse fps est documentée, et il est prévu pour un budget. Mais son coût fixe (+69 % mémoire, weights, streaming CPU) vise les scènes de plusieurs km sur PC. Il convient mal à un casque autonome.
- **La meilleure représentation pour un casque est Octree-GS en variante explicite (Our-3D-GS)**. Elle est la plus rapide des variantes (56-57 fps en 2K contre 35-41 pour Scaffold, Tab. V). Elle n'a pas de MLP. Son rendu se fait par un rasteriseur standard après une simple sélection d'ancres. Ses niveaux cumulatifs donnent un ordre naturel de streaming. Il faudrait y **ajouter un bouton** : un décalage global ΔL_global sur L*, continu grâce au fondu d'opacité. C'est une hypothèse à valider : la monotonie fps/qualité n'est pas mesurée.
- Pour une scène industrielle d'intérieur (P5), l'out-of-core de HGS est inutile. Octree-GS suffit.

## Pour (vis-à-vis de notre problématique)

- **Fps stabilisé sur toute la trajectoire.** En 2K sur A100 : ≥ 30 fps pour les deux variantes, 56-57 fps pour Our-3D-GS, contre 7-25 fps pour tous les concurrents, HGS τ₃ compris (Tab. V, Fig. 9). Ce sont les « ≥ 30 fps » du sujet, en mono et sur GPU serveur.
- **Moins de Gaussiennes par vue à qualité égale ou meilleure.** Mip-NeRF 360 : 504k (Our-3D-GS) contre 937k (3DGS), pour +0,11 dB. Deep Blending : 79k contre 398k (Tab. I). Le coût de rendu suit le nombre de Gaussiennes rendues (enseignement n°1 de la synthèse), c'est donc le bon levier.
- **Pas de surcoût mémoire de hiérarchie**, contrairement à HGS. Le disque diminue : Our-Scaffold-GS 139,6 Mo contre 786,7 Mo pour 3DGS (Tab. I).
- **Anti-aliasing multi-résolution** proche de Mip-Splatting (Tab. VI). Cela compte quand l'utilisateur s'approche ou recule en VR.
- **Transitions de LOD lissées** par fondu d'opacité : moins de popping de LOD qu'avec des seuils durs (CityGaussian).
- **Entraînement plus court que 3DGS** (21-23 min contre 34 min, A100), ce qui respecte la contrainte « sans entraînement lourd ».
- **Générique** : la même stratégie s'applique à 3DGS, 2D-GS (géométrie, utile pour P5) et Scaffold-GS.

## Contre / limites

- **Mesures de fps très partielles.** Aucun fps sur les datasets standards (Tab. I). Les seuls fps concernent MatrixCity (2K) et SmallCity. Dans le Tab. III, **le matériel est hétérogène** (A100 contre A6000 pour les valeurs reprises de HGS). Tout est mono et sur **A100 80 GB**, un GPU de datacenter bien plus puissant qu'un casque.
- **Variante Scaffold = MLP à chaque image.** Opacité, échelle, rotation et couleur sont décodées par des MLP qui prennent la **distance et la direction de vue** (éq. 4). Ce décodage a lieu pour chaque ancre sélectionnée, à chaque image, et doit donc être fait **deux fois en stéréo**. Son coût n'est pas isolé. Comme pour [lee2023_compact3d](../lee2023_compact3d/fiche.md), ce n'est **pas lisible par un viewer standard** (Unity, WebGL, casque). Seule la variante explicite l'est, et c'est aussi la plus rapide (Tab. V).
- **Variante explicite peu compacte.** 418,6 Mo sur Mip-NeRF 360 et 3 205 Mo sur Block All (Tab. I-II). La compacité vient surtout des ancres Scaffold. Une compression complémentaire serait nécessaire (voir [papantonakis2024_reduced-memory](../papantonakis2024_reduced-memory/fiche.md)).
- **Critère de distance, pas de pixels.** Il suppose des intrinsèques constants, corrigés par un facteur s (p. 5). Il ne tient compte ni de la résolution par œil du casque, ni de l'excentricité (fovéa), ni de l'occlusion. Le coût de la sélection (« on évalue itérativement toutes les ancres », p. 5) n'est pas mesuré.
- **Aucun pilotage en ligne.** Le LOD est fixé par la géométrie de la vue. Rien ne réagit au temps d'image mesuré ni à une ressource. Le « fps constant » est une propriété de construction, pas une boucle de contrôle. **P3′ n'est pas réalisée.**
- **Pas d'out-of-core.** Tout réside en VRAM (80 GB disponibles), la VRAM au rendu n'est pas rapportée, et les grandes scènes pèsent 0,6 à 3,2 Go sur disque (Tab. II).
- Hyperparamètres nombreux (octree, entraînement progressif, τ_v de 0,01 à 0,7 selon le dataset) ; dépendance aux poses précises ; pas de géométrie (p. 9, 12).
- Popping dû au tri 3DGS non traité (voir [radl2024_stopthepop](../radl2024_stopthepop/fiche.md)).

## Idées à creuser pour une approche novatrice

Toutes ces pistes sont des **hypothèses**, non testées dans le papier.

- **H1 — Bouton ΔL_global pour P3′.** On ajouterait un décalage global à L* (éq. 7), piloté par le contrôleur QoS/QoE (éq. 1 de [Kamdjou](../kamdjou2024_xr-dt-iiot/fiche.md)) sur le temps d'image stéréo mesuré. Le fondu d'opacité le rendrait continu. On mesurerait la courbe #GS/fps/LPIPS en fonction de ΔL_global, puis on la comparerait à τ_ε de HGS et au budget de [Taming](../mallick2024_taming-3dgs/fiche.md).
- **H2 — LOD fovéal et sélection « cyclope » (P3′ + P2 résiduelle).** On remplacerait d par d × f(excentricité) pour dégrader la périphérie (voir [VR-Splatting](../franke2024_vr-splatting/fiche.md) et [VRSplat](../tu2025_vrsplat/fiche.md)). Avec une IPD d'environ 6 cm, la sélection par distance est quasi identique pour les deux yeux : **une seule sélection au centre cyclopéen** pourrait servir aux deux vues. Il faudrait mesurer l'erreur sur les objets proches.
- **H3 — Streaming par niveaux cumulatifs (P4 résiduelle / P1′).** LOD 0 à k resteraient résidents sur le casque, et les niveaux fins proches seraient envoyés par l'edge à la demande. L'ordre de l'octree fournit la priorité ; les auteurs évoquent eux-mêmes le « streaming » (p. 12). À comparer à [LapisGS](../shi2024_lapisgs/fiche.md) et [Nebula](../zhu2025_nebula/fiche.md).
- **H4 — Octree explicite + compression Inria.** On appliquerait l'élagage par redondance et les SH adaptatives de [papantonakis2024_reduced-memory](../papantonakis2024_reduced-memory/fiche.md) à la variante Our-3D-GS. Le but serait d'obtenir un LOD compact, lisible par un rasteriseur standard, et d'en mesurer la VRAM sur Quest 3 (P6).
- **H5 — Mesure P6 du coût de la variante Scaffold.** On chronométrerait séparément sélection, décodage MLP et rasterisation, en stéréo, sur GPU mobile. Cela trancherait entre variantes neuronale et explicite pour un casque autonome.

## Citations clés

> « we introduce Octree-GS, a Level-of-Detail (LOD) structured approach that dynamically selects appropriate levels from a set of multi-scale Gaussian primitives, ensuring consistent rendering performance » (`doc:6d07bd7/tier:standard/page:1/block:6`)

> « In practice, we simplify this by using the observation distance d_ij, as it is proportional to the footprint under consistent camera intrinsics. » (`doc:6d07bd7/tier:standard/page:5/block:8`)

> « Our method shows consistent rendering speed above 30 FPS at 2k image resolution while all baseline methods fail to meet the real-time performance. » (`doc:6d07bd7/tier:standard/page:10/block:6`)

> « All experiments are conducted on a single NVIDIA A100 80G GPU. » (`doc:6d07bd7/tier:standard/page:9/block:10`)

> « However, certain model components, like octree construction and progressive training, still require hyperparameter tuning. » (`doc:6d07bd7/tier:standard/page:12/block:18`)

## Liens

- **Papiers liés :**
  - [kerbl2024_hierarchical-3dgs](../kerbl2024_hierarchical-3dgs/fiche.md) : LOD concurrent (coupe en pixels, τ_ε). Voir la comparaison ci-dessus.
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) : rasteriseur réutilisé.
  - [yu2023_mip-splatting](../yu2023_mip-splatting/fiche.md) : référence anti-aliasing multi-échelle (Tab. VI).
  - [huang2024_2dgs](../huang2024_2dgs/fiche.md) : variante Our-2D-GS.
  - [lee2023_compact3d](../lee2023_compact3d/fiche.md) : même problème de MLP par vue que la variante Scaffold.
  - [fan2023_lightgaussian](../fan2023_lightgaussian/fiche.md), [papantonakis2024_reduced-memory](../papantonakis2024_reduced-memory/fiche.md) : compression complémentaire (H4).
  - [mallick2024_taming-3dgs](../mallick2024_taming-3dgs/fiche.md), [shi2024_lapisgs](../shi2024_lapisgs/fiche.md) : autres leviers pour P3′.
  - [wan2025_edge-collab-gs](../wan2025_edge-collab-gs/fiche.md), [kamdjou2024_xr-dt-iiot](../kamdjou2024_xr-dt-iiot/fiche.md) : contrôleur et cadre QoS/QoE (H1).
  - [franke2024_vr-splatting](../franke2024_vr-splatting/fiche.md), [tu2025_vrsplat](../tu2025_vrsplat/fiche.md) : fovéation VR (H2).
- **Travaux cités à suivre :** Scaffold-GS (Lu et al. 2023, arXiv:2312.00109), CityGaussian (Liu et al. 2024), LetsGo (Cui et al. 2024), VR-NeRF (Xu et al. 2023, LOD mip-map pour la VR).
