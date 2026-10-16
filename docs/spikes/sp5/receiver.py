"""SP-5 : récepteur TCP côté PC. Mesure le débit soutenu casque -> PC (H-06, ADR-c36f).

Accepte une connexion, lit pendant `--seconds` à partir du premier octet reçu, puis ferme. Compte les octets par
seconde et rend : débit moyen, minimum et maximum sur fenêtres glissantes de 10 s (pas de 1 s), et la série par seconde.

  python receiver.py --port 5001 --seconds 180 --out sp5_result.json

Côté casque, l'émetteur est toybox nc (présent sur Android), qui envoie /dev/zero aussi vite que TCP le permet :
  adb shell "toybox nc <IP du PC> 5001 < /dev/zero"
Bibliothèque standard seulement.
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
import time

WINDOW_S = 10


def summarize(per_second: list[int], window: int = WINDOW_S) -> dict:
    """Débits en Mbit/s à partir des octets reçus par seconde."""
    mbps = [b * 8 / 1e6 for b in per_second]
    windows = [sum(mbps[i:i + window]) / window for i in range(0, len(mbps) - window + 1)]
    total = sum(per_second)
    return {
        "seconds": len(per_second),
        "bytes": total,
        "mean_mbps": round(total * 8 / 1e6 / len(per_second), 2) if per_second else 0.0,
        "min_10s_mbps": round(min(windows), 2) if windows else None,
        "max_10s_mbps": round(max(windows), 2) if windows else None,
        "per_second_mbps": [round(m, 2) for m in mbps],
    }


def receive(port: int, seconds: int, bind: str = "0.0.0.0", ready=None) -> list[int]:
    """Octets reçus par seconde pleine, pendant `seconds` secondes à partir du premier octet."""
    with socket.create_server((bind, port)) as srv:
        if ready:
            ready()
        print(f"en attente sur {bind}:{port} ...", file=sys.stderr, flush=True)
        conn, peer = srv.accept()
        print(f"connexion de {peer[0]}:{peer[1]}", file=sys.stderr, flush=True)
        with conn:
            conn.settimeout(5.0)
            buf = bytearray(1 << 20)
            per_second = [0] * seconds
            t0 = None
            while True:
                try:
                    n = conn.recv_into(buf)
                except TimeoutError:
                    print("aucune donnée depuis 5 s : arrêt", file=sys.stderr)
                    break
                if n == 0:
                    print("connexion fermée par l'émetteur", file=sys.stderr)
                    break
                now = time.monotonic()
                if t0 is None:
                    t0 = now
                k = int(now - t0)
                if k >= seconds:
                    break
                per_second[k] += n
                if k and per_second[k] == n:   # première lecture d'une nouvelle seconde
                    print(f"{k:4d} s  {per_second[k - 1] * 8 / 1e6:7.1f} Mbit/s", file=sys.stderr, flush=True)
            elapsed = int(time.monotonic() - t0) if t0 is not None else 0
    return per_second[:min(seconds, max(elapsed, 0))]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=5001)
    ap.add_argument("--seconds", type=int, default=180)
    ap.add_argument("--out", default="sp5_result.json")
    a = ap.parse_args()
    per_second = receive(a.port, a.seconds)
    r = summarize(per_second)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1)
    print(json.dumps({k: v for k, v in r.items() if k != "per_second_mbps"}))
    if r["seconds"] < a.seconds:
        print(f"attention : {r['seconds']} s mesurées sur {a.seconds} demandées", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
