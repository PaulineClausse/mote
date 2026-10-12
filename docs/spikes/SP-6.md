# SP-6 : entraînement 3DGS incrémental quasi temps réel sur les poses du casque

Statut : brouillon. Méthode et règle fixées avant les mesures ; kit prêt (`docs/spikes/sp6/`), mesures en attente du
PC NVIDIA · Date : 2026-10-12 · Auteur : claude-agent@mote-session · Tâche : TASK-45ec

Contexte : SP-0 a validé H-01 (ADR-0bbb) : l'aperçu live s'entraîne sur les poses du casque, sans SfM. Le risque se
déplace vers l'entraînement incrémental : RISK-09 (il ne tient pas la cible live) et Q-06 (quelle stratégie).

## 1. Verdict (à remplir en dernier)

Stratégie recommandée pour Q-06 : ___
RISK-09 : **levé / confirmé** (barrer l'un). Meilleure configuration en flux : ___, 20 dB à ___ s après le début du flux.
Conséquence pour WP-15 : ___

## 2. Règle, écrite avant de regarder les chiffres

- **Cible** : le critère de WP-15. L'aperçu atteint 20 dB (SC-01, calibré par SP-0) en 60 s au plus après le début du
  flux, mesuré sur les vues de validation déjà couvertes.
- **RISK-09 levé** si la meilleure configuration en flux atteint 20 dB sur ses trois graines, en 60 s au plus en
  moyenne, sur le GPU de SP-0. **Confirmé** sinon. Le verdict vaut pour ce GPU, nommé en §5.
- **Stratégie recommandée** : celle qui atteint 20 dB le plus tôt. Si deux stratégies sont à moins d'un écart-type
  l'une de l'autre, celle qui a le meilleur PSNR en fin de flux.
- La demi-résolution compte comme une configuration à part entière : si elle seule tient la cible, RISK-09 est levé
  avec cette condition, écrite en conséquence.

Date de fixation de la règle : 2026-10-12, avant toute mesure.

## 3. Méthode

Données : S1 de SP-0 (`20261007_120820`), poses du casque, même jeu commun et même hold-out que le bench de SP-0 :
70 vues de validation, en blocs de paires. Entraîneur : gsplat 1.4.0 directement, pas splatfacto (WP-15 prévoit une
boucle gsplat). Détails : `docs/spikes/sp6/README.md`.

- **Horloge du flux** : le temps d'entraînement écoulé, évaluations exclues. Une vue d'entraînement arrive à son
  horodatage de capture.
- **Semis** : 500 gaussiennes par vue arrivée, le long de rayons de son image, à profondeur aléatoire entre 0,3 et 4 m.
- **Stratégies** : `uniform` (toutes les vues arrivées), `recent` (une fois sur deux dans les 5 dernières secondes),
  `window` (seulement les 5 dernières secondes).
- **Vue couverte** : capturée depuis au moins 2 s. Le seuil n'est retenu qu'à partir de 4 vues couvertes.
- **Hors ligne** : toutes les vues dès t = 0, PSNR de tout le hold-out toutes les 200 itérations. C'est la latence
  d'aperçu sans l'arrivée des images, à comparer aux 42 s de SP-0 (borne haute, évaluation toutes les 2 000).

## 4. Résultats

### 4.1 Latence d'aperçu hors ligne (évaluation toutes les 200 itérations)

| Graine | 20 dB (s) | 20 dB (itération) | it/s | PSNR à 7 000 it. |
|---|---|---|---|---|
| 0 | ___ | ___ | ___ | ___ |
| 1 | ___ | ___ | ___ | ___ |
| 2 | ___ | ___ | ___ | ___ |
| **moyenne ± écart-type** | ___ | ___ | ___ | ___ |

### 4.2 Rejeu en flux de S1 (122 s, puis 60 s)

| Configuration | 20 dB après le début du flux (s) | it/s | PSNR fin du flux (dB) | PSNR final (dB) | Gaussiennes |
|---|---|---|---|---|---|
| `uniform` | ___ | ___ | ___ | ___ | ___ |
| `recent` | ___ | ___ | ___ | ___ | ___ |
| `window` | ___ | ___ | ___ | ___ | ___ |
| `recent`, demi-résolution | ___ | ___ | ___ | ___ | ___ |

Courbes PSNR(temps de flux) : `$HOME\sp0\sp6\runs\*.json`, champ `curve`.

## 5. Débit

GPU : ___. Images absorbées par seconde (une itération = une image) : ___ en pleine résolution, ___ en
demi-résolution, contre ~9,6 images par seconde produites par le casque (4,8 paires par seconde).

## 6. Lecture et limites

- Une seule scène (S1), un seul GPU, un rejeu à partir de fichiers : le transport réel (WP-14) n'y est pas.
- Le semis à profondeur aléatoire est une borne basse ; SP-7 mesure le gain de la profondeur du casque.
- Les vues de validation sont rendues avec leurs poses d'origine, sans raffinement (comme dans SP-0).
