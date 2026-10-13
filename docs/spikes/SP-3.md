# SP-3 : profondeur sur Quest 3S

Statut : brouillon. Méthode et règle fixées avant les mesures · Date : 2026-10-13 · Auteur : claude-agent@mote-session
· Tâche : TASK-eea1

Contexte : SPEC-64c5 §9.5 stocke la profondeur brute (`F32_RAW`) et linéarise à l'ingest avec une formule déduite de la
documentation, `distance = nearZ / (1 - d)` pour un far infini `[HYPOTHESE]`. La résolution, la cadence et le coût de
la relecture GPU vers CPU ne sont pas documentés. H-02 : la profondeur du Quest 3S, sans projecteur contrairement au
Quest 3, est-elle exploitable pour initialiser un nuage de points ? SP-7 (initialisation de l'aperçu live par la
profondeur) et WP-10 en dépendent.

## 1. Verdict (à remplir en dernier)

Formule de linéarisation : ___ (confirmée / à corriger).
H-02 : ___ (validée / invalidée / validée avec réserve).
Tolérance de distance proposée : ___
Coût de la relecture : ___ ms par carte sur le thread principal, latence ___ frames.
Conséquences pour SPEC-64c5 §9.5 et WP-10 : ___

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

## 3. Méthode

Outils : `docs/spikes/sp3/` (README.md). QuestRealityCapture v1.5.0 (SRC-1, commit 649c012), instrumenté par un seul
fichier qui chronomètre la relecture (`qrc_patch/`). Identifiant de paquet à part, l'original n'est pas touché.

- **Ce que SRC-1 enregistre** (lu dans son code) : profondeur par le sous-système d'occlusion OpenXR de Unity ; texture
  copiée par un compute shader dans deux buffers float, puis `AsyncGPUReadback` ; un `.raw` float32 par œil et par
  carte, ligne 0 en haut ; valeurs brutes non linéaires dans ]0, 1[ ; descripteur par carte : pose de création (repère
  Unity), tangentes du champ, near_z, far_z, taille.
- **Résolution et cadence** : lues dans les descripteurs d'une session enregistrée à pleine cadence
  (`targetSaveFps` 0).
- **Linéarisation** : `ndc = 2d - 1`, projection OpenGL ; far infini : `z = near / (1 - d)` (même formule que SRC-3 et
  que le shader de couverture de SRC-1). z est la distance le long de l'axe de visée.
- **Mur** : mur plan texturé, distances de 0,5 à 3 m mesurées au mètre ruban entre le mur et la face avant du casque,
  6 s immobile à chacune. Plan ajusté sur les 40 % centraux de chaque carte, rejet itératif des points hors plan,
  distance perpendiculaire de l'origine de la carte au plan.
- **Relecture** : chronométrée sur le thread principal (Export, callback) et en latence (ms et frames).
- **Rétroprojection** : toutes les cartes gauches de S1 (SP-0, 5 Hz) portées dans le monde par leur pose de création.
  Le résultat est un nuage PLY et des vues de dessus et de face.

## 4. Résultats

### 4.1 Résolution, cadence, valeurs

___

### 4.2 Linéarisation contre le mur

___

### 4.3 Relecture GPU vers CPU

___

### 4.4 Rétroprojection

___

## 5. Lecture et limites

- Une seule scène et un seul mur ; la profondeur passive du 3S dépend de la texture : un mur blanc uni donnera moins
  de pixels valides (session B, facultative).
- Le mètre vise la face avant du casque : le décalage constant absorbe la distance entre celle-ci et l'origine de la
  carte. Une erreur d'échelle, elle, ne s'absorbe pas.
- Le coût mesuré est celui du chemin de SRC-1 (compute shader, buffer, readback asynchrone), pas encore celui de
  l'hôte mote.
