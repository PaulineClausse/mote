---
citekey: yu2023_mip-splatting
mineru_doc: 63b9629
type: prépublication (arXiv) — venue non indiquée dans le texte
statut: fiche complète
tags: [3dgs, anti-aliasing, mip-splatting, filtrage, nyquist, multi-echelle, zoom, generalisation-hors-distribution, representation, xr-a-evaluer, fovea]
---

# Mip-Splatting: Alias-free 3D Gaussian Splatting

**Référence :** Yu, Z., Chen, A., Huang, B., Sattler, T., Geiger, A. (2023). Mip-Splatting: Alias-free 3D Gaussian Splatting. Prépublication arXiv:2311.16493v1 (27 nov. 2023). La venue n'est pas indiquée dans le texte. https://arxiv.org/abs/2311.16493
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Code / page projet :** https://niujinshuchong.github.io/mip-splatting (p. 1). Le code est construit sur le dépôt officiel 3DGS (p. 6, note 3).

## En une phrase

Deux filtres corrigent les artefacts de 3DGS qui apparaissent quand la fréquence d'échantillonnage change (zoom, distance caméra, résolution) (p. 1, 4-5) :
- un **filtre de lissage 3D** borne la taille minimale de chaque Gaussienne selon la fréquence de Nyquist des vues d'entraînement ;
- un **filtre Mip 2D** remplace la dilatation écran de 3DGS en approximant la boîte-pixel.

Même qualité que 3DGS à l'échelle d'entraînement, forte hausse hors échelle, et aucun surcoût revendiqué au rendu (p. 8).

## Problème traité

- 3DGS applique une **dilatation 2D** fixe en espace écran : on ajoute s·I à la covariance 2D, ce qui correspond à un filtre d'environ 1 pixel (p. 4, éq. 5). Les auteurs notent que cette opération n'est pas décrite dans l'article original (p. 4, note 1).
- Le « shrinkage bias » de l'optimisation produit des Gaussiennes dégénérées, plus petites qu'un pixel, que la dilatation masque à l'échelle d'entraînement (p. 4, Fig. 1).
- **Zoom avant / caméra plus proche** : la dilatation devient relativement petite. On observe une érosion, des structures trop fines et des artefacts haute fréquence (p. 4).
- **Zoom arrière / caméra plus loin** : la dilatation étale la radiance de façon physiquement fausse. On observe une sur-luminosité et un aliasing, par exemple sur les rayons de roue de vélo (p. 4).
- Supprimer simplement la dilatation n'est pas une solution. La densification crée alors trop de petites Gaussiennes (« exceeding GPU capacity »), et le zoom arrière reste aliasé (p. 4). Sans aucun des deux filtres, les auteurs obtiennent un OOM même sur un A100 40 Go (p. 11).

## Méthode / contributions

**1. Filtre de lissage 3D (étape 2 de notre sujet, covariance anisotrope).**
- On rétroprojette l'intervalle d'un pixel dans le monde : T̂ = 1/ν̂ = d/f (p. 5, éq. 6).
- Pour chaque Gaussienne k, on garde la fréquence maximale sur toutes les caméras d'entraînement qui voient son centre : ν̂_k = max_n(𝟙_n(p_k)·f_n/d_n) (p. 5, éq. 7). L'occlusion est ignorée et la profondeur est approchée par le centre.
- Convolution par une Gaussienne passe-bas : Σ_k ← Σ_k + (s/ν̂_k)·I, avec une renormalisation de l'amplitude par √(|Σ_k|/|Σ_k + (s/ν̂_k)I|) (p. 5, éq. 9).
- ν̂_k est recalculé toutes les m = 100 itérations (p. 6). Après l'entraînement, ce filtre fait partie intégrante de la représentation et reste constant quel que soit le point de vue (p. 5).
- **Il peut être fusionné dans les primitives, ce qui élimine tout surcoût au rendu** (p. 8).

