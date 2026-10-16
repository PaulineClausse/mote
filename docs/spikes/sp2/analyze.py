"""SP-2 : analyse des captures du damier (TASK-552b).

  uv run --no-project --with opencv-python-headless --with numpy python docs/spikes/sp2/analyze.py ^
      --square-mm 23.0 B=$HOME\\sp2\\<session B> C=... D=... E=... --out $HOME\\sp2\\analyse

Pour chaque image où le damier est détecté, la pose de la caméra est calculée depuis le damier (PnP), mesure
indépendante de MRUK. On en tire :
1. la formule de conversion Unity -> canonique : celle qui laisse le damier immobile dans le monde quand le casque
   bouge, et son erreur de reprojection en pixels ;
2. le décalage entre la pose MRUK d'une image et l'instant de sa prise (H-04, NFR-01 : 5 ms au plus) ;
3. le décalage entre l'horodatage d'une image et l'instant de sa prise, par rapport au suivi du casque ;
4. la synchronisation gauche/droite (H-09) ;
5. les résidus selon la vitesse (H-10) et selon la distance au centre de l'image (H-11).
Les seuils (immobilité, vitesse minimale pour les décalages) sont des réglages.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sp2lib as L  # noqa: E402

EYES = ("left", "right")


def f(x, nd=2):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"


def pct(a, q):
    return float(np.percentile(a, q)) if len(a) else float("nan")


def build_obs(sessions, cams, hmds, dets, obj, flip):
    """Observations PnP par session et par œil, dans la convention d'image testée (retournée ou non)."""
    out = {}
    for label, s in sessions.items():
        for eye in EYES:
            cam = cams[(label, eye)]
            frames = {fr.file: fr for fr in L.load_frames(s, eye)}
            K = cam.K.copy()
            if flip:
                K[1, 2] = cam.height - 1 - K[1, 2]
            lst = []
            for name, c in dets[(label, eye)].items():
                fr = frames.get(name)
                if fr is None or not fr.pose_ok:
                    continue
                img = L.flip_v(c, cam) if flip else c
                r = L.pnp(obj, img, K)
                if r is None:
                    continue
                o = L.Obs(label, eye, name, fr.t, r[0], r[1], r[2], img, fr)
                o.omega = hmds[label].omega(fr.t)
                o.speed = hmds[label].speed(fr.t)
                o.radius = float(np.mean(np.linalg.norm(img - K[:2, 2], axis=1)))
                lst.append(o)
            out[(label, eye)] = sorted(lst, key=lambda o: o.t)
    return out


