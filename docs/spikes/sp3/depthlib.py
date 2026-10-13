"""SP-3 : lecture et géométrie des cartes de profondeur enregistrées par QuestRealityCapture v1.5.0 (SRC-1). numpy seul.

Format (lu dans le code de SRC-1 v1.5.0, commit 649c012) :
- `<oeil>_depth/<timestamp_ms>.raw` : float32 little-endian sans en-tête, largeur x hauteur, ligne 0 = haut de l'image.
  Valeurs brutes non linéaires du tampon de profondeur, dans ]0, 1[ (0 et 1 : pas de mesure).
- `<oeil>_depth_descriptors.csv` : timestamp_ms (Unix estimé), ovr_timestamp (s, base XrTime), create_pose_location_*,
  create_pose_rotation_* (x, y, z, w ; repère Unity : main gauche, Y haut, avant +Z), fov_*_angle_tangent (tangentes
  positives), near_z, far_z (peut être infini), width, height.

Linéarisation (hypothèse de SPEC-64c5 §9.5, formule de SRC-3) : ndc = 2d - 1 ; projection OpenGL ; far infini donne
z = near / (1 - d). z est la distance le long de l'axe de visée, pas le long du rayon.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np


def parse_float(s: str) -> float:
    s = s.strip()
    if s in ("Infinity", "∞", "+∞", "inf", "+inf"):
        return math.inf
    if s in ("-Infinity", "-∞", "-inf"):
        return -math.inf
    return float(s.replace(",", "."))


def load_frames(session: Path, eye: str) -> list[dict]:
    path = Path(session) / f"{eye}_depth_descriptors.csv"
    frames = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r = {k.strip(): v for k, v in r.items()}
            g = lambda k: parse_float(r[k])  # noqa: E731
            frames.append({
                "ts": int(round(g("timestamp_ms"))), "t": g("ovr_timestamp"),
                "pos": np.array([g(f"create_pose_location_{a}") for a in "xyz"]),
                "rot": np.array([g(f"create_pose_rotation_{a}") for a in "xyzw"]),
                "tans": tuple(g(f"fov_{a}_angle_tangent") for a in ("left", "right", "top", "down")),
                "near": g("near_z"), "far": g("far_z"), "W": int(g("width")), "H": int(g("height")),
            })
    frames.sort(key=lambda fr: fr["t"])
    return frames


def load_raw(session: Path, eye: str, fr: dict) -> np.ndarray | None:
    p = Path(session) / f"{eye}_depth" / f"{fr['ts']}.raw"
    if not p.exists() or p.stat().st_size != 4 * fr["W"] * fr["H"]:
        return None
    return np.fromfile(p, dtype="<f4").reshape(fr["H"], fr["W"])


def linearize(d: np.ndarray, near: float, far: float) -> np.ndarray:
    """Distance le long de l'axe de visée (m). NaN hors de ]0, 1[."""
    d = np.asarray(d, dtype=np.float64)
    ndc = 2.0 * d - 1.0
    if math.isinf(far) or far < near:
        x, y = -2.0 * near, -1.0
    else:
        x, y = -2.0 * far * near / (far - near), -(far + near) / (far - near)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = x / (ndc + y)
    ok = (d > 0.0) & (d < 1.0) & np.isfinite(z) & (z > 0)
    return np.where(ok, z, np.nan)


def intrinsics(W: int, H: int, left: float, right: float, top: float, down: float) -> dict:
    """Sténopé à partir des tangentes : le bord gauche regarde à x/z = -left, le haut à y/z = -top (y vers le bas).
    SRC-3 prend cx = W * right / (left + right) ; identique si le champ est symétrique."""
    return {"fx": W / (left + right), "cx": W * left / (left + right),
            "fy": H / (top + down), "cy": H * top / (top + down), "W": W, "H": H}


def camera_points(z: np.ndarray, K: dict) -> np.ndarray:
    """Points dans le repère OpenCV de la caméra (x droite, y bas, z avant), un par pixel, ligne par ligne."""
    H, W = z.shape
    u, v = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
    return np.stack([(u - K["cx"]) / K["fx"] * z, (v - K["cy"]) / K["fy"] * z, z], -1).reshape(-1, 3)


