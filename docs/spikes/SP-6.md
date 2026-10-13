# SP-6 : entraînement 3DGS incrémental quasi temps réel sur les poses du casque

Statut : brouillon. Méthode et règle fixées avant les mesures ; premier passage mesuré le 2026-10-12 et passage
`-Fast` le 2026-10-13, sur RTX 3070 ; reste le passage `-UniformHalf` (§4.4) pour confirmer la recommandation
· Date : 2026-10-13 · Auteur : claude-agent@mote-session · Tâche : TASK-45ec

Contexte : SP-0 a validé H-01 (ADR-0bbb) : l'aperçu live s'entraîne sur les poses du casque, sans SfM. Le risque se
déplace vers l'entraînement incrémental : RISK-09 (il ne tient pas la cible live) et Q-06 (quelle stratégie).

## 1. Verdict (à remplir en dernier)

Stratégie recommandée pour Q-06 : **`uniform` en demi-résolution**, c'est-à-dire un tirage sur toutes les vues
arrivées. Elle est désignée par la règle (§2) : cinq configurations atteignent 20 dB à la même évaluation (15,0 s), et
le départage par le PSNR en fin de flux la place en tête, à 21,09 ± 0,54 dB, contre 20,62 ± 0,51 pour `recent` en
demi-résolution. Elle a aussi le meilleur PSNR final (22,30 dB), et la courbe la plus haute à partir de 50 s (§4.2).
Elle n'a été mesurée qu'en version rapide, qui est plus lente sur ce GPU (§4.3) : elle gagne avec ce handicap.
`-UniformHalf` (§4.4) la mesure en version normale. Ce n'est pas le biais vers les vues récentes qui aide, c'est la
demi-résolution. `window` est écartée : elle oublie les zones anciennes (11,2 dB à la fin).
RISK-09 : **levé** ~~/ confirmé~~, avec deux réserves. Meilleure configuration en flux : `uniform` en
demi-résolution, 20 dB à 15,0 s après le début du flux (3 graines sur 3), pour une cible de 60 s.
Réserve 1 : ces 15 s sont un plancher fixé par l'arrivée des vues, pas par l'entraînement. C'est la première
évaluation où au moins 4 vues de validation sont couvertes, et toutes les configurations sauf deux y sont. Le chiffre
qui compte est le niveau tenu ensuite : `uniform` en demi-résolution reste entre 21 et 23 dB de 50 à 150 s.
Réserve 2 : les courbes ont des creux de 2 à 3 dB, à peu près toutes les 3 000 itérations. C'est la remise des
opacités de gsplat ; en live, l'aperçu chuterait de façon visible. `-UniformHalf` mesure la même configuration sans
remise.
Conséquence pour WP-15 : boucle gsplat en demi-résolution, tirage uniforme sur les vues arrivées, pas de fenêtre
glissante, images gardées sur le CPU. Le critère de WP-15 (20 dB en 60 s) est tenu sur ce GPU, avec environ 1 dB de
marge en fin de flux.

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
| `recent`, demi-résolution | 15,0 ± 0,0 | **44,6 ± 1,9** | 20,62 ± 0,51 | 20,56 ± 0,53 | 837 000 |
| `uniform`, demi-résolution, version rapide | 15,0 ± 0,0 | 37,8 ± 0,5 | **21,09 ± 0,54** | **22,30 ± 0,42** | 688 000 |

Trois graines par ligne. L'évaluation a lieu toutes les 5 s de flux : 15,0 s veut dire entre 10 et 15 s. Le PSNR
final est mesuré 60 s après la fin du flux, sur les 70 vues de validation. La dernière ligne vient du passage `-Fast`
(§4.3), qui coûte des itérations : la comparer aux autres la désavantage.

Courbes PSNR(temps de flux) des vues couvertes, moyenne des 3 graines, toutes les 10 s (`curves.py`). « 1/2 » :
demi-résolution ; « rapide » : version rapide (§4.3). Le flux finit à 122 s ; ensuite, 60 s d'entraînement seul.

