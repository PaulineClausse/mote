# mote-net

Transport live et rattrapage (ADR-c36f, SPEC-9df2), côté casque.

- **Trames** : taille sur 4 octets en ordre réseau, puis une `Envelope` (casque vers PC) ou un `Control` (PC vers
  casque) ; au-delà de 64 Mo, erreur de protocole.
- **Connexion** : ouverte par le casque vers `server_addr` ; première trame `Hello` (session, jeton, version de
  schéma). En cas de coupure, reconnexion avec un délai doublé à chaque échec, et même `Hello`. Le scan continue.
- **File live** bornée en octets : quand elle déborde, les `ImageFrame` et `DepthFrame` les plus anciens sont retirés,
  chacun avec un événement `LIVE_DROPPED` ; les autres canaux ne sont jamais retirés. Tout reste dans le fichier local.
- **Rattrapage** : les `ResendRequest` du PC sont servis par lots, en relisant le fichier MCAP local, après le live.
  Le client vit jusqu'à `mote_destroy` : après `mote_stop`, il continue de servir le rattrapage.

Réglages (`mote_config`, 0 = défaut) : `live_queue_bytes` (64 Mio, environ 5 s du pire cas de 100 Mbit/s),
`connect_timeout_ms` (3000), `reconnect_min_ms` (500), `reconnect_max_ms` (5000), `resend_batch_ms` (500). Les défauts
viennent de SP-5 (Wi-Fi 6 en 5 GHz) ; un autre réseau peut demander d'autres valeurs.

Test de bout en bout : `mote-capi/tests/live.rs` (coupure de 10 s entre le core et `mote ingest --listen`).
