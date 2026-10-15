---
citekey: mallick2024_taming-3dgs
mineru_doc: ebb0fc1
type: conférence   # préprint arXiv v1 ; la venue n'est pas indiquée dans le texte
statut: fiche complète
tags: [3dgs, entrainement-rapide, budget-gaussiennes, densification, backpropagation, cuda, vram, gpu-grand-public, compression, roi, piste-P3]
---

# Taming 3DGS: High-Quality Radiance Fields with Limited Resources

**Référence :** Mallick, S. S., Goel, R., Kerbl, B., Vicente Carrasco, F., Steinberger, M., De La Torre, F. (2024). *Taming 3DGS: High-Quality Radiance Fields with Limited Resources*. Préprint arXiv:2406.15643v1 (21 juin 2024) ; la venue n'est pas indiquée dans le texte. Affiliations : CMU, TU Graz, IIIT Hyderabad (p. 1). https://arxiv.org/abs/2406.15643
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Code :** https://github.com/nullptr81/3dgs-accel (p. 8)

## En une phrase

On remplace la densification heuristique de 3DGS par une densification **purement constructive, guidée par un score et calée sur un budget exact de Gaussiennes**. On accélère aussi le pipeline d'entraînement : rétropropagation parallélisée par splat, SH mis à jour par lots, SSIM fusionné. Résultat : qualité proche de 3DGS avec **4 à 5 fois moins de Gaussiennes et de temps d'entraînement** (p. 1), et un entraînement sous **10 GB de VRAM** (p. 10).

## Problème traité

- 3DGS converge vers un nombre **indéfini et imprévisible** de Gaussiennes, dont beaucoup sont redondantes. D'une scène à l'autre, le nombre peut varier d'un ordre de grandeur pour un même nombre de points SfM (p. 1-2).
- Un modèle typique compte plusieurs millions de Gaussiennes et dépasse **1 GB** sur disque. Le papier cite explicitement le streaming réseau et l'AR/VR embarquée comme usages empêchés (p. 2).
- Sur matériel contraint, l'entraînement se dégrade, voire **n'aboutit pas** faute de mémoire (p. 1). Le temps d'entraînement fluctue beaucoup d'une scène à l'autre (p. 2).
- C'est notre verrou « entraînement coûteux ». Le papier le traite côté **entraînement** et **taille du modèle**, pas côté rendu.

## Méthode / contributions

**1. Croissance prévisible (p. 4, éq. 2, Fig. 2b).**
- Les auteurs ont analysé les courbes de croissance de 3DGS sur les scènes extérieures de Mip-NeRF360 : le nombre de Gaussiennes ajoutées par étape **décroît de façon quadratique**. Ils imposent donc une parabole A(x) = ((B − S − 2N)/N²)·x² + 2x + B, avec N le nombre d'étapes de densification, B le budget final et S le nombre de points SfM.
- 3DGS élague les Gaussiennes de faible opacité, donc suivre la courbe telle quelle ne suffirait pas. À chaque étape, on densifie donc **la différence entre le nombre actuel et la cible cumulée** : on atteint exactement B.
- **Le pic de Gaussiennes est égal au nombre final** (Peak #G = #G, Tab. 1). Il n'y a pas de sur-échantillonnage suivi d'un élagage, contrairement à Mini-Splatting (pic jusqu'à 10× le nombre final, p. 9). Cela évite les pics mémoire qui pourraient dépasser la capacité du matériel (p. 2).

**2. Densification pilotée par un score (p. 5-6, éq. 3-5, Algo. 1).**
- La densification a lieu **toutes les 500 itérations**, soit 5 fois moins souvent que 3DGS. On laisse ainsi à l'optimisation le temps d'éteindre les Gaussiennes mal placées avant de les dupliquer (p. 5).
- **Saliance par vue** : S_v = 𝟙_ROI ⊙ (λ₁ L1 + λ₂ Laplacien), avec λ₁ = λ₂ = 0,5. Le masque ROI permet de prioriser une région, par exemple un visage (p. 5).
- **Score par Gaussienne** : S_g = Σ sur N = 10 vues échantillonnées de F(·). F est une somme pondérée d'attributs normalisés par la médiane, multipliée par la perte photométrique de la vue (p. 5-6). Poids utilisés :

| Attribut | Poids |
|---|---|
| Gradient de position ∇g | 50 |
| Nombre de pixels couverts | 0,1 |
| Distance des pixels au centre (pour les « slivers ») | 50 |
| Saliance couverte | 10 |
| Poids de blending cumulés | 50 |
| Profondeur (0 hors frustum) | 5 |
| Opacité (écarte les floaters) | 100 |
| Échelle | 25 |

- On tire **B nouvelles Gaussiennes au hasard, avec S_G comme poids d'échantillonnage**. Chacune est ensuite scindée (split) ou clonée selon les seuils de gradient et de rayon de 3DGS (p. 6, Algo. 1).

> ⚠️ **Compatibilité du `.ply` (vérifié dans le code le 2026-09-29, `scene/gaussian_model.py`)** : à `--ho_iteration` (15000 par défaut), `modify_functions()` passe l'activation d'opacité de `sigmoid` à `abs` et stocke la valeur brute ; `save_ply` l'écrit telle quelle. Un visualiseur standard (UnityGaussianSplatting) applique `sigmoid` : **opacités fausses** (x = 0,05 → 0,51 affiché). Parades : **désactiver le mode haute opacité** (`--ho_iteration` > nombre d'itérations), ou **convertir à l'export** avec `logit(clamp(|x|, ε, 1−ε))`, ce qui perd les opacités > 1 (elles élargissent la zone saturée des splats). Écart de qualité entre les deux à mesurer.

