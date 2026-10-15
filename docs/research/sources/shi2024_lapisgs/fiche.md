---
citekey: shi2024_lapisgs
mineru_doc: e9895f2
type: conférence   # 3DV 2025 (indiqué indirectement par la note de bas de page p. 2) ; préprint arXiv 2408.14823v2
statut: fiche complète
tags: [3dgs, lod, streaming-adaptatif, codage-scalable, couches-progressives, opacité, compaction, rendu-fovéal, xr, abr]
---

# LapisGS: Layered Progressive 3D Gaussian Splatting for Adaptive Streaming

**Référence :** Yuang Shi, Géraldine Morin, Simone Gasparini, Wei Tsang Ooi (2024/2025). *LapisGS: Layered Progressive 3D Gaussian Splatting for Adaptive Streaming.* arXiv 2408.14823v2 [cs.CV], 10 févr. 2025. La venue est implicite : la note 1 cite « Singapore — the host of 3DV'25 » (`doc:e9895f2/tier:standard/page:2`). Affiliations : NUS, IRIT – Univ. Toulouse, IPAL IRL2955. Lien : [arXiv 2408.14823](https://arxiv.org/abs/2408.14823). Page projet : yuang-ian.github.io/lapisgs (`page:1`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
LapisGS est une représentation 3DGS **en couches cumulatives**, inspirée du codage vidéo scalable (SVC). Une couche de base est entraînée en basse résolution (8×), puis des couches d'amélioration ΔG₁…ΔG₃ sont entraînées en résolutions croissantes. Les couches précédentes sont figées, **sauf leur opacité**, qui est ré-optimisée. Une « occupancy map » (seuil d'opacité 0,005) exclut les splats devenus transparents. On obtient un modèle unique, transmissible couche par couche, dont chaque préfixe G_i = G₀ + ΣΔG_k est une scène complète de qualité croissante (`page:3–5`). **Aucune expérience de streaming, de débit, de latence ni de fps.**

## Problème traité
- La taille des modèles 3DGS est prohibitive pour le streaming vers des utilisateurs à bande passante et capacités variables. La compaction seule (LightGaussian, Compact3D, HAC…) ne s'adapte pas à un réseau dynamique (`page:1`).
- Les hiérarchies spatiales (Octree-GS, Hierarchical 3DGS, CityGaussian) ont trois défauts pour le streaming selon les auteurs (`page:2`) :
  1. elles ne définissent pas de **niveaux de qualité explicites**, d'où un parcours d'arbre coûteux pour sélectionner les splats ;
  2. chaque LOD est représenté **indépendamment** (ancres propres), sans corrélation entre niveaux, ce qui gêne la transmission progressive et le rendu fovéal ou dépendant de la distance ;
  3. la **redondance** entre niveaux gonfle la taille globale et intermédiaire.

## Méthode / contributions
- **Représentation en couches** : pyramide d'images D_i (1×, 2×, 4×, 8×), N+1 = 4 niveaux L₀ (8×) … L₃ (1×). Le modèle s'écrit {G₀, {ΔG_i}}, avec G_i = G₀ + Σ_{k≤i} ΔG_k (éq. 2, `page:4`).
- **Optimisation multi-niveaux** : au niveau i, on entraîne ΔG_i ; les couches précédentes sont figées **sauf l'opacité**. Justification : l'opacité module la contribution additive (α-blending) sans changer l'information spatiale. Perte L1 + D-SSIM avec **λ = 0,2** : le poids de SSIM est volontairement élevé pour éviter la convergence prématurée des couches basses (éq. 3, `page:4`).
- **Occupancy map** O_i par niveau : les splats dont l'opacité passe sous **0,005** (seuil de pruning de 3DGS) sont omis **au streaming et au rendu** (`page:5`). Les auteurs notent que **faire varier ce seuil permettrait un débit adaptatif (ABR)**, mais ne le mettent pas en œuvre (`page:5`).
- **Transition continue entre niveaux** : l'opacité est interpolée linéairement entre niveaux adjacents, avec t = (r_t − r_i)/(r_{i+1} − r_i) (éq. 4, `page:5`), pour éviter le popping.
- **Rendu adaptatif à la vue** (matériel supplémentaire, `page:11`) : le rendu fovéal selon la distance réglerait le niveau **splat par splat** grâce à l'éq. 4, contre un réglage par chunk dans les hiérarchies spatiales. La démonstration est **qualitative** uniquement (Fig. 8–9) : aucune mesure de gain.
- Implémentation sur le code officiel 3DGS, tous hyperparamètres identiques entre étapes, entraînement sur **NVIDIA A100** (`page:5`).

