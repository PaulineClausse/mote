---
citekey: kerbl2023_3dgs
mineru_doc: 192d1b7
type: article de revue
statut: fiche complète
tags: [3dgs, gaussian-splatting, radiance-fields, novel-view-synthesis, rasterisation, sfm, temps-reel, cuda, article-fondateur, xr-a-evaluer]
---

# 3D Gaussian Splatting for Real-Time Radiance Field Rendering

**Référence :** Kerbl, B., Kopanas, G., Leimkühler, T., Drettakis, G. (2023). 3D Gaussian Splatting for Real-Time Radiance Field Rendering. *ACM Transactions on Graphics* 42(4), art. 139. DOI [10.1145/3592433](https://doi.org/10.1145/3592433)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)
**Code / données :** https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/ (p. 8)

> Note : l'en-tête MinerU affiche un « ACM Reference Format » avec des champs de gabarit (2018, DOI XXXXXXX, p. 1) ; la référence exacte ci-dessus est celle de la publication (TOG, août 2023, p. 1 pied de page).

## En une phrase

Représenter une scène statique par 1 à 5 millions de Gaussiennes 3D anisotropes, initialisées depuis les points SfM, optimisées par descente de gradient avec contrôle adaptatif de densité, et rendues par un rasteriseur logiciel CUDA par tuiles avec tri radix global : qualité ≈ Mip-NeRF360, entraînement de 35 à 45 min, ≥ 30 fps en 1080p (p. 1, 2, 9).

## Problème traité

- Les champs de radiance de meilleure qualité (Mip-NeRF360) coûtent jusqu'à 48 h d'entraînement et environ 10 s par image au rendu (p. 2, 9). Les méthodes rapides (InstantNGP, Plenoxels) sacrifient la qualité et restent à 10-15 fps selon la scène (p. 2).
- Le papier affirme qu'aucune méthode antérieure n'atteignait le temps réel pour des scènes complètes non bornées rendues en 1080p (p. 1).
- La cause identifiée est le ray-marching volumétrique. L'échantillonnage stochastique est coûteux, produit du bruit et ralentit sur l'espace vide (p. 1, 3).
- C'est exactement la problématique de notre sujet : sortir du dilemme « entraînement neuronal coûteux » contre « vitesse au détriment de la qualité ».

## Méthode / contributions

**Entrée.** Des images d'une scène statique et des caméras calibrées par SfM (Schönberger & Frahm 2016). Le nuage de points épars produit par SfM sert d'initialisation. Aucune donnée MVS n'est nécessaire, contrairement aux méthodes à points antérieures (p. 2, 4).

**Représentation (étape 2 de notre sujet).**
- Chaque Gaussienne a une position μ, une covariance 3D complète Σ en espace monde, une opacité α et des coefficients SH pour la couleur dépendante de la vue. G(x) = exp(−½ xᵀ Σ⁻¹ x), multipliée par α au blending (p. 4, éq. 4). Aucune normale n'est requise, car les normales des points SfM épars sont trop bruitées pour être estimées (p. 4).
- **Paramétrisation de la covariance.** Optimiser Σ directement produirait des matrices non semi-définies positives. Le papier utilise donc **Σ = R S Sᵀ Rᵀ**, avec un vecteur d'échelle 3D *s* et un quaternion *q* stockés séparément ; *q* est normalisé à chaque conversion (p. 4, éq. 6).
- **Projection.** Σ′ = J W Σ Wᵀ Jᵀ (EWA, Zwicker et al. 2001), où W est la transformation de vue et J le jacobien de l'approximation affine de la projection. On garde ensuite le bloc 2×2 supérieur gauche (p. 4, éq. 5).
- Les gradients sont dérivés **explicitement**, sans autodiff, pour éviter son surcoût (p. 4 ; annexe A p. 13). Ils passent par M = RS et dΣ/dM = 2Mᵀ, avec des dérivées analytiques par rapport à *s* et à chaque composante de *q* (éq. 8-11, p. 13).
- Activations : sigmoïde pour α (dans [0,1)), exponentielle pour l'échelle (p. 5).
- **Initialisation.** Chaque Gaussienne part isotrope, avec un rayon égal à la distance moyenne à ses 3 plus proches voisins (p. 5).
- **Couleur SH.** On optimise d'abord la bande 0 (couleur diffuse), puis on ajoute une bande toutes les 1000 itérations jusqu'à 4 bandes (soit le degré 3, d'après notre calcul). Sans ce schéma, les captures à couverture angulaire incomplète (coins, « inside-out ») produisent une couleur de base fausse (p. 8-9).

**Optimisation.**
- Descente de gradient stochastique (Adam, Algorithme 1 p. 13), avec décroissance exponentielle du learning rate pour les positions seulement (p. 5).
- Perte : ℒ = (1−λ) ℒ₁ + λ ℒ_D-SSIM, avec λ = 0,2 (p. 5, éq. 7).
- Warm-up à une résolution 4× plus faible, avec deux sur-échantillonnages aux itérations 250 et 500 (p. 8).
- Tous les tests utilisent les mêmes hyperparamètres (p. 8). Exception : les très grandes scènes (urbaines) peuvent demander un learning rate de position plus faible (p. 10).

**Contrôle adaptatif de densité (p. 5-6, Fig. 4, Algo. 1).**
- Après le warm-up, on densifie toutes les 100 itérations. Les Gaussiennes sélectionnées sont celles dont le gradient moyen de position en espace vue dépasse τ_pos = 0,0002. Ce critère couvre à la fois la sous-reconstruction et la sur-reconstruction.
- **Clone** : une petite Gaussienne en zone sous-reconstruite est copiée, puis la copie est déplacée dans la direction du gradient. Le volume total et le nombre augmentent.
- **Split** : une grande Gaussienne à forte variance est remplacée par 2 Gaussiennes dont l'échelle est divisée par φ = 1,6. Leurs positions sont échantillonnées en utilisant la Gaussienne d'origine comme PDF. Le volume est conservé.
- **Prune** : on supprime les Gaussiennes où α < ε_α, ainsi que celles qui sont trop grandes en espace monde ou dont l'empreinte en espace vue est trop grande. **Toutes les 3000 itérations, α est remis près de 0**, pour limiter les floaters proches des caméras et l'inflation du nombre de Gaussiennes.
- Aucune contraction ni aucun warping de l'espace n'est nécessaire pour les zones lointaines, contrairement à Mip-NeRF360 et Plenoxels (p. 6).

**Rasteriseur différentiable par tuiles (étape 3 de notre sujet ; p. 6, annexe C p. 13-14).**
1. L'écran est découpé en **tuiles de 16×16 pixels**.
2. Culling contre le frustum : on garde une Gaussienne si son intervalle de confiance à 99 % intersecte le frustum. Une **guard band** rejette trivialement les Gaussiennes proches du plan near ou très hors champ, dont la covariance 2D serait instable.
3. Chaque Gaussienne est instanciée une fois par tuile recouverte, avec une clé de 64 bits : les bits hauts contiennent l'ID de tuile et les 32 bits bas la profondeur projetée (p. 13).
4. Un **tri radix GPU unique** (NVIDIA CUB, Merrill & Grimshaw 2010) règle l'ordre de profondeur de tous les splats en parallèle. **Il n'y a pas de tri par pixel**, donc l'α-blending est approximatif dans certaines configurations. Les auteurs jugent cette approximation négligeable quand les splats approchent la taille d'un pixel (p. 6).
5. Les plages par tuile sont trouvées en parallèle en comparant chaque clé à ses voisines (p. 14).
6. Un bloc de threads est lancé par tuile. Il charge les Gaussiennes en mémoire partagée par paquets, puis accumule couleur et α **front-to-back**. Un thread s'arrête quand son pixel est saturé en α ; la tuile entière s'arrête quand tous ses pixels le sont (p. 6).
7. Stabilité numérique : on ignore les contributions où α < 1/255, on borne α à 0,99, et le blending s'arrête avant que l'opacité accumulée ne dépasse 0,9999 (p. 14).

**Backward pass (p. 6).**
- Le nombre de splats qui reçoivent un gradient n'est pas limité ; le seul critère d'arrêt est la saturation de α.
- Les listes par tuile sont reparcourues **back-to-front**, en réutilisant le tableau trié du forward. Il n'y a pas de listes dynamiques par pixel, donc le surcoût mémoire par pixel est constant.
- Les opacités intermédiaires sont retrouvées en divisant l'opacité accumulée finale par l'α de chaque point.

**Implémentation.** PyTorch avec des kernels CUDA pour la rasterisation. Viewer interactif basé sur SIBR, utilisé pour mesurer les fps (p. 8). Environ 80 % du temps d'entraînement est passé dans le code Python (p. 11).

## Résultats chiffrés

GPU : **NVIDIA A6000** pour tous les résultats, sauf Mip-NeRF360, entraîné sur 4×A100 pendant 12 h, soit l'équivalent de 48 h sur un seul GPU (p. 8, 9). Protocole : 1 image sur 8 réservée au test ; rendus à la **résolution native des datasets**, qui varie selon le dataset (p. 8-9). La résolution exacte de chaque dataset n'est pas donnée dans le texte (non rapporté).

| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| FPS | 134 (30K) / 160 (7K) | Mip-NeRF360, moyenne, A6000, résolution native (Tab. 1, p. 8) |
| FPS | 154 (30K) / 197 (7K) | Tanks&Temples (Tab. 1, p. 8) |
| FPS | 137 (30K) / 172 (7K) | Deep Blending (Tab. 1, p. 8) |
| FPS | 180-300 | Blender synthétique (p. 9) |
| FPS comparés | Mip-NeRF360 0,06 ; INGP-Big 9,43 ; Plenoxels 6,79 | Mip-NeRF360 dataset (Tab. 1, p. 8) |
| Qualité SSIM / PSNR / LPIPS | 0,815 / 27,21 / 0,214 (30K) ; 0,770 / 25,60 / 0,279 (7K) | Mip-NeRF360. Référence Mip-NeRF360 : 0,792 / 27,69 / 0,237 (Tab. 1, p. 8) |
| Qualité SSIM / PSNR / LPIPS | 0,841 / 23,14 / 0,183 (30K) | Tanks&Temples. Mip-NeRF360 : 0,759 / 22,22 / 0,257 (Tab. 1) |
| Qualité SSIM / PSNR / LPIPS | 0,903 / 29,41 / 0,243 (30K) | Deep Blending. Mip-NeRF360 : 0,901 / 29,40 / 0,245 (Tab. 1) |
| PSNR synthétique | 33,32 en moyenne (30K, init. aléatoire de 100K points) | NeRF-Synthetic, fond blanc (Tab. 2, p. 8) |
| Temps d'entraînement | 41m33s (30K) / 6m25s (7K) | Mip-NeRF360 (Tab. 1). Deep Blending : 36m2s / 4m35s ; T&T : 26m54s / 6m55s |
| Temps d'entraînement (comparés) | Mip-NeRF360 48 h ; INGP-Base 5m37s ; Plenoxels 25m49s | Mip-NeRF360 dataset (Tab. 1) |
| Mémoire / taille du modèle | 734 MB (30K) / 523 MB (7K) | Mip-NeRF360. T&T : 411 / 270 MB ; DB : 676 / 386 MB (Tab. 1) |
| Nombre de Gaussiennes | 1-5 M (scènes réelles) ; 200-500K (synthétique) | p. 2 ; p. 9 |
| Mémoire GPU | > 20 GB en pic à l'entraînement (grandes scènes) ; + 30-500 MB pour le rasteriseur au rendu | p. 11 |
| Compacité | 3,8 MB contre 9 MB pour Zhang et al. 2022, avec environ ¼ des points et SH de degré 2 | p. 9 |
| Latence | non rapportée (ni motion-to-photon, ni temps par image séparé des fps) | — |
| Rendu stéréo / casque XR / GPU mobile | non rapporté | — |

**Ablations (PSNR moyen à 30K, Tab. 3 p. 9).**

| Variante | PSNR moyen |
|---|---|
| Full | 26,05 |
| No-Clone | 25,91 |
| No-SH | 25,35 |
| Isotropic | 25,23 |
| No-Split | 23,90 |
| Random Init | 20,42 |
| Limited-BW (10 splats avec gradient) | 19,19 ; −11 dB sur Truck (p. 10) |

## Pertinence pour notre sujet

| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Article fondateur : il fixe la baseline et les datasets (Mip-NeRF360, T&T, Deep Blending, Blender) et donne un code public (PyTorch + CUDA, viewer SIBR). Il ne dit **rien sur la XR** (stéréo, casque, latence). Pour l'environnement XR, voir [kamdjou2024](../kamdjou2024_xr-dt-iiot/fiche.md). |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | Correspond presque mot pour mot à notre étape 2. Il donne l'initialisation SfM (Random Init : −5,6 dB, Tab. 3), Σ = RSSᵀRᵀ avec gradients analytiques, le calendrier SH progressif et les heuristiques clone/split/prune avec leurs seuils (τ_pos = 0,0002, φ = 1,6, reset de α toutes les 3000 itérations). |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | C'est la référence du rendu « visibility-aware » : tuiles 16×16, clés profondeur + tuile, tri radix, blending front-to-back avec arrêt précoce. Le portage casque (stéréo, GPU mobile, API graphique standard plutôt que CUDA) reste **entièrement à faire**. |
| 4. Évaluation (fps, latence, qualité, coût) | Donne un protocole réutilisable (split 1/8, PSNR/SSIM/LPIPS, temps d'entraînement, fps, mémoire). Il **manque la latence**, la mesure par œil, la consommation d'énergie et l'évaluation perceptive du popping. |

## Pour (vis-à-vis de notre problématique)

- **Marge de performance importante sur GPU de bureau.** 134-197 fps en moyenne sur A6000 (Tab. 1), soit 4 à 6 fois notre seuil de 30 fps. Hypothèse, calcul naïf de notre part : un rendu stéréo par deux passes indépendantes tiendrait encore plus de 60 fps sur ce matériel, mais c'est **non mesuré**.
- **Aucun réseau au rendu.** Le rendu est une rasterisation explicite, sans MLP ni ray-marching (p. 3). Le coût est donc prévisible et proportionnel au nombre de Gaussiennes visibles, ce qui aide à budgéter une image XR.
- **Pas de CNN en post-traitement.** On évite le scintillement temporel reproché aux méthodes neuronales à points (p. 2-3), un point important pour le confort en casque.
- **Pipeline par tuiles adapté au rendu à coût variable.** Les tuiles indépendantes et l'arrêt précoce par saturation de α se prêtent a priori au rendu fovéal (hypothèse).
- **Entraînement abordable.** 7K itérations (4m35s à 6m55s) donnent déjà une qualité comparable à InstantNGP (p. 9 ; Tab. 1). Cela suffit pour une capture rapide, par exemple pour un jumeau numérique.
- **Détail préservé à distance** sur les régions bien couvertes (p. 9), et **scènes non bornées sans contraction d'espace** (p. 6) : c'est utile pour des environnements industriels ou extérieurs complets.
- **Code et données publics** (p. 8) : on peut reproduire la baseline et mesurer nous-mêmes les fps par œil.

## Contre / limites

- **Aucune évaluation XR.** Le rendu stéréo, la résolution par œil, la latence motion-to-photon et le reprojection/ATW ne sont pas rapportés. Les fps sont mesurés dans un viewer de bureau (SIBR) à la résolution native des datasets (p. 8-9).
- **Dépendance à CUDA et à un GPU haut de gamme.** Les mesures sont faites uniquement sur A6000 et le rasteriseur est en CUDA (p. 8). Rien sur les GPU mobiles des casques autonomes, ni sur Vulkan/OpenXR.
- **Mémoire.** 270-734 MB par scène (Tab. 1), plus 30-500 MB pour le rasteriseur (p. 11). Les auteurs le reconnaissent : c'est nettement plus que les solutions NeRF (INGP : 13-48 MB). Pour un casque autonome, la compression est obligatoire ; ils la citent seulement comme perspective (p. 11).
- **Popping** (p. 10). Il apparaît quand de grandes Gaussiennes se forment, surtout dans les zones à apparence dépendante de la vue. Deux causes sont données : (i) le rejet par guard band, (ii) le tri par tuile et non par pixel, qui peut inverser brutalement l'ordre de blending. **Risque XR accru** (hypothèse) : les mouvements de tête sont continus et chaque œil a un ordre de tri propre, d'où des incohérences binoculaires possibles.
- **Aliasing.** Il n'y a pas d'antialiasing (laissé en perspective, p. 10). Or l'optique des casques et les variations de distance à la scène rendent l'aliasing très visible (hypothèse, hors papier).
- **Floaters et vues hors distribution.** On observe des artefacts dans les zones mal observées, des Gaussiennes allongées ou « splotchy » (p. 10 ; Fig. 11-12 p. 11), et plus de floaters avec une init aléatoire (p. 9). En XR, l'utilisateur sort librement des trajectoires de capture, donc cette limite est centrale.
- **Pas de régularisation** de l'optimisation (p. 10).
- **Coût d'entraînement.** 26-42 min à 30K itérations sur A6000 (Tab. 1), avec plus de 20 GB de mémoire GPU en pic pour les grandes scènes (p. 11). L'entraînement n'est donc pas faisable sur le casque. Environ 80 % du temps est passé en Python (p. 11), ce qui laisse de la marge d'optimisation.
- **Scènes statiques uniquement** (p. 4). Rien pour le dynamique ni pour les humains ; voir [cao2025_rt-fvhp](../cao2025_rt-fvhp/fiche.md).
- **SH sensibles à la couverture angulaire** (p. 8-9) : les captures d'intérieur « inside-out », typiques d'un atelier, sont justement le cas difficile.

## Idées à creuser pour une approche novatrice

Toutes les pistes ci-dessous sont des **hypothèses** à vérifier. Aucune n'est testée dans le papier.

- **H1 — Tri partagé entre les deux yeux.** On trierait une seule fois pour une caméra « cyclope » (centre inter-oculaire), avec des tuiles élargies, puis on réutiliserait cet ordre pour les deux yeux. On mesurerait le gain de temps face à deux tris indépendants et l'effet sur le popping et la cohérence binoculaire.
- **H2 — Rendu fovéal par tuiles.** Avec un suivi du regard, les tuiles périphériques utiliseraient un seuil de saturation de α plus bas, un degré SH réduit (bande 0-1) et élimineraient les petites Gaussiennes. Le découpage 16×16 et l'arrêt précoce s'y prêtent naturellement. À évaluer en fps par œil et en LPIPS fovéal.
- **H3 — Budget mémoire pour casque autonome.** On combinerait pruning (par opacité ou contribution), SH tronqués (le papier atteint 3,8 MB avec des SH de degré 2 en scène d'objet, p. 9) et quantification. Objectif : passer de plusieurs centaines de MB à un budget compatible avec un GPU mobile, sans perdre plus d'environ 0,5 dB (seuil à fixer).
- **H4 — Antipopping par stabilité temporelle.** Il s'agirait d'un culling plus propre que la guard band (piste suggérée p. 10) et d'un tri hystérétique d'une image à l'autre. On quantifierait le popping par une métrique temporelle (flicker entre images consécutives sur des trajectoires de tête réelles).
- **H5 — Split rendering edge/casque.** Le rendu 3DGS se ferait sur un GPU edge, avec streaming et reprojection côté casque. On comparerait latence et qualité à un rendu local compressé (H3), dans le cadre QoS/QoE et edge-cloud de [kamdjou2024](../kamdjou2024_xr-dt-iiot/fiche.md).
- **H6 — Capture rapide pour jumeau numérique.** On retiendrait le point de fonctionnement à 7K itérations (≈ 5-7 min, qualité comparable à INGP) et on mesurerait le compromis « temps de capture → qualité perçue en casque ». On pourrait y ajouter une régularisation des zones mal vues (absente, p. 10) pour limiter les floaters hors trajectoire.

## Citations clés

> « allow high-quality real-time (≥ 30 fps) novel-view synthesis at 1080p resolution » (`doc:192d1b7/tier:standard/page:1/block:8`)

> « Given a scaling matrix 𝑆 and rotation matrix 𝑅, we can find the corresponding Σ: Σ = R S Sᵀ Rᵀ » (`doc:192d1b7/tier:standard/page:4/block:17`, `…/page:4/block:18`)

> « Our method starts by splitting the screen into 16×16 tiles, and then proceeds to cull 3D Gaussians against the view frustum and each tile. » (`doc:192d1b7/tier:standard/page:6/block:9`)

> « Note that there is no additional per-pixel ordering of points, and blending is performed based on this initial sorting. As a consequence, our 𝛼-blending can be approximate in some configurations. » (`doc:192d1b7/tier:standard/page:6/block:10`)

> « We also occasionally have popping artifacts when our optimization creates large Gaussians […] One reason for these popping artifacts is the trivial rejection of Gaussians via a guard band in the rasterizer. » (`doc:192d1b7/tier:standard/page:10/block:15`)

> « our memory consumption is significantly higher than NeRF-based solutions. During training of large scenes, peak GPU memory consumption can exceed 20 GB in our unoptimized prototype. » (`doc:192d1b7/tier:standard/page:11/block:5`)

> « The majority (∼80%) of our training time is spent in Python code » (`doc:192d1b7/tier:standard/page:11/block:13`)

## Liens

- **Support de cours :** [kim2023 — CS482 slides 3DGS](../../supports/kim2023_cs482-slides-3dgs/slides.md). C'est une présentation pédagogique de ce même papier (rasterisation contre ray-casting, SfM, géométrie et couleur des Gaussiennes, contrôle adaptatif, tuiles 16×16), utile comme introduction avant cette fiche.
- **Papiers liés :**
  - [kamdjou2024_xr-dt-iiot](../kamdjou2024_xr-dt-iiot/fiche.md) : survey sur la XR en ressources contraintes avec jumeau numérique en IIoT (QoS/QoE, edge-cloud, compression). Il fournit le cadre des contraintes casque qui manque ici (pistes H3, H5).
  - [uzun2025_gs-alive-xr](../uzun2025_gs-alive-xr/fiche.md) : 3DGS appliqué à la XR. Le texte n'était pas encore disponible dans le dossier au moment de la rédaction ; le lien reste à qualifier (portage stéréo et casque de cette baseline ?).
  - [mirocha2025_beyond-dt](../mirocha2025_beyond-dt/fiche.md) : au-delà du jumeau numérique. Texte non encore disponible ; lien avec la piste H6 (capture rapide pour DT) à vérifier.
  - [cao2025_rt-fvhp](../cao2025_rt-fvhp/fiche.md) : temps réel pour le free-viewpoint et les humains (d'après le nom du dossier). Texte non encore disponible ; il complèterait la limite « scènes statiques uniquement ».
- **Travaux cités à suivre (depuis ce papier) :** Mip-NeRF360 (Barron 2022, référence qualité), InstantNGP (Müller 2022), Plenoxels (Fridovich-Keil 2022), Pulsar (Lassner 2021, inspiration du rasteriseur), EWA splatting (Zwicker 2001), MobileNeRF (Chen 2022, rendu mobile, pertinent pour les casques autonomes).