def quat_matrix(q: np.ndarray) -> np.ndarray:
    x, y, zq, w = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + zq * zq), 2 * (x * y - zq * w), 2 * (x * zq + y * w)],
                     [2 * (x * y + zq * w), 1 - 2 * (x * x + zq * zq), 2 * (y * zq - x * w)],
                     [2 * (x * zq - y * w), 2 * (y * zq + x * w), 1 - 2 * (x * x + y * y)]])


def world_points(z: np.ndarray, K: dict, pos: np.ndarray, rot_xyzw: np.ndarray) -> np.ndarray:
    """Points monde en main droite (monde Unity, Z inversé), à partir de la pose de création Unity de la carte."""
    pc = camera_points(z, K) * np.array([1.0, -1.0, 1.0])          # OpenCV -> caméra Unity (y haut)
    pw = pc @ quat_matrix(rot_xyzw).T + pos                         # monde Unity
    return pw * np.array([1.0, 1.0, -1.0])                          # monde main droite


def wall_measure(d: np.ndarray, near: float, far: float, tans: tuple, crop: float = 0.4, iters: int = 6) -> dict:
    """Plan ajusté sur la zone centrale (fraction `crop` de chaque dimension) : distance perpendiculaire de la caméra
    au plan, inclinaison du plan par rapport à l'axe de visée, résidu RMS, fraction de pixels valides et d'inliers."""
    H, W = d.shape
    h0, w0 = int(H * (1 - crop) / 2), int(W * (1 - crop) / 2)
    K = intrinsics(W, H, *tans)
    z = np.full(d.shape, np.nan)
    z[h0:H - h0, w0:W - w0] = linearize(d[h0:H - h0, w0:W - w0], near, far)
    n_crop = (H - 2 * h0) * (W - 2 * w0)
    p = camera_points(z, K)
    p = p[np.isfinite(p).all(1)]
    out = {"valid": len(p) / n_crop, "inliers": 0.0, "dist": math.nan, "tilt_deg": math.nan, "rms": math.nan,
           "z_median": float(np.median(p[:, 2])) if len(p) else math.nan}
    if len(p) < 30:
        return out
    keep = np.ones(len(p), bool)
    for _ in range(iters):
        c = p[keep].mean(0)
        n = np.linalg.svd(p[keep] - c, full_matrices=False)[2][2]
        r = (p - c) @ n
        mad = np.median(np.abs(r[keep] - np.median(r[keep]))) * 1.4826
        keep = np.abs(r) < max(3.0 * mad, 0.002)
        if keep.sum() < 30:
            return out
    c = p[keep].mean(0)
    n = np.linalg.svd(p[keep] - c, full_matrices=False)[2][2]
    out.update(inliers=keep.sum() / n_crop, dist=float(abs(c @ n)),
               tilt_deg=float(math.degrees(math.acos(min(1.0, abs(n[2]))))),
               rms=float(np.sqrt(np.mean(((p[keep] - c) @ n) ** 2))))
    return out


def stationary_segments(t: np.ndarray, pos: np.ndarray, max_speed: float = 0.05, min_s: float = 3.0,
                        half_window_s: float = 0.25) -> list[tuple[float, float]]:
    """Intervalles où la tête bouge à moins de `max_speed` m/s, mesurée sur ±half_window_s, d'au moins `min_s`."""
    t = np.asarray(t, float)
    a = np.stack([np.interp(t - half_window_s, t, pos[:, k]) for k in range(3)], 1)
    b = np.stack([np.interp(t + half_window_s, t, pos[:, k]) for k in range(3)], 1)
    still = np.linalg.norm(b - a, axis=1) / (2 * half_window_s) < max_speed
    segs, start = [], None
    for i, s in enumerate(still):
        if s and start is None:
            start = i
        if (not s or i == len(still) - 1) and start is not None:
            end = i if s else i - 1
            if t[end] - t[start] >= min_s:
                segs.append((float(t[start]), float(t[end])))
            start = None
    return segs