**2. Filtre Mip 2D (étape 3, splatting anisotrope).**
- On remplace la dilatation par une Gaussienne 2D qui approxime l'intégration du capteur sur la surface d'un pixel (boîte 2D) : Σ²ᴰ + s·I, avec le même facteur de renormalisation √(|Σ²ᴰ|/|Σ²ᴰ+sI|) (p. 5, éq. 10). La valeur de s couvre un pixel.
- La différence avec EWA tient au rôle du filtre (p. 5) : EWA limite la bande passante de l'image de sortie avec une taille choisie empiriquement, typiquement 3×3 pixels, ce qui sur-lisse au zoom arrière.

**Réglages.**
- 30K itérations, pertes, densification et hyperparamètres identiques à 3DGS (p. 6).
- Variance du Mip 2D = 0,1 et du lissage 3D = 0,2. Le total de 0,3 est égal à la dilatation 3DGS, pour une comparaison équitable (p. 6).
- Les auteurs revendiquent des modifications « principled and simple » qui ne demandent que quelques changements au code 3DGS (p. 2).

## Résultats chiffrés

**GPU d'entraînement / de rendu :** non précisé, sauf la mention A100 40 Go dans l'ablation (p. 11). **FPS, taille disque, nombre de Gaussiennes, temps d'entraînement : non rapportés.**

### Tableau comparatif au 3DGS original (chiffres rapportés DANS CE papier)

| Protocole (dataset) | Méthode | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Source |
|---|---|---|---|---|---|
| Mip-NeRF 360, même échelle (intérieur ↓2, extérieur ↓4) | 3DGS (valeurs publiées) | 27,21 | 0,815 | 0,214 | p. 8, Tab. 4 |
| idem | 3DGS* (ré-entraîné) | 27,70 | 0,826 | 0,202 | p. 8, Tab. 4 |
| idem | 3DGS + EWA | 27,77 | 0,826 | 0,206 | p. 8, Tab. 4 |
| idem | **Mip-Splatting** | **27,79** | **0,827** | **0,203** | p. 8, Tab. 4 |
| Blender, entraînement ×1, test 1 → 1/8 (zoom arrière), moyenne | 3DGS | 24,84 | 0,890 | 0,063 | p. 7, Tab. 2 |
| idem | 3DGS + EWA | 29,40 | 0,960 | 0,034 | p. 7, Tab. 2 |
| idem | **Mip-Splatting** | **31,97** | **0,974** | **0,024** | p. 7, Tab. 2 |
| Blender, à 1/8 de résolution | 3DGS / Mip | 17,69 / 28,67 | 0,766 / 0,973 | 0,121 / 0,026 | p. 7, Tab. 2 |
| Mip-NeRF 360, entraînement ↓8, test 1× → 8× (zoom avant), moyenne | 3DGS | 23,25 | 0,715 | 0,305 | p. 8, Tab. 3 |
| idem | **Mip-Splatting** | **27,37** | **0,803** | **0,252** | p. 8, Tab. 3 |
| Mip-NeRF 360, à 8× | 3DGS / Mip | 19,59 / 26,22 | 0,619 / 0,765 | 0,476 / 0,392 | p. 8, Tab. 3 |
| Mip-NeRF 360, entraînement ↓4, test 1/4× → 4× (zoom avant et arrière), moyenne | 3DGS / Mip | 24,39 / 28,06 | 0,765 / 0,844 | 0,237 / 0,189 | p. 14, Tab. 7 |
| Blender multi-échelle (entraînement et test), moyenne | 3DGS / Mip | 29,77 / 34,56 | 0,960 / 0,979 | 0,040 / 0,019 | p. 6, Tab. 1 |

