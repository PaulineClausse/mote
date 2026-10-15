---
citekey: qiu2024_3dgs-xr-survey
mineru_doc: 88a9bde
type: survey
statut: fiche complète
tags: [survey, 3DGS, XR, taxonomie, compression, streaming, avatars, VR-GS, DualGS, prospective]
---

# Advancing Extended Reality with 3D Gaussian Splatting: Innovations and Prospects

**Référence :** Shi Qiu, Binzhu Xie, Qixuan Liu, Pheng-Ann Heng (2024). *Advancing Extended Reality with 3D Gaussian Splatting: Innovations and Prospects*. Prépublication (6 pages, venue non indiquée dans le texte), The Chinese University of Hong Kong. arXiv:2412.06257v2 — https://arxiv.org/abs/2412.06257
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

## En une phrase
Court article de position (6 pages) qui trie 272 papiers 3DGS selon leur lien avec la XR, propose une taxonomie en cinq axes et liste des pistes XR peu explorées, sans aucune mesure propre.

## Problème traité
- Parmi 272 papiers 3DGS publics (juillet 2023 à fin octobre 2024), 152 mentionnent la XR, mais la plupart de façon superficielle, sans implémentation ni évaluation XR (`doc:88a9bde/tier:standard/page:1`, `page:2`).
- Objectif : synthétiser les innovations 3DGS utiles à la XR et proposer une feuille de route (`doc:88a9bde/tier:standard/page:2`).

## Méthode / contributions
- **Trois travaux « vraiment XR »** mis en avant (`doc:88a9bde/tier:standard/page:2`) :
  - [VR-GS](../jiang2024_vr-gs/fiche.md) : dynamique XPBD, cages tétraédriques embarquant des groupes de Gaussiennes, préparation hors ligne.
  - DualGS : Gaussiennes « articulations » et « peau » pour la vidéo volumétrique humaine ; entropie + tables de correspondance, environ **350 KB par frame**.
  - RGCA (Relightable Gaussian Codec Avatars) : avatars ré-éclairables, modèle d'œil explicite.
