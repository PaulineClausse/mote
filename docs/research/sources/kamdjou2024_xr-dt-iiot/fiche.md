---
citekey: kamdjou2024_xr-dt-iiot
mineru_doc: ad303eb
type: article de revue   # survey publié en revue (IEEE OJ-COMS)
statut: fiche complète
tags: [survey, XR, jumeau-numérique, IIoT, edge-cloud, offloading, QoS, QoE, contraintes-ressources, compression, latence, CESI-LINEACT, contexte-applicatif]
---

# Resource-Constrained eXtended Reality Operated With Digital Twin in Industrial Internet of Things

**Référence :** Kamdjou, H. M., Baudry, D., Havard, V., Ouchani, S. (2024). Resource-Constrained eXtended Reality Operated With Digital Twin in Industrial Internet of Things. *IEEE Open Journal of the Communications Society*, vol. 5, pp. 928-950. DOI [10.1109/OJCOMS.2024.3356508](https://doi.org/10.1109/OJCOMS.2024.3356508)
**Texte intégral :** [paper.md](paper.md) · [PDF](source.pdf)

> Convention de pagination : « p. N » = page N/23 du PDF (locator `doc:ad303eb/tier:standard/page:N`). Page imprimée de la revue = 927 + N.

## En une phrase
Survey (sans expérimentation propre) du laboratoire CESI LINEACT qui recense les techniques d'optimisation de performance pour l'XR (AR/VR) couplée à un jumeau numérique (DT) sur architectures edge/fog/cloud en IIoT, formalise les compromis QoS / QoE / ressources par un modèle d'optimisation pondéré, fixe des seuils de métriques recommandés et propose un agenda de recherche.

## Problème traité
- Les systèmes XR+DT actuels n'offrent pas une expérience de qualité, notamment à cause de ressources limitées pour traiter et transmettre des données complexes et massives (p. 1).
- Contraintes des dispositifs sans fil mobiles : puissance de calcul, consommation d'énergie, mémoire, autonomie de batterie (p. 3). Les AR/VR mobiles doivent faire de la reconnaissance d'objets, de voix, de gestes et de l'estimation de pose caméra « with limited battery and computation capability » (p. 3).
- La latence (délai entre requête utilisateur et réponse réseau) est présentée comme l'un des principaux défis de recherche en contexte de ressources limitées (p. 3).
- Côté rendu : l'XR implique du calcul intensif (tracking temps réel, rendu d'objets virtuels, traitement d'image) ; le rendu haute fidélité temps réel est exigeant pour le matériel, surtout avec scènes complexes et éclairage dynamique ; il faut arbitrer qualité de rendu vs performance (p. 7).
- Autres verrous listés : consommation (usage prolongé en industrie), besoin de réseau stable à haut débit pour le traitement edge/cloud et le streaming, fragmentation des dispositifs (matériels/OS hétérogènes), cybersécurité (p. 8).

## Méthode / contributions
- **Bibliométrie** (Sect. II) : requête IEEE Xplore (XR/DT × performance/optimisation/QoS/QoE × industrie/CPS/ressources contraintes/edge/cloud), traitement Excel → Power BI (p. 6). Corpus de **2432 papiers (1981 – juin 2023)** : 1706 conférences, 566 revues, 85 magazines, 64 early access, 11 livres (p. 6). Hausse marquée depuis 2017 ; 2022 = 19,94 % des publications (p. 6). Réseau de co-occurrence de termes (Fig. 6, p. 7).
- **Revue approfondie de 51 papiers clés** (IEEE Xplore + compléments Google Scholar ; critères : citations, récence, architecture, techniques d'optimisation, QoS/QoE, types de données, cas d'usage) (p. 6).
- **Comparaison à 10 surveys existants** sur 12 critères (Background, Application, XR+DT, QoS, QoE, Security, AI/ML, Edge/Cloud, Optimization, Collaboration, Resources, Comparison) — les auteurs revendiquent être les seuls à tous les couvrir (Table 1, p. 4).
- **Architecture de référence XR + DT edge/cloud** (Fig. 1, p. 2), purement illustrative (non implémentée ni évaluée dans le papier) :
  - *Actif physique* : serveur OPC (OPC-UA, collecte locale, historique/contrôle/modèle/process), opérateur en **AR** guidé sur un robot ;
  - *Serveur cloud* (via WAN) : données historiques, de modèle, contextuelles, de process ; tableau de bord en ligne (modélisation, visualisation, prédiction « live ») ;
  - *Serveur edge local* : données, visualisation, modélisation, traitement, paramètres, prédiction, optimisation, analyse, décision → alimente le **DT** consulté par un opérateur/expert en **VR** ;
  - flux « Data » (montants) et « Control » (descendants) entre les trois blocs.
- **Paradigmes de calcul** comparés qualitativement : edge (traitement local en bordure), fog (couches intermédiaires), cloudlet (mini-cloud en bordure), cloud (centralisé) ; modèle hybride recommandé (p. 8). Principe de répartition : **opérations simples à l'edge, opérations complexes déportées au cloud** (p. 14, d'après [28]).
- **Niveaux de latence réseau selon l'emplacement du calcul** (Fig. 8, p. 18) — seule grille chiffrée de latence d'architecture :

