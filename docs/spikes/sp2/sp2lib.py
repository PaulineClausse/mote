"""SP-2 : lecture des sessions QuestRealityCapture, détection du damier, géométrie et estimateurs.

Conventions (SPEC-64c5 §9.4) :
- Unity : monde main gauche, Y haut ; caméra regardant +Z, Y haut. Poses MRUK et casque en Unity.
- Canonique (OpenCV) : monde main droite ; caméra X droite, Y bas, Z avant ; poses `world_from_camera`.
- Hypothèse de la spec : T_gl = S T_unity S (S = diag(1,1,-1)), puis caméra OpenGL vers OpenCV par diag(1,-1,-1).
  Soit T_cv = S T_unity D avec D = diag(1,-1,1) côté caméra. Les autres choix de D (de déterminant -1) et un
  retournement vertical des images sont les variantes que la mesure départage.

Temps : les images portent un horodatage Unix en µs ; `hmd_poses.csv` porte l'heure Unix en ms et l'horloge XR (s).
Les poses du casque sont replacées en secondes Unix par le décalage médian entre les deux horloges.
"""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

S = np.diag([1.0, 1.0, -1.0])
# Côté caméra : signes candidats, tous de déterminant -1 (passage main gauche -> main droite).
CAM_SIGNS = {
    "diag(1,-1,1)": np.diag([1.0, -1.0, 1.0]),     # hypothèse de la spec
    "diag(-1,1,1)": np.diag([-1.0, 1.0, 1.0]),
    "diag(1,1,-1)": np.diag([1.0, 1.0, -1.0]),
    "diag(-1,-1,-1)": np.diag([-1.0, -1.0, -1.0]),
}
SPEC_CANDIDATE = ("diag(1,-1,1)", False)


# ----------------------------------------------------------------------------------------------- rotations

def quat_to_mat(q) -> np.ndarray:
    x, y, z, w = np.asarray(q, dtype=float) / np.linalg.norm(q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def mat_to_quat(R) -> np.ndarray:
    m = np.asarray(R)
    t = np.trace(m)
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        q = [(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, 0.25 * s]
    else:
        i = int(np.argmax(np.diag(m)))
        j, k = (i + 1) % 3, (i + 2) % 3
        s = math.sqrt(1.0 + m[i, i] - m[j, j] - m[k, k]) * 2
        q = [0.0, 0.0, 0.0, (m[k, j] - m[j, k]) / s]
        q[i] = 0.25 * s
        q[j] = (m[j, i] + m[i, j]) / s
        q[k] = (m[k, i] + m[i, k]) / s
    q = np.array(q)
    return q / np.linalg.norm(q)


def log_rot(R) -> np.ndarray:
    """Vecteur de rotation (axe x angle, rad)."""
    c = (np.trace(R) - 1) / 2
    a = math.acos(max(-1.0, min(1.0, c)))
    if a < 1e-9:
        return np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / 2
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    return v * a / (2 * math.sin(a))


def exp_rot(v) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    a = np.linalg.norm(v)
    if a < 1e-12:
        return np.eye(3)
    k = v / a
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def angle_deg(R) -> float:
    return math.degrees(np.linalg.norm(log_rot(R)))


def mean_rotation(Rs) -> np.ndarray:
    """Moyenne chordale (projection de la somme sur SO(3))."""
    U, _, Vt = np.linalg.svd(np.sum(Rs, axis=0))
    R = U @ Vt
    if np.linalg.det(R) < 0:
        U[:, -1] *= -1
        R = U @ Vt
    return R


def unity_to_cv(pos, quat, cam_sign: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """world_from_camera canonique d'une pose Unity : R = S R_u D, t = S p."""
    return S @ quat_to_mat(quat) @ cam_sign, S @ np.asarray(pos, dtype=float)


# ----------------------------------------------------------------------------------------------- sessions

@dataclass
class Frame:
    eye: str
    file: str
    t: float                 # secondes Unix (horodatage de l'image)
    pos: np.ndarray          # pose MRUK, Unity
    quat: np.ndarray
    pose_ok: bool


@dataclass
class Camera:
    K: np.ndarray
    width: int
    height: int


def _rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _b(s: str) -> bool:
    return str(s).strip().lower() in ("true", "1")


def load_frames(session: Path, eye: str) -> list[Frame]:
    out = []
    for r in _rows(session / f"{eye}_camera_mruk_frame_metadata.csv"):
        out.append(Frame(
            eye=eye, file=r["file_name"], t=int(r["timestamp_us_realtime"]) * 1e-6,
            pos=np.array([float(r[f"pose_pos_{a}"]) for a in "xyz"]),
            quat=np.array([float(r[f"pose_rot_{a}"]) for a in "xyzw"]),
            pose_ok=_b(r.get("pose_ok", "true"))))
    return out


def load_camera(session: Path, eye: str) -> Camera:
    j = json.loads((session / f"{eye}_camera_mruk_intrinsics.json").read_text(encoding="utf-8"))
    fx, fy = j["focalLength"]["x"], j["focalLength"]["y"]
    cx, cy = j["principalPoint"]["x"], j["principalPoint"]["y"]
    w, h = j["resolution"]["width"], j["resolution"]["height"]
    return Camera(np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1.0]]), int(w), int(h))


