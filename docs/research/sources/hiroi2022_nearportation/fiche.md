---
citekey: hiroi2022_nearportation
mineru_doc: 2b2dc79
type: conférence   # papier court 5 pages, « preprint for VRST '22 » (ACM VRST 2022, Tsukuba)
statut: fiche complète
tags: [nerf, instant-ngp, rendu-distant, remote-rendering, webrtc, stereo, afficheur-autostereoscopique, latence, round-trip-latency, protocole-de-mesure, reseau-reel]
---

# NeARportation: A Remote Real-time Neural Rendering Framework

**Référence :** Yuichi Hiroi, Yuta Itoh, Jun Rekimoto (2022). *NeARportation: A Remote Real-time Neural Rendering Framework.* Preprint pour ACM VRST '22 (28th ACM Symposium on Virtual Reality Software and Technology), Tsukuba, 29 nov.–1er déc. 2022, 5 pages (`doc:2b2dc79/tier:standard/page:1`). Affiliations : Sony CSL Kyoto, University of Tokyo, RIKEN AIP. Lien : [arXiv 2210.12398](https://arxiv.org/abs/2210.12398). Code : non mentionné (vidéo supplémentaire seulement, `page:3`).
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Un client léger envoie **la pose de chaque œil** à un serveur GPU qui fait tourner **un processus instant-ngp (NeRF) par œil** ; les images rendues reviennent en **vidéo WebRTC (VP8)** et sont plaquées sur un quad aligné sur chaque caméra virtuelle. Sur un afficheur autostéréoscopique Sony ELF-SR1, le prototype atteint **35 à 40 fps en full HD stéréo**, mais avec une **latence aller-retour mesurée de 100 à 400 ms** (`page:1`, `page:4`). **Ce n'est pas du 3DGS et ce n'est pas un casque.**

> **Correction importante pour la base :** NeARportation **n'atteint pas** < 20 ms. Ce chiffre est un **seuil cité** (« an RTL exceeding 20 ms is perceived to have detrimental effects ») que les auteurs jugent eux-mêmes « difficile » à tenir en rendu déporté (`page:4`). [Li 2025](../li2025_rf-xr-survey/fiche.md) le reprend comme **objectif** (« crucial to minimize RTL below 20 ms »), pas comme mesure. La valeur mesurée est de **100 à 400 ms** (Fig. 4b, `page:4/block:4`).

## Problème traité
- Reproduire l'apparence photoréaliste d'objets réels (brillance, transparence, diffusion sous-surfacique, couleurs structurelles) en AR/VR. La photogrammétrie suppose une radiance constante (aspect « plâtre ») ; les dômes de mesure sont coûteux ; le ray tracing temps réel demande > 11 GB de VRAM (`page:1–2`).
- Les NeRF temps réel existent, mais le compromis **résolution × nombre de vues × ressources de calcul** reste ouvert sur un appareil XR. D'où l'idée de déporter le rendu neuronal (`page:2`).

## Méthode / contributions
- **Architecture** (Fig. 1, `page:2`) :
  - **Client** : capteur de pose tête (caméra), afficheurs, pairs RTC, moteur de jeu (Unity).
  - **Serveur** : un processus principal (1 récepteur + 1 émetteur par pair), **autant de renderers NeRF et de pairs RTC que d'afficheurs du client** (donc 2 pour la stéréo). Communication inter-processus par **nanomsg** (TCP port à port) (`page:2–3`).
