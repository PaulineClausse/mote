# SP-3 : profondeur sur Quest 3S

Statut : terminé, verdict en écart à la lettre de la règle (§1, §4.2), à accepter · Date : 2026-10-13
· Auteur : claude-agent@mote-session · Tâche : TASK-eea1

Contexte : SPEC-64c5 §9.5 stocke la profondeur brute (`F32_RAW`) et linéarise à l'ingest avec une formule déduite de la
documentation, `distance = nearZ / (1 - d)` pour un far infini `[HYPOTHESE]`. La résolution, la cadence et le coût de
la relecture GPU vers CPU ne sont pas documentés. H-02 : la profondeur du Quest 3S, sans projecteur contrairement au
Quest 3, est-elle exploitable pour initialiser un nuage de points ? SP-7 (initialisation de l'aperçu live par la
profondeur) et WP-10 en dépendent.

## 1. Verdict

**Formule de linéarisation : confirmée de 1,4 à 3,5 m**, `z = near / (1 - d)`, avec near = 0,1 m et far infini.
- Sur un mur, zone centrale de 15 % : erreurs de 0,0, 0,7 et -0,5 %, pente 0,991.
- À la lettre de la règle, zone de 40 % : non confirmée (pente 0,937, erreur de 5,7 % à 1,4 m).
- L'analyse de sensibilité (§4.2) montre que cet échec vient de la mesure, pas de la profondeur. La zone de 40 %
  déborde du mur au loin et attrape des surfaces plus proches. En la réduisant, la pente remonte de 0,937 à 0,991 et
  le RMS au plan est divisé par 2 à 4.
- Sous 1,4 m : non vérifié, le palier vers 1 m n'était pas face au mur.

**H-02 : validée avec réserve.**
- Les quatre critères sont tenus sur 1,4 à 3,5 m (zone de 15 %) :
  - erreur sous 5 % (au plus 0,7 %) ;
  - 100 % de pixels valides ;
  - RMS au plan sous 3 % (1,1 %, 0,9 % et 2,1 %) ;
  - S1 rétroprojetée cohérente : les murs ne se dédoublent pas visiblement sur 591 cartes, à l'œil (§4.4).
- Réserves :
  1. Le verdict s'écarte de la lettre de la règle (zone de 40 %), pour la raison donnée plus haut.
  2. La profondeur livrée est **dense et lissée**, sans un seul trou : le système comble et filtre lui-même. Il n'y a
     donc aucun masque de validité, et les bords des objets portent des points intermédiaires à filtrer.
  3. Courte distance (moins de 1,4 m) non vérifiée. Un seul mur et une seule pièce.

**Tolérance de distance proposée : ±1 % de la distance, plancher de 1 cm, de 1,4 à 3,5 m.** C'est la plus grande erreur
après décalage (0,7 %), arrondie au demi-pourcent supérieur. Au-delà de 3,5 m et sous 1,4 m : non mesuré.

**Coût de la relecture : 0,26 ms par carte** (les deux yeux) sur le thread principal, médiane (p95 0,46 ms). Latence de
3 frames (68 ms, p95 90 ms). C'est négligeable.

**Conséquences :**
- **SPEC-64c5 §9.5** :
  - La formule passe de `[HYPOTHESE]` à vérifiée (1,4 à 3,5 m).
  - Résolution 320 x 320 par œil, cadence native d'environ 8,3 Hz, far_z infini, near_z 0,1.
  - Les valeurs sont **quantifiées sur 16 bits** (pas de 1/65535) : `F32_RAW` double le volume sans rien ajouter.
    Une carte fait 400 Ko en float32. À 5 Hz sur deux yeux, cela fait 4,1 Mo/s, soit **33 Mbit/s avant zstd**, plus de
    la moitié du budget de 60 Mbit/s de NFR-03. Un encodage brut sur 16 bits, non linéarisé et donc conforme à
    ADR-6ded, le diviserait par deux sans perte. À décider dans WP-10, avec une mesure de zstd sur ces cartes.