@dataclass
class HmdTrack:
    """Poses du casque en secondes Unix (horloge XR recalée), rotations dans le monde canonique."""
    t: np.ndarray
    R: np.ndarray            # (n, 3, 3), S R_u S
    p: np.ndarray            # (n, 3), S p_u
    clock_offset: float      # ovr - unix (s), médiane
    clock_spread_ms: float

    @classmethod
    def load(cls, session: Path) -> "HmdTrack":
        rows = _rows(session / "hmd_poses.csv")
        unix = np.array([int(r["unix_time"]) for r in rows]) * 1e-3
        ovr = np.array([float(r["ovr_timestamp"]) for r in rows])
        off = ovr - unix
        c = float(np.median(off))
        t = ovr - c
        order = np.argsort(t, kind="stable")
        R = np.array([S @ quat_to_mat([float(r[f"rot_{a}"]) for a in "xyzw"]) @ S for r in rows])[order]
        p = np.array([S @ np.array([float(r[f"pos_{a}"]) for a in "xyz"]) for r in rows])[order]
        keep = np.concatenate([[True], np.diff(t[order]) > 0])
        return cls(t[order][keep], R[keep], p[keep], c, float(np.percentile(np.abs(off - c), 95) * 1e3))

    def rot_at(self, t: float) -> np.ndarray:
        i = int(np.clip(np.searchsorted(self.t, t), 1, len(self.t) - 1))
        a = (t - self.t[i - 1]) / (self.t[i] - self.t[i - 1])
        R0, R1 = self.R[i - 1], self.R[i]
        return R0 @ exp_rot(a * log_rot(R0.T @ R1))

    def omega(self, t: float, h: float = 0.01) -> np.ndarray:
        """Vitesse angulaire (rad/s) dans le monde, par différence centrée."""
        return log_rot(self.rot_at(t + h) @ self.rot_at(t - h).T) / (2 * h)

    def speed(self, t: float, h: float = 0.01) -> float:
        i0 = int(np.clip(np.searchsorted(self.t, t - h), 0, len(self.t) - 1))
        i1 = int(np.clip(np.searchsorted(self.t, t + h), 0, len(self.t) - 1))
        dt = self.t[i1] - self.t[i0]
        return float(np.linalg.norm(self.p[i1] - self.p[i0]) / dt) if dt > 0 else 0.0


# ----------------------------------------------------------------------------------------------- damier

def board_points(cols: int, rows: int, square_mm: float) -> np.ndarray:
    """Coins intérieurs dans le repère du damier (m), dans l'ordre de findChessboardCornersSB."""
    s = square_mm / 1000
    return np.array([[i * s, j * s, 0.0] for j in range(rows) for i in range(cols)])


def read_gray(path: Path, cam: Camera):
    import cv2
    raw = np.fromfile(path, dtype=np.uint8)
    if raw.size != cam.width * cam.height * 4:
        return None
    return cv2.cvtColor(raw.reshape(cam.height, cam.width, 4), cv2.COLOR_RGBA2GRAY)


def canonical_order(corners: np.ndarray, gray, cols: int) -> np.ndarray:
    """Le damier n'a qu'une orientation (une dimension paire, l'autre impaire), mais le détecteur peut numéroter
    ses coins dans un sens ou dans l'autre : on retourne la liste si la case extérieure au coin 0 est claire."""
    if gray is None:
        return corners
    c0, dx, dy = corners[0], corners[1] - corners[0], corners[cols] - corners[0]
    x, y = (c0 - (dx + dy) / 2).round().astype(int)
    if 0 <= y < gray.shape[0] and 0 <= x < gray.shape[1]:
        ref = float(np.median(gray))
        if gray[y, x] > ref:
            return corners[::-1].copy()
    return corners


def _detect_one(args):
    import cv2
    path, cam, pattern = args
    g = read_gray(Path(path), cam)
    if g is None:
        return Path(path).name, None
    ok, c = cv2.findChessboardCornersSB(g, pattern)
    if not ok:
        return Path(path).name, None
    c = canonical_order(c.reshape(-1, 2).astype(np.float64), g, pattern[0])
    return Path(path).name, c


def detect_session(session: Path, eye: str, cam: Camera, pattern: tuple[int, int], workers: int = 0) -> dict:
    """Coins détectés par image (nom de fichier -> (N, 2), coordonnées du fichier). Mis en cache dans la session."""
    cache = session / "sp2_cache" / f"corners_{eye}_{pattern[0]}x{pattern[1]}.npz"
    if cache.exists():
        z = np.load(cache)
        return {k: z[k] for k in z.files}
    files = sorted((session / f"{eye}_camera_mruk_rgba").glob("*.rgba"))
    jobs = [(str(p), cam, pattern) for p in files]
    if workers != 1 and len(jobs) > 8:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers or None) as ex:
            res = list(ex.map(_detect_one, jobs, chunksize=4))
    else:
        res = [_detect_one(j) for j in jobs]
    out = {name: c for name, c in res if c is not None}
    cache.parent.mkdir(exist_ok=True)
    np.savez_compressed(cache, **out)
    return out