- **Protocole par frame** (`page:2`) :
  1. Hors ligne : le client téléverse une vidéo de l'objet ; le serveur entraîne le NeRF.
  2. À la connexion P2P, le serveur envoie les intrinsèques de la caméra de capture ; le client configure une caméra virtuelle par vue (taille réelle de l'objet).
  3. À chaque frame, le client envoie **la matrice de pose de chaque caméra virtuelle, étiquetée par œil** (gauche/droite).
  4. Le récepteur route la pose vers le renderer de l'œil correspondant. Chaque renderer a un **tampon de pose écrasé par la plus récente** : dès qu'un rendu finit, le NeRF prend la dernière pose disponible (les poses intermédiaires sont abandonnées).
  5. L'image rendue part par **MediaStream WebRTC**. Le client la plaque sur un **quad planaire aligné sur le champ de vision** de la caméra virtuelle.
- **Implémentation** (`page:2–3`) :

| Élément | Choix |
|---|---|
| Serveur | Ubuntu 20.04, 2× Intel i9-10920X, **2× RTX 3090** (un instant-ngp par GPU, donc un par œil), **Ethernet 1 GbE filaire** |
| Renderer | **instant-ngp** via binding Python ; rendu limité à la zone au-dessus de la mire ChArUco (pour gagner en fps) |
| WebRTC | Momo (client) + Ayame Labo (signalisation), **codec VP8** ; côté Unity : Microsoft MixedReality-WebRTC |
| Client | Windows 10, AMD Ryzen 5950X, **RTX 3090**, **Wi-Fi 2,4 GHz** sur LAN 1 GbE, segment réseau différent du serveur |
| Affichage | **Sony ELF-SR1** : afficheur autostéréoscopique (LCD 3840×2160 incliné à 45°, microlentilles, caméra de suivi de tête rapide). Rendu à **mi-résolution du panneau (full HD)** ; Unity 2020.3.36f + Sony Spatial Display SDK fusionne les deux vues selon la géométrie des microlentilles |
| Entraînement | Poses caméra par **mire ChArUco** (pas COLMAP) pour avoir l'échelle réelle et donc une disparité correcte ; instant-ngp 3×10⁴ pas, batch 2¹⁸, **≈ 4 min** (`page:3`) |

## Mesure de latence (référence de protocole pour P6)
- **Méthode** (`page:4`) : le client ajoute un **horodatage en ms** à chaque paquet de pose ; le serveur renvoie cet horodatage **intact avec l'image correspondante**, plus le **temps de rendu instant-ngp** de cette image. Le client calcule :
  - **RTL** = heure courante − horodatage reçu ;
  - **fps** = intervalle entre horodatages reçus ;
  - la **part du rendu NeRF** dans la RTL.
- Mesure sur **10 s**, l'utilisateur bouge la tête pendant la mesure.
- **Ce que cette RTL couvre** (analyse de la fiche) : de l'émission de la pose à la réception de l'image par le client. Elle **n'inclut pas** la latence du capteur de suivi ni l'affichage (composition, balayage de l'écran). Ce n'est donc **pas une motion-to-photon** au sens strict, mais une borne inférieure de celle-ci.
- **Horloge unique** côté client : pas de problème de synchronisation d'horloges entre machines. Méthode simple et directement réutilisable.

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| FPS | **≈ 35 à 40 fps** ; chutes ≈ 4 fps pendant une vérification P2P périodique (≈ 200 ms), puis ≈ 25–33 fps pendant ≈ 1 s de rétablissement (lecture Fig. 4a) | Stéréo réelle (un flux par œil, un GPU par œil), full HD par vue, réseau réel Wi-Fi 2,4 GHz (`page:4/block:3`) |
| Latence aller-retour (RTL) | **≈ 100 à 400 ms**, oscillante (lecture Fig. 4b : majoritairement 250–400 ms) | Mesurée, même montage (`page:4/block:4`) |
| Temps de rendu NeRF | **≈ 30 à 40 ms** par image, quasi constant quelle que soit la pose | instant-ngp sur RTX 3090 (`page:4`) |
| Décomposition | Le réseau (plus l'encodage/décodage) domine la RTL : ≈ 60 à 360 ms hors rendu (calcul de la fiche : RTL − rendu) | `page:4` |
| Qualité (PSNR/SSIM/LPIPS) | **Non rapportée**. Évaluation qualitative seulement : kiwi, gelée d'agar, fouet à thé, tasse métallique, CD (Fig. 3) | `page:3–4` |
| Débit réseau | **Non rapporté** (ni bitrate VP8, ni bande passante) | — |
| Entraînement | ≈ 4 min (instant-ngp) ; 267 à 440 images extraites à 2 fps de vidéos iPhone SE 2 de 3–5 min | `page:3` |
| Mémoire / taille du modèle | Non rapportée | — |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Architecture de référence du rendu neuronal déporté stéréo (WebRTC, Unity, un renderer par œil). Pile logicielle concrète |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | Nul (NeRF). Remarque utile : poses par **mire ChArUco** plutôt que COLMAP pour avoir l'**échelle métrique**, nécessaire à une disparité stéréo correcte |
| 3. Rendu rapide, visibilité, casque XR | Montre la limite d'un rendu 100 % déporté en pixels : fps corrects, latence inacceptable. Aucun casque |
| 4. Évaluation (fps, latence, qualité, coût) | **Protocole d'horodatage en écho** avec décomposition rendu/réseau, réutilisable pour P6 |

## Pour (vis-à-vis de notre problématique)
- **Seul système de la base qui mesure une latence aller-retour réelle** sur un vrai réseau (Wi-Fi) en stéréo réelle. Il fournit une base chiffrée : 35–40 fps, 100–400 ms.
- **Protocole de mesure simple et transposable** à P6 : écho d'horodatage + temps de rendu dans le paquet retour, horloge unique côté client.
- **Tampon « dernière pose seulement »** : évite l'accumulation de retard quand le rendu est plus lent que l'envoi des poses. Brique simple pour P1′.
- Démontre qu'une **stéréo déportée par duplication** (un renderer et un GPU par œil) tient ≈ 35–40 fps : borne de comparaison pour la mutualisation stéréo (P2).
- Motive l'intérêt de la **3DGS** : le rendu NeRF (30–40 ms) plafonne déjà les fps ; 3DGS rend en quelques ms sur le même GPU (voir [Kerbl 2023](../kerbl2023_3dgs/fiche.md)).

## Contre / limites
- **Pas de casque** : afficheur autostéréoscopique de bureau (ELF-SR1). Le « client léger » est en fait un PC avec **RTX 3090**. Aucun résultat sur un appareil contraint.
- **Latence 5 à 20 fois au-dessus** du seuil XR de 20 ms, **sans compensation** (ni prédiction de mouvement, ni reprojection/ATW) : explicitement hors périmètre (`page:4`).
- **Mesure courte** (10 s, un seul essai rapporté), sans statistique (pas de moyenne, p50/p95), sans trace réseau décrite.
- **Aucune métrique de qualité** ni de débit ; résolution exacte par vue non chiffrée (« full HD »).
- Coupure périodique de ≈ 200 ms due à la vérification de connexion P2P : artefact d'implémentation qui fausse les courbes.
- Pas de profondeur transmise : **aucune composition possible** avec un rendu local (pixels RGB seuls sur un quad).
- Stéréo sans mutualisation : 2 GPU serveur pour 2 yeux, coût doublé.

## Idées à creuser pour une approche novatrice
- *Hypothèse (P6)* : reprendre le **protocole d'écho d'horodatage** sur Quest 3 (natif et PC-VR), en ajoutant le temps d'affichage prédit par OpenXR (`predictedDisplayTime`) pour approcher une **vraie motion-to-photon**, et publier p50/p95 sur des sessions longues. Servirait de **ligne de base « tout déporté »** (NeARportation refait en 3DGS).
- *Hypothèse (P1′)* : conserver l'architecture NeARportation (pose montante, tampon dernière pose, un flux par œil) mais **transmettre RGB + profondeur** pour la seule **périphérie/lointain**, et rendre **localement** la fovéa et le proche en 3DGS. Le rendu local supprime la latence là où elle est la plus visible ; la périphérie tolère mieux 100 ms si elle est **reprojetée** avec la profondeur.
- *Hypothèse (P2)* : remplacer « un renderer par œil » par un **rendu stéréo partagé** côté serveur (tri et projection communs) et mesurer le gain sur le même montage. Les auteurs le citent comme travail futur (« render images from multiple poses simultaneously on a single GPU », `page:4`).
- *Hypothèse* : quantifier la part **encodage/décodage vidéo** dans les 60–360 ms hors rendu (non séparée ici) ; si elle domine, un codec matériel à faible latence (H.264/HEVC NVENC) changerait l'ordre de grandeur, ce qui conditionne la faisabilité de P1′.

## Citations clés
> « we confirm that it can display a high-fidelity appearance on full-HD stereo videos at 35-40 frames per second (fps) according to the user's head motion » (`doc:2b2dc79/tier:standard/page:1`)

> « the RTL of this prototype oscillates at about 100 ∼ 400 ms. Additionally, we see that the rendering time of instant-ngp is almost constant regardless of the head position (30 ∼ 40 ms). » (`doc:2b2dc79/tier:standard/page:4`)

> « An RTL exceeding 20 ms is perceived to have detrimental effects [20]. However, due to the nature of our framework, which uses remote rendering, it is difficult to keep latency below 20 ms. » (`doc:2b2dc79/tier:standard/page:4`)

> « The matrix on the pose buffer is always overwritten with the latest one, and then the NeRF acquires the latest pose matrix and starts a new rendering immediately after the rendering is finished. » (`doc:2b2dc79/tier:standard/page:2`)

## Liens
- Papiers liés :
  - [Li 2025, survey champs de radiance XR](../li2025_rf-xr-survey/fiche.md) : cite NeARportation ; le seuil RTL < 20 ms y est un **objectif**, pas un résultat de NeARportation.
  - [Wan 2025, ECO-GS](../wan2025_edge-collab-gs/fiche.md) : edge + pixels en 3DGS, latence garantie < 60 ms mais **réseau simulé** ; NeARportation mesure sur réseau réel (100–400 ms).
  - [Zhu 2025, Nebula](../zhu2025_nebula/fiche.md) : collaboration cloud/casque qui transmet des Gaussiennes (Δcut) au lieu de pixels, et partage la stéréo : réponse aux deux faiblesses de NeARportation (latence pixels, stéréo dupliquée).
  - [Franke 2024, VR-Splatting](../franke2024_vr-splatting/fiche.md) et [Tu 2025, VRSplat](../tu2025_vrsplat/fiche.md) : 3DGS stéréo en local sur PC-VR, sans réseau.
  - [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) : seuils < 20 ms et grille de latence edge/cloud.
  - [Kerbl 2023, 3DGS](../kerbl2023_3dgs/fiche.md) : le remplacement naturel d'instant-ngp (rendu bien plus rapide).
