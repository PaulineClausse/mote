---
citekey: eckenhoff2019_multicam-vins
mineru_doc: a895f80
type: conférence   # Proc. IEEE International Conference on Robotics and Automation (ICRA 2019), Montréal
statut: fiche complète
tags: [vio, vins, msckf, multi-caméras, asynchrone, calibration-en-ligne, décalage-temporel, intrinsèques, extrinsèques, interpolation-de-pose, clonage-stochastique, fisheye, drone, temps-réel, rpng-delaware, openvins, piste-mote]
---

# Multi-Camera Visual-Inertial Navigation with Online Intrinsic and Extrinsic Calibration

**Référence :** Kevin Eckenhoff, Patrick Geneva, Jesse Bloecker, Guoquan Huang (2019). *Multi-Camera Visual-Inertial Navigation with Online Intrinsic and Extrinsic Calibration.* Proc. IEEE International Conference on Robotics and Automation (ICRA 2019), Montréal, 7 p. DOI non imprimé dans le PDF auteur (IEEE Xplore : 10.1109/ICRA.2019.8793886, métadonnée de la base, à vérifier) · pas d'arXiv · PDF auteur : https://udel.edu/~pgeneva/downloads/papers/c07.pdf · **code : aucune URL dans le papier** (l'implémentation ouverte ultérieure du groupe est OpenVINS, voir [geneva2020_openvins](../geneva2020_openvins/fiche.md)) · version journal étendue : MIMC-VINS, IEEE T-RO 2021, **non ingérée**. Robot Perception and Navigation Group, University of Delaware ; financement partiel NSF, DTRA et **Google Daydream** (`doc:a895f80/tier:standard/page:1`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Extension du MSCKF à **un nombre arbitraire de caméras asynchrones, non recouvrantes et hétérogènes** : on ne clone dans l'état que les poses IMU aux instants d'une seule « caméra de base », les poses des autres caméras étant **interpolées linéairement sur SO(3)×R³** entre deux clones voisins en fonction d'un décalage temporel inconnu, ce qui permet d'estimer en ligne, pour chaque caméra, extrinsèques spatiales, décalage temporel et intrinsèques ; sur un drone à deux caméras (143 m, 3 étages) et un rig à trois caméras (440 m), l'erreur de fermeture passe de 0,48 % à 0,33 % et de 0,80 % à **0,14 %** de la trajectoire par rapport à la caméra de base seule, en temps réel (23–30 ms par mise à jour) (`page:1`, `page:5`, `page:6`).

## Problème traité
- La littérature VINS est centrée sur le cas minimal **une caméra + un IMU** ; fusionner **toutes** les caméras d'une plateforme améliore robustesse et précision mais augmente le coût de l'estimateur (`page:1`).
- Les extensions stéréo (Sun et al. [3], Paul et al. [13]) supposent un **recouvrement des champs de vue et un déclenchement synchrone**, ce qui ne s'étend pas à des caméras « plug-and-play » ; l'appariement gauche-droite couple le suivi visuel et empêche sa parallélisation ; la stéréo reste vulnérable aux scènes dynamiques et sans texture dans sa direction de vue (`page:2`).
- Houben et al. [16] (ORB-SLAM multi-caméras + IMU) supposent calibration connue et déclenchement simultané ; Paul et Roumeliotis [18] (stéréo alternée) interpolent les poses mais ne calibrent pas n ≥ 2 caméras dans le temps et l'espace (`page:2`).
- Les paramètres de calibration (extrinsèques spatiales, décalage temporel, intrinsèques) dégradent la localisation « if not catastrophically » s'ils sont faux ; la calibration hors ligne (Kalibr [19]) est fastidieuse, à refaire à chaque changement de configuration, et traiter ses valeurs comme parfaites introduit de l'inconsistance ; peu de systèmes calibrent en ligne le décalage temporel, et ceux qui le font se limitent à une paire caméra-IMU (`page:2`).

## Méthode / contributions
- **État** : état de navigation IMU standard (quaternion JPL, biais gyro et accéléro, vitesse, position) (éq. 1, `page:3`) ; **fenêtre de M clones de pose IMU aux seuls instants d'image de la caméra de base**, « as this greatly decreases the number of variables in our state » (éq. 5, `page:3`) ; par caméra i, un état de calibration x_ci = [extrinsèques C_i↔I (rotation + translation), décalage temporel ⁱt_b vers la caméra de base, intrinsèques ζ_i = (f_x, f_y, p_x, p_y, d_i)] où d_i est le vecteur de distorsion dépendant du modèle (radial-tangentiel ou fisheye) ; la caméra de base stocke son décalage ᵇt_I vers l'IMU (éq. 6–7, `page:3`).
- **Propagation IMU jusqu'à l'instant estimé de l'image** : l'horloge de la caméra de base diffère de celle de l'IMU par ᵇt_I (éq. 10) ; on propage l'IMU jusqu'à ᴵt̂_{k+1} = ᵇt_{k+1} + ᵇt̂_I (`page:3`).
- **Clonage stochastique avec décalage temporel** : la pose au vrai instant est écrite comme fonction de la pose à l'instant estimé et de l'erreur de décalage (position + v·δt, rotation ⊗ Exp(−ω·δt), éq. 12–13), ce qui donne les jacobiens par rapport à δᵇt_I (vitesse pour la position, vitesse angulaire débiaisée pour l'orientation) (`page:3`).
- **Front-end par caméra indépendant** : extraction uniforme FAST, suivi KLT « tracked independently for each camera's image stream », rejet RANSAC 8 points ; **aucun appariement inter-images** (`page:2`, `page:4`).
- **Mesures en coordonnées pixel brutes** (et non normalisées/non distordues) pour que le jacobien passe par la fonction de projection w_i(·, ζ_i) et permette la calibration des intrinsèques (éq. 15–16, `page:4`) ; mise à jour MSCKF classique par projection sur le noyau du jacobien de la feature, quand la piste atteint sa longueur max ou est perdue (éq. 17–19, `page:4`).
- **Mesures asynchrones** (Fig. 1) : l'instant ⁱt_k de la caméra i est ramené dans l'horloge de base (ᵇt_k = ⁱt_k + ⁱt_b), puis la pose est **interpolée linéairement** entre les clones ᵇt_1 et ᵇt_2 qui l'encadrent : rotation par Exp(λ·Log(R_2 R_1ᵀ))·R_1, position par (1−λ)p_1 + λp_2, avec λ fonction du décalage ⁱt_b (éq. 20–22). Hypothèse : vitesses linéaire et angulaire constantes sur l'intervalle, jugée bonne car la caméra de base tourne « around 20 Hz in most applications » et toute pose demandée est « within 25 milliseconds of a clone » ; les schémas d'ordre supérieur sont mentionnés mais écartés pour le coût (`page:4`).
- **Jacobiens de l'interpolation** par rapport aux deux clones et au décalage ⁱt_b via les jacobiens gauche/droit de SO(3) (éq. 23–28, dérivation dans un rapport technique [36]) : c'est ce qui rend **observable et estimable le décalage temporel de chaque caméra non-base** sans stocker ses poses (`page:5`).
- **Complexité** : les front-ends sont « independent » et peuvent tourner en parallèle, y compris en traitement « camera-edge » (un micro-calculateur ou un processeur embarqué par caméra qui envoie ses pistes à l'estimateur central) ; « The only introduced increase in computation is the possibly larger magnitude of features used during update », gérable par sélection d'un sous-ensemble de features (Fig. 2, `page:5`).

## Résultats chiffrés
| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| Matériel, exp. A (duo) | Snapdragon Flight (Qualcomm) sur quadrirotor 10 × 11 in, rotors 5 in ; 2 × Omnivision **OV7251 fisheye global shutter** (une avant, une vers le bas, **non recouvrantes**) à **30 Hz** ; IMU InvenSense **MPU-9250 à 500 Hz** ; résolution d'image non rapportée ; plateforme de calcul de l'estimateur non précisée | `page:5` |
| Trajectoire A | ≈ 143 m (« 140 meter » dans la légende de Fig. 3), Spencer Lab (UD), 1er → 3e étage par l'escalier et retour ; ≤ 250 features/image, fenêtre MSCKF 15, moyenne de 10 runs ; extrinsèques Kalibr perturbées à la main comme initialisation, intrinsèques non perturbées mais raffinées | `page:5`, `page:6` |
| ATE / RMSE | **non rapporté** (pas de vérité terrain) ; seule l'**erreur de fermeture début-fin** est mesurée | `page:5` |
| Erreur de fermeture A | mc-VINS 2 cam. **0,45 m (0,33 %)** ; caméra de base seule 0,65 m (0,48 %) ; 2 cam. **sans raffinement des intrinsèques 1,37 m (1,00 %)** | `page:5`, `page:6` |
| Temps par image A | suivi d'une image + mise à jour MSCKF toutes caméras = **0,023 s en moyenne (44 Hz)** pour des caméras à 30 Hz → temps réel | `page:6` |
| Matériel, exp. B (trio) | rig custom : **Pointgrey Blackfly** (une avant, deux fisheye inclinées en sens opposés ; une seule des deux caméras avant du rig utilisée, Fig. 5) + IMU **MTI-100** (fabricant non nommé) ; chaque caméra **asynchrone à 20 Hz** ; cadence IMU non rapportée | `page:6` |
| Trajectoire B | ≈ **440 m** en boucle fermée, plusieurs étages, Gore Hall (UD), **« poor lighting conditions »** ; fenêtre réduite à **12** pour rester temps réel ; moyenne de 10 runs | `page:6` |
| Erreur de fermeture B | mc-VINS 3 cam. **0,61 m (0,14 %)** ; caméra de base seule **3,58 m (0,80 %)** ; sans calibration des intrinsèques 0,49 m (Kalibr déjà très précis ici, pas de gain) | `page:6` |
| Temps par image B | suivi + mise à jour MSCKF = **0,03 s en moyenne** (≈ 33 Hz, caméras à 20 Hz) | `page:6` |
| Convergence de la calibration | extrinsèques et décalage caméra-IMU convergent « quickly » vers les valeurs Kalibr (Fig. 3 centre/droite, premières secondes) ; en B, initialisation à **> 20° et 0,2 m d'erreur** sur la transformation base-IMU, convergence tout de même | `page:5`, `page:6` |
| Dérive | non mesurée autrement que par la fermeture ; 0,14–0,33 % du chemin (multi-caméras) contre 0,48–0,80 % (mono) | `page:5`, `page:6` |
| CPU / mémoire | **non rapporté** (ni charge CPU, ni mémoire, ni plateforme d'exécution) | — |
| Fréquence de sortie | non rapportée séparément ; la mise à jour suit la cadence caméra (30 Hz ou 20 Hz) ; propagation IMU à 500 Hz en A | `page:5`, `page:6` |
| Passage à l'échelle (n > 3) | **non testé** : « In the future, we will increase the number of cameras to investigate the scaling properties of the system » | `page:6` |

## Ce que ça dit du tracking du Quest
- **Même famille d'estimateur que la lignée ARCore/Daydream.** Travail financé par Google Daydream (`page:1`), bâti sur le MSCKF de Mourikis-Roumeliotis et sur les travaux de Hesch et al. [7, 8] — le Joel Hesch qui co-signe ensuite le billet Meta décrivant Oculus Insight (dossier [Insight](../../supports/meta2019_oculus-insight-quest/dossier.md)). La formulation interne d'Insight n'est pas publiée, mais la **structure du problème** (quatre caméras monochromes grand angle à champs de vue peu recouvrants + un IMU à haute cadence, sur une puce mobile) est exactement celle que ce papier formalise.
- **Multi-caméras non recouvrantes, sans appariement inter-caméras.** Le papier montre qu'on peut fusionner des caméras qui ne voient pas la même chose, chacune suivie indépendamment et en parallèle, avec robustesse « to environmental conditions and single-camera failure » (`page:2`). C'est cohérent avec ce que Meta décrit : pyramides d'images « not computed at every frame or even for every camera », multithreading, opérations asynchrones et « Quest-specific DSP tuning » [Hesch 2019 ; Melim 2019]. Le traitement « camera-edge » proposé Fig. 2 (`page:5`) est la version académique d'un front-end par caméra déporté sur DSP.
- **Asynchronisme.** Le dossier Insight rapporte que les caméras avant du Quest alternent image par image entre mode visible (SLAM) et infrarouge (manettes) ; la cadence et la synchronisation des quatre caméras ne sont pas documentées. Si elles ne sont pas déclenchées au même instant, le mécanisme « une caméra de base clonée + interpolation des autres » est la façon standard de les fusionner sans multiplier les clones. Avec un IMU à 1 kHz et une propagation à chaque mesure, l'intervalle d'interpolation sur le Quest serait de l'ordre de la milliseconde contre 25 ms ici (`page:4`), donc l'approximation à vitesse constante y est bien meilleure.
- **Calibration en ligne.** Le papier estime en continu extrinsèques, décalage temporel **et** intrinsèques de chaque caméra, et quantifie le coût d'intrinsèques fausses : 0,33 % → 1,00 % de la trajectoire (`page:6`). Aria MPS publie une calibration en ligne variant dans le temps ([engel2023_project-aria](../engel2023_project-aria/fiche.md)) ; il est raisonnable de supposer (hypothèse, pas un fait publié) qu'Insight fait de même, ce qui expliquerait la stabilité des poses SP-0 malgré la déformation thermique et mécanique d'un casque.
- **Ce qui manque par rapport à Insight** : pas de carte persistante, pas de relocalisation, pas de fermeture de boucle, pas de prédiction de pose ; c'est un **odomètre** (couche « open loop » au sens d'Aria) qui dérive de 0,14–0,33 % du chemin (`page:5`, `page:6`). Le « pas de dérive visible » du SP-0 vient donc de la couche carte d'Insight, que ce papier ne modélise pas.
- **Implication directe pour mote** : la pose que MRUK attache à une image passthrough RGB est, structurellement, une pose de **caméra non-base** au sens de ce papier : pose IMU interpolée à l'instant d'exposition de la caméra RGB, transformée par les extrinsèques RGB↔IMU, avec un décalage d'horloge RGB↔tracking (points ouverts Q-03/Q-11 du SPEC mote). Les trois sources d'erreur sont donc exactement les trois paramètres que ce papier estime en ligne : ⁱt_b, (R, p)_{C_i↔I} et ζ_i (`page:3`). L'erreur de position induite par un décalage δt vaut v·δt (éq. 12, `page:3`) : à 0,5 m/s de vitesse de tête, 10 ms de décalage non compensé donnent 5 mm, soit l'ordre de grandeur du 4–6 mm médian du SP-0.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Formalisation de référence du **VIO multi-caméras asynchrone à filtre** : état avec un seul jeu de clones, interpolation SO(3)×R³, calibration en ligne complète ; lignée directe Roumeliotis → Hesch → Insight et Huang → OpenVINS ; définit le vocabulaire (caméra de base, clone, décalage temporel) à réutiliser dans la synthèse (`page:1`, `page:3`, `page:4`) |
| 2. Poses pour 3DGS (piste mote, H-01) | Donne le **modèle d'erreur** de la pose attachée à une caméra secondaire : v·δt pour le décalage temporel, ω·δt pour l'orientation (`page:3`), plus l'effet des intrinsèques (×3 d'erreur si non raffinées, `page:6`). Justifie un raffinement de poses **paramétré physiquement** (un δt et une transformation partagés par toutes les images) plutôt que 6 DoF libres par image |
| 3. Temps réel et contraintes embarquées | Front-ends parallélisables par caméra, « camera-edge » (`page:5`) ; chiffres de coût : 23 ms (2 cam., fenêtre 15) et 30 ms (3 cam., fenêtre 12) par mise à jour ; la fenêtre est **réduite** quand on ajoute une caméra pour tenir le temps réel (`page:6`). Pas de mesure CPU/mémoire ni de plateforme précisée |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole **sans vérité terrain** : erreur de fermeture début-fin en m et en % du chemin, moyenne de 10 runs, Kalibr comme pseudo-vérité pour la calibration, ablation mono/multi/sans-intrinsèques (`page:5`, `page:6`). Faible : pas d'ATE/RPE, pas de dataset public, pas de dérive en fonction de la distance |

## Pour (vis-à-vis de notre problématique)
- Seul papier de l'axe qui traite **explicitement** le cas « n caméras non synchronisées + IMU » avec calibration en ligne du décalage temporel de chaque caméra, c'est-à-dire la configuration du Quest (4 caméras) et le cas de la caméra RGB passthrough de mote.
- Chiffres d'ablation clairs sur le **gain de chaque caméra supplémentaire** (0,80 % → 0,14 % avec 3 caméras, `page:6`) et sur le **coût d'une mauvaise calibration** (0,33 % → 1,00 % sans intrinsèques, `page:6`) : deux ordres de grandeur utiles pour raisonner sur la qualité des poses Quest.
- Formules fermées (éq. 12–13, 20–22) réutilisables telles quelles pour interpoler/corriger des poses Quest à l'instant d'exposition d'une image RGB.
- Expériences réelles sur matériel embarqué de classe mobile (Snapdragon Flight, caméras OV7251 fisheye global shutter comparables en classe aux caméras de tracking d'un casque), en conditions difficiles (escaliers, faible éclairage) (`page:5`, `page:6`).
- Lignée directe vers OpenVINS (code ouvert) : la méthode est reproductible avec l'outil déjà fiché.

## Contre / limites
- **Pas de vérité terrain** : erreur de fermeture seulement, qui peut masquer des erreurs compensées en cours de trajectoire ; pas d'ATE/RPE, pas de jitter, pas de latence (`page:5`, `page:6`).
- Interpolation **linéaire à vitesse constante** sur jusqu'à 25 ms (`page:4`) : fausse lors de mouvements de tête rapides (rotations de plusieurs centaines de °/s en VR) ; les schémas d'ordre supérieur sont écartés sans être évalués.
- Caméras **global shutter** supposées ; le rolling shutter (cas probable de la caméra RGB passthrough) n'est pas traité (renvoi à [23] seulement, `page:2`).
- Seulement 2 et 3 caméras testées ; passage à 4+ laissé en travail futur (`page:6`) ; aucune mesure de charge CPU ou mémoire ; plateforme d'exécution non précisée.
- En B, la calibration en ligne des intrinsèques **n'apporte rien** quand Kalibr est bon (0,49 m sans vs 0,61 m avec, `page:6`) : elle ajoute des variables sans gain garanti.
- Pas de carte, pas de relocalisation : pur odomètre, non comparable au Quest sur les longues sessions.
- Rapport technique [36] cité pour les dérivations mais absent de la liste de références extraite (qui s'arrête à [35], `page:7`).

## Idées à creuser pour mote
- *Hypothèse (H-01, raffinement de poses)* : au lieu de laisser 6 DoF libres par image dans l'entraînement 3DGS, **paramétrer la correction** par (i) un décalage temporel δt RGB↔tracking unique, appliqué via p + v·δt et R·Exp(−ω·δt) (éq. 12–13, `page:3`) en utilisant les vitesses dérivées des poses Quest, (ii) une transformation extrinsèque RGB↔casque unique, (iii) des intrinsèques RGB raffinées. Trois petits jeux de paramètres partagés, bien conditionnés, au lieu de N × 6 DoF.
- *Hypothèse (mesure)* : estimer δt hors ligne en minimisant la reprojection de points COLMAP sur les poses Quest interpolées — version « batch » de ce que le filtre fait en ligne — et vérifier si le 4–6 mm du SP-0 contient une composante v·δt corrélée à la vitesse de tête.
- *Hypothèse (sélection d'images)* : rejeter ou sous-pondérer les images capturées à forte vitesse angulaire, où l'interpolation à vitesse constante et le flou dégradent à la fois la pose et la photométrie.
- *Hypothèse (évaluation sans vérité terrain)* : adopter l'erreur de fermeture début-fin en % du chemin comme métrique bon marché pour les captures mote (pas de robot ni OptiTrack nécessaires), en complément de la comparaison COLMAP du SP-0 et de la RPE par longueur de segment suggérée dans la fiche OpenVINS.
- *Hypothèse (intrinsèques)* : tester, comme le papier, l'entraînement 3DGS **avec et sans** raffinement des intrinsèques de la caméra passthrough ; si les intrinsèques d'usine sont bonnes, le gain sera nul (cas B) ; sinon il peut être du même ordre que l'écart ×3 observé en A.
- *Lecture à faire* : MIMC-VINS (T-RO 2021), version journal avec multi-IMU et passage à plus de caméras, pour les propriétés d'échelle non testées ici.

## Citations clés
> « we only clone the IMU poses related to a single "base camera" (rather than all cameras) in the state vector, while the IMU poses corresponding to all other camera images are represented via an interpolation of the poses bounding the measuring time. » (`doc:a895f80/tier:standard/page:1`)

> « We shall stress that in the proposed mc-VINS, we do not perform any cross-image matching, since we have non-overlapping images and instead allow each camera feed to be processed independently and in parallel. » (`doc:a895f80/tier:standard/page:2`)

> « As images of the base camera typically arrive at high rate (around 20 Hz in most applications) as compared to the physical camera motion, we argue that this serves as a good approximation. Due to the fact that marginalization is only ever performed on the oldest clone, any required camera pose will typically be within 25 milliseconds of a clone in the sliding window. » (`doc:a895f80/tier:standard/page:4`)

> « The only introduced increase in computation is the possibly larger magnitude of features used during update, which can be managed by careful selection of a subset of features to be processed. » (`doc:a895f80/tier:standard/page:5`)

> « the final position error was approximately 0.61 meters (0.14%). By contrast, the same dataset processed with the base camera alone yielded a final ending error of 3.58 meters (0.80%). This large increase in performance clearly validates our desire to include more cameras into the estimation process. » (`doc:a895f80/tier:standard/page:6`)

## Liens
- Papiers liés :
  - [OpenVINS](../geneva2020_openvins/fiche.md) — implémentation ouverte du même groupe qui reprend ce MSCKF avec calibration en ligne (mais un seul décalage temporel pour toutes les caméras) ; ce papier est sa référence [9] pour le multi-caméras.
  - [Kuo 2020](../kuo2020_multicam-slam/fiche.md) — l'autre approche multi-caméras de l'axe, côté optimisation/keyframes (SVO), testée de 2 à 6 caméras ; complémentaire sur la question de l'échelle non traitée ici.
  - [VINS-Mono](../qin2018_vins-mono/fiche.md) — référence [1] du papier, estimateur mono par optimisation ; [VINS-Fusion](../qin2019_vins-fusion/fiche.md) pour le stéréo synchrone.
  - [Huang 2019 (revue VIN)](../huang2019_vin-review/fiche.md) — revue du même auteur senior qui situe le MSCKF parmi les estimateurs.
  - [Project Aria](../engel2023_project-aria/fiche.md) — calibration en ligne variant dans le temps et trajectoires open/closed loop : ce que Meta publie de plus proche de l'usage de cette méthode dans un casque.
  - [Banaszczyk 2024](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — mesure boîte noire des poses Quest ; à lire avec le modèle d'erreur v·δt de ce papier.
  - [Basalt](../usenko2020_basalt/fiche.md), [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — estimateurs à optimisation avec carte/relocalisation, pour ce que l'odomètre pur de ce papier ne fait pas.
  - [Nagy 2020](../nagy2020_faster-than-fast/fiche.md) — front-end FAST embarqué, pertinent pour le traitement « camera-edge » proposé Fig. 2.
  - [Delmerico 2018](../delmerico2018_vio-benchmark/fiche.md) — benchmark des VIO sur plateformes embarquées (fiche à écrire).
  - [3DGS](../kerbl2023_3dgs/fiche.md) — consommateur des poses ; le raffinement paramétré proposé ci-dessus s'y branche.
- Dossier : [Oculus Insight](../../supports/meta2019_oculus-insight-quest/dossier.md).
