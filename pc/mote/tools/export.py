"""`mote export` : du répertoire de dataset vers nerfstudio (transforms.json) et COLMAP (modèle texte).

Le dataset est en repère canonique (caméras OpenCV, `world_from_camera`). La conversion vers la caméra OpenGL de
nerfstudio n'a lieu qu'ici, à l'export (SPEC-64c5 §9.4). Les images ne sont pas copiées : les chemins pointent vers
celles du dataset.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from mote import geometry as g


def load_frames(dataset: Path) -> list[dict]:
    lines = (Path(dataset) / "frames.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def _distortion(fr: dict) -> dict:
    """Coefficients OPENCV de nerfstudio (k1 k2 p1 p2), nuls pour un sténopé."""
    d = list(fr.get("dist") or []) + [0.0] * 4
    if fr["model"] not in ("PINHOLE", "OPENCV"):
        raise ValueError(f"{fr['file']} : modèle {fr['model']} non exportable")
    return {"k1": d[0], "k2": d[1], "p1": d[2], "p2": d[3]}


def _rel(target: Path, start: Path) -> str:
    return Path(os.path.relpath(target, start)).as_posix()


def export_nerfstudio(dataset: Path, out: Path) -> Path:
    """Écrit `out/transforms.json`. Intrinsèques par image (les deux yeux diffèrent), modèle OPENCV."""
    dataset, out = Path(dataset).resolve(), Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    frames = []
    for fr in load_frames(dataset):
        frames.append({
            "file_path": _rel(dataset / fr["file"], out),
            "transform_matrix": g.canonical_to_opengl(fr["world_from_camera"]),
            "fl_x": fr["fx"], "fl_y": fr["fy"], "cx": fr["cx"], "cy": fr["cy"],
            "w": fr["width"], "h": fr["height"], **_distortion(fr),
        })
    path = out / "transforms.json"
    path.write_text(json.dumps({"camera_model": "OPENCV", "frames": frames}, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")
    return path


def export_colmap(dataset: Path, out: Path) -> Path:
    """Écrit `out/{cameras,images,points3D}.txt` : une caméra par œil et par intrinsèques, poses monde -> caméra (OpenCV),
    aucun point 3D. Les noms d'images sont relatifs à `<dataset>/images`."""
    dataset, out = Path(dataset), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    cams: dict[tuple, int] = {}
    cam_lines, img_lines = [], []
    for i, fr in enumerate(load_frames(dataset), start=1):
        d = _distortion(fr)
        pinhole = all(v == 0.0 for v in d.values())
        params = ((fr["fx"], fr["fy"], fr["cx"], fr["cy"]) if pinhole
                  else (fr["fx"], fr["fy"], fr["cx"], fr["cy"], d["k1"], d["k2"], d["p1"], d["p2"]))
        # une caméra par œil (deux capteurs physiques, même si leurs intrinsèques coïncident) et par intrinsèques
        key = (fr["camera"], "PINHOLE" if pinhole else "OPENCV", fr["width"], fr["height"], params)
        if key not in cams:
            cams[key] = len(cams) + 1
            cam_lines.append(" ".join([str(cams[key]), key[1], str(fr["width"]), str(fr["height"])]
                                      + [repr(float(p)) for p in params]))
        w2c = g.invert_rigid(fr["world_from_camera"])
        qx, qy, qz, qw = g.matrix_quat(w2c)
        name = fr["file"].removeprefix("images/")
        img_lines.append(" ".join([str(i)] + [repr(v) for v in (qw, qx, qy, qz, w2c[0][3], w2c[1][3], w2c[2][3])]
                                  + [str(cams[key]), name]))
        img_lines.append("")                                       # pas de points 2D
    head = "# mote export, modèle COLMAP texte (poses du casque, repère canonique)\n"
    (out / "cameras.txt").write_text(head + "# CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n"
                                     + "".join(line + "\n" for line in cam_lines), encoding="utf-8", newline="\n")
    (out / "images.txt").write_text(head + "# IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n"
                                    "# POINTS2D[] as (X, Y, POINT3D_ID)\n"
                                    + "".join(line + "\n" for line in img_lines), encoding="utf-8", newline="\n")
    (out / "points3D.txt").write_text(head + "# POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[]\n",
                                      encoding="utf-8", newline="\n")
    return out
