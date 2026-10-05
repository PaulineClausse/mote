#!/usr/bin/env python3
"""PSNR, SSIM et LPIPS entre vues rendues et vues tenues à l'écart (SP-0, SPEC 13.2).

Outil de spike jetable, pas du code mote.

  python metrics.py --pred renders/ --gt holdout_images/ --out metrics.json [--no-lpips]
  python metrics.py --selftest

Appariement par nom de fichier (stem). Les images sont lues en RGB, flottants [0,1].
PSNR et SSIM : numpy + Pillow (SSIM gaussien 11x11, sigma 1,5, K1=0,01, K2=0,03, moyenne sur
les canaux, bords « valid » : même définition que skimage/torchmetrics par défaut ; l'écart avec
nerfstudio, qui utilise torchmetrics, doit rester < 1e-3, à confirmer sur la 1re capture).
LPIPS : torch + paquet `lpips`, réseau VGG par défaut dans nerfstudio (`--lpips-net vgg`),
importés seulement si LPIPS est demandé. Si absents, le script le dit et sort 2 (pas de valeur
inventée).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def load(path: Path) -> np.ndarray:
    from PIL import Image
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0


def psnr(a: np.ndarray, b: np.ndarray) -> float:
    mse = float(np.mean((a - b) ** 2))
    return float("inf") if mse == 0 else -10.0 * np.log10(mse)


def _gauss_win(size=11, sigma=1.5) -> np.ndarray:
    x = np.arange(size) - (size - 1) / 2
    g = np.exp(-(x ** 2) / (2 * sigma ** 2))
    return g / g.sum()


def _filter(img: np.ndarray, g: np.ndarray) -> np.ndarray:
    """Filtre gaussien séparable, sortie « valid »."""
    k = len(g)
    h = sum(g[i] * img[:, i:img.shape[1] - k + 1 + i] for i in range(k))
    return sum(g[i] * h[i:h.shape[0] - k + 1 + i] for i in range(k))


def ssim(a: np.ndarray, b: np.ndarray) -> float:
    g = _gauss_win()
    c1, c2 = 0.01 ** 2, 0.03 ** 2
    vals = []
    for ch in range(a.shape[2]):
        x, y = a[..., ch], b[..., ch]
        mx, my = _filter(x, g), _filter(y, g)
        sxx = _filter(x * x, g) - mx * mx
        syy = _filter(y * y, g) - my * my
        sxy = _filter(x * y, g) - mx * my
        s = ((2 * mx * my + c1) * (2 * sxy + c2)) / ((mx * mx + my * my + c1) * (sxx + syy + c2))
        vals.append(s.mean())
    return float(np.mean(vals))


class Lpips:
    def __init__(self, net: str = "vgg"):
        import torch  # noqa: F401
        import lpips
        self.torch = torch
        self.dev = "cuda" if torch.cuda.is_available() else "cpu"
        self.m = lpips.LPIPS(net=net).to(self.dev).eval()

    def __call__(self, a: np.ndarray, b: np.ndarray) -> float:
        t = lambda x: (self.torch.from_numpy(x).permute(2, 0, 1)[None].float() * 2 - 1).to(self.dev)
        with self.torch.no_grad():
            return float(self.m(t(a), t(b)).item())


def compute(pred_dir: Path, gt_dir: Path, lpips_net: str | None) -> dict:
    preds = {p.stem: p for p in sorted(pred_dir.iterdir()) if p.suffix.lower() in EXTS}
    gts = {p.stem: p for p in sorted(gt_dir.iterdir()) if p.suffix.lower() in EXTS}
    names = sorted(set(preds) & set(gts))
    if not names:
        raise SystemExit(f"aucun nom en commun entre {pred_dir} ({len(preds)}) et {gt_dir} ({len(gts)})")
    lp = Lpips(lpips_net) if lpips_net else None
    rows = []
    for n in names:
        a, b = load(preds[n]), load(gts[n])
        if a.shape != b.shape:
            raise SystemExit(f"{n}: tailles différentes {a.shape} vs {b.shape} (rendre à la résolution GT)")
        rows.append({"name": n, "psnr": psnr(a, b), "ssim": ssim(a, b),
                     "lpips": lp(a, b) if lp else None})
    summ = {k: float(np.mean([r[k] for r in rows])) for k in ("psnr", "ssim")}
    summ["lpips"] = float(np.mean([r["lpips"] for r in rows])) if lp else None
    return {"n_views": len(rows), "mean": summ, "lpips_net": lpips_net, "per_view": rows,
            "missing_pred": sorted(set(gts) - set(preds)), "missing_gt": sorted(set(preds) - set(gts))}


def selftest() -> int:
    rng = np.random.default_rng(0)
    a = rng.random((64, 64, 3))
    assert psnr(a, a) == float("inf") and abs(ssim(a, a) - 1) < 1e-9
    b = np.clip(a + 0.1, 0, 1)
    assert abs(psnr(a, np.clip(a + 0.1, 0, 1)) - psnr(a, b)) < 1e-12
    c = a.copy(); c[...] = np.clip(a + 0.05 * rng.standard_normal(a.shape), 0, 1)
    p = psnr(a, c)
    assert 25 < p < 28, p                      # sigma 0,05 -> ~26 dB
    assert ssim(a, c) < ssim(a, np.clip(a + 0.01 * rng.standard_normal(a.shape), 0, 1)) < 1
    print(f"selftest PSNR/SSIM ok (psnr={p:.2f} dB). LPIPS non testé ici (torch absent ou non requis)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pred", type=Path)
    ap.add_argument("--gt", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--no-lpips", action="store_true")
    ap.add_argument("--lpips-net", default="vgg", choices=["vgg", "alex", "squeeze"])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.pred and a.gt):
        ap.error("--pred et --gt requis")
    try:
        res = compute(a.pred, a.gt, None if a.no_lpips else a.lpips_net)
    except ImportError as e:
        print(f"LPIPS indisponible ({e}). Installer torch + lpips dans le venv de spike "
              f"(voir VERSIONS.md) ou passer --no-lpips (PSNR/SSIM seuls).", file=sys.stderr)
        return 2
    txt = json.dumps(res, indent=2)
    if a.out:
        a.out.write_text(txt)
    print(json.dumps({k: res[k] for k in ("n_views", "mean", "lpips_net")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
