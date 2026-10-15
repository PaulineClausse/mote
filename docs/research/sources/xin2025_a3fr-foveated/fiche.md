---
citekey: xin2025_a3fr-foveated
mineru_doc: a2b354b
type: conférence   # ICS '25 (International Conference on Supercomputing), ACM
statut: fiche complète
tags: [3dgs, vr, rendu-fovéal, eye-tracking, vit, early-exit, rendu-incrémental, cpu-gpu, jetson-orin-nx, tesla-t4, latence, étude-utilisateurs, meta-quest-pro, mono]
---

# A3FR: Agile 3D Gaussian Splatting with Incremental Gaze Tracked Foveated Rendering in Virtual Reality

**Référence :** Shuo Xin, Haiyu Wang, Sai Qian Zhang (2025). *A3FR: Agile 3D Gaussian Splatting with Incremental Gaze Tracked Foveated Rendering in Virtual Reality.* In **ICS '25**, 2025 International Conference on Supercomputing, 8–11 juin 2025, Salt Lake City, ACM, 14 p. DOI [10.1145/3721145.3735112](https://doi.org/10.1145/3721145.3735112) · [arXiv 2507.04147](https://arxiv.org/abs/2507.04147) (`doc:a2b354b/tier:standard/page:1/block:14`). NYU Tandon. Code : non mentionné.
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Pour que le rendu fovéal piloté par le regard (TFR) rapporte vraiment en latence avec la 3DGS, A3FR exécute **en parallèle** le suivi du regard (ViT à sorties précoces, sur **CPU**) et le rendu 3DGS fovéal (sur **GPU**). Le GPU rend d'abord la périphérie, puis **raffine incrémentalement** la fovéa à mesure que les prédictions de regard se précisent, en ne sous-échantillonnant que les pixels (blocs 2×2). Résultat : jusqu'à **2×** de latence en moins que le rendu pleine résolution, sans perte perçue (étude à 8 participants) (`page:1/block:8`, `page:9`, `page:12`).

## Problème traité
- Le TFR réduit le coût de rendu, mais le **suivi du regard (DNN) ajoute de la latence**, qui peut dépasser le gain de rendu. En séquentiel sur le même GPU, on a T_tot = T_s + T_c + T_d + T_r (`page:1/block:8`, `page:4`).
- Mesures sur **Jetson Orin NX** (Table 1, `page:4`) : ViT de regard à 6 couches = **11,43 ms sur GPU**, **30,93 ms sur CPU** (3 couches : 16,44 ms). 3DGS sur le GPU Orin NX = **27,00 ms (720p), 37,78 ms (1080p), 53,14 ms (1440p)**. Exécuter l'eye-tracking en concurrence sur le GPU ajoute **~12 ms**.
- L'erreur de regard élargit la zone fovéale (marge c, éq. 1, θ_i = 18° d'après MetaSapiens), ce qui réduit l'économie (`page:3`). Budget cible de latence système : **20–50 ms** (`page:3`).

## Méthode / contributions
- **Parallélisation CPU/GPU dans le casque** : regard sur CPU, rendu sur GPU, d'où T_tot = T_s + T_c + max(T_d, T_r). Capteur ~1 ms, MIPI < 1 ms (`page:4–5`).
- **A3FR-ViT** : 6 blocs transformer, 6 têtes, dim 384, sortie de régression 2D du regard. Une **sortie précoce** (couche linéaire) après chaque bloc. Entraînement « multi-résolution » : somme pondérée des pertes L2 de toutes les sorties (éq. 2), avec une perte « max par batch ». **Élagage de tokens** par score d'attention (10 % / 20 %) (`page:5`, `page:8`).
- **Rendu incrémental** (`page:5–6`, Fig. 7–8) :
  - le round 1 lance le préprocessing (projection, tri) et rend la **périphérie** sans attendre le regard ;
  - chaque prédiction u_i arrivée étend le **disque haute résolution**, de rayon r_f,i = max(0, r_f,N − E[dist(u_i, u_N)]) (éq. 4). E[·] est calibré hors ligne sur l'erreur OpenEDS2020, de sorte que la zone déjà rendue soit contenue dans la fovéa finale : **pas de travail gaspillé** ;
  - seul l'**anneau incrémental** est rendu au round suivant.
