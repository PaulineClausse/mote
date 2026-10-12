#!/usr/bin/env python3
"""SP-6 : rejeu d'une session en flux, sans GPU ni torch (testable partout).

Outil de spike jetable, pas du code mote. Lit le jeu commun préparé par le bench de SP-0
(<work>/<session>/nsdata : headset/sparse/0/{cameras,images}.txt, images/, train_list.txt, test_list.txt),
range les vues dans l'ordre de capture d'après l'horodatage du nom (LEFT_<ts_us>.png), et décide :
  - quelles vues d'entraînement sont arrivées à un instant du flux ;
  - quelles vues de validation sont « déjà couvertes » (capturées depuis au moins `margin_s`) ;
  - quelle vue entraîner à l'itération suivante, selon la stratégie.
"""
from __future__ import annotations

import bisect
import math
import random
from dataclasses import dataclass, field
from pathlib import Path

STRATEGIES = ("uniform", "recent", "window")


@dataclass
class View:
    name: str
    t: float                 # secondes depuis la première image de la session
    camera_id: int
    qvec: tuple              # monde -> caméra, convention COLMAP (w, x, y, z)
    tvec: tuple
    split: str               # "train" ou "test"


@dataclass
class Camera:
    model: str
    width: int
    height: int
    fx: float
    fy: float
    cx: float
    cy: float


def ts_us(name: str) -> int:
    tail = Path(name).stem.split("_")[-1]
    if not tail.isdigit():
        raise ValueError(f"{name} : pas d'horodatage en fin de nom")
    return int(tail)


def read_cameras(path: Path) -> dict[int, Camera]:
    cams = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split()
        cid, model, w, h, prm = int(f[0]), f[1], int(f[2]), int(f[3]), [float(x) for x in f[4:]]
        if model == "PINHOLE":
            fx, fy, cx, cy = prm[:4]
        elif model in ("SIMPLE_PINHOLE", "SIMPLE_RADIAL"):
            fx = fy = prm[0]; cx, cy = prm[1:3]
        elif model in ("OPENCV", "RADIAL", "FULL_OPENCV"):
            fx, fy, cx, cy = prm[:4]           # distorsion ignorée : les images MRUK sont déjà rectifiées (SP-0 §4)
        else:
            raise ValueError(f"modèle de caméra non géré : {model}")
        cams[cid] = Camera(model, w, h, fx, fy, cx, cy)
    return cams


def read_images(path: Path) -> list[tuple]:
    """(nom, qvec, tvec, camera_id) ; images.txt alterne une ligne de pose et une ligne de points."""
    out = []
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if not ln.startswith("#")]
    i = 0
    while i < len(lines):
        f = lines[i].split()
        if len(f) >= 10:
            out.append((f[9], tuple(map(float, f[1:5])), tuple(map(float, f[5:8])), int(f[8])))
            i += 2
        else:
            i += 1
    return out


def load_session(nsdata: Path, poses: str = "headset/sparse/0") -> tuple[list[View], dict[int, Camera]]:
    cams = read_cameras(nsdata / poses / "cameras.txt")
    train = set((nsdata / "train_list.txt").read_text(encoding="utf-8").split())
    test = set((nsdata / "test_list.txt").read_text(encoding="utf-8").split())
    if train & test:
        raise ValueError(f"{len(train & test)} vues à la fois en train et en test")
    recs = read_images(nsdata / poses / "images.txt")
    t0 = min(ts_us(n) for n, *_ in recs)
    views = []
    for n, q, t, cid in recs:
        split = "train" if n in train else "test" if n in test else None
        if split:
            views.append(View(n, (ts_us(n) - t0) / 1e6, cid, q, t, split))
    views.sort(key=lambda v: (v.t, v.name))
    return views, cams


@dataclass
class Stream:
    """Arrivée des vues à leur cadence réelle. `speed` > 1 accélère le rejeu ; offline : tout est là à t = 0."""
    views: list[View]
    speed: float = 1.0
    offline: bool = False
    margin_s: float = 2.0
    train: list[View] = field(init=False)
    test: list[View] = field(init=False)

    def __post_init__(self):
        self.train = [v for v in self.views if v.split == "train"]
        self.test = [v for v in self.views if v.split == "test"]
        self._train_t = [v.t for v in self.train]

    @property
    def duration_s(self) -> float:
        return 0.0 if self.offline else max(v.t for v in self.views) / self.speed

    def session_time(self, stream_s: float) -> float:
        return math.inf if self.offline else stream_s * self.speed

    def n_arrived(self, stream_s: float) -> int:
        """Nombre de vues d'entraînement arrivées : ce sont les premières de self.train."""
        return bisect.bisect_right(self._train_t, self.session_time(stream_s))

    def covered_test(self, stream_s: float) -> list[int]:
        """Indices dans self.test des vues de validation capturées depuis au moins margin_s (zone déjà vue)."""
        st = self.session_time(stream_s)
        return [i for i, v in enumerate(self.test) if v.t + self.margin_s <= st]


class Sampler:
    """uniform : toutes les vues arrivées ; recent : p_recent du temps dans les `window_s` dernières secondes,
    le reste uniforme ; window : seulement les `window_s` dernières secondes (oublie le reste)."""

    def __init__(self, stream: Stream, strategy: str, seed: int = 0, window_s: float = 5.0, p_recent: float = 0.5):
        if strategy not in STRATEGIES:
            raise ValueError(f"stratégie inconnue {strategy!r}, attendu : {', '.join(STRATEGIES)}")
        self.s, self.strategy, self.window_s, self.p_recent = stream, strategy, window_s, p_recent
        self.rng = random.Random(seed)

    def pick(self, stream_s: float) -> int | None:
        n = self.s.n_arrived(stream_s)
        if n == 0:
            return None
        if self.strategy == "uniform" or self.s.offline:
            return self.rng.randrange(n)
        lo = bisect.bisect_left(self.s._train_t, self.s.session_time(stream_s) - self.window_s)
        lo = min(lo, n - 1)                       # au moins la dernière vue arrivée
        if self.strategy == "window" or self.rng.random() < self.p_recent:
            return self.rng.randrange(lo, n)
        return self.rng.randrange(n)


def first_reaching(curve: list[dict], level: float, min_views: int = 4) -> dict | None:
    """Premier point de la courbe où le PSNR atteint `level` sur au moins `min_views` vues couvertes."""
    return next((c for c in curve if c.get("psnr") is not None and c["n_test"] >= min_views
                 and c["psnr"] >= level), None)
