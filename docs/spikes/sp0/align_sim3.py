#!/usr/bin/env python3
"""Alignement Sim(3) de deux jeux de poses caméra et erreurs de tracking (SP-0, REF).

Outil de spike jetable, pas du code mote. Dépend de numpy seulement.

Entrées : deux jeux de poses caméra-vers-monde (c2w) appariés par nom d'image.
  --est : poses à évaluer (casque, export SRC-3)
  --ref : poses de référence (REF, COLMAP mapper)
Formats lus, détectés à l'extension :
  *.txt  modèle texte COLMAP `images.txt` (qvec/tvec = monde vers caméra, convertis ici en c2w)
  *.json transforms.json nerfstudio (transform_matrix = c2w, file_path = nom)

Sortie : JSON (stdout, ou --out) avec
  scale, rotation_deg_align, translation_align
  translation_error_m  : rmse, mean, median, max (centres de caméra, après alignement, en unités de REF)
  rotation_error_deg   : rmse, mean, median, max (angle de R_ref^T R_aligned_est)
  drift                : RMSE de translation par tiers de la trajectoire (ordre temporel = ordre du nom)
                         et pente de l'erreur le long du chemin parcouru (m par m)
Si REF est à une échelle arbitraire (COLMAP), l'erreur de translation est en unités de REF ;
passer --ref-scale-m <mètres par unité REF> si l'échelle est connue, sinon utiliser le facteur
`scale` (le casque est métrique : scale ≈ 1/(taille d'unité REF en mètres)).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np


# ----------------------------------------------------------------- quaternions / rotations

def quat_to_rot(q) -> np.ndarray:
    """Quaternion (w, x, y, z) -> matrice 3x3."""
    w, x, y, z = np.asarray(q, dtype=float) / np.linalg.norm(q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def axis_angle_to_rot(axis, angle_rad: float) -> np.ndarray:
    a = np.asarray(axis, dtype=float)
    a = a / np.linalg.norm(a)
    k = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(angle_rad) * k + (1 - math.cos(angle_rad)) * (k @ k)


def rot_angle_deg(r: np.ndarray) -> float:
    """Angle (degrés) d'une rotation, robuste près de 0 et de pi."""
    c = (np.trace(r) - 1.0) / 2.0
    s = np.linalg.norm(np.array([r[2, 1] - r[1, 2], r[0, 2] - r[2, 0], r[1, 0] - r[0, 1]])) / 2.0
    return math.degrees(math.atan2(s, c))


# ----------------------------------------------------------------- Umeyama

def umeyama_sim3(src: np.ndarray, dst: np.ndarray, with_scale: bool = True):
    """Sim(3) (s, R, t) minimisant sum ||dst_i - (s R src_i + t)||^2. src, dst : (N, 3).

    Umeyama 1991. Impose det(R) = +1 (pas de réflexion) : si les deux repères n'ont pas la
    même chiralité (Unity est main gauche, COLMAP main droite), l'alignement sera mauvais et
    le résidu le dira ; convertir le repère en amont, ne pas autoriser la réflexion ici.
    """
    n = src.shape[0]
    if n < 3:
        raise ValueError("au moins 3 points non alignés requis")
    mu_s, mu_d = src.mean(0), dst.mean(0)
    xs, xd = src - mu_s, dst - mu_d
    cov = xd.T @ xs / n
    u, d, vt = np.linalg.svd(cov)
    sign = np.eye(3)
    if np.linalg.det(u) * np.linalg.det(vt) < 0:
        sign[2, 2] = -1.0
    r = u @ sign @ vt
    var_s = (xs ** 2).sum() / n
    s = float(np.trace(np.diag(d) @ sign) / var_s) if with_scale else 1.0
    t = mu_d - s * r @ mu_s
    return s, r, t


# ----------------------------------------------------------------- erreurs

