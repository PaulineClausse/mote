# train

Initialisations, entraînement incrémental et final (SPEC-834a).

L'entraînement tourne dans **son propre environnement** (ADR-976d) : nerfstudio 1.1.5 exige protobuf <= 3.20.3, le
code généré de mote.v1 protobuf >= 7.35.1. `launch.py` exporte le dataset au format nerfstudio, côté mote, puis lance
`ns-train` par `uv run --no-project --with nerfstudio==1.1.5` : le processus d'entraînement ne voit ni le paquet mote
ni le MCAP, il ne lit que le répertoire de dataset.

```sh
uv run --project pc mote train <dataset>                          # splatfacto, CUDA (PC NVIDIA)
uv run --project pc mote train <dataset> --method nerfacto --device cpu --iterations 20   # essai sans GPU
```

La première exécution installe nerfstudio et torch (environ une minute). Le test de bout en bout
(`tests/test_train_env.py`, ingest puis entraînement de 3 itérations en CPU) se lance avec `MOTE_TEST_NERFSTUDIO=1`.
