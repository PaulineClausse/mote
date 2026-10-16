# SP-2 : kit synchronisation image/pose, repères, paires stéréo

Outils de spike, pas du code mote. Rapport à venir : `docs/spikes/SP-2.md`. Tâche : TASK-552b.

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

## 2. Capture et analyse

À venir dans ce dossier : protocole de capture, script d'installation de l'application de capture, scripts
d'analyse.
