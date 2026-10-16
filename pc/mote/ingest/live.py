"""Réception du flux live (SPEC-9df2, ADR-c36f) : `mote ingest --listen`.

Le casque ouvre une connexion TCP ; chaque trame est une taille sur 4 octets (ordre réseau) suivie d'une `Envelope`.
La première est `Hello` : un jeton ou une version de schéma inattendus ferment la connexion. Les messages sont écrits
au fil de l'eau dans un MCAP de session côté PC (ordre d'arrivée, `sequence` = seq du casque). Les trous de seq sont
demandés par `ResendRequest`, puis redemandés tant qu'ils manquent. La session est complète quand `/session/end` est
arrivé et que tous les seq qu'il annonce sont présents : elle contient alors les mêmes messages que celle du casque.

Les délais sont des réglages (`LiveConfig`) : ils dépendent du réseau de chacun.
"""
from __future__ import annotations

import hmac
import socket
import struct
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from google.protobuf import descriptor_pb2
from mcap.writer import CompressionType, Writer

from mote.v1 import mote_pb2 as pb

MAX_FRAME = 64 << 20            # SPEC-9df2 : constante du protocole, partagée avec le casque
SCHEMA_VERSIONS = {1}

# Canal -> (champ de l'Envelope, message protobuf) ; SPEC-64c5 §9.1.
CHANNELS = {
    "/session/info": "session_info",
    "/cam/left/frame": "image", "/cam/right/frame": "image",
    "/cam/left/intrinsics": "intrinsics", "/cam/right/intrinsics": "intrinsics",
    "/pose/hmd": "pose",
    "/depth/left": "depth", "/depth/right": "depth",
    "/events": "event",
    "/stats": "stats",
    "/session/end": "session_end",
}


@dataclass
class LiveConfig:
    host: str = "0.0.0.0"
    port: int = 5000
    token: str = ""
    sessions_dir: Path = Path("sessions")
    # Délai avant de redemander un seq déjà demandé et toujours absent. Plus long sur un réseau lent ou chargé.
    resend_after_s: float = 2.0
    # Abandon si rien n'arrive pendant ce délai (0 : attendre indéfiniment).
    idle_timeout_s: float = 0.0
    log: object = sys.stderr


def _file_descriptor_set() -> bytes:
    fdp = descriptor_pb2.FileDescriptorProto()
    pb.DESCRIPTOR.CopyToProto(fdp)
    return descriptor_pb2.FileDescriptorSet(file=[fdp]).SerializeToString()


def read_frame(sock: socket.socket) -> bytes | None:
    """Une trame, ou None si la connexion est fermée ; ValueError au-delà de MAX_FRAME."""
    head = _recv_exact(sock, 4)
    if head is None:
        return None
    (n,) = struct.unpack(">I", head)
    if n > MAX_FRAME:
        raise ValueError(f"trame de {n} octets, au-delà de 64 Mo")
    return _recv_exact(sock, n)


def write_frame(sock: socket.socket, payload: bytes) -> None:
    sock.sendall(struct.pack(">I", len(payload)) + payload)


def _recv_exact(sock: socket.socket, n: int) -> bytes | None:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return bytes(buf)


class Session:
    """Session reçue : MCAP côté PC, seq reçus par canal, trous à demander."""

    def __init__(self, session_id: str, path: Path):
        self.session_id = session_id
        self.path = path
        self.lock = threading.Lock()
        self.seqs: dict[str, set[int]] = {}
        self.end: dict[str, int] | None = None
        self.requested: dict[tuple[str, int], float] = {}
        self._f = path.open("wb")
        self._w = Writer(self._f, compression=CompressionType.ZSTD)
        self._w.start(profile="", library="mote ingest --listen")
        fds = _file_descriptor_set()
        self._schemas: dict[str, int] = {}
        self._channels: dict[str, int] = {}
        for topic, field in CHANNELS.items():
            name = "mote.v1." + pb.Envelope.DESCRIPTOR.fields_by_name[field].message_type.name
            if name not in self._schemas:
                self._schemas[name] = self._w.register_schema(name=name, encoding="protobuf", data=fds)
            self._channels[topic] = self._w.register_channel(topic=topic, message_encoding="protobuf",
                                                             schema_id=self._schemas[name])

    def add(self, env: pb.Envelope) -> bool:
        """Écrit un message s'il est nouveau ; renvoie False pour un doublon ou un canal inconnu."""
        field = CHANNELS.get(env.channel)
        if field is None or env.WhichOneof("body") != field:
            return False
        with self.lock:
            got = self.seqs.setdefault(env.channel, set())
            if env.seq in got:
                return False
            msg = getattr(env, field)
            t = getattr(msg, "t_ns", 0) or getattr(msg, "start_t_ns", 0)
            self._w.add_message(channel_id=self._channels[env.channel], log_time=max(t, 0), publish_time=max(t, 0),
                                sequence=env.seq, data=msg.SerializeToString())
            got.add(env.seq)
            self.requested.pop((env.channel, env.seq), None)
            if env.channel == "/session/end":
                self.end = {c.channel: c.last_seq for c in msg.channels}
            return True

    def missing(self) -> dict[str, list[int]]:
        """Seq manquants par canal : sous le plus grand reçu, et jusqu'au dernier annoncé par /session/end."""
        with self.lock:
            out = {}
            for topic in set(self.seqs) | set(self.end or {}):
                got = self.seqs.get(topic, set())
                top = (self.end or {}).get(topic, max(got) if got else -1)
                gaps = [k for k in range(top + 1) if k not in got]
                if gaps:
                    out[topic] = gaps
            return out

    def complete(self) -> bool:
        return self.end is not None and "/session/end" in self.seqs and not self.missing()

    def due_requests(self, now: float, resend_after: float) -> list[tuple[str, int, int]]:
        """Plages à demander : seq manquants jamais demandés, ou demandés depuis plus de `resend_after`."""
        ranges = []
        for topic, gaps in self.missing().items():
            due = [k for k in gaps if now - self.requested.get((topic, k), -1e18) >= resend_after]
            for k in due:
                self.requested[(topic, k)] = now
            start = prev = None
            for k in due:
                if start is None:
                    start = prev = k
                elif k == prev + 1:
                    prev = k
                else:
                    ranges.append((topic, start, prev))
                    start = prev = k
            if start is not None:
                ranges.append((topic, start, prev))
        return ranges

    def close(self) -> None:
        with self.lock:
            self._w.finish()
            self._f.close()


