"""Le transforms.json exporté se charge avec le parseur de nerfstudio lui-même (critère de WP-07).

nerfstudio 1.1.5 exige protobuf <= 3.20.3, et le code généré de mote.v1 exige protobuf >= 7.35.1 : les deux ne tiennent
pas dans un même environnement. L'export est donc produit ici, puis chargé dans un processus à part, avec son propre
environnement (uv). Lent la première fois (installation de nerfstudio et de torch) : test lancé seulement avec
MOTE_TEST_NERFSTUDIO=1.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from mote.ingest.replay import ingest_replay
from mote.tools.export import export_nerfstudio

SAMPLE = Path(__file__).resolve().parent / "data" / "sample_session.mcap"

CHECK = """
import sys
from pathlib import Path
from nerfstudio.data.dataparsers.nerfstudio_dataparser import NerfstudioDataParserConfig
cfg = NerfstudioDataParserConfig(data=Path(sys.argv[1]), train_split_fraction=1.0, auto_scale_poses=False,
                                 center_method="none", orientation_method="none", load_3D_points=False)
out = cfg.setup().get_dataparser_outputs(split="train")
assert all(Path(p).exists() for p in out.image_filenames)
# Les pixels aussi : nerfstudio empile toutes les images, qui doivent avoir le même nombre de canaux (TASK-af1e).
import torch
from nerfstudio.data.datasets.base_dataset import InputDataset
ds = InputDataset(out)
assert torch.stack([ds[i]["image"] for i in range(len(ds))]).shape[-1] == 3
print(len(out.image_filenames), tuple(out.cameras.camera_to_worlds.shape), float(out.cameras.fx[0]),
      int(out.cameras.width[0]))
"""


@pytest.mark.skipif(os.environ.get("MOTE_TEST_NERFSTUDIO") != "1", reason="MOTE_TEST_NERFSTUDIO=1 pour le lancer")
def test_nerfstudio_dataparser_loads_export(tmp_path):
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv absent")
    d = tmp_path / "dataset"
    ingest_replay(SAMPLE, d)
    path = export_nerfstudio(d, tmp_path / "ns")
    r = subprocess.run([uv, "run", "--no-project", "--python", "3.11", "--with", "nerfstudio==1.1.5",
                        "python", "-c", CHECK, str(path)], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr[-3000:]
    assert r.stdout.split()[-6:] == ["14", "(14,", "3,", "4)", "50.0", "64"], r.stdout
