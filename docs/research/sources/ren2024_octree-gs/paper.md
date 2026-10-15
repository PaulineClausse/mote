<!-- page 1 of 16 -->

arXiv:2403.17898v2 [cs.CV] 17 Oct 2024

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

1

# Octree-GS: Towards Consistent Real-time Rendering with LOD-Structured 3D Gaussians

Kerui Ren<sup>∗</sup>, Lihan Jiang<sup>∗</sup>, Tao Lu, Mulin Yu, Linning Xu, Zhangkai Ni, Bo Dai†

**Abstract—The recently proposed 3D Gaussian Splatting (3D-GS) demonstrates superior rendering fidelity and efficiency compared to NeRF-based scene representations. However, it struggles in large-scale scenes due to the high number of Gaussian primitives, particularly in zoomed-out views, where all primitives are rendered regardless of their projected size. This often results in inefficient use of model capacity and difficulty capturing details at varying scales. To address this, we introduce Octree-GS, a Level-of-Detail (LOD) structured approach that dynamically selects appropriate levels from a set of multi-scale Gaussian primitives, ensuring consistent rendering performance. To adapt the design of LOD, we employ an innovative grow-and-prune strategy for densification and also propose a progressive training strategy to arrange Gaussians into appropriate LOD levels. Additionally, our LOD strategy generalizes to other Gaussianbased methods, such as 2D-GS and Scaffold-GS, reducing the number of primitives needed for rendering while maintaining scene reconstruction accuracy. Experiments on diverse datasets demonstrate that our method achieves real-time speeds, with even 10** × **faster than state-of-the-art methods in large-scale scenes, without compromising visual quality. Project page:** [**https://city-super.github.io/octree-gs/**](https://city-super.github.io/octree-gs/)**.**

**Index Terms—Novel View Synthesis, 3D Gaussian Splatting, Consistent Real-time Rendering, Level-of-Detail**

## I. INTRODUCTION

HE field of novel view synthesis has seen significant advancements driven by the advancement of radiance fields [4], which deliver high-fidelity rendering. However, these methods often suffer from slow training and rendering speeds due to time-consuming stochastic sampling. Recently, 3D Gaussian splatting (3D-GS) [5] has pushed the field forward by using anisotropic Gaussian primitives, achieving near-perfect visual quality with efficient training times and tile-based splatting techniques for real-time rendering. With such strengths, it has significantly accelerated the process of replicating the real world into a digital counterpart [6]– [9], igniting the community’s imagination for scaling real-to-simulation environments [3], [10], [11]. With its exceptional visual effects, an unprecedented photorealistic experience in VR/AR [12], [13] is now more attainable than ever before.

A key drawback of 3D-GS [5] is the misalignment between the distribution of 3D Gaussians and the actual scene structure. Instead of aligning with the geometry of the scene, the Gaussian primitives are distributed based on their fit to the training views, leading to inaccurate and inefficient placement. This misalignment causes two bottleneck challenges: 1) it reduces robustness in rendering views that differ significantly from the training set, as the primitives are not optimized for generalization, and 2) results in redundant and overlap primitives that fail to efficiently represent scene details for real-time rendering, especially in large-scale urban scenes with millions of primitives.

There are variants of the vanilla 3D-GS [5] that aim at resolving the misalignment between the organization of 3D Gaussians and the structure of target scene. Scaffold-GS [3] enhances the structure alignment by introducing a regularly spaced feature grid as a structural prior, improving the arrangement and viewpoint-aware adjustment of Gaussians for better rendering quality and efficiency. Mip-Splatting [14] resorts to 3D smoothing and 2D Mip filters to alleviate the redundancy of 3D Gaussians during the optimiziation process of 3D-GS. 2D-GS [15] forces the primitives to better align with the surface, enabling faster reconstruction.

Although the aforementioned improvements have been extensively tested on diverse public datasets, we identify a new challenge in the Gaussian era: recording large-scale scenes is becoming increasingly common, yet these methods inherently struggles to scale, as shown in Fig 1. This limitation arises because they still rely on visibility-based filtering for primitive selection, considering all primitives within the view frustum without accounting for their projected sizes. As a result, every object detail is rendered, regardless of distance, leading to redundant computations and inconsistent rendering speeds, particularly in zoom-out scenarios involving large, complex scenes. The lack of Level-of-Detail (LOD) adaptation further forces all 3D Gaussians to compete across views, degrading rendering quality at different scales. As scene complexity increases, the growing number of Gaussians amplifies bottlenecks in real-time rendering.

To address the aforementioned issues and better accommodate the new era, we integrate an octree structure into the Gaussian representation, inspired by previous works [16]–[18] that demonstrate the effectiveness of spatial structures like octrees and multi-resolution grids for flexible content allocation and real-time rendering. Specifically, our method organizes scenes with hierarchical grids to meet LOD needs, efficiently adapting to complex or large-scale scenes during both training and inference, with LOD levels selected based on observation

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">K. Ren is with Shanghai Jiao Tong University and Shanghai AI Laboratory. E-mail: renkerui@sjtu.edu.cn.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">L. Jiang is with The University of Science and Technology of China and Shanghai AI Laboratory. E-mail: jianglihan@mail.ustc.edu.cn.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">T. Lu is with Brown University. E-mail: tao lu@brown.edu.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">B. Dai and M. Yu are with Shanghai AI Laboratory. E-mails: doubledaibo@gmail.com, yumulin@pjlab.org.cn.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">L. Xu is with The Chinese University of Hong Kong. E-mail: linningxu@link.cuhk.edu.hk.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">Z. Ni is with Tongji University.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">∗ Equal contribution.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">† Corresponding author.</span></small>

<!-- page 2 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

2

![Image block](images/ren2024_octree-gs_p2_b3.png)

Fig. 1: Visualization of a continuous zoom-out trajectory on the MatrixCity [1] dataset. Both the rendered 2D images and the corresponding Gaussian primitives are indicated. As indicated by the highlighted arrows, Octree-GS consistently demonstrates superior visual quality compared to state-of-the-art methods Hierarchical-GS [2] and Scaffold-GS [3]. Both SOTA methods fail to render the excessive number of Gaussian primitives included in distant views in real-time, whereas Octree-GS consistently achieves real-time rendering performance (≥ 30 FPS). First row metrics: FPS/storage size.

footprint and scene detail richness. We further employ a progressive training strategy, introducing a novel growing and pruning approach. A next-level growth operator enhances connections between LODs, increasing high-frequency detail, while redundant Gaussians are pruned based on opacity and view frequency. By adaptively querying LOD levels from the octree-based Gaussian structure based on viewing distance and scene complexity, our method minimizes the number of primitives needed for rendering, ensuring consistent efficiency, as shown in Fig. 1. In addition, Octree-GS effectively separates coarse and fine scene details, allowing for accurate Gaussian placement at appropriate scales, significantly improving reconstruction fidelity and texture detail.

Unlike other concurrent LOD methods [2], [19], our approach is an end-to-end algorithm that achieves LOD effects in a single training round, reducing training time and storage overhead. Notably, our LOD framework is also compatible with various Gaussian representations, including explicit Gaussians [5], [15] and neural Gaussians [3]. By incorporating our strategy, we have demonstrated significant enhancements in visual performance and rendering speed across a wide range of datasets, including both fine-detailed indoor scenes and largescale urban environments.

In summary, our method offers the following key contributions:

• To the best of our knowledge, Octree-GS is the **first approach to deal with the problem of Level-of-Detail in Gaussian representation**, enabling consistent rendering speed by dynamically adjusting the fetched LOD on-the-fly owing to our explicit octree structure design.

• We develop a novel **grow-and-prune strategy** optimized for LOD adaptation.

• We introduce a **progressive training strategy** to encourage more reliable distributions of primitives.

• Our LOD strategy is able to **generalize to any Gaussian-**

**based method**.

• Our methods, while maintaining the superior rendering quality, achieves **state-of-the-art rendering speed**, especially in **large-scale scenes** and extreme-view sequences, as shown in Fig. 1.

## II. RELATED WORK

## A. Novel View Synthesis

NeRF methods [4] have revolutionized the novel view synthesis task with their photorealistic rendering and viewdependent modeling effects. By leveraging classical volume rendering equations, NeRF trains a coordinate-based MLP to encode scene geometry and radiance, mapping directly from positionally encoded spatial coordinates and viewing directions. To ease the computational load of dense sampling process and forward through deep MLP layers, researchers have resorted to various hybrid-feature grid representations, akin to ‘caching’ intermediate latent features for final rendering [17], [20]–[26]. Multi-resolution hash encoding [24] is commonly chosen as the default backbone for many recent advancements due to its versatility for enabling fast and efficient rendering, encoding scene details at various granularities [27]–[29] and extended supports for LOD renderings [16], [30].

Recently, 3D-GS [5] has ignited a revolution in the field by employing anisotropic 3D Gaussians to represent scenes, achieving state-of-the-art rendering quality and speed. Subsequent studies have rapidly expanded 3D-GS into diverse downstream applications beyond static 3D reconstruction, sparking a surge of extended applications to 3D generative modeling [31]–[33], physical simulation [13], [34], dynamic modeling [35]–[37], SLAMs [38], [39], and autonomous driving scenes [10]–[12], etc. Despite the impressive rendering quality and speed of 3D-GS, its ability to sustain stable real-time rendering with rich content is hampered by the

<!-- page 3 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

3

accompanying rise in resource costs. This limitation hampers its practicality in speed-demanding applications, such as gaming in open-world environments and other immersive experiences, particularly for large indoor and outdoor scenes with computation-restricted devices.

## B. Spatial Structures for Neural Scene Representations

Various spatial structures have been explored in previous NeRF-based representations, including dense voxel grids [20], [22], sparse voxel grids [17], [21], point clouds [40], multiple compact low-rank tensor components [23], [41], [42], and multi-resolution hash tables [24]. These structures primarily aim to enhance training or inference speed and optimize storage efficiency. Inspired by classical computer graphics techniques such as BVH [43] and SVO [44] which are designed to model the scene in a sparse hierarchical structure for ray tracing acceleration. NSVF [20] efficiently skipping the empty voxels leveraging the neural implicit fields structured in sparse octree grids. PlenOctree [17] stores the appearance and density values in every leaf to enable highly efficient rendering. DOT [45] improves the fixed octree design in Plenoctree with hierarchical feature fusion. ACORN [18] introduces a multi-scale hybrid implicit–explicit network architecture based on octree optimization.

While vanilla 3D-GS [5] imposes no restrictions on the spatial distribution of all 3D Gaussians, allowing the modeling of scenes with a set of initial sparse point clouds, Scaffold-GS [3] introduces a hierarchical structure, facilitating more accurate and efficient scene reconstruction. In this work, we introduce a sparse octree structure to Gaussian primitives, which demonstrates improved capabilities such as real-time rendering stability irrespective of trajectory changes.

## C. Level-of-Detail (LOD)

LOD is widely used in computer graphics to manage the complexity of 3D scenes, balancing visual quality and computational efficiency. It is crucial in various applications, including real-time graphics, CAD models, virtual environments, and simulations. Geometry-based LOD involves simplifying the geometric representation of 3D models using techniques like mesh decimation; while rendering-based LOD creates the illusion of detail for distant objects presented on 2D images. The concept of LOD finds extensive applications in geometry reconstruction [46]–[48] and neural rendering [16], [27], [30], [49], [50]. Mip-NeRF [49] addresses aliasing artifacts by cone-casting approach approximated with Gaussians. BungeeNeRF [51] employs residual blocks and inclusive data supervision for diverse multi-scale scene reconstruction. To incorporate LOD into efficient grid-based NeRF approaches like instant-NGP [24], Zip-NeRF [30] further leverages supersampling as a prefiltered feature approximation. VR-NeRF [16] utilizes mip-mapping hash grid for continuous LOD rendering and an immersive VR experience. PyNeRF [27] employs a pyramid design to adaptively capture details based on scene characteristics. However, GS-based LOD methods fundamentally differ from above LOD-aware NeRF methods in scene representation and LOD introduction. For instance, NeRF can

compute LOD from per-pixel footprint size, whereas GS-based methods require joint LOD modeling from both the view and 3D scene level. We introduce a flexible octree structure to address LOD-aware rendering in the 3D-GS framework.

Concurrent works related to our method include LetsGo [52], CityGaussian [19], and Hierarchical-GS [2], all of which also leverage LOD for large-scale scene reconstruction. 1) LetsGo introduces multi-resolution Gaussian models optimized jointly, focusing on garage reconstruction, but requires multi-resolution point cloud inputs, leading to higher training overhead and reliance on precise point cloud accuracy, making it more suited for lidar scanning scenarios. 2) CityGaussian selects LOD levels based on distance intervals and fuses them for efficient large-scale rendering, but lacks robustness due to the need for manual distance threshold adjustments, and faces issues like stroboscopic effects when switching between LOD levels. 3) Hierarchical-GS, using a tree-based hierarchy, shows promising results in street-view scenes but involves post-processing for LOD, leading to increased complexity and longer training times. A common limitation across these methods is that each LOD level independently represents the entire scene, increasing storage demands. In contrast, Octree-GS employs an explicit octree structure with an accumulative LOD strategy, which significantly accelerates rendering speed while reducing storage requirements.

## III. PRELIMINARIES

In this section, we present a brief overview of the core concepts underlying 3D-GS [5] and Scaffold-GS [3].

## A. 3D-GS

3D Gaussian splatting [5] explicitly models scenes using anisotropic 3D Gaussians and renders images by rasterizing the projected 2D counterparts. Each 3D Gaussian $G ( x )$ is parameterized by a center position $\mu \in \mathbb { R } ^ { 3 }$ and a covariance $\tilde { \Sigma } \in \mathbb { R } ^ { 3 \times 3 }$

$$
G (x) = e ^ {- \frac {1}{2} (x - \mu) ^ {T} \Sigma^ {- 1} (x - \mu)},\tag{1}
$$

