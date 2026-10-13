# SP-6 : entraînement 3DGS incrémental quasi temps réel sur les poses du casque

Statut : terminé. Méthode et règle fixées avant les mesures ; mesuré sur RTX 3070 en trois passages : premier passage
le 2026-10-12, `-Fast` et `-UniformHalf` le 2026-10-13 · Date : 2026-10-13 · Auteur : claude-agent@mote-session
· Tâche : TASK-45ec

Contexte : SP-0 a validé H-01 (ADR-0bbb) : l'aperçu live s'entraîne sur les poses du casque, sans SfM. Le risque se
déplace vers l'entraînement incrémental : RISK-09 (il ne tient pas la cible live) et Q-06 (quelle stratégie).

## 1. Verdict

Stratégie recommandée pour Q-06 : **`uniform` en demi-résolution, avec la remise des opacités de gsplat**,
c'est-à-dire un tirage sur toutes les vues arrivées. La règle (§2) la désigne : sept configurations atteignent 20 dB à
la même évaluation (15,0 s), et le départage par le PSNR en fin de flux la place en tête, à 21,38 ± 0,11 dB. Suivent
la même configuration en version rapide (21,09 ± 0,54) et `recent` en demi-résolution (20,62 ± 0,51). C'est aussi la
plus régulière : de 40 à 180 s, sa courbe reste entre 21,1 et 23,1 dB, sans creux (§4.2). Ce n'est pas le biais vers
les vues récentes qui aide, c'est la demi-résolution. `window` est écartée : elle oublie les zones anciennes
(11,2 dB à la fin). Sans remise des opacités, la même configuration perd 2 dB (19,40 en fin de flux, §4.4) : la remise
reste.
RISK-09 : **levé** ~~/ confirmé~~, avec une réserve. Meilleure configuration en flux : `uniform` en demi-résolution,
20 dB à 15,0 s après le début du flux (3 graines sur 3), pour une cible de 60 s.
Réserve : ces 15 s sont un plancher fixé par l'arrivée des vues, pas par l'entraînement. C'est la première
évaluation où au moins 4 vues de validation sont couvertes, et presque toutes les configurations y sont. Le chiffre
qui compte est le niveau tenu ensuite : entre 21,1 et 23,1 dB, soit 1 à 3 dB au-dessus du seuil, avec un écart-type
de 0,1 dB entre graines en fin de flux.
Conséquence pour WP-15 : boucle gsplat en demi-résolution, tirage uniforme sur les vues arrivées, pas de fenêtre
glissante, remise des opacités gardée, images gardées sur le CPU (sur 8 Go, les garder sur le GPU ralentit tout,
§4.3). La rétropropagation fait 58 % du temps d'une itération : c'est là que se trouve la marge suivante. Le critère
de WP-15 (20 dB en 60 s) est tenu sur ce GPU, avec environ 1,4 dB de marge en fin de flux.

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
| `uniform` | 16,7 ± 2,9 | 18,9 ± 0,9 | 20,08 ± 0,34 | 20,87 ± 0,14 | 355 000 |
| `recent` | 15,0 ± 0,0 | 20,0 ± 0,8 | 19,29 ± 0,40 | 19,98 ± 0,27 | 362 000 |
| `window` | 15,0 ± 0,0 | 22,6 ± 1,1 | 18,92 ± 0,18 | 11,24 ± 0,10 | 260 000 |
| `recent`, demi-résolution | 15,0 ± 0,0 | 44,6 ± 1,9 | 20,62 ± 0,51 | 20,56 ± 0,53 | 837 000 |
| **`uniform`, demi-résolution** | 15,0 ± 0,0 | **44,9 ± 0,2** | **21,38 ± 0,11** | 21,35 ± 0,13 | 827 000 |
| `uniform`, demi-résolution, sans remise des opacités | 15,0 ± 0,0 | 44,7 ± 1,2 | 19,40 ± 0,47 | 19,23 ± 0,14 | 921 000 |
| `uniform`, demi-résolution, version rapide | 15,0 ± 0,0 | 37,8 ± 0,5 | 21,09 ± 0,54 | **22,30 ± 0,42** | 688 000 |

Trois graines par ligne. L'évaluation a lieu toutes les 5 s de flux : 15,0 s veut dire entre 10 et 15 s. Le PSNR
final est mesuré 60 s après la fin du flux, sur les 70 vues de validation. Les versions rapides de `uniform` et
`recent` en pleine résolution sont en §4.3. Sortie complète : `$HOME\sp0\sp6\runs\summary.json`.

