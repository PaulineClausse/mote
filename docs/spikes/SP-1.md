# SP-1 : relecture de la documentation Meta et du code MRUK

Date de lecture : 2026-10-05. Tâche : TASK-ab76. Périmètre : SPEC.md 4.3, 14.1, Q-11, Q-13.

## 0. Sources lues et méthode

**Code MRUK** (package `com.meta.xr.mrutilitykit`), aucune copie locale trouvée (pas de `PackageCache` ni de dossier du package sous `C:/Users/seanl`). Archives téléchargées depuis `https://npm.developer.oculus.com/com.meta.xr.mrutilitykit/-/...tgz` dans un dossier temporaire hors dépôt :

| Version | Pourquoi |
|---|---|
| **207.0.0** (dernier `dist-tags.latest`) | version courante du registre |
| **83.0.4** | version de la page de référence citée par SPEC 4.3 (`reference/mruk/v83`) |

Chemins cités ci-dessous relatifs à `package/` de chaque archive. `PCA.cs` = `Core/Scripts/PassthroughCameraAccess.cs`, `Native.cs` = `Core/Scripts/Generated/MRUKNativeFuncs.cs`.

Pour la fonction publique `OVRPlugin.GetNodePoseStateAtTime` (Q-13), lue dans `com.meta.xr.sdk.core` **83.0.4**, `Scripts/OVRPlugin.cs`. L'archive (106 Mo) a été coupée au téléchargement (`unexpected end of file`) mais `OVRPlugin.cs` (16 040 lignes) a été extrait en entier ; les lignes citées existent.

**Limite structurelle** : le code natif (`Plugins/arm64-v8a/libmrutilitykitshared.so`, `Plugins/Win64/mrutilitykitshared.dll`, présents dans 83.0.4) n'est livré que compilé. Tout ce qui se passe derrière `MRUKNativeFuncs.*` n'est pas lisible.

**Pages Meta** : les 8 pages de SPEC 4.3 ont été récupérées en HTML brut (`curl`, HTTP 200) puis réduites en texte, sans outil de résumé. Dates d'« Updated » affichées : p1 21 avr. 2026, p2 9 déc. 2025, p4 21 avr. 2026, p5 24 avr. 2025, p7 29 avr. 2026 ; p3, p6, p8 sans date.

| Réf. | URL (sous `https://developers.meta.com/horizon/`) |
|---|---|
| p1 | `documentation/spatial-sdk/spatial-sdk-pca-overview/` |
| p2 | `documentation/unity/unity-pca-documentation/` |
| p3 | `reference/mruk/v83/class_meta_x_r_passthrough_camera_access/` |
| p4 | `documentation/unity/unity-pca-migration-from-webcamtexture/` |
| p5 | `documentation/native/android/pca-native-documentation/` |
| p6 | `documentation/native/android/mobile-depth/` (titre : « OpenXR Depth API Overview ») |
| p7 | `documentation/unity/unity-depthapi-overview/` |
| p8 | `documentation/unity/unity-depthapi-xr-oculus/` |

## 1. Q-11 : horloge du `Timestamp` MRUK et instant dans l'exposition

### Réponse (partiellement déterminée par lecture)

**Ce qui est établi.**

