# SP-3 : kit profondeur Quest 3S

Outils de spike jetables, pas du code mote. Rapport : `docs/spikes/SP-3.md` (méthode et règle de décision).

Tout se fait depuis le PC NVIDIA : Unity, `adb`, `uv` et la session S1 (`$HOME\sp0\sessions\20261007_120820`) y sont.

## 1. Construire et installer l'APK instrumenté (une fois)

```powershell
git pull
powershell -ExecutionPolicy Bypass -File docs\spikes\sp3\build_qrc.ps1
```

Le script fait cinq choses :

1. Il clone QuestRealityCapture v1.5.0 dans `$HOME\sp3\qrc` et vérifie le commit (649c012).
2. Il remplace un seul fichier, `DepthRenderTextureExporter.cs`, par sa copie instrumentée (`qrc_patch/`). Celle-ci
   écrit `depth_readback_timing.csv` dans chaque session.
3. Il construit l'APK Android en batchmode avec **Unity 6000.4.5f1**. Il faut le module Android Build Support,
   installé depuis Unity Hub. Pour une autre installation : `-Unity <chemin de Unity.exe>`. Le premier build prend 10
   à 20 minutes ; journal dans `$HOME\sp3\build.log`.
4. Il installe l'APK sous un identifiant à part, `com.t34400.QuestRealityCapture.sp3` : l'original et ses sessions
   restent en place.
5. Il pousse `recording_config_sp3.json`. C'est la config de SP-0, avec la profondeur à pleine cadence
   (`targetSaveFps` 0).

L'application apparaît dans la bibliothèque du casque, sous « Sources inconnues », avec le nom « QuestRealityCapture
SP3 ».

## 2. Capture devant un mur (environ 5 minutes, deux personnes)

Préparer :
- un mur plan **texturé** : affiches, ruban adhésif en croix, étagère. La profondeur du 3S est passive (stéréo, sans
  projecteur), donc un mur blanc uni donne des trous ;
- un mètre ruban, et une deuxième personne pour mesurer ;
- de la place pour reculer jusqu'à 3 m.

Session A, obligatoire :
1. Lancer « QuestRealityCapture SP3 ». Se placer face au mur, à environ 0,5 m, et regarder le centre de la zone
   texturée, tête droite.
2. Démarrer l'enregistrement comme pour SP-0, puis baisser les mains et **ne plus bouger pendant 6 s**.
3. Pendant ce temps, l'autre personne mesure au mètre la distance du mur à la **face avant du casque**, au centre, et
   la note.
4. Reculer à environ 1 m, s'immobiliser 6 s, mesurer. Faire de même vers 2 m, puis vers 3 m. Rester face au mur, sans
   tourner la tête. Ajouter 1,5 m et 2,5 m si possible (trois distances minimum).
5. Arrêter **par le bouton du menu** (consigne de SP-0), puis quitter.

Session B, facultative : la même chose devant un mur blanc uni, pour voir ce que devient la profondeur sans texture.

## 3. Analyse

```powershell
powershell -ExecutionPolicy Bypass -File docs\spikes\sp3\run_sp3.ps1                                # référence : tracking
powershell -ExecutionPolicy Bypass -File docs\spikes\sp3\run_sp3.ps1 -Distances 0.52,1.01,2.0,3.03  # référence : mètre
```

Sans `-Distances`, la référence est le recul du casque entre deux paliers, mesuré par son tracking et projeté sur la
normale du mur. La distance au plan doit croître d'autant (pente 1). C'est le mode à utiliser si les distances n'ont pas
été relevées précisément.

Avec `-Distances`, donner les valeurs notées, dans l'ordre, avec un point décimal. Le script fait trois choses :

1. Il récupère par `adb pull` la dernière session de l'APK SP3 dans `$HOME\sp3\sessions`.
2. Il lance `analyze.py`.
3. Il écrit les tableaux à coller dans SP-3.md, ainsi que des figures et un nuage `scene_depth.ply` (S1 rétroprojetée,
   à ouvrir dans CloudCompare ou MeshLab), dans `$HOME\sp3\out\<session>`.

Copier la sortie dans la conversation, avec les PNG si possible.

Le script compte les paliers immobiles. S'il n'en trouve pas autant que de distances (pause au démarrage, recul
hésitant), il affiche les paliers trouvés. Relancer alors avec `-Segments "3-9,14-20,..."` (secondes depuis le début de
la session) pour retenir les bons.

Pour une autre session (la B par exemple) : `-Session YYYYMMDD_hhmmss`.

## Fichiers

| Fichier | Rôle |
|---|---|
| `build_qrc.ps1` | clone, patch, build, installation, configuration |
| `qrc_patch/DepthRenderTextureExporter.cs` | l'exporteur de profondeur de SRC-1, chronométré |
| `qrc_patch/Sp3Build.cs` | build Android en ligne de commande, identifiant de paquet à part |
| `recording_config_sp3.json` | config de SP-0, profondeur à pleine cadence |
| `run_sp3.ps1` | récupération de la session et analyse |
| `analyze.py` | tableaux, figures, nuage rétroprojeté |
| `depthlib.py` | lecture des cartes, linéarisation, rétroprojection, plan, paliers (numpy seul) |
| `test_depthlib.py` | tests sur cartes synthétiques : `python test_depthlib.py` |
| `test_analyze.py` | test de bout en bout de l'analyse : `uv run docs/spikes/sp3/test_analyze.py` |
