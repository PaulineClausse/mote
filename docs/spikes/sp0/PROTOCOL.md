# SP-0 : protocole de capture, d'export et de mesure

Valide H-01 (SPEC.md 14.1) : les poses du casque suffisent-elles à entraîner un 3DGS correct ?
Outils de spike jetables : rien ici n'est du code mote. SRC-1 est utilisé **non modifié** (APK de
la release officielle, pas de rebuild). Étiquettes : `[SOURCE]` lu dans un README ou une doc,
`[A VERIFIER]` à confirmer au premier passage et à noter dans `SP-0.md`.

Dossier de travail conseillé (hors dépôt, volumineux) : `D:\sp0\<scene>\`, avec les sous-dossiers
`raw/` (copie ADB), `colmap_export/` (export SRC-3), `ref/` (SfM REF), `runs/` (splats), `eval/`.
Variable utilisée plus bas : `$W = D:\sp0\<scene>` (PowerShell). Les scripts sont dans ce dossier
(`docs/spikes/sp0/`), à lancer depuis lui.

## 0. Pré-requis (une fois)

Voir `VERSIONS.md` (outils, versions à figer, ce qui manque sur la machine de préparation). Avant de partir :
1. Casque : firmware v74 ou plus `[SOURCE]`, mode développeur actif, `adb devices` affiche `device`.
2. APK : release **v1.5.0** de QuestRealityCapture (SRC-1) téléchargée telle quelle. Noter son SHA-256
   (`Get-FileHash QuestRealityCapture.apk`) dans `SP-0.md`. `adb install QuestRealityCapture.apk` `[SOURCE]`.
3. PC : venv Python avec SRC-3, COLMAP, nerfstudio et LPIPS (VERSIONS.md). Lancer
   `python test_align_sim3.py` (doit afficher `6/6 tests passent`) et `python metrics.py --selftest`.
4. Casque chargé à plus de 60 %, au moins 10 Go libres. Un `.rgba` 1280x1280 pèse 6 553 600 octets `[SOURCE]` :
   à 5 fps et deux caméras, une minute ≈ 600 fichiers ≈ 3,9 Go ; à 10 fps ≈ 7,9 Go par minute.

## 1. Configuration de l'enregistrement (SRC-1 non modifié)

SRC-1 lit un `recording_config.json` optionnel (override à l'exécution, ce n'est pas une modification du code) :
`/sdcard/Android/data/com.t34400.QuestRealityCapture/files/recording_config.json` `[SOURCE]`.
Pour SP-0, configuration MRUK minimale avec une cadence caméra réduite pour limiter le volume et le coût du SfM :

```json
{
  "camera": { "enabled": true, "backend": "MRUK", "targetSaveFps": 5,
              "left": {"enabled": true}, "right": {"enabled": true} },
  "pose":   { "enabled": true, "targetSaveFps": 30 },
  "depth":  { "enabled": true, "targetSaveFps": 5 }
}
```

```powershell
adb push recording_config.json /sdcard/Android/data/com.t34400.QuestRealityCapture/files/recording_config.json
```

- `targetSaveFps` caméra : 5 (le défaut est 10 `[SOURCE]`). À 5 fps, une minute donne environ 300 paires. Si la
  scène est parcourue vite, remonter à 10 et sous-échantillonner à l'export (`--interval`).
- La profondeur reste active : elle servira à SP-3 et à l'option B, et ne coûte rien à garder maintenant.
- Noter la version exacte du firmware (Paramètres, Système, À propos).
- Si le fichier n'est pas pris en compte (la cadence relevée dans `*_frame_metadata.csv` ne correspond pas),
  noter l'écart dans `SP-0.md` et continuer avec les valeurs obtenues : c'est l'application qu'on teste. `[A VERIFIER]`

## 2. Scène et trajectoire

Deux scènes de nature différente (SPEC 13.1 point 6) ; pour SP-0, au moins la scène 1, la scène 2 si possible.
- **Scène 1 : petite pièce encombrée** (bureau, étagères, objets variés, environ 3 x 4 m).
- **Scène 2 : grand espace plus vide** (salon ou couloir, plus de 25 m²).

Règles de capture (conseils SRC-2 repris de SPEC section 12) `[SOURCE]` `[HYPOTHESE]` :
- Éclairage constant et suffisant ; éviter les contre-jours forts.
- Mouvements lents et réguliers ; pas de rotation rapide sur place (flou, parallaxe insuffisante, erreur de
  synchronisation amplifiée).
- Chaque surface sous plusieurs angles, y compris rasants et frontaux ; recouvrement important entre vues
  successives.
- Durée : **1 à 3 minutes** par scène (viser 2 minutes).
- Pas d'objets mobiles, pas de surfaces très réfléchissantes ou transparentes dans le champ ; noter celles
  qu'on ne peut pas éviter.
- **Ne pas recentrer le casque** pendant le scan : cela déplace l'origine du suivi (SPEC 9.4).

Trajectoire type :
1. Départ au centre de la pièce, 10 s de regard sur une zone très texturée (initialisation du suivi).
2. Boucle lente le long des murs, regard vers le mur puis en diagonale, à hauteur des yeux, environ 60 s.
3. Seconde boucle à environ 1 m du centre, regard vers l'extérieur, autre hauteur (accroupi puis debout), environ 40 s.
4. Retour au point de départ (fermeture de boucle, sert à lire la dérive) et 5 s de regard sur la même zone qu'au début.
5. Optionnel, capture séparée de 60 s : mêmes zones mais mouvements plus rapides, pour borner la tolérance de H-01.

Fiche de capture, une par session, recopiée dans `SP-0.md` : date, lieu, scène, lumière, durée réelle, firmware,
hash de l'APK, incidents (perte de suivi, recentrage accidentel, crash à la fermeture).

## 3. Enregistrement

1. Lancer l'application. Accepter les permissions caméra et scène au premier lancement `[SOURCE]`.
2. Appuyer sur le **bouton menu du contrôleur gauche** pour fermer le panneau d'instructions : l'enregistrement
   démarre `[SOURCE]`. Noter l'heure.
3. Exécuter la trajectoire du §2. Surveiller le retour visuel (couverture de profondeur, trajectoire, marqueurs de
   discontinuité du suivi) `[SOURCE]`. Noter tout marqueur de discontinuité avec l'instant approximatif dans la
   trajectoire : il explique un pic d'erreur à l'alignement du §6.
4. Quitter l'application. Le crash natif possible à la fermeture après usage de la caméra MRUK est connu
   `[SOURCE]` ; les fichiers sont déjà écrits. Noter s'il survient.

## 4. Copie vers le PC

```powershell
$W = "D:\sp0\scene1"; New-Item -ItemType Directory -Force $W\raw | Out-Null
adb shell ls /sdcard/Android/data/com.t34400.QuestRealityCapture/files/        # repérer YYYYMMDD_hhmmss
Measure-Command { adb pull /sdcard/Android/data/com.t34400.QuestRealityCapture/files/YYYYMMDD_hhmmss $W\raw }
```
`adb pull` direct, sans ZIP (l'export ZIP de SRC-2 est lent `[SOURCE]`). Noter la durée de la copie et la taille
(SPEC 1.4 : l'export lent est une des motivations de mote).

Contrôles de santé sur `$W\raw\YYYYMMDD_hhmmss` (structure MRUK `[SOURCE]`) :
- présents : `session_info.json` (`captureBackend: MRUK`), `hmd_poses.csv`, `left_camera_mruk_rgba/` et
  `right_camera_mruk_rgba/`, `left/right_camera_mruk_intrinsics.json`, `left/right_camera_mruk_frame_metadata.csv`,
  `mruk_stereo_pairs.csv`, `left/right_depth/` et `*_depth_descriptors.csv`.
- chaque `.rgba` pèse 6 553 600 octets :
  `(Get-ChildItem $W\raw\*\left_camera_mruk_rgba | Where Length -ne 6553600 | Measure).Count` doit valoir 0.
- nombre de lignes de `mruk_stereo_pairs.csv` et durée (dernier moins premier `unix_time` de `hmd_poses.csv`)
  cohérents avec la durée chronométrée et `targetSaveFps`. **Noter les cadences réelles**, qui peuvent être
  inférieures aux cibles.

## 5. Export SRC-3 vers COLMAP (poses du casque) : dataset A

SRC-3 : outil `mq3drecon`, Python 3.10 ou plus `[SOURCE]`.

```powershell
cd <metaquest-3d-reconstruction>; .\.venv\Scripts\Activate.ps1
$S = (Get-ChildItem $W\raw | Select -First 1).FullName        # dossier de session
mq3drecon rgba-to-png --project-dir $S                          # aperçus PNG (left/right_camera_mruk_rgba_png)
mq3drecon export-colmap --project-dir $S --output-dir $W\colmap_export --use-optimized-color-dataset --interval 1
```
Noms de commandes et d'options : docs/CLI.md de SRC-3 `[SOURCE]`. Rappels de docs/DATA_FORMAT.md `[SOURCE]` : les
`.rgba` sont stockés de bas en haut et retournés par les chargeurs ; les poses MRUK sont des caméra-vers-monde en
repère Unity ; l'exporteur convertit les `.rgba` en PNG dans le dossier d'export et laisse les sources intactes.

La documentation lue ne décrit pas le contenu exact de l'export. À vérifier au premier passage et à consigner :
1. Arborescence réelle de `$W\colmap_export` : dossier d'images (`images/`), modèle texte (`sparse/0/cameras.txt`,
   `images.txt`, `points3D.txt`) ou autre. `[A VERIFIER]` Adapter les chemins `--colmap-path` du §7.
2. Les deux caméras sont-elles exportées, avec quels noms d'image et quel modèle de caméra (une caméra COLMAP par
   œil ?). `[A VERIFIER]` `align_sim3.py` apparie par **nom d'image** ; REF est calculé sur ce même dossier d'images
   (§6), donc les noms coïncident.
3. `points3D.txt` : vide ou non. **L'option A est une initialisation aléatoire** (SPEC 11.3) : ne pas passer
   `--use-colored-pointcloud`, et si `points3D.txt` n'est pas vide, le vider (garder l'en-tête) pour que splatfacto ne
   s'en serve pas. `[A VERIFIER]`
4. Chiralité : les poses exportées doivent être en repère COLMAP (main droite, y vers le bas, z devant). Test : le
   Sim(3) du §6 doit donner des résidus de l'ordre du centimètre ; un miroir non traité donne des mètres (voir
   `test_reflection_is_not_silently_accepted`). `[A VERIFIER]`
5. `--interval N` sous-échantillonne : garder la **même** liste d'images pour A et pour REF.

Hold-out par blocs (SPEC 13.1) : 5 paires consécutives toutes les 40 (12,5 %), gauche et droite ensemble.

```powershell
python make_holdout.py --images $W\colmap_export\images --out-dir $W\colmap_export
```
Écrit `train_list.txt`, `test_list.txt` et `holdout.json`. Les paires du hold-out sont exclues de l'entraînement.
Elles restent dans REF : REF sert à mesurer le suivi, pas à entraîner.

## 6. REF : SfM COLMAP complet chronométré, puis alignement Sim(3)

REF = `mapper` COLMAP sans poses imposées, sur les mêmes images que l'export (SPEC 13.3). Chaque étape est chronométrée
par `run_timed.py` ; le temps du SfM (SC-03) est la **somme des étapes** (extraction, appariement, mapper), à reporter
en secondes et en minutes.

```powershell
$I = "$W\colmap_export\images"; $R = "$W\ref"; New-Item -ItemType Directory -Force $R\sparse, $W\eval | Out-Null
$T = "$R\timings.json"