La version rapide de `uniform` 1/2 a le meilleur PSNR final, mais pas le meilleur en fin de flux, qui est le critère
de la règle. Elle finit avec moins de gaussiennes (688 000) : moins d'itérations, donc moins de densification
pendant le flux. Ce PSNR final ne dit rien de l'aperçu live, qui s'arrête à la fin du flux.

Courbes PSNR(temps de flux) des vues couvertes, moyenne des 3 graines, toutes les 10 s (`curves.py`). « 1/2 » :
demi-résolution ; « rapide » : version rapide (§4.3). Le flux finit à 122 s ; ensuite, 60 s d'entraînement seul. Les
versions rapides en pleine résolution, sans intérêt pour la conclusion, sont omises.

| t (s) | vues couvertes | `recent` | `recent` 1/2 | `uniform` | **`uniform` 1/2** | `uniform` 1/2 sans remise | `uniform` 1/2 rapide | `window` |
|---|---|---|---|---|---|---|---|---|
| 10 | 2 | - | 28,97 | - | 27,38 | - | 28,03 | 27,44 |
| 20 | 14 | 21,12 | 19,01 | 20,56 | 20,40 | 22,14 | 21,08 | 22,72 |
| 30 | 14 | 19,64 | 20,35 | 19,41 | 18,90 | 18,91 | 20,47 | 18,89 |
| 40 | 26 | 21,78 | 20,67 | 20,77 | 21,33 | 21,78 | 21,29 | 20,20 |
| 50 | 28 | 22,37 | 20,48 | 21,65 | 22,08 | 22,30 | 22,50 | 22,46 |
| 60 | 28 | 21,43 | 21,27 | 21,95 | 23,12 | 22,33 | 22,89 | 20,75 |
| 70 | 36 | 22,10 | 22,48 | 21,62 | 21,97 | 22,16 | 22,41 | 21,58 |
| 80 | 46 | 21,18 | 21,46 | 20,61 | 21,67 | 20,92 | 21,35 | 20,56 |
| 90 | 46 | 20,87 | 21,76 | 20,68 | 21,36 | 20,65 | 22,27 | 20,16 |
| 100 | 56 | 20,36 | 21,43 | 20,75 | 21,57 | 20,72 | 22,79 | 19,52 |
| 110 | 56 | 19,93 | 20,82 | 20,80 | 21,58 | 20,60 | 22,79 | 19,13 |
| 120 | 68 | 19,82 | 17,33 | 20,79 | 21,11 | 19,82 | 22,23 | 19,28 |
| 130 | 70 | 19,29 | 20,62 | 20,08 | 21,38 | 19,38 | 21,27 | 18,92 |
| 140 | 70 | 19,44 | 21,36 | 20,23 | 21,44 | 19,38 | 21,45 | 13,90 |
| 150 | 70 | 19,53 | 21,04 | 20,33 | 21,67 | 19,44 | 21,55 | 11,25 |
| 160 | 70 | 19,54 | 20,94 | 20,56 | 21,51 | 19,31 | 18,58 | 11,25 |
| 170 | 70 | 19,73 | 20,94 | 18,58 | 21,32 | 19,46 | 21,86 | 11,25 |
| 180 | 70 | 20,08 | 20,58 | 20,44 | 21,20 | 19,25 | 22,06 | 11,24 |

La colonne « vues couvertes » prend, pour chaque instant, le plus grand nombre de vues couvertes parmi les
configurations : l'horloge de chaque run exclut ses évaluations, donc elles ne tombent pas exactement au même instant.

Lecture :

- La ligne 10 s ne porte que sur 2 vues, sous le seuil de 4 : à ignorer.
- De 20 à 120 s, les vues couvertes passent de 14 à 68, et le PSNR baisse lentement dans presque toutes les
  configurations : les nouvelles zones sont plus dures que les premières. `uniform` 1/2 tient : de 40 à 180 s, elle
  reste entre 21,1 et 23,1 dB.
- Les creux isolés (17,33 dB pour `recent` 1/2 à 120 s, 18,58 pour `uniform` à 170 s et pour `uniform` 1/2 rapide à
  160 s) ne viennent pas de la remise des opacités. `uniform` 1/2 subit les mêmes remises, vers 67 et 134 s, sans creux
  marqué : elle perd au plus 1,2 dB, entre 60 et 70 s. Sans remise, il n'y a pas de creux, mais la courbe passe sous
  20 dB dès 120 s (§4.4). Ces creux viennent probablement d'une seule graine, qui tire la moyenne vers le bas.
- `window` décroche dès la fin du flux : elle ne s'entraîne plus que sur les dernières vues.

### 4.3 Version rapide (SSIM séparable, images sur GPU)

