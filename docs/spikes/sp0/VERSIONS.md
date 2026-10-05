# SP-0 : versions d'outils requises

Les versions sont à **figer au moment de la capture** et recopiées dans `SP-0.md` (RISK-08 : le SDK Meta, MRUK et le
firmware changent souvent). Colonnes : « requis » vient d'un README ou d'une doc lue ; « préconisé » est mon choix pour
le spike ; « présent » est l'état de la machine où ce dossier a été préparé (Windows 11, Python 3.14.5, pas de GPU
NVIDIA visible, pas d'`adb`) et ne dit rien de la machine de capture.

| Outil | Requis / source | Préconisé pour SP-0 | Présent ici |
|---|---|---|---|
| Firmware Quest 3 / 3S | v74 ou plus (SRC-1) | version courante, **notée** | sans objet |
| QuestRealityCapture (SRC-1) | release v1.5.0, APK, non modifié (SPEC 4.1) | v1.5.0, SHA-256 noté | non téléchargé |
| Unity | 6000.4.5f1 (SRC-1), seulement pour *rebuild* | **aucun** : l'APK de release suffit, SRC-1 reste non modifié | sans objet |
| ADB (platform-tools) | requis pour `adb install` / `adb pull` (SRC-1) | version récente, notée (`adb version`) | absent |
| Python pour SRC-3 | 3.10 ou plus (SRC-3, INSTALLATION.md) | **3.10 ou 3.11**, venv dédié (`uv venv --python 3.10`) | 3.14.5 système, trop récent pour torch/nerfstudio : ne pas l'utiliser |
| SRC-3 `metaquest-3d-reconstruction` | `uv pip install .` (ou `-e ".[io,convert]"`, sans Open3D ni ONNX pour l'export COLMAP seul) | commit noté (`git rev-parse HEAD`) | non cloné |
| COLMAP | non imposé par SPEC | **3.11 ou plus, build CUDA** (binaire Windows ou conda-forge) ; noter `colmap -h` | absent |
| CUDA toolkit | doit correspondre à PyTorch et à gsplat (compilation de gsplat à la première utilisation) | **12.1** ou la version CUDA de la roue PyTorch choisie | absent (aucun GPU NVIDIA détecté) |
| PyTorch | nerfstudio 1.1.x ; roue cu121 | **2.1 à 2.4 avec CUDA 12.1**, la même pour tout le spike | absent |
| nerfstudio | PyPI : dernière 1.1.5 (relevé le 2026-10-05) | **1.1.5** (`pip install nerfstudio==1.1.5`) | absent |
| gsplat | dépendance de splatfacto, PyPI : dernière 1.5.3 | celle qu'installe nerfstudio 1.1.5, notée (`pip show gsplat`) | absent |
| LPIPS | PyPI `lpips` 0.1.4 ; nécessite torch, télécharge les poids VGG ou AlexNet de torchvision au premier appel | `lpips==0.1.4`, réseau `vgg`, le même partout | absent |
| numpy, Pillow | `metrics.py`, `align_sim3.py` | n'importe quelle version récente | numpy 2.4.6, Pillow 12.2.0 |
| ffmpeg | non requis | non requis | non vérifié |

Contraintes de matériel pour la partie PC (entraînement et COLMAP GPU) :
- **GPU NVIDIA CUDA** : splatfacto et le matching SIFT GPU de COLMAP en ont besoin. Ordre de grandeur pour une scène
  de pièce : 8 Go de VRAM suffisent à titre indicatif, 12 Go ou plus sont plus confortables. `[HYPOTHESE]` à confirmer
  par la mesure de la mémoire sur la première exécution et à noter dans `SP-0.md`.
- Compilateur C++ (MSVC Build Tools sous Windows) : gsplat compile ses extensions CUDA à la première exécution et
  échoue sans lui. `[A VERIFIER]` selon la roue gsplat disponible.
- Disque : environ 4 Go par minute de capture à 5 fps (PROTOCOL.md §0), plus images PNG exportées et base COLMAP.

## Installation proposée (à exécuter à la main, rien n'a été installé par la préparation)

```powershell
# venv d'outils de spike, hors dépôt
uv venv --python 3.10 D:\sp0\.venv ; D:\sp0\.venv\Scripts\Activate.ps1
uv pip install torch==2.4.1 torchvision --index-url https://download.pytorch.org/whl/cu121
uv pip install nerfstudio==1.1.5 lpips==0.1.4 numpy pillow
# SRC-3, dans son propre clone (peut partager ce venv)
git clone https://github.com/t-34400/metaquest-3d-reconstruction.git ; cd metaquest-3d-reconstruction
uv pip install -e ".[io,convert]"
# COLMAP : binaire de la release GitHub (colmap/colmap, variante CUDA) dans le PATH
colmap -h | Select -First 3
```
Le numéro de version de torch (2.4.1) est un point de départ plausible, pas une certitude : nerfstudio 1.1.5 déclare
ses bornes dans ses métadonnées (`pip show nerfstudio`). `[A VERIFIER]`

## Relevé à coller dans SP-0.md avant la capture

```powershell
python --version; pip show nerfstudio gsplat lpips torch | Select-String "^(Name|Version)"
colmap -h | Select -First 2 ; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
nvcc --version | Select -Last 2 ; adb version | Select -First 1
git -C <metaquest-3d-reconstruction> rev-parse HEAD
```
