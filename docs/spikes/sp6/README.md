# SP-6 : kit du PC NVIDIA

Outils de spike jetables, pas du code mote. Ils rejouent la session S1 de SP-0 comme un flux et entraînent un 3DGS
incrémental avec gsplat, sur les poses du casque. Rapport : `docs/spikes/SP-6.md`.

## Prérequis

Le bench de SP-0 doit avoir tourné sur la même machine (`docs/spikes/sp0/gpu/train_all.ps1`). Il a créé :

- le venv d'entraînement `$HOME\sp0\tools\venv-train` (torch 2.1.2 CUDA 11.8, gsplat 1.4.0, torchmetrics) ;
- le jeu commun de S1, `$HOME\sp0\work\20261007_120820\nsdata` : images, poses du casque, `train_list.txt` et
  `test_list.txt` (le même hold-out que le bench de SP-0).

## Une commande

```powershell
git pull
powershell -ExecutionPolicy Bypass -File docs\spikes\sp6\run_sp6.ps1
```

Environ 1 h 15 sur une RTX 3070. Relancer la même commande saute les runs déjà faits. Pour chaque graine (0, 1, 2) :

1. **hors ligne** : toutes les vues dès t = 0, 7 000 itérations, PSNR du hold-out toutes les 200 itérations. Donne la
   latence d'aperçu pure, sans l'arrivée des images.
2. **flux** `uniform`, `recent`, `window` : S1 rejouée à sa cadence réelle (122 s), puis 60 s d'entraînement. Le
   PSNR des vues de validation déjà couvertes est mesuré toutes les 5 s de flux.
3. **flux `recent` en demi-résolution** : la mitigation prévue pour RISK-09.

Option `-WithNoReset` : ajoute `recent` sans la remise périodique des opacités de gsplat, si la courbe montre des
chutes toutes les 3 000 itérations.

À la fin, `summarize.py` affiche un tableau par configuration et écrit `$HOME\sp0\sp6\runs\summary.json`. Copier ce
tableau dans la conversation : il remplit SP-6.md.

## Ce que fait l'entraîneur (`incremental.py`)

- **Horloge** : le temps d'entraînement écoulé, évaluations exclues. Une vue d'entraînement est disponible quand son
  horodatage de capture est passé.
- **Semis** : chaque vue qui arrive ajoute 500 gaussiennes le long de rayons tirés dans son image, à une profondeur
  aléatoire entre 0,3 et 4 m, de la couleur du pixel. Les poses du casque sont métriques. SP-7 remplacera la
  profondeur aléatoire par la profondeur mesurée par le casque.
- **Stratégies** : `uniform` tire parmi toutes les vues arrivées ; `recent` tire une fois sur deux dans les 5
  dernières secondes ; `window` ne tire que dans les 5 dernières secondes.
- **Entraînement** : perte 0,8 L1 + 0,2 (1 - SSIM), densification et élagage de `gsplat.DefaultStrategy` sans date
  d'arrêt, degré SH augmenté toutes les 1 000 itérations jusqu'à 3, raffinement de pose par vue (équivalent de
  SO3xR3, `--no-pose-opt` pour le couper).
- **Vue couverte** : une vue de validation compte quand elle a été capturée depuis au moins 2 s. Le seuil de 20 dB
  n'est retenu qu'à partir de 4 vues couvertes.

## Fichiers

| Fichier | Rôle |
|---|---|
| `run_sp6.ps1` | point d'entrée : tous les runs, puis le résumé |
| `incremental.py` | entraîneur gsplat incrémental, un run par appel, un JSON par run |
| `stream.py` | chargement de la session, arrivée des vues, couverture, stratégies ; sans torch |
| `summarize.py` | tableau par configuration, verdict sur RISK-09 |
| `test_stream.py` | tests de `stream.py`, sans torch : `python test_stream.py` |
| `test_loop.py` | test de la boucle sur CPU, rendu gsplat simulé ; demande torch et gsplat |
