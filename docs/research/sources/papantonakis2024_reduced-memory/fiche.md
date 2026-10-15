---
citekey: papantonakis2024_reduced-memory
mineru_doc: cac03a1
type: article de revue   # Proc. ACM Comput. Graph. Interact. Tech. (PACMCGIT), revue des actes de conférence
statut: fiche complète
tags: [3dgs, compression, pruning, redondance, sh-adaptatives, quantification, codebook, half-float, stockage, vram, webgl, mobile, streaming, piste-P3, piste-P4, brique-P3-prime]
---

# Reducing the Memory Footprint of 3D Gaussian Splatting

**Référence :** Papantonakis, P., Kopanas, G., Kerbl, B., Lanvin, A., Drettakis, G. (2024). Reducing the Memory Footprint of 3D Gaussian Splatting. *Proceedings of the ACM on Computer Graphics and Interactive Techniques* 7(1), art. 1, mai 2024 (p. 1). DOI [10.1145/3651282](https://doi.org/10.1145/3651282). arXiv [2406.17074](https://arxiv.org/abs/2406.17074). Inria / Université Côte d'Azur, TU Wien. *Le texte indique PACMCGIT ; « I3D 2024 » n'y figure pas explicitement.*
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Code :** https://repo-sam.inria.fr/fungraph/reduced_3dgs/ (p. 10)

## En une phrase

Trois réductions qui se cumulent, chacune d'un facteur ≈ 3, donnent **×27 sur le disque** et **×1,7 en fps**, pour −0,21 dB en moyenne (p. 1, 6, 11) :
1. un **élagage « résolution-aware »** des Gaussiennes redondantes pendant l'entraînement (environ −60 %) ;
2. un **nombre de bandes SH adaptatif par Gaussienne** (89 % finissent sans SH, en RGB seul) ;
3. une **quantification par codebook** (256 entrées) et des **half-floats**.

Cible explicite : le **streaming web/mobile**. Sur téléphone (WebGL), le téléchargement est ×24 plus court et le rendu passe de 16 à 45 fps (p. 12).

## Problème traité

- 3DGS pèse 700 Mo à 1,2 Go par scène, ce qui est « prohibitif pour le streaming vers des appareils mobiles » (p. 2).
- Analyse des causes (p. 5) :
  - **densification excessive** : trop de primitives dans certaines régions ;
  - **SH** : 45 des 59 floats par Gaussienne (76 %), alors que la plupart des surfaces sont diffuses ;
  - **précision** : l'opacité, l'échelle, la rotation et les SH n'ont pas besoin de float32. La position, si (sa quantification dégrade fortement la qualité).

## Méthode / contributions

**1. Élagage par redondance, conscient de l'échelle et de la résolution (Sec. 4.1, p. 6-8).**
- Pour chaque Gaussienne g, on prend l'**empreinte pixel minimale a_min** parmi les vues d'entraînement qui la voient (vue la plus proche), puis une sphère de rayon a_min·√3/2 autour de g. On compte les Gaussiennes (ellipsoïdes) qui l'intersectent : c'est le **score de redondance**.
- Implémentation efficace : k-NN (30 voisins) en CUDA, puis un test ellipsoïde-point réduit à un produit scalaire. Le score se propage aux voisins par le **minimum**, ce qui rend le critère conservateur (p. 7).
- On filtre avec un seuil adaptatif τ_p = max(μ + λ_r σ, 3), λ_r = 1. On supprime **50 %** des candidates, en choisissant les plus faibles opacités. S'y ajoutent l'élagage des 3 % d'opacité la plus faible (plafond 0,05) et une perte L1 de parcimonie sur l'opacité. Le tout est appliqué toutes les 1000 itérations (p. 8).
- Propriété revendiquée : **pas de perte pour les vues plus lointaines que les vues d'entraînement**, et la même information pour les vues plus proches (p. 7).

**2. Bandes SH adaptatives (Sec. 4.2, p. 8-9).** Appliquées une fois, à 15K itérations, quand la densification s'arrête.
- (a) Si la variance de la couleur évaluée sur toutes les vues, pondérée par la transmittance, est inférieure à ε_σ = 0,04, on passe en RGB seul (éq. 1-2).
- (b) Sinon, on garde la plus petite bande q dont l'écart de couleur à la bande 3 est inférieur à ε_cdist = 0,04.
- Une perte de parcimonie sur les SH est ajoutée. Répartition finale : **89 % / 0,1 % / 2,7 % / 8,2 %** des Gaussiennes en 0 / 1 / 2 / 3 bandes (p. 9).
- Pour le stockage, les Gaussiennes forment **4 ensembles**, un par nombre de bandes (p. 10).

**3. Quantification (Sec. 4.3, p. 9-10).** Codebooks K-means de 256 entrées (index sur 1 octet) pour l'opacité, l'échelle, la rotation (partie réelle et partie imaginaire), la couleur de base et chacun des 15 groupes de coefficients SH. Positions et entrées de codebook en **half-float**. Soit −96,3 % au total (p. 10).

**4. Implémentation (p. 10).**
- Code 3DGS original modifié ; **rasteriseur CUDA standard**, avec une lecture à nombre de SH variable « sans ralentissement perceptible ».
- Portage **WebGL** (viewer gsplat.js de D. Ebert), où les auteurs ont ajouté l'évaluation des SH.
- **Décompression au chargement** : la représentation quantifiée est décompressée au parsing, et les codebooks ne sont pas utilisés pendant le rendu (p. 10).
- La mémoire d'entraînement n'est **pas réduite** : les élagages interviennent après le pic (p. 10).

## Résultats chiffrés

**Matériel : NVIDIA RTX A6000**, Linux. Les fps mesurent **uniquement la routine du rasteriseur CUDA**, sans blit ni présentation (swapchain) (p. 10). **Rendu mono.** Résolution : protocole standard des datasets, **non précisée**. 30K itérations. Téléphone : **modèle non précisé**, Wi-Fi local, WebGL.

| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| FPS (3DGS\* → Ours) | **178 → 284** (5,6 → 3,5 ms) ; **227 → 433** (4,4 → 2,3 ms) ; **201 → 360** (5,0 → 2,8 ms) | Mip-NeRF 360 / T&T / Deep Blending, A6000, rasteriseur seul (Tab. 2, p. 13) |
| FPS variantes Low / High | 295 / 298 ; 436 / 468 ; 371 / 406 | idem (Tab. 2) |
| FPS par scène | bicycle 115 → 260 ; garden 127 → 245 ; truck 214 → 418 ; drjohnson 171 → 335 | Tab. 7-9, p. 15 |
| FPS sur téléphone | 3DGS complet **16 fps** → Ours **45 fps** ; ≈ ×3 annoncé (p. 14) | WebGL, téléphone non identifié, résolution non rapportée (p. 12) |
| Qualité (SSIM / PSNR / LPIPS, 3DGS\* → Ours) | 0,813 / 27,42 / 0,217 → 0,809 / 27,10 / 0,226 ; 0,844 / 23,66 / 0,178 → 0,840 / 23,57 / 0,188 ; 0,899 / 29,47 / 0,247 → 0,902 / 29,63 / 0,249 | Mip-NeRF 360 / T&T / DB (Tab. 1-2) |
| Disque, par étape | Mip-NeRF 360 : 744 → 339 (élagage) → **102** (SH) → **29 Mo** (quantif.), soit ×25,7 ; T&T : 412 → 154 → 49 → 14 Mo (×27,6) ; DB : 630 → 224 → 62 → 18 Mo (×34,8) | Tab. 1, p. 11 |
| Variante High | 23 / 10 / 13 Mo ; PSNR 27,02 / 23,28 / 29,56 | Tab. 2 |
| Nombre de Gaussiennes | 1,46 M (43 % de la base) ; 0,68 M (39 %) ; 1,01 M (35 %). Bicycle : 6,05 M → 2,41 M | Tab. 3 p. 13, Tab. 7 p. 15 |
| Half-float seul | 38 → 29 Mo (Mip-NeRF 360) pour −0,07 dB ; la position représente alors 28 % du fichier | Tab. 4, p. 13 |
| Entraînement | 31 min 16 s → **25 min 27 s** ; 17 min 47 s → 14 min 0 s ; 28 min 2 s → 22 min 4 s | A6000 (Tab. 2) |
| Téléchargement mobile | **120 s → 5 s** (×24) | Wi-Fi local (p. 12) |
| **VRAM au rendu** | **non mesurée** | — |
| Latence | non rapportée | — |

## La question de la VRAM au rendu

[Compact3D (Lee)](../lee2023_compact3d/fiche.md) a montré que −95 % sur le disque ne donnait que −5 à −19 % de VRAM. Qu'en est-il ici ?

- **Les auteurs ne mesurent pas la VRAM.** Ils écrivent seulement que le modèle *peut* réduire fortement la mémoire d'inférence « selon l'implémentation » (p. 3), et que ce n'est **pas le cas pour la quantification** : il faudrait intégrer les codebooks et les half-floats au renderer pour que la VRAM baisse autant que le disque (p. 11). Ils signalent aussi que les taux de Compressed3D ne se traduisent pas en VRAM, puisque DEFLATE compte pour environ ×2 (p. 14). Ils sont donc conscients de l'écart disque/VRAM.
- **Ce qui réduit réellement la VRAM**, selon le texte : moins de Gaussiennes et moins de bandes SH, parce que le rasteriseur lit un nombre de SH variable (p. 10). La quantification, elle, est défaite au chargement.
- **Estimation (notre calcul, à vérifier) :**
  - En float32 après décompression, une Gaussienne coûte en moyenne 0,89×14 + 0,001×23 + 0,027×38 + 0,082×59 ≈ **18,4 floats** au lieu de 59, soit ×3,2 (répartition p. 9).
  - Avec ≈ 43 % des primitives, les **attributs** en VRAM devraient donc correspondre à la ligne « +SH culling » du Tab. 1 : **≈ 102 Mo au lieu de 744 Mo** sur Mip-NeRF 360 (×7,3). Avec les codebooks dans le renderer, on descendrait vers 29 Mo.
  - Les tampons du rasteriseur (prétraitement, paires tuile-Gaussienne, tri) baissent aussi, puisque N est divisé par 2,3 à 2,9, mais on ne sait pas de combien.
- **Différence avec Compact3D** : ici, pas de hash grid ni de MLP à reconstituer par Gaussienne. La baisse de VRAM devrait donc être **bien plus proche** de la baisse du disque que chez Lee. Cela reste une **hypothèse à mesurer (P6)**.

## Pertinence pour notre sujet

| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Seul papier compression du groupe à montrer un **rendu sur téléphone** (WebGL) et un scénario de **streaming** réel. Code public. Aucun casque. |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | L'élagage utilise l'ellipsoïde anisotrope (échelle et rotation) pour le test d'intersection. La position, elle, doit rester précise (p. 5). |
| 3. Rendu rapide, visibilité, casque XR | ×1,6 à ×1,9 en fps avec le rasteriseur standard, grâce à N ÷ 2,3-2,9 et aux SH courtes. Le format reste 3DGS après décodage, avec 4 blocs de SH. |
| 4. Évaluation (fps, latence, qualité, coût) | Méthode propre : fps du rasteriseur seul, décomposition par étape (Tab. 1), variantes Low/High. Mais pas de VRAM, pas de latence et pas de fiche technique du téléphone. |

## Pour (vis-à-vis de notre problématique)

- **Compatible avec un rasteriseur standard.** Aucun réseau à l'exécution. Le décodage est un lookup de codebook au chargement, et le seul ajout est la lecture d'un nombre de SH variable (p. 10). Le portage WebGL le démontre (p. 12). C'est le point décisif face à [Compact3D](../lee2023_compact3d/fiche.md) (MLP par vue) et à la variante Scaffold d'[Octree-GS](../ren2024_octree-gs/fiche.md).
- **Web/mobile explicitement visés et démontrés** : Fig. 1, téléchargement en 5 s au lieu de 120 s, 45 fps au lieu de 16 sur téléphone (p. 12). Les auteurs se présentent comme « la première solution 3DGS streaming/mobile qui préserve une haute qualité » (p. 14).
- **Casque autonome.** Deux gains en même temps :
  - moins de Gaussiennes (−57 à −65 %), donc moins de tri et de rasterisation ;
  - des attributs environ ×7 plus légers en VRAM (notre estimation).

  Le coût par Gaussienne rendue est l'enseignement n°1 de la synthèse. C'est le bon levier.
- **Qualité quasi intacte** : −0,32 à +0,16 dB, LPIPS +0,002 à +0,010 (Tab. 1-2). C'est mieux que LightGaussian en LPIPS (voir ci-dessous).
- **Entraînement plus court** que 3DGS (−19 à −21 %), sans modèle professeur.
- **Même équipe que [Hierarchical 3DGS](../kerbl2024_hierarchical-3dgs/fiche.md)** (Kerbl, Kopanas, Lanvin, Drettakis) : combinaison naturelle pour annuler les +69 % de mémoire par Gaussienne de la hiérarchie (H5 de cette fiche).

## Contre / limites

- **VRAM non mesurée.** Le gain de quantification ne s'applique pas à la VRAM tant que le renderer décompresse (p. 10-11). Pour un casque autonome, c'est justement l'indicateur clé.
- **Fps de rasteriseur seul, sur A6000.** Ils excluent l'overhead de l'API graphique (p. 10). Ils ne sont donc pas comparables à un temps d'image bout-à-bout sur casque. Tout est mono.
- **Téléphone non identifié**, résolution inconnue, et un seul chiffre (16 → 45 fps). On ne peut pas en tirer de conclusion pour un Quest 3.
- **Compression statique, hors ligne.** Les seuls réglages sont ε_σ, ε_cdist, λ_r et le score minimal (profils Low / Ours / High). Changer de profil demande un **ré-entraînement**. Rien n'est piloté en ligne. **P3′ n'est pas réalisée.**
- **Méthode intégrée à l'entraînement** : il faut ré-entraîner depuis zéro. On ne peut pas l'appliquer à un modèle 3DGS existant, contrairement à LightGaussian qui est un post-traitement.
- **Élagage fondé sur les vues d'entraînement** (a_min de la vue la plus proche). En VR, l'utilisateur peut s'approcher plus près que toute caméra de capture. Il garde alors « la même information » que 3DGS, mais pas plus (p. 7).
- **SH réduites à RGB pour 89 % des Gaussiennes.** Cela peut appauvrir les reflets en stéréo, où la disparité des spéculaires compte (notre remarque ; non évalué).

## Comparaison avec LightGaussian

Voir [fan2023_lightgaussian](../fan2023_lightgaussian/fiche.md).

| Critère | Papantonakis et al. | LightGaussian |
|---|---|---|
| Moment | Pendant l'entraînement | Post-traitement d'un modèle entraîné (+10K itérations environ) |
| Élagage | Redondance spatiale à l'échelle du pixel + opacité : −57 à −65 % | Score global de significance : −66 % environ |
| SH | Nombre de bandes adaptatif par Gaussienne (0 à 3) | Degré 2 pour tous, par distillation |
| Quantification | Codebooks à 256 entrées pour tous les attributs sauf la position, + FP16 | VQ à 8192 entrées sur les SH des 60 % de Gaussiennes les moins significatives, + FP16 |
| Mip-NeRF 360 (A6000) | 744 → 29 Mo ; 178 → 284 fps ; LPIPS +0,009 | 782 → 45 Mo ; 144 → 237 fps ; LPIPS +0,020 |
| T&T | 412 → 14 Mo ; 227 → 433 fps ; LPIPS +0,010 | 433 → 25 Mo ; 106 → 357 fps ; LPIPS +0,024 |
| Comparaison directe (Tab. 6, sans flowers ni treehill) | 28,58 dB / 0,193 / 27 Mo | 28,46 dB / 0,210 / 42 Mo (chiffres d'une version préprint de LightGaussian, qui diffèrent de sa version NeurIPS) |
| Rasteriseur standard | Oui, avec des SH variables | Oui, SH de degré 2 |

**Bilan :** les gains en fps sont du même ordre (×1,6-1,9), et viennent dans les deux cas surtout de l'élagage. Papantonakis compresse **environ 1,5× mieux** avec une **perte perceptuelle environ 2× plus faible**. LightGaussian garde l'avantage d'être un post-traitement d'un modèle existant. **Pour notre chaîne, Papantonakis est préférable si l'on entraîne soi-même** ; LightGaussian l'est si l'on part de modèles tiers.

## Idées à creuser pour une approche novatrice

Toutes ces pistes sont des **hypothèses**, non testées dans le papier.

- **H1 — Mesure P6 de la VRAM réelle.** On mesurerait sur Quest 3 et sur PC-VR la VRAM et le temps d'image stéréo pour 3DGS, [Compact3D](../lee2023_compact3d/fiche.md), [LightGaussian](../fan2023_lightgaussian/fiche.md) et Papantonakis, avec et sans codebooks dans le shader. Le but est de valider ou d'invalider l'estimation « ≈ ×7 sur les attributs ». Cela trancherait l'enseignement n°1 de la synthèse.
- **H2 — Compression ≠ fps dans le modèle de P3′.** Le Tab. 1 et la variante High montrent que la **quantification réduit disque et bande passante sans changer le fps**, alors que **l'élagage change le fps**. Dans l'éq. 1 de [Kamdjou](../kamdjou2024_xr-dt-iiot/fiche.md), la compression serait donc une variable **réseau/mémoire** (P1′/P4), et le budget ou le LOD une variable **temps d'image**. Ce découplage simplifie le contrôleur.
- **H3 — Score de redondance comme ordre de budget.** Le score est calculé par Gaussienne. Trié, il donne un ordre d'élimination qu'un contrôleur pourrait tronquer en ligne, à la manière du score GS de LightGaussian. Il faudrait vérifier la qualité quand on élague au-delà de 60 % sans ré-entraînement.
- **H4 — Empreinte pixel du casque.** On recalculerait a_min avec la résolution par œil et le champ de vision du casque (2064×2208 pour le Quest 3, voir [Nebula](../zhu2025_nebula/fiche.md)), plutôt qu'avec les caméras d'entraînement. L'élagage serait ainsi adapté à l'affichage cible, et pourrait être rendu fovéal.
- **H5 — Streaming par blocs SH (P4 résiduelle / P1′).** Le fichier est déjà organisé en 4 ensembles selon le nombre de bandes SH (p. 10). On enverrait d'abord positions et RGB (89 % des Gaussiennes), puis les bandes supérieures. Cela se combinerait avec les niveaux cumulatifs d'[Octree-GS](../ren2024_octree-gs/fiche.md).

## Citations clés

> « Taken together, these three components result in a ×27 reduction in overall size on disk on the standard datasets we tested, along with a ×1.7 speedup in rendering speed. » (`doc:cac03a1/tier:standard/page:1/block:6`)

> « Even though our ultimate goal is to reduce the final, stored size of the representation, depending on the implementation, the resulting 3DGS model can have significantly reduced memory requirements at inference-time rendering. » (`doc:cac03a1/tier:standard/page:3/block:6`)

> « In our current implementation, the quantized representation is decompressed at parsing time rather than on-the-fly. Furthermore, we do not yet employ codebooks during rendering. » (`doc:cac03a1/tier:standard/page:10/block:10`)

> « We note that integrating codebooks and half-float type handling into the renderer would enable the same reduction for a scene's VRAM consumption as for its required disk storage. » (`doc:cac03a1/tier:standard/page:11/block:4`)

> « The initial loading time for the full 3DGS scene on our local wifi network was 120sec, displaying at 16FPS, while using our method, the download time is only 5sec and 45FPS » (`doc:cac03a1/tier:standard/page:12/block:11`)

> « the FPS measurements of 3DGS variants on our system isolate the runtime of the CUDA rasterizer routine only » (`doc:cac03a1/tier:standard/page:10/block:12`)

## Liens

- **Papiers liés :**
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) : base, code et rasteriseur réutilisés.
  - [fan2023_lightgaussian](../fan2023_lightgaussian/fiche.md) : concurrent le plus proche (voir la comparaison ci-dessus).
  - [lee2023_compact3d](../lee2023_compact3d/fiche.md) : « Compact3DGS [Lee] » dans les Tab. 5-6, et contre-exemple disque/VRAM. **Attention** : le « Compact3D [Navaneet] » cité ici est un autre papier.
  - [kerbl2024_hierarchical-3dgs](../kerbl2024_hierarchical-3dgs/fiche.md) : même équipe ; combinaison hiérarchie + compression.
  - [ren2024_octree-gs](../ren2024_octree-gs/fiche.md) : LOD compatible, candidat à la même compression.
  - [hanson2024_speedy-splat](../hanson2024_speedy-splat/fiche.md), [mallick2024_taming-3dgs](../mallick2024_taming-3dgs/fiche.md) : autres réductions de N.
  - [han2026_websplatter](../han2026_websplatter/fiche.md), [du2026_mobile-gs](../du2026_mobile-gs/fiche.md) : rendu web et mobile mesuré.
  - [shi2024_lapisgs](../shi2024_lapisgs/fiche.md), [zhu2025_nebula](../zhu2025_nebula/fiche.md) : streaming (H5).
  - [kamdjou2024_xr-dt-iiot](../kamdjou2024_xr-dt-iiot/fiche.md), [wan2025_edge-collab-gs](../wan2025_edge-collab-gs/fiche.md) : contrôleur QoS (H2).
- **Travaux cités à suivre :** Compressed3D (Niedermayr et al. 2023, codebooks dans le renderer), EAGLES (Girish et al. 2023), Compact3D (Navaneet et al. 2023), la note d'Aras Pranckevičius sur la compression de splats par textures GPU, SMERF (Duckworth et al. 2023).