python run_timed.py --log $T --label colmap_feature_extractor -- colmap feature_extractor `
  --database_path $R\database.db --image_path $I `
  --ImageReader.camera_model OPENCV --ImageReader.single_camera_per_folder 1 `
  --FeatureExtraction.use_gpu 1

python run_timed.py --log $T --label colmap_matcher -- colmap exhaustive_matcher `
  --database_path $R\database.db --FeatureMatching.use_gpu 1

python run_timed.py --log $T --label colmap_mapper -- colmap mapper `
  --database_path $R\database.db --image_path $I --output_path $R\sparse

colmap model_converter --input_path $R\sparse\0 --output_path $R\sparse\0 --output_type TXT
```

Notes :
- Les options GPU s'appellent `--FeatureExtraction.use_gpu` et `--FeatureMatching.use_gpu` en COLMAP 3.11 et plus,
  `--SiftExtraction.use_gpu` et `--SiftMatching.use_gpu` avant : lancer `colmap feature_extractor --help` et utiliser
  les noms de la version figée. `[A VERIFIER]`
- `single_camera_per_folder` suppose `images/left/...` et `images/right/...`. Si l'export met tout dans un seul
  dossier, séparer les deux yeux ou laisser une caméra par image (plus lent). `[A VERIFIER]`
