---
citekey: liu2025_robotic-mr-gs-crosslayer
mineru_doc: ff0a998
type: article de revue   # format IEEE journal (14 p.), venue non indiquée ; version préliminaire à IEEE INFOCOM 2025 Workshop NetRobiCS ; arXiv 2508.08624v2 [cs.RO]
statut: fiche complète
tags: [3dgs, robotique, mixed-reality-robotique, optimisation-cross-layer, minlp, penalty, difference-of-convex, allocation-de-puissance, content-switching, jumeau-numerique, ros, carla, canal-simule, qos-qoe]
---

# Communication Efficient Robotic Mixed Reality with Gaussian Splatting Cross-Layer Optimization

**Référence :** Chenxuan Liu, He Li, Zongze Li, Shuai Wang, Wei Xu, Kejiang Ye, Derrick Wing Kwan Ng, Chengzhong Xu (2025). *Communication Efficient Robotic Mixed Reality with Gaussian Splatting Cross-Layer Optimization.* arXiv 2508.08624v2 [cs.RO], 3 sept. 2025. Venue de la version longue non indiquée ; version préliminaire : « Green robotic mixed reality with Gaussian splatting », IEEE INFOCOM Workshop NetRobiCS 2025 (`doc:ff0a998/tier:standard/page:1`, réf. [1]). Affiliations : SIAT-CAS, Univ. Macau, Peng Cheng Lab, UNSW. Lien : [arXiv 2508.08624](https://arxiv.org/abs/2508.08624). Code : non mentionné.
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
En « robotic mixed reality » (RoboMR : un robot réel et des agents virtuels dans un simulateur partagé), le robot doit envoyer ses images caméra au serveur. GSMR le remplace, image par image, par l'envoi de sa **seule pose (192 bits)** : le serveur **rend la vue à partir d'un modèle 3DGS** de l'environnement (« mémoire »). Un problème d'optimisation mixte (**GSCLO**) décide pour chaque frame **image ou pose** (x_t ∈ {0,1}) et la **puissance d'émission montante du robot** (p_t), pour minimiser l'erreur d'image sous contraintes de débit et de puissance. Il est résolu par pénalité + algorithme DC (**APO**) (`page:1–6`). **Ni casque, ni utilisateur humain, ni mesure de fps ou de latence.**

## Problème traité
- Les systèmes RoboMR doivent remonter des images haute résolution à haute fréquence par radio : coût de communication élevé (`page:1`).
- Les allocateurs de ressources existants (1) n'exploitent pas la **mémoire** des exécutions précédentes, (2) séparent couche application (codage) et couche physique (puissance), (3) sont surtout testés en simulation (`page:1–2`).
- Le modèle GS peut diverger du réel (éclairage, changements de scène) : c'est le **« memory bias »**, qui impose d'envoyer une vraie image quand le GS est mauvais (`page:1`).

## Méthode / contributions
- **Boucle RoboMR** (Fig. 1, `page:3`) par pas de temps τ : captation (image réelle r_t sur le robot, image virtuelle v_t sur le serveur) → communication montante → fusion par masque m_t = d_t ⊙ r_t + (1 − d_t) ⊙ v_t → commande u_t du robot à partir de l'image MR.
- **Encodeur à bascule** (éq. 6–7, `page:4`) : c_t = x_t·r_t + (1 − x_t)·s_t. Si x_t = 0, le serveur reconstruit r̂_t = Φ(s_t) par rendu 3DGS ([Kerbl 2023](../kerbl2023_3dgs/fiche.md), réf. [24]).
- **Perte GS par frame** L_t (éq. 9) : L1 + D-SSIM (λ = 0,2) entre l'image MR avec image réelle et l'image MR avec image GS. L'objectif devient Θ_t(x_t) = L_t·(1 − x_t) (éq. 8).
- **Problème GSCLO P_GS** (éq. 11, `page:4–5`) :

| Élément | Contenu |
|---|---|
| Variables | x_t ∈ {0,1} (envoyer l'image ou la pose), p_t ≥ 0 (puissance d'émission **du robot**, liaison montante), pour **toutes les frames t = 1…T à la fois** |
| Objectif | min (1/T) Σ_t L_t·(1 − x_t) : erreur d'image moyenne (proxy de qualité) |
| C1 : transmission (QoS) | τ·B·log₂(1 + \|h_t\|²p_t/σ²) ≥ x_t·I + (1 − x_t)·S : les données doivent passer dans le pas de temps τ |
| C2 : puissance (ressource) | (1/T) Σ p_t ≤ P (budget moyen de puissance radio du robot) |
| Nature | MINLP ; B&B (Mosek) exponentiel en T |

- **Solveur APO** (Algorithme 1, `page:5–6`) :
  1. relaxation x_t ∈ [0,1] + pénalité φ(x) = (1/β) Σ x_t(1 − x_t), équivalente au problème binaire pour β adéquat ;
  2. φ est une différence de fonctions convexes : linéarisation (éq. 14), suite de sous-problèmes convexes résolus par **CVXPY**, complexité O((2T)^3,5) par itération ; tout point limite est KKT ;
  3. **initialisation par classement** (éq. 17) : trier les L_t par ordre décroissant, envoyer l'image pour les μ premières frames, μ trouvé par bissection en O(log T). Optimale si les gains de canal sont égaux (Prop. 2).
- **Variantes** :
  - **robuste** (`page:6–7`) : erreur d'estimation du canal gaussienne, probabilité de coupure via la fonction Q de Marcum, contrainte P_out ≤ ε ; résolue par recherche locale itérée + bissection (BILS, Algorithme 2) ;
  - **basse consommation** Q_GS (`page:7–8`) : **min puissance s.c. perte ≤ L_th**, avec L_th ∈ [0,02 ; 0,04] (PSNR 30–40 dB). Version par frame en **forme close** (Prop. 3) : envoyer l'image **si et seulement si L_t > L_th**. Facteur d'économie ΔP (éq. 33) ;
  - **multi-robot** (`page:8`) : N antennes, récepteur zero-forcing, même structure, même solveur.
- Canal : gains obtenus par une **carte radio** (position → atténuation), apprise par mesures ou ray tracing (Sionna) (`page:7`). Les L_t supposent de connaître l'écart GS/réel ; en pratique « estimé par des images pilotes » (note 3, `page:13`).

## Architecture (question spécifique)
| Aspect | Liu 2025 (GSMR/GSCLO) |
|---|---|
| Ce qui transite | **Montant (robot → serveur)** : soit l'image RGB (I = 537,6 kbit = 67,2 KB, robot LIMO ; 13,84 Mbit = 1,73 MB, chien Go2), soit la pose (6 flottants, **S = 192 bits**). Le retour de l'image MR vers le robot **n'est pas modélisé** (`page:9`, `page:12`) |
| Où se fait le rendu GS | **Serveur uniquement** (CARLA + modèle GS) ; rien sur le robot |
| Débit | Débit de Shannon ; B = **1 MHz** (LIMO) ou **20 MHz** (Go2) ; τ = 0,1 s (10 frames/s) ; σ² = −60 dBm. Revendication : **< 200 bits/frame** quand le GS suffit (`page:2`, `page:9`, `page:12`) |
| Latence | **Non mesurée**. Seule contrainte temporelle : transmission dans τ = 100 ms |
| Réseau réel ou simulé | Images, poses et trajectoires **réelles** (ROS) ; **canal radio simulé** : Rice (K-facteur 0–30 dB, d = 10 m, α = 3) ou Rayleigh avec atténuation murale −10 dB ; moyenne de 50 tirages (`page:9`, `page:13`) |
| Matériel | Serveur : Ryzen 9 5900X + **RTX 3090 Ti** (CARLA). Robot : **AgileX LIMO** (lidar 2D, caméra RGB-D, **Jetson Nano**) dans un bac à sable 4 m × 4 m ; **Unitree Go2** dans un immeuble de bureaux (`page:9`, `page:12`) |
| Casque / stéréo / fps | **Aucun casque, aucune stéréo, fps de rendu GS non rapportés** |

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| FPS | **Non rapporté** (ni temps de rendu GS) | — |
| Qualité (PSNR) | APO **> 30 dB** pour P = 10–40 mW ; **≥ +5 dB** par rapport aux autres schémas ; lecture Fig. 7b : ≈ 33,5 dB (10 mW) à ≈ 44 dB (40 mW), contre ≈ 23 dB (Fairness) à ≈ 39 dB (Search) | LIMO, K = 0 dB, T = 288 (`page:10`) |
| Qualité (perte, SSIM) | Perte APO < 0,03, au moins −10 % par rapport aux autres ; SSIM « très proche de 1 » à forte puissance | `page:10` |
| APO vs MaxImg (plus d'images) | P = 5–8 mW : PSNR 26,95–29,08 contre 26,49–28,57 ; SSIM 0,961–0,965 contre 0,955–0,960 | Tab. II (`page:11`) |
| Robuste (BILS) | ≈ −10 % de perte, ≈ +2 dB par rapport à APO sous incertitude de canal ; coupure < ε = 0,1 | ω² = 0,04\|h̃\|², K = 10 dB (`page:11–12`) |
| Économie de puissance | **≥ 2 dB** pour L_th ∈ [0,01 ; 0,04] ; **> 6 dB (−75 %)** à L_th = 0,03 | Q_GS vs RoboMR, K = 30 dB (`page:12`) |
| Multi-robot | PSNR APO 31,1–40,5 dB contre 13,3–23,4 dB (GS seul, MaxRate) | N = 4, K = 2, T = 433, Tab. III (`page:12`) |
| Temps de calcul du solveur | APO ≈ **2 s (T = 100) à ≈ 6 s (T = 250)** ; Mosek ≈ 250 s à ≈ 2 500 s (lecture Fig. 6a, échelle log) ; « au moins 100× » plus rapide que Mosek. Convergence : ‖Δx‖ < 10⁻⁴ en 35 itérations | P = 5 mW, K = 30 dB (`page:9–10`) |
| Entraînement GS | Non rapporté (H = 288 images LIMO, H = 400 images Go2) | `page:9`, `page:12` |
| Mémoire / taille du modèle | Non rapportée | — |

## Comparaison avec ECO-GS et l'éq. 1 de Kamdjou
**Même groupe** (Liu, Wang, Ye, Xu sont co-auteurs d'[ECO-GS](../wan2025_edge-collab-gs/fiche.md), qui cite ce travail comme réf. [6]). Liu 2025 est le **prédécesseur** : même machinerie (bascule binaire + puissance, pénalité (1/β)Σx(1−x), majoration convexe DC/MM, perte L1 + D-SSIM de 3DGS).

| | [Kamdjou 2024, éq. 1](../kamdjou2024_xr-dt-iiot/fiche.md) | Liu 2025 (GSCLO) | [ECO-GS (Wan 2025)](../wan2025_edge-collab-gs/fiche.md) |
|---|---|---|---|
| Forme | Somme pondérée f(QoS)·W + g(QoE)·W + h(Res)·W s.c. seuils ; non résolue | **ε-contrainte** : min erreur s.c. débit et puissance ; et forme duale Q_GS : min puissance s.c. erreur ≤ L_th | ε-contrainte : min erreur s.c. délai, puissance, capacité serveur |
| QoE | g(QoE) | Erreur image L_t vs **image réelle** (supposée connue ou estimée) | Écart grand/petit modèle (sans vérité terrain) |
| QoS | ≥ Target_QoS | Données transmises dans τ = 100 ms | Délai bout-en-bout ≤ 60 ms |
| Ressources | ≤ Max_power | Puissance radio **moyenne du robot** | Puissance radio de l'edge + nombre d'utilisateurs servis |
| Décision | — | **Quoi envoyer** (image/pose) + puissance, **planifiée sur T frames à l'avance** | **Où rendre** (local/edge) + puissance, par pas de temps |
| Solveur | aucun | APO (secondes pour T = 100–250) | PMM (16–58 ms) puis DNN imitateur (< 1 ms) |
| Côté appareil (fps, GPU, énergie de rendu, LOD, fovéa) | cité qualitativement | **absent** | **absent** |

**Verdict P3′ :** Liu 2025 **n'occupe pas P3′**. Il n'y a ni casque, ni utilisateur, ni rendu côté appareil : la seule décision est **binaire** (image ou pose) et porte sur la **couche radio montante** d'un robot. Aucune variable de rendu (LOD, budget de Gaussiennes, couches, fovéa, compression), aucune contrainte de fps ou de motion-to-photon, aucune ressource GPU/énergie de rendu. La planification est **hors ligne sur un horizon connu** (les L_t et h_t de toutes les frames doivent être connus d'avance), pas une boucle de contrôle en ligne. Avec ECO-GS, il confirme seulement que ce groupe a formalisé le compromis qualité/radio pour la 3DGS : **l'antériorité reste « côté radio »**, et P3′ garde sa nouveauté côté casque. À citer comme antériorité méthodologique (formalisme et solveur), pas comme concurrent.

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Cadre de la « mixed reality robotique » (sens différent de la MR casque) ; utile pour P5 (jumeau numérique avec robot) |
| 2. Gaussiennes depuis SfM, covariance | Nul (3DGS standard entraîné sur 288–400 images du robot) |
| 3. Rendu rapide, visibilité, casque | Nul : rendu serveur, pas de casque |
| 4. Évaluation | PSNR/SSIM/perte et puissance radio ; pas de fps, pas de latence |

## Pour (vis-à-vis de notre problématique)
- **Formalisme réutilisable pour P3′** : pénalité binaire + DC, initialisation par classement, bissection. Et surtout la **règle en forme close** de Q_GS (Prop. 3) : « monter en qualité si l'erreur prédite dépasse L_th ». C'est exactement la forme d'un contrôleur à seuil, transposable à un choix de LOD par frame.
- **Correspondance chiffrée perte ↔ PSNR** : L1 + D-SSIM de 0,02–0,035 ≈ 30–40 dB (`page:8`, `page:10`). Utile pour fixer une contrainte de qualité L_th dans l'éq. 1 de Kamdjou.
- Idée de **« mémoire » 3DGS + correction ponctuelle** par données réelles quand le modèle diverge : pertinent pour **P5** (jumeau numérique dont le décor 3DGS vieillit).
- Données réelles (robots, ROS, deux environnements), même si le canal est simulé.

## Contre / limites
- **Aucune mesure de rendu** : ni fps, ni temps de rendu GS, ni résolution des images, ni latence réelle.
- **Canal radio entièrement simulé** (Rice/Rayleigh, tirages indépendants) ; pas de trace Wi-Fi/5G.
- **Planification non causale** : l'optimisation sur T frames suppose de connaître d'avance toutes les pertes L_t (qui exigent l'image réelle) et tous les canaux ; les auteurs évoquent un horizon glissant sans l'évaluer (`page:10`).
- **Coût du solveur** : APO prend plusieurs secondes pour 100–250 frames, incompatible en l'état avec une décision par frame à 72–90 Hz (ECO-GS a dû ajouter un imitateur DNN).
- Le « mixed reality » désigne une fusion d'images pour l'**apprentissage robotique**, pas une expérience utilisateur XR : pas de QoE humaine.
- Pas de LPIPS ; comparaison uniquement à des allocateurs radio, pas à des codecs vidéo.

## Idées à creuser pour une approche novatrice
- *Hypothèse (P3′)* : transposer Q_GS côté casque : **min coût (temps GPU, énergie) s.c. erreur prédite ≤ L_th et temps de frame stéréo ≤ 1/90 s**, avec variables continues (τ de Hierarchical 3DGS, couches LapisGS, rayon fovéal). La forme close à seuil de la Prop. 3 donnerait un contrôleur léger, sans solveur en ligne.
- *Hypothèse (P3′)* : remplacer la planification sur horizon par un **horizon glissant** court (quelques frames) et mesurer la perte d'optimalité ; c'est le point que Liu 2025 laisse ouvert.
- *Hypothèse (P5)* : dans un jumeau numérique industriel, n'envoyer que les **poses OPC-UA** des pièces mobiles tant que le décor 3DGS reste fidèle, et déclencher une **mise à jour de la capture** quand l'écart (estimé par image pilote) dépasse un seuil, sur le modèle du « memory bias ».
- *Hypothèse (P1′)* : la bascule image/pose par frame deviendrait une bascule **par région** (local/edge), avec la même initialisation par classement des erreurs par tuile.

## Citations clés
> « GSMR, which enables the simulator to opportunistically render a photo-realistic view from the robot's pose by calling "memory" from a GS model, thus reducing the need for excessive image uploads » (`doc:ff0a998/tier:standard/page:1`)

> « robotic mixed reality can be achieved with ultra-low communication costs (< 200 bits/frame) if Gaussian splatting is leveraged properly » (`doc:ff0a998/tier:standard/page:12`)

> « the GS parameters will have more significant impacts on the physical layer design than those of the wireless channels. Therefore, the principle of GSMR is to allocate more power to frames associated with high GS losses. » (`doc:ff0a998/tier:standard/page:8`)

> « the existing GS scheme works poorly in dynamic scenarios. This is due to the inherent limitation of static reconstruction. » (`doc:ff0a998/tier:standard/page:13`)

## Liens
- Papiers liés :
  - [Wan 2025, ECO-GS](../wan2025_edge-collab-gs/fiche.md) : successeur du même groupe, même formalisme, appliqué au rendu local/edge avec solveur < 1 ms.
  - [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) : éq. 1 QoS/QoE/ressources ; Liu 2025 en est une instanciation ε-contrainte côté radio.
  - [Kerbl 2023, 3DGS](../kerbl2023_3dgs/fiche.md) : modèle GS utilisé et perte L1 + D-SSIM reprise comme objectif.
  - [Mirocha 2025](../mirocha2025_beyond-dt/fiche.md), [Warsinke 2026](../warsinke2026_gs-mesh-dt-vr/fiche.md) : jumeaux numériques 3DGS, cadre de P5.
  - [Sun 2024, 3DGStream](../sun2024_3dgstream/fiche.md) : autre réponse au caractère statique du GS (mise à jour des Gaussiennes par frame).
  - [Hiroi 2022, NeARportation](../hiroi2022_nearportation/fiche.md) : rendu déporté avec latence réellement mesurée, ce qui manque ici.
