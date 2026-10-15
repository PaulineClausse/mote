# Piste R0 : micro-benchmark du décodage Smol-GS sur GPU

*Rédigé le 2026-09-29. **Pas encore implémenté** : c'est une intention documentée, à reprendre plus tard.*
Contexte : [plan_environnement.md](plan_environnement.md), section « Piste R » · [options.md](options.md), piste P7 · [fiche Smol-GS](../sources/wang2025_smol-gs/fiche.md) · [note critique du rapport runtime](../supports/rapport2026_smol-gs-quest3-runtime/note_critique.md).

## 1. Pourquoi

### La question
> **Combien de millisecondes par image coûte le décodage des splats Smol-GS sur le GPU d'un Quest 3, en stéréo ?**

### Pourquoi c'est la bonne première question
- Dans [Smol-GS](../sources/wang2025_smol-gs/fiche.md), un splat ne stocke ni couleur, ni forme, ni opacité : seulement une **feature de 8 nombres**. À **chaque image**, 4 petits MLP transforment cette feature en **opacité, couleur, rotation et échelle** (éq. 2–3, `doc:d6bdbe6/tier:standard/page:4`).
- Leur entrée contient **la direction de vue et la distance caméra–splat**. Conséquences :
  - on **ne peut pas mettre en cache** le résultat d'une image à l'autre : il change dès que la tête bouge ;
  - il faut **un décodage par œil**, soit deux par splat en stéréo.
- Ordre de grandeur (calcul personnel) : ≈ 7,7·10⁴ multiplications-additions (MAC) par splat et par œil. Pour 500k splats en stéréo, cela fait ≈ 77 GMAC par image, soit ≈ 5,5 TMAC/s à 72 Hz.
- Signal d'alerte : SqueezeMe (Meta, arXiv 2412.15171) identifie déjà le décodeur comme goulot sur Quest 3, avec seulement ≈ 180k Gaussiennes ([faisabilite_quest3.md](faisabilite_quest3.md)).

**C'est le risque n°1 de toute la piste « moteur Smol-GS sur casque » (P7).** Tant qu'on n'a pas ce chiffre, construire un moteur autour de Smol-GS reviendrait à parier. Avec lui, on décide en une session casque.

### Ce que R0 n'est pas
- Ce n'est **pas un moteur de rendu** : pas d'image, pas de tri, pas de rastérisation.
- Il n'a **pas besoin d'un modèle Smol-GS entraîné** : le coût d'un MLP ne dépend pas de la valeur de ses poids, seulement de sa taille. Des poids aléatoires suffisent pour mesurer le temps. Les vrais poids ne servent qu'à vérifier la précision FP16 (étape 4).

## 2. Ce qu'on mesure exactement

Architecture tirée du papier (Tab. A6, `page:15`) :

| MLP | Entrée | Couches | Neurones cachés | Sortie | Dépend de la vue ? |
|---|---|---|---|---|---|
| MLP_oct | 3R = 48 bits (code Morton, R = 16) | 3 | 64 | 8 | **non** : calculé une fois au chargement |
| MLP_o (opacité) | 8 + 8 + 4 = 20 | 3 | 128 | 1 | oui |
| MLP_c (couleur) | 20 | 3 | 128 | 3 | oui |
| MLP_r (rotation) | 20 | 3 | 128 | 4 | oui |
| MLP_s (échelle) | 20 | 3 | 128 | 3 | oui |

Entrée par splat et par œil : f (8) + MLP_oct (8, précalculé) + direction de vue (3) + distance (1) = 20.
**Hypothèse d'interprétation** : « 3 couches » = 3 couches linéaires (20 → 128 → 128 → sortie). À vérifier dans le code (github.com/AaltoML/Smol-GS).

Poids : ≈ 4 × 19,3k ≈ 77k paramètres, soit ≈ 0,31 MB en FP32 et 0,15 MB en FP16. C'est **trop gros pour la mémoire partagée** d'un workgroup (typiquement 32–64 kB) : les poids seront lus depuis le cache. C'est un des points que le benchmark doit révéler.

## 3. Comment

### Deux variantes, dans cet ordre

