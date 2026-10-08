#!/usr/bin/env python3
"""Bench 3DGS de SP-0 sur un PC NVIDIA : splatfacto option A, poses du casque contre poses REF COLMAP.

Outil de spike jetable, pas du code mote. Appelé par train_all.ps1, après run_all.ps1 ; lancé seul :

  python train.py --work <sorties de run_all> [--seeds 0 1 2] [--dry-run]

Pour chaque session de --work qui a un REF (summary.json de post_ref.py), dans --work/<session>/ :
  1. nsdata      jeu commun aux deux sources de poses (PROTOCOL.md §7, GPU_RUN.md §0) : images présentes dans
                 le modèle du casque ET dans le REF, paires gauche/droite complètes seulement, hold-out par blocs
                 de paires (make_holdout.py, 5 toutes les 40) ; headset/sparse/0 et ref/sparse/0 filtrés pareil,
                 train_list, test_list, val_list et validation_list (selon la version, nerfstudio lit l'une ou
                 l'autre, et s'arrête s'il en manque une dès que train_list existe)
  2. entraînement  ns-train splatfacto, variantes A (poses du casque) et AREF (poses REF), mêmes images, mêmes
                 listes, mêmes graines, mêmes hyperparamètres : 30 000 itérations, SO3xR3, initialisation aléatoire
  3. rendu       ns-render dataset du hold-out, en PNG (JPEG par défaut dans nerfstudio : fausserait le PSNR)
  4. métriques   metrics.py (PSNR, SSIM, LPIPS VGG) entre rendu et gt-rgb ; ns-eval pour recouper ;
                 courbe PSNR(temps) lue dans tensorboard, temps pour atteindre 20 dB (SC-01)
  5. bench.json  moyennes et écarts-types par variante, écart de PSNR A - AREF contre la règle de SP-0.md §2,
                 seuils proposés pour SC-01 et SC-02 (PROTOCOL.md §9)
Mêmes marqueurs de reprise que pipeline.py : relancer reprend à l'entraînement en échec.
"""
from __future__ import annotations

import argparse
import bisect
import json
import os
import shutil
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import make_holdout  # noqa: E402
import pipeline  # noqa: E402
import post_ref  # noqa: E402
from pipeline import StepError, run_logged, say  # noqa: E402

VARIANTS = {"A": "headset/sparse/0", "AREF": "ref/sparse/0"}
PAIR_MAX_DT_US = 50_000                  # au-delà, deux images ne sont pas une paire (S1 : 27,8 ms au plus)
PSNR_TAG = "Eval Images Metrics Dict (all images)/psnr"
SC01_PSNR = 20.0
RULE = {"poursuite": -1.0, "arret": -3.0}    # SP-0.md §2 : PSNR A - PSNR A sur poses REF (dB)


# ----------------------------------------------------------------- jeu commun

def ts_of(name: str) -> int | None:
    stem = Path(name).stem
    tail = stem.split("_")[-1]
    return int(tail) if tail.isdigit() else None


def pair_keys(names: list[str], pairs_csv: Path | None) -> tuple[dict, str]:
    """Clé de paire par nom d'image : mruk_stereo_pairs.csv s'il est là, sinon horodatages les plus proches
    (un LEFT et un RIGHT à moins de 50 ms, un à un). L'appariement par nom seul sépare 30 % des paires de S1."""
    if pairs_csv and pairs_csv.is_file():
        by_stem = make_holdout.pairs_csv_keys(pairs_csv)
        return {n: by_stem[Path(n).stem.lower()] for n in names if Path(n).stem.lower() in by_stem}, "csv"
    left = sorted((ts_of(n), n) for n in names if post_ref.eye(n) == "left" and ts_of(n) is not None)
    right = sorted((ts_of(n), n) for n in names if post_ref.eye(n) == "right" and ts_of(n) is not None)
    rts = [t for t, _ in right]
    cands = []
    for t, n in left:
        i = bisect.bisect_left(rts, t)
        for j in (i - 1, i):
            if 0 <= j < len(right) and abs(rts[j] - t) <= PAIR_MAX_DT_US:
                cands.append((abs(rts[j] - t), n, right[j][1]))
    keys, used = {}, set()
    for _, l, r in sorted(cands):
        if l in used or r in used:
            continue
        used |= {l, r}
        keys[l] = keys[r] = f"{ts_of(l):020d}"
    return keys, "horodatage"


