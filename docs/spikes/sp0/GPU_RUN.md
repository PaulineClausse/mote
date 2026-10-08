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

## Annexe : refaire le SfM REF sur ce PC (optionnel)

Le REF de S1 a été calculé sur un Mac sans GPU, en 138 min. Le refaire ici, avec le GPU, donne le temps de SC-03 sur une
machine CUDA. Ce sont les mêmes commandes que sur le Mac. Il faut COLMAP **avec CUDA** (binaire Windows « cuda » de la
release GitHub colmap/colmap), et le kit doit contenir `tools\align_sim3.py` et `data\est_txt\`.

```powershell
colmap -h | Select -First 1                     # doit afficher "with CUDA"
# 1. Une caméra par œil : séparer les images en deux dossiers (copie, environ 2 Go)
mkdir images_by_eye\left, images_by_eye\right -Force | Out-Null
Copy-Item data\images\LEFT_*.png  images_by_eye\left\
Copy-Item data\images\RIGHT_*.png images_by_eye\right\
# 2. SfM complet chronométré (PROTOCOL.md §6)
mkdir ref\sparse -Force | Out-Null ; $T = "ref\timings.json"
python tools\run_timed.py --log $T --label colmap_feature_extractor -- colmap feature_extractor `
  --database_path ref\database.db --image_path images_by_eye `
  --ImageReader.camera_model OPENCV --ImageReader.single_camera_per_folder 1 --FeatureExtraction.use_gpu 1
python tools\run_timed.py --log $T --label colmap_matcher -- colmap exhaustive_matcher `
  --database_path ref\database.db --FeatureMatching.use_gpu 1
python tools\run_timed.py --log $T --label colmap_mapper -- colmap mapper `
  --database_path ref\database.db --image_path images_by_eye --output_path ref\sparse
# 3. Modèle en texte : prendre le dossier ref\sparse\N qui a le plus d'images
colmap model_converter --input_path ref\sparse\0 --output_path ref\sparse\0 --output_type TXT
Select-String "^# Number of images" ref\sparse\*\images.txt
# 4. Comparaison avec le casque : lancer une fois pour lire "scale", puis en mètres avec 1/scale
python tools\align_sim3.py --est data\est_txt\images.txt --ref ref\sparse\0\images.txt
python tools\align_sim3.py --est data\est_txt\images.txt --ref ref\sparse\0\images.txt --ref-scale-m <1/scale> --out eval\align_m.json
```
- Avant COLMAP 3.11, les options s'appellent `--SiftExtraction.use_gpu` et `--SiftMatching.use_gpu` : lancer
  `colmap feature_extractor -h` pour voir lesquelles existent.
- Rapporter `ref\timings.json`, `eval\align_m.json`, la ligne `colmap -h` et le nom du GPU. Le temps ne se compare à celui
  du Mac qu'en le disant : autre machine, GPU.
