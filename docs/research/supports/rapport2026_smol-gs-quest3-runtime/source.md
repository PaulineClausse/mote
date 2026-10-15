# Projet: runtime 3DGS compact on-device pour Meta Quest 3

> Document de cadrage et de recherche destiné à un agent chargé de poursuivre l'état de l'art, de vérifier les hypothèses et de proposer une architecture d'implémentation.

**Date:** 2026-09-29  
**Cible principale:** Meta Quest 3, standalone, scène entièrement on-device  
**Langage/runtime envisagé:** Rust  
**Représentation de départ:** Smol-GS  
**Backend graphique envisagé:** Vulkan  
**Objectif principal:** rendre des scènes 3D Gaussian Splatting compactifiées avec une QoS VR stable, faible latence et consommation maîtrisée, sans dépendre d'un PC/cloud au runtime.

---

## 1. Résumé exécutif

L'idée est de construire un **runtime natif de scènes 3D Gaussian Splatting (3DGS) compactes**, capable de charger et rendre des représentations de type **Smol-GS** directement sur un **Meta Quest 3**.

Le point de départ est Smol-GS, qui propose une représentation compacte des scènes 3DGS: coordonnées codées via une hiérarchie voxel/octree, features de splats quantifiées et codées entropiquement, et petites MLP permettant de décoder des propriétés abstraites des splats. Les auteurs rapportent des représentations pouvant être environ deux ordres de grandeur plus petites que des modèles 3DGS classiques, avec une qualité visuelle comparable sur leurs benchmarks. [SOURCE: Smol-GS](https://aaltoml.github.io/Smol-GS/)

L'hypothèse centrale du projet est la suivante:

> **La bonne architecture n'est pas de décompresser toute une scène Smol-GS en millions de splats classiques puis de les rendre, mais de construire un runtime GPU-driven capable de conserver la scène sous forme compacte, sélectionner les données visibles/pertinentes et décoder seulement ce qui est nécessaire.**

Le projet devrait donc être abordé comme un **moteur/runtime de rendu XR spécialisé**, et non comme un simple viewer de fichiers 3DGS.

---

# 2. Pourquoi le problème est intéressant

Le Quest 3 dispose d'un Snapdragon XR2 Gen 2, de 8 Go de RAM et d'un GPU nettement plus puissant que celui du Quest 2. Meta indique aujourd'hui environ 2,5× les performances GPU du Quest 2 pour le Quest 3 dans son tableau matériel, avec des fréquences de 72, 80, 90 et 120 Hz. [SOURCE: Meta device comparison](https://developers.meta.com/horizon/resources/device-optimization-comparison/)

Cela reste toutefois une plateforme mobile avec:

- mémoire et bande passante limitées par rapport à un PC GPU;
- budget thermique;
- consommation batterie;
- GPU tile-based;
- contraintes fortes de frame time en VR;
- besoin de maintenir une cadence stable, pas simplement une moyenne élevée.

Une étude récente dédiée au Quest 3 a testé 180 combinaisons de résolution, densité de splats et distance caméra, avec une cible de 72 Hz. Elle rapporte que la résolution de rendu est un facteur majeur du coût GPU, et que réduire la densité de splats devient particulièrement utile lorsque le GPU est déjà proche du budget de frame. [SOURCE: ATHENA/VCIP 2026](https://athena.itec.aau.at/2026/09/3d-gaussian-splatting-rendering-performance-trade-offs-on-the-meta-quest-3/)

Le problème est donc double:

1. **représentation:** faire tenir des scènes beaucoup plus grosses que des 3DGS classiques;
2. **rendu:** transformer cette représentation compacte en images stéréo avec un frame time stable.

---

# 3. Ce que nous avons trouvé sur Smol-GS

Smol-GS est particulièrement pertinent comme point de départ parce qu'il ne se contente pas d'appliquer une compression générique à un fichier 3DGS.

La représentation combine plusieurs mécanismes:

```text
                Smol-GS
                   |
       +-----------+-----------+
       |                       |
       v                       v
coordonnées                splat features
       |                       |
occupancy octree          abstract features
       |                       |
entropy/arithmetic        quantization
coding                         |
                               v
                         tiny MLP decoders
```

Les coordonnées des splats sont représentées via une hiérarchie spatiale récursive. Les features par splat sont des représentations abstraites pouvant encoder couleur, opacité, transformation et propriétés de matériau. Les auteurs utilisent également quantification, codage arithmétique et apprentissage des coûts de représentation. [SOURCE: Smol-GS](https://aaltoml.github.io/Smol-GS/)

Le point particulièrement intéressant pour notre cas est que Smol-GS conserve une structure compatible avec le paradigme Gaussian Splatting tout en remplaçant les gros paramètres explicites par une représentation plus compacte.

### Conséquence architecturale

Il faut éviter de concevoir:

```text
Smol-GS
   |
   v
décompression complète
   |
   v
énorme tableau de splats
   |
   v
renderer
```

et plutôt viser:

```text
Smol-GS
   |
   v
spatial index
   |
   v
visibility / LOD
   |
   v
sélection de chunks
   |
   v
GPU decode
   |
   v
GPU render
```

La différence est fondamentale pour la mémoire et le QoS.

---

# 4. Pourquoi un renderer Rust/Vulkan

## Rust

Rust est intéressant principalement pour le runtime système:

- contrôle explicite des allocations;
- absence de garbage collector;
- gestion sûre des buffers et ressources;
- bonne intégration native Android;
- possibilité de construire une architecture très déterministe;
- séparation claire CPU / GPU;
- faible overhead d'abstraction si le code est conçu correctement.

Rust ne rend pas automatiquement le renderer rapide. La performance viendra surtout de l'architecture GPU, du layout mémoire, du culling, du streaming et du nombre de travaux réellement exécutés.

## Vulkan

Vulkan est intéressant parce qu'il permet de contrôler explicitement:

- compute pipelines;
- storage buffers;
- indirect dispatch/draw;
- synchronisation;
- memory allocation;
- descriptor management;
- async compute;
- formats FP16;
- multi-view/stereo;
- pipelines spécialisés.

La documentation Vulkan fournit déjà une implémentation pédagogique de rendu 3DGS avec projection de covariance, rasterisation de splats, tri en profondeur et pistes d'optimisation GPU. [SOURCE: Vulkan Gaussian Splatting tutorial](https://docs.vulkan.org/samples/latest/samples/complex/render_octomap/Tutorials/gaussian-splats-rendering.html)

Il existe également des travaux récents montrant des pipelines 3DGS entièrement basés sur Vulkan Compute, ce qui renforce l'intérêt de cette direction pour un renderer portable et contrôlé. [SOURCE: VkSplat](https://arxiv.org/abs/2605.00219)

---

# 5. Architecture cible proposée

Architecture conceptuelle:

```text
                    .smolgs
                       |
              +--------v---------+
              |   Scene Loader   |
              |      Rust        |
              +--------+---------+
                       |
              compressed scene
                       |
              +--------v---------+
              | Spatial / Chunk  |
              |    Manager       |
              +--------+---------+
                       |
                 visible chunks
                       |
              +--------v---------+
              | GPU Upload /     |
              | Streaming        |
              +--------+---------+
                       |
              +--------v---------+
              | Vulkan Compute   |
              |                  |
              | culling          |
              | LOD              |
              | decode           |
              | projection       |
              | compaction       |
              | sorting          |
              +--------+---------+
                       |
              +--------v---------+
              | Splat Renderer   |
              | / Rasterization  |
              +--------+---------+
                       |
                  Quest display
```

Le CPU doit rester essentiellement un **orchestrateur**.

Il ne faut pas transformer chaque frame en:

```text
CPU:
  charger
  décompresser
  calculer
  trier
  envoyer
  attendre
```

Il faut tendre vers:

```text
CPU:
  caméra
  scheduling
  streaming
  orchestration

GPU:
  culling
  LOD
  decode
  projection
  compaction
  sorting
  rendering
```

---

# 6. Représentation runtime recommandée

Le format de distribution peut rester fortement compressé, mais le GPU ne doit pas forcément travailler directement sur la représentation bit-level.

Proposition:

```text
                .smolgs
                   |
                   v
        +----------------------+
        | compressed storage   |
        |                      |
        | octree                |
        | entropy coded data   |
        | quantized features   |
        | metadata             |
        +----------+-----------+
                   |
             runtime decode
                   |
                   v
        +----------------------+
        | GPU runtime format   |
        |                      |
        | packed positions     |
        | packed covariance    |
        | FP16 features        |
        | opacity              |
        | material data        |
        | LOD metadata         |
        +----------------------+
```

Cela permet de distinguer:

- **format de distribution**, optimisé pour taille disque/transfert;
- **format runtime**, optimisé pour bande passante GPU et accès mémoire.

Le runtime pourrait maintenir un cache de chunks décodés.

---

# 7. Spatialisation, chunks et LOD

La hiérarchie spatiale de Smol-GS est potentiellement un point d'appui naturel pour un système de streaming et LOD.

Une scène pourrait être organisée ainsi:

```text
Scene
 |
 +-- root
      |
      +-- node
      |    +-- chunk
      |    +-- chunk
      |
      +-- node
           +-- chunk
           +-- chunk
```

Pour chaque frame:

```text
camera
  |
  v
frustum
  |
  v
octree traversal
  |
  +-- invisible -> discard
  |
  +-- far -> coarse LOD
  |
  +-- medium -> medium LOD
  |
  +-- near -> high LOD
  |
  v
visible chunks
```

Le but est de ne jamais considérer la totalité de la scène comme un ensemble homogène de splats.

---

# 8. Streaming

À terme, le runtime devrait être capable d'avoir une scène plus grosse que la représentation active en mémoire GPU.

Concept:

```text
          disk / APK / file
                 |
                 v
          compressed chunks
                 |
             async I/O
                 |
                 v
             CPU cache
                 |
           async transfer
                 |
                 v
             GPU cache
                 |
                 v
              render
```

Le streaming doit être anticipatif.

La caméra actuelle et sa vélocité peuvent servir à estimer les chunks qui seront nécessaires prochainement.

Exemple:

```text
camera position
camera velocity
view direction
        |
        v
prefetch prediction
        |
        v
load likely-visible chunks
```

Cela devient particulièrement important pour une navigation VR rapide.

---

# 9. Rendering pipeline

Pipeline cible possible:

```text
Frame N
 |
 +-- Camera update
 |
 +-- Update visible octree nodes
 |
 +-- Select LOD
 |
 +-- Select resident chunks
 |
 +-- Async upload missing chunks
 |
 +-- GPU culling
 |
 +-- GPU decode
 |
 +-- Project Gaussians
 |
 +-- Compact visible splats
 |
 +-- Depth ordering
 |
 +-- Stereo rendering
 |
 +-- Present
```

Certaines étapes pourront être fusionnées.

L'ordre exact doit être déterminé par profiling.

---

# 10. Le problème du sorting

Le 3DGS classique dépend généralement d'un ordre de profondeur pour obtenir un alpha blending correct. La documentation Vulkan décrit explicitement le depth sorting comme nécessaire pour le pipeline classique et mentionne notamment CPU sort, GPU radix sort et tile-based sorting. [SOURCE: Vulkan](https://docs.vulkan.org/samples/latest/samples/complex/render_octomap/Tutorials/gaussian-splats-rendering.html)

Cela peut devenir l'un des principaux coûts.

Trois pistes doivent être étudiées:

### A. GPU radix sort

Solution relativement directe:

```text
splats
  |
depth key
  |
GPU radix sort
  |
sorted splats
```

### B. Tile-based sorting

Réduire le problème à des listes locales par tile:

```text
screen
+----+----+----+
| T0 | T1 | T2 |
+----+----+----+
| T3 | T4 | T5 |
+----+----+----+
```

Chaque tile ne trie que les splats qui l'affectent.

### C. Order-independent / approximate rendering

Des travaux récents comme Mobile-GS explorent des méthodes qui évitent le sorting complet avec un rendu depth-aware order-independent, au prix potentiel d'artefacts de transparence, complétés par un traitement neural des effets dépendants du point de vue. [SOURCE: Mobile-GS](https://arxiv.org/abs/2603.11531)

**Recommandation:** ne pas choisir A/B/C théoriquement. Implémenter d'abord une baseline correcte, puis benchmarker les trois familles sur Quest 3.

---

# 11. Le problème du MLP Smol-GS

C'est probablement le principal point de recherche spécifique à Smol-GS.

Le runtime doit décoder des features abstraites avec de petits MLP.

Naïvement:

```text
1 splat
   |
MLP
   |
decoded properties
```

est probablement trop coûteux à grande échelle.

Il faut tester:

```text
chunk
  |
batched MLP
  |
decoded chunk
```

et déterminer:

- taille optimale de batch;
- FP32 vs FP16;
- fusion des opérations;
- nombre de couches;
- nombre de features;
- partage de décodage entre splats voisins;
- cache des résultats;
- fréquence de recalcul;
- possibilité de pré-calculer certaines propriétés.

Un travail VR antérieur, SqueezeMe, identifie justement le décodeur et le rendu comme deux gros goulots d'étranglement sur Quest 3 et utilise un pipeline Vulkan custom. Les auteurs rapportent jusqu'à trois avatars Gaussian simultanément à 72 FPS après leurs optimisations. [SOURCE: SqueezeMe](https://arxiv.org/abs/2412.15171)

Cela constitue un signal important: **le coût neural ne doit pas être considéré comme secondaire.**

---

# 12. QoS: objectif principal

Le projet ne doit pas optimiser uniquement le FPS moyen.

Pour VR, il faut suivre au minimum:

- frame time CPU;
- frame time GPU;
- 99e percentile frame time;
- dropped/stale frames;
- motion-to-photon latency si mesurable;
- GPU utilization;
- CPU utilization;
- power draw;
- température;
- fréquence CPU/GPU;
- mémoire système;
- mémoire GPU;
- bande passante mémoire;
- temps de streaming;
- nombre de chunks actifs;
- nombre de splats actifs;
- coût du decode;
- coût du sorting;
- coût du rasterization;
- overdraw.

Une scène qui fait:

```text
11 ms
12 ms
11 ms
45 ms
11 ms
```

est un échec QoS même si la moyenne semble acceptable.

Il faut privilégier une performance stable.

---

# 13. Budget de frame

Le Quest 3 supporte notamment 72, 80, 90 et 120 Hz. [SOURCE: Meta](https://developers.meta.com/horizon/essentials/compare-devices/)

Budgets théoriques:

| Refresh | Budget/frame |
|---:|---:|
| 72 Hz | 13.89 ms |
| 80 Hz | 12.50 ms |
| 90 Hz | 11.11 ms |
| 120 Hz | 8.33 ms |

Le premier objectif devrait être **72 Hz stable**, puis 90 Hz.

Il ne faut pas commencer par optimiser pour 120 Hz. Ce serait une excellente manière de passer trois semaines à optimiser un shader avant de découvrir que le problème réel est le streaming.

---

# 14. Particularité du GPU Quest 3

Le Quest 3 utilise un XR2 Gen 2 avec GPU Adreno 740. Meta documente son architecture de rendu tiled et indique environ 2 Mo de tile memory pour l'Adreno 740/XR2 Gen 2. [SOURCE: Meta GPU pipeline documentation](https://developers.meta.com/horizon/documentation/unity/po-advanced-gpu-pipelines/)

Cela signifie qu'il faut considérer sérieusement:

- overdraw;
- coût des blending operations;
- taille des render targets;
- nombre de passes;
- loads/stores;
- MSAA;
- multiview;
- organisation des tiles.

Le renderer ne doit donc pas être conçu comme un renderer desktop simplement porté vers Android.

---

# 15. Stereo / VR

Le renderer doit être conçu nativement pour deux yeux.

Une approche à étudier est le **Mobile Multi-View**, déjà utilisée/recommandée dans certains renderers Gaussian Splatting standalone Quest. [SOURCE: WallGS documentation](https://walhargohar.com/WallGS/documentation/wallgs/)

L'objectif est d'éviter de traiter deux fois autant de données lorsque certaines étapes peuvent être partagées.

Pipeline potentiel:

```text
                scene data
                    |
             shared visibility
                    |
          +---------+---------+
          |                   |
       left eye            right eye
          |                   |
       projection          projection
          |                   |
          +---------+---------+
                    |
                 render
```

La possibilité de partager culling, decode et certaines données entre les yeux doit être mesurée.

---

# 16. Baseline indispensable

Avant d'implémenter Smol-GS, construire un renderer minimal de 3DGS classique.

Objectif:

```text
PLY
 |
Rust
 |
Vulkan
 |
Quest 3
 |
stable stereo rendering
```

Fonctions minimales:

- position;
- scale;
- rotation/covariance;
- opacity;
- RGB ou SH simplifié;
- projection;
- culling;
- sorting;
- rasterization;
- stereo.

Cette baseline permet de répondre à:

> combien de splats un renderer Rust/Vulkan contrôlé peut-il réellement afficher sur Quest 3?

Sans cette donnée, impossible de savoir si Smol-GS est réellement le goulot d'étranglement ou si le renderer lui-même est insuffisant.

---

# 17. Plan d'implémentation recommandé

## Phase 0 - Recherche

Durée indicative: quelques jours.

Questions:

- format exact Smol-GS;
- licence/code disponible;
- architecture exacte des MLP;
- tailles des features;
- quantification;
- entropy coding;
- octree;
- benchmarks publiés;
- format des checkpoints;
- possibilités de réimplémentation indépendante;
- contraintes Android;
- Vulkan supporté par Quest 3;
- possibilités de FP16;
- possibilités de subgroup operations;
- limitations du driver.

Livrable:

```text
research.md
```

---

## Phase 1 - Quest Vulkan hello-world

Objectif:

- application Android native;
- Rust;
- Vulkan;
- surface Quest;
- OpenXR ou couche XR minimale;
- triangle/quad;
- profiling GPU.

Livrable:

```text
quest-vulkan/
```

Critère de réussite:

> application stable installable sur Quest 3 avec instrumentation de performance.

---

## Phase 2 - Renderer 3DGS minimal

Implémenter:

```text
PLY
 ↓
CPU upload
 ↓
GPU buffers
 ↓
projection
 ↓
sorting
 ↓
rasterization
```

Commencer avec 10k, 50k, 100k, 250k, 500k, 1M splats.

Mesurer:

- CPU ms;
- GPU ms;
- FPS;
- memory;
- power si possible.

---

## Phase 3 - GPU-driven pipeline

Déplacer progressivement:

- frustum culling;
- size culling;
- opacity culling;
- compaction;
- depth calculation;
- sorting.

Objectif:

```text
CPU
 └── camera + orchestration

GPU
 ├── culling
 ├── compaction
 ├── sorting
 └── rendering
```

---

## Phase 4 - Octree / LOD

Introduire une représentation hiérarchique.

Tests:

```text
1M splats
5M splats
10M splats
```

avec plusieurs LOD.

Mesurer:

- visible splats/frame;
- upload/frame;
- GPU memory;
- quality loss;
- popping;
- temporal stability.

---

## Phase 5 - Smol-GS decoder

Implémenter le format Smol-GS côté CPU.

Puis déplacer progressivement le decode vers GPU.

Ordre recommandé:

```text
CPU decode
   ↓
GPU upload
```

puis:

```text
compressed
   ↓
GPU decode
   ↓
render
```

Le premier permet de valider la représentation indépendamment du renderer GPU.

---

## Phase 6 - Runtime compact

Construire:

```text
Scene
 |
Chunk manager
 |
Residency manager
 |
GPU cache
 |
LOD
 |
streaming
```

Objectif:

> une scène dont la taille totale dépasse la mémoire active du renderer peut quand même être explorée sans stall visible.

---

## Phase 7 - QoS / thermals

Tests longs:

- 5 min;
- 15 min;
- 30 min;
- 60 min.

Mesurer:

- thermal throttling;
- fréquence GPU;
- puissance;
- FPS;
- frame-time percentile;
- mémoire;
- stabilité.

Une optimisation qui donne +20 % de FPS pendant 30 secondes puis provoque du throttling n'est pas une optimisation utile.

---

# 18. Benchmarks à construire

Il faut avoir un benchmark reproductible.

### Axe scène

```text
100k
250k
500k
1M
2M
5M
10M+
```

### Axe résolution

```text
0.5x
0.67x
0.75x
1.0x
```

### Axe refresh

```text
72 Hz
80 Hz
90 Hz
120 Hz
```

### Axe LOD

```text
off
low
medium
high
adaptive
```

### Axe renderer

```text
CPU sort
GPU radix
tile sort
OIT/approximation
```

### Axe decode

```text
CPU FP32
CPU FP16
GPU FP32
GPU FP16
cached
uncached
```

---

# 19. Métriques de qualité visuelle

Il ne faut pas optimiser uniquement le runtime.

Mesurer aussi:

- PSNR;
- SSIM;
- LPIPS;
- erreur perceptuelle;
- artefacts de transparence;
- popping LOD;
- temporal instability;
- view-dependent effect fidelity.

Pour Smol-GS en particulier, il faut comparer:

```text
Original 3DGS
      vs
Smol-GS offline reference
      vs
Quest runtime
```

Le Quest renderer ne doit pas être accusé d'une perte de qualité qui provient en réalité de la compression.

---

# 20. Comparaisons importantes à faire

L'agent de recherche devrait examiner au minimum:

### Smol-GS

Pour la représentation compacte.

### Mobile-GS

Pour les stratégies spécifiques aux appareils mobiles, notamment l'évitement du sorting et la compression. [SOURCE](https://arxiv.org/abs/2603.11531)

### Voyager

Pour les stratégies de streaming et de rendu de scènes 3DGS à très grande échelle sur appareils mobiles. Le travail exploite notamment le fait que le nombre de nouveaux Gaussians visibles par seconde peut rester relativement limité sous mouvement normal et propose un streaming sélectif. [SOURCE](https://arxiv.org/abs/2506.02774)

### SqueezeMe

Pour les contraintes Quest 3, le coût des décodeurs et le renderer Vulkan mobile. [SOURCE](https://arxiv.org/abs/2412.15171)

### Vulkan Gaussian Splatting

Pour les détails d'implémentation du pipeline de rendu. [SOURCE](https://docs.vulkan.org/samples/latest/samples/complex/render_octomap/Tutorials/gaussian-splats-rendering.html)

### Meta Spatial SDK Splat

Comme baseline officielle Quest.

Meta supporte actuellement les splats dans Spatial SDK sur Quest 3/3S, avec PLY et SPZ, mais recommande d'éviter les scènes de plus de 150k splats pour les performances. L'API est actuellement expérimentale. [SOURCE](https://developers.meta.com/horizon/documentation/spatial-sdk/spatial-sdk-splats/)

Cette limite de 150k ne doit pas être interprétée comme une limite matérielle fondamentale du Quest 3. C'est une recommandation pour cette implémentation/API. Des travaux et moteurs indépendants ciblent des budgets beaucoup plus élevés. [SOURCE](https://walhargohar.com/WallGS/documentation/wallgs/)

---

# 21. Risques principaux

## Risque 1: MLP trop cher

Le gain de compression pourrait être payé par trop de calcul.

**Mitigation:** benchmarker immédiatement le decode.

---

## Risque 2: sorting trop cher

Le renderer classique peut devenir limité par le depth sorting.

**Mitigation:** comparer GPU radix, tile sorting et approches approximatives.

---

## Risque 3: overdraw

Les Gaussian splats peuvent générer beaucoup de fragments.

**Mitigation:**

- culling;
- size culling;
- opacity culling;
- tile-aware rendering;
- LOD;
- éventuellement techniques de réduction d'overdraw.

---

## Risque 4: mémoire

Même une représentation compressée peut exploser après décodage.

**Mitigation:** cache par chunks et format GPU compact.

---

## Risque 5: streaming stalls

Un chunk manquant peut provoquer une attente visible.

**Mitigation:** prefetch basé sur caméra + vélocité + priorité.

---

## Risque 6: thermal throttling

Le benchmark court peut être trompeur.

**Mitigation:** benchmarks longs et suivi thermique.

---

## Risque 7: qualité VR

Une scène acceptable sur écran peut produire des artefacts particulièrement visibles en stéréo.

**Mitigation:** évaluation stéréo réelle sur casque.

---

# 22. Architecture logicielle Rust possible

Proposition de workspace:

```text
smolxr/
├── crates/
│   ├── smol-format/
│   │   └── parsing + compression
│   │
│   ├── smol-scene/
│   │   └── scene graph / octree / chunks
│   │
│   ├── smol-runtime/
│   │   └── scheduling / cache / streaming
│   │
│   ├── smol-renderer/
│   │   └── Vulkan renderer
│   │
│   ├── smol-shaders/
│   │   └── GLSL/HLSL/SPIR-V
│   │
│   ├── smol-xr/
│   │   └── OpenXR / Quest integration
│   │
│   └── smol-bench/
│       └── benchmarking / telemetry
│
├── assets/
├── shaders/
├── benches/
└── docs/
```

---

# 23. API runtime envisagée

Quelque chose de volontairement simple:

```rust
let runtime = Runtime::new(config)?;

let scene = runtime.load_scene("scene.smolgs").await?;

runtime.attach_scene(scene);

loop {
    let frame = runtime.begin_frame(xr_frame)?;

    runtime.update_camera(frame.camera());

    runtime.render(frame)?;

    runtime.end_frame(frame)?;
}
```

Le runtime devrait cacher:

- streaming;
- residency;
- GPU synchronization;
- LOD;
- culling;
- decode;
- rendering.

---

# 24. Principes d'architecture à conserver

### 1. GPU-first

Si une opération est exécutée par millions d'éléments, elle doit être suspecte si elle est sur CPU.

### 2. No full decompression

Ne jamais supposer que toute la scène doit être décodée.

### 3. Chunk everything

La scène doit être partitionnable.

### 4. Stable frame time > peak FPS

Le QoS prime sur le benchmark marketing.

### 5. Profile on device

Les performances PC ne sont pas représentatives du Quest.

Meta recommande explicitement le profiling directement sur Quest, notamment avec son fork RenderDoc et les outils GPU associés. [SOURCE](https://developers.meta.com/horizon/blog/start-developing-Meta-Quest-3-tips-performance-mixed-reality/)

### 6. Separate representation from renderer

Le format Smol-GS ne doit pas devenir une contrainte absolue du renderer.

### 7. Keep a dumb baseline

Un renderer 3DGS classique simple est indispensable pour mesurer les gains réels.

---

# 25. Questions que l'agent de recherche doit résoudre

Priorité haute:

1. Quel est exactement le format de fichier/checkpoint produit par Smol-GS?
2. Le code officiel permet-il une réimplémentation du decoder sans PyTorch?
3. Quelles sont les dimensions exactes des features pour tiny/small/base?
4. Quelle est la structure exacte des MLP?
5. Peut-on convertir leurs poids vers un format GPU FP16?
6. Quel est le coût du decode par splat?
7. Peut-on fusionner plusieurs opérations du MLP?
8. Peut-on décoder directement en covariance/opacity/color sans matérialiser des features intermédiaires?
9. Comment fonctionne exactement leur occupancy octree?
10. Peut-il servir directement de structure de LOD?
11. Quelle est la taille réelle des scènes Smol-GS sur les datasets?
12. Quel renderer officiel est utilisé pour les benchmarks?
13. Quelles parties du pipeline restent coûteuses malgré la compression?

Priorité Quest/Vulkan:

14. Quelles extensions Vulkan sont disponibles sur Quest 3?
15. FP16 compute?
16. subgroup operations?
17. indirect draw/dispatch?
18. timeline semaphores?
19. descriptor indexing?
20. multiview?
21. limites de storage buffers?
22. possibilités de async compute?
23. comportement exact du driver Adreno avec les workloads proposés?

Priorité rendering:

24. GPU radix sort réaliste à 1M/5M splats?
25. Tile-based sorting?
26. OIT approximatif?
27. Quelle approche minimise le frame-time variance?
28. Quel niveau d'overdraw devient problématique?
29. Peut-on partager une grande partie du travail entre les deux yeux?

Priorité runtime:

30. Quelle stratégie de chunking?
31. Quelle taille de chunk?
32. Quel cache GPU?
33. Comment anticiper la caméra?
34. Quelle politique d'éviction?
35. Comment éviter les stalls lors des uploads?

---

# 26. Critères de réussite proposés

## Milestone A

**Quest 3 + Rust + Vulkan**

Une scène 3DGS simple tourne en standalone avec tracking caméra correct.

## Milestone B

**500k à 1M splats**

72 Hz stable sur une scène benchmark maîtrisée.

## Milestone C

**Smol-GS decode**

Une scène Smol-GS peut être chargée et rendue sans dépendance Python/PyTorch au runtime.

## Milestone D

**GPU-driven**

Culling + LOD + sorting + rendering principalement GPU.

## Milestone E

**Large scene**

Scène de plusieurs millions de splats avec seulement une fraction résidente/décodée.

## Milestone F

**Long-run QoS**

30 à 60 minutes de navigation sans frame-time degradation catastrophique ni thermal collapse.

---

# 27. Ce que nous ne devons PAS faire au début

Ne pas commencer par:

- UI;
- app store;
- interaction avancée;
- passthrough;
- hand tracking;
- scène dynamique;
- réseau;
- cloud;
- streaming distant;
- support Quest 2;
- support de multiples formats.

Le premier problème à résoudre est beaucoup plus simple:

> **Combien de Gaussian Splats pouvons-nous rendre correctement et de façon stable sur Quest 3 avec notre propre pipeline Vulkan?**

Puis:

> **Quel est le coût réel du decode Smol-GS?**

Puis:

> **Est-ce que la compression nous permet d'augmenter la taille des scènes sans détruire le frame budget?**

---

# 28. Direction finale envisagée

Le projet pourrait évoluer vers:

```text
                  Smol-GS Asset
                       |
                       v
              +----------------+
              | Rust XR Runtime|
              +----------------+
                       |
          +------------+------------+
          |            |            |
       Storage       Spatial       GPU
       Manager       Manager       Runtime
          |            |            |
       chunks         LOD       culling
          |            |         decode
          |            |         sorting
          |            |         render
          +------------+------------+
                       |
                       v
                  Quest 3
```

La proposition de valeur serait alors:

> **Un runtime standalone capable de rendre des scènes 3DGS compactes et potentiellement très grandes directement sur un casque XR, avec un pipeline GPU/Vulkan conçu pour maintenir une QoS VR stable.**

Le point différenciant ne serait pas simplement « faire du 3DGS sur Quest ». Meta supporte déjà les Gaussian Splats nativement dans Spatial SDK, et des moteurs tiers font également du rendu standalone. [SOURCE: Meta Spatial SDK](https://developers.meta.com/horizon/documentation/spatial-sdk/spatial-sdk-splats/) [SOURCE: WallGS](https://walhargohar.com/WallGS/documentation/wallgs/)

Le différenciateur serait plutôt la combinaison:

```text
compact representation
        +
hierarchical scene
        +
on-device decoding
        +
GPU-driven rendering
        +
out-of-core streaming
        +
VR QoS
        +
Rust/Vulkan
```

---

# 29. Conclusion de cadrage

**Hypothèse de travail:** le projet est techniquement crédible, mais sa faisabilité à grande échelle doit être démontrée expérimentalement.

Le plus gros risque n'est pas la capacité du Quest 3 à afficher des Gaussian Splats. Il existe déjà plusieurs démonstrations et runtimes montrant que c'est possible.

Les vraies inconnues sont:

1. **coût du décodage Smol-GS sur Adreno;**
2. **coût du sorting;**
3. **coût du blending/overdraw;**
4. **coût mémoire après décodage;**
5. **efficacité réelle du streaming par chunks;**
6. **stabilité thermique à long terme;**
7. **qualité stéréo à forte compression/LOD.**

La bonne stratégie est donc expérimentale:

```text
baseline
   ↓
measure
   ↓
identify bottleneck
   ↓
optimize
   ↓
measure again
```

et non:

```text
design enormous engine
   ↓
implement everything
   ↓
discover after 6 months that sorting costs 80%
```

Le premier livrable sérieux devrait donc être un **benchmark renderer Rust/Vulkan standalone Quest 3**, suivi d'une implémentation minimale du decoder Smol-GS. Une fois ces deux pièces mesurées indépendamment, il sera possible de décider rationnellement si le chemin vers un runtime compact complet mérite d'être poursuivi.