| Variante | Techno | Où ça tourne | Avantage | Inconvénient |
|---|---|---|---|---|
| **R0-U** | Compute shader **HLSL dans le projet Unity de P6** | Dans l'APK de P6, en session VR réelle | Mesuré **dans les vraies conditions** : horloges GPU d'une app VR, compositeur actif. Aucun outil nouveau | Moins de contrôle bas niveau (FP16, sous-groupes) |
| **R0-R** | **Rust + Vulkan compute** (crate `ash` ou `wgpu`), binaire autonome | Portable (Iris Xe) pour valider, puis Quest (binaire Android `aarch64-linux-android` lancé via `adb shell`, *à vérifier*, ou petite app native) | Contrôle total (FP16, sous-groupes, fusion). C'est la **première brique du moteur P7** | Risque : hors app VR, le Quest peut garder le GPU à une horloge basse. Il faut relever le niveau GPU et le mesurer |

Le mieux est de faire **R0-U d'abord** (chiffre fiable, peu de travail, dans l'app qu'on construit déjà), puis **R0-R** si P7 devient sérieuse.

### Implémentations à comparer dans le shader
1. **Naïve** : un thread = un splat × un œil ; les 4 MLP à la suite ; poids lus en mémoire globale.
2. **Fusion de la 1re couche** : les 4 MLP reçoivent **la même entrée** de 20 valeurs. Leurs 4 premières couches (20 → 128) se fusionnent en **une seule 20 → 512**, ce qui donne une meilleure réutilisation des données chargées.
3. **FP16** pour les poids et les activations, si le GPU et le shader le permettent.
4. *(optionnel)* **Par sous-groupe** : un groupe de threads traite un lot de splats comme une petite multiplication de matrices. On passerait par des matrices coopératives si Adreno les expose (*inconnu, à vérifier*).

### Protocole
- N ∈ {100k, 250k, 500k, 1M} splats × 2 yeux.
- Pour chaque configuration : 20 dispatchs de chauffe, puis 300 dispatchs chronométrés (timestamp queries GPU).
- Sortie : un CSV avec N, variante, précision, **médiane / p95 / p99 en ms**, GMAC/s effectifs, horloge GPU relevée.
- Sur Quest : mesure au **même niveau CPU/GPU** que l'app de P6. On note le niveau Meta (0–5) et la température.

## 4. Étapes

| # | Étape | Où | Critère de fin |
|---|---|---|---|
| 1 | Lire le code officiel de Smol-GS : architecture exacte des MLP, activations, format des poids | portable | Tableau §2 confirmé ou corrigé |
| 2 | Référence CPU (Python/numpy) des 4 MLP sur quelques splats | portable | Sorties de référence sauvegardées |
| 3 | Shader naïf + fusionné, FP32 puis FP16 (R0-U et/ou R0-R) | portable (Iris Xe) | **Correction** : écart max avec le CPU < 1e-4 (FP32) et mesuré en FP16. Les temps sur Iris Xe ne servent qu'à vérifier que ça tourne |
| 4 | *(optionnel)* Entraîner un vrai Smol-GS (Garden) sur le PC de l'école, exporter les poids | PC école | Erreur FP16 mesurée sur de vrais poids ; conséquence en PSNR/LPIPS |
| 5 | Session casque : 10 min de mesure dans l'app P6 | Quest 3 | CSV rempli |
| 6 | Décision (§5), consignée dans `options.md` (P7) | — | P7 activée, abandonnée ou réorientée |

## 5. Grille de décision

Budget à 72 Hz : **13,9 ms** pour *tout* (décodage + projection + tri + rastérisation + compositeur). Référence : **500k splats visibles, stéréo**.

| Temps de décodage mesuré | Lecture | Suite |
|---|---|---|
| **< 2 ms** | Le décodage est bon marché | **P7 crédible**. On passe à R1 (rendu minimal) puis R2 (portage OpenXR) |
| **2 – 6 ms** | Le décodage coûte cher mais reste jouable | Seulement avec culling agressif (ne décoder que les splats visibles), FP16, moins de splats. P7 reste possible mais sans marge |
| **> 6 ms** | Le décodage mange le budget | **Décodage Smol-GS par image : abandonné sur Quest.** Repli : « cuire » Smol-GS en 3DGS standard hors ligne (SH ajustées, covariance figée) et le rendre avec la chaîne normale. Smol-GS reste un format de transport |

## 6. Ce que R0 rapporte même si le résultat est négatif
- Un **chiffre inédit**, puisque personne n'a publié de coût de décodage Smol-GS sur casque. C'est une ligne du tableau de P6 : « coût d'un format neuronal compact sur casque autonome ».
- Un **argument appuyé sur une mesure** pour le mémoire : pourquoi on garde un format 3DGS standard pour le rendu, et où se situe la frontière entre compression (disque, réseau) et coût de rendu.
- Une **brique réutilisable** (R0-R) si P7 est activée plus tard.