def flip_v(corners: np.ndarray, cam: Camera) -> np.ndarray:
    c = corners.copy()
    c[:, 1] = cam.height - 1 - c[:, 1]
    return c


def pnp(obj: np.ndarray, img: np.ndarray, K: np.ndarray, dist=None):
    """camera_from_board (OpenCV) et erreur RMS de reprojection (px)."""
    import cv2
    ok, rvec, tvec = cv2.solvePnP(obj, img, K, dist, flags=cv2.SOLVEPNP_IPPE)
    if not ok:
        return None
    rvec, tvec = cv2.solvePnPRefineLM(obj, img, K, dist, rvec, tvec)
    proj, _ = cv2.projectPoints(obj, rvec, tvec, K, dist)
    rms = float(np.sqrt(np.mean(np.sum((proj.reshape(-1, 2) - img) ** 2, axis=1))))
    R, _ = cv2.Rodrigues(rvec)
    return R, tvec.reshape(3), rms


def project(obj, R_wb, t_wb, R_wc, t_wc, K) -> np.ndarray:
    Xw = obj @ R_wb.T + t_wb
    Xc = (Xw - t_wc) @ R_wc
    uv = Xc @ K.T
    return uv[:, :2] / uv[:, 2:3]


# ----------------------------------------------------------------------------------------------- mesures

@dataclass
class Obs:
    """Une image où le damier est détecté."""
    session: str
    eye: str
    file: str
    t: float
    R_cb: np.ndarray         # camera_from_board, mesuré par PnP
    t_cb: np.ndarray
    rms: float               # résidu PnP (px)
    corners: np.ndarray      # coins dans la convention de l'image testée
    frame: Frame
    omega: np.ndarray = field(default_factory=lambda: np.zeros(3))
    speed: float = 0.0
    radius: float = 0.0      # distance moyenne des coins au point principal (px)


def spread(Rs, ts) -> dict:
    Rm = mean_rotation(Rs)
    tm = np.median(ts, axis=0)
    da = np.array([angle_deg(R @ Rm.T) for R in Rs])
    dp = np.linalg.norm(np.asarray(ts) - tm, axis=1) * 1e3
    return {"R": Rm, "t": tm, "rot_med_deg": float(np.median(da)), "rot_p95_deg": float(np.percentile(da, 95)),
            "pos_med_mm": float(np.median(dp)), "pos_p95_mm": float(np.percentile(dp, 95))}


def world_board(obs: list[Obs], cam_sign: np.ndarray):
    Rs, ts = [], []
    for o in obs:
        R_wc, t_wc = unity_to_cv(o.frame.pos, o.frame.quat, cam_sign)
        Rs.append(R_wc @ o.R_cb)
        ts.append(R_wc @ o.t_cb + t_wc)
    return Rs, ts


def vision_camera(o: Obs, R_wb, t_wb):
    """world_from_camera déduit du damier (supposé fixe à R_wb, t_wb)."""
    R = R_wb @ o.R_cb.T
    return R, t_wb - R @ o.t_cb


def lag_from_rotation_errors(errs, omegas, min_omega: float, sign: float = 1.0, boot: int = 400, seed: int = 0):
    """Décalage τ (s) tel que err ≈ sign · ω τ, moindres carrés sur les images où |ω| >= min_omega, avec rejet des
    aberrants (3 MAD) et intervalle bootstrap à 95 %."""
    E, W = np.asarray(errs), np.asarray(omegas)
    m = np.linalg.norm(W, axis=1) >= min_omega
    E, W = E[m], W[m]
    if len(E) < 5:
        return None
    per = sign * np.sum(E * W, axis=1) / np.sum(W * W, axis=1)
    med = np.median(per)
    mad = np.median(np.abs(per - med)) * 1.4826 + 1e-6
    keep = np.abs(per - med) <= 3 * mad
    E, W = E[keep], W[keep]

    def fit(e, w):
        return sign * np.sum(e * w) / np.sum(w * w)

    tau = fit(E, W)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(boot):
        k = rng.integers(0, len(E), len(E))
        bs.append(fit(E[k], W[k]))
    resid = np.linalg.norm(E - sign * W * tau, axis=1)
    return {"tau_ms": tau * 1e3, "ci95_ms": (float(np.percentile(bs, 2.5) * 1e3), float(np.percentile(bs, 97.5) * 1e3)),
            "n": int(len(E)), "rejected": int((~keep).sum()),
            "resid_mrad_med": float(np.median(resid) * 1e3)}


def search_lag(fn, lo: float = -0.1, hi: float = 0.1, step: float = 0.0005):
    """Minimise fn(δ) sur une grille puis affine localement ; renvoie (δ, valeur)."""
    grid = np.arange(lo, hi + step / 2, step)
    vals = [fn(d) for d in grid]
    i = int(np.argmin(vals))
    best = grid[i]
    fine = np.arange(best - step, best + step, step / 20)
    fv = [fn(d) for d in fine]
    j = int(np.argmin(fv))
    return float(fine[j]), float(fv[j])