1. `Timestamp` est une `DateTime` reconstruite à partir d'un entier de **microsecondes depuis l'epoch Unix**, rendu par le code natif : `Timestamp = DateTime.UnixEpoch.AddTicks(timestampMicroseconds * ticksPerMicrosecond)` avec `ticksPerMicrosecond = 10` (207.0.0 `PCA.cs:258-259` ; 83.0.4 `PCA.cs:239-240`). Résolution : 1 µs. C'est donc une horloge **temps réel (murale)**, pas l'horloge monotone.
2. Le commentaire de l'API native le confirme : « Timestamp of the image in microseconds since the Unix epoch » (`timestampMicrosecondsRealtime`, 207.0.0 `Native.cs:694-696` et `713-715` ; 83.0.4 `Native.cs:680-681`, `699-700`).
3. Le natif rend **en plus** un second horodatage, en nanosecondes **monotone**, « used for getting the precise headset pose at the image's timestamp » (207.0.0 `Native.cs:696-697`, `715-716`). La version 207 ajoute : « Same time base as XrTime » (`Native.cs:716`, `726` ; `PCA.cs:75`). La version 83.0.4 dit seulement « monotonic nanoseconds » et expose une conversion `ConvertToXrTimeInSeconds` : « Converts a timestamp in nanoseconds to seconds in XR time domain » (83.0.4 `Native.cs:711-715`).
4. Cet horodatage monotone est un champ **privé** (`private long _timestampNsMonotonic`, 207.0.0 `PCA.cs:75` ; 83.0.4 `PCA.cs:74`), alimenté par `CameraGetLatestImage(...)` (207.0.0 `PCA.cs:248` ; 83.0.4 `PCA.cs:229`) ou, dans l'éditeur, par `CameraAcquireLatestCpuImage` (207.0.0 `PCA.cs:225-226`). **Seul le `Timestamp` temps réel est public** (`PCA.cs:127` en 207, `:125` en 83.0.4).
5. `Timestamp` n'est mis à jour que dans `Update()` quand une nouvelle image est disponible (207.0.0 `PCA.cs:248-260`).

**Ce qui n'est pas déterminable par lecture.**

- **À quel instant de l'exposition l'horodatage se réfère** (début, milieu, fin, ou heure de livraison par Camera2). Le C# ne fait que relayer un entier produit par la bibliothèque native fermée ; aucun commentaire ne le précise (« Timestamp of the image », `Native.cs:694`). Raison : l'information est dans le binaire natif et dans la pile Camera2 de Horizon OS, pas dans le C#.
- **Le décalage entre l'horloge temps réel et l'horloge monotone/XrTime** : non exposé. Les deux valeurs sont rendues ensemble par le natif, mais le C# public ne donne que la première.
- Cohérence avec `SENSOR_TIMESTAMP` d'Android Camera2 : non lisible (la page native p5 n'en parle pas).

**Conséquence pour SP-2.** Q-11 reste à mesurer (cible connue, mouvement contrôlé), avec ce cadre : l'horodatage publié est temps réel UTC, et la pose associée est calculée par le natif à partir d'un autre horodatage (monotone, base XrTime). Un biais constant entre « instant image » et « instant pose » ne peut pas se détecter par lecture.

## 2. Q-13 : pose du casque à un instant passé donné depuis Unity

### Réponse (partiellement déterminée par lecture)

**Ce qui est établi.**

1. **`GetCameraPose()` est déjà une requête de pose « exacte » à l'instant de l'image**, pas une interpolation côté Unity : elle interroge le suivi à l'horodatage monotone de l'image.
   - 207.0.0 : `MRUKNativeFuncs.GetHeadsetPoseAtTime(_timestampNsMonotonic, ref pos, ref rot)` (`PCA.cs:585`), puis conversion de repère `MRUK.FlipZ(...)` (`:586`) et composition avec `Intrinsics.LensOffset` (`:587-589`). Valeur par défaut (`default`) si la fonction native est absente (`:575-582`).
   - 83.0.4 : `OVRPlugin.GetNodePoseStateAtTime(GetMonotonicTimestamp(), OVRPlugin.Node.Head).Pose.ToOVRPose()` (`PCA.cs:540`), où `GetMonotonicTimestamp()` renvoie `MRUKNativeFuncs.ConvertToXrTimeInSeconds(_timestampNsMonotonic)` (`:546-554`).
