"""SP-2 : vérification rapide d'une session QuestRealityCapture avant les vraies prises.

  uv run --no-project --with opencv-python-headless --with numpy python docs/spikes/sp2/check_session.py <session>

- fichiers présents et en-têtes des CSV (format des métadonnées, des poses et des paires stéréo) ;
- cadence des images par œil ;
- détection du damier (9 x 6 coins par défaut) sur un échantillon d'images ;
- pixels saturés sur le damier (surexposition ou reflet) et bandes (scintillement de l'écran) ;
- deux aperçus PNG avec les coins détectés, dans <session>/sp2_check/.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np


def rgba_files(session: Path, eye: str) -> list[Path]:
    d = session / f"{eye}_camera_mruk_rgba"
    return sorted(d.glob("*")) if d.exists() else []


def image_size(session: Path, eye: str) -> tuple[int, int]:
    p = session / f"{eye}_camera_mruk_intrinsics.json"
    if p.exists():
        j = json.loads(p.read_text(encoding="utf-8"))
        flat = json.dumps(j)
        for wk, hk in (("width", "height"), ("Width", "Height"), ("imageWidth", "imageHeight")):
            w, h = _find(j, wk), _find(j, hk)
            if w and h:
                return int(w), int(h)
        print(f"  (dimensions non trouvées dans {p.name} : {flat[:200]})")
    return 1280, 1280


def _find(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = _find(v, key)
            if r:
                return r
    if isinstance(obj, list):
        for v in obj:
            r = _find(v, key)
            if r:
                return r
    return None


def load_gray(path: Path, w: int, h: int) -> np.ndarray | None:
    raw = np.fromfile(path, dtype=np.uint8)
    if raw.size != w * h * 4:
        return None
    rgba = raw.reshape(h, w, 4)
    return cv2.cvtColor(rgba, cv2.COLOR_RGBA2GRAY)


def csv_head(path: Path, n: int = 2) -> list[str]:
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        rows = [r for _, r in zip(range(n + 1), csv.reader(f))]
    return [",".join(r) for r in rows]


def banding(gray: np.ndarray, corners: np.ndarray) -> float:
    """Écart-type (niveaux de gris) du profil vertical des cases blanches, après retrait de la tendance lente : des
    bandes de scintillement le font monter au-dessus de quelques niveaux."""
    x0, y0 = corners.min(axis=0).astype(int)
    x1, y1 = corners.max(axis=0).astype(int)
    roi = gray[max(y0, 0):y1, max(x0, 0):x1].astype(np.float32)
    if roi.size == 0:
        return float("nan")
    bright = np.where(roi >= np.percentile(roi, 60), roi, np.nan)
    prof = np.nanmean(bright, axis=1)
    prof = prof[~np.isnan(prof)]
    if len(prof) < 20:
        return float("nan")
    smooth = np.convolve(prof, np.ones(15) / 15, mode="same")
    return float(np.std((prof - smooth)[7:-7]))


def check_eye(session: Path, eye: str, pattern: tuple[int, int], samples: int, out: Path) -> None:
    files = rgba_files(session, eye)
    print(f"\n## {eye} : {len(files)} images")
    if not files:
        return
    w, h = image_size(session, eye)
    print(f"  dimensions : {w} x {h}, taille du premier fichier {files[0].stat().st_size} o")
    step = max(1, len(files) // samples)
    found, glare, bands = 0, [], []
    preview_done = False
    for p in files[::step]:
        g = load_gray(p, w, h)
        if g is None:
            print(f"  {p.name} : taille inattendue ({p.stat().st_size} o)")
            continue
        ok, c = cv2.findChessboardCornersSB(g, pattern)
        if not ok:
            continue
        found += 1
        c = c.reshape(-1, 2)
        x0, y0 = c.min(axis=0).astype(int)
        x1, y1 = c.max(axis=0).astype(int)
        roi = g[max(y0, 0):y1, max(x0, 0):x1]
        glare.append(float((roi >= 250).mean() * 100))
        bands.append(banding(g, c))
        if not preview_done:
            vis = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
            cv2.drawChessboardCorners(vis, pattern, c.reshape(-1, 1, 2), True)
            out.mkdir(exist_ok=True)
            cv2.imwrite(str(out / f"{eye}_{p.stem}.png"), vis)
            preview_done = True
    n = len(files[::step])
    print(f"  damier {pattern[0]} x {pattern[1]} détecté sur {found} / {n} images échantillonnées")
    if glare:
        print(f"  pixels saturés (>= 250) sur le damier : médiane {np.median(glare):.1f} %, max {max(glare):.1f} % "
              f"(cases blanches surexposées, ou reflet : à regarder sur les aperçus)")
        print(f"  bandes (écart-type du profil des cases blanches) : médiane {np.nanmedian(bands):.2f} niveaux "
              f"(au-delà de 3 : scintillement probable)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session", type=Path)
    ap.add_argument("--cols", type=int, default=9, help="coins intérieurs en largeur (défaut 9)")
    ap.add_argument("--rows", type=int, default=6, help="coins intérieurs en hauteur (défaut 6)")
    ap.add_argument("--samples", type=int, default=20, help="images vérifiées par œil (défaut 20)")
    a = ap.parse_args()
    s = a.session
    if not s.is_dir():
        print(f"{s} : dossier introuvable")
        return 2
    print(f"# Session {s.name}\n\nContenu :")
    for p in sorted(s.iterdir()):
        size = sum(f.stat().st_size for f in p.rglob("*")) if p.is_dir() else p.stat().st_size
        n = len(list(p.iterdir())) if p.is_dir() else ""
        print(f"  {p.name:45s} {size / 1e6:9.1f} Mo {n}")
    print("\nEn-têtes des CSV (deux premières lignes de données) :")
    for p in sorted(s.glob("*.csv")):
        print(f"  {p.name} :")
        for line in csv_head(p):
            print(f"    {line[:300]}")
    for p in sorted(s.glob("*.json")):
        print(f"  {p.name} : {p.read_text(encoding='utf-8', errors='replace')[:400]}")
    out = s / "sp2_check"
    for eye in ("left", "right"):
        check_eye(s, eye, (a.cols, a.rows), a.samples, out)
    print(f"\nAperçus : {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