## Architecture casque/serveur (question spécifique)
| Aspect | LapisGS |
|---|---|
| Ce qui transite | **Gaussiennes, par couches** (base, puis ΔG₁, ΔG₂, ΔG₃, cumulatives), filtrées par occupancy map. Ni pixels ni vidéo. Couches **globales à la scène**, non dépendantes de la vue |
| Débit / bande passante | **Non rapporté** : seulement des tailles de modèle **normalisées** (fraction du plus gros modèle de la scène), aucun Mbps ni Mo absolu |
| Latence | Non rapportée |
| Réseau réel ou simulé | **Aucun réseau.** L'évaluation sous réseau fluctuant est explicitement hors périmètre, avec renvoi à LTS [30], un système DASH bâti sur LapisGS (`page:8`) |
| Matériel client / serveur | Entraînement sur A100. Client et rendu : **non rapportés**, aucun fps |
| Qualité par couche | Oui : SSIM/LPIPS/taille par niveau L₀–L₃ sur 4 datasets (voir tableau). **PSNR exclu volontairement** (`page:6`) |
| Adaptation au débit (ABR) | **Évoquée, non implémentée** : sélection de couches et seuil d'opacité (`page:5`, `page:8`) |
| Modèle d'optimisation formel | **Aucun** : ni fonction objectif réseau, ni contrainte, ni solveur |

## Résultats chiffrés
Datasets : Synthetic Blender, Mip-NeRF 360, Tanks&Temples, Deep Blending, soit 19 objets/scènes (`page:5`). Tailles normalisées par rapport au plus gros modèle de la scène (`page:6`). La résolution absolue des images n'est pas indiquée ; les niveaux sont des sous-échantillonnages 2×, 4×, 8× de la « full-scale ».