2. **La requête à instant arbitraire existe sous forme publique dans le SDK Core** : `public static PoseStatef GetNodePoseStateAtTime(double time, Node nodeId)` (`com.meta.xr.sdk.core` 83.0.4, `Scripts/OVRPlugin.cs:4934`). Elle appelle `ovrp_GetNodePoseStateAtTime(time, nodeId, out state)` (`:4942`, déclaration native `:15160`), exige `version >= OVRP_1_76_0` (`:4939`) et **renvoie `PoseStatef.identity` silencieusement en cas d'échec** (`:4948-4950`). Le temps est un `double` en secondes dans le domaine XrTime (voir l'usage en `PCA.cs:540`) ; `OVRPlugin.GetTimeInSeconds()` existe (`OVRPlugin.cs:8091`).
3. **MRUK n'expose pas de requête à instant arbitraire** : `GetHeadsetPoseAtTime` est `internal` (`Native.cs:792` en 207) et `_timestampNsMonotonic` est privé. Le seul accès public est `GetCameraPose()` à l'instant de la dernière image ; `ViewportPointToRay` et `WorldToViewportPoint` acceptent une pose mise en cache (`cameraPose`, 207.0.0 `PCA.cs:506-516`, `537-546` ; p3 : « you can cache GetCameraPose, do a long-running image processing, then use the cached camera pose »).

**Ce qui n'est pas déterminable par lecture.**

- **Profondeur d'historique** : jusqu'où dans le passé `GetNodePoseStateAtTime` répond, s'il extrapole ou borne. Le C# ne fait que passer un `double` à `ovrp_GetNodePoseStateAtTime` (binaire natif).
- **Comportement au recentrage** (question de SPEC 4.3) : non lisible.
- **Correspondance entre le `Timestamp` public (temps réel) et l'argument `time` de `OVRPlugin`** (XrTime) : non exposée côté public. Pour interroger `OVRPlugin` à l'instant d'une image, il faudrait connaître son XrTime, qui est privé dans MRUK. Estimer le décalage entre l'epoch Unix et `OVRPlugin.GetTimeInSeconds()` est possible mais seulement par mesure.

**Conséquence pour mote.** Pour une image traitée au plus tard dans la frame où `IsUpdatedThisFrame` est vrai, appeler `GetCameraPose()` à ce moment donne la pose exacte à l'instant de l'image : il n'y a pas d'interpolation à faire. Une requête à instant passé n'est utile que si l'on traite l'image plus tard (cache de pose avant tout). Le chemin à instant arbitraire (`OVRPlugin.GetNodePoseStateAtTime`) existe mais sa plage de validité est à tester (SP-2).

## 3. Relecture des chiffres `[DOC]` de SPEC 4.3

Légende : **OK** concordant avec la page ; **ÉCART** différence ou nuance à corriger ; **NON ÉCRIT** affirmation que les pages n'énoncent pas.

### 3.1 Caméras passthrough

| # | Chiffre / affirmation de SPEC | Page | Verdict |
|---|---|---|---|
| 1 | Quest 3 et 3S, Horizon OS v74+ | p1 (« Horizon OS v74 or later »), p4 | OK |
| 2 | Construit sur Android Camera2 | p1 | OK |
| 3 | Passthrough doit être activé dans l'app | p1, p2 | OK |
| 4 | Deux caméras RGB frontales | p1 (« forward-facing RGB cameras »), p2/p3 (Left/Right) | OK |
| 5 | YUV420, 60 Hz, latence 20-40 ms | p1 « Performance » (« Internal data format YUV420 », « Data rate: 60Hz », « Image capture latency: 20-40ms ») | OK |
| 6 | 1280x960 max jusqu'à v81 ; 1280x1280 « et autres formats intermédiaires » dès v83 | p2 tableau : v81 et avant = 320x240, 640x480, 800x600, 1280x960 ; v83 et après = ces quatre + 640x360, 720x480, 720x576, 1024x576, 1280x720, 1280x1080, 1280x1280 | OK, mais précis : « intermédiaires » = 6 formats listés (dont 16:9 et 5:4) |
| 7 | ~1-2 % GPU par caméra, ~45 Mo | p1 « GPU overhead: ~1-2% per streamed camera », « Memory overhead: ~45MB » | OK. Nuance : la mémoire n'est pas dite « par caméra » |
| 8 | Permission `horizonos.permission.HEADSET_CAMERA` | p3, p4 (« only requires »), p5 | OK pour Unity/MRUK. **ÉCART inter-pages** : p1 dit « either `android.permission.CAMERA` or `horizonos.permission.HEADSET_CAMERA` », `CAMERA` donnant aussi accès à la caméra d'avatar ; p5 dit « you need **both** » ; p4 demande de retirer `CAMERA` |
| 9 | Non supporté dans le XR Simulator | p1, p4 | OK. p4 ajoute : casque physique ou Meta Horizon Link v2.1+ requis |
| 10 | Images = « Device User Data » | p1 « Best practices » | OK |