| Niveau | Emplacement | Latence indiquée |
|---|---|---|
| — | Terminaux (IoT, capteurs, **HMD**, véhicules, mobiles) | « no latency » |
| 1 | Network edge (locaux client, points d'accès, gateways) | < 10 ms |
| 2 | Access network (edge gateways, micro-cellules, nœuds edge) | [5, 12 ms] |
| 3 | Aggregation point (cloudlet, macro-cellule, C-RAN, ISP locaux) | [10, 20 ms[ |
| 4 | Core network (edge PoP, ISP régionaux, data centers cœur) | [20, 30 ms[ |
| 5 | Peering/exchange (backbone ISP, data centers entreprise) | [30, 50 ms] |
| 6 | Cloud hyperscale/public/privé | > 50 ms |

  Les niveaux 1-3 relèvent du « Mobile Edge Computing »/« Edge Computing », le fog couvre ~3-5, le cloud 5-6 (Fig. 8, p. 18).
- **Axes d'évaluation de performance** : efficacité, flexibilité/reconfigurabilité, adaptativité, robustesse, durabilité (p. 8-9). L'efficacité passe par l'optimisation du contenu de rendu (réduction du nombre de polygones, taille des textures, **compression d'assets**), du réseau (protocoles, compression, cache) et du matériel (p. 8-9).
- **Six compromis** (Fig. 7, p. 10-11) : QoE vs QoS ; performance vs qualité visuelle ; mémoire/calcul vs batterie (la compression/le streaming d'assets réduit l'empreinte mémoire et les temps de chargement, mais une compression avec pertes dégrade la qualité) ; réalisme vs interactivité ; latence vs performance ; complexité vs facilité d'usage.
- **Modèle d'optimisation combinatoire** (éq. 1, p. 11), problème qualifié de NP-difficile (p. 11) :
  `max P = f(QoS)·W_QoS + g(QoE)·W_QoE + h(Res)·W_Res` s.c. `W_QoE + W_QoS + W_Res = 1`, `QoS(i) ≥ Target_QoS(i)`, `QoE(i) ≥ Target_QoE(i)`, `Res(i) ≤ Max_power(i)`. Un poids `W_DevT` (temps de développement) est défini mais n'apparaît pas dans l'équation. Aucune résolution, instanciation ni fonction f, g, h explicite n'est fournie : seulement des seuils qualitatifs/quantitatifs par métrique (p. 11-12).
- **Agenda de recherche** (Sect. V, p. 13-19) : context-awareness et personnalisation ; interaction/collaboration contextuelle ; gestion efficace des ressources (serverless, federated clouds, énergie) ; gestion des types de données et **schémas de codage** XR-DT (compression, fusion, transmission, décodage) ; sécurité/vie privée ; approches data-driven ; coût des équipements ; processus itératif (dont **rendu adaptatif** : LOD, qualité de rendu et streaming ajustés aux ressources et au réseau, p. 16 ; **rendu et affichage économes en énergie**, p. 16) ; IA explicable/éthique/verte. Technologies émergentes : 5G/6G, cloud-fog/edge + IIoT, IA/ML (optimisation du rendu temps réel, streaming adaptatif, prédiction des interactions, p. 18), apprentissage fédéré, calcul quantique, blockchain (p. 17-19).
- **Compression sémantique** citée comme piste majeure (p. 15) : transmission de keypoints de mouvement [83], compression IA + transmission sémantique pour la vidéo volumétrique [84], livraison VR sémantique sans fil (WiserVR [85]), compression sémantique voxelisée cXR+ [86] ; promesse de réductions « exponential-scale » du trafic de synchronisation XR-DT (p. 15).

## Résultats chiffrés
Le papier est un survey : **aucune mesure expérimentale propre** (pas de fps mesuré, pas de PSNR/SSIM, pas de dataset, pas de GPU). Les chiffres sont des **seuils recommandés** (Table 2, p. 9, détaillés p. 11-12) et des repères d'architecture.

| Métrique | Valeur | Conditions / remarque |
|---|---|---|
| Frame rate | ≥ 60 fps | Recommandation (Table 2, p. 9 ; p. 11) |
| Latence | < 20 ms visé ; 20-50 ms acceptable | Texte p. 11. La Table 2 (p. 9) écrit « ≥ 20 ms », manifestement une coquille. Définie comme délai entrée utilisateur → réponse de l'environnement XR (p. 9) ; le terme *motion-to-photon* n'est **pas** employé |
| Latence réseau par niveau | de < 10 ms (network edge) à > 50 ms (cloud) | Fig. 8, p. 18 (tableau ci-dessus) |
| Précision de tracking | 0,05 à 0,5 mm | Tête et contrôleurs (Table 2, p. 9 ; p. 12) |
| Fidélité visuelle | ≥ 4K (3840×2160) recommandé ; ≥ 720p toléré | Table 2, p. 9 ; p. 12. Pas de métrique de qualité image (PSNR/SSIM/LPIPS) : non rapporté |
| Audio / réseau | « 50-500 Mbps » et « 32 / 44,1 / 48 kHz » | Lignes apparemment inversées dans la Table 2 (p. 9) : le texte p. 12 attribue 32/44,1/48 kHz à l'échantillonnage audio. Aucun débit réseau XR requis n'est chiffré explicitement |
| RAM | ≤ 80-90 % utilisée | Table 2, p. 9 ; p. 12 |
| CPU | 20-30 % (usage courant) ; < 70-80 % (tolérance) | Table 2, p. 9 ; p. 12 |
| GPU | ≤ 90-95 % | Pas de seuil minimal (p. 12) |
| Batterie | garder ≥ 10-20 % | Table 2, p. 9 ; p. 12 |
| Énergie consommée (W, J/frame) | non rapporté | — |
| Taux de compression | non rapporté | Compression citée qualitativement (p. 10, 15, 16) |
| Temps de chargement | non rapporté (métrique citée, p. 10) | — |
| Coût HMD | 300 $ à 450 000 $ | p. 16, + PC puissant requis |
| Corpus | 2432 papiers ; 51 étudiés en profondeur | p. 6 |

## Pertinence pour notre sujet
| Étape du sujet | Apport de ce papier |
|---|---|
| 1. Littérature + environnement XR | **Fort (contexte).** Cadre applicatif du labo encadrant : XR+DT industriel, opérateur AR sur l'actif physique / expert VR sur le DT, architecture edge/cloud (Fig. 1, p. 2). Typologie des afficheurs (moniteur, projection, handheld, HMD, p. 2) et des contraintes HMD/standalone : calcul, mémoire, batterie, **thermique** (p. 13). Aucun casque précis n'est nommé ni utilisé. |
| 2. Gaussiennes 3D depuis points SfM, covariance anisotrope | **Nul.** Ni NeRF, ni 3DGS, ni SfM ne sont mentionnés. Seule mention voisine : estimation de pose caméra comme tâche lourde sur mobile (p. 3). |
| 3. Rendu rapide, visibilité, splatting anisotrope, casque XR | **Indirect.** Recommandations génériques : réduction polygones/textures, compression d'assets (p. 8), rendu adaptatif LOD/qualité selon ressources et réseau (p. 16), rendu économe en énergie (p. 16), répartition edge/cloud (p. 14, 18). Aucun algorithme de rendu décrit. |
| 4. Évaluation (fps, latence, qualité, coût) | **Utile.** Grille de seuils (Table 2, p. 9) : ≥ 60 fps, < 20 ms (≤ 50 ms toléré), CPU/GPU/RAM/batterie ; distinction QoS (objectif) / QoE (subjectif : réalisme visuel, confort, cybersickness, questionnaires) (p. 10, 12) ; modèle pondéré (éq. 1, p. 11) réutilisable pour justifier un compromis qualité/fps/ressources. |

## Pour (vis-à-vis de notre problématique)
- **Aligne nos objectifs sur les attentes du labo** : l'arbitrage « performance vs qualité visuelle » (p. 10) et le constat que le rendu haute fidélité temps réel est exigeant pour le matériel (p. 7) correspondent exactement à la problématique 3DGS (photoréalisme sans entraînement neuronal coûteux ni sacrifice de qualité).
- **Seuils exploitables pour l'étape 4** : notre objectif de ≥ 30 fps en 1080p est **en dessous** de la recommandation XR du papier (≥ 60 fps, ≥ 4K recommandé / ≥ 720p toléré, p. 9). À prendre en compte pour positionner nos résultats (et motiver un objectif stéréo casque plus ambitieux).
- **Grille de latence edge/cloud (Fig. 8, p. 18)** directement transposable pour décider où exécuter le rendu 3DGS : un rendu déporté au-delà du niveau 3 (~20 ms réseau) consomme à lui seul le budget < 20 ms ; seul l'edge proche (< 10-12 ms) laisse une marge pour le rendu et l'encodage.
- **Découpage edge/cloud réutilisable** (simples à l'edge, complexes au cloud, p. 14) : l'optimisation 3DGS (entraînement des gaussiennes depuis le SfM) au cloud/edge serveur, le rasterisation au plus près du casque.
- **Compression et streaming d'assets** identifiés comme leviers mémoire/temps de chargement avec compromis sur la qualité (p. 10) ; les scènes 3DGS (millions de gaussiennes) entrent pleinement dans cette catégorie.
- **Vocabulaire QoS/QoE et cybersickness** (p. 10, 12, 13) utile pour une évaluation utilisateur complémentaire aux métriques PSNR/SSIM/LPIPS.

## Contre / limites
- **Aucune validation expérimentale** : pas de prototype, pas de casque, pas de mesure ; la Fig. 1 et l'éq. 1 restent conceptuelles (f, g, h non définies, pas de résolution) (p. 2, 11).
- **Seuils non sourcés individuellement et incohérences** dans la Table 2 (« ≥ 20 ms » pour la latence, lignes audio/réseau inversées, p. 9 vs p. 11-12) : à ne pas citer sans recouper avec une source primaire.
- **Pas de modèle de coût du rendu** : pas de notion de latence motion-to-photon, de reprojection (ATW/ASW), de rendu stéréo, de foveated rendering, ni de budget GPU par frame — éléments centraux pour 3DGS sur casque.
- **Représentation 3D absente** : rendu évoqué en termes de polygones/textures (p. 8) ; ni champs de radiance ni splatting ; seules références proches : codec de nuages de points [24] et vidéo volumétrique [54], [84] (bibliographie).
- **Orientation réseau/télécom** (revue ComSoc) : l'essentiel porte sur 5G/6G, offloading, sécurité, blockchain, quantique — peu transposable à l'algorithmique de rendu de l'étape 3.
- **Portée large et descriptive** : beaucoup de pistes génériques (IA, serverless, federated clouds) sans hiérarchisation quantitative.

## Idées à creuser pour une approche novatrice
- **[Hypothèse] Rendu 3DGS partitionné edge/casque selon la grille de latence (Fig. 8)** : optimisation des gaussiennes (SfM → covariance anisotrope) sur le serveur cloud/edge du DT (Fig. 1), rasterisation locale sur le casque d'un sous-ensemble visible, et repli sur rendu déporté edge niveau 1-2 (< 10-12 ms) quand la charge GPU dépasse le seuil de 90-95 % (Table 2). À comparer au rendu 100 % local de [uzun2025](../uzun2025_gs-alive-xr/fiche.md).
- **[Hypothèse] Streaming progressif de splats piloté par visibilité** : transmettre depuis l'edge uniquement les gaussiennes du frustum/des tuiles visibles, triées par contribution d'opacité, pour réduire mémoire et temps de chargement (compromis p. 10). Métrique cible : temps de chargement (p. 10) + fps + PSNR.
- **[Hypothèse] Instancier l'éq. 1 pour le 3DGS** : f(QoS) = fps/latence, g(QoE) = PSNR/SSIM/LPIPS (+ questionnaire cybersickness), h(Res) = VRAM/GPU/énergie ; faire varier le nombre de gaussiennes / le degré SH / la résolution pour tracer un front de Pareto qualité-coût. Donnerait au modèle théorique du labo sa première instanciation mesurée.
- **[Hypothèse] LOD adaptatif de gaussiennes** (le « rendu adaptatif » de la p. 16 appliqué au 3DGS) : élagage/fusion de gaussiennes à faible contribution selon la distance, la fovéa (si eye tracking, cité p. 16-17) et la bande passante disponible, pour tenir ≥ 60 fps stéréo.
- **[Hypothèse] Compression sémantique d'un DT gaussien** : séparer gaussiennes statiques (atelier, envoyées une fois) et dynamiques (robot, pièces) mises à jour par paramètres de pose, dans l'esprit des keypoints de mouvement [83] (p. 15), pour la synchronisation XR-DT temps réel (p. 16). Lien avec les travaux dynamiques de [cao2025](../cao2025_rt-fvhp/fiche.md).

## Citations clés
> « Resource constraints, particularly in terms of computing power, energy consumption, memory, and battery lifespan, continue to pose significant challenges for wireless devices in mobile environments » (`doc:ad303eb/tier:standard/page:3`)

> « Achieving high-fidelity rendering in real-time is demanding on the hardware, especially for complex scenes with multiple objects and dynamic lighting conditions [...] Striking a balance between rendering quality and performance is essential » (`doc:ad303eb/tier:standard/page:7`)

> « Low latency, below 20 milliseconds (ms) for real-time or near-real-time responsiveness and within the acceptable range of 20 to 50 ms » (`doc:ad303eb/tier:standard/page:11`)

> « it is essential to distribute tasks by performing simpler operations on the edge whereas offloading complex operations to the cloud » (`doc:ad303eb/tier:standard/page:14`)

> « intelligent adaptive rendering techniques. These techniques can dynamically adjust the level of detail, rendering quality, and content streaming based on the available resources and network conditions » (`doc:ad303eb/tier:standard/page:16`)

> Figure 8 — niveaux de latence par emplacement du calcul (`doc:ad303eb/tier:standard/page:18/block:2`) ; Figure 1 — architecture DT + XR edge/cloud (`doc:ad303eb/tier:standard/page:2/block:2`)

## Liens
- Papiers liés :
  - [kerbl2023_3dgs](../kerbl2023_3dgs/fiche.md) — méthode 3DGS de référence : fournit le « quoi rendre » absent de ce survey ; ses coûts (mémoire, fps) sont à confronter aux seuils de la Table 2 (≥ 60 fps, GPU ≤ 90-95 %).
  - [uzun2025_gs-alive-xr](../uzun2025_gs-alive-xr/fiche.md) — 3DGS en XR : à lire comme l'instanciation « rendu local sur casque » du compromis performance/qualité visuelle (p. 10).
  - [mirocha2025_beyond-dt](../mirocha2025_beyond-dt/fiche.md) — autre regard sur le jumeau numérique : à croiser avec l'architecture DT edge/cloud de la Fig. 1.
  - [cao2025_rt-fvhp](../cao2025_rt-fvhp/fiche.md) — rendu temps réel de contenu dynamique : pertinent pour la synchronisation XR-DT et la compression de contenus volumétriques (p. 15-16).
  - Travaux CESI LINEACT cités : Havard et al. [3] (architecture de données CPPS), Dallel et al. [4] (DT de poste de travail + VR), Havard et al. [77] (DT + VR + OPC-UA pédagogique) — bibliographie p. 19-22.
