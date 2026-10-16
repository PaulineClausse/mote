# mote-mcap

Écriture du fichier MCAP de session (ADR-5955, ADR-d5f3) : `SessionWriter` déclare les 11 canaux de SPEC-64c5 §9.1
(schéma protobuf mote.v1, FileDescriptorSet embarqué par `build.rs`), numérote chaque canal à partir de 0, écrit
`/session/end` à la fermeture. Chunks zstd de 1 Mio au plus ; le core en ferme un au moins chaque seconde, si bien
qu'un processus tué laisse lisible tout ce qui précède.

Le core écrit `<local_dir>/<session_id>.mcap`, `session_id` = date UTC du démarrage (`AAAAMMJJ-HHMMSS-mmm`).

Vérification par le lecteur de l'ingest PC (bibliothèque Python `mcap`), aussi lancée par la CI :

```sh
cd core
MOTE_KEEP_SESSION_DIR=/tmp/mote-session cargo test -p mote-capi --test session_file apres_stop
uv run --project ../pc python mote-mcap/tests/check_session.py /tmp/mote-session
```
