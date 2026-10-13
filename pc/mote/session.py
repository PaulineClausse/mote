"""Lecture d'une session MCAP mote : messages protobuf `mote.v1` décodés, par canal (SPEC-64c5 §9.1)."""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mcap.reader import make_reader

from mote.v1 import mote_pb2 as pb

PACKAGE = "mote.v1"


@dataclass
class Message:
    topic: str
    seq: int
    log_time: int
    msg: Any


@dataclass
class Session:
    info: pb.SessionInfo | None = None
    end: pb.SessionEnd | None = None
    images: list[Message] = field(default_factory=list)        # /cam/{left,right}/frame
    intrinsics: list[Message] = field(default_factory=list)    # /cam/{left,right}/intrinsics
    poses: list[Message] = field(default_factory=list)         # /pose/hmd
    depth: list[Message] = field(default_factory=list)         # /depth/{left,right}
    events: list[Message] = field(default_factory=list)        # /events
    stats: list[Message] = field(default_factory=list)         # /stats
    unknown_topics: dict[str, int] = field(default_factory=dict)
    seqs: dict[str, list[int]] = field(default_factory=dict)


def message_class(schema_name: str):
    """Classe protobuf d'un nom de schéma MCAP (« mote.v1.ImageFrame »)."""
    pkg, _, name = schema_name.rpartition(".")
    if pkg != PACKAGE or name not in pb.DESCRIPTOR.message_types_by_name:
        raise ValueError(f"schéma inconnu : {schema_name!r} (attendu {PACKAGE}.<Message>)")
    return getattr(pb, name)


def iter_messages(path: Path) -> Iterator[Message]:
    """Messages dans l'ordre du fichier (l'ordre de l'ingest ne dépend donc pas de l'index)."""
    with Path(path).open("rb") as f:
        for schema, channel, m in make_reader(f).iter_messages(log_time_order=False):
            if schema is None or schema.encoding != "protobuf" or channel.message_encoding != "protobuf":
                raise ValueError(f"{channel.topic} : encodage non protobuf")
            yield Message(channel.topic, m.sequence, m.log_time, message_class(schema.name).FromString(m.data))


def read_session(path: Path) -> Session:
    s = Session()
    for m in iter_messages(path):
        s.seqs.setdefault(m.topic, []).append(m.seq)
        t = m.topic
        if t == "/session/info":
            s.info = m.msg
        elif t == "/session/end":
            s.end = m.msg
        elif t in ("/cam/left/frame", "/cam/right/frame"):
            s.images.append(m)
        elif t in ("/cam/left/intrinsics", "/cam/right/intrinsics"):
            s.intrinsics.append(m)
        elif t == "/pose/hmd":
            s.poses.append(m)
        elif t in ("/depth/left", "/depth/right"):
            s.depth.append(m)
        elif t == "/events":
            s.events.append(m)
        elif t == "/stats":
            s.stats.append(m)
        else:
            s.unknown_topics[t] = s.unknown_topics.get(t, 0) + 1
    return s


def missing_seqs(s: Session) -> dict[str, list[int]]:
    """Trous par canal, d'après les seq contigus à partir de 0 et le dernier seq annoncé par /session/end."""
    last = {c.channel: c.last_seq for c in s.end.channels} if s.end else {}
    out = {}
    for topic in sorted(set(s.seqs) | set(last)):
        have = set(s.seqs.get(topic, []))
        top = last.get(topic, max(have) if have else -1)
        gaps = [k for k in range(top + 1) if k not in have]
        if gaps:
            out[topic] = gaps
    return out