**3. Gaussiennes à haute opacité (p. 6).** À mi-entraînement (15K itérations), l'activation d'opacité devient abs(·), avec un poids de blending plafonné à 1. L'idée vient de la hiérarchie de Kerbl et al. [35]. Elle aide à modéliser des surfaces opaques avec peu de primitives et améliore surtout le PSNR.

**4. Accélérations de l'entraînement (p. 7-8).**
- **Diagnostic (Fig. 3a)** : la rétropropagation domine le temps d'itération, suivie des mises à jour Adam quand le nombre de Gaussiennes grandit.
- **Rétropropagation par splat plutôt que par pixel.** Dans 3DGS, les additions atomiques de gradients par pixel entrent en collision. Ici, chaque thread d'une tuile porte un splat, et les états par pixel (transmittance T, couleur accumulée) circulent entre threads. Pendant la passe avant, on stocke l'état des pixels tous les 32 splats ; les splats sont regroupés en paquets de 32 par warp CUDA, avec échange par shuffle intra-warp (p. 7, Fig. 3b).
- Le backward saute les paires splat-tuile au-delà du dernier contributeur. Le culling est resserré comme dans StopThePop [37] (p. 7).
- **SH** : 48 des 59 attributs par Gaussienne. Les bandes au-delà de la première ne reçoivent un pas Adam que **toutes les 16 itérations**. Les tenseurs SH sont chargés séparément, sans concaténation (p. 8).
- **SSIM** : la convolution gaussienne 11×11 est séparée en deux convolutions 1D, et un kernel fusionné calcule la SSIM (p. 8).
- Tout cela est **numériquement équivalent à 3DGS, sauf le calendrier SH**. Les auteurs annoncent 1,5 à 2 fois plus rapide que gsplat v1.0 (p. 8).
- Hyperparamètres modifiés : learning rate SH multiplié par 4 (0,001), learning rate d'opacité divisé par 2 (0,025) (p. 8).

## Résultats chiffrés

Matériel : **NVIDIA RTX A4500** (GPU station de travail) pour toutes les mesures ; les résultats des autres méthodes sont « obtenus sur le même matériel ou ajustés » (p. 8). Datasets : Tanks&Temples (2 scènes), Deep Blending (2), Mip-NeRF360 (9), avec le split de 3DGS (p. 8). La résolution d'entraînement et d'évaluation n'est pas rapportée.

Budgets du scénario 1, fixés à la main selon le nombre de points SfM : 2× pour les petites scènes intérieures de Mip-NeRF360, 5× pour Deep Blending, 15× pour les scènes extérieures non bornées, 2× pour T&T (p. 9).