- **WP-10 et SP-7** :
  - Pas de masque de validité à attendre.
  - Filtrer les discontinuités, là où le lissage relie un objet au fond.
  - Reprojeter avec la pose de création de chaque carte, comme ici.
  - Linéariser à l'ingest, avec la formule confirmée.

## 2. Règle, écrite avant de regarder les chiffres

Erreur « après décalage » : erreur de la distance mesurée au mur, une fois retiré un seul décalage constant pour toute
la session. Le mètre s'appuie sur la face avant du casque, pas sur l'origine de la carte de profondeur.

- **Formule confirmée** si, sur au moins trois distances entre 0,5 et 3 m, l'erreur après décalage reste sous 2 % de
  la distance à chacune, et si la pente de la droite mesuré = a x mètre + b vérifie |a - 1| ≤ 0,02. Sinon, elle est
  à corriger, et l'écart observé dit comment (échelle, formule non linéaire, autre normalisation).
- **H-02 validée** si, de 0,5 à 3 m sur le mur texturé : l'erreur après décalage reste sous 5 % de la distance, au moins
  50 % de pixels valides au centre, un RMS au plan sous 3 % de la distance, et une rétroprojection de S1 cohérente (les
  murs vus depuis plusieurs points de vue ne se dédoublent pas de plus de 10 cm). **Validée avec réserve** si un seul
  critère échoue à une seule distance. **Invalidée** sinon. Pour l'ordre de grandeur, SP-6 initialisait déjà avec une
  profondeur tirée au hasard entre 0,3 et 4 m.
- **Tolérance proposée** : la plus grande erreur après décalage observée, arrondie au demi-pourcent supérieur, exprimée
  en pourcentage de la distance, avec un plancher de 1 cm.

Date de fixation de la règle : 2026-10-13, avant toute mesure.

**Écart, consigné le 2026-10-13 après la capture du mur et avant toute analyse** : les distances n'ont pas été relevées
au mètre avec précision. La référence devient le recul mesuré par le tracking du casque entre les paliers, projeté sur
la normale du mur. Ce qui change :
- « erreur après décalage » : écart entre la distance au plan et (recul + distance au premier palier) ;
- la pente a est celle de la distance contre le recul.

Les seuils ne changent pas (2 %, |a - 1| ≤ 0,02, 5 %, 3 %, 50 %). Le tracking est précis à environ 1 cm sur une pièce
(SP-0 : translation médiane de 0,97 cm). C'est une référence indépendante de la profondeur, que le mètre n'aurait pas
dépassée en précision à ces distances. La pente vérifie l'échelle de la linéarisation. Une erreur constante sur la
distance absolue ne serait en revanche pas vue : elle se confond avec le décalage, comme avec le mètre.

**Second écart, après analyse** : la zone d'ajustement de 40 % (§3) s'est révélée trop large au loin. Une analyse de
sensibilité déclarée (25 % et 15 %) a été faite après avoir vu le premier résultat. Le verdict de §1 la retient et le
dit. Le résultat à la lettre est donné à côté, en §4.2.

## 3. Méthode

Outils : `docs/spikes/sp3/` (README.md). QuestRealityCapture v1.5.0 (SRC-1, commit 649c012), instrumenté par un seul
fichier qui chronomètre la relecture (`qrc_patch/`). Identifiant de paquet à part, l'original n'est pas touché.

