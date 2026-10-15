---
citekey: meta2019_oculus-insight-quest
type: dossier web (billets Meta, presse spécialisée, documentation Project Aria)
statut: fiche complète
consulte: 2026-10-08
tags: [oculus-insight, meta-quest-3, meta-quest-3s, vi-slam, imu, cameras-de-tracking, constellation, prediction, dsp, project-aria, mps, piste-mote]
---

# Ce que fait réellement le Quest 3 / 3S avec ses caméras et son IMU (Oculus Insight)

Meta n'a publié **aucun article scientifique** décrivant le tracking des casques Quest. Ce dossier rassemble les sources publiques exploitables : trois billets Meta de 2019 (les seuls « techniques »), les fiches matérielles du Quest 3 et du Quest 3S, et la documentation de Project Aria, dont les services de perception (MPS) sont la description publique la plus proche de la pile SLAM/VIO de Meta. Toutes les pages ont été consultées le 2026-10-08. Les citations sont reproduites en anglais, telles quelles.

## 1. Sources (ISO 690, auteur-date)

| Clé | Référence |
|---|---|
| [Meta 2019a] | META (Reality Labs). *From the lab to the living room: The story behind Facebook's Oculus Insight technology and a new era of consumer VR* [en ligne]. 21 août 2019. Disponible sur : https://tech.facebook.com/reality-labs/2019/8/the-story-behind-oculus-insight-technology/ [consulté le 8 octobre 2026]. Personnes citées : Anna Kozminski, Oskar Linde, Joel Hesch. |
| [Hesch 2019] | HESCH, Joel, KOZMINSKI, Anna et LINDE, Oskar. *Powered by AI: Oculus Insight* [en ligne]. Meta AI, 22 août 2019. Disponible sur : https://ai.meta.com/blog/powered-by-ai-oculus-insight/ [consulté le 8 octobre 2026]. **Source principale.** |
| [Melim 2019] | MELIM, Andrew. *Increasing Fidelity with Constellation-Tracked Controllers* [en ligne]. Meta for Developers, 20 septembre 2019. Disponible sur : https://developers.meta.com/horizon/blog/increasing-fidelity-with-constellation-tracked-controllers/ [consulté le 8 octobre 2026]. |
| [Lang 2018] | LANG, Ben. *Oculus Quest Supports "Arena-scale" Tracking and Multi-room Guardian* [en ligne]. Road to VR, 26 septembre 2018. Disponible sur : https://www.roadtovr.com/oculus-says-quest-tracking-supports-arena-scale-multi-room-guardian-oculus-connect-5/ [consulté le 8 octobre 2026]. |
| [McAloon 2019] | McALOON, Alissa. *C'mon and SLAM: How Oculus tackled portable, 6DOF tracking for the Quest* [en ligne]. Game Developer, 22 août 2019. Disponible sur : https://www.gamedeveloper.com/extended-reality/c-mon-and-slam-how-oculus-tackled-portable-6dof-tracking-for-the-quest [consulté le 8 octobre 2026]. Reprise de [Meta 2019a], sans information supplémentaire. |
| [Road to VR 2024] | ROAD TO VR. *Quest 3S vs Quest 3 vs Quest 2 Compared with Detailed Specs* [en ligne]. 2024. Disponible sur : https://roadtovr.com/quest-3s-quest-3-quest-2-specs-compared/ [consulté le 8 octobre 2026]. |
| [Heaney 2024a] | HEANEY, David. *Quest 3S Specs – Compared To Quest 3, Quest 2, Apple Vision Pro, And More* [en ligne]. UploadVR, 15 octobre 2024. Disponible sur : https://www.uploadvr.com/quest-3s-specs/ [consulté le 8 octobre 2026]. |
| [Heaney 2024b] | HEANEY, David. *Quest 3S Has Better Low-Light Head & Hand Tracking Than Quest 3* [en ligne]. UploadVR, 14 octobre 2024. Disponible sur : https://www.uploadvr.com/quest3s-hand-tracking-better-than-quest-3/ [consulté le 8 octobre 2026]. |
| [Wikipedia 2026] | WIKIPEDIA. *Meta Quest 3* [en ligne]. Disponible sur : https://en.wikipedia.org/wiki/Meta_Quest_3 [consulté le 8 octobre 2026]. Source tertiaire, utilisée seulement pour la disposition des caméras ; à recouper. |
| [Meta 2026a] | META (Project Aria). *Machine Perception Services (MPS)* [en ligne]. projectaria_tools. Disponible sur : https://facebookresearch.github.io/projectaria_tools/docs/ARK/mps [consulté le 8 octobre 2026]. |
| [Meta 2026b] | META (Project Aria). *MPS Trajectory* [en ligne]. projectaria_tools. Disponible sur : https://facebookresearch.github.io/projectaria_tools/docs/data_formats/mps/slam/mps_trajectory [consulté le 8 octobre 2026]. |
| [Engel 2023] | Papier Project Aria, ingéré dans la base : [sources/engel2023_project-aria/fiche.md](../../sources/engel2023_project-aria/fiche.md). |

