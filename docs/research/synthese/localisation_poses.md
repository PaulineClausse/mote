# Localisation des poses : SLAM / VIO temps réel et piste mote

Rédigé le 2026-10-08. Complète [options.md](options.md) pour la piste mote (poses du casque Quest 3S à la place de COLMAP). Chaque chiffre renvoie à une fiche de `sources/` où il est sourcé page par page. Marquage : ✅ sourcé dans la base, 🔎 à sourcer ou à mesurer.

**Question directrice :** quelle qualité de poses un SLAM temps réel fournit-il, comment le Quest la produit-il, et que faut-il en faire pour entraîner un 3DGS (hypothèse H-01 de mote) ?

## 1. Ce que fait réellement le casque (Oculus Insight)

Résumé du [dossier Insight](../supports/meta2019_oculus-insight-quest/dossier.md) ; Meta n'a rien publié de plus précis que ses billets de 2019.

| Point | Ce qui est établi ✅ | Ce qui reste inconnu 🔎 |
|---|---|---|
| Nature | VI-SLAM maison (2ᵉ génération de la bibliothèque 13th Lab), landmarks triangulés, **carte 3D persistante** mise à jour en arrière-plan, reconnaissance de lieu, détection du sol | formulation de l'estimateur (filtre type MSCKF ou fenêtre glissante par optimisation) |
| Capteurs | 4 caméras monochrome/IR grand angle + IMU ; les 2 caméras RGB passthrough (celles de MRUK) **ne servent pas au tracking** | résolution/cadence des caméras de tracking, modèle et cadence de l'IMU |
| Sortie | pose « every millisecond » (1 kHz), prédiction par extrapolation amortie de quelques ms | latence capteur→pose, jitter |
| Calcul | mobile SoC (XR2 Gen 2), multithread + asynchrone + « Quest-specific DSP tuning », ≈ 10× moins de calcul qu'un PC | répartition CPU/DSP/GPU, budget en ms |
| Précision | objectif « sub-millimeter », validé en interne contre OptiTrack ; **mesure indépendante** : Quest 2 / Quest Pro RMSE 2,3–3,5 mm (max ≈ 8–9 mm) contre robot + OptiTrack, translation seulement ([Banaszczyk 2024](../sources/banaszczyk2024_vr-positioning-accuracy/fiche.md), p. 6) | Quest 3 / 3S jamais mesurés publiquement ; erreur d'orientation jamais mesurée |
| Analogue public | Project Aria (même labo) : VIO embarqué « open loop » dérive ≤ 0,4 % de la distance, SLAM hors ligne « closed loop » RMSE ≤ 1,5 cm en pièce, nuage semi-dense, calibration en ligne ([Engel 2023](../sources/engel2023_project-aria/fiche.md), p. 6–7) | si le Quest applique une optimisation globale ou seulement une relocalisation |

Lecture pour mote : la pose MRUK est très probablement une **odométrie VIO causale, recalée sur une carte persistante** ; précise localement (mm), jamais corrigée rétroactivement (ce que MRUK renvoie est figé), avec des sauts possibles à la relocalisation. Le SP-0 (4–6 mm / 0,3–0,5° médians contre COLMAP) est cohérent avec Banaszczyk 2024, et COLMAP n'est pas une vérité terrain : l'écart SP-0 additionne l'erreur casque, l'erreur COLMAP et l'alignement.

## 2. Familles d'estimateurs ouverts et ce qu'ils livrent

Taxonomie d'après [Huang 2019](../sources/huang2019_vin-review/fiche.md) ; chiffres des fiches respectives. ATE = erreur absolue de trajectoire (RMSE après alignement), sur EuRoC (drone, stéréo 20 Hz + IMU 200 Hz) sauf mention.

