---
citekey: oh2025_neo-on-device
mineru_doc: 43d3857
type: conférence   # ASPLOS '26 (arXiv 2511.12930, cs.AR)
statut: fiche complète
tags: [3dgs, accélérateur-matériel, asic, tri, cohérence-temporelle, réutilisation-inter-frames, bande-passante-dram, on-device, gscore, jetson-orin, simulation-cycle-accurate, ar-vr]
---

# Neo: Real-Time On-Device 3D Gaussian Splatting with Reuse-and-Update Sorting Acceleration

**Référence :** Changhun Oh, Seongryong Oh, Jinwoo Hwang, Yoonsung Kim (KAIST), Hardik Sharma (Meta), Jongse Park (KAIST) (2025/2026). *Neo: Real-Time On-Device 3D Gaussian Splatting with Reuse-and-Update Sorting Acceleration.* Proc. ASPLOS '26 (Pittsburgh, 22–26 mars 2026), 15 p. arXiv [2511.12930](https://arxiv.org/abs/2511.12930) (`doc:43d3857/tier:standard/page:1`, `page:2`)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Co-design algorithme/**ASIC** qui supprime le goulot « tri » (bande passante DRAM) du 3DGS embarqué en **réutilisant la table triée de la frame précédente** et en ne la corrigeant que localement (tri partiel par blocs de 256 à frontières alternées + insertion/suppression + mise à jour différée des profondeurs) : **99,3 FPS moyen en QHD (2560×1440) mono**, −94,4 % de trafic DRAM vs Jetson Orin AGX, perte ≤ 0,1 dB — **résultats d'un simulateur cycle-accurate d'un accélérateur synthétisé en 7 nm, pas d'une mesure sur appareil** (`page:1`, `page:2`, `page:10`, `page:11`).

## Problème traité
- AR/VR exige haute résolution + latence 7–15 ms ; le cloud ajoute des délais → rendu **sur l'appareil** nécessaire (`page:1`). Quest 3 : 2064×2208 par œil, jusqu'à 90 Hz ; Vision Pro : 23 Mpx (`page:3`).
- Même l'ASIC GSCore (ASPLOS'24) ne fait que **66,7 FPS en HD, 31,1 en FHD, 15,8 en QHD** (4 cœurs, 51,2 GB/s) sur 6 scènes T&T (`page:4`).
- Diagnostic : le rendu HD+ embarqué est **limité par la bande passante DRAM, pas par le calcul** : 4× plus de cœurs → ×1,12 FPS seulement ; 4× plus de bande passante (204,8 GB/s) → ×3,83 (`page:4`). Le **tri** représente jusqu'à **90,8 %** du trafic DRAM sur GPU et **69,3 %** sur GSCore ; GSCore demande en moyenne 60,7 GB/s (FHD) et 80,0 GB/s (QHD) alors que les appareils AR/VR offrent **17,8 à 59,7 GB/s** (`page:5`).
- **Nuance importante pour nous** : ce goulot « tri » n'apparaît qu'**une fois la rasterisation accélérée** (GSCore). Sur GPU (Orin), la **rasterisation reste dominante (68,8 % du temps)** (`page:8`) — cohérent avec le constat de la base (après StopThePop, le coût dominant est par pixel).

## Méthode / contributions
**Observation (cohérence temporelle)** — > 90 % des tuiles conservent > 78 % de leurs Gaussiennes d'une frame à l'autre ; 99 % de l'ordre de tri est stable ; au 99ᵉ percentile la Gaussienne la plus déplacée ne bouge que de **31 positions** dans une liste de milliers (`page:5`, Fig. 6–7). Séquences T&T capturées à 30 FPS (poses consécutives du dataset) (`page:10`).

**Algorithme reuse-and-update (par tuile de 64×64 px)** (`page:6`, `page:7`, Table 1 `page:10`) :
1. **Reordering — Dynamic Partial Sorting** : la table triée de la frame t−1 est découpée en **chunks de 256** entrées tenant en SRAM ; chaque chunk est trié localement (1 lecture + 1 écriture DRAM, **une seule passe**). Les frontières de chunks sont **décalées d'un demi-chunk une frame sur deux** (interleaving) pour qu'une Gaussienne puisse migrer au-delà d'un chunk en quelques frames (`page:6–7`, Algo 1, Fig. 9).
2. **Insertion** : les Gaussiennes nouvellement visibles dans la tuile (« incoming », détectées au préprocessing par comparaison avec la table précédente) sont triées à part puis fusionnées (merge) (`page:6`, `page:8`).
3. **Deletion** : les Gaussiennes sorties de la tuile sont marquées invalides (bit) pendant la rasterisation et physiquement retirées lors du merge suivant (`page:6`, `page:9`).
4. **Depth update différé** : pendant la rasterisation (qui lit déjà les attributs), la profondeur de chaque entrée est réécrite dans la table → le tri de la frame suivante utilise des profondeurs **en retard d'une frame**. Sans ce mécanisme : +33,2 % de trafic (`page:6`, `page:7`).

