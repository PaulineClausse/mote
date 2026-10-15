---
citekey: geneva2020_openvins
mineru_doc: 194e432
type: conférence   # IEEE ICRA 2020, Paris
statut: fiche complète
tags: [vio, vi-slam, msckf, ekf, fej, fenêtre-glissante, calibration-en-ligne, décalage-temporel, landmarks-slam, simulateur, évaluation-ate-rpe-nees, euroc, open-source, filtre, piste-mote, quest-tracking]
---

# OpenVINS: A Research Platform for Visual-Inertial Estimation

**Référence :** Patrick Geneva, Kevin Eckenhoff, Woosik Lee, Yulin Yang, Guoquan Huang (2020). *OpenVINS: A Research Platform for Visual-Inertial Estimation.* Proc. IEEE International Conference on Robotics and Automation (ICRA 2020), Paris, pp. 4666–4672. DOI [10.1109/ICRA40945.2020.9196524](https://doi.org/10.1109/ICRA40945.2020.9196524) (venue, pages et DOI non imprimés dans le PDF auteur ; métadonnées de la base) · pas d'arXiv · PDF auteur : https://udel.edu/~pgeneva/downloads/papers/c10.pdf · code : https://github.com/rpng/open_vins · documentation : https://docs.openvins.com (`doc:194e432/tier:standard/page:1`). Robot Perception and Navigation Group (RPNG), University of Delaware ; financement partiel **Google ARCore** (`page:1`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Plateforme open source de VIO/VI-SLAM par **filtre de Kalman étendu sur variété à fenêtre glissante (MSCKF avec First-Estimates Jacobians)**, qui calibre en ligne intrinsèques, extrinsèques et décalage temporel caméra-IMU, garde des landmarks « SLAM » dans l'état, fournit un simulateur visuel-inertiel et une boîte à outils d'évaluation, et atteint sur EuRoC une ATE moyenne de 0,079 m (mono SLAM) / 0,054 m (stéréo SLAM), meilleure ou équivalente à OKVIS, VINS-Fusion, ROVIO, R-VIO, ICE-BA et S-MSCKF, seul Basalt faisant mieux en RPE stéréo (`page:1`, `page:6`).

## Problème traité
- Les VINS (fusion caméra + IMU) sont le moyen standard de localiser « mobile AR/VR » et robots, mais écrire un estimateur fiable à partir de zéro est difficile ; les bases de code ouvertes existantes (OKVIS, VINS-Fusion, Basalt, R-VIO, ROVIO, ICE-BA, S-MSCKF) « are not developed for extensibility and lack proper documentation and evaluation tools », avec « many hard-coded assumptions » liées à un capteur donné (`page:1`).
- Objectif : une base de code extensible pour chercheurs et praticiens, avec documentation et dérivations théoriques, qui serve de socle aux travaux du groupe (multi-caméras, multi-IMU, suivi d'objets mobiles, Schmidt-EKF SLAM, points-plans, points-lignes, LiDAR-inertiel-caméra) (`page:1`).
- Sous-problèmes techniques traités : gestion automatique de l'état et de la covariance (système de types), initialisation retardée des variables d'état, calibration spatio-temporelle en ligne pour les capteurs bas coût (latence, dérive d'horloge, délais de transmission), cohérence du filtre (FEJ), et validation en simulation Monte-Carlo puis sur données réelles (`page:2`, `page:3`, `page:4`).

## Méthode / contributions
### Estimateur : EKF modulaire sur variété
- **Vecteur d'état** (éq. 1–5) : état inertiel courant x_I (quaternion, position, vitesse, biais gyro et accéléro ; variété H × R¹², **15 DOF**), **c clones de poses IMU historiques** x_C (fenêtre glissante, « stochastic cloning »), **m landmarks** x_M, **w jeux de paramètres caméra** x_W (intrinsèques ζ : focale, centre, distorsion ; extrinsèques IMU→caméra) et **un décalage temporel unique** ᶜt_I entre horloge caméra et horloge IMU (caméras supposées synchronisées entre elles) (`page:2`).
- Opérations « boxplus/boxminus » pour rester sur la variété ; erreur de quaternion à gauche, mais tout autre paramétrage sur variété est possible (ex. invariant-EKF) (`page:2`).
- **Représentations de landmarks** : position 3D globale (par simplicité dans le papier), inverse-MSCKF, inverse depth complet, position 3D ancrée (`page:2`).
- **Propagation** : cinématique IMU non linéaire à chaque mesure inertielle (éq. 7–9) ; clones, landmarks et calibration n'évoluent pas → Jacobien identité et bruit nul, sparsité exploitée pour économiser du calcul (`page:2`).
- **Mise à jour sur variété** : EKF indirect linéarisé sur l'état d'erreur (éq. 10–17) (`page:2`).

### Plateforme
- **Système d'index par types** (inspiré de GTSAM) : chaque variable d'état connaît sa position dans la covariance, sa taille d'erreur et sa fonction `update` (boxplus) ; l'utilisateur construit des **Jacobiens creux** limités aux variables impliquées, ce qui réduit le calcul et les erreurs d'implémentation lors du clonage/marginalisation (`page:2`, `page:3`).
- **Initialisation de variables d'état** (ex. landmark SLAM) : décomposition QR par rotations de Givens de l'équation de mesure linéarisée en deux sous-systèmes, l'un dépendant du nouvel état (initialisation EKF, éq. 20–22, nécessite H_f1 de rang plein, donc **initialisation retardée**), l'autre non, traité comme une **mise à jour MSCKF avec projection sur le noyau** (`page:3`).
- **Modèle de mesure emboîté** h_d ∘ h_p ∘ h_t (distorsion, projection, transformation) : résidus calculés **sur les pixels bruts uv** pour permettre la calibration des intrinsèques, modèle de caméra interchangeable (radial-tangentiel, équidistant), Jacobiens par règle de chaîne (`page:3`).
- **Calibration en ligne spatio-temporelle** : Jacobiens supplémentaires par rapport à ζ, aux extrinsèques {ᶜ_I R, ᶜp_I} et au décalage ᴵt = ᶜt + ᶜt_I (éq. 27), motivée par les « low-cost devices » (« sensor latency, clock skew, or data transmission delays ») (`page:3`).
- **Landmarks SLAM** : « visual features that can be tracked beyond the current window, kept in the state vector, and marginalized out when lost » ; pas de carte persistante ni de fermeture de boucle dans l'estimateur évalué (`page:4`).
- **Documentation** présentée comme contribution à part entière : Doxygen + m.css, pages de dérivation couplées au code (`page:3`, `page:4`).
- **Trois modules** : *ov_core* (suivi de points épars 2D, triangulation linéaire et Gauss-Newton, simulateur pour un nombre arbitraire de caméras et de fréquences, maths sur variété), *ov_eval* (alignement de trajectoires, tracés précision/cohérence, évaluation Monte-Carlo, enregistrement de topics ROS), *ov_msckf* (estimateur EKF fenêtre glissante : FEJ, décalage temporel, calibration intrinsèque/extrinsèque, MSCKF standard, landmarks SLAM) (`page:1`).

### Simulateur visuel-inertiel
- **B-spline cubique SE(3)** (Patron-Perez 2015, Mueggler 2018) construite à partir d'une trajectoire de poses uniformément rééchantillonnée en points de contrôle ; pose, vitesse et accélération analytiques à tout instant (éq. 28–30) (`page:4`).
- Mesures inertielles dérivées de la spline (continuité C²) puis corrompues par biais à marche aléatoire et bruit blanc ; landmarks générés par rayons aléatoires avec profondeur aléatoire lorsque la caméra n'en voit pas assez, projetés dans les images futures (FOV, devant la caméra, distance bornée), bruit pixel ajouté (`page:4`).

### Protocole d'évaluation
- Simulation : mono, **fenêtre de 11**, ≤ 100 pistes par image, ≤ 50 landmarks SLAM dans l'état, caméra **10 Hz**, IMU **400 Hz**, bruit 1 px, bruits d'un IMU MEMS ADIS16448 ; calibration initiale tirée aléatoirement dans la distribution a priori ; **20 runs** Monte-Carlo (`page:4`).
- Réel : EuRoC MAV, scènes **Vicon room V1/V2** (stéréo 20 Hz, IMU ADIS16448 200 Hz, vérité terrain optimisée) ; vérité terrain de **V1_01 recalculée** (orientations d'origine incorrectes) et republiée ; **10 runs par algorithme et par séquence** ; **V2_03 exclue** (certains algorithmes ne tournent pas) ; seule la **partie VIO** des concurrents est évaluée (pas le pose graph de VINS-Fusion ni le mapping de Basalt) (`page:5`, `page:6`).

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| **Simulation — ATE / NEES** (20 runs) | calib. vraie avec calibration en ligne : 0,212° / 0,134 m, NEES ori 2,203 / pos 1,880 · calib. vraie sans : 0,200° / 0,128 m, NEES 2,265 / 1,909 · **calib. fausse avec calibration en ligne : 0,218° / 0,139 m, NEES 2,235 / 2,007** · calib. fausse sans : **5,432° / 508,719 m, NEES 9,159 / 1045,174** (« in many cases the estimate diverges ») | mono, fenêtre 11, cam 10 Hz, IMU 400 Hz, 1 px (`page:4`, `page:5`) |
| Convergence de la calibration | intrinsèques, extrinsèques et décalage temporel « rapidly converge from their initially poor guesses » dans les 10 à 60 premières secondes (figures 2 et 4, pas de valeur chiffrée) | `page:4`, `page:5` |
| **ATE EuRoC moyenne (°/m)** — OpenVINS | mono SLAM **1,445 / 0,079** · mono VIO 1,442 / 0,148 · stéréo SLAM 1,552 / **0,054** · stéréo VIO 1,454 / 0,055 | moyenne V1_01, V1_02, V1_03, V2_01, V2_02 ; 10 runs (`page:6`) |
| ATE EuRoC moyenne — concurrents | mono : OKVIS 1,911 / 0,154 · ROVIO(li) 2,054 / 0,140 · R-VIO 1,693 / 0,149 · VINS-Fusion VIO 2,926 / 0,104 ; stéréo : **Basalt 1,321 / 0,057** · ICE-BA 1,944 / 0,112 · OKVIS 1,744 / 0,081 · S-MSCKF 2,099 / 0,130 · VINS-Fusion VIO 2,383 / 0,084 | idem (`page:6`) |
| ATE par séquence (ov) | mono SLAM : V1_01 0,699°/0,058 m · V1_02 1,675/0,076 · **V1_03 2,542/0,063** · V2_01 0,773/0,124 · V2_02 1,538/0,074 ; mono VIO V1_03 2,391/**0,344** (le gain des landmarks SLAM en mono) ; stéréo SLAM V1_01 0,856/0,061 · V1_03 2,764/0,059 · V2_02 1,292/0,047 | `page:6` |
| **RPE (°/m) par longueur de segment** | mono ov SLAM : 8 m 0,661/0,074 → 48 m 1,289/0,122 (meilleur des monoculaires ; mono OKVIS 48 m 1,603/0,251, mono VINS-Fusion 1,860/0,171, ROVIO(li) 2,402/0,295) · stéréo ov VIO 0,722/0,068 → 1,489/0,106 ; stéréo ov SLAM 0,685/0,069 → 1,488/0,105 · **stéréo Basalt 0,538/0,063 → 0,758/0,111** (meilleur en orientation) | toutes séquences sauf V2_03 (`page:6`) |
| Dérive | pas de métrique de dérive en %, mais la RPE croît avec la longueur (ci-dessus) ; « the addition of SLAM landmarks in our OpenVINS greatly reduces the drift in the monocular case, while it has a smaller impact on the stereo performance » | `page:6` |
| **Temps de calcul** | V1_01 traité à **2,7× / 4,3× temps réel** (mono SLAM / mono VIO) et **1,2× / 1,9× temps réel** (stéréo SLAM / stéréo VIO), **mono-thread**, Intel Xeon E3-1505M v6 @ 3,00 GHz ; « we did not evaluate per-frame timing rigorously » ; Basalt « outperformed all other algorithms » en vitesse ; OpenVINS limité par le front-end OpenCV et par la mise à jour des landmarks SLAM | caméra 20 Hz → de l'ordre de 12 à 40 ms par image stéréo/mono selon la variante (ordre de grandeur déduit du facteur temps réel, non rapporté par les auteurs) (`page:6`) |
| Fréquence de sortie | non rapportée (propagation à la cadence IMU, mises à jour à la cadence caméra 20 Hz sur EuRoC, 10 Hz en simulation) | `page:2`, `page:4`, `page:5` |
| CPU / mémoire / énergie | non rapportés (hors facteur temps réel ci-dessus) | — |
| Matériel embarqué | non testé ; seulement un CPU laptop Xeon | `page:6` |
| **TUM-VI** | **non rapporté** (seul EuRoC est utilisé) | — |
| VINS-Mono | non évalué directement : représenté par « VINS-Fusion VIO », extension stéréo de VINS-Mono dont seule la partie odométrie est comparée | `page:5`, `page:6` |

## Ce que ça dit du tracking du Quest
- **Même famille d'estimateur, périmètre plus étroit.** Oculus Insight est un VI-SLAM à landmarks avec carte persistante, relocalisation et mises à jour de carte asynchrones (dossier [Insight](../../supports/meta2019_oculus-insight-quest/dossier.md)). OpenVINS est un **filtre MSCKF à fenêtre glissante** : les landmarks SLAM restent dans l'état tant qu'ils sont suivis puis sont **marginalisés** (`page:4`) ; il n'y a ni carte persistante, ni fermeture de boucle, ni relocalisation dans l'estimateur évalué (le pose graph est explicitement laissé à un module aval, `page:6`). Il modélise donc la **couche odométrique** du casque (l'équivalent de la trajectoire « open loop » d'Aria), pas sa couche carte.
- **Filiation documentée.** Le MSCKF de Mourikis et Roumeliotis [25] est la base d'OpenVINS (`page:1`, `page:3`) ; J. A. Hesch, nommé dans le dossier Insight comme responsable du tracking Quest, est co-auteur de la référence [30] (analyse comparative mono/binoculaire/stéréo VINS tightly-coupled avec Roumeliotis, `page:2`, `page:7`). C'est l'indice le plus concret dans la base que le casque relève de cette lignée « filtre type MSCKF », sans que Meta l'ait jamais confirmé.
- **Pose haute fréquence.** La propagation EKF à chaque mesure IMU (`page:2`) est le mécanisme qui donne une pose à la cadence IMU entre deux images ; Insight annonce une pose « every millisecond » plus une extrapolation amortie. OpenVINS n'implémente pas la prédiction vers le futur (non rapporté), seulement la propagation jusqu'à la dernière mesure.
- **Multi-caméras et calibration en ligne.** Le vecteur de calibration gère w caméras avec intrinsèques et extrinsèques propres et un décalage temporel unique (`page:2`) ; la version multi-caméras avec calibration en ligne est le travail [9] du même groupe (`page:1`) → voir [eckenhoff2019_multicam-vins](../eckenhoff2019_multicam-vins/fiche.md). Les quatre caméras monochromes du Quest relèvent de ce schéma ; la calibration en ligne variant dans le temps documentée pour Aria MPS est exactement ce que fait OpenVINS en continu.
- **Cohérence et FEJ.** Avec FEJ et calibration en ligne, le filtre reste cohérent même avec une calibration initiale fausse (NEES ≈ 2 contre 1045 sans, `page:5`). Pour mote, cela signifie qu'un casque bien conçu a une **covariance de pose exploitable** ; mais MRUK n'expose pas cette covariance (non rapporté ici, point ouvert côté Quest).
- **Implication pour la qualité des poses récupérées par mote.** Sur EuRoC (pièce Vicon de quelques mètres, trajectoires de dizaines de mètres), un filtre de cette famille donne une ATE de **5 à 8 cm** et une RPE position qui croît de ~7 cm à 8 m à ~11–12 cm à 48 m (`page:6`), hors relocalisation. Le SP-0 (4–6 mm médian vs COLMAP, pas de dérive visible) est bien meilleur, ce qui s'explique par la carte persistante et la relocalisation d'Insight que le filtre pur n'a pas, par la stéréo/multi-caméras, et par un protocole différent (erreur après alignement sur quelques dizaines de secondes). La comparaison plaide pour mesurer la RPE par longueur de segment sur mote, pas seulement une erreur médiane.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Représentant « filtre MSCKF sur variété » de l'axe SLAM/VIO ; formalisation complète de l'état (clones, landmarks, calibration, décalage temporel) et taxonomie des concurrents (smoothers à keyframes OKVIS/Basalt, optimisation VINS-Fusion, filtres R-VIO/ROVIO/S-MSCKF, BA incrémental ICE-BA) (`page:2`, `page:5`) |
| 2. Poses pour 3DGS (piste mote, H-01) | Donne l'ordre de grandeur d'erreur d'une odométrie VI sans carte : ATE 5–8 cm, RPE 7–12 cm, angles 0,7–2,8° selon la difficulté (`page:6`) ; souligne que la calibration (intrinsèques, extrinsèques, décalage temporel) fait partie de l'estimation et conditionne la pose caméra que mote reprojette ; les landmarks SLAM réduisent la dérive mono d'un facteur ~5 sur V1_03 (0,344 → 0,063 m) (`page:6`) |
| 3. Temps réel et contraintes embarquées | Filtre mono-thread à 1,2–4,3× temps réel sur un Xeon laptop, goulots = front-end OpenCV et mise à jour des landmarks SLAM (`page:6`) ; sparsité de la propagation et Jacobiens creux comme leviers (`page:2`, `page:3`) ; aucun résultat sur SoC mobile, GPU ou DSP |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole réutilisable : ATE et RPE par longueur de segment (8–48 m), NEES pour la cohérence, 10 runs par séquence pour la variabilité du front-end, vérité terrain V1_01 corrigée, outil *ov_eval* (alignement, tracés, Monte-Carlo) ; simulateur B-spline pour injecter des bruits contrôlés (`page:1`, `page:4`, `page:5`, `page:6`) |

## Pour (vis-à-vis de notre problématique)
- Code et documentation publics, dérivations détaillées : la meilleure entrée pour comprendre ce qu'un estimateur de type casque calcule réellement (état, propagation, mise à jour, marginalisation) (`page:1`, `page:3`).
- Résultats comparatifs sur huit systèmes ouverts, avec le même protocole (10 runs, VIO seul) : table de référence pour l'axe (`page:6`).
- Calibration en ligne du décalage caméra-IMU et des intrinsèques, démontrée consistante en simulation : répond directement aux inconnues de mote sur les intrinsèques de la caméra RGB et sa synchronisation avec l'horloge de tracking (`page:3`, `page:5`).
- *ov_eval* et le simulateur sont réutilisables tels quels pour évaluer les poses Quest (ATE/RPE) et pour fabriquer des trajectoires synthétiques à bruit connu (`page:1`, `page:4`).

## Contre / limites
- **Pas de temps par image mesuré rigoureusement**, pas de profil CPU/mémoire, pas de test embarqué : « we did not evaluate per-frame timing rigorously » (`page:6`).
- **Pas de carte persistante, de fermeture de boucle ni de relocalisation** : l'écart avec Insight est précisément là, et le papier ne dit rien de la relocalisation (`page:4`, `page:6`).
- Datasets : seules les cinq séquences Vicon room d'EuRoC (V2_03 exclue, Machine Hall absentes) ; **pas de TUM-VI** ni de données type casque (grand angle, 4 caméras, 1 kHz IMU) (`page:5`, `page:6`).
- Caméras supposées synchronisées entre elles (un seul décalage temporel) (`page:2`) ; les caméras asynchrones sont traitées ailleurs ([kuo2020_multicam-slam](../kuo2020_multicam-slam/fiche.md)).
- Pas de latence de sortie, pas de prédiction de pose, pas de covariance publiée pour les comparaisons réelles.
- Basalt reste meilleur en RPE orientation (0,758° vs 1,488° à 48 m) et en vitesse (`page:6`).

## Idées à creuser pour mote
- *Hypothèse* : utiliser *ov_eval* pour rejouer le SP-0 avec la métrique du papier (ATE après alignement + **RPE par longueur de segment** 1, 2, 4, 8 m) afin de distinguer bruit local et dérive sur les poses Quest, et comparer aux 7–12 cm d'une odométrie pure (`page:6`).
- *Hypothèse* : employer le **simulateur B-spline** pour générer une trajectoire de casque avec IMU et bruit pixel contrôlés, estimer avec OpenVINS, puis entraîner un 3DGS sur des images synthétiques avec ces poses bruitées : courbe « erreur de pose → PSNR » qui quantifierait la tolérance de H-01 sans dépendre du Quest (`page:4`).
- *Hypothèse* : estimer **hors ligne** le décalage temporel et les intrinsèques de la caméra passthrough RGB vis-à-vis des poses MRUK en reprenant le modèle h_d ∘ h_p ∘ h_t sur pixels bruts (`page:3`) ; c'est le même formalisme que la calibration en ligne du papier, appliqué à une caméra qui n'est pas celle du tracking.
- *Hypothèse* : faire tourner OpenVINS stéréo sur un enregistrement Aria ou sur un dataset type casque pour avoir une **baseline « filtre » reproductible** face aux poses Insight (qu'on ne peut pas instrumenter), à confronter aux smoothers ([usenko2020_basalt](../usenko2020_basalt/fiche.md), [qin2019_vins-fusion](../qin2019_vins-fusion/fiche.md)).
- *Hypothèse* : la marginalisation des landmarks SLAM (`page:4`) implique que les poses MRUK anciennes ne sont jamais corrigées rétroactivement ; pour mote, cela justifie le raffinement des poses à l'entraînement 3DGS (le volet « raffinement » de H-01) plutôt que d'attendre une correction côté casque.

## Citations clés
> « This codebase has out of the box support for commonly desired visual-inertial estimation features, which include: (i) on-manifold sliding window Kalman filter, (ii) online camera intrinsic and extrinsic calibration, (iii) camera to inertial sensor time offset calibration, (iv) SLAM landmarks with different representations and consistent First-Estimates Jacobian (FEJ) treatments, (v) modular type system for state management, (vi) extendable visual-inertial system simulator, and (vii) extensive toolbox for algorithm evaluation. » (`doc:194e432/tier:standard/page:1`)

> « We also co-estimate the time offset between the camera and IMU, which can commonly exist in low-cost devices due to sensor latency, clock skew, or data transmission delays. » (`doc:194e432/tier:standard/page:3`)

> « SLAM landmarks refer to the visual features that can be tracked beyond the current window, kept in the state vector, and marginalized out when lost. » (`doc:194e432/tier:standard/page:4`)

> « It is clear that the addition of SLAM landmarks in our OpenVINS greatly reduces the drift in the monocular case, while it has a smaller impact on the stereo performance; and more importantly, OpenVINS is able to perform competitively to other methods. » (`doc:194e432/tier:standard/page:6`)

> « On the first EurocMav dataset we could process at 2.7x/4.3x and 1.2x/1.9x realtime for our monocular SLAM/VIO, and stereo SLAM/VIO, respectively, on an Intel(R) Xeon(R) CPU E3-1505M v6 @ 3.00GHz processor in single threaded execution. » (`doc:194e432/tier:standard/page:6`)

## Liens
- Dossier casque : [Oculus Insight / Quest](../../supports/meta2019_oculus-insight-quest/dossier.md) — ce que le filtre modélise (odométrie) et ce qu'il ne modélise pas (carte persistante, relocalisation, DSP).
- Papiers liés :
  - [huang2019_vin-review](../huang2019_vin-review/fiche.md) — revue du même auteur (référence [1] du papier), cadre théorique filtre vs optimisation.
  - [eckenhoff2019_multicam-vins](../eckenhoff2019_multicam-vins/fiche.md) — extension multi-caméras avec calibration en ligne bâtie sur OpenVINS (réf. [9]).
  - [kuo2020_multicam-slam](../kuo2020_multicam-slam/fiche.md) — multi-caméras asynchrones, ce que le décalage temporel unique d'OpenVINS ne couvre pas.
  - [usenko2020_basalt](../usenko2020_basalt/fiche.md) — concurrent le plus fort du benchmark (RPE orientation, vitesse).
  - [qin2018_vins-mono](../qin2018_vins-mono/fiche.md) / [qin2019_vins-fusion](../qin2019_vins-fusion/fiche.md) — alternative optimisation par fenêtre glissante, comparée ici en mode VIO seul.
  - [campos2021_orb-slam3](../campos2021_orb-slam3/fiche.md) — la couche carte/relocalisation absente d'OpenVINS.
  - [rosinol2020_kimera](../rosinol2020_kimera/fiche.md) — autre plateforme ouverte (smoother + mapping).
  - [delmerico2018_vio-benchmark](../delmerico2018_vio-benchmark/fiche.md) — benchmark embarqué des mêmes familles d'estimateurs (ce qui manque ici : CPU/mémoire).
  - [suleiman2019_navion](../suleiman2019_navion/fiche.md) — accélérateur matériel d'un VIO, pour la question DSP/ASIC.
  - [nagy2020_faster-than-fast](../nagy2020_faster-than-fast/fiche.md) — front-end de points, goulot identifié par le papier.
  - [engel2023_project-aria](../engel2023_project-aria/fiche.md) — VIO embarqué Meta, calibration en ligne variant dans le temps (parallèle avec x_W).
  - [banaszczyk2024_vr-positioning-accuracy](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — précision mesurée des casques, à comparer aux ATE/RPE EuRoC.
  - [tosi2024_nerf-gs-slam-survey](../tosi2024_nerf-gs-slam-survey/fiche.md), [huang2024_photo-slam](../huang2024_photo-slam/fiche.md) — où un tel filtre se branche sur un 3DGS.
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) — consommateur des poses ; H-01 et raffinement des poses.
