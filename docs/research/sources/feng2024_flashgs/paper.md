<!-- page 1 of 14 -->

![Image block](images/feng2024_flashgs_p1_b1.png)

arXiv:2408.07967v2 [cs.CV] 19 Aug 2024

# FlashGS: Efficient 3D Gaussian Splatting for Large-scale and High-resolution Rendering

Guofeng Feng<sup>†</sup>, Siyan Chen†, Rong Fu<sup>∗</sup>, Zimu Liao, Yi Wang, Tao Liu, Zhilin Pei, Hengjie Li, Xingcheng Zhang, Bo Dai

Shanghai AI Laboratory

## Abstract

This work introduces FlashGS, an open-source CUDA Python library <sup>1</sup> designed to facilitate the efficient differentiable rasterization of 3D Gaussian Splatting through algorithmic and kernel-level optimizations. FlashGS is developed based on the observations from a comprehensive analysis of rendering process to enhance computational efficiency and bring the technique to wide adoption. The paper includes a suite of optimization strategies, encompassing redundancy elimination, efficient pipelining, refined control and scheduling mecha nisms, and memory access optimizations, all of which are meticulously integrated to amplify the performance of the rasterization process. An extensive evaluation of FlashGS performance has been conducted across a diverse spectrum of synthetic and real-world large-scale scenes, encompassing a variety of image resolutions. The empirical findings demonstrate that FlashGS consistently achieves an average 4x acceleration over mobile consumer GPUs, coupled with reduced memory consumption. These results underscore the superior performance and resource optimization capabilities of FlashGS, positioning it as a formidable tool in the domain of 3D rendering.

Keywords: 3D Gaussian Splatting, CUDA optimization, Largescale real-time rendering

## 1 Introduction

Neural Radiance Fields (NeRF) [19] have become popular for producing realistic image renderings, but the process of sampling numerous points per ray for pixel rendering hinders real-time capabilities. Recently, a new representation method known as 3D Gaussian Splatting (3DGS) [13] has come to the forefront as a viable alternative. This technique has demonstrated the ability to attain real-time rendering speeds. The emergence of 3DGS has opened up a realm of possibilities, allowing for real-time exploration of indoor environments. This has far-reaching implications across various practical applications, including immersive free-viewpoint navigation,

virtual property tours, and interactive virtual-reality gaming experiences.

Figure 1. Two representative rendering output images with 3D Gaussian Splatting [13] and our FlashGS.

Despite 3DGS’s advantages, real-time rendering of largescale or high-resolution areas on city-scale scenes [16] or high quality scenes recorded by consumer GPS receivers [4] is still hindered by limited computational and memory resources. This is due to the increase in the number of Gaussians and the size of each Gaussian as the image scale and resolution increase.

Existing works widely employ well-established compression or pruning methods to avoid storing or computing excessive Gaussians [7, 9, 18]. However, these methods have not yielded significant performance improvements. A recent work, GScore [15], attempts to analyze the original 3DGS algorithm but primarily addresses limitations on mobile GPUs by designing a novel domain-specific hardware.

To address the shortcomings of current works, we’ve analyzed the 3DGS rendering process on a single consumergrade GPU, identifying rendering performance bottlenecks, such as the rough intersection testing between Gaussians and tiles during preprocessing, and the massive redundant computations in volume rendering. We further conduct a detailed performance profiling and extract several key factors hindering performance: 1) Some Gaussian-tile pairs generated during preprocessing stage are not used in the actual rendering process. 2) There are severe compute and memory

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>1</sup>Available at [https://github.com/InternLandMark/FlashGS.](https://github.com/InternLandMark/FlashGS)</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>\*</sup>Corresponding Author (e-mail: furong@pjlab.org.cn).</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">†The first two authors contribute equally to this work, and this work was done when they were interns at Shanghai AI Lab.</span></small>

Conference’17, July 2017, Washington, DC, USA 2024.

1

<!-- page 2 of 14 -->

access bottlenecks at different stages of the entire rasterization algorithm.

Based on our in-depth observations, we propose FlashGS, a novel 3DGS rendering algorithm with efficient system-level optimizations. Specifically, we first introduce a new design of rasterization workflow, constructing a more efficient rendering pipeline. For the implementation of this new rendering process, we firstly perform geometric and algebraic simplifications to alleviate high computational costs. We propose new runtime scheduling strategies to utilize the hardware, including the load balance and divergence elimination between threads, and a two-step prefetching execution pipeline to overlap computation and memory access operations. We also optimize memory management to better leverage the GPU memory hierarchy. Additionally, we further improve the performance by directly applying assembly-level optimizations. Compared to 3DGS [13], GScore [15] and gsplat [28], FlashGS achieves up to 4× speedup and 49% memory reduction, while keeping the same high quality metric peak signal-to-noise ratio (PSNR).

To the best of our knowledge, this is the first work to indepth analyze, delicately re-design, and efficiently implement 3DGS-based volume rendering on a single consumer GPU. We make it possible to achieve efficient rendering for largescale and high-resolution scenes with low overhead. Our main contributions are as follows:

• We conduct an in-depth study of the original 3DGS algorithm and the current state-of-the-art research. We identify main challenges in large-scale and highresolution scenes and pinpoint the fundamental problems of performance bottlenecks.

• We propose a new algorithm, FlashGS, which includes a precise redundancy elimination algorithm and an efficient rendering execution workflow.

• We systematically implement FlashGS on GPU with holistic optimizations, including computation, memory management, and scheduling.

• We test FlashGS on representative datesets, demonstrating that it significantly improves rendering speed while maintaining high image quality and low memory usage.

## 2 Background and Related Work

We briefly overview the novel-view synthesis and some existing methods, particularly the radiance field methods. Then, we introduce the current state-of-the-art, 3D Gaussian Splatting (3DGS). Finally, we briefly report some recent improvements in 3DGS.

## 2.1 Novel View Synthesis

Novel view synthesis is an important method in 3D reconstruction. It generates new images from new viewpoints (target poses) based on a set of input images of a 3D scene

from certain viewpoints (source poses). Before reconstruction, some representations are proposed to construct the 3D scene. Traditional methods use point clouds, voxels, or meshes to describe the spatial structure. However, these traditional explicit and discrete representations can lead to information loss and thus result in an incomplete representation of the scene.

Neural Radiance Fields (NeRF) [19] is a widely adopted attractive representation method, leveraging deep learning techniques. It implicitly models 3D scenes using multi-layer perceptrons (MLPs), and this continuous function achieves a fine representation of the scene. Some subsequent works focus on improving the quality of synthesized images through optimizing the models. Mip-NeRF [1] is a multiscale model that casts cones and encodes the positions and sizes of frustum to address the aliasing issues of NeRF. Some methods [5, 23, 26] leveraging depth supervision of point clouds to make the model converge faster. The substantial computation required by the MLP in NeRF results in slow training and rendering processes, which has inspired plenty of works on efficient training and inference. A common technique is storing the precompute training results to simplified data structures, such as sparse voxel grid [11] and octrees [12, 22, 29]. Other works propose or integrate new features with MLPs to enable faster training or inference, such as features in a voxel grid [17, 24]. A notable work greatly accelerates NeRF, Instant-NGP [20], introduces a multi-resolution hash encoding grid, and simultaneously trains it with optimized MLPs.

## 2.2 3D Gaussian Splatting

3D Gaussian Splatting (3DGS) [13] models the scene with a set of Gaussian ellipsoids, allowing fast rendering through rasterizing these Gaussians into high quality images. Figure 2 illustrate the 3DGS mechanism. The rasterizer can be coarsely divided into 3 steps: preprocessing (preprocess-CUDA and DuplicateWithKeys), sorting and rendering.

The preprocessing step in the original implementation contains two main operations. To begin with, 𝑃 3D Gaussians after frustum culling are projected into the image plane as 2D Gaussians with mean $\pmb { \mu } ^ { \prime } \in \mathbb { R } ^ { 2 }$ and anisotropic covariance $\boldsymbol { \Sigma } ^ { \prime } \in \mathbb { R } ^ { 2 \times 2 }$ . Then the preprocessing pipeline assigns an ellipse with its axis-aligned bounding box (AABB) to each corresponding 2D Gaussian. 3DGS uses AABB to get the intersected tiles with the ellipse, and for an AABB assigned by a certain Gaussian, the duplicateWithKeys operation traverses all tiles overlapping the AABB and organizes every tile with the Gaussian as key-value pairs. The keys are composed by the tile indexes and the depths of Gaussians, the values are the Gaussian indexes. The sorting process sorts 𝑁 key-value pairs by depth for the front-to-back rendering, using the RadixSort in Nvidia CUB library. The final rendering precess obtains the pixel color taking the time complexity of 𝑂(𝑁) (the workload is divided into tiles) and each pixel color is computed considering the opacity 𝛼 and transmittance.

2

<!-- page 3 of 14 -->

![Image block](images/feng2024_flashgs_p3_b1.png)

Figure 2. 3DGS Overview

## 2.3 Improvement of 3DGS

Although 3DGS has achieved a significant leap in 3D reconstruction, there remains considerable room for improvement. Some work has further improved image quality (photorealistic) by enhancing the sampling process of 3DGS, to eliminate blur and artifacts. Yan et al. [27] analyze the aliasing effect in 3DGS rendering and introduce a multi-scale 3D Gaussians representation to render different levels of detail of the scene, by improving the sampling frequency. Zhang et al. [30] propose FreGS, a novel framework leveraging regularization to perform coarse-to-fine high-quality Gaussian densification, to alleviate the over-construction problem. These aspects are not the focus of this paper, readers can find more details in some surveys [2, 8, 25].

In some high-resolution, large-scale scenes, 3DGS can generate millions of or even more (huge) Gaussians, putting immense pressure on memory units. This has inspired some works focusing on optimizing memory usage, which can be categorized into two main types: 1) Leveraging widely used techniques in model compression, like pruning and encoding. Scaffold-GS [18] leverages the underlying scene geometry which uses anchor points growing and pruning strategies to effectively reduce redundant Gaussians, without loss of quality when rendering. EAGLES [9] applies vector quantization (VQ) to quantize per-point attributes to compress the 3D Gaussian point clouds. LightGaussian [7] further introduces data distillation to reduce the degree of spherical harmonics coefficients and proposes a VQ strategy by the global significance of Gaussians. 2) Introducing multi-GPU parallelism to avoid the memory constraints of a single GPU. Grendel [31] is a scalable (up to 32 GPUs) distributed 3DGS

