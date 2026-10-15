---
citekey: sun2024_3dgstream
mineru_doc: f99b745
type: conférence   # venue non indiquée dans le texte ; arXiv 2403.01444v4 [cs.CV], 11 juin 2024
statut: fiche complète
tags: [3dgs, scenes-dynamiques, free-viewpoint-video, streaming, entrainement-en-ligne, hash-encoding, neural-transformation-cache, n3dv, meet-room, rtx-3090]
---

# 3DGStream: On-the-Fly Training of 3D Gaussians for Efficient Streaming of Photo-Realistic Free-Viewpoint Videos

**Référence :** Jiakai Sun, Han Jiao, Guangyuan Li, Zhanjie Zhang, Lei Zhao, Wei Xing (2024). *3DGStream: On-the-Fly Training of 3D Gaussians for Efficient Streaming of Photo-Realistic Free-Viewpoint Videos.* arXiv 2403.01444v4 [cs.CV], 11 juin 2024. Venue non indiquée dans le texte (`doc:f99b745/tier:standard/page:1`). Affiliation : Zhejiang University. Lien : [arXiv 2403.01444](https://arxiv.org/abs/2403.01444). Page projet : sjojok.github.io/3dgstream.
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Pour des **vidéos free-viewpoint (FVV) de scènes dynamiques** captées par un réseau de caméras, 3DGStream entraîne un 3DGS sur la frame 0, puis, pour chaque frame suivante, n'apprend qu'un **petit cache de transformation neuronal (NTC : hash multi-résolution + MLP)** qui déplace et fait tourner les Gaussiennes existantes, plus quelques **Gaussiennes additionnelles propres à la frame** pour les objets qui apparaissent. Résultat : **≈ 12 s d'entraînement et ≈ 7,8 MB par frame**, rendu **≈ 215 fps** sur RTX 3090 (`page:1`, `page:6`, `page:10`). **« Streaming » signifie ici entraînement en ligne frame par frame, pas transmission réseau mesurée.**

## Problème traité
- Les méthodes NeRF de FVV exigent en général **la séquence complète pour un entraînement hors ligne** (elles rejouent mais ne diffusent pas) et **ne rendent pas en temps réel** (`page:1`).
- Réentraîner un 3DGS par frame est trop coûteux en temps et en stockage ; StreamRF (en ligne) rend lentement (8,3 fps) (`page:3`, `page:6`).

## Méthode / contributions
- **Frame 0** : 3DGS classique (densification arrêtée à 5 000 itérations ; modèle de l'itération 15 000 sur N3DV, 10 000 sur Meet Room ; SH de degré 1) (`page:9`).
- **Étape 1 : NTC** (`page:4–5`) : hash multi-résolution à la I-NGP (table 2¹⁵ entrées sur N3DV, 2¹⁴ sur Meet Room, 16 niveaux, 4 features) + MLP fully-fused (2 couches cachées de 64). Entrée : la **position** μ de chaque Gaussienne ; sortie : **translation dμ et rotation dq** (7 valeurs). Les SH sont tournés en conséquence. Les Gaussiennes de la frame précédente sont **gelées** ; seul le NTC est optimisé (perte L1 + D-SSIM, λ = 0,2), **150 itérations**. Initialisation par un « warm-up » unique de 3 000 itérations (≈ 20 s) vers la transformation identité.
- **Étape 2 : ajout adaptatif** (`page:5–6`) : on détecte les Gaussiennes à fort gradient de position en espace image (seuil τ_grad = 0,00015). On génère autour d'elles de nouvelles Gaussiennes (position ~ N(μ, 2Σ), SH et échelle héritées, opacité 0,1), optimisées **100 itérations**, puis élaguées si opacité < 0,01. Elles ne servent **qu'à la frame courante** (pas d'accumulation).
- Seules les Gaussiennes transformées passent à la frame suivante. Le stockage par frame = **NTC + Gaussiennes additionnelles** (`page:4`).
- Nombres (`page:10`) : ≈ **10⁵ Gaussiennes** initiales (transformées), ≈ **10²** additionnelles par frame (477,7 en moyenne sur flame salmon, Tab. 3, `page:7`).

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| FPS de rendu | **215 fps** en moyenne (N3DV) ; **288 fps** (Meet Room). Contre 390 et 571 fps pour 3DGS sans NTC | **RTX 3090**, SIBR, **mono**. N3DV à 1352×1014 (2704×2028 sous-échantillonné ×2), Meet Room à 1280×720 (`page:6`, `page:9–10`) |
| Décomposition du temps de frame | 2,56 ms (rendu) + 0,62 ms (requête NTC) + 0,02 ms (transformation) + **1,46 ms (rotation SH)** = **4,66 ms** (flame salmon, scène la plus lourde). Meet Room : 1,75 + 0,46 + 0,02 + 1,24 = 3,47 ms | Tab. 4 et 7 (`page:8`, `page:10`). Remarque : le texte donne aussi 215 fps comme **moyenne** N3DV (Tab. 1), alors que Tab. 4 l'attribue à la scène la plus lourde (incohérence mineure) |
| Qualité (PSNR) | **31,67 dB** (N3DV) contre 32,08 (3DGS réentraîné par frame), 30,68 (StreamRF), 31,10 (HyperReel) ; Meet Room : **30,79** contre 31,31 (3DGS) et 26,72 (StreamRF). SSIM et LPIPS **non rapportés** | Moyenne sur 300 frames (`page:6`, Tab. 5 `page:9`) |
| Entraînement par frame | **0,20 min ≈ 12 s** (N3DV) ; **0,10 min ≈ 6 s** (Meet Room). 3DGS réentraîné : 8,3 min et 2,6 min. +100 itérations d'étape 1 = +3 s | Moyenne 300 frames, RTX 3090 (`page:6`, `page:10`) |
| Taille par frame | **7 830,6 KB** (N3DV : NTC 7 781,5 KB + nouvelles Gaussiennes 49,1 KB) ; **4 136,8 KB** (Meet Room : 3 941,5 + 195,3). Avec le modèle initial amorti : 7,8 et 4,1 MB | Tab. 1, 2, 8 (`page:6`, `page:10`) |
| Débit équivalent | **≈ 235 MB/s ≈ 1,9 Gbit/s** (N3DV) et ≈ 124 MB/s ≈ 1 Gbit/s (Meet Room) à 30 fps de vidéo | **Calcul de la fiche** (taille par frame × 30 fps), aucun débit ni réseau n'est mesuré dans le papier |
| Latence | **Non rapportée**. Le délai capture → frame visible est au minimum le temps d'entraînement (≈ 6–12 s par frame) | — |
| Mémoire GPU | Non rapportée | — |

## Pertinence pour notre sujet
**Pertinence limitée si notre sujet reste statique** (question ouverte n°3 de [options.md](../../synthese/options.md)) : 3DGStream résout un problème différent (vidéo volumétrique dynamique captée par 13 à 21 caméras) et ses fps sont ceux d'un rendu 3DGS mono sur GPU desktop.

| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Référence des FVV 3DGS « streamables » ; classement utile des méthodes dynamiques (prior, flot, warp, spatio-temporel, par frame) (`page:3`) |
| 2. Gaussiennes depuis SfM, covariance | Hérite de 3DGS ; dépend fortement du nuage COLMAP initial (artefacts au-delà des fenêtres, `page:8`) |
| 3. Rendu rapide, casque | Surcoût de rendu de ≈ 2 ms par frame sur 3090 (NTC + rotation SH). Aucune stéréo, aucun casque |
| 4. Évaluation | Datasets N3DV et Meet Room ; métriques temps d'entraînement et stockage par frame |

## Pour (vis-à-vis de notre problématique)
- Montre qu'on peut **mettre à jour une scène 3DGS par transformations rigides locales** (translation + rotation par Gaussienne) sans réentraîner les attributs : piste pour les **parties mobiles d'un jumeau numérique** (P5).
- Le **surcoût de rendu est faible** (≈ 2 ms) et **la rotation SH en est la plus grande part** alors qu'elle a « un impact minimal » sur la qualité (`page:8`) : pour un rendu XR, on pourrait la supprimer.
- Le **delta par frame** (NTC + quelques centaines de Gaussiennes) plutôt que le modèle entier : idée proche de P4 (transmettre des mises à jour de splats plutôt que des pixels).

## Contre / limites
- **Pas de réseau** : « streaming » = entraînement en ligne ; aucun débit, aucune latence, aucun client distant.
- **Débit implicite très élevé** (≈ 1 à 1,9 Gbit/s à 30 fps, calcul de la fiche) : bien au-dessus d'une vidéo compressée, donc **contre-argument pour P4** appliqué au dynamique.
- **Pas temps réel côté capture** : 6 à 12 s d'entraînement par frame sur 3090, soit 180 à 360 fois plus lent que 30 fps.
- Capture multi-caméras (13 à 21 caméras calibrées), scènes intérieures d'un seul lieu ; mouvements brusques et objets complexes mal gérés à cause du nombre limité d'itérations (`page:8`).
- Mono, GPU desktop, pas de casque ; ≈ 10⁵ Gaussiennes seulement (scènes petites).
- Qualité mesurée en PSNR seulement.

## Idées à creuser pour une approche novatrice
- *Hypothèse (P5)* : pour un jumeau numérique, remplacer le NTC **appris** par des transformations **données** (poses OPC-UA des pièces articulées appliquées aux Gaussiennes segmentées) : même mécanisme de rendu que 3DGStream, sans entraînement, avec quelques octets par pièce et par frame au lieu de 7,8 MB.
- *Hypothèse (P2/XR)* : supprimer la rotation SH (1,24–1,46 ms, soit ≈ 31 à 36 % du temps de frame) ou l'appliquer une seule fois pour les deux yeux ; à vérifier sur la stabilité de la couleur en stéréo.
- *Hypothèse (P4)* : si le dynamique entre dans le sujet, mesurer le débit réel de 3DGStream après quantification du NTC (hash table en fp16/int8) et le comparer à une vidéo H.265 stéréo de même qualité, sur une trace réseau réelle.

## Citations clés
> « Our method achieves fast on-the-fly per-frame reconstruction within 12 seconds and real-time rendering at 200 FPS. » (`doc:f99b745/tier:standard/page:1`)

> « Note that we only need to train and store the parameters of the NTC and the additional 3DGs for each subsequent timestep, not all the 3DGs. » (`doc:f99b745/tier:standard/page:4`)

> « our experiments indicate that the SH rotation has a minimal impact on the reconstruction quality » (`doc:f99b745/tier:standard/page:8`)

> « for efficient on-the-fly training, we limit the number of training iterations, which restricts modeling of drastic motion in Stage 1 and complex emerging objects in Stage 2. » (`doc:f99b745/tier:standard/page:8`)

## Liens
- Papiers liés :
  - [Kerbl 2023, 3DGS](../kerbl2023_3dgs/fiche.md) : base du code et de la frame 0.
  - [Cao 2025, RT-FVHP](../cao2025_rt-fvhp/A_RECUPERER.md) : autre référence dynamique du sujet (pas de PDF, pas encore de fiche).
  - [Shi 2024, LapisGS](../shi2024_lapisgs/fiche.md) et [Zhu 2025, Nebula](../zhu2025_nebula/fiche.md) : streaming de Gaussiennes pour scènes **statiques**, avec réseau (Nebula) ou couches (LapisGS).
  - [Jiang 2024, VR-GS](../jiang2024_vr-gs/fiche.md) : déformation de Gaussiennes pilotée par la physique en VR, alternative à un NTC appris pour P5.
  - [Warsinke 2026](../warsinke2026_gs-mesh-dt-vr/fiche.md) : jumeau numérique 3DGS statique, cadre de P5.
  - [Liu 2025, GSMR](../liu2025_robotic-mr-gs-crosslayer/fiche.md) : constate que le GS statique échoue en scène dynamique et corrige par envoi d'images réelles plutôt que par mise à jour des Gaussiennes.
