# SP-5 : débit réseau soutenu casque vers PC

Statut : terminé · Date : 2026-10-16 · Auteur : claude-agent@mote-session · Tâche : TASK-1227

Contexte : le flux live du casque vers le PC (ADR-006, ADR-c36f : TCP, trames préfixées par leur taille) doit porter,
au pire, environ 100 Mbit/s d'images JPEG et de profondeur brute (SPEC-234a §6.2). H-06 suppose que le Wi-Fi 6 en
5 GHz le soutient en continu. WP-14 (transport live, rattrapage) en dépend.

## 1. Verdict

**H-06 : validée.** Pendant 180 s, en se déplaçant avec le casque dans un rayon de 4 m, le débit TCP casque vers PC
vaut **200,1 Mbit/s en moyenne** et **153,7 Mbit/s au minimum** sur fenêtre glissante de 10 s, soit 1,5 fois les
100 Mbit/s demandés dans la pire fenêtre. Une seule seconde sur 180 passe sous 100 Mbit/s (90,6 Mbit/s).

**ADR-006 (transport TCP, ADR-c36f) : confirmé pour le débit.** Une seule connexion TCP porte le double du pire cas
estimé, sans réglage. La condition de remise en cause de l'ADR porte sur la latence du live au regard de NFR-04 (premier
aperçu en 60 s au plus). Elle n'est pas en jeu à cette échelle : le RTT au repos est de 6 ms. La latence sous charge
n'a pas été mesurée (§5).

## 2. Règle

Fixée par H-06 (SPEC.md) et le critère de la tâche, avant la mesure de 3 minutes : H-06 est validée si le **minimum
sur fenêtres glissantes de 10 s** atteint 100 Mbit/s. La moyenne seule ne suffit pas : un creux prolongé ferait
déborder la file live du casque (ADR-c36f) même avec une bonne moyenne.

## 3. Méthode

- **Émetteur** : le casque lui-même, par `adb shell "toybox nc <IP du PC> 5001 < /dev/zero"`. toybox 0.8.9 est
  présent sur le système du Quest. Rien à compiler, aucune application. Le flux est du TCP brut, sans cadrage ni
  protobuf : il mesure ce que la liaison laisse passer, pas le coût de sérialisation.
- **Récepteur** : `docs/spikes/sp5/receiver.py` sur le PC, bibliothèque standard seulement. Il compte les octets reçus
  par seconde pendant 180 s à partir du premier octet, puis ferme. Tests : `test_receiver.py` (calcul des fenêtres,
  mesure en boucle locale).
- **Casque** : Quest 3S, build `UP1A.231005.007.A1`, maintenu éveillé (`svc power stayon true`, capteur de proximité
  neutralisé). Tenu en main, **déplacé dans un rayon d'environ 4 m** pendant les 3 minutes, comme pendant un scan.
- **Réseau** : point d'accès du réseau de l'établissement (SSID `CESI_Recherche`), Wi-Fi 6 (802.11ax), **5 GHz,
  canal 60**, WPA3-Personnel. Modèle et emplacement du point d'accès non connus ; distance au casque inconnue.
- **PC** : RTX 3070, Windows, **en Wi-Fi sur le même point d'accès** (Intel Wi-Fi 6E AX211 160 MHz, pilote
  22.220.0.4, liaison agrégée 344/459 Mbit/s). Pas de liaison filaire disponible.
- Un essai de 20 s, casque posé et immobile, a précédé la mesure : 225,3 Mbit/s en moyenne, 204,7 au minimum sur 10 s.

Le PC en Wi-Fi est le cas défavorable : chaque octet traverse l'air deux fois (casque vers point d'accès, puis point
d'accès vers PC) sur le même canal. Un PC en filaire derrière le point d'accès ne peut que faire mieux.

## 4. Résultats

Mesure de 180 s, casque en mouvement (`sp5/sp5_result.json`, série par seconde) :

| Mesure | Valeur |
|---|---|
| Octets reçus | 4 501 765 496 |
| **Débit moyen** | **200,1 Mbit/s** |
| **Minimum sur fenêtre de 10 s** | **153,7 Mbit/s** (secondes 157 à 166) |
| Maximum sur fenêtre de 10 s | 238,1 Mbit/s |
| Médiane par seconde | 204,2 Mbit/s |
| 5e centile par seconde | 142,8 Mbit/s |
| Pire seconde | 90,6 Mbit/s (seconde 175) |
| Secondes sous 100 / 120 / 150 Mbit/s | 1 / 4 / 15 sur 180 |
| Moyenne par minute | 206,0 · 195,8 · 198,4 Mbit/s |

Pas de dérive sur les trois minutes. Le creux de la fin (secondes 157 à 177, de 90 à 180 Mbit/s) est le seul passage
prolongé sous 150 Mbit/s ; il correspond vraisemblablement à une position du casque plus défavorable pendant le
déplacement, sans qu'on puisse l'attribuer (position non relevée).

La série a été reconstituée depuis la sortie console du récepteur, qui affiche chaque seconde une fois terminée ; la
dernière seconde est déduite du total d'octets. Recalculée, elle redonne exactement la moyenne, le minimum et le
maximum imprimés par le récepteur.

## 5. Lecture et limites

- **Marge** : la pire fenêtre de 10 s vaut 1,5 fois le pire cas estimé de 100 Mbit/s (SPEC-234a §6.2) et 2,6 fois la
  cible de débit moyen de NFR-03 (60 Mbit/s, sélection active). Le transport n'est pas le facteur limitant de mote.
- **Une session, un lieu, un réseau partagé.** Le réseau de l'établissement porte d'autres usagers ; leur charge
  n'est pas connue. Un autre lieu (Wi-Fi domestique, 2,4 GHz, cloisons) peut donner beaucoup moins : H-06 est validée
  pour du Wi-Fi 6 en 5 GHz, ce qu'elle énonce, pas au-delà.
- **Casque sans autre charge.** L'émetteur est un processus shell : ni rendu Unity, ni acquisition MRUK, ni encodage
  JPEG en parallèle. La concurrence pour le CPU et la radio pendant un vrai scan relève de H-05 et des tests de charge
  de WP-18.
- **Latence sous charge non mesurée.** Le RTT au repos est de 6 ms (ping). La latence du live sous charge, avec la file
  bornée du casque, se mesurera dans WP-14.
- **Creux d'une seconde.** Une seconde à 90 Mbit/s reste possible même en bonnes conditions : la file live bornée du
  casque (ADR-c36f) doit absorber quelques secondes de creux sans retirer de données ; WP-14 peut se dimensionner sur
  ces chiffres (5e centile à 143 Mbit/s).
- **Débit du lien du casque non relevé** (`adb shell dumpsys wifi`), ni sa force de signal.

## 6. Reproduire

```powershell
adb shell svc power stayon true
adb shell am broadcast -a com.oculus.vrpowermanager.prox_close
# terminal 1, sur le PC
uv run --no-project python docs\spikes\sp5\receiver.py --seconds 180 --out docs\spikes\sp5\sp5_result.json
# terminal 2, une fois le récepteur en attente
adb shell "toybox nc <IP du PC> 5001 < /dev/zero"
```
Si rien ne se connecte, le pare-feu Windows bloque probablement le port 5001 (réseau classé « Public ») : autoriser
Python sur le réseau privé.
