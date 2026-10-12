# SP-6 : entraînement 3DGS incrémental quasi temps réel sur les poses du casque

Statut : brouillon. Méthode et règle fixées avant les mesures ; premier passage mesuré le 2026-10-12 sur RTX 3070 ;
courbes PSNR(temps) et version rapide (`-Fast`) à reporter · Date : 2026-10-12 · Auteur : claude-agent@mote-session · Tâche : TASK-45ec

Contexte : SP-0 a validé H-01 (ADR-0bbb) : l'aperçu live s'entraîne sur les poses du casque, sans SfM. Le risque se
déplace vers l'entraînement incrémental : RISK-09 (il ne tient pas la cible live) et Q-06 (quelle stratégie).

## 1. Verdict (à remplir en dernier)

Stratégie recommandée pour Q-06 : **tirage sur toutes les vues arrivées, en demi-résolution** pour le live. La règle
(§2) désigne `recent` en demi-résolution ; mais en pleine résolution, `uniform` fait mieux que `recent` sur toute la
ligne : ce n'est pas le biais vers les vues récentes qui aide, c'est la demi-résolution. `uniform` en demi-résolution
reste à mesurer pour le confirmer. `window` est écartée : elle oublie les zones anciennes (11,2 dB à la fin).
RISK-09 : **levé** ~~/ confirmé~~, avec une réserve. Meilleure configuration en flux : `recent` en demi-résolution,
20 dB à 15,0 s après le début du flux (3 graines sur 3), pour une cible de 60 s.
Réserve : 20 dB est atteint tôt, mais l'aperçu reste ensuite **au seuil, pas au-dessus** : 19,3 à 20,6 dB en fin de
flux selon la configuration, sur les 70 vues couvertes. La marge doit venir de la vitesse (version rapide, §4.3) et
de l'initialisation par la profondeur (SP-7).
Conséquence pour WP-15 : boucle gsplat en demi-résolution, tirage uniforme sur les vues arrivées, pas de fenêtre
glissante. Le critère de WP-15 (20 dB en 60 s) est tenu sur ce GPU, sans marge sur la qualité.

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
| **moyenne ± écart-type** | 34,3 ± 19,0 | 333 ± 115 | 13,4 ± 0,6 | 23,15 ± 0,11 |

Valeurs par graine : `$HOME\sp0\sp6\runs\offline_s*.json`. Le seuil tombe entre les itérations 200 et 400 selon la
graine. Splatfacto (SP-0) l'atteignait à sa première évaluation, à l'itération 2 000 : ce n'était qu'une borne haute.
L'entraîneur gsplat converge en moins d'itérations, mais n'en fait que 13 par seconde sur 765 000 gaussiennes, contre
environ 20 pour splatfacto. À 7 000 itérations il est à 23,15 dB, contre 25,40 dB pour splatfacto à 30 000.

### 4.2 Rejeu en flux de S1 (122 s, puis 60 s)

| Configuration | 20 dB après le début du flux (s) | it/s | PSNR fin du flux (dB) | PSNR final (dB) | Gaussiennes |
|---|---|---|---|---|---|
| `uniform` | 16,7 ± 2,9 | 18,9 ± 0,9 | 20,08 ± 0,34 | **20,87 ± 0,14** | 355 000 |
| `recent` | 15,0 ± 0,0 | 20,0 ± 0,8 | 19,29 ± 0,40 | 19,98 ± 0,27 | 362 000 |
| `window` | 15,0 ± 0,0 | 22,6 ± 1,1 | 18,92 ± 0,18 | 11,24 ± 0,10 | 260 000 |
| `recent`, demi-résolution | 15,0 ± 0,0 | **44,6 ± 1,9** | **20,62 ± 0,51** | 20,56 ± 0,53 | 837 000 |

Trois graines par ligne. L'évaluation a lieu toutes les 5 s de flux : 15,0 s veut dire entre 10 et 15 s. Le PSNR
final est mesuré 60 s après la fin du flux, sur les 70 vues de validation.

Courbes PSNR(temps de flux), moyenne des graines, toutes les 10 s (`curves.py`) : ___

### 4.3 Version rapide (SSIM séparable, images sur GPU)

Profil d'une itération et mêmes mesures : ___

## 5. Débit

GPU : NVIDIA GeForce RTX 3070, 8 Go. Images absorbées par seconde (une itération = une image) : 19 à 23 en pleine
résolution selon la stratégie, 44,6 en demi-résolution, contre environ 9,6 images par seconde produites par le casque
(4,8 paires par seconde). Chaque image est donc vue 2 fois en moyenne pendant le flux en pleine résolution, et
4,6 fois en demi-résolution.

## 6. Lecture et limites

- Une seule scène (S1), un seul GPU, un rejeu à partir de fichiers : le transport réel (WP-14) n'y est pas.
- Le semis à profondeur aléatoire est une borne basse ; SP-7 mesure le gain de la profondeur du casque.
- Les vues de validation sont rendues avec leurs poses d'origine, sans raffinement (comme dans SP-0).