training system, splitting 3DGS parameters across multiple GPUs and using sparse communication and dynamic load balance mechanisms. Chen et al. [3] proposed DoGaussian, which decomposes a scene into K blocks and applies Alternating Direction Methods of Multipliers (ADMM) to train 3DGS distributedly.

However, only a handful of papers focus on the design and implementation of the original 3DGS algorithm itself and try to efficiently support critical operators in the computation process. This forms the direct motivation for our work. gsplat [28] is a CUDA-accelerated differentiable rasterization library for 3DGS, achieving faster and more memory efficient rendering. Durvasula et al. [6] perform a performance characterization on the rasterization-based differential rendering, including 3DGS, and introduce a novel primitive using warplevel reduction to accelerate costly atomic operations during the gradient computation. GScore [15] is a specific hardware acceleration unit to efficiently support the rendering pipeline over the mobile GPU along with some algorithmic co-design, based on an analysis of Gaussian-based rendering.

## 3 Observation and Motivation

We conduct a detailed analysis of the 3D Gaussian Splatting rendering process. First, we obtain the critical steps in the rendering process by profiling the runtime breakdown. Based on it, we identify several significant performance issues, which inspired our optimization design. As shown in the Figure 3, we test 3D Gaussian Splatting on A100 and V100 GPUs with a representative large-scale dataset, Matrix-City [28]. From top to bottom it shows the time proportion of key operators in the rendering process. The rendering

3

<!-- page 4 of 14 -->

![Chart block](images/feng2024_flashgs_p4_b1.png)

Figure 3. Runtime breakdown of 3GDS rasterization on the MatrixCity[16] dataset.

(renderCUDA) is the primary performance bottleneck, accounting for about 60% of the total time. Gaussian sorting (SortPairs) and the preceding generation of the unsorted key-value list (DuplicateWithKeys) take up nearly 20% of the time. Preprocessing time is within 10%, but it also should not be overlooked. Given that these steps are not independent, we conduct a comprehensive study of them.

## 3.1 Observation 1: Excessive redundant computations hinder efficient rendering.

![Chart block](images/feng2024_flashgs_p4_b5.png)

Figure 4. We evaluate the key-value pairs binning process from the rendering process of 6 frames in the scene trained from MatrixCity[16] dataset. The number of assigned k-v pairs is much more than the number of tiles really covered by the AABB or the projected ellipse.

We observe that there are several computational redundancies in the rasterizing pipeline. Figure 4 shows that only a small proportion of the key-value pairs contribute to the result of rendering. Namely, the preprocessing kernels as signed unnecessary tiles without overlapping the projected

![Image block](images/feng2024_flashgs_p4_b8.png)

Figure 5. Geometry Redundancies. There are 3 kinds of redundancies in original 3DGS intersection algorithm: I. The definition of ellipse ignores the opacity. II. The AABB is overestimated. III. The tiles out of the ellipse are binned with the Gaussian.

ellipse to the Gaussian, creating redundant key values and inefficiencies in the sorting and rendering process. There are three main factors contribute to the redundancies as Figure 5 shows. We find that the redundancy I & II in Figure 5 results in that the assigned AABB covers more tiles of the real AABB as Figure 4 shows. The redundancy III results in the difference between the number of tiles covered by the AABB and the projected ellipse.

![Image block](images/feng2024_flashgs_p4_b11.png)

Figure 6. Opacity distribution in the smallcity scene of MatrixCity dataset. The horizontal axis below the bar shows percentage ranging from 0% to 100%. These percentages correspond to the opacity values from 0 to 1 shown above the bar.

The opacity of Gaussians is ignored when defining the ellipse. The original implementation adopts the threesigma rule of thumb that data points with an absolute difference from more than 3𝜎 are extremely rare and define the

4

<!-- page 5 of 14 -->

boundary of an ellipse using $3 \Sigma ^ { \prime } ,$ . Considering the opacity can scale down the size of the ellipse, reducing the area of the AABB and the number of key-value pairs. When opacity is sufficiently low, the overestimation problem is more significant. As shown in Figure 6, most Gaussian opacities in the smallcity scene of the MatrixCity dataset are quite low ( 65.1% Gaussians have the center opacity less than 0.35), further proving the importance of considering opacity when defining the ellipse.

The defined AABB of the ellipse covers more tiles than the real one. The preprocessCUDA operation defines the assigned AABB as the bounding box of the circle whose radius is the semi-major axis of the projected ellipse. The AABB is larger than the real AABB of the ellipse, especially for the ellipsoids with high flattening, which introduces computational redundancies for key-values binning, sorting, and rendering.

The duplicateWithKeys kernel assigns redundant tiles in the AABB to key-value pairs. All tiles in AABB are traversed and binned to key-value pairs, even if the tile utterly not covered by the ellipse, which will result in redundant computation in subsequent sorting and rendering process.

