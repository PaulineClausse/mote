---
citekey: franke2024_vr-splatting
mineru_doc: 93e1df8
type: article de revue   # Proc. ACM Comput. Graph. Interact. Tech. 8(1), Article 18
statut: fiche complète
tags: [3dgs, vr, rendu-fovéal, eye-tracking, points-neuronaux, trips, hybride, stopthepop, htc-vive-pro-eye, rtx-4090, étude-utilisateurs, occlusion-culling, 90hz]
---

# VR-Splatting: Foveated Radiance Field Rendering via 3D Gaussian Splatting and Neural Points

**Référence :** Linus Franke, Laura Fink, Marc Stamminger (FAU Erlangen-Nürnberg) (2025). *VR-Splatting: Foveated Radiance Field Rendering via 3D Gaussian Splatting and Neural Points.* Proc. ACM Comput. Graph. Interact. Tech. 8(1), Article 18, 21 p. DOI [10.1145/3728302](https://doi.org/10.1145/3728302) · arXiv [2410.17932](https://arxiv.org/abs/2410.17932) (v2, avril 2025) · projet : lfranke.github.io/vr_splatting (`doc:93e1df8/tier:standard/page:1`, `page:2`)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Rendu fovéal **hybride** guidé par eye-tracking : un 3DGS pauvre en primitives (0,3–0,5 M), trié sans popping (StopThePop), rend tout le champ de vision pour la périphérie ; un rendu de points neuronaux (TRIPS + petit CNN) ajoute le détail net dans un crop fovéal de 512 px, les points étant cullés par la profondeur issue des Gaussiennes ; 10,9 ms/frame à 2016 × 2240 px par œil sur RTX 4090, soit la cible 90 Hz (`page:1`, `page:3`, `page:12`).

## Problème traité
- 3DGS ne donne des détails nets qu'avec beaucoup de petites Gaussiennes, et son coût croît avec le nombre de primitives (tuilage + tri) ; le rendu de points neuronaux (TRIPS) rasterise vite des millions de points mais son CNN coûte cher avec la résolution. Aucun des deux ne tient la cadence VR à pleine résolution avec leurs réglages par défaut (`page:1`, `page:2`, `page:3`).
- « Sweet spot » identifié : 3DGS lisse et temporellement stable pour la périphérie (sensible au flicker), points neuronaux + CNN pour un petit crop fovéal (`page:3`).
- Un « VRGS » (3DGS limité à 0,5 M primitives pour tenir le budget) devient flou et sous-reconstruit (`page:7`, `page:12`).

## Méthode / contributions
- **Étude pilote** (4 experts, scène Garden) sur une combinaison naïve : popping 3DGS très visible en VR (amplifié par la loupe des lentilles et le peu de primitives), dérive de couleurs entre les deux représentations (perte VGG), latence/clignements de l'eye-tracker, bruit temporel des points (`page:6`, `page:7`, `page:8`).
- **Périphérie** : 3DGS avec tri hiérarchique par pixel de **StopThePop**, densification limitée (seuil de gradient 0,0002, intervalle 200, élagage d'opacité 0,005, décroissance 0,999) → 0,3–0,5 M Gaussiennes ; rendu de l'**image complète** (fovéa non masquée) + **carte de profondeur approchée** accumulée par α-blending (éq. 1) (`page:8`, `page:9`, `page:11`).
- **Fovéa** : l'eye-tracker est interrogé **après** le rendu périphérique ; sous-frustum autour du point de fixation ; points hors frustum rejetés tôt, points **occultés** rejetés contre la profondeur des Gaussiennes (réduit le temps, accélère la convergence, supprime le flicker des points) ; le crop 3DGS est injecté dans le CNN qui n'ajoute plus que le détail fin → filtres de la couche pleine résolution divisés par 2 (couche qui représentait > 70 % de l'inférence TRIPS) (`page:9`).
- **Combinaison** : facteur par pixel mêlant distance au point de fixation (rayon fovéal d_f = 256 px, début du mélange m = 0,75) et un terme de bords Sobel (γ = 0,2), lissé par smootherstep ; tone-mapping différentiable type ADOP (`page:9`, `page:10`).
- **Optimisation bout-en-bout** : L1 + D-SSIM + VGG (points seulement) + régulariseur de moyenne de couleur fovéa/périphérie ; point de fixation tiré aléatoirement à chaque itération (équivaut au cropped training de TRIPS) ; 30K it. Gaussiennes puis 30K it. points (Gaussiennes figées), ~5 M points neuronaux (`page:10`, `page:11`).
- **Inférence VR** : attributs « bakés », demi-précision, **CNN évalué en batch pour les deux yeux** (cuDNN), fusion des 8 couches de pyramide TRIPS (−2 ms, ×4 mémoire GPU jugé négligeable vu la petite zone) (`page:11`).
- **Taille de fovéa** : 15,7 px/degré (estimation Kreylos), fovéa max 17°, facteur de résolution pilote 1,4× → ~400 px, arrondi à 512 px pour compenser l'imprécision de l'eye-tracker (`page:11`).

## Résultats chiffrés
| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| Matériel | **HTC Vive Pro Eye** (eye-tracker 120 Hz), **une RTX 4090** ; casque PC-VR, liaison non décrite | `page:11`, `page:12` |
| Résolution | **2016 × 2240 px par œil** (recommandée par le driver) | `page:11`, `page:13` |
| Cible | **90 Hz = 11,1 ms/frame** | `page:1`, `page:11` |
| Temps de frame | **Ours 10,9 ms** ; VRGS 10,4 ms ; 3DGS 23,1 ms ; TRIPS 33,1 ms ; SA Fov-NeRF 16,1 ms (1440×1700) ; HybridNeRF 21,8 ms ; VR-NeRF 165,3 ms (2064×2096) | RTX 4090 ; valeurs NeRF reprises de Shi et al./Turki et al. (`page:12`). **Stéréo non explicitée** : budget « par frame » et CNN batché 2 yeux suggèrent un temps pour les deux yeux, sans que ce soit écrit |
| Décomposition (Tab. 3) | Périphérie GS 4,9 · points fovéaux 3,5 · CNN 1,6 · combinaison 0,5 · tone-mapping 0,4 = 10,9 ms ; sans correctif popping −2,3 ms ; sans pénalité d'opacité +2,5 ms ; sans culling profondeur +0,4 ms ; CNN non réduit +0,3 ms | `page:14` |
| Qualité fovéale Mip-NeRF 360 | Ours LPIPS **0,237** / PSNR 26,03 / SSIM 0,755 ; VRGS 0,286 / 26,45 / 0,765 ; 3DGS 0,247 / 27,01 / 0,804 ; TRIPS 0,222 / 25,19 / 0,761 | métriques calculées **sur la fovéa seule** (`page:12`) |
| Qualité fovéale T&T | Ours 0,196 / 25,97 / 0,815 ; VRGS 0,211 / 26,73 / 0,854 ; 3DGS 0,198 / 27,15 / 0,874 | idem (`page:12`) |
| JOD (FovVideoVDP, mode fovéal, image entière) | Mip-360 : Ours **8,02** vs VRGS 7,74 (3DGS 7,90, TRIPS 8,06) ; T&T : 8,16 vs 8,11 (3DGS 8,24) | preset HTC Vive Pro, 13,15 px/deg (`page:12`) |
| Entraînement | Ours **1,4 h** ; VRGS 0,4 h ; 3DGS 0,5 h ; TRIPS 2,5 h | GPU d'entraînement non précisé (`page:12`) |
| Primitives | 0,3–0,5 M Gaussiennes + ~5 M points neuronaux | `page:11` |
| Mémoire | Non rapportée globalement (seule mention : pyramide fusionnée ×4 mémoire, négligeable) | `page:11` |
| Latence | **Non mesurée** ; seul levier : lecture du regard retardée après le rendu périphérique (« réduit drastiquement le lag ») ; rappel bibliographique : 50–70 ms tolérables pour l'eye-tracking | `page:4`, `page:11` |
| Étude utilisateurs | **12 participants** (22–30 ans, 4 F / 8 H), assis, Vive Pro Eye calibré, **2AFC** Ours vs VRGS, bascule libre à la barre d'espace, pause grise 0,5 s, 20 essais/personne (240 décisions), 5 scènes (garden, bicycle, bonsai, family, playground), comité d'éthique | `page:12`, `page:13` |
| Résultats étude | **~76 % préfèrent Ours** (SD = 0,196), test binomial p < 0,005 ; garden > 90 %, playground 67 % | `page:14` |

## Artefacts VR identifiés et traitement
| Artefact | Traitement |
|---|---|
| Popping 3DGS (amplifié par lentilles et peu de primitives) | tri hiérarchique **StopThePop** (coût +2,3 ms) (`page:7`, `page:8`, `page:14`) |
| Flou / sous-reconstruction en réduisant les Gaussiennes | points neuronaux + CNN en fovéa ; densification plus fine (AbsGS, Hierarchical 3DGS) ; 3DGS-MCMC testé et rejeté (fonds dégradés, Gaussiennes « piquantes ») (`page:8`, `page:15`) |
| Flicker/bruit des points neuronaux | culling d'occlusion par profondeur des Gaussiennes (`page:9`) |
| Couture fovéa/périphérie, dérive de couleur | masque position + bords Sobel, régulariseur de moyenne (`page:9`, `page:10`) |
| Lag d'eye-tracking | lecture tardive du regard, fovéa agrandie (`page:11`, `page:15`) |
| Floaters traversés perçus comme flicker | **non résolu** (`page:15`) |

Réutilisations : **StopThePop** (algorithme de tri + profondeur approchée) ; **Mip-Splatting** cité seulement comme extension algorithmique (`page:5`), non utilisé ; **Speedy-Splat** non cité ; implémentation basée sur gaussian-splatting-cuda (Patas 2023) (`page:10`).

## Stéréo (piste P2) — verdict
- Les Gaussiennes sont rendues « pour les deux yeux » (`page:3`) sans partage décrit du tri ni de la projection ; le seul partage explicite est le **batch CNN des deux yeux** (`page:11`).
- **Verdict P2 : non réalisée.** VR-Splatting ne mutualise ni tri ni projection entre yeux.

## Fovéation / edge (piste P1) — verdict
- Partition **en espace écran pilotée par le regard** (eye-tracking), deux représentations différentes, **les deux rendues sur le même GPU local** ; aucun rendu déporté, aucun edge, aucun casque autonome.
- Le papier utilise bien une notion de **visibilité** (profondeur 3DGS pour culler les points fovéaux), mais pour accélérer, pas pour répartir entre machines ; aucune partition par distance (proche/lointain).
- **Verdict P1 : seule la partie « fovéa détaillée / périphérie bon marché » en local est faite** (ici avec un hybride 3DGS/points). Le partage casque/edge par visibilité reste ouvert ; P1 doit se positionner clairement contre VR-Splatting (partition fovéale) et VRSplat (fovéation 1 passe) en insistant sur la **distribution** et le critère **profondeur**.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Tableau comparatif des méthodes RF « VR-capables » à résolution casque (Tab. 1) ; Vive Pro Eye + RTX 4090 ; rappels HVS (fovéa < 10°, bâtonnets à 17°) (`page:4`, `page:12`) |
| 2. Gaussiennes 3D depuis SfM, covariance anisotrope | Densification contrainte pour budget VR, comparaison MCMC ; init SfM/MVS COLMAP (`page:6`, `page:11`, `page:15`) |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | Culling d'occlusion par profondeur 3DGS, sous-frustum fovéal, budget 11,1 ms décomposé |
| 4. Évaluation (fps, latence, qualité, coût) | Métrique **JOD FovVideoVDP** adaptée au fovéal ; étude 2AFC ; pas de latence mesurée |

## Pour (vis-à-vis de notre problématique)
- Tient **90 Hz à 2016 × 2240 px par œil** (≈ 2,2× la surface 1080p par œil) sur un GPU grand public.
- Décomposition fine du budget : périphérie 3DGS ≈ 4,9 ms pour 0,3–0,5 M Gaussiennes à pleine résolution.
- Montre qu'une périphérie 3DGS « pauvre » suffit perceptuellement si elle est sans popping : argument fort pour déporter/dégrader la périphérie (P1).
- Métrique JOD fovéale et protocole 2AFC réutilisables.

## Contre / limites
- **Dépend de l'eye-tracking** (absent sur Quest 3 grand public) ; fovéa agrandie faute de précision (`page:11`, `page:15`).
- Pipeline lourd : deux représentations (0,5 M Gaussiennes + 5 M points + CNN), entraînement 1,4 h, dépendance COLMAP MVS dense (`page:12`, `page:15`).
- Qualité fovéale **PSNR/SSIM inférieurs** à VRGS et à 3DGS ; seul LPIPS/JOD favorables (`page:12`).
- Marge minime (10,9 vs 11,1 ms), sur RTX 4090 : inapplicable tel quel sur casque autonome.
- Stéréo et latence non documentées ; floaters non traités (`page:15`).
- Étude utilisateurs petite (12 p., 22–30 ans), comparée seulement à VRGS.

## Idées à creuser pour une approche novatrice
- *Hypothèse (P1)* : reprendre le schéma « périphérie 3DGS pauvre + fovéa riche » mais en le **distribuant** : edge = image périphérique pleine (4,9 ms sur 4090) + profondeur approchée ; casque = fovéa/proche, composition locale avec le masque position+bords de VR-Splatting.
- *Hypothèse* : utiliser la carte de profondeur approchée (éq. 1) comme **signal de visibilité** pour partitionner proche/lointain et comme support de reprojection (timewarp) de la couche edge pour masquer la latence réseau.
- *Hypothèse (P2)* : l'image périphérique basse fréquence est un bon candidat au **partage stéréo** (une vue centrale reprojetée vers les deux yeux) ; à tester avec JOD.
- *Hypothèse (P3)* : piloter le rayon fovéal d_f et le nombre de Gaussiennes périphériques par un contrôleur QoE (JOD comme proxy de QoE).
- *Hypothèse* : remplacer la fovéa à points neuronaux par une fovéa 3DGS dense (même représentation, LOD) pour éviter la double représentation et la dérive de couleur.

## Citations clés
> « our method provides high fidelity in the foveal region and meets the 90 Hz VR framerate requirements at 2016 × 2240 pixels per eye. » (`doc:93e1df8/tier:standard/page:1`)

> « Given a VR headset with integrated eye tracking, our method first renders a low-detailed Gaussian rendering for both eyes for the full field of view. Hereby, we find that pixel-correct sorting [Radl et al. 2024] proves vital for rendering smoothly. » (`doc:93e1df8/tier:standard/page:3`)

> « Additionally, we use the approximate depth buffer rendered (Eq. 1) from the Gaussians to discard occluded points. » (`doc:93e1df8/tier:standard/page:9`)

> « Our method is the only that surpasses the VR framerate limit of 11.1ms per frame » (`doc:93e1df8/tier:standard/page:11`)

## Liens
- Papiers liés :
  - [VRSplat](../tu2025_vrsplat/fiche.md) — concurrent direct : fovéation fixe 1 passe, 3DGS seul, 72 FPS Quest 3.
  - [StopThePop](../radl2024_stopthepop/fiche.md) — tri réutilisé pour la périphérie et la profondeur approchée.
  - [3DGS](../kerbl2023_3dgs/fiche.md) — base de la périphérie.
  - [Hierarchical 3DGS](../kerbl2024_hierarchical-3dgs/fiche.md) — heuristique de densification reprise.
  - [Mip-Splatting](../yu2023_mip-splatting/fiche.md), [2DGS](../huang2024_2dgs/fiche.md), [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md) — cités comme extensions, non utilisés.
  - [Speedy-Splat](../hanson2024_speedy-splat/fiche.md) — non cité ; pourrait réduire le coût périphérique.
  - [VR-GS](../jiang2024_vr-gs/fiche.md) — cité comme application VR ne visant pas l'efficacité.
  - [A3FR (fovéal)](../xin2025_a3fr-foveated/fiche.md), [Edge collaboratif GS](../wan2025_edge-collab-gs/fiche.md) — à croiser pour P1.
