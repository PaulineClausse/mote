---
citekey: murartal2015_orb-slam
mineru_doc: 442bcef
type: article de revue   # IEEE Transactions on Robotics
statut: fiche complète
tags: [slam, visual-slam, monoculaire, orb, keyframes, covisibility-graph, essential-graph, bag-of-words, dbow2, relocalisation, loop-closing, bundle-adjustment, g2o, ptam, lsd-slam, tum-rgbd, kitti, newcollege, cpu-only, lignée-orb-slam, localisation-poses]
---

# ORB-SLAM: a Versatile and Accurate Monocular SLAM System

**Référence :** Raúl Mur-Artal, J. M. M. Montiel, Juan D. Tardós (2015). *ORB-SLAM: a Versatile and Accurate Monocular SLAM System.* IEEE Transactions on Robotics, 31(5), 1147–1163. DOI [10.1109/TRO.2015.2463671](https://doi.org/10.1109/TRO.2015.2463671) · arXiv [1502.00956v2](https://arxiv.org/abs/1502.00956) (version lue, 18 sept. 2015) · code public : http://webdiis.unizar.es/~raulmur/orbslam (`doc:442bcef/tier:standard/page:1`, `page:3`) · place recognition : DBoW2, https://github.com/dorian3d/DBoW2 (`page:6`). Univ. Zaragoza (I3A), financement DPI2012-32168 (`page:2`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Système fondateur de SLAM visuel **monoculaire, à points épars et keyframes**, qui fait tourner **trois threads parallèles (tracking, local mapping, loop closing)** sur une seule carte de points ORB + keyframes reliés par un **graphe de covisibilité**, avec initialisation automatique, **relocalisation par sac de mots (DBoW2)** et fermeture de boucle par pose graph Sim(3) sur un **Essential Graph** ; le tout **sans GPU, à 25–30 Hz** sur un i7 portable, avec une erreur de trajectoire **< 1 cm** en intérieur sur TUM RGB-D (`page:2`, `page:9`, `page:10`, `page:15`).

## Problème traité
- Le bundle adjustment (BA) est la méthode « gold standard » de la SfM, mais en SLAM temps réel il faut lui fournir : des correspondances entre **keyframes** sélectionnées sans redondance, un réseau fort de keyframes/points avec parallaxe, une bonne initialisation, une **carte locale** pour l'exploration, et des optimisations globales rapides (pose graph) pour fermer les boucles (`page:2`).
- PTAM (Klein & Murray 2007), référence de l'époque, est limité aux petites scènes : pas de fermeture de boucle, relocalisation peu invariante au point de vue (corrélation de vignettes basse résolution), initialisation manuelle, insertion de keyframes trop prudente qui fait échouer le tracking en exploration difficile (`page:2`, `page:3`, `page:4`).
- Les systèmes « grande échelle » existants utilisent des features différentes pour le tracking et la reconnaissance de lieu (ex. SURF), ou ne réutilisent pas la carte (odométrie visuelle pure, Lim et al. 2014), ou n'ont pas de code public (CD-SLAM) (`page:3`, `page:4`).
- Les méthodes **directes** (LSD-SLAM) donnent des cartes semi-denses, mais leur précision de localisation est « significantly lower » que celle des méthodes à features, résultat « surprising » que le papier mesure puis discute (`page:4`, `page:16`).

## Méthode / contributions
### Architecture : trois threads, une carte
- **Tracking** (chaque image) : extraction ORB → estimation initiale de pose par **modèle à vitesse constante** et recherche guidée des points de la frame précédente (recherche élargie si le modèle est violé) → si perdu, **relocalisation globale** (BoW + PnP RANSAC) → **track local map** : projection des points des keyframes K1 (partageant des points avec la frame) et K2 (voisins de K1 dans le graphe de covisibilité), filtrage par angle de vue (rejet si v·n < cos 60°) et par plage d'échelle [d_min, d_max] → **motion-only BA** → décision de nouvelle keyframe (`page:5`, `page:7`, `page:8`).
- **Local mapping** (chaque keyframe) : insertion dans le graphe de covisibilité et le spanning tree, calcul du BoW, **culling des points récents**, triangulation de nouveaux points avec les keyframes connectées (contrainte épipolaire, profondeur positive, parallaxe, reprojection, cohérence d'échelle), **local BA** (keyframe courante + voisines covisibles + leurs points, autres keyframes observatrices fixées, outliers rejetés au milieu et à la fin), **culling de keyframes** (`page:5`, `page:8`, `page:9`).
- **Loop closing** (chaque keyframe traitée) : candidats BoW filtrés par le score minimal des voisines covisibles (θ_min = 30), **trois candidats consécutifs cohérents** exigés ; calcul d'une **similarité Sim(3)** (Horn, RANSAC) car la carte monoculaire dérive en 7 DoF (3 rotations, 3 translations, échelle) ; fusion des points dupliqués ; **pose graph sur l'Essential Graph** (`page:5`, `page:9`).
- Toutes les optimisations utilisent Levenberg-Marquardt dans **g2o** ; coût de Huber, covariance Ω = σ² I liée à l'échelle de détection du point (`page:5`, `page:16`).

### Carte : points + keyframes + graphes
- **Point de carte** : position 3D, direction de vue moyenne n, descripteur ORB représentatif (distance de Hamming minimale aux autres), distances d_min/d_max d'observabilité selon l'invariance d'échelle d'ORB (`page:5`).
- **Keyframe** : pose T_iw, intrinsèques, toutes les features ORB (associées ou non) (`page:5`).
- **Graphe de covisibilité** : arête entre deux keyframes si ≥ 15 points communs, poids θ = nombre de points communs (`page:5`).
- **Essential Graph** : spanning tree incrémental + arêtes de covisibilité avec θ_min = 100 + arêtes de boucle ; ≈ 5 arêtes par keyframe sur NewCollege, « a quite sparse graph » (`page:6`, `page:11`).
- **Politique « survival of the fittest »** : création généreuse, élimination sévère. Point gardé seulement s'il est retrouvé dans > 25 % des frames où il est prédit visible et observé par ≥ 3 keyframes ; keyframe supprimée si 90 % de ses points sont vus par ≥ 3 autres keyframes à échelle égale ou plus fine ⇒ carte qui « only grows if the scene content changes » (`page:2`, `page:5`, `page:8`, `page:9`).
- Décision de nouvelle keyframe : > 20 frames depuis la dernière relocalisation ; local mapping libre ou > 20 frames depuis la dernière keyframe ; ≥ 50 points suivis ; < 90 % des points de K_ref (critère de changement visuel, pas de distance) ; une keyframe insérée pendant un local BA **interrompt** celui-ci (`page:8`).

### Features : les mêmes ORB pour tout
- Besoin d'une extraction « much less than 33 ms » : SIFT ≈ 300 ms, SURF ≈ 300 ms, A-KAZE ≈ 100 ms exclus ; BRIEF/LDB exclus faute d'invariance en rotation ; **ORB** = FAST orientés multi-échelle + descripteur binaire 256 bits (`page:4`).
- Extraction : 8 niveaux d'échelle, facteur 1,2 ; 1000 coins pour 512×384 à 752×480 px, 2000 pour KITTI 1241×376 ; grille par niveau avec ≥ 5 coins par cellule, seuil adaptatif (`page:7`).
- **Place recognition DBoW2** : vocabulaire ORB appris hors ligne (générique, réutilisable entre environnements), index inversé mis à jour aux suppressions de keyframes, regroupement des candidats par covisibilité (et non par proximité temporelle), retour de tous les candidats > 75 % du meilleur score ; le même arbre de vocabulaire (niveau 2 sur 6) accélère la mise en correspondance par force brute, avec test de cohérence d'orientation (`page:6`). Le recognizer antérieur [11] retrouvait un candidat en < 39 ms (extraction incluse) sur 10 000 images (`page:3`).

### Initialisation automatique
- Calcul **en parallèle** d'une homographie H (DLT normalisée, 4 points) et d'une matrice fondamentale F (8 points) en RANSAC avec le même tirage ; score symétrique avec seuils χ² à 95 % (T_H = 5,99, T_F = 3,84, σ = 1 px) ; sélection H si R_H = S_H/(S_H+S_F) > 0,45 (`page:6`, `page:7`).
- Les 8 hypothèses (H, Faugeras) ou 4 (E, SVD) sont **toutes triangulées** ; initialisation seulement s'il existe un gagnant net (parallaxe, points devant les deux caméras, faible reprojection), sinon on attend ; ceci évite l'ambiguïté double planaire — PTAM et LSD-SLAM initialisent une solution plane corrompue sur NewCollege (`page:7`).

### Ce qui a été repris par ORB-SLAM3 (lecture croisée, à confirmer dans la fiche voisine)
D'après le papier ORB-SLAM3 (Campos et al. 2021, fiche [campos2021_orb-slam3](../campos2021_orb-slam3/fiche.md)), la lignée a conservé tel quel : les features ORB uniques pour tracking/mapping/relocalisation/boucles ; l'architecture à trois threads ; la carte points + keyframes avec graphe de covisibilité, spanning tree et Essential Graph ; DBoW2 et la relocalisation BoW + PnP ; la politique de culling des keyframes et des points ; le local BA interrompu par l'arrivée de keyframes ; g2o. ORB-SLAM3 y ajoute ce qui manque ici : fusion **IMU** (visuel-inertiel), stéréo/RGB-D, caméras fisheye, et le système **multi-cartes Atlas** (cartes déconnectées fusionnées plus tard), avec une reconnaissance de lieu dont la vérification géométrique est renforcée. Ces ajouts ne sont pas décrits dans le présent papier (non rapporté ici).

## Résultats chiffrés
| Métrique | Valeur | Conditions (dataset, résolution, matériel) |
|---|---|---|
| Matériel | **Intel Core i7-4700MQ (4 cœurs @ 2,40 GHz), 8 Go RAM**, pas de GPU ; 3 threads + ROS, d'où une variabilité (médiane sur plusieurs runs) | `page:9` |
| Fréquence de tracking | **25–30 Hz** ; images traitées « exactly at the frame rate they were acquired » | NewCollege 512×382 à 20 fps, KITTI à 10 fps (`page:9`, `page:10`, `page:13`) |
| Temps par image (thread tracking) | Total **30,57 ms** médiane (31,60 ± 10,39) : extraction ORB 11,10 · pose initiale 3,38 · track local map 14,84 ms | NewCollege, Table I (`page:10`) |
| Temps par keyframe (local mapping) | Total **383,59 ms** médiane (464,27 ± 217,89) : insertion 10,29 · culling points 0,10 · création points 66,79 · **local BA 296,08** · culling keyframes 8,07 ms | Table I (`page:10`) |
| Détection de boucle | Candidats 4,71 → 14,71 ms et Sim(3) 17,98 → 48,68 ms pour 287 → 4496 keyframes (croissance sous-linéaire) | Table II (`page:10`) |
| Correction de boucle | 0,51 s (287 KF, 1347 arêtes) → **4,69 s** (4496 KF, 21 797 arêtes), dont optimisation Essential Graph 0,26 → 3,62 s | Table II (`page:10`) |
| ATE RMSE intérieur (keyframes, alignement Sim(3)) | **0,30 cm** (fr2 xyz) à **3,81 cm** (fr2 360 kidnap) ; fr1 desk 1,69 ; fr2 desk 0,88 ; fr3 long office 3,45 ; fr3 walk xyz 1,24 ; fr3 walk halfsph 1,74 cm ; fr3 nstr tex far : « ambiguity detected », refus d'initialiser | TUM RGB-D, 16 séquences, médiane sur 5 runs, Table III (`page:11`, `page:12`) |
| Comparaison | PTAM 0,20–2,74 cm quand il survit mais **perd le tracking dans 8/16** ; LSD-SLAM 2,15–38,53 cm, perd dans 3/16 ; RGBD-SLAM 1,34–9,50 cm (6 DoF) | Table III (`page:11`, `page:12`) |
| Relocalisation | fr2_xyz : recall **78,4 %** (ORB-SLAM, 24 KF) vs 34,9 % (PTAM, 37 KF), RMSE 0,38 vs 0,26 cm, max 1,67 vs 1,52 cm ; fr3_walking_xyz (occlusions dynamiques) : **77,9 %** vs **0 %**, RMSE 1,32 cm, max 4,95 cm | carte construite sur les 30 premières s, 2769 et 859 frames à relocaliser, Table IV (`page:11`, `page:13`) |
| Dérive / grande échelle | RMSE **≈ 1 %** de la dimension de la carte : KITTI 03 1,59 m (0,3 %), KITTI 00 6,68 m sur 564×496 m, KITTI 02 21,75 m, **KITTI 08 46,58 m (5 %, aucune boucle)** ; KITTI 01 (autoroute) échoue | 10 séquences KITTI, médiane sur 5 runs, Table V (`page:13`, `page:15`) |
| Apport d'un BA global final (20 it.) | 6,68 → 5,33 m (KITTI 00, 24,83 s) ; 8,23 → 4,85 m (05) ; négligeable sans boucle (08 : 46,58 → 46,68 m) | Table V (`page:15`) |
| Stratégies de fermeture (KITTI 09) | sans boucle 48,77 m ; BA(100 it.) 72,16 s → 18,82 m ; **EG(θ_min=100) 0,48 s, 1979 arêtes → 8,36 m** ; EG(100)+BA(20) 13,40 s → 7,22 m | Table VI (`page:15`) |
| Taille de carte / lifelong | Nb de keyframes **borné** en scène statique (93 s de vues changeantes, PTAM croît sans cesse) ; en dynamique, la carte ne grandit que si le contenu change | TUM fr3 sitting/walking, Fig. 9–10 (`page:12`, `page:13`) |
| Mémoire | non rapporté | — |
| Latence capteur → pose | non rapportée (seulement le temps de traitement par image) | — |
| Précision globale annoncée | « typically below 1 cm in small indoor scenarios and of a few meters in large outdoor scenarios » (échelle alignée à la vérité terrain) | `page:15` |

## Ce que ça dit du tracking du Quest
- **Même famille algorithmique.** Oculus Insight tel que décrit par Meta (dossier [meta2019_oculus-insight-quest](../../supports/meta2019_oculus-insight-quest/dossier.md)) est un SLAM à **landmarks épars, carte persistante, mises à jour asynchrones en arrière-plan, reconnaissance de lieu** : c'est exactement le schéma tracking / mapping asynchrone / relocalisation d'ORB-SLAM, lui-même hérité de PTAM (`page:3`, `page:4`). La séparation « tracking à la cadence image, carte optimisée à part » est la raison pour laquelle le casque peut sortir une pose à chaque image sans attendre le BA.
- **Ce qu'ORB-SLAM n'a pas et que le Quest a.** (1) **Pas d'IMU** : ORB-SLAM est purement visuel, monoculaire, donc **l'échelle est inobservable** (alignement Sim(3) obligatoire avant toute évaluation, dérive en 7 DoF) ; le Quest obtient l'échelle métrique et la gravité par l'IMU (`page:9`, `page:11`). (2) **Une seule caméra** vs 4 caméras monochromes grand angle ; ORB-SLAM échoue sur les rotations pures et les scènes sans objets proches (KITTI 01), cas que le multi-caméras et l'IMU couvrent (`page:11`, `page:13`). (3) **Pas de prédiction haute cadence** : la seule « prédiction » est le modèle à vitesse constante pour la recherche guidée (`page:7`) ; pas de pose à 1 kHz ni d'extrapolation pour la latence d'affichage. (4) Pas de DSP ni de SIMD discuté : CPU 4 cœurs portable (`page:9`).
- **Ce qui se transpose directement à la qualité des poses récupérées par mote.** La pose de tracking est une **motion-only BA** sur la carte locale (`page:8`, `page:16`) : précision locale sous le centimètre quand la carte est bonne (Table III), mais (a) les poses des **frames** ne sont pas raffinées rétroactivement comme celles des keyframes, (b) une fermeture de boucle ou une relocalisation **déplace la carte** (correction Sim(3) propagée aux voisins, Table II : jusqu'à 4,7 s) : les poses déjà émises avant la correction ne sont plus cohérentes avec celles émises après (`page:9`, `page:10`). Si le Quest fait de même, une capture mote qui traverse une relocalisation contiendra un **saut** dans la trajectoire ; il faut détecter ces événements (ou capturer sur une carte déjà stabilisée).
- **Les keyframes sont une notion interne** : ORB-SLAM ne garde que les keyframes « non redondantes » (90 % des points vus ailleurs), au mieux quelques centaines à quelques milliers (`page:9`, `page:10`, `page:15`). Les images que mote capture via la caméra RGB ne coïncident pas avec ces keyframes internes : les poses fournies sont celles du tracking, pas celles, plus précises, du BA sur keyframes.
- Lecture pour H-01 : l'erreur SP-0 de 4–6 mm / 0,3–0,5° est du même ordre que l'ATE RMSE d'ORB-SLAM monoculaire sur bureau (0,3–1,7 cm, `page:12`), ce qui est cohérent avec un casque disposant en plus d'IMU et de 4 caméras ; mais les chiffres d'ORB-SLAM sont des erreurs sur **keyframes après BA**, pas sur toutes les frames.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Papier de référence qui fixe le vocabulaire (keyframe, carte locale, covisibilité, relocalisation BoW, pose graph Sim(3)) utilisé par toute la lignée et, vraisemblablement, par Insight ; comparaison expérimentale features vs direct (`page:4`, `page:11`, `page:16`) |
| 2. Poses pour 3DGS (piste mote, H-01) | Donne l'ordre de grandeur d'un SLAM épars sans IMU : < 1 cm en intérieur sur keyframes, ≈ 1 % de dérive sans boucle ; explique pourquoi les poses « live » diffèrent des poses « BA » et pourquoi une boucle crée une discontinuité ; la sortie keyframes + points + covisibilité est présentée par les auteurs comme « excellent initial guess and skeleton » pour une reconstruction dense (`page:12`, `page:15`, `page:16`) |
| 3. Temps réel, contraintes embarquées | Budget détaillé par opération sur CPU portable : 30 ms/image de tracking dont 11 ms d'extraction ORB, 300 ms de local BA par keyframe ; pas de GPU ; pas de mesure d'énergie ni de version mobile (`page:10`) |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole devenu standard : **ATE RMSE sur la trajectoire des keyframes**, alignement Sim(3) (7 DoF) pour le monoculaire, 6 DoF pour RGB-D, **médiane sur 5 exécutions**, datasets TUM RGB-D (motion capture), KITTI (GPS + Velodyne), NewCollege ; recall + RMSE pour la relocalisation ; courbes de keyframes pour le lifelong (`page:9`, `page:11`, `page:12`, `page:13`) |

## Pour (vis-à-vis de notre problématique)
- Architecture claire et complète, décrite jusqu'aux seuils numériques (θ_min, 20 frames, 90 %, 0,45…) : base idéale pour expliquer ce que fait un VI-SLAM de casque et pour lire ORB-SLAM3 (`page:5` à `page:9`).
- Code public et évaluation sur 27 séquences avec ground truth externe : baseline reproductible pour comparer la qualité de poses Quest vs SLAM ouvert (`page:2`, `page:9`).
- Précision < 1 cm en intérieur **sans GPU** sur un CPU de 2013, ce qui calibre les attentes sur le calcul embarqué (`page:9`, `page:15`).
- Table VI quantifie ce que coûte et rapporte chaque stratégie de correction (BA vs pose graph) : argument direct pour « raffinement des poses à l'entraînement » (H-01) : un pose graph sur Essential Graph converge en 0,5 s là où un BA brut n'y arrive pas (`page:15`).
- Discussion explicite des limites des méthodes directes (rolling shutter, auto-exposition, baseline étroite) et des méthodes à features (`page:16`).

## Contre / limites
- **Monoculaire, sans IMU** : pas d'échelle métrique, pas de gravité, dérive 7 DoF ; toute mesure d'erreur passe par un alignement Sim(3) avec la vérité terrain (`page:9`, `page:11`). Non comparable tel quel aux poses métriques du Quest.
- Échoue en rotation pure, scène sans texture ou sans objets proches (séquences TUM écartées, KITTI 01) ; refuse d'initialiser en cas d'ambiguïté planaire (`page:11`, `page:12`, `page:13`).
- Les erreurs rapportées portent sur les **keyframes** (après local BA), pas sur toutes les frames ; aucune latence capteur → pose, aucune mémoire, aucune énergie (`page:11`, `page:15`).
- Local BA ≈ 300 ms par keyframe et boucles jusqu'à 4,7 s : le mapping est asynchrone, donc les poses émises pendant ces fenêtres restent non corrigées (`page:10`).
- Sortie **éparse** : quelques milliers de points, pas de maillage ni de densité exploitable directement par un 3DGS (les auteurs renvoient à un travail semi-dense ultérieur) (`page:16`).
- Grande boucle de NewCollege parcourue en sens inverse non fermée (BoW non invariant au sens de parcours) (`page:10`, `page:11`).
- Vocabulaire BoW appris hors ligne, à fournir avec le système (`page:6`).

## Idées à creuser pour mote
- *Détection des discontinuités de carte* : enregistrer, côté casque, les instants où la pose MRUK « saute » (équivalent d'une relocalisation ou d'une correction de boucle, `page:9`) et segmenter la capture en tronçons cohérents avant l'entraînement 3DGS ; mesurer dans SP-1 si de tels sauts apparaissent.
- *Capturer sur carte stabilisée* : ORB-SLAM montre que les keyframes se stabilisent après quelques passages (Fig. 10, `page:13`) ; protocole mote = un tour de « chauffe » du casque dans la pièce avant la capture utile, pour que les poses viennent d'une carte déjà bouclée.
- *Sélection de keyframes pour 3DGS* : réutiliser le critère « < 90 % des points de K_ref » (`page:8`) comme critère de sélection des images à envoyer au PC (moins d'images redondantes, meilleure parallaxe), au lieu d'un échantillonnage temporel fixe.
- *Raffinement des poses à l'entraînement (H-01)* : la Table VI (`page:15`) suggère de préférer un **pose graph** (contraintes relatives entre images voisines issues des poses casque) à un BA photométrique global comme étape de raffinement : plus rapide, meilleure convergence depuis une mauvaise initialisation ; à relier à la question « quelle quantité de raffinement un 3DGS tolère-t-il ».
- *Baseline de comparaison* : faire tourner ORB-SLAM (ou ORB-SLAM3 mono-inertiel) sur les images RGB du Quest et comparer avec les poses MRUK et COLMAP, avec le protocole ATE RMSE Sim(3) / médiane sur 5 runs du papier (`page:11`).
- *Mesurer l'écart frames/keyframes* : le papier ne donne pas l'erreur des poses de tracking (frames) ; une expérience mote pourrait quantifier combien les poses « live » du casque diffèrent d'une ré-optimisation hors ligne, pour savoir si le raffinement est indispensable.

## Citations clés
> « Building on excellent algorithms of recent years, we designed from scratch a novel system that uses the same features for all SLAM tasks: tracking, mapping, relocalization, and loop closing. A survival of the fittest strategy that selects the points and keyframes of the reconstruction leads to excellent robustness and generates a compact and trackable map that only grows if the scene content changes, allowing lifelong operation. » (`doc:442bcef/tier:standard/page:2`)

> « We use ORB features [9] which allow real-time performance without GPUs, providing good invariance to changes in viewpoint and illumination. » (`doc:442bcef/tier:standard/page:2`)

> « In monocular SLAM there are seven degrees of freedom in which the map can drift, three translations, three rotations and a scale factor [6]. Therefore to close a loop we need to compute a similarity transformation from the current keyframe K_i to the loop keyframe K_l that informs us about the error accumulated in the loop. » (`doc:442bcef/tier:standard/page:9`)

> « Tracking works at frame-rates around 25-30Hz, being the most demanding task to track the local map. » (`doc:442bcef/tier:standard/page:10`)

> « Thanks to our keyframe selection, keyframes comprise a compact summary of the environment with a very high pose accuracy and rich information of covisibility. Therefore the ORB-SLAM sparse map can be an excellent initial guess and skeleton, on top of which a dense and accurate map of the scene can be built. » (`doc:442bcef/tier:standard/page:16`)

## Liens
- Papiers liés :
  - [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — successeur direct : même architecture, + IMU, stéréo/RGB-D, fisheye, multi-cartes Atlas.
  - [VINS-Mono](../qin2018_vins-mono/fiche.md), [VINS-Fusion](../qin2019_vins-fusion/fiche.md) — alternative visuelle-inertielle par optimisation en fenêtre glissante ; apporte l'échelle métrique qu'ORB-SLAM mono n'a pas.
  - [OpenVINS](../geneva2020_openvins/fiche.md), [Basalt](../usenko2020_basalt/fiche.md), [Kimera](../rosinol2020_kimera/fiche.md) — autres estimateurs ouverts de l'axe « localisation des poses ».
  - [DROID-SLAM](../teed2021_droid-slam/fiche.md), [DPVO](../teed2023_dpvo/fiche.md) — approches apprises, à opposer à la chaîne features/BA classique décrite ici.
  - [Multi-caméras : Kuo 2020](../kuo2020_multicam-slam/fiche.md), [Eckenhoff 2019](../eckenhoff2019_multicam-vins/fiche.md) — extension au cas 4 caméras du Quest.
  - [Delmerico 2018 (benchmark VIO)](../delmerico2018_vio-benchmark/fiche.md), [Nagy 2020](../nagy2020_faster-than-fast/fiche.md), [Navion](../suleiman2019_navion/fiche.md) — contraintes embarquées que ce papier ne traite pas.
  - [Huang 2019 (revue VIN)](../huang2019_vin-review/fiche.md) — pour situer ORB-SLAM dans la taxonomie filtre / optimisation.
  - [Project Aria](../engel2023_project-aria/fiche.md) — pile VIO/SLAM de Meta la plus proche du Quest.
  - [Tosi 2024 (survey NeRF/GS-SLAM)](../tosi2024_nerf-gs-slam-survey/fiche.md), [Photo-SLAM](../huang2024_photo-slam/fiche.md) — SLAM dont le front-end ORB alimente un 3DGS : prolongement direct du « skeleton » annoncé en future work (`page:16`).
  - [3DGS](../kerbl2023_3dgs/fiche.md) — consommateur des poses ; [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — précision mesurée du positionnement VR, à comparer aux ATE de ce papier.
- Dossier : [Oculus Insight / Quest 3](../../supports/meta2019_oculus-insight-quest/dossier.md).