## 3.2 Observation 2: Inappropriate execution pipelines reduce hardware utilization.

We find that the main steps in 3DGS exhibit an imbalance between computation and memory access, which can put excessive pressure on the corresponding hardware units, causing computation or memory bottlenecks. The preprocess step (preprocessCUDA in Algorithm 1) kernel has a linear complexity 𝑂(𝑃), where P is the number of Gaussians. And each Gaussian is related to a large array of spherical harmonics coefficients. This results in significant pressure on cache bandwidth due to the massive read-write operations (lines 17-22 of Algorithm 1).

During the rasterization phase, 3DGS first projects Gaussian spheres on tiles to obtain the tile-gaussian pairs (DuplicateWithKeys). Its asymptotic complexity depends on the number of Gaussians and the number of tiles covered by their projection 𝑂 (𝑃 + 𝑁). As shown in Algorithm 2, in this step, aside from some bitwise operations, all the operations involve reading and writing to global memory.

During rendering, the extensive pixel-level calculations introduce computational bottlenecks, whereas the aforementioned two steps are primarily memory access operations. This results in an imbalance between computation and memory access in the entire 3DGS execution workflow, which can lead to under-utilization of GPU hardware resources.

## 4 FlashGS Design

To address the aforementioned issues, we optimize the Gaussian rendering process in two stages. First, we design a more

<div class="docvortex-algorithm" style="white-space: pre-wrap; font-family:monospace;">
Algorithm 1 preprocessCUDA
Input: $P$, $cam_{pose}$, $s$, $R$, $\sigma$, $shs$, $viewmatrix$, $projmatrix$, $o$
Output: $radii$, $x'_I, depths, \Sigma$, $c$, $conic\_opacity$, $tiles\_touched$
if $idx \geq P$ then
    return
$p\_view \leftarrow in\_frustum()$
if $!p\_view$ then
    return
$p\_proj \leftarrow project()$
$\Sigma \leftarrow computeCov3D()$
$\Sigma' \leftarrow computeCov2D()$
$\lambda_1, \lambda_2 \leftarrow eigenvalues(\Sigma')$
$radii \leftarrow \lceil 3 \times \sqrt{\max(\lambda_1, \lambda_2)} \rceil$
$x'_I \leftarrow ndc2Pix()$
$rect\_min, rect\_max \leftarrow getRect()$
if $(rect\_max.x - rect\_min.x) \times (rect\_max.y - rect\_min.y) == 0$ then
    return
$c[idx] \leftarrow computeColorFromSH()$
$depths[idx] \leftarrow p\_view.z$
$radii[idx] \leftarrow radii$
$x'_I[idx] \leftarrow point\_image$
conic\_opacity[idx] $\leftarrow (conic, opacities[idx])$
$tiles\_touched[idx] \leftarrow (rect\_max.y - rect\_min.y) \times (rect\_max.x - rect\_min.x)$
</div>

<div class="docvortex-algorithm" style="white-space: pre-wrap; font-family:monospace;">
Algorithm 2 duplicateWithKeys

Input: $P$, $\mathbf{x}_I'$, depths, offsets(Prefix sum of tile counts for each Gaussian), radii
Output: gaussian_keys_unsorted(Array for storing key-value pairs), gaussian_values_unsorted(Array for storing key-value pairs),
idx ← thread_rank()
if idx ≥ P then
    return
if radii[idx] &gt; 0 then
    off ← (idx == 0)?0 : offsets[idx - 1]
    rect_min, rect_max ← getRect()
    for y of rect_min.y to rect_max.y do
        for x of rect_min.x to rect_max.x do
            gaussian_keys_unsorted[off] ← key
            gaussian_values_unsorted[off] ← idx
            off ← off + 1
</div>

precise intersection algorithm to alleviate subsequent computational bottlenecks related to redundant Gaussian calculations, and use geometric simplifications to avoid expensive intersection computations. Additionally, we reorganized and restructured the computation process based on the characteristics of each kernel/micro kernel to prevent unbalanced workloads. As Figure 7 illustrates, the whole process can

5

<!-- page 6 of 14 -->

![Image block](images/feng2024_flashgs_p6_b1.png)

Figure 7. FlashGS Overview.

greatly benefits from the reduced number of false positive tile kv pairs in FlashGS, as well as from the optimization in algorithms and scheduling for runtime.

## 4.1 Efficient and Precise Intersection Algorithm

![Image block](images/feng2024_flashgs_p6_b5.png)

Figure 8. intersection tiles with the ellipse (purple represents the real intersection tiles, green shows the tiles each method treats as intersected, and white means not). (a) 3DGS uses AABB and gets 16 tiles. (b) GScore applies OBB and gets 8 tiles. (c) Precise intersection shows only 4 tiles.

As shown in Figure 8, the precise intersection algorithm can reduce the number of Gaussians involved in subsequent computations, thereby alleviating the computational and memory access intensity/pressure. This is crucial because for the two vital bottlenecks, sorting and rendering, their workload and the number of Gaussians to be processed are proportional.

We need to confirm the valid range of the ellipse projected by the Gaussians before performing the precise intersection

calculation. As mentioned in Section 3.1, for 3D image reconstruction, we must consider not only the effect of the general Gaussian distribution on the effective range but also the changes in opacity.

3D Gaussian Splatting applies the three-sigma rule to get the valid ellipse:

$$
r = 3 \sqrt {\lambda},\tag{1}
$$

where 𝜆 represents the semi-major axis length of the projected ellipse, which corresponds to the eigenvalue of the covariance matrix, and 𝑟 is the radius of the circle abstracted from the ellipse. Considering the statistics in Section 3.1, 65% of Gaussian centers have opacity in quite a low range ([0, 0.35], this range will be explained in the following paragraphs), which motivates us to incorporate opacity 𝛼 to obtain the effective range:

$$
\alpha = \alpha_ {0} \times \exp (- \frac {r ^ {2}}{2 \lambda}),\tag{2}
$$

where $\alpha _ { 0 }$ is the initial (central) opacity of the Gaussian. When 𝛼 decays to a certain threshold $\tau ,$ we consider this to be the boundary of the ellipse, as described in Equation 3:

$$
r = \sqrt {2 l n (\frac {\alpha_ {0}}{\tau}) \lambda},\tag{3}
$$

Given that RGB typically has 256 discrete values, typically $\begin{array} { r } { \tau \; = \; \frac { 1 } { 2 5 5 } } \end{array}$ . We can solve that when $\alpha _ { 0 } \; \leq \; 0 . 3 5$ , our method outperforms the three-sigma rule, and still use 3𝜎 conversely.

6

<!-- page 7 of 14 -->

We adopted an exact intersection algorithm to eliminate invalid Gaussians. Consider that a rough intersection algorithm can be highly inefficient for ellipses since they can be quite elongated, which potentially introduces a large amount of unnecessary computations on invalid Gaussians for tiles. Directly computing the intersection between the Gaussianprojected ellipse and the tiles on the screen is expensive. We reduce the overhead of direct intersection computation through a two-stage filtering process: (1) Use a bounding box (note: we calculate a rectangle tightly tangent to the ellipse, rather than a square tangent to the circle enclosing the ellipse as in the original algorithm) is to set a coarse-grained range. (2) For tiles within or intersecting the bounding box, check whether they intersect with the ellipse.

![Image block](images/feng2024_flashgs_p7_b2.png)

Figure 9. Geometric simplification for precise per-tile intersection. A tile is considered intersected if the segment of the ellipse intersecting the line of the tile’s edge coincides with the edge.

For each tile intersection, we use geometric equivalent transformations to avoid the cost of directly solving multi-ple quadratic equations, considering that rectangular tiles are not easily represented by simple equations. Our key observation is that the intersection between an ellipse and a rectangle can be transformed into a problem of determining whether the projection line segment of the ellipse onto the line of each edge of the rectangular overlaps with the line segment of the rectangle’s edge, as illustrated in Figure 9. If they intersect, we find the endpoints of the segment on the line that is enclosed by the ellipse. We then use these endpoints to determine whether this segment overlaps with the corresponding edge of the rectangle.

As shown in Algorithm 3, we first classify the intersection between an ellipse and a rectangle into two cases. The first case is straightforward: if the center of the ellipse is inside the rectangular, there must be an overlap. For the more complex case where the ellipse’s center is outside the rectangle, we solve for the intersection of the ellipse with each line containing the edge of the rectangle.

<div class="docvortex-algorithm" style="white-space: pre-wrap; font-family:monospace;">
Algorithm 3 Algorithm to Determine if a Rectangle Tile Needs Rendering

Input: Rectangle $R$, Ellipse $E$
Output: Boolean indicating if the tile needs rendering
if the center point of $E$ lies in $R$ then
    return true
else
    for edge $e$ of $R$ do
        $l \leftarrow$ line containing segment $e$
        if $l \cap E \neq \emptyset$ and intersection(s) lie on $e$ then
            return true
return false
</div>

## 4.2 Refined and Balanced Workflow

The workflow of 3DGS rendering is a complex process involving multiple steps as mentioned above. Moreover, different sub-components may have varying computational patterns, and these sub-computations are not entirely independent of each other. Therefore, we need to perform a systematic analysis and optimization from a more holistic perspective.

Our key idea is to balance the computational cost of each part as much as possible to avoid potential bottlenecks. Our approach behind this idea is to amortize different types of operations over the timeline to prevent a specific transaction from bursting and putting excessive pressure. We extract the computational bottlenecks and memory access bottlenecks from different operators and interweave them to form a more efficient execution workflow.

![Image block](images/feng2024_flashgs_p7_b10.png)

Figure 10. Schematic for the workflow of original 3DGS and the improved FlashGS. We balance the computation and memory access across various stages and reduce redundant operations (M\_c and M\_b are indicative of the amount of computation and memory access, respectively).

We observe that before performing rendering, there are several important operations, including the previously men tioned precise intersection, calculating and recording some Gaussian-related information, and constructing key-value pairs for sorting. In baseline, both these two functions are bandwidth-limited and involve extensive memory read and write operations. However, we observed that the subsequent rendering process is computation-bound. This is due to the unrefined method for Gaussian intersection in the baseline algorithm, which led to massive false positives. Therefore, we

7

<!-- page 8 of 14 -->

may be able to afford more computation during the preprocessing stage. This not only helps to balance the bandwidthlimited parts but also reduces the overhead for subsequent per-pixel rendering. This is one of the key motivations for adopting a precise intersection algorithm mentioned before.

In the preprocessing stage, we checked the visibility of the Gaussian and then computed and stored various pieces of information needed for subsequent steps, such as depth, Gaussian radius, and coordinates. In the original algorithm, each thread processing a Gaussian that intersects with a tile accesses global memory to read the sphere coefficients and write several Gaussian information at the end of the pre-processing. This results in significant bandwidth contention, causing the workflow to be stalled during global memory access due to implicit synchronization between the separately launched kernels. We combined our new exact intersection algorithm with DuplicateWithKeys() to precisely generate the valid Gaussian key-value pairs.

As previously mentioned, accurately computing the intersection between a tile and a projected ellipse is complex and requires solving multiple equations. Consequently, many operations during this process are compute-bound, leaving surplus bandwidth resources available. Therefore, we reorganized these two operators. By interleaving our exact intersection computations within the delays caused by extensive global memory writes, we ensure that both the GPU’s compute units and memory bandwidth are efficiently utilized throughout the execution workflow. Our approach achieves a high compute-to-memory ratio. As the result shown in Figure 10, the precise intersection operation reduces redundant Gaussians, alleviating the significant memory access overhead during the sorting stage and the additional computations during the rendering stage. In our new preprocessing stage, we can reuse some intermediate results by kernel fusion, transitioning directly from intersection to key-value pair generation, thereby reducing the number of memory read and write operations. Although the total number of computations and memory access operations of the pre-cise intersection and the merged operators may increase, we expose more scheduling opportunities to the compiler and hardware to achieve better balance and amortize over a longer timeline.

## 5 FlashGS Implementation

In this section, we efficiently implement the proposed FlashGS algorithm in Section 4 to fully leverage algorithm benefits while avoiding the additional overhead of complex computations. In our implementation, we further enhance the hardware utilization at runtime by applying optimizations on computation, scheduling, and memory management.

## 5.1 Preprocess

In the new preprocessing stage as shown in Algorithm 4, Our precise per-tile intersection algorithm with the ellipse introduces massive complex calculations, which might significantly hinder applying this algorithm in current SOTA works. It is essential to implement this algorithm efficiently, despite our efforts in Section 4.2 to balance the computeto-memory ratio by binding the precise intersection with some memory access operations. We optimized the algorithm in two key aspects: 1) applying algebraic simplifications to reduce the overhead of a single tile-ellipse intersection; 2) proposing an adaptive scheduling strategy to balance the intersection tasks of the entire projected ellipse of a Gaussian.

