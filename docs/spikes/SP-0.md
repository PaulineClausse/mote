# SP-0 : H-01, les poses du casque suffisent-elles ?

Statut : brouillon. Règle fixée ; erreur de suivi et temps du SfM mesurés sur une session d'essai (S0) ; splat A en attente d'un PC NVIDIA ; S1 au protocole à capturer · Date : 2026-10-07 · Auteur : claude-agent@mote-session · Tâche : TASK-e447

Protocole : `docs/spikes/sp0/PROTOCOL.md`. Versions : `docs/spikes/sp0/VERSIONS.md`. Les cases `___` se remplissent
pendant et après la capture.

## 1. Décision (à remplir en dernier, règle fixée en §2 avant les mesures)

**Décision sur H-01 : POURSUITE / ARRÊT** (barrer l'un).
Règle appliquée (§2) : ___
Justification en trois lignes au plus, chiffres à l'appui : ___
Conséquence : ___ (par exemple : on poursuit M0 ; ou : H-01 invalidée, ce qui change : ___)

## 2. Règle de décision, écrite avant de regarder les chiffres

| Mesure | Seuil de poursuite | Seuil d'arrêt | Pourquoi ce seuil |
|---|---|---|---|
| Erreur de translation médiane après Sim(3) (m) | ≤ 0,05 | > 0,15 | 0,05 m ≈ 2 % d'une pièce de 3 x 4 m, ordre de ce qu'un raffinement `SO3xR3` local rattrape ; au-delà de 0,15 m, l'erreur dépasse la taille des détails de la scène et le raffinement ne la corrige plus (fantômes) |
| Erreur de rotation médiane après Sim(3) (°) | ≤ 1,5 | > 5 | à 3 m, 1,5° décale un point d'environ 8 cm, cohérent avec le seuil de translation ; 5° le décale d'environ 26 cm |
| PSNR du splat A moins PSNR du splat A sur poses REF (dB) | ≥ -1 | < -3 | -1 dB est l'ordre de grandeur du gain visé par SC-02, donc une perte tolérable ; -3 dB est une dégradation visible |
| Dérive (RMSE du dernier tiers / RMSE du premier tiers) | ≤ 2 | > 4 | un rapport sous 2 indique une erreur stable ; au-dessus de 4, l'erreur s'accumule le long de la trajectoire et grandira avec la durée du scan |

Combinaison :
- **Poursuite** si les quatre mesures sont sous leur seuil de poursuite.
- **Arrêt** si l'écart de PSNR est sous son seuil d'arrêt, ou si la translation et la rotation dépassent toutes deux leur
  seuil d'arrêt.
- Sinon, **poursuite conditionnelle** : H-01 tient à condition d'un raffinement de pose systématique ; le recalage hors
  ligne (options C et D, WP-17) devient prioritaire au lieu d'être un comparatif. La décision s'écrit alors POURSUITE,
  avec cette condition en conséquence.
- Si REF recale moins de 90 % des images (PROTOCOL.md §6), REF n'est pas une référence : pas de décision sur cette
  session, refaire la capture.

Date et heure de fixation de la règle : 2026-10-05, avant toute capture (avant l'export SRC-3 : oui)

## 3. Conditions de capture (une ligne par session)

| Session | Scène | Date | Durée réelle | Cadence caméra réelle (fps) | Paires | Lumière | Incidents (suivi, recentrage, crash) |
|---|---|---|---|---|---|---|---|
| S0 (essai, hors protocole) | bureau, opérateur assis qui regarde autour de lui ; mains et manettes dans le champ, murs et plafond blancs | 2026-10-07 | 89 s | 9,1 (cible 10, config par défaut) | 808 | néons, fenêtre en contre-jour | aucun ; arrêt propre par le bouton menu |
| S1 | petite pièce encombrée | ___ | ___ | ___ | ___ | ___ | ___ |
| S2 | grand espace plus vide | ___ | ___ | ___ | ___ | ___ | ___ |

- Casque : Quest 3S, build `UP1A.231005.007.A1` (incrémental 3814840036500610). APK QuestRealityCapture v1.5.0 (`build.apk` de la release),
  SHA-256 `940feffa26ebae7e58993d28ee35817a9396b99dd101eafff6afb5f7240db5ff`, identique à l'APK installé : non modifié, oui.
- `recording_config.json` appliqué : non pour S0 (cadences par défaut) ; poussé ensuite pour S1 (caméra et profondeur à
  5 fps, copie intégrale de `recording_config.default.json` de SRC-1, le chargeur faisant un `FromJsonOverwrite`) :
  `docs/spikes/sp0/recording_config.json`.
- Taille de la session et durée de `adb pull` : S0 11,2 Go (3 049 fichiers), 53 s, soit 201 Mo/s en USB.
- Marqueurs de discontinuité du suivi relevés dans le casque : non relevés pour S0 ; aucun saut de pose de plus de 30 cm
  entre images.
- Sessions écartées, enregistrées le même jour : 094826 et 095323 n'ont pas été arrêtées par le bouton (plantage, tombstone
  à 10 h 00). `hmd_poses.csv` y est tronqué et `mruk_stereo_pairs.csv` vide, alors que les poses par image
  (`*_frame_metadata.csv`) sont complètes. Consigne : toujours arrêter par le bouton menu avant de quitter l'application.
  Les quatre autres sessions durent moins de 35 s.

## 4. Outils et versions réellement utilisés

Export et REF (MacBook Air, Apple M5, 24 Go) : Python 3.11.15 (venv uv) · SRC-3 commit `97d15f7` · COLMAP 4.2.1 Homebrew
**sans GPU** · numpy 2.4.6 · adb 1.0.41.
Entraînement : CUDA ___ · PyTorch ___ · nerfstudio ___ · gsplat ___ · LPIPS ___ (réseau ___)
Machine d'entraînement : GPU ___, VRAM ___ Go, CPU ___, RAM ___ Go.

Points `[A VERIFIER]` du protocole tranchés :
- Arborescence de l'export SRC-3 : `images/` à plat, modèle binaire dans `distorted/sparse/0/`. `points3D` est vide sans
  `--use-colored-pointcloud`, ce qui convient à l'option A sans rien vider.
- **Écart au protocole §5** : `--use-optimized-color-dataset` remplace les poses du casque par celles recalées par la
  reconstruction SRC-3 quand elles existent (`colmap_export.py`). Ce n'est plus l'option A : l'export a été fait **sans** cette
  option, avec `--interval 2` (404 paires, environ 4,5 fps, proche des 5 fps visés).
- Œil(s) exporté(s), nommage, modèle de caméra : les deux yeux, `LEFT_<ts_us>.png` et `RIGHT_<ts_us>.png`, une caméra
  `PINHOLE` par œil (gauche f = 868,68 px, c = (642,0 ; 640,6)). Pour `single_camera_per_folder`, des liens symboliques
  `images_by_eye/left|right` ont été créés. `align_sim3.py` apparie sur le nom de base, donc les noms coïncident.
- Intrinsèques : REF estime f = 870,31 px pour la caméra gauche, contre 868,68 px pour MRUK (0,2 % d'écart), et une
  distorsion OPENCV quasi nulle (k1 = 0,0022, k2 = -0,0013). C'est un premier indice pour H-11 et Q-03 : les images MRUK
  semblent déjà rectifiées. À confirmer en SP-2.
- Chiralité / repère des poses exportées : cohérents. Résidu médian de 4 mm après Sim(3) ; un miroir donnerait des mètres.
- Prise en compte de `train_list.txt` / `test_list.txt` par nerfstudio (nombre train/eval observé) : ___
- Prise en compte de `recording_config.json` par SRC-1 : ___
- Poses de test raffinées (SPEC 13.1 point 5) : fait / non fait, raison : ___

## 5. Splat option A (splatfacto, poses du casque, initialisation aléatoire)

Configuration : `--max-num-iterations` ___, camera optimizer `SO3xR3`, hold-out ___ paires sur ___ (___ %, blocs de 5 toutes les 40).

| Scène | Graine | PSNR (dB) | SSIM | LPIPS | Temps d'entraînement (s) |
|---|---|---|---|---|---|
| S1 | 0 | ___ | ___ | ___ | ___ |
| S1 | 1 | ___ | ___ | ___ | ___ |
| S1 | 2 | ___ | ___ | ___ | ___ |
| S1 | **moyenne ± écart-type** | ___ ± ___ | ___ ± ___ | ___ ± ___ | ___ |
| S2 | (idem, si capturée) | | | | |

Métriques sans raffinement des poses de test (indiquées comme telles) : ___ ; avec raffinement : ___ ou non disponible.
Temps jusqu'au premier aperçu à ≥ 20 dB (SC-01) : ___ s (itération ___).

Comparaison de contrôle, A sur poses REF (mêmes images, mêmes listes, mêmes graines) :

| Scène | PSNR (dB) | SSIM | LPIPS | Écart de PSNR A - REF (dB) |
|---|---|---|---|---|
| S1 | ___ | ___ | ___ | ___ |

## 6. Erreur de suivi du casque contre un SfM COLMAP complet (Sim(3))

S0 : images communes 763 sur 808 (casque) et 763 (REF). Fraction recalée par REF : 94,4 %, au-dessus du minimum de 90 %.
Facteur d'échelle trouvé (casque vers unités REF) : 8,2516 ; 1 unité REF = 0,12119 m. L'échelle est la même par œil
(8,2497 à gauche, 8,2539 à droite, 0,05 % d'écart) : le casque est bien métrique et cohérent entre les deux caméras.

| Scène | Translation RMSE (m) | Translation médiane (m) | Translation max (m) | Rotation RMSE (°) | Rotation médiane (°) | Rotation max (°) |
|---|---|---|---|---|---|---|
| S0 (deux yeux) | 0,0068 | 0,0040 | 0,0375 | 0,513 | 0,457 | 1,305 |
| S0 (gauche seul) | 0,0068 | 0,0038 | 0,0334 | 0,583 | 0,509 | 1,306 |
| S0 (droite seule) | 0,0068 | 0,0040 | 0,0373 | 0,425 | 0,368 | 1,237 |
| S1 | ___ | ___ | ___ | ___ | ___ | ___ |

Dérive S0, calculée par œil, parce que le tri par nom de `align_sim3.py` range tous les LEFT puis tous les RIGHT et mélange
les tiers sur les deux yeux. RMSE par tiers en unités REF : gauche 0,051 / 0,063 / 0,053, rapport 1,05 ; droite 0,053 /
0,064 / 0,052, rapport 0,98. Pente de l'erreur : environ 0. Pas de dérive mesurable sur 89 s.
Erreur à la fermeture de boucle : sans objet pour S0, l'opérateur étant assis. Le casque revient à 6 cm de sa position de
départ.
Résultat sur la partie sans discontinuité de suivi (si pertinent) : sans objet, aucune discontinuité.
Test d'alignement `test_align_sim3.py` rejoué sur la machine d'export : 6/6.
Mesures brutes : `docs/spikes/sp0/results/S0/align_m*.json`.

## 7. Temps du SfM REF (SC-03)

| Étape | Durée (s) |
|---|---|
| Étape | S0 (CPU) |
|---|---|
| `feature_extractor` | 142 |
| matcher (`exhaustive`) | 2 492 |
| `mapper` | 656 |
| **Total** | 3 290 s = 54,8 min |

S0 : 808 images (404 paires), 1280x1280. GPU utilisé pour SIFT : **non**, car COLMAP Homebrew n'a pas de GPU sur Apple
Silicon (M5, 24 Go). Le modèle REF compte 763 images recalées et 70 628 points, une seule composante. Ce temps sert de
dénominateur à SC-03, à condition de garder la même machine et le même matcher pour toute comparaison. Avec un GPU CUDA,
il serait plus court. Mesures brutes : `docs/spikes/sp0/results/S0/timings.json`.
Pour comparaison, l'export SRC-3 avec les poses du casque (option A, sans SfM) a pris 33 s pour les mêmes 808 images, soit
100 fois moins.

## 8. Seuils proposés pour SC-01 et SC-02

Les seuils actuels sont des `[HYPOTHESE]` (SPEC 2.3). Méthode de calcul : PROTOCOL.md §9.

| Critère | Valeur actuelle (SPEC) | Valeur proposée | Mesures qui la fondent |
|---|---|---|---|
| SC-01 : PSNR d'aperçu sur vues couvertes | ≥ 20 dB | ___ dB | PSNR final de A ___ dB, courbe PSNR(temps) ___ |
| SC-01 : délai d'aperçu (NFR-04) | ___ | ___ s | temps pour atteindre le seuil : ___ s |
| SC-02 : gain de la meilleure option sur A | ≥ 1 dB | ___ dB | σ de A entre graines = ___ dB, règle `max(1 dB, 2σ)` |
| SC-03 : dénominateur (SfM complet) | un ordre de grandeur | ___ s | §7 |

## 9. Lecture et limites

- Ce que les mesures disent de H-01 : ___
- Ce qu'elles ne disent pas (nombre de scènes, une seule pièce, une seule date, un seul casque, REF lui-même incertain) : ___
- Risques confirmés ou levés : RISK-05 (MRUK sur 3S) ___ ; RISK-08 (versions) ___ ; RISK-12 (crash à la fermeture) ___
- Incidents du protocole et corrections à reporter dans `docs/spikes/sp0/PROTOCOL.md` : ___

## 10. Suites

- Tâches à créer ou à débloquer : ___
- Questions ouvertes remontées à SP-1 / SP-2 (base de temps, repères) : ___
- Données conservées (hors dépôt) et où : ___ ; JSON de mesures versés dans le dépôt : ___
