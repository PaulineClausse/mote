# SP-7 : kit initialisation par la profondeur

Outils de spike jetables, pas du code mote. Rapport : `docs/spikes/SP-7.md` (méthode et règle de décision).

Sur le PC NVIDIA, **sans casque**. Prérequis, déjà en place depuis SP-0 et SP-6 :
- la session S1 brute, avec la profondeur, dans `$HOME\sp0\sessions\20261007_120820` ;
- son jeu commun dans `$HOME\sp0\work\20261007_120820\nsdata` ;
- le venv d'entraînement `$HOME\sp0\tools\venv-train`.

## Une commande

```powershell
git pull
powershell -ExecutionPolicy Bypass -File docs\spikes\sp7\run_sp7.ps1
```

Le script fait quatre choses :

1. **Nuage d'initialisation**, en quelques minutes : `$HOME\sp0\sp7\init\` contient `init.ply` (à ouvrir dans
   CloudCompare ou MeshLab), `init_views.png` et `init.json` (nombre de points, alignement, filtres).
2. **Flux**, environ 30 min : 3 graines x {aléatoire, profondeur}, `uniform` en demi-résolution, le banc de SP-6. C'est
   la partie qui décide pour le live.
3. **Hors ligne**, **4 à 5 h** : 3 graines x {aléatoire, profondeur}, 30 000 itérations en pleine résolution.
4. **Résumé** : `compare.py` (tableaux et verdict selon la règle), puis `curves.py` (PSNR en fonction du temps de flux).

`-SkipOffline` ne fait que le flux, pour avoir la réponse sur le live tout de suite ; relancer sans l'option complète
le hors ligne, en sautant ce qui est déjà fait. Copier la sortie dans la conversation, avec `init_views.png`.

## Fichiers

| Fichier | Rôle |
|---|---|
| `run_sp7.ps1` | point d'entrée |
| `depth_init.py` | nuage d'initialisation de S1 : profondeur linéarisée, bords et hold-out exclus, alignement, couleur, grille |
| `compare.py` | profondeur contre aléatoire, verdict selon SP-7.md §2 |
| `test_depth_init.py` | scène synthétique : `uv run docs/spikes/sp7/test_depth_init.py` |
| `test_compare.py` | règle : `python docs/spikes/sp7/test_compare.py` |

L'entraîneur est `docs/spikes/sp6/incremental.py`, avec l'option `--init-npz` ; son test `test_loop.py` couvre ce cas.
