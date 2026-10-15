---
citekey: huang2019_vin-review
mineru_doc: e27584d
type: survey   # revue courte (preprint arXiv 1906.02650v1, 7 juin 2019 ; ICRA 2019 selon le brief ; le paper.md ne porte que l'en-tête arXiv)
statut: fiche complète
tags: [survey, vins, vio, vi-slam, msckf, ekf, fenêtre-glissante, lissage, pré-intégration, observabilité, consistance, fej, calibration-en-ligne, décalage-temporel, initialisation, couplage-serré, direct-vs-indirect, fermeture-de-boucle, carte-a-priori, mobile, localisation-poses, piste-mote]
---

# Visual-Inertial Navigation: A Concise Review

**Référence :** Guoquan (Paul) Huang (2019). *Visual-Inertial Navigation: A Concise Review.* Preprint arXiv [1906.02650](https://arxiv.org/abs/1906.02650) (v1, 6 juin 2019, 16 p. dont 8 de texte et 8 de bibliographie, 181 références) ; publié à ICRA 2019 selon le brief (la venue n'apparaît pas dans le paper.md, qui ne porte que « A PREPRINT - JUNE 7, 2019 »). Robot Perception and Navigation Group, University of Delaware (`doc:e27584d/tier:standard/page:1`). DOI : non rapporté. Code public : aucun (c'est une revue ; le papier ne donne aucune URL de dépôt, seules les URL d'ARCore, ARKit, Oculus et Tango figurent en bibliographie, `page:9`, `page:10`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Revue courte et dense, écrite par l'un des principaux auteurs de la famille MSCKF/OpenVINS, qui pose le vocabulaire des systèmes de navigation visuelle-inertielle (VINS) : modèle EKF canonique (IMU + caméra), puis taxonomie des estimateurs selon quatre axes (filtrage vs optimisation, couplage serré vs lâche, VIO vs SLAM, direct vs indirect), pré-intégration IMU, initialisation, calibration spatio-temporelle et analyse d'observabilité/consistance ; aucun chiffre de performance, mais une carte mentale indispensable pour lire les papiers ORB-SLAM, VINS-Mono, OpenVINS ou Basalt de la base (`page:1`, `page:2`, `page:8`).

## Problème traité
- Les IMU MEMS bon marché sont partout (mobiles, drones, AR/VR : ARCore, ARKit, Oculus cités comme applications), mais l'intégration simple de mesures bruitées et biaisées « often results in pose estimates unreliable for long-term navigation » ; une caméra, petite et peu gourmande, est « an idea[l] aiding source for INS », d'où les VINS (`page:1`).
- Difficulté de fond : « the lack of global information to reduce the motion drift accumulated over time (which is even exacerbated if low-cost, low-quality sensors are used) » (`page:1`).
- Constat bibliographique : il existe des revues SLAM générales (Cadena 2016, Bresson 2017) mais « no contemporary literature review of VINS » ; l'auteur veut (i) une revue concise mais complète centrée sur l'estimation d'état, (ii) sa lecture personnelle des travaux les plus importants, (iii) une liste de défis ouverts (`page:1`, `page:2`).

## Contenu / taxonomie
### 1. Modèle canonique EKF (section 2)
- État IMU + point 3D : quaternion {G}→{I}, biais gyro, vitesse, biais accéléro, position, position du point (éq. 1) ; dynamique continue (éq. 2) ; mesures gyro/accéléro avec biais, bruit blanc et gravité (éq. 3–4) ; **état d'erreur de dimension 18 × 1** avec erreur multiplicative sur le quaternion (représentation minimale 3 × 3 de l'incertitude d'attitude) (`page:2`).
- Propagation de la covariance par la matrice de transition discrète Φ, obtenue numériquement ou analytiquement, et bruit discret Q_d (éq. 7–11) (`page:3`).
- Mesure caméra = projection perspective du point exprimé dans le repère caméra via l'extrinsèque caméra–IMU {q, p} (éq. 12–13) ; « when the perfect calibration is unavailable, it is beneficial to VINS consistency to include these calibration parameters in the state vector » ; jacobiens (éq. 14–17) (`page:3`).

### 2. Filtrage vs optimisation (3.1)
- **MSCKF** (Mourikis & Roumeliotis 2007) : propagation par dynamique inertielle quaternion, mise à jour EKF ; les points ne sont **pas** dans l'état, leurs observations sont projetées sur le noyau du jacobien des points (marginalisation linéaire) pour ne garder que des contraintes entre poses caméra clonées stochastiquement. Avantage : pas de co-estimation de « potentially hundreds and thousands of point features » ; limite : « prevents the relinearization of the features' nonlinear measurements at later times » (`page:4`).
- Extensions MSCKF citées : OC-MSCKF (observabilité contrainte, consistance), **SR-ISWF** (racine carrée inverse, « to enable VINS running on mobile devices with limited resources while not sacrificing estimation accuracy »), OSC-EKF, filtre de Kalman invariant (consistance), EKF itéré robocentrique (ROVIO = Bloesch et al. [61, 62], R-VIO), points + lignes + plans, **rolling shutter avec horodatage imprécis**, RGBD, **multi-caméras** [53, 75, 76], multi-IMU [77] (`page:4`).
- Limite théorique commune au filtrage : « nonlinear measurements (12) must have a onetime linearization before processing, possibly introducing large linearization errors » (`page:4`).
- **Optimisation par lots** (BA) : réduit l'erreur par relinéarisation « but with high computational cost » ; graphe de facteurs incrémental (Indelman, iSAM) ; pour un temps constant, **fenêtre glissante** bornée + marginalisation des états passés ; **OKVIS** (Leutenegger 2015) = keyframes non séquentielles + états inertiels récents ; **VINS-Mono** (Qin 2018) = optimisation avec fermetures de boucle dans un thread non temps réel ; Schmidt-MSCKF [86] = fermetures de boucle en un seul thread à complexité linéaire (`page:4`).

### 3. Couplage serré vs lâche (3.2)
- Lâche : vision et inertiel traités séparément puis fusion de contraintes (PTAM + filtre, Weiss, Lynen MSF…) : « computationally efficient » mais « information loss » ; serré : fusion dans un seul processus, « thus achieving higher accuracy » (`page:4`, `page:5`).

### 4. VIO vs SLAM (3.3)
- VI-SLAM = points dans l'état (carte, fermetures de boucle, erreur bornée, coût plus élevé) ; VIO = « essentially odometry (dead reckoning) methods whose localization errors may grow unbounded unless some global information (e.g., GPS or a priori map) or constraints to previous locations (i.e., loop-closures) are used » (`page:5`).
- Architecture dominante à **deux threads** : fenêtre locale de keyframes (dérive court terme) + graphe de poses épars en arrière-plan (cohérence long terme) ; VINS-Mono suppose les poses de keyframes parfaites pour garder le problème petit (`page:5`).
- Fermeture de boucle = « one of the key differences between VIO and SLAM » ; difficulté : rester efficace sans « inconsistent assumptions such as treating keyframe poses to be true, or reusing information » ; solutions : estimateur hybride MSCKF + BA global déclenché par fermeture de boucle (le filtre attend le BA), **carte a priori compressée** (Lynen 2015), Cholesky-Schmidt EKF (DuToit 2017, carte avec incertitude complète), Schmidt-MSCKF (`page:5`).

### 5. Direct vs indirect (3.4)
- Indirect (points + reprojection ; ORB-SLAM2, MSCKF, OKVIS) ; direct (intensités ; LSD-SLAM, DSO, Stereo DSO, SVO semi-direct) ; direct + IMU : ROVIO (patchs, EKF itéré), Usenko 2016 (stéréo, pré-intégration discrète), Eckenhoff 2017 (`page:5`, `page:6`).
- Compromis : « direct image alignments require a good initial guess and high frame rate due to the photometric consistency assumption, indirect visual tracking consumes extra computational resources on extracting and matching features » ; l'indirect domine en pratique « due to its maturity and robustness », le direct « ha[s] potentials in textureless scenarios » (`page:6`).

### 6. Pré-intégration IMU (3.5)
- Lupton & Sukkarieh 2012 : intégration discrète dans un repère local, évite de ré-intégrer à chaque itération d'optimisation, mais singularités (angles d'Euler) ; Forster et al. 2015/2017 : sur la variété SO(3), sans singularité ; Shen 2015 : forme continue mais échantillonnée ; Eckenhoff/Geneva/Huang : **solutions fermées** des équations de pré-intégration (mesure et covariance), « improved accuracy over the discrete methods, especially in the case of highly dynamic motion » (`page:6`).

