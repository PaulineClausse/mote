---
citekey: shukhratov2025_capture-interact-unity
mineru_doc: e32a053
type: talk court   # papier de démonstration, 3 p. (arXiv cs.GR) ; venue non indiquée dans le texte
statut: fiche complète
tags: [3DGS, Unity, UnityGaussianSplatting, pipeline-capture, smartphone, cloud, COLMAP, jumeau-numérique, téléprésence, Apple-M4, RTX-A40, démo]
---

# Capture and Interact: Rapid 3D Object Acquisition and Rendering with Gaussian Splatting in Unity

**Référence :** Shukhratov, I., Gorinsky, S. (2025). Capture and Interact: Rapid 3D Object Acquisition and Rendering with Gaussian Splatting in Unity. Papier de démonstration, IMDEA Networks (venue non indiquée dans le texte). arXiv [2510.06802](https://arxiv.org/abs/2510.06802)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Une démo de pipeline de bout en bout : vidéo smartphone (interface web), puis SfM COLMAP et 3DGS original de Kerbl sur un serveur cloud (RTX A40), puis téléchargement du modèle et rendu interactif dans Unity avec **UnityGaussianSplatting (Aras P.)**. Environ 10 min de la capture au rendu, ≈ 150 fps pour ≈ 500 k splats sur un MacBook Pro M4. Aucun casque XR.

## Problème traité
- La capture et le rendu 3D temps réel d'objets réels reposent sur du matériel coûteux (LiDAR), des environnements contrôlés et du post-traitement (p. 1).
- NeRF est trop long à entraîner pour la téléprésence ou l'AR. MobileNeRF rend sur mobile mais sans capture ni reconstruction de bout en bout (p. 1).
- Objectif : « démocratiser » la création de contenu 3D photoréaliste pour l'AR, les jumeaux numériques, la collaboration à distance et le prototypage (p. 1).

## Méthode / contributions
Pipeline en 5 étapes (Fig. 1, p. 1) :
1. vidéo courte enregistrée via un front-end **HTML5 / JavaScript** sur n'importe quel mobile, puis envoi au cloud (p. 2, Fig. 2) ;
2. découpage de la vidéo en images ;
3. **SfM COLMAP** : poses et nuage épars (p. 2) ;
4. **3DGS de l'implémentation INRIA** de Kerbl et al., ≈ 30 k itérations, avec densification et élagage adaptatifs (p. 2) ;
5. téléchargement du modèle gaussien sur le client, puis rendu dans **Unity via UnityGaussianSplatting** (Aras Pranckevičius, réf. [6]). Interactions : pan, zoom, rotation, mise à l'échelle (p. 2, Fig. 3).

Ce papier n'apporte **aucune contribution algorithmique** : c'est un assemblage d'outils existants, à visée démonstrative.

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| FPS | **≈ 150 fps en moyenne** | ≈ 500 k splats, **MacBook Pro M4** (GPU intégré Apple), Unity + UnityGaussianSplatting ; affichage écran **mono**, **résolution non rapportée** (p. 2) |
| Qualité | **PSNR moyen 34,65 dB** | Objets simples (tasses, livres) et complexes (fleurs, lunettes) ; SSIM / LPIPS non rapportés ; protocole de test (vues retenues) non décrit (p. 2) |
| Temps capture → rendu | **≈ 10 min en moyenne** (optimisation + pipeline complet) | GPU cloud **NVIDIA RTX A40**, selon la complexité et la durée de la vidéo (p. 1-2). Décomposition COLMAP / entraînement non rapportée |
| Mémoire / taille du modèle | non rapporté | — |
| Latence (réseau, interaction) | non rapporté | — |
| Échelle | objets isolés, pas de scènes | p. 2 |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Confirme que **Unity + UnityGaussianSplatting** est la voie « sans code » la plus courante (déjà citée par [Mirocha](../mirocha2025_beyond-dt/fiche.md)). Ce plugin tourne aussi sur GPU Apple, pas seulement NVIDIA/CUDA (p. 2). Aucun test XR |
| 2. Gaussiennes depuis SfM | Pipeline de référence COLMAP → 3DGS INRIA, 30 k itérations : utilisable tel quel comme **baseline de reconstruction** (p. 2) |
| 3. Rendu, casque XR | Aucun ; 150 fps mono sur portable, sans résolution indiquée |
| 4. Évaluation | Un seul chiffre de qualité (PSNR) et de temps ; pas de protocole |

## Pour (vis-à-vis de notre problématique)
- Montre qu'un **objet d'environ 500 k Gaussiennes** tient ≈ 150 fps sur un GPU intégré de portable (M4) dans Unity (p. 2). C'est un ordre de grandeur utile pour dimensionner des **objets 3DGS insérés dans une scène XR** (pièces d'un DT, par exemple).
- L'architecture **capture mobile → entraînement cloud → rendu local** (Fig. 1) est un découpage type « opérations complexes au cloud, simples au bord », cohérent avec [Kamdjou](../kamdjou2024_xr-dt-iiot/fiche.md) (p. 14 de Kamdjou).
- Environ 10 min de la capture à l'objet interactif (p. 2) : un temps de numérisation compatible avec l'ajout rapide de pièces dans un jumeau numérique (les auteurs citent le prototypage industriel, p. 2).

