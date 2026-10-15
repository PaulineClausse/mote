# Plan d'environnement : étape 1 (volet logiciel et matériel)

Rédigé le 2026-09-29, **révisé le même jour**. Le **Quest 3** et un **PC avec un bon GPU** seront **empruntables à l'école** (à confirmer). Le portable personnel (i5-1135G7 / Intel Iris Xe / 16 Go, sans CUDA) ne sert plus que d'appoint (rédaction, analyse Python des CSV, visualisation web).

**Conséquences de la révision :**
- l'entraînement se fait en local sur le PC de l'école, sans cloud ;
- la phase 3 (téléphone substitut) devient inutile ;
- le PC-VR (Quest 3 en Link sur le PC de l'école) devient une **deuxième plateforme de mesure**, en plus du Quest 3 natif.

Faits et sources : [faisabilite_quest3.md](faisabilite_quest3.md) · antériorité : [anteriorite_p3_p6.md](anteriorite_p3_p6.md) · options : [options.md](options.md).

## Principe

On sépare ce qui **dépend du matériel** (temps GPU, puissance, thermique, motion-to-photon) de ce qui **n'en dépend pas** (Gaussiennes visibles, couverture en pixels, overdraw, coût du tri). Tout ce qui ne dépend pas du matériel se développe et se mesure sur le PC de l'école, sans casque. Les sessions sur Quest 3, préparées à l'avance, servent à **mesurer ce qui dépend du matériel**. Il reste utile de tout préparer avant chaque créneau casque, car le matériel est prêté.

Ce qu'on peut raisonnablement attendre du Quest 3 natif, d'après les sources réunies :
- **≈ 150k** Gaussiennes : recommandation officielle de Meta ;
- **≈ 180–200k** : mesures académiques (SqueezeMe, Kleinbeck) ;
- **≈ 400–500k** : meilleurs chiffres annoncés à 72 Hz (fork ninjamode, Gracia).

Une scène réelle en compte **1 à 6 M**. **L'objectif « bonnes perfs sur Quest 3 » se formule donc en Gaussiennes *rendues par image* (≤ 0,3–0,5 M), pas en taille de scène.** Le coût dominant sur Quest est le *fill-rate* (pixels × taille des splats × overdraw), plus que le nombre de splats (aras-p #145, ATHENA/VCIP 2026).

## Avant d'emprunter : ce qu'il faut vérifier

| Matériel | À vérifier | Pourquoi |
|---|---|---|
| PC de l'école | Modèle de GPU NVIDIA et **VRAM** (≥ 12 Go pour Taming/gsplat, 24 Go pour le 3DGS officiel en qualité papier) ; droits administrateur (installer CUDA, Unity, Python) ; ≥ 100 Go libres ; port USB-C 3 ou Wi-Fi 6 pour Quest Link | Entraînement et PC-VR |
| Quest 3 | Compte Meta avec **mode développeur** activable (organisation développeur Meta), câble USB-C data, qui gère le compte (ne pas réinitialiser un casque partagé sans accord) | Installer des APK, utiliser OVR Metrics, adb, Perfetto |
| Durée | Idéalement **un créneau régulier** (1 à 2 demi-journées par semaine) plutôt qu'un seul prêt | Itérer : mesurer, corriger, remesurer |

## Phase 0 : poste de développement (semaine 1, 0 €)

| # | Action | Détail | Critère de fin |
|---|---|---|---|
| 0.1 | Installer **Unity 6 LTS** (URP) + **UnityGaussianSplatting (aras-p) ≥ v1.1**, **sur le PC de l'école** | Forcer **D3D12** (Project Settings → Player → Graphics APIs) : **DX11 ne marche pas**. Ajouter le module Android Build Support (build Quest) et OpenXR / Meta XR. Le portable Iris Xe peut servir de poste d'appoint, mais le tri GPU n'y a jamais été testé | La scène d'exemple s'affiche sur PC, puis dans le Quest en Link |
| 0.2 | Télécharger les **modèles pré-entraînés INRIA** (Mip-NeRF 360, T&T, Deep Blending) | `models.zip`, 14,7 Go ([lien](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/pretrained/models.zip)). **Pas besoin d'entraîner pour démarrer.** Vérifier l'espace disque avant | `bicycle`, `garden`, `room`, `truck` importés dans Unity |
| 0.3 | Cloner le dépôt **Kleinbeck** (Unity **2022.3**, projet séparé) + scène Leg ([osf.io/tuwh5](https://osf.io/tuwh5)) | C'est la baseline Quest 3 publiée, qui sert de **point de contrôle** | Leg s'affiche ; options de tri partagé repérées dans le code |
| 0.4 | **Premier test de faisabilité sur Quest 3 natif** : build APK Vulkan, scène d'exemple puis `garden` élagué à ~300k, mesure avec OVR Metrics Tool | C'est le test qui répond directement à « peut-on avoir de bonnes perfs sur Quest 3 ? ». Attention au bug de tri Adreno (aras-p #112) : utiliser DeviceRadixSort ≥ v1.0 (#146), mode Multi-Pass (#201) | Un chiffre GPU time / fps à 72 Hz pour 1 à 2 budgets |
| 0.5 | **Point de contrôle Kleinbeck** : scène Leg sur le même Quest | On doit retrouver l'ordre de grandeur de leur Tab. 4 (10–27 ms). Sinon, c'est notre chaîne qui est en cause, pas la méthode | Écart à Kleinbeck documenté |

## Phase 1 : instrumentation indépendante du matériel (semaines 2–3)

Objectif : un **banc de mesure logiciel** qui donne, pour une trajectoire de tête et une configuration de rendu, les grandeurs qui pilotent le coût sur Quest. Tout se mesure **à la résolution Quest (2 × 1680×1760 par défaut)**.

1. **Trajectoires de tête scriptées** : cercle, marche vers un objet proche (cas pathologique de fill-rate, aras-p #145), rotation rapide. Rejouables à l'identique.
2. **Compteurs** exportés en CSV à chaque image :
   - Gaussiennes après culling ;
   - pixels couverts ;
   - overdraw moyen et p95 par pixel ;
   - paires tuile-Gaussienne ;
   - temps de tri et de rastérisation (GPU timestamps Unity, *relatifs*).
3. **Leviers exposés** en paramètres runtime (ce sont les futures variables de P3′) :
   - *render scale* ;
   - budget de Gaussiennes (élagage opacité × échelle) ;
   - tri partagé entre les yeux / par œil ;
   - tri toutes les N images ;
   - `maxStdDev` (taille max d'un splat) ;
   - rayon fovéal fixe ;
   - reprendre le PR aras-p **#225** (covariance/SH calculées une fois pour les deux yeux, −40 % d'ALU annoncé).
4. **Qualité** : capture d'images de référence vs dégradées, puis PSNR/SSIM/LPIPS et FLIP temporel (hors Unity, en Python, CPU suffit).

Livrable : courbes *pixels traités* et *Gaussiennes visibles* en fonction de chaque levier. C'est déjà la moitié de la caractérisation que VCIP 2026 fait sur Quest, **mais avec des compteurs explicites**, alors que VCIP ne donne pas de nombre absolu de splats.

## Phase 2 : modèles « dimensionnés casque » (étape 2 du sujet, en parallèle de la phase 1)

**Scènes retenues (décision du 2026-09-29)** : les 4 scènes de l'étude utilisateurs de [VRSplat](../sources/tu2025_vrsplat/fiche.md), pour pouvoir comparer directement nos résultats natifs Quest 3 aux leurs (PC-VR), plus la scène Leg de Kleinbeck comme point de contrôle.

| Scène | Dataset | Gaussiennes (3DGS INRIA) | Type |
|---|---|---|---|
| bonsai | Mip-NeRF 360 | 1,24 M | intérieur, petit |
| truck | Tanks & Temples | 2,54 M | extérieur, objet central |
| drjohnson | Deep Blending | 3,41 M | intérieur, pièces |
| bicycle | Mip-NeRF 360 | 6,13 M | extérieur, grand (test de charge) |

**Données, sur le PC de l'école** : `python outils/telecharger_donnees.py D:\donnees_ir --modeles --kleinbeck`
- Le script **n'extrait que les 4 scènes** directement depuis les serveurs, grâce aux requêtes HTTP partielles, sans télécharger les archives entières. **≈ 10,8 Go au lieu de 31 Go** : photos + COLMAP 4,3 Go, modèles 3DGS INRIA des 4 scènes 3,3 Go, Kleinbeck 3,2 Go.
- Testé le 2026-09-29 (extraction partielle vérifiée par CRC, reprise après coupure). `--liste` affiche le plan sans rien télécharger.
- Les photos + COLMAP sont **indispensables à Taming**, qui ré-entraîne depuis la reconstruction et pas depuis un modèle 3DGS.
- Charge d'entraînement : 4 scènes × (3 paliers A + 1 modèle B) = **16 entraînements**, ≈ 11 min chacun, soit ≈ 3 h.

C'est ici que l'étape 2 du sujet devient concrète : produire, pour chaque scène, des variantes à **budget exact** de 150k / 300k / 500k / 1M Gaussiennes.

- **Taming 3DGS** (budget B exact, 7–11 min sur GPU haut de gamme) ✅ [Mallick 2024](../sources/mallick2024_taming-3dgs/fiche.md), ou **gsplat** (4× moins de VRAM que l'implémentation officielle, tient sur un T4 de 16 Go).
- **Sur le PC de l'école** (CUDA local). Selon la VRAM, choisir Taming ou gsplat (≥ 12 Go) ou le 3DGS officiel (24 Go). Compter ~30 à 60 min par scène complète sur un GPU haut de gamme, moins sous budget (inféré).
- Solution de repli si le PC est indisponible ou si la VRAM est trop faible : Kaggle (≈ 30 h de GPU par semaine, gratuit) ou RunPod (RTX 4090 ≈ 0,34 $/h).
- Variante sans entraînement : élagage post-hoc des modèles INRIA (LightGaussian, Speedy-Splat) pour comparer.
- **Décision du 2026-09-29 : scènes INRIA uniquement pour la v1.** Les scènes « maison » (capture Scaniverse ou photos + COLMAP d'un atelier, pour une scène alignée LINEACT) restent un **point ouvert à discuter avec l'encadrant** (question 3 de la note).

## P3′ v1 : contrôleur à paliers Taming (décision du 2026-09-29)

**Principe :** on commence par des paliers discrets, et le vrai LOD (Hierarchical 3DGS, Octree-GS) viendra en v2. Le contrôleur choisit à chaque image parmi : **palier** {150k, 300k, 500k} × *render scale* {0,7 ; 0,85 ; 1,0} × tri partagé {on, off}. Objectif : **p99 du temps d'image ≤ budget** (13,9 ms à 72 Hz), en maximisant la qualité. On part d'une règle simple à hystérésis, dans l'esprit de MoQSplat mais sur plusieurs leviers, avant de formaliser selon l'éq. 1 de Kamdjou.

**Deux façons de fabriquer les paliers, à comparer en phase 2 :**

| | A. Paliers indépendants | B. Paliers emboîtés (préfixes) |
|---|---|---|
| Fabrication | 3 entraînements Taming, B = 150k, 300k, 500k | 1 entraînement Taming à 500k, Gaussiennes **classées par importance** (score de Taming ou de Speedy-Splat) ; palier k = les k premières |
| Qualité à budget égal | la meilleure : chaque palier est optimisé pour son budget | probablement moins bonne pour les petits paliers *(à mesurer)* |
| Mémoire GPU | 3 jeux de données (≈ 950k Gaussiennes au total) | **1 seul** jeu de 500k : un palier = un nombre de splats à dessiner |
| Changement de palier | **saut visible** : les Gaussiennes des deux modèles n'ont rien en commun | **doux** : on ajoute ou retire des splats, sans tout remplacer |
| Coût du changement | changer de buffer | changer un compteur |

L'option B ressemble aux LOD continus par préfixe (Matryoshka GS, CLOD-3DGS, voir [anteriorite_p3_p6.md](anteriorite_p3_p6.md)), mais sans ré-entraînement dédié. **Mesure clé de la phase 2 : l'écart de LPIPS entre A et B à 150k et 300k.** Si l'écart est faible, B l'emporte, car les changements de palier sont doux et un seul jeu de données suffit.

### Réglages de Taming (proposition du 2026-09-29)

| Argument | Valeur | Pourquoi |
|---|---|---|
| `--mode final_count --budget` | 150000 / 300000 / 500000 (A) ; 500000 (B) | Budget exact = palier |
| `--ho_iteration` | **> nombre d'itérations** (ex. 999999), soit mode haute opacité **désactivé** | Sinon le `.ply` stocke l'opacité en `abs` et le plugin Unity l'affiche faux (voir la [fiche Taming](../sources/mallick2024_taming-3dgs/fiche.md)). **Variante de contrôle** sur une scène : haute opacité + conversion `logit(clamp(|x|))` à l'export, pour chiffrer ce qu'on perd |
| `--sh_lower` | activé | Plus rapide ; seul le calendrier des SH change |
| `--cams` | 10 (défaut) | Nombre de vues pour le score de densification |
| Itérations, résolution | 30k ; protocole 3DGS (images_4 en extérieur, images_2 en intérieur pour Mip-NeRF 360), via le `full_eval.py` de Taming | Comparable à 3DGS, VRSplat et au papier |
| Degré des SH | 3 à l'entraînement | La réduction des SH reste un levier au moment de l'import dans Unity |

**Vérification systématique** : ouvrir chaque `.ply` dans aras-p et comparer avec le rendu de référence de Taming sur 3 vues de test (PSNR > 40 dB entre les deux, sinon problème de format).

### Classement d'importance pour les paliers emboîtés (option B)

| Score | Principe | Pour | Contre |
|---|---|---|---|
| **Significance globale** ([LightGaussian](../sources/fan2023_lightgaussian/fiche.md)) | Σ sur les vues d'entraînement : pixels touchés × opacité × transmittance × volume^0,1 | Passe avant seule, simple ; éprouvé (≈ 66 % élagables sans perte) | Dépend des vues d'entraînement ; les points de vue VR hors distribution sont mal couverts |
| **Score hessien** ([Speedy-Splat](../sources/hanson2024_speedy-splat/fiche.md)) | Σ (∇_g I)², sensibilité de l'image à chaque Gaussienne | Mesure l'effet réel sur l'image ; sous-produit du backward | Élagage plus agressif = LPIPS moins bon dans le papier (à tempérer : ratio différent) |
| Score de Taming | Gradient, pixels, opacité, etc. pondérés | Déjà dans le code | **Conçu pour choisir où *ajouter*** ; le gradient ≈ 0 à la convergence, donc peu adapté pour retirer |
| Opacité × volume | Trivial | Référence plancher | Ignore la visibilité |

**Proposition : significance globale en score principal, score hessien en second, opacité × volume comme plancher.**

**Point clé : l'affinage.** Les méthodes d'élagage ré-affinent toujours après avoir retiré des Gaussiennes (LightGaussian : 5000 itérations). Des préfixes bruts ne le sont pas. Deux sous-variantes :
- **B0** : classer puis couper, sans ré-entraînement. Gratuit, mais probablement moins bon.
- **B1** : classer, puis **affiner en rendant à chaque itération un préfixe de taille aléatoire** (150k à 500k), dans l'esprit de Matryoshka GS ([anteriorite_p3_p6.md](anteriorite_p3_p6.md)). Tous les préfixes s'améliorent en même temps et l'emboîtement est conservé. Coût : quelques milliers d'itérations, à écrire (petite modification de la boucle de Taming).

**Grille de la phase 2, par scène (validée le 2026-09-29) :**
- A : 3 entraînements (150k, 300k, 500k) ;
- B : 1 entraînement à 500k, puis préfixes 150k / 300k selon les 3 scores (B0) ;
- B1 : un affinage avec le meilleur score.

On mesure le **LPIPS à 150k et 300k** : A contre B0 contre B1. On rend ensuite ces paliers sur le Quest, puisque c'est le même format.

**Risque principal : le popping au changement de palier** (option A surtout). Deux parades à tester :
- un **fondu d'opacité** sur quelques images, au prix du rendu des deux paliers pendant le fondu ;
- basculer **pendant une rotation rapide de la tête**, qui masque le changement. Ça rejoint la composante anticipative de P3′.

Le changement de palier se mesure par **FLIP temporel**.

**Pourquoi c'est un bon premier pas :**
- tout reste au **format standard**, donc lisible par aras-p sans modifier le rasteriseur ;
- les paliers sont **exactement ceux dont P6 a besoin** : le banc de mesure et le contrôleur partagent les mêmes données ;
- le contrôleur v1 donne la **référence** contre laquelle le LOD v2 devra prouver son gain.

## Phase 3 : proxy matériel sans casque (**devenue optionnelle** : le Quest 3 de l'école rend cette phase inutile)

À garder seulement comme solution de repli si l'accès au casque est trop rare.

- **Snapdragon 8 Gen 2** (Galaxy S23 / S23+ / S23 Ultra, Xiaomi 13, OnePlus 11…) : **même GPU Adreno 740** que le Quest 3/3S. Un contributeur du dépôt aras-p le confirme (#187).
- Build Android **Vulkan** (pas GLES : aras-p #26) du même projet, rendu hors écran **2 × 1680×1760**, timings GPU via **Snapdragon Profiler** ou Android GPU Inspector.
- Correction d'horloge : GPU Quest 599–640 MHz contre 680–719 MHz sur téléphone, soit **× 0,83–0,94**, plus une marge thermique.
- **Étalonnage obligatoire** : reproduire l'ordre de grandeur de la Tab. 4 de Kleinbeck (Leg, 10–27 ms) avant d'extrapoler quoi que ce soit.
- Attention au bug de tri Adreno (aras-p #112, ouvert). Utiliser DeviceRadixSort ≥ v1.0 (#146).

Le **Meta XR Simulator ne sert à rien pour la performance** : il n'émule pas le matériel.

## Phase 4 : campagne de mesure sur Quest 3 réel (natif + PC-VR)

**Casque :** prêt de l'école. Si le prêt tombe, repli sur une location (CCL Live, 60 € HT/jour) ou un Quest 3S (359,99 €, même SoC et même résolution de rendu).

**Deux plateformes, même casque :**
- **Quest 3 natif** : le cœur de P6 ;
- **PC-VR via Quest Link** sur le PC de l'école : la référence, comparable à VRSplat et Kleinbeck (Varjo/4090). Elle permet aussi de voir ce que coûte le passage en natif.

**Préparer avant d'avoir le casque :**
- APK prêt ;
- scènes aux budgets 150k / 300k / 500k / 1M ;
- *render scale* 0,7 / 0,85 / 1,0 ;
- 72 et 90 Hz ;
- tri partagé on/off ;
- sessions de 5 min pour atteindre le régime thermique stable, comme le fait [Mobile-GS](../sources/du2026_mobile-gs/fiche.md), puis **quelques runs longs de 15, 30 et 60 min** sur les configurations retenues, pour voir le bridage thermique. Un gain qui tient 30 s puis déclenche du bridage n'en est pas un ;
- **méthodes de tri** comme axe de mesure : tri radix GPU (aras-p), tri partagé entre les yeux, et si possible un rendu sans tri à la Mobile-GS.

**Métriques QoS** : on rapporte **p50 / p95 / p99** du temps d'image CPU et GPU, les images perdues ou périmées, la fréquence GPU, la puissance et la température. Pas de fps moyen seul : une série 11 / 12 / 11 / 45 / 11 ms est un échec en VR même si la moyenne est bonne.

**Imputation de la qualité, en trois temps** : 3DGS d'origine → modèle réduit ou compressé rendu **hors ligne sur PC** → même modèle **rendu sur Quest**. On capture les mêmes vues et on calcule PSNR, SSIM, LPIPS et FLIP temporel à chaque étage. Le rendu sur casque ne doit pas se voir imputer une perte qui vient de la compression ou du budget.

**Outils sur casque :**
- **OVR Metrics Tool** en mode CSV : GPU time, stale frames, puissance, throttling. C'est l'outil de VCIP 2026, donc les chiffres seront comparables ;
- **Perfetto** via Meta Quest Developer Hub ;
- **RenderDoc Meta Fork** pour le détail par tuile.

**Motion-to-photon** : aucun outil logiciel ne le donne. Protocole à concevoir, *hypothèse* : filmer à 240 fps la lentille et un repère physique solidaire du casque pendant une rotation brusque, puis mesurer l'écart en images (résolution ≈ 4 ms). À valider avec l'encadrant ; une photodiode sur l'écran serait plus précise.

**Protocole détaillé de la phase 4 : [protocole_mesure_P6.md](protocole_mesure_P6.md)** (rejeu de traces EyeNavGS et scriptées, grille par étapes, métriques, qualité, latence).

## Ce que la phase 4 doit trancher

La question « peut-on avoir de bonnes perfs sur Quest 3 ? » devient mesurable :

> **H1** : sur des scènes réelles (Mip-NeRF 360), avec au plus 0,3–0,5 M Gaussiennes rendues par image, *render scale* ≥ 0,85 et tri partagé, le Quest 3 natif tient 72 Hz au p95 en régime thermique stable, avec une perte de LPIPS ≤ X par rapport au modèle complet.

Si H1 tient, c'est un résultat P6 publiable. Si elle ne tient que dans certaines zones de la scène ou pour certains mouvements, c'est l'argument direct pour **P3′** : aucun réglage fixe ne tient la cadence partout, il faut un contrôleur qui ajuste les leviers en ligne. Selon VCIP 2026, la densité de splats n'est efficace qu'à l'approche du budget : le contrôleur doit donc choisir *quel* levier actionner selon le régime.

## Piste R (en réserve) : moteur natif Rust/Vulkan

Origine : rapport [smol-gs-quest3-runtime](../supports/rapport2026_smol-gs-quest3-runtime/note_critique.md) (2026-09-29). Idée : un runtime 3DGS natif sur Quest 3, piloté par le GPU, en Rust, Vulkan et OpenXR. **On le garde en réserve, sans l'abandonner.** Avec un agent de code, écrire le moteur va vite. Ce qui reste coûteux, ce sont les créneaux casque et le débogage propre au Quest (pilote Adreno, OpenXR, APK).

**Déclencheurs** (un seul suffit) :
- le profilage de la phase 4 montre que **Unity ou le plugin aras-p** coûte une part importante du temps d'image, au-delà du travail GPU utile ;
- P3′ a besoin de leviers que le plugin n'expose pas proprement (décodage partiel, ordonnancement fin du tri, *multiview*) ;
- le micro-benchmark R0 montre que le décodage de Smol-GS tient dans le budget.

**Ce qu'on peut faire dès maintenant, sans casque** (Rust 1.95 et Vulkan 1.3 sont déjà installés sur le portable ; Iris Xe expose des sous-groupes de 8 à 32) :

| # | Brique | Où | Ce qu'elle mesure |
|---|---|---|---|
| R0 | **Micro-benchmark des 4 MLP de Smol-GS** en compute Vulkan (FP32 et FP16), sur 100k / 250k / 500k splats × 2 yeux | portable → Quest | Le coût réel du décodage, donc le risque n°1 du rapport. Sur le portable, le chiffre sert seulement à valider le code |
| R1 | Rendu 3DGS de référence minimal (PLY → projection → tri radix → rastérisation), desktop | portable / PC école | Correction, comparaison avec aras-p à scène égale |
| R2 | Portage Android + OpenXR, stéréo | Quest | La même courbe « Gaussiennes → temps d'image » qu'avec aras-p, pour savoir si le moteur maison fait mieux |

R0 est aussi la **première brique** du moteur : si la piste R est activée, rien n'est perdu. Détail (pourquoi, comment, étapes, grille de décision) : [piste_R0_microbench_smolgs.md](piste_R0_microbench_smolgs.md).

## Budget

| Poste | Coût |
|---|---|
| Phases 0–2 | 0 € (PC de l'école) |
| Phase 3 | abandonnée |
| Phase 4 | 0 € (prêt de l'école) ; repli : 60–200 € HT de location |