- `exhaustive_matcher` est la référence « SfM complet » la plus honnête mais son coût croît en N². Au-delà d'environ
  1500 images, passer à `sequential_matcher --SequentialMatching.loop_detection 1` (arbre de vocabulaire à
  télécharger) et **le noter** : ne jamais comparer des temps entre matchers différents sans le dire (SC-03).
- Si `mapper` produit plusieurs modèles (`sparse/0`, `sparse/1`...), prendre celui qui recale le plus d'images et noter
  la fraction recalée. Un REF qui recale moins de 90 % des images n'est pas une référence : le dire dans `SP-0.md`
  plutôt qu'aligner un modèle partiel.
- Temps total du SfM : `python -c "import json,sys;print(sum(x['wall_s'] for x in json.load(open(sys.argv[1]))))" $T`.

Alignement Sim(3) (poses du casque contre REF, images communes) :

```powershell
python align_sim3.py --est $W\colmap_export\sparse\0\images.txt --ref $R\sparse\0\images.txt --out $W\eval\align.json
```
Lecture de `align.json` :
- `scale` : facteur casque vers unités REF. Le casque est métrique et REF est à échelle libre, donc 1 unité REF
  vaut `1/scale` mètre ; relancer avec `--ref-scale-m <1/scale>` pour obtenir `translation_error_m` en mètres.
