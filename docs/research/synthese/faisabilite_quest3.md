# Faisabilité 3DGS temps réel sur Meta Quest 3 — faits pratiques (recherche du 29/09/2026)

Convention : tout ce qui n'est pas marqué a été lu dans la source citée. « (inféré) » = raisonnement personnel, pas une affirmation de la source. « (source secondaire) » = agrégateur ou blog, pas la source primaire.

---

## 1. Matériel Quest 3 / Quest 3S

| | Quest 3 | Quest 3S |
|---|---|---|
| SoC | Qualcomm Snapdragon XR2 Gen 2, « basé sur le Snapdragon 8 Gen 2 » | **Même SoC** XR2 Gen 2 |
| GPU | Adreno 740 (max 640 MHz selon Wikipédia) | Adreno 740 @ 640 MHz |
| CPU | 2 cœurs perf. (Cortex‑A715) + 4 cœurs efficacité (A510), 2,36 GHz | idem |
| RAM | 8 Go LPDDR5, 68 Go/s (Wikipédia) | 8 Go (LPDDR4X selon Wikipédia) |
| Écran par œil | 2064×2208, LCD, lentilles pancake | 1832×1920, LCD, lentilles Fresnel |
| Résolution de rendu par défaut (render scale 1.0) | **1680×1760 px/œil** | 1680×1760 px/œil |
| Fréquences | 72 (défaut), 80, 90, 100, 120 Hz ; étendu jusqu'à 207 Hz (240 Hz en mode dev) | 72, 80, 90, 100, 120 Hz |

