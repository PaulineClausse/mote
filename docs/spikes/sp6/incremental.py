#!/usr/bin/env python3
"""SP-6 : entraînement 3DGS incrémental sur les poses du casque, rejoué en temps réel (gsplat 1.4.0, CUDA).

Outil de spike jetable, pas du code mote. Lancé par run_sp6.ps1 dans le venv d'entraînement de SP-0 :

  python incremental.py --nsdata <work>/<session>/nsdata --out run.json --strategy recent --seed 0
  python incremental.py --nsdata ... --out off.json --offline --max-steps 6000 --eval-every-it 200

Boucle : à chaque itération, les vues d'entraînement dont l'horodatage est passé (horloge = temps d'entraînement
écoulé, évaluations exclues) sont disponibles ; chaque vue qui arrive sème `--seed-per-view` gaussiennes le long de
rayons tirés au hasard dans son image, à une profondeur aléatoire (SP-7 la remplacera par la profondeur mesurée).
Une vue est tirée selon la stratégie (stream.Sampler), rendue, et la perte 0,8 L1 + 0,2 (1 - SSIM) est rétropropagée ;
densification et élagage par gsplat.DefaultStrategy ; raffinement de pose par vue (comme SO3xR3) si --pose-opt.
Toutes les `--eval-every-s` secondes de flux (ou `--eval-every-it` itérations hors ligne), on mesure le PSNR des vues
de validation déjà couvertes, rendues avec leurs poses d'origine.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stream as st  # noqa: E402

C0 = 0.28209479177387814


def qvec_to_rot(q) -> np.ndarray:
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


def viewmat(v: st.View) -> np.ndarray:
    m = np.eye(4)
    m[:3, :3] = qvec_to_rot(v.qvec)
    m[:3, 3] = v.tvec
    return m


def make_ssim_fast(torch, F, device, size: int = 11, sigma: float = 1.5):
    """SSIM gaussien 11x11, sigma 1,5, K1 = 0,01, K2 = 0,03, bords « valid » : la définition de torchmetrics
    (qui filtre en 2D puis rogne les bords), calculée avec deux filtres 1D."""
    x = torch.arange(size, dtype=torch.float32, device=device) - (size - 1) / 2
    g = torch.exp(-x ** 2 / (2 * sigma ** 2)); g = g / g.sum()
    gh, gv = g.view(1, 1, 1, size), g.view(1, 1, size, 1)
    c1, c2 = 0.01 ** 2, 0.03 ** 2

    def ssim(a, b):                                     # [B, C, H, W], valeurs dans [0, 1]
        B, C = a.shape[:2]
        z = torch.cat([a, b, a * a, b * b, a * b], 1)   # [B, 5C, H, W]
        z = F.conv2d(z, gh.expand(5 * C, 1, 1, size), groups=5 * C)
        z = F.conv2d(z, gv.expand(5 * C, 1, size, 1), groups=5 * C)
        ma, mb, saa, sbb, sab = z.split(C, 1)
        saa, sbb, sab = saa - ma * ma, sbb - mb * mb, sab - ma * mb
        s = ((2 * ma * mb + c1) * (2 * sab + c2)) / ((ma * ma + mb * mb + c1) * (saa + sbb + c2))
        return s.mean()
    return ssim


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nsdata", type=Path, required=True)
    ap.add_argument("--poses", default="headset/sparse/0", help="headset/sparse/0 (casque) ou ref/sparse/0")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--strategy", choices=st.STRATEGIES, default="uniform")
    ap.add_argument("--offline", action="store_true", help="toutes les vues dès t = 0 (latence d'aperçu pure)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--speed", type=float, default=1.0, help="vitesse du rejeu (1 = cadence réelle)")
    ap.add_argument("--tail-s", type=float, default=60.0, help="entraînement continué après la fin du flux")
    ap.add_argument("--max-steps", type=int, default=0, help="hors ligne : arrêt à ce nombre d'itérations")
    ap.add_argument("--eval-every-s", type=float, default=5.0)
    ap.add_argument("--eval-every-it", type=int, default=200)
    ap.add_argument("--margin-s", type=float, default=2.0, help="délai après lequel une vue de test est couverte")
    ap.add_argument("--window-s", type=float, default=5.0)
    ap.add_argument("--p-recent", type=float, default=0.5)
    ap.add_argument("--downscale", type=int, default=1)
    ap.add_argument("--seed-per-view", type=int, default=500)
    ap.add_argument("--init-npz", type=Path, default=None,
                    help="SP-7 : nuage de profondeur (depth_init.py) à la place du semis aléatoire ; hors ligne, tout "
                         "au départ ; en flux, chaque point quand sa carte de profondeur est arrivée")
    ap.add_argument("--depth-range", type=float, nargs=2, default=(0.3, 4.0), help="profondeur de semis (m)")
    ap.add_argument("--scene-scale", type=float, default=2.0, help="échelle de la scène (m), pour gsplat")
    ap.add_argument("--sh-degree", type=int, default=3)
    ap.add_argument("--pose-opt", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--device", default="cuda", help="cuda ; cpu seulement pour le test de la boucle")
    ap.add_argument("--reset-every", type=int, default=3000,
                    help="remise des opacités de gsplat (3000 par défaut) ; 0 = jamais, pour voir si elle gêne l'aperçu")
    ap.add_argument("--ssim", choices=("torchmetrics", "fast", "off"), default="torchmetrics",
                    help="SSIM de la perte : torchmetrics (filtre 2D), fast (filtre séparable, même définition), "
                         "off (L1 seule)")
    ap.add_argument("--images-on-gpu", action="store_true", help="garder les images en uint8 sur le GPU")
    ap.add_argument("--profile", type=int, default=0,
                    help="N > 0 : chronomètre chaque partie de l'itération (avec synchronisation) sur N itérations")
    a = ap.parse_args(argv)

    import torch
    import torch.nn.functional as F
    from PIL import Image
    from gsplat import DefaultStrategy, rasterization
    from gsplat.strategy.ops import _update_param_with_optimizer
    from torchmetrics.functional.image import structural_similarity_index_measure as ssim_fn

    if a.ssim == "fast":
        ssim_fn = make_ssim_fast(torch, F, a.device)  # noqa: F811
    torch.manual_seed(a.seed)
    np.random.seed(a.seed)
    dev = a.device
    gpu = torch.cuda.get_device_name(0) if dev == "cuda" else dev

    def sync():
        if dev == "cuda":
            torch.cuda.synchronize()
    views, cams = st.load_session(a.nsdata, a.poses)
    s = st.Stream(views, speed=a.speed, offline=a.offline, margin_s=a.margin_s)
    sampler = st.Sampler(s, a.strategy, seed=a.seed, window_s=a.window_s, p_recent=a.p_recent)
    print(f"[sp6] {len(s.train)} vues train, {len(s.test)} test, flux {s.duration_s:.0f} s, "
          f"{'hors ligne' if a.offline else a.strategy}, GPU {gpu}", flush=True)

    # ---------------------------------------------------------------- données (CPU, uint8)
    def load(v: st.View) -> torch.Tensor:
        im = Image.open(a.nsdata / "images" / v.name).convert("RGB")
        if a.downscale > 1:
            im = im.resize((im.width // a.downscale, im.height // a.downscale), Image.BICUBIC)
        return torch.from_numpy(np.asarray(im).copy())

    def K_of(v: st.View) -> torch.Tensor:
        c, d = cams[v.camera_id], a.downscale
        return torch.tensor([[c.fx / d, 0, c.cx / d], [0, c.fy / d, c.cy / d], [0, 0, 1]], dtype=torch.float32)

    t_load = time.perf_counter()
    imgs_tr = [load(v) for v in s.train]
    imgs_te = [load(v) for v in s.test]
    if a.images_on_gpu:
        imgs_tr = [im.to(dev) for im in imgs_tr]
        imgs_te = [im.to(dev) for im in imgs_te]
    print(f"[sp6] images chargées en {time.perf_counter() - t_load:.0f} s (hors chrono)", flush=True)
    H, W = imgs_tr[0].shape[:2]
    Ks_tr = torch.stack([K_of(v) for v in s.train]).to(dev)
    Ks_te = torch.stack([K_of(v) for v in s.test]).to(dev)
    vm_tr = torch.tensor(np.stack([viewmat(v) for v in s.train]), dtype=torch.float32, device=dev)
    vm_te = torch.tensor(np.stack([viewmat(v) for v in s.test]), dtype=torch.float32, device=dev)
    c2w_tr = torch.linalg.inv(vm_tr)

    # ---------------------------------------------------------------- gaussiennes et optimiseurs
    lrs = {"means": 1.6e-4 * a.scene_scale, "scales": 5e-3, "quats": 1e-3, "opacities": 5e-2,
           "sh0": 2.5e-3, "shN": 2.5e-3 / 20}
    K_sh = (a.sh_degree + 1) ** 2
    splats = torch.nn.ParameterDict({
        "means": torch.nn.Parameter(torch.zeros(0, 3, device=dev)),
        "scales": torch.nn.Parameter(torch.zeros(0, 3, device=dev)),
        "quats": torch.nn.Parameter(torch.zeros(0, 4, device=dev)),
        "opacities": torch.nn.Parameter(torch.zeros(0, device=dev)),
        "sh0": torch.nn.Parameter(torch.zeros(0, 1, 3, device=dev)),
        "shN": torch.nn.Parameter(torch.zeros(0, K_sh - 1, 3, device=dev)),
    })
    optimizers = {k: torch.optim.Adam([{"params": splats[k], "lr": lr, "name": k}], eps=1e-15)
                  for k, lr in lrs.items()}
    strategy = DefaultStrategy(refine_stop_iter=10 ** 9,   # le flux ne s'arrête pas : densifier tout du long
                               reset_every=a.reset_every if a.reset_every > 0 else 10 ** 9)
    strategy.check_sanity(splats, optimizers)
    sstate = strategy.initialize_state(scene_scale=a.scene_scale)

    pose_delta = torch.nn.Parameter(torch.zeros(len(s.train), 9, device=dev))
    pose_opt = torch.optim.Adam([pose_delta], lr=1e-5, weight_decay=1e-6) if a.pose_opt else None
    ident6 = torch.tensor([1.0, 0, 0, 0, 1.0, 0], device=dev)

    def rot6d(d6: torch.Tensor) -> torch.Tensor:
        a1, a2 = d6[..., :3], d6[..., 3:]
        b1 = F.normalize(a1, dim=-1)
        b2 = F.normalize(a2 - (b1 * a2).sum(-1, keepdim=True) * b1, dim=-1)
        return torch.stack((b1, b2, torch.cross(b1, b2, dim=-1)), dim=-2)

    init = None
    if a.init_npz is not None:
        with np.load(a.init_npz) as z:
            order = np.argsort(z["t"], kind="stable")
            init = {"xyz": torch.tensor(z["xyz"][order], dtype=torch.float32, device=dev),
                    "rgb": torch.tensor(z["rgb"][order], dtype=torch.float32, device=dev),
                    "t": z["t"][order], "voxel": float(z["voxel"]), "next": 0}
        print(f"[sp6] init profondeur : {len(init['t'])} points ({a.init_npz})", flush=True)

    @torch.no_grad()
    def add_gaussians(means: torch.Tensor, rgb: torch.Tensor, log_scale: torch.Tensor):
        n = len(means)
        if n == 0:
            return
        new = {
            "means": means,
            "scales": log_scale[:, None].repeat(1, 3),
            "quats": torch.rand(n, 4, device=dev),
            "opacities": torch.logit(torch.full((n,), 0.1, device=dev)),
            "sh0": ((rgb - 0.5) / C0)[:, None, :],
            "shN": torch.zeros(n, K_sh - 1, 3, device=dev),
        }
        _update_param_with_optimizer(
            lambda name, p_: torch.nn.Parameter(torch.cat([p_, new[name]])),
            lambda key, v_: torch.cat([v_, torch.zeros((n, *v_.shape[1:]), device=dev)]),
            splats, optimizers)
        for k, v_ in sstate.items():
            if isinstance(v_, torch.Tensor):
                sstate[k] = torch.cat([v_, torch.zeros((n, *v_.shape[1:]), device=v_.device)])

    @torch.no_grad()
    def seed_view(i: int):
        """Sème des gaussiennes pour la vue i qui arrive : le nuage de profondeur arrivé jusqu'à son instant (SP-7, tout
        hors ligne), sinon des rayons de la vue à profondeur aléatoire, couleur du pixel."""
        if init is not None:
            t_i = math.inf if a.offline else s.train[i].t
            j0 = init["next"]
            j1 = int(np.searchsorted(init["t"], t_i, side="right"))
            if j1 > j0:
                add_gaussians(init["xyz"][j0:j1], init["rgb"][j0:j1],
                              torch.full((j1 - j0,), math.log(init["voxel"]), device=dev))
                init["next"] = j1
            return
        n = a.seed_per_view
        img = imgs_tr[i]
        u = torch.randint(0, W, (n,)); v = torch.randint(0, H, (n,))
        rgb = img[v.to(img.device), u.to(img.device)].float().to(dev) / 255.0
        K = Ks_tr[i]
        d = torch.empty(n, device=dev).uniform_(*a.depth_range)
        x = (u.to(dev).float() + 0.5 - K[0, 2]) / K[0, 0] * d
        y = (v.to(dev).float() + 0.5 - K[1, 2]) / K[1, 1] * d
        p = c2w_tr[i] @ torch.stack([x, y, d, torch.ones_like(d)])
        add_gaussians(p[:3].T, rgb, torch.log((d / K[0, 0] * (W / math.sqrt(n)) * 0.5).clamp(min=1e-4)))

    def render(vm: torch.Tensor, K: torch.Tensor, sh_deg: int):
        colors = torch.cat([splats["sh0"], splats["shN"]], 1)
        return rasterization(
            means=splats["means"], quats=splats["quats"], scales=torch.exp(splats["scales"]),
            opacities=torch.sigmoid(splats["opacities"]), colors=colors, viewmats=vm, Ks=K,
            width=W, height=H, sh_degree=sh_deg, packed=False)

    @torch.no_grad()
    def evaluate(idx: list[int], sh_deg: int) -> float | None:
        if not idx or len(splats["means"]) == 0:
            return None
        ps = []
        for i in idx:
            out, _, _ = render(vm_te[i:i + 1], Ks_te[i:i + 1], sh_deg)
            gt = imgs_te[i].to(dev).float() / 255.0
            mse = torch.mean((out[0].clamp(0, 1) - gt) ** 2)
            ps.append(float(-10 * torch.log10(mse)))
        return float(np.mean(ps))

    # ---------------------------------------------------------------- boucle
    curve, step, seeded, train_s = [], 0, 0, 0.0
    timing: dict[str, float] = {}
    tp = 0.0
    next_eval = a.eval_every_s
    end_s = s.duration_s + a.tail_s
    sync()
    t_last = time.perf_counter()
    while True:
        stream_s = train_s
        sh_deg = min(step // 1000, a.sh_degree)
        if a.offline:
            if step % a.eval_every_it == 0 or step == a.max_steps:
                sync(); train_s += time.perf_counter() - t_last
                cov = list(range(len(s.test)))
                curve.append({"step": step, "train_s": round(train_s, 2), "stream_s": round(train_s, 2),
                              "n_gauss": len(splats["means"]), "n_train": seeded, "n_test": len(cov),
                              "psnr": evaluate(cov, sh_deg)})
                print(f"[sp6] it {step:6d}  {train_s:7.1f} s  {len(splats['means']):8d} gaussiennes  "
                      f"PSNR {curve[-1]['psnr']}", flush=True)
                t_last = time.perf_counter()
            if step >= a.max_steps:
                break
        else:
            if stream_s >= next_eval or stream_s >= end_s:
                sync(); train_s += time.perf_counter() - t_last
                cov = s.covered_test(train_s)
                curve.append({"step": step, "train_s": round(train_s, 2), "stream_s": round(train_s, 2),
                              "n_gauss": len(splats["means"]), "n_train": seeded, "n_test": len(cov),
                              "psnr": evaluate(cov, sh_deg)})
                print(f"[sp6] flux {train_s:6.1f} s  it {step:6d}  {seeded:4d} vues arrivées  "
                      f"{len(cov):3d} vues test couvertes  {len(splats['means']):8d} gaussiennes  "
                      f"PSNR {curve[-1]['psnr']}", flush=True)
                next_eval += a.eval_every_s
                t_last = time.perf_counter()
                if train_s >= end_s:
                    break

        n_arr = s.n_arrived(stream_s)
        while seeded < n_arr:
            seed_view(seeded)
            seeded += 1
        i = sampler.pick(stream_s)
        if i is None:                                   # rien d'arrivé : on attend la première image
            time.sleep(0.001)
            now = time.perf_counter(); train_s += now - t_last; t_last = now
            continue

        prof = a.profile and step < a.profile
        if prof:
            sync(); tp = time.perf_counter()

        def lap(name):
            nonlocal tp
            if prof:
                sync(); now_ = time.perf_counter()
                timing[name] = timing.get(name, 0.0) + now_ - tp
                tp = now_

        vm = vm_tr[i:i + 1]
        if pose_opt is not None:
            d = pose_delta[i]
            T = torch.eye(4, device=dev)
            T[:3, :3] = rot6d(d[3:] + ident6)
            T[:3, 3] = d[:3]
            vm = torch.linalg.inv(c2w_tr[i] @ T)[None]
        lap("pose")
        gt = imgs_tr[i].to(dev, non_blocking=True).float()[None] / 255.0
        lap("image")
        out, alphas, info = render(vm, Ks_tr[i:i + 1], sh_deg)
        strategy.step_pre_backward(splats, optimizers, sstate, step, info)
        lap("rendu")
        l1 = (out - gt).abs().mean()
        if a.ssim == "off":
            loss = l1
        elif a.ssim == "fast":
            loss = 0.8 * l1 + 0.2 * (1 - ssim_fn(out.permute(0, 3, 1, 2), gt.permute(0, 3, 1, 2)))
        else:
            ssim = ssim_fn(out.permute(0, 3, 1, 2), gt.permute(0, 3, 1, 2), data_range=1.0)
            loss = 0.8 * l1 + 0.2 * (1 - ssim)
        lap("perte")
        loss.backward()
        lap("retropropagation")
        for opt in optimizers.values():
            opt.step(); opt.zero_grad(set_to_none=True)
        if pose_opt is not None:
            pose_opt.step(); pose_opt.zero_grad(set_to_none=True)
        lap("optimiseurs")
        strategy.step_post_backward(splats, optimizers, sstate, step, info, packed=False)
        lap("densification")
        step += 1
        if a.profile and step == a.profile:
            tot = sum(timing.values())
            print("[sp6] profil sur %d itérations : %s ; %.1f ms/it" % (
                step, ", ".join(f"{k} {1000 * v / step:.1f} ms" for k, v in timing.items()), 1000 * tot / step),
                flush=True)
        if not a.offline:
            now = time.perf_counter(); train_s += now - t_last; t_last = now

    # ---------------------------------------------------------------- résumé
    hit = st.first_reaching(curve, 20.0, min_views=1 if a.offline else 4)
    last = curve[-1]
    res = {
        "args": {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(a).items()},
        "gpu": gpu, "resolution": [W, H],
        "n_train": len(s.train), "n_test": len(s.test), "stream_duration_s": s.duration_s,
        "steps": step, "train_s": round(train_s, 2), "it_per_s": round(step / max(train_s, 1e-9), 1),
        "t20_s": hit["stream_s"] if hit else None, "t20_step": hit["step"] if hit else None,
        "psnr_end_of_stream": None if a.offline else next(
            (c["psnr"] for c in curve if c["stream_s"] >= s.duration_s and c["psnr"] is not None), None),
        "profile_ms": {k: round(1000 * v / max(min(step, a.profile), 1), 2) for k, v in timing.items()},
        "psnr_final": last["psnr"], "n_gauss_final": last["n_gauss"], "curve": curve,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"[sp6] {res['it_per_s']} it/s ; 20 dB à {res['t20_s']} s (it. {res['t20_step']}) ; "
          f"PSNR final {res['psnr_final']} ; -> {a.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