### 3.2 Composant MRUK `PassthroughCameraAccess`

| # | Affirmation | Page | Verdict |
|---|---|---|---|
| 11 | MRUK v81+ | p4 (« MRUK v81 or later ») | OK. Nuance p4 : « available in Horizon OS v81 and later » |
| 12 | Une instance par caméra, deux pour les deux | p3 (champ `CameraPosition`) | OK |
| 13 | `Timestamp` (`DateTime`), `GetCameraPose()` à ce timestamp, `IsUpdatedThisFrame` | p3, p2 (« at the current timestamp »), p4 | OK. La page p3 (v83) ne documente pas `GetCameraPose`, seule p2/p4 le fait |
| 14 | `Intrinsics` : `FocalLength`, `PrincipalPoint`, `SensorResolution`, `LensOffset`, **aucune distorsion** | p3 (structure à 4 champs) ; p3 ajoute « static … never change after » activation | OK |
| 15 | `GetTexture()` GPU ; `GetColors()` `NativeArray<Color32>`, coûteux | p3 (« this method is expensive, consider … AsyncGPUReadback ») | OK. p3 précise que la texture est mise à jour sur le thread de rendu avant l'affichage (un `Graphics.Blit()` lit la frame précédente) |
| 16 | `MaxFramerate` 60 par défaut, cadence réelle variable | p2 « Default value is 60 FPS » ; p3 « may vary based on lighting conditions and the current workload » | OK. p3 : modifiable seulement composant désactivé |
| 17 | `RequestedResolution`, `GetSupportedResolutions()` | p3 | OK. **ÉCART avec le code** : p3 (v83) dit « first smaller resolution » ; le C# 207.0.0 applique trois règles (même rapport d'aspect plus petit, sinon plus petit, sinon le minimum) (`PCA.cs:54-57`) |

### 3.3 Accès Camera2 natif

| # | Affirmation | Page | Verdict |
|---|---|---|---|
| 18 | Permissions `CAMERA` + `HEADSET_CAMERA`, `minSdk` 34 | p5 (« you need both », « minSdk set to 34 ») | OK |
| 19 | Clés `com.meta.extra_metadata.position` (0 gauche, 1 droite) et `camera_source` (0) | p1, p5 | OK. p5 : sur les caméras non passthrough, `position` est `null` |
| 20 | Exemples de calcul de pose « suivront » | p5 : « Examples on calculation position and rotation will follow soon » | OK. La page date du 24 avr. 2025 : non mise à jour |
| – | (SPEC 4.3 : disponibilité Camera2) | p1 : « Starting from Horizon OS v74, Camera2 … available » ; p5 : « Camera2 API is available on Horizon OS v76+ » | **ÉCART inter-pages** : v74 vs v76. SPEC retient v74 |

### 3.4 Profondeur d'environnement

