---
citekey: wan2025_edge-collab-gs
mineru_doc: 78d5358
type: conférence   # papier court 4+1 pages (format type ICASSP, « Index Terms ») ; venue non indiquée ; arXiv 2510.22718v2 [cs.IT]
statut: fiche complète
tags: [3dgs, edge-computing, rendu-collaboratif, rendu-distant, optimisation-cross-layer, minlp, majorization-minimization, imitation-learning, allocation-de-puissance, massive-mimo, qos-qoe, simulation]
---

# Edge Collaborative Gaussian Splatting with Integrated Rendering and Communication

**Référence :** Yujie Wan, Chenxuan Liu, Shuai Wang, Tong Zhang, James Jianqiao Yu, Kejiang Ye, Dusit Niyato, Chengzhong Xu (2025). *Edge Collaborative Gaussian Splatting with Integrated Rendering and Communication.* arXiv 2510.22718v2 [cs.IT], 29 janv. 2026. Venue non indiquée dans le texte (`doc:78d5358/tier:standard/page:1`). Affiliations : SUSTech, SIAT-CAS, HIT Shenzhen, NTU, Univ. Macau. Lien : [arXiv 2510.22718](https://arxiv.org/abs/2510.22718). Code : non mentionné.
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
ECO-GS : chaque utilisateur rend localement un **petit modèle GS** (compressé, rapide) et peut basculer, image par image, vers un **grand modèle GS rendu sur un serveur edge** dont l'**image** lui est renvoyée par liaison descendante. Un problème d'optimisation mixte binaire/continu (IRAC) choisit **quels utilisateurs collaborent** (x_k ∈ {0,1}) et **la puissance d'émission** allouée à chacun (p_k). Il minimise une borne supérieure de l'erreur de rendu (« GS switching function ») sous contraintes de délai, de puissance et de capacité serveur. Le problème est résolu par pénalité + majorization-minimization (PMM), puis imité par un petit DNN (ILO) en < 1 ms (`page:1–4`). **Réseau entièrement simulé.**

## Problème traité
- Sur appareil bas coût, la quantification ou le pruning dégradent la qualité GS. Le rendu à l'edge améliore la fidélité, mais ajoute un délai de communication qui rend le rendu « non fluide » (`page:1`).
- Deux difficultés (`page:1`) :
  1. la collaboration n'est utile qu'aux **« pain points »**, c'est-à-dire les poses où le petit modèle s'écarte beaucoup de la réalité ;
  2. les schémas edge existants ignorent l'hétérogénéité des écarts GS et le couplage entre exigences de rendu et ressources radio.

## Méthode / contributions
- **Système** (Fig. 1, `page:2`) : serveur edge à **N antennes**, **K utilisateurs** mono-antenne (N ≫ K). Chaque utilisateur envoie sa pose 6D s_k. Sortie (éq. 1) : v_k = (1 − x_k)·Φ_k(s_k) + x_k·Φ_edge(s_k).
- **Canal** : liaison descendante avec beamforming MRC (asymptotiquement optimal pour N ≫ K). Débit de Shannon R_k = B_k·log₂(1 + ‖h_k‖²p_k/σ_k²), interférences inter-utilisateurs négligées (N → ∞) (`page:2`).
- **Problème IRAC P** (éq. 3, `page:2`) :

| Élément | Contenu |
|---|---|
| Variables | x ∈ {0,1}^K (collaboration), p ∈ ℝ₊^K (puissance d'émission edge) |
| Objectif | min Σ_k L(v_k, v̂_k), avec L = (1−λ)‖·‖₁ + λ(1 − SSIM) (perte de 3DGS) par rapport à l'image **vérité terrain** |
| C1 : délai (QoS) | B_k·log₂(1 + ‖h_k‖²p_k/σ²) ≥ x_k·V_k/(T − T₀) : le rendu edge T₀ plus le téléchargement de V_k bits doivent tenir dans T |
| C2 : puissance (ressource) | Σ p_k ≤ P |
| C3 : calcul serveur (ressource) | Σ x_k ≤ S |
| Domaine | p_k ≥ 0, x_k binaire, donc **MINLP non convexe** |

- **Fonction de substitution** (éq. 4–5, `page:2`) : la vérité terrain n'est pas disponible en ligne. Par inégalité triangulaire, on majore l'objectif par const + Σ(1 − x_k)·L(Φ_edge(s_k), Φ_k(s_k)). Cette **« GS switching function »** mesure l'écart entre grand et petit modèle à la pose demandée. Elle se calcule **en déployant tous les modèles sur le serveur**.
- **PMM** (`page:2–3`) : relaxation x_k ∈ [0,1] plus pénalité φ(x) = (1/β)Σx_k(1 − x_k), équivalente à P1 pour un β adéquat [21]. Majoration convexe φ̂ (éq. 8, Prop. 1). Chaque sous-problème convexe est résolu par **Mosek**. Chaque point limite est un point critique. Complexité **O(M(2K)^3,5)**.
- **ILO** (`page:3`, Fig. 2) : 10 000 échantillons générés par PMM (5 000 train / 5 000 test). Entrées : L_k et h_k (B_k, V_k, σ², T, P, S optionnels). DNN à 3 couches FC (100, 72, 20), ReLU, Focal Loss, AdamW, 200 epochs, lr 6×10⁻⁴, batch 96. En ligne, l'edge estime les conditions à chaque pas de temps (poses et pilotes) et infère (x, p) (`page:3–4`).

## Architecture casque/serveur (question spécifique)
| Aspect | ECO-GS |
|---|---|
| Ce qui transite | **Montant** : poses 6D. **Descendant** : **images RGB rendues** (pixels, V_k bits par image) pour les seuls utilisateurs x_k = 1. **Aucune Gaussienne transmise** en ligne : les deux modèles sont pré-déployés |
| Débit / bande passante | B_k = **2 MHz** par utilisateur. Débit de Shannon selon la puissance (P = 10–40 mW au total). **Volume V_k, résolution et codec non rapportés** |
| Latence | Budget bout-en-bout **T = 60 ms**. Rendu edge T₀ = **6,5 ms** (grand modèle, A6000). Rendu local **16,7 ms** (petit modèle, « desktop computer »). Fig. 6 (P = 10 mW, lecture) : utilisateurs PMM à ~17 ms (local) ou ~60 ms (edge) ; EdgeGS (tous à l'edge) de ~60 à **> 80 ms** (`page:3–4`) |
| Réseau réel ou simulé | **Simulé** : N = 600 antennes, (K, S) = (20, 10), utilisateurs aléatoires dans 100 × 100 m², canal h_k ~ CN(0, d_k^−α·I), α = 3, σ² = −70 dBm. Moyenne sur 100 tirages indépendants, **sans corrélation temporelle** (`page:3`) |
| Matériel client / serveur | Serveur : station Linux AMD 3,7 GHz + **NVIDIA A6000**. « Client » : temps mesuré sur un **ordinateur de bureau**, **pas sur mobile ni casque** (`page:3`) |
| Qualité par niveau | 2 niveaux seulement (Tab. 1, `page:3`) : grand modèle PSNR 27,49 / SSIM 0,98, contre 24,99 / 0,97 pour le petit |
| Adaptation au débit (ABR) | Non au sens vidéo : pas de choix de débit ni de compression. L'adaptation est **binaire** (local/edge), par utilisateur et par pas de temps, selon le canal et l'écart de modèle |
| Modèle d'optimisation formel | **Oui** : MINLP (voir ci-dessus), résolu par PMM + Mosek ou DNN imitateur |

### Comparaison avec l'éq. 1 de Kamdjou
[Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) propose max P = f(QoS)·W_QoS + g(QoE)·W_QoE + h(Res)·W_Res, avec seuils Target_QoS, Target_QoE et Max_power, mais **sans instanciation ni solveur**. ECO-GS en est une **instanciation concrète, sous forme ε-contrainte plutôt que somme pondérée** (analyse de la fiche) :

| Kamdjou (éq. 1) | ECO-GS (éq. 3/5) |
|---|---|
| g(QoE) maximisée | Objectif unique : erreur image L1 + D-SSIM par rapport à la VT, approximée par l'écart grand/petit modèle. Qualité **objective** pixel, pas de QoE subjective |
| QoS ≥ Target_QoS | Délai T₀ + V_k/R_k ≤ T = 60 ms (contrainte dure) |
| Res ≤ Max_power | Σp_k ≤ P (puissance **radio de l'edge**) et Σx_k ≤ S (capacité GPU serveur) |
| Poids W, NP-difficile, non résolu | Pas de poids ; MINLP résolu (point critique) ; inférence temps réel < 1 ms |
| — | **Absents** : ressources du **client** (GPU, énergie, batterie), fps, choix continu de LOD/compression/fovéa, dynamique temporelle |

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| FPS | Non rapporté en fps. Rendu local 16,7 ms/image (≈ 60 fps, calcul de la fiche) sur PC de bureau ; rendu edge 6,5 ms sur A6000. **Mono, pas de stéréo** | Truck (T&T), résolution non indiquée (`page:3`) |
| Qualité des modèles | Grand Φ_edge : **PSNR 27,49**, SSIM 0,98, L1 0,031. Petit Φ_k : **24,99**, 0,97, 0,043 | Tab. 1 (`page:3`) |
| Qualité du système | PMM : **≥ +1,3 dB** PSNR et **≥ −15 %** de perte par rapport à UserGS (tout local). Lecture Fig. 3b : PMM ~26,3 dB (10 mW) à ~26,9 dB (40 mW), UserGS ~25,0 ; Greedy et Search proches, Rounding ~25,9–26,1, MaxRate ~25,5–26,1 | K = 20, S = 10 (`page:4`) |
| Taille du modèle | 509,8 M contre 9,3 M (unité non précisée), soit « over 50× ». Dimension par Gaussienne : 64 contre 14 | Tab. 1. Le rapport 54,8× dépasse le rapport de dimension (4,6×) : le nombre de Gaussiennes est donc aussi réduit (déduction de la fiche, non décrit) |
| Latence bout-en-bout | PMM **≤ 60 ms garanti** ; EdgeGS **> 80 ms** pour certains utilisateurs | Fig. 6, P = 10 mW (`page:4`) |
| Temps de décision | PMM **16 ms (K = 20) à 58 ms (K = 80)** ; ILO **0,1–0,2 ms**. Texte : « 100× » plus rapide, « within 1 ms » | Lecture Fig. 7d (`page:4`) |
| Fidélité de l'ILO | Précision 0,9, perte 0,0175 ; −0,02 dB PSNR par rapport à PMM | Fig. 7 (`page:4`) |
| Entraînement GS | Non rapporté | — |
| Énergie client | Non rapportée | — |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Références edge/GS utiles : Voyager [2] (3DGS à l'échelle d'une ville sur téléphone), Multi-tier CloudVR [4], Liu et al. [6] (MR robotique GS, optimisation cross-layer), [Qiu 2024](../qiu2024_3dgs-xr-survey/fiche.md) [8] |
| 2. Gaussiennes depuis SfM, covariance | Nul (3DGS standard, petit modèle « compressé » non décrit) |
| 3. Rendu rapide, visibilité, casque | Architecture hybride local/edge au niveau **image entière** ; rien sur la visibilité, la stéréo ou le casque |
| 4. Évaluation | Grandeurs réseau (puissance, débit, délai) et qualité PSNR ; pas de fps casque, pas de motion-to-photon |

## Pour (vis-à-vis de notre problématique)
- **Première instanciation formelle** (dans notre base) d'un compromis qualité / délai / ressources pour la 3DGS edge, avec un **solveur temps réel** (< 1 ms). C'est le modèle concret qui manque à l'éq. 1 de Kamdjou (P3).
- L'idée de la **« GS switching function »** est transposable : quantifier l'écart entre deux LOD **sans vérité terrain** pour décider où investir les ressources.
- Montre que **tout déporter à l'edge (EdgeGS) dépasse le budget de latence** (> 80 ms) et qu'il faut choisir sélectivement : argument pour un partage hybride.
- Architecture « petit modèle local + grand modèle distant » : cadre proche de notre P1 reformulée.

## Contre / limites
- **Tout est simulé côté réseau** (canal gaussien, massive MIMO, 100 tirages indépendants). Aucun réseau réel, aucune trace, aucune corrélation temporelle entre pas de temps.
- **Latences incompatibles avec la XR** : un budget de 60 ms est loin des < 20 ms de Kamdjou et des exigences de la VR. L'image edge correspond à une pose **périmée** de 60 ms, sans reprojection ni ATW.
- Client = **PC de bureau**, pas de mobile ni de casque. Pas de stéréo, pas de fps. Résolution et taille d'image V_k non indiquées ; un seul dataset (Truck).
- **Coût caché de l'objectif** (analyse de la fiche, non discuté par les auteurs) : évaluer L(Φ_edge(s_k), Φ_k(s_k)) suppose de **rendre les deux modèles sur le serveur pour les K poses** à chaque pas. La contrainte de capacité Σx_k ≤ S devient alors peu significative, car le serveur rend déjà tout.
- Décision **binaire par image entière** : pas de partage spatial (fovéa/périphérie, près/loin), pas de composition, pas de choix continu de LOD.
- Qualité mesurée en PSNR et perte uniquement, **pas de LPIPS** ni d'étude perceptive.
- Le « 100× » d'ILO est approximatif : environ 160× à 290× d'après la Fig. 7d.

## Idées à creuser pour une approche novatrice
- *Hypothèse (P3)* : **étendre IRAC au casque**. Variables = {nombre de couches LapisGS ou τ* Nebula, compression, rayon fovéal, local/edge par région} ; objectif = GS switching function (pas de VT) ; contraintes = motion-to-photon ≤ 20 ms, fps ≥ 72/90 stéréo, budget GPU/énergie du casque, débit mesuré. Solveur rapide par imitation (ILO) pour la décision par frame. On instancierait ainsi l'éq. 1 de Kamdjou côté casque, là où ECO-GS reste côté radio.
- *Hypothèse (P1 reformulée)* : remplacer la bascule **binaire par image** par une bascule **par région** : fovéa = Gaussiennes locales (latence nulle), périphérie = pixels edge en basse résolution (latence tolérable, grand modèle), puis composition par profondeur. La GS switching function **par tuile** indiquerait où l'edge apporte le plus.
- *Hypothèse* : **GS switching function prédite** par un petit réseau à partir de la pose et de statistiques de splats, pour éviter le double rendu serveur. À comparer au vrai calcul.
- *Hypothèse (P4)* : évaluer sur **traces réseau réelles** (Wi-Fi 6 / 5G) avec corrélation temporelle, point laissé ouvert par ECO-GS comme par Nebula.

## Citations clés
> « each user can switch between a local small GS model to guarantee timeliness and a remote large GS model to guarantee fidelity » (`doc:78d5358/tier:standard/page:1`)

> « This function no longer involves ground truth images, and can be computed using GS models Φ_edge and {Φ_k}. Consequently, we can deploy all GS models at the server to evaluate the GS switching cost. » (`doc:78d5358/tier:standard/page:2`)

> « EdgeGS leads to over 80 ms latency, while our method strictly guarantees less than 60 ms for smooth rendering. » (`doc:78d5358/tier:standard/page:4`)

> « The computation time of ILO-IRAC is within 1 ms, making it suitable for real-time execution. » (`doc:78d5358/tier:standard/page:4`)

## Liens
- Papiers liés :
  - [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) : éq. 1 QoS/QoE/ressources, dont ECO-GS est une instanciation ε-contrainte côté radio ; grille de latence edge (< 10–12 ms aux niveaux 1–2), bien en deçà des 60 ms d'ECO-GS.
  - [Zhu 2025, Nebula](../zhu2025_nebula/fiche.md) : collaboration cloud/casque qui envoie des **Gaussiennes** (Δcut) et non des pixels, et rejette le partage au niveau pixel. Choix inverse de celui d'ECO-GS.
  - [Shi 2024, LapisGS](../shi2024_lapisgs/fiche.md) : fournirait des niveaux de qualité continus (couches) à la place des 2 modèles d'ECO-GS.
  - [Fan 2023, LightGaussian](../fan2023_lightgaussian/fiche.md), [Lee 2023, Compact3D](../lee2023_compact3d/fiche.md) : candidats pour le « petit modèle » local (compression non décrite ici).
  - [Oh 2025, NEO](../oh2025_neo-on-device/fiche.md), [Du 2026, Mobile-GS](../du2026_mobile-gs/fiche.md) : rendu 3DGS sur appareil, c'est-à-dire la partie « local » réaliste qu'ECO-GS mesure sur PC de bureau.
  - [Qiu 2024, 3DGS XR survey](../qiu2024_3dgs-xr-survey/fiche.md) : cité [8].
  - [Kerbl 2023, 3DGS](../kerbl2023_3dgs/fiche.md) : implémentation de base et perte L1 + D-SSIM reprise comme objectif.
