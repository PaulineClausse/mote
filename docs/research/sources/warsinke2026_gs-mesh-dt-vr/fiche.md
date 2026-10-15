---
citekey: warsinke2026_gs-mesh-dt-vr
mineru_doc: 23f3828
type: conférence   # atelier Hype-XR, IEEE ISMAR 2026 adjunct (version auteur, 7 p.)
statut: fiche complète
tags: [3DGS, maillage, jumeau-numérique, VR, tourisme-virtuel, étude-utilisateurs, UEQ-S, IPQ, CSQ-VR, Unity, Meta-Quest-3, GTX-1080, IoT, protocole-évaluation]
---

# 3D Gaussian Splatting and Mesh-Based Digital Twins: An Exploratory Study for Virtual Reality Tourism

**Référence :** Warsinke, M., Vona, F., Islam, A. T., Kojić, T., Voigt-Antons, J.-N., Möller, S. (2026). 3D Gaussian Splatting and Mesh-Based Digital Twins: An Exploratory Study for Virtual Reality Tourism. Atelier Hype-XR, *IEEE ISMAR 2026 Adjunct* (version auteur acceptée, DOI non encore attribué, p. 1). arXiv [2608.01969](https://arxiv.org/abs/2608.01969)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Étude utilisateurs exploratoire (20 participants, intra-sujets) comparant dans une application VR de tourisme sous Unity 6 un jumeau numérique en **maillage** (village d'Etteln, avec données IoT temps réel) et un jumeau en **3DGS** (Vilanova i la Geltrú) : le 3DGS obtient un meilleur réalisme perçu, mais une qualité pragmatique « Bad » et une présence plus faible. Aucune mesure de performance.

## Problème traité
- La création de jumeaux numériques haute fidélité pour la VR est coûteuse : laser + photogrammétrie, puis post-traitement manuel (retopologie, textures) pour tenir le temps réel (p. 1-2).
- Le 3DGS promet une création rapide et « scalable », mais son effet sur l'expérience utilisateur (UX), la présence, le réalisme perçu et la cybercinétose en VR reste peu étudié (p. 2-3, section 2.4).

## Méthode / contributions
- **Matériel (p. 3)** : **Meta Quest 3 filaire** (Meta Link Cable) sur PC **NVIDIA GTX 1080**, Intel i7-7700K 4,2 GHz, 16 Go de RAM ; manettes Quest 3 standard.
- **Logiciel (p. 3)** : **Unity 6**, locomotion par **Unity XR Interaction Toolkit** (déplacement continu au joystick + téléportation avec fondu « blink » anti-cybercinétose), menu de téléportation vers des points d'intérêt (POI). **Le renderer / plugin 3DGS utilisé n'est pas nommé** (non rapporté).
- **Version 3DGS (p. 3)** : images de drone → SfM (poses + points épars) → optimisation de Gaussiennes 3D. Plusieurs POI **reconstruits et rendus indépendamment** (église Sant Antoni, Plaça dels Lledoners) : pas de ville continue, navigation entre POI par menu seulement. Niveau d'intégration : *digital model* (aucun flux de données).
- **Version maillage (p. 3)** : images de drone → NeRF par POI → extraction d'isosurface (Marching Cubes) → maillage optimisé, retouché dans 3ds Max (géométrie, LOD, textures). Environnement **continu** explorable librement. Certains POI affichent des **données IoT temps réel** (ex. puissance de charge d'un moulin) : niveau *digital shadow* (flux unidirectionnel).
- **Protocole (p. 3-4)** : intra-sujets, contrebalancement AB/BA, ~30 min au total, **5 min d'exploration libre par version** ; questionnaires après chaque version.
- **Questionnaires (p. 3-4)** :
  - démographie + expérience XR / modélisation 3D / jeux vidéo ; **ATI** (affinité technologique, 9 items, 1-6) ;
  - **Affective Slider** (valence, arousal ; échelle 1-10 ici) ;
  - **UEQ-S** (qualité pragmatique / hédonique, 8 paires, ramené à −3..3) ;
  - **CSQ-VR** (nausée, oculomoteur, vestibulaire ; total 6-42) ;
  - **IPQ** (présence générale, spatiale, implication, réalisme vécu ; ramené à −3..3) ;
  - questionnaire **« perception du DT »** maison, non validé (Enjoyment, Understanding, Information, Reliability, Simulation ; Table 1, p. 3).