| Famille | Représentant (fiche) | Capteurs | Précision ✅ | Coût / matériel ✅ | Carte, boucle, reloc |
|---|---|---|---|---|---|
| Filtre MSCKF sur variété | [OpenVINS](../sources/geneva2020_openvins/fiche.md) | mono/stéréo + IMU | ATE EuRoC 0,054 m (stéréo SLAM), 0,079 m (mono) ; RPE 0,07→0,12 m de 8 à 48 m (p. 6) | 1,2–4,3× temps réel sur un seul thread Xeon mobile (p. 6) | landmarks SLAM marginalisés, pas de boucle ; calibration en ligne (intrinsèques, extrinsèques, décalage temporel) |
| Filtre multi-caméras asynchrones | [Eckenhoff 2019](../sources/eckenhoff2019_multicam-vins/fiche.md) | N caméras + IMU | erreur de fermeture sur 440 m : 0,80 % (caméra de base seule) → 0,14 % (3 caméras asynchrones) ; intrinsèques non raffinées : 0,33 % → 1,00 % (p. 5–6) | 23 ms par mise à jour (44 Hz) à 2 caméras 30 Hz, 30 ms à 3 caméras (p. 4, 6) | clones de pose pour une caméra de base, interpolation pour les autres ; le schéma le plus proche des 4 caméras Quest |
| Fenêtre glissante par optimisation | [VINS-Mono](../sources/qin2018_vins-mono/fiche.md) | mono + IMU | dérive 0,88 % sans boucle (> 700 m), ramenée à ≈ 0,1 m avec boucle (p. 13) ; 0,29 % vs OptiTrack sur drone (p. 14) | détecteur 15 ms + KLT 5 ms à 25 Hz, optimisation 50 ms à 10 Hz sur i7 ; > 50 ms par image en embarqué (p. 14) | graphe de poses 4 DOF, reloc DBoW2 |
| idem, stéréo + IMU | [VINS-Fusion](../sources/qin2019_vins-fusion/fiche.md) | stéréo + IMU | ATE EuRoC 0,10–0,39 m (stéréo+IMU), 0,06–0,26 m (mono+IMU) ; extérieur 230 m : 0,43–0,75 m (p. 5–6) | non rapporté | facteurs génériques, boucle via le papier compagnon |
| Fenêtre glissante + récupération de facteurs | [Basalt](../sources/usenko2020_basalt/fiche.md) | stéréo + IMU | ATE VIO 0,04–0,13 m, mapping NFR 0,02–0,10 m (p. 8) | VIO 7,8 ms/image sur 4 cœurs sans GPU, 11,5 % de keyframes (p. 8) | couche globale qui réoptimise les keyframes de plusieurs cm |
| Lissage iSAM2 + maillage | [Kimera](../sources/rosinol2020_kimera/fiche.md) | stéréo + IMU | ATE 0,05–0,35 m (VIO), 0,05–0,24 m (RPGO) (p. 5) ; dérive < 0,2 % simulée (p. 6) | front-end 4,5 ms/image, keyframe 45 ms, back-end < 40 ms, mesher 15 ms, PGO 55 ms (p. 6) | graphe de poses robuste (PCM), maillage dense temps réel = analogue du « scene mesh » Quest |
| SLAM à keyframes et carte de points | [ORB-SLAM](../sources/murartal2015_orb-slam/fiche.md) → [ORB-SLAM3](../sources/campos2021_orb-slam3/fiche.md) | mono/stéréo/RGB-D ± IMU, multi-cartes | **ORB-SLAM3 stéréo-inertiel : ATE 0,009 m sur TUM-VI room (« representative of AR/VR », p. 13), 0,035 m sur EuRoC (p. 12)** ; échelle à 5 % en 2 s, 1 % en 15 s (p. 5, 8) | 30–40 fps, 33 ms/image stéréo-inertiel sur i7 CPU seul (p. 14–15) ; ORB-SLAM 2015 : 30 ms/image, BA local 296 ms/keyframe (p. 10) | Atlas multi-cartes, reloc DBoW2 à rappel élevé, BA global ; sauts de pose à la fermeture de boucle |
| SLAM dense appris (sans IMU) | [DROID-SLAM](../sources/teed2021_droid-slam/fiche.md) | mono/stéréo/RGB-D | ATE EuRoC mono 0,022 m, stéréo 0,024 m, zéro échec (p. 8, 13) | **2 × RTX 3090**, 8–24 Go, 20 fps à 320×512 (p. 9) | BA global dense, pas de reloc classique |
| VO épars appris | [DPVO](../sources/teed2023_dpvo/fiche.md) | mono | ATE EuRoC 0,105 m (VO seule) ; TartanAir 0,21 vs COLMAP 12,5 (p. 7) | 60 fps / 4,9 Go ou 120 fps / 2,5 Go sur RTX 3090 (p. 2, 8) | ni carte ni reloc ; échelle non observée |
| SLAM multi-caméras générique | [Kuo 2020](../sources/kuo2020_multicam-slam/fiche.md) | N caméras | erreur relative ≈ 1,1 % (2 cam.) → 0,2–0,3 % (3–5 cam.), gain marginal au-delà de 3 (p. 5) | front-end ≈ 3,4 → 7,6 ms de 2 à 4 caméras (p. 5) | cite l'Oculus Quest comme rig cible (p. 1) |

Ordres de grandeur à retenir ✅ : un VI-SLAM de bureau en pièce fermée atteint **≈ 1 cm d'ATE** (ORB-SLAM3 TUM-VI room) ; une odométrie sans carte dérive de **0,2 à 0,9 % de la distance** ; un casque Quest mesuré contre robot est à **2–5 mm RMSE** sur une trajectoire assise de 2 min. Les poses Quest sont donc au niveau des meilleurs systèmes ouverts, pas en dessous.

## 3. Contraintes embarquées : CPU, GPU, DSP, SIMD, ASIC