- `translation_error` (rmse, mean, median, max) : erreur de position des centres de caméra après alignement ;
  `rotation_error_deg` : angle de la rotation résiduelle.
- `drift.translation_rmse_by_third` et `drift.error_slope_per_path_unit` : dérive le long de la trajectoire.
- Si le §3 a relevé une discontinuité de suivi, refaire l'alignement sur la partie sans discontinuité en plus de la
  trajectoire entière, et rapporter les deux.

## 7. Entraînement splatfacto, option A (poses du casque, initialisation aléatoire)

Le raffinement de pose est commun à toutes les options : camera optimizer `SO3xR3` (SPEC 11.3). Mêmes
hyperparamètres et même nombre d'itérations pour A et pour tout ce qui suit (SPEC 13.1 point 2). SP-0 fige
`--max-num-iterations 30000`.

```powershell
$D = "$W\colmap_export"; $O = "$W\runs"
python run_timed.py --log $W\eval\train_timings.json --label splatfacto_A_seed0 -- `
  ns-train splatfacto --data $D --output-dir $O --experiment-name A --timestamp seed0 `
  --max-num-iterations 30000 --pipeline.model.camera-optimizer.mode SO3xR3 --machine.seed 0 `
  colmap --colmap-path sparse/0 --images-path images --eval-mode all