```csv
Algorithm 4 preprocessCUDA
Input: o, σ, shs, viewmatrix, projmatrix, ocam,
    W, H, tan_fovx, tan_fovy, focal_x, focal_y,
Output: x'_I,offset,depths, Σ, c, conic_opacity,
    gaussian_keys_unsorted, gaussian_values_unsorted
if idx_vec < P then
    Initialize p_orig,p_view
    if p_view.z > 0.2 and opacity > 1.0/255 then
        p_proj ← project()
        Σ' ← computeCov2D()
        x'_I ← ndc2Pix()
        rect_min, rect_max ← getRect()
        point_valid ← (bounding box is non-zero)
if point_valid and bounding box is single tile then
    if tile intersects ellipse or contains center then
        key ← compute tile key
        offset ← atomicAdd(curr_offset, 1)
        gaussian_keys_unsorted[offset] ← key
        gaussian_values_unsorted[offset] ← idx_vec
for each thread in warp do
    if multi_tiles then
        parameters ← shuffle values
        for y ← rect_min.y to rect_max.y do
            for x ← rect_min.x to rect_max.x do
                if valid then
                    key ← compute tile key
                    store key and value
if any thread has valid point then
    c[idx_vec] ← computeColorFromSH()
    store depth, point_xy, conic_opacity
```

**5.1.1 Algebraic Simplification.** We use algebraic equivalence transformations to avoid high-cost operations (instructions). In our geometric transformations of intersection in Section 4.1, to determine if two line segments on the same line overlap, we can compare their endpoint coordinates. Assume the two line segments are <sup>[a</sup>𝑖, b<sub>𝑖</sub>] and <sup>[a</sup>𝑗, b<sub>𝑗</sub>], they

8

<!-- page 9 of 14 -->

overlap if their intersection is not empty as shown in Equation 4:

$$
\min (b _ {i}, b _ {j}) - \max (a _ {i}, b _ {i}) \geq 0\tag{4}
$$

Specifically, this is equivalent to checking Equation 5 that if the right endpoint (end) of one line segment is after the left endpoint (start) of the other line segment, and if the left endpoint (start) of the line segment is before the right endpoint (end) of the other line segment:

$$
a _ {i} \leq b _ {j} \& \& a _ {j} \geq b _ {i}\tag{5}
$$

