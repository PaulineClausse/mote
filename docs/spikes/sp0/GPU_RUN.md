# SP-0 : entraînement et métriques sur un PC NVIDIA

Ce document couvre la partie de SP-0 qui demande un GPU CUDA : PROTOCOL.md §7 et §8, appliqués à un export déjà fait
sur une autre machine. Il est écrit pour Windows (PowerShell). Sous Linux, remplacer `\` par `/` et
`.venv\Scripts\Activate.ps1` par `source .venv/bin/activate`.

## 0. Ce qu'on apporte (clé USB ou disque, environ 2 Go)

```
sp0_s1\
  data\                  = colmap_export de S1
    images\              1178 PNG : LEFT_<ts>.png et RIGHT_<ts>.png
    distorted\sparse\0\  poses du casque (option A), points3D vide
    ref_flat\sparse\0\   poses REF (COLMAP complet), mêmes noms d'image : contrôle « A sur poses REF »
    train_list.txt  test_list.txt  val_list.txt  validation_list.txt  holdout.json
                         534 paires : celles que REF a recalées des deux côtés, pour que A et « A sur poses REF »
                         s'entraînent et s'évaluent sur exactement les mêmes images
  tools\                 metrics.py, run_timed.py (copiés depuis docs/spikes/sp0)
```
`val_list.txt` et `validation_list.txt` sont des copies de `test_list.txt` : selon sa version, le dataparser
COLMAP de nerfstudio cherche l'un ou l'autre pour la partie évaluation, et s'arrête s'il trouve une liste sans les autres.

## 1. Vérifier la machine (5 min)

```powershell
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
```
Il faut un GPU NVIDIA avec au moins 8 Go de VRAM. Noter la ligne affichée, elle va dans `SP-0.md` §4.

## 2. Installer (20 à 40 min, une fois)

Sans droits administrateur, `uv` s'installe dans le profil utilisateur :
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
cd sp0_s1
uv venv --python 3.10 .venv ; .venv\Scripts\Activate.ps1
uv pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cu118
uv pip install nerfstudio==1.1.5 lpips==0.1.4 numpy pillow
python -c "import torch;print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```
La dernière ligne doit afficher `True` suivi du nom du GPU. Si elle affiche `False`, le pilote NVIDIA est trop ancien pour
CUDA 11.8 : le noter et arrêter là.

gsplat compile ses extensions CUDA au premier entraînement. Il lui faut le CUDA Toolkit de la même version (11.8) et, sous
Windows, les « Build Tools for Visual Studio » (C++). Si le premier `ns-train` échoue en compilant gsplat, il manque l'un
des deux. Il existe aussi des roues gsplat précompilées par version de torch et de CUDA (voir la doc de gsplat).
`[A VERIFIER]` sur la machine.

Relevé des versions, à coller dans `SP-0.md` §4 :
```powershell
python --version ; pip show nerfstudio gsplat lpips torch | Select-String "^(Name|Version)" ; nvcc --version | Select -Last 2
```

## 3. Entraîner A, trois graines (environ 20 à 40 min par graine selon le GPU)

```powershell
$D = "data" ; $O = "runs" ; mkdir eval -Force | Out-Null
foreach ($s in 0,1,2) {
  python tools\run_timed.py --log eval\train_timings.json --label "A_seed$s" -- `
    ns-train splatfacto --data $D --output-dir $O --experiment-name A --timestamp "seed$s" `
      --max-num-iterations 30000 --pipeline.model.camera-optimizer.mode SO3xR3 --machine.seed $s `
      --viewer.quit-on-train-completion True `
      colmap --colmap-path distorted/sparse/0 --images-path images --load-3D-points False --downscale-factor 1
}
```
- `--load-3D-points False` : initialisation aléatoire, c'est la définition de l'option A.
- **Contrôle du hold-out**, dans les premières lignes du premier entraînement : nerfstudio doit annoncer **938** images
  d'entraînement et **130** d'évaluation. Si les nombres diffèrent (par exemple 1178 et 0, ou une répartition 90/10), les
  listes n'ont pas été lues : arrêter et le noter. Repli décrit dans PROTOCOL.md §7.
- Pendant l'entraînement, noter dans tensorboard (`runs\A\splatfacto\seed0\`) l'itération et le temps où le PSNR
  d'évaluation dépasse 20 dB. C'est la mesure de SC-01.

## 4. Contrôle : A sur les poses REF (une graine suffit si le temps manque, trois sinon)

Même commande, avec seulement `--experiment-name AREF` et `--colmap-path ref_flat/sparse/0`. Mêmes images, mêmes listes,
mêmes graines.

## 5. Métriques (PROTOCOL.md §8)

Pour chaque entraînement (A et AREF, graines 0 à 2) :
```powershell
$CFG = "runs\A\splatfacto\seed0\config.yml"
ns-eval --load-config $CFG --output-path eval\A_seed0_nseval.json
ns-render dataset --load-config $CFG --split test --output-path eval\A_seed0 --rendered-output-names rgb gt-rgb
python tools\metrics.py --pred eval\A_seed0\test\rgb --gt eval\A_seed0\test\gt-rgb --lpips-net vgg --out eval\A_seed0\metrics.json
```
- `ns-eval` donne PSNR, SSIM et LPIPS, LPIPS avec le réseau par défaut de nerfstudio. `metrics.py` donne LPIPS VGG,
  le même réseau pour toutes les mesures. Rapporter `metrics.py` comme mesure officielle et garder `ns-eval` pour
  recouper.
- Si `ns-render dataset` range les fichiers ailleurs que dans `test\rgb` et `test\gt-rgb`, adapter les deux chemins.
- Mesures sans raffinement des poses de test : le dire dans `SP-0.md` (PROTOCOL.md §8).

## 6. Ce qu'on rapporte (quelques Mo)

Tout le dossier `eval\` (JSON de métriques et de temps) et les `runs\*\splatfacto\*\config.yml`. Un ou deux rendus PNG
peuvent servir d'illustration. Les splats (`.ckpt`) ne vont pas dans le dépôt.
