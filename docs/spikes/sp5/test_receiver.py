"""Tests du récepteur SP-5 : calcul des fenêtres, et une mesure réelle en boucle locale."""
import socket
import threading
import time

from receiver import receive, summarize


def test_summary_windows_of_ten_seconds():
    # 12 s : 10 s à 12,5 Mo/s (100 Mbit/s), puis 2 s à 6,25 Mo/s (50 Mbit/s).
    per_second = [12_500_000] * 10 + [6_250_000] * 2
    r = summarize(per_second)
    assert r["seconds"] == 12
    assert r["max_10s_mbps"] == 100.0
    assert r["min_10s_mbps"] == 90.0          # fenêtre 2..11 : 8 s à 100, 2 s à 50
    assert r["mean_mbps"] == round((10 * 100 + 2 * 50) / 12, 2)


def test_short_run_has_no_window():
    r = summarize([1_000_000] * 3)
    assert r["min_10s_mbps"] is None and r["seconds"] == 3


def test_loopback_measures_what_was_sent():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    ready = threading.Event()
    result = {}
    t = threading.Thread(target=lambda: result.setdefault("ps", receive(port, 2, "127.0.0.1", ready.set)))
    t.start()
    ready.wait(5)
    sent = 0
    chunk = b"\0" * 65536
    with socket.create_connection(("127.0.0.1", port)) as c:
        end = time.monotonic() + 3
        try:
            while time.monotonic() < end:
                c.sendall(chunk)
                sent += len(chunk)
        except OSError:
            pass                                   # le récepteur ferme après 2 s
    t.join(10)
    ps = result["ps"]
    assert len(ps) == 2 and all(b > 0 for b in ps), ps
    assert sum(ps) <= sent
