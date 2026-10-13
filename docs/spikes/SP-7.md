# SP-7 : initialisation par la profondeur du casque pour l'aperçu live

Statut : brouillon. Méthode et règle fixées avant les mesures · Date : 2026-10-13 · Auteur : claude-agent@mote-session
· Tâche : TASK-697a

Contexte : option B de SPEC 11.3. Au lieu des gaussiennes semées à profondeur aléatoire (SP-6), on part de la
géométrie mesurée par le casque, ce qui devrait raccourcir la convergence de l'aperçu live.
- SP-6 a fixé le banc : rejeu de S1 en flux, `uniform` en demi-résolution, 20 dB à 15 s (un plancher fixé par
  l'arrivée des vues), puis 21,4 dB en fin de flux.
- SP-3 a fixé la profondeur : formule `near / (1 - d)` de bonne forme, échelle à ±5 % près par rapport au tracking,
  carte dense et lissée sans masque de validité, reflets dans les vitres.

## 1. Verdict (à remplir en dernier)

Nuage d'initialisation : ___ points, alignement ___ (échelle, résidu).
Hors ligne, 30 000 itérations : 20 dB à ___ s (profondeur) contre ___ s (aléatoire) ; PSNR final ___ contre ___ dB.
Flux (SP-6, `uniform` en demi-résolution) : PSNR moyen du flux ___ contre ___ dB ; 20 dB à ___ contre ___ s.
Recommandation pour l'option B en live : ___

## 2. Règle, écrite avant de regarder les chiffres

Le but est l'aperçu live. En flux, le temps jusqu'à 20 dB bute sur un plancher de 15 s, fixé par l'arrivée des vues
(SP-6). La règle porte donc d'abord sur le **PSNR moyen du flux** : la moyenne des évaluations faites toutes les 5 s, de
20 s à la fin du flux, sur les vues couvertes (au moins 4). Moyennes sur 3 graines, même configuration que la meilleure
de SP-6 (`uniform`, demi-résolution).

- **Option B recommandée pour le live** si le PSNR moyen du flux gagne au moins 0,5 dB, ou si 20 dB est atteint plus
  tôt de plus d'un écart-type. Il faut en plus que le PSNR en fin de flux ne baisse pas, et que le PSNR final (60 s après
  le flux) ne perde pas plus de 0,3 dB.
- **Déconseillée** si le PSNR moyen du flux perd au moins 0,5 dB, ou si le PSNR final perd plus de 0,3 dB.
- **Neutre** sinon : pas de gain suffisant pour le coût de l'option (flux de profondeur de 33 Mbit/s avant zstd,
  rétroprojection à l'ingest, SP-3).
- **Hors ligne** (30 000 itérations, pleine résolution, évaluation toutes les 200 itérations) : temps jusqu'à 20 dB et
  PSNR final, rapportés pour information et pour la passe finale. Ils ne changent pas la recommandation pour le live.

Date de fixation de la règle : 2026-10-13, avant toute mesure.

## 3. Méthode

Outils : `docs/spikes/sp7/` (README.md). L'entraîneur est celui de SP-6 (`docs/spikes/sp6/incremental.py`), avec une
seule option en plus : `--init-npz`. Sans elle, il se comporte exactement comme avant.

- **Nuage d'initialisation** (`depth_init.py`) :
  - les cartes gauches et droites de S1, enregistrées à 5 Hz par QuestRealityCapture, sont linéarisées par la formule
    de SP-3, avec un pixel sur 4 et une profondeur de 0,3 à 4,5 m ;
  - les pixels de bord sont rejetés : un voisin s'écarte de plus de 3 % (SP-3 : la carte est lissée) ;
  - le hold-out est exclu : aucune carte prise à moins de 0,25 s d'une vue de validation ;
  - les points passent dans le repère du jeu commun par une similitude, ajustée en alignant la trajectoire de la caméra
    de profondeur sur les centres des caméras RGB appariées dans le temps (Umeyama). L'échelle et le résidu sont
    rapportés : on attend une échelle de 1 et quelques centimètres ;
  - la couleur vient de l'image d'entraînement la plus proche dans le temps ;
  - une grille de 2,5 cm garde un point par voxel, celui vu en premier, avec 300 000 points au plus.
- **Semis** : chaque point devient une gaussienne de la taille du voxel, avec une opacité de 0,1, comme le semis
  aléatoire. Hors ligne, tout le nuage est semé au départ. En flux, un point est semé quand sa carte de profondeur est
  arrivée, à l'arrivée de la vue suivante.
- **Comparaisons** :
  - flux : 3 graines, `uniform`, demi-résolution, aléatoire contre profondeur ;
  - hors ligne : 3 graines, pleine résolution, 30 000 itérations, aléatoire contre profondeur ;
  - le tout comparé par `compare.py`, qui applique §2.

Vérifications sans GPU :
- `depth_init.py` sur une scène synthétique (mur plan, repère du jeu tourné de 30°) : alignement retrouvé, points sur le
  mur à 2 mm près, couleurs des bonnes vues, hold-out exclu ;
- la boucle de SP-6 avec `--init-npz` sur CPU, avec un faux rendu : tout le nuage au départ hors ligne, et des points qui
  arrivent avec le flux ;
- la règle (`test_compare.py`).

## 4. Résultats

### 4.1 Nuage d'initialisation

___

### 4.2 Flux (aperçu live)

___

### 4.3 Hors ligne, 30 000 itérations

___

## 5. Lecture et limites

- Une seule scène (S1) ; la profondeur y voit vraisemblablement des reflets dans les vitres (SP-3 §4.4). Ils ne sont
  pas filtrés : ils entrent dans le nuage comme dans un usage réel.
- L'échelle de la profondeur n'est connue qu'à 5 % près par rapport au tracking (SP-3). L'alignement ne la corrige pas :
  la similitude porte sur la trajectoire, pas sur les valeurs de profondeur.
- Les cartes sont à 5 Hz, cadence de S1 (SP-0). La profondeur native est d'environ 8,3 Hz (SP-3).