## Contre / limites
- **Pas de XR** : ni casque, ni stéréo, ni AR, malgré les motivations affichées (p. 1).
- **Résolution de rendu, VRAM, taille des fichiers et latence réseau non rapportées** ; PSNR sans protocole ni dataset de référence.
- Le modèle est **téléchargé en entier** avant le rendu : aucun streaming progressif ni LOD.
- Objets isolés uniquement ; pas de scène ni d'intégration avec un maillage ou de la physique (les interactions se limitent à des transformations rigides de visualisation).
- 3 pages, niveau démo : aucune comparaison avec d'autres pipelines.

## Idées à creuser pour une approche novatrice
- **Hypothèse (P4)** : remplacer le téléchargement complet du modèle (étape 5) par un **streaming progressif de splats** ordonnés par contribution, pour que l'objet soit visible en quelques secondes et s'affine ensuite ([LapisGS](../shi2024_lapisgs/fiche.md) va dans ce sens).
- **Hypothèse (P5)** : utiliser ce pipeline « 10 min » comme **outil de numérisation des pièces mobiles** d'un DT. Chaque pièce serait un objet 3DGS séparé, attaché dans Unity à un transform piloté par des variables OPC-UA, et le décor statique une scène 3DGS à part.
- **Hypothèse (étape 1)** : banc d'essai du plugin UnityGaussianSplatting en **stéréo sur casque** (fps par œil, VRAM, nombre de splats maximal à ≥ 30 / 72 fps), pour mesurer la marge de cette solution « sur étagère » avant de développer un rendu maison.

## Citations clés
> « visualize it interactively in Unity at an average of 150 frames per second (fps) on a laptop » (`doc:e32a053/tier:standard/page:1`)
> « The optimization runs for approximately 30K iterations on an NVIDIA RTX A40 GPU and the whole pipeline completes in an average of 10 minutes [...] the reconstructed objects achieve a Peak Signal-to Noise Ratio (PSNR) of 34.65. » (`doc:e32a053/tier:standard/page:2`)
> « The renderer operates at an average of 150 fps for approximately 500K splats on a MacBook Pro with the M4 chip. » (`doc:e32a053/tier:standard/page:2`)

## Liens
- [Kerbl 2023](../kerbl2023_3dgs/fiche.md) : implémentation d'entraînement utilisée telle quelle.
- [Mirocha 2025](../mirocha2025_beyond-dt/fiche.md) : utilise aussi UnityGaussianSplatting (Aras P.), parmi six plugins moteur.
- [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) : répartition edge/cloud des traitements dans un DT.
- [Wan 2025 (edge collaboratif)](../wan2025_edge-collab-gs/fiche.md) et [Shi 2024 (LapisGS)](../shi2024_lapisgs/fiche.md) : répartition du calcul et streaming, absents ici.
- [Jiang 2024 (VR-GS)](../jiang2024_vr-gs/fiche.md) : Unity + plugin CUDA maison en VR, avec physique. C'est la version « interactive » de ce que ce pipeline ne fait pas.
- [Uzun 2025](../uzun2025_gs-alive-xr/) (PDF manquant) : pipeline photogrammétrie + 3DGS pour la XR, voisin de celui-ci.
