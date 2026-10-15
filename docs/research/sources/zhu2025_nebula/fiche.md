---
citekey: zhu2025_nebula
mineru_doc: f69941e
type: conférence   # préprint arXiv (cs.AR), venue non indiquée dans le texte ; papier d'architecture (co-design algo/matériel)
statut: fiche complète
tags: [3dgs, vr, rendu-collaboratif, cloud-client, streaming-de-gaussiennes, lod, hierarchical-3dgs, rasterisation-stéréo, accélérateur-matériel, gscore, jetson-orin, simulation-rtl, large-échelle, bande-passante, énergie]
---

# Nebula: Enable City-Scale 3D Gaussian Splatting in Virtual Reality via Collaborative Rendering and Accelerated Stereo Rasterization

**Référence :** He Zhu, Zheng Liu, Xingyang Li, Anbang Wu, Jieru Zhao, Fangxin Liu, Yiming Gan, Jingwen Leng, Yu Feng (2025). *Nebula: Enable City-Scale 3D Gaussian Splatting in Virtual Reality via Collaborative Rendering and Accelerated Stereo Rasterization.* Préprint arXiv 2512.20495v1 [cs.AR], 23 déc. 2025. Venue non indiquée (`doc:f69941e/tier:standard/page:1/block:1`). Shanghai Jiao Tong Univ., Shanghai Qi Zhi Institute, ICT-CAS. Lien : [arXiv 2512.20495](https://arxiv.org/abs/2512.20495). Code : non mentionné.
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Framework **cloud–client** (co-design algorithme/matériel) pour la 3DGS à l'échelle d'une ville en VR. Le cloud n'exécute que la **recherche de LoD** (la partie gourmande en mémoire), accélérée par la cohérence temporelle. Il envoie au casque le **delta de Gaussiennes** (Δcut, compressé), et non des pixels. Le client exécute préprocessing, tri et une **rasterisation stéréo** où l'œil droit réutilise le tri et les listes de l'œil gauche par triangulation (disparité = Bf/D), sur un accélérateur dérivé de GSCore. Résultats **simulés** : 70,1 FPS stéréo en 2064×2208 par œil, latence motion-to-photon 2,7× meilleure et bande passante ~19× plus faible (« 1925 % ») que le streaming vidéo H.265 (`page:1/block:11`, `page:11`).

## Problème traité
- **Mémoire** : les scènes 3DGS de grande échelle vont jusqu'à **66 Go** (HierGS), alors que les casques ont < 12 Go (`page:1`, `page:3`, Fig. 2).
- **Déplacement du goulot** : sur GPU mobile Ampere (Orin), la recherche de LoD atteint **jusqu'à 47 %** de la latence de bout en bout sur les grandes scènes. La rasterisation domine sur les petites (`page:4`, Fig. 3).
- **Streaming vidéo** : en VR (≥ 90 FPS, 2064×2208 par œil, Quest 3), le réseau domine la latence de bout en bout. Le rendu distant total fait **~50–85 ms** selon la scène (lecture Fig. 4, `page:3`). La vidéo 4K VR à 90 FPS demande > 1 Gbps en HEVC (`page:1`), et même en lossy la 1080p et au-delà dépasse le débit moyen des foyers US (Fig. 5, `page:4`).
- **Collaboratif existant inadapté** : les travaux antérieurs (Q-VR, EDC, CollabVR, Cicero…) partitionnent au niveau **pixel**. Or le coût 3DGS dépend du **nombre de Gaussiennes**, pas des pixels (`page:2`, `page:4`, `page:12`).

## Méthode / contributions

### Architecture : qui calcule quoi, et ce qui transite
| Côté | Tâche | Détail |
|---|---|---|
| **Cloud** (2× A100 80 Go, un par œil pour la baseline vidéo) | Recherche de LoD (arbre HierGS irrégulier) | Critère : taille projetée < τ* (en pixels) et parent > τ*. Le résultat est un « cut » de l'arbre (`page:3`) |
| Cloud | Table de gestion | Suit les Gaussiennes présentes sur le client. Fenêtre de réutilisation w_r, seuil w_r* = **32** frames, éviction façon ramasse-miettes (`page:7`) |
| **Réseau** | **Δcut** = seulement les Gaussiennes nouvellement entrées dans le cut | SH en **quantification vectorielle** (comme Compact3DGS), position et échelle en **virgule fixe 16 bits**. Les auteurs revendiquent « no contribution » sur la compression (`page:7`) |
| **Client** (casque) | Décompression, mise à jour du sous-graphe LoD local, file de rendu au bon LoD, puis **préprocessing + tri + rasterisation stéréo** | Le préprocessing reste sur le client **volontairement** : le client peut rendre n'importe quel viewport proche de la pose courante sans trafic, ce qui absorbe les rotations rapides de la tête (`page:5`) |
| Timing | LoD search 1 fois toutes les **w = 4** frames | La latence cloud est masquée par plusieurs frames locales. Le client n'attend pas les données cloud (« negligible quality sacrifice », non chiffré). **Seul le client est sur le chemin critique** (`page:6`, Fig. 10) |

Ce qui transite, ce sont donc des **Gaussiennes** (primitives 3D compressées), pas des pixels ni des images. Le découpage se fait **par étape du pipeline** (LoD search / reste), pas par visibilité, profondeur ou excentricité.

### Recherche de LoD temporelle (côté cloud, logicielle, GPU serveur standard)
- **1re frame** : parcours « fully-streaming » de l'arbre. On ajoute des liens en largeur, on découpe en blocs de nœuds tenant en mémoire partagée, avec dispatch dynamique aux warps. Cela évite les accès DRAM irréguliers (`page:6`, Fig. 11a).
- **Frames suivantes** : l'arbre est pré-partitionné hors ligne en sous-arbres de taille égale. On ne reparcourt que les sous-arbres contenant le cut précédent (un warp par sous-arbre), en remontant au top-tree si nécessaire. Le résultat est **bit-exact** par rapport au parcours complet (`page:7/block:3`).
- Base empirique : **99 %** des Gaussiennes du cut sont inchangées d'une frame à l'autre à 90 FPS, et encore **> 95 %** à 64 frames d'écart (HierGS, `page:4`, Fig. 7).

### Rasterisation stéréo (côté client) : ce qui est partagé entre les yeux
1. **Préprocessing + tri : partagés**. Une caméra virtuelle est placée légèrement derrière les deux yeux. On en dérive un FoV gauche **élargi** couvrant la zone commune, puis on fait **une seule** projection et **un seul** tri sur ce FoV (`page:8`, Fig. 13 gauche).
2. **Œil gauche** : rasterisation standard par tuiles **4×4**, avec α-check et blending.
3. Chaque Gaussienne qui **passe l'α-check** dans une tuile gauche est reprojetée par **triangulation**, avec la disparité X = B·f/D (D = profondeur de la Gaussienne). Elle est insérée dans l'une de **4 listes** (T_N→T_N … T_N→T_N+3), parce que la disparité maximale est bornée à **16 px** grâce au near plane (`page:7/block:16`, `page:8`).
4. **Œil droit** : la liste de chaque tuile est la **fusion (merge-sort) de 4 listes déjà triées**, avec dédoublonnage. Il n'y a **ni re-préprocessing ni re-tri**. Le blending se fait ensuite normalement (`page:8`).
- Revendication : rendu **« bit-accurate »**. Gain de **1,4×** sur GPU mobile, car l'œil droit ne traite que des Gaussiennes ayant déjà passé l'α-check (`page:7/block:13`, `page:8`). Les 3 premières tuiles de l'œil droit sont rendues indépendamment (`page:9`).
- Motivation : moins de 1 % de pixels non recouvrants entre les deux yeux après warping (Fig. 8, `page:5`). Le warping d'image (Warp, Cicero) est rejeté car la profondeur 3DGS n'est pas fiable et il casse la dépendance à la vue (`page:5`, `page:7`).

### Support matériel (papier d'architecture)
- Base **GSCore** (accélérateur 3DGS, ASPLOS'24). Le VRC est augmenté d'une **stereo re-projection unit (SRU)**, d'une **merge unit** et d'un **stereo buffer** de 16 Ko en line-buffer (une ligne par classe de disparité, buffers circulaires), plus un **décodeur** VQ avec buffer de codebook (`page:8–9`, Fig. 14–15).
- RTL à 1 GHz : 4 unités de projection, 4 de tri, **8 VRC × (4×4 RU) = 128 RU**, feature buffer de 16 Ko, global buffer de 144 Ko. Synthèse **TSMC 16 nm**, puis mise à l'échelle **8 nm** (DeepScaleTool) pour correspondre à l'Orin. DRAM LPDDR3-1600 modélisée (`page:9`).
- **Surcoût de surface : +14 % (0,25 mm²)** par rapport à GSCore (1,78 mm²) en 16 nm (`page:10/block:2`).

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| Résolution | **2064 × 2208 par œil**, stéréo, baseline 6 cm | Toutes les évaluations (`page:10/block:3`) |
| FPS | **70,1 FPS stéréo** en moyenne (Nebula) : **n'atteint pas 90 FPS**. Lecture Fig. 18 : ~60 (HierGS, Urban, T&T) à ~97 (DB). GPU Orin seul : quelques FPS (< 10, lecture) | Accélérateur simulé 128 RU (8 nm) ; rendu et communication supposés pipelinés (`page:11`) |
| FPS (mise à l'échelle) | **≥ 90 FPS avec 256 RU**, pour **+62,9 % de surface** (lecture Fig. 23 : ~100 FPS à 256 RU, ~130 à 512) | Moyenne des 3 grandes scènes (`page:12`) |
| Latence motion-to-photon | **12,1×** plus rapide que GPU Orin local, contre 4,6× pour le streaming vidéo « Remote ». Soit **2,7×** (abstract) ou 2,6× (contributions) par rapport à la vidéo lossy. **Aucune valeur absolue en ms n'est rapportée pour Nebula** | HierGS sur toutes les variantes (`page:11`, `page:1`) |
| Latence du streaming vidéo (baseline) | ~50–85 ms de bout en bout, dominée par le réseau (lecture Fig. 4) | Wi-Fi modélisé à 100 Mbps (`page:3`, `page:10`) |
| Accélération côté client | Stéréo : **1,4×** (GPU), **1,9×** (GBU), **1,7×** (GSCore). Nebula sur GSCore jusqu'à **21,7×** par rapport au GPU mobile, **5,3×** par rapport à GSCore/GBU | 6 datasets (`page:1`, `page:11`, Fig. 21) |
| LoD search | Jusqu'à **52,7×** par rapport à OctreeGS (baseline), meilleur que HierGS et CityGS | GPU serveur (`page:11`, Fig. 20) |
| Ablation | CMP 2,5× ; CMP+TA 2,7× ; +SR (tout) **3,9×** en vitesse. Énergie : 1,5× / 1,5× / **2,0×** | Grandes scènes, par rapport à « Base » collaboratif sur la même architecture (`page:11–12`) |
| Bande passante | **« 1925 % » de moins que la vidéo** (≈ 19× ; formulation des auteurs). Lecture Fig. 24 : **~20–36 Mbps à w = 4** (Mega ~20, Urban/HierGS ~35), 17–45 Mbps pour w = 1…32 ; peu sensible à w | Pour tenir 90 FPS (`page:11`, `page:12`) |
| Énergie | **14,9×** moins que GPU et 1,4× moins que GSCore. Remote (vidéo) reste meilleur : **38,4×**, car le casque ne fait presque que recevoir | Wi-Fi 100 nJ/octet ; affichage exclu (`page:10–11`, Fig. 19) |
| Qualité stéréo | **−0,1 dB PSNR** par rapport à Base (rendu séparé des deux yeux). SSIM et LPIPS sans perte. La perte est attribuée **uniquement à la compression**. Lecture Fig. 16 (PSNR / GT) : ~24–28 dB selon le dataset ; Warp/Cicero nettement en dessous (jusqu'à ~2 dB sur Mega) | HierGS (`page:10`) |
| Qualité de la compression | PSNR (par rapport au rendu de référence, pas au GT) proche de H.265 Lossy-H (lecture Fig. 17 : ~44–48 dB) pour une bande passante bien moindre | `page:10–11` |
| Mémoire | Scènes jusqu'à 66 Go (cloud). Côté client : non chiffré (sous-graphe avec éviction à 32 frames) | `page:3`, `page:7` |
| Entraînement | Non traité : arbres LoD construits avec HierGS (`page:6`) | — |

**Matériel : tout est simulé.** Client = RTL d'accélérateur mis à l'échelle 8 nm, avec baselines GPU Orin et GSCore **également en RTL** (« We develop the RTL implementation of both GPU and GSCore », `page:10/block:13`). Serveur = 2× A100. Réseau = modèle à 100 Mbps constant. **Aucun casque réel, aucun réseau réel, aucune étude utilisateur.**

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Panorama du rendu distant et collaboratif VR (Q-VR, EDC, CollabVR, Cicero, E-VR, DejaView) et des accélérateurs 3DGS (GSCore, GBU, MetaSapiens, Lumina) (`page:12`). Chiffres de contrainte : < 12 Go sur casque, > 1 Gbps en vidéo 4K à 90 FPS |
| 2. Gaussiennes depuis SfM, covariance | Rien (réutilise les modèles HierGS, CityGS, OctreeGS) |
| 3. Rendu rapide, visibilité, casque | **Cœur** : répartition cloud/client par étape, streaming de Gaussiennes, tri et projection partagés entre les yeux, reprojection par disparité |
| 4. Évaluation | Grille utile : motion-to-photon, FPS stéréo, bande passante, énergie par composant, PSNR par rapport à Base (erreur de l'approximation stéréo) et par rapport au GT. Mais tout est **simulé** |

## Ce que Nebula fait déjà / ce qui reste ouvert (pistes P1–P5)
| Piste | Déjà fait par Nebula | Reste ouvert |
|---|---|---|
| **P1** rendu partagé edge/casque par visibilité | Rendu **collaboratif cloud/casque pour la 3DGS** : partage **par étape** (LoD search au cloud, **toute** la rasterisation sur le casque). Le papier argumente que le partage au niveau pixel est incompatible avec la 3DGS et limité par la bande passante (`page:2`, `page:12`) | Partage **par visibilité / profondeur / excentricité** (casque = proche + fovéa, edge = lointain + périphérie **en pixels**, puis composition) : **non fait**. Pas de fovéation, pas de composition d'images. Nebula suppose un casque **doté d'un accélérateur 3DGS** capable de tout rasteriser. Un casque à GPU standard (Quest 3) n'y arrive pas (GPU Orin < 10 FPS dans leur Fig. 18) |
| **P2** mutualisation stéréo | **Réalisé pour l'essentiel** : **un seul préprocessing et un seul tri** sur un FoV élargi. Réutilisation des Gaussiennes α-valides de l'œil gauche par disparité, et fusion de 4 listes triées pour l'œil droit. −0,1 dB (`page:8`, `page:10`) | (a) **Implémentation logicielle sur GPU standard** (CUDA/Vulkan compute sur GPU PC ou casque) : seul un gain de 1,4× « GPU » est donné, **modélisé en RTL**. (b) **Analyse d'erreur** que le papier ne discute pas (voir Contre). (c) Compatibilité avec le tri par pixel StopThePop/VRSplat et l'Optimal Projection. (d) Combinaison avec le **fovéal par œil**. (e) Mesure sur casque réel |
| **P3** budget de Gaussiennes / LOD piloté par un modèle QoS/QoE | Non : seuil τ* fixe, w = 4 fixe, w_r* = 32 fixe. Seules des **sensibilités** sont étudiées (w, taille de tuile, nombre de RU) (`page:12`) | **Entièrement ouvert.** Nebula fournit justement les « boutons » (τ*, w, w_r*, taux de compression) et les grandeurs (bande passante, énergie, FPS) qu'un contrôleur QoS/QoE pourrait piloter |
| **P4** streaming progressif de splats | **Réalisé** dans sa forme de base : streaming de Gaussiennes (Δcut) au lieu de vidéo, avec compression VQ + 16 bits, cache client et éviction synchronisée, ~19× moins de bande passante, peu sensible à la résolution et au FPS (`page:4`, `page:7`, `page:11`) | Ordonnancement **progressif / priorisé** dans le Δcut (importance, fovéa, saillance). **Démarrage à froid** (1re frame complète : volume non chiffré). Réseau **variable** ou avec pertes (seulement 100 Mbps constants). Petites scènes sans LoD (petites scènes seulement évaluées en rendu). Mesure réelle |
| **P5** jumeau numérique hybride | Non abordé | Entièrement ouvert |

## Pour (vis-à-vis de notre problématique)
- Vise exactement la VR stéréo haute résolution (2064×2208 par œil) et mesure les bonnes grandeurs : motion-to-photon, bande passante, énergie.
- Montre **quantitativement** que le streaming vidéo est la mauvaise abstraction pour la 3DGS en VR et qu'envoyer des Gaussiennes est ~19× plus sobre. C'est un argument fort pour P4.
- La partie **cloud** (recherche de LoD temporelle, bit-exacte) et le **gestionnaire de Δcut** sont **logiciels et tournent sur GPU standard** (« out-of-the-box », `page:5`) : reproductibles.
- L'algorithme stéréo est décrit assez précisément (disparité bornée à 16 px, 4 listes, merge) pour être réimplémenté en CUDA.
- Qualité quasi intacte (−0,1 dB), et nettement meilleure que les méthodes de warping d'image.

## Contre / limites
- **Papier d'architecture (cs.AR) : co-design matériel.** Les chiffres phares (70,1 FPS, 21,7×, énergie) supposent un **accélérateur dédié simulé** (RTL mis à l'échelle en 8 nm), pas un casque du commerce. Même la baseline « GPU Orin » est modélisée en RTL (`page:10/block:13`). Rien n'est mesuré sur un casque, un réseau réel ou avec des utilisateurs.
- **Part reproductible sur GPU standard** : la LoD search temporelle (serveur), le Δcut, la compression (reprise de Compact3DGS) et l'algorithme de rasterisation stéréo (**1,4× seulement** sur GPU mobile). Le reste du gain (1,7–1,9×, et 21,7× au total) dépend du matériel.
- **N'atteint pas 90 FPS** (70,1 FPS). Il faut doubler les RU (+62,9 % de surface) (`page:11–12`). Aucune valeur absolue de latence motion-to-photon (seulement des ratios).
- **« Bit-accurate » à nuancer** (analyse critique ; points **non discutés** dans le papier) :
  - une Gaussienne qui échoue à l'α-check ou est coupée par la terminaison précoce à gauche peut être visible à droite (**désocclusions**, bord droit du FoV) ;
  - la reprojection par un **décalage horizontal constant** (X = Bf/D sur le centre) suppose des caméras parallèles rectifiées, alors que la forme 2D projetée diffère légèrement d'un œil à l'autre ;
  - la **couleur SH** dépend de la direction de vue par œil, et on ne sait pas si elle est réévaluée ;
  - le tri partagé depuis un FoV gauche élargi n'est pas l'ordre exact de l'œil droit.
  La perte mesurée (−0,1 dB, attribuée à la compression) suggère un impact faible sur ces scènes, mais **aucune expérience ne l'isole**.
- La cible est la **grande échelle (ville)**. Pour nos scènes (Mip-NeRF 360, T&T, DB), l'intérêt du cloud est plus faible, car tout tient sur le casque. Seule la partie stéréo transfère directement.
- Le gain de qualité liée à la compression est mesuré par rapport au **rendu de référence**, pas au GT (`page:11`). La perte liée au fait que le client continue sans les données cloud n'est pas chiffrée (`page:6`).
- Pas de fovéation, pas d'eye-tracking. Énergie : le streaming vidéo reste **2,6× plus économe** pour le casque (38,4× contre 14,9×).

## Idées à creuser pour une approche novatrice
- *Hypothèse (P2 reformulée)* : **« stéréo partagée logicielle, sans accélérateur »**. Porter la réutilisation par disparité en CUDA/Vulkan compute sur GPU PC-VR et Quest 3, en l'**intégrant au tri par pixel StopThePop/VRSplat**. Mesurer l'erreur isolée (désocclusions, SH par œil) par rapport à deux rendus indépendants, avec une passe de rattrapage pour les Gaussiennes « œil droit seulement ». La différenciation tient au GPU standard, à l'analyse d'erreur et à la compatibilité anti-popping.
- *Hypothèse (P1 reformulée)* : **partage fovéal Gaussienne/pixel**. Le casque rasterise localement la **fovéa** à partir de Gaussiennes streamées (façon Nebula). L'edge envoie la **périphérie** en vidéo basse résolution, où l'acuité est faible et le débit donc modeste. La composition se fait par profondeur. C'est pertinent pour les casques **sans accélérateur**, là où Nebula ne tient pas.
- *Hypothèse (P3)* : **contrôleur QoS/QoE** (éq. 1 de Kamdjou) pilotant τ*, w et le taux de compression selon le débit mesuré et le budget GPU du casque. Nebula donne les courbes de sensibilité (Fig. 23–25) comme point de départ.
- *Hypothèse (P4)* : **Δcut priorisé** (fovéa, saillance, contribution α) avec dégradation gracieuse sous débit variable, et démarrage à froid progressif. Évaluer sur trace réseau réelle plutôt qu'à 100 Mbps constants.

## Citations clés
> « Instead of streaming videos, Nebula streams intermediate results after the LoD search, reducing 1925% data communication between the cloud and the client. » (`doc:f69941e/tier:standard/page:1/block:11`)

> « we propose a triangulation-based technique that skips redundant computation in the remaining stages, i.e., preprocessing, sorting, and rasterization, while preserving bit-accurate results in 3DGS. » (`doc:f69941e/tier:standard/page:7/block:13`)

> « Note that, we offload only LoD search, not preprocessing, to the cloud, so that the client can render any viewport near the current position with no extra data traffic. » (`doc:f69941e/tier:standard/page:5`)

> « Overall, Nebula achieve 70.1 FPS. While Nebula does not achieve the VR requirement, 90 FPS, Sec. 7.4 shows that Nebula can easily achieve 90 FPS by scaling up VRC. » (`doc:f69941e/tier:standard/page:11`)

## Liens
- Papiers liés :
  - [Kerbl 2024, Hierarchical 3DGS](../kerbl2024_hierarchical-3dgs/fiche.md) : arbre LoD et critère τ réutilisés tels quels.
  - [Lee 2023, Compact3D](../lee2023_compact3d/fiche.md) : quantification vectorielle des SH réutilisée pour le Δcut.
  - [Radl 2024, StopThePop](../radl2024_stopthepop/fiche.md) et [Tu 2025, VRSplat](../tu2025_vrsplat/fiche.md) : tri par pixel et anti-popping. VRSplat **double les temps mono** pour simuler la stéréo, alors que Nebula partage réellement le tri : combinaison à explorer (P2).
  - [Franke 2024, VR-Splatting](../franke2024_vr-splatting/fiche.md), [Xin 2025, A3FR](../xin2025_a3fr-foveated/fiche.md) : fovéal, absent de Nebula (P1).
  - [Shi 2024, LapisGS](../shi2024_lapisgs/fiche.md), [Wan 2025, edge-collab GS](../wan2025_edge-collab-gs/fiche.md) : streaming et collaboration edge, à comparer pour P1/P4.
  - [Oh 2025, NEO on-device](../oh2025_neo-on-device/fiche.md), [Feng 2024, FlashGS](../feng2024_flashgs/fiche.md) : accélération du rendu sur appareil et sur GPU.
  - [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) : cadre QoS/QoE (P3) et latences edge.
  - [Kerbl 2023, 3DGS](../kerbl2023_3dgs/fiche.md) : pipeline de base.
