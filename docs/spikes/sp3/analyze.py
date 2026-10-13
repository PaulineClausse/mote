# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8"]
# ///
"""SP-3 : analyse des sessions QuestRealityCapture pour la profondeur du Quest 3S. Affiche les tableaux à coller dans
SP-3.md, écrit les figures et le nuage rétroprojeté dans --out.

  uv run docs/spikes/sp3/analyze.py --wall <session du mur> --distances 0.5 1 2 3 \
      [--scene <session S1>] [--out <dossier>] [--segments 12.0-18.5,25-31,...]

- Résolution, cadence, format des valeurs : lus dans la session du mur (profondeur à pleine cadence).
- Relecture GPU vers CPU : depth_readback_timing.csv écrit par l'APK instrumenté (build_qrc.ps1).
- Mur : paliers immobiles détectés sur la pose de la carte, un par distance mesurée au mètre, dans l'ordre ; plan
  ajusté au centre de chaque carte, distance perpendiculaire caméra-mur comparée au mètre ruban.
- Scène (S1) : rétroprojection de toutes les cartes dans le monde (nuage PLY et vues PNG).
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics as stats
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import depthlib as dl  # noqa: E402


def say(m: str) -> None:
    print(f"[sp3] {m}", file=sys.stderr, flush=True)


def pct(xs, q):
    return float(np.percentile(np.asarray(xs, float), q)) if len(xs) else math.nan


def f2(x, nd=2):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}".replace(".", ",")


# ------------------------------------------------------------------------------------------------ format et cadence
def format_section(session: Path) -> list[str]:
    out = ["### Résolution, cadence et valeurs (lues à l'exécution)", ""]
    out += ["| Œil | Cartes | Résolution | Cadence médiane (Hz) | Intervalle médian / p95 (ms) | near_z | far_z |",
            "|---|---|---|---|---|---|---|"]
    raws = []
    for eye in ("left", "right"):
        fr = dl.load_frames(session, eye)
        if not fr:
            continue
        dt = np.diff([f["t"] for f in fr]) * 1000
        res = sorted({(f["W"], f["H"]) for f in fr})
        near = sorted({f["near"] for f in fr})
        far = sorted({f["far"] for f in fr})
        out.append(f"| {eye} | {len(fr)} | {', '.join(f'{w} x {h}' for w, h in res)} | "
                   f"{f2(1000 / np.median(dt), 1)} | {f2(np.median(dt), 1)} / {f2(pct(dt, 95), 1)} | "
                   f"{', '.join(f2(x, 3) for x in near[:3])} | {', '.join('infini' if math.isinf(x) else f2(x, 1) for x in far[:3])} |")
        if eye == "left":
            for f in fr[:: max(1, len(fr) // 20)]:
                d = dl.load_raw(session, eye, f)
                if d is not None:
                    raws.append(d)
    if raws:
        valid = [float(((d > 0) & (d < 1)).mean()) for d in raws]
        distinct = [len(np.unique(d[(d > 0) & (d < 1)])) for d in raws]
        steps = []
        for d in raws:
            u = np.unique(d[(d > 0) & (d < 1)])
            if len(u) > 1:
                steps.append(float(np.min(np.diff(u))))
        out += ["", f"Valeurs brutes, sur {len(raws)} cartes : pixels valides (dans ]0, 1[) {f2(100 * np.median(valid), 1)} % "
                f"en médiane ; {int(np.median(distinct))} valeurs distinctes par carte en médiane ; plus petit écart "
                f"entre deux valeurs {min(steps):.3g} (un format 16 bits normalisé donnerait des multiples de 1/65535 "
                f"≈ 1,5e-5)." if steps else ""]
    return out + [""]


# ------------------------------------------------------------------------------------------------ relecture
def timing_section(session: Path) -> list[str]:
    p = session / "depth_readback_timing.csv"
    out = ["### Relecture GPU vers CPU (APK instrumenté)", ""]
    if not p.exists():
        return out + [f"Pas de `{p.name}` dans {session} : la session n'a pas été enregistrée avec l'APK SP3.", ""]
    rows = list(csv.DictReader(p.open(newline="", encoding="utf-8")))
    col = lambda k: [float(r[k]) for r in rows]  # noqa: E731
    out += [f"{len(rows)} relectures (une par œil et par carte), {rows[0]['width']} x {rows[0]['height']} float32.", "",
            "| Mesure | médiane | p95 | max |", "|---|---|---|---|"]
    names = {"export_cpu_ms": "thread principal, Export (dispatch + 2 requêtes), ms",
             "latency_ms": "latence requête → callback, ms", "latency_frames": "latence requête → callback, frames",
             "callback_ms": "thread principal, callback (GetData + copie), ms"}
    for k, label in names.items():
        xs = col(k)
        out.append(f"| {label} | {f2(stats.median(xs))} | {f2(pct(xs, 95))} | {f2(max(xs))} |")
    by_file: dict[str, float] = {}
    for r in rows:
        by_file[r["file"]] = by_file.get(r["file"], 0.0) + float(r["callback_ms"])
    per_map = [by_file[k] + float(next(r["export_cpu_ms"] for r in rows if r["file"] == k)) for k in by_file]
    out += ["", f"Coût total sur le thread principal par carte (Export + deux callbacks) : médiane {f2(stats.median(per_map))} ms, "
            f"p95 {f2(pct(per_map, 95))} ms.", ""]
    return out


# ------------------------------------------------------------------------------------------------ mur
def wall_section(session: Path, distances: list[float], manual: list[tuple[float, float]] | None, out_dir: Path,
                 crop: float) -> list[str]:
    out = ["### Mur à distances mesurées", ""]
    per_eye = {}
    for eye in ("left", "right"):
        fr = dl.load_frames(session, eye)
        ms = []
        for f in fr:
            d = dl.load_raw(session, eye, f)
            ms.append(dl.wall_measure(d, f["near"], f["far"], f["tans"], crop=crop) if d is not None else None)
        per_eye[eye] = (fr, ms)
    fr, _ = per_eye["left"]
    t = np.array([f["t"] for f in fr])
    pos = np.stack([f["pos"] for f in fr])
    segs = manual or dl.stationary_segments(t, pos, max_speed=0.05, min_s=3.0)
    t0 = t[0]
    if len(segs) != len(distances):
        out += [f"**{len(segs)} paliers immobiles détectés pour {len(distances)} distances** : relancer avec "
                f"`--segments` (secondes depuis le début de la session) en choisissant dans cette liste.", "",
                "| Palier | début (s) | fin (s) | distance plan, médiane (m) |", "|---|---|---|---|"]
        for i, (a, b) in enumerate(segs):
            sel = [m["dist"] for m, tt in zip(per_eye["left"][1], t) if m and a <= tt <= b]
            out.append(f"| {i} | {f2(a - t0, 1)} | {f2(b - t0, 1)} | {f2(stats.median(sel)) if sel else '-'} |")
        _wall_plot(t, per_eye, segs, distances, out_dir)
        return out + [""]

    rows = []
    for (a, b), tape in zip(segs, distances):
        a, b = a + 0.5, b - 0.5                                     # marges : début et fin de palier
        r = {"tape": tape, "a": a - t0, "b": b - t0}
        for eye, (fr_e, ms) in per_eye.items():
            sel = [m for m, f in zip(ms, fr_e) if m and a <= f["t"] <= b and not math.isnan(m["dist"])]
            r[eye] = {
                "n": len(sel),
                "dist": stats.median([m["dist"] for m in sel]) if sel else math.nan,
                "std": stats.pstdev([m["dist"] for m in sel]) if len(sel) > 1 else math.nan,
                "rms": stats.median([m["rms"] for m in sel]) if sel else math.nan,
                "valid": stats.median([m["valid"] for m in sel]) if sel else math.nan,
                "tilt": stats.median([m["tilt_deg"] for m in sel]) if sel else math.nan,
                "zmed": stats.median([m["z_median"] for m in sel]) if sel else math.nan,
            }
        rows.append(r)
    meas = np.array([r["left"]["dist"] for r in rows])
    tape = np.array(distances)
    offset = float(np.median(meas - tape))
    slope, icpt = np.polyfit(tape, meas, 1) if len(tape) >= 2 else (math.nan, math.nan)
    out += [f"Zone centrale de {int(crop * 100)} % de la carte en largeur et en hauteur, plan ajusté par moindres "
            f"carrés avec rejet itératif (3 MAD) ; distance perpendiculaire de l'origine de la carte (sa pose de "
            f"création) au plan. Médianes sur les cartes de chaque palier.", "",
            "| Mètre (m) | Mesuré, gauche (m) | droite (m) | Erreur brute, gauche (cm) | après décalage (cm) | "
            "après décalage (%) | σ temporelle (cm) | RMS au plan (cm) | Pixels valides (%) | Inclinaison (°) | Cartes |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L, R = r["left"], r["right"]
        e = L["dist"] - r["tape"]
        out.append(f"| {f2(r['tape'])} | {f2(L['dist'], 3)} | {f2(R['dist'], 3)} | {f2(100 * e, 1)} | "
                   f"{f2(100 * (e - offset), 1)} | {f2(100 * (e - offset) / r['tape'], 1)} | {f2(100 * L['std'], 1)} | "
                   f"{f2(100 * L['rms'], 1)} | {f2(100 * L['valid'], 0)} | {f2(L['tilt'], 1)} | {L['n']} |")
    out += ["", f"Décalage constant (médiane de mesuré - mètre) : {f2(100 * offset, 1)} cm : l'origine de la carte n'est "
            f"pas la face avant du casque où s'appuie le mètre. Droite mesuré = a x mètre + b : a = {f2(slope, 3)}, "
            f"b = {f2(100 * icpt, 1)} cm (a = 1 : pas d'erreur d'échelle).", ""]
    _wall_plot(t, per_eye, segs, distances, out_dir)
    out.append(f"Figure : `{out_dir / 'wall_series.png'}` (distance au plan, carte par carte, et paliers retenus).")
    return out + [""]


def _wall_plot(t, per_eye, segs, distances, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 4))
    for eye, (fr, ms) in per_eye.items():
        ax.plot([f["t"] - t[0] for f, m in zip(fr, ms) if m], [m["dist"] for m in ms if m], ".", ms=2, label=eye)
    for i, (a, b) in enumerate(segs):
        ax.axvspan(a - t[0], b - t[0], alpha=0.15)
        if i < len(distances):
            ax.hlines(distances[i], a - t[0], b - t[0], colors="k", linestyles="--")
    ax.set_xlabel("temps depuis le début de la session (s)")
    ax.set_ylabel("distance au plan (m)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "wall_series.png", dpi=120)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ scène
def scene_section(session: Path, out_dir: Path, max_frames: int, step: int, zmax: float) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fr = dl.load_frames(session, "left")
    pick = fr[:: max(1, len(fr) // max_frames)]
    pts, valid, traj = [], [], []
    for f in pick:
        d = dl.load_raw(session, "left", f)
        if d is None:
            continue
        z = dl.linearize(d, f["near"], f["far"])
        valid.append(float(np.isfinite(z).mean()))
        z = np.where(z <= zmax, z, np.nan)[::step, ::step]
        K = dl.intrinsics(f["W"], f["H"], *f["tans"])
        K = {**K, "fx": K["fx"] / step, "fy": K["fy"] / step, "cx": K["cx"] / step, "cy": K["cy"] / step}
        p = dl.world_points(z, K, f["pos"], f["rot"])
        pts.append(p[np.isfinite(p).all(1)])
        traj.append(f["pos"] * np.array([1, 1, -1]))
    P = np.concatenate(pts)
    traj = np.array(traj)
    ply = out_dir / "scene_depth.ply"
    with ply.open("wb") as fh:
        fh.write(f"ply\nformat binary_little_endian 1.0\nelement vertex {len(P)}\nproperty float x\nproperty float y\n"
                 f"property float z\nend_header\n".encode())
        fh.write(P.astype("<f4").tobytes())
    rng = np.random.default_rng(0)
    S = P[rng.choice(len(P), min(len(P), 400_000), replace=False)]
    fig, axs = plt.subplots(1, 2, figsize=(14, 7))
    for ax, (i, j, title) in zip(axs, ((0, 2, "vue de dessus (x, z)"), (0, 1, "vue de face (x, y)"))):
        ax.scatter(S[:, i], S[:, j], s=0.05, c=S[:, 1], cmap="viridis", alpha=0.5)
        ax.plot(traj[:, i], traj[:, j], "r-", lw=1, label="trajectoire")
        ax.set_aspect("equal")
        ax.set_title(title)
        ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "scene_views.png", dpi=130)
    plt.close(fig)
    # une carte isolée, pour voir sa texture
    mid = pick[len(pick) // 2]
    z = dl.linearize(dl.load_raw(session, "left", mid), mid["near"], mid["far"])
    fig, ax = plt.subplots(figsize=(5, 5))
    im = ax.imshow(np.clip(z, 0, zmax), cmap="turbo")
    fig.colorbar(im, ax=ax, label="z (m)")
    ax.set_title(f"carte gauche {mid['ts']}")
    fig.savefig(out_dir / "scene_frame.png", dpi=120)
    plt.close(fig)
    return ["### Rétroprojection de la session S1", "",
            f"{len(pick)} cartes gauches sur {len(fr)}, un pixel sur {step} dans chaque direction, z ≤ {f2(zmax, 1)} m : "
            f"{len(P):_} points".replace("_", " ") + f". Pixels valides par carte : médiane {f2(100 * np.median(valid), 0)} %, "
            f"p5 {f2(100 * pct(valid, 5), 0)} %.", "",
            f"Fichiers : `{ply}` (à ouvrir dans CloudCompare ou MeshLab), `{out_dir / 'scene_views.png'}`, "
            f"`{out_dir / 'scene_frame.png'}`.", ""]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wall", type=Path, help="session enregistrée avec l'APK SP3 devant le mur")
    ap.add_argument("--distances", type=float, nargs="+", help="distances au mètre ruban, dans l'ordre (m)")
    ap.add_argument("--segments", help="paliers forcés, en s depuis le début : 12-18.5,25-31")
    ap.add_argument("--scene", type=Path, help="session de scène à rétroprojeter (S1)")
    ap.add_argument("--out", type=Path, default=Path.home() / "sp3" / "out")
    ap.add_argument("--crop", type=float, default=0.4)
    ap.add_argument("--max-frames", type=int, default=300)
    ap.add_argument("--step", type=int, default=2)
    ap.add_argument("--zmax", type=float, default=5.0)
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    a.out.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if a.wall:
        say(f"session du mur : {a.wall}")
        lines += format_section(a.wall) + timing_section(a.wall)
        if a.distances:
            manual = None
            if a.segments:
                t0 = dl.load_frames(a.wall, "left")[0]["t"]
                manual = [(t0 + float(x.split("-")[0]), t0 + float(x.split("-")[1])) for x in a.segments.split(",")]
            lines += wall_section(a.wall, a.distances, manual, a.out, a.crop)
    if a.scene:
        say(f"scène : {a.scene}")
        if not a.wall:
            lines += format_section(a.scene)
        lines += scene_section(a.scene, a.out, a.max_frames, a.step, a.zmax)
    if not lines:
        ap.error("donner --wall et/ou --scene")
    text = "\n".join(lines)
    (a.out / "sp3_tables.md").write_text(text, encoding="utf-8")
    print(text)
    say(f"tableaux aussi dans {a.out / 'sp3_tables.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