**Erreur tolérée (explicitement)** — l'ordre n'est pas garanti exact : il « converge en quelques frames » après un mouvement brusque ; une passe unique coûte « < 0,1 dB » ; la boucle vertueuse « plus rapide → tri plus fréquent → ordre plus juste » est invoquée (`page:5–7`). Pas de borne formelle d'erreur.

**Matériel** (`page:8–9`, Table 1 `page:10`) : Preprocessing Engine (4 unités projection/couleur/duplication), Sorting Engine (16 cœurs : Bitonic Sort Unit 16 entrées + Merge Sort Unit+ qui fusionne insertions/suppressions ; buffers I/O 64 Ko), Rasterization Engine (4 cœurs, 16 Subtile Compute Units, 16 Intersection Test Units qui génèrent à la volée les bitmaps de sous-tuiles 8×8 et détectent les sortants ; buffer 200 Ko). Rasterisation par sous-tuiles héritée de GSCore.

**Version logicielle (Neo-SW, CUDA sur Orin AGX)** : −70,4 % de trafic total, −82,8 % sur le tri, mais **seulement ×1,1 de latence** (tri ×1,54) car accès irréguliers (insertion/suppression) et rasterisation dominante sur GPU (`page:7–8`).

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| **Nature des mesures** | Neo et GSCore : **simulateur cycle-accurate** (timings RTL Verilog synthétisé Synopsys DC, ASAP7 7 nm ; buffers CACTI 22 nm → 7 nm ; DRAM LPDDR4 modélisée Ramulator). Orin AGX : **vrai matériel** (Jetson AGX Orin 64 GB, jusqu'à 60 W, 204,8 GB/s) | `page:10` |
| FPS moyen Neo | **HD ~128 · FHD ~115 · QHD 99,3** (99,3 explicite ; autres = lecture Fig. 15) | 6 scènes T&T, **mono**, 1280×720 / 1920×1080 / 2560×1440 (`page:10`) |
| Speedup Neo | vs Orin AGX : **×5,0 / ×7,2 / ×10,0** (HD/FHD/QHD) ; vs GSCore 16 cœurs : ×1,8 / ×3,3 / ×5,6 | idem (`page:10`) |
| Orin AGX (réel) | ~25 (HD) · ~16 (FHD) · ~10 FPS (QHD) — lecture Fig. 15 | 3DGS CUDA standard (`page:10`) |
| GSCore 16 cœurs (simulé) | ~73 (HD) · ~35 (FHD) · ~18 FPS (QHD) — lecture Fig. 15 | `page:10` |
| Par scène Neo QHD | ~80 (Playground) à ~134 (Francis) FPS — lecture Fig. 15 | `page:10` |
| Latence par frame | Neo ≈ 11–12 ms/frame, **sans pic** ; tri périodique : pics > 23 ms (viole le SLO 16,6 ms) ; tri en arrière-plan ≈ 15 ms ; tri hiérarchique GSCore ≈ 13–15 ms — lecture Fig. 19 (résolution non précisée) | `page:12` |
| Motion-to-photon | **Non rapportée** | — |
| Trafic DRAM (60 frames QHD) | Orin 346,5 GB · GSCore 104,6 GB · **Neo 19,6 GB** (−94,4 % / −81,3 %) → tient sous 51,2 GB/s | `page:10–11` |
| Qualité | PSNR/LPIPS vs 3DGS original : **Δ ≤ 0,1 dB et ≤ 0,001** sur les 6 scènes (ex. Family 28,2 → 28,1 dB ; Train 25,0 → 24,9) ; SSIM non rapporté | `page:11`, Table 2 |
| Surface / puissance | Neo **0,387 mm², 797,8 mW** @1 GHz 7 nm (GSCore mis à l'échelle : 0,417 mm², 719,9 mW) ; ajouts MSU+ et ITU = 9,04 % surface, 8,91 % puissance | `page:11`, Tables 3–4 |
| Énergie par frame | Non rapportée (seulement la puissance de l'accélérateur ; DRAM, SoC, affichage exclus) | — |
| Grande scène (Mill19 Building/Rubble) | Neo **65,2 FPS** ; Orin < 13,6 ; GSCore < 24,9 | résolution non précisée (`page:11`) |
| Mouvement caméra rapide | ~89 FPS (×1) → ~67 FPS (×16) — lecture Fig. 17b ; « > 60 FPS » | `page:11` |
| Ablation HW | Sorting Engine seul (Neo-S) : ×3,3, −71,1 % trafic ; + Rasterization Engine : ×1,7 et −35,8 % supplémentaires | `page:11–12` |
| Entraînement | 3DGS standard, 400 images/scène, **200K itérations** ; **aucun ré-entraînement** requis par Neo | `page:10`, `page:12` |
| Mémoire modèle | Non rapportée | — |

## Stéréo / VR — ce que dit (et ne dit pas) le papier
- Motivation entièrement AR/VR (Quest 3, Vision Pro, 2K–4K par œil) mais **toutes les évaluations sont mono**, sur écran virtuel HD/FHD/QHD ; **aucune mention de rendu stéréo, de second œil ni de casque réel**. QHD mono (3,7 Mpx) ≈ 0,8× la surface d'**un seul** œil Quest 3 (2064×2208 = 4,56 Mpx) — calcul personnel.
- Aucune latence motion-to-photon, pas de reprojection/ATW, pas d'étude utilisateur.
- **Transposition à la stéréo (hypothèse, piste P2)** : la réutilisation inter-frames repose sur (i) une forte rétention des Gaussiennes par tuile et (ii) des déplacements d'ordre faibles. Entre les deux yeux (baseline ~6 cm, poses simultanées), la situation est analogue à un petit déplacement latéral de caméra : on peut supposer une rétention élevée **à distance** (disparité faible), mais elle chute au premier plan (disparité de dizaines de px → changement de tuile) et aux désocclusions. Le mécanisme Neo (tri partiel à partir d'un ordre « presque juste » + insertion des entrants + suppression des sortants) est précisément l'outil pour produire la liste de l'œil droit à partir de celle de l'œil gauche, **sans attendre la convergence sur plusieurs frames** (la stéréo n'a pas de « frame suivante » pour corriger) : il faudrait donc soit plusieurs passes de tri partiel, soit limiter la réutilisation aux Gaussiennes lointaines. [Nebula](../zhu2025_nebula/fiche.md) réalise déjà une réutilisation gauche→droite par disparité sur accélérateur simulé (dérivé de GSCore) → P2 est occupée côté ASIC ; l'espace libre reste le **logiciel sur GPU standard** et la **combinaison inter-yeux × inter-frames**.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Chiffres d'environnement utiles : bande passante DRAM des appareils AR/VR 17,8–59,7 GB/s ; Quest 3 2064×2208/œil, 90 Hz ; exigence 7–15 ms ; baseline réelle Jetson Orin AGX (~10 FPS QHD) (`page:1`, `page:3`, `page:5`). **Pas de mesure Quest/XR2.** |
| 2. Gaussiennes 3D depuis SfM, covariance | Rien (3DGS standard, 200K itérations) |
| 3. Rendu rapide, visibilité, casque XR | Cœur : tri incrémental par tuile exploitant la cohérence temporelle ; détection des entrants/sortants par tuile ; mise à jour différée des profondeurs. **Mais gain réel sur GPU : ×1,1 seulement** |
| 4. Évaluation | Méthodologie « DRAM traffic / 60 frames » et latence frame-à-frame (pics) réutilisable ; mais tout est simulé, mono, sans motion-to-photon ni énergie système |

## Pour (vis-à-vis de notre problématique)
- Identifie clairement **la bande passante mémoire** (et non le calcul) comme limite du 3DGS HD+ embarqué ; chiffres utiles pour dimensionner un casque autonome (`page:4–5`).
- Qualité quasi intacte (≤ 0,1 dB), **sans ré-entraînement** : compatible avec n'importe quel modèle 3DGS (`page:11–12`).
- Robuste aux mouvements rapides (> 60 FPS à ×16) et à grande échelle (65,2 FPS Mill19) en simulation (`page:11`).
- Montre que les stratégies naïves (tri périodique, tri en arrière-plan à la Lumina / antimatter15) créent des pics de latence ou des chutes de PSNR visibles (Fig. 19) → argument pour un tri incrémental propre (`page:12`).

## Contre / limites
- **Pas un résultat sur appareil** : ASIC hypothétique de 0,387 mm² simulé ; aucun casque ni SoC mobile réel (Snapdragon/XR2 absents). Le seul matériel réel (Orin AGX, 60 W) est **bien plus puissant qu'un XR2** et reste à ~10 FPS QHD mono.
- **Mono uniquement** : 99,3 FPS QHD mono ≈ ~50 FPS stéréo par dédoublement naïf à une résolution < celle du Quest 3 (extrapolation personnelle) → sous 72 Hz.
- En logiciel sur GPU le gain est ×1,1 : **inutilisable tel quel sur Quest 3** (pas d'accès à un ASIC) ; la rasterisation (68,8 %) domine sur GPU, en accord avec notre constat post-StopThePop.
- Tri **par tuile, par profondeur de centre** (style 3DGS/GSCore) : pas de gestion du popping, incompatibilité non discutée avec le tri par pixel de [StopThePop](../radl2024_stopthepop/fiche.md)/[VRSplat](../tu2025_vrsplat/fiche.md).
- Erreur d'ordre non bornée formellement ; profondeurs en retard d'une frame ; SSIM non rapporté ; puissance DRAM/SoC non comptée.
- Beaucoup de chiffres par scène uniquement sur graphiques.

## Idées à creuser pour une approche novatrice
- *Hypothèse (P2 × Neo)* : **tri incrémental inter-yeux + inter-frames** — l'œil gauche à t sert de base à l'œil droit à t (réutilisation par disparité, cf. Nebula) **et** à l'œil gauche à t+1 (Neo). Mesurer sur GPU PC-VR puis Quest 3 la rétention par tuile gauche/droite en fonction de la profondeur, pour savoir où la réutilisation est sûre.
- *Hypothèse* : porter le Dynamic Partial Sorting en **compute shader Vulkan/WebGPU** (chunks de 256 en mémoire partagée) sur GPU mobile tuilé (Adreno), où la bande passante DRAM est justement la ressource rare — le ×1,1 d'Orin ne présage pas du gain sur un GPU mobile bandwidth-bound.
- *Hypothèse (P1)* : dans un split edge/casque, la table triée réutilisée pourrait être maintenue côté casque et seuls les « incoming » (entrants par tuile) transmis par l'edge — rapprocher de [Nebula](../zhu2025_nebula/fiche.md) (Δcut) et [LapisGS](../shi2024_lapisgs/fiche.md).
- *Hypothèse (P3)* : la mesure « taux d'entrants/sortants par tuile » est un bon signal bon marché pour piloter un budget de Gaussiennes/LOD selon le mouvement de tête.

## Citations clés
> « Our analysis identifies the sorting stage in the 3DGS rendering pipeline as the major bottleneck due to its high memory bandwidth demand. » (`doc:43d3857/tier:standard/page:1`)

> « at the 99th percentile, the Gaussian with the greatest shift moves only 31 positions from its original location » (`doc:43d3857/tier:standard/page:5`)

> « this design defers the depth update such that, for any given frame, sorting relies on depth values that are one frame stale. » (`doc:43d3857/tier:standard/page:7`)

> « rasterization remains the dominant bottleneck in GPU-based execution, accounting for 68.8% of total runtime. » (`doc:43d3857/tier:standard/page:8`)

> « We measure the latency of GSCore, and Neo using a cycle-accurate simulator » (`doc:43d3857/tier:standard/page:10`)

## Liens
- Papiers liés :
  - [Zhu 2025, Nebula](../zhu2025_nebula/fiche.md) : même famille (accélérateur dérivé de GSCore, simulé) mais **stéréo** réelle (réutilisation gauche→droite) et cloud–client — complément direct pour P1/P2.
  - [Radl 2024, StopThePop](../radl2024_stopthepop/fiche.md), [Tu 2025, VRSplat](../tu2025_vrsplat/fiche.md) : tri par pixel/anti-popping ; question ouverte de la compatibilité avec un tri incrémental.
  - [Du 2026, Mobile-GS](../du2026_mobile-gs/fiche.md) : approche opposée — **supprimer** le tri (rendu order-independent) plutôt que l'amortir ; mesures sur vrai téléphone.
  - [Han 2026, WebSplatter](../han2026_websplatter/fiche.md) : tri radix GPU sur mobile via WebGPU ; montre qu'en pratique mobile le système est **render-bound**, pas sort-bound.
  - [Feng 2024, FlashGS](../feng2024_flashgs/fiche.md), [Hanson 2024, Speedy-Splat](../hanson2024_speedy-splat/fiche.md) : réduction des paires Gaussienne/tuile (alimente aussi le trafic de tri).
  - [Kerbl 2023, 3DGS](../kerbl2023_3dgs/fiche.md) : pipeline de référence.
