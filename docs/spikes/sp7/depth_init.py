#!/usr/bin/env python3
"""SP-7 : nuage d'initialisation de S1 par rétroprojection de la profondeur du casque (option B, SPEC 11.3).

Outil de spike jetable, pas du code mote. numpy et Pillow (venv d'entraînement de SP-0), plus matplotlib pour les vues.

  python depth_init.py --session <S1 brute, avec left_depth/> --nsdata <jeu commun de S1> --out <dossier>

1. Cartes de profondeur gauche et droite (QuestRealityCapture), linéarisées par la formule de SP-3,
   z = near / (1 - d), un pixel sur `--stride`, z dans [--zmin, --zmax].
2. Bords écartés : la profondeur du casque est lissée par le système (SP-3) et relie les objets au fond par des valeurs
   intermédiaires ; un pixel dont un voisin diffère de plus de `--edge` (relatif) est rejeté.
3. Hold-out exclu : aucune carte prise à moins de `--holdout-margin` s d'une vue de validation.
4. Repère : les points (monde Unity, Z inversé) sont portés dans le repère du jeu commun par la similitude qui aligne la
   trajectoire de la caméra de profondeur sur les centres des caméras RGB du jeu commun, appariés dans le temps
   (Umeyama). L'écart résiduel et l'échelle sont rapportés : on attend une échelle de 1 et quelques cm.
5. Couleur : projection dans l'image d'entraînement la plus proche dans le temps.
6. Grille de `--voxel` m : un point par voxel, celui vu en premier ; son instant `t` (s depuis la première image)
   sert au semis en flux (incremental.py --init-npz).

Sorties : init.npz (xyz, rgb, t, voxel), init.ply, init_views.png, init.json.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import OrderedDict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sp3"))
sys.path.insert(0, str(HERE.parent / "sp6"))
import depthlib as dl  # noqa: E402
import stream as st  # noqa: E402


def edge_mask(z: np.ndarray, rel: float) -> np.ndarray:
    """Vrai là où aucun des 4 voisins ne s'écarte de plus de `rel` (relatif) : écarte les bords lissés."""
    ok = np.isfinite(z)
    m = ok.copy()
    for dy, dx in ((0, 1), (1, 0)):
        a = z[: z.shape[0] - dy, : z.shape[1] - dx]
        b = z[dy:, dx:]
        bad = ~(np.abs(a - b) <= rel * np.minimum(a, b))       # NaN compris
        m[: z.shape[0] - dy, : z.shape[1] - dx] &= ~bad
        m[dy:, dx:] &= ~bad
    return m & ok


