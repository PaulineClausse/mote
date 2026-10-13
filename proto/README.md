# proto

Schémas protobuf `mote.v1`, partagés entre le fichier MCAP et le flux réseau (ADR-956c). Spécification : `SPEC-64c5`
(`ank show SPEC-64c5`), §9.2.

| Chemin | Rôle |
|---|---|
| `mote/v1/mote.proto` | le schéma, seule source de vérité |
| `rust/` | crate `mote-proto` : types Rust générés au build par prost (avec protox, sans protoc) |
| `../pc/mote/v1/mote_pb2.py` | code Python généré, versionné (`from mote.v1 import mote_pb2`) |
| `generate.py` | régénère le code Python et construit la crate Rust |
| `roundtrip_test.py` | test croisé : chaque message sérialisé en Rust, relu en Python |

Prérequis : `cargo` et [`uv`](https://docs.astral.sh/uv/). Les scripts déclarent leurs dépendances Python (PEP 723),
`uv run` les installe dans un environnement isolé. Aucun `protoc` à installer.

## Générer

Après toute modification de `mote.proto` :

```sh
uv run proto/generate.py
```

Le code Python généré demande le runtime `protobuf` 7.35.1 ou plus récent, en 7.x (celui de grpcio-tools 1.84.0).
Côté Rust, une dépendance de chemin suffit : `mote-proto = { path = "../../proto/rust" }`, puis
`use mote_proto::v1::ImageFrame;`.

## Tester

```sh
uv run proto/roundtrip_test.py
```

Le test lance `cargo run --example write_fixtures`, qui écrit un exemplaire de chaque message, tous champs renseignés
(y compris un `pair_id` au-delà de 2^63, `far_z` infini, des octets non UTF-8), puis relit chaque fichier en Python. Il
vérifie que les champs sont identiques à ceux construits en Python et que le réencodage redonne les mêmes octets. Il
vérifie aussi la couverture : un exemplaire par message du schéma et par variante de `Envelope.body`, et aucun champ
laissé à sa valeur par défaut. Un message ou un champ ajouté au schéma fait donc échouer le test tant qu'il n'est pas
ajouté des deux côtés (`rust/examples/write_fixtures.rs` et `expected()` de `roundtrip_test.py`).

## Évolution

Ajout de champs uniquement ; tout changement cassant incrémente `schema_version` et fournit un convertisseur
(SPEC-64c5 §9.6).

Écart à l'esquisse de SPEC-64c5 §9.2, issu de SP-1 (§3.4) : `DepthFrame.src_predicted_display_time_ns` (champ 18)
garde le `predictedDisplayTime` du descripteur Unity. `isValid` n'est pas stocké : l'hôte ne pousse que les cartes
valides.
