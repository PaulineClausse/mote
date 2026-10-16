# ingest

Réception, MCAP, conversion de repères, dataset.

## Hors ligne : rejouer un MCAP

```sh
uv run --project pc mote ingest --replay session.mcap --out dataset
```

## En direct : recevoir le flux du casque (WP-14, SPEC-9df2)

```sh
uv run --project pc mote ingest --listen 0.0.0.0:5000 --token <jeton> --out dataset
```

- Le casque se connecte à `server_addr` avec le même jeton (`auth_token` de `mote_config`). Une connexion sans le bon
  jeton, ou d'une version de schéma inconnue, est fermée aussitôt. Le jeton peut aussi venir de la variable
  `MOTE_TOKEN`, pour ne pas le laisser dans l'historique du shell.
- Les messages sont écrits au fil de l'eau dans `<out>/../sessions/<session_id>.mcap` (`--sessions` pour un autre
  dossier). Les trous de seq (coupure, file live du casque pleine) sont demandés au casque, qui les relit dans son
  fichier local. Une fois `/session/end` reçu et tous les seq présents, la session PC contient les mêmes messages que
  celle du casque ; le dataset est alors construit comme avec `--replay`.
- Flux non chiffré : réseau local de confiance seulement (SPEC-9df2).

Réglages, à adapter à votre réseau (les défauts viennent de SP-5, Wi-Fi 6 en 5 GHz) :

| Option | Défaut | Rôle |
|---|---|---|
| `--resend-after S` | 2 s | délai avant de redemander un message toujours absent ; plus long sur un réseau lent ou chargé |
| `--idle-timeout S` | 0 (attendre) | abandon si rien n'arrive pendant S secondes |

Côté casque, les réglages du transport sont dans `mote_config` (0 = défaut) : `live_queue_bytes` (64 Mio),
`connect_timeout_ms` (3000), `reconnect_min_ms` (500), `reconnect_max_ms` (5000), `resend_batch_ms` (500).
