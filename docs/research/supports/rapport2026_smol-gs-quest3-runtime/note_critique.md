# Note critique : « Projet : runtime 3DGS compact on-device pour Meta Quest 3 »

**Document :** [source.md](source.md). Rapport de cadrage rédigé par un agent IA à la demande de l'étudiant, daté du 2026-09-29. Ce n'est **pas une source scientifique** : il ne faut pas le citer comme tel, mais s'appuyer sur les références primaires qu'il mentionne.
**Proposition du rapport :** un runtime natif Rust + Vulkan + OpenXR sur Quest 3, piloté par le GPU, qui garde la scène sous forme Smol-GS compacte et ne décode que les morceaux visibles.
**Décision :** on reprend certaines idées dans P6 et P3′, et le moteur est gardé **en réserve** comme piste P7, voir [options.md](../../synthese/options.md) et [plan_environnement.md](../../synthese/plan_environnement.md), section « Piste R ».

## Repris dans notre plan
| Idée | Où elle va |
|---|---|
| Une référence simple d'abord, on mesure, puis on optimise (§16, §29) | Logique de P6 |
| p99 du temps d'image et images perdues plutôt que fps moyen (§12) | Métriques de P6 **et objectif du contrôleur P3′** |
| Runs thermiques longs de 5 à 60 min (§17, phase 7) | Phase 4 du plan |
| Imputation de la qualité : 3DGS d'origine → compressé hors ligne → rendu sur casque (§19) | Évaluation (options.md §4.C) |
| Anticipation par la position et la vitesse de la tête (§8) | **Composante anticipative de P3′** |
| Format de distribution séparé du format de rendu (§6) | Rôle de Smol-GS comme format de transport (P4/P1′) |
| Comparaison des méthodes de tri : radix GPU, par tuile, sans tri (§10) | Axe du banc de mesure P6 |

## Points contestés (vérifiés dans notre base)
1. **Il confond compression et coût de rendu (§2, §28).** Sur Quest 3, la limite est le nombre de Gaussiennes affichées par image et le *fill-rate*, pas le stockage :
   - Meta recommande ≤ 150k, les meilleurs chiffres annoncés sont ≈ 400–500k, et la résolution domine le coût selon VCIP 2026 ([faisabilite_quest3.md](../../synthese/faisabilite_quest3.md)) ;
   - même bicycle (6,13 M Gaussiennes, 1,5 GB en `.ply`) tient dans les 8 GB du casque ([donnees/inria_pretrained](../../donnees/inria_pretrained/README.md)).

   Une scène plus grosse doit quand même se limiter à ≈ 0,5 M Gaussiennes affichées : c'est un problème de **LOD**, pas de compression (enseignement n°7 d'options.md).
2. **Le « décodage à la demande » et le cache (§6, §11) se heurtent à la conception de Smol-GS.** Les MLP prennent en entrée la direction de vue et la distance, et prédisent l'opacité, la couleur, **la rotation et l'échelle** (éq. 2–3, `doc:d6bdbe6/tier:standard/page:4`). Le résultat change donc à chaque mouvement de tête : il n'y a pas de cache exact entre images, et il faut **deux décodages par splat en stéréo**. Ordre de grandeur (estimation personnelle, [fiche](../../sources/wang2025_smol-gs/fiche.md)) : ≈ 7,7·10⁴ multiplications-additions par splat et par œil, soit ≈ 5,5 TMAC/s pour 0,5 M splats à 72 Hz.
3. **L'octree de Smol-GS n'est pas un LOD (question 10).** C'est un octree d'occupation : au plus un splat par feuille, et **les nœuds internes ne portent aucune Gaussienne agrégée** (`page:4`). Pour en faire un LOD, il faudrait construire des niveaux grossiers comme [Hierarchical 3DGS](../../sources/kerbl2024_hierarchical-3dgs/fiche.md) ou [Octree-GS](../../sources/ren2024_octree-gs/fiche.md).
4. **Le décodage par morceaux suppose de changer le format.** Le codage arithmétique s'appuie sur une grille de hachage globale, avec un octree par scène (`page:5`). Décoder seulement les morceaux visibles demande de ré-encoder par morceau (*inféré, à vérifier dans le code*).
5. **Le jalon B (500k à 1M à 72 Hz stables) est optimiste** par rapport aux chiffres connus (≈ 400–500k au mieux, sans preuve pour 1M).
6. **Il s'éloigne du sujet.** Le sujet demande d'éviter les réseaux neuronaux coûteux. Smol-GS en ajoute au moment du rendu, avec un LPIPS moins bon que 3DGS (0,248 contre 0,214).

## Sources citées par le rapport, pas encore vérifiées
- 🔎 WallGS (walhargohar.com) : « budgets beaucoup plus élevés », sans chiffre ;
- 🔎 VkSplat (arXiv 2605.00219) ;
- 🔎 les 2 MB de mémoire de tuile de l'Adreno 740 (doc Meta) ;
- 🔎 le tutoriel Vulkan « gaussian-splats-rendering ».

Déjà dans la base ou vérifiées : [Mobile-GS](../../sources/du2026_mobile-gs/fiche.md) (2603.11531), Voyager (2506.02774, dans [anteriorite_p3_p6.md](../../synthese/anteriorite_p3_p6.md)), ATHENA/VCIP 2026, Meta Spatial SDK (150k), SqueezeMe (dans [faisabilite_quest3.md](../../synthese/faisabilite_quest3.md)).

## Ce qui trancherait la question
Le **micro-benchmark R0** : les 4 MLP de Smol-GS en compute Vulkan, en FP32 et FP16, pour 100k, 250k et 500k splats, sur les deux yeux, mesurés sur le Quest. Si le décodage mange l'essentiel des 13,9 ms à 72 Hz, P7 est à écarter sous cette forme. Sinon, la piste redevient crédible. On peut écrire et valider le code dès maintenant sur le portable (Rust 1.95, Vulkan 1.3).