- **Analyse (p. 4)** : statistiques descriptives (JASP), corrélations de Spearman facteurs utilisateurs × variables dépendantes avec correction Holm-Bonferroni. **Aucun test inférentiel entre versions**, car plusieurs variables changent à la fois (lieu, continuité, IoT).

## Résultats chiffrés
**Performance : rien n'est rapporté.** Pas de fps (ni mono ni stéréo), pas de résolution, pas de nombre de Gaussiennes, pas de taille de scène, pas de temps d'entraînement ni de temps capture → VR, pas de latence, pas de PSNR/SSIM/LPIPS.

| Métrique (moyenne, 20 participants) | 3DGS | Maillage | Source |
|---|---|---|---|
| UEQ-S pragmatique | 0,41 (« Bad ») | 1,70 (« Good ») | Tables 2-3, p. 4 ; p. 5 |
| UEQ-S hédonique | 0,61 (« Below Average ») | 1,16 (Table) / 1,17 (texte) (« Above Average ») | p. 4-5 |
| UEQ-S global | 0,51 (SD 1,31), « Bad » | 1,43 (SD 0,87), « Good » | p. 5 |
| IPQ total | −0,39 (SD 0,97) [chiffre mal OCRisé, « −0.3̇9 »] | −0,06 (SD 0,70) | p. 5 |
| IPQ réalisme vécu | **−0,71** | −0,83 | Tables 2-3, p. 4 |
| IPQ présence générale / spatiale / implication | 0,50 / 0,07 / 0,13 | 1,05 / 0,66 / 0,51 | p. 4-5 |
| CSQ-VR total (6-42) | 19,50 (SD 9,76) | 17,80 (SD 8,92) | p. 4-5 |
| CSQ-VR sous-scores | vestibulaire 6,75 ; nausée 6,65 ; oculomoteur 6,10 | oculomoteur 6,50 ; nausée 6,10 ; vestibulaire 5,20 | p. 5 |
| Valence / arousal (1-10) | 5,95 / 6,10 | 6,80 / 7,10 | p. 4-5 |
| DT : Enjoyment / Simulation / Understanding / Reliability / Information (1-7) | 4,40 / 4,30 / 3,95 / 3,55 / 3,15 | 5,35 / 5,40 / 5,05 / 4,30 / 4,15 | p. 5 |

- **Participants (p. 4)** : 20 (9 H, 11 F), 33,8 ans en moyenne (SD 11,31), expérience XR 4,05/7, ATI 4,27/6.
- **Corrélations significatives après Holm (p. 5)** : expérience en modélisation 3D × Reliability pour le 3DGS (r_s = 0,68, p_Holm = 0,012) ; × réalisme vécu pour le maillage (r_s = 0,65, p_Holm = 0,024).
- **Qualitatif (p. 5)** : pour le 3DGS, les participants citent des visuels flous, du **scintillement (flickering)** et une locomotion peu naturelle comme causes de nausée ; des artefacts sont visibles dans la cime des arbres (Fig. 4, p. 6). Pour le maillage, l'inconfort vient surtout de la locomotion. Présence « Low » partout pour le 3DGS selon le benchmark IPQ de Tran et al. (p. 5).

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Un cas concret **Unity 6 + XR Interaction Toolkit + Quest 3 en Link** (p. 3). Plugin 3DGS non nommé. Revue de l'état de l'art 3DGS/tourisme et renvoi à [VRSplat](../tu2025_vrsplat/fiche.md) et au [survey de Li](../li2025_rf-xr-survey/fiche.md) (p. 2) |
| 2. Gaussiennes depuis SfM | Pipeline standard drone → SfM → 3DGS, sans détail (p. 3) |
| 3. Rendu, casque XR | Aucun apport algorithmique. Un **GTX 1080** (Pascal, 2016) pilote un Quest 3 en stéréo : l'absence de chiffres de fps est problématique, car le scintillement signalé peut venir de la performance comme des artefacts |
| 4. Évaluation | **Protocole UX réutilisable** : UEQ-S + IPQ + CSQ-VR + Affective Slider, intra-sujets AB/BA, 5 min par condition, corrélations Holm. Montre aussi ce qu'il **faut éviter** : conditions confondues (lieux différents), donc aucune comparaison possible |

