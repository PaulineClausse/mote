"""Critère de TASK-239e : une session ingérée puis entraînée selon ADR-976d, sans conflit de versions protobuf.

L'ingest tourne ici, dans l'environnement de mote (protobuf 7, mote.v1) ; l'entraînement tourne dans un processus et
un environnement à part (nerfstudio 1.1.5, protobuf 3.20), qui ne lit que le répertoire de dataset. Le test complet
installe nerfstudio et torch la première fois : lancé seulement avec MOTE_TEST_NERFSTUDIO=1.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from google.protobuf import __version__ as protobuf_version

from mote.ingest.replay import ingest_replay
from mote.train.launch import NERFSTUDIO, train, train_env, train_env_command

SAMPLE = Path(__file__).resolve().parent / "data" / "sample_session.mcap"


def test_training_command_runs_outside_the_mote_project():
    cmd = train_env_command("python", "-c", "pass")
    assert cmd[1:3] == ["run", "--no-project"], cmd
    assert cmd[cmd.index("--with") + 1] == NERFSTUDIO == "nerfstudio==1.1.5"
    assert cmd[-3:] == ["python", "-c", "pass"]
    assert not any("mote" in a for a in cmd[:-3]), "l'environnement d'entraînement ne doit pas contenir mote"
    env = train_env({"VIRTUAL_ENV": "x", "PYTHONPATH": "y", "UV_PROJECT": "z", "PATH": "p"})
    assert "VIRTUAL_ENV" not in env and "PYTHONPATH" not in env and "UV_PROJECT" not in env
    assert env["PATH"] == "p" and env["PYTHONUTF8"] == "1"


@pytest.mark.skipif(os.environ.get("MOTE_TEST_NERFSTUDIO") != "1", reason="MOTE_TEST_NERFSTUDIO=1 pour le lancer")
def test_session_ingested_then_trained_without_protobuf_conflict(tmp_path):
    if shutil.which("uv") is None:
        pytest.skip("uv absent")
    # Côté mote : protobuf 7 et le code généré de mote.v1.
    from mote.v1 import mote_pb2  # noqa: F401
    assert int(protobuf_version.split(".")[0]) >= 7, protobuf_version
    d = tmp_path / "dataset"
    assert ingest_replay(SAMPLE, d)["complete"]

    ckpt = train(d, tmp_path / "runs", method="nerfacto", iterations=3, device="cpu",
                 extra=["--pipeline.datamanager.train-num-rays-per-batch", "256"])
    assert ckpt.suffix == ".ckpt" and ckpt.stat().st_size > 0, ckpt

    # Côté entraînement : protobuf 3.20, et mote introuvable.
    probe = ("import google.protobuf as p, importlib.util as u; "
             "print(p.__version__, u.find_spec('mote') is None)")
    r = subprocess.run(train_env_command("python", "-c", probe), env=train_env(os.environ), capture_output=True,
                       text=True, encoding="utf-8", cwd=tmp_path)
    assert r.returncode == 0, r.stderr[-2000:]
    assert r.stdout.split()[-2:] == ["3.20.3", "True"], r.stdout