### 7. Initialisation (3.6)
- Souvent résolue en forme linéaire fermée (Martinelli : échelle, gravité, vitesse, biais) mais sans modéliser l'incertitude de la double intégration ; Faessler (SVO, capteur de distance pour l'échelle) ; **ORB-SLAM VI : initialiseur « high-latency (about 10 seconds) »** avec BA visuel-inertiel sur un jeu de keyframes ; méthodes linéaires sans biais gyro « may be unreliable in real world in particular when distant visual features are observed » (`page:6`).

### 8. Calibration des capteurs (section 4)
- Deux familles de paramètres : **spatiaux** (transformation rigide caméra–IMU) et **temporels** (décalage d'horloges dû au déclenchement matériel, aux délais de transmission et à la synchronisation : « will eventually lead to unstable or inaccurate state estimates ») (`page:6`).
- Hors ligne avec cibles : **Kalibr** (trajectoire B-spline en temps continu, extrinsèques + intrinsèques multi-capteurs) ; inconvénient : à refaire à chaque reconfiguration (`page:6`, `page:7`).
- En ligne : Kim 2018 (pré-intégration reformulée, sans temporel), **Li & Mourikis 2014 : spatial + temporel simultanés dans un filtre « for use on mobile devices »**, étendu aux intrinsèques caméra et IMU ; Qin & Shen 2018 : décalage temporel par interpolation des points sur le plan image ; Schneider 2019 : calibration « observability-aware » (mouvements informatifs) ; mouvements dégénérés (Yang 2019) ; question ouverte : « how to optimally model intrinsics and simultaneously calibrate them along with extrinsics » (`page:7`).

### 9. Observabilité et consistance (section 5)
- Observabilité ⇔ matrice d'observabilité inversible ⇔ information de Fisher ; étudier son noyau indique les directions non informées (`page:7`).
- Résultats analytiques : Martinelli → biais IMU, vitesse 3D, roulis et tangage globaux observables ; **Hesch et al. → le VINS monoculaire a 4 directions non observables : lacet global et position globale** ; extrinsèque caméra–IMU observable « given generic motions » ; caméra vers le bas sur plan horizontal → z global observable (`page:7`).
- Pour le système linéarisé (éq. 18) : noyau idéal de **4 directions** (translation globale + rotation autour de la gravité) ; or « the standard EKF linearized system … has an unobservable subspace of three, instead of four dimensions. This implies that the filter gains non-existent information from available measurements, leading to inconsistency » ; remèdes : **FEJ** (first-estimates Jacobian) adopté dans MSCKF, OC-VINS, R-VIO robocentrique (`page:7`, `page:8`).

### 10. Défis ouverts (section 6)
Localisation **persistante** (long terme, grande échelle, « in part due to resource constraints », intégration efficace des fermetures de boucle et de nouvelles cartes) ; features apprises et SLAM sémantique ; suivi d'objets mobiles ; VINS coopératif distribué ; autres capteurs d'aide (sonar, LiDAR léger, caméras événementielles) (`page:8`).

## Tableau récapitulatif : familles d'estimateurs
Les représentants « cités » sont ceux du papier (numéro de référence du papier) ; la colonne « dans la base, non cités » ajoute les systèmes postérieurs à 2019 que la revue ne pouvait pas connaître, pour relier aux fiches de l'axe localisation. Les compromis sont ceux énoncés par le papier, pas des mesures.

| Famille | Principe | Représentants cités (réf. papier) | Dans la base, non cités par le papier | Compromis précision / coût selon le papier | Pages |
|---|---|---|---|---|---|
| **Filtre EKF type MSCKF** (VIO, couplage serré, indirect) | poses clonées dans l'état, points marginalisés par projection sur le noyau, mise à jour EKF | MSCKF [18] ; OC-MSCKF [19, 38–40, 50–52] ; SR-ISWF mobile [6, 53] ; OSC-EKF [54, 55] ; stéréo pour vol rapide [43] ; « Project Tango [32] (or ARCore [12]) appears to use an EKF » | [OpenVINS](../geneva2020_openvins/fiche.md) (même groupe, successeur direct) ; [Navion](../suleiman2019_navion/fiche.md) (MSCKF sur ASIC) | coût faible (pas de co-estimation des points, « efficiency ») ; précision limitée par la linéarisation unique ; consistance à corriger (FEJ/OC) | `page:1`, `page:4`, `page:8` |
| **Filtres consistants / itérés / robocentriques** | filtre invariant (Lie), EKF itéré, repère robocentrique | IEKF [25, 56–60] ; ROVIO [61, 62] (direct par patchs, EKF itéré) ; R-VIO [22, 63] | — | consistance « independent of linearization points » ; ROVIO : robuste en faible texture mais nécessite bonne initialisation et cadence élevée (direct) | `page:4`, `page:5`, `page:6`, `page:8` |
| **Optimisation par fenêtre glissante** (keyframes + marginalisation) | moindres carrés non linéaires sur une fenêtre bornée, pré-intégration IMU | OKVIS [28] ; VINS-Mono [31, 100] ; Shen 2015 [85] ; Yang & Shen [84] ; Usenko 2016 direct stéréo [96] ; Ling [9] ; Eckenhoff direct [115] | [VINS-Fusion](../qin2019_vins-fusion/fiche.md) ; [Basalt](../usenko2020_basalt/fiche.md) ; [Kimera](../rosinol2020_kimera/fiche.md) | relinéarisation → erreur réduite, « but with high computational cost » ; fenêtre bornée pour un « constant processing time » | `page:4`, `page:6` |
| **Lissage incrémental / BA global** | graphe de facteurs complet ou incrémental (iSAM), BA | Indelman [27] ; iSAM/iSAM2 [81, 82] ; ORB-SLAM VI full BA [83] ; ICE-BA [99] ; maplab [101] | [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) | meilleure précision (relinéarisation complète, fermetures de boucle) ; coût le plus élevé, relégué au thread d'arrière-plan | `page:4`, `page:5` |
| **Hybrides et localisation sur carte a priori** | filtre temps réel + BA global ou carte compressée/Schmidt | double couche MSCKF + BA [109] ; Lynen « Get out of my lab » [110] ; Cholesky-Schmidt EKF [102] ; Schmidt-MSCKF [86] ; VINS-Mono 2 threads [31] | [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) (multi-cartes, relocalisation) ; Insight (voir section Quest) | erreur bornée grâce à la carte ; risque d'inconsistance si keyframes « treated as true », ou latence (« the filter waits for the BA to finish ») | `page:5` |
| **SLAM / VO purement visuels** (cités comme références) | indirect (ORB) ou direct (photométrique) sans IMU | ORB-SLAM/ORB-SLAM2 [83, 112] ; LSD-SLAM [114, 116, 117] ; DSO / Stereo DSO [118, 119] ; SVO [113] ; PTAM [87] | [ORB-SLAM](../murartal2015_orb-slam/fiche.md) ; [DROID-SLAM](../teed2021_droid-slam/fiche.md), [DPVO](../teed2023_dpvo/fiche.md) (appris, hors taxonomie 2019) | indirect : mature et robuste, coût d'extraction/appariement ; direct : plus d'information image, « potentials in textureless scenarios », exige bonne initialisation | `page:5`, `page:6` |

### Axes de la taxonomie (résumé)
| Axe | Option A | Option B | Verdict du papier | Page |
|---|---|---|---|---|
| Estimateur | filtrage (EKF/UKF, MSCKF) | optimisation (BA, fenêtre glissante, iSAM) | EKF « remain popular because of its efficiency » ; optimisation plus précise mais plus chère ; la pré-intégration a rendu l'optimisation viable en temps réel | `page:1`, `page:4` |
| Fusion | lâche | serrée | serrée « achieving higher accuracy » ; lâche efficace mais perte d'information | `page:4`, `page:5` |
| Carte | VIO (pas de points dans l'état) | VI-SLAM (points + fermetures de boucle) | SLAM : erreur bornée, coût plus élevé ; VIO : dérive non bornée sans information globale | `page:5` |
| Résidu visuel | indirect (points, reprojection) | direct (intensités) | indirect dominant (maturité, robustesse) ; direct prometteur en faible texture | `page:5`, `page:6` |

## Résultats chiffrés
Le papier est une revue : **aucune évaluation expérimentale, aucun tableau comparatif, aucune mesure de précision, de fréquence ou de coût**. Les seuls chiffres sont structurels.

| Métrique | Valeur | Conditions / page |
|---|---|---|
| ATE / RMSE des estimateurs | **non rapporté** (aucune comparaison quantitative ; le benchmark de Delmerico & Scaramuzza 2018 est cité [11] sans en reprendre les chiffres) | `page:9` |
| Dérive | non rapporté (qualitatif : VIO « may grow unbounded » sans information globale) | `page:5` |
| Fréquence (Hz), temps par image | non rapporté | — |
| CPU / mémoire / matériel | non rapporté ; mentions qualitatives : SR-ISWF « on mobile devices with limited resources », Li & Mourikis « for use on mobile devices », Tango/ARCore en EKF, VIO « on chip » [164] cité parmi les contraintes de ressources | `page:1`, `page:4`, `page:7`, `page:8` |
| Dimension de l'état d'erreur EKF canonique | **18 × 1** (attitude 3, biais gyro 3, vitesse 3, biais accéléro 3, position 3, point 3) | `page:2` |
| Directions non observables du VINS monoculaire | **4** (position globale 3 + lacet autour de la gravité 1) ; **3** seulement pour l'EKF standard linéarisé → inconsistance | `page:7`, `page:8` |
| Latence d'initialisation ORB-SLAM VI | « about 10 seconds » (BA visuel-inertiel sur un jeu de keyframes) | `page:6` |
| Degrés de liberté estimés | 6DOF (position + orientation) | `page:1` |
| Volume de la revue | 8 pages de texte (sections 1–6) + références [1]–[181] sur les pages 8–16 | `page:8`, `page:16` |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Fournit la grille de lecture (filtrage vs optimisation, VIO vs SLAM, carte a priori, calibration en ligne, consistance) avec laquelle classer Insight et les estimateurs ouverts de la base ; situe Tango/ARCore côté EKF et Oculus parmi les applications VR (`page:1`, `page:4`, `page:5`) |
| 2. Poses pour 3DGS (piste mote, H-01) | Explique **pourquoi** une pose VIO/VI-SLAM temps réel est métrique et alignée sur la gravité (biais, vitesse, roulis/tangage observables) mais arbitraire en position/lacet globaux (4 directions non observables), et pourquoi une estimation filtrée peut être légèrement biaisée et trop confiante (linéarisation unique, inconsistance) : c'est exactement ce que le raffinement de poses de H-01 doit corriger (`page:4`, `page:7`, `page:8`) |
| 3. Temps réel et contraintes embarquées (CPU/GPU/DSP) | Qualitatif seulement : l'EKF/MSCKF est la famille « efficace » retenue sur mobile (SR-ISWF, Tango), l'optimisation est plus précise mais plus chère ; la localisation persistante bute sur « resource constraints » (`page:1`, `page:4`, `page:8`) |
| 4. Évaluation (métriques, protocoles, datasets) | Rien de chiffré ; signale le benchmark VIO de Delmerico & Scaramuzza [11] et la notion de consistance (covariance vs erreur réelle) comme critère d'évaluation au-delà de l'ATE (`page:7`, `page:8`, `page:9`) |

## Ce que ça dit du tracking du Quest
- **Famille probable d'Insight** : d'après le [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md), le casque fait un VI-SLAM à landmarks avec carte persistante, relocalisation et mises à jour de carte asynchrones. Dans la taxonomie de Huang, cela correspond à la famille **« hybride / localisation sur carte »** (section 3.3) : un estimateur local temps réel (type MSCKF ou fenêtre glissante, Meta ne le dit pas) contraint par une carte de points et des fermetures de boucle, avec l'architecture à deux threads « local window + background global optimization » que le papier décrit comme dominante (`page:5`). La ressemblance avec Tango/ARCore (« appears to use an EKF ») et la mention explicite d'Oculus VR [14] parmi les applications des VINS vont dans ce sens, sans preuve (`page:1`).
- **Multi-caméras, 1 kHz, rolling shutter** : le papier liste comme extensions du MSCKF les systèmes multi-caméras [53, 75, 76], multi-IMU [77] et les caméras à obturateur roulant avec horodatage imprécis [64, 73] (`page:4`) ; la propagation IMU à haute cadence est le mécanisme standard (section 2.1) qui explique que la pose Insight soit calculée « every millisecond » entre deux images (`page:2`, `page:3`). Rien dans le papier ne traite du DSP ni de la répartition CPU/DSP.
- **Ce que la théorie prédit pour la pose MRUK récupérée par mote** :
  1. Elle est **métrique** (échelle, vitesse et biais observables grâce à l'IMU) et **alignée sur la gravité** (roulis/tangage observables) ; seules la position et le lacet globaux sont une jauge arbitraire, fixée par la carte persistante du casque (`page:7`). Pour un 3DGS, cette jauge n'a aucune importance : c'est la cohérence relative des poses qui compte, et la gravité connue est un bonus.
  2. Elle sort d'un estimateur qui **linéarise une seule fois** (si filtre) ou **suppose les keyframes exactes** pour rester temps réel (si fenêtre glissante avec fermetures de boucle) : erreurs d'approximation de l'ordre de quelques millimètres sont attendues, et la covariance interne est probablement optimiste (inconsistance) (`page:4`, `page:5`, `page:8`). Le SP-0 (4–6 mm / 0,3–0,5° en médiane contre COLMAP, sans dérive visible, mémoire du projet) est cohérent avec un SLAM à carte (erreur bornée) plutôt qu'avec un VIO pur (dérive non bornée, `page:5`).
  3. La **calibration spatio-temporelle** est le point faible que le papier met en avant : un décalage d'horloge entre capteurs « will eventually lead to unstable or inaccurate state estimates » (`page:6`). Pour mote, le risque n'est pas dans le tracking (calibré en usine et sans doute en ligne) mais dans la **transformation vers la caméra passthrough RGB** et la synchronisation de ses images avec l'horloge de tracking (questions Q-03/Q-11 du SPEC) : les méthodes de calibration temporelle en ligne de Li & Mourikis et de Qin & Shen (`page:7`) sont les références à adapter.

## Pour (vis-à-vis de notre problématique)
- Entrée pédagogique compacte (8 pages) : donne en une lecture le vocabulaire et les quatre axes de classification nécessaires pour lire toutes les autres fiches de l'axe localisation (`page:4`–`page:6`).
- Écrit par l'auteur de référence de la lignée MSCKF/OC/FEJ (Huang) : la section observabilité/consistance (`page:7`, `page:8`) est la synthèse la plus accessible de pourquoi un filtre VIO est « trop confiant », argument utile pour justifier le raffinement de poses de H-01.
- Insiste sur la calibration **temporelle** et sur le rolling shutter, deux risques concrets de la chaîne mote (`page:4`, `page:6`, `page:7`).
- Bibliographie de 181 entrées qui sert d'index : benchmark VIO [11], Kalibr [130, 134], VIO on chip [164], multi-caméras [76], Delmerico, Usenko, Qin… (`page:9`–`page:16`).

## Contre / limites
- **Aucun chiffre** : pas de comparaison ATE, fréquence, CPU ; la revue ne permet pas de choisir un estimateur, seulement de les classer (`page:1`–`page:8`).
- Datée de juin 2019 : ne couvre ni OpenVINS (2020), ni ORB-SLAM3 (2021), ni Basalt (2020), ni Kimera (2020), ni les méthodes apprises (DROID-SLAM, DPVO) ; Usenko n'est cité que pour son VIO direct stéréo de 2016 [96] (`page:13`).
- Forte autocitation (groupe de l'auteur : [22, 30, 35, 44, 46–49, 52, 54, 63, 71, 72, 76, 77, 86, 92, 105–108, 115, 141, 146–152, 165, 176]) ; la lecture est centrée sur la lignée filtrage/consistance, l'optimisation est traitée plus rapidement (`page:4`).
- Rien sur le matériel embarqué (DSP, SIMD, budget en ms), sur la latence ou sur la prédiction de pose, qui sont au cœur du tracking d'un casque.
- Mono-centrée : le stéréo et le multi-caméras sont mentionnés en une ligne (`page:4`).
- Quelques coquilles de l'OCR MinerU : « idea aiding source » (p. 1), éq. 15 mal reconstruite (`page:3`), « ewhere » (`page:3`) ; sans incidence.

## Idées à creuser pour mote
- *Hypothèse (H-01)* : formuler le raffinement de poses pendant l'entraînement 3DGS comme l'étape « BA global » d'un estimateur hybride (section 3.3) : la pose Quest est l'estimée filtrée, l'entraînement joue le rôle de relinéarisation ; on peut donc s'attendre à un gain de l'ordre de l'erreur de linéarisation (millimétrique), pas à une correction de dérive (`page:4`, `page:5`).
- *Hypothèse* : estimer **en ligne le décalage temporel** entre les horodatages de pose MRUK et les images RGB passthrough, par l'idée de Qin & Shen (interpolation des points sur le plan image, `page:7`) ou simplement par balayage du décalage qui minimise l'erreur de reprojection dans le 3DGS.
- *Hypothèse* : vérifier si la caméra passthrough est à obturateur roulant ; si oui, modéliser l'intra-image comme dans les extensions MSCKF rolling shutter [64, 73] (`page:4`), ou n'utiliser que les images prises en faible vitesse angulaire.
- *Protocole de capture* : éviter les **mouvements dégénérés** (rotation pure, translation constante) qui rendent la calibration et l'échelle mal observables (`page:7`) ; prévoir une phase d'excitation en début de capture, comme pour une initialisation VINS (`page:6`).
- *Évaluation* : ne pas se fier à une covariance éventuellement exposée par le casque (filtres inconsistants, `page:8`) ; conserver la mesure indépendante (SP-0 vs COLMAP, OptiTrack dans [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md)).
- *Positionnement* : utiliser les deux tableaux ci-dessus comme colonne « famille » dans la synthèse de l'axe localisation, puis y accrocher les chiffres de [Delmerico 2018](../delmerico2018_vio-benchmark/fiche.md).

## Citations clés
> « Among these, the EKF-based methods remain popular because of its efficiency. For example, as a state-of-the-art solution of VINS on mobile devices, Project Tango [32] (or ARCore [12]) appears to use an EKF to fuse the visual and inertial measurements for motion tracking. » (`doc:e27584d/tier:standard/page:1`)

> « While reducing the computational cost by removing the need to co-estimate potentially hundreds and thousands of point features, this operation prevents the relinearization of the features' nonlinear measurements at later times, yielding approximations deteriorating its performance. » (`doc:e27584d/tier:standard/page:4`)

> « However, VIO estimators are essentially odometry (dead reckoning) methods whose localization errors may grow unbounded unless some global information (e.g., GPS or a priori map) or constraints to previous locations (i.e., loop-closures) are used. » (`doc:e27584d/tier:standard/page:5`)

> « […] the timestamped sensing data of each sensor may disagree and thus, a timeline misalignment (time offset) between visual and inertial measurements might occur, which will eventually lead to unstable or inaccurate state estimates. » (`doc:e27584d/tier:standard/page:6`)

> « In particular, the standard EKF linearized system, which linearizes system and measurement functions at the current state estimate, has an unobservable subspace of three, instead of four dimensions. This implies that the filter gains non-existent information from available measurements, leading to inconsistency. » (`doc:e27584d/tier:standard/page:8`)

## Liens
- Dossier casque : [Oculus Insight / Quest 3](../../supports/meta2019_oculus-insight-quest/dossier.md) — à classer dans la famille « hybride / carte a priori » de cette revue.
- Papiers liés (axe localisation) :
  - [OpenVINS](../geneva2020_openvins/fiche.md) — successeur direct de la lignée MSCKF/FEJ décrite ici (même groupe), non cité (2020).
  - [VINS-Mono](../qin2018_vins-mono/fiche.md) — exemple du papier pour l'optimisation par fenêtre glissante à deux threads et la calibration temporelle (`page:4`, `page:5`, `page:7`) ; [VINS-Fusion](../qin2019_vins-fusion/fiche.md).
  - [ORB-SLAM](../murartal2015_orb-slam/fiche.md) — cité comme SLAM indirect de référence et pour l'initialiseur VI de ~10 s (`page:5`, `page:6`) ; [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) (non cité).
  - [Basalt](../usenko2020_basalt/fiche.md) — fenêtre glissante avec FEJ et marginalisation, héritier du VIO direct stéréo d'Usenko cité en [96] (`page:5`).
  - [Kimera](../rosinol2020_kimera/fiche.md) — lissage par graphe de facteurs (iSAM2, cité en [82]).
  - [Eckenhoff 2019 multi-caméras](../eckenhoff2019_multicam-vins/fiche.md) — réf. [76] du papier, calibration intrinsèque/extrinsèque en ligne (`page:4`) ; [Kuo 2020](../kuo2020_multicam-slam/fiche.md).
  - [Delmerico 2018](../delmerico2018_vio-benchmark/fiche.md) — réf. [11], les chiffres que cette revue ne donne pas ; [Navion](../suleiman2019_navion/fiche.md) — réf. [164] « VIO on chip » ; [Nagy 2020](../nagy2020_faster-than-fast/fiche.md).
  - [DROID-SLAM](../teed2021_droid-slam/fiche.md), [DPVO](../teed2023_dpvo/fiche.md) — méthodes apprises, hors du cadre 2019 (le papier ne cite l'apprentissage que comme défi ouvert, `page:8`).
  - [Project Aria](../engel2023_project-aria/fiche.md) — VIO embarqué Meta (open loop / closed loop), illustration moderne de la distinction VIO vs SLAM de la section 3.3.
  - [Tosi 2024](../tosi2024_nerf-gs-slam-survey/fiche.md), [Photo-SLAM](../huang2024_photo-slam/fiche.md) — jonction SLAM ↔ 3DGS.
  - [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — mesure indépendante de la précision des casques.
- Côté 3DGS : [3DGS](../kerbl2023_3dgs/fiche.md) (poses COLMAP que mote remplace), [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md), [VRSplat](../tu2025_vrsplat/fiche.md).