| Métrique | Valeur | Conditions |
|---|---|---|
| FPS | non rapporté. Les auteurs affirment l'absence de surcoût au rendu une fois le filtre 3D fusionné (p. 8) | — |
| Temps d'entraînement | « slight increase » ; le calcul de ν̂ en PyTorch toutes les 100 itérations n'est pas chiffré (p. 7) | — |
| Mémoire / taille | non rapportée | — |
| Latence | non rapportée | — |

**Ablations.** Sans le filtre 3D, on voit des artefacts haute fréquence au zoom avant : moyenne 26,93 dB contre 27,37 dB (p. 12, Tab. 5). Sans le Mip 2D, on voit de l'aliasing au zoom arrière : Blender 30,76 dB contre 31,97 dB (p. 13, Tab. 6).

**Limite déclarée.** L'approximation gaussienne de la boîte-pixel produit une erreur qui croît avec le dézoom (p. 7).

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Seule la VR est citée comme application (p. 1). Aucune mesure XR. |
| 2. Gaussiennes 3D depuis SfM, covariance anisotrope | **Direct.** On contraint la covariance par une borne de Nyquist issue des caméras SfM (Σ + s/ν̂·I). Cela régularise l'échelle, qui est sous-contrainte dans 3DGS. |
| 3. Rendu rapide, splatting anisotrope, casque XR | Remplace la dilatation par un filtre Mip 2D, avec un changement minime du noyau de projection. Pas de coût annoncé au rendu. |
| 4. Évaluation | Introduit le protocole « entraînement à une échelle, test multi-échelles », pertinent pour la VR. **N'évalue ni fps, ni mémoire, ni latence.** |

## Pour (vis-à-vis de notre problématique)
- **Cas d'usage VR typique.** En VR, l'utilisateur s'approche des objets, s'en éloigne ou se penche, et la résolution ou la focale du casque diffèrent de celles des caméras de capture. C'est exactement le changement de fréquence d'échantillonnage où 3DGS s'effondre : −15,6 dB à 1/8 sur Blender, −9,6 dB à 8× sur Mip-NeRF 360 (p. 7-8).
- **Neutre en coût au rendu** d'après les auteurs (p. 8). Il n'y a ni Gaussienne supplémentaire ni passe supplémentaire, donc c'est compatible a priori avec un budget de 30 fps en 1080p. Aucune mesure ne le confirme.
- **Compatible avec le rasteriseur standard**, avec une réserve : c'est notre analyse, non testée dans le papier. Le filtre 3D se fusionne dans Σ et dans l'opacité. Le filtre 2D demande de changer la constante de dilatation (0,3 → 0,1) et d'ajouter un facteur multiplicatif d'opacité dans le shader. Un viewer 3DGS existant (WebGL, Unity, casque) peut donc l'adopter à faible coût.
- **Robuste à la réduction de résolution de rendu**, ce qui intéresse le rendu fovéal (périphérie basse résolution) et la résolution dynamique : rendre à ½ ou ¼ équivaut à un zoom arrière (p. 13-14).
- Le filtre 3D limite la prolifération de micro-Gaussiennes : sans filtre, OOM sur A100 (p. 11). C'est un effet indirect favorable à la mémoire.