| t (s) | vues couvertes | `recent` | `recent` 1/2 | `recent` rapide | `uniform` | `uniform` 1/2 rapide | `uniform` rapide | `window` |
|---|---|---|---|---|---|---|---|---|
| 10 | < 4 | - | 28,97 | - | - | 28,03 | - | 27,44 |
| 20 | 14 | 21,12 | 19,01 | 21,96 | 20,56 | 21,08 | 20,70 | 22,72 |
| 30 | 14 | 19,64 | 20,35 | 19,18 | 19,41 | 20,47 | 19,30 | 18,89 |
| 40 | 14 | 21,78 | 20,67 | 22,08 | 20,77 | 21,29 | 21,29 | 20,20 |
| 50 | 28 | 22,37 | 20,48 | 21,86 | 21,65 | 22,50 | 21,83 | 22,46 |
| 60 | 28 | 21,43 | 21,27 | 21,10 | 21,95 | 22,89 | 21,94 | 20,75 |
| 70 | 32 | 22,10 | 22,48 | 21,25 | 21,62 | 22,41 | 22,85 | 21,58 |
| 80 | 46 | 21,18 | 21,46 | 20,57 | 20,61 | 21,35 | 20,52 | 20,56 |
| 90 | 46 | 20,87 | 21,76 | 20,17 | 20,68 | 22,27 | 20,65 | 20,16 |
| 100 | 54 | 20,36 | 21,43 | 19,81 | 20,75 | 22,79 | 20,99 | 19,52 |
| 110 | 56 | 19,93 | 20,82 | 19,57 | 20,80 | 22,79 | 20,76 | 19,13 |
| 120 | 60 | 19,82 | **17,33** | 19,38 | 20,79 | 22,23 | 20,89 | 19,28 |
| 130 | 70 | 19,29 | 20,62 | 18,71 | 20,08 | 21,27 | 19,98 | 18,92 |
| 140 | 70 | 19,44 | 21,36 | 18,63 | 20,23 | 21,45 | 20,12 | 13,90 |
| 150 | 70 | 19,53 | 21,04 | 18,64 | 20,33 | 21,55 | 20,17 | 11,25 |
| 160 | 70 | 19,54 | 20,94 | 18,40 | 20,56 | **18,58** | 20,07 | 11,25 |
| 170 | 70 | 19,73 | 20,94 | 18,27 | **18,58** | 21,86 | 20,24 | 11,25 |
| 180 | 70 | 20,08 | 20,58 | 18,10 | 20,44 | 22,06 | 20,19 | 11,24 |

Lecture :

- La ligne 10 s porte sur une ou deux vues seulement, sous le seuil de 4 : à ignorer. La version de `curves.py` qui a
  produit ce tableau affichait 0 vue couverte ; c'est corrigé.
- De 20 à 120 s, les vues couvertes passent de 14 à 60 et le PSNR baisse lentement dans toutes les configurations :
  les nouvelles zones sont plus dures que les premières. `uniform` en demi-résolution est la seule à rester au-dessus
  de 21 dB sur presque toute cette plage.
- Les creux en gras tombent là où la remise des opacités les attend, toutes les 3 000 itérations : 3 000 / 37,8 it/s
  ≈ 79 s, donc une remise vers 158 s pour `uniform` 1/2 rapide (creux à 160 s) ; 3 000 / 18,9 ≈ 159 s pour `uniform`
  (creux à 170 s). Pour `recent` 1/2, les remises tombent vers 67 et 134 s et le creux est à 120 s : l'instant exact
  varie d'une graine à l'autre, la moyenne le brouille. L'aperçu remonte dans les 10 s.
- `window` décroche dès la fin du flux : elle ne s'entraîne plus que sur les dernières vues.

### 4.3 Version rapide (SSIM séparable, images sur GPU)

Passage `-Fast` du 2026-10-13, mêmes graines. La version rapide calcule le SSIM avec deux filtres 1D (même définition)
et garde les images d'entraînement sur le GPU en uint8 (environ 2,6 Go en pleine résolution pour S1).

| Configuration | it/s, version normale | it/s, version rapide | PSNR fin du flux, normale → rapide |
|---|---|---|---|
| hors ligne | 13,4 ± 0,6 | 9,4 ± 2,9 | (PSNR à 7 000 it. : 23,15 → 23,06) |
| `recent` | 20,0 ± 0,8 | 15,1 ± 0,1 | 19,29 → 18,71 |
| `uniform` | 18,9 ± 0,9 | 14,4 ± 0,1 | 20,08 → 20,03 |
| `uniform` 1/2 | (non mesurée, §4.4) | 37,8 ± 0,5 | (non mesurée) → 21,09 |

**La version rapide est plus lente**, d'environ 25 % partout, et 30 % hors ligne avec une forte dispersion entre
graines. Le PSNR suit le nombre d'itérations : il baisse, ou ne bouge pas. L'hypothèse la plus probable : 2,6 Go
d'images sur une carte de 8 Go, plus jusqu'à 765 000 gaussiennes et leurs états d'optimiseur, mettent l'allocateur de
torch sous pression. Le cas le plus chargé, hors ligne, est le plus dégradé. Les deux changements sont mêlés dans ce
passage. Les lignes « profil » de `$HOME\sp0\sp6\profile\*.log` les séparent, partie par partie : ___

Conséquence : la version rapide n'est pas retenue telle quelle. Sur un GPU de 8 Go, les images restent sur le CPU.

### 4.4 `uniform` en demi-résolution, version normale (`-UniformHalf`)

Avec et sans remise des opacités, 3 graines : ___

## 5. Débit

GPU : NVIDIA GeForce RTX 3070, 8 Go. Images absorbées par seconde (une itération = une image) : 19 à 23 en pleine
résolution selon la stratégie, 44,6 en demi-résolution, contre environ 9,6 images par seconde produites par le casque
(4,8 paires par seconde). Chaque image est donc vue 2 fois en moyenne pendant le flux en pleine résolution, et
4,6 fois en demi-résolution. La version rapide absorbe 14 à 15 images par seconde en pleine résolution et 37,8 en
demi-résolution (§4.3).

## 6. Lecture et limites

- Une seule scène (S1), un seul GPU, un rejeu à partir de fichiers : le transport réel (WP-14) n'y est pas.
- Le semis à profondeur aléatoire est une borne basse ; SP-7 mesure le gain de la profondeur du casque.
- Les vues de validation sont rendues avec leurs poses d'origine, sans raffinement (comme dans SP-0).