| Niveau | Source ✅ | Résultat | Transposition au Quest |
|---|---|---|---|
| CPU ARM embarqué, 6 VIO comparés | [Delmerico 2018](../sources/delmerico2018_vio-benchmark/fiche.md) | VINS-Mono garde ≈ 0,16 m d'ATE moyen du laptop à l'ODROID XU4 (ARM), mais la fermeture de boucle (0,075 m sur laptop) n'y tient plus ; temps par image ≈ 140 ms (VINS-Mono) et ≈ 340 ms (OKVIS) sur ODROID contre 55 / 25 ms sur laptop, à 100–240 % d'un cœur ; ROVIO diverge sur Atom 1,44 GHz (p. 5–7) | XR2 Gen 2 = Cortex-A715/A510 : même classe que l'Odroid, en plus rapide ; « no free lunch : more computation, better accuracy » |
| GPU embarqué, frontend | [Nagy 2020](../sources/nagy2020_faster-than-fast/fiche.md) | FAST 1,11 ms et KLT 0,90 ms sur Jetson TX2 ; VIO complet 4,7–6,4 ms/image (≈ 200 fps), 2,25× vs CPU, perte de précision ≈ 0,5 point (p. 7–8) | le GPU Adreno est réservé au rendu ; Meta parle de **DSP tuning** (Hexagon), pas de GPU |
| ASIC dédié | [Navion](../sources/suleiman2019_navion/fiche.md) | VIO stéréo + IMU complet à **2 mW** (20 fps, EuRoC), 24 mW à 171 fps ; 2,3 mJ par keyframe contre 1573 mJ sur ARM Cortex-A15 ; erreur 0,28 % de la distance en virgule fixe contre 0,22 % en flottant (p. 1, 9–10, 12) | borne basse de l'énergie ; le Quest n'a pas d'ASIC de tracking connu |
| Décalage CPU → PC | [DROID-SLAM](../sources/teed2021_droid-slam/fiche.md), [DPVO](../sources/teed2023_dpvo/fiche.md) | précision maximale contre 2 GPU desktop, ou 1 GPU avec DPVO | c'est le rôle du PC dans mote : raffinement, pas tracking |

Conclusion pour mote ✅ : le casque fait le tracking (CPU + DSP, budget serré, cf. [Kimera](../sources/rosinol2020_kimera/fiche.md) pour les ordres de grandeur par module) ; toute charge supplémentaire côté casque (lecture CPU des images, encodage) entre en concurrence avec lui (RISK-06 du SPEC). Le PC GPU prend le mapping et, au besoin, un raffinement de poses de type BA.

## 4. Poses et 3DGS : où se situe mote

Le survey [Tosi 2024](../sources/tosi2024_nerf-gs-slam-survey/fiche.md) distingue les SLAM **couplés** (le rendu 3DGS sert au tracking : MonoGS, SplaTAM, GS-SLAM) des SLAM **découplés** (un tracker géométrique externe fournit les poses : Photo-SLAM ← ORB-SLAM3, MonoGS++ et MGS-SLAM ← DPVO, DG-SLAM ← DROID). **mote est un SLAM découplé dont le tracker est le casque.**

| Schéma | Exemple ✅ | ATE | Rendu | Coût GPU |
|---|---|---|---|---|
| Couplé (tracking par rendu) | SplaTAM | — | — | 18,5 Go, 0,14 fps sur RTX 3090 (Tosi p. 19) |
| Couplé | MonoGS (TUM mono) | 4,4 cm (Tosi p. 15) | PSNR Replica 37,5 (p. 17) | — |
| Découplé | MonoGS++ (poses DPVO) | 0,9 cm (p. 15) | 37,8 (p. 17) | — |
| Découplé | [Photo-SLAM](../sources/huang2024_photo-slam/fiche.md) (poses ORB-SLAM3) | Replica mono 1,09 cm vs ORB-SLAM3 seul 3,94 cm (p. 6) | PSNR 33,3 ; 41,6 Hz desktop / 18,3 Hz Jetson Orin, 4–6 Go (p. 6) | découplé = presque tout le budget GPU au mapping |

Deux résultats ✅ pèsent directement sur H-01 :
1. **Le nuage initial compte autant que les poses** : à poses fixées, un 3DGS passe de 27,8 dB (points aléatoires) à 37,1 dB (points du tracker) (Photo-SLAM, p. 12). Sans COLMAP, mote doit produire un nuage épars autrement (triangulation entre images à poses connues, profondeur/scene mesh du Quest 3, profondeur monoculaire sur 3S).
2. **Photo-SLAM ne raffine jamais les poses** par la photométrie (p. 4) et obtient tout de même 33 dB : le volet « raffinement des poses » de H-01 n'est peut-être pas indispensable au premier ordre. Aucun papier de la base ne donne la courbe « erreur de pose → PSNR » 🔎 : c'est l'expérience la plus utile à faire (bruiter artificiellement les poses, σ 2–20 mm / 0,1–1°, avec et sans raffinement).

