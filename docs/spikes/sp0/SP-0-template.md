# SP-0 : H-01, les poses du casque suffisent-elles ?

> Trame à copier vers `docs/spikes/SP-0.md` (par la tâche SP-0, pas ici) puis à remplir avec les mesures.
> Les cases `___` sont à remplir ; supprimer ce bandeau et les consignes en italique à la fin.
> Protocole : `docs/spikes/sp0/PROTOCOL.md`. Versions : `docs/spikes/sp0/VERSIONS.md`.

Statut : ___ (brouillon / terminé) · Date : ___ · Auteur : ___ · Tâche : TASK-e447

## 1. Décision (à remplir en dernier, règle fixée en §2 avant les mesures)

**Décision sur H-01 : POURSUITE / ARRÊT** (barrer l'un).
Règle appliquée (§2) : ___
Justification en trois lignes au plus, chiffres à l'appui : ___
Conséquence : ___ (par exemple : on poursuit M0 ; ou : H-01 invalidée, ce qui change : ___)

## 2. Règle de décision, écrite avant de regarder les chiffres

| Mesure | Seuil de poursuite | Seuil d'arrêt | Pourquoi ce seuil |
|---|---|---|---|
| Erreur de translation médiane après Sim(3) (m) | ≤ ___ | > ___ | ___ |
| Erreur de rotation médiane après Sim(3) (°) | ≤ ___ | > ___ | ___ |
| PSNR du splat A moins PSNR du splat A sur poses REF (dB) | ≥ ___ | < ___ | ___ |
| Dérive (RMSE du dernier tiers / RMSE du premier tiers) | ≤ ___ | > ___ | ___ |

Date et heure de fixation de la règle : ___ (avant l'export SRC-3 : oui / non)

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

Les seuils actuels sont des `[HYPOTHESE]` (SPEC 2.3).

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

---
*Correspondance avec le done_criteria de SP-0 (à supprimer) :
PSNR, SSIM, LPIPS du splat option A → §5 ·
erreur de translation et de rotation contre SfM COLMAP complet après Sim(3) → §6 ·
temps du SfM → §7 ·
seuils chiffrés pour SC-01 et SC-02 → §8 ·
décision explicite de poursuite ou d'arrêt sur H-01 → §1 et §2 ·
capture faite avec QuestRealityCapture non modifié → §3.*