def write_model(src_dir: Path, records: list, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_dir / "cameras.txt", dest / "cameras.txt")
    # en-têtes ASCII et UTF-8 explicite : nerfstudio lit ces fichiers en UTF-8, Windows écrit en cp1252 par défaut
    (dest / "points3D.txt").write_text("# 3D point list: empty (option A, random init)\n", encoding="utf-8")
    out = ["# Image list with two lines of data per image: filtered by train.py (common set A / AREF)"]
    for head, pts in records:
        out += [head, pts]
    (dest / "images.txt").write_text("\n".join(out) + "\n", encoding="utf-8")


def prepare(sdir: Path, images: Path, pairs_csv: Path | None, block: int, period: int) -> dict:
    est = {Path(h.split()[9]).name: (h, p) for h, p in post_ref.image_records(sdir / "est_txt" / "images.txt")}
    ref = {Path(h.split()[9]).name: (h, p) for h, p in
           post_ref.image_records(sdir / "ref_flat" / "sparse" / "0" / "images.txt")}
    common = sorted(set(est) & set(ref))
    keys, method = pair_keys(common, pairs_csv)
    groups = {}
    for n in common:
        if n in keys:
            groups.setdefault(keys[n], []).append(n)
    full = {k: v for k, v in groups.items() if sorted(post_ref.eye(n) for n in v) == ["left", "right"]}
    kept = sorted(n for v in full.values() for n in v)
    train, test, _, test_keys = make_holdout.split(kept, block, period, keys_by_stem={Path(n).stem.lower(): keys[n]
                                                                                     for n in kept})
    if len(test_keys) < 2 * block:                      # au moins deux blocs tenus à part
        raise StepError(f"{sdir.name} : {len(full)} paires communes au casque et au REF, {len(test_keys)} tenues "
                        f"à part : trop peu pour un hold-out (session trop courte ?)")
    nd = sdir / "nsdata"
    if nd.exists():
        shutil.rmtree(nd)
    write_model(sdir / "est_txt", [est[n] for n in kept], nd / "headset" / "sparse" / "0")
    write_model(sdir / "ref_flat" / "sparse" / "0", [ref[n] for n in kept], nd / "ref" / "sparse" / "0")
    (nd / "images").mkdir(parents=True)
    for n in kept:
        try:
            os.link(images / n, nd / "images" / n)
        except OSError:
            shutil.copy2(images / n, nd / "images" / n)
    for f, names in (("train_list.txt", train), ("test_list.txt", test),
                     ("val_list.txt", test), ("validation_list.txt", test)):
        (nd / f).write_text("\n".join(names) + "\n", encoding="utf-8")
    info = {"n_images_est": len(est), "n_images_ref": len(ref), "n_common": len(common), "pairing": method,
            "n_pairs": len(full), "n_test_pairs": len(test_keys), "n_train_images": len(train),
            "n_test_images": len(test), "block": block, "period": period, "test": test}
    (nd / "holdout.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    say(f"{sdir.name} : {len(full)} paires communes ({method}), {len(train)} images train, {len(test)} test")
    return info


# ----------------------------------------------------------------- mesures

def psnr_curve(run_dir: Path) -> list[dict] | None:
    """(itération, secondes depuis le premier événement, PSNR moyen du hold-out) lus dans tensorboard."""
    try:
        from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    except ImportError:
        return None
    acc = EventAccumulator(str(run_dir), size_guidance={"scalars": 0})
    acc.Reload()
    tags = acc.Tags().get("scalars", [])
    if PSNR_TAG not in tags:
        return None
    t0 = min(e.wall_time for t in tags for e in acc.Scalars(t))
    return [{"step": e.step, "t_s": round(e.wall_time - t0, 1), "psnr": e.value} for e in acc.Scalars(PSNR_TAG)]


def first_above(curve: list[dict] | None, level: float) -> dict | None:
    return next((c for c in curve or [] if c["psnr"] >= level), None)


def mean_std(xs: list) -> dict:
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"mean": None, "std": None, "n": 0}
    return {"mean": statistics.fmean(xs), "std": statistics.stdev(xs) if len(xs) > 1 else 0.0, "n": len(xs)}