def umeyama(src: np.ndarray, dst: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    """Similitude (s, R, t) minimisant |dst - (s R src + t)|² (Umeyama 1991)."""
    mu_s, mu_d = src.mean(0), dst.mean(0)
    xs, xd = src - mu_s, dst - mu_d
    cov = xd.T @ xs / len(src)
    U, D, Vt = np.linalg.svd(cov)
    S = np.eye(3)
    if np.linalg.det(U) * np.linalg.det(Vt) < 0:
        S[2, 2] = -1
    R = U @ S @ Vt
    s = float(np.trace(np.diag(D) @ S) / (xs ** 2).sum(1).mean())
    return s, R, mu_d - s * R @ mu_s


def first_per_voxel(xyz: np.ndarray, t: np.ndarray, voxel: float) -> np.ndarray:
    """Indices d'un point par voxel : le premier vu (plus petit t), dans l'ordre des t croissants."""
    order = np.argsort(t, kind="stable")
    keys = np.floor(xyz[order] / voxel).astype(np.int64)
    _, first = np.unique(keys, axis=0, return_index=True)
    return order[np.sort(first)]


def nearest(times: np.ndarray, t: float) -> int:
    i = int(np.searchsorted(times, t))
    if i == 0:
        return 0
    if i == len(times):
        return len(times) - 1
    return i if times[i] - t < t - times[i - 1] else i - 1


def view_center(v: st.View) -> np.ndarray:
    w, x, y, z = v.qvec
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                  [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                  [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])
    return -R.T @ np.asarray(v.tvec), R


def build(session: Path, nsdata: Path, stride: int = 4, zmin: float = 0.3, zmax: float = 4.5, edge: float = 0.03,
          voxel: float = 0.025, max_points: int = 300_000, holdout_margin: float = 0.25, match_s: float = 0.06,
          seed: int = 0, log=print) -> dict:
    from PIL import Image
    views, cams = st.load_session(nsdata)
    recs = st.read_images(nsdata / "headset" / "sparse" / "0" / "images.txt")
    t0_us = min(st.ts_us(n) for n, *_ in recs)
    train = [v for v in views if v.split == "train"]
    test_t = np.array(sorted(v.t for v in views if v.split == "test"))
    all_t = np.array([v.t for v in views])
    centers = {v.name: view_center(v) for v in views}

    # cartes de profondeur, hold-out exclu
    frames = []
    for eye in ("left", "right"):
        for f in dl.load_frames(session, eye):
            tr = (f["ts"] * 1000 - t0_us) / 1e6
            if len(test_t) and np.min(np.abs(test_t - tr)) < holdout_margin:
                continue
            frames.append((tr, eye, f))
    frames.sort(key=lambda x: x[0])
    log(f"[sp7] {len(frames)} cartes après exclusion du hold-out (marge {holdout_margin} s)")

    # similitude Unity (Z inversé) -> repère du jeu commun, sur la trajectoire appariée dans le temps
    src, dst = [], []
    for tr, _, f in frames:
        j = nearest(all_t, tr)
        if abs(all_t[j] - tr) <= match_s:
            src.append(f["pos"] * np.array([1.0, 1.0, -1.0]))
            dst.append(centers[views[j].name][0])
    src, dst = np.array(src), np.array(dst)
    if len(src) < 10:
        raise ValueError(f"{len(src)} cartes appariées à une vue à {match_s} s près : horloges incohérentes ?")
    sv = np.linalg.svd(src - src.mean(0), compute_uv=False)
    if sv[1] < 0.05 * sv[0]:                                        # trajectoire quasi rectiligne : rotation indéterminée
        raise ValueError("trajectoire quasi rectiligne : l'alignement est indéterminé autour de son axe")
    s, R, tvec = umeyama(src, dst)
    res = np.linalg.norm(dst - (s * src @ R.T + tvec), axis=1)
    angle = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2))))
    align = {"pairs": len(src), "scale": s, "rotation_deg": angle, "translation_m": float(np.linalg.norm(tvec)),
             "residual_median_m": float(np.median(res)), "residual_p95_m": float(np.percentile(res, 95))}
    log(f"[sp7] alignement : {len(src)} paires, échelle {s:.4f}, rotation {angle:.2f}°, résidu médian "
        f"{100 * align['residual_median_m']:.1f} cm (p95 {100 * align['residual_p95_m']:.1f})")

    # rétroprojection, filtre des bords, couleur dans la vue d'entraînement la plus proche
    train_t = np.array([v.t for v in train])
    cache: OrderedDict[str, np.ndarray] = OrderedDict()

    def image(v: st.View) -> np.ndarray:
        if v.name not in cache:
            cache[v.name] = np.asarray(Image.open(nsdata / "images" / v.name).convert("RGB"))
            if len(cache) > 12:
                cache.popitem(last=False)
        return cache[v.name]

    xyz_l, rgb_l, t_l = [], [], []
    stats = {"pixels": 0, "edges": 0, "range": 0, "no_color": 0}
    for tr, eye, f in frames:
        d = dl.load_raw(session, eye, f)
        if d is None:
            continue
        z = dl.linearize(d, f["near"], f["far"])
        keep = edge_mask(z, edge)
        z_s = z[::stride, ::stride]
        k_s = keep[::stride, ::stride]
        in_range = (z_s >= zmin) & (z_s <= zmax)
        stats["pixels"] += z_s.size
        stats["edges"] += int((~k_s & np.isfinite(z_s)).sum())
        stats["range"] += int((~in_range & k_s).sum())
        zz = np.where(k_s & in_range, z_s, np.nan)
        K = dl.intrinsics(f["W"], f["H"], *f["tans"])
        K = {**K, "fx": K["fx"] / stride, "fy": K["fy"] / stride, "cx": K["cx"] / stride, "cy": K["cy"] / stride}
        p = dl.world_points(zz, K, f["pos"], f["rot"])
        p = p[np.isfinite(p).all(1)]
        if not len(p):
            continue
        p = s * p @ R.T + tvec                                         # repère du jeu commun
        v = train[nearest(train_t, tr)]
        c, Rw = centers[v.name]
        cam = cams[v.camera_id]
        pc = (p - c) @ Rw.T                                             # monde -> caméra (OpenCV)
        ok = pc[:, 2] > 0.05
        u = np.full(len(p), -1.0)
        w = np.full(len(p), -1.0)
        u[ok] = cam.fx * pc[ok, 0] / pc[ok, 2] + cam.cx
        w[ok] = cam.fy * pc[ok, 1] / pc[ok, 2] + cam.cy
        img = image(v)
        H, W = img.shape[:2]
        inb = ok & (u >= 0) & (u < W) & (w >= 0) & (w < H)
        stats["no_color"] += int((~inb).sum())
        xyz_l.append(p[inb])
        rgb_l.append(img[w[inb].astype(int), u[inb].astype(int)].astype(np.float32) / 255.0)
        t_l.append(np.full(int(inb.sum()), tr, dtype=np.float32))
    xyz, rgb, tt = np.concatenate(xyz_l), np.concatenate(rgb_l), np.concatenate(t_l)
    idx = first_per_voxel(xyz, tt, voxel)
    log(f"[sp7] {len(xyz)} points colorés, {len(idx)} après la grille de {100 * voxel:.1f} cm")
    if len(idx) > max_points:                                           # sous-échantillon, ordre du temps conservé
        rng = np.random.default_rng(seed)
        idx = np.sort(rng.choice(idx, max_points, replace=False))
        idx = idx[np.argsort(tt[idx], kind="stable")]
    return {"xyz": xyz[idx].astype(np.float32), "rgb": rgb[idx].astype(np.float32), "t": tt[idx].astype(np.float32),
            "voxel": voxel, "align": align, "stats": stats, "n_frames": len(frames),
            "trajectory": np.array([centers[v.name][0] for v in train])}