where $x$ is an arbitrary position within the scene, Σ is parameterized by a scaling matrix $S \in \mathbb { R } ^ { 3 }$ and rotation matrix $\mathbf { \hat { \nabla } } R \in \mathbb { R } ^ { 3 \times 3 }$ with $\left[ R S S ^ { T } R ^ { \tilde { T } } \right.$ . For rendering, opacity $\sigma \in \mathbb { R }$ and color feature $F   \in   \mathbb { R } ^ { C }$ are associated to each 3D Gaussian, while $F$ is represented using spherical harmonics (SH) to model view-dependent color $c   \in   \mathbb { R } ^ { 3 }$ . A tile-based rasterizer efficiently sorts the 3D Gaussians in front-to-back depth order and employs α-blending, following projecting them onto the image plane as 2D Gaussians $G ^ { \prime } ( x ^ { \prime } )$ [53]:

$$
C \left(x ^ {\prime}\right) = \sum_ {i \in N} T _ {i} c _ {i} \sigma_ {i}, \quad \sigma_ {i} = \alpha_ {i} G _ {i} ^ {\prime} \left(x ^ {\prime}\right),\tag{2}
$$

where $x ^ { \prime }$ is the queried pixel, N represents the number of sorted 2D Gaussians binded with that pixel, and $T$ denotes the transmittance as $\textstyle \prod _ { j = 1 } ^ { i - 1 } \left( 1 - \sigma _ { j } \right)$

<!-- page 4 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

4

![Image block](images/ren2024_octree-gs_p4_b3.png)

Fig. 2: (a) Pipeline of Octree-GS: starting from given sparse SfM points, we construct octree-structured anchors from the bounded 3D space and assign them to the corresponding LOD level. Unlike conventional 3D-GS methods treating all Gaussians equally, our approach involves primitives with varying LOD levels. We determine the required LOD levels based on the observation view and invoke corresponding anchors for rendering, as shown in the middle. As the LOD levels increase (from LOD 0 to LOD 2), the fine details of the vase accumulate progressively. (b) Anchor Initialization: We construct the octree structure grids within the determined bounding box. Then, the anchors are initialized at the voxel center of each layer , with their LOD level corresponding to the octree layer of the voxel, ranging from 0 to K − 1.

## B. Scaffold-GS

To efficiently manage Gaussian primitives, Scaffold-GS [3] introduces anchors, each associated with a feature describing the local structure. From each anchor, k neural Gaussians are emitted as follows:

$$
\{\mu_ {0}, \dots , \mu_ {k - 1} \} = x _ {v} + \{\mathcal {O} _ {0}, \dots , \mathcal {O} _ {k - 1} \} \cdot l _ {v}\tag{3}
$$

where $x _ { v }$ is the anchor position, $\{ \mu _ { i } \}$ denotes the positions of the $\mathbf { i } ^ { t h }$ neural Gaussian, and $l _ { v }$ is a scaling factor controlling the predicted offsets $\{ \mathcal { O } _ { i } \}$ . In addition, opacities, scales, rotations, and colors are decoded from the anchor features through corresponding MLPs. For example, the opacities are computed as:

$$
\{\alpha_ {0}, \dots , \alpha_ {k - 1} \} = \mathrm{F} _ {\alpha} (\tilde {\mathrm{f}} _ {\mathrm{v}}, \Delta_ {\mathrm{vc}}, \tilde {\mathrm{d}} _ {\mathrm{vc}}),\tag{4}
$$

where $\{ \alpha _ { i } \}$ represents the opacity of the $\mathbf { i } ^ { t h }$ neural Gaussian, decoded by the opacity MLP $F _ { \alpha }$ . Here, $\hat { f } _ { v } , \Delta _ { v c } ,$ and $\vec { d } _ { v c }$ correspond to the anchor feature, the relative viewing distance, and the direction to the camera, respectively. Once these properties are predicted, neural Gaussians are fed into the tile-based rasterizer, as described in [5], to render images. During the densification stage, Scaffold-GS treats anchors as the basic primitives. New anchors are established where the gradient of a neural Gaussian exceeds a certain threshold, while anchors with low average transparency are removed. This structured representation improves robustness and storage efficiency compared to the vanilla 3D-GS.

## IV. METHODS

Octree-GS hierarchically organizes anchors into an octree structure to learn a neural scene from multiview images. Each anchor can emit different types of Gaussian primitives, such as explicit Gaussians [5], [15] and neural Gaussians [3]. By incorporating the octree structure, which naturally introduces a

LOD hierarchy for both reconstruction and rendering, Octree-GS ensures consistently efficient training and rendering by dynamically selecting anchors from the appropriate LOD levels, allowing it to efficiently adapt to complex or largescale scenes. Fig. 2 illustrates our framework.

In this section, we first explain how to construct the octree from a set of given sparse SfM [54] points in Sec. IV-A. Next, we introduce an adapted anchor densification strategy based on LOD-aware ‘growing’ and ‘pruning’ operations in Sec IV-B. Sec. IV-C then introduces a progressive training strategy that activates anchors from coarse to fine. Finally, to address reconstruction challenges in wild scenes, we introduce appearance embedding (Sec. IV-D).

## A. LOD-structured Anchors

1) Anchor Definition.: Inspired by Scaffold-GS [3], we introduce anchors to manage Gaussian primitives. These anchors are positioned at the centers of sparse, uniform voxel grids with varying voxel sizes. Specifically, anchors with higher LOD L are placed within grids with smaller voxel sizes. In this paper, we define LOD 0 as the coarsest level. As the LOD level increases, more details are captured. Note that our LOD design is cumulative: the rendered images at LOD K rasterize all Gaussian primitives from LOD 0 to K. Additionally, each anchor is assigned a LOD bias $\Delta L$ to account for local complexity, and each anchor is associated with k Gaussian primitives for image rendering, whose positions are determined by Eq. 3. Moreover, our framework is generalized to support various types of Gaussians. For example, the Gaussian primitive can be explicitly defined with learnable distinct properties, such as 2D [15] or 3D Gaussians [5], or they can be neural Gaussians decoded from the corresponding anchors, as described in Sec. V-A4.

<!-- page 5 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

5

2) Anchor Initialization.: In this section, we describe the process of initializing octree-structured anchors from a set of sparse SfM points P. First, the number of octree layers, $K ,$ is determined based on the range of observed distances. Specifically, we begin by calculating the distance $d _ { i j }$ between each camera center of training image i and SfM point j. The $r _ { d } \mathrm { t h }$ largest and $r _ { d } \mathrm { t h }$ smallest distances are then defined as $d _ { m a x }$ and $d _ { m i n } ,$ respectively. Here, $r _ { d }$ is a hyperparameter used to discard outliers, which is typically set to 0.999 in all our experiment. Finally, K is calculated as:

$$
K = \lfloor \log_ {2} (\hat {d} _ {m a x} / \hat {d} _ {m i n}) \rceil + 1.\tag{5}
$$

where ⌊·⌉ denotes the round operator. The octree-structured grids with K layers are then constructed, and the anchors of each layer are voxelized by the corresponding voxel size:

$$
\mathbf {V} _ {L} = \left\{\left\lfloor \frac {\mathbf {P}}{\delta / 2 ^ {L}} \right\rceil \cdot \delta / 2 ^ {L} \right\},\tag{6}
$$

given the base voxel size δ for the coarsest layer corresponding to LOD 0 and $\mathbf { V } _ { L }$ for initialed anchors in LOD L . The properties of anchors and the corresponding Gaussian primitives are also initialized, please check the implementation V-A4 for details.

3) Anchor Selection.: In this section, we explain how to select the appropriate visible anchors to maintain both stable real-time rendering speed and high rendering quality. An ideal anchors is dynamically fetched from K LOD levels based on the pixel footprint of projected Gaussians on the screen. In practice, we simplify this by using the observation distance $d _ { i j }$ , as it is proportional to the footprint under consistent camera intrinsics. For varying intrinsics, a focal scale factor s is applied to adjust the distance equivalently. However, we find it sub-optimal if we estimate the LOD level solely based on observation distances. So we further set a learnable LOD bias $\Delta L$ for each anchor as a residual, which effectively supplements the high-frequency regions with more consistent details to be rendered during inference process, such as the presented sharp edges of an object as shown in Fig. 13. In detail, for a given viewpoint i, the corresponding LOD level of an arbitrary anchor $j$ is estimated as:

$$
\hat {L _ {i j}} = \lfloor L _ {i j} ^ {*} \rfloor = \lfloor \Phi (\log_ {2} (d _ {m a x} / (d _ {i j} * s))) + \Delta L _ {j} \rfloor ,\tag{7}
$$

where $d _ { i j }$ is the distance between viewpoint i and anchor $j . \quad \Phi ( \cdot )$ is a clamping function that restricts the fractional LOD level $L _ { i j } ^ { * }$ to the range $[ 0 , K   -   1 ]$ . Inspired by the progressive LOD techniques [55], Octree-GS renders images using cumulative LOD levels rather than a single LOD level. In summary, the anchor will be selected if its LOD level $L _ { j } \leq \hat { L _ { i j } }$ . We iteratively evaluate all anchors and select those that meet this criterion, as illustrated in Fig. 3. The Gaussian primitives emitted from the selected anchors are then passed into the rasterizer for rendering.

During inference, to ensure smooth rendering transitions between different LOD levels without introducing visible artifacts, we adopt an opacity blending technique inspired by [16], [51]. We use piecewise linear interpolation between adjacent levels to make LOD transitions continuous, effectively eliminating LOD aliasing. Specifically, in addition to

fully satisfied anchors, we also select nearly satisfied anchors that meet the criterion $L _ { j } = \hat { L _ { i j } } + 1$ . The Gaussian primitives of these anchors are also passed to the rasterizer, with their opacities scaled by $L _ { i j } ^ { * } - \hat { L _ { i j } }$

## B. Adaptive Anchor Gaussians Control

1) Anchor Growing.: Following the approach of [5], we use the view-space positional gradients of Gaussian primitives as a criterion to guide anchor densification. New anchors are grown in the unoccupied voxels across the octree-structured grids, following the practice of [3]. Specifically, every $T$ iterations, we calculate the average accumulated gradient of the spawned Gaussian primitives, denoted as $\nabla _ { g } .$ Gaussian primitives with $\nabla _ { g }$ exceeding a predefined threshold $\tau _ { g }$ are considered significant and they are converted into new anchors if located in empty voxels. In the context of the octree structure, the question arises: which LOD level should be assigned to these newly converted anchors? To address this, we propose a ‘nextlevel’ growing operation. This method adjusts the growing strategy by adding new anchors at varying granularities, with Gaussian primitives that have exceptionally high gradients being promoted to higher levels. To prevent overly aggressive growth into higher LOD levels, we monotonically increase the difficulty of growing new anchors to higher LOD levels by setting the threshold $\tau _ { g } ^ { L }   =   \tau _ { g } * 2 ^ { \beta L }$ , where $\tau _ { g }$ and $\beta$ are both hyperparameters, with default values of 0.0002 and 0.2, respectively. Gaussians at level $L$ are only promoted to the next level $L + 1$ if $\nabla _ { g } > \tau _ { g } ^ { L + 1 }$ , and they remain at the same level if $\tau _ { g } ^ { L } < \nabla _ { g } < \tau _ { g } ^ { \tilde { L } + 1 }$

We also utilize the gradient as the complexity cue of the scene to adjust the LOD bias $\Delta L$ . The gradient of an anchor is defined as the average gradient of the spawned Gaussian primitives, denoted as $\nabla _ { v } .$ . We select those anchors with $\nabla _ { v } >$ $\tau _ { g } ^ { L }   *   0 . 2 5$ , and increase the corresponding $\Delta L$ by a small userdefined quantity $\epsilon \colon \Delta L = \Delta L   +   \epsilon$ . We empirically set $\epsilon = 0 . 0 1$ 2) Anchor Pruning.: To eliminate redundant and ineffective anchors, we compute the average opacity of Gaussians generated over $T$ training iterations, in a manner similar to the strategies adopted in [3].

Moreover, we observe that some intolerable floaters appear in Fig. 4 (a) because a significant portion of anchors are not visible or selected in most training view frustums. Consequently, they are not sufficiently optimized, impacting rendering quality and storage overhead significantly. To address this issue, we define ‘view-frequency’ as the probability that anchors are selected in the training views, which directly correlates with the received gradient. We remove anchors with the view-frequency below $\tau _ { v } ,$ , where $\tau _ { v }$ represents the visibility threshold. This strategy effectively eliminates floaters, improving visual quality and significantly reducing storage, as demonstrated in Fig. 4.

## C. Progressive Training

Optimizing anchors across all LOD levels simultaneously poses inherent challenges in explaining rendering with decomposed LOD levels. All LOD levels try their best to represent

<!-- page 6 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

6

![Image block](images/ren2024_octree-gs_p6_b3.png)

Fig. 3: Visualization of anchors and projected 2D Gaussians in varying LOD levels. (1) The first row depicts scene decomposition with our full model, employing a coarse-to-fine training strategy as detailed in Sec. IV-C. A clear division of roles is evident between varying LOD levels: LOD 0 captures most rough contents, and higher LODs gradually recover the previously missed high-frequency details. This alignment with our motivation allows for more efficient allocation of model capacity with an adaptive learning process. (2) In contrast, our ablated progressive training studies (elaborated in Sec. V-C) take a naive approach. Here, all anchors are simultaneously trained, leading to an entangled distribution of Gaussian primitives across all LOD levels.

![Image block](images/ren2024_octree-gs_p6_b5.png)

Fig. 4: Illustration of the effect of view frequency. We visualize the rendered image and the corresponding LOD levels (with whiter colors indicating higher LOD levels) from a novel view. We observe that insufficiently optimized anchors will produce artifacts if pruning is based solely on opacity. After pruning anchors based on view frequency, not only are the artifacts eliminated, but the final storage is also reduced. Last row metrics: PSNR/storage size.

the 3D scene, making it difficult to decompose them thus leading to large overlaps.

Inspired by the progressive training strategy commonly used in prior NeRF methods [28], [51], [56], we implement a coarse-to-fine optimization strategy. begins by training on a subset of anchors representing lower LOD levels and progressively activates finer LOD levels throughout optimization, complementing the coarse levels with fine-grained details. In practice, we iteratively activate an additional LOD level after N iterations. Empirically, we start training from $\left\lfloor \frac { K } { 2 } \right\rfloor$ level to balance visual quality and rendering efficiency. Additionally, more time is dedicated to learning the overall structure because we want coarse-grained anchors to perform well in reconstructing the scene as the viewpoint moves away. Therefore, we set $N _ { i - 1 } = \omega N _ { i }$ , where $N _ { i }$ denotes the training iterations for LOD level $L = i ,$ and $\omega \geq 1$ is the growth factor. Note that during the progressive training stage, we disable the next level grow operator.

With this approach, we find that the anchors can be arranged more faithfully into different LOD levels as demonstrated in Fig. 3, reducing anchor redundance and leading to faster

rendering without reducing the rendering quality.

## D. Appearance Embedding

In large-scale scenes, the exposure compensation of training images is always inconsistent, and 3D-GS [5] tends to produce artifacts by averaging the appearance variations across training images. To address this, and following the approach of prior NeRF papers [57], [58], we integrate Generative Latent Optimization (GLO) [59] to generate the color of Gaussian primitives. For instance, we introduce a learnable individual appearance code for each anchor, which is fed as an addition input to the color MLP to decode the colors of the Gaussian primitives. This allows us to effectively model in-the-wild scenes with varying appearances. Moreover, we can also interpolate the appearance code to alter the visual appearance of these environments, as shown in Fig. 12.

## V. EXPERIMENTS

## A. Experimental Setup

1) Datasets: We conduct comprehensive evaluations on 21 small-scale scenes and 7 large-scale scenes from various public datasets. Small-scale scenes include 9 scenes from Mip-NeRF360 [50], 2 scenes from Tanks&Temples [60], 2 scenes in DeepBlending [61] and 8 scenes from BungeeNeRF [51].

