# /// script
# requires-python = ">=3.10"
# dependencies = ["grpcio-tools==1.84.0"]
# ///
"""Génère le code de mote.v1 depuis proto/mote/v1/mote.proto.

  uv run proto/generate.py

- Python : pc/mote/v1/mote_pb2.py et mote_pb2.pyi (protoc embarqué par grpcio-tools), versionnés : le paquet `mote`
  s'importe sans outil de génération.
- Rust : la crate proto/rust (mote-proto) génère ses types au build (prost + protox, sans protoc) ; la commande lance
  `cargo build` pour le vérifier.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTO = ROOT / "proto"
PY_OUT = ROOT / "pc"


def main() -> int:
    from grpc_tools import protoc

    (PY_OUT / "mote" / "v1").mkdir(parents=True, exist_ok=True)
    rc = protoc.main(["protoc", f"-I{PROTO}", f"--python_out={PY_OUT}", f"--pyi_out={PY_OUT}",
                      str(PROTO / "mote" / "v1" / "mote.proto")])
    if rc != 0:
        print(f"protoc a échoué (code {rc})", file=sys.stderr)
        return rc
    print(f"Python : {PY_OUT / 'mote' / 'v1' / 'mote_pb2.py'}")
    subprocess.run(["cargo", "build", "--quiet", "--manifest-path", str(PROTO / "rust" / "Cargo.toml")], check=True)
    print(f"Rust : crate {PROTO / 'rust'} construite")
    return 0


if __name__ == "__main__":
    sys.exit(main())
