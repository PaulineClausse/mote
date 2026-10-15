---
citekey: campos2021_orb-slam3
mineru_doc: 4d11951
type: article de revue   # IEEE Transactions on Robotics, 2021 ; preprint arXiv 2007.11898v2
statut: fiche complète
tags: [slam, vi-slam, visual-inertial, orb, multi-map, atlas, place-recognition, dbow2, imu-initialisation, map-estimation, fisheye, stereo, euroc, tum-vi, ar-vr, temps-réel, cpu, open-source, piste-mote, poses-casque]
---

# ORB-SLAM3: An Accurate Open-Source Library for Visual, Visual-Inertial and Multi-Map SLAM

**Référence :** Carlos Campos, Richard Elvira, Juan J. Gómez Rodríguez, José M. M. Montiel, Juan D. Tardós (2021). *ORB-SLAM3: An Accurate Open-Source Library for Visual, Visual-Inertial and Multi-Map SLAM.* IEEE Transactions on Robotics (accepté 2021). DOI [10.1109/TRO.2021.3075644](https://doi.org/10.1109/TRO.2021.3075644) · arXiv [2007.11898v2](https://arxiv.org/abs/2007.11898) (23 avril 2021) · code : [github.com/UZ-SLAMLab/ORB_SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) (réf. [5]) · Universidad de Zaragoza, I3A (`doc:4d11951/tier:standard/page:1`, `page:2`, `page:16`)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Bibliothèque SLAM open source à points ORB qui fusionne caméras (mono, stéréo, RGB-D, pin-hole ou fisheye) et IMU par estimation MAP (bundle adjustment visuel-inertiel), initialise l'IMU en 2 s avec 5 % d'erreur d'échelle, gère plusieurs cartes (Atlas) avec une reconnaissance de lieu à meilleur rappel, et atteint 3,5 cm d'ATE moyen sur EuRoC et **9 mm sur les séquences « room » de TUM-VI, « a setting representative of AR/VR scenarios »**, le tout en temps réel sur CPU seul (`page:2`, `page:11`, `page:13`).

## Problème traité
- Les systèmes d'odométrie visuelle (VO) ou visuelle-inertielle (VIO) n'exploitent que l'association de données **à court terme** (dernières secondes) ; ils dérivent en continu même quand on revient au même endroit. Le SLAM ajoute l'association **à moyen terme** (points proches de la caméra dont la dérive accumulée est faible, utilisables en BA, d'où une dérive nulle en zone cartographiée) et **à long terme** (reconnaissance de lieu : fermeture de boucle, fusion de cartes, relocalisation). ORB-SLAM3 ajoute l'association **multi-carte** : réutiliser en BA des éléments issus de sessions précédentes (`page:2`).
- L'initialisation de l'IMU d'ORB-SLAM-VI prenait 15 s ; les méthodes en forme fermée ignorent le bruit capteur et minimisent une erreur 3D au lieu de l'erreur de reprojection, d'où des erreurs « large unpredictable » ; VI-DSO met 20–30 s à converger à 1 % d'échelle (`page:4`, `page:8`).
- DBoW2 impose une cohérence temporelle sur 3 keyframes consécutives avant la vérification géométrique : précision 100 % mais rappel 30–40 % (contre 50–80 % en requête brute) et retard d'au moins 3 keyframes ; dans un système multi-carte cela produit des zones dupliquées (`page:3`, `page:9`).
- Les SLAM stéréo supposent des images rectifiées, inapplicable aux fisheye proches de 180° ou aux paires divergentes (`page:6`).

## Méthode / contributions
Papier « système » dont la contribution principale est la bibliothèque elle-même (`page:2`). Quatre nouveautés :
- **VI-SLAM mono et stéréo entièrement MAP**, y compris pendant l'initialisation IMU. État par keyframe : pose SE(3), vitesse, biais gyro et accéléro (marche brownienne) ; préintégration IMU sur variété [60], [61] ; coût = résidus inertiels (sans noyau robuste, « miss-associations do not exist ») + reprojection avec noyau de Huber (éq. 4) (`page:6`, `page:7`).
- **Initialisation IMU en trois étapes** : (1) SLAM mono pur pendant 2 s, keyframes à 4 Hz, soit k = 10 poses à l'échelle près ; (2) optimisation **inertial-only** MAP des variables {échelle s, direction de gravité R_wg, biais b, vitesses} avec la trajectoire visuelle fixée et un a priori de biais proches de zéro (éq. 8) ; l'échelle est mise à jour par s·exp(δs) pour rester positive ; (3) BA visuel-inertiel joint. Résultat : 5 % d'erreur d'échelle à 2 s, 1 % après les BA relancés à 5 s et 15 s (carte « mature ») ; raffinement d'échelle (échelle + gravité seules) toutes les 10 s jusqu'à 100 keyframes ou 75 s. En stéréo-inertiel, l'échelle est fixée à 1 (`page:7`, `page:8`).
- **Tracking et mapping** : le tracking n'optimise que les deux dernières frames, points fixes ; le mapping optimise une fenêtre glissante de keyframes et leurs points, avec les observations des keyframes covisibles à pose fixée (pas de marginalisation) (`page:8`, `page:15`).
- **Robustesse à la perte** : état « visually lost » sous 15 points suivis ; court terme : pose prédite par IMU et recherche des points dans une grande fenêtre image ; après 5 s, long terme : nouvelle carte VI active ; carte jetée si perte dans les 15 s suivant l'init IMU (`page:8`, `page:9`).
- **Reconnaissance de lieu à rappel amélioré** : pour chaque nouvelle keyframe, 3 candidates DBoW2 (hors covisibles) ; fenêtre locale (candidate + covisibles + points) ; alignement 3D-3D par RANSAC/Horn sur 3 appariements, Sim(3) si mono ou carte non mature, SE(3) sinon ; raffinement par matching guidé bidirectionnel en 2 passes ; vérification sur **3 keyframes covisibles déjà dans la carte** au lieu d'attendre 3 keyframes futures ; en VI, vérification des angles pitch/roll (gravité) (`page:9`).
- **Atlas multi-carte** : carte active + cartes non actives, une seule base DBoW2 ; relocalisation dans toutes les cartes ; **fusion de cartes** en deux temps : fenêtre de soudure (welding window = voisins covisibles des deux keyframes) avec BA local, puis propagation par optimisation du graphe essentiel ; variante VI incluant poses/vitesses/biais des 5 dernières keyframes temporelles reliées par préintégration ; fermeture de boucle analogue + BA global dans un thread séparé (limité en VI par un seuil de keyframes) (`page:5`, `page:6`, `page:10`, `page:11`).
- **Modèle de caméra abstrait** : projection, déprojection et jacobiens isolés ; pin-hole et Kannala-Brandt fisheye fournis ; relocalisation par MLPnP (rayons projectifs, indépendant du modèle) ; **stéréo non rectifiée** traitée comme deux caméras mono liées par une SE(3) constante, les zones de recouvrement donnant la vraie échelle, le reste étant exploité en mono (`page:6`).
- Pas de sémantique, pas de carte dense, pas de GPU : tout le papier est CPU (`page:11`).

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| Matériel | Intel Core i7-7700 à 3,6 GHz, 32 Go, **CPU uniquement** | toutes les expériences (`page:11`) |
| Entrées (timings) | 752 × 480 à 20 Hz, IMU 200 Hz, 1000 (mono) ou 1200 (stéréo) points ORB | EuRoC V202 (`page:15`) |
| Précision EuRoC, ATE RMS moyen | Mono 0,041 m* (V203 échouée) · Stéréo 0,084 m · Mono-inertiel **0,043 m** (échelle 0,9 %) · Stéréo-inertiel **0,035 m** (échelle 0,6 %) ; comparés : VINS-Mono 0,110, VI-DSO 0,089, OKVIS 0,231, ROVIO 0,224, MSCKF 0,414 (mono-inertiel) ; VINS-Fusion 0,138, Kimera 0,119, BASALT 0,051* (stéréo-inertiel) | médiane de 10 exécutions, alignement Sim(3) en mono, SE(3) sinon (`page:11`, `page:12`) |
| Gain déclaré | mono-inertiel « five to ten times more accurate » que MSCKF/OKVIS/ROVIO, plus de 2× VI-DSO et VINS-Mono ; stéréo-inertiel 3–4× Kimera et VINS-Fusion ; BASALT seul proche mais échoue sur V203 | EuRoC (`page:11`) |
| TUM-VI, salles (AR/VR) | ATE RMS moyen sur 6 séquences room : Mono 0,039 · Stéréo 0,068 · Mono-inertiel **0,011** · Stéréo-inertiel **0,009 m** (room1 : 0,008 m, 146 m parcourus) ; concurrents stéréo-inertiels room1 : OKVIS 0,06, ROVIO 0,16, BASALT 0,09 | médiane de 3 exécutions, fisheye, CLAHE, 1500 ORB (mono-in.) / 1000 (stéréo-in.) (`page:12`, `page:13`) |
| TUM-VI, couloirs / magistrale / extérieur | corridor1–5 stéréo-inertiel 0,01–0,21 m (300 m) ; magistrale 0,24–1,86 m (jusqu'à 918 m) ; outdoors 4,58–54,77 m (jusqu'à 2 656 m) ; slides (toboggan sombre) 0,41–0,49 m | vérité terrain seulement en début/fin, donc mesure de la dérive accumulée (`page:11`, `page:12`, `page:13`) |
| Dérive | outdoors1 single-session ≈ 60 m ; fortement réduite en multi-session après magistrale2 (Fig. 6) ; « errors in the order of 10 to 70 meters » en extérieur par dérive d'échelle et de biais accéléro faute de points proches | (`page:12`, `page:14`) |
| Multi-session EuRoC | Stéréo-inertiel 0,041 / 0,047 / 0,031 / 0,046 m (MH01-03, MH01-05, V101-103, V201-203) ; VINS-Mono 0,210 m sur MH01-05 ; ORB-SLAM3 **2,6×** plus précis que VINS-Mono en single-session, **3,2×** en multi-session | médiane de 5 exécutions (`page:5`, `page:13`) |
| Fréquence | « real time at 30-40 frames and at 3-6 keyframes per second » | (`page:14`) |
| Temps de tracking par image | Mono 21,5 ± 6,5 ms · Stéréo 31,5 ± 5,8 · Mono-inertiel 23,2 ± 15,0 · **Stéréo-inertiel 33,1 ± 9,3 ms** (dont extraction ORB 15,2, appariement stéréo 3,4, intégration IMU 0,22, prédiction de pose 0,15, suivi carte locale 11,5) | EuRoC V202 (`page:15`) |
| Temps de mapping par keyframe | 159–267 ms selon config (stéréo-inertiel 196,6 ± 54,5 ms, dont BA local 152,7 ± 38,4) ; carte V202 stéréo-inertielle : 135 keyframes, 9 761 points | (`page:15`) |
| Reconnaissance de lieu / fusion / boucle | ≈ 10 ms par keyframe annoncés dans le texte (`page:14`) ; Tableau VII : 3,5–5,9 ms ; fusion de cartes 121–287 ms ; fermeture de boucle (fusion + graphe essentiel) 119–570 ms ; BA global 1,1–4,1 s | multi-session V201–V203, thread séparé (`page:14`, `page:15`) |
| Initialisation IMU | 5 % d'erreur d'échelle à 2 s, 1 % à 15 s (vs 15 s pour ORB-SLAM-VI, 20–30 s pour VI-DSO) | EuRoC (`page:5`, `page:8`) |
| Mémoire / charge CPU / énergie | non rapporté | — |
| Comparaison de temps avec d'autres systèmes | non rapportée (« beyond the scope of this work ») | (`page:14`) |

## Ce que ça dit du tracking du Quest
- **Même famille algorithmique** : Oculus Insight est un VI-SLAM à landmarks avec carte persistante, relocalisation et reconnaissance de lieu (voir [dossier Insight](../../supports/meta2019_oculus-insight-quest/dossier.md)). ORB-SLAM3 est la version académique ouverte la plus proche de ce cahier des charges : carte de points 3D réutilisable, relocalisation dans toutes les cartes de l'Atlas, fusion de cartes entre sessions (`page:5`). Il indique quelle précision ce type d'architecture atteint sur un matériel de recherche : **moins de 1 cm d'ATE RMS en stéréo-inertiel dans une pièce** (`page:13`), face à l'objectif « less than a millimeter » revendiqué sans mesure par Meta.
- **Différences structurelles** : ORB-SLAM3 traite 1 ou 2 caméras à 20 Hz et un IMU à 200 Hz sur un i7 de bureau (`page:15`) ; le Quest 3/3S fusionne 4 caméras monochromes + IMU (≈ 1 kHz) sur un SoC mobile avec DSP. Le papier ne traite **ni** le multi-caméra au-delà de la stéréo, **ni** la prédiction de pose pour l'affichage, **ni** les contraintes embarquées (voir [Kuo 2020](../kuo2020_multicam-slam/fiche.md), [Nagy 2020](../nagy2020_faster-than-fast/fiche.md)). Il note seulement que l'IMU « allows to estimate pose at IMU rate, which is orders of magnitude higher than frame rate », ce qu'Insight fait à 1 kHz (`page:16`).
- **Ce que le papier apprend sur la pose que mote récupère** : (a) la pose d'un VI-SLAM en zone déjà cartographiée est à **dérive quasi nulle** grâce à l'association moyen terme (`page:2`) : une capture mote en boucle dans une pièce bénéficie du même effet ; (b) l'**échelle métrique** vient de l'IMU (et de la stéréo) et se stabilise à environ 1 % en 15 s après le démarrage (`page:8`) : les premières secondes d'une session Quest sont probablement les moins fiables en échelle ; (c) la **fermeture de boucle corrige la carte a posteriori** par BA global dans un thread séparé (`page:6`, `page:14`) : si le casque fait de même, les poses enregistrées par mote à un instant t peuvent être incohérentes avec la carte corrigée plus tard, sauf à relire les poses des keyframes après correction ; (d) le cas d'échec principal est le **manque de texture** (`page:15`), ce qui rejoint la limite du Quest 3 dans le noir.
- **Ordres de grandeur à rapprocher de SP-0** : l'erreur médiane Quest vs COLMAP mesurée (≈ 4–6 mm) est du même ordre que l'ATE RMS d'ORB-SLAM3 stéréo-inertiel en salle (6–12 mm, `page:13`), ce qui rend plausible que le casque atteigne une précision de classe « SLAM académique de pointe » sans que mote ait à refaire du SLAM.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. État de l'art / ce que fait le casque | Référence de la génération « optimisation + features + carte réutilisable » ; le Tableau I compare 19 systèmes (capteurs, features, association, estimation, relocalisation, boucles, multi-carte, fisheye, précision/robustesse qualitatives, code) (`page:4`). Fournit le vocabulaire court/moyen/long terme + multi-carte pour décrire Insight (`page:2`). |
| 2. Poses pour 3DGS (piste mote, H-01) | Donne le plancher de qualité atteignable par un VI-SLAM temps réel : **≈ 1 cm d'ATE RMS** dans une pièce, échelle à 0,6–0,9 % (`page:12`, `page:13`). Les poses sont des keyframes à 3–6 Hz plus des frames à 20 Hz (`page:14`) : le raffinement à l'entraînement 3DGS doit absorber une erreur centimétrique et une incertitude d'échelle de l'ordre du pour-cent. Rien sur NeRF/3DGS. |
| 3. Temps réel et contraintes embarquées | Budget CPU mesuré : 33 ms/frame stéréo-inertiel, 200 ms/keyframe de mapping, BA global jusqu'à 4 s hors de la boucle temps réel (`page:15`). Aucune mesure mobile, GPU, DSP, mémoire ou énergie. |
| 4. Évaluation (métriques, protocoles, datasets) | Protocole standard : ATE RMS après alignement Sim(3)/SE(3), erreur d'échelle \|1−s\|, médiane de 10 (EuRoC) ou 3 (TUM-VI) runs, Fig. 4 des 10 runs pour la robustesse (`page:11`). Datasets EuRoC (11 séq.) et TUM-VI (28 séq., 6 environnements ; vérité terrain seulement début/fin sauf room) ; TUM-VI **room** désignée comme représentative AR/VR (`page:11`, `page:13`). |

## Pour (vis-à-vis de notre problématique)
- Seul système ouvert du corpus qui réunit VI-SLAM, carte réutilisable, multi-session, fisheye et stéréo non rectifiée, la combinaison la plus proche de ce qu'un casque doit faire (`page:2`, `page:3`).
- Chiffres de précision explicitement rattachés au cas AR/VR (TUM-VI room : 9 mm stéréo-inertiel) (`page:13`), directement comparables au spike SP-0.
- Tableaux de temps détaillés par étape (extraction ORB, appariement stéréo, IMU, BA local, reconnaissance de lieu, fusion, BA global) qui donnent une décomposition de budget utilisable pour raisonner sur l'embarqué (`page:15`).
- Code public et largement réutilisé (par ex. [Photo-SLAM](../huang2024_photo-slam/fiche.md) s'appuie dessus pour des poses alimentant un 3DGS) ; baseline disponible pour rejouer nos captures Quest si on exporte les images.
- Recommandations pratiques : stéréo-inertiel = configuration la plus robuste et précise ; mono-inertiel presque équivalent sauf rotations pures ; IMU difficile à initialiser en mouvement lent ou sans roulis/tangage (`page:16`).

## Contre / limites
- **CPU de bureau uniquement** (i7-7700) ; aucune mesure sur ARM, mobile, GPU ou DSP, et pas de comparaison de temps avec les autres systèmes (`page:11`, `page:14`).
- 1 ou 2 caméras seulement ; pas de multi-caméra à 4 vues ni de prédiction de pose/latence d'affichage : ne couvre pas les spécificités du Quest.
- Échec sur zones peu texturées ; le matching de descripteurs ORB est jugé par les auteurs « less robust for tracking than Lucas-Kanade » (VINS-Mono et BASALT font mieux sur certaines séquences slides) (`page:12`, `page:15`).
- Dérive d'échelle et de biais en extérieur sans points proches (10–70 m) ; suppression ad hoc des points à plus de 20 m en extérieur (`page:12`).
- BA global de fermeture de boucle désactivé en VI au-delà d'un seuil de keyframes (`page:11`) ; précision des poses intermédiaires (non keyframes) non analysée séparément.
- Résultats concurrents en partie repris des publications d'origine (notes du Tableau II : GT brute vs traitée, trajectoire keyframes vs complète) : comparaison pas totalement homogène (`page:12`).
- Pas de mesure de latence, de mémoire ni d'énergie.

## Idées à creuser pour mote
- *Hypothèse* : la précision Quest mesurée en SP-0 (4–6 mm) est cohérente avec un VI-SLAM de classe ORB-SLAM3 (6–12 mm en salle, `page:13`) ; formuler H-01 en termes de **budget d'erreur de pose toléré par 3DGS** et vérifier si un raffinement de poses à l'entraînement suffit pour environ 1 cm / 0,5° d'erreur.
- *Protocole* : exporter les images passthrough + poses MRUK et rejouer ORB-SLAM3 (mono-inertiel si l'IMU est accessible, mono sinon) pour obtenir une **seconde référence indépendante de COLMAP**, bien plus rapide (temps réel à 20 Hz) ; aligner par Sim(3) et reporter ATE RMS + erreur d'échelle comme dans le papier (`page:11`).
- *Expérience* : tester l'effet des **15 premières secondes** (maturation de l'échelle) : commencer la capture mote après un délai, ou comparer les poses Quest de début de session avec celles d'une relocalisation ultérieure (`page:8`).
- *Expérience* : provoquer une fermeture de boucle (revenir au point de départ) et vérifier si les poses Quest déjà enregistrées « sautent » ; si oui, ne garder que les poses relues après correction, ou laisser le raffinement 3DGS absorber le saut (`page:6`, `page:14`).
- *Réutilisation* : le schéma « keyframes à 3–6 Hz + BA local » suggère de sélectionner pour 3DGS les images proches des keyframes (parallaxe suffisante) plutôt que toutes les frames à 20–30 Hz (`page:14`).
- *Comparatif* : construire le tableau « ATE room TUM-VI » pour ORB-SLAM3, VINS, Basalt, OpenVINS, Kimera, DROID-SLAM à partir des fiches de l'axe, comme référence de « ce qu'un SLAM temps réel sait fournir ».

## Citations clés
> « Notably, our stereo-inertial SLAM achieves an average accuracy of 3.5 cm in the EuRoC drone and 9 mm under quick hand-held motions in the room of TUM-VI dataset, a setting representative of AR/VR scenarios. » (`doc:4d11951/tier:standard/page:2`)

> « Mid-term data association, matching map elements that are close to the camera whose accumulated drift is still small. These can be matched and used in BA in the same way than short-term observations and allow to reach zero drift when the systems moves in mapped areas. » (`doc:4d11951/tier:standard/page:2`)

> « We propose a novel fast initialization method based on Maximum-a-Posteriori (MAP) estimation that properly takes into account visual and inertial sensor uncertainties, and estimates the true scale with 5% error in 2 seconds, converging to 1% scale error in 15 seconds. » (`doc:4d11951/tier:standard/page:5`)

> « Table VI summarizes the running time of the main operations performed in the tracking and mapping threads, showing that our system is able to run in real time at 30-40 frames and at 3-6 keyframes per second. » (`doc:4d11951/tier:standard/page:14`)

> « Furthermore, the inertial sensor allows to estimate pose at IMU rate, which is orders of magnitude higher than frame rate, being a key feature for some use cases. » (`doc:4d11951/tier:standard/page:16`)

## Liens
- Papiers liés :
  - [ORB-SLAM (Mur-Artal 2015)](../murartal2015_orb-slam/fiche.md) — système d'origine (ORB, covisibilité, DBoW2) sur lequel ORB-SLAM3 est bâti (`page:3`).
  - [VINS-Mono](../qin2018_vins-mono/fiche.md) — concurrent principal mono-inertiel ; 2,6× moins précis en single-session, 3,2× en multi-session (`page:5`, `page:13`).
  - [VINS-Fusion](../qin2019_vins-fusion/fiche.md) — concurrent stéréo-inertiel (0,138 m vs 0,035 m sur EuRoC) (`page:12`).
  - [Kimera](../rosinol2020_kimera/fiche.md) — VIO stéréo-inertiel + boucles DBoW2 ; 3–4× moins précis (`page:5`, `page:11`).
  - [Basalt](../usenko2020_basalt/fiche.md) — seul système « approché » en précision stéréo-inertielle ; meilleur sur certaines séquences slides (`page:11`, `page:12`).
  - [OpenVINS](../geneva2020_openvins/fiche.md) — non cité dans le papier ; à comparer sur le même protocole.
  - [Delmerico 2018 (benchmark VIO)](../delmerico2018_vio-benchmark/fiche.md) — source des chiffres MSCKF/OKVIS/ROVIO du Tableau II (réf. [78]) (`page:12`).
  - [Multi-camera SLAM (Kuo 2020)](../kuo2020_multicam-slam/fiche.md), [Eckenhoff 2019](../eckenhoff2019_multicam-vins/fiche.md) — extension au multi-caméra que le Quest utilise et qu'ORB-SLAM3 ne couvre pas.
  - [Nagy 2020 (Faster than FAST)](../nagy2020_faster-than-fast/fiche.md) — coût de l'extraction de features sur embarqué (ici 12–16 ms sur i7, `page:15`).
  - [Project Aria (Engel 2023)](../engel2023_project-aria/fiche.md) — description publique la plus proche de la pile Meta (VIO 1 kHz, SLAM hors ligne).
  - [Photo-SLAM](../huang2024_photo-slam/fiche.md) et [Tosi 2024 (survey NeRF/GS SLAM)](../tosi2024_nerf-gs-slam-survey/fiche.md) — passage des poses ORB-SLAM3 à une carte 3DGS.
  - [Banaszczyk 2024 (précision positionnement VR)](../banaszczyk2024_vr-positioning-accuracy/fiche.md) — mesure de la précision des casques, à mettre en regard du 9 mm de TUM-VI room.
  - [3DGS (Kerbl 2023)](../kerbl2023_3dgs/fiche.md) — consommateur des poses ; H-01 porte sur la tolérance de son entraînement à l'erreur de pose SLAM.
- Support : [dossier Oculus Insight](../../supports/meta2019_oculus-insight-quest/dossier.md).
