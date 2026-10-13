"""`mote ingest --replay` : d'un fichier MCAP au répertoire de dataset (SPEC-834a §11.1, SPEC-3d2a §7.3).

Étapes faites ici : décodage des images, poses par image (ou interpolées sur /pose/hmd), conversion vers le repère
canonique, découpage aux RECENTER (le plus long segment est gardé, SPEC-64c5 §9.4), intrinsèques ramenées à la taille
des images. Hors de cette étape : profondeur (WP-10), sélection finale et hold-out (WP-09, WP-13), validation de la
conversion de repère (WP-08).

Le répertoire produit :
- `images/<left|right>/<pair_id:012d>.jpg` : le JPEG d'origine, octet pour octet (réencoder perdrait de la qualité ;
  il est décodé pour vérification) ; `.png` pour RAW_RGBA ;
- `frames.jsonl` : une ligne par image, dans l'ordre de capture, poses `world_from_camera` canoniques (OpenCV) ;
- `session.json` : SessionInfo, segments, comptes, empreinte du MCAP source, conversion appliquée.

Sorties identiques bit à bit d'une exécution à l'autre (NFR-07) : ordre fixé, JSON trié, flottants en Python pur, pas
de date d'exécution ni de chemin absolu.
"""
from __future__ import annotations

import bisect
import hashlib
import io
import json
from pathlib import Path

from PIL import Image

import mote
from mote import geometry as g
from mote.session import Message, missing_seqs, read_session
from mote.v1 import mote_pb2 as pb

MAX_INTERP_GAP_NS = 100_000_000      # au-delà, pas d'interpolation de la pose du casque
CAMERAS = ("left", "right")


def pose3_matrix(p: pb.Pose3) -> g.Mat:
    return g.pose_matrix((p.px, p.py, p.pz), (p.qx, p.qy, p.qz, p.qw))


def to_canonical(m: g.Mat, convention: int) -> g.Mat:
    if convention == pb.UNITY:
        return g.unity_to_canonical(m)
    if convention == pb.OPENXR:
        return g.openxr_to_canonical(m)
    raise ValueError(f"convention de pose non prise en charge : {pb.PoseConvention.Name(convention)}")


def interpolate_hmd(samples: list[pb.PoseSample], t_ns: int, max_gap_ns: int = MAX_INTERP_GAP_NS) -> g.Mat | None:
    """Pose du casque à t_ns (lerp en translation, slerp en rotation, SPEC-64c5 §9.3), dans la convention des
    échantillons ; None hors de la plage ou si les deux échantillons encadrants sont trop éloignés."""
    times = [s.t_ns for s in samples]
    i = bisect.bisect_left(times, t_ns)
    if i < len(times) and times[i] == t_ns:
        return pose3_matrix(samples[i].world_from_hmd)
    if i == 0 or i == len(times) or times[i] - times[i - 1] > max_gap_ns:
        return None
    a, b = samples[i - 1], samples[i]
    s = (t_ns - a.t_ns) / (b.t_ns - a.t_ns)
    pa, pb_ = a.world_from_hmd, b.world_from_hmd
    p = (g.lerp(pa.px, pb_.px, s), g.lerp(pa.py, pb_.py, s), g.lerp(pa.pz, pb_.pz, s))
    q = g.slerp((pa.qx, pa.qy, pa.qz, pa.qw), (pb_.qx, pb_.qy, pb_.qz, pb_.qw), s)
    return g.pose_matrix(p, q)


def scaled_intrinsics(k: pb.CameraIntrinsics, w: int, h: int) -> dict:
    """Intrinsèques ramenées à la taille de l'image (MRUK les donne pour le capteur, l'image peut être plus petite)."""
    sx, sy = w / k.width, h / k.height
    if abs(sx - sy) > 1e-6:
        raise ValueError(f"rapport d'aspect différent : intrinsèques {k.width}x{k.height}, image {w}x{h}")
    return {"fx": k.fx * sx, "fy": k.fy * sy, "cx": k.cx * sx, "cy": k.cy * sy,
            "model": pb.DistortionModel.Name(k.model), "dist": list(k.dist)}


