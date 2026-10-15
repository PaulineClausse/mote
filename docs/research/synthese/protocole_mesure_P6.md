# Protocole de mesure P6 : 3DGS sur Quest 3 natif

*Rédigé le 2026-09-29, version 1, à valider.* Contexte : [plan_environnement.md](plan_environnement.md) (phases 2 et 4, P3′ v1) · [options.md](options.md) (P6) · [faisabilite_quest3.md](faisabilite_quest3.md).

**Question de P6 :** sur des scènes réelles, avec des budgets de Gaussiennes explicites, que tient le Quest 3 en natif (temps d'image p50/p95/p99, images perdues, puissance, thermique, latence) et à quel coût en qualité ?
**Hypothèse H1** ([plan](plan_environnement.md)) : avec au plus 0,3–0,5 M Gaussiennes rendues, un *render scale* ≥ 0,85 et le tri partagé, le Quest 3 natif tient **72 Hz au p99** en régime thermique stable.

## 1. Principe : deux modes de mesure

Mesurer pendant qu'une personne porte le casque n'est **pas reproductible** : chaque passage produit une trajectoire différente, donc une charge GPU différente. On sépare donc :

| Mode | Comment | Mesure | Ne mesure pas |
|---|---|---|---|
| **Rejeu** (l'essentiel des mesures) | Le casque est posé sur un support fixe. L'app **remplace la pose suivie par une trajectoire enregistrée**, rejouée image par image | Temps d'image, images perdues, puissance, thermique, qualité : **reproductible** d'une condition à l'autre | La latence réelle (la pose ne vient pas des capteurs) |
| **Direct** (quelques sessions) | Une personne porte le casque et bouge librement | Latence, contrôle de réalisme (la charge du rejeu ressemble-t-elle à la charge réelle ?) | Comparaisons fines entre conditions |

## 2. Trajectoires

| Source | Scènes | Détail |
|---|---|---|
| **EyeNavGS** ([symmru.github.io/EyeNavGS](https://symmru.github.io/EyeNavGS/), arXiv 2506.02380, CC BY 4.0) | **bicycle, drjohnson, truck** | Traces **réelles** de 46 participants sur Quest Pro : pose 6DoF + regard, dans le repère des modèles 3DGS originaux, avec facteur d'échelle par scène. *À vérifier* : le repère des modèles Taming doit être le même (même COLMAP), ce qui est attendu |
| **Trajectoires scriptées** | les 4 scènes, dont **bonsai** (absent d'EyeNavGS) | (a) tour lent autour du centre ; (b) **approche jusqu'à 30 cm d'un objet**, pire cas de *fill-rate* (aras-p #145) ; (c) **rotation de tête rapide**, lacet à 200 °/s, pire cas pour le tri et le popping ; (d) immobile (référence) |

Pour chaque scène : **3 traces EyeNavGS représentatives** (médiane et extrêmes de vitesse angulaire) + les 4 traces scriptées. Chaque trace est découpée ou rebouclée à **60 s**.

## 3. Configuration fixe du casque (à noter dans chaque fichier de résultats)

| Réglage | Valeur | Pourquoi |
|---|---|---|
| **Application SpaceWarp (ASW)** | **désactivé** | Sinon les images manquées sont masquées par interpolation, et les mesures sont fausses |
| **Résolution dynamique** | **désactivée** | Sinon elle se confond avec le levier *render scale* |
| Passthrough | désactivé | Sinon les niveaux GPU 3–4 sont indisponibles (doc Meta) |
| Niveaux CPU/GPU | **fixés et notés** (ex. CPU 4 / GPU 4) | Ce sont des indications, pas des garanties : on relève la fréquence réelle |
| Fixed Foveated Rendering de Meta | désactivé en v1 | *Levier potentiel à tester à part* : il ne s'applique que si les splats sont rastérisés dans la texture de l'œil. Or aras-p passe par une texture intermédiaire (*à vérifier*) |
| Fréquence | 72 Hz (tout) ; 90 Hz (sous-ensemble) | — |
| Alimentation | **sur batterie**, charge ≥ 50 %, câble débranché pendant les mesures | La charge fausse la thermique et la puissance |
| Environnement | température de la pièce notée ; casque sur support, même position | Thermique comparable |

## 4. Grille de conditions (par étapes, pour tenir en 1 à 3 jours de casque)

Grille complète : 4 scènes × 3 paliers × 2 fabrications (A/B) × 3 *render scales* × tri partagé on/off × 2 fréquences = 288 conditions, **trop pour le temps disponible**. On procède par étapes.

| Étape | Conditions | Durée estimée |
|---|---|---|
| **0. Contrôles** | Leg de Kleinbeck (reproduire la Tab. 4 de leur papier) · bicycle en 3DGS complet 6,1 M (effondrement attendu, point de référence) | 20 min |
| **1. Balayage** | 4 scènes × paliers A {150k, 300k, 500k} × *render scale* {0,7 ; 0,85 ; 1,0} × tri partagé {on, off}, à 72 Hz, trace EyeNavGS médiane (ou tour lent pour bonsai) = **72 conditions × 60 s** | ≈ 1 h 30 |
| **2. Paliers emboîtés** | Les 3 meilleures configurations de l'étape 1 × paliers B0/B1 | 30 min |
| **3. Pires cas** | Traces « approche » et « rotation rapide » sur les configurations retenues | 30 min |
| **4. 90 Hz** | Les configurations qui tiennent 72 Hz, rejouées à 90 Hz | 30 min |
| **5. Thermique longue** | 2 configurations × 30 min + 1 × 60 min, trace EyeNavGS en boucle | 2 h |
| **6. Direct** | Une personne, 3 configurations × 3 min : latence et contrôle de réalisme | 30 min |

**Précautions :**
- **Chauffe** de 5 min avant chaque bloc, jusqu'à ce que la température se stabilise.
- **Ordre des conditions tiré au hasard** dans chaque bloc, pour ne pas confondre dérive thermique et effet de la condition.
- **3 répétitions** des conditions de l'étape 1 retenues pour la suite.

## 5. Ce qu'on enregistre

| Grandeur | Outil | Remarque |
|---|---|---|
| Temps d'image app GPU et CPU, images perdues/périmées, fps, niveaux et fréquences CPU/GPU, utilisation, température, puissance | **OVR Metrics Tool**, mode rapport CSV | Même outil que VCIP 2026 : chiffres comparables |
| Temps par passe (tri, préparation, rastérisation, composition) | **Timestamps GPU dans l'app**, autour des passes compute d'aras-p | Pour savoir *où* part le temps |
| Gaussiennes visibles après culling, pixels couverts, overdraw | Compteurs GPU de l'app (phase 1 du plan) | Pour relier le coût à la charge |
| Pose rejouée + index d'image + palier/config actifs | Journal de l'app | Pour aligner les mesures sur la trajectoire |
| Détail par tuile, ponctuellement | RenderDoc Meta Fork, Perfetto | Seulement pour les anomalies |

**Statistiques rapportées par condition :** p50 / p95 / **p99** du temps d'image GPU et CPU ; % d'images perdues ; puissance moyenne ; température en fin de run ; intervalle de confiance sur les 3 répétitions.

## 6. Qualité

- **Qualité statique** : sur les vues de test standard de chaque dataset (une image sur 8), PSNR / SSIM / LPIPS de chaque palier contre les photos. Calculée **sur PC avec le même moteur (aras-p)** pour que le rendu soit comparable.
- **Imputation en trois temps** : 3DGS INRIA complet → palier Taming rendu sur PC → **même palier rendu sur Quest**, sur quelques images capturées sur le casque. Le dernier écart doit être quasi nul, sinon il y a un problème de précision ou de format sur casque.
- **Qualité temporelle** : **FLIP temporel** sur les séquences rejouées, rendues hors ligne. Il mesure le popping, notamment aux changements de palier et avec le tri partagé.
- **Erreur stéréo du tri partagé** : pour l'œil gauche, tri propre contre tri partagé, puis FLIP. Personne ne l'a mesurée (Kleinbeck, Nebula).

## 7. Latence : ce qu'on peut raisonnablement mesurer

Sur Quest, le compositeur **reprojette toujours la dernière image selon la pose la plus récente** (timewarp). La latence de *rotation* dépend donc surtout du compositeur, pas de notre rendu, **tant qu'on ne perd pas d'images**. Ce que notre rendu fait varier :
- la **latence de l'application** : entre la lecture de la pose et l'image prête, soit environ le temps d'image ;
- la **latence effective** quand des images sont perdues : on réaffiche une image vieille d'un cycle ou plus ; en translation et pour le contenu, le timewarp ne compense pas.

**Plan :**
1. **Latence de l'application** (chaque condition) : horodater la pose utilisée et la fin du rendu GPU dans l'app. Vérifier aussi si OVR Metrics expose une latence (*à vérifier*).
2. **Motion-to-photon externe** (mode direct, quelques points) : caméra rapide à 240 fps (ralenti d'un smartphone) qui filme à la fois un repère physique solidaire du casque et l'image dans la lentille, pendant un mouvement brusque. Résolution ≈ 4 ms. Une photodiode serait plus précise (à voir avec l'encadrant, question 4 de la note).
3. **Présentation honnête** : P6 rapporte la latence de l'application pour toutes les conditions et le motion-to-photon externe sur quelques-unes. Il ne prétend pas mesurer le motion-to-photon partout.

## 8. Ce qu'il faut préparer avant la première session

- [ ] App Unity avec : chargement des paliers, **mode rejeu** (lecture d'une trace CSV à la place de la pose), sélection de la condition par fichier de config, timestamps GPU, compteurs, journal.
- [ ] Traces EyeNavGS converties dans le repère Unity (vérifier l'alignement sur une vue connue) + traces scriptées.
- [ ] Paliers de la phase 2 importés et vérifiés (`.ply` standard : contrôle PSNR > 40 dB contre le rendu Taming).
- [ ] Script d'enchaînement (liste de conditions dans un ordre aléatoire) et nommage des fichiers CSV.
- [ ] Casque : mode développeur, OVR Metrics Tool installé, ASW et résolution dynamique désactivés.
- [ ] Support fixe pour le casque ; smartphone à 240 fps pour la latence.
- [ ] Script Python d'analyse : CSV → p50/p95/p99, images perdues, graphiques.
