# SP-0 : H-01, les poses du casque suffisent-elles ?

Statut : brouillon, règle de décision fixée, mesures en attente de capture · Date : 2026-10-05 · Auteur : claude-agent@mote-session · Tâche : TASK-e447

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
| S1 | petite pièce encombrée | ___ | ___ | ___ | ___ | ___ | ___ |
| S2 | grand espace plus vide | ___ | ___ | ___ | ___ | ___ | ___ |

- Casque : Quest ___, firmware ___. APK QuestRealityCapture ___ (v1.5.0 ?), SHA-256 ___, non modifié : oui / non.
- `recording_config.json` appliqué : oui / non ; écart observé : ___
- Taille de la session et durée de `adb pull` : ___ Go, ___ s (SPEC 1.4, export lent).
- Marqueurs de discontinuité du suivi relevés dans le casque : ___

## 4. Outils et versions réellement utilisés

Python ___ · SRC-3 commit ___ · COLMAP ___ · CUDA ___ · PyTorch ___ · nerfstudio ___ · gsplat ___ · LPIPS ___ (réseau ___)
Machine d'entraînement : GPU ___, VRAM ___ Go, CPU ___, RAM ___ Go.

Points `[A VERIFIER]` du protocole tranchés :
- Arborescence de l'export SRC-3 : ___
- Œil(s) exporté(s), nommage, modèle de caméra : ___
- Chiralité / repère des poses exportées (résidu Sim(3) cohérent) : ___
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

Images communes : ___ sur ___ (casque) et ___ (REF). Fraction recalée par REF : ___ %.
Facteur d'échelle trouvé (casque vers unités REF) : ___ ; 1 unité REF = ___ m.

| Scène | Translation RMSE (m) | Translation médiane (m) | Translation max (m) | Rotation RMSE (°) | Rotation médiane (°) | Rotation max (°) |
|---|---|---|---|---|---|---|
| S1 | ___ | ___ | ___ | ___ | ___ | ___ |

Dérive : RMSE de translation par tiers de la trajectoire = ___ / ___ / ___ m ; pente de l'erreur = ___ m par m parcouru.
Erreur à la fermeture de boucle (retour au point de départ) : ___ m.
Résultat sur la partie sans discontinuité de suivi (si pertinent) : ___
Test d'alignement `test_align_sim3.py` rejoué sur la machine de capture : ___/6.

## 7. Temps du SfM REF (SC-03)

| Étape | Durée (s) |
|---|---|
| `feature_extractor` | ___ |
| matcher (`exhaustive` / `sequential`, barrer) | ___ |
| `mapper` | ___ |
| **Total** | ___ s = ___ min |

Nombre d'images : ___ ; GPU utilisé pour SIFT : oui / non. Ce temps sert de dénominateur à SC-03.

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