## Pour (vis-à-vis de notre problématique)
- Donne une **batterie de questionnaires courte** (≈ 30 min par participant, p. 3) directement transposable à l'étape 4 pour compléter fps / latence / PSNR par la QoE (cf. distinction QoS/QoE de [Kamdjou](../kamdjou2024_xr-dt-iiot/fiche.md)).
- Confirme que le 3DGS gagne sur le **réalisme perçu** face à un maillage issu de drone (−0,71 contre −0,83), même sur un GPU d'entrée de gamme actuel (p. 4-5).
- Signal fort pour notre sujet : **les artefacts 3DGS (flou, scintillement) causent de la cybercinétose en VR** (p. 5). Cela justifie de mesurer la stabilité temporelle (popping, cf. [StopThePop](../radl2024_stopthepop/fiche.md)) et pas seulement le PSNR.
- Montre qu'un **DT « digital shadow » (panneaux de données IoT temps réel)** s'intègre facilement côté maillage dans Unity (p. 3). C'est la brique « données » de P5.

## Contre / limites
- **Aucune donnée de performance** (fps, résolution par œil, taille des scènes, VRAM, temps de reconstruction) : inutilisable comme référence technique.
- **Conditions confondues** (lieu, continuité de la scène, IoT, mode de navigation) : les auteurs refusent eux-mêmes toute conclusion comparative (p. 4, p. 6). La mauvaise qualité pragmatique du 3DGS peut venir de la navigation par menu entre POI isolés, et pas du rendu.
- Échantillon petit (n = 20), questionnaire DT non validé (p. 6).
- Le maillage n'est pas un maillage « classique » : il est extrait d'un NeRF (p. 3). Ce n'est donc pas 3DGS contre photogrammétrie.
- Pas d'hybride : les deux représentations ne coexistent jamais dans une même scène.

## Idées à creuser pour une approche novatrice
- **Hypothèse (protocole étape 4)** : reprendre la batterie UEQ-S + IPQ + CSQ-VR, mais en **2×2 contrôlé** (même lieu reconstruit en 3DGS et en maillage, comme le suggèrent les auteurs, p. 6). Il faudrait y ajouter des **mesures objectives synchronisées** (fps par œil, temps de frame, latence) pour relier QoS et QoE (instanciation de l'éq. 1 de [Kamdjou](../kamdjou2024_xr-dt-iiot/fiche.md)).
- **Hypothèse (P5)** : fusionner les deux versions en **un seul DT hybride**. Le décor statique serait en 3DGS (pour le réalisme perçu) ; la navigation, les collisions et les panneaux de données temps réel passeraient par une géométrie maillée proxy (pour la qualité pragmatique). Ce papier suggère que chaque représentation gagne sur un axe différent.
- **Hypothèse** : corréler le score CSQ-VR au taux de scintillement / popping mesuré (métrique temporelle), pour quantifier le lien artefacts → cybercinétose rapporté qualitativement (p. 5).

## Citations clés
> « While the 3DGS version scored higher in terms of experienced realism, it showed clear weaknesses in pragmatic quality. » (`doc:23f3828/tier:standard/page:1`)
> « The application ran on an external PC tethered to a Meta Quest 3 headset via a Meta Link Cable. The PC specifications were an NVIDIA GeForce GTX 1080 » (`doc:23f3828/tier:standard/page:3`)
> « In the Mesh version, participants reported discomfort mainly from locomotion, while in the 3DGS version, visual artifacts seemed to have caused symptoms. » (`doc:23f3828/tier:standard/page:5`)
> « No statistical tests were conducted to compare the two versions, as the study design did not isolate a single variable. » (`doc:23f3828/tier:standard/page:4`)

## Liens
- [Kamdjou 2024](../kamdjou2024_xr-dt-iiot/fiche.md) : cadre DT industriel (OPC-UA, edge) ; la version maillage de Warsinke en est un équivalent « tourisme » en *digital shadow*.
- [Mirocha 2025](../mirocha2025_beyond-dt/fiche.md) : même constat qualitatif (artefacts, géométrie imprécise du 3DGS) côté patrimoine.
- [Tu 2025 (VRSplat)](../tu2025_vrsplat/fiche.md) : cité ici (p. 2, p. 5) pour les artefacts 3DGS en VR ; lui fournit les chiffres de performance absents ici.
- [Li 2025 (survey RF-XR)](../li2025_rf-xr-survey/fiche.md) : plaide pour des benchmarks centrés utilisateur (présence, cybercinétose), ce que tente ce papier.
- [Jiang 2024 (VR-GS)](../jiang2024_vr-gs/fiche.md) : autre étude utilisateurs (SUS), et un vrai hybride maillage + Gaussiennes.
- [Uzun 2025](../uzun2025_gs-alive-xr/) (PDF manquant) : pipeline photogrammétrie + 3DGS pour la XR, que ce papier remplace en partie.
