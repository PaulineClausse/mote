"""Tests de l'analyse SP-2 sur des sessions synthétiques, au format de QuestRealityCapture, dont la vérité est connue :
formule de conversion, décalages temporels et synchronisation gauche/droite.

  uv run --no-project --with opencv-python-headless --with numpy --with pytest python -m pytest -q docs/spikes/sp2
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze  # noqa: E402
import sp2lib as L  # noqa: E402

SQUARE = 23.0
COLS, ROWS = 9, 6
K = np.array([[868.7, 0, 641.7], [0, 868.7, 640.7], [0, 0, 1.0]])
T0 = 1792154091.0
OVR_OFFSET = 50722.0 - T0              # ovr = unix + OVR_OFFSET
D_SPEC = L.CAM_SIGNS["diag(1,-1,1)"]


STILL = [  # (lacet, tangage, roulis, x, y, z) : cinq positions immobiles de 1 s, comme la session B
    (0.05, -0.10, 0.00, 0.00, 0.00, 0.00),
    (0.30, -0.05, 0.10, -0.12, 0.02, 0.03),
    (-0.30, -0.15, -0.12, 0.12, -0.03, 0.02),
    (0.10, 0.10, 0.25, 0.03, 0.05, 0.12),
    (-0.10, -0.25, -0.20, -0.04, -0.05, -0.10),
]


def _pose(yaw, pitch, roll, x, y, z):
    R = L.exp_rot([0, yaw, 0]) @ L.exp_rot([pitch, 0, 0]) @ L.exp_rot([0, 0, roll])
    return R, np.array([x, y, z])


def head(t: float, t_start: float):
    """Tête dans le monde canonique : cinq positions immobiles d'une seconde (avec 0,3 s de transition), puis des
    lacets de plus en plus rapides et une petite translation."""
    u = t - t_start
    if u < 6.5:
        k = min(int(u // 1.3), len(STILL) - 1)
        w = u - k * 1.3
        if w < 1.0 or k == len(STILL) - 1:
            return _pose(*STILL[k])
        a = (w - 1.0) / 0.3
        p0, p1 = np.array(STILL[k]), np.array(STILL[k + 1])
        return _pose(*(p0 + a * (p1 - p0)))
    v = u - 6.5
    f = 0.25 + 0.08 * v               # fréquence croissante
    yaw = 0.05 + 0.25 * math.sin(2 * math.pi * f * v)
    pitch = -0.1 + 0.05 * math.sin(2 * math.pi * 0.3 * v)
    x = 0.05 * math.sin(2 * math.pi * 0.2 * v)
    return _pose(yaw, pitch, 0.0, x, 0.0, 0.0)


def write_session(root: Path, name: str, *, delta=-0.030, tau=0.004, stereo=0.002, flip=False, k1=0.0,
                  duration=16.0, fps=15.0, noise=0.15, seed=0, origin=(0.0, 0.0, 0.0), right_bias_deg=0.0):
    """`origin` (lacet, x, z) : monde propre à la session. QuestRealityCapture remet l'origine du suivi à zéro à chaque
    session : poses du casque et poses MRUK sont écrites dans ce monde-là, le damier ne bouge pas physiquement."""
    rng = np.random.default_rng(seed)
    s = root / name
    s.mkdir(parents=True)
    obj = L.board_points(COLS, ROWS, SQUARE)
    R_wb = np.eye(3)
    t_wb = np.array([-(COLS - 1) * SQUARE / 2000, -(ROWS - 1) * SQUARE / 2000, 0.55])
    X = {"left": (np.eye(3), np.array([-0.032, 0, 0])), "right": (np.eye(3), np.array([0.032, 0, 0]))}
    start = T0
    R_g = L.exp_rot([0, origin[0], 0])
    t_g = np.array([origin[1], 0.0, origin[2]])

    def cam_pose(eye, t):
        R_h, p_h = head(t, start)
        R_hc, t_hc = X[eye]
        return R_h @ R_hc, p_h + R_h @ t_hc

    # Poses du casque à 1 kHz, en Unity (S R S, S p).
    with (s / "hmd_poses.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unix_time", "ovr_timestamp", "pos_x", "pos_y", "pos_z", "rot_x", "rot_y", "rot_z", "rot_w"])
        for t in np.arange(start - 0.5, start + duration + 0.5, 0.001):
            R_h, p_h = head(t, start)
            R_h, p_h = R_g @ R_h, R_g @ p_h + t_g
            q = L.mat_to_quat(L.S @ R_h @ L.S)
            p = L.S @ p_h
            w.writerow([int(math.floor(t * 1000)), f"{t + OVR_OFFSET:.9f}", *p, *q])
    corners = {"left": {}, "right": {}}
    stamps = np.arange(start + 0.1, start + duration, 1 / fps)
    for eye in ("left", "right"):
        rows = []
        for k, ts in enumerate(stamps):
            name_ = f"{round(ts * 1e6)}.rgba"
            capture = ts + delta + (stereo if eye == "right" else 0.0)
            R_c, t_c = cam_pose(eye, capture)
            Xc = (obj @ R_wb.T + t_wb - t_c) @ R_c
            xn = Xc[:, :2] / Xc[:, 2:3]
            r2 = np.sum(xn ** 2, axis=1, keepdims=True)
            xn = xn * (1 + k1 * r2)
            uv = xn @ K[:2, :2].T + K[:2, 2] + rng.normal(0, noise, (len(obj), 2))
            if flip:
                uv[:, 1] = 1280 - 1 - uv[:, 1]
            if np.all((uv > 5) & (uv < 1275)):
                corners[eye][name_] = uv
            # Pose MRUK : celle de la caméra à l'instant capture + tau (l'œil droit à l'instant du gauche + tau).
            R_m, t_m = cam_pose(eye, ts + delta + tau)
            R_m, t_m = R_g @ R_m, R_g @ t_m + t_g
            if eye == "right" and right_bias_deg:
                # Extrinsèque MRUK de l'œil droit fausse d'un angle constant, autour de l'axe des lacets.
                R_m = R_m @ L.exp_rot([0, math.radians(right_bias_deg), 0])
            q_u = L.mat_to_quat(L.S @ R_m @ D_SPEC)
            p_u = L.S @ t_m
            rows.append([k + 1, name_, int(ts * 1e3), round(ts * 1e6), *p_u, *q_u, "true"])
        with (s / f"{eye}_camera_mruk_frame_metadata.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["frame_index", "file_name", "unix_time_ms", "timestamp_us_realtime", "pose_pos_x",
                        "pose_pos_y", "pose_pos_z", "pose_rot_x", "pose_rot_y", "pose_rot_z", "pose_rot_w", "pose_ok"])
            w.writerows(rows)
        (s / f"{eye}_camera_mruk_intrinsics.json").write_text(json.dumps({
            "focalLength": {"x": K[0, 0], "y": K[1, 1]}, "principalPoint": {"x": K[0, 2], "y": K[1, 2]},
            "resolution": {"width": 1280, "height": 1280}}), encoding="utf-8")
        (s / "sp2_cache").mkdir(exist_ok=True)
        np.savez_compressed(s / "sp2_cache" / f"corners_v2_{eye}_{COLS}x{ROWS}.npz", **corners[eye])
    with (s / "mruk_stereo_pairs.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pair_index", "time_delta_us"])
        w.writerows([[i, 0] for i in range(len(stamps))])
    return s


@pytest.fixture(scope="module")
def spec_result(tmp_path_factory):
    root = tmp_path_factory.mktemp("sp2")
    # Deux sessions, deux mondes : l'analyse doit situer le damier dans chacun.
    sessions = {"B": write_session(root, "B", seed=1, right_bias_deg=0.2),
                "D": write_session(root, "D", seed=2, origin=(0.8, 0.3, -0.2), right_bias_deg=0.2)}
    return analyze.analyze(sessions, SQUARE, COLS, ROWS, workers=1)[1]


def test_retrouve_la_formule_de_la_spec(spec_result):
    c = spec_result["conversion"]
    assert c["spec_hypothesis"] and c["cam_sign"] == "diag(1,-1,1)" and not c["image_flipped"]
    # Les images lentes qui choisissent la formule bougent un peu : environ 0,2 rad/s pendant ~34 ms de décalage.
    assert c["pos_p95_mm"] < 2.0 and c["rot_p95_deg"] < 0.5
    assert c["margin"] >= 3, "la formule suivante doit disperser nettement plus"
    assert spec_result["reprojection_px"]["left"]["static_p95"] < 1.0


def test_retrouve_le_decalage_pose_mruk(spec_result):
    assert spec_result["tau"]["left"]["tau_ms"] == pytest.approx(4.0, abs=1.0)


def test_biais_constant_de_l_oeil_droit_sans_effet_sur_tau(spec_result):
    # Pose MRUK de l'œil droit : instant du gauche + τ, image droite prise 2 ms après la gauche, d'où τ - 2 ms.
    r = spec_result["tau"]["right"]
    assert r["tau_ms"] == pytest.approx(2.0, abs=1.5)
    assert r["bias_mrad"] == pytest.approx(math.radians(0.2) * 1e3, abs=1.0)


def test_estimateur_separe_biais_et_retard():
    # Rotations toutes dans le même sens : un biais constant se confond avec un retard sans terme de biais.
    rng = np.random.default_rng(0)
    W = np.column_stack([np.zeros(50), rng.uniform(0.5, 2.0, 50), np.zeros(50)])
    b = np.array([0.0, 0.004, 0.0])
    E = b - W * 0.003
    sans = L.lag_from_rotation_errors(E, W, 0.3, sign=-1.0)
    avec = L.lag_from_rotation_errors(E, W, 0.3, sign=-1.0, intercept=True)
    assert abs(sans["tau_ms"] - 3.0) > 1.0
    assert avec["tau_ms"] == pytest.approx(3.0, abs=0.01)
    assert avec["bias_mrad"] == pytest.approx(4.0, abs=0.01)


def test_retrouve_l_instant_de_prise(spec_result):
    d = spec_result["delta"]["left"]
    assert d["image_ms"] == pytest.approx(-30.0, abs=1.5)
    assert d["mruk_pose_ms"] - d["image_ms"] == pytest.approx(4.0, abs=1.5)


def test_retrouve_la_desynchronisation_gauche_droite(spec_result):
    st = spec_result["stereo"]
    assert st["lag"]["tau_ms"] == pytest.approx(2.0, abs=1.0)
    assert st["baseline_vision_mm"] == pytest.approx(64.0, abs=1.0)


def test_sans_distorsion_k1_nul(spec_result):
    assert abs(spec_result["distortion"]["left"]["shift_px_r640"]) < 1.0


def test_reconnait_des_images_retournees(tmp_path):
    sessions = {"B": write_session(tmp_path, "B", flip=True, seed=3)}
    c = analyze.analyze(sessions, SQUARE, COLS, ROWS, workers=1)[1]["conversion"]
    assert c["image_flipped"] and not c["spec_hypothesis"]


def test_mesure_une_distorsion(tmp_path):
    sessions = {"B": write_session(tmp_path, "B", k1=-0.05, tau=0.0, seed=4)}
    d = analyze.analyze(sessions, SQUARE, COLS, ROWS, workers=1)[1]["distortion"]["left"]
    assert d["k1"] == pytest.approx(-0.05, abs=0.02)


def _board_image(cols_sq=10, rows_sq=7, px=60, at=(200, 300), size=(1280, 1280)):
    """Image d'un damier de cols_sq x rows_sq cases, case (0, 0) sombre, coin haut gauche en `at`."""
    img = np.full(size, 200, np.uint8)
    x0, y0 = at
    for r in range(rows_sq):
        for c in range(cols_sq):
            if (r + c) % 2 == 0:
                ya, yb = max(y0 + r * px, 0), max(y0 + (r + 1) * px, 0)
                xa, xb = max(x0 + c * px, 0), max(x0 + (c + 1) * px, 0)
                img[ya:yb, xa:xb] = 20      # les cases qui dépassent de l'image sont coupées
    return img


# Damier entier, collé au bord, puis coupé : la case de coin sort de l'image (cas de la session E).
@pytest.mark.parametrize("at", [(200, 300), (5, 5), (1280 - 10 * 60 - 3, 1280 - 7 * 60 - 3), (-40, -40), (-40, 300)])
def test_numerotation_des_coins_stable_par_rotation(at):
    """Le même coin physique doit porter le même numéro, l'image tournée de 180° ou non, damier au bord compris."""
    import cv2
    img = _board_image(at=at)
    rot = img[::-1, ::-1].copy()
    ok1, c1 = cv2.findChessboardCornersSB(img, (COLS, ROWS))
    ok2, c2 = cv2.findChessboardCornersSB(rot, (COLS, ROWS))
    assert ok1 and ok2
    c1 = L.canonical_order(c1.reshape(-1, 2).astype(float), img, COLS)
    c2 = L.canonical_order(c2.reshape(-1, 2).astype(float), rot, COLS)
    back = np.column_stack([1280 - 1 - c2[:, 0], 1280 - 1 - c2[:, 1]])
    assert np.abs(back - c1).max() < 1.0