def bench(sdir: Path, runs: dict) -> dict:
    """runs : {variante: {graine: {psnr, ssim, lpips, train_s, t20_s, t20_step, ...}}} -> bench.json"""
    out = {"session": sdir.name, "variants": {}}
    for v, seeds in runs.items():
        out["variants"][v] = {"per_seed": seeds, **{k: mean_std([r.get(k) for r in seeds.values()])
                                                    for k in ("psnr", "ssim", "lpips", "train_s", "t20_s")}}
    va = out["variants"]
    if "A" in va and "AREF" in va and va["A"]["psnr"]["n"] and va["AREF"]["psnr"]["n"]:
        d = va["A"]["psnr"]["mean"] - va["AREF"]["psnr"]["mean"]
        out["delta_psnr_A_minus_AREF"] = d
        out["rule_sp0_psnr"] = ("poursuite" if d >= RULE["poursuite"] else "arret" if d < RULE["arret"]
                                else "intermediaire")
    if "A" in va and va["A"]["psnr"]["n"]:
        a = va["A"]["psnr"]
        out["proposals"] = {                                   # PROTOCOL.md §9
            "sc01_psnr_db": round(min(SC01_PSNR, a["mean"] - 3.0), 1),
            "sc02_gain_db": round(max(1.0, 2 * a["std"]), 2) if a["n"] > 1 else None,
            "note": "SC-01 = min(20 dB, PSNR_A - 3 dB) ; SC-02 = max(1 dB, 2 sigma de A entre graines)",
        }
    (sdir / "bench.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return out


def fmt(ms: dict, nd=2) -> str:
    return "-" if ms["mean"] is None else f"{ms['mean']:.{nd}f} ± {ms['std']:.{nd}f}"


def table(benches: list[dict]) -> str:
    rows = ["", "session      | variante | PSNR (dB)      | SSIM            | LPIPS           | entraîn. (min) | 20 dB (s)",
            "-------------|----------|----------------|-----------------|-----------------|----------------|----------"]
    for b in benches:
        for v, r in b["variants"].items():
            tr = r["train_s"]
            trm = "-" if tr["mean"] is None else f"{tr['mean'] / 60:.1f}"
            rows.append(f"{b['session'][:12]:<12} | {v:<8} | {fmt(r['psnr']):<14} | {fmt(r['ssim'], 4):<15} | "
                        f"{fmt(r['lpips'], 4):<15} | {trm:>14} | {fmt(r['t20_s'], 0)}")
        if "delta_psnr_A_minus_AREF" in b:
            rows.append(f"{'':<12} | A - AREF : {b['delta_psnr_A_minus_AREF']:+.2f} dB -> règle SP-0.md §2 : "
                        f"{b['rule_sp0_psnr']}")
    return "\n".join(rows)


# ----------------------------------------------------------------- orchestration

def ns(tool: str) -> str:
    scripts = Path(sys.executable).parent
    for n in (f"{tool}.exe", tool):
        if (scripts / n).exists():
            return str(scripts / n)
    return tool


def train_one(s: pipeline.Session, v: str, seed: int, a) -> dict:
    nd, runs = s.dir / "nsdata", s.dir / "runs"
    run_dir = runs / v / "splatfacto" / f"seed{seed}"
    ev = s.dir / "eval" / f"{v}_seed{seed}"
    cfg = run_dir / "config.yml"

    def train():
        if run_dir.exists() and not pipeline.DRY:
            shutil.rmtree(run_dir)                    # entraînement interrompu : on le refait, temps complet
        run_logged([ns("ns-train"), "splatfacto", "--data", nd, "--output-dir", runs,
                    "--experiment-name", v, "--timestamp", f"seed{seed}",
                    "--max-num-iterations", a.iterations, "--machine.seed", seed,
                    "--pipeline.model.camera-optimizer.mode", "SO3xR3",
                    "--vis", "tensorboard", "--steps-per-eval-all-images", a.eval_every,
                    "colmap", "--colmap-path", VARIANTS[v], "--images-path", "images",
                    "--load-3D-points", "False", "--downscale-factor", "1"],
                   s.logs / f"train_{v}_seed{seed}.log", s.timings, f"splatfacto_{v}_seed{seed}")
    s.step(f"train_{v}_seed{seed}", train)

    def render():
        if ev.exists() and not pipeline.DRY:
            shutil.rmtree(ev)
        run_logged([ns("ns-render"), "dataset", "--load-config", cfg, "--split", "test", "--output-path", ev,
                    "--rendered-output-names", "rgb", "gt-rgb", "--image-format", "png"],
                   s.logs / f"render_{v}_seed{seed}.log")
        run_logged([sys.executable, HERE.parent / "metrics.py", "--pred", ev / "test" / "rgb",
                    "--gt", ev / "test" / "gt-rgb", "--lpips-net", "vgg", "--out", ev / "metrics.json"],
                   s.logs / f"metrics_{v}_seed{seed}.log")
        run_logged([ns("ns-eval"), "--load-config", cfg, "--output-path", ev / "nseval.json"],
                   s.logs / f"nseval_{v}_seed{seed}.log")
    s.step(f"eval_{v}_seed{seed}", render)

    if pipeline.DRY:
        return {}
    m = json.loads((ev / "metrics.json").read_text(encoding="utf-8"))
    rows = json.loads(s.timings.read_text(encoding="utf-8"))
    tr = [r for r in rows if r["label"] == f"splatfacto_{v}_seed{seed}" and r["exit_code"] == 0]
    curve = psnr_curve(run_dir)
    hit = first_above(curve, SC01_PSNR)
    res = {"psnr": m["mean"]["psnr"], "ssim": m["mean"]["ssim"], "lpips": m["mean"]["lpips"],
           "n_views": m["n_views"], "train_s": tr[-1]["wall_s"] if tr else None,
           "t20_s": hit["t_s"] if hit else None, "t20_step": hit["step"] if hit else None,
           "psnr_curve": curve}
    try:
        nse = json.loads((ev / "nseval.json").read_text(encoding="utf-8"))["results"]
        res["nseval"] = {k: nse.get(k) for k in ("psnr", "ssim", "lpips")}
    except (OSError, KeyError, ValueError):
        pass
    return res


def sources(sdir: Path) -> tuple[Path, Path | None]:
    summ = json.loads((sdir / "summary.json").read_text(encoding="utf-8"))
    if summ.get("kind") == "raw":
        return sdir / "export" / "images", Path(summ["source"]) / "mruk_stereo_pairs.csv"
    src = Path(summ.get("source", sdir / "export"))
    csv = next((p for p in (src / "mruk_stereo_pairs.csv", src.parent / "mruk_stereo_pairs.csv") if p.exists()), None)
    return src / "images", csv


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True, type=Path, help="dossier des sorties de run_all.ps1 / pipeline.py")
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--variants", nargs="+", choices=list(VARIANTS), default=list(VARIANTS))
    ap.add_argument("--iterations", type=int, default=30000, help="SP-0 fige 30 000 (PROTOCOL.md §7)")
    ap.add_argument("--eval-every", type=int, default=2000,
                    help="évaluation du hold-out entier toutes les N itérations, pour la courbe PSNR(temps) de SC-01")
    ap.add_argument("--block", type=int, default=5)
    ap.add_argument("--period", type=int, default=40)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    pipeline.DRY = a.dry_run
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    os.environ["PYTHONUTF8"] = "1"                   # rich et tqdm dans un tube sous Windows
    a.work = a.work.resolve()
    pipeline.keep_awake()

    sessions = sorted(p for p in a.work.iterdir() if (p / "summary.json").exists()
                      and (p / "ref_flat" / "sparse" / "0" / "images.txt").exists()) if a.work.is_dir() else []
    sessions = [p for p in sessions if a.only is None or p.name in a.only]
    if not sessions:
        say(f"aucune session avec un REF dans {a.work} : lancer d'abord run_all.ps1")
        return 2
    benches, failed = [], []
    for sdir in sessions:
        s = pipeline.Session(sdir.name, sdir, "done", a.work)
        try:
            images, csv = sources(sdir)
            s.step("nsdata", lambda: prepare(sdir, images, csv, a.block, a.period))
            runs = {v: {} for v in a.variants}
            for seed in a.seeds:                              # graine par graine : A et AREF avancent ensemble
                for v in a.variants:
                    runs[v][f"seed{seed}"] = train_one(s, v, seed, a)
            if not pipeline.DRY:
                benches.append(bench(sdir, runs))
        except StepError as e:
            say(f"ÉCHEC {sdir.name} : {e}")
            failed.append(sdir.name)
    if benches:
        (a.work / "bench_all.json").write_text(json.dumps(benches, indent=1, ensure_ascii=False), encoding="utf-8")
        print(table(benches))
        say(f"résumé : {a.work / 'bench_all.json'}")
    if failed:
        say(f"sessions en échec : {', '.join(failed)}. Relancer la même commande reprend où ça s'est arrêté.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
