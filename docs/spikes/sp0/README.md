# SP-0a : kit de préparation de SP-0

Outils de spike jetables pour SP-0 (H-01, SPEC.md 14.1). **Pas du code mote.** Rien ici ne demande le casque ; le
casque ne sert qu'à capturer (PROTOCOL.md §3).

| Fichier | Rôle |
|---|---|
| `PROTOCOL.md` | protocole pas à pas : configuration SRC-1, capture, copie ADB, export SRC-3, SfM REF chronométré, splatfacto A, métriques, seuils, décision |
| `VERSIONS.md` | versions d'outils requises (Unity, nerfstudio, COLMAP, Python, CUDA...) et installation proposée |
| `align_sim3.py` | alignement Sim(3) de deux jeux de poses (COLMAP `images.txt` ou `transforms.json`), erreurs de translation, de rotation, dérive |
| `test_align_sim3.py` | test sur poses synthétiques à erreur injectée connue : `python test_align_sim3.py` |
| `metrics.py` | PSNR, SSIM (numpy) et LPIPS (torch + `lpips`) entre rendus et vues tenues à l'écart ; `--selftest` |
| `make_holdout.py` | hold-out par blocs (5 paires toutes les 40, gauche et droite ensemble) → `train_list.txt`, `test_list.txt` |
| `run_timed.py` | chronomètre une commande (COLMAP, `ns-train`) et journalise dans un JSON |
| `SP-0-template.md` | trame de `docs/spikes/SP-0.md` (à copier par la tâche SP-0) |

Vérification rapide sans GPU : `python test_align_sim3.py` (6 tests) et `python metrics.py --selftest`. Python 3.10 ou
plus avec numpy ; Pillow pour `metrics.py` ; LPIPS demande torch.
