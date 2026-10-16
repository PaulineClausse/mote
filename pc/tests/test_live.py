"""Réception live (WP-14) avec un faux casque en Python : jeton, trous et rattrapage, complétude, doublons.

Le test de bout en bout avec le vrai core (coupure de 10 s) est dans core/mote-capi/tests/live.rs.
"""
import socket
import threading
import time

import pytest

from mote.ingest.live import LiveConfig, read_frame, serve, write_frame
from mote.session import missing_seqs, read_session
from mote.v1 import mote_pb2 as pb

TOKEN = "secret-de-test"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_server(tmp_path, **kw):
    port = free_port()
    cfg = LiveConfig(host="127.0.0.1", port=port, token=TOKEN, sessions_dir=tmp_path / "sessions",
                     resend_after_s=0.2, idle_timeout_s=20.0, **kw)
    ready, result = threading.Event(), {}

    def run():
        try:
            result["path"] = serve(cfg, ready)
        except Exception as e:  # noqa: BLE001 - remonté au test
            result["error"] = e

    t = threading.Thread(target=run, daemon=True)
    t.start()
    assert ready.wait(5)
    return port, t, result


def hello(token=TOKEN, session="S1", version=1) -> bytes:
    return pb.Envelope(hello=pb.Hello(session_id=session, auth_token=token, schema_version=version)).SerializeToString()


def pose(seq: int) -> bytes:
    return pb.Envelope(channel="/pose/hmd", seq=seq, pose=pb.PoseSample(t_ns=1000 + seq)).SerializeToString()


def end(**last) -> bytes:
    return pb.Envelope(channel="/session/end", seq=0, session_end=pb.SessionEnd(
        channels=[pb.ChannelEnd(channel=c, last_seq=s) for c, s in last.items()])).SerializeToString()


def info() -> bytes:
    return pb.Envelope(channel="/session/info", seq=0,
                       session_info=pb.SessionInfo(session_id="S1", schema_version=1)).SerializeToString()


@pytest.mark.parametrize("token,version", [("mauvais", 1), ("", 1), (TOKEN, 2)])
def test_connexion_sans_jeton_valide_refusee(tmp_path, token, version):
    port, t, result = start_server(tmp_path)
    with socket.create_connection(("127.0.0.1", port)) as c:
        write_frame(c, hello(token=token, version=version))
        write_frame(c, info())
        c.settimeout(5)
        try:
            closed = c.recv(1) == b""
        except (ConnectionResetError, ConnectionAbortedError):
            closed = True       # fermeture avec des données non lues : RST, selon le système
        assert closed, "le serveur doit fermer la connexion"
    assert not (tmp_path / "sessions" / "S1.mcap").exists(), "aucune session ouverte pour une connexion refusée"
    # Le serveur reste disponible pour une connexion valide.
    with socket.create_connection(("127.0.0.1", port)) as c:
        write_frame(c, hello())
        for f in (info(), pose(0), end(**{"/session/info": 0, "/pose/hmd": 0})):
            write_frame(c, f)
        t.join(10)
    assert "path" in result, result


def test_trous_demandes_puis_session_complete(tmp_path):
    port, t, result = start_server(tmp_path)
    requests = []
    with socket.create_connection(("127.0.0.1", port)) as c:
        write_frame(c, hello())
        write_frame(c, info())
        for k in (0, 1, 4, 5):                      # 2 et 3 manquent
            write_frame(c, pose(k))
        write_frame(c, pose(1))                     # doublon, ignoré
        write_frame(c, end(**{"/session/info": 0, "/pose/hmd": 7}))   # 6 et 7 manquent aussi
        c.settimeout(5)
        wanted = set()
        while wanted != {2, 3, 6, 7}:
            ctl = pb.Control.FromString(read_frame(c))
            r = ctl.resend
            requests.append((r.channel, r.first_seq, r.last_seq))
            wanted |= set(range(r.first_seq, r.last_seq + 1))
        for k in (2, 3, 6, 7):
            write_frame(c, pose(k))
        t.join(10)
    assert ("/pose/hmd", 2, 3) in requests
    s = read_session(result["path"])
    assert missing_seqs(s) == {}
    assert sorted(m.seq for m in s.poses) == list(range(8))


def test_reconnexion_meme_session(tmp_path):
    port, t, result = start_server(tmp_path)
    with socket.create_connection(("127.0.0.1", port)) as c:
        write_frame(c, hello())
        write_frame(c, info())
        write_frame(c, pose(0))
    time.sleep(0.2)
    with socket.create_connection(("127.0.0.1", port)) as c:
        write_frame(c, hello())
        write_frame(c, pose(1))
        write_frame(c, end(**{"/session/info": 0, "/pose/hmd": 1}))
        t.join(10)
    s = read_session(result["path"])
    assert missing_seqs(s) == {} and len(s.poses) == 2