Sources : [Wikipédia Quest 3](https://en.wikipedia.org/wiki/Meta_Quest_3), [Wikipédia Quest 3S](https://en.wikipedia.org/wiki/Meta_Quest_3S), [Meta — Render Scale](https://developers.meta.com/horizon/documentation/unity/os-render-scale/), [Meta — Display refresh rates](https://developers.meta.com/horizon/documentation/unreal/unreal-change-display-refresh-rate/), [UploadVR — XR2 Gen 2](https://www.uploadvr.com/snapdragon-xr2-gen-2/) (« up to 2.5x peak GPU performance », 2 cœurs perf. + 4 efficacité).

**Niveaux d'horloge (doc Meta, Quest 3/3S)** — [CPU and GPU levels](https://developers.meta.com/horizon/documentation/unity/os-cpu-gpu-levels/) :
- GPU : niveau 0 = 285 MHz, 1 = 350, 2 = 456, 3 = 492, 4 = 545, **5 = 599 MHz**. Les niveaux 3–4 ne sont disponibles que si l'app n'active pas le passthrough ; le niveau 5 exige le « CPU/GPU level trading » ou la **résolution dynamique**.
- CPU : de 0,69 GHz (niv. 0) à 2,36 GHz (niv. 8).
- « Performance settings are hints, not requests for fixed clock frequencies » (throttling thermique possible).
- UploadVR (31/10/2024) : un firmware a relevé le max GPU de 545→599 MHz (défaut) et 599→**640 MHz** en mode « Favor GPU », réservé aux apps avec résolution dynamique ; le Quest 3S en bénéficie aussi (même puce) — [UploadVR](https://www.uploadvr.com/meta-quest-3-gpu-clock-speed-performance-boost/).

**Prix France (hausse Meta du 19/04/2026, cause : prix de la mémoire)** — [hivr.fr](https://hivr.fr/meta-augmente-le-prix-du-quest-3-et-quest-3s-des-le-19-avril-la-france-concernee-il-te-reste-24h/) :
- Quest 3 512 Go : 549,99 € → **619,99 €**
- Quest 3S 128 Go : 329,99 € → **359,99 €** ; 3S 256 Go : 439,99 € → 469,99 €
- Reconditionné : un Quest 3 observé à ~459 € sur Back Market (source secondaire, résumé de recherche ; prix variable) — [Back Market](https://www.backmarket.fr/fr-fr/p/casque-vr-realite-virtuelle-meta-quest-3/01a020f4-e1d6-4dec-967a-12cc0dc3c7b2).

**Téléphone « proxy » avec le même GPU** :
- Le Snapdragon 8 Gen 2 embarque l'Adreno 740 à **680 MHz** (version standard) et **719 MHz** dans la variante « for Galaxy » des Galaxy S23/S23+/S23 Ultra (source secondaire : résumé de recherche GSMArena/Gizmochina — [GSMArena](https://www.gsmarena.com/samsung_galaxy_s23_ultra_benchmarks__snapdragon_8_gen_2_for_galaxy_examined-news-57447.php)).
- Un utilisateur confirme dans le dépôt aras-p : « The Snapdragon 8 Gen 2 has the same GPU as the Quest 3 » et que le renderer fonctionne sur son Quest 3 — [issue #187](https://github.com/aras-p/UnityGaussianSplatting/issues/187) (@AdrianTheFrog, 17/07/2025).
- Galaxy S23 reconditionné : à partir d'environ 261 $ (août 2026, Back Market US, source secondaire) — [Back Market price guide](https://www.backmarket.com/en-us/price-guide/galaxy-s23).
- Différences à corriger (inféré) : horloge GPU Quest 599–640 MHz vs 680–719 MHz sur téléphone (ratio ≈ 0,83–0,94) ; enveloppe thermique différente ; surtout **charge pixel** : Quest stéréo par défaut = 2×1680×1760 ≈ 5,9 Mpx/frame contre ≈ 2,5 Mpx pour un écran 1080×2340, soit ≈ 2,3× plus de pixels, à 72 Hz au lieu de 60.

---

## 2. État de l'art des renderers 3DGS sur Quest 3 natif (2025–2026)

### aras-p/UnityGaussianSplatting
- README : fonctionne sous D3D12, Metal ou Vulkan ; « DX11 will not work » ; « Some virtual reality devices work (reportedly HTC Vive, Varjo Aero, Quest 3 and Quest Pro) » ; « not tested at all on mobile/web, and probably does not work there » ; « some Androids do not work either ». Perf de référence : bicycle 6,1 M splats, 1200×797 → RTX 3080 Ti 6,8 ms (147 FPS : 4,5 ms raster, 1,1 ms tri) ; M1 Max 21,5 ms ; **48 octets de VRAM par splat** pour tri/cache ; Unity 2022.3 — [README](https://github.com/aras-p/UnityGaussianSplatting).
- **Support VR = contribution communautaire, pas officiel** : v1.0.0 (28/11/2024) « Virtual Reality support is in! » via le PR [#146](https://github.com/aras-p/UnityGaussianSplatting/issues/146) (ninjamode) qui met à jour DeviceRadixSort « that has better GPU support (needed for Quest 3) » ; mode Multi‑Pass, URP, OpenXR ; conseil : « keep the Gaussian count low on mobile devices, try not to be super close (fillrate issue?), don't sort every frame ». aras‑p lui‑même (28/10/2025) : « I myself have zero VR devices around, and code here may or might not work in VR » — [issue #205](https://github.com/aras-p/UnityGaussianSplatting/issues/205).
- v1.1.0 (30/01/2025) : l'URP utilise le render graph d'**Unity 6** (Unity 6+ requis pour l'URP) — [Releases](https://github.com/aras-p/UnityGaussianSplatting/releases).
- Problèmes connus Android/Adreno : [#112](https://github.com/aras-p/UnityGaussianSplatting/issues/112) (ouvert depuis 04/2024) — tri corrompu sur Quest 3 et Lenovo A3 (« So the sort is the problem ») ; [#26](https://github.com/aras-p/UnityGaussianSplatting/issues/26) — ne compile pas en OpenGL ES (il faut Vulkan) ; [#201](https://github.com/aras-p/UnityGaussianSplatting/issues/201) — mode Multiview/Single‑pass instancié ne marche pas (Multi‑pass OK mais « big performance impact »).
- Code : le tri GPU impose `#pragma require wavebasic`, `#pragma require waveballot`, `#pragma use_dxc` (« GPU sorting needs wave ops ») et gère explicitement les tailles de wave < 16 et ≥ 16, avec un contournement Vulkan pour obtenir la taille de wave (`WaveActiveBallot`) — fichiers `package/Shaders/SplatUtilities.compute`, `SortCommon.hlsl`, `DeviceRadixSort.hlsl` du dépôt.
- Chiffres Quest 3 remontés en issues :
  - [#145](https://github.com/aras-p/UnityGaussianSplatting/issues/145) : en VR, chute de 72 fps à ~10 fps quand on s'approche. aras‑p : le coût est surtout le « number of pixels to process » (résolution × taille des splats à l'écran), pas le nombre de splats ; test : si baisser la résolution accélère, le nombre de splats n'est pas le goulot. Un utilisateur (12/2025) : scène de **300k splats à render scale 0,9 dans un APK = inutilisable**.
  - [#225](https://github.com/aras-p/UnityGaussianSplatting/issues/225) (PR ouvert, 03/2026) : stéréo Multiview Quest 3, covariance/SH calculés une fois pour les deux yeux (« Saves ~40% of compute shader ALU »), tri une seule fois (œil central), `clip()` au lieu de `discard` pour le TBDR Adreno. Commentaire de l'auteur (18/03/2026) : sa branche rend « as high as **300k at 16‑18FPS** in quest 3 » avec culling opacité/échelle/frustum, rendu en résolution réduite + upscale bilinéaire, RT de plus faible précision (chiffre tel qu'écrit ; ambigu, peut‑être « ms »).
  - [#207](https://github.com/aras-p/UnityGaussianSplatting/issues/207) : 1–5 FPS sur Quest 2 standalone.

### Fork ninjamode (base du support VR d'aras‑p)
« **Quest 3 gets 72 fps stable until around 400k Gaussians with proper settings** » ; le README précise que le support VR a été intégré en amont chez aras‑p — [ninjamode/Unity-VR-Gaussian-Splatting](https://github.com/ninjamode/Unity-VR-Gaussian-Splatting).

### Kleinbeck et al. 2024 (arXiv 2410.16978)
Dépôt [roth-hex-lab/Multi-Layer-Anatomy-GS-Unity-Rendering](https://github.com/roth-hex-lab/Multi-Layer-Anatomy-GS-Unity-Rendering) : Unity 2022.3, DX12/Vulkan, le README reprend l'avertissement « not tested at all on mobile/web ». Article ([HTML](https://arxiv.org/html/2410.16978)) : Quest 3 standalone, scène « Leg » à résolution native. **Correction d'après notre fiche** ([kleinbeck2024](../sources/kleinbeck2024_multilayer-gs-anatomy/fiche.md), Tab. 4, `page:7/block:4`) : 10,2 / 17,6 / 16,3 / 26,6 ms selon les options Sort et HQ (la lecture « compression faible 16,3 / forte 6,0 ms » du rapport initial était erronée). Modèles de 57k–196k Gaussiennes ; le tri pour l'œil central seulement fait gagner ≈ 40 % sur Quest 3.

### Autres chiffres Quest 3 natifs
- **Meta Spatial SDK (API Splat expérimentale, doc du 10/11/2025)** : « For performance, avoid using Gaussian splats with a splat count greater than **150k** », format .spz recommandé, un seul splat affiché à la fois, Quest 3/3S uniquement — [Meta — Use Gaussian splats](https://developers.meta.com/horizon/documentation/spatial-sdk/spatial-sdk-splats/).
- **SqueezeMe (Meta, arXiv 2412.15171)** : 3 avatars de ~60k Gaussiennes chacun (≈180k) à **72 FPS** sur Quest 3, pipeline Vulkan maison (compute pour projection/couleur, puis rasterisation matérielle de quads) — [arXiv](https://arxiv.org/html/2412.15171v1).
- **Gracia** : rendu on‑device ; CEO (23/02/2026) : « We can render up to **half a million splats per frame** on a standalone headset, starting from Quest 3, at around **72 FPS** » — [interview](https://aipressroom.com/georgii-vysotskii-gracia/). Test Mixed : résolution des scènes « quite low », « Quest 3 apparently is already at its limit », les splats utilisateurs doivent être optimisés — [Mixed](https://mixed-news.com/en/gracia-quest-3-hands-on/).
- **ATHENA / AAU (VCIP 2026, Ghanbari, Amirpour, Timmerer)** : étude de 180 conditions sur Quest 3 (render scale 0,5–1,0, densité 10–100 %, distances 0,7–1,5 m, cible 72 Hz), mesures via OVR Metrics Tool : « Resolution scale is the dominant GPU cost driver » ; réduire la densité de splats n'aide que quand le temps GPU approche le budget ; les faibles render scales consomment plus de puissance (cadence plus élevée). Nombres absolus de Gaussiennes non fournis dans la page — [ATHENA](https://athena.itec.aau.at/2026/09/3d-gaussian-splatting-rendering-performance-trade-offs-on-the-meta-quest-3/).
- **VRSplat (arXiv 2505.10144)** : Quest 3 **tethered** à une RTX 4090 (pas natif) ; 7,88–14,11 ms ; modèles compactés, ex. Truck 2,56 M → 0,21 M, Bonsai 1,25 M → 0,36 M — [arXiv](https://arxiv.org/html/2505.10144v1).
- **GaussianSplatViewer (zachdrouin)** : Unity 6/URP/Vulkan, « 400,000 visible (configurable) », « Keep PLY files under 1M Gaussians » — ce sont des cibles de conception, pas des mesures publiées — [GitHub](https://github.com/zachdrouin/GaussianSplatViewer).
- **World Labs « Splat World »** : Unity natif, Quest 3 standalone et tethered, grilles 10×10 m, « GPU profiling kept splat counts within limits » — aucun chiffre — [World Labs](https://www.worldlabs.ai/case-studies/1-splat-world).
- Forum Unity : « latest versions do work in Quest2/3 also, but pretty slow » (09/01/2025) — [Unity Discussions](https://discussions.unity.com/t/3d-gaussian-splats-on-quest-3/1542816).
- Mobile‑GS (Du 2026, 74 fps mono sur Snapdragon 8 Gen 3) : fourni dans le brief, non re‑vérifié ici.
- Point de repère téléphone : WebSplatter (arXiv 2602.03207), scène bicycle compressée **1,06 M splats** : 33,6 ms sur Snapdragon 8 Gen 3 (Chrome), 38,5 ms iPhone 15 Pro Max, 105,2 ms Snapdragon 865 (mono, résolution téléphone) — [arXiv](https://arxiv.org/html/2602.03207v1).

### Meta Horizon Hyperscape
- Lancement (17/09/2025) : capture sur Quest 3/3S, traitement 1–8 h sur serveurs Meta ; rendu **streamé depuis le cloud** (« Avalanche ») ; « None of the hardest computational work … happens on-device, and you don't get access to the raw file » — [UploadVR](https://www.uploadvr.com/meta-horizon-hyperscape-photorealistic-scene-capture-quest-3/).
- Depuis la mise à jour du 20/11/2025 : « Hyperscape worlds are **rendered on-device in VR**, via the Horizon Engine » (cloud conservé pour les smartphones), traitement toujours serveur — [UploadVR](https://www.uploadvr.com/horizon-hyperscape-worlds-invite-friends-visit-meta-avatars/). Aucun nombre de splats publié.

### Scaniverse / Niantic
« Into the Scaniverse » : app Quest 3/3S (pas les Quest plus anciens), développée dans Niantic Studio (WebXR), rendu on‑device — [Niantic Labs](https://nianticlabs.com/news/the-scaniverse-expands), [scaniverse.com/quest](https://scaniverse.com/quest). Aucun chiffre de perf.

### Viewers WebXR (Quest Browser)
- **Spark (sparkjs)** — budgets recommandés : « **Quest 3: 1 million splats or less**, not too many splats concentrated in a small area » ; Android 1–2 M ; `maxStdDev = sqrt(5)` conseillé en VR ; désactiver l'antialiasing — [Spark perf](https://sparkjs.dev/docs/performance/). Avec le LoD de Spark 2.0 : `lodSplatCount` par défaut 1,5 M desktop / **500K mobile** — [Spark LoD](https://sparkjs.dev/docs/new-spark-renderer/).
- **PlayCanvas / SuperSplat 2.0** : VR testée sur Quest 2 et 3 et Vision Pro, pas de chiffres — [blog](https://blog.playcanvas.com/publish-your-gaussian-splats-with-supersplat/) ; streaming LOD par morceaux SOG — [tutoriel](https://developer.playcanvas.com/tutorials/gaussian-splat-streaming-lod/).
- GaussianSplats3D issue #65 : un renderer WebXR interne (gmix) à « 90FPS on Quest 3 » sur des splats fortement réduits (29/11/2023), taille non précisée — [issue](https://github.com/mkkellogg/GaussianSplats3D/issues/65).

### Unreal
- XVERSE XScene‑UEPlugin : UE5 + Niagara — [GitHub](https://github.com/xverse-engine/XScene-UEPlugin). Aucun support Quest standalone documenté trouvé.
- Plugin Unreal de Luma : présenté comme abandonné (source secondaire, résumé de recherche) ; la page « interactive scenes » de Luma redirige aujourd'hui vers ses produits génératifs (inféré : capture 3DGS plus mise en avant).

---

## 3. Budget pratique de Gaussiennes sur Quest 3 natif à 72 Hz

| Source | Budget | Nature |
|---|---|---|
| Meta Spatial SDK | ≤ **150k** | recommandation officielle |
| SqueezeMe (Meta) | ~180k (3×60k) à 72 FPS | mesuré, pipeline Vulkan dédié |
| Kleinbeck 2024 | ~57–196k : 10,2–26,6 ms selon tri et HQ | mesuré, Unity/aras‑p |
| ninjamode | ~**400k** à 72 fps « with proper settings » | déclaration README |
| Gracia | ≤ **500k** par frame à ~72 FPS | déclaration commerciale |
| Spark (WebXR) | ≤ **1 M** au total ; 500k rendus par défaut en LoD mobile | recommandation doc |
| Issues aras‑p | 300k : inutilisable à 0,9 de render scale ; 16–18 « FPS » avec optimisations | retours dév. |

Point commun : le coût dominant est le **fill‑rate** (pixels × taille des splats à l'écran × overdraw), confirmé par aras‑p (#145) et par l'étude ATHENA ; le nombre de splats compte surtout via le tri et le pré‑traitement.

**Règle empirique (inféré)** : ~150–300k Gaussiennes visibles par frame pour un renderer Unity générique ; ~400–500k avec un pipeline spécialisé ; au‑delà seulement avec LoD/streaming (le total de la scène peut être plus grand, pas le nombre rendu).

---

## 4. Outils de mesure

**Avec casque (Quest) :**
- **OVR Metrics Tool** : overlay HUD + « Report Mode » exportable en CSV (fréquence, chaleur, throttling CPU/GPU, frames périmées, app GPU time, utilisation, puissance, mémoire) ; stats GPU avancées (stalls, miss L1/L2) via `ovrgpuprofiler` — [doc](https://developers.meta.com/horizon/documentation/unity/ts-ovrmetricstool/), [ovrgpuprofiler](https://developers.meta.com/horizon/documentation/unity/ts-ovrgpuprofiler/). C'est l'outil utilisé par l'étude ATHENA.
- **Perfetto via Meta Quest Developer Hub** : GPU Render Stage Trace, métriques GPU, métriques runtime XR ; GPU Systrace déprécié depuis le 02/12/2024 — [doc](https://developers.meta.com/horizon/documentation/unity/ts-perfettoguide/).
- **RenderDoc Meta Fork** : trace des render stages par tuile (XR2 Gen 2 de Quest 3/3S compris), jusqu'à 48 métriques par draw call, stats de shaders via `KHR_pipeline_executable_properties` — [doc](https://developers.meta.com/horizon/documentation/unity/ts-renderdoc-for-oculus/).

**Sans casque :**
- **Meta XR Simulator** : « a lightweight OpenXR runtime that runs on your computer… ships no operating system image and no Android layer, so it does not emulate device hardware » → **aucune valeur pour la perf** (inféré de cette phrase ; la doc ne l'interdit pas explicitement) — [doc](https://developers.meta.com/horizon/documentation/unity/xrsim-intro/).
- **Android GPU Inspector** : la liste officielle ne cite que Pixel 4/6/7, Galaxy S21, OnePlus 9R, OPPO Find X3 Pro ; l'Adreno 740 n'y figure pas, mais « new devices with Android 12 … are expected to pass this validation check » — [AGI supported devices](https://developer.android.com/agi/supported-devices).
- **Snapdragon Profiler** (Qualcomm) : > 150 compteurs matériels CPU/GPU/mémoire sur appareils Snapdragon — [Qualcomm](https://developer.qualcomm.com/software/snapdragon-profiler) (source secondaire : résumé de recherche). Outil naturel pour un téléphone Snapdragon 8 Gen 2.

---

## 5. Unity + UnityGaussianSplatting sur Intel Iris Xe (i5‑1135G7)

- Prérequis déclarés par aras‑p : D3D12, Vulkan ou Metal, **pas DX11** ; aucune exigence GPU minimale chiffrée, aucune mention d'Intel dans le README — [README](https://github.com/aras-p/UnityGaussianSplatting). Unity 6 sous Windows peut mettre D3D11 par défaut ; il faut passer à Vulkan/D3D12 et redémarrer (commentaire @DebbyX3, 14/04/2025, [#146](https://github.com/aras-p/UnityGaussianSplatting/issues/146)).
- Le tri a besoin des wave intrinsics (`wavebasic`, `waveballot`, DXC). Guide Intel Xe‑LP : « Xe‑LP supports the use of wave intrinsics for both 3D and compute workloads » ; largeur de wave SIMD8/16/32 choisie par le compilateur ; jusqu'à 96 EU, ~2,2 TFLOPS pour la version complète — [Intel](https://www.intel.com/content/www/us/en/developer/articles/guide/lp-api-developer-optimization-guide.html). L'Iris Xe du i5‑1135G7 a **80 EU, 400–1300 MHz** (source secondaire : résumé de recherche CPU‑Monkey/LaptopMedia).
- Le code de tri gère les waves < 16 (chemin `WLT16`), donc SIMD8 est prévu (inféré : **devrait fonctionner** en D3D12, mais aucun rapport de test sur Iris Xe trouvé). Le PR #225 ajoute même une garde « for GPUs lacking wave intrinsics ».
- Performance (inféré) : un M1 Max met 21,5 ms sur bicycle 6,1 M ; l'Iris Xe 80 EU est plusieurs fois moins puissant et partage la RAM (~1,3 Go de VRAM pour bicycle selon le README Kleinbeck) → aperçu possible à quelques fps sur des scènes de plusieurs millions, fluide sur quelques centaines de milliers. Suffisant pour développer, pas pour mesurer la perf Quest. Quest Link en PC VR n'est pas envisageable sur un iGPU Intel (inféré, non vérifié).
- Attention aux versions : le dépôt Kleinbeck est figé sur Unity 2022.3 ; l'URP d'aras‑p ≥ v1.1.0 exige Unity 6.

---

## 6. Entraîner du 3DGS sans GPU NVIDIA

**Pas besoin d'entraîner pour le benchmark** : l'INRIA fournit des modèles pré‑entraînés (Mip‑NeRF 360, T&T, Deep Blending) :
- [Pre‑trained Models (14 GB)](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/pretrained/models.zip) — vérifié : HTTP 200, Content‑Length = 14 660 630 999 octets. Les `.ply` s'importent directement dans UnityGaussianSplatting (inféré, format standard graphdeco).
- Aussi : [T&T+DB COLMAP (650 MB)](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/input/tandt_db.zip), [Evaluation Images (7 GB)](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/evaluation/images.zip), scènes Mip‑NeRF 360 sur [jonbarron.info/mipnerf360](https://jonbarron.info/mipnerf360/) — [README graphdeco](https://github.com/graphdeco-inria/gaussian-splatting).

**Implémentations** :
- graphdeco officiel : GPU CUDA CC 7.0+, **24 GB VRAM** pour la qualité du papier ; la FAQ explique comment réduire (moins de densification, 7k itérations) ; lien vers un template Colab (camenduru, état août 2023) — [README](https://github.com/graphdeco-inria/gaussian-splatting).
- **gsplat** (nerfstudio) : `pip install gsplat` ; reproduit 3DGS avec « up to **4x less GPU memory** » et ~15 % plus rapide ; PyTorch 2.7+ requis — [gsplat](https://github.com/nerfstudio-project/gsplat). Inféré : c'est l'option la plus réaliste sur un T4 16 Go.

**GPU cloud gratuits / pas chers** :
- **Google Colab** gratuit : limites dynamiques, sessions de 12 h max, type de GPU non garanti — [FAQ Colab](https://research.google.com/colaboratory/faq.html). Pro 9,99 $/mois pour 100 unités de calcul, T4 ≈ 1,76 UC/h (source secondaire).
- **Kaggle** : ~30 h GPU/semaine, P100 ou 2×T4 (16 Go chacun), sessions jusqu'à 9 h, vérification par téléphone (source secondaire, résumé de recherche — la doc Kaggle n'a pas pu être lue).
- **Lightning.ai** : offre gratuite annoncée avec ~80 h GPU/mois (source secondaire ; la page officielle n'a pas chargé).
- **RunPod** : RTX 4090 **0,34 $/h** (community) / 0,74 $/h (secure) ; RTX 3090 0,22 $/h ; L4 0,44 $/h ; A100 80 Go 1,19 $/h — [RunPod pricing](https://www.runpod.io/pricing).
- **Vast.ai** : RTX 4090 ~0,32–0,50 $/h selon les annonces (source secondaire ; aucune offre affichée au moment de la lecture) — [Vast.ai](https://vast.ai/pricing/gpu/RTX-4090).
- Ordre de grandeur (inféré) : une scène Mip‑NeRF 360 à 30k itérations prend ~30–60 min sur une 4090, soit moins de 1 $ chez RunPod.

**Capture → splat** :
- **Scaniverse** (Niantic) : gratuit, illimité, iOS & Android, traitement **sur le téléphone** (< 90 s), export .SPZ (et PLY selon d'autres sources) — [RadianceFields](https://radiancefields.com/platforms/scaniverse), [SPZ open source](https://dev.scaniverse.com/news/spz-gaussian-splat-open-source-file-format). aras‑p ≥ v1.1.0 lit le SPZ.
- **Postshot** (Jawset) : Windows + **GPU NVIDIA CC 7.5+ obligatoire** (inutilisable sur Iris Xe) ; plan gratuit sans export PLY/SPZ (réservé aux plans payants ; Indie ≈ 17 €/mois selon une source secondaire) — [Jawset](https://www.jawset.com/), [pricing](https://www.jawset.com/shop/pricing).
- **Polycam** : export PLY des splats réservé aux plans payants (source secondaire) — [Polycam](https://poly.cam/tools/gaussian-splatting).
- **Luma** : voir §2 (capture plus mise en avant, inféré).
- **Hyperscape** : pas d'accès au fichier brut ([UploadVR](https://www.uploadvr.com/meta-horizon-hyperscape-photorealistic-scene-capture-quest-3/)), donc inutilisable pour un benchmark.

---

## 7. Emprunter / louer un Quest 3

- **CCL Live** : 60 € HT/jour, caution 550 €, assurance casse 8 % — [CCL Live](https://www.ccl-live.fr/produit/meta-quest-3/).
- **Deli VR** : à partir de 99,90 € HT, durées de 1 à 30 jours, caution bancaire non débitée — [Deli VR](https://www.delivr.fr/location-du-casque-vr-meta-quest-3-plongez-dans-une-realite-virtuelle-immersive-a-360/).
- **MILE** : « à partir de 9 €/jour » en location mensuelle dégressive, sur devis, orientée entreprises — [MILE](https://location.mile.fr/tv-son/casque-de-realite-virtuelle/casque-meta-quest3/).
- Alternatives (inféré) : fablab ou pôle XR de l'école, laboratoire partenaire, reconditionné (~459 €) revendu ensuite, ou un Quest 3S neuf à 359,99 € (**même SoC et même résolution de rendu par défaut** que le Quest 3, donc un proxy de perf GPU quasi exact ; seuls l'écran et les lentilles changent).

---

## Ce que ça implique

**1. 72 Hz stéréo avec 1–3 M Gaussiennes rendues à chaque frame, en natif sur Quest 3 : pas plausible avec les renderers publics actuels (inféré, confiance assez élevée).**
- Les meilleures valeurs publiées ou annoncées plafonnent à **~0,4–0,5 M Gaussiennes à 72 FPS** (ninjamode 400k « with proper settings », Gracia 500k avec un pipeline propriétaire). Meta recommande officiellement ≤ 150k. Les mesures académiques natives (Kleinbeck : 196k → 26,6 ms ≈ 38 fps ; SqueezeMe : 180k à 72 FPS) restent sous 0,2 M.
- Extrapolation grossière : 1–3 M, c'est 2 à 6× au‑delà du meilleur cas (500k), et 5 à 15× au‑delà du cas Kleinbeck. Côté téléphone, WebSplatter mesure déjà 33,6 ms pour 1,06 M splats en mono sur un Snapdragon 8 Gen 3 (plus puissant que l'Adreno 740), à une résolution environ 2,3× plus basse que la stéréo Quest. Le budget à 72 Hz est de 13,9 ms, et 11,1 ms à 90 Hz.
- **Formulation plausible pour le projet** : une scène de 1–3 M Gaussiennes au total, avec **≤ 0,3–0,5 M Gaussiennes rendues par frame**. On y arrive par (a) compaction ou élagage, à la manière de VRSplat/Mini‑Splatting (Truck 2,56 M → 0,21 M) ; (b) LoD/streaming (Spark : 500k rendus par défaut sur mobile ; SOG streamé chez PlayCanvas) ; (c) travail stéréo partagé (tri et SH une seule fois : −40 % d'ALU selon PR #225, gain de tri chez Kleinbeck) ; (d) baisse du render scale, rendu fovéal ou résolution dynamique, qui sont les principaux leviers d'après ATHENA et aras‑p ; (e) tri toutes les N frames. Un résultat à 72 Hz sur des scènes Mip‑NeRF 360 compactées vers ~0,3–0,5 M est un objectif ambitieux mais défendable. 90 Hz demande environ 20 % de marge en plus.

**2. Meilleure stratégie de proxy sans casque (inféré).**
1. **Développement sur le laptop Iris Xe** : Unity + aras‑p en D3D12 (pas DX11), avec les modèles INRIA pré‑entraînés (14 Go). Ne pas s'appuyer sur ces chiffres pour la perf : Iris Xe ≠ Adreno et le Meta XR Simulator n'émule pas le matériel. En revanche, le laptop sert à calculer des **métriques indépendantes du matériel** : nombre de Gaussiennes visibles après culling, couverture en pixels, overdraw moyen et maximal par pixel, coût du tri. Toutes calculées à la résolution Quest (2×1680×1760) et sur des trajectoires de tête réalistes.
2. **Proxy matériel** : un téléphone Snapdragon 8 Gen 2 (Galaxy S23 reconditionné, ~260 $), même Adreno 740. Build Android/Vulkan du même projet, rendu hors écran en 2×1680×1760 (ou deux passes de 1680×1760), temps GPU mesurés avec Snapdragon Profiler / AGI. Correction : horloge ×(599–640)/(680–719) ≈ 0,83–0,94, plus une marge thermique. Réutiliser au passage le correctif de tri Adreno (#146, #112).
3. **Calibration** : les chiffres publiés servent de points d'ancrage (Kleinbeck ms/Gaussiennes, SqueezeMe, ATHENA, Meta 150k). Le proxy téléphone doit reproduire l'ordre de grandeur de Kleinbeck avant d'être utilisé pour extrapoler.
4. **Validation finale** : une journée ou un week‑end de location (60–100 € HT, ou Quest 3S neuf à 360 € revendable), avec OVR Metrics Tool en mode CSV et Perfetto/RenderDoc Meta Fork. Tout préparer à l'avance : APK prêt, scènes à 150k, 300k, 500k et 1 M, render scales 0,7/0,85/1,0, sessions de 5 min à 72 et 90 Hz.
