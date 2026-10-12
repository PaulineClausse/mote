#!/usr/bin/env python3
"""Test de la boucle d'incremental.py sur CPU, rendu gsplat remplacé par un faux rendu différentiable.

Vérifie la mécanique, pas la qualité : arrivée des vues, semis de gaussiennes (paramètres, états d'Adam et de
gsplat agrandis ensemble), densification de gsplat.DefaultStrategy, raffinement de pose, évaluation, JSON de sortie.
Demande torch, gsplat 1.4.0, torchmetrics et Pillow ; sinon le test est sauté.

  python test_loop.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

try:
    import numpy as np
    import torch
    import gsplat
    from PIL import Image
except ImportError as e:
    print(f"test_loop sauté : {e}")
    sys.exit(0)

import test_stream  # noqa: E402


def fake_rasterization(means, quats, scales, opacities, colors, viewmats, Ks, width, height,
                       sh_degree=None, packed=False, **_):
    """Projette les centres (means2d dans le graphe, comme gsplat) et rend une image uniforme de la couleur moyenne."""
    C, N = viewmats.shape[0], means.shape[0]
    hom = torch.cat([means, torch.ones_like(means[:, :1])], 1)
    cam = torch.einsum("cij,nj->cni", viewmats, hom)[..., :3]
    z = cam[..., 2:3].clamp(min=1e-3)
    means2d = torch.einsum("cij,cnj->cni", Ks, cam / z)[..., :2]
    radii = (scales.mean(-1)[None] * Ks[:, None, 0, 0] / z[..., 0]).clamp(max=1e4).int() + (cam[..., 2] > 0).int()
    rgb = colors[:, 0, :] * 0.28209479177387814 + 0.5
    w = opacities[:, None]
    g = 1e-2 * means2d.sum()                     # gradient sur means2d, valeur rendue inchangée
    col = (w * rgb).sum(0) / (w.sum() + 1e-6) + (g - g.detach())
    out = col.expand(C, height, width, 3).clamp(0, 1)
    info = {"means2d": means2d, "radii": radii, "width": width, "height": height, "n_cameras": C,
            "gaussian_ids": None}
    return out, torch.ones(C, height, width, 1), info


def write_images(nd: Path, size: int = 32):
    names = (nd / "train_list.txt").read_text().split() + (nd / "test_list.txt").read_text().split()
    (nd / "images").mkdir()
    rng = np.random.default_rng(0)
    for n in names:
        Image.fromarray(rng.integers(0, 255, (size, size, 3), dtype=np.uint8)).save(nd / "images" / n)
    cam = nd / "headset" / "sparse" / "0" / "cameras.txt"
    cam.write_text(f"1 PINHOLE {size} {size} 20 20 16 16\n2 PINHOLE {size} {size} 20 20 16 16\n")


def run(args: list[str]) -> dict:
    gsplat.rasterization = fake_rasterization
    sys.modules.pop("incremental", None)
    import incremental
    assert incremental.main(args) == 0
    return json.loads(Path(args[args.index("--out") + 1]).read_text(encoding="utf-8"))


def main() -> int:
    torch.set_num_threads(2)
    import torch.nn.functional as F
    from torchmetrics.functional.image import structural_similarity_index_measure as tm_ssim
    import incremental
    fast_ssim = incremental.make_ssim_fast(torch, F, "cpu")
    g = torch.Generator().manual_seed(0)
    x = torch.rand(1, 3, 64, 48, generator=g)
    y = (x + 0.1 * torch.randn(1, 3, 64, 48, generator=g)).clamp(0, 1)
    ref, got = float(tm_ssim(y, x, data_range=1.0)), float(fast_ssim(y, x))
    assert abs(ref - got) < 1e-4, (ref, got)
    print(f"ok SSIM séparable = torchmetrics ({got:.5f} contre {ref:.5f})")
    with tempfile.TemporaryDirectory() as d:
        nd = test_stream.session(Path(d), n_pairs=40, fps=20.0, test_every=8)
        write_images(nd)
        common = ["--nsdata", str(nd), "--device", "cpu", "--seed-per-view", "20", "--sh-degree", "1"]

        off = run(common + ["--out", f"{d}/off.json", "--offline", "--max-steps", "720", "--eval-every-it", "200"])
        assert off["steps"] == 720 and [c["step"] for c in off["curve"]] == [0, 200, 400, 600, 720], off["curve"]
        assert off["curve"][0]["psnr"] is None and off["curve"][1]["psnr"] is not None
        assert all(c["n_test"] == 10 for c in off["curve"]) and off["curve"][-1]["n_train"] == 70
        assert off["n_gauss_final"] != 70 * 20, "la densification (étape 600) n'a rien changé"
        print("ok hors ligne :", off["it_per_s"], "it/s,", off["n_gauss_final"], "gaussiennes")

        for strat in ("uniform", "recent", "window"):
            r = run(common + ["--out", f"{d}/{strat}.json", "--strategy", strat, "--speed", "4",
                              "--tail-s", "0.5", "--eval-every-s", "0.25", "--margin-s", "0.5", "--no-pose-opt" if strat == "window"
                              else "--pose-opt"])
            c = r["curve"]
            assert c[-1]["n_train"] == 70 and c[-1]["n_test"] == 10, c[-1]
            assert [x["n_train"] for x in c] == sorted(x["n_train"] for x in c)          # les vues arrivent
            assert c[0]["n_train"] < 70, "tout est arrivé dès la première évaluation : le flux n'est pas rejoué"
            assert r["psnr_end_of_stream"] is not None and r["steps"] > 0
            print(f"ok flux {strat} :", r["steps"], "itérations,", len(c), "évaluations")
        fast = run(common + ["--out", f"{d}/fast.json", "--offline", "--max-steps", "60", "--eval-every-it", "30",
                             "--ssim", "fast", "--images-on-gpu", "--profile", "50"])
        assert set(fast["profile_ms"]) == {"pose", "image", "rendu", "perte", "retropropagation", "optimiseurs",
                                           "densification"}, fast["profile_ms"]
        print("ok options rapides, profil :", fast["profile_ms"])
        (Path(d) / "fast.json").unlink()
        import summarize
        assert summarize.main(["--runs", d]) == 0
        summ = json.loads((Path(d) / "summary.json").read_text(encoding="utf-8"))
        assert set(summ["configs"]) == {"hors ligne", "uniform", "recent", "window sans pose"}, summ["configs"].keys()
        assert summ["configs"]["hors ligne"]["it_per_s"]["n"] == 1
    print("test_loop : ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
