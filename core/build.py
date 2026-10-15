# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Construit le core : libmote.so pour le casque (arm64-v8a) et la bibliothèque du PC hôte, plus mote.h.

  uv run core/build.py                       # les deux
  uv run core/build.py --host                # PC hôte seulement (sans NDK)
  uv run core/build.py --android --ndk C:\ndk\android-ndk-r27c

Sorties dans core/dist/ :
  include/mote.h                 header C (cbindgen, aussi versionné dans core/mote-capi/include/)
  android/arm64-v8a/libmote.so   pour Assets/Plugins/Android/arm64-v8a/ de l'hôte Unity
  host/                          libmote.so, libmote.dylib ou mote.dll (+ mote.dll.lib), et la lib statique

Prérequis : rustup ; pour Android : `rustup target add aarch64-linux-android`,
`cargo install cargo-ndk`, NDK r27c (option --ndk ou ANDROID_NDK_HOME). Sous Windows, garder le NDK et le dossier
target (CARGO_TARGET_DIR) sur des chemins courts : le clang du NDK échoue au-delà de 260 caractères.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

CORE = Path(__file__).resolve().parent
DIST = CORE / "dist"
ABI = "arm64-v8a"
TRIPLE = "aarch64-linux-android"
API_LEVEL = "32"  # Quest 3S, comme SP-4


def run(cmd: list[str], env: dict[str, str] | None = None) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=CORE, env=env, check=True)


def target_dir() -> Path:
    return Path(os.environ.get("CARGO_TARGET_DIR", CORE / "target"))


def copy(src: Path, dst_dir: Path) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst_dir / src.name)
    print(f"  -> {(dst_dir / src.name).relative_to(CORE)}")


def build_host() -> None:
    run(["cargo", "build", "--release", "-p", "mote-capi"])
    out = target_dir() / "release"
    names = ["libmote.so", "libmote.dylib", "libmote.a", "mote.dll", "mote.dll.lib", "mote.lib"]
    found = [out / n for n in names if (out / n).exists()]
    if not found:
        sys.exit(f"aucune bibliothèque dans {out}")
    for f in found:
        copy(f, DIST / "host")


def build_android(ndk: str | None) -> None:
    env = dict(os.environ)
    if ndk:
        env["ANDROID_NDK_HOME"] = ndk
    if not env.get("ANDROID_NDK_HOME") and not env.get("ANDROID_NDK_ROOT"):
        sys.exit("NDK introuvable : passer --ndk <chemin> ou définir ANDROID_NDK_HOME")
    run(["cargo", "ndk", "-t", ABI, "-P", API_LEVEL, "build", "--release", "-p", "mote-capi"], env)
    copy(target_dir() / TRIPLE / "release" / "libmote.so", DIST / "android" / ABI)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--host", action="store_true", help="PC hôte seulement")
    p.add_argument("--android", action="store_true", help="arm64-v8a seulement")
    p.add_argument("--ndk", help="chemin du NDK (sinon ANDROID_NDK_HOME)")
    a = p.parse_args()
    both = not (a.host or a.android)
    if a.host or both:
        build_host()
    if a.android or both:
        build_android(a.ndk)
    # build.rs de mote-capi régénère le header à chaque build.
    copy(CORE / "mote-capi" / "include" / "mote.h", DIST / "include")


if __name__ == "__main__":
    main()
