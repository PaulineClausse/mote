# SP-2 : synchronisation image/pose, repères, paires stéréo

Statut : terminé · Date : 2026-10-16 · Auteur : claude-agent@mote-session · Tâche : TASK-552b

Contexte : mote entraîne son aperçu live sur les poses du casque, sans les recalculer (ADR-0bbb). Cela suppose quatre
choses que la documentation Meta ne garantit pas : la pose fournie avec chaque image correspond à l'instant de la prise
(H-04, NFR-01 : 5 ms au plus), les deux caméras sont synchrones (H-09), l'obturateur et le flou ne dégradent pas la
géométrie aux vitesses de scan (H-10), les images sont sans distorsion (H-11). La formule de conversion Unity vers le
repère canonique (SPEC-64c5 §9.4) restait une hypothèse. WP-06 (hôte Unity) et WP-08 (conversion de repères) en
dépendent.

## 1. Verdicts

| Point | Verdict | Mesure |
|---|---|---|
| Formule de conversion | **Pose : formule de la spec confirmée. Images : à retourner verticalement.** | damier immobile à 1,8 mm et 0,22° près (médianes ; p95 4,1 mm et 0,45°), départage 78 fois meilleur que la formule suivante |
| Erreur de reprojection de la formule | **3,0 px** à gauche (p95 6,8), **6,6 px** à droite (p95 12,8) | pose MRUK convertie, toutes images |
| H-04, NFR-01 (≤ 5 ms) | **Validée avec réserve** | τ = 2,9 ms à gauche (IC 95 % 0,8 à 5,1), 3,8 ms à droite (1,6 à 6,2) ; recoupement par le suivi du casque 1,0 et 3,8 ms |
| H-09 (paires stéréo synchrones) | **Validée** | décalage droite − gauche −0,2 ms (IC 95 % −1,4 à 0,9) |
| H-10 (obturateur, flou) | **Validée jusqu'à 2 rad/s** | résidu PnP médian 0,10 px immobile, 0,19 px entre 1 et 2 rad/s ; damier plus détecté au-delà |
| H-11 (sténopé, pas de distorsion) | **Validée dans le champ observé** | résidu 0,10 à 0,12 px du centre jusqu'aux bords observés ; k1, k2 n'apportent rien (0,43 px dans les deux cas) |
| Seuil proposé pour `mote validate` | **15 px RMS par image**, 8 px une fois l'extrinsèque droite corrigée | au-dessus du p95 des deux yeux (6,8 et 12,8 px) |

### Formule de conversion

La pose MRUK se convertit comme le prévoit la spec : `world_from_camera` canonique = `S · T_unity · diag(1, -1, 1)`
côté caméra, avec `S = diag(1, 1, -1)` (équivalent à `T_gl = S T_unity S`, puis OpenGL vers OpenCV par
`diag(1, -1, -1)`).

**Mais les images RGBA de QuestRealityCapture sont stockées à l'envers verticalement** : la ligne 0 est le bas de
l'image, convention des textures Unity. Avec l'image prise telle quelle, aucune formule ne laisse le damier immobile
(16° et 77 mm de dispersion pour celle de la spec) ; une fois l'image retournée, la formule de la spec le tient à 1,8 mm
et 0,22°. La seule autre formule de même dispersion en rotation (`diag(-1,-1,-1)` sans retournement) déplace le damier
de 324 mm : elle est exclue.

