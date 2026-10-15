# Sujet — 3D Gaussian Splatting pour le rendu temps réel de champs de radiance en XR

## Description

Ce travail explore une méthode novatrice, le « 3D Gaussian Splatting », pour le rendu en temps réel des champs de radiance, adaptée aux applications immersives en réalité étendue (XR), incluant la réalité virtuelle (VR), la réalité augmentée (AR) et la réalité mixte (MR). Cette approche vise à générer des rendus photoréalistes de scènes complexes à partir de multiples photos ou vidéos, avec une qualité visuelle élevée et un affichage en temps réel (≥ 30 fps) à une résolution de 1080p, tout en optimisant les coûts computationnels pour les environnements XR.

**Problématique centrale :** surmonter les limitations des méthodes actuelles, qui soit nécessitent un entraînement coûteux via des réseaux neuronaux, soit sacrifient la qualité visuelle pour la vitesse.

## Cibles chiffrées

| Critère | Cible |
|---|---|
| Fréquence d'images | ≥ 30 fps |
| Résolution | 1080p |
| Entrée | photos multiples ou vidéo |
| Qualité | photoréaliste (PSNR / SSIM / LPIPS à comparer aux références) |
| Plateforme | pipeline compatible casque XR, coûts computationnels optimisés |

> À préciser avec l'encadrant : 1080p **par œil** ou total ? 30 fps suffit-il en VR (les casques visent 72–90 Hz, avec reprojection) ? Casque autonome ou rendu PC/edge en streaming ?

## Étapes de l'étude

1. Étudier la littérature scientifique sur les champs de radiance et configurer un environnement logiciel et matériel compatible avec XR.
2. Identifier et adapter un modèle basé sur des Gaussiennes 3D à partir de points épars issus de la calibration de caméra, en optimisant la covariance anisotrope pour une représentation précise des scènes.
3. Intégrer et tester un algorithme de rendu rapide, tenant compte de la visibilité et utilisant un splatting anisotrope, dans un pipeline compatible avec un casque XR.
4. Évaluer les performances (fréquence d'images, latence, qualité visuelle, coûts computationnels) sur des ensembles de données établis et documenter les résultats.

## Références fournies

| Citekey | Référence | Dossier | État |
|---|---|---|---|
| `kamdjou2024_xr-dt-iiot` | Kamdjou, Baudry, Havard, Ouchani (2024). *Resource-Constrained eXtended Reality operated with Digital Twin in Industrial Internet of Things.* IEEE OJCOMS 5, 928–950. [10.1109/OJCOMS.2024.3356508](https://doi.org/10.1109/OJCOMS.2024.3356508) | [lien](../sources/kamdjou2024_xr-dt-iiot/) | parsé |
| `kerbl2023_3dgs` | Kerbl, Kopanas, Leimkühler, Drettakis (2023). *3D Gaussian Splatting for Real-Time Radiance Field Rendering.* ACM TOG 42(4), 139. [10.1145/3592433](https://doi.org/10.1145/3592433) | [lien](../sources/kerbl2023_3dgs/) | parsé |
| `uzun2025_gs-alive-xr` | Uzun, Riedinger, Biswas, Hetzer, Oppermann (2025). *Enabling Digital Spaces: Bringing Gaussian Splats Alive in XR.* XR Salento 2025, LNCS 15738. [10.1007/978-3-031-97769-5_6](https://doi.org/10.1007/978-3-031-97769-5_6) | [lien](../sources/uzun2025_gs-alive-xr/) | PDF manquant |
| `mirocha2025_beyond-dt` | Mirocha (2025). *Beyond Digital Twins: 3D Gaussian Splatting, Game Engines and Crossmedia Cultural Heritage Representations.* SIGGRAPH Talks '25, art. 42. [10.1145/3721239.3734094](https://doi.org/10.1145/3721239.3734094) | [lien](../sources/mirocha2025_beyond-dt/) | PDF manquant |
| `cao2025_rt-fvhp` | Cao, Zhao, Hu, Gan (2025). *Real-Time, Free-Viewpoint Holographic Patient Rendering for Telerehabilitation via a Single Camera: A Data-Driven Approach With 3D Gaussian Splatting for Real-World Adaptation.* IEEE TVCG 31(10), 7311–7323. [10.1109/TVCG.2025.3544297](https://doi.org/10.1109/TVCG.2025.3544297) | [lien](../sources/cao2025_rt-fvhp/) | PDF manquant |