For large-scale scenes, we provide a detailed explanation. Specifically, we evaluate on the Block Small and Block All scenes (the latter being 10× larger) in the MatrixCity [1] dataset, which uses Zig-Zag trajectories commonly used in oblique photography. In the MegaNeRF [62] dataset, we choose the Rubble and Building scenes, while in the UrbanScene3D [63] dataset, we select the Residence and Sci-Art scenes. Each scene contains thousands of high-resolution images, and we use COLMAP [54] to obtain sparse SfM points and camera poses. In the Hierarchical-GS [2] dataset, we maintain their original settings and compare both methods

<!-- page 7 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

7

TABLE I: Quantitative comparison on real-world datasets [50], [60], [61]. Octree-GS consistently achieves superior rendering quality compared to baselines with reduced number of Gaussian primitives rendered per-view. We highlight best and second-best in each category.

<table><tr><td rowspan="2">DatasetMethod | Metrics</td><td colspan="4">Mip-NeRF360</td><td colspan="4">Tanks&amp;Temples</td><td colspan="4">Deep Blending</td></tr><tr><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>#GS(k)/Mem</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>#GS(k)/Mem</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>#GS(k)/Mem</td></tr><tr><td>Mip-NeRF360 [50]</td><td>27.69</td><td>0.792</td><td>0.237</td><td>-</td><td>23.14</td><td>0.841</td><td>0.183</td><td>-</td><td>29.40</td><td>0.901</td><td>0.245</td><td>-</td></tr><tr><td>2D-GS [5]</td><td>26.93</td><td>0.800</td><td>0.251</td><td>397/440.8M</td><td>23.25</td><td>0.830</td><td>0.212</td><td>352/204.4M</td><td>29.32</td><td>0.899</td><td>0.257</td><td>196/335.3M</td></tr><tr><td>3D-GS [5]</td><td>27.54</td><td>0.815</td><td>0.216</td><td>937/786.7M</td><td>23.91</td><td>0.852</td><td>0.172</td><td>765/430.1M</td><td>29.46</td><td>0.903</td><td>0.242</td><td>398/705.6M</td></tr><tr><td>Mip-Splatting [14]</td><td>27.61</td><td>0.816</td><td>0.215</td><td>1013/838.4M</td><td>23.96</td><td>0.856</td><td>0.171</td><td>832/500.4M</td><td>29.56</td><td>0.901</td><td>0.243</td><td>410/736.8M</td></tr><tr><td>Scaffold-GS [3]</td><td>27.90</td><td>0.815</td><td>0.220</td><td>666/197.5M</td><td>24.48</td><td>0.864</td><td>0.156</td><td>626/167.5M</td><td>30.28</td><td>0.909</td><td>0.239</td><td>207/125.5M</td></tr><tr><td>Anchor-2D-GS</td><td>26.98</td><td>0.801</td><td>0.241</td><td>547/392.7M</td><td>23.52</td><td>0.835</td><td>0.199</td><td>465/279.0M</td><td>29.35</td><td>0.896</td><td>0.264</td><td>162/289.0M</td></tr><tr><td>Anchor-3D-GS</td><td>27.59</td><td>0.815</td><td>0.220</td><td>707/492.0M</td><td>24.02</td><td>0.847</td><td>0.184</td><td>572/349.2M</td><td>29.66</td><td>0.899</td><td>0.260</td><td>150/272.9M</td></tr><tr><td>Our-2D-GS</td><td>27.02</td><td>0.801</td><td>0.241</td><td>397/371.6M</td><td>23.62</td><td>0.842</td><td>0.187</td><td>330/191.2M</td><td>29.44</td><td>0.897</td><td>0.264</td><td>84/202.3M</td></tr><tr><td>Our-3D-GS</td><td>27.65</td><td>0.815</td><td>0.220</td><td>504/418.6M</td><td>24.17</td><td>0.858</td><td>0.161</td><td>424/383.9M</td><td>29.65</td><td>0.901</td><td>0.257</td><td>79/180.0M</td></tr><tr><td>Our-Scaffold-GS</td><td>28.05</td><td>0.819</td><td>0.214</td><td>657/139.6M</td><td>24.68</td><td>0.866</td><td>0.153</td><td>443/88.5M</td><td>30.49</td><td>0.912</td><td>0.241</td><td>112/71.7M</td></tr></table>

2D-GS

3D-GS

Mip-Splatting

Scaffold-GS

GT

Our-Scaffold-GS

![Image block](images/ren2024_octree-gs_p7_b11.png)

Fig. 5: Qualitative comparison of our method and SOTA methods [3], [5], [14], [15] across diverse datasets [50], [51], [60], [61]. We highlight the difference with colored patches. Compared to existing baselines, our method successfully captures very fine details presented in indoor and outdoor scenes, particularly for objects with thin structures such as trees, light-bulbs, decorative texts and etc..

on a chunk of the SmallCity scene, which includes 1,470 training images and 30 test images, each paired with depth and mask images.

For the Block All scene and the SmallCity scene, we employ the train and test information provided by their authors. For other scenes, we uniformly select one out of every eight images as test images, with the remaining images used for training.

2) Metrics: In addition to the visual quality metrics PSNR, SSIM [64] and LPIPS [65], we also report the file size for storing anchors, the average selected Gaussian primitives used in per-view rendering process, and the rendering speed FPS as a fair indicator for memory and rendering efficiency. We provide the average quantitative metrics on test sets in the main paper and leave the full table for each scene in the supplementary material.

3) Baselines: We compare our method against 2D-GS [15], 3D-GS [5], Scaffold-GS [3], Mip-Splatting [14] and two concurrent works, CityGaussian [19] and Hierarchical-GS [2]. In the Mip-NeRF360 [50], Tanks&Temples [60], and Deep-Blending [61] datasets, we compare our method with the top four methods. In the large-scale scene datasets MatrixCity [1], MegaNeRF [62] and UrbanScene3D [63], we add the results of CityGaussian and Hierarchical-GS for comparison. To ensure consistency, we remove depth supervision from Hierarchical-GS in these experiments. Following the original setup of Hierarchical-GS, we report results at different granularities (leaves, $\tau _ { 1 } ~ = ~ 3 , ~ \tau _ { 2 } ~ = ~ 6 , ~ \tau _ { 3 } ~ = ~ 1 5 )$ , each one is after the optimization of the hierarchy. In the street-view dataset, we compare exclusively with Hierarchical-GS, the current state-of-the-art (SOTA) method for street-view data. In this experiment, we apply the same depth supervision used in

<!-- page 8 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

8

TABLE II: Quantitative comparison on large-scale urban dataset [1], [62], [63]. In addition to three methods compared in Tab. I, we also compare our method with CityGaussian [19] and Hierarchical-GS [2], both of which are specifically targeted at large-scale scenes. It is evident that Octree-GS outperforms the others in both rendering quality and storage efficiency. We highlight best and second-best in each category.

| Dataset Method Metrics | PSNR↑ | Bl SSIM↑ | ock Sma LPIPS↓ | ll#GS(k)/Mem | PSNR↑ | B SSIM↑ | lock All LPIPS↓ | #GS(k)/Mem | PSNR↑ | SSIM↑ | Building LPIPS↓ | #GS(k)/Mem |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 26.82 | 0.823 | 0.246 | 1432/3387.4M | 24.45 | 0.746 | 0.385 | 979/3584.3M | 22.04 | 0.728 | 0.332 | 842/1919.2M |
| Mip-Splatting [14] | 27.14 | 0.829 | 0.24 | 860/3654.6M | 24.28 | 0.742 | 0.388 | 694/3061.8M | 22.13 | 0.726 | 0.335 | 1066/2498.6M |
| Scaffold-GS [3] | 29.00 | 0.868 | 0.210 | 357/371.2M | 26.30 | 0.808 | 0.293 | 690/2272.2M | 22.42 | 0.719 | 0.336 | 438/833.2M |
| CityGaussian [19] | 27.46 | 0.808 | 0.267 | 538/4382.7M | 26.26 | 0.800 | 0.324 | 235/4316.6M | 20.94 | 0.706 | 0.310 | 520/3026.8M |
| Hierarchical-GS [2] | 27.69 | 0.823 | 0.276 | 271/1866.7M | 26.00 | 0.803 | 0.306 | 492/4874.2M | 23.28 | 0.769 | 0.273 | 1973/3778.6M |
| Hierarchical-GS(τ<sub>1</sub>) | 27.67 | 0.823 | 0.276 | 271/1866.7M | 25.44 | 0.788 | 0.320 | 435/4874.2M | 23.08 | 0.758 | 0.285 | 1819/3778.6M |
| Hierarchical-GS(τ<sub>2</sub>) | 27.54 | 0.820 | 0.280 | 268/1866.7M | 25.39 | 0.783 | 0.325 | 355/4874.2M | 22.55 | 0.726 | 0.313 | 1473/3778.6M |
| Hierarchical-GS(τ<sub>3</sub>) | 26.60 | 0.794 | 0.319 | 221/1866.7M | 25.19 | 0.773 | 0.352 | 186/4874.2M | 21.35 | 0.635 | 0.392 | 820/3778.6M |
| Our-3D-GS | 29.37 | 0.875 | 0.197 | 175/755.7M | 26.86 | 0.833 | 0.260 | 218/3205.1M | 22.67 | 0.736 | 0.320 | 447/1474.5M |
| Our-Scaffold-GS | 29.83 | 0.887 | 0.192 | 360/380.3M | 27.31 | 0.849 | 0.229 | 344/1648.6M | 23.66 | 0.776 | 0.267 | 619/1146.9M |

| Dataset Method Metrics | PSNR↑ | SSIM↑ | Rubble LPIPS↓ | #GS(k)/Mem | PSNR↑ | SSIM↑ | Residence LPIPS↓ | #GS(k)/Mem | PSNR↑ | SSIM↑ | Sci-Art LPIPS↓ | #GS(k)/Mem |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 25.20 | 0.757 | 0.318 | 956/2355.2M | 21.94 | 0.764 | 0.279 | 1209/2498.6M | 21.85 | 0.787 | 0.311 | 705/950.6M |
| Mip-Splatting [14] | 25.16 | 0.746 | 0.335 | 760/1787.0M | 21.97 | 0.763 | 0.283 | 1301/2570.2M | 21.92 | 0.784 | 0.321 | 615/880.2M |
| Scaffold-GS [3] | 24.83 | 0.721 | 0.353 | 492/470.3M | 22.00 | 0.761 | 0.286 | 596/697.7M | 22.56 | 0.796 | 0.302 | 526/452.5M |
| CityGaussian [19] | 24.67 | 0.758 | 0.286 | 619/3000.3M | 21.92 | 0.774 | 0.257 | 732/3196.0M | 20.07 | 0.757 | 0.290 | 461/1300.3M |
| Hierarchical-GS [2] | 25.37 | 0.761 | 0.300 | 1541/2345.0M | 21.74 | 0.758 | 0.274 | 2040/2498.6M | 22.02 | 0.810 | 0.257 | 2363/2160.6M |
| Hierarchical-GS(τ<sub>1</sub>) | 25.27 | 0.754 | 0.305 | 1478/2345.0M | 21.70 | 0.756 | 0.276 | 1972/2498.6M | 22.00 | 0.808 | 0.259 | 2226/2160.6M |
| Hierarchical-GS(τ<sub>2</sub>) | 24.80 | 0.724 | 0.329 | 1273/2345.0M | 21.49 | 0.743 | 0.291 | 1694/2498.6M | 21.93 | 0.802 | 0.268 | 1916/2160.6M |
| Hierarchical-GS(τ<sub>3</sub>) | 23.55 | 0.628 | 0.414 | 781/2345.0M | 20.69 | 0.683 | 0.363 | 976/2498.6M | 21.50 | 0.766 | 0.324 | 1165/2160.6M |
| Our-3D-GS | 24.67 | 0.728 | 0.345 | 489/1392.6M | 21.60 | 0.736 | 0.314 | 350/986.2M | 22.52 | 0.817 | 0.256 | 630/1331.2M |
| Our-Scaffold-GS | 25.34 | 0.763 | 0.299 | 674/693.5M | 22.29 | 0.762 | 0.288 | 344/618.8M | 23.38 | 0.828 | 0.240 | 871/866.9M |

![Image block](images/ren2024_octree-gs_p8_b6.png)

Fig. 6: Qualitative comparisons of Octree-GS against baselines [2], [3], [5], [19] across large-scale datasets [1], [62], [63]. As shown in the highlighted patches and arrows above, our method consistently outperforms the baselines, especially in modeling fine details (1st & 3rd row), texture-less regions (2nd row), which are common in large-scale scenes.

## Hierarchical-GS for fair comparison.

4) Instances of Our Framework: To demonstrate the generalizability of the proposed framework, we apply it to 2D-GS [15], 3D-GS [5], and Scaffold-GS [3], which we refer to as Our-2D-GS, Our-3D-GS and Our-Scaffold-GS, respectively. In addition, for a fair comparison and deeper analysis, we modify 2D-GS and 3D-GS to anchor versions. Specifically, we voxelize the input SfM points to anchors and assign each of them 2D or 3D Gaussians, while maintaining the

same densification strategy as Scaffold-GS. We denote these modified versions as Anchor-2D-GS and Anchor-3D-GS.

5) Implementation Details: For 3D-GS model we employ standard L1 and SSIM loss, with weights set to 0.8 and 0.2, respectively. For 2D-GS model, we retain the distortion loss $\mathcal { L } _ { d } \; = \; \textstyle \sum _ { i , j } \omega _ { i } \omega _ { j } \left| z _ { i } - z _ { j } \right|$ and normal loss ${ \mathcal { L } } _ { n } \; = \;$ $\begin{array} { r } { \sum _ { i } \omega _ { i } \left( 1 - \mathbf { n } _ { i } ^ { \mathrm { T } } \mathbf { N } \right) } \end{array}$ , with weights set to 0.01 and 0.05, respectively. For Scaffold-GS model, we keep an additional volume regularization loss $\begin{array} { r } { \mathcal { L } _ { \mathrm { v o l } } = \sum _ { i = 1 } ^ { N } \mathrm { P r o d } \left( s _ { i } \right) } \end{array}$ , with a weight set

<!-- page 9 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

9

![Image block](images/ren2024_octree-gs_p9_b3.png)

Fig. 7: Qualitative comparisons of our approach against Hierarchical-GS [2]. We present both the highest-quality setting (leaves) and a reasonably reduced LOD setting (τ<sub>2</sub> = 6 pixels). Octree-GS demonstrates superior performance in street views, specially in thin geometries and texture-less regions (e.g., railings, signs and pavements.)

TABLE III: Quantitative comparison on the SMALLCITY scene of the Hierarchical-GS [2] dataset. The competing metrics are sourced from the original paper.

