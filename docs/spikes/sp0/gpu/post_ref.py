#!/usr/bin/env python3
"""Post-traitement du SfM REF d'une session (PROTOCOL.md §6). Outil de spike jetable.

  python post_ref.py --session <work>/<session>

Lit <session>/est_txt/images.txt (poses du casque) et les modèles texte <session>/ref/sparse/N/,
puis écrit dans <session>/ :
  eval/align_all.json, eval/align_left.json, eval/align_right.json   Sim(3) casque -> REF (align_sim3.py),
                     avec translation_error_m = erreur / scale : le casque est métrique, 1 unité REF = 1/scale m
  ref_flat/sparse/0/  modèle REF retenu, noms d'image sans le dossier left/ ou right/, pour entraîner
                     « A sur poses REF » sur les mêmes noms que l'export (GPU_RUN.md §4)
  summary.json       modèle retenu, fraction recalée, erreurs, dérive par œil, temps du SfM (SC-03)
La dérive n'est donnée que par œil : triées par nom, les deux yeux se suivent (tous les LEFT puis tous les RIGHT)
et les tiers mélangeraient les yeux (SP-0.md §6).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # docs/spikes/sp0/align_sim3.py
import align_sim3  # noqa: E402

SFM_LABELS = ("colmap_feature_extractor", "colmap_matcher", "colmap_mapper")
MIN_REGISTERED = 0.90                                            # PROTOCOL.md §6, SP-0.md §2


def image_records(images_txt: Path) -> list[tuple[str, str]]:
    """(ligne de pose, ligne de points 2D) par image, commentaires retirés, lecture par parité comme align_sim3."""
    lines = [l for l in images_txt.read_text(encoding="utf-8").splitlines() if not l.startswith("#")]
    while lines and not lines[-1].strip() and len(lines) % 2:
        lines.pop()
    recs = []
    for i in range(0, len(lines), 2):
        if len(lines[i].split()) >= 10:
            recs.append((lines[i], lines[i + 1] if i + 1 < len(lines) else ""))
    return recs


def pick_model(sparse: Path) -> tuple[Path, int, dict]:
    counts = {p.name: len(image_records(p / "images.txt"))
              for p in sorted(sparse.iterdir()) if (p / "images.txt").exists()}
    if not counts:
        raise SystemExit(f"aucun modèle texte dans {sparse} (le mapper n'a rien reconstruit ?)")
    best = max(counts, key=counts.get)
    return sparse / best, counts[best], counts


def write_flat(model: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for f in ("cameras.txt", "points3D.txt"):
        (dest / f).write_text((model / f).read_text(encoding="utf-8"), encoding="utf-8")
    out = ["# Image list with two lines of data per image: noms sans dossier (ref_flat, post_ref.py)"]
    for head, pts in image_records(model / "images.txt"):
        f = head.split()
        f[9] = Path(f[9]).name
        out += [" ".join(f[:10]), pts]
    (dest / "images.txt").write_text("\n".join(out) + "\n", encoding="utf-8")


def sfm_seconds(timings: Path) -> dict:
    rows = json.loads(timings.read_text(encoding="utf-8")) if timings.exists() else []
    last = {r["label"]: r for r in rows if r["exit_code"] == 0}          # dernier passage réussi par étape
    steps = {k: last[k]["wall_s"] for k in SFM_LABELS if k in last}
    out = {"steps_s": steps}
    if len(steps) == len(SFM_LABELS):
        out["total_s"] = round(sum(steps.values()), 1)
        out["total_min"] = round(out["total_s"] / 60, 1)
    if "src3_export_colmap" in last:
        out["export_src3_s"] = last["src3_export_colmap"]["wall_s"]
    return out


def eye(name: str) -> str:
    n = name.lower()
    return "left" if n.startswith("left") else "right" if n.startswith("right") else "other"


def align_subset(est: dict, ref: dict, which: str) -> dict:
    keep = (lambda n: True) if which == "all" else (lambda n: eye(n) == which)
    e = {n: p for n, p in est.items() if keep(n)}
    r = {n: p for n, p in ref.items() if keep(n)}
    names, pe, pr = align_sim3.match(e, r)
    res = align_sim3.align_and_score(pe, pr, with_scale=True)
    res["n_est"] = len(e)
    res["names_first_last"] = [names[0], names[-1]]
    res["m_per_ref_unit"] = 1.0 / res["scale"]
    res["translation_error_m"] = {k: v / res["scale"] for k, v in res["translation_error"].items()}
    thirds = res["drift"]["translation_rmse_by_third"]
    if which == "all":
        res.pop("drift")
    else:
        res["drift"]["translation_rmse_by_third_m"] = [t / res["scale"] for t in thirds]
        res["drift"]["ratio_last_first"] = thirds[2] / thirds[0] if thirds[0] else None
    return res


def summarize(sdir: Path, est_txt: Path, sparse: Path, timings: Path, extra: dict | None = None) -> dict:
    model, n_ref, counts = pick_model(sparse)
    write_flat(model, sdir / "ref_flat" / "sparse" / "0")
    est = align_sim3.read_poses(est_txt)
    ref = align_sim3.read_poses(model / "images.txt")
    frac = n_ref / len(est) if est else 0.0
    out = dict(extra or {})
    out.update({
        "n_images": len(est),
        "ref_model": model.name,
        "ref_models_images": counts,
        "ref_registered": n_ref,
        "ref_registered_fraction": round(frac, 4),
        "ref_is_reference": frac >= MIN_REGISTERED,
        "sfm_time": sfm_seconds(timings),
        "align": {},
    })
    (sdir / "eval").mkdir(parents=True, exist_ok=True)
    for which in ("all", "left", "right"):
        try:
            res = align_subset(est, ref, which)
        except SystemExit as e:                     # moins de 3 images communes (un seul œil exporté...)
            out["align"][which] = {"error": str(e)}
            continue
        (sdir / "eval" / f"align_{which}.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
        out["align"][which] = {
            "n_common": res["n_poses"], "scale": res["scale"], "m_per_ref_unit": res["m_per_ref_unit"],
            "translation_error_m": res["translation_error_m"], "rotation_error_deg": res["rotation_error_deg"],
            **({"drift_rmse_by_third_m": res["drift"]["translation_rmse_by_third_m"],
                "drift_ratio_last_first": res["drift"]["ratio_last_first"]} if "drift" in res else {}),
        }
    (sdir / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return out


def table(results: list[dict]) -> str:
    rows = ["", "session      | images | REF recalées      | transl. méd. (m) tous/G/D | rot. méd. (°) tous | SfM (min)",
            "-------------|--------|-------------------|---------------------------|--------------------|----------"]
    for r in results:
        if "align" not in r:
            continue
        al = r["align"]
        tm = "/".join(f"{al[w]['translation_error_m']['median']:.4f}" if "translation_error_m" in al[w] else "-"
                      for w in ("all", "left", "right"))
        rot = f"{al['all']['rotation_error_deg']['median']:.3f}" if "rotation_error_deg" in al["all"] else "-"
        reg = f"{r['ref_registered']} ({100 * r['ref_registered_fraction']:.1f} %)" + ("" if r["ref_is_reference"] else " <90%")
        rows.append(f"{r['session'][:12]:<12} | {r['n_images']:>6} | {reg:<17} | {tm:<25} | {rot:>18} | "
                    f"{r['sfm_time'].get('total_min', '-')}")
    return "\n".join(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", required=True, type=Path, help="dossier <work>/<session> de pipeline.py")
    a = ap.parse_args(argv)
    s = a.session
    r = summarize(s, s / "est_txt" / "images.txt", s / "ref" / "sparse", s / "timings.json",
                  extra={"session": s.name})
    print(table([r]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