The process of finding the endpoints of intersecting line segments requires solving quadratic equations, which involves high-cost operations such as division and square roots. Assume an edge of a tile is represented by the line segment $[ \mathbf { a } _ { i } ,   \mathbf { b } _ { i } ]$ , The endpoints of the intersecting line $[ \mathbf { a } _ { j } ,   \mathbf { b } _ { j } ]$ (if exists) are two roots of the quadratic equation formed by the line (on which the tile edge lies) and the ellipse. As shown in the Equation 6, where $DELTA = B^{2} - 4AC$ , and 𝐴, 𝐵, 𝐶 are the coefficients of the quadratic equation $A X ^ { 2 } + B X + C = 0 ;$

$$
a _ {i} \leq \frac {- B + \sqrt {D E L T A}}{2 A} \& \& b _ {i} \geq \frac {- B - \sqrt {D E L T A}}{2 A}\tag{6}
$$

Without loss of generality, let $A > 0 ,$ then this condition can be transformed into Equation 7 to avoid the high-cost operations, division, and square roots, where the two expressions $e _ { 1 } = 2 A a _ { i } + B$ and $e _ { 2 } = 2 A b _ { i } + B ;$

$$
(e _ {1} \leq 0 | | e _ {1} ^ {2} \leq D E L T A) \& \& (e _ {2} \geq 0 | | e _ {2} ^ {2} \leq D E L T A)\tag{7}
$$

**5.1.2 Adaptive Size-aware Scheduling.** The precise pertile intersection algorithm also implies that the workload for intersection tasks can vary significantly for different Gaussians, as the number of tiles covered by ellipses of different sizes can vary greatly. In the original 3DGS intersection algorithm, which is based on bounding boxes, this issue does not arise because the covered tile region can be located directly using only the vertices of the bounding box, ignoring the bounding box size. As shown in the figure 11, for Gaussians of different sizes, the resulting bounding boxes, i.e., the number of tiles to be intersected, can vary greatly.

We automatically select our processing method based on the size of the Gaussians to achieve efficient scheduling. To ensure that the workload of each thread is balanced, we use an adaptive mapping. When the ellipse is quite small and only requires calculation for one tile, we continue using the current thread for the precise intersection of this Gaussian. When the ellipse is large, we remap the workload to a thread group (in our implementation, we chose a warp to balance synchronization overhead, considering that in practice, the size of the ellipse seldom covers more than 32 tiles). Thus, we achieve an efficient calculation for the entire Gaussian projected ellipse which can intersect with different numbers of tiles. After applying all the aforementioned optimizations, our new processing kernel is shown in the Algorithm 4.

![Image block](images/feng2024_flashgs_p9_b11.png)

Figure 11. Adaptive task partitioning for Gaussian intersec tions with varying sizes. If a large ellipse requires processing multiple tiles, other threads within the warp are utilized to collaborate on the intersection.

## 5.2 Rendering

To address the issue of low hardware utilization during the 3DGS execution, we implement a two-level pipeline optimization from top to bottom. We adjusted the application’s execution workflow and the instruction dispatch.

![Image block](images/feng2024_flashgs_p9_b15.png)

Figure 12. Software pipelining to achieve better overlap between computation and memory access.

**5.2.1 Low-latency Execution Pipelining.** During rendering, each tile performs computations related to its associated Gaussians, such as calculating transmittance and color. These computations may terminate early based on the accumulated 𝛼 saturation. These calculations depend on the preprocessed and sorted Gaussian lists, which need to be loaded from global memory in advance. The process of reading Gaussian information can be divided into two steps: (1) obtaining the Gaussian index based on the current tile information; (2) using the index to fetch the stored specific information, such as the pixel coordinates of the Gaussian center, the quadratic form of the ellipse, and opacity, among other details. The high latency of global memory access can hinder the efficient execution of the computation pipeline, especially since there are two dependent steps of global memory access as mentioned above.

9

<!-- page 10 of 14 -->

Our core strategy is to issue as many instructions as possible during memory access latency periods to alleviate stalls caused by data dependencies. Specifically, we introduced a two-level prefetching strategy to maximize the overlap between computation and memory access illustrated in Figure 12. Using a software pipelining approach, for the computation at step i, we first fetch the Gaussian index for step i+2 from global memory. Then, using the already fetched index, we retrieve the specific Gaussian information for step i+1 from global memory. Finally, we perform the rendering computation for step i using the Gaussian information fetched at step i-1. We overlap independent instructions as much as possible in our fine-grained rearrangement, thereby achieving a more efficient instruction dispatch pipeline.

**5.2.2 Warp Divergence Control.** Thread divergence within a warp can cause some threads to stall, affecting execution efficiency. The core idea is to minimize conditional branching or move conditional checks to an outer layer (coarser granularity), thus ensuring that threads within a warp execute the same path as much as possible. In the render step of the original 3DGS algorithm, each thread must check opacity and transmittance when computing a pixel to perform early stopping and determine whether the pixel is valid before writeback. We move the opacity check to the preprocessing stage for effective Gaussian computations. This preemptive filtering at the coarser Gaussian level eliminates redundancy, replacing the per-pixel conditional checks during rendering.

**5.2.3 Coarse-grained Workload Partition.** We facilitate common data sharing by adjusting the task dispatch granularity so that a single thread handles multiple groups of tasks. This larger granularity is mainly based on two considerations. Firstly, it aims to fully utilize fast memory units (such as registers), thus we cannot set the buffer too small (e.g., only buffering a very small amount of data for a single item). Secondly, it takes into account the issue of shared data. In rendering, there is also a certain amount of common computation. We provide a group of tasks as a unit to the compiler to expose more potential sharing opportunities. Specifically, we expose the opportunities for common subexpression elimination (CSE) to further improve computational performance by reducing FLOPs.

## 5.3 Common Optimizations

In addition to the aforementioned efficient parallel algorithm implementation of some critical kernels, we also applied sev eral general techniques to optimize memory and instruction usage throughout the FlashGS computation, achieving further performance benefits.

**5.3.1 Memory Management.** 3DGS involves a large number of memory operations, including read, write, and allocation. We need a meticulous design to exploit the GPU’s hierarchical memory and the memory bandwidth.

We utilize the constant memory to reduce latency. We carefully analyze the algorithm and extract the special parameters to efficiently utilize the GPU memory hierarchy. The core idea is to leverage special memory access patterns to maximize the use of data loaded into a faster memory hierarchy. We use constant memory when available, which is highly beneficial for accessing data shared across all threads. For example, in the preprocessing step, all threads need to read some predefined input information, such as projection matrices and transformation matrices. By leveraging the large parameter passing feature (CUDA 12.1), we pass these data directly as parameters to the kernel rather than pointers to their memory locations. This ensures these parameters are placed in constant memory instead of global memory. Given that global memory latency is approximately 500 cycles, while constant memory access latency with caching is only around 5 cycles, our data placement strategy not only improves access speed but also reduces bandwidth pressure on the L1 cache caused by frequent global memory accesses.

We reduce the dynamic memory allocation. We avoid the performance reduction of frequent memory allocation, which could be caused by the overhead of system calls and memory fragmentation. We extract the dynamic memory allocation operations and related preprocessing operations to the initial stage. For example, a unified preprocessing can be done in advance for computations involving different viewpoints of the same scenario.

**5.3.2 Assembly Optimization.** We also utilize explicit and implicit optimizations to better leverage efficient instruc tions supported by the GPUs. In Gaussian computations, due to the exponential part of the Gaussian distribution, naive calls can result in high overhead. By converting the direct multiplication in the exponential expression to logarithmic form, we first perform addition and then exponential operations. This approach is beneficial because it allows the compiler to use fused multiply-add (FMA) instructions, which have the same overhead as a single MUL or ADD instruction. Additionally, when performing logarithmic and exponential operations, we explicitly specify base 2 because the GPU’s Special Function Unit (SFU) hardware instructions are opti mized for base 2, allowing for direct and efficient calls of the fast ex2.approx.ftz.f32 PTX instruction.