| Métrique | Valeur | Conditions |
|---|---|---|
| **FPS de rendu** | **non rapporté** (aucune mesure de rendu) | — |
| Qualité T&T (SSIM/PSNR/LPIPS) | Ours 0,837 / 23,95 / 0,201 ; 3DGS 0,847 / 23,65 / 0,176 ; Ours (#3DGS) 0,851 / 24,04 / 0,170 | Tab. 1, p. 9 |
| Qualité Mip-NeRF360 | Ours 0,801 / 27,31 / 0,252 ; 3DGS 0,815 / 27,46 / 0,215 ; Ours (#3DGS) 0,822 / 27,79 / 0,205 ; Zip-NeRF 0,828 / 28,54 / 0,189 | Tab. 1, p. 9 |
| Qualité Deep Blending | Ours 0,904 / 29,82 / 0,260 ; 3DGS 0,904 / 29,64 / 0,243 ; Ours (#3DGS) 0,907 / 30,14 / 0,235 | Tab. 1, p. 9 |
| Temps d'entraînement | Ours **7 / 11 / 7 min** (T&T / M360 / DB) contre 3DGS **28 / 43 / 39 min** ; Ours (#3DGS) 20 / 32 / 22 min ; INGP-Big 7 / 8 / 8 min ; Mip-NeRF360 48 h ; Zip-NeRF 1,5 h | A4500, Tab. 1, p. 9 |
| Nombre de Gaussiennes (final = pic) | Ours **0,29 / 0,63 / 0,27 M** contre 3DGS **1,84 / 3,31 / 2,81 M** ; Mini-Splatting final 0,31-0,56 M mais pic 4,32-4,51 M | Tab. 1, p. 9 |
| Ratios par rapport à 3DGS (notre calcul sur Tab. 1) | temps ÷4,0 / ÷3,9 / ÷5,6 ; nombre de Gaussiennes ÷6,3 / ÷5,3 / ÷10,4 | — |
| Exemple BICYCLE (Fig. 1) | 3DGS : 47 min, 25,2 dB, 1 450 MB, 6 M de Gaussiennes ; Ours : 9 min, 24,97 dB, 196 MB, 0,8 M | lu sur la figure, p. 2 |
| VRAM d'entraînement | **< 10 GB en continu** dans le scénario 1, « compact enough for a mid-range NVIDIA RTX 3080 ». Pas de mesure publiée sur RTX 3080 | p. 10 |
| Backward sur BICYCLE (Fig. 4) | environ 20 ms/itération (3DGS) → environ 16 (DISTWAR) → environ 12 (notre backward seul) → environ 4 ms (avec le budget) | valeurs lues sur la courbe, p. 8 |
| Temps d'itération (Fig. 3a) | 3DGS jusqu'à environ 60 ms vers 10-15K itérations ; Ours environ 8-14 ms | lu sur la figure, p. 7 |
| Ablations Truck / Train | Ours 7 / 9 min ; sans backward par splat 14 / 17 min ; sans SH espacé 9 / 12 min (PSNR +0,19 / +0,06) ; sans score : −0,28 / −0,45 dB | Tab. 2, p. 9 |
| ROI visage (THuman) | 3DGS : 5 min, 33,7 dB, 15k Gaussiennes ; Ours : 2 min, 33,5 dB, 4k Gaussiennes (PSNR mesuré sur le visage) | Fig. 6, p. 11 |
| Latence | non rapportée | — |

## Pertinence pour notre sujet

| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Dresse un état des méthodes de compression 3DGS (C3DGS, RVQ, Papantonakis, LightGaussian) et affirme qu'elles ne rendent pas le processus plus contrôlable (p. 3). Il n'y a pas de volet XR. |
| 2. Gaussiennes depuis SfM, covariance anisotrope | **Apport central.** On part des mêmes points SfM, avec une densification sous budget exact dont le budget dépend du nombre de points SfM. On garde la covariance anisotrope R S Sᵀ Rᵀ de 3DGS (p. 4). |
| 3. Rendu rapide, visibilité, casque XR | Indirect. Le rasteriseur par tuiles est conservé, et 5 à 10 fois moins de Gaussiennes devrait alléger le rendu, mais **aucun fps n'est mesuré**. Le culling plus serré de StopThePop sert aussi en passe avant (p. 7). |
| 4. Évaluation | Métriques de ressources reprenables : temps d'entraînement, nombre de Gaussiennes final et au pic, VRAM. Il manque les fps, la latence et l'énergie. |

## Pour (vis-à-vis de notre problématique)

- **Entraînement en quelques minutes sur un GPU unique** : 7-11 min en moyenne sur A4500, contre 28-43 min pour 3DGS (Tab. 1). C'est compatible avec un scénario de capture puis visualisation XR le jour même.
- **Mémoire bornée et prévisible.** Le nombre de Gaussiennes est exact, sans pic d'entraînement, avec moins de 10 GB de VRAM (p. 10). Un GPU grand public (RTX 3080) suffirait d'après les auteurs, mais ce n'est pas mesuré.
- **Le budget est un paramètre explicite.** Qualité et taille progressent de façon monotone (Fig. 1, GARDEN). C'est exactement le « bouton » dont P3 a besoin.
- **Score personnalisable avec ROI** : on peut densifier en priorité une zone d'intérêt, par exemple un visage (Fig. 6), ou par extension une machine dans un jumeau numérique.
- Les accélérations sont **équivalentes à 3DGS** (sauf SH) et publiées : réutilisables comme brique d'entraînement de base.

## Contre / limites

- **Aucune mesure de rendu** : ni fps, ni résolution, ni latence, ni stéréo. Le gain de rendu reste à démontrer.
- Sous budget serré, le **LPIPS se dégrade nettement** : 0,252 contre 0,215 sur Mip-NeRF360, et 0,201 contre 0,176 sur T&T (Tab. 1). La perte perceptuelle pourrait être visible en casque, sur de grands champs de vision.
- Le **budget est fixé à la main**, comme multiplicateur du nombre de points SfM par type de scène (p. 9). Aucun lien n'est fait avec une contrainte fps ou matérielle.
- Le budget est **statique**, fixé à l'entraînement. Il n'y a ni LOD, ni adaptation au point de vue ou au rendu.
- Pour une qualité optimale, il faut encore beaucoup d'échantillons et une longue exploration (p. 11).
- Le matériel est un GPU de station de travail (A4500). Aucun test mobile ou embarqué, malgré le discours sur les « mobile devices » (p. 1, 11).

## Idées à creuser pour une approche novatrice

- **H1 (P3) — Budget dérivé d'une contrainte fps.** On inverserait la chaîne : partir d'un fps cible par œil sur le casque visé, mesurer le coût de rendu en fonction du nombre de Gaussiennes, en déduire B, puis entraîner avec Taming. On obtiendrait un modèle « dimensionné pour le casque ». À valider par une courbe fps(B) × LPIPS(B).
- **H2 (P3 et LOD) — Plusieurs budgets emboîtés.** Comme la croissance est constructive, on pourrait sauvegarder des instantanés à B/8, B/4, B/2 et B pour obtenir des niveaux de détail sans réentraînement. Il faut vérifier si les petits niveaux sont des sous-ensembles cohérents ; le papier ne le teste pas.
- **H3 (P1) — Score orienté fovéa ou proximité.** On remplacerait le masque ROI par une carte de saliance « zone probable du regard / zone proche de l'utilisateur » pour concentrer le budget côté casque. La périphérie ou le lointain, moins dense, serait déléguée à l'edge.
- **H4 (P4) — Ordre de streaming.** L'ordre de création des Gaussiennes, du score le plus haut au plus bas, pourrait servir d'ordre de transmission progressive. C'est une hypothèse : le papier ne l'évoque que via le « latency-constrained streaming » (p. 11).
- **H5 — Combiner avec une compression** (quantification ou codebook, [LightGaussian](../fan2023_lightgaussian/fiche.md), [Compact3D](../lee2023_compact3d/fiche.md)). Les auteurs affirment la compatibilité (p. 3, 11) sans la mesurer.

## Citations clés

> « we obtain competitive quality metrics with 3DGS while achieving a 4–5× reduction in both model size and training time » (`doc:ebb0fc1/tier:standard/page:1`)

> « our method uses a purely constructive optimization that only adds Gaussians towards an exact target budget » (`doc:ebb0fc1/tier:standard/page:9`)

> « our first budgeted scenario allows training with consistently less than 10 GB VRAM—compact enough for a mid-range NVIDIA RTX 3080 » (`doc:ebb0fc1/tier:standard/page:10`)

> « Such substantial memory usage and geometry workload complicate real-time rendering on low-end devices, preventing application in constrained settings like network streaming or AR/VR on embedded systems » (`doc:ebb0fc1/tier:standard/page:2`)

## Liens

- **Papiers liés :**
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) : baseline dont Taming remplace la densification et accélère le backward. Kerbl est aussi co-auteur de Taming.
  - [kerbl2024_hierarchical-3dgs](../kerbl2024_hierarchical-3dgs/fiche.md) : origine des Gaussiennes à haute opacité [35]. C'est aussi la référence LOD complémentaire pour P3.
  - [radl2024_stopthepop](../radl2024_stopthepop/fiche.md) : son culling resserré est réutilisé [37].
  - [fan2023_lightgaussian](../fan2023_lightgaussian/fiche.md), [lee2023_compact3d](../lee2023_compact3d/fiche.md) : compressions citées [25] et [23] ; RVQ figure dans le Tab. 1.
  - [hanson2024_speedy-splat](../hanson2024_speedy-splat/fiche.md) : à croiser pour vérifier si la réduction du nombre de Gaussiennes accélère réellement le rendu.
  - [huang2024_2dgs](../huang2024_2dgs/fiche.md) : même groupe de lecture (représentation et entraînement).
- **Options du projet :** [../../synthese/options.md](../../synthese/options.md), piste P3.