- **Taxonomie en 5 axes** (Fig. 2) (`doc:88a9bde/tier:standard/page:2`, `page:3`) :
  1. Création de contenu 3D (avatars, scènes, texte-vers-3D) ;
  2. Rendu & visualisation (temps réel, photoréalisme/effets) ;
  3. Interaction & manipulation (édition de scène, contrôle d'objets virtuels) ;
  4. Optimisation système & efficacité (compression, accélération matérielle) ;
  5. Applications spécialisées (SLAM, XR médicale).
- **Six pistes prospectives** : modélisation de maillages, scènes dynamiques/4D, compréhension de scène en monde ouvert, suivi des mains, passthrough, visualisation immersive de données (`doc:88a9bde/tier:standard/page:4`).

## Résultats chiffrés
Aucun chiffre propre. Les seules valeurs sont reprises de papiers cités :

| Métrique | Valeur | Conditions (dataset, résolution, GPU) |
|---|---|---|
| FPS | LightGaussian : « plus de 200 FPS » | non précisé dans le survey (`page:3`) → voir [LightGaussian](../fan2023_lightgaussian/fiche.md) |
| Qualité (PSNR / SSIM / LPIPS) | non rapporté | — |
| Temps d'entraînement / préparation | non rapporté | — |
| Mémoire / taille du modèle | LightGaussian : compression jusqu'à 15× ; DualGS : environ 350 KB par frame | `page:3` ; `page:2` |
| Latence | non rapporté (seulement qualitatif : « latency affects immersion ») | `page:3` |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | Moyen. Carte rapide avec une bibliographie de 95 références, utile pour repérer compression, streaming et accélération matérielle mobile. Pas d'environnement logiciel/matériel XR décrit. |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | Nul (aucun rappel technique). |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | Faible. Signale l'accélération matérielle/algorithmique pour mobile (GSCore [26]) et les méthodes qui réduisent mémoire et calcul pour casques AR/VR ([56], [71]) (`page:3`). Aucune discussion du tri, de la stéréo ni du fovéal. |
| 4. Évaluation (fps, latence, qualité, coût) | Nul. Aucune métrique ni protocole. |

## Pour (vis-à-vis de notre problématique)
- Lecture rapide pour positionner l'axe « System Optimization & Efficiency » (compression + accélération matérielle), qui correspond à notre verrou de coût.
- Pointe explicitement vers le streaming (« efficiently managing streaming resources », [12], [52], [54]) pour afficher de la 3DGS sur casques et lunettes AR légers (`page:3`). Le sujet P4 y est donc reconnu mais pas traité.
- Même équipe qu'une étude SUS comparant maillage / 3DGS / panoramas pour créer des environnements VR (citée par [li2025](../li2025_rf-xr-survey/fiche.md) [48]).

## Contre / limites
- Très superficiel : aucun chiffre de fps, de résolution ni de matériel, aucune distinction mono/stéréo ou casque/desktop.
- Aucun critère de sélection explicite (pas de PRISMA), à la différence de [li2025](../li2025_rf-xr-survey/fiche.md).
- Couverture arrêtée à octobre 2024. Il manque les travaux VR spécifiques ([VR-Splatting](../franke2024_vr-splatting/fiche.md), [VRSplat](../tu2025_vrsplat/fiche.md), fovéal 3DGS…).
- Les pistes prospectives restent génériques et sans analyse de faisabilité ni de coût.

## Idées à creuser pour une approche novatrice
- *Hypothèse :* l'axe « streaming resources » est cité sans méthode (`page:3`). **P4** (streaming progressif de splats) n'est **pas réalisée** ici, seulement éclairée. Il faut lire 3DGStream [54] et DualGS [12] pour vérifier ce qui existe déjà en streaming 3DGS.
- *Hypothèse :* la piste « Mesh Modeling » (interactions précises utilisateur/objets) (`page:4`) **éclaire P5** (jumeau hybride 3DGS statique + maillage dynamique), sans la réaliser.
- *Hypothèse :* la piste « Passthrough » (reconstruire en temps réel l'environnement immédiat de l'utilisateur) (`doc:88a9bde/tier:standard/page:4/block:9`) peut se combiner à **P1** : le casque rend le proche (passthrough/3DGS local) et l'edge rend la scène lointaine.
- *Hypothèse :* GSCore [26] (support architectural de la 3DGS) peut servir à justifier quantitativement où se trouve le goulot sur mobile (tri, rastérisation) avant de concevoir P2 (tri partagé entre les deux yeux).

## Citations clés
> « By efficiently managing streaming resources, 3DGS can enable smooth rendering and visualization of 3D objects on a range of devices, including those with limited hardware capabilities such as mobile AR glasses and VR headsets » (`doc:88a9bde/tier:standard/page:3/block:4`)

> « Although many studies acknowledge the potential relevance of 3DGS to XR, our investigation reveals that the majority do not specifically exploit 3DGS techniques in XR environments. » (`doc:88a9bde/tier:standard/page:1`)

> « DualGS uses entropy encoding and lookup table compression to reduce storage to ∼350KB per frame » (`doc:88a9bde/tier:standard/page:2`)

## Papiers cités à ajouter à la base
Références telles que données dans la bibliographie du survey, hors dossiers existants :
1. **J. Lee, S. Lee, J. Lee, J. Park, J. Sim (2024).** *Gscore: Efficient radiance field rendering via architectural support for 3d gaussian splatting.* ASPLOS 2024 [26]. Profilage matériel des goulots 3DGS (tri, rastérisation) sur mobile.
2. **J. Sun, H. Jiao, G. Li, Z. Zhang, L. Zhao, W. Xing (2024).** *3dgstream: On-the-fly training of 3d gaussians for efficient streaming of photo-realistic free-viewpoint videos.* CVPR 2024 [54]. Streaming 3DGS (P4).
3. **S. Niedermayr, J. Stumpfegger, R. Westermann (2024).** *Compressed 3d gaussian splatting for accelerated novel view synthesis.* CVPR 2024 [56]. Codebooks, rendu accéléré, cible les appareils peu puissants.
4. **K. Navaneet, K. P. Meibodi, S. A. Koohpayegani, H. Pirsiavash (2024).** *Compgs: Smaller and faster gaussian splatting with vector quantization.* ECCV 2024 [71]. Quantification vectorielle (à distinguer de [lee2023_compact3d](../lee2023_compact3d/fiche.md)).
5. **Y. Jiang, Z. Shen, Y. Hong, C. Guo, Y. Wu, Y. Zhang, J. Yu, L. Xu (2024).** *Robust dual gaussian splatting for immersive human-centric volumetric videos.* arXiv:2409.08353 [12]. Environ 350 KB par frame, rendu sur casque VR.
6. **Y. Jiang et al. (2024).** *Hifi4g: High-fidelity human performance rendering via compact gaussian splatting.* CVPR 2024 [52].
7. **T. Lu, M. Yu, L. Xu, Y. Xiangli, L. Wang, D. Lin, B. Dai (2024).** *Scaffold-gs: Structured 3d gaussians for view-adaptive rendering.* CVPR 2024 [28]. Ancres et Gaussiennes générées selon la vue, base de LOD.
8. **Y. Liu, H. Guan, C. Luo, L. Fan, J. Peng, Z. Zhang (2024).** *Citygaussian: Real-time high-quality large-scale scene rendering with gaussians.* arXiv:2404.01133 [29]. LoD pour grandes scènes (P3).
9. **S. Niedermayr, C. Neuhauser, K. Petkov, K. Engel, R. Westermann (2024).** *Application of 3d gaussian splatting for cinematic anatomy on consumer class devices* [84]. 3DGS sur appareils grand public.
10. **Z. Peng, T. Shao, Y. Liu, J. Zhou, Y. Yang, J. Wang, K. Zhou (2024).** *Rtg-slam: Real-time 3d reconstruction at scale using gaussian splatting.* SIGGRAPH 2024 [53]. Reconstruction 3DGS en ligne, pour un jumeau numérique mis à jour (P5).

## Liens
- Papiers liés : [Kerbl 2023](../kerbl2023_3dgs/fiche.md) [5] · [VR-GS](../jiang2024_vr-gs/fiche.md) [13] · [StopThePop](../radl2024_stopthepop/fiche.md) [24] · [Mip-Splatting](../yu2023_mip-splatting/fiche.md) [27] · [LightGaussian](../fan2023_lightgaussian/fiche.md) [69] · [Li 2025](../li2025_rf-xr-survey/fiche.md) (survey XR systématique, bien plus complet) · [Chen 2024](../chen2024_3dgs-survey/fiche.md) (cité [88]) · [LapisGS](../shi2024_lapisgs/fiche.md) (streaming progressif, à comparer à 3DGStream).