def align_and_score(est_c2w: np.ndarray, ref_c2w: np.ndarray, with_scale: bool = True) -> dict:
    """est_c2w, ref_c2w : (N, 4, 4), déjà appariées et dans l'ordre temporel."""
    n = est_c2w.shape[0]
    est_c, ref_c = est_c2w[:, :3, 3], ref_c2w[:, :3, 3]
    s, r, t = umeyama_sim3(est_c, ref_c, with_scale)

    aligned_c = (s * (r @ est_c.T)).T + t
    terr = np.linalg.norm(aligned_c - ref_c, axis=1)
    rerr = np.array([
        rot_angle_deg(ref_c2w[i, :3, :3].T @ (r @ est_c2w[i, :3, :3])) for i in range(n)
    ])

    # dérive : erreur par tiers temporel, et pente erreur / chemin parcouru (REF)
    path = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ref_c, axis=0), axis=1))])
    thirds = [terr[a:b] for a, b in zip(
        [0, n // 3, 2 * n // 3], [n // 3, 2 * n // 3, n])]
    if path[-1] > 0 and n >= 3:
        slope = float(np.polyfit(path, terr, 1)[0])
    else:
        slope = float("nan")

    def stats(x):
        return {"rmse": float(np.sqrt(np.mean(x ** 2))), "mean": float(x.mean()),
                "median": float(np.median(x)), "max": float(x.max())}

    return {
        "n_poses": int(n),
        "scale": float(s),
        "rotation_deg_align": rot_angle_deg(r),
        "translation_align": t.tolist(),
        "translation_error": stats(terr),
        "rotation_error_deg": stats(rerr),
        "drift": {
            "translation_rmse_by_third": [float(np.sqrt(np.mean(x ** 2))) for x in thirds],
            "error_slope_per_path_unit": slope,
            "path_length_ref": float(path[-1]),
        },
    }


# ----------------------------------------------------------------- lecture des poses

def _read_colmap_images_txt(path: Path) -> dict[str, np.ndarray]:
    poses: dict[str, np.ndarray] = {}
    # 2 lignes par image (pose+nom, puis points 2D, éventuellement vide) : on lit par parité,
    # donc les lignes vides sont conservées ; seuls les commentaires sont retirés.
    lines = [l for l in path.read_text().splitlines() if not l.startswith("#")]
    for head in lines[0::2]:
        f = head.split()
        if len(f) < 10:
            continue
        qw, qx, qy, qz, tx, ty, tz = map(float, f[1:8])
        r_wc = quat_to_rot((qw, qx, qy, qz))
        c2w = np.eye(4)
        c2w[:3, :3] = r_wc.T
        c2w[:3, 3] = -r_wc.T @ np.array([tx, ty, tz])
        poses[Path(f[9]).name] = c2w
    return poses


def _read_transforms_json(path: Path) -> dict[str, np.ndarray]:
    data = json.loads(path.read_text())
    return {Path(fr["file_path"]).name: np.array(fr["transform_matrix"], dtype=float)
            for fr in data["frames"]}


def read_poses(path: Path) -> dict[str, np.ndarray]:
    if path.suffix == ".json":
        return _read_transforms_json(path)
    return _read_colmap_images_txt(path)


def match(est: dict, ref: dict):
    names = sorted(set(est) & set(ref))
    if len(names) < 3:
        raise SystemExit(f"seulement {len(names)} noms d'image en commun entre est ({len(est)}) "
                         f"et ref ({len(ref)}) : vérifier que COLMAP n'a pas renommé les images")
    return names, np.stack([est[n] for n in names]), np.stack([ref[n] for n in names])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--est", required=True, type=Path)
    ap.add_argument("--ref", required=True, type=Path)
    ap.add_argument("--no-scale", action="store_true", help="SE(3) au lieu de Sim(3)")
    ap.add_argument("--ref-scale-m", type=float, default=None,
                    help="mètres par unité REF, pour convertir l'erreur de translation en mètres")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)

    names, est, ref = match(read_poses(a.est), read_poses(a.ref))
    res = align_and_score(est, ref, with_scale=not a.no_scale)
    res["n_est_total"], res["names_first_last"] = len(read_poses(a.est)), [names[0], names[-1]]
    if a.ref_scale_m:
        res["translation_error_m"] = {k: v * a.ref_scale_m for k, v in res["translation_error"].items()}
    txt = json.dumps(res, indent=2)
    if a.out:
        a.out.write_text(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