## 6 Evaluation

## 6.1 Experimental Setup

**6.1.1 Testbed.** We conduct our experiments on two NVIDIA GPU platforms. Most tests are performed on a consumergrade RTX 3090 (Ampere architecture, 24GB GDDR6X memory, CUDA Compute Capability 8.6). We use an A100 (Ampere architecture, 80GB HBM2e, CUDA Compute Capability 8.0) data-center GPU to study performance sensitivity. We compile our codes with GCC 10.5.0 and NVCC in CUDA

10

<!-- page 11 of 14 -->

<table><tr><td rowspan="2">Metrics\Dataset</td><td colspan="2">Truck</td><td colspan="2">Train</td><td colspan="2">Playroom</td><td colspan="2">DrJohnson</td><td colspan="2">Matrixcity</td><td>Rubble</td></tr><tr><td>1080p</td><td>4k</td><td>1080p</td><td>4k</td><td>1080p</td><td>4k</td><td>1080p</td><td>4k</td><td>1080p</td><td>4k</td><td>4608*3456</td></tr><tr><td>AvgTime (FlashGS / 3DGS)</td><td>2.22 / 8.21</td><td>3.46 / 24.19</td><td>1.93 / 7.82</td><td>3.32 / 12.82</td><td>1.44 / 6.83</td><td>2.72 / 10.74</td><td>1.63 / 9.11</td><td>2.99 / 28.74</td><td>3.22 / 20.90</td><td>4.90 / 66.55</td><td>6.19 / 44.11</td></tr><tr><td>MaxTime (FlashGS / 3DGS)</td><td>4.44 / 10.18</td><td>4.65 / 29.87</td><td>3.48 / 12.82</td><td>4.22 / 42.73</td><td>2.92 / 10.74</td><td>4.69 / 32.11</td><td>4.95 / 16.92</td><td>6.91 / 57.67</td><td>4.77 / 40.74</td><td>7.25 / 140.52</td><td>9.32 / 67.57</td></tr><tr><td>AvgSpeedup</td><td>3.76</td><td>7.01</td><td>4.20</td><td>7.48</td><td>4.92</td><td>7.86</td><td>6.18</td><td>9.99</td><td>6.56</td><td>13.64</td><td>7.41</td></tr><tr><td>MaxSpeedup</td><td>4.74</td><td>8.60</td><td>6.89</td><td>11.51</td><td>7.91</td><td>11.16</td><td>14.99</td><td>21.66</td><td>13.49</td><td>30.53</td><td>14.10</td></tr><tr><td>MinSpeedup</td><td>2.29</td><td>5.53</td><td>2.19</td><td>4.46</td><td>3.16</td><td>5.69</td><td>3.07</td><td>6.39</td><td>3.92</td><td>7.30</td><td>5.23</td></tr><tr><td>AvgTime (FlashGS on A100)</td><td>3.37</td><td>4.87</td><td>3.05</td><td>4.58</td><td>2.36</td><td>3.98</td><td>2.59</td><td>4.35</td><td>4.18</td><td>6.55</td><td>8.08</td></tr></table>

Table 1. FlashGS average/slowest frame rendering time (ms) and corresponding FPS with speedup relative to 3DGS across different datasets and resolutions on 3090 GPU.

12.0. We have also integrated FlashGS as a callable module in Python to enhance usability.

**6.1.2 Dataset.** We comprehensively test FlashGS and 3DGS on 6 representative datasets, which cover very different resolutions on a total of 11 scenes with hundreds or thousands of frames per scene. The Truck and Train are outdoor scenes from the Tanks & Temple [14]. The Playroom and DrJohnson are two indoor scenes in DeepBlending [10]. 3DGS claims that they achieve real-time rendering with 1080p resolution on these datasets. We use another 2 large-scale and highresolution datasets which beyond 3DGS’s capabilities to render in real-time. MatrixCity [16] is a comprehensive and large-scale high-quality dataset, comprising thousands of aerial images at a resolution of 1080p. Rubble in Mill19 [21] contains high-resolution images captured by drones. We train 30K iterations on each dataset with 3DGS to obtain the Gaussian model for rendering.

**6.1.3 Baseline.** We compare FlashGS with 3DGS [13] and the recent optimizations on GScore [15]. Since GScore is implemented as a hardware accelerator unit, we cannot directly test it. They claim that GScore achieves 1.86× speedup with their intersection and scheduling techniques <sup>2</sup>.

## 6.2 Overall Performance

As shown in Table 1, the rasterization pipe of FlashGS outperforms the original 3DGS algorithm across all the performance metrics on every dataset with different scenes and resolutions. We can always achieve > 100FPS rendering on RTX 3090, even for high-resolution and large-scale datasets. In the slowest frame in Rubble of all datasets, we achieve 107.3 FPS. This demonstrates that FlashGS can perform realtime rendering even in extremely large and high-resolution cases. Flash GS achieves up to 30.53× speedup with an average of 12.18× on the Matrixcity dataset at 4k resolution. We achieve 7.2× average speedup on all 11 scenes, while achieving 8.6× speedup on the 7 large-scale or high-resolution tests, which is 3.87× of the GScores results [15]. FlashGS achieves a 2.29× to 30.53× speedup for all the frames in different scenes, comprehensively proving the generality of our design and optimization.

## 6.3 Runtime Breakdown Analysis

![Chart block](images/feng2024_flashgs_p11_b9.png)

Figure 13. Rasterization runtime breakdown on 6 representative frames from different datasets, normalized to 3DGS.

In this section, we compare and analyze the runtime breakdown of FlashGS to 3DGS, aiming to reveal the source of our excellent performance. Figure 13 shows the rasterization time and the breakdown for 6 representative frames shows max or min speedup. This demonstrates that we have accelerated all stages, including preprocess, sort, and render. In FlashGS, these stages respectively account for average 19.6%, 29.1%, and 47.6% of the total time, whereas in 3DGS, they account for 13.2%, 25.4%, and 59.6%. The optimizations in the preprocess and render stages have already been discussed earlier, while the speedup in the sorting stage is primarily due to the reduction in the number of key-value pairs to be sorted after applying our precise intersection algorithm. We will give a more detailed analysis below.

![Chart block](images/feng2024_flashgs_p11_b12.png)

Figure 14. Profiling results of FlashGS: The number of instructions issued in rendering and the memory transactions in preprocessing. All results are normalized to 3DGS.

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>2</sup>Their shape-aware intersection test provides 1.71× speedup and subtle skipping offers an additional 15% improvement.</span></small>

11

<!-- page 12 of 14 -->

**6.3.1 Profiling Results.** We further demonstrate our optimizations in the rendering and preprocessing stages through profiling results of memory and compute units, as shown in the figures. Figure 14 shows that we reduce the issued instructions in the rendering stage, alleviating the computationbound problem. This prove the effectiveness of our precise intersection algorithm and the optimizations for low-latency rendering. The total issues instructions is significantly reduced by one to two orders of magnitude. For memory access trasactions in preprocessing, we also reduced the number of global memory accesses by 43%-87% compared to 3DGS.

![Chart block](images/feng2024_flashgs_p12_b2.png)

Figure 15. Number of rendered Gaussian-tile (kv) pairs and instructions issued per pair of FlashGS (Normalized to 3DGS).