def dumps(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _camera(m: Message) -> str:
    return m.topic.split("/")[2]


def ingest_replay(mcap_path: Path, out: Path) -> dict:
    """Construit le dataset de `mcap_path` dans `out` (vide ou absent). Renvoie le contenu de session.json."""
    mcap_path, out = Path(mcap_path), Path(out)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"{out} n'est pas vide : le dataset est en ajout seul, choisir un autre dossier")
    s = read_session(mcap_path)

    intr: dict[str, list[tuple[int, pb.CameraIntrinsics]]] = {c: [] for c in CAMERAS}
    for m in s.intrinsics:
        intr[_camera(m)].append((m.log_time, m.msg))
    hmd = sorted((m.msg for m in s.poses), key=lambda p: p.t_ns)
    recenters = sorted(m.msg.t_ns for m in s.events if m.msg.type == pb.RECENTER)

    def intrinsics_at(cam: str, log_time: int) -> pb.CameraIntrinsics | None:
        cands = [k for t, k in intr[cam] if t <= log_time] or [k for _, k in intr[cam][:1]]
        return cands[-1] if cands else None

    dropped = {"no_pose": 0, "no_intrinsics": 0, "bad_image": 0, "unknown_convention": 0, "other_segments": 0}
    records: list[tuple[dict, bytes, str]] = []
    images = sorted(s.images, key=lambda m: (m.msg.t_ns, CAMERAS.index(_camera(m)), m.msg.pair_id, m.seq))
    for m in images:
        f, cam = m.msg, _camera(m)
        k = intrinsics_at(cam, m.log_time)
        if k is None:
            dropped["no_intrinsics"] += 1
            continue
        # pose : par image si fournie, sinon pose du casque interpolée composée avec les extrinsèques
        try:
            if f.HasField("world_from_camera"):
                c2w, source = to_canonical(pose3_matrix(f.world_from_camera), f.convention), "frame"
            else:
                hm = interpolate_hmd(hmd, f.t_ns) if hmd else None
                conv = hmd[0].convention if hmd else pb.POSE_CONVENTION_UNSPECIFIED
                if hm is None or not k.HasField("hmd_from_camera") or k.convention != conv:
                    dropped["no_pose"] += 1
                    continue
                c2w, source = to_canonical(g.matmul(hm, pose3_matrix(k.hmd_from_camera)), conv), "hmd_interp"
        except ValueError:
            dropped["unknown_convention"] += 1
            continue
        try:
            kk = scaled_intrinsics(k, f.width, f.height)
            if f.codec == pb.JPEG:
                img = Image.open(io.BytesIO(f.data))
                img.load()
                if img.size != (f.width, f.height):
                    raise ValueError("taille JPEG")
                data, ext = bytes(f.data), "jpg"
            elif f.codec == pb.RAW_RGBA:
                img = Image.frombytes("RGBA", (f.width, f.height), bytes(f.data))
                buf = io.BytesIO()
                img.save(buf, format="PNG", compress_level=6)
                data, ext = buf.getvalue(), "png"
            else:
                raise ValueError("codec")
        except (ValueError, OSError):
            dropped["bad_image"] += 1
            continue
        rec = {
            "file": f"images/{cam}/{f.pair_id:012d}.{ext}", "camera": cam, "pair_id": f.pair_id, "seq": m.seq,
            "t_ns": f.t_ns, "src_time_ns": f.src_time_ns, "src_domain": pb.TimeDomain.Name(f.src_domain),
            "codec": pb.ImageCodec.Name(f.codec), "width": f.width, "height": f.height, **kk,
            "segment": bisect.bisect_right(recenters, f.t_ns), "pose_source": source,
            "world_from_camera": c2w, "blur_score": f.blur_score,
            "exposure_ns": f.exposure_ns if f.HasField("exposure_ns") else None,
            "iso": f.iso if f.HasField("iso") else None,
        }
        records.append((rec, data, ext))

    counts: dict[int, int] = {}
    for rec, _, _ in records:
        counts[rec["segment"]] = counts.get(rec["segment"], 0) + 1
    kept = max(sorted(counts), key=lambda k: counts[k]) if counts else 0   # à égalité, le premier
    bounds = [None, *recenters, None]
    segments = [{"index": i, "t_start_ns": bounds[i], "t_end_ns": bounds[i + 1], "images": counts.get(i, 0)}
                for i in range(len(recenters) + 1)]

    out.mkdir(parents=True, exist_ok=True)
    lines = []
    for rec, data, _ in records:
        if rec["segment"] != kept:
            dropped["other_segments"] += 1
            continue
        p = out / rec["file"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        lines.append(dumps(rec))
    (out / "frames.jsonl").write_text("".join(line + "\n" for line in lines), encoding="utf-8", newline="\n")

    info = s.info
    summary = {
        "dataset_version": 1,
        "ingest_version": mote.__version__,
        "pose_conversion": g.POSE_CONVERSION,
        "canonical_frame": "monde main droite, métrique ; caméras OpenCV (x droite, y bas, z avant) ; world_from_camera",
        "source": {"file": mcap_path.name, "sha256": hashlib.sha256(mcap_path.read_bytes()).hexdigest()},
        "session_info": None if info is None else {
            "schema_version": info.schema_version, "session_id": info.session_id, "start_unix_ns": info.start_unix_ns,
            "start_t_ns": info.start_t_ns, "device_model": info.device_model, "os_build": info.os_build,
            "sdk_versions": info.sdk_versions, "host_kind": info.host_kind, "core_version": info.core_version,
            "tracking_space": info.tracking_space, "config_json": info.config_json},
        "complete": s.end is not None and not missing_seqs(s),
        "missing_seqs": missing_seqs(s),
        "segments": segments,
        "kept_segment": kept,
        "images": len(lines),
        "dropped": dropped,
        "unknown_topics": dict(sorted(s.unknown_topics.items())),
    }
    (out / "session.json").write_text(json.dumps(summary, sort_keys=True, ensure_ascii=False, indent=1) + "\n",
                                      encoding="utf-8", newline="\n")
    return summary