| Dataset | Niveau | LapisGS SSIM / LPIPS / taille | Single (modèle 1× rendu à l'échelle) | Multiscale (4 modèles indépendants, borne haute) |
|---|---|---|---|---|
| Mip-NeRF 360 (Tab. 2, `page:6`) | L₀ (8×) | 0,957 / 0,052 / 0,239 | 0,635 / 0,201 / 1,000 | 0,957 / 0,052 / 0,239 |
| | L₁ (4×) | 0,936 / 0,080 / 0,413 | 0,752 / 0,164 / 1,000 | 0,947 / 0,065 / 0,531 |
| | L₂ (2×) | 0,928 / 0,111 / 0,520 | 0,881 / 0,119 / 1,000 | 0,928 / 0,096 / 0,783 |
| | L₃ (1×) | 0,925 / **0,161** / **0,568** | 0,918 / **0,124** / 1,000 | 0,918 / 0,124 / 1,000 |
| Tanks&Temples (Tab. 3) | L₃ | 0,916 / 0,163 / 0,608 | 0,923 / 0,106 / 1,000 | idem Single |
| Deep Blending (Tab. 4) | L₃ | 0,951 / 0,219 / 0,544 | 0,959 / 0,171 / 1,000 | idem Single |
| Blender (Tab. 1) | L₃ | 0,970 / 0,044 / 0,430 | 0,969 / 0,027 / 1,000 | idem Single |

| Métrique | Valeur | Conditions |
|---|---|---|
| FPS | **Non rapporté**. Les auteurs affirment que la réduction de taille « directly correlates to decreased rendering times », sans mesure (`page:7`) | — |
| Qualité (vs Single, basse résolution) | « Jusqu'à **+50,71 % SSIM**, **286,53 % LPIPS** avec **23 %** de la taille d'origine » (`page:1`, `page:7`) | Comparaison avec un modèle 1× rendu en basse résolution : baseline faible (aliasing) |
| Qualité (vs Multiscale) | Qualité comparable avec un modèle **jusqu'à 2,33× plus petit** (`page:7`) | Écarts ΔSSIM entre −0,013 et +0,007 ; ΔLPIPS de +0,008 à +0,057 (plus mauvais) (Tab. 1–4) |
| Qualité pleine résolution | **LPIPS nettement dégradé** au niveau L₃ par rapport au modèle standard (360 : 0,161 contre 0,124 ; T&T : 0,163 contre 0,106 ; DB : 0,219 contre 0,171) | Tab. 1–4 (analyse de la fiche : ce coût n'est pas commenté par les auteurs) |
| Mémoire / taille du modèle | Modèle complet L₃ = **43–61 %** de la taille du modèle 3DGS standard (0,430 à 0,608) | Tailles normalisées, aucune valeur absolue en Mo |
| Ablation « Freeze » (opacité figée) | Sans ré-optimisation d'opacité, la taille grossit (ΔSize −118,9 % à −201,5 %) et la qualité baisse (ΔSSIM +0,8 à +5,0 %, ΔLPIPS −12 à −32 %) | Tab. 5 (`page:7`), détail par scène Tab. 6–9 (`page:15`) |
| Temps d'entraînement | Non rapporté (A100, 4 étapes successives) | `page:5` |
| Latence / débit | Non rapportés | — |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Positionne le streaming 3DGS dans la lignée du codage scalable (SVC, V-PCC) et du LOD de nuages de points. Critique argumentée des hiérarchies spatiales pour le streaming (`page:2–3`) |
| 2. Gaussiennes depuis SfM, covariance | Entraînement progressif coarse-to-fine sur pyramide d'images (initialisation SfM standard). Ré-optimisation de l'opacité seule comme mécanisme de raffinement |
| 3. Rendu rapide, visibilité, casque | Indirect : représentation LOD transmissible, transition continue par interpolation d'opacité, rendu fovéal/distance par splat (qualitatif seulement). **Aucun rendu casque, aucun fps** |
| 4. Évaluation | Protocole qualité/taille par niveau (SSIM, LPIPS, taille normalisée) réutilisable. Il manque fps, débit absolu, latence et PSNR |

## Pour (vis-à-vis de notre problématique)
- Fournit la **brique de représentation** de la P4 : un préfixe de couches donne toujours une scène complète, d'où une **dégradation gracieuse** naturelle si une couche manque.
- Pas de redondance entre niveaux : chaque couche ajoute des splats sans renvoyer les précédentes. C'est compatible avec un protocole incrémental façon Δcut de [Nebula](../zhu2025_nebula/fiche.md).
- La **transition continue par interpolation d'opacité** (éq. 4) est un mécanisme anti-popping peu coûteux, réutilisable pour des changements de LOD en XR.
- Le modèle complet est **43–61 % plus léger** que le 3DGS standard, pour un SSIM équivalent.
- Code de base = 3DGS officiel ; les modèles pré-entraînés sont annoncés comme publics (`page:2`).

## Contre / limites
- **Aucune mesure système** : ni fps, ni temps de rendu, ni débit absolu, ni latence, ni réseau (réel ou simulé), ni matériel client. Le titre promet l'« adaptive streaming » ; le papier n'évalue que la représentation (`page:8`).
- **LPIPS dégradé au niveau pleine résolution** par rapport au 3DGS standard (+0,037 à +0,057 sur les scènes réelles). En XR 1080p, c'est justement le niveau fovéal qui compte.
- **PSNR exclu** de l'évaluation (`page:6`) : la comparaison avec le reste de la littérature, qui rapporte PSNR, SSIM et LPIPS, est difficile.
- Couches définies par **résolution d'entraînement**, globales à la scène : **pas de LOD dépendant de la vue** ni de la distance dans les expériences. Le rendu fovéal par splat reste une illustration qualitative (Fig. 8–9).
- Scènes **statiques** uniquement (`page:8`). Pas de stéréo, pas de casque.
- La baseline « Single » rendue en basse résolution est faible : les « +286 % LPIPS » sont un effet d'aliasing, pas un gain à la résolution cible.

## Idées à creuser pour une approche novatrice
- *Hypothèse (P4 reformulée)* : **Δcut en couches**. Envoyer d'abord la couche de base des Gaussiennes entrant dans le cut Nebula, puis les ΔG_i par ordre de priorité (fovéa, contribution α). Sous débit variable, on tronque aux couches reçues et l'interpolation d'opacité (éq. 4) lisse l'arrivée tardive. À mesurer sur trace réseau réelle, avec la latence d'affichage de la première image utile.
- *Hypothèse (P3)* : **contrôleur QoS/QoE à variables discrètes** « nombre de couches par région » et « seuil d'occupancy ». L'[éq. 1 de Kamdjou](../kamdjou2024_xr-dt-iiot/fiche.md) peut s'instancier avec g(QoE) = SSIM/LPIPS par couche (courbes Tab. 1–4) et f(QoS) = débit + fps. Les courbes taille/qualité de LapisGS donnent directement la fonction débit-distorsion.
- *Hypothèse (P1 reformulée)* : fovéa = couches hautes streamées et rasterisées localement ; périphérie = couche de base seule (locale) **ou** pixels edge. La couche de base (~10–30 % de la taille) pourrait suffire à un casque sans accélérateur pour la périphérie : à mesurer en fps.
- *À vérifier (risque de nouveauté)* : lire **LTS** [30] (système DASH pour scènes 3DGS dynamiques multicouches, MMSys 2025) et **Sun et al.** [29] (allocation de débit multi-trames pour le streaming 3DGS dynamique, EMS 2024). Ils réalisent probablement l'ABR sur couches LapisGS, donc une partie de P3/P4.

## Citations clés
> « this approach could allow for adaptive bitrate streaming by dynamically selecting splats based on their opacity. By adjusting the opacity threshold, the system could fine-tune the amount of data transmitted » (`doc:e9895f2/tier:standard/page:5`)

> « While the parameters of the prior layers remain fixed, their opacity is optimized to adjust the influence of each layer dynamically. » (`doc:e9895f2/tier:standard/page:3`)

> « a notable aspect not explored in this work is the evaluation of performance under fluctuating network conditions. » (`doc:e9895f2/tier:standard/page:8`)

> « We exclude PSNR from our evaluation as it primarily estimates pixel-wise error » (`doc:e9895f2/tier:standard/page:6`)

## Liens
- Papiers liés :
  - [Zhu 2025, Nebula](../zhu2025_nebula/fiche.md) : streaming de Gaussiennes dépendant de la vue (Δcut sur arbre HierGS) avec réseau et latence modélisés. LapisGS apporte l'axe **qualité progressive** que Nebula n'a pas ; Nebula apporte l'axe **visibilité** que LapisGS n'a pas.
  - [Wan 2025, ECO-GS](../wan2025_edge-collab-gs/fiche.md) : modèle d'optimisation formel edge/utilisateur, pixels et non splats.
  - [Kerbl 2024, Hierarchical 3DGS](../kerbl2024_hierarchical-3dgs/fiche.md) : hiérarchie spatiale critiquée ici (niveaux indépendants, parcours d'arbre).
  - [Fan 2023, LightGaussian](../fan2023_lightgaussian/fiche.md) : baseline « Downsample » (score d'importance opacité × échelle, `page:6`).
  - [Lee 2023, Compact3D](../lee2023_compact3d/fiche.md) : compaction orthogonale, combinable avec les couches.
  - [Franke 2024, VR-Splatting](../franke2024_vr-splatting/fiche.md), [Xin 2025, A3FR](../xin2025_a3fr-foveated/fiche.md) : rendu fovéal, que LapisGS n'illustre que qualitativement.
  - [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) : le « rendu adaptatif LOD/streaming selon le réseau » (p. 16) décrit en théorie, dont LapisGS fournit une représentation.
  - [Kerbl 2023, 3DGS](../kerbl2023_3dgs/fiche.md) : code de base et seuil de pruning 0,005.
