"""Vérifie qu'une session écrite par le core se lit avec la bibliothèque Python mcap, par le lecteur de l'ingest
(pc/mote/session.py) : critère de WP-05 (TASK-3159), côté PC.

  cd core
  MOTE_KEEP_SESSION_DIR=<dir> cargo test -p mote-capi --test session_file apres_stop
  uv run --project ../pc python mote-mcap/tests/check_session.py <dir>
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pc"))

from mcap.reader import make_reader  # noqa: E402

from mote.session import missing_seqs, read_session  # noqa: E402

# SPEC-64c5 §9.1
CHANNELS = {
    "/session/info", "/cam/left/frame", "/cam/right/frame", "/cam/left/intrinsics", "/cam/right/intrinsics",
    "/pose/hmd", "/depth/left", "/depth/right", "/events", "/stats", "/session/end",
}


def main() -> int:
    files = sorted(Path(sys.argv[1]).glob("*.mcap"))
    if len(files) != 1:
        print(f"check_session : un fichier .mcap attendu, trouvé {files}")
        return 1
    path = files[0]
    with path.open("rb") as f:
        summary = make_reader(f).get_summary()
    declared = {c.topic for c in summary.channels.values()}
    s = read_session(path)
    errors = []
    if declared != CHANNELS:
        errors.append(f"canaux {sorted(declared ^ CHANNELS)} en trop ou manquants")
    if s.unknown_topics:
        errors.append(f"canaux inconnus de l'ingest : {s.unknown_topics}")
    for topic, seqs in s.seqs.items():
        if seqs != list(range(len(seqs))):
            errors.append(f"{topic} : seq non contigus à partir de 0")
    if s.info is None or s.info.session_id != path.stem:
        errors.append("/session/info absent ou session_id différent du nom du fichier")
    if s.end is None:
        errors.append("/session/end absent")
    else:
        announced = {c.channel: c.last_seq for c in s.end.channels}
        expected = {t: len(q) - 1 for t, q in s.seqs.items() if t != "/session/end"}
        if announced != expected:
            errors.append(f"/session/end annonce {announced}, attendu {expected}")
    if missing_seqs(s):
        errors.append(f"trous selon l'ingest : {missing_seqs(s)}")
    for e in errors:
        print("check_session :", e)
    if not errors:
        counts = {t: len(q) for t, q in sorted(s.seqs.items())}
        print(f"check_session : ok, {path.name}, {counts}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