def _hello_ok(cfg: LiveConfig, env: pb.Envelope) -> bool:
    if env.WhichOneof("body") != "hello":
        return False
    h = env.hello
    return hmac.compare_digest(h.auth_token.encode(), cfg.token.encode()) and h.schema_version in SCHEMA_VERSIONS


def serve(cfg: LiveConfig, ready: threading.Event | None = None) -> Path:
    """Reçoit une session jusqu'à ce qu'elle soit complète ; renvoie le chemin du MCAP côté PC."""
    cfg.sessions_dir.mkdir(parents=True, exist_ok=True)
    session: Session | None = None
    last_activity = time.monotonic()
    with socket.create_server((cfg.host, cfg.port)) as srv:
        srv.settimeout(0.5)
        if ready is not None:
            ready.set()
        print(f"mote ingest : en attente sur {cfg.host}:{cfg.port}", file=cfg.log, flush=True)
        while session is None or not session.complete():
            if cfg.idle_timeout_s and time.monotonic() - last_activity > cfg.idle_timeout_s:
                raise TimeoutError(f"rien reçu depuis {cfg.idle_timeout_s} s")
            try:
                conn, peer = srv.accept()
            except TimeoutError:
                continue
            with conn:
                conn.settimeout(None)
                try:
                    first = read_frame(conn)
                    hello = pb.Envelope.FromString(first) if first is not None else None
                except (ValueError, OSError):
                    hello = None
                if hello is None or not _hello_ok(cfg, hello):
                    print(f"mote ingest : connexion de {peer[0]} refusée (jeton ou version)", file=cfg.log, flush=True)
                    continue
                sid = hello.hello.session_id
                if session is None:
                    session = Session(sid, cfg.sessions_dir / f"{sid}.mcap")
                elif sid != session.session_id:
                    print(f"mote ingest : session {sid} refusée, {session.session_id} en cours", file=cfg.log,
                          flush=True)
                    continue
                print(f"mote ingest : {peer[0]} connecté, session {sid}", file=cfg.log, flush=True)
                last_activity = time.monotonic()
                last_activity = _receive(cfg, conn, session, last_activity)
                print("mote ingest : connexion fermée", file=cfg.log, flush=True)
    session.close()
    return session.path


def _receive(cfg: LiveConfig, conn: socket.socket, session: Session, last_activity: float) -> float:
    """Reçoit jusqu'à la fin de la connexion ou la complétude de la session ; demande les trous au fil de l'eau."""
    send_lock = threading.Lock()
    stop = threading.Event()

    def request_gaps():
        for topic, first, last in session.due_requests(time.monotonic(), cfg.resend_after_s):
            ctl = pb.Control(resend=pb.ResendRequest(channel=topic, first_seq=first, last_seq=last))
            with send_lock:
                write_frame(conn, ctl.SerializeToString())

    def ticker():
        while not stop.wait(min(0.5, cfg.resend_after_s)):
            try:
                request_gaps()
            except OSError:
                return

    t = threading.Thread(target=ticker, daemon=True)
    t.start()
    try:
        while not session.complete():
            try:
                frame = read_frame(conn)
            except (ValueError, OSError):
                break
            if frame is None:
                break
            last_activity = time.monotonic()
            session.add(pb.Envelope.FromString(frame))
    finally:
        stop.set()
        t.join()
    return last_activity