Figure 15 further shows the reason for the significant instruction reduction in the rendering stage, which is dominant in the rasterization. In tile-based rendering, the total number of issued instructions is the product of the number of tiles and the instructions per tile. Therefore, this reduction mainly stems from two aspects. In Figure 15, the number of rendered key-value pairs benefit from our intersection optimization, reducing by 68%-96%. The instructions involved in each tile’s computation also decrease by 67%-71%, as we further optimize the renderCUDA kernel at the instruction level. The reduction in the number of generated key-value pairs also benefits the sorting process, as it significantly decreases the size of the list to be sorted. Additionally, less memory is required to store these key-value pairs.

## 6.4 Sensitivity Study

In this section, we study the FlashGS performance sensitivity on different GPUs and sciences.

**6.4.1 Performance on A100.** We also conduct the experiments presented in Table 1 on the A100 GPU, and the results are shown in Table 1. The total rasterizerization time is slower on the A100 compared to the 3090, with on average 1.43× slower. This is primarily due to the rendering step is dominant, as shown in Figure 13, which heavily relies on FP32 computation, where the FP32 peak performance of the A100 is only 19.5TFLOPS while the 3090 is 35.6TFLOPS. Although the operations before rendering, such as sorting, are mainly memory-bandwidth-bound, and the A100 has a

higher bandwidth than 3090, these benefits can not outweigh the render performance reduction. However, we still achieve significant speedups to 3DGS in all datasets on the A100 with an average of 123.8-423.7 FPS across 11 scenes in Table 1, always reaching real-time rendering.

**6.4.2 Performance on different scenes.** In Table 1, we observe two main results: 1) For the same dataset, the speedup at 4K resolution is higher than at 1080p. 2) Across different datasets, the highest speedup is achieved in large-scale, high resolution scenes (MatrixCity-4K). This is primarily source from our precise intersection calculations, where the computational load in the rendering is proportional to the number of Gaussians and the number of tiles each Gaussian intersects. In large scenes with more objects, the number of Gaussians increases; for high resolutions, the Gaussians become larger to render finer details. In such cases, the redundancy elimination effect is more pronounced. And if in a very small and simple scene, each Gaussian might be so small that it intersects only one tile, leading to a lower improvement of our precise intersection.

## 6.5 Image Quality

![Image block](images/feng2024_flashgs_p12_b11.png)

Figure 16. The rendering quality and rasterization time on Matricity(1080p)-800 frame.

Figure 17 shows the most complex frame of the origin large-scale MatrixCity dataset at 1080p, to compare the output quality. We compare the Peak Signal to Noise Ratio (PSNR) between FlashGS and 3DGS, which is a standard metric in computer graphics (higher is better). The result shows that FlashGS does not change the quality, keeping 31.52 PSNR with 8.57× speedup. It is reasonable that our pre-cise intersection algorithms only reduce the false-positive redundancies. And we do not apply pruning or quantization strategies in our implementation so there is no accuracy loss.

In Table 2, we observe two main results: 1) For the same dataset, the speedup at 4K resolution is higher than at 1080p. 2) Across different datasets, the highest speedup is achieved in large-scale, high-resolution scenes (MatrixCity-4K). This is primarily source from our precise intersection calculations, where the computational load in the rendering is proportional to the number of Gaussians and the number of tiles each Gaussian intersects. In large scenes with more objects, the number of Gaussians increases; for high resolutions, the Gaussians become larger to render finer details. In such cases, the redundancy elimination effect is more pronounced. And

12

<!-- page 13 of 14 -->

| Method | Before Rendering | After Rendering | #key-value pairs |
| --- | --- | --- | --- |
| 3DGS | 7.86 GB | 13.45 GB | 56,148,670 |
| gsplat (𝑝𝑎𝑐𝑘𝑒𝑑 𝐹𝑎𝑙𝑠𝑒) | 4.52 GB | 10.75 GB | 56,996,302 |
| gsplat (𝑝𝑎𝑐𝑘𝑒𝑑 𝑇𝑟𝑢𝑒) | 4.52 GB | 9.83 GB | 56,998,101 |
| FlashGS | 6.83 GB | 6.83 GB | 3,436,142 |

Table 2. Memory allocated before and after rendering the 800th frame in MatrixCity dataset.

if in a very small and simple scene, each Gaussian might be so small that it intersects only one tile, leading to a lower improvement of our precise intersection.

## 6.6 Image Quality

![Image block](images/feng2024_flashgs_p13_b5.png)

Figure 17. Above is the 800th image (the longest one), below is the 809th image (the shortest one), the left is the baseline, and the right is the FlashGS (ours)

Figure 17 shows two representative frames of the largescale MatrixCity dataset. We compare the PSNR between FlashGS and 3DGS, and the result shows that FlashGS does not change the quality. It is reasonable that our precise intersection algorithms only reduce the false-positive redundancies. And we do not apply pruning or quantization strategies in our implementation so there is no accuracy loss.

## 6.7 Memory Comparison

FlashGS allocates less memory than 3DGS and gsplat, up to 49.2% reduction. Table 2 compares the memory usage before and after rendering the 800th frame on an NVIDIA A100 GPU for different models, including gsplat (with 𝑝𝑎𝑐𝑘𝑒𝑑 set to 𝑇 𝑟𝑢𝑒 and 𝐹𝑎𝑙𝑠𝑒), the original 3DGS, and FlashGS. Specifically, the gsplat with 𝑝𝑎𝑐𝑘𝑒𝑑 set to 𝐹𝑎𝑙𝑠𝑒 has a maximum memory allocation of 10.75 GB after rendering, while with 𝑝𝑎𝑐𝑘𝑒𝑑 set to 𝑇 𝑟𝑢𝑒, the maximum memory allocation is reduced to 9.83 GB, significantly decreasing memory usage. This reduction occurs because, when 𝑝𝑎𝑐𝑘𝑒𝑑 is set to 𝑇 𝑟𝑢𝑒, the rasterization process is more memory-efficient, packing intermediate tensors into sparse tensor layouts. This is particularly beneficial in large scenes where each camera only

sees a small portion of the scene, greatly reducing memory usage. However, this also introduces some runtime overhead. In contrast, the original GS uses the most memory, with a memory allocation of 13.45 GB after rendering , making it an important factor to consider when dealing with complex scenes.

FlashGS also ensures consistency and predictability in memory usage through a static allocation method, with a maximum memory allocation of 6.83 GB, which is lower than the other models. This demonstrates its superior efficiency and performance when handling large scenes. The static allocation method effectively avoids fluctuations in memory allocation and release processes, resulting in more stable memory management.

The number of kv pairs generated by each method is a crucial factor in determining memory usage when rendering. The original 3DGS model generates 56,148,670 key-value pairs, which leads to its higher memory consumption. In comparison, gsplat with 𝑝𝑎𝑐𝑘𝑒𝑑 set to 𝐹𝑎𝑙𝑠𝑒 and 𝑇 𝑟𝑢𝑒 generates 56,996,302 and 56,998,101 key-value pairs respectively, showing a slight increase. And it proves that the memory reduction come from its compression techniques. FlashGS, on the other hand, generates only 3,436,142 key-value pairs, drastically reducing the memory usage.

## 7 Conclusions

We propose FlashGS, enabling real-time rendering of largescale and high-resolution scenes. In this paper, we achieved a fast rendering pipeline through a refined algorithm design and several highly optimized implementations, addressing the redundancy and improper compute-to-memory ratio issues present in original 3DGS. FlashGS significantly surpasses the rendering performance of existing methods on GPUs, achieves efficient memory management, while maintaining high image quality.

## References

[1] Jonathan T Barron, Ben Mildenhall, Matthew Tancik, Peter Hedman, Ricardo Martin-Brualla, and Pratul P Srinivasan. 2021. Mip-nerf: A multiscale representation for anti-aliasing neural radiance fields. In Proceedings of the IEEE/CVF international conference on computer vision. 5855–5864.

