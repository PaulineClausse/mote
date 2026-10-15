---
citekey: banaszczyk2024_vr-positioning-accuracy
mineru_doc: 5a3002b
type: prépublication (arXiv) — venue non indiquée dans le texte (mise en page type IEEE VR)
statut: fiche complète
tags: [meta-quest-2, meta-quest-pro, oculus-insight, précision-de-pose, vérité-terrain, optitrack, mocap, robot-ur5e, hand-eye, ape, ate, evo, benchmark, inside-out, piste-mote, synchronisation-temporelle]
---

# How Accurate is the Positioning in VR? Using Motion Capture and Robotics to Compare Positioning Capabilities of Popular VR Headsets

**Référence :** Adam Banaszczyk, Mikołaj Łysakowski, Michał R. Nowicki, Piotr Skrzypczyński (Poznan University of Technology), Sławomir K. Tadeja (University of Cambridge) (2024). *How Accurate is the Positioning in VR? Using Motion Capture and Robotics to Compare Positioning Capabilities of Popular VR Headsets.* arXiv [2412.06116](https://arxiv.org/abs/2412.06116) v1 [cs.RO], 9 décembre 2024, 8 p. ; venue non indiquée dans le texte ; DOI non rapporté · code, données et procédure : [github.com/AdamBanaszczyk/head_trajectory](https://github.com/AdamBanaszczyk/head_trajectory) (`doc:5a3002b/tier:standard/page:1`) · financement : « unrestricted gift by Meta » (`page:7`)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Banc de mesure **boîte noire** de la précision de position des casques Meta : une trajectoire de tête réelle (joueur assis, enregistrée par OptiTrack à 120 Hz) est rejouée par un bras UR5e portant un buste mannequin + casque, et la pose « Center Eye Anchor » loggée par Unity à 30 Hz est comparée à la pose du robot par l'APE/ATE d'evo ; **Quest 2 et Quest Pro** (pas de Quest 3) donnent un RMSE de translation de **2,3–5,3 mm** (max ≈ 8–13 mm) sur une partie de 2 min, sans différence significative entre les deux, **sans aucune mesure d'orientation, de jitter ni de latence** (`page:1`, `page:6`).

## Problème traité
- Les casques grand public (Meta) localisent par **tracking inside-out visuel** (odométrie visuelle + SLAM), coûteux en calcul et fragile en cas de textures répétitives, de mouvements rapides ou d'occultations ; or « comprehensive evaluations of the latest VR headsets using standardized testing methods for inside-out visual tracking are lacking » (`page:1`).
- Les évaluations antérieures portaient sur des systèmes outside-in (HTC Vive, refs [16, 22]) ; ici il s'agit de mesurer la précision **absolue** d'un casque inside-out contre une vérité terrain externe, de façon **reproductible** (même trajectoire physique rejouée pour chaque casque) (`page:1`).
- Contributions annoncées : (i) comparaison Quest Pro vs Quest 2 ; (ii) analyse des forces/faiblesses du tracking ; (iii) méthodologie reproductible « headset-agnostic » avec ROS, OptiTrack portable et cobot (`page:1`).

## Méthode / contributions
Chaîne en trois modules (Fig. 2, `page:2`) :
1. **Acquisition de trajectoires réelles** : 6 caméras OptiTrack autour d'une aire de jeu assise ; marqueurs collés sur le casque sans masquer ses capteurs (Fig. 3) ; corps rigide = centre de masse des marqueurs ; précision OptiTrack attendue **< 0,2 mm à 120 Hz** (`page:2`). Jeux choisis par critères (gratuit/démo, assis, > 1 000 votes, ≥ 80 % positifs) : Space Pirate Trainer DX, Oculus First Contact, Bait!, Mission: ISS, Gorilla Tag (Tableau 1, `page:2`). Motive → paquet NatNet maison → messages ROS, liaison Ethernet directe pour éviter le lag de transfert (`page:2`).
2. **Calibration Unity ↔ OptiTrack (hand-eye)** : appli Unity loggant à **30 Hz** timestamp + pose 6 DoF (quaternion) du **Center Eye Anchor** de l'Oculus SDK / Oculus Integration (`page:3`). Firmware **Meta Quest build 60.0.0**, OS SQ3A.220605.009.A1 (`page:3`). Résolution de AX = XB (Horaud & Dornaika) en C++/OpenCV/Eigen : interpolation linéaire (translation) + slerp (rotation), appariement par timestamp, passage main gauche → main droite, sous-échantillonnage ×4 de l'OptiTrack ; **méthode Daniilidis (quaternions duaux)** retenue car Tsai « sometimes failed » (`page:3`). Décalage temporel OptiTrack/Unity de **0–200 ms**, variable selon l'enregistrement, malgré horloges synchronisées par Internet ; corrigé à « quelques ms » par **détection de pics axiaux** de position et moyenne des écarts de timestamps (`page:3`).
3. **Rejeu robotisé** : UR5e (portée 850 mm, charge 5 kg, 6 axes, répétabilité ±0,03 mm, précision de pose unidirectionnelle < 0,1 mm d'après [23]) (`page:3`), buste mannequin en plastique fixé par pièces imprimées 3D + plaques acier, TCP à hauteur de tête assise (`page:3`). Deuxième hand-eye **TCP ↔ Unity** : poses TCP lues via RTDE (Ethernet direct), publiées en ROS à 30 Hz ; mouvement de calibration scripté « slow and steady » ; casque piloté par **casting** pour ne jamais le toucher entre calibration et test (`page:4`, `page:5`). Simulation Docker ROS + Gazebo + MoveIt + RViz ; trajectoire OptiTrack **diluée de 120 Hz à 12 poses/s** pour éviter les vibrations ; poses cibles T_i = B·ΔH_i avec ΔH_i = A·ΔO_i·A⁻¹ (éq. 1–2, Fig. 5) (`page:4`) ; tolérance `eef_step` relâchée de 1 cm à **3 cm** pour la fluidité ; seules les configurations avec `fraction = 1.0` (toutes les poses atteintes, « plusieurs dizaines d'essais » par trajectoire) sont retenues (`page:5`).
4. **Métrique** : APE d'evo avec alignement et relation translationnelle, « equivalent to the Absolute Trajectory Error (ATE) » ; trajectoires en format TUM (timestamp x y z qx qy qz qw) ; vérité terrain = TCP du contrôleur robot ramené à l'origine (éq. 3), estimation = Unity ramené au repère robot via la hand-eye (éq. 4) ; synchronisation par détection de pics ; segments d'arrêt et freinage final retirés (`page:2`, `page:5`).

## Résultats chiffrés
Toutes les erreurs sont des **erreurs de translation** (APE translationnelle après alignement) en mm. Aucune erreur d'orientation, aucun jitter, aucune latence n'est rapporté pour les casques.

| Métrique | Valeur | Conditions |
|---|---|---|
| Casques testés | **Meta Quest 2** et **Meta Quest Pro** uniquement (pas de Quest 3 / 3S, pas de Vision Pro) | firmware build 60.0.0 (`page:1`, `page:3`) |
| Vérité terrain | OptiTrack 6 caméras, < 0,2 mm, 120 Hz (acquisition) ; UR5e, répétabilité ±0,03 mm, précision < 0,1 mm (rejeu) | (`page:2`, `page:3`) |
| Fréquence des poses casque | **30 Hz** (log Unity du Center Eye Anchor) ; robot publié à 30 Hz ; rejeu à 12 poses/s | (`page:3`, `page:4`) |
| Résidu hand-eye TCP↔Unity | Quest 2 : **9,3 mm / 0,178°** ; Quest Pro : **6,2 mm / 0,209°** ; expérience d'occultation : 2,8 mm / 0,179° ; session 2 h (autre jour) : 42,74 mm / 3,96° (composant déplacé) | (`page:5`, `page:7`) |
| Répétabilité du robot (mouvement de calibration) | APE moyen 0,467 mm, RMSE 0,057 mm, max 1,5 mm | deux exécutions identiques, volume ≈ 0,3 m³ (`page:5`) |
| Casques, mouvement de calibration | RMSE **3,17 mm (Quest 2)** / **3,23 mm (Quest Pro)** ; max 10,48 / 11,97 mm | mouvements lents, 0,3 m³ (`page:5`) |
| Répétabilité du robot (trajectoire réelle) | RMSE 1,53 mm, max 3,69 mm (≈ ×3 vs calibration) | trajectoire plus rapide/complexe, volume 0,11–0,13 m³ (`page:6`) |
| **Casques, trajectoire réelle, run 1** | Quest 2 : RMSE **2,29 mm**, moyenne 2,05, max 8,32 ; Quest Pro : RMSE **3,49 mm**, moyenne 3,16, max 8,83 ; « without a single error of 9.0[mm] » | partie de Space Pirate Trainer DX ≈ 2 min, joueur assis (`page:6`) |
| Casques, trajectoire réelle, run 2 (Tab. 2) | Quest 2 : RMSE 3,19 / moy. 2,85 / σ 1,46 / max 9,51 ; Quest Pro : 5,29 / 4,74 / 2,34 / 13,48 ; TCP : 2,40 / 2,16 / 1,05 / 5,11 | même trajectoire, « slightly elevated error values » (`page:6`) |
| Occultation de caméras, Quest Pro (Tab. 3) | 0 caméra : RMSE 3,05 / moy. 2,69 / σ 1,44 / max 8,73 ; **2 caméras (id 0, 3) : 6,08 / 5,49 / 2,62 / 13,60** ; 3 caméras (id 0, 2, 3) : 5,56 / 5,06 / 2,39 / 13,59 | « two and three out of five RGB cameras » masquées (`page:6`, `page:7`) |
| Dérive longue durée | trajectoire bouclée **2 h** sur Quest Pro : aucune valeur chiffrée exploitable (calibration dégradée à 42,74 mm) ; pics périodiques dus au freinage du robot au rechargement de la boucle ; le **décalage d'horloge robot/Unity croît** au fil des 2 h et dégrade l'APE | (`page:7`) |
| Erreur d'orientation des casques | **non rapportée** (seuls les résidus de rotation des hand-eye, 0,178–0,209°, sont donnés) | — |
| Jitter / bruit à l'arrêt | non rapporté | — |
| Latence | non rapportée (seulement le décalage de timestamps 0–200 ms entre systèmes) | (`page:3`) |
| CPU / mémoire casque | non rapporté | — |
| Conclusion des auteurs | « both devices exhibit high positioning accuracy, with no significant differences » ; léger avantage Quest 2 « within the limits of calibration accuracy » | (`page:1`, `page:6`) |

Lecture critique des chiffres : les résidus de hand-eye (2,8–9,3 mm) sont **du même ordre que l'erreur mesurée** (2–5 mm), et les auteurs le reconnaissent (`page:6`) ; les RMSE rapportés sont donc des **bornes supérieures** de l'erreur propre du tracking, qui inclut aussi la répétabilité du robot (1,5–2,4 mm RMSE) et l'erreur de synchronisation temporelle (quelques ms × vitesse de la tête).

## Ce que ça dit du tracking du Quest
- **Mesure boîte noire d'Insight** : le papier ne regarde ni les caméras, ni l'IMU, ni la carte ; il consomme la pose **déjà fusionnée** que l'Oculus SDK expose à Unity (Center Eye Anchor), c'est-à-dire exactement le type de pose que mote lit via OVR/MRUK sur Quest 3S (`page:3`). Les auteurs rappellent seulement que ces casques font du VO + SLAM inside-out avec cartographie de l'environnement (`page:1`).
- **Ordre de grandeur** : 2–5 mm RMSE de translation sur un volume de 0,11–0,13 m³ assis, avec le firmware v60 de fin 2023 ; cohérent avec l'objectif Meta « less than a millimeter » du [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md) **seulement** si on retire la part due à la calibration et au robot, ce que le protocole ne permet pas de séparer (`page:5`, `page:6`).
- **Redondance multi-caméras confirmée** : masquer 2 des 5 caméras du Quest Pro double le RMSE (3,05 → 6,08 mm) mais le tracking **ne décroche pas** ; 3 caméras masquées ≈ 2 masquées (`page:7`). C'est le comportement attendu d'un VI-SLAM multi-caméras avec IMU : la perte de champ de vue dégrade l'observabilité mais l'IMU + les caméras restantes maintiennent la pose (cf. [Kuo 2020](../kuo2020_multicam-slam/fiche.md)). Le Quest 3S (4 caméras mono) n'est pas testé ; il faut supposer la même famille d'algorithme (dossier Insight) sans preuve ici.
- **Pas de dérive visible sur 2 h**, mais la preuve est faible : la calibration de cette session était mauvaise (42,74 mm) et le signal est pollué par la dérive d'horloge robot/Unity, pas par le tracking (`page:7`). Rien n'est dit sur la relocalisation, la carte persistante, les fermetures de boucle ni les « sauts » de pose après correction de carte ; le mouvement assis en boucle ne les sollicite guère.
- **Horloge du casque** : le timestamp Unity dérive de 0–200 ms par rapport à un PC synchronisé par NTP et cette dérive **augmente** sur 2 h (`page:3`, `page:7`). Pour mote, cela signifie que l'horodatage des poses MRUK n'est pas directement comparable à celui d'un capteur externe sans recalage ; en revanche poses et images passthrough viennent de la **même horloge** interne, ce qui est le cas favorable.
- **Prédiction / latence** : non traité ; on ne sait pas si la pose loggée à 30 Hz est la pose estimée ou la pose prédite pour l'affichage, ce qui pourrait biaiser une comparaison à une vérité terrain horodatée.
- Implication pour la qualité des poses que mote récupère : à firmware comparable, on peut attendre **quelques mm de RMSE de translation absolue** en salle sur un volume de tête, soit bien mieux qu'un centimètre ; l'orientation reste **non caractérisée** par ce papier.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Seule mesure **indépendante et publiée** de la précision absolue d'un casque Meta (Quest 2 / Quest Pro) contre une vérité terrain métrologique (OptiTrack + cobot), avec code et données (`page:1`, `page:6`). Confirme la tolérance à l'occultation partielle des caméras (`page:7`). Rien sur l'algorithme lui-même. |
| 2. Poses pour 3DGS (piste mote, H-01) | Donne un **plancher d'erreur absolue de translation de 2–5 mm RMSE** (max 8–13 mm) pour une pose Oculus SDK en salle assis (`page:6`). SP-0 mesurait 4–6 mm **médians** Quest 3S vs COLMAP : les deux ordres de grandeur concordent, ce qui suggère que l'écart SP-0 vient pour une bonne part de COLMAP (échelle, alignement Sim(3)) et non d'un défaut du casque. Mais : pas d'orientation (SP-0 : 0,3–0,5°), volume minuscule (0,11–0,13 m³) contre une capture mote debout qui parcourt une pièce, pas de Quest 3/3S. |
| 3. Temps réel et contraintes embarquées (CPU/GPU/DSP) | Rien : aucune mesure de charge, de fréquence interne, de consommation. Seule info : la pose est disponible à ≥ 30 Hz dans Unity (`page:3`). |
| 4. Évaluation (métriques, protocoles, datasets) | **Protocole réutilisable** : APE/ATE d'evo avec alignement, format TUM, hand-eye Daniilidis, synchronisation par détection de pics, retrait des segments d'arrêt (`page:2`, `page:3`, `page:5`). Dataset public de trajectoires de tête (GitHub). Montre que la **calibration et la synchronisation dominent le budget d'erreur** à l'échelle du mm (`page:5`, `page:7`). |

## Pour (vis-à-vis de notre problématique)
- Vérité terrain **métrologique** (OptiTrack < 0,2 mm, robot ±0,03 mm) et trajectoires **réelles** de jeu, rejouées à l'identique pour chaque casque : la comparaison entre casques est équitable et reproductible (`page:2`, `page:3`).
- Chiffres directement comparables à SP-0 (RMSE/moyenne/σ/max en mm, deux runs, Tab. 2) et au vocabulaire des fiches SLAM de l'axe (ATE, evo, TUM) (`page:6`).
- Expérience d'occultation unique dans la littérature publique sur les Quest (`page:7`).
- Code, scripts ROS et données publics ; procédure pas à pas (`page:1`) ; protocole « headset-agnostic » applicable au Quest 3S.
- Identifie un piège concret pour toute évaluation de poses Quest contre un capteur externe : la **dérive d'horloge** du casque (`page:3`, `page:7`).

## Contre / limites
- **Quest 2 et Quest Pro seulement**, firmware v60 (2023) : aucun résultat sur Quest 3 / 3S ni sur d'autres vendeurs (extension listée en travail futur, `page:7`).
- **Uniquement la translation** : aucune erreur d'orientation, aucun jitter, aucune latence (motion-to-photon ou pose-to-log) ; la relation translationnelle de l'APE ignore la rotation (`page:2`).
- Résidus de calibration (2,8–9,3 mm) et répétabilité du robot (1,5–2,4 mm) **comparables au signal mesuré** ; la différence Quest 2 / Quest Pro n'est donc pas significative, et l'erreur intrinsèque du casque n'est pas isolée (`page:5`, `page:6`).
- Mouvement **assis**, volume 0,11–0,13 m³, une seule trajectoire de 2 min (Space Pirate Trainer DX) pour les résultats principaux ; pas de marche, pas de parcours de pièce, pas de retour au point de départ (fermeture de boucle), pas de faible luminosité ni de scène peu texturée (`page:6`).
- Test 2 h **inexploitable quantitativement** (calibration à 42,74 mm, dérive d'horloge, freinages périodiques du robot) (`page:7`).
- Environnement de test unique (labo, Fig. 4) ; aucune variation de texture/éclairage.
- Le rejeu robot dilue la trajectoire à 12 poses/s et tolère 3 cm d'écart de passage : la dynamique rejouée est plus lisse que la tête humaine, ce qui favorise le tracking (`page:4`, `page:5`).
- Financement Meta déclaré (`page:7`) ; prépublication non évaluée par les pairs.

## Idées à creuser pour mote
- *Lecture de SP-0* : le 4–6 mm médian Quest 3S vs COLMAP est du même ordre que les 2–5 mm RMSE mesurés ici contre un robot ; formuler dans le rapport que **COLMAP n'est pas une vérité terrain** et que l'écart SP-0 est une somme (erreur casque + erreur COLMAP + alignement Sim(3)), en citant ce papier comme borne indépendante (`page:6`).
- *Protocole* : réutiliser tel quel evo APE/ATE + format TUM + alignement, et reporter RMSE / moyenne / σ / max comme Tab. 2 pour rendre SP-0 comparable (`page:5`, `page:6`).
- *Expérience bon marché* : sans robot ni OptiTrack, reproduire l'esprit du test avec une **règle / mire métrique** (déplacements connus du casque sur un rail ou une table à positions repérées) pour obtenir une borne sur l'échelle et la translation du Quest 3S, et une **mesure d'orientation** (rotation sur un plateau gradué), absente ici.
- *Hypothèse* : la tolérance à l'occultation de 2–3 caméras (`page:7`) suggère que tenir le casque à la main ou devant soi pendant une capture mote (mains dans le champ) dégradera la pose d'un facteur ≈ 2 mais sans décrochage ; à vérifier sur Quest 3S.
- *Vigilance horodatage* : les timestamps du casque dérivent (0–200 ms, croissant sur 2 h) (`page:3`, `page:7`) ; si mote associe un jour les poses à un capteur externe (GPU PC, caméra), prévoir un recalage par détection de pics comme ici ; en interne, vérifier que l'image passthrough et la pose MRUK partagent bien le même timestamp de capture et non le timestamp d'affichage prédit.
- *Évaluation H-01* : convertir les chiffres du papier en **budget d'erreur à absorber par le raffinement de poses 3DGS** : ≈ 3 mm RMSE / ≈ 10 mm max en translation sur un volume de tête ; comparer à l'erreur de reprojection correspondante à la distance des surfaces capturées (à 2 m, 10 mm ≈ 0,3° d'erreur angulaire apparente).
- *Extension* : demander au labo (LINEACT) s'il existe un OptiTrack ou un bras ; sinon, le protocole GitHub peut être rejoué avec un cobot d'école pour produire la première mesure publiée sur **Quest 3S**, ce qui serait un résultat en soi.

## Citations clés
> « Our analysis revealed that both devices exhibit high positioning accuracy, with no significant differences between them. » (`doc:5a3002b/tier:standard/page:1`)

> « The APE in evo with alignment and translational pose relation is equivalent to the Absolute Trajectory Error (ATE) metric defined in [7], and commonly used in robot localization research. » (`doc:5a3002b/tier:standard/page:2`)

> « As for Quest 2, the mean absolute pose RMSE amounted to 2.29[mm], and the mean error equaled 2.05[mm] with the maximum error reaching 8.32[mm]. In the case of Quest Pro, RMSE was equal to 3.49[mm], and the mean error leveled at 3.16[mm] with the maximum error reaching 8.83[mm] » (`doc:5a3002b/tier:standard/page:6`)

> « However, the differences between the headsets were within the limits of calibration accuracy. Therefore, it is difficult to assess unambiguously whether Quest 2 is more accurate. » (`doc:5a3002b/tier:standard/page:6`)

> « Throughout the experiment, the time offset between the robot and Unity data increased, directly deteriorating the results seen on the APE plot [...] evaluating longer trajectories recorded in Unity with external ground truth is particularly challenging due to the progressively increasing divergence of their timestamps. » (`doc:5a3002b/tier:standard/page:7`)

## Liens
- Dossier de l'axe : [Oculus Insight (billets Meta, specs Quest 3/3S, Project Aria)](../../supports/meta2019_oculus-insight-quest/dossier.md) — l'objectif « < 1 mm » de Meta et la validation OptiTrack interne, dont ce papier est la seule contrepartie indépendante.
- Papiers liés :
  - [ORB-SLAM3](../campos2021_orb-slam3/fiche.md) — ATE RMS 6–12 mm stéréo-inertiel en salle (TUM-VI room) : le Quest mesuré ici (2–5 mm sur un petit volume) est dans la même classe ou mieux.
  - [Multi-camera SLAM (Kuo 2020)](../kuo2020_multicam-slam/fiche.md) — cadre théorique de la redondance multi-caméras observée dans le test d'occultation.
  - [Project Aria (Engel 2023)](../engel2023_project-aria/fiche.md) — description publique la plus proche de la pile SLAM Meta, avec ses propres chiffres de précision MPS.
  - [VINS-Fusion](../qin2019_vins-fusion/fiche.md), [Basalt](../usenko2020_basalt/fiche.md), [OpenVINS](../geneva2020_openvins/fiche.md) — estimateurs ouverts dont l'ATE sert de point de comparaison ; même métrique evo/ATE.
  - [Benchmark VIO (Delmerico 2018)](../delmerico2018_vio-benchmark/fiche.md) — protocole d'évaluation d'estimateurs académiques, complémentaire de ce banc « boîte noire » pour casques (fiche pas encore écrite).
  - [Photo-SLAM](../huang2024_photo-slam/fiche.md), [Survey NeRF/GS-SLAM (Tosi 2024)](../tosi2024_nerf-gs-slam-survey/fiche.md) — côté « poses pour 3DGS » : quelle précision de pose un 3DGS tolère.
  - [3DGS (Kerbl 2023)](../kerbl2023_3dgs/fiche.md) — pipeline COLMAP de référence que mote remplace par les poses casque ; les chiffres de ce papier bornent l'erreur de la pose casque indépendamment de COLMAP.
