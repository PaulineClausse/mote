---
citekey: kuo2020_multicam-slam
mineru_doc: 0704d9d
type: conférence   # IEEE ICRA 2020 (Paris), 7 p. ; preprint arXiv 2003.02014
statut: fiche complète
tags: [slam, vio, multi-caméra, rig-arbitraire, initialisation-adaptative, keyframe, entropie, fisher-information, voxel-map, voxel-hashing, euroc, autovision, svo, scaramuzza, oculus-quest, piste-mote]
---

# Redesigning SLAM for Arbitrary Multi-Camera Systems

**Référence :** Juichung Kuo, Manasi Muglikar, Zichao Zhang, Davide Scaramuzza (2020). *Redesigning SLAM for Arbitrary Multi-Camera Systems.* IEEE International Conference on Robotics and Automation (ICRA), Paris, 2020. arXiv [2003.02014](https://arxiv.org/abs/2003.02014) (v1, 4 mars 2020) · DOI non indiqué dans le preprint (à récupérer sur IEEE Xplore pour la version publiée) · Robotics and Perception Group, Univ. Zurich / ETH Zurich (rpg.ifi.uzh.ch) · vidéo : https://youtu.be/JGL4H93BiNw · **code public : non rapporté** (`doc:0704d9d/tier:standard/page:1`)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Pour qu'un VIO/SLAM à keyframes fonctionne sur **n'importe quel rig multi-caméras sans réglage spécifique**, les auteurs remplacent trois briques heuristiques du front-end par des mécanismes agnostiques au capteur — initialisation choisie en ligne par test de recouvrement des frustums, sélection de keyframes par **entropie de la pose (log-déterminant de l'information de Fisher)** à un seul paramètre, et carte **voxelisée (voxel hashing)** interrogée en échantillonnant les frustums — puis montrent sur un VIO type SVO que la même configuration tourne de 2 à 6 caméras, avec une précision égale ou meilleure qu'un pipeline stéréo soigneusement réglé sur EuRoC (`page:1`, `page:5`, `page:6`).

## Problème traité
- Ajouter des caméras à un SLAM améliore robustesse et précision (HDR, flou de bougé) et c'est déjà exploité industriellement : le papier cite explicitement **Oculus Quest** et Skydio comme exemples de produits multi-caméras (`page:1`). Mais le **front-end** (initialisation, sélection de keyframes, gestion de carte) est conçu par heuristiques « tailored for specific camera configurations » : ce qui marche pour une mono ou une paire stéréo très recouvrante devient compliqué quand les caméras ont des conditions de vue très différentes (`page:1`).
- Le back-end (bundle adjustment) se généralise naturellement à plusieurs capteurs « as long as the measurement process is modeled correctly » ; c'est le front-end qui est « much less theoretically grounded » (`page:1`).
- Trois sous-problèmes :
  1. **Initialisation** : mono = homographie / 5 points avec contrainte de mouvement (translation, pas de rotation pure) ; stéréo = triangulation directe ; multi-caméras = règles codées en dur (MCPTAM initialise chaque mono sur une cible connue ; Liu et al. 2018 utilise des paires stéréo prédéfinies) (`page:2`).
  2. **Sélection de keyframes** : heuristiques (nb d'images depuis la dernière keyframe, quantité de mouvement, nb/pourcentage de features suivies, flot optique, variation de luminosité) dont les seuils « varies greatly between different scenarios » (`page:2`). Les méthodes informationnelles sont rares : Das & Waslander 2015 (entropie des points pour le BA), DVO (ratio d'entropie de pose vs dernière keyframe) (`page:2`).
  3. **Requête de carte** : le test de covisibilité par keyframes a une complexité qui « increases quadratically » avec le nombre de caméras et introduit de la redondance quand les FoV se recouvrent ; « there is no previous study about efficiently querying map points in a general multi-camera setup » (`page:2`).

## Méthode / contributions
### 1. Initialisation adaptative par test de recouvrement (Section III, `page:2`–`page:3`)
- Hypothèses : intrinsèques et extrinsèques **connus** (calibrés). Aucune hypothèse codée en dur sur la disposition des caméras (`page:2`).
- Pour chaque paire ordonnée (C_i, C_j), i ≠ j parmi n caméras : échantillonnage uniforme de points U_i sur le plan image de i ; rétroprojection par π⁻¹ à deux profondeurs utilisateur d_min et d_max ; projection dans j via T_ij ; une projection est « réussie » seulement si **les deux** points (d_min et d_max) tombent dans l'image de j. La paire est stéréo si le ratio (projections réussies / échantillons) dépasse un seuil utilisateur (`page:3`, Fig. 2 `page:2`).
- Décision en ligne : s'il existe des paires stéréo → carte initiale par appariement stéréo ; sinon → algorithme 5 points **sur chaque caméra** en parallèle, carte initialisée dès qu'une caméra triangule avec succès (parallaxe suffisante, pas de forte rotation) (`page:2`, `page:3`).
- Point clé pour les rigs hétérogènes : la méthode passe par les fonctions de projection/rétroprojection génériques, donc elle trouve les paires stéréo « across different types of camera models » (pinhole, **fisheye**) sans calculer analytiquement l'intersection de frustums de formes très différentes ; le test peut être **précalculé hors ligne** (`page:3`). C'est ce que l'on entend par « adaptation automatique au rig » : il n'y a pas de modèle de caméra généralisé unique, mais une procédure qui ne dépend que de π, π⁻¹ et T_ij.

### 2. Sélection de keyframes par entropie négative de la pose (Section IV, `page:3`–`page:4`)
- Généralisation du concept de keyframe en **keyframe bundle** (toutes les caméras au même instant, comme MCPTAM) (`page:3`).
- Principe : une keyframe doit être insérée quand la carte locale ne suffit plus à localiser ; on mesure donc l'**incertitude de la pose courante par rapport à la carte locale**, en agrégeant les observations de toutes les caméras (`page:3`).
- Outil : dans la résolution NLLS (Gauss-Newton) du PnP, l'information de Fisher I_T = J_Tᵀ Σ_u⁻¹ J_T vient gratuitement ; la covariance est Σ_T = I_T⁻¹ (éq. 1–2) (`page:3`, `page:4`). L'entropie différentielle gaussienne ne dépend que de ln|Σ|, et ln|Σ_T| = −ln|I_T|, d'où le scalaire **E(T) ≜ ln|I_T|** (éq. 3), appelé « negative entropy », **sans inversion de matrice** (`page:4`).
- Multi-caméras « for free » : l'information (2) est une **somme sur les mesures individuelles**, donc les observations de toutes les caméras s'agrègent en un seul scalaire quel que soit le rig (`page:4`).
- Seuil **relatif** : la valeur absolue de E(T) varie d'un run à l'autre dans le même environnement (Fig. 3, `page:3`, `page:4`), donc un seuil absolu est « not feasible ». On suit E(T) par une moyenne glissante Ẽ(T) (Algo. 1, moyenne cumulative réinitialisée à chaque insertion de keyframe) et on insère une keyframe quand E(T) < r·Ẽ(T) ; r est **le seul paramètre** (r élevé → plus de keyframes) (`page:4`, Fig. 4 `page:3`).

### 3. Carte voxelisée et requête par échantillonnage de frustum (Section V, `page:4`)
- Carte = table de hachage de voxels (voxel hashing de Nießner et al. 2013), chaque voxel (taille utilisateur) contenant les points 3D du SLAM ; accès en **temps constant** via les coordonnées monde entières ; seuls les voxels non vides sont alloués ; synchronisée avec les points du pipeline (`page:4`).
- Requête : on échantillonne un **nombre fixe de points dans les frustums** des caméras, on récupère les voxels correspondants, et on apparie leurs points avec les nouvelles images. Garantie « all and only the 3D points within the FoVs of all cameras », sans test de keyframes recouvrantes (`page:4`). Méthode reprise de Muglikar et al., « Voxel map for visual SLAM », ICRA 2020 (`page:4`, `page:7`).
- La voxel-map ne sert **qu'à la requête des landmarks visibles** ; les keyframes restent nécessaires pour la triangulation et le BA (`page:4`).

### 4. Intégration
- Les trois briques sont greffées sur un VIO à keyframes « state-of-the-art » : front-end visuel efficace SVO (Forster et al. 2017, mono et multi-caméras) + back-end par optimisation type OKVIS (Leutenegger et al. 2015) (`page:4`, `page:7`). Nom et implémentation du pipeline complet non rapportés.
- Paramètres **identiques pour toutes les configurations de caméras** dans chaque expérience ; 5 runs par séquence ; protocole d'évaluation de Zhang & Scaramuzza 2018 (`page:5`).

## Résultats chiffrés
Les Fig. 6 et 7 sont des graphiques sans valeurs numériques dans le texte ; les valeurs marquées « ≈ » sont des **lectures graphiques** (incertitude ≈ ±0,2 ms, ±30 landmarks, ±100 pointeurs).

| Métrique | Valeur | Conditions (dataset, matériel) |
|---|---|---|
| Plage de rigs testés | **2 à 6 caméras** dans une même expérience, « without the need of sensor-specific modifications or tuning » | résumé (`page:1`) ; simulation 2–5 caméras, AutoVision jusqu'à FRB (`page:5`, `page:6`) |
| Configurations simulées (drone, trajectoire en 8) | 2 cam (mono avant + mono latérale) · 3 cam (stéréo avant + mono latérale) · 4 cam (stéréo avant + stéréo latérale) · 5 cam (+ mono vers le bas) ; **mono seule (avant ou latérale) perd le suivi** devant un pilier sans texture | Fig. 5 (`page:5`) |
| Précision vs nb de caméras (simulation) | Erreur relative de translation (boîtes sur 5 runs) : 2 cam ≈ 1,1 % de médiane à 5 m (valeurs extrêmes > 5 %) décroissant vers ≈ 0,6 % à 28 m ; **3, 4 et 5 cam ≈ 0,2–0,3 %** avec dispersion bien plus faible ; gain « marginal after the 3-camera configuration » car la 3e caméra forme la première paire stéréo (triangulation directe) | Fig. 6 (`page:5`), lecture graphique |
| **Temps front-end vs nb de caméras** (simulation) | Voxel-map : ≈ 3,4 ms (2 cam) · ≈ 5,3 ms (3) · ≈ 7,6 ms (4) · ≈ 7,4 ms (5) ; keyframe-map : ≈ 3,1 · ≈ 4,0 · ≈ 5,6 · ≈ 6,3 ms. Croissance à peu près linéaire de 2 à 4 cam ; quasi plateau 4→5 car la caméra vers le bas « did not produce as many landmarks » | Fig. 7 gauche (`page:5`), lecture graphique ; **CPU, fréquence d'horloge et résolution des images non rapportés** |
| Landmarks récupérés pour l'appariement | Voxel-map ≈ 210 / 500 / 790 / 800 (2→5 cam) vs keyframes ≈ 230 / 400 / 610 / 670 : la voxel-map en retrouve plus (points visibles absents des keyframes voisines) mais **coûte plus de temps front-end** dans cette implémentation | Fig. 7 milieu (`page:5`), lecture graphique |
| Mémoire (références vers landmarks) | Voxel-map ≈ 800 / 1 100 / 1 400 / 1 500 pointeurs vs keyframes ≈ 2 300 / 3 800 / 4 800 / 6 000 : la carte à keyframes stocke des copies redondantes des observations communes aux caméras, la voxel-map une seule référence | Fig. 7 droite (`page:5`), lecture graphique |
| ATE EuRoC, médiane du RMSE sur 5 runs (m) — stéréo, fenêtre de 10 keyframes | default-kf : 0,140 / 0,078 / 0,091 / 0,119 / 0,330 / 0,042 / 0,070 / 0,047 / 0,056 / 0,066 / 0,127 (MH01…V2 03) ; **e98-voxel : 0,095 / 0,074 / 0,088 / 0,128 / 0,180 / 0,039 / 0,053 / 0,041 / 0,046 / 0,057 / 0,111** ; e95-voxel : 0,078 / 0,084 / 0,093 / 0,182 / 0,237 / 0,040 / 0,047 / 0,049 / 0,056 / 0,087 / 0,171 ; e93-voxel : 0,104 / 0,390 / 0,107 / 0,177 / 0,262 / 0,038 / 0,036 / 0,043 / 0,080 / 0,103 / 0,169 | Table I (`page:6`) ; « no definite winner », pipeline adapté meilleur sur 10 séquences sur 11 en erreur d'odométrie, e98 le plus souvent (`page:5`) |
| Nombre moyen de keyframes EuRoC (5 runs) | default-kf : 64,0 / 57,8 / 91,4 / 76,0 / 70,2 / 70,6 / 119,6 / 238,8 / 74,8 / 172,0 / 281,4 ; e93 : 46,0 … 86,8 ; e95 : 71,2 / 66,0 / 87,0 / 74,4 / 75,8 / 76,4 / 86,8 / 160,0 / 39,8 / 85,0 / 107,8 ; e98 : 154,2 / 137,2 / 181,2 / 138,6 / 143,6 / 176,8 / 177,8 / 305,2 / 84,4 / 169,0 / 203,6 | Table II (`page:6`) ; e95 : « fewer keyframes … accuracy still similar » (`page:5`) |
| Agnosticisme capteur (front-end seul, sans back-end) | Keyframes moyennes sur MH01 / MH02 / V2 01 / V2 02 : heuristique mono 202,75 / 190,75 / 150,75 / 379,75 vs heuristique stéréo 90,00 / 117,25 / 84,75 / 204,5 ; **entropie mono 129,5 / 128,25 / 100,00 / 193,5 vs entropie stéréo 122,25 / 125,25 / 98,5 / 195** (quasi identiques) | Table III (`page:6`) |
| AutoVision Science Park (jour), voiture, trajectoire 547,488 m (légende) / 547,448 m (texte), vitesse max 3,941 m/s | ATE (m) : F 1,184 · FR 2,366 · FRB 1,766 ; erreur rel. translation @200 m : 0,582 / 1,808 / 1,320 % ; @400 m : 0,642 / 1,07 / 0,760 % — **plus de caméras n'améliore pas** ici, extrinsèques suspectées inexactes (idem chez Liu et al. 2018) | Table IV, Fig. 9 (`page:6`) ; signification de F/FR/FRB non définie dans le papier (notation reprise de Liu et al. 2018) |
| Fréquence (Hz) du pipeline complet | non rapporté | — |
| Latence, CPU utilisé, mémoire totale, consommation | non rapporté (seuls temps front-end et nb de pointeurs en simulation) | — |
| Relocalisation / fermeture de boucle | non traité (VIO à fenêtre glissante) | — |

## Ce que ça dit du tracking du Quest
- **Le papier nomme le Quest comme archétype du SLAM multi-caméras** : « adding more cameras in SLAM systems proves to be effective and is already exploited in successful commercial products, such as Oculus Quest [4] and Skydio [5] » (`page:1`) ; la Fig. 1 montre un casque VR parmi les trois applications (`page:1`). Il confirme donc de l'extérieur que le casque est un VI-SLAM multi-caméras à keyframes, mais n'apporte aucune information interne sur Insight.
- **Ressemblances structurelles avec ce qu'on sait d'Insight** ([dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md)) : rig de 4 caméras **grand angle** (fisheye) peu ou partiellement recouvrantes + IMU ; VIO à keyframes/landmarks ; back-end par optimisation. Le test de recouvrement de Kuo et al. est exactement l'outil qui décide, pour un rig comme celui du Quest 3 (2 caméras frontales dans les « pills », 2 en bas à gauche/droite), **quelles paires sont stéréo** (triangulation immédiate, profondeur métrique) et lesquelles ne le sont pas (initialisation 5 points, échelle par l'IMU) ; la précalculabilité hors ligne (`page:3`) correspond à un rig fixe calibré en usine.
- **Ce qui diffère** : Insight entretient une **carte persistante** avec relocalisation et reconnaissance de lieu, une prédiction à 1 kHz et du DSP ; le pipeline de Kuo et al. est un **VIO à fenêtre glissante (10 keyframes)** sans fermeture de boucle ni relocalisation (`page:5`), sans prédiction ni contraintes embarquées évaluées. La voxel-map est toutefois une structure de carte **persistante et interrogeable en O(1)** par position, ce qui ressemble davantage à une carte de landmarks de casque qu'à un graphe de covisibilité type ORB-SLAM.
- **Implication pour la qualité des poses que mote récupère** : (i) le gain de précision en passant de 2 à 3 caméras vient de la **première paire stéréo** (`page:5`) ; avec 4 caméras et un recouvrement partiel, le Quest est probablement dans le régime « ≥ 3 caméras » de la Fig. 6 (erreur relative ≈ 0,2–0,3 % en simulation, dispersion faible), ce qui est cohérent avec les 4–6 mm / 0,3–0,5° médians mesurés en SP-0 ; (ii) le papier montre aussi que la précision **ne croît pas automatiquement avec le nombre de caméras si les extrinsèques sont imprécises** (`page:6`), donc la qualité de la calibration d'usine (et sa dérive thermique/mécanique, non traitée ici) borne ce que mote peut espérer ; (iii) la redondance des observations entre caméras recouvrantes (`page:5`) explique pourquoi un casque est robuste aux zones sans texture là où une mono perd le suivi (`page:5`).

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Formalise les trois briques du front-end qu'un SLAM multi-caméras de casque doit résoudre (initialisation par paires stéréo, insertion de keyframes, requête de carte) et cite le Quest comme cas d'usage (`page:1`, `page:2`) ; revue courte des critères de keyframes d'ORB-SLAM, DSO, SVO, VINS-Mono (`page:2`) |
| 2. Poses pour 3DGS (piste mote, H-01) | Le critère d'entropie E(T) = ln\|I_T\| est une **mesure de confiance de pose** directement calculable à partir du PnP (`page:4`) : transposable à mote pour pondérer ou filtrer les images selon la qualité de localisation avant l'entraînement 3DGS, et pour choisir les keyframes à envoyer au PC (moins redondantes qu'un seuil de distance). Montre que 3+ caméras donnent des poses relatives ≈ 0,2–0,3 % (`page:5`), ordre de grandeur compatible avec H-01 |
| 3. Temps réel et contraintes embarquées (CPU/GPU/DSP) | Seule mesure : temps front-end ≈ 3–8 ms de 2 à 5 caméras (`page:5`), croissance quasi linéaire avec le nombre de landmarks plutôt qu'avec le nombre de caméras ; **matériel non rapporté**, pas de GPU/DSP, pas de pipeline complet chronométré. Pas exploitable comme référence embarquée, mais donne la tendance « coût ∝ landmarks observés » |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole de Zhang & Scaramuzza 2018 (ATE RMSE médian sur 5 runs + erreur relative par distance parcourue, boîtes à moustaches) (`page:5`) ; EuRoC 11 séquences, AutoVision Science Park ; comparaison par nb de keyframes (Tables II–III) comme indicateur de redondance (`page:6`). Modèle pour notre protocole SP-0/SP-1 : rapporter l'erreur relative **par distance parcourue** en plus de l'ATE |

## Pour (vis-à-vis de notre problématique)
- Seul papier de l'axe qui traite explicitement du **passage de 2 à n caméras arbitraires** avec les mêmes paramètres, et qui chiffre précision et coût en fonction du nombre de caméras (`page:5`).
- Critère de keyframe **à un seul paramètre**, agnostique au capteur, fondé sur l'information de Fisher déjà disponible : résultats similaires ou meilleurs qu'un pipeline stéréo réglé à la main (10/11 séquences en odométrie, e98) (`page:5`, `page:6`) avec moins de keyframes à r = 95 % (`page:5`).
- Test de recouvrement générique **pinhole/fisheye** et précalculable (`page:3`) : directement applicable à un rig de caméras grand angle de casque.
- Voxel-map : mémoire croissant lentement avec le nombre de caméras (≈ 1 500 vs ≈ 6 000 pointeurs à 5 cam) (`page:5`), structure proche d'une carte persistante.
- Expérimentation honnête : cas où plus de caméras n'aide pas (AutoVision) attribué aux extrinsèques (`page:6`).

## Contre / limites
- **Aucune information matérielle** (CPU, résolution, fréquence caméra) ni mesure du pipeline complet, de la latence ou de l'énergie ; les temps front-end sont en simulation uniquement (`page:5`). Inutilisable pour dimensionner un système embarqué.
- Pas de code public mentionné ; pipeline décrit par références (SVO + back-end type OKVIS) (`page:4`).
- Voxel-map **plus lente** que les keyframes dans l'implémentation testée (≈ 7,6 vs ≈ 5,6 ms à 4 cam) ; les auteurs « assume that it can be further reduced » sans le démontrer (`page:5`).
- Résultats EuRoC uniquement en **stéréo** (2 caméras) ; les configurations à 3–5 caméras ne sont évaluées qu'en simulation (vérité terrain parfaite, pas de HDR ni de flou), et AutoVision ne montre pas d'amélioration avec plus de caméras (`page:5`, `page:6`).
- Variance notable entre seuils : e93 donne 0,390 m sur MH02 contre 0,078 pour la référence (`page:6`), donc le « seul paramètre » reste sensible.
- Initialisation : nécessite extrinsèques/intrinsèques calibrés et bornes de profondeur d_min/d_max fournies par l'utilisateur (`page:3`) ; pas d'estimation en ligne de la calibration.
- Pas de relocalisation, de fermeture de boucle ni de carte persistante multi-sessions : on est loin du périmètre fonctionnel d'Insight.
- Incohérence mineure : longueur de trajectoire 547,488 m (légende Table IV) vs 547,448 m (texte) (`page:6`).

## Idées à creuser pour mote
- *Hypothèse (H-01, sélection d'images)* : calculer sur PC un E(T) approché pour chaque image RGB reçue du Quest (PnP de l'image contre le nuage 3DGS courant ou contre les points triangulés), et n'insérer dans l'entraînement que les images dont E(T) < r·Ẽ(T), c'est-à-dire celles qui apportent de l'information nouvelle ; comparer le nombre d'images retenues et le PSNR final à une sélection par distance/angle (comme `page:5`–`page:6` comparent nb de keyframes et ATE).
- *Hypothèse (raffinement des poses)* : utiliser ln|I_T| (information de Fisher du PnP) comme **poids par image** dans le raffinement des poses à l'entraînement 3DGS : images bien localisées = poses figées, images à faible E(T) = poses libres.
- *Hypothèse (protocole SP-1)* : ajouter à l'évaluation Quest vs COLMAP l'erreur relative de translation **par distance parcourue** (5/11/17/23/28 m comme Fig. 6 `page:5`), pour distinguer dérive et bruit local.
- *Hypothèse (rig du Quest)* : appliquer le test de recouvrement (`page:3`) aux extrinsèques des 4 caméras de tracking et des 2 caméras RGB du Quest 3 (si MRUK les expose) pour savoir quelles paires sont stéréo et à quelle plage de profondeur ; cela renseigne la Q-03/Q-11 du SPEC mote (intrinsèques, géométrie du rig).
- *Hypothèse (carte voxel)* : réutiliser l'idée de voxel hashing pour indexer les Gaussiennes par position et ne charger, à chaque nouvelle image, que les voxels dans le frustum (requête O(1) par voxel, `page:4`) — pont entre carte SLAM et structure de rendu.

## Citations clés
> « Adding more cameras to SLAM systems improves robustness and accuracy but complicates the design of the visual front-end significantly. Thus, most systems in the literature are tailored for specific camera configurations. » (`doc:0704d9d/tier:standard/page:1`)

> « adding more cameras in SLAM systems proves to be effective and is already exploited in successful commercial products, such as Oculus Quest [4] and Skydio [5]. » (`doc:0704d9d/tier:standard/page:1`)

> « Since that the Fisher information I_T comes for free in the process of solving NLLS problems, we can actually avoid the matrix inversion and use E(T) ≜ ln(|I_T|) to indicate how well the camera can localize in the current map. » (`doc:0704d9d/tier:standard/page:4`)

> « Adding more cameras to the system improved the trajectory estimation accuracy, but the improvement became marginal after the 3-camera configuration. This is because adding the third camera formed a stereo pair (front stereo) compared with the 2-camera configuration, which made direct triangulation possible. » (`doc:0704d9d/tier:standard/page:5`)

> « we indeed observed that the accuracy of the trajectory estimates does not necessarily increase as we add more cameras to the pipeline. We suspect that the reason to be the inaccurate extrinsic » (`doc:0704d9d/tier:standard/page:6`)

## Liens
- Dossier Insight : [meta2019_oculus-insight-quest](../../supports/meta2019_oculus-insight-quest/dossier.md) — le Quest cité comme produit multi-caméras (`page:1`).
- Papiers liés :
  - [ORB-SLAM](../murartal2015_orb-slam/fiche.md) — critères heuristiques de keyframes et covisibilité pris comme contre-exemples (`page:2`).
  - [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — multi-cartes et relocalisation absentes ici ; comparaison des stratégies de keyframes.
  - [VINS-Mono](../qin2018_vins-mono/fiche.md) — cité pour le critère « nombre de features suivies » (`page:2`) ; [VINS-Fusion](../qin2019_vins-fusion/fiche.md) — stéréo/multi-capteurs.
  - [Multi-camera VINS (Eckenhoff 2019)](../eckenhoff2019_multicam-vins/fiche.md) — approche filtre (MSCKF) du même problème multi-caméras, à comparer au front-end par optimisation ici.
  - [OpenVINS](../geneva2020_openvins/fiche.md), [Basalt](../usenko2020_basalt/fiche.md), [Kimera](../rosinol2020_kimera/fiche.md) — estimateurs ouverts auxquels greffer les trois briques.
  - [Faster than FAST (Nagy 2020)](../nagy2020_faster-than-fast/fiche.md) — même groupe RPG, coût du front-end sur GPU embarqué, complément à l'absence de chiffres matériels ici.
  - [VIO benchmark (Delmerico 2018)](../delmerico2018_vio-benchmark/fiche.md), [Huang 2019 VIN review](../huang2019_vin-review/fiche.md) — protocole d'évaluation (Zhang & Scaramuzza 2018 réutilisé `page:5`) et panorama.
  - [Project Aria (Engel 2023)](../engel2023_project-aria/fiche.md) — rig Meta 2 caméras SLAM + 2 IMU, le plus proche du Quest dans la base.
  - [VR positioning accuracy (Banaszczyk 2024)](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — mesures externes de précision du tracking de casque, à rapprocher de la Fig. 6.
  - [3DGS](../kerbl2023_3dgs/fiche.md), [Taming 3DGS](../mallick2024_taming-3dgs/fiche.md) — consommateurs des poses ; [Photo-SLAM](../huang2024_photo-slam/fiche.md), [NeRF/GS-SLAM survey](../tosi2024_nerf-gs-slam-survey/fiche.md) — SLAM couplé au rendu.