[2] Guikun Chen and Wenguan Wang. 2024. A survey on 3d gaussian splatting. arXiv preprint arXiv:2401.03890 (2024).

[3] Yu Chen and Gim Hee Lee. 2024. DoGaussian: Distributed-Oriented Gaussian Splatting for Large-Scale 3D Reconstruction Via Gaussian Consensus. arXiv preprint arXiv:2405.13943 (2024).

[4] David Crandall, Andrew Owens, Noah Snavely, and Dan Huttenlocher. 2011. Discrete-continuous optimization for large-scale structure from motion. In CVPR 2011. IEEE, 3001–3008.

[5] Kangle Deng, Andrew Liu, Jun-Yan Zhu, and Deva Ramanan. 2022. Depth-supervised nerf: Fewer views and faster training for free. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 12882–12891.

[6] Sankeerth Durvasula, Adrian Zhao, Fan Chen, Ruofan Liang, Pawan Kumar Sanjaya, and Nandita Vijaykumar. 2023. DISTWAR:

13

<!-- page 14 of 14 -->

Fast Differentiable Rendering on Raster-based Rendering Pipelines. arXiv preprint arXiv:2401.05345 (2023).

[7] Zhiwen Fan, Kevin Wang, Kairun Wen, Zehao Zhu, Dejia Xu, and Zhangyang Wang. 2023. Lightgaussian: Unbounded 3d gaussian compression with 15x reduction and 200+ fps. arXiv preprint arXiv:2311.17245 (2023).

[8] Ben Fei, Jingyi Xu, Rui Zhang, Qingyuan Zhou, Weidong Yang, and Ying He. 2024. 3d gaussian splatting as new era: A survey. IEEE Transactions on Visualization and Computer Graphics (2024).

[9] Sharath Girish, Kamal Gupta, and Abhinav Shrivastava. 2023. Eagles: Efficient accelerated 3d gaussians with lightweight encodings. arXiv preprint arXiv:2312.04564 (2023).

[10] Peter Hedman, Julien Philip, True Price, Jan-Michael Frahm, George Drettakis, and Gabriel Brostow. 2018. Deep blending for free-viewpoint image-based rendering. ACM Transactions on Graphics (ToG) 37, 6 (2018), 1–15.

[11] Peter Hedman, Pratul P Srinivasan, Ben Mildenhall, Jonathan T Barron, and Paul Debevec. 2021. Baking neural radiance fields for real-time view synthesis. In Proceedings of the IEEE/CVF international conference on computer vision. 5875–5884.

[12] Tao Hu, Shu Liu, Yilun Chen, Tiancheng Shen, and Jiaya Jia. 2022. Efficientnerf efficient neural radiance fields. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 12902–12911.

[13] Bernhard Kerbl, Georgios Kopanas, Thomas Leimkuehler, and George Drettakis. 2023. 3D Gaussian Splatting for Real-Time Radiance Field Rendering. ACM Transactions on Graphics (TOG) 42 (2023), 1–14.

[14] Arno Knapitsch, Jaesik Park, Qian-Yi Zhou, and Vladlen Koltun. 2017. Tanks and temples: Benchmarking large-scale scene reconstruction. ACM Transactions on Graphics (ToG) 36, 4 (2017), 1–13.

[15] Junseo Lee, Seokwon Lee, Jungi Lee, Junyong Park, and Jaewoong Sim. 2024. GSCore: Efficient Radiance Field Rendering via Architectural Support for 3D Gaussian Splatting. In Proceedings of the 29th ACM International Conference on Architectural Support for Programming Languages and Operating Systems, Volume 3. 497–511.

[16] Yixuan Li, Lihan Jiang, Linning Xu, Yuanbo Xiangli, Zhenzhi Wang, Dahua Lin, and Bo Dai. 2023. Matrixcity: A large-scale city dataset for city-scale neural rendering and beyond. In Proceedings of the IEEE/CVF International Conference on Computer Vision. 3205–3215.

[17] Lingjie Liu, Jiatao Gu, Kyaw Zaw Lin, Tat-Seng Chua, and Christian Theobalt. 2020. Neural sparse voxel fields. Advances in Neural Information Processing Systems 33 (2020), 15651–15663.

[18] Tao Lu, Mulin Yu, Linning Xu, Yuanbo Xiangli, Limin Wang, Dahua Lin, and Bo Dai. 2024. Scaffold-gs: Structured 3d gaussians for viewadaptive rendering. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 20654–20664.

[19] Ben Mildenhall, Pratul P Srinivasan, Matthew Tancik, Jonathan T Barron, Ravi Ramamoorthi, and Ren Ng. 2021. NeRF: Representing scenes as neural radiance fields for view synthesis. Commun. ACM 65, 1 (2021), 99–106.

[20] Thomas Müller, Alex Evans, Christoph Schied, and Alexander Keller. 2022. Instant neural graphics primitives with a multiresolution hash encoding. ACM transactions on graphics (TOG) 41, 4 (2022), 1–15.

[21] Haithem Turki, Deva Ramanan, and Mahadev Satyanarayanan. 2022. Mega-nerf: Scalable construction of large-scale nerfs for virtual flythroughs. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 12922–12931.

[22] Liao Wang, Jiakai Zhang, Xinhang Liu, Fuqiang Zhao, Yanshun Zhang, Yingliang Zhang, Minye Wu, Jingyi Yu, and Lan Xu. 2022. Fourier plenoctrees for dynamic radiance field rendering in real-time. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 13524–13534.

[23] Yi Wei, Shaohui Liu, Yongming Rao, Wang Zhao, Jiwen Lu, and Jie Zhou. 2021. Nerfingmvs: Guided optimization of neural radiance fields for indoor multi-view stereo. In Proceedings of the IEEE/CVF

International Conference on Computer Vision. 5610–5619.

[24] Liwen Wu, Jae Yong Lee, Anand Bhattad, Yu-Xiong Wang, and David Forsyth. 2022. Diver: Real-time and accurate neural radiance fields with deterministic integration for volume rendering. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 16200–16209.

[25] Tong Wu, Yu-Jie Yuan, Ling-Xiao Zhang, Jie Yang, Yan-Pei Cao, Ling-Qi Yan, and Lin Gao. 2024. Recent advances in 3d gaussian splatting. Computational Visual Media (2024), 1–30.

[26] Qiangeng Xu, Zexiang Xu, Julien Philip, Sai Bi, Zhixin Shu, Kalyan Sunkavalli, and Ulrich Neumann. 2022. Point-nerf: Point-based neural radiance fields. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. 5438–5448.

[27] Zhiwen Yan, Weng Fei Low, Yu Chen, and Gim Hee Lee. 2024. Multi-scale 3d gaussian splatting for anti-aliased rendering. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 20923–20931.

[28] Vickie Ye and Angjoo Kanazawa. 2023. Mathematical Supplement for the gsplat Library. arXiv[:2312.02121](https://arxiv.org/abs/2312.02121) [cs.MS]

[29] Alex Yu, Ruilong Li, Matthew Tancik, Hao Li, Ren Ng, and Angjoo Kanazawa. 2021. Plenoctrees for real-time rendering of neural radiance fields. In Proceedings of the IEEE/CVF International Conference on Computer Vision. 5752–5761.

[30] Jiahui Zhang, Fangneng Zhan, Muyu Xu, Shijian Lu, and Eric Xing. 2024. Fregs: 3d gaussian splatting with progressive frequency regularization. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 21424–21433.

[31] Hexu Zhao, Haoyang Weng, Daohan Lu, Ang Li, Jinyang Li, Aurojit Panda, and Saining Xie. 2024. On Scaling Up 3D Gaussian Splatting Training. arXiv preprint arXiv:2406.18533 (2024).

14