def analyze(sessions: dict, square_mm: float, cols: int = 9, rows: int = 6, workers: int = 4,
            static_omega: float = 0.05, static_speed: float = 0.01, min_omega: float = 0.3,
            select_omega: float = 0.2, select_speed: float = 0.05):
    obj = L.board_points(cols, rows, square_mm)
    cams = {(lb, e): L.load_camera(s, e) for lb, s in sessions.items() for e in EYES}
    hmds = {lb: L.HmdTrack.load(s) for lb, s in sessions.items()}
    dets = {(lb, e): L.detect_session(s, e, cams[(lb, e)], (cols, rows), workers)
            for lb, s in sessions.items() for e in EYES}
    rep, res = [], {"square_mm": square_mm, "pattern": [cols, rows]}

    def is_static(o):
        return np.linalg.norm(o.omega) < static_omega and o.speed < static_speed

    def is_slow(o):
        return np.linalg.norm(o.omega) < select_omega and o.speed < select_speed

    # --- 0. Données
    rep += ["## 0. Données", "", "| Session | Œil | Images | Damier détecté | Immobiles détectées | Cadence (i/s) |",
            "|---|---|---|---|---|---|"]
    base = build_obs(sessions, cams, hmds, dets, obj, flip=False)
    for lb, s in sessions.items():
        for e in EYES:
            frames = L.load_frames(s, e)
            ts = np.array([fr.t for fr in frames])
            rate = (len(ts) - 1) / (ts[-1] - ts[0]) if len(ts) > 1 else float("nan")
            obs = base[(lb, e)]
            rep.append(f"| {lb} | {e} | {len(frames)} | {len(obs)} | {sum(map(is_static, obs))} | {f(rate, 1)} |")
    rep += ["", "Horloges du casque : écart XR - Unix stable à " +
            ", ".join(f"{lb} {f(h.clock_spread_ms, 2)} ms (p95)" for lb, h in hmds.items()) + ".", ""]

    # --- 1. Formule de conversion
    rep += ["## 1. Conversion Unity -> canonique", "",
            "Damier immobile : sa pose dans le monde, calculée image par image avec la pose MRUK convertie, doit rester "
            f"la même. Chaque session a son propre monde (origine remise à zéro au début de la capture) : la "
            f"dispersion se mesure autour de la pose propre à chaque session. Images immobiles ou lentes "
            f"(|ω| < {select_omega} rad/s, "
            f"< {select_speed} m/s), œil gauche : plus les poses sont variées, plus la mesure départage les formules.",
            "",
            "| Côté caméra | Image retournée | Images | Rotation médiane / p95 (°) | Position médiane / p95 (mm) |",
            "|---|---|---|---|---|"]
    cands = []
    obs_by_flip = {False: base, True: build_obs(sessions, cams, hmds, dets, obj, flip=True)}
    for flip in (False, True):
        st = [o for (lb, e), lst in obs_by_flip[flip].items() if e == "left" for o in lst if is_slow(o)]
        if len(st) < 3:
            continue
        for name, D in L.CAM_SIGNS.items():
            sp = L.pooled_spread([L.world_board([o for o in st if o.session == lb], D) for lb in sessions])
            if sp:
                cands.append((sp["pos_p95_mm"] + 10 * sp["rot_p95_deg"], name, flip, sp, sp["n"]))
    cands.sort(key=lambda c: c[0])
    for _, name, flip, sp, n in cands:
        mark = " (hypothèse de la spec)" if (name, flip) == L.SPEC_CANDIDATE else ""
        rep.append(f"| {name}{mark} | {'oui' if flip else 'non'} | {n} | {f(sp['rot_med_deg'])} / "
                   f"{f(sp['rot_p95_deg'])} | {f(sp['pos_med_mm'], 1)} / {f(sp['pos_p95_mm'], 1)} |")
    if not cands:
        rep += ["", "**Pas assez d'images immobiles avec le damier : analyse impossible.**"]
        return rep, res
    _, best_name, best_flip, best_sp, _ = cands[0]
    D = L.CAM_SIGNS[best_name]
    obs = obs_by_flip[best_flip]
    spec_ok = (best_name, best_flip) == L.SPEC_CANDIDATE
    res["conversion"] = {"cam_sign": best_name, "image_flipped": best_flip, "spec_hypothesis": spec_ok,
                         "rot_p95_deg": best_sp["rot_p95_deg"], "pos_p95_mm": best_sp["pos_p95_mm"]}
    margin = cands[1][0] / max(cands[0][0], 1e-9) if len(cands) > 1 else float("inf")
    res["conversion"]["margin"] = margin
    rep += ["", f"Retenue : côté caméra {best_name}, image {'retournée' if best_flip else 'telle quelle'}"
            f"{' : c’est l’hypothèse de la spec' if spec_ok else ' : ce n’est PAS l’hypothèse de la spec'}. "
            f"La suivante disperse {f(margin, 1)} fois plus"
            f"{' : départage net' if margin >= 3 else ' : départage FAIBLE, poses trop peu variées'}.", ""]

    # Pose du damier, session par session (chaque session a son monde) : images immobiles de l'œil gauche, à
    # défaut images lentes ; l'œil droit doit retrouver la même.
    def board_for(lst):
        pick = [o for o in lst if is_static(o)]
        if len(pick) < 3:
            pick = [o for o in lst if is_slow(o)]
        if len(pick) < 3:
            return None
        sp = L.spread(*L.world_board(pick, D))
        return sp["R"], sp["t"]

    boards, lr = {}, []
    for lb in sessions:
        bl = board_for(obs.get((lb, "left"), []))
        br = board_for(obs.get((lb, "right"), []))
        if bl is not None:
            boards[lb] = bl
            if br is not None:
                lr.append((L.angle_deg(br[0] @ bl[0].T), float(np.linalg.norm(br[1] - bl[1]) * 1e3)))
        elif br is not None:
            boards[lb] = br
    missing = [lb for lb in sessions if lb not in boards]
    if missing:
        rep += [f"Sessions sans assez d'images lentes pour situer le damier, écartées : {', '.join(missing)}.", ""]
    obs = {k: v for k, v in obs.items() if k[0] in boards}

    def bw(o):
        return boards[o.session]

    if lr:
        d_ang, d_pos = float(np.median([a for a, _ in lr])), float(np.median([m for _, m in lr]))
        res["left_right_board"] = {"deg": d_ang, "mm": d_pos}
        rep += [f"Pose du damier vue par l'œil droit contre l'œil gauche (médiane des sessions) : {f(d_ang)}° et "
                f"{f(d_pos, 1)} mm d'écart (extrinsèques MRUK des deux caméras cohérentes si quelques mm).", ""]

    # Erreur de reprojection de la formule : coins projetés avec la pose MRUK convertie.
    rep += ["Erreur de reprojection avec la pose MRUK convertie (RMS par image, px) :", "",
            "| Œil | Immobiles : médiane / p95 | En mouvement : médiane / p95 | Résidu PnP médian |", "|---|---|---|---|"]
    reproj = {}
    worst = []
    t_first = {(lb, e): min(fr.t for fr in L.load_frames(s, e)) for lb, s in sessions.items() for e in EYES}
    for e in EYES:
        errs_s, errs_m, pnp_r = [], [], []
        for (lb, ee), lst in obs.items():
            if ee != e:
                continue
            K = cams[(lb, e)].K.copy()
            if best_flip:
                K[1, 2] = cams[(lb, e)].height - 1 - K[1, 2]
            for o in lst:
                R_wc, t_wc = L.unity_to_cv(o.frame.pos, o.frame.quat, D)
                uv = L.project(obj, *bw(o), R_wc, t_wc, K)
                err = float(np.sqrt(np.mean(np.sum((uv - o.corners) ** 2, axis=1))))
                (errs_s if is_static(o) else errs_m).append(err)
                pnp_r.append(o.rms)
                worst.append((err, lb, e, o.t - t_first[(lb, e)], o.frame.updated, float(np.linalg.norm(o.omega)),
                              is_static(o), o.file))
        reproj[e] = {"static_med": pct(errs_s, 50), "static_p95": pct(errs_s, 95),
                     "moving_med": pct(errs_m, 50), "moving_p95": pct(errs_m, 95), "pnp_med": pct(pnp_r, 50)}
        r = reproj[e]
        rep.append(f"| {e} | {f(r['static_med'])} / {f(r['static_p95'])} | {f(r['moving_med'])} / "
                   f"{f(r['moving_p95'])} | {f(r['pnp_med'])} |")
    res["reprojection_px"] = reproj
    worst.sort(key=lambda w: -w[0])
    n_out = sum(1 for w in worst if w[0] > 20)
    rep += ["", f"Images reprojetées à plus de 20 px : {n_out} sur {len(worst)}, dont "
            f"{sum(1 for w in worst if w[0] > 20 and not w[4])} sans pose MRUK neuve (is_updated_this_frame = false). "
            "Les dix pires :", "",
            "| Erreur (px) | Session | Œil | Depuis le début (s) | Pose neuve | |ω| (rad/s) | Immobile | Image |",
            "|---|---|---|---|---|---|---|---|"]
    for err, lb, e, dt, upd, om, st_, name in worst[:10]:
        rep.append(f"| {f(err, 1)} | {lb} | {e} | {f(dt, 2)} | {'oui' if upd else 'non'} | {f(om)} | "
                   f"{'oui' if st_ else 'non'} | {name} |")
    clean = [w for w in worst if w[4]]
    res["reprojection_updated_only"] = {"n": len(clean), "p50": pct([w[0] for w in clean], 50),
                                        "p95": pct([w[0] for w in clean], 95)}
    rep += ["", f"Sur les seules images avec pose MRUK neuve : médiane {f(pct([w[0] for w in clean], 50))} px, "
            f"p95 {f(pct([w[0] for w in clean], 95))} px ({len(clean)} images).", ""]

    # --- 2. Synchronisation image/pose. D'abord l'instant de prise réel (δ), sur le suivi du casque : la vitesse
    # angulaire qui sert ensuite à τ et à la stéréo doit être prise à cet instant, pas à l'horodatage, sans quoi
    # l'estimation est tirée vers zéro quand la rotation change vite.
    rep += ["## 2. Synchronisation image/pose", "", "δ : instant de prise de l'image par rapport à son horodatage, mesuré sur le suivi du casque "
            "(δ < 0 : l'image a été prise avant son horodatage). δ_MRUK : instant auquel correspond la pose MRUK.", "",
            "| Œil | δ image (ms) | δ pose MRUK (ms) | Écart (ms) |", "|---|---|---|---|"]
    res["delta"] = {}
    for e in EYES:
        allo = [o for (lb, ee), lst in obs.items() if ee == e for o in lst]
        st = [o for o in allo if is_static(o)]
        mv = [o for o in allo if np.linalg.norm(o.omega) >= min_omega]
        if len(st) < 3 or len(mv) < 5:
            rep.append(f"| {e} | trop peu d'images | | |")
            continue
        vis = {id(o): L.vision_camera(o, *bw(o))[0] for o in allo}
        mr = {id(o): L.unity_to_cv(o.frame.pos, o.frame.quat, D)[0] for o in allo}
        hm = {o.session: hmds[o.session] for o in allo}
        X_v = L.mean_rotation([hm[o.session].rot_at(o.t).T @ vis[id(o)] for o in st])
        X_m = L.mean_rotation([hm[o.session].rot_at(o.t).T @ mr[id(o)] for o in st])

        def cost(d, X, poses):
            return float(np.median([L.angle_deg(poses[id(o)].T @ hm[o.session].rot_at(o.t + d) @ X) for o in mv]))

        dv, _ = L.search_lag(lambda d: cost(d, X_v, vis))
        dm, _ = L.search_lag(lambda d: cost(d, X_m, mr))
        res["delta"][e] = {"image_ms": dv * 1e3, "mruk_pose_ms": dm * 1e3}
        for o in allo:
            o.omega = hm[o.session].omega(o.t + dv)
        rep.append(f"| {e} | {f(dv * 1e3)} | {f(dm * 1e3)} | {f((dm - dv) * 1e3)} |")
    rep += ["", "L'écart δ_MRUK − δ_image recoupe τ par une autre voie (suivi du casque au lieu de la vitesse angulaire).",
            ""]

    # Pose MRUK contre contenu de l'image (H-04, NFR-01).
    rep += ["τ : décalage de la pose MRUK par rapport à l'instant où l'image a été prise (τ > 0 : pose plus tardive). "
            f"Estimé par l'écart de rotation entre pose MRUK et pose du damier, rapporté à la vitesse angulaire "
            f"à l'instant de prise (δ ci-dessus), sur les images où |ω| ≥ {min_omega} rad/s.", "",
            "Un biais de rotation constant de la pose MRUK (erreur d'extrinsèque) est estimé en même temps, sans quoi "
            "il passerait pour un retard.", "",
            "| Œil | τ (ms) | IC 95 % (ms) | Images | Rejetées | Résidu médian (mrad) | Biais constant (mrad) |",
            "|---|---|---|---|---|---|---|"]
    res["tau"] = {}
    for e in EYES:
        errs, oms = [], []
        for (lb, ee), lst in obs.items():
            if ee != e:
                continue
            for o in lst:
                R_v, _ = L.vision_camera(o, *bw(o))
                R_m, _ = L.unity_to_cv(o.frame.pos, o.frame.quat, D)
                errs.append(L.log_rot(R_v @ R_m.T))
                oms.append(o.omega)
        r = L.lag_from_rotation_errors(errs, oms, min_omega, sign=-1.0, intercept=True) if errs else None
        res["tau"][e] = r
        rep.append(f"| {e} | {f(r['tau_ms'])} | {f(r['ci95_ms'][0])} à {f(r['ci95_ms'][1])} | {r['n']} | "
                   f"{r['rejected']} | {f(r['resid_mrad_med'])} | {f(r['bias_mrad'])} |" if r
                   else f"| {e} | - | - | trop peu d'images | | | |")

    # --- 3. Gauche / droite (H-09)
    rep += ["## 3. Synchronisation gauche/droite", ""]
    pairs = {}
    for lb, s in sessions.items():
        pf = s / "mruk_stereo_pairs.csv"
        if pf.exists():
            d_us = [int(r["time_delta_us"]) for r in L._rows(pf)]
            if d_us:
                rep.append(f"- {lb} : écart d'horodatage gauche/droite annoncé par MRUK : médiane {f(np.median(d_us), 0)} µs, "
                           f"max {f(float(np.max(np.abs(d_us))), 0)} µs sur {len(d_us)} paires.")
    for (lb, e), lst in obs.items():
        for o in lst:
            pairs.setdefault((lb, round(o.t * 1e6)), {})[e] = o
    both = [p for p in pairs.values() if len(p) == 2]
    st_b = [p for p in both if is_static(p["left"])]
    rep.append("")
    if len(st_b) >= 3 and len(both) >= 8:
        R_lr0 = L.mean_rotation([L.vision_camera(p["left"], *bw(p["left"]))[0].T @ L.vision_camera(p["right"], *bw(p["right"]))[0]
                                 for p in st_b])
        errs, oms = [], []
        for p in both:
            Rl = L.vision_camera(p["left"], *bw(p["left"]))[0]
            Rr = L.vision_camera(p["right"], *bw(p["right"]))[0]
            errs.append(L.log_rot(Rr @ (Rl @ R_lr0).T))
            oms.append(p["left"].omega)
        r = L.lag_from_rotation_errors(errs, oms, min_omega, sign=1.0)
        base_v = np.median([np.linalg.norm(L.vision_camera(p["right"], *bw(p["right"]))[1] -
                                           L.vision_camera(p["left"], *bw(p["left"]))[1]) for p in st_b]) * 1e3
        base_m = np.median([np.linalg.norm(L.unity_to_cv(p["right"].frame.pos, p["right"].frame.quat, D)[1] -
                                           L.unity_to_cv(p["left"].frame.pos, p["left"].frame.quat, D)[1])
                            for p in st_b]) * 1e3
        res["stereo"] = {"lag": r, "baseline_vision_mm": float(base_v), "baseline_mruk_mm": float(base_m),
                         "pairs": len(both)}
        rep += [f"Paires où le damier est vu des deux yeux : {len(both)} (dont {len(st_b)} immobiles).",
                f"Décalage de prise droite − gauche, mesuré dans les images : "
                + (f"**{f(r['tau_ms'])} ms** (IC 95 % {f(r['ci95_ms'][0])} à {f(r['ci95_ms'][1])}, {r['n']} paires "
                   f"en mouvement)." if r else "trop peu de paires en mouvement."),
                f"Base stéréo : {f(base_v, 1)} mm d'après le damier, {f(base_m, 1)} mm d'après les poses MRUK.", ""]
    else:
        rep += [f"Trop peu de paires vues des deux yeux ({len(both)}, dont {len(st_b)} immobiles).", ""]

    # --- 4. Vitesse (H-10)
    rep += ["## 4. Effet de la vitesse (obturateur, flou)", "",
            "| |ω| (rad/s) | Images détectées | Résidu PnP médian / p95 (px) | Reprojection MRUK médiane (px) |",
            "|---|---|---|---|---|"]
    bins = [(0, 0.05), (0.05, 0.3), (0.3, 1.0), (1.0, 2.0), (2.0, 99)]
    res["speed"] = []
    tau_l = (res["tau"].get("left") or {}).get("tau_ms", 0.0) / 1e3
    for lo, hi in bins:
        sel = [o for (lb, e), lst in obs.items() if e == "left" for o in lst if lo <= np.linalg.norm(o.omega) < hi]
        if not sel:
            rep.append(f"| {lo} à {hi} | 0 | - | - |")
            continue
        K = cams[(sel[0].session, "left")].K
        rp = []
        for o in sel:
            R_wc, t_wc = L.unity_to_cv(o.frame.pos, o.frame.quat, D)
            uv = L.project(obj, *bw(o), R_wc, t_wc, K)
            rp.append(float(np.sqrt(np.mean(np.sum((uv - o.corners) ** 2, axis=1)))))
        pr = [o.rms for o in sel]
        res["speed"].append({"bin": [lo, hi], "n": len(sel), "pnp_med": pct(pr, 50), "pnp_p95": pct(pr, 95),
                             "reproj_med": pct(rp, 50)})
        rep.append(f"| {lo} à {hi} | {len(sel)} | {f(pct(pr, 50))} / {f(pct(pr, 95))} | {f(pct(rp, 50))} |")
    rep += ["", f"(τ œil gauche utilisé ailleurs : {f(tau_l * 1e3)} ms ; la reprojection ci-dessus n'est pas corrigée.)",
            ""]

    # --- 5. Distorsion (H-11)
    rep += ["## 5. Distorsion", ""]
    res["distortion"] = {}
    try:
        import cv2
        for e in EYES:
            allo = [o for (lb, ee), lst in obs.items() if ee == e for o in lst]
            if len(allo) < 10:
                continue
            allo.sort(key=lambda o: o.radius)
            pick = [allo[int(i)] for i in np.linspace(0, len(allo) - 1, min(80, len(allo)))]
            cam = cams[(pick[0].session, e)]
            K = cam.K.copy()
            if best_flip:
                K[1, 2] = cam.height - 1 - K[1, 2]
            flags = (cv2.CALIB_USE_INTRINSIC_GUESS | cv2.CALIB_FIX_FOCAL_LENGTH | cv2.CALIB_FIX_PRINCIPAL_POINT |
                     cv2.CALIB_ZERO_TANGENT_DIST | cv2.CALIB_FIX_K3)
            o3 = [obj.astype(np.float32)] * len(pick)
            i2 = [o.corners.astype(np.float32) for o in pick]
            rms0 = float(np.sqrt(np.mean([o.rms ** 2 for o in pick])))
            rms1, _, dist, _, _ = cv2.calibrateCamera(o3, i2, (cam.width, cam.height), K.copy(), np.zeros(5),
                                                      flags=flags)
            k1, k2 = float(dist.ravel()[0]), float(dist.ravel()[1])
            fx = K[0, 0]

            def shift(r_px):
                rn = r_px / fx
                return r_px * (k1 * rn ** 2 + k2 * rn ** 4)

            res["distortion"][e] = {"k1": k1, "k2": k2, "rms_pinhole": rms0, "rms_k1k2": float(rms1),
                                    "shift_px_r400": shift(400), "shift_px_r640": shift(640), "shift_px_r850": shift(850)}
            rep.append(f"- {e} : sténopé RMS {f(rms0)} px ; avec k1, k2 RMS {f(rms1)} px (k1 = {k1:.4f}, k2 = {k2:.4f}). "
                       f"Déplacement radial prédit : {f(shift(400))} px à 400 px du centre, {f(shift(640))} px à 640 px, "
                       f"{f(shift(850))} px à 850 px (coins de l'image).")
        rr = [(o.radius, o.rms) for (lb, e), lst in obs.items() if e == "left" for o in lst if is_static(o)
              or np.linalg.norm(o.omega) < 0.3]
        if rr:
            rep += ["", "| Distance moyenne des coins au centre (px) | Images | Résidu PnP médian (px) |", "|---|---|---|"]
            for lo, hi in [(0, 150), (150, 300), (300, 450), (450, 2000)]:
                sel = [r for d, r in rr if lo <= d < hi]
                rep.append(f"| {lo} à {hi} | {len(sel)} | {f(pct(sel, 50))} |")
    except Exception as ex:  # noqa: BLE001 - la distorsion ne doit pas faire perdre le reste
        rep.append(f"Calibration impossible : {ex}")
    rep.append("")

    # --- 6. Seuil proposé pour mote validate
    st_p95 = reproj.get("left", {}).get("static_p95", float("nan"))
    mv_p95 = reproj.get("left", {}).get("moving_p95", float("nan"))
    res["validate"] = {"static_p95_px": st_p95, "moving_p95_px": mv_p95}
    rep += ["## 6. Erreur de reprojection de référence (pour mote validate)", "",
            f"Œil gauche : p95 {f(st_p95)} px immobile, {f(mv_p95)} px en mouvement.", ""]
    return rep, res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sessions", nargs="+", help="ÉTIQUETTE=chemin de session, par exemple B=C:\\...\\20261016_144513")
    ap.add_argument("--square-mm", type=float, required=True, help="côté d'une case, mesuré à la règle")
    ap.add_argument("--cols", type=int, default=9)
    ap.add_argument("--rows", type=int, default=6)
    ap.add_argument("--workers", type=int, default=4, help="processus de détection (défaut 4 : chacun charge des images de 6,5 Mo)")
    ap.add_argument("--static-omega", type=float, default=0.05, help="|ω| sous lequel une image est immobile (rad/s)")
    ap.add_argument("--static-speed", type=float, default=0.01, help="vitesse sous laquelle une image est immobile (m/s)")
    ap.add_argument("--min-omega", type=float, default=0.3, help="|ω| minimal pour estimer un décalage (rad/s)")
    ap.add_argument("--select-omega", type=float, default=0.2, help="|ω| maximal des images qui choisissent la formule")
    ap.add_argument("--select-speed", type=float, default=0.05, help="vitesse maximale des mêmes images (m/s)")
    ap.add_argument("--out", type=Path, default=Path("sp2_analyse"))
    a = ap.parse_args()
    sessions = {}
    for s in a.sessions:
        lb, _, p = s.partition("=")
        sessions[lb] = Path(p)
    rep, res = analyze(sessions, a.square_mm, a.cols, a.rows, a.workers, a.static_omega, a.static_speed, a.min_omega,
                       a.select_omega, a.select_speed)
    a.out.mkdir(parents=True, exist_ok=True)
    text = "\n".join(["# SP-2 : résultats de l'analyse", "", f"Case : {a.square_mm} mm ; sessions : " +
                      ", ".join(f"{k} = {v.name}" for k, v in sessions.items()), ""] + rep)
    (a.out / "sp2_resultats.md").write_text(text, encoding="utf-8")
    (a.out / "sp2_resultats.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