- **Rendu incrémental spéculatif (SIR)** : GPU et CPU sont asynchrones, le dernier regard est lu en mémoire GPU. Si aucune nouvelle prédiction n'arrive, le GPU continue autour de u_j jusqu'à r_j^max = r_f,N + E[dist] (éq. 5) (`page:6–7`).
- **AMR (adaptive mesh refinement)** : tuiles **32×32**, sous-divisées en 16×16 blocs de **2×2 pixels**. 4 niveaux (1 à 4 pixels rendus sur 4) selon l'excentricité. Les pixels non rendus sont hérités ou interpolés. En CUDA, cela donne 4 cooperative groups de 256 threads par tuile, et les groupes inutiles sortent immédiatement (`page:7`, Fig. 9). Les variables intermédiaires (projection, listes par tuile, tri) sont **mises en tampon au round 1** et réutilisées par les rounds suivants (`page:7`).
- **Point clé pour nous** : la fovéation porte **sur les pixels, pas sur les Gaussiennes**. Préprocessing et tri restent **entiers**. Le préprocessing pèse **8,48 ms sur 22,7 ms** dans la décomposition truck 1080p (lecture Fig. 12a, `page:11`).

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| Matériel | **Tesla T4** 16 Go (1590 MHz, 2560 cœurs) + Xeon 8259CL (4c/8t, 2,5 GHz). Mode « Orin NX » : **T4 bridé à 915 MHz et 1024 cœurs**, CPU à 2,2 GHz, pour **émuler** un Jetson Orin NX 16 Go. **Pas de casque réel pour le rendu** | `page:8` |
| Latence, **T4 standard, 1080p** (FRR / SFR / A3FR) | truck 38/28/**23** ms · train 31/26/**21** · drjohnson 39/28/**23** · playroom 29/22/**17** | Lecture Fig. 11a, **mono** (1 image), moyenne sur 100 poses (`page:9–10`) |
| Latence, **T4 standard, 720p / 1440p** (A3FR) | 720p : 20 / 18 / 19 / 13 ms · 1440p : 30 / 27 / 29 / 22 ms (FRR 1440p : 53 / 44 / 55 / 42) | Lecture Fig. 11a |
| Latence, **émulation Orin NX, 1080p** (FRR / SFR / A3FR) | truck 114/69/**55** ms · train 89/59/**47** · drjohnson 116/67/**51** · playroom 87/51/**38**. Soit **~18–26 FPS mono**, sous le seuil de 30 FPS | Lecture Fig. 11b |
| Latence, **émulation Orin NX, 720p / 1440p** (A3FR) | 720p : 42 / 36 / 38 / 27 ms · 1440p : 73 / 64 / 70 / 53 ms | Lecture Fig. 11b |
| Réglage « 16 TOPS » | playroom 720p : FRR 151,239 ms · SFR 104,328 ms · A3FR **76,757 ms** | `page:9` |
| Gains moyens | 1080p/1440p : **−20 %** par rapport à SFR, **−40 %** par rapport à FRR. 720p : −30 %. Abstract : « up to 2× » | `page:9/block:10`, `page:1` |
| Décomposition (truck 1080p) | GPU : préprocessing 8,48 + R1 6,54 + R2 2,49 + R3 3,19 + R4 0,56 = **22,7 ms**. CPU : embedding + L1…L5 (4,00 / 4,26 / 4,51 / 4,48 / 3,95) = 22,1 ms | Lecture Fig. 12a (`page:11`) |
| SIR sous charge CPU fluctuante | **26,0 ms** (CPU alterné entre 50 % et 100 % toutes les 0,1 s). La valeur sans SIR n'est pas chiffrée dans le texte | truck 1080p (`page:10`) |
| AMR | ~**10 %** de latence en moins à 1440p, effet marginal à 720p. Lecture Fig. 13b (Orin) : 1440p 74 contre 91 ms (truck) | `page:10`, `page:11` |
| Précision du regard (erreur σx, σy en degrés) et latence CPU Orin NX | A3FR-ViT : couche 1 (8,40 ; 9,33) → couche 6 (**2,05 ; 2,16**), cumul **26,28 ms**. Élagage 10 % : (2,53 ; 2,56), 24,23 ms. Élagage 20 % : (2,69 ; 2,39), **21,64 ms**. ResNet-34 : (2,24 ; 1,94), 37,30 ms. DeepVOG : (1,91 ; 2,03), **114,6 ms** | OpenEDS, images 640×400 (Table 2, `page:10`) |
| Qualité d'image | **Aucun PSNR/SSIM/LPIPS.** Étude 2IFC, **8 participants**, 20 paires par personne, **Meta Quest Pro**, images **statiques** avec **point de fixation imposé** (pas d'eye-tracking en boucle). A3FR choisi **49,4 % ± 8,2 %** du temps, donc indiscernable du rendu plein | `page:11–12` |
| Entraînement | 3DGS original, 30k itérations (T&T : truck, train ; DB : drjohnson, playroom). ViT : 25 époques sur OpenEDS | `page:8` |
| Mémoire | Non rapportée | — |
| Stéréo | **Non traitée** : toutes les latences sont pour une seule image (720p/1080p/1440p) | — |

*Incohérence du texte* : il attribue 26,28 ms à « 20 % pruned », alors que la Table 2 donne 26,28 ms sans élagage et 21,64 ms à 20 % (`page:9`).

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Chaîne TFR complète (caméra oculaire → ISP → MIPI → DNN → rendu) avec ordres de grandeur de latence. Budget de 20–50 ms. Jetson Orin NX comme proxy de casque (`page:3–4`) |
| 2. Gaussiennes depuis SfM, covariance | Rien (3DGS original) |
| 3. Rendu rapide, visibilité, casque | Rendu fovéal 3DGS **simple à implémenter** dans le rasteriseur CUDA d'origine (masque de threads par blocs 2×2, tuiles 32×32). Mise en tampon et réutilisation de projection et tri entre rounds. Ordonnancement CPU/GPU |
| 4. Évaluation | Protocole 2IFC utile, mais faible (8 sujets, images fixes). Absence de métriques d'image : **à ne pas reproduire** |

## Verdict P1 / P2 (et autres pistes)
- **P1 (edge/casque par visibilité)** : **non réalisée**. Tout reste **dans le casque** (répartition CPU/GPU, pas edge/casque). Le papier **éclaire** le volet « fovéa » : la fovéation par pixels ne fait pas baisser le coût préprocessing + tri (~37 % du temps GPU dans la décomposition). Un partage P1 doit donc porter sur les **Gaussiennes** (LOD par excentricité), pas seulement sur les pixels. Cela rejoint l'argument de [Nebula](../zhu2025_nebula/fiche.md) : le coût 3DGS suit le nombre de Gaussiennes.
- **P2 (mutualisation stéréo)** : **non abordée** (mono). Remarque utile : le buffering de projection et tri entre rounds est un mécanisme de réutilisation proche de ce que P2 demande entre les yeux.
- **P3** : éclairée à la marge. Le rayon fovéal dépend de l'**incertitude du regard** (éq. 1, 4, 5), une variable QoE naturelle pour un contrôleur de budget. **P4, P5** : non concernées.

## Pour (vis-à-vis de notre problématique)
- Vise la VR avec 3DGS et mesure en **1080p** sur un proxy de GPU embarqué (Orin NX) : proche de notre cible.
- Mécanismes **purement logiciels** sur GPU standard (CUDA), sans accélérateur : reproductibles.
- Montre qu'**aucun travail n'est gaspillé** grâce au rayon calibré sur l'erreur attendue, et que le système est robuste aux fluctuations CPU (SIR).
- Rappelle que la latence d'eye-tracking (21–30 ms sur CPU embarqué) est du même ordre que le rendu. Tout pipeline fovéal doit la cacher.

## Contre / limites
- **Pas de casque réel pour le rendu** : T4 serveur bridé pour « imiter » l'Orin NX. L'équivalence n'est que par fréquence et nombre de cœurs, sans tenir compte de la mémoire ni de la thermique.
- **Mono uniquement** : aucune mesure stéréo, alors qu'un casque exige 2 vues. En émulation Orin, la 1080p mono est déjà à 38–55 ms (18–26 FPS), donc **sous 30 FPS**, et la stéréo doublerait approximativement la charge (hypothèse).
- **Aucune métrique d'image** (PSNR/SSIM/LPIPS). La validation perceptuelle ne repose que sur 8 sujets, des **images fixes** et un regard imposé. Artefacts temporels, saccades et latence de regard en boucle réelle **non évalués**.
- La latence mesurée est celle **d'une frame TFR**, pas le motion-to-photon (pose de tête non prise en compte).
- La fovéation par sous-échantillonnage de pixels (hériter ou interpoler) **ne réduit ni le nombre de Gaussiennes, ni le préprocessing, ni le tri**. Le gain plafonne donc (AMR ≈ 10 % à 1440p).
- Scènes petites (4 scènes T&T/DB). Pas de comparaison avec d'autres rendus fovéaux 3DGS (VR-Splatting, MetaSapiens).

## Idées à creuser pour une approche novatrice
- *Hypothèse (P1)* : **fovéation au niveau des Gaussiennes** (LOD de la hiérarchie choisi selon l'excentricité, en plus du sous-échantillonnage de pixels) pour réduire aussi le préprocessing et le tri. La périphérie basse résolution pourrait être **déportée à l'edge**, la fovéa rendue localement.
- *Hypothèse (P2 + fovéal)* : A3FR met déjà projection et tri en tampon entre rounds. Étendre ce tampon **aux deux yeux** (tri partagé façon Nebula), puis faire le raffinement fovéal **par œil**, pour obtenir un pipeline stéréo fovéal incrémental évalué en stéréo réelle.
- *Hypothèse (P3)* : utiliser l'**incertitude de regard** (σ par sortie précoce) comme entrée d'un contrôleur de budget. Un rayon fovéal dynamique et un nombre de Gaussiennes ajusté pour tenir 30 à 72 FPS.
- *Hypothèse (évaluation)* : reprendre le protocole 2IFC, mais sur **séquences** en casque avec eye-tracking réel, et le compléter par des métriques fovéales (FovVideoVDP ou équivalent, à sourcer).

## Citations clés
> « Although gaze-tracked foveated rendering can reduce rendering costs, the computational overhead of the gaze tracking process itself can sometimes outweigh the rendering savings, leading to increased processing latency. » (`doc:a2b354b/tier:standard/page:1/block:8`)

> « At 1080p and 1440p resolutions, A3FR achieves an average speedup of 20% compared to SFR and 40% compared to FRR. » (`doc:a2b354b/tier:standard/page:9/block:10`)

> « Across all participants, the TFR within our A3FR framework was selected 49.4%±8.2% of the time compared to the baseline rendering method » (`doc:a2b354b/tier:standard/page:12`)

## Liens
- Papiers liés :
  - [Zhu 2025, Nebula](../zhu2025_nebula/fiche.md) : même constat (le coût 3DGS suit les Gaussiennes), collaboratif cloud/casque et stéréo partagée, mais sans fovéation.
  - [Franke 2024, VR-Splatting](../franke2024_vr-splatting/fiche.md) et [Tu 2025, VRSplat](../tu2025_vrsplat/fiche.md) : rendu fovéal 3DGS en VR (hybride neuronal / fovéal fixe), à comparer.
  - [Kerbl 2023, 3DGS](../kerbl2023_3dgs/fiche.md) : rasteriseur modifié.
  - [Kerbl 2024, Hierarchical 3DGS](../kerbl2024_hierarchical-3dgs/fiche.md) : LOD utilisable pour une fovéation au niveau des Gaussiennes.
  - [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) : seuils de latence XR.
  - [Li 2025, survey RF-XR](../li2025_rf-xr-survey/fiche.md), [Qiu 2024, survey 3DGS-XR](../qiu2024_3dgs-xr-survey/fiche.md) : contexte fovéal et XR.