| Method | PSNR(↑) | SSIM(↑) | LPIPS(↓) | FPS(↑) |
| --- | --- | --- | --- | --- |
| 3D-GS [5] | 25.34 | 0.776 | 0.337 | 99 |
| Hierarchical-GS [2] | 26.62 | 0.820 | 0.259 | 58 |
| Hierarchical-GS(τ<sub>1</sub>) | 26.53 | 0.817 | 0.263 | 86 |
| Hierarchical-GS(τ<sub>2</sub>) | 26.29 | 0.810 | 0.275 | 110 |
| Hierarchical-GS(τ<sub>3</sub>) | 25.68 | 0.786 | 0.324 | 159 |
| Our-3D-GS | 25.77 | 0.811 | 0.272 | 130 |
| Our-Scaffold-GS | 26.10 | 0.826 | 0.235 | 89 |

to 0.01.

We adjust the training and densification iterations across all compared methods to ensure a fair comparison. Specifically, for small-scale scenes [2], [50], [51], [60], [61], training was set to 40k iterations, with densification concluding at 20k iterations. For large-scale scenes [1], [62], [63], training was set to 100k iterations, with densification ending at 50k iterations.

We set the voxel size to 0.001 for all scenes in the modified anchor versions of 2D-GS [15], 3D-GS [5], and Scaffold-GS [3], while for our method, we set the voxel size for the intermediate level of the anchor grid to 0.02. For the progress training, we set the total training iteration to 10k with ω = 1.5. Since not all layers are fully densified during the progressive training process, we extend the densification by an additional 10k iterations, and we set the densification interval T = 100 empirically. We set the visibility threshold $\tau _ { v }$ to 0.7 for the small-scale scenes [50], [51], [60], [61],as these datasets contain densely captured images, while for large-scale scenes [2], [62], [63], we set $\tau _ { v }$ to 0.01. In addition, for the multi-scale dataset [51], we set $\tau _ { v }$ to 0.2.

All experiments are conducted on a single NVIDIA A100 80G GPU. To avoid the impact of image storage on GPU memory, all images were stored on the CPU.

![Image block](images/ren2024_octree-gs_p9_b11.png)

Fig. 8: Comparison of different versions of the 2D-GS [15] model. We showcase the rendering results on the stump scene from the Mip-NeRF360 [50] dataset. We report PSNR, average number of Gaussians for rendering and storage size.

## B. Results Analysis

Our evaluation encompasses a wide range of scenes, including indoor and outdoor environments, both synthetic and real-world, as well as large-scale urban scenes from both aerial views and street views. We demonstrate that our method pre-serves fine-scale details while reducing the number of Gaussians, resulting in faster rendering speed and lower storage overhead, as shown in Fig. 5, 6, 7, 8 and Tab. I, IV, II, III, V.

## 1) Performance Analysis:

a) Quality Comparisons: Our method introduces anchors with octree structure, which decouple multi-scale Gaussian primitives into varying LOD levels. This approach enables finer Gaussian primitives to capture scene details more accurately, thereby enhancing the overall rendering quality. In Fig. 5, 6, 7 and Tab. I, II, III, we compare Octree-GS to previous state-of-the-art (SOTA) methods, demonstrating that our method consistently outperforms the baselines across both small-scale and large-scale scenes, especially in fine details and texture-less regions. Notably, when compared to Hierarchical-GS [2] on the street-view dataset, Octree-GS exhibits slightly lower PSNR values but significantly better visual quality, with LPIPS scores of 0.235 for ours and 0.259 for theirs.

b) Storage Comparisons: As shown in Tab. I, II, our method reduces the number of Gaussian primitives used for rendering, resulting in faster rendering speed and lower storage overhead. This demonstrates the benefits of our two main improvements: 1) our LOD structure efficiently arranges Gaussian primitives, with coarse primitives representing low-

<!-- page 10 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

10

TABLE IV: Quantitative comparison on the BungeeNeRF [51] dataset. We provide metrics for each scale and their average across all four. Scale-1 denotes the closest views, while scale-4 covers the entire landscape. We note a notable rise in Gaussian counts for baseline methods when zooming out from scale 1 to 4, whereas our method maintains a significantly lower count, ensuring consistent rendering speed across all LOD levels. We highlight best and second-best in each category.

| Dataset Method Metrics | PSNR↑ | Bungee SSIM↑ | NeRF (A LPIPS↓ | verage)#GS(k)/Mem | scal PSNR↑ | e-1#GS(k) | scal PSNR↑ | e-2#GS(k) | scal PSNR↑ | e-3#GS(k) | scal PSNR↑ | e-4#GS(k) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2D-GS [5] | 27.10 | 0.903 | 0.121 | 1079/886.1M | 28.18 | 205 | 28.11 | 494 | 25.99 | 1826 | 23.71 | 2365 |
| 3D-GS [5] | 27.79 | 0.917 | 0.093 | 2686/1792.3M | 30.00 | 522 | 28.97 | 1272 | 26.19 | 4407 | 24.20 | 5821 |
| Mip-Splatting [14] | 28.14 | 0.918 | 0.094 | 2502/1610.2M | 29.79 | 503 | 29.37 | 1231 | 26.74 | 4075 | 24.44 | 5298 |
| Scaffold-GS [3] | 28.16 | 0.917 | 0.095 | 1652/319.2M | 30.48 | 303 | 29.18 | 768 | 26.56 | 2708 | 24.95 | 3876 |
| Anchor-2D-GS | 27.18 | 0.885 | 0.140 | 1050/533.8M | 29.80 | 260 | 28.26 | 601 | 25.43 | 1645 | 23.71 | 2026 |
| Anchor-3D-GS | 27.90 | 0.909 | 0.114 | 1565/790.3M | 30.85 | 391 | 29.29 | 905 | 26.13 | 2443 | 24.49 | 3009 |
| Our-2D-GS | 27.34 | 0.893 | 0.129 | 676/736.1M | 30.09 | 249 | 28.72 | 511 | 25.42 | 1003 | 23.41 | 775 |
| Our-3D-GS | 27.94 | 0.909 | 0.110 | 952/1045.7M | 31.11 | 411 | 29.42 | 819 | 25.88 | 1275 | 23.77 | 938 |
| Our-Scaffold-GS | 28.39 | 0.923 | 0.088 | 1474/296.7M | 31.11 | 486 | 29.59 | 1010 | 26.51 | 2206 | 25.07 | 2167 |

TABLE V: Quantitative comparison of rendering speed on the MatrixCity [1] dataset. We report the averaged FPS on three novel view trajectories (Fig. 9). Our method shows consistent rendering speed above 30 FPS at 2k image resolution while all baseline methods fail to meet the real-time performance.

| Method Traj. | T<sub>1</sub> | T<sub>2</sub> | T<sub>3</sub> |
| --- | --- | --- | --- |
| 3D-GS [5] | 13.81 | 11.70 | 13.50 |
| Scaffold-GS [3] | 6.69 | 7.37 | 8.04 |
| Hierarchical-GS [2] | 9.13 | 8.54 | 8.91 |
| Hierarchical-GS(τ<sub>1</sub>) | 16.14 | 13.26 | 14.79 |
| Hierarchical-GS(τ<sub>2</sub>) | 19.70 | 19.59 | 18.94 |
| Hierarchical-GS(τ<sub>3</sub>) | 24.33 | 25.29 | 24.75 |
| Our-3D-GS | 57.08 | 56.85 | 56.07 |
| Our-Scaffold-GS | 40.91 | 35.17 | 40.31 |

frequency scene information, which previously required redundant primitives; and 2) our view-frequency strategy significantly prunes unnecessary primitives.

c) Variants Comparisons: As described in Sec. IV, our method is agnostic to the specific Gaussian representation and can be easily adapted to any Gaussian-based method with minimal effort. In Tab. I, the modified anchor-version of 2D-GS [15] and 3D-GS [5] achieve competitive rendering quality with fewer file storage than the original methods. This demonstrates that the anchor design organizes the Gaussian primitives more efficiently, reducing redundancy and creating a more compact way. More than the anchor design, Octree-GS delivers better visual performance and fewer Gaussian primitives as shown in Tab. I, which benefits from the explicit, multi-level anchor design. In Fig. 8, we compare the vanilla 2D-GS with the anchor-version and octree-version method. Among them, the octree-version provides the most detail and the least amount of Gaussian primitives and storage.

## 2) Efficiency Analysis:

a) Rendering Time Comparisons: Our goal is to enable real-time rendering of Gaussian representation models at any position within the scene using Level-of-Detail techniques. To evaluate our approach, we compare Octree-GS with three state-

![Chart block](images/ren2024_octree-gs_p10_b11.png)

Fig. 9: (a) The figure shows the rendering speed with respect to distance for different methods along trajectory $T _ { 1 }$ , both Our-3D-GS and Our-Scaffold-GS achieve real-time rendering speeds (≥ 30FPS). (b) The visualization depicts three different trajectories, corresponding to $T _ { 1 }$ , $T _ { 2 } ,$ , and $T _ { 3 }$ in Tab. V, which are commonly found in video captures of large-scale scenes and illustrate the practical challenges involved.

of-the-art methods [2], [3], [5] on three novel view trajectories in Tab. V and Fig. 9. These trajectories represent common movements in large-scale scenes, such as zoom-in, 360-degree circling, and multi-scale circling. As shown in Tab. V and Fig. 5, our method excels at capturing fine-grained details in close views while maintaining consistent rendering speeds at larger scales. Notably, our rendering speed is nearly 10× faster than Scaffold-GS [3] in large-scale scenes and extreme-view sequences, which depends on our innovative LOD structure design.

b) Training Time Comparisons: While our core contribution is the acceleration of rendering speed through LOD design, training speed is also critical for the practical application of photorealistic scene reconstruction. Below, we provide statistics for the Mip-NeRF360 [50] dataset (40k iterations): 2D-GS (28 mins), 3D-GS (34 mins), Mip-Splatting (46 mins), Scaffold-GS (29 mins), and Our-2D-GS (20 mins), Our-3D-GS (21 mins), Our-Scaffold-GS (23 mins). Additionally, we report the training time for the concurrent work, Hierarchical-GS [2]. This method requires three stages to construct the LOD structure, which result in a longer training time (38 minutes for

<!-- page 11 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

11

TABLE VI: Quantitative comparison on multi-resolution Mip-NeRF360 [50] dataset. Octree-GS achieves better rendering quality across all scales compared to baselines.

<table><tbody><tr><td rowspan="2">Scale Factor</td><td rowspan="2"></td><td rowspan="2">1×</td><td rowspan="2"></td><td rowspan="2"></td><td rowspan="2">2×</td><td rowspan="2"></td><td rowspan="2"></td><td rowspan="2">4×</td><td rowspan="2"></td><td rowspan="2"></td><td rowspan="2">8×</td><td rowspan="2"></td><td rowspan="2">#GS(k)</td></tr><tr></tr><tr><td>Method Metrics</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td></td></tr><tr><td>3D-GS [5]</td><td>26.16</td><td>0.757</td><td>0.301</td><td>27.33</td><td>0.822</td><td>0.202</td><td>28.55</td><td>0.884</td><td>0.117</td><td>27.85</td><td>0.897</td><td>0.086</td><td>430</td></tr><tr><td>Scaffold-GS [3]</td><td>26.81</td><td>0.767</td><td>0.285</td><td>28.09</td><td>0.835</td><td>0.183</td><td>29.52</td><td>0.898</td><td>0.099</td><td>28.98</td><td>0.915</td><td>0.072</td><td>369</td></tr><tr><td>Mip-Splatting [14]</td><td>27.43</td><td>0.801</td><td>0.244</td><td>28.56</td><td>0.857</td><td>0.152</td><td>30.00</td><td>0.910</td><td>0.087</td><td>31.05</td><td>0.942</td><td>0.055</td><td>642</td></tr><tr><td>Our-Scaffold-GS</td><td>27.68</td><td>0.791</td><td>0.245</td><td>28.82</td><td>0.850</td><td>0.157</td><td>30.27</td><td>0.906</td><td>0.087</td><td>31.18</td><td>0.932</td><td>0.057</td><td>471</td></tr></tbody></table>

![Image block](images/ren2024_octree-gs_p11_b5.png)

Fig. 10: Qualitative comparison of full-resolution and low-resolution (1/8 of full-resolution) on multi-resolution Mip-NeRF360 [50] datasets. Our approach demonstrates adaptive anti-aliasing and effectively recovers fine-grained details, while baselines often produce artifacts, particularly on elongated structures such as bicycle wheels and handrails.

![Image block](images/ren2024_octree-gs_p11_b7.png)

Fig. 11: Qualitative comparison of scale-1 and scale-4 on the Barcelona scene from the BungeeNeRF [51] dataset. Both Anchor-3D-GS and Our-3D-GS accurately reconstruct fine details, such as the crane in scale-1 and the building surface in scale-4 (see highlighted patches and arrows), while Our-3D-GS uses fewer primitives to model the entire scene. We report PSNR and the number of Gaussians used for rendering.

the first stage, totaling 69 minutes). In contrast, under the same number of iterations, our proposed method requires less time. Our-Scaffold-GS achieves the construction and optimization of the LOD structure in a single stage, taking only 35 minutes. The reason our method can accelerate training time is twofold: the number of Gaussian primitives is relatively smaller, and not all Gaussians need to be optimized during progressive training.

3) Robustness Analysis:

a) Multi-Scale Results: To evaluate the ability of Octree-GS to handle multi-scale scene details, we conduct an experiment using the BungeeNeRF [51] dataset across four different scales (i.e., from ground-level to satellite-level camera altitudes). Our results show that Octree-GS accurately captures scene details and models the entire scene more efficiently with fewer Gaussian primitives, as demonstrated in Tab. IV and Fig. 11.

b) Multi-Resolution Results: As mentioned in Sec. IV, when dealing with training views that vary in camera resolution or intrinsics, such as datasets presented in [50] with a fourfold downsampling operation, we multiply the observation distance with factor scale factor accordingly to handle this multi-resolution dataset. As shown in Fig. 10 and Tab. VI, we train all models on images with downsampling scales of 1, 2, 4, 8, and Octree-GS adaptively handle the changed footprint size and effectively address the aliasing issues inherent to 3D-GS [5] and Scaffold-GS [3]. As resolution changes, 3D-GS and Scaffold-GS introduce noticeable erosion artifacts, but our approach avoids such issues, achieving results competitive with Mip-Splatting [14] and even closer to the ground truth. Additionally, we provide multi-resolution results for the Tanks&Temples dataset [60] and the Deep Blending dataset [61] in the supplementary materials.

c) Random Initialization Results: To illustrate the independence of our framework from SfM points, we evaluate it using randomly initialized points, with 0.31/0.27 (LPIPS↓), 25.93/26.41 (PSNR↑), 0.76/0.77 (SSIM↑) on Mip-NeRF360 [50] dataset comparing Scaffold-GS with Our-Scaffold-GS. The improvement primarily depends on the efficient densification strategy.

d) Appearance Embedding Results: We demonstrate that our specialized design can handle input images with different exposure compensations and provide detailed control over lighting and appearance. As shown in Fig. 12, we reconstruct

<!-- page 12 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

12

![Image block](images/ren2024_octree-gs_p12_b3.png)