```
- **Hold-out** : le dataparser COLMAP de nerfstudio lit des listes `train_list.txt` et `test_list.txt`
  `[SOURCE : colmap_dataparser.py de nerfstudio]` ; `make_holdout.py` les écrit à la racine de `--data`. Les modes
  `--eval-mode` documentés sont `fraction`, `filename`, `interval` et `all`, et le choix qui active les listes dépend
  de la version : vérifier avec `ns-train splatfacto colmap --help`, puis dans le journal de démarrage que le
  nombre d'images train et eval vaut 87,5 % et 12,5 % (350 et 50 pour 200 paires). Si les listes ne sont pas prises
  en compte, repli : deux dossiers `train/` et `test/` avec leurs `images.txt` filtrés. `[A VERIFIER]`
- Graines : au moins **3** (`--machine.seed 0`, `1`, `2`, une exécution par graine, `--timestamp seed0|seed1|seed2`).
  Les écarts entre options ne s'interprètent que s'ils dépassent la dispersion entre graines (SPEC 13.1 point 7).
- Pas de `--load-3D-points` et pas de points3D utiles : initialisation aléatoire (§5, point 3).
- Temps d'entraînement : relevé par `run_timed.py` (`train_timings.json`). Temps jusqu'au premier aperçu conforme à
  SC-01 : suivre le PSNR d'évaluation pendant l'entraînement (viewer `ns-viewer --load-config <config.yml>` ou courbes
  tensorboard) et noter l'itération et l'instant où il dépasse 20 dB.
- Variante utile pour isoler l'effet du suivi : « A sur poses REF », même commande avec `--colmap-path ../ref/sparse/0`
  (mêmes images, mêmes listes, mêmes graines). `[A VERIFIER]` selon que le dataparser accepte un chemin hors de `--data`.

## 8. Rendu du hold-out et métriques (PSNR, SSIM, LPIPS)

```powershell
$CFG = "$O\A\splatfacto\seed0\config.yml"           # chemin exact imprimé à la fin de l'entraînement
ns-render dataset --load-config $CFG --split test --output-path $W\eval\A_seed0 --rendered-output-names rgb
python metrics.py --pred $W\eval\A_seed0\test\rgb --gt $W\eval\holdout_gt --out $W\eval\A_seed0\metrics.json
```
- `holdout_gt` : les images du hold-out (copiées d'après `holdout.json`), à la **résolution** des rendus. Si nerfstudio a
  réduit la résolution (`downscale_factor`), redimensionner les GT de la même façon ou rendre à pleine résolution :
  `metrics.py` refuse des tailles différentes. Les noms des rendus doivent coïncider avec ceux des GT ; sinon renommer
  dans l'ordre de `test_list.txt`. `[A VERIFIER]` selon la version de `ns-render`.
- LPIPS : réseau VGG par défaut (`--lpips-net vgg`) ; **le même réseau pour toutes les mesures**, noté dans `SP-0.md`.
- **Poses de test** (SPEC 13.1 point 5) : le raffinement des poses du hold-out, Gaussiennes gelées, n'est pas fourni par
  un outil nerfstudio prêt à l'emploi à ma connaissance. `[A VERIFIER]` Pour SP-0, mesurer **sans** ce raffinement et le
  dire : la SPEC demande de rapporter ces métriques « à côté ». Si l'écart avec le rendu raffiné est grand, c'est un
  résultat de SP-0 et la matière d'un outil à écrire en WP-13, pas d'un contournement ici.
- Rapporter la moyenne par graine, puis la moyenne et l'écart-type sur les trois graines.

## 9. Seuils SC-01 et SC-02 (calibration)

Les seuils sont des `[HYPOTHESE]` (SPEC 2.3). Méthode proposée, à appliquer aux mesures de A :
- **SC-01** (aperçu d'au moins 20 dB sur les vues couvertes, dans le délai de NFR-04) : relever la courbe PSNR du hold-out
  en fonction du temps d'entraînement pour A. Proposer comme seuil `min(20 dB, PSNR_A_final - 3 dB)` arrondi, et comme délai
  l'instant où A atteint ce niveau. Si A final est sous 23 dB, 20 dB est déjà hors d'atteinte pour un aperçu : le dire.
- **SC-02** (gain d'au moins 1 dB de la meilleure option sur A) : prendre l'écart-type σ de A entre graines sur le PSNR ;
  un gain n'est interprétable que s'il dépasse environ 2σ. Proposer `max(1 dB, 2σ)` arrondi.
- Dans les deux cas, écrire les valeurs proposées **et** les données qui les fondent dans `SP-0.md` ; pas de seuil sans mesure.

## 10. Décision sur H-01

`SP-0.md` finit par une décision explicite **poursuite** ou **arrêt**, avec la règle appliquée. Fixer la règle **avant**
de regarder les chiffres (la trame en réserve la place). Éléments à peser : erreur de translation et de rotation médianes
après Sim(3), dérive, qualité du splat A relativement au splat « A sur poses REF » (même hold-out). Un splat A nettement
sous le splat REF, avec une grande erreur de suivi, invalide H-01.

## 11. Rangement

Ne commiter dans le dépôt que les **résultats** (`SP-0.md`, JSON de mesures légers). Jamais les `.rgba`, les images ni
les splats.