Conséquence directe pour WP-06 : l'hôte Unity lit ses images par MRUK de la même façon et doit les retourner avant de
les pousser au core (ou le core doit savoir qu'elles arrivent retournées). Sans cela, toute la géométrie est fausse.

### Synchronisation image/pose (H-04, NFR-01)

τ est le décalage de la pose MRUK par rapport à l'instant où l'image a été prise (τ > 0 : pose plus tardive), estimé de
deux façons indépendantes :
- par l'écart de rotation entre la pose MRUK et la pose de la caméra mesurée sur le damier, rapporté à la vitesse
  angulaire, avec un biais constant estimé en même temps ;
- par le suivi du casque : l'instant auquel correspond l'image (δ image) et celui auquel correspond la pose MRUK
  (δ MRUK), dont la différence recoupe τ.

| Œil | τ (ms) | IC 95 % (ms) | δ image (ms) | δ pose MRUK (ms) | δ MRUK − δ image (ms) |
|---|---|---|---|---|---|
| gauche | 2,9 | 0,8 à 5,1 | −2,0 | −1,0 | 1,0 |
| droite | 3,8 | 1,6 à 6,2 | −4,8 | −1,0 | 3,8 |

Les deux méthodes concordent (3,8 et 3,8 ms à droite ; 2,9 et 1,0 ms à gauche, dans l'intervalle). Les valeurs
centrales sont sous les 5 ms de NFR-01 ; la borne haute de l'intervalle les dépasse de peu (5,1 et 6,2 ms), d'où la
réserve. À 1 rad/s, 4 ms valent 4 mrad, soit environ 3,5 px avec une focale de 868 px.

L'horodatage des images est proche de l'instant de prise : l'image précède son horodatage de 2 à 5 ms. La latence de
capture de 20 à 40 ms annoncée par la documentation ne se retrouve donc pas dans l'horodatage, qui date bien la prise.

### Paires stéréo (H-09)

Mesuré dans les images, sur 40 paires en mouvement où le damier est vu des deux yeux : la caméra droite prend son image
0,2 ms avant la gauche (IC 95 % −1,4 à 0,9 ms). La base stéréo mesurée sur le damier (63,3 mm) concorde avec celle des
poses MRUK (63,5 mm).

MRUK annonce un écart d'horodatage nul sur la grande majorité des paires, mais `mruk_stereo_pairs.csv` contient aussi des
paires à 13,9 ms et 27,8 ms d'écart : une ou deux images d'affichage (1/72 s). L'appariement doit se faire sur des
horodatages égaux, ou écarter ces paires.

### Vitesse (H-10)

| \|ω\| (rad/s) | Images | Résidu PnP médian / p95 (px) | Reprojection MRUK médiane (px) |
|---|---|---|---|
| 0 à 0,05 | 380 | 0,10 / 0,14 | 3,1 |
| 0,05 à 0,3 | 443 | 0,11 / 0,19 | 3,1 |
| 0,3 à 1 | 72 | 0,15 / 0,30 | 3,1 |
| 1 à 2 | 17 | 0,19 / 0,98 | 4,6 |
| au-delà de 2 | 0 | - | - |

Jusqu'à 2 rad/s, l'obturateur et le flou dégradent à peine la géométrie de l'image. Au-delà, le damier n'est plus
détecté du tout : le flou rend l'image inexploitable bien avant que l'obturateur ne déforme la géométrie. La
détection tombe déjà à 29 % (gauche) et 13 % (droite) des images dans la session de rotations. Pour le guidage du
scan, rester sous 1 rad/s.

### Distorsion (H-11)

| Distance moyenne des coins au centre (px) | Images | Résidu PnP médian (px) |
|---|---|---|
| 0 à 150 | 298 | 0,11 |
| 150 à 300 | 357 | 0,10 |
| 300 à 450 | 123 | 0,10 |
| au-delà de 450 | 45 | 0,12 |

Le résidu ne monte pas vers les bords, et une calibration avec k1 et k2 (focale et point principal de MRUK fixés) ne
l'améliore pas : les images sont déjà corrigées de la distorsion. Réserve : les vrais coins de l'image (au-delà
d'environ 600 px du centre) n'ont pas été couverts ; les coefficients extrapolés y donneraient 2 à 5 px, valeur non
mesurée.

## 2. Autres constats

- **Une session, un monde.** QuestRealityCapture remet l'origine du suivi à zéro au début de chaque session : la pose
  du casque y part de l'origine. Deux sessions ne se mélangent pas sans recalage. Avec une pose de damier commune aux
  sessions, la reprojection était bimodale (11 px contre 400 à 1000 px).
- **Extrinsèque de la caméra droite.** La pose MRUK de la caméra droite porte un biais constant de 3,3 mrad (0,19°) et
  le damier vu par l'œil droit est décalé de 3,3 mm par rapport à l'œil gauche : d'où 6,6 px de reprojection à droite
  contre 3,0 à gauche. Un raffinement de l'extrinsèque droite (WP-08 ou WP-17) ramènerait les deux yeux au même niveau.
- **Cadence réelle.** 9 images par seconde par œil, pour 10 demandées (`targetSaveFps`).
- **Détecteur du damier.** Sur 31 images (1,8 %), la grille est numérotée à l'envers ; l'analyse les renumérote.
- **Groupe non expliqué.** Sur l'œil droit, à la fin de la session de rotations (29 à 31 s), le damier paraît décalé de
  25 mm alors que la pose MRUK concorde avec le casque : vraisemblablement un mouvement de l'écran en fin de prise. 31
  images, gardées dans les statistiques (elles restent sous le p95).
- **Écran comme mire.** Damier affiché sur l'écran d'un ordinateur portable posé à plat, luminosité maximale : pas de
  scintillement visible (bandes à moins de 1 niveau de gris), surexposition modérée des cases blanches (6 à 11 % de
  pixels saturés), sans effet mesurable sur la détection.

## 3. Méthode

- **Capture** : QuestRealityCapture (SRC-1) non modifié, configuration de SP-2 (images à 10 i/s demandées, poses du
  casque à pleine cadence, profondeur coupée). Casque Quest 3S, build `UP1A.231005.007.A1`. Damier 10 x 7 cases
  (`sp2/damier_A4.pdf`) affiché en plein écran sur un Lenovo Yoga posé à plat, cases mesurées à la règle : **23,0 mm**.
- **Prises** (2026-10-16) : A, essai immobile (5 s) ; B, cinq positions immobiles (30 s) ; C, translations lentes
  (20 s) ; D, rotations de lentes à rapides (30 s) ; E, damier amené dans chaque coin de la vue (30 s). 1 526 images
  par œil, damier détecté sur 912 (gauche) et 835 (droite).
- **Analyse** (`sp2/analyze.py`, `sp2/sp2lib.py`) : détection du damier (OpenCV `findChessboardCornersSB`) ; pose de
  la caméra depuis le damier (PnP) ; pour chaque formule candidate, dispersion de la pose du damier dans le monde de sa
  session ; décalages par régression sur la vitesse angulaire et par recherche sur le suivi du casque ; calibration
  k1, k2 à focale et point principal fixés. Tests (`sp2/test_analyze.py`, 15) sur des sessions synthétiques à vérité
  connue : formule, retournement d'image, δ = −30 ms, τ = 4 ms, décalage stéréo de 2 ms, biais d'extrinsèque, mondes
  distincts par session, grilles retournées, distorsion.
- Réglages de l'analyse (seuils d'immobilité, vitesse minimale pour les décalages) : options de `analyze.py`.

## 4. Limites

- Une seule journée de capture, un seul casque, un écran comme mire.
- Peu d'images en rotation détectées des deux yeux (40 paires) : l'intervalle sur H-09 reste de l'ordre de la
  milliseconde.
- Les coins de l'image ne sont pas couverts (H-11).
- τ a un intervalle de confiance qui dépasse 5 ms : une capture dédiée, avec plus de rotations lentes et moyennes face
  au damier, le resserrerait.

## 5. Conséquences pour mote

1. **WP-06** : retourner verticalement les images MRUK avant de les pousser au core (à vérifier sur la première session
   de l'hôte : même source de texture que QuestRealityCapture).
2. **WP-08** : formule de conversion de la spec confirmée pour les poses ; seuil de reprojection de 15 px pour
   `mote validate`, à resserrer si l'extrinsèque droite est raffinée.
3. **Ingest** : apparier les images gauche et droite sur des horodatages égaux ; une session = un monde.
4. **Guidage du scan** (WP-16) : rester sous 1 rad/s de rotation de tête.
5. **SPEC-64c5 §9.3 et §9.4** à mettre à jour avec ces résultats (tâche dédiée).

## 6. Reproduire

Sur le PC de capture, sessions dans `$HOME\sp2` :
```powershell
uv run --no-project --with opencv-python-headless --with numpy python docs\spikes\sp2\analyze.py --square-mm 23.0 `
  "B=$HOME\sp2\20261016_144513" "C=$HOME\sp2\20261016_144715" "D=$HOME\sp2\20261016_144808" `
  "E=$HOME\sp2\20261016_144851" --out $HOME\sp2\analyse
```
Le kit (impression du damier, configuration, vérification d'une session) est décrit dans `sp2/README.md`.