## 2. Architecture d'Oculus Insight (billets Meta 2019)

### 2.1 Un VI-SLAM maison, deuxième génération d'une bibliothèque mobile
- Insight est un **SLAM visuel-inertiel** pour le casque, plus un **« constellation tracking »** (LED infrarouges) pour les manettes [Hesch 2019].
- Il descend de la bibliothèque SLAM de 13th Lab (start-up d'Oskar Linde, rachetée en 2014), qui avait « demonstrated the world's first use of visual SLAM in a consumer application as part of a mobile AR game in 2011 » ; la première génération utilisait une seule caméra de téléphone et un IMU. Insight est « the second generation », qui ajoute « multiple IMUs, ultra-wide-angle cameras, and infrared LEDs » [Hesch 2019 ; Meta 2019a]. Démonstration sur le prototype Santa Cruz en 2016 [Meta 2019a]. L'équipe de Zurich vient en partie de Zurich Eye (ETH/UZH), c'est-à-dire du milieu académique du VIO (même origine que les papiers de Scaramuzza et Siegwart dans la base) [Meta 2019a].

### 2.2 Chaîne de traitement
1. **Détection et suivi de points** : « high-contrast pixels, such as window corners », suivis d'image en image ; triangulés après assez d'observations ; les points stables (coins de meubles, motifs du sol) deviennent des **landmarks** [Hesch 2019].
2. **Carte 3D persistante** : « generate a real-time 3D map of your immediate surroundings so the headset could compute your position within the map » [Meta 2019a]. Les mises à jour de carte tournent **de manière asynchrone en arrière-plan** ; la carte est raffinée quand l'environnement change ; **reconnaissance de lieu** et reconstruction de géométrie (ex. détection du sol) font partie du système [Hesch 2019]. Insight reconnaît la pièce (Guardian multi-pièces) et visait dès 2018 le « arena-scale » (plusieurs milliers de pieds carrés, « still experimental ») [Lang 2018].
3. **Fusion IMU** : « drawing acceleration and velocity data from the inertial measurement units (IMUs) located in the headset and controllers » ; accélération linéaire et vitesse angulaire intégrées pour une pose basse latence ; la dérive de l'intégration est corrigée par les observations répétées des landmarks [Meta 2019a ; Hesch 2019]. L'IMU a **son propre thread, de priorité plus haute**, qui écrit dans un tampon en mémoire partagée pour réduire la latence [Hesch 2019].
4. **Cadence et prédiction** : « Oculus Insight computes an accurate and real-time position for the headset and controllers every millisecond » (soit **1 kHz**, cadence IMU). Une fonction d'**extrapolation à amortissement dynamique** et un modèle cinématique prédisent la pose « in the next few milliseconds » pour masquer la latence [Hesch 2019].
5. **Manettes** : détection de « bright infrared volumes » dans des images à **exposition très courte**, appariement avec le modèle 3D des LED (15 LED sur les manettes Quest contre 22 sur les Touch Rift), résolution de pose puis fusion inertielle ; pyramides d'images calculées sélectivement, « not computed at every frame or even for every camera » [Melim 2019].

### 2.3 Objectifs de précision et validation
- Objectif de précision : « The tracking had to be accurate down to less than a millimeter » ; Insight « exceeds this in most environments » [Meta 2019a ; Hesch 2019]. **Aucune mesure publiée** (ni erreur absolue, ni dérive, ni latence).
- Vérité terrain **OptiTrack** sur « hundreds of environments », rejeu automatisé de vidéos enregistrées pour détecter les régressions, modèle de performance de la puce mobile simulé sur serveurs [Hesch 2019].
- « swimminess » et « judder » cités comme artefacts perceptifs à réduire [Meta 2019a].

### 2.4 Contraintes de calcul : CPU, DSP, asynchronisme
- Insight tourne sur la puce mobile en même temps que le rendu, avec « roughly one order of magnitude less compute and two orders of magnitude less power than a PC or console » [Hesch 2019].
- Optimisations déclarées : **multithreading, opérations asynchrones, et « Quest-specific DSP tuning »** [Hesch 2019]. C'est la seule mention publique d'un usage du DSP (Hexagon) pour le tracking Quest ; aucun détail (SIMD, précision fixe, répartition CPU/DSP).
- Aucune description de modèle d'apprentissage dans la boucle de tracking en 2019 ; l'IA est présentée comme direction future [Hesch 2019]. Les fiches techniques Quest 3S de 2024 parlent de « Hybrid using Computer Vision and Machine learning tracking » pour les manettes (hand tracking + Constellation) ; rien n'est dit du SLAM casque.

## 3. Matériel Quest 3 et Quest 3S

| Élément | Quest 3 | Quest 3S | Sources |
|---|---|---|---|
| Caméras de tracking | 4 caméras IR/monochrome (400 × 400 px selon Wikipédia, non confirmé par Meta) : 2 dans les « pills » avant externes, 2 en bas à gauche et à droite | 4 caméras IR | [Road to VR 2024 ; Wikipedia 2026] |
| Rôle double des caméras avant | alternent d'une image à l'autre entre visible monochrome (SLAM casque) et infrarouge (LED des manettes) | idem (même pile logicielle) | [Wikipedia 2026], à recouper |
| Caméras passthrough couleur | 2 × 4 MP RGB (18 PPD) | 2 × 4 MP RGB (18 PPD) | [Road to VR 2024 ; Heaney 2024a] |
| Profondeur | projecteur IR à motif (lumière structurée) au centre, utilisé pour le maillage de scène ; « only appears to be used during mixed reality scene mesh scanning » | **pas de projecteur** ; 2 illuminateurs IR (flood) ; profondeur calculée par les caméras de tracking | [Heaney 2024a ; Heaney 2024b ; Wikipedia 2026] |
| Tracking dans le noir | impossible (tête et mains) | mains OK, tête OK « as long as I'm near a wall or other geometry, though with some minor jitter » | [Heaney 2024b] |
| SoC | Snapdragon XR2 Gen 2 (SXR2230P, 4 nm) : 2 × Cortex-A715 + 4 × Cortex-A510, Adreno 740, 8 Go LPDDR5 | identique | [Wikipedia 2026 ; Road to VR 2024] |
| Affichage | 2 × LCD, 2064 × 2208 par œil, 25 PPD, pancake | 1 × LCD, 1832 × 1920 par œil (≈ 20 PPD), Fresnel | [Road to VR 2024 ; Heaney 2024a] |
| IMU | **non documenté** (modèle, cadence) ; la cadence « every millisecond » de [Hesch 2019] suggère 1 kHz | idem | — |

Point important pour mote : les caméras **passthrough RGB** (celles que MRUK expose) ne sont **pas** les caméras de tracking. La pose « caméra » fournie par MRUK est donc la pose du casque, estimée par le VI-SLAM sur les 4 caméras monochromes + IMU, puis transformée vers la caméra RGB par les extrinsèques d'usine. Les intrinsèques et la synchronisation des caméras RGB avec l'horloge de tracking restent les points ouverts Q-03/Q-11 du SPEC mote.

## 4. Project Aria : la description publique la plus proche de la pile Meta

Project Aria (lunettes de recherche Meta) publie ce que Quest ne publie pas. Son papier [Engel 2023] et sa documentation décrivent un **VIO embarqué** et un **SLAM hors ligne** (MPS) sur un matériel comparable au Quest : deux caméras SLAM monochromes grand angle, deux IMU, et les mêmes équipes Reality Labs.
- Deux trajectoires 6DoF à **1 kHz** (cadence IMU) : **open loop** = odométrie locale du VIO (bonne précision locale sur quelques minutes, dérive avec le temps et la distance, repère d'odométrie arbitraire, score de qualité 0–1) ; **closed loop** = optimisation globale par lots (SLAM + IMU + baromètre + Wi-Fi + GPS), repère monde aligné sur la gravité, fermetures de boucle, « fully bundle adjusted » [Meta 2026a ; Meta 2026b].
- Sorties annexes utiles à une chaîne 3DGS : **nuage de points semi-dense** (triangulé par stéréo photométrique entre images successives ou entre caméras gauche/droite), **calibration en ligne** variant dans le temps (intrinsèques et extrinsèques caméras + IMU, à la cadence des caméras SLAM), **multi-SLAM** dans un repère commun [Meta 2026a].
- Chiffres (voir la fiche [Engel 2023] pour les pages) : dérive open loop < 0,4 % de la distance parcourue ; erreur RMSE de translation closed loop ≤ 1,5 cm à l'échelle d'une pièce. Comparaison autodéclarée « superior accuracy and robustness » face aux solutions open source.
- Ce qu'on peut raisonnablement supposer pour le Quest (hypothèse, à ne pas citer comme fait) : la pose MRUK est l'équivalent d'une trajectoire **open loop** (odométrie VIO temps réel) corrigée par relocalisation sur la carte persistante, sans l'optimisation globale hors ligne.

## 5. Ce que l'on sait, ce que l'on ignore

| Connu (source Meta) | Inconnu (jamais publié) |
|---|---|
| VI-SLAM à landmarks avec carte persistante, relocalisation, mises à jour asynchrones | Formulation de l'estimateur (filtre type MSCKF ou optimisation par fenêtre glissante type VINS/Basalt) |
| Pose à 1 kHz, prédiction par extrapolation amortie | Précision mesurée (erreur absolue, dérive, jitter), latence capteur-pose |
| 4 caméras monochrome/IR + IMU ; passthrough RGB séparé | Résolution et cadence réelles des caméras de tracking, modèle et cadence de l'IMU |
| CPU multithread + DSP, ordre de grandeur de 10× moins de calcul qu'un PC | Répartition CPU/DSP/GPU, budget en ms, consommation du tracking |
| Validation OptiTrack en interne | Toute donnée brute (images de tracking, IMU) : aucune API publique |

Conséquence pour mote : la précision des poses Quest ne peut venir que d'une **mesure indépendante**. C'est ce que fait le spike SP-0 (4–6 mm / 0,3–0,5° en médiane contre COLMAP complet, voir la mémoire du projet) et ce que fait, avec une vérité terrain OptiTrack et un robot, le papier [Banaszczyk 2024](../../sources/banaszczyk2024_vr-positioning-accuracy/fiche.md).

## 6. Liens avec la base
- Estimateurs ouverts comparables : [ORB-SLAM3](../../sources/campos2021_orb-slam3/fiche.md) (optimisation, multi-cartes, relocalisation), [VINS-Mono](../../sources/qin2018_vins-mono/fiche.md) / [VINS-Fusion](../../sources/qin2019_vins-fusion/fiche.md), [OpenVINS](../../sources/geneva2020_openvins/fiche.md) (filtre MSCKF, calibration en ligne), [Basalt](../../sources/usenko2020_basalt/fiche.md), [Kimera](../../sources/rosinol2020_kimera/fiche.md).
- Multi-caméras asynchrones comme sur Quest : [Eckenhoff 2019](../../sources/eckenhoff2019_multicam-vins/fiche.md), [Kuo 2020](../../sources/kuo2020_multicam-slam/fiche.md).
- Contraintes embarquées (CPU/GPU/DSP/ASIC) : [Delmerico 2018](../../sources/delmerico2018_vio-benchmark/fiche.md), [Nagy 2020](../../sources/nagy2020_faster-than-fast/fiche.md), [Navion](../../sources/suleiman2019_navion/fiche.md).
- Synthèse : [synthese/localisation_poses.md](../../synthese/localisation_poses.md).
