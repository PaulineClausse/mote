# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8"]
# ///
"""Test de bout en bout de analyze.py sur une session synthétique : uv run docs/spikes/sp3/test_analyze.py

Mur vu à 0,5, 1, 2 et 3 m (6 s immobile par palier, 2 s de déplacement entre deux), origine de la carte 5 cm
derrière la face avant du casque : l'analyse doit retrouver les quatre paliers, un décalage de 5 cm et une erreur
résiduelle nulle.
"""
from __future__ import annotations

import io
import math
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze  # noqa: E402
from test_depthlib import wall  # noqa: E402

HEADER = ("timestamp_ms,ovr_timestamp,create_pose_location_x,create_pose_location_y,create_pose_location_z,"
          "create_pose_rotation_x,create_pose_rotation_y,create_pose_rotation_z,create_pose_rotation_w,"
          "fov_left_angle_tangent,fov_right_angle_tangent,fov_top_angle_tangent,fov_down_angle_tangent,"
          "near_z,far_z,width,height")
TAPE = [0.5, 1.0, 2.0, 3.0]
OFFSET = 0.05


def fake_session(root: Path) -> Path:
    s = root / "20261014_100000"
    rows = {"left": [HEADER], "right": [HEADER]}
    timing = ["file,eye,width,height,export_cpu_ms,latency_ms,latency_frames,callback_ms"]
    # palier i : immobile de 8i à 8i + 6 s, puis 2 s de recul vers le palier suivant ; le mur est en z = 0 (Unity)
    k = 0
    for t in np.arange(0.0, 8 * len(TAPE) - 2, 0.1):
        i, r = int(t // 8), t % 8
        cur = TAPE[i] + OFFSET
        nxt = TAPE[min(i + 1, len(TAPE) - 1)] + OFFSET
        dist = cur if r < 6 else cur + (nxt - cur) * (r - 6) / 2
        ts = 1791367700000 + int(round(t * 1000))
        for eye in ("left", "right"):
            (s / f"{eye}_depth").mkdir(parents=True, exist_ok=True)
            wall(dist, W=32, H=32, tans=(1.0, 1.0, 1.0, 1.0)).tofile(s / f"{eye}_depth" / f"{ts}.raw")
            # caméra à z = -dist (Unity), regardant +Z vers le mur
            rows[eye].append(f"{ts},{1000 + t:.3f},0,1.6,{-dist},0,0,0,1,1,1,1,1,0.1,Infinity,32,32")
            timing.append(f"{ts}.raw,{eye},32,32,0.4,{20 + k % 5},2,0.{3 + k % 3}")
        k += 1
    for eye in rows:
        (s / f"{eye}_depth_descriptors.csv").write_text("\n".join(rows[eye]) + "\n", encoding="utf-8")
    (s / "depth_readback_timing.csv").write_text("\n".join(timing) + "\n", encoding="utf-8")
    return s


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        s = fake_session(Path(d))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analyze.main(["--wall", str(s), "--distances", *map(str, TAPE), "--scene", str(s),
                               "--out", str(Path(d) / "out"), "--max-frames", "20"])
        text = buf.getvalue()
        out = Path(d) / "out"
        assert rc == 0, text
        assert "| 32 x 32 |" in text and "| 10,0 |" in text, text                    # résolution, 10 Hz
        assert "Décalage constant (médiane de mesuré - mètre) : 5,0 cm" in text, text
        lines = [ln for ln in text.splitlines() if ln.startswith("| 0,50 |") or ln.startswith("| 1,00 |")
                 or ln.startswith("| 2,00 |") or ln.startswith("| 3,00 |")]
        assert len(lines) == 4, text
        for ln in lines:
            after = float(ln.split("|")[5].strip().replace(",", "."))
            assert abs(after) <= 0.2, ln                                              # ≤ 2 mm après décalage
        assert "relectures" in text and "médiane 1,20 ms" in text, text           # 0,4 + 2 x 0,4 ms par carte
        assert "sur 300, un pixel sur 2" in text and "z ≤ 5,0 m" in text, text
        for f in ("wall_series.png", "wall_frames.png", "scene_views.png", "scene_frame.png", "scene_depth.ply", "sp3_tables.md"):
            assert (out / f).exists(), f
    print("ok analyse de bout en bout, référence au mètre")

    # sans mètre : la référence est le recul mesuré par la pose ; la caméra recule de 0,5 m à 3 m, le décalage du
    # premier palier vaut 0,55 m et l'erreur résiduelle doit être nulle, la pente 1
    with tempfile.TemporaryDirectory() as d:
        s = fake_session(Path(d))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analyze.main(["--wall", str(s), "--out", str(Path(d) / "out")])
        text = buf.getvalue()
        assert rc == 0, text
        assert "référence : recul mesuré par le tracking" in text and "a = 1,000" in text, text
        assert "(médiane de mesuré - recul : 55,0 cm)" in text, text
        rows = [ln for ln in text.splitlines() if ln.startswith("| ") and "-" in ln.split("|")[1]
                and ln.split("|")[1].strip()[0].isdigit()]
        assert len(rows) == 4, text
        reculs = [float(ln.split("|")[2].strip().replace(",", ".")) for ln in rows]
        assert [round(x, 3) for x in reculs] == [0.0, 0.5, 1.5, 2.5], reculs
        for ln in rows:
            assert abs(float(ln.split("|")[6].strip().replace(",", "."))) <= 0.2, ln       # erreur ≤ 2 mm
    print("ok analyse de bout en bout, référence au tracking")
    return 0


if __name__ == "__main__":
    sys.exit(main())
