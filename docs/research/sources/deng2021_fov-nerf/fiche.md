---
citekey: deng2021_fov-nerf
mineru_doc: 000550c
type: article de revue   # gabarit IEEE TVCG ; publié TVCG 28(11), 2022 selon la bibliographie de Kleinbeck 2024
statut: fiche complète
tags: [nerf, vr, rendu-fovéal, eye-tracking, stéréo, acuité-stéréo, disparité, htc-vive-pro-eye, rtx-3090, étude-utilisateurs, fovvideovdp, latence, optimisation-latence-qualité]
---

# FoV-NeRF: Foveated Neural Radiance Fields for Virtual Reality

**Référence :** Nianchen Deng, Zhenyi He, Jiannan Ye, Budmonde Duinkharjav, Praneeth Chakravarthula, Xubo Yang, Qi Sun (Shanghai Jiao Tong Univ., NYU, UNC) (2021, v2 juillet 2022). *FoV-NeRF: Foveated Neural Radiance Fields for Virtual Reality.* arXiv [2103.16365](https://arxiv.org/abs/2103.16365). Gabarit IEEE TVCG, sans venue explicite dans le texte (`doc:000550c/tier:standard/page:1`). La bibliographie de [Kleinbeck 2024](../kleinbeck2024_multilayer-gs-anatomy/fiche.md) le cite comme IEEE TVCG 28(11):3854–3864, 2022, DOI 10.1109/TVCG.2022.3203102 (`doc:3efd049/tier:standard/page:10`). Code : github.com/dengnianchen/fovnerf (`page:2`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Le **premier NeRF pensé pour le regard** (« gaze-contingent ») en VR. Une représentation égocentrique en sphères concentriques est rendue sous forme de trois « images élémentaires » par œil (fovéa 0–20°, moyenne excentricité 0–45°, champ entier 0–110°). Deux réseaux distincts, réglés par une optimisation latence/qualité sous contrainte l < 24 ms, les produisent. La périphérie est rendue **une seule fois depuis l'œil cyclope**, puis décalée de ±Δx_g/2 selon la vergence au lieu d'être rendue pour chaque œil. Résultat : 21,5 ms/frame stéréo (≈ 50 fps annoncés) en 1440×1600 par œil sur une RTX 3090, contre 90 s pour NeRF. L'image est jugée indiscernable de la vérité terrain (42,4 % de votes en 2AFC) (`page:3`, `page:5`, `page:6`, `page:9`).

## Problème traité
- En VR, NeRF combine grand champ de vision, haute résolution, stéréo et vue égocentrique « inside-out ». Il en résulte une latence élevée (≈ 0,5 s par frame stéréo, même avec la représentation égocentrique) et une qualité faible (ghosting, basse résolution) sur de grands environnements (`page:1`, `page:3/block:10`).
- Le rendu fovéal classique suppose l'accès aux maillages. Les méthodes à base d'images (NeRF, panoramas) n'intégraient pas encore le système visuel humain (`page:1`, `page:2`).

## Méthode / contributions
- **Représentation égocentrique** : N sphères concentriques de rayons r_i. Un MLP (N_m couches × N_c canaux) reçoit en **une seule inférence** les N intersections du rayon avec les sphères et renvoie un vecteur (R, G, B, D) de dimension N (éq. 1). NeRF fait une inférence par échantillon. La scène est couverte par 64 sphères réparties entre les réseaux (`page:3/block:5`, `block:8`, `page:5/block:14`).
- **Mécanisme 1 : acuité monoscopique adaptative (partition fovéa/périphérie)** (`page:3/block:14`, `block:15`, `page:4` Fig. 3) :
  - trois images élémentaires par œil. I_f couvre 0–20° (fovéa), I_m 0–45° (moyenne excentricité), I_p 0–110° (champ entier du casque) ;
  - résolutions : I_f 256², I_m 256², I_p 230×256, soit **12,8 / 5,7 / 2,33 pixels par degré** ;
  - deux réseaux « orthogonaux ». C_foveal (N_m = 4, N_c = 512, N = 16) produit I_f. C_periph (N_m = 4, N_c = 256, N = 32) produit I_m et I_p (`page:5/block:14`) ;
  - **I_p ne dépend pas du regard**, seulement de la pose de tête. I_f et I_m suivent le regard (`page:3/block:14`).
- **Mécanisme 2 : acuité stéréoscopique adaptative (astuce stéréo)** (`page:3/block:17`, `block:18`, `page:4` Fig. 4) :
  - motivation : la stéréopsie humaine décroît avec l'excentricité (réf. Mochizuki et al.) ;
  - on infère **4 images au lieu de 6** : I_f pour chaque œil (stéréo complète en fovéa), et I_m, I_p une seule fois pour la vue « c » au milieu des deux yeux (disparité nulle) ;
  - pour limiter le désalignement à la jonction I_f/I_m, **I_m^c et I_p^c sont translatées horizontalement** de +Δx_g/2 pour l'œil gauche et −Δx_g/2 pour le droit, avec Δx_g = x_g^l − x_g^r la différence horizontale (en pixels) entre les points de regard des deux yeux, c.-à-d. la vergence. La périphérie reçoit ainsi une **disparité uniforme égale à celle du point fixé**.
- **Composition** : IBR dans un fragment shader. Couches voisines fondues par smooth-step sur 40 % de la couche interne, puis renforcement de contraste façon Patney et al. pour compenser la faible résolution en pixels par degré (PPD) de la périphérie (`page:3/block:20`).
- **Optimisation conjointe latence/qualité** (`page:5/block:4` à `block:9`) :
  - erreur spatio-temporelle E(N, N_m, N_c) (éq. 7). Elle combine l'erreur de couleur du réseau et l'erreur de reprojection due à la latence l ;
  - **argmin E s.t. l < L₀ = 24 ms** (éq. 8) ;
  - L₀ se déduit du seuil de ≈ 50 ms pour un système fovéal (Albert et al.), moins ≈ 12 ms d'eye-tracking et ≈ 14 ms de « photon submission ». Ces deux valeurs sont reprises de la littérature, pas mesurées ;
  - l'optimisation est **hors ligne** et porte sur des hyperparamètres discrets (N, N_m, N_c). Les rayons r restent uniformes (`page:9/block:28`).
- **Données** : 4 scènes synthétiques (barbershop et classroom sous Blender Cycles, lobby et stones sous Unity). Jeux fovéaux en 400×400 à 40° de FoV, jeux périphériques en 400×400 à 60°. Scènes réelles : vidéo au téléphone, une image par seconde, poses COLMAP, jeu périphérique sous-échantillonné ×2 (`page:5/block:13`).

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| Matériel | OpenGL + CUDA + **TensorRT**, Xeon Gold 6230R, 256 GB de RAM, « NVIDIA GTX 3090 » (sic, sans doute une RTX 3090) | PC, `page:5/block:15` |
| Casque | **HTC Vive Pro Eye** avec eye-tracking, 1440×1600 par œil, FoV 110° | `page:5/block:22`, `page:8/block:19` |
| Temps par composant (Tab. 2) | inférence fovéale **8 ms par œil** · inférence moyenne + lointaine périphérie **5,4 ms par œil** · fondu + contraste 0,1 ms | 1440×1600 par œil, stéréo, `page:9/block:9` |
| Temps total (Tab. 2) | sans fovéation 562 ms · sans fovéation stéréo 27 ms · **méthode complète 21,5 ms** · NeRF 9,0×10⁴ ms · PANO 1,0×10⁴ ms | idem. Cohérent : 2×8 + 5,4 + 0,1 = 21,5 ms, et 2×8 + 2×5,4 + 0,1 ≈ 27 ms |
| fps annoncés | « ≈ 30 fps » avec fovéation spatiale seule, **« 50 fps »** complet (1000/21,5 ≈ 46,5 fps, calcul de ma part) | `page:9/block:8` |
| Gain de l'astuce stéréo | 27 → 21,5 ms, soit **−20 %** (calcul de ma part) : on économise l'inférence périphérique d'un œil | Tab. 2 |
| Incohérence | Le texte annonce **31,8 ms** sans fovéation stéréo, le Tab. 2 donne 27 ms | `page:8/block:19` vs `page:9/block:9` |
| Réduction annoncée | « jusqu'à 99 % » (résumé), « de 9 s à 20 ms » (intro), « 99,8 % » (§5.2) | `page:1`, `page:2`, `page:6` |
| Étude 2AFC (statique) | **12 participants** (6 F, âge moyen 23,25), assis, images stéréo fixes en 1440×1600 par œil, 500 ms par stimulus, 36 essais, fixation contrôlée (essai rejeté si le regard s'écarte de > 5°) | `page:5/block:22`, `page:6` |
| Résultats 2AFC | OURS vs GT : **42,4 %** pour OURS (≈ hasard) · GT vs NeRF : 91,0 % pour GT · OURS vs NeRF : 89,6 % pour OURS (p < 0,005, d de Cohen = 3,5) | `page:6` |
| LPIPS par excentricité | OURS < NeRF de 0 à ≤ 15° (jusqu'à 35° sur 2 scènes) ; OURS > NeRF au-delà de 40°, mais < F-GT (fovéation image) | 4 scènes, 25 vues, pas de 5°, `page:6` |
| FovVideoVDP (dynamique) | OURS **8,26** ± 0,14 · F-GT 7,99 · M-GT (métamères) 6,77 · NeRF ≤ 5,1 | 12 trajectoires tête + regard de ≈ 2 s (100 frames), **œil gauche seul**, `page:8/block:7`, `block:8` |
| PSNR / SSIM | **Non rapportés** (seul LPIPS) | — |
| Entraînement | 200 epochs par réseau ; **durée non rapportée** | `page:5/block:15` |
| Mémoire / taille modèle | Non rapportées | — |
| Latence motion-to-photon | **Non mesurée**. Seul le budget L₀ = 24 ms (dérivé de la littérature) est donné | `page:5/block:7` |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Référence historique du rendu fovéal de champs de radiance. Casque avec eye-tracking, TensorRT, pas de moteur de jeu |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | Aucun (NeRF implicite, sphères concentriques). Données réelles via COLMAP (`page:5/block:13`) |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | **Fort sur le plan perceptuel** : bornes d'excentricité (20/45/110°), PPD par couche, fondu à 40 %, et astuce stéréo périphérique par translation selon la vergence |
| 4. Évaluation (fps, latence, qualité, coût) | Protocole réutilisable : 2AFC avec fixation contrôlée, LPIPS par tranche d'excentricité, **FovVideoVDP sur trajectoires tête + regard enregistrées** (même trajectoire pour toutes les méthodes) |

## Pour (vis-à-vis de notre problématique)
- **Modèle perceptuel explicite et chiffré**, transposable tel quel à un rendu 3DGS fovéal : trois anneaux, 12,8/5,7/2,33 PPD, fondu smooth-step sur 40 %, renforcement de contraste (`page:3`).
- **Astuce stéréo simple et peu coûteuse** : 4 rendus au lieu de 6, soit −20 % du temps total, sans perte perçue en 2AFC (`page:3/block:18`, `page:9/block:9`).
- **La périphérie I_p ne dépend que de la pose de tête**, pas du regard. Elle peut donc être calculée ailleurs ou avec plus de latence que la fovéa, ce qui est un argument direct pour P1′ (`page:3/block:14`).
- Formulation **latence sous contrainte** (argmin E s.t. l < L₀) avec un budget motivé par la perception (50 ms fovéal − eye-tracking − affichage) : c'est un précédent formel pour P3′ (`page:5/block:7`, `block:8`).
- L'évaluation dynamique par FovVideoVDP complète le JOD de [VR-Splatting](../franke2024_vr-splatting/fiche.md).

## Contre / limites
- **NeRF, pas 3DGS** : le coût est dominé par l'inférence MLP par pixel, donc la réduction de pixels suffit. En 3DGS, la fovéation par pixels plafonne parce que le tri et le prétraitement restent entiers ([A3FR](../xin2025_a3fr-foveated/fiche.md)). Les gains ne se transposent pas mécaniquement.
- **21,5 ms ≈ 46 fps** en 1440×1600 sur une RTX 3090 : c'est sous les 90 Hz visés pour ce casque ([VR-Splatting](../franke2024_vr-splatting/fiche.md)), et loin d'un casque autonome.
- **Eye-tracking obligatoire** : Δx_g vient de la vergence mesurée.
- La translation périphérique ne donne qu'une **disparité uniforme** (celle du point fixé). Les objets périphériques à une autre profondeur ont une disparité fausse. Aucune mesure d'erreur stéréo n'est donnée (seule une anaglyphe qualitative, Fig. 4).
- Déplacement limité à la sphère la plus interne ; aliasing périphérique non traité (`page:9/block:25`, `block:26`).
- Scènes surtout synthétiques et datasets propres (400×400) ; PSNR/SSIM absents ; incohérence 31,8 vs 27 ms ; latence réelle et motion-to-photon non mesurées.
- L'étude utilisateurs est **statique** (500 ms, regard fixe) ; le dynamique n'est évalué que par une métrique objective.

## Transposition au 3DGS (hypothèses)
- **Partition fovéa/périphérie** : rendre la fovéa (≈ 20°) par œil avec l'ensemble complet de Gaussiennes, et la périphérie à 2–6 PPD avec un **LOD grossier**. Exemples : coupe τ de [Hierarchical 3DGS](../kerbl2024_hierarchical-3dgs/fiche.md), couche basse de [LapisGS](../shi2024_lapisgs/fiche.md), ou modèle élagué façon [LightGaussian](../fan2023_lightgaussian/fiche.md). Le gain vient alors du nombre de Gaussiennes, pas seulement des pixels (enseignement n°1 de `options.md`).
- **Astuce stéréo en 3DGS** : un seul prétraitement + tri + rastérisation basse résolution pour la périphérie depuis l'œil cyclope, puis translation ±Δx_g/2 dans le compositeur. On économise la moitié du coût périphérique, là où [Nebula](../zhu2025_nebula/fiche.md) reprojette par disparité par pixel en ASIC. Sans eye-tracking, on remplacerait Δx_g par la disparité d'une **profondeur de référence** : profondeur médiane du centre de l'image, tirée du buffer de profondeur α-blendé de 3DGS.
- **Variante plus fidèle** : pour chaque pixel périphérique, utiliser la profondeur 3DGS au lieu d'un décalage uniforme (warping par disparité). On se rapproche de Nebula, mais sur un GPU standard, et on peut mesurer l'erreur de désocclusion.
- Le fondu à 40 % des couches est à combiner avec StopThePop pour éviter le popping à la frontière fovéa/périphérie ([VR-Splatting](../franke2024_vr-splatting/fiche.md)).

## Verdict vis-à-vis de nos pistes
- **P1′ (partage casque/edge par région)** : **non réalisée, mais éclairée**. FoV-NeRF fait tout localement. Il fournit en revanche la **frontière naturelle** du partage : fovéa I_f par œil (dépend du regard, critique en latence, haute PPD) → casque ; périphérie I_p cyclope (ne dépend que de la tête, 2,33 PPD, **une seule image pour les deux yeux** grâce au décalage) → edge. Le décalage stéréo diviserait aussi par deux le débit edge → casque pour la périphérie (hypothèse). Q-VR et EDC 🔎 restent à vérifier pour l'antériorité côté maillages.
- **P2 résiduelle (mutualisation stéréo)** : FoV-NeRF réalise une mutualisation **partielle et perceptuelle**. La stéréo reste complète en fovéa, la périphérie est partagée par translation, en NeRF. Ce n'est ni un tri partagé ni une projection partagée. Avec Nebula (ASIC) et le tri partagé de [Kleinbeck 2024](../kleinbeck2024_multilayer-gs-anatomy/fiche.md), P2 est **encore moins nouvelle**. Il reste une combinaison possible pour le 3DGS : fovéa stéréo + périphérie cyclope décalée, avec **erreur stéréo mesurée** (à vérifier contre 🔎 FoV-GS, TVCG 2025).
- **P3′** : l'éq. 8 (argmin E s.t. l < 24 ms) est un **précédent de contrôle latence/qualité**, mais hors ligne et sur des hyperparamètres de réseau. Il faut le citer. P3′ (en ligne, leviers continus, contraintes casque) reste ouverte.
- **P6** : aucune mesure motion-to-photon. Le protocole FovVideoVDP sur trajectoires rejouées est réutilisable.
- **P4, P5** : sans objet.

## Idées à creuser pour une approche novatrice
- *Hypothèse :* **« FoV-3DGS » split** (P1′) : fovéa 3DGS par œil sur le casque, périphérie cyclope à ≈ 2–3 PPD rendue sur l'edge avec un LOD grossier, envoyée **en une seule image** et décalée localement selon la vergence ou une profondeur de référence. On mesurerait débit, latence et FovVideoVDP.
- *Hypothèse :* dans P3′, le **rayon fovéal** et les **PPD par couche** deviennent des variables de décision continues. La contrainte l < L₀ de FoV-NeRF sert de contrainte de latence, et le seuil de 50 ms (Albert et al.) de borne perceptuelle.
- *Hypothèse :* comparer, sur un même 3DGS, trois modes stéréo : 2 rendus complets, tri partagé ([Kleinbeck](../kleinbeck2024_multilayer-gs-anatomy/fiche.md)), et périphérie cyclope décalée (FoV-NeRF). On mesurerait le temps et l'erreur stéréo (FLIP, FovVideoVDP) : c'est la contribution P2 résiduelle la plus propre.
- *Hypothèse :* reprendre le protocole « trajectoires tête + regard enregistrées puis rejouées » pour le banc P6. Toutes les conditions sont alors évaluées sur la même trajectoire.

## Citations clés
> « we perform the computation with I_f^{l,r}, I_m^c, and I_p^c instead of inferring 6 elemental images, where c indicates the view at the midpoint of the left and right eyes […] we shift I_m^c and I_p^c according to the vergence of eyes » (`doc:000550c/tier:standard/page:3/block:18`)

> « our full method with both spatial and stereoscopic foveation achieves a high performance of 50 FPS » (`doc:000550c/tier:standard/page:9/block:8`)

> « Given our test device's eye-tracking latency ˜12ms and the photon submission latency ˜14ms, the synthesis and rendering latency shall be less than L0 = 24ms » (`doc:000550c/tier:standard/page:5/block:7`)

## Liens
- Papiers liés :
  - [VR-Splatting (Franke 2024)](../franke2024_vr-splatting/fiche.md) : fovéal hybride 3DGS + points neuronaux, compare « SA Fov-NeRF » (16,1 ms, 1440×1700) ;
  - [VRSplat (Tu 2025)](../tu2025_vrsplat/fiche.md) : cite FoV-NeRF, fovéation fixe en une passe ;
  - [A3FR (Xin 2025)](../xin2025_a3fr-foveated/fiche.md) : limites de la fovéation par pixels en 3DGS ;
  - [Nebula (Zhu 2025)](../zhu2025_nebula/fiche.md) : mutualisation stéréo par reprojection de disparité (ASIC) ;
  - [Kleinbeck 2024](../kleinbeck2024_multilayer-gs-anatomy/fiche.md) : tri partagé entre les deux yeux sous Unity ;
  - [Li 2025 (survey RF-XR)](../li2025_rf-xr-survey/fiche.md) : cite le décalage de disparité de FoV-NeRF ;
  - [ECO-GS (Wan 2025)](../wan2025_edge-collab-gs/fiche.md) : edge + pixels, pour P1′ ;
  - [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) : éq. 1, cadre de P3′.
