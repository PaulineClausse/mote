# core

Workspace Rust du core natif (`libmote.so`, API C). Décisions : ADR-8d03 (Rust, cargo-ndk, cbindgen), ADR-7a16 (API C
en push) ; API : SPEC-fdb8 (`ank show SPEC-fdb8`).

| Crate | Rôle |
|---|---|
| `mote-capi` | API C ; produit `libmote.so` / `mote.dll` et `include/mote.h` (cbindgen, au build) |
| `mote-core` | sélection des paires, files, orchestration, horloge |
| `mote-codec` | encodage JPEG |
| `mote-mcap` | écriture du fichier MCAP de session |
| `mote-net` | transport live et rattrapage |

## Construire

```sh
uv run core/build.py                                   # casque (arm64-v8a) et PC hôte
uv run core/build.py --host                            # PC hôte seulement, sans NDK
uv run core/build.py --android --ndk <chemin du NDK>   # casque seulement
```

Sorties dans `core/dist/` : `android/arm64-v8a/libmote.so` (à copier dans `Assets/Plugins/Android/arm64-v8a/` de
l'hôte Unity), `host/` (bibliothèque du PC) et `include/mote.h`.

Prérequis :
- [rustup](https://rustup.rs) (Rust 1.85 ou plus) et [`uv`](https://docs.astral.sh/uv/) ;
- pour le casque : `rustup target add aarch64-linux-android`, `cargo install cargo-ndk`, NDK r27c (API 32, comme
  SP-4). Sous Windows, garder le NDK et `CARGO_TARGET_DIR` sur des chemins courts : le clang du NDK échoue au-delà
  de 260 caractères.

## Header

`mote-capi/include/mote.h` est régénéré par `build.rs` à chaque build et versionné : après un changement de l'API,
committer le header avec le Rust. La CI échoue s'ils divergent.

## Tester

```sh
cd core
cargo test --workspace
```

## CI

`.github/workflows/core.yml`, à chaque push : format, clippy, tests sous Linux et Windows, build hôte, header à jour,
test C du header (`mote-capi/tests/smoke.c`), puis build arm64-v8a avec NDK r27c et contrôle de l'ELF. Le `.so`
arm64 est publié en artefact du run.
