# SP-0 sur le PC NVIDIA : REF COLMAP et bench 3DGS, en une commande

Outils de spike jetables, **pas du code mote**. Ils refont, sur un PC Windows avec GPU NVIDIA, la partie COLMAP de SP-0
(PROTOCOL.md §5 et §6, annexe de GPU_RUN.md) pour toutes les sessions du casque d'un coup : export avec les poses du
casque, SfM COLMAP complet chronométré (SIFT sur GPU), alignement Sim(3) casque contre REF, résumé. Puis, si on le demande, le bench 3DGS : splatfacto entraîné sur les poses
du casque **et** sur les poses COLMAP, mêmes images, même hold-out, mêmes graines (PROTOCOL.md §7 et §8).

| Commande | Ce qu'elle fait | Durée indicative |
|---|---|---|
| `run_all.ps1` | export, REF COLMAP, erreur de suivi du casque | quelques dizaines de minutes par session |
| `train_all.ps1` | `run_all.ps1` (sauté si déjà fait), puis le bench 3DGS A contre AREF | 6 entraînements par session (2 sources x 3 graines), de 20 à 40 min chacun |

## La commande

1. Copier les sessions du casque dans `%USERPROFILE%\sp0\sessions\`, un dossier par session tel que `adb pull` le
   donne (`20261007_101500\` avec `hmd_poses.csv`, `left_camera_mruk_rgba\`...). Un export SRC-3 déjà fait (dossier
   avec `images\` et `distorted\sparse\0\`, par exemple `data\` du kit de GPU_RUN.md) est accepté aussi, sans réexport.
2. Depuis la racine du dépôt :

```powershell
powershell -ExecutionPolicy Bypass -File docs\spikes\sp0\gpu\run_all.ps1
```

Rien d'autre à faire. Au premier lancement, le script installe ce qui manque dans `%USERPROFILE%\sp0\tools\`, sans
droits administrateur : uv, Python 3.11 (venv dédié), COLMAP **4.2.1** CUDA (la version du REF S0/S1, zip de la release
GitHub, environ 415 Mo) et SRC-3 au commit `97d15f7` (celui de l'export S0/S1). Ensuite, pour chaque session :

| Étape | Commande | Note |
|---|---|---|
| export | `mq3drecon export-colmap --interval 2` | poses du casque (option A), **sans** `--use-optimized-color-dataset` (SP-0.md §4) |
| est_txt | `colmap model_converter` | modèle du casque en texte |
| by_eye | liens physiques `ref\images_by_eye\left|right` | une caméra par œil, sans copier les images |
| SfM REF | `feature_extractor`, `exhaustive_matcher`, `mapper` | chronométrés, SIFT sur GPU, mêmes options que S0/S1 |
| ref_txt | `colmap model_converter` | tous les modèles `ref\sparse\N` en texte |
| post_ref | `post_ref.py` | modèle qui recale le plus d'images, Sim(3), résumé |

À la fin, un tableau s'affiche (images, fraction recalée par REF, erreur de translation médiane en mètres pour les deux
yeux, gauche et droite, erreur de rotation médiane, temps du SfM).

**Durée** : S1 (1 178 images) a pris 138 min sur le Mac sans GPU, dont 89 min d'appariement. Sur GPU, c'est beaucoup
plus court, mais l'appariement `exhaustive` croît en N². Windows ne se met pas en veille pendant le calcul : le script
l'en empêche, pour que les temps restent continus (SC-03).

**Reprise** : chaque étape réussie laisse un marqueur dans `<session>\.steps\`. Si quelque chose casse (coupure,
Ctrl+C, erreur), relancer **la même commande** reprend à l'étape en échec ; les sessions déjà finies ne sont pas
recalculées. Un appariement interrompu est refait depuis l'extraction, pour que son temps reste complet. Pour tout refaire pour une session, supprimer son dossier dans `%USERPROFILE%\sp0\work\`.

## Options

| Option | Défaut | Rôle |
|---|---|---|
| `-Data <dossier>` | `%USERPROFILE%\sp0\sessions` | où sont les sessions (cherchées dans les sous-dossiers) |
| `-Work <dossier>` | `%USERPROFILE%\sp0\work` | sorties ; prévoir environ 1 Go de PNG par minute de capture à `-Interval 2` (S1 : 1 178 PNG, 2 Go) |
| `-Tools <dossier>` | `%USERPROFILE%\sp0\tools` | outils téléchargés |
| `-Only S1,S2` | toutes | ne traiter que ces sessions (noms de dossier) |
| `-Interval N` | 2 | une image sur N à l'export, comme S0 et S1 |
| `-Matcher sequential` | `exhaustive` | plus rapide sur de longues sessions, mais temps **non comparables** à S0/S1 : le dire dans SP-0.md |
| `-DryRun` | | affiche toutes les commandes sans rien exécuter ni télécharger |
| `-AllowCpu` | | accepter l'absence de GPU ou un COLMAP sans CUDA |

Un COLMAP CUDA déjà installé est utilisé s'il est dans le `PATH` ou désigné par la variable d'environnement `COLMAP`.
Sous Linux, lancer `pipeline.py` directement, avec un COLMAP CUDA dans le `PATH` :
`python pipeline.py --data ~/sp0/sessions --work ~/sp0/work --tools ~/sp0/tools`.

## Ce qui sort, par session (`work\<session>\`)

```
summary.json        modèle REF retenu, fraction recalée (>= 90 % sinon REF n'est pas une référence), erreurs Sim(3)
                    en mètres (tous, gauche, droite), dérive par œil (RMSE par tiers, rapport dernier/premier), temps du SfM
timings.json        temps de chaque étape, format de run_timed.py (total du SfM = extraction + appariement + mapper)
eval\align_all.json, align_left.json, align_right.json      sorties complètes d'align_sim3, avec translation_error_m
ref_flat\sparse\0\  modèle REF avec les noms de l'export : --colmap-path pour « A sur poses REF » (GPU_RUN.md §4)
export\             export SRC-3 (images\, distorted\sparse\0\) : --data de l'entraînement A (GPU_RUN.md §3)
est_txt\            poses du casque en texte
ref\                base COLMAP, images_by_eye\, sparse\N\
logs\               sortie complète de SRC-3 et de COLMAP
```
`work\summary_all.json` regroupe les résumés de toutes les sessions.

Erreurs en mètres : le casque est métrique, donc 1 unité REF vaut `1/scale` mètre (`m_per_ref_unit`). La dérive n'est
donnée que par œil : triés par nom, tous les LEFT passent avant tous les RIGHT, et des tiers sur les deux yeux mélangeraient
les deux (SP-0.md §6). Les aberrants du REF (S1 : 10 images sur des murs blancs) restent dans les statistiques : le
réajustement « sans aberrants » de SP-0.md §6 se fait à la main, à côté.

## Bench 3DGS : poses du casque contre poses COLMAP

```powershell
powershell -ExecutionPolicy Bypass -File docs\spikes\sp0\gpu\train_all.ps1
```

Mêmes dossiers par défaut que `run_all.ps1`, qu'il lance d'abord (rien n'est refait pour une session déjà finie). Il
installe ensuite un second venv, `tools\venv-train` (Python 3.10, environ 3 Go) : torch 2.1.2 CUDA 11.8, nerfstudio
1.1.5, LPIPS 0.1.4 et **gsplat 1.4.0 précompilé pour Windows**. Il n'y a donc ni CUDA Toolkit ni Visual Studio à installer.
Il vérifie que torch voit le GPU, puis, pour chaque session qui a un REF :

1. **Jeu commun** (`nsdata\`) : les images présentes à la fois dans le modèle du casque et dans le REF, par paires
   gauche/droite complètes (appariées par `mruk_stereo_pairs.csv` de la session brute, sinon par horodatage à moins de
   50 ms). Hold-out par blocs de paires (`make_holdout.py`, 5 toutes les 40). Les deux variantes voient **exactement**
   les mêmes images d'entraînement et de test (GPU_RUN.md §0).
2. **Entraînement** `ns-train splatfacto`, 30 000 itérations, raffinement de pose `SO3xR3`, initialisation aléatoire
   (`--load-3D-points False`), graines 0, 1 et 2, pour les deux variantes :
   - **A** : poses du casque (`nsdata\headset\sparse\0`), l'option A de SPEC 11.3 ;
   - **AREF** : poses du REF COLMAP (`nsdata\ref\sparse\0`), le contrôle « A sur poses REF ».
3. **Rendu** du hold-out en **PNG** (`ns-render` écrit du JPEG par défaut, ce qui fausserait le PSNR), puis
   `metrics.py` (PSNR, SSIM, LPIPS VGG) entre rendu et `gt-rgb`, et `ns-eval` pour recouper.
4. **Courbe PSNR(temps)** : le hold-out entier est évalué toutes les 2 000 itérations (`--steps-per-eval-all-images`).
   On en tire le temps et l'itération où le PSNR dépasse 20 dB (SC-01). Ces évaluations s'ajoutent au temps
   d'entraînement, à dire dans SP-0.md.

À la fin, un tableau par session et par variante affiche PSNR, SSIM et LPIPS (moyenne ± écart-type sur les graines),
le temps d'entraînement, le temps pour 20 dB et l'écart **A - AREF** avec sa lecture selon la règle de SP-0.md §2
(poursuite si l'écart est d'au moins -1 dB, arrêt sous -3 dB, intermédiaire entre les deux).

Sorties en plus, par session : `bench.json` (tout, dont les seuils proposés pour SC-01 et SC-02 selon PROTOCOL.md §9),
`eval\<A|AREF>_seed<k>\metrics.json` et `nseval.json`, `runs\` (splats et tensorboard), `nsdata\holdout.json`.
Plus `work\bench_all.json` pour toutes les sessions.

Options : `-Seeds 0,1,2`, `-Variants A,AREF`, `-Iterations 30000`, `-Only S1`, `-SkipColmap`, `-DryRun`. Un
entraînement interrompu est refait depuis le début, pour garder un temps complet.

Deux écarts entre A et AREF tiennent à la méthode et non au suivi du casque. Le REF a ses propres intrinsèques
(OPENCV, estimées par COLMAP), alors que A utilise les intrinsèques MRUK. Pour AREF, nerfstudio redresse les images
avant l'entraînement : PSNR et SSIM sont donc mesurés contre le `gt-rgb` de chaque variante.

## Ce qu'on rapporte dans le dépôt

Pour chaque session `<S>` : `summary.json`, `timings.json` et `eval\align_*.json`, à copier dans
`docs/spikes/sp0/results/<S>/`, plus la ligne GPU et la version de COLMAP (présentes dans `summary.json`, clé `env`) pour
SP-0.md §4 et §7. Pour le bench : `bench.json`, `nsdata\holdout.json` et `eval\*\metrics.json`, pour SP-0.md §5 et §8.
Jamais les images, la base COLMAP, les modèles ni les splats.

## Fichiers

| Fichier | Rôle |
|---|---|
| `run_all.ps1` | point d'entrée : uv, venv Python 3.11, numpy, puis `pipeline.py` |
| `pipeline.py` | installe COLMAP et SRC-3 s'ils manquent, trouve les sessions, enchaîne les étapes, reprend après un échec |
| `post_ref.py` | choix du modèle REF, Sim(3) avec `../align_sim3.py`, `ref_flat`, `summary.json` ; relançable seul : `python post_ref.py --session <work>\<S>` |
| `test_pipeline.py` | tests sans GPU ni COLMAP : `python test_pipeline.py` |
| `train_all.ps1` | point d'entrée du bench : `run_all.ps1`, venv d'entraînement, puis `train.py` |
| `train.py` | jeu commun A / AREF, entraînements, rendus, métriques, `bench.json` |
| `test_train.py` | tests sans GPU ni nerfstudio : `python test_train.py` |

## Vérifié, pas vérifié

Vérifié sur un portable Windows 11 sans GPU : `run_all.ps1` sous Windows PowerShell 5.1 (uv, venv, `-DryRun` complet),
installation de SRC-3 au commit `97d15f7` et options de `mq3drecon export-colmap`, `test_pipeline.py` sous Python 3.11 et
3.14 (choix du modèle, échelle et erreurs retrouvées sur un Sim(3) connu, `ref_flat`, temps, découverte des sessions,
liens physiques, et un passage complet avec un faux `colmap` dont l'appariement tombe en panne une fois : reprise,
extraction refaite, résumé).
Le zip COLMAP 4.2.1 CUDA contient `bin\colmap.exe` et `COLMAP.bat`, lus à distance.

Bench 3DGS, vérifié sur la même machine : l'environnement d'entraînement s'installe sous Windows sans compilation
(torch 2.1.2+cu118, gsplat 1.4.0+pt21cu118, nerfstudio 1.1.5, numpy 1.26). La commande `ns-train` exacte de
`train.py`, lancée sur un `nsdata` synthétique pour A et pour AREF, passe le parsing des options et le dataparser
COLMAP. nerfstudio y annonce « Using train_list.txt » et « Using val_list.txt », avec le bon nombre d'images. Elle va
jusqu'à la première itération, où gsplat demande CUDA. Les options de `ns-render dataset` et de `ns-eval`, ainsi que le
tag tensorboard de la courbe PSNR, sont vérifiés sur la version installée. `test_train.py` passe à 5/5 (appariement,
jeu commun, règle de décision, courbe PSNR, commandes). `train_all.ps1 -DryRun` tourne sous PowerShell 5.1.

**Pas vérifié faute de GPU** : un entraînement, un rendu et des métriques réels, le temps d'entraînement, la mémoire
GPU nécessaire. Ni, côté COLMAP, le démarrage de COLMAP CUDA sous Windows, un export et un SfM réels sur cette machine.
Au premier lancement sur la tour, regarder que la ligne `COLMAP :` affiche `with CUDA` et que le premier
`feature_extractor` ne se plaint pas de `use_gpu`. Si COLMAP ne démarre pas, essayer `tools\colmap\4.2.1\COLMAP.bat -h`
à la main.