Passage `-Fast` du 2026-10-13, mêmes graines. La version rapide calcule le SSIM avec deux filtres 1D (même définition)
et garde les images d'entraînement sur le GPU en uint8 (environ 2,6 Go en pleine résolution pour S1).

| Configuration | it/s, version normale | it/s, version rapide | PSNR fin du flux, normale → rapide |
|---|---|---|---|
| hors ligne | 13,4 ± 0,6 | 9,4 ± 2,9 | (PSNR à 7 000 it. : 23,15 → 23,06) |
| `recent` | 20,0 ± 0,8 | 15,1 ± 0,1 | 19,29 → 18,71 |
| `uniform` | 18,9 ± 0,9 | 14,4 ± 0,1 | 20,08 → 20,03 |
| `uniform` 1/2 | 44,9 ± 0,2 | 37,8 ± 0,5 | 21,38 → 21,09 |

Profil d'une itération, hors ligne, pleine résolution, 300 itérations chronométrées partie par partie (en ms) :

| Partie | version normale | version rapide |
|---|---|---|
| pose | 0,6 | 0,9 |
| image | 0,6 | 0,2 |
| rendu | 16,6 | 24,3 |
| perte (L1 + SSIM) | 10,1 | 16,7 |
| rétropropagation | 44,2 | 63,0 |
| optimiseurs | 3,6 | 7,9 |
| densification | 0,5 | 0,7 |
| **total** | **76,2** (13,1 it/s) | **113,7** (8,8 it/s) |

**La version rapide est plus lente**, d'environ 25 % en flux et de 30 % hors ligne. Le profil dit pourquoi : seule la
copie de l'image gagne (0,4 ms). Toutes les autres parties ralentissent d'environ 1,5 fois, y compris le rendu, la
rétropropagation et les optimiseurs, que le SSIM ne touche pas. Ce n'est donc pas le SSIM séparable qui coûte : c'est
le GPU tout entier qui est ralenti. Avec 2,6 Go d'images sur une carte de 8 Go, plus jusqu'à 765 000 gaussiennes et
leurs états d'optimiseur, l'allocateur de torch est sous pression. Le PSNR suit le nombre d'itérations : il baisse, ou
ne bouge pas.

Conséquence : la version rapide n'est pas retenue. Sur un GPU de 8 Go, les images restent sur le CPU ; leur copie ne
coûte que 0,6 ms par itération. Le SSIM séparable, non testé seul, n'est pas une piste prioritaire : la perte ne fait
que 13 % d'une itération. La rétropropagation en fait 58 %, le rendu 22 %.

### 4.4 `uniform` en demi-résolution, version normale (`-UniformHalf`)

Passage du 2026-10-13, 3 graines, avec puis sans remise des opacités (`--reset-every 0`) :

| | 20 dB (s) | it/s | PSNR fin du flux (dB) | PSNR final (dB) | Gaussiennes |
|---|---|---|---|---|---|
| avec remise (toutes les 3 000 it.) | 15,0 ± 0,0 | 44,9 ± 0,2 | **21,38 ± 0,11** | **21,35 ± 0,13** | 827 000 |
| sans remise | 15,0 ± 0,0 | 44,7 ± 1,2 | 19,40 ± 0,47 | 19,23 ± 0,14 | 921 000 |

- La version normale confirme la recommandation du passage `-Fast` : elle est même meilleure en fin de flux
  (21,38 contre 21,09 dB) et quatre fois plus stable entre graines (écart-type de 0,11 contre 0,54).
- Sans remise des opacités, elle perd 2 dB et garde 11 % de gaussiennes en plus : les gaussiennes du semis aléatoire
  qui ne servent à rien ne sont plus élaguées. La remise reste.

## 5. Débit

GPU : NVIDIA GeForce RTX 3070, 8 Go. Images absorbées par seconde (une itération = une image) : 19 à 23 en pleine
résolution selon la stratégie, **44,9 en demi-résolution pour la configuration recommandée** (44,6 à 44,9 selon la
stratégie), contre environ 9,6 images par seconde produites par le casque (4,8 paires par seconde). Chaque image est
donc vue 2 fois en moyenne pendant le flux en pleine résolution, et 4,7 fois en demi-résolution. La version rapide
absorbe 14 à 15 images par seconde en pleine résolution, et 37,8 en demi-résolution (§4.3).

## 6. Lecture et limites

- Une seule scène (S1), un seul GPU, un rejeu à partir de fichiers : le transport réel (WP-14) n'y est pas.
- Le semis à profondeur aléatoire est une borne basse ; SP-7 mesure le gain de la profondeur du casque.
- Les vues de validation sont rendues avec leurs poses d'origine, sans raffinement (comme dans SP-0).