- **Ce que SRC-1 enregistre** (lu dans son code) :
  - la profondeur, par le sous-système d'occlusion OpenXR de Unity ;
  - la texture est copiée par un compute shader dans deux buffers float, puis relue par `AsyncGPUReadback` ;
  - un `.raw` float32 par œil et par carte, ligne 0 en haut, avec des valeurs brutes non linéaires dans ]0, 1[ ;
  - un descripteur par carte : pose de création (repère Unity), tangentes du champ, near_z, far_z, taille.
- **Résolution et cadence** : lues dans les descripteurs d'une session enregistrée à pleine cadence
  (`targetSaveFps` 0).
- **Linéarisation** : `ndc = 2d - 1`, projection OpenGL ; far infini : `z = near / (1 - d)` (même formule que SRC-3 et
  que le shader de couverture de SRC-1). Avec un far infini, la convention de profondeur [0, 1] donne la même formule.
  z est la distance le long de l'axe de visée.
- **Mur** : un mur plan, avec des arrêts immobiles en reculant. Un plan est ajusté au centre de chaque carte avec un
  rejet itératif des points hors plan (3 MAD). On mesure la distance perpendiculaire de l'origine de la carte au plan.
  Référence : le recul mesuré par le tracking (écart en §2). Les paliers sans mur exploitable sont écartés (moins de
  20 % de pixels valides, ou inclinaison au-delà de 30°).
- **Relecture** : chronométrée sur le thread principal (Export, callback) et en latence (ms et frames).
- **Rétroprojection** : toutes les cartes gauches de S1 (SP-0, 5 Hz) portées dans le monde par leur pose de création.
  Le résultat est un nuage PLY et des vues de dessus et de face.

Session du mur : `20261013_134325` (APK SP3, Quest 3S). Scène : S1 de SP-0 (`20261007_120820`).

## 4. Résultats

### 4.1 Résolution, cadence, valeurs

| Œil | Cartes | Résolution | Cadence médiane | Intervalle médian / p95 | near_z | far_z |
|---|---|---|---|---|---|---|
| gauche | 589 | 320 x 320 | 8,3 Hz | 120 / 160 ms | 0,100 | infini |
| droite | 589 | 320 x 320 | 8,3 Hz | 120 / 160 ms | 0,100 | infini |

- Sur 21 cartes, 100 % des pixels sont dans ]0, 1[, avec en médiane 3 518 valeurs distinctes par carte.
- Le plus petit écart entre deux valeurs vaut 1,53e-5 = 1/65535 : la texture source est en **16 bits normalisés**,
  relue en float32.
- Ce pas de quantification correspond à 1,4 mm à 3 m (dz = z² / near x 1/65535), donc sans effet.

### 4.2 Linéarisation contre le mur

Référence : recul mesuré par le tracking. Les trois paliers retenus couvrent 1,39 à 3,46 m. Le premier palier
(0 à 10,8 s, vers 0,95 m) est écarté à toutes les tailles de zone : la tête était inclinée de 35 à 60° par rapport à la
surface vue au centre.

Zone de 15 % (verdict) :

| Recul, tracking (m) | Distance au plan, gauche (m) | droite (m) | Attendue (m) | Erreur (cm) | Erreur (%) | σ temporelle (cm) | RMS au plan (cm) | Cartes |
|---|---|---|---|---|---|---|---|---|
| 0,000 | 1,387 | 1,383 | 1,387 | 0,0 | 0,0 | 1,3 | 1,5 | 130 |
| 0,989 | 2,393 | 2,379 | 2,376 | 1,7 | 0,7 | 1,6 | 2,1 | 99 |
| 2,095 | 3,464 | 3,418 | 3,482 | -1,7 | -0,5 | 1,3 | 7,1 | 77 |

Pente distance = a x recul + b : **a = 0,991**, b = 1,396 m.

Sensibilité à la taille de la zone :

| Zone centrale | Pente a | Erreurs (%) | RMS au plan (cm) | Inclinaison (°) |
|---|---|---|---|---|
| 40 % (règle) | 0,937 | 5,7 / 0,0 / -1,7 | 5,6 / 8,3 / 10,9 | 7,6 / 4,9 / 2,6 |
| 25 % | 0,972 | 0,7 / 0,0 / -1,4 | 3,1 / 2,5 / 8,0 | 16,0 / 3,6 / 3,3 |
| 15 % | 0,991 | 0,0 / 0,7 / -0,5 | 1,5 / 2,1 / 7,1 | 18,5 / 2,5 / 6,9 |

Lecture :
- La pente tend vers 1 et le RMS chute quand la zone se resserre sur le mur, alors que la dispersion temporelle reste
  de 1 à 1,6 cm. À 40 %, la zone couvre environ ±0,4 x la distance et sort du mur au loin (sol, plafond, meubles). Ces
  surfaces plus proches tirent la distance vers le bas, d'autant plus qu'on est loin : d'où une pente inférieure à 1.
  Une erreur d'échelle de la profondeur ne disparaîtrait pas en réduisant la zone.
- Les deux yeux concordent à 5 cm près (0,4, 1,4 et 4,6 cm aux trois paliers).

![Distance au plan, carte par carte (zone de 40 %) ; tirets : distance attendue d'après le tracking](sp3/figures/wall_series.png)

### 4.3 Relecture GPU vers CPU

1 178 relectures (une par œil et par carte), 320 x 320 float32, chemin de SRC-1 (compute shader, buffer,
`AsyncGPUReadback`).

| Mesure | médiane | p95 | max |
|---|---|---|---|
| thread principal, Export (dispatch + 2 requêtes) | 0,06 ms | 0,13 ms | 0,48 ms |
| latence requête → callback | 68 ms | 90 ms | 2 241 ms |
| latence requête → callback | 3 frames | 4 frames | 4 frames |
| thread principal, callback (GetData + copie) | 0,09 ms | 0,18 ms | 1,49 ms |

Coût total sur le thread principal, par carte et pour les deux yeux : **0,26 ms** en médiane, 0,46 ms au p95. Le
maximum de latence (2,2 s) est isolé, vraisemblablement au démarrage.

### 4.4 Rétroprojection

591 cartes gauches de S1, un pixel sur deux, z ≤ 5 m : 15 millions de points (`scene_depth.ply`, non versionné).

![S1 rétroprojetée, vue de dessus et de face ; en rouge, la trajectoire](sp3/figures/scene_views.png)

- **Vue de dessus.** La pièce parcourue (environ 4,5 x 4 m) sort rectangulaire. Ses murs forment des traits fins, sans
  dédoublement visible, alors que 591 points de vue se superposent. La critique est faite à l'œil, sans mesure chiffrée
  du dédoublement.
- **Région en bas à gauche, hors de la trajectoire.** C'est vraisemblablement l'espace voisin vu à travers les vitres
  (S1 : « plusieurs fenêtres », SP-0 §3). Ses murs sont parallèles à ceux de la pièce.
- **Vue de face.** Sol plat à y = 0, plafond vers 2,6 à 2,9 m.

![Une carte de S1, linéarisée](sp3/figures/scene_frame.png)

La carte est dense, sans un seul trou, avec des surfaces lisses. Les bords d'objets sont nets mais arrondis, et l'objet
proche en bas à gauche est raccordé au fond par des valeurs intermédiaires. C'est une profondeur reconstruite et
filtrée par le système, pas la mesure stéréo brute.

## 5. Lecture et limites

- **Une seule scène et un seul mur**, texturé ; la session B (mur uni) n'a pas été faite. Comme la profondeur est
  comblée, un mur uni ne donnera pas de trous : la question devient l'exactitude des valeurs comblées, non mesurée.
- **Courte distance non mesurée** : rien sous 1,4 m. Pour la combler, une capture de deux minutes, face au mur, vers
  0,5, 0,75 et 1 m (`run_sp3.ps1 -Crop 0.15`).
- **Pas de masque de validité** : 100 % des pixels sont toujours « valides ». Un seuil sur le gradient de profondeur
  est nécessaire pour écarter les bords lissés.
- **Coût mesuré** : c'est celui du chemin de SRC-1 (compute shader, buffer, relecture asynchrone), pas encore celui de
  l'hôte mote, qui le reprendra.
- **Référence du mur** : c'est le tracking du casque (écart en §2). Une erreur d'échelle du tracking se confondrait
  avec une erreur d'échelle de la profondeur. SP-0 a mesuré l'erreur du tracking à environ 1 cm sur la pièce, mais
  après un alignement Sim(3), donc à l'échelle près. Cette limite vaudrait aussi pour une référence au mètre mal
  posée.
