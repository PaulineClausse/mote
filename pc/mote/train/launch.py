"""Entraînement dans son propre environnement (ADR-976d).

nerfstudio 1.1.5 exige protobuf <= 3.20.3, le code généré de mote.v1 protobuf >= 7.35.1 : les deux ne tiennent pas dans
un même environnement. L'entraînement tourne donc dans un processus à part, lancé par uv hors du projet mote
(`--no-project`), avec ses propres dépendances. Il n'importe ni mote.v1 ni le MCAP : il ne lit que l'export nerfstudio
du répertoire de dataset (SPEC-3d2a §7.3), produit ici, côté mote.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

from mote.tools.export import export_nerfstudio

NERFSTUDIO = "nerfstudio==1.1.5"    # ADR-da6e, version de SP-0
PYTHON = "3.11"

# Variables qui feraient voir le projet ou l'environnement de mote au processus d'entraînement.
_LEAKS = ("VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME", "UV_PROJECT", "UV_PROJECT_ENVIRONMENT", "CONDA_PREFIX")


def train_env_command(*args: str) -> list[str]:
    """Commande qui exécute `args` dans l'environnement d'entraînement."""
    uv = shutil.which("uv") or "uv"
    return [uv, "run", "--no-project", "--python", PYTHON, "--with", NERFSTUDIO, *args]


def train_env(base: Mapping[str, str]) -> dict[str, str]:
    """Environnement du processus d'entraînement : celui de l'appelant sans ce qui mène à mote ; sortie en UTF-8
    (la console Windows en cp1252 fait échouer l'affichage de nerfstudio)."""
    env = {k: v for k, v in base.items() if k not in _LEAKS}
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def train(dataset: Path, runs: Path, method: str = "splatfacto", iterations: int = 30000, device: str = "cuda",
          extra: Sequence[str] = ()) -> Path:
    """Exporte le dataset au format nerfstudio (s'il ne l'est pas), lance `ns-train` dans l'environnement
    d'entraînement et renvoie le dernier checkpoint. Le repère est déjà canonique : nerfstudio ne recentre ni ne
    réoriente les poses."""
    dataset, runs = Path(dataset), Path(runs)
    ns = dataset / "export" / "nerfstudio"
    if not (ns / "transforms.json").exists():
        export_nerfstudio(dataset, ns)
    runs.mkdir(parents=True, exist_ok=True)
    cmd = train_env_command(
        "ns-train", method,
        "--data", str(ns), "--output-dir", str(runs),
        "--max-num-iterations", str(iterations),
        "--steps-per-save", str(max(1, iterations - 1)),
        "--machine.device-type", device,
        "--vis", "tensorboard", "--viewer.quit-on-train-completion", "True",
        *extra,
        "nerfstudio-data", "--auto-scale-poses", "False", "--center-method", "none",
        "--orientation-method", "none", "--train-split-fraction", "1.0",
    )
    r = subprocess.run(cmd, env=train_env(os.environ), cwd=runs, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ns-train a échoué ({r.returncode}) :\n{r.stderr[-4000:]}")
    ckpts = sorted(runs.rglob("*.ckpt"), key=lambda p: p.stat().st_mtime)
    if not ckpts:
        raise RuntimeError(f"ns-train n'a écrit aucun checkpoint sous {runs}")
    return ckpts[-1]
