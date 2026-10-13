# /// script
# requires-python = ">=3.10"
# dependencies = ["mcap==1.3.1", "protobuf==7.35.1", "pillow>=10"]
# ///
"""SP-4 : preuve qu'un MCAP écrit sur le casque se lit sur PC (ADR-5955), avec le code Python de mote.v1.

  uv run docs/spikes/sp4/verify_mcap.py <fichier.mcap> [--out <dossier>]

Vérifie : schémas protobuf auto-décrits (FileDescriptorSet dans le MCAP) ; chaque message décodé par
pc/mote/v1/mote_pb2 ; séquences contiguës par canal ; /session/end cohérent avec le dernier seq ; chaque JPEG décodé,
à la taille annoncée. Extrait la première paire en JPEG dans --out. Code de sortie 0 si tout est conforme.
"""
from __future__ import annotations

import argparse
import io
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pc"))
from google.protobuf import descriptor_pb2  # noqa: E402
from mcap.reader import make_reader  # noqa: E402
from PIL import Image  # noqa: E402

from mote.v1 import mote_pb2 as pb  # noqa: E402

TYPES = {"mote.v1.ImageFrame": pb.ImageFrame, "mote.v1.SessionInfo": pb.SessionInfo,
         "mote.v1.SessionEnd": pb.SessionEnd}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mcap", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    problems: list[str] = []
    seqs: dict[str, list[int]] = defaultdict(list)
    jpeg_bytes, t_min, t_max, n_img = 0, None, None, 0
    first: dict[str, bytes] = {}
    info = end = None
    with a.mcap.open("rb") as f:
        reader = make_reader(f)
        summary = reader.get_summary()
        for schema, channel, message in reader.iter_messages(log_time_order=False):
            if schema.encoding != "protobuf" or channel.message_encoding != "protobuf":
                problems.append(f"{channel.topic} : encodage {schema.encoding}/{channel.message_encoding}")
                continue
            fds = descriptor_pb2.FileDescriptorSet.FromString(schema.data)
            if not any(fd.package == "mote.v1" for fd in fds.file):
                problems.append(f"{channel.topic} : schéma sans paquet mote.v1")
            cls = TYPES.get(schema.name)
            if cls is None:
                problems.append(f"{channel.topic} : type inattendu {schema.name}")
                continue
            msg = cls.FromString(message.data)
            seqs[channel.topic].append(message.sequence)
            if cls is pb.ImageFrame:
                n_img += 1
                if msg.codec != pb.JPEG:
                    problems.append(f"{channel.topic} seq {message.sequence} : codec {msg.codec}")
                    continue
                img = Image.open(io.BytesIO(msg.data))
                img.load()
                if img.size != (msg.width, msg.height):
                    problems.append(f"{channel.topic} seq {message.sequence} : {img.size} au lieu de "
                                    f"{(msg.width, msg.height)}")
                jpeg_bytes += len(msg.data)
                t_min = msg.t_ns if t_min is None else min(t_min, msg.t_ns)
                t_max = msg.t_ns if t_max is None else max(t_max, msg.t_ns)
                first.setdefault(channel.topic, msg.data)
            elif cls is pb.SessionInfo:
                info = msg
            else:
                end = msg

    for topic, s in seqs.items():
        if sorted(s) != list(range(len(s))):
            problems.append(f"{topic} : séquences non contiguës ({len(s)} messages)")
    if end is None:
        problems.append("pas de /session/end : le core n'a pas fermé le fichier")
    else:
        for c in end.channels:
            if c.last_seq != len(seqs.get(c.channel, [])) - 1:
                problems.append(f"/session/end : {c.channel} last_seq {c.last_seq}, {len(seqs.get(c.channel, []))} reçus")
    if info is None:
        problems.append("pas de /session/info")

    if a.out and first:
        a.out.mkdir(parents=True, exist_ok=True)
        for topic, data in first.items():
            (a.out / (topic.strip("/").replace("/", "_") + ".jpg")).write_bytes(data)

    dur = (t_max - t_min) / 1e9 if t_min is not None and t_max != t_min else 0.0
    size = a.mcap.stat().st_size
    print(f"Fichier : {a.mcap.name}, {size / 1e6:.1f} Mo ; chunks : "
          f"{len(summary.chunk_indexes) if summary else '?'} ; compression : "
          f"{sorted({ci.compression for ci in summary.chunk_indexes}) if summary else '?'}")
    print(f"Écrit par : {info.core_version if info else '?'} ; config : {info.config_json if info else '?'}")
    print("| Canal | messages | dernier seq |")
    print("|---|---|---|")
    for topic in sorted(seqs):
        print(f"| `{topic}` | {len(seqs[topic])} | {max(seqs[topic])} |")
    if n_img:
        print(f"\n{n_img} images JPEG décodées, {jpeg_bytes / n_img / 1024:.0f} Ko en moyenne"
              + (f" ; {dur:.1f} s couvertes, {8 * jpeg_bytes / dur / 1e6:.1f} Mbit/s d'images sans sélection"
                 if dur > 0 else ""))
    print("\nConforme : oui" if not problems else "\nConforme : NON\n- " + "\n- ".join(problems[:20]))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