def write_ply(path: Path, xyz: np.ndarray, rgb: np.ndarray) -> None:
    n = len(xyz)
    rec = np.zeros(n, dtype=[("x", "<f4"), ("y", "<f4"), ("z", "<f4"), ("r", "u1"), ("g", "u1"), ("b", "u1")])
    rec["x"], rec["y"], rec["z"] = xyz.T
    c = np.clip(rgb * 255 + 0.5, 0, 255).astype(np.uint8)
    rec["r"], rec["g"], rec["b"] = c.T
    with path.open("wb") as fh:
        fh.write((f"ply\nformat binary_little_endian 1.0\nelement vertex {n}\nproperty float x\nproperty float y\n"
                  f"property float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\n"
                  f"end_header\n").encode())
        fh.write(rec.tobytes())


def plot(path: Path, xyz: np.ndarray, rgb: np.ndarray, traj: np.ndarray) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rng = np.random.default_rng(0)
    sel = rng.choice(len(xyz), min(len(xyz), 200_000), replace=False)
    P, C = xyz[sel], rgb[sel]
    # axe vertical : celui de plus faible étendue de la trajectoire (le casque reste à hauteur d'yeux)
    up = int(np.argmin(traj.max(0) - traj.min(0)))
    a, b = [k for k in range(3) if k != up]
    fig, axs = plt.subplots(1, 2, figsize=(14, 7))
    for ax, (i, j, title) in zip(axs, ((a, b, "vue de dessus"), (a, up, "vue de face"))):
        ax.scatter(P[:, i], P[:, j], s=0.05, c=C)
        ax.plot(traj[:, i], traj[:, j], "r-", lw=1, label="trajectoire (vues d'entraînement)")
        ax.set_aspect("equal")
        ax.set_title(f"{title} (axes {'xyz'[i]}, {'xyz'[j]})")
        if j == up:
            ax.invert_yaxis()                                           # repère OpenCV/COLMAP : y vers le bas
        ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", type=Path, required=True, help="session brute de QuestRealityCapture (S1)")
    ap.add_argument("--nsdata", type=Path, required=True, help="jeu commun de S1 (bench de SP-0)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--stride", type=int, default=4)
    ap.add_argument("--zmin", type=float, default=0.3)
    ap.add_argument("--zmax", type=float, default=4.5)
    ap.add_argument("--edge", type=float, default=0.03)
    ap.add_argument("--voxel", type=float, default=0.025)
    ap.add_argument("--max-points", type=int, default=300_000)
    ap.add_argument("--holdout-margin", type=float, default=0.25)
    a = ap.parse_args(argv)
    for s_ in (sys.stdout, sys.stderr):
        if hasattr(s_, "reconfigure"):
            s_.reconfigure(encoding="utf-8", errors="replace")
    a.out.mkdir(parents=True, exist_ok=True)
    r = build(a.session, a.nsdata, a.stride, a.zmin, a.zmax, a.edge, a.voxel, a.max_points, a.holdout_margin)
    np.savez(a.out / "init.npz", xyz=r["xyz"], rgb=r["rgb"], t=r["t"], voxel=np.float32(r["voxel"]))
    write_ply(a.out / "init.ply", r["xyz"], r["rgb"])
    try:
        plot(a.out / "init_views.png", r["xyz"], r["rgb"], r["trajectory"])
    except ImportError:
        print("[sp7] matplotlib absent : pas de init_views.png (le nuage init.ply s'ouvre dans CloudCompare ou MeshLab)")
    info = {"points": int(len(r["xyz"])), "frames": r["n_frames"], "align": r["align"], "stats": r["stats"],
            "args": {k: str(v) for k, v in vars(a).items()},
            "t_range_s": [float(r["t"].min()), float(r["t"].max())]}
    (a.out / "init.json").write_text(json.dumps(info, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[sp7] {info['points']} points -> {a.out / 'init.npz'}, init.ply, init_views.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
