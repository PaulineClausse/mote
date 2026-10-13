# SP-4 : kit « le core tourne sur le casque »

Outils de spike jetables, pas du code mote. Rapport : `docs/spikes/SP-4.md` (méthode et règle de décision).

Tout se fait depuis le PC NVIDIA, avec Unity, `adb` et `uv`. Ni Rust ni le NDK ne sont nécessaires :
`prebuilt/libsp4core.so` est versionné, avec son empreinte SHA-256, et `build_sp4.ps1` la vérifie.

## 1. Construire et installer l'APK (une fois)

```powershell
git pull
powershell -ExecutionPolicy Bypass -File docs\spikes\sp4\build_sp4.ps1
```

Le script fait quatre choses :

1. Il clone QuestRealityCapture v1.5.0 dans `$HOME\sp4\qrc`, à part du clone de SP-3.
2. Il injecte trois éléments :
   - `libsp4core.so` dans `Assets/Plugins/Android/arm64-v8a/` ;
   - la sonde dans `Assets/Sp4/` (asmdef avec code unsafe) ;
   - le script de build.
3. Il construit l'APK avec **Unity 6000.4.5f1** et le module Android, comme pour SP-3. Journal dans
   `$HOME\sp4\build.log`. En cas d'erreur de compilation C#, les lignes `error CS` sont affichées : les copier dans la
   conversation.
4. Il installe l'APK sous `com.t34400.QuestRealityCapture.sp4`, puis pousse `sp4_config.json` (durées des phases).

## 2. Mesure (environ 8 minutes)

1. Casque chargé et frais, aucune autre app ouverte.
2. Lancer « QuestRealityCapture SP4 » (Sources inconnues). Au premier lancement, accepter les permissions caméra et
   scène, puis quitter l'app et la relancer.
3. Porter le casque et regarder la pièce en bougeant normalement la tête, comme pendant un scan. Le texte en bas du
   champ de vision indique la phase en cours : `Warmup`, `Baseline`, `GetColors`, `Nominal`, `Async`, puis « SP-4 terminé ».
4. **Ne pas appuyer sur le bouton menu** : il démarrerait l'enregistrement de QRC, qui couperait les caméras de la
   sonde en s'arrêtant.
5. À « SP-4 terminé », retirer le casque.

## 3. Analyse

```powershell
powershell -ExecutionPolicy Bypass -File docs\spikes\sp4\run_sp4.ps1
```

Le script fait trois choses :

1. Il récupère par `adb pull` les journaux et le MCAP de la sonde dans `$HOME\sp4\runs\<date>`.
2. Il affiche les tableaux de SP-4.md et le verdict selon la règle.
3. Il relit le MCAP sur PC (`verify_mcap.py`) et extrait la première paire en JPEG.

Copier toute la sortie dans la conversation.

## Fichiers

| Fichier | Rôle |
|---|---|
| `build_sp4.ps1` | clone, injection, build, installation |
| `run_sp4.ps1` | récupération, analyse, vérification du MCAP |
| `sp4_config.json` | durées des phases, cadence, qualité JPEG, threads |
| `unity/Sp4Probe.cs` | la sonde : caméras, phases, chronométrage, appels au core |
| `unity/Editor/Sp4Build.cs` | build Android en ligne de commande, plugin réglé en ARM64 |
| `sp4core/` | le core minimal en Rust (API C, JPEG libjpeg-turbo, MCAP) |
| `prebuilt/libsp4core.so` | le core compilé pour arm64-v8a, et son empreinte |
| `build_so.ps1` | recompile le `.so` (Rust, cargo-ndk, NDK r27c, cmake, ninja) |
| `analyze_sp4.py` | tableaux et verdict à partir des journaux |
| `verify_mcap.py` | relit un MCAP du core avec le code Python de mote.v1 |
| `test_analyze_sp4.py` | tests de la règle : `python test_analyze_sp4.py` |

Tests du core (Linux ou WSL) : `cd sp4core && cargo test --release`. Petit MCAP de démonstration :
`cargo run --release --example sample -- <dossier>`, puis `uv run verify_mcap.py <fichier>`.
