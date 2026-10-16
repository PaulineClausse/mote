# SP-2 : kit synchronisation image/pose, repères, paires stéréo

Outils de spike, pas du code mote. Rapport : `docs/spikes/SP-2.md`. Tâche : TASK-552b.

## 1. Imprimer le damier

`damier_A4.pdf` : A4 paysage, 10 x 7 cases de 25 mm (9 x 6 coins intérieurs).

1. Imprimer **en taille réelle (100 %)**. Surtout pas « Ajuster à la page » ni « Réduire » : le calcul repose sur la
   taille exacte des cases.
2. Vérifier à la règle que **la réglette du bas mesure 100 mm**. Mesurer aussi dix cases d'un bord à l'autre :
   250 mm. Noter les deux mesures, elles vont dans le rapport.
3. Coller la feuille **bien à plat** sur un support rigide (carton épais, plaque, vitre), sans bulle ni pli. Un damier
   gondolé fausse la mesure plus que tout le reste.
4. Le fixer au mur, ou le poser sur une table, dans une pièce bien éclairée, sans reflet sur le papier (le papier mat
   est préférable).

Autre format ou autre taille de case :
```sh
python docs/spikes/sp2/make_damier.py --page A3 --square 35 --out damier_A3.pdf
```
Une dimension doit rester paire et l'autre impaire, pour que l'orientation du damier soit sans ambiguïté.

Un écran convient aussi (SP-2 a été fait ainsi) : damier en plein écran, luminosité maximale, luminosité automatique
et veille coupées, **cases mesurées à la règle** (la taille affichée n'est jamais exactement celle du PDF), sans reflet.

## 2. Configurer QuestRealityCapture

Images à 10 i/s, poses du casque à pleine cadence, profondeur coupée :
```powershell
@'
{
  "sessionNameFormat": "yyyyMMdd_HHmmss",
  "camera": { "enabled": true, "backend": "MRUK", "targetSaveFps": 10,
              "left": {"enabled": true}, "right": {"enabled": true} },
  "pose":   { "enabled": true, "targetSaveFps": 0 },
  "depth":  { "enabled": false }
}
'@ | Set-Content -Encoding ascii $env:TEMP\sp2_config.json
$F = "/sdcard/Android/data/com.t34400.QuestRealityCapture/files"
adb shell mv $F/recording_config.json $F/recording_config.sp0.json
adb push $env:TEMP\sp2_config.json $F/recording_config.json
```

## 3. Prises

Damier à 40 à 70 cm, une session de l'application par prise :

| Prise | Durée | Mouvement |
|---|---|---|
| A, essai | 5 s | immobile face au damier |
| B, statique | 30 s | 5 positions (face, biais gauche et droite, plus près, plus loin), 3 s immobile à chacune |
| C, translations | 20 s | glisser lentement gauche-droite puis haut-bas, sans tourner la tête |
| D, rotations | 30 s | tourner la tête : 3 allers-retours lents (2 s), 3 moyens (1 s), 3 rapides (0,5 s) |
| E, bords | 30 s | amener le damier dans chaque coin de la vue puis au centre, 3 s à chaque endroit |

```powershell
adb shell ls -t /sdcard/Android/data/com.t34400.QuestRealityCapture/files/
adb pull /sdcard/Android/data/com.t34400.QuestRealityCapture/files/<session> $HOME\sp2\
```

## 4. Vérifier puis analyser

```powershell
uv run --no-project --with opencv-python-headless --with numpy python docs\spikes\sp2\check_session.py $HOME\sp2\<session A>
uv run --no-project --with opencv-python-headless --with numpy python docs\spikes\sp2\analyze.py --square-mm <mesure> `
  "B=$HOME\sp2\<B>" "C=$HOME\sp2\<C>" "D=$HOME\sp2\<D>" "E=$HOME\sp2\<E>" --out $HOME\sp2\analyse
```
La détection du damier est mise en cache dans chaque session (`sp2_cache/`) : le premier passage prend quelques
minutes (4 processus par défaut, `--workers` pour changer), les suivants quelques secondes.

Tests de l'analyse, sur des sessions synthétiques à vérité connue :
```sh
uv run --no-project --with opencv-python-headless --with numpy --with pytest python -m pytest -q docs/spikes/sp2
```