| # | Affirmation | Page | Verdict |
|---|---|---|---|
| 21 | Quest 3 et 3S supportés (Unity « overview ») ; « XR.Oculus » dit Quest 3 seulement | p7 (« Quest 3 or Quest 3S »), p8 (« only supported on Quest 3 devices ») | OK, contradiction entre pages correctement relevée |
| 22 | Passthrough requis | p7, p6 | OK |
| 23 | Cartes par œil, swapchain lisible ; Unity : `RenderTexture` en rendu ou compute | p6 (`views[2]`, « readable swapchain »), p8 | OK |
| 24 | **« Aucune API CPU »** | p6, p8 n'en listent pas | **NON ÉCRIT** : déduit de l'absence d'une fonction CPU, jamais énoncé |
| 25 | Résolution à interroger à l'exécution via `xrGetEnvironmentDepthSwapchainStateMETA` ; ni résolution ni cadence documentées | p6 (`width`, `height`) | OK. Aucun chiffre de résolution ni de cadence dans p6, p7, p8 |
| 26 | Descripteur par œil : pose de création, FOV, `nearZ`, `farZ`, `createTime`, `minDepth`, `maxDepth` | p6 : par vue `fov`, `pose` ; image : `nearZ`, `farZ`, `swapchainIndex`. p8 (Unity `EnvironmentDepthFrameDesc`) : `isValid`, `createTime`, `predictedDisplayTime`, `swapchainIndex`, pose, FOV, `nearZ`, `farZ`, `minDepth`, `maxDepth` | **ÉCART** : SPEC mélange deux API. `createTime`, `minDepth`, `maxDepth` n'existent que dans le descripteur **Unity** ; la structure **OpenXR** (`XrEnvironmentDepthImageMETA`) ne les a pas. `isValid` et `predictedDisplayTime` sont omis |
| 27 | Pose dans l'espace de référence demandé | p6 (`XrEnvironmentDepthImageAcquireInfoMETA.space`) | OK |
| 28 | `nearZ`/`farZ` de projection OpenGL ; `farZ` infini ; quadrant `[[-1, -2*nearZ], [-1, 0]]` | p6 | OK (identique) |
| 29 | Portée minimale fiable ~0,2 m | p6, p7 | OK |
| 30 | Suppression des mains optionnelle selon l'appareil | p6 (`supportsHandRemoval`), p8 | OK |
| 31 | Surcoût dès activation, même sans lecture | p8 (« a performance overhead still exists if the feature is enabled ») | OK |

### 3.5 Éléments des pages absents de SPEC 4.3 mais utiles

- **Permission de profondeur** : `com.oculus.permission.USE_SCENE` (p6) ; en Unity `SetupEnvironmentDepth` la demande automatiquement (p8). SPEC 4.3 ne mentionne aucune permission pour la profondeur.
- **Décalage pose/instant de la carte** : « the display time and pose of the acquired depth map is likely not the same as the estimated display time and pose for your app's frame » (p6) ; il faut reprojeter avec la pose et le FOV fournis. Les cartes ne sont lues qu'entre `xrBeginFrame` et `xrEndFrame`, une acquisition par frame (p6). Un seul fournisseur de profondeur par application (p6).
- **Champ de vue** : le passthrough 1280x960 couvre une zone plus petite que ce que l'utilisateur voit ; 1280x1280 étend le FOV vertical sans tout couvrir (p1 « Known issues »). Pertinent pour la couverture de capture.
- **Pas sur toutes les plateformes** : `supportsEnvironmentDepth` doit être testé via `xrGetSystemProperties` (p6).
- **Résolution** : p1 déconseille de choisir « la plus grande » ; filtrer par format ou résolution testée.
- **Complément UploadVR** (`[SOURCE]`, SPEC 4.3) : source non officielle, **non relue** ici (hors du périmètre « pages Meta »).
- Le lien MRUK de p3 pointe vers `unity-pca-overview`, slug différent de `unity-pca-documentation` cité dans SPEC (même sujet ; slug non récupéré ici).

## 4. Effet sur SPEC (à traiter par le réviseur, SPEC.md non modifié)

- Q-11 : réponse partielle (horloge temps réel Unix µs ; instant d'exposition non déterminable) ; garder en SP-2.
- Q-13 : réponse partielle. `GetCameraPose()` suffit à l'instant de l'image ; l'API à instant arbitraire existe (`OVRPlugin.GetNodePoseStateAtTime`) mais plage et recentrage restent à tester.
- Corriger 4.3 : écart permission `CAMERA`/`HEADSET_CAMERA` (p1 vs p5), v74 vs v76 pour Camera2, descripteur de profondeur (Unity vs OpenXR), « aucune API CPU » à retagger (déduit), ajouter `USE_SCENE` et le décalage pose/instant de la carte.
- Version de MRUK à noter dans SPEC : 207.0.0 (courante), 83.0.4 (référence v83).