## 5. Ce que la littérature recommande de faire dans mote

Issu des sections « Idées à creuser » des fiches ; chaque ligne cite la fiche d'origine.

**Protocole de capture**
- Phase de « chauffe » de 15 s avant la capture utile (maturation de l'échelle et de la carte : ORB-SLAM3 p. 8, ORB-SLAM Fig. 10) ; éviter les rotations pures et les mouvements dégénérés (Huang 2019 p. 7) ; éclairage et vitesse angulaire bornés (Nagy p. 7).
- Détecter les **sauts de pose** (relocalisation, fermeture de boucle) dans le flux MRUK avec le critère de VINS-Mono (p. 9) et segmenter la capture en tronçons à repère cohérent, puis les aligner (Sim(3)/SE(3)) avant l'entraînement ; une correction de boucle reçue peut être appliquée aux Gaussiennes par déformation de leurs centres (Photo-SLAM p. 5, Tosi p. 11).
- Sélection d'images par **critère de keyframe** (parallaxe compensée en rotation, < 70–90 % de points communs : VINS-Mono p. 4, Basalt p. 7, ORB-SLAM p. 8) plutôt qu'à cadence fixe : 10–15 % des images suffisent au mapping (Basalt p. 8).

**Raffinement et pondération des poses (H-01)**
- Ne raffiner que les 4 DOF non observables (x, y, z, lacet), roulis et tangage étant fixés par la gravité (VINS-Mono p. 11) ; un seul extrinsèque rigide corps→caméra RGB partagé par toutes les vues plutôt qu'une correction par pose (VINS-Fusion p. 5).
- Formuler le raffinement comme BA à facteurs hétérogènes : pose casque = facteur a priori pondéré, résidu photométrique 3DGS = facteur image (VINS-Fusion p. 3–4, Basalt éq. 30 p. 7) ; attendre un gain millimétrique (erreur de linéarisation), pas une correction de dérive (Huang 2019 p. 4–5).
- Raffineur externe possible sur PC : backend DROID-SLAM ou DPVO initialisé avec les poses MRUK (≈ 17 ms/image sur GPU, DPVO p. 11) comme alternative aux 33–86 s de COLMAP.
- Estimer hors ligne le décalage temporel pose/image RGB et vérifier l'obturateur roulant de la caméra passthrough (OpenVINS p. 3, Huang 2019 p. 4–7, Aria p. 7 : 25 arcmin ≈ 1,5 px d'écart inter-caméras au port des lunettes).

**Évaluation**
- Rapporter ATE RMSE (Horn/Sim(3)) **et** RPE par longueur de segment (1, 2, 4, 8 m) pour séparer bruit local et dérive (OpenVINS p. 6, Kuo Fig. 6), plus la dérive en % de la distance (Aria p. 6), plus une erreur angulaire que personne ne mesure sur casque (Banaszczyk).
- Références chiffrées : ≈ 1 cm d'ATE en pièce (ORB-SLAM3 TUM-VI room, TUM fr1), 2–5 mm RMSE casque vs robot (Banaszczyk p. 6), PSNR ≥ 33 dB pour la carte (Photo-SLAM).
- Expérience bon marché sans OptiTrack : mire métrique et plateau gradué pour une borne sur l'échelle, la translation et l'orientation du Quest 3S ; aucune mesure publiée n'existe sur Quest 3/3S, ce serait un résultat en soi (Banaszczyk).
- Rejeu d'un estimateur ouvert (ORB-SLAM3 mono ou DPVO sur les images passthrough) comme **troisième juge** entre poses Quest et COLMAP (ORB-SLAM3 p. 11, DPVO).

## 6. Références repérées, non ingérées
- MIMC-VINS (Eckenhoff, Geneva, Huang, T-RO 2021) : version journal multi-IMU multi-caméras de [Eckenhoff 2019](../sources/eckenhoff2019_multicam-vins/fiche.md).
- VINS-Fusion, papier compagnon fusion globale GPS (arXiv 1901.03642).
- MonoGS (arXiv 2312.06741), SplaTAM (2312.02126), GS-ICP SLAM (2403.12550), MASt3R-SLAM (2412.12392) : cités via le survey Tosi 2024 ; MASt3R-SLAM est déjà listé `[CONNU]` dans le SPEC mote.
- Schubert et al. 2018, dataset TUM-VI (rig stéréo + IMU proche d'un casque), base des chiffres « room » d'ORB-SLAM3.
- Cadena et al. 2016, « Past, Present and Future of SLAM » (arXiv 1606.05830), revue générale.
- Kühne et al. 2024, flot optique sur capteur pour VIO embarqué (arXiv 2406.13345).