Fig. 12: Visualization of appearance code interpolation. We show five test views from the Phototourism [67] dataset (top) and a self-captured tree scene (bottom) with linearlyinterpolated appearance codes.

two scenes: one is from the widely-used Phototourism [66] dataset and the other is a self-captured scene of a ginkgo tree. We present five images rendered from a fixed camera view, where we interpolate the appearance codes linearly to produce a fancy style transfer effect.

## C. Ablation Studies

In this section, we ablate each individual module to validate their effectiveness. We select all scenes from the Mip-NeRF360 [50] dataset as quantitative comparison, given its representative characteristics. Additionally, we select Block Small from the MatrixCity [1] dataset for qualitative comparison. In this section, we ablate each individual module to verify their effectiveness. Meanwhile, we choose the octreeversion of Scaffold-GS as the full model, with the vanilla Scaffold-GS serving as the baseline for comparison. Quantitative and qualitative results can be found in Tab. VII and Fig. 13.

1) Next Level Grow Operator: To evaluate the effectiveness of next-level anchor growing, as detailed in Section IV-B, we conduct an ablation in which new anchors are only allowed to grow at the same LOD level. The results, presented in Tab. VII, show that while the number of rendered Gaussian primitives and storage requirements decreased, there was a significant decline in image visual quality. This suggests that incorporating finer anchors into higher LOD levels not only improves the capture of high-frequency details but also enhances the interaction between adjacent LOD levels.

2) LOD Bias: To validate its contribution to margin details, we ablate the proposed LOD bias. The results, presented in Tab. VII, indicates that LOD bias is essential for enhancing the rendering quality, particularly in regions rich in high-frequency details for smooth trajectories, which can be observed in column (a)(b) of Fig. 13, as the white stripes on the black buildings become continuous and complete.

3) Progressive Training: To compare its influence on LOD level overlapping, we ablate progressive training strategy. In column (a)(c) of Fig. 13, the building windows are clearly noticeable, indicating that the strategy contributes to reduce the rendered Gaussian redundancy and decouple the Gaussias of different scales in the scene to their corresponding LOD levels. In addition, the quantitative results also verify the improvement of scene reconstruction accuracy by the proposed strategy, as shown in Tab. VII.

TABLE VII: Quantitative results on ablation studies. We list the rendering metrics for each ablation described in Sec. V-C.

| Method | PSNR(↑) | SSIM(↑) | LPIPS(↓) | #GS(k)/Mem |
| --- | --- | --- | --- | --- |
| Scaffold-GS [3] | 27.90 | 0.815 | 0.220 | 666/197.5M |
| Ours w/o l<sub>next</sub> grow. | 27.64 | 0.811 | 0.223 | 594/99.7M |
| Ours w/o progressive. | 27.86 | 0.818 | 0.215 | 698/142.3M |
| Ours w/o LOD bias | 27.85 | 0.818 | 0.214 | 667/146.8M |
| Ours w/o view freq. | 27.74 | 0.817 | 0.211 | 765/244.4M |
| Our-Scaffold-GS | 28.05 | 0.819 | 0.214 | 657/139.6M |

![Image block](images/ren2024_octree-gs_p12_b13.png)

Fig. 13: Visualizations of the rendered images from (a) our full model, (b) ours w/o LOD bias, (c) ours w/o progressive training. As observed, LOD bias aids in restoring sharp building edges and lines, while progressive training helps recover the geometric structure from coarse to fine details.

4) View Frequency: Due to the design of the octree structure, anchors at higher LOD levels are only rendered and optimized when the camera view is close to them. These anchors are often not sufficiently optimized due to their limited number, leading to visual artifacts when rendering from novel views. We perform an ablation of the view frequency strategy during the anchor pruning stage, as described detailly in Sec. IV-B2. Implementing this strategy eliminates floaters, particularly in close-up views, enhances visual quality, and significantly reduces storage requirements, as shown in Tab. VII and Fig. 4.

## VI. LIMITATIONS AND CONCLUSION

In this work, we introduce Level-of-Details (LOD) to Gaussian representation, using a novel octree structure to organize anchors hierarchically. Our model, Octree-GS, addresses pre-vious limitations by dynamically fetching appropriate LOD levels based on observed views and scene complexity, ensuring consistent rendering performance with adaptive LOD adjustments. Through careful design, Octree-GS significantly enhances detail capture while maintaining real-time rendering performance without increasing the number of Gaussian primitives. This suggests potential for future real-world streaming experiences, demonstrating the capability of advanced rendering methods to deliver seamless, high-quality interactive 3D scene and content.

However, certain model components, like octree construction and progressive training, still require hyperparameter tuning. Balancing anchors in each LOD level and adjusting training iteration activation are also crucial. Moreover, our model still faces challenges associated with 3D-GS, including dependency on the precise camera poses and lack of geometry support. These are left as our future works.

<!-- page 13 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

13

## VII. SUPPLEMENTARY MATERIAL

The supplementary material includes quantitative results for each scene from the dataset used in the main text, covering image quality metrics such as PSNR, [64] and LPIPS [65], as well as the number of rendered Gaussian primitives and storage size.

TABLE VIII: PSNR for all scenes in the Mip-NeRF360 [50] dataset.

| Method\|Scenes | bicycle | bonsai | counter | flowers | garden | kitchen | room | stump | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2D-GS [15] | 24.77 | 31.42 | 28.20 | 21.02 | 26.73 | 30.66 | 30.95 | 26.17 | 22.48 |
| 3D-GS [5] | 25.10 | 32.19 | 29.22 | 21.57 | 27.45 | 31.62 | 31.53 | 26.70 | 22.46 |
| Mip-Splatting [14] | 25.13 | 32.56 | 29.30 | 21.64 | 27.43 | 31.48 | 31.73 | 26.65 | 22.60 |
| Scaffold-GS [3] | 25.19 | 33.22 | 29.99 | 21.40 | 27.48 | 31.77 | 32.30 | 26.67 | 23.08 |
| Anchor-2D-GS | 24.81 | 31.01 | 28.44 | 21.25 | 26.65 | 30.35 | 31.08 | 26.52 | 22.72 |
| Anchor-3D-GS | 25.21 | 32.20 | 29.12 | 21.52 | 27.37 | 31.46 | 31.83 | 26.74 | 22.85 |
| Our-2D-GS | 24.89 | 30.85 | 28.56 | 21.19 | 26.88 | 30.22 | 31.17 | 26.62 | 22.78 |
| Our-3D-GS | 25.20 | 32.29 | 29.27 | 21.40 | 27.36 | 31.70 | 31.96 | 26.78 | 22.85 |
| Our-Scaffold-GS | 25.24 | 33.76 | 30.19 | 21.46 | 27.67 | 31.84 | 32.51 | 26.63 | 23.13 |

TABLE IX: SSIM for all scenes in the Mip-NeRF360 [50] dataset.

| Method\|Scenes | bicycle | bonsai | counter | flowers | garden | kitchen | room | stump | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2D-GS [15] | 0.730 | 0.935 | 0.899 | 0.568 | 0.839 | 0.923 | 0.916 | 0.759 | 0.627 |
| 3D-GS [5] | 0.747 | 0.947 | 0.917 | 0.600 | 0.861 | 0.932 | 0.926 | 0.773 | 0.636 |
| Mip-Splatting [14] | 0.747 | 0.948 | 0.917 | 0.601 | 0.861 | 0.933 | 0.928 | 0.772 | 0.639 |
| Scaffold-GS [3] | 0.751 | 0.952 | 0.922 | 0.587 | 0.853 | 0.931 | 0.932 | 0.767 | 0.644 |
| Anchor-2D-GS | 0.735 | 0.933 | 0.900 | 0.575 | 0.838 | 0.917 | 0.917 | 0.762 | 0.630 |
| Anchor-3D-GS | 0.758 | 0.946 | 0.913 | 0.591 | 0.857 | 0.928 | 0.927 | 0.772 | 0.640 |
| Our-2D-GS | 0.737 | 0.932 | 0.903 | 0.572 | 0.838 | 0.918 | 0.919 | 0.763 | 0.630 |
| Our-3D-GS | 0.761 | 0.946 | 0.916 | 0.587 | 0.855 | 0.931 | 0.929 | 0.772 | 0.640 |
| Our-Scaffold-GS | 0.755 | 0.955 | 0.925 | 0.595 | 0.861 | 0.933 | 0.936 | 0.766 | 0.641 |

TABLE X: LPIPS for all scenes in the Mip-NeRF360 [50] dataset.

| Method\|Scenes | bicycle | bonsai | counter | flowers | garden | kitchen | room | stump | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2D-GS [15] | 0.284 | 0.204 | 0.214 | 0.389 | 0.153 | 0.134 | 0.218 | 0.279 | 0.385 |
| 3D-GS [5] | 0.243 | 0.178 | 0.179 | 0.345 | 0.114 | 0.117 | 0.196 | 0.231 | 0.335 |
| Mip-Splatting [14] | 0.245 | 0.178 | 0.179 | 0.347 | 0.115 | 0.115 | 0.192 | 0.232 | 0.334 |
| Scaffold-GS [3] | 0.247 | 0.173 | 0.177 | 0.359 | 0.13 | 0.118 | 0.183 | 0.252 | 0.338 |
| Anchor-2D-GS | 0.262 | 0.200 | 0.203 | 0.376 | 0.146 | 0.140 | 0.209 | 0.261 | 0.371 |
| Anchor-3D-GS | 0.230 | 0.177 | 0.182 | 0.363 | 0.121 | 0.121 | 0.193 | 0.249 | 0.348 |
| Our-2D-GS | 0.262 | 0.205 | 0.198 | 0.378 | 0.148 | 0.140 | 0.205 | 0.264 | 0.374 |
| Our-3D-GS | 0.225 | 0.178 | 0.176 | 0.364 | 0.125 | 0.116 | 0.190 | 0.250 | 0.357 |
| Our-Scaffold-GS | 0.235 | 0.164 | 0.169 | 0.347 | 0.116 | 0.115 | 0.172 | 0.250 | 0.360 |