## Contre / limites
- **Aucun chiffre de performance** : ni fps, ni VRAM, ni taille, ni nombre de Gaussiennes. On ne peut pas vérifier le « pas de surcoût » ni l'effet du filtre 3D sur le nombre de primitives.
- **Pas de réduction de coût** : au zoom arrière, on rend toujours toutes les Gaussiennes (pas de LOD). Mip-Splatting règle la qualité, pas le budget.
- ν̂ ignore l'occlusion et approche la profondeur par le centre de la Gaussienne (p. 5). La fréquence dépend des seules caméras d'entraînement. Pour des points de vue VR très proches, hors de la distribution de capture, on obtient du flou (pas d'hallucination de détails), ce que les auteurs assument (p. 7).
- Le filtre 2D suppose des pixels réguliers d'environ 1 px. Les lentilles et la distorsion d'un casque rendent l'empreinte pixel non uniforme. Ce cas n'est pas traité (notre remarque).
- Toutes les évaluations sont en mono sur des datasets statiques (Blender, Mip-NeRF 360) ; il n'y a pas de stéréo.

## Idées à creuser pour une approche novatrice
- *Hypothèse :* un **filtre Mip 2D à variance variable selon l'excentricité** (fovéa / périphérie) ou selon la carte de distorsion de la lentille du casque, qui combinerait anti-aliasing et rendu fovéal. À croiser avec [xin2025_a3fr-foveated](../xin2025_a3fr-foveated/fiche.md) et [franke2024_vr-splatting](../franke2024_vr-splatting/fiche.md).
- *Hypothèse (P1) :* dans un rendu partagé edge/casque où l'edge rend la périphérie en basse résolution, Mip-Splatting garantirait l'absence d'aliasing sur la partie sous-échantillonnée. Il est à évaluer comme brique qualité de P1.
- *Hypothèse (P3) :* utiliser ν̂_k, la fréquence maximale utile de chaque Gaussienne, comme **critère de LOD**. Une Gaussienne dont la taille filtrée tombe sous un pixel à la distance courante peut être fusionnée ou élaguée. Ce serait un pont entre anti-aliasing et budget de Gaussiennes, à comparer avec [kerbl2024_hierarchical-3dgs](../kerbl2024_hierarchical-3dgs/fiche.md).
- *Hypothèse :* combiner Mip-Splatting avec une compression ([fan2023_lightgaussian](../fan2023_lightgaussian/fiche.md), [lee2023_compact3d](../lee2023_compact3d/fiche.md)). Le pruning pourrait interagir avec le filtre 3D, qui grossit les petites Gaussiennes. Non testé.

## Citations clés
> « strong artifacts can be observed when changing the sampling rate, e.g., by changing focal length or camera distance » (`doc:63b9629/tier:standard/page:1/block:9`)

> « we introduce a 3D smoothing filter which constrains the size of the 3D Gaussian primitives based on the maximal sampling frequency induced by the input views » (`doc:63b9629/tier:standard/page:1/block:9`)

> « the 3D smoothing filter can be fused with the Gaussian primitives per Eq. 9, thereby eliminating any additional overhead during rendering » (`doc:63b9629/tier:standard/page:8/block:10`)

> « The absence of both the 3D smoothing filter and the 2D Mip filter leads to an excessive generation of small Gaussian primitives [...] resulting in out of memory error even on an A100 GPU with 40GB memory » (`doc:63b9629/tier:standard/page:11/block:7`)

> « there is a slight increase in training overhead as the sampling rate for each 3D Gaussian must be calculated every m = 100 iterations » (`doc:63b9629/tier:standard/page:7/block:10`)

## Liens
- Papiers liés :
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) : base modifiée ; la dilatation 2D n'y est pas décrite.
  - [fan2023_lightgaussian](../fan2023_lightgaussian/fiche.md), [lee2023_compact3d](../lee2023_compact3d/fiche.md) : même groupe « représentation ». Ce sont des approches orthogonales (compression contre anti-aliasing).
  - [kerbl2024_hierarchical-3dgs](../kerbl2024_hierarchical-3dgs/fiche.md) : LOD, complémentaire pour le coût au dézoom.
  - [radl2024_stopthepop](../radl2024_stopthepop/fiche.md) : autre artefact de rendu 3DGS, le popping dû au tri.
  - [huang2024_2dgs](../huang2024_2dgs/fiche.md) : primitive alternative.
  - [xin2025_a3fr-foveated](../xin2025_a3fr-foveated/fiche.md), [franke2024_vr-splatting](../franke2024_vr-splatting/fiche.md), [tu2025_vrsplat](../tu2025_vrsplat/fiche.md) : rendu VR / fovéal, où le changement de résolution est central.
