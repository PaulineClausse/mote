---
citekey: mirocha2025_beyond-dt
mineru_doc: 7d35b42
type: talk court   # SIGGRAPH Talks, 2 pages
statut: fiche complète
tags: [3DGS, moteurs-de-jeu, Unity, Unreal, patrimoine-culturel, SLAM, LiDAR, jumeau-numérique, retour-d-expérience, plugins]
---

# Beyond Digital Twins: 3D Gaussian Splatting, Game Engines and Crossmedia Cultural Heritage Representations

**Référence :** Mirocha, L. (2025). Beyond Digital Twins: 3D Gaussian Splatting, Game Engines and Crossmedia Cultural Heritage Representations. *SIGGRAPH Talks '25*, art. 42, 2 p. ACM. DOI [10.1145/3721239.3734094](https://doi.org/10.1145/3721239.3734094)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Un retour d'expérience de praticien qui numérise un manoir historique de Hong Kong en 3DGS (photos, vidéo, SLAM + LiDAR) et l'intègre dans Unity et Unreal Engine 5 via des plugins tiers. Le papier dresse un constat qualitatif des limites : éclairage figé, géométrie imprécise, artefacts.

## Problème traité
Comment les nouvelles méthodes de capture, de traitement et d'affichage 3D permettent-elles de concevoir des expériences temps réel immersives et interactives ? Le talk interroge aussi l'espace entre le « jumeau numérique » exact et la représentation visuelle (p. 1). Il n'y a pas de question de performance : l'angle est esthétique et patrimonial.

## Méthode / contributions
- **Site :** le manoir Pun Uk (1932), plus de 600 m², trois halls et des cours (p. 1).
- **Capture :** 5 visites entre août et décembre 2024 (p. 2). Trois sources :
  - un reflex Canon pour les détails (plafonds peints, carrelages) ;
  - des iPhone 13 Pro et 16 Pro en vidéo HD pour les pièces et les cours ;
  - un scanner SLAM **Xgrids LixelKity K1** (deux modules panoramiques 48 MP + LiDAR) pour le manoir entier.
- **Traitement :** entraînement 3DGS dans **Postshot** sur une **RTX 3080**, sauf pour les données Xgrids, traitées dans leur logiciel propriétaire Lixel CyberColor. Nettoyage dans Postshot et **SuperSplat** : suppression de groupes de splats, élagage des zones inutiles, retrait des artefacts dus aux variations d'éclairage et aux trous de données (p. 2).
- **Intégration moteur**, avec six plugins testés (p. 2) :
  - pour Unreal : Luma AI, XVERSE 3D-GS UE Plugin, LCC Unreal SDK ;
  - pour Unity : LCC Unity SDK, UnityGaussianSplatting (Aras P.) ;
  - le plugin Postshot, sans précision de moteur.
- **Trois réalisations** (p. 2) :
  - une installation Unity sur un mur LED (une douzaine de scans et trois captures 360°) ;
  - une exploration interactive à la troisième personne sur PC sous Unreal (10 scans 3DGS reliés entre eux) ;
  - un survol animé sous Unity, construit à partir du scan SLAM complet, d'une précision « digne d'un jumeau numérique ».

## Résultats chiffrés
| Métrique | Valeur | Conditions |
|---|---|---|
| FPS | non rapporté | |
| Qualité (PSNR / SSIM / LPIPS) | non rapporté | évaluation qualitative uniquement |
| Temps d'entraînement | non rapporté | Postshot, RTX 3080 (p. 2) |
| Mémoire / taille | non rapporté | |
| Latence | non rapporté | |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Recense l'**écosystème d'outils praticiens** pour 3DGS : Postshot, SuperSplat, six plugins moteur. Utile pour choisir notre environnement logiciel |
| 2. Gaussiennes depuis SfM | Rappelle que les captures 3DGS « par objectif » (lens-based) manquent de précision géométrique et souffrent de défauts d'échelle et d'orientation. Seul le SLAM + LiDAR atteint une précision de jumeau numérique (p. 2). Piste : initialiser ou contraindre avec du LiDAR plutôt qu'avec du SfM seul |
| 3. Rendu, casque XR | Les plugins permettent le rendu temps réel, mais **pas d'ombres dynamiques** : l'éclairage reste « figé » (baked) tel qu'au moment du scan (p. 2). Aucun test sur casque |
| 4. Évaluation | Aucune mesure |

## Pour (vis-à-vis de notre problématique)
- Montre qu'une chaîne **sans code** (Postshot, puis plugin Unity ou Unreal) aboutit à du temps réel sur un GPU grand public (RTX 3080). C'est une base de comparaison réaliste pour notre prototype.
- Confirme l'intérêt de l'intégration dans un moteur de jeu pour la XR (interaction, narration, mélange avec d'autres médias).
- Le couplage SLAM/LiDAR + 3DGS apporte à la fois la qualité visuelle et la précision géométrique (p. 2).

## Contre / limites
- Deux pages seulement, **aucune mesure quantitative** (ni fps, ni qualité, ni coût). Le talk ne sert pas de référence de performance.
- Pas d'expérience sur casque XR : le PC en troisième personne et le mur LED ne sont pas de la VR.
- Limites 3DGS rapportées :
  - pas d'ombres portées ni reçues : éclairage figé, donc aucun rééclairage possible ;
  - artefacts, flous et halos en bord de scan ;
  - problèmes d'échelle et d'orientation ;
  - pipelines logiciels instables (p. 1-2).
- L'approche assume les artefacts comme un choix esthétique, ce qui est l'inverse de notre objectif photoréaliste.

## Idées à creuser pour une approche novatrice
- **Hypothèse :** initialiser les Gaussiennes à partir d'un nuage LiDAR/SLAM plutôt que de points SfM épars, pour mieux maîtriser l'échelle et la géométrie. C'est une variante directe de notre étape 2 (voir la [fiche Kerbl](../kerbl2023_3dgs/fiche.md) sur l'importance de l'initialisation).
- **Hypothèse :** banc d'essai comparatif des plugins Unity et Unreal cités (fps par œil sur casque, VRAM, qualité), une mesure qu'aucune des sources de la base ne fournit.
- **Hypothèse :** rééclairage partiel ou ombres approximatives en MR, pour résoudre la limite de l'éclairage figé quand on mélange du 3DGS avec des objets virtuels dynamiques.

## Citations clés
> « current limitations prevent splats from casting or receiving dynamic shadows » (`doc:7d35b42/tier:standard/page:2`)
> « lens-based 3DGS reconstructions lack digital twin-level geometric accuracy » (`doc:7d35b42/tier:standard/page:2`)

## Liens
- [Kerbl 2023](../kerbl2023_3dgs/fiche.md) : la méthode de base utilisée par tous les outils cités.
- [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) : le jumeau numérique vu sous l'angle de l'ingénierie. Mirocha le questionne sous l'angle de la représentation.
- [Uzun 2025](../uzun2025_gs-alive-xr/) (PDF manquant) : approche voisine, photogrammétrie + GS pour des espaces XR.
- [Shukhratov 2025](../shukhratov2025_capture-interact-unity/) : 3DGS dans Unity.
- [Warsinke 2026](../warsinke2026_gs-mesh-dt-vr/) : jumeaux numériques 3DGS vs maillage en VR.