TABLE XI: Number of Gaussian Primitives(#K) for all scenes in the Mip-NeRF360 [50] dataset.

<table><tr><td>Method|Scenes</td><td colspan="2">bicycle bonsai</td><td colspan="2">counter flowers</td><td colspan="2">garden kitchen</td><td colspan="2">room stump</td><td>treehill</td></tr><tr><td>2D-GS [15]</td><td>555</td><td>210</td><td>232</td><td>390</td><td>749</td><td>440</td><td>199</td><td>413</td><td>383</td></tr><tr><td>3D-GS [5]</td><td>1453</td><td>402</td><td>530</td><td>907</td><td>2030</td><td>1034</td><td>358</td><td>932</td><td>785</td></tr><tr><td>Mip-Splatting [14]</td><td>1584</td><td>430</td><td>545</td><td>950</td><td>2089</td><td>1142</td><td>405</td><td>1077</td><td>892</td></tr><tr><td>Scaffold-GS [3]</td><td>764</td><td>532</td><td>377</td><td>656</td><td>1121</td><td>905</td><td>272</td><td>637</td><td>731</td></tr><tr><td>Anchor-2D-GS</td><td>887</td><td>337</td><td>353</td><td>548</td><td>938</td><td>466</td><td>270</td><td>587</td><td>540</td></tr><tr><td>Anchor-3D-GS</td><td>1187</td><td>370</td><td>388</td><td>634</td><td>1524</td><td>535</td><td>293</td><td>647</td><td>781</td></tr><tr><td>Our-2D-GS</td><td>540</td><td>259</td><td>294</td><td>428</td><td>718</td><td>414</td><td>184</td><td>394</td><td>344</td></tr><tr><td>Our-3D-GS</td><td>659</td><td>301</td><td>334</td><td>478</td><td>987</td><td>710</td><td>195</td><td>436</td><td>433</td></tr><tr><td>Our-Scaffold-GS</td><td>653</td><td>631</td><td>409</td><td>675</td><td>1475</td><td>777</td><td>374</td><td>549</td><td>372</td></tr></table>

TABLE XII: Storage memory(#MB) for all scenes in the Mip-NeRF360 [50] dataset.

| Method\|Scenes | bicycle | bonsai | counter | flowers | garden | kitchen | room | stump | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2D-GS [15] | 889.6 | 173.1 | 135.4 | 493.5 | 603.1 | 191.0 | 180.0 | 670.3 | 630.9 |
| 3D-GS [5] | 1361.8 | 293.5 | 293.3 | 878.5 | 1490.6 | 413.1 | 355.6 | 1115.2 | 878.6 |
| Mip-Splatting [14] | 1433.6 | 318.1 | 307.5 | 970.2 | 1448.9 | 463.4 | 401.0 | 1239.0 | 964.3 |
| Scaffold-GS [3] | 340.2 | 133.3 | 90.4 | 243.8 | 231.7 | 102.2 | 86.1 | 294.2 | 256.0 |
| Anchor-2D-GS | 599.2 | 280.0 | 191.5 | 530.0 | 634.4 | 190.7 | 228.4 | 359.1 | 521.4 |
| Anchor-3D-GS | 765.5 | 301.7 | 204.9 | 656.1 | 988.6 | 217.0 | 244.6 | 417.4 | 632.2 |
| Our-2D-GS | 485.0 | 368.6 | 265.6 | 442.3 | 598.6 | 272.3 | 180.8 | 292.8 | 438.3 |
| Our-3D-GS | 648.6 | 382.7 | 305.8 | 487.7 | 706.2 | 282.9 | 162.7 | 322.1 | 468.4 |
| Our-Scaffold-GS | 216.0 | 133.5 | 83.2 | 198.3 | 236.3 | 88.7 | 83.5 | 141.9 | 104.4 |

TABLE XIII: Quantitative results for all scenes in the Tanks&Temples [60] dataset.

<table><tr><td rowspan="2">DatasetMethod\Metrics</td><td colspan="4">Truck</td><td colspan="4">Train</td></tr><tr><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>#GS(k)/Mem</td><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>#GS(k)/Mem</td></tr><tr><td>2D-GS [15]</td><td>25.12</td><td>0.870</td><td>0.173</td><td>393/287.2M</td><td>21.38</td><td>0.790</td><td>0.251</td><td>310/121.5M</td></tr><tr><td>3D-GS [5]</td><td>25.52</td><td>0.884</td><td>0.142</td><td>876/610.8M</td><td>22.30</td><td>0.819</td><td>0.201</td><td>653/249.3M</td></tr><tr><td>Mip-Splatting [14]</td><td>25.74</td><td>0.888</td><td>0.142</td><td>967/718.9M</td><td>22.17</td><td>0.824</td><td>0.199</td><td>696/281.9M</td></tr><tr><td>Scaffold-GS [3]</td><td>26.04</td><td>0.889</td><td>0.131</td><td>698/214.6M</td><td>22.91</td><td>0.838</td><td>0.181</td><td>554/120.4M</td></tr><tr><td>Anchor-2D-GS</td><td>25.45</td><td>0.873</td><td>0.161</td><td>472/349.7M</td><td>21.58</td><td>0.797</td><td>0.237</td><td>457/208.3M</td></tr><tr><td>Anchor-3D-GS</td><td>25.85</td><td>0.883</td><td>0.146</td><td>603/452.8M</td><td>22.18</td><td>0.810</td><td>0.222</td><td>541/245.6M</td></tr><tr><td>Our-2D-GS</td><td>25.32</td><td>0.872</td><td>0.158</td><td>304/208.5M</td><td>21.92</td><td>0.812</td><td>0.215</td><td>355/173.9M</td></tr><tr><td>Our-3D-GS</td><td>25.81</td><td>0.887</td><td>0.131</td><td>407/542.8M</td><td>22.52</td><td>0.828</td><td>0.190</td><td>440/224.90M</td></tr><tr><td>Our-Scaffold-GS</td><td>26.24</td><td>0.894</td><td>0.122</td><td>426/93.7M</td><td>23.11</td><td>0.838</td><td>0.184</td><td>460/83.4M</td></tr></table>

TABLE XIV: Quantitative results for all scenes in the Deep-Blending [61] dataset.

<table><tr><td rowspan="2">DatasetMethod\Metrics</td><td colspan="4">Dr Johnson</td><td colspan="4">Playroom</td></tr><tr><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>#GS(k)/Mem</td><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>#GS(k)/Mem</td></tr><tr><td>2D-GS [15]</td><td>28.74</td><td>0.897</td><td>0.257</td><td>232/393.8M</td><td>29.89</td><td>0.900</td><td>0.257</td><td>160/276.7M</td></tr><tr><td>3D-GS [5]</td><td>29.09</td><td>0.900</td><td>0.242</td><td>472/818.9M</td><td>29.83</td><td>0.905</td><td>0.241</td><td>324/592.3M</td></tr><tr><td>Mip-Splatting [14]</td><td>29.08</td><td>0.900</td><td>0.241</td><td>512/911.6M</td><td>30.03</td><td>0.902</td><td>0.245</td><td>307/562.0M</td></tr><tr><td>Scaffold-GS [3]</td><td>29.73</td><td>0.910</td><td>0.235</td><td>232/145.0M</td><td>30.83</td><td>0.907</td><td>0.242</td><td>182/106.0M</td></tr><tr><td>Anchor-2D-GS</td><td>28.68</td><td>0.893</td><td>0.266</td><td>186/346.3M</td><td>30.02</td><td>0.899</td><td>0.262</td><td>138/231.8M</td></tr><tr><td>Anchor-3D-GS</td><td>29.23</td><td>0.897</td><td>0.267</td><td>141/242.3M</td><td>30.08</td><td>0.901</td><td>0.252</td><td>159/303.4M</td></tr><tr><td>Our-2D-GS</td><td>28.94</td><td>0.894</td><td>0.26</td><td>97/268.2M</td><td>29.93</td><td>0.899</td><td>0.268</td><td>70/136.4M</td></tr><tr><td>Our-3D-GS</td><td>29.27</td><td>0.900</td><td>0.251</td><td>95/240.7M</td><td>30.03</td><td>0.901</td><td>0.263</td><td>63/119.2M</td></tr><tr><td>Our-Scaffold-GS</td><td>29.83</td><td>0.909</td><td>0.237</td><td>124/92.46M</td><td>31.15</td><td>0.914</td><td>0.245</td><td>100/50.91M</td></tr></table>

TABLE XV: PSNR for all scenes in the BungeeNeRF [51] dataset.

| Method\|Scenes | Amsterdam | Barcelona | Bilbao | Chicago | Hollywood | Pompidou | Quebec | Rome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2D-GS [15] | 27.22 | 27.01 | 28.59 | 25.62 | 26.43 | 26.62 | 28.38 | 26.95 |
| 3D-GS [5] | 27.75 | 27.55 | 28.91 | 28.27 | 26.25 | 27.16 | 28.86 | 27.56 |
| Mip-Splatting [14] | 28.16 | 27.72 | 29.13 | 28.28 | 26.59 | 27.71 | 29.23 | 28.33 |
| Scaffold-GS [3] | 27.82 | 28.09 | 29.20 | 28.55 | 26.36 | 27.72 | 29.29 | 28.24 |
| Anchor-2D-GS | 26.80 | 27.03 | 28.02 | 27.50 | 25.68 | 26.87 | 28.21 | 27.32 |
| Anchor-3D-GS | 27.70 | 27.93 | 28.92 | 28.20 | 26.20 | 27.17 | 28.83 | 28.22 |
| Our-2D-GS | 27.14 | 27.28 | 28.24 | 27.78 | 26.13 | 26.58 | 28.07 | 27.47 |
| Our-3D-GS | 27.95 | 27.91 | 28.81 | 28.24 | 26.51 | 27.00 | 28.98 | 28.09 |
| Our-Scaffold-GS | 28.16 | 28.40 | 29.39 | 28.86 | 26.76 | 27.46 | 29.46 | 28.59 |

TABLE XVI: SSIM for all scenes in the BungeeNeRF [51] dataset.

| Method\|Scenes | Amsterdam | Barcelona | Bilbao | Chicago | Hollywood | Pompidou | Quebec | Rome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2D-GS [15] | 0.896 | 0.907 | 0.912 | 0.901 | 0.872 | 0.907 | 0.923 | 0.902 |
| 3D-GS [5] | 0.918 | 0.919 | 0.918 | 0.932 | 0.873 | 0.919 | 0.937 | 0.918 |
| Mip-Splatting [14] | 0.918 | 0.919 | 0.918 | 0.930 | 0.876 | 0.923 | 0.938 | 0.922 |
| Scaffold-GS [3] | 0.914 | 0.923 | 0.918 | 0.929 | 0.866 | 0.926 | 0.939 | 0.924 |
| Anchor-2D-GS | 0.872 | 0.887 | 0.886 | 0.897 | 0.838 | 0.900 | 0.910 | 0.891 |
| Anchor-3D-GS | 0.902 | 0.912 | 0.907 | 0.916 | 0.871 | 0.919 | 0.930 | 0.915 |
| Our-2D-GS | 0.887 | 0.894 | 0.892 | 0.912 | 0.857 | 0.893 | 0.911 | 0.895 |
| Our-3D-GS | 0.912 | 0.910 | 0.905 | 0.920 | 0.875 | 0.907 | 0.928 | 0.912 |
| Our-Scaffold-GS | 0.922 | 0.928 | 0.921 | 0.934 | 0.884 | 0.923 | 0.942 | 0.930 |

<!-- page 14 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

14

TABLE XVII: LPIPS for all scenes in the BungeeNeRF [51] dataset.

| Method\|Scenes | Amsterdam | Barcelona | Bilbao | Chicago | Hollywood | Pompidou | Quebec | Rome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2D-GS [15] | 0.132 | 0.101 | 0.109 | 0.13 | 0.152 | 0.109 | 0.113 | 0.123 |
| 3D-GS [5] | 0.092 | 0.082 | 0.092 | 0.080 | 0.128 | 0.090 | 0.087 | 0.096 |
| Mip-Splatting [14] | 0.094 | 0.082 | 0.095 | 0.081 | 0.130 | 0.087 | 0.087 | 0.093 |
| Scaffold-GS [3] | 0.102 | 0.078 | 0.090 | 0.08 | 0.157 | 0.082 | 0.080 | 0.087 |
| Anchor-2D-GS | 0.156 | 0.125 | 0.137 | 0.125 | 0.196 | 0.119 | 0.127 | 0.131 |
| Anchor-3D-GS | 0.127 | 0.099 | 0.119 | 0.105 | 0.160 | 0.100 | 0.100 | 0.105 |
| Our-2D-GS | 0.139 | 0.112 | 0.131 | 0.103 | 0.169 | 0.126 | 0.125 | 0.128 |
| Our-3D-GS | 0.105 | 0.094 | 0.115 | 0.095 | 0.146 | 0.113 | 0.100 | 0.108 |
| Our-Scaffold-GS | 0.090 | 0.071 | 0.091 | 0.077 | 0.128 | 0.089 | 0.081 | 0.080 |

TABLE XVIII: Number of Gaussian Primitives(#K) for all scenes in the BungeeNeRF [51] dataset.

| Method\|Scenes | Amsterdam | Barcelona | Bilbao | Chicago | Hollywood | Pompidou | Quebec | Rome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2D-GS [15] | 1026 | 1251 | 968 | 1008 | 1125 | 1526 | 811 | 914 |
| 3D-GS [5] | 2358 | 3106 | 2190 | 2794 | 2812 | 3594 | 2176 | 2459 |
| Mip-Splatting [14] | 2325 | 2874 | 2072 | 2712 | 2578 | 3233 | 1969 | 2251 |
| Scaffold-GS [3] | 1219 | 1687 | 1122 | 1958 | 1117 | 2600 | 1630 | 1886 |
| Anchor-2D-GS | 1222 | 1050 | 1054 | 1168 | 706 | 1266 | 881 | 1050 |
| Anchor-3D-GS | 1842 | 1630 | 1393 | 1593 | 1061 | 1995 | 1368 | 1641 |
| Our-2D-GS | 703 | 771 | 629 | 631 | 680 | 786 | 582 | 629 |
| Our-3D-GS | 1094 | 1090 | 760 | 830 | 975 | 1120 | 816 | 932 |
| Our-Scaffold-GS | 1508 | 1666 | 1296 | 1284 | 1478 | 1584 | 1354 | 1622 |

TABLE XIX: Storage memory(#MB) for all scenes in the BungeeNeRF [51] dataset.

| Method Scenes | Amsterdam | Barcelona | Bilbao | Chicago | Hollywood | Pompidou | Quebec Rome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2D-GS [15] | 809.6 | 1027.7 | 952.2 | 633.2 | 814.3 | 1503.4 | 643.2 705.5 |
| 3D-GS [5] | 1569.1 | 2191.9 | 1446.1 | 1630.2 | 1758.3 | 2357.6 | 1573.7 1811.8 |
| Mip-Splatting [14] | 1464.3 | 1935.4 | 1341.4 | 1536.0 | 1607.7 | 2037.8 | 1382.4 1577.0 |
| Scaffold-GS [3] | 236.2 | 378.8 | 219.0 | 306.1 | 208.3 | 478.5 | 340.2 386.6 |
| Anchor-2D-GS | 559.6 | 564.5 | 520.3 | 567.9 | 411.6 | 629.1 | 479.5 537.9 |
| Anchor-3D-GS | 866.4 | 862.8 | 699.4 | 778.5 | 607.9 | 979.3 | 725.3 802.5 |
| Our-2D-GS | 449.8 | 1014.4 | 425.9 | 1127.8 | 776.2 | 765.52 | 498.8 830.2 |
| Our-3D-GS | 1213.5 | 1414.3 | 892.4 | 1268.5 | 960.5 | 949.8 | 618.5 1048.3 |
| Our-Scaffold-GS | 273.8 | 355.9 | 246.5 | 286.8 | 259.0 | 339.6 | 258.8 353.4 |

TABLE XX: PSNR for multi-resolution Mip-NeRF360 [50] scenes (1× resolution).

| Method\|Scenes | bicycle | bonsai | counter | flowers | garden | kitchen | room | stump | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 23.66 | 29.89 | 27.98 | 20.42 | 25.45 | 29.55 | 30.51 | 25.48 | 22.50 |
| Mip-Splatting [14] | 25.19 | 31.76 | 29.07 | 21.68 | 26.82 | 31.27 | 31.60 | 26.71 | 22.74 |
| Scaffold-GS [3] | 23.64 | 31.31 | 28.82 | 20.87 | 26.04 | 30.39 | 31.36 | 25.66 | 23.14 |
| Our-Scaffold-GS | 24.21 | 33.44 | 30.15 | 20.89 | 27.01 | 31.83 | 32.39 | 25.92 | 23.26 |

TABLE XXI: SSIM for multi-resolution Mip-NeRF360 [50] scenes (1× resolution).

| Method\|Scenes | bicycle | bonsai | counter | flowers | garden | kitchen | room | stump | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 0.648 | 0.917 | 0.883 | 0.510 | 0.752 | 0.902 | 0.905 | 0.707 | 0.587 |
| Mip-Splatting [14] | 0.730 | 0.939 | 0.904 | 0.586 | 0.817 | 0.924 | 0.919 | 0.764 | 0.622 |
| Scaffold-GS [3] | 0.640 | 0.932 | 0.895 | 0.521 | 0.772 | 0.910 | 0.916 | 0.709 | 0.605 |
| Our-Scaffold-GS | 0.676 | 0.952 | 0.919 | 0.541 | 0.823 | 0.930 | 0.932 | 0.722 | 0.628 |

TABLE XXII: LPIPS for multi-resolution Mip-NeRF360 [50] scenes (1× resolution).

| Method\|Scenes | bicycle | bonsai | counter | flowers | garden | kitchen | room | stump | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 0.359 | 0.223 | 0.235 | 0.443 | 0.269 | 0.167 | 0.242 | 0.331 | 0.440 |
| Mip-Splatting [14] | 0.275 | 0.188 | 0.196 | 0.367 | 0.190 | 0.130 | 0.214 | 0.258 | 0.379 |
| Scaffold-GS [3] | 0.355 | 0.208 | 0.219 | 0.430 | 0.242 | 0.159 | 0.219 | 0.326 | 0.407 |
| Our-Scaffold-GS | 0.313 | 0.169 | 0.178 | 0.401 | 0.168 | 0.119 | 0.186 | 0.309 | 0.364 |

TABLE XXIII: PSNR for multi-resolution Mip-NeRF360 [50] scenes (2× resolution).

| Method\|Scenes | bicycle | garden | stump | room | counter | kitchen | bonsai | flowers | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 25.41 | 27.56 | 26.42 | 31.29 | 28.57 | 30.54 | 30.71 | 21.83 | 23.67 |
| Mip-Splatting [14] | 26.83 | 28.80 | 27.57 | 32.44 | 29.59 | 32.27 | 32.41 | 23.22 | 23.90 |
| Scaffold-GS [3] | 25.43 | 28.37 | 26.60 | 32.36 | 29.52 | 31.50 | 32.20 | 22.36 | 24.51 |
| Our-Scaffold-GS | 25.92 | 29.08 | 26.81 | 33.31 | 30.77 | 32.44 | 34.13 | 22.38 | 24.53 |

TABLE XXIV: SSIM for multi-resolution Mip-NeRF360 [50] scenes (2× resolution).

| Method\|Scenes | bicycle | garden | stump | room | counter | kitchen | bonsai | flowers | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 0.756 | 0.866 | 0.769 | 0.933 | 0.904 | 0.935 | 0.939 | 0.620 | 0.676 |
| Mip-Splatting [14] | 0.823 | 0.902 | 0.819 | 0.946 | 0.923 | 0.950 | 0.956 | 0.693 | 0.705 |
| Scaffold-GS [3] | 0.759 | 0.883 | 0.773 | 0.946 | 0.918 | 0.941 | 0.953 | 0.640 | 0.701 |
| Our-Scaffold-GS | 0.785 | 0.903 | 0.781 | 0.956 | 0.937 | 0.949 | 0.966 | 0.657 | 0.714 |

TABLE XXV: LPIPS for multi-resolution Mip-NeRF360 [50] scenes (2× resolution).

| Method\|Scenes | bicycle | garden | stump | room | counter | kitchen | bonsai | flowers | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 0.261 | 0.138 | 0.239 | 0.134 | 0.141 | 0.093 | 0.114 | 0.351 | 0.349 |
| Mip-Splatting [14] | 0.177 | 0.084 | 0.170 | 0.110 | 0.110 | 0.067 | 0.088 | 0.276 | 0.284 |
| Scaffold-GS [3] | 0.245 | 0.110 | 0.234 | 0.108 | 0.125 | 0.086 | 0.099 | 0.335 | 0.307 |
| Our-Scaffold-GS | 0.210 | 0.080 | 0.221 | 0.087 | 0.095 | 0.068 | 0.071 | 0.304 | 0.274 |

TABLE XXVI: PSNR for multi-resolution Mip-NeRF360 [50] scenes (4× resolution).

| Method\|Scenes | bicycle | garden | stump | room | counter | kitchen | bonsai | flowers | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 27.06 | 29.19 | 27.77 | 31.75 | 29.29 | 31.51 | 31.25 | 24.04 | 25.12 |
| Mip-Splatting [14] | 28.66 | 30.69 | 29.12 | 33.29 | 30.44 | 33.40 | 33.25 | 25.66 | 25.53 |
| Scaffold-GS [3] | 27.34 | 30.40 | 28.11 | 33.03 | 30.42 | 32.55 | 32.83 | 24.72 | 26.31 |
| Our-Scaffold-GS | 28.00 | 31.23 | 28.36 | 34.01 | 31.60 | 33.39 | 34.86 | 24.66 | 26.27 |

TABLE XXVII: SSIM for multi-resolution Mip-NeRF360 [50] scenes (4× resolution).

| Method\|Scenes | bicycle | garden | stump | room | counter | kitchen | bonsai | flowers | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 0.857 | 0.921 | 0.841 | 0.954 | 0.929 | 0.958 | 0.953 | 0.753 | 0.788 |
| Mip-Splatting [14] | 0.901 | 0.945 | 0.882 | 0.965 | 0.943 | 0.967 | 0.968 | 0.807 | 0.811 |
| Scaffold-GS [3] | 0.868 | 0.936 | 0.852 | 0.966 | 0.942 | 0.963 | 0.966 | 0.776 | 0.815 |
| Our-Scaffold-GS | 0.883 | 0.945 | 0.857 | 0.971 | 0.952 | 0.966 | 0.975 | 0.782 | 0.822 |

TABLE XXVIII: LPIPS for multi-resolution Mip-NeRF360 [50] scenes (4× resolution).

| Method\|Scenes | bicycle | garden | stump | room | counter | kitchen | bonsai | flowers | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 0.140 | 0.062 | 0.149 | 0.066 | 0.081 | 0.045 | 0.059 | 0.227 | 0.220 |
| Mip-Splatting [14] | 0.085 | 0.040 | 0.102 | 0.050 | 0.063 | 0.038 | 0.043 | 0.177 | 0.183 |
| Scaffold-GS [3] | 0.118 | 0.048 | 0.138 | 0.047 | 0.069 | 0.039 | 0.045 | 0.204 | 0.185 |
| Our-Scaffold-GS | 0.101 | 0.039 | 0.131 | 0.039 | 0.054 | 0.036 | 0.032 | 0.182 | 0.168 |

TABLE XXIX: PSNR for multi-resolution Mip-NeRF360 [50] scenes (8× resolution).

| Method\|Scenes | bicycle | garden | stump | room | counter | kitchen | bonsai | flowers | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 26.26 | 29.28 | 27.50 | 30.45 | 28.14 | 29.86 | 29.25 | 24.33 | 25.62 |
| Mip-Splatting [14] | 29.80 | 31.93 | 30.78 | 33.60 | 31.11 | 33.74 | 33.38 | 27.95 | 27.13 |
| Scaffold-GS [3] | 27.29 | 30.26 | 28.61 | 31.51 | 29.67 | 30.84 | 30.61 | 24.99 | 27.04 |
| Our-Scaffold-GS | 29.09 | 32.61 | 29.05 | 34.24 | 32.35 | 34.35 | 35.42 | 25.83 | 27.69 |

<!-- page 15 of 16 -->

<table><tr><td rowspan="2" colspan="2">PSNRMethod | Scales</td><td colspan="4">Dr Johnson</td><td colspan="4">Playroom</td></tr><tr><td>1×</td><td>2×</td><td>4×</td><td>8×</td><td>1×</td><td>2×</td><td>4×</td><td>8×</td></tr><tr><td colspan="2">3D-GS [5]</td><td>28.62</td><td>28.97</td><td>29.23</td><td>28.71</td><td>29.43</td><td>29.89</td><td>30.25</td><td>29.47</td></tr><tr><td colspan="2">Mip-Splatting [14]</td><td>28.95</td><td>29.30</td><td>29.91</td><td>30.55</td><td>30.18</td><td>30.62</td><td>31.16</td><td>31.61</td></tr><tr><td colspan="2">Scaffold-GS [3]</td><td>29.51</td><td>29.99</td><td>30.58</td><td>30.31</td><td>29.77</td><td>30.39</td><td>31.10</td><td>30.47</td></tr><tr><td colspan="2">Our-Scaffold-GS</td><td>29.75</td><td>30.14</td><td>30.58</td><td>30.92</td><td>30.87</td><td>31.42</td><td>31.76</td><td>31.63</td></tr><tr><td colspan="10"></td></tr><tr><td rowspan="2" colspan="2">SSIMMethod | Scales</td><td colspan="4">Dr Johnson</td><td colspan="4">Playroom</td></tr><tr><td>1×</td><td>2×</td><td>4×</td><td>8×</td><td>1×</td><td>2×</td><td>4×</td><td>8×</td></tr><tr><td colspan="2">3D-GS [5]</td><td>0.890</td><td>0.900</td><td>0.911</td><td>0.907</td><td>0.898</td><td>0.919</td><td>0.935</td><td>0.934</td></tr><tr><td colspan="2">Mip-Splatting [14]</td><td>0.900</td><td>0.911</td><td>0.925</td><td>0.936</td><td>0.909</td><td>0.929</td><td>0.946</td><td>0.956</td></tr><tr><td colspan="2">Scaffold-GS [3]</td><td>0.900</td><td>0.914</td><td>0.930</td><td>0.932</td><td>0.900</td><td>0.923</td><td>0.944</td><td>0.949</td></tr><tr><td colspan="2">Our-Scaffold-GS</td><td>0.908</td><td>0.920</td><td>0.932</td><td>0.940</td><td>0.911</td><td>0.933</td><td>0.949</td><td>0.957</td></tr><tr><td colspan="10"></td></tr><tr><td rowspan="2" colspan="2">LPIPSMethod | Scales</td><td colspan="4">Dr Johnson</td><td colspan="4">Playroom</td></tr><tr><td>1×</td><td>2×</td><td>4×</td><td>8×</td><td>1×</td><td>2×</td><td>4×</td><td>8×</td></tr><tr><td colspan="2">3D-GS [5]</td><td>0.277</td><td>0.177</td><td>0.103</td><td>0.083</td><td>0.277</td><td>0.170</td><td>0.081</td><td>0.060</td></tr><tr><td colspan="2">Mip-Splatting [14]</td><td>0.251</td><td>0.151</td><td>0.084</td><td>0.060</td><td>0.247</td><td>0.140</td><td>0.061</td><td>0.039</td></tr><tr><td colspan="2">Scaffold-GS [3]</td><td>0.244</td><td>0.144</td><td>0.078</td><td>0.057</td><td>0.257</td><td>0.150</td><td>0.064</td><td>0.038</td></tr><tr><td colspan="2">Our-Scaffold-GS</td><td>0.263</td><td>0.159</td><td>0.082</td><td>0.061</td><td>0.274</td><td>0.164</td><td>0.068</td><td>0.041</td></tr></table>

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

15

TABLE XXX: SSIM for multi-resolution Mip-NeRF360 [50] scenes (8× resolution).

| Method\|Scenes | bicycle | garden | stump | room | counter | kitchen | bonsai | flowers | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 0.871 | 0.930 | 0.846 | 0.953 | 0.928 | 0.954 | 0.944 | 0.805 | 0.840 |
| Mip-Splatting [14] | 0.938 | 0.964 | 0.925 | 0.973 | 0.957 | 0.975 | 0.973 | 0.883 | 0.886 |
| Scaffold-GS [3] | 0.894 | 0.941 | 0.875 | 0.965 | 0.946 | 0.961 | 0.959 | 0.825 | 0.871 |
| Our-Scaffold-GS | 0.919 | 0.964 | 0.885 | 0.978 | 0.964 | 0.977 | 0.981 | 0.838 | 0.885 |

TABLE XXXI: LPIPS for multi-resolution Mip-NeRF360 [50] scenes (8× resolution).

| Method\|Scenes | bicycle | garden | stump | room | counter | kitchen | bonsai | flowers | treehill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-GS [5] | 0.098 | 0.047 | 0.126 | 0.048 | 0.063 | 0.037 | 0.047 | 0.159 | 0.147 |
| Mip-Splatting [14] | 0.049 | 0.026 | 0.068 | 0.031 | 0.041 | 0.029 | 0.029 | 0.109 | 0.113 |
| Scaffold-GS [3] | 0.082 | 0.040 | 0.110 | 0.033 | 0.048 | 0.032 | 0.035 | 0.144 | 0.120 |
| Our-Scaffold-GS | 0.062 | 0.025 | 0.103 | 0.023 | 0.032 | 0.021 | 0.017 | 0.118 | 0.106 |

TABLE XXXII: Quantitative results for multi-resolution Tanks&Temples [60] dataset.

<table><tr><td rowspan="2" colspan="2">PSNRMethod | Scales</td><td colspan="4">Train</td><td colspan="4">Truck</td></tr><tr><td>1×</td><td>2×</td><td>4×</td><td>8×</td><td>1×</td><td>2×</td><td>4×</td><td>8×</td></tr><tr><td colspan="2">3D-GS [5]</td><td>21.23</td><td>22.17</td><td>22.69</td><td>22.16</td><td>23.92</td><td>25.47</td><td>26.24</td><td>25.51</td></tr><tr><td colspan="2">Mip-Splatting [14]</td><td>21.87</td><td>22.70</td><td>23.41</td><td>23.83</td><td>25.29</td><td>26.79</td><td>28.07</td><td>28.81</td></tr><tr><td colspan="2">Scaffold-GS [3]</td><td>21.91</td><td>23.04</td><td>23.84</td><td>23.50</td><td>24.66</td><td>26.47</td><td>27.44</td><td>26.67</td></tr><tr><td colspan="2">Our-Scaffold-GS</td><td>22.49</td><td>23.50</td><td>24.18</td><td>24.22</td><td>25.85</td><td>27.53</td><td>28.83</td><td>29.67</td></tr><tr><td colspan="10"></td></tr><tr><td rowspan="2" colspan="2">SSIMMethod | Scales</td><td colspan="4">Train</td><td colspan="4">Truck</td></tr><tr><td>1×</td><td>2×</td><td>4×</td><td>8×</td><td>1×</td><td>2×</td><td>4×</td><td>8×</td></tr><tr><td colspan="2">3D-GS [5]</td><td>0.754</td><td>0.830</td><td>0.879</td><td>0.880</td><td>0.827</td><td>0.899</td><td>0.930</td><td>0.929</td></tr><tr><td colspan="2">Mip-Splatting [14]</td><td>0.791</td><td>0.859</td><td>0.906</td><td>0.929</td><td>0.868</td><td>0.925</td><td>0.955</td><td>0.969</td></tr><tr><td colspan="2">Scaffold-GS [3]</td><td>0.781</td><td>0.860</td><td>0.907</td><td>0.913</td><td>0.844</td><td>0.916</td><td>0.946</td><td>0.945</td></tr><tr><td colspan="2">Our-Scaffold-GS</td><td>0.817</td><td>0.882</td><td>0.919</td><td>0.932</td><td>0.878</td><td>0.932</td><td>0.958</td><td>0.971</td></tr><tr><td colspan="10"></td></tr><tr><td rowspan="2" colspan="2">LPIPSMethod | Scales</td><td colspan="4">Train</td><td colspan="4">Truck</td></tr><tr><td>1×</td><td>2×</td><td>4×</td><td>8×</td><td>1×</td><td>2×</td><td>4×</td><td>8×</td></tr><tr><td colspan="2">3D-GS [5]</td><td>0.292</td><td>0.181</td><td>0.106</td><td>0.093</td><td>0.239</td><td>0.116</td><td>0.058</td><td>0.050</td></tr><tr><td colspan="2">Mip-Splatting [14]</td><td>0.243</td><td>0.143</td><td>0.080</td><td>0.056</td><td>0.179</td><td>0.082</td><td>0.039</td><td>0.025</td></tr><tr><td colspan="2">Scaffold-GS [3]</td><td>0.261</td><td>0.149</td><td>0.080</td><td>0.070</td><td>0.216</td><td>0.094</td><td>0.045</td><td>0.041</td></tr><tr><td colspan="2">Our-Scaffold-GS</td><td>0.216</td><td>0.119</td><td>0.068</td><td>0.055</td><td>0.154</td><td>0.066</td><td>0.033</td><td>0.023</td></tr></table>

TABLE XXXIII: Quantitative results for multi-resolution Deep Blending [61] dataset.

REFERENCES

[1] Y. Li, L. Jiang, L. Xu, Y. Xiangli, Z. Wang, D. Lin, and B. Dai, “Matrixcity: A large-scale city dataset for city-scale neural rendering and beyond,” in Proceedings of the IEEE/CVF International Conference on Computer Vision, 2023, pp. 3205–3215.

[2] B. Kerbl, A. Meuleman, G. Kopanas, M. Wimmer, A. Lanvin, and G. Drettakis, “A hierarchical 3d gaussian representation for real-time rendering of very large datasets,” ACM Transactions on Graphics (TOG), vol. 43, no. 4, pp. 1–15, 2024.

[3] T. Lu, M. Yu, L. Xu, Y. Xiangli, L. Wang, D. Lin, and B. Dai, “Scaffoldgs: Structured 3d gaussians for view-adaptive rendering,” arXiv preprint arXiv:2312.00109, 2023.

[4] B. Mildenhall, P. P. Srinivasan, M. Tancik, J. T. Barron, R. Ramamoorthi, and R. Ng, “Nerf: Representing scenes as neural radiance fields for view synthesis,” Communications of the ACM, vol. 65, no. 1, pp. 99–106, 2021.

[5] B. Kerbl, G. Kopanas, T. Leimkuhler, and G. Drettakis, “3d gaussian ¨ splatting for real-time radiance field rendering,” ACM Transactions on Graphics, vol. 42, no. 4, 2023.

[6] W. Zielonka, T. Bagautdinov, S. Saito, M. Zollhofer, J. Thies, ¨ and J. Romero, “Drivable 3d gaussian avatars,” arXiv preprint arXiv:2311.08581, 2023.

[7] S. Saito, G. Schwartz, T. Simon, J. Li, and G. Nam, “Relightable gaussian codec avatars,” arXiv preprint arXiv:2312.03704, 2023.

[8] S. Zheng, B. Zhou, R. Shao, B. Liu, S. Zhang, L. Nie, and Y. Liu, “Gps-gaussian: Generalizable pixel-wise 3d gaussian splatting for realtime human novel view synthesis,” arXiv preprint arXiv:2312.02155, 2023.

[9] S. Qian, T. Kirschstein, L. Schoneveld, D. Davoli, S. Giebenhain, and M. Nießner, “Gaussianavatars: Photorealistic head avatars with rigged 3d gaussians,” arXiv preprint arXiv:2312.02069, 2023.

[10] Y. Yan, H. Lin, C. Zhou, W. Wang, H. Sun, K. Zhan, X. Lang, X. Zhou, and S. Peng, “Street gaussians for modeling dynamic urban scenes,” arXiv preprint arXiv:2401.01339, 2024.

[11] X. Zhou, Z. Lin, X. Shan, Y. Wang, D. Sun, and M.-H. Yang, “Drivinggaussian: Composite gaussian splatting for surrounding dynamic autonomous driving scenes,” arXiv preprint arXiv:2312.07920, 2023.

[12] Y. Jiang, C. Yu, T. Xie, X. Li, Y. Feng, H. Wang, M. Li, H. Lau, F. Gao, Y. Yang et al., “Vr-gs: A physical dynamics-aware interactive gaussian splatting system in virtual reality,” arXiv preprint arXiv:2401.16663, 2024.

[13] T. Xie, Z. Zong, Y. Qiu, X. Li, Y. Feng, Y. Yang, and C. Jiang, “Physgaussian: Physics-integrated 3d gaussians for generative dynamics,” arXiv preprint arXiv:2311.12198, 2023.

[14] Z. Yu, A. Chen, B. Huang, T. Sattler, and A. Geiger, “Mip-splatting: Alias-free 3d gaussian splatting,” arXiv preprint arXiv:2311.16493, 2023.

[15] B. Huang, Z. Yu, A. Chen, A. Geiger, and S. Gao, “2d gaussian splatting for geometrically accurate radiance fields,” in ACM SIGGRAPH 2024 Conference Papers, 2024, pp. 1–11.

[16] L. Xu, V. Agrawal, W. Laney, T. Garcia, A. Bansal, C. Kim, S. Rota Bulo, L. Porzi, P. Kontschieder, A. Bo \` ziˇ č et al., “Vr-nerf: High-fidelity virtualized walkable spaces,” in SIGGRAPH Asia 2023 Conference Papers, 2023, pp. 1–12.

[17] A. Yu, R. Li, M. Tancik, H. Li, R. Ng, and A. Kanazawa, “Plenoctrees for real-time rendering of neural radiance fields,” in Proceedings of the IEEE/CVF International Conference on Computer Vision, 2021, pp. 5752–5761.

[18] J. N. Martel, D. B. Lindell, C. Z. Lin, E. R. Chan, M. Monteiro, and G. Wetzstein, “Acorn: Adaptive coordinate networks for neural scene representation,” arXiv preprint arXiv:2105.02788, 2021.

[19] Y. Liu, H. Guan, C. Luo, L. Fan, J. Peng, and Z. Zhang, “Citygaussian: Real-time high-quality large-scale scene rendering with gaussians,” arXiv preprint arXiv:2404.01133, 2024.

[20] L. Liu, J. Gu, K. Zaw Lin, T.-S. Chua, and C. Theobalt, “Neural sparse voxel fields,” Advances in Neural Information Processing Systems, vol. 33, pp. 15 651–15 663, 2020.

[21] S. Fridovich-Keil, A. Yu, M. Tancik, Q. Chen, B. Recht, and A. Kanazawa, “Plenoxels: Radiance fields without neural networks,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 5501–5510.

[22] C. Sun, M. Sun, and H.-T. Chen, “Direct voxel grid optimization: Superfast convergence for radiance fields reconstruction,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 5459–5469.

<!-- page 16 of 16 -->

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE

16

[23] A. Chen, Z. Xu, A. Geiger, J. Yu, and H. Su, “Tensorf: Tensorial radiance fields,” in European Conference on Computer Vision. Springer, 2022, pp. 333–350.

[24] T. Muller, A. Evans, C. Schied, and A. Keller, “Instant neural graphics ¨ primitives with a multiresolution hash encoding,” ACM Transactions on Graphics (ToG), vol. 41, no. 4, pp. 1–15, 2022.

[25] L. Xu, Y. Xiangli, S. Peng, X. Pan, N. Zhao, C. Theobalt, B. Dai, and D. Lin, “Grid-guided neural radiance fields for large urban scenes,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2023, pp. 8296–8306.

[26] Y. Xiangli, L. Xu, X. Pan, N. Zhao, B. Dai, and D. Lin, “Assetfield: Assets mining and reconfiguration in ground feature plane representation,” arXiv preprint arXiv:2303.13953, 2023.

[27] H. Turki, M. Zollhofer, C. Richardt, and D. Ramanan, “Pynerf: Pyrami- ¨ dal neural radiance fields,” Advances in Neural Information Processing Systems, vol. 36, 2024.

[28] Z. Li, T. Muller, A. Evans, R. H. Taylor, M. Unberath, M.-Y. Liu, and ¨ C.-H. Lin, “Neuralangelo: High-fidelity neural surface reconstruction,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2023, pp. 8456–8465.

[29] C. Reiser, S. Garbin, P. P. Srinivasan, D. Verbin, R. Szeliski, B. Mildenhall, J. T. Barron, P. Hedman, and A. Geiger, “Binary opacity grids: Capturing fine geometric detail for mesh-based view synthesis,” arXiv preprint arXiv:2402.12377, 2024.

[30] J. T. Barron, B. Mildenhall, D. Verbin, P. P. Srinivasan, and P. Hedman, “Zip-nerf: Anti-aliased grid-based neural radiance fields,” arXiv preprint arXiv:2304.06706, 2023.

[31] J. Tang, J. Ren, H. Zhou, Z. Liu, and G. Zeng, “Dreamgaussian: Generative gaussian splatting for efficient 3d content creation,” arXiv preprint arXiv:2309.16653, 2023.

[32] Y. Liang, X. Yang, J. Lin, H. Li, X. Xu, and Y. Chen, “Luciddreamer: Towards high-fidelity text-to-3d generation via interval score matching,” arXiv preprint arXiv:2311.11284, 2023.

[33] J. Tang, Z. Chen, X. Chen, T. Wang, G. Zeng, and Z. Liu, “Lgm: Large multi-view gaussian model for high-resolution 3d content creation,” arXiv preprint arXiv:2402.05054, 2024.

[34] Y. Feng, X. Feng, Y. Shang, Y. Jiang, C. Yu, Z. Zong, T. Shao, H. Wu, K. Zhou, C. Jiang et al., “Gaussian splashing: Dynamic fluid synthesis with gaussian splatting,” arXiv preprint arXiv:2401.15318, 2024.

[35] J. Luiten, G. Kopanas, B. Leibe, and D. Ramanan, “Dynamic 3d gaussians: Tracking by persistent dynamic view synthesis,” arXiv preprint arXiv:2308.09713, 2023.

[36] Z. Yang, X. Gao, W. Zhou, S. Jiao, Y. Zhang, and X. Jin, “Deformable 3d gaussians for high-fidelity monocular dynamic scene reconstruction,” arXiv preprint arXiv:2309.13101, 2023.

[37] Y.-H. Huang, Y.-T. Sun, Z. Yang, X. Lyu, Y.-P. Cao, and X. Qi, “Sc-gs: Sparse-controlled gaussian splatting for editable dynamic scenes,” arXiv preprint arXiv:2312.14937, 2023.

[38] V. Yugay, Y. Li, T. Gevers, and M. R. Oswald, “Gaussian-slam: Photo-realistic dense slam with gaussian splatting,” arXiv preprint arXiv:2312.10070, 2023.

[39] N. Keetha, J. Karhade, K. M. Jatavallabhula, G. Yang, S. Scherer, D. Ramanan, and J. Luiten, “Splatam: Splat, track & map 3d gaussians for dense rgb-d slam,” arXiv preprint arXiv:2312.02126, 2023.

[40] Q. Xu, Z. Xu, J. Philip, S. Bi, Z. Shu, K. Sunkavalli, and U. Neumann, “Point-nerf: Point-based neural radiance fields,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 5438–5448.

[41] S. Fridovich-Keil, G. Meanti, F. R. Warburg, B. Recht, and A. Kanazawa, “K-planes: Explicit radiance fields in space, time, and appearance,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2023, pp. 12 479–12 488.

[42] A. Cao and J. Johnson, “Hexplane: A fast representation for dynamic scenes,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2023, pp. 130–141.

[43] S. M. Rubin and T. Whitted, “A 3-dimensional representation for fast rendering of complex scenes,” in Proceedings of the 7th annual conference on Computer graphics and interactive techniques, 1980, pp. 110–116.

[44] S. Laine and T. Karras, “Efficient sparse voxel octrees–analysis, extensions, and implementation,” NVIDIA Corporation, vol. 2, no. 6, 2010.

[45] H. Bai, Y. Lin, Y. Chen, and L. Wang, “Dynamic plenoctree for adaptive sampling refinement in explicit nerf,” in Proceedings of the IEEE/CVF International Conference on Computer Vision, 2023, pp. 8785–8795.

[46] Y. Verdie, F. Lafarge, and P. Alliez, “LOD Generation for Urban Scenes,” ACM Trans. on Graphics, vol. 34, no. 3, 2015.

[47] H. Fang, F. Lafarge, and M. Desbrun, “Planar Shape Detection at Structural Scales,” in Proc. of the IEEE conference on Computer Vision and Pattern Recognition (CVPR), Salt Lake City, US, 2018.

[48] M. Yu and F. Lafarge, “Finding Good Configurations of Planar Primitives in Unorganized Point Clouds,” in Proc. of the IEEE conference on Computer Vision and Pattern Recognition (CVPR), New Orleans, US, 2022.

[49] J. T. Barron, B. Mildenhall, M. Tancik, P. Hedman, R. Martin-Brualla, and P. P. Srinivasan, “Mip-nerf: A multiscale representation for anti-aliasing neural radiance fields,” in Proceedings of the IEEE/CVF International Conference on Computer Vision, 2021, pp. 5855–5864.

[50] J. T. Barron, B. Mildenhall, D. Verbin, P. P. Srinivasan, and P. Hedman, “Mip-nerf 360: Unbounded anti-aliased neural radiance fields,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 5470–5479.

[51] Y. Xiangli, L. Xu, X. Pan, N. Zhao, A. Rao, C. Theobalt, B. Dai, and D. Lin, “Bungeenerf: Progressive neural radiance field for extreme multi-scale scene rendering,” in European conference on computer vision. Springer, 2022, pp. 106–122.

[52] J. Cui, J. Cao, Y. Zhong, L. Wang, F. Zhao, P. Wang, Y. Chen, Z. He, L. Xu, Y. Shi et al., “Letsgo: Large-scale garage modeling and rendering via lidar-assisted gaussian primitives,” arXiv preprint arXiv:2404.09748, 2024.

[53] M. Zwicker, H. Pfister, J. Van Baar, and M. Gross, “Ewa volume splatting,” in Proceedings Visualization, 2001. VIS’01. IEEE, 2001, pp. 29–538.

[54] J. L. Schonberger and J.-M. Frahm, “Structure-from-motion revisited,” in Proceedings of the IEEE conference on computer vision and pattern recognition, 2016, pp. 4104–4113.

[55] H. Hoppe, “Progressive meshes,” in Seminal Graphics Papers: Pushing the Boundaries, Volume 2, 2023, pp. 111–120.

[56] K. Park, U. Sinha, J. T. Barron, S. Bouaziz, D. B. Goldman, S. M. Seitz, and R. Martin-Brualla, “Nerfies: Deformable neural radiance fields,” in Proceedings of the IEEE/CVF International Conference on Computer Vision, 2021, pp. 5865–5874.

[57] R. Martin-Brualla, N. Radwan, M. S. Sajjadi, J. T. Barron, A. Dosovitskiy, and D. Duckworth, “Nerf in the wild: Neural radiance fields for unconstrained photo collections,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2021, pp. 7210–7219.

[58] M. Tancik, V. Casser, X. Yan, S. Pradhan, B. Mildenhall, P. P. Srinivasan, J. T. Barron, and H. Kretzschmar, “Block-nerf: Scalable large scene neural view synthesis,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 8248–8258.

[59] P. Bojanowski, A. Joulin, D. Lopez-Paz, and A. Szlam, “Optimizing the latent space of generative networks,” arXiv preprint arXiv:1707.05776, 2017.

[60] A. Knapitsch, J. Park, Q.-Y. Zhou, and V. Koltun, “Tanks and temples: Benchmarking large-scale scene reconstruction,” ACM Transactions on Graphics (ToG), vol. 36, no. 4, pp. 1–13, 2017.

[61] P. Hedman, J. Philip, T. Price, J.-M. Frahm, G. Drettakis, and G. Brostow, “Deep blending for free-viewpoint image-based rendering,” ACM Transactions on Graphics (ToG), vol. 37, no. 6, pp. 1–15, 2018.

[62] H. Turki, D. Ramanan, and M. Satyanarayanan, “Mega-nerf: Scalable construction of large-scale nerfs for virtual fly-throughs,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 12 922–12 931.

[63] L. Lin, Y. Liu, Y. Hu, X. Yan, K. Xie, and H. Huang, “Capturing, reconstructing, and simulating: the urbanscene3d dataset,” in European Conference on Computer Vision. Springer, 2022, pp. 93–109.

[64] Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli, “Image quality assessment: from error visibility to structural similarity,” IEEE transactions on image processing, vol. 13, no. 4, pp. 600–612, 2004.

[65] R. Zhang, P. Isola, A. A. Efros, E. Shechtman, and O. Wang, “The unreasonable effectiveness of deep features as a perceptual metric,” in Proceedings of the IEEE conference on computer vision and pattern recognition, 2018, pp. 586–595.

[66] N. Snavely, S. M. Seitz, and R. Szeliski, “Photo tourism: exploring photo collections in 3d,” in ACM siggraph 2006 papers, 2006, pp. 835–846.

[67] Y. Jin, D. Mishkin, A. Mishchuk, J. Matas, P. Fua, K. M. Yi, and E. Trulls, “Image matching across wide baselines: From paper to practice,” International Journal of Computer Vision, vol. 129, no. 2, pp. 517–547, 2021.