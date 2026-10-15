<!-- page 1 of 17 -->

arXiv:2402.00525v3 [cs.GR] 9 Oct 2024

# StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering

LUKAS RADL<sup>∗</sup>and MICHAEL STEINER<sup>∗</sup>, Graz University of Technology, Austria

MATHIAS PARGER, Huawei Technologies, Austria

ALEXANDER WEINRAUCH, Graz University of Technology, Austria

BERNHARD KERBL, TU Wien, Austria

MARKUS STEINBERGER, Graz University of Technology, Austria and Huawei Technologies, Austria

## 3D Gaussian Splatting

Ours

3D Gaussian Splatting

Ours

![Image block](images/radl2024_stopthepop_p1_b12.png)

Fig. 1. 3D Gaussian Splatting [Kerbl et al. 2023] suffers from popping artifacts during view rotation due to its approximate, global sorting scheme. Our method is able to effectively circumvent short-range popping artifacts (left) and long-range view-inconsistencies (right) during rotation with a novel, hierarchical per-pixel sorting strategy.

Gaussian Splatting has emerged as a prominent model for constructing 3D representations from images across diverse domains. However, the efficiency of the 3D Gaussian Splatting rendering pipeline relies on several simplifications. Notably, reducing Gaussian to 2D splats with a single viewspace depth introduces popping and blending artifacts during view rotation. Addressing this issue requires accurate per-pixel depth computation, yet a full per-pixel sort proves excessively costly compared to a global sort operation. In this paper, we present a novel hierarchical rasterization approach that systematically resorts and culls splats with minimal processing overhead. Our software rasterizer effectively eliminates popping artifacts and view inconsistencies, as demonstrated through both quantitative and qualitative measurements. Simultaneously, our method mitigates the potential for cheating view-dependent effects with popping, ensuring a more authentic representation. Despite the elimination of cheating, our approach achieves comparable quantitative results for test images, while increasing the consistency for novel view synthesis in motion. Due to its design, our hierarchical approach is only 4% slower on average than the original Gaussian

Splatting. Notably, enforcing consistency enables a reduction in the number of Gaussians by approximately half with nearly identical quality and view-consistency. Consequently, rendering performance is nearly doubled, making our approach 1.6x faster than the original Gaussian Splatting, with a 50% reduction in memory requirements. Our renderer is publicly available at [https://github.com/r4dl/StopThePop.](https://github.com/r4dl/StopThePop)

CCS Concepts: • **Computing methodologies** → **Rasterization**.

Additional Key Words and Phrases: Parallel Computing, Point-based Rendering, Real-Time Rendering

## ACM Reference Format:

Lukas Radl, Michael Steiner, Mathias Parger, Alexander Weinrauch, Bernhard Kerbl, and Markus Steinberger. 2024. StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering. ACM Trans. Graph. 43, 4, Article 64 (July 2024), 17 pages. [https://doi.org/10.1145/3658187](https://doi.org/10.1145/3658187)

## 1 INTRODUCTION

In recent years, Neural Radiance Fields (NeRFs) [Mildenhall et al. 2020] have triggered a new surge of research around differentiable rendering of 3D representations. Leveraging the traditional volume rendering equation, NeRFs are fully differentiable, enabling contin uous optimization to align the representation to diverse input views and support high-quality novel view synthesis. This differentiability also proves valuable in addressing other rendering challenges that necessitate gradient flow and optimization.

Various strategies have arisen to tackle challenges in NeRFs, particularly mitigating the computational costs linked to multilayer perceptron (MLP) evaluation. These approaches include adopting direct voxel representations [Fridovich-Keil et al. 2022], employing

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>∗</sup>Both authors contributed equally to this work</span></small>

Authors’ addresses: Lukas Radl, lukas.radl@icg.tugraz.at; Michael Steiner, michael. steiner@tugraz.at, Graz University of Technology, Austria; Mathias Parger, Huawei Technologies, Austria, mathias.parger@huawei.com; Alexander Weinrauch, Graz University of Technology, Austria, alexander.weinrauch@icg.tugraz.at; Bernhard Kerbl, TU Wien, Austria, kerbl@cg.tuwien.ac.at; Markus Steinberger, Graz University of Technology, Austria and Huawei Technologies, Austria, steinberger@icg.tugraz.at.

© 2024 Copyright held by the owner/author(s). This is the author’s version of the work. It is posted here for your personal use. Not for redistribution. The definitive Version of Record was published in ACM Transactions on Graphics, [https://doi.org/10.1145/3658187.](https://doi.org/10.1145/3658187)

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 2 of 17 -->

64:2

• Radl and Steiner et al

![Image block](images/radl2024_stopthepop_p2_b3.png)

Fig. 2. Effect of collapsing 3D Gaussians into 2D splats and 3DGS’s depth simplification: (a) Integrating Gaussians along view rays r requires careful consideration of potentially overlapping 1D Gaussians. (b) Using flattened 2D splats and view-space 𝑧 as depth (projection of 𝜇 onto v) puts 2D splats on spherical segments around the camera, inverting the relative positions of the two Gaussians along the example view ray. (c) Camera rotation inverts the order along r, resulting in popping. (d) Camera translation does not alter the distance compared to (b).

feature hash maps [Müller et al. 2022], and exploring tensor factorizations [Chen et al. 2022; Tang et al. 2022]—departing to some extent from the original pure MLP design. A recent notable development in this trajectory is 3D Gaussian Splatting (3DGS) [Kerbl et al. 2023], which renders oriented 3D Gaussians with spherical harmonics (SH) as a view-dependent color representation.

Remaining faithful to the traditional volume rendering equation, 3DGS facilitates gradient flows from image errors to the Gaussians positions, shapes, densities, and colors. With an initialization based on structure-from-motion [Snavely et al. 2006], a real-time computemode rasterizer, and heuristic-driven densification and sparsification, 3DGS converges to a high-quality representation with compact memory requirements. Consequently, 3DGS has firmly established itself as one of the most widely used methods for 3D scene reconstruction and differentiable rendering. Colored, semi-transparent 3D Gaussians serve as a versatile representation, but their accurate rendering is challenging. Although the projection of a 3D Gaussian onto a view ray is straightforward, leveraging synergies between neighboring rays under perspective projection proves intricate. Hence, 3DGS approximates them as flattened 2D splats [Zwicker et al. 2002], necessitating depth-based sorting for rendering. 3DGS further simplifies this step by sorting based on the view-space 𝑧-coordinate of each Gaussian’s mean, effectively projecting splats onto spherical shells reminiscent of Broxton et al. [2020]. While this global sorting eases the rendering algorithm, it introduces popping artifacts, i.e., sudden color changes for consistent geometry, during camera rotations due to changes in the relative depth of shells (see Fig. 2). Such view inconsistencies due to popping can be very irritating and immersion-breaking, e.g. during head rotation in a virtual reality setting.

Fully evaluating all Gaussians in 3D along each view ray while considering their overlap would be ideal, but likely not feasible in real-time. The next best solution involves approximating the location where each Gaussian contributes the most for each view ray, i.e., determining its depth, followed by a correct per-pixel blending. Sorting must now happen for each view ray, rather than globally for all Gaussians; an obvious challenge as it is not uncommon to see thousands of Gaussians be considered for individual rays in 3DGS. To solve this challenge, we propose a novel 3D Gaussian Splatting rendering pipeline that exploits coherence among neighboring view

rays on multiple hierarchy levels, interleaving culling, depth evaluation and resorting. We make the following contributions:

• A novel hierarchical 3D Gaussian Splatting renderer that leads to per-pixel sorting of Gaussian splats for both the forward and backward pass of the 3DGS rendering pipeline and thus removes popping artifacts.

• An in-depth analysis of culling and depth approximation strategies, as well as pipeline optimizations and workload dis tribution schemes for our compute-mode 3DGS hierarchical renderer.

• A discussion and evaluation of various sorting strategies of Gaussian splats and their influence on overall rendering quality and view-consistency.

• An effective automatic method to detect popping artifacts in videos captured from trained 3D Gaussians as well as a user study confirming the results of the presented method.

Our results indicate that a full per-pixel sorted renderer for Gaussian splats eliminates all popping artifacts but reduces rendering speed by 100×. Our hierarchical renderer is virtually indistinguishable from a full per-pixel sorted renderer, but only adds an overhead of 4% compared to the original 3DGS.

## 2 PRELIMINARIES AND RELATED WORK

In the following, we review the renderer used in 3DGS. For a complete description of the approach, cf. Kerbl et al. [2023].

## 2.1 3D Gaussian Splatting

NeRF-style rendering and 3DGS use the volume rendering equation:

$$
\begin{array}{c} C (\mathbf {r}) = \int_ {0} ^ {t} \mathbf {c} \left(\mathbf {r}, t\right) \sigma \left(\mathbf {r}, t\right) T (\mathbf {r}, t) d t, \text {where} \\ T (\mathbf {r}, t) = e ^ {- \int_ {0} ^ {t} \sigma (\mathbf {r}, s) d s}, \end{array}\tag{1}
$$

𝐶(r) is the output color for a given ray $\mathbf { r } , \sigma \left( \mathbf { r } , t \right)$ is the opacity along the ray and 𝑐 (r, 𝑡) is the view-dependent emitted radiance. 3DGS represents a scene as a mixture of 𝑁 3D Gaussians each given by:

$$
\begin{array}{c} G (\mathbf {x}) = e ^ {- \frac {1}{2} (\mathbf {x} - \mu) ^ {T} \Sigma^ {- 1} (\mathbf {x} - \mu)}, \text {where} \\ \Sigma = R S S ^ {T} R ^ {T}, \end{array}
$$

𝜇 is the Gaussian’s location, 𝑅 is a rotation matrix and 𝑆 is a diagonal scaling matrix, allowing to position, rotate and non-uniformly scale

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 3 of 17 -->

StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering

64:3

Gaussians in 3D space while ensuring that Σ is positive semi-definite. When evaluating a 3D Gaussian along a ray, the resulting projection is a 1D Gaussian. It seems natural to evaluate Eqn. (1) considering how multiple Gaussians influence any location along the ray. As there is no elementary indefinite integral known for Gaussians, numerical integration is likely the only option. In practice, this would require a strict sorting of all starting and end points of all Gaussians and sampled numerical integration.

Instead, 3DGS makes multiple simplifications. First, they consider all Gaussians to be separated in space, i.e., compress their extent to a Dirac delta along the ray. Second, the Dirac delta of the 𝑖-th Gaussian is located at

$$
t _ {i} = \mu_ {i} ^ {T} \mathbf {v},\tag{2}
$$

i.e., the projection of the mean $\mu _ { i }$ onto the view direction v, independent of the individual ray r. Third, they approximate the projection of the Gaussian onto all rays, relying on an orthogonal projection approximation considering the first derivative of the 3D Gaussian to construct a 2D splat $G _ { 2 }$ [Zwicker et al. 2002].

These approximations enable faster rendering: Eqn. (1) becomes

$$
C (\mathbf {r}) = \sum_ {i = 1} ^ {N _ {\mathrm{r}}} \mathbf {c} _ {i} \alpha_ {i} \prod_ {j = 1} ^ {i - 1} (1 - \alpha_ {j}),\tag{3}
$$

where 𝑖 iterates over the $N _ { \mathbf { r } }$ Gaussians that influence the ray in the ordering of $t _ { i } ,$ and 𝛼𝑖 is the opacity of the Gaussian along the ray, $i . e . , G _ { 2 } ( x , y )$ , multiplied by a learned per-Gaussian opacity value.

Because $t _ { i }$ is independent of r, a global sort of all 𝑡 is possible. Naïvely, this would lead to $N _ { \mathbf { r } } = N$ for all rays. To reduce the number of Gaussians considered per ray, 3DGS splits the image into 16×16 pixel tiles, and runs a combined depth and tile sorting pre-pass, before evaluating Eqn. (3). For each tile and each Gaussian that may potentially contribute to any pixel in this tile—considering the 2D bounding box around the 1% Gaussian contribution threshold—a sorting key is generated with the tile index in the higher order bits and the depth in the lower bits. Sorting those combined keys leads to a $t _ { i } \cdot$ sorted list for each tile.

## 2.2 Radiance Field Methods

Contrary to 3DGS, NeRFs [Mildenhall et al. 2020] require sampling a continuous, implicit neural scene representation densely. Therefore, real-time rendering as well as handling unbounded scenes proves difficult. Many follow-up works investigated NeRF extensions to handle unbounded scenes [Barron et al. 2021, 2022, 2023] as well as faster rendering [Chen et al. 2022; Fridovich-Keil et al. 2022; Müller et al. 2022], 3D scene editing [Jambon et al. 2023; Kuang et al. 2023; Nguyen-Phuoc et al. 2022], avatar generation [Zielonka et al. 2023], scene dynamics [Park et al. 2021; Pumarola et al. 2020] and 3D object generation [Jain et al. 2022; Poole et al. 2022; Raj et al. 2023].

## 2.3 3DGS Follow-up Work

Following the code release and subsequent publication of 3DGS, several extensions have popped up investigating various paradigms, including the editing of trained Gaussians [Chen et al. 2023; Fang et al. 2023], text-to-3D [Tang et al. 2023; Yi et al. 2023] and 4D novel view synthesis [Luiten et al. 2024; Wu et al. 2023]. Mip-Splatting [Yu et al. 2023] proposes a 3D smoothing filter and 2D Mip filter to

![Image block](images/radl2024_stopthepop_p3_b15.png)

Fig. 3. Our approach to compute $t _ { o p t }$ avoids popping by placing splats at the point of maximum contribution along the view ray r, creating sort orders independent of camera rotation (red view vector). Note that the shape of $t _ { o p t }$ is a curved surface and changes with the camera position; cf. Fig. 2.

remedy aliasing in 3DGS. Besides them, most approaches merely leverage Gaussians as graphics primitives, whereas our approach tackles current problems with 3DGS.

## 2.4 Software Rasterization

Our compute-mode rendering pipeline for 3DGS is related to other software-based rendering pipelines. Early works like Pomegranate [Eldridge et al. 2000] and the Larrabee project [Seiler et al. 2008] showed that software pipelines on custom hardware are viable for rendering. Special compute-mode rendering pipelines have been proposed for REYES [Tzeng et al. 2010; Zhou et al. 2009], triangle rasterization [Karis et al. 2021; Kenzel et al. 2018; Laine and Karras 2011; Liu et al. 2010; Patney et al. 2015] and point clouds [Schütz et al. 2021]. Similarly to these efforts, we show that taking into account the specifics of the rendering problem, a compute-mode renderer for sorted Gaussian splats can execute in real-time on modern GPUs.

## 2.5 Order Independent Transparency

Correctly and efficiently rendering semi-transparent primitives, such as Gaussian splats, proves intricate for rasterization-based renderers. Methods approximating order independent transparency [Wyman 2016] investigate this paradigm. 𝑘-buffers [Bavoil et al. 2007; Callahan et al. 2005] operate with a fixed per-pixel memory budget, circumventing the large memory requirement of 𝐴- buffers [Carpenter 1984]. When this budget is exceeded, new incoming fragments are either merged [Salvi et al. 2011; Salvi and Vaidyanathan 2014] or the closest fragment gets written to the color buffer [Callahan et al. 2005]; both cases require a nearly-sorted order for incoming fragments. Our work combines hierarchical levels of 𝑘-buffers with 3DGS’s tile-based rasterization.

## 3 REAL-TIME SORTED GAUSSIAN SPLATTING

We present a novel per-pixel sorted 3D Gaussian splatting approach, departing from the current global sorting paradigm. Utilizing fast per-pixel depth calculations and a hierarchical intra-tile cooperative sorting approach, our method enhances the accuracy of the resulting sort order. To streamline computations, we incorporate per-tile opacity culling and a fast and GPU-friendly load balancing scheme.

## 3.1 Global Sorting

3DGS [Kerbl et al. 2023] performs a global sort based on the viewspace 𝑧-coordinate of each Gaussian’s mean 𝜇, see Eqn. (2). This leads to a consistent sort order during translation, but not during

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 4 of 17 -->

64:4

• Radl and Steiner et al

![Image block](images/radl2024_stopthepop_p4_b3.png)

Fig. 4. Correct rendering of a trained 3DGS scene with per-pixel sorting reveals how 3DGS cheats with the location of Gaussians. Our approach, on the other hand, considers correct sorting during training and rendering. Below, we show the sort error of different resorting windows and our full approach cf. Tab. 1. We intentionally use the trained 3DGS model here, as our trained version does not show these kinds of artifacts for visualization. The error visualization captures the sum over the depth difference of all wrongly sorted neighbors. For resorting with a window size of $^ { 4 , }$ tile artifacts are still visible. Our approach hardly diverges from fully sorted rendering, while running 100× faster; it is also about 5× faster than resort 24 and on average only 4% slower than 3DGS.

rotation, as illustrated in Fig. 2. While 3DGS may use this fact during training to introduce differences between views (and thus reduce the loss), it is in general undesirable, as camera rotations can lead to popping artifacts, which are particularly disturbing when inspecting the optimized 3D scene. Our objective is to stabilize color computations under rotation by splatting Gaussians based on the point of highest contribution along each view ray. Note that, although we improve rendering consistency, we still approximate true 3D Gaussians, neglecting any overlap between them.

## 3.2 Per-pixel Depth and Naïve Sorting

When replacing a 1D Gaussian along the view ray with a Dirac impulse, the mean/maximum of this 1D Gaussian is arguably the best discrete blend location. This maximum, $t _ { o p t }$ , can be computed from the derivative of the 3D Gaussian along the view ray $\mathbf { r } ( t ) = \mathbf { o } + t \mathbf { d } ;$

$$
t _ {o p t} = \frac {\mathbf {d} ^ {T} \Sigma^ {- 1} (\mu - \mathbf {o})}{\mathbf {d} ^ {T} \Sigma^ {- 1} \mathbf {d}}.\tag{4}
$$

Please see Appendix A for the step-by-step derivation.

Consider a simple 2D case with an isotropic Gaussian $\Sigma ^ { - 1 } = \mathbf { I } _ { \mathbf { \hat { z } } }$ the camera at (0, 0) and the Gaussian at $\mu = ( 0 , \mu _ { y } )$ . It is easy to see that the depth function follows a cosine as d is normalized:

$$
t = \frac {\mathbf {d} ^ {T} \mathbf {I} \mu}{\mathbf {d} ^ {T} \mathbf {I d}} = d _ {y} \cdot \mu_ {y} = \cos (\theta) \mu_ {y},
$$

where $\theta$ is the angle of the view ray. Thus, we conclude that there is no simple primitive, like, e.g., a plane to represent the $t _ { o p t }$ which could be rasterized traditionally, see Fig. 3. Therefore, we compute 𝑡𝑜𝑝𝑡 on a per-ray basis.

When reconstructing surfaces, Gaussians often turn very flat, as such, $\Sigma ^ { - 1 }$ may become large and lead to instabilities in the computation. Bounding the entries of $[ S ^ { - 1 } \mathrm { ~ t o ~ } 1 0 ^ { 3 }$ removes those instabilities in our experiments, by effectively thickening very thin Gaussians, with minimal impact on the computed depth.

With the computation of $t _ { o p t }$ in place, we can eliminate all popping artifacts and ensure perfect view-consistency by sorting all

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 5 of 17 -->

StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering

64:5

![Image block](images/radl2024_stopthepop_p5_b3.png)

![Image block](images/radl2024_stopthepop_p5_b4.png)

(a) w/o per-tile depth

(b) w/ naïve per-tile depth

Fig. 5. Comparison of 3DGS with and without per-tile depth calculation. Per-tile depth calculation lowers sorting errors $( \delta _ { m a x } = 4 . 0 1 , \delta _ { a v g } = 0 . 2 8 4$ compared to $\delta_{max} = 5.43, \delta_{avg} = 0.898$ . However, doing this without additional per-pixel sorting leads to artifacts at the tile borders.

Gaussians per ray by their $t _ { o p t }$ value. Unfortunately, even the simplest 3DGS reconstructions consist of tens of thousands of Gaussians, often leading to thousands of potentially contributing Gaussians per view ray. Furthermore, early ray termination cannot be performed before sorting, as it is dependent on the sort order. Even an optimized parallel per-ray sort on top of the original 3DGS tile-based rasterizer leads to slowdowns of more than 100×, not only making the approach impractical for real-time rendering, but also impeding optimization.

## 3.3 Per-tile Sorting and Local Resorting

Although it is not possible to describe $t _ { o p t }$ with a simple primitive for rasterization, we may still rely on the fact that $t _ { o p t }$ is smooth across neighboring rays. As such, the sorting order of neighboring rays should also be similar. Because sorting in 3DGS already happens with a combined tile/depth key, we could replace the global depth with an accurate per-tile depth value for each Gaussian, e.g., using the tile center ray for Eqn. (4). As can be seen in Fig. 5, using per-tile depth clearly leads to artifacts along the tile borders.

With that in mind, we propose a simple per-ray resorting extension. Instead of immediately blending the next Gaussian when walking through the tile list, we keep a small resorting window in registers. When loading a Gaussian, we evaluate its $t _ { o p t }$ and use insertion sort to place it in the resorting window. If the window overflows, we blend the sample with the smallest depth. This simple method follows the idea of 𝑘-buffers [Bavoil et al. 2007; Callahan et al. 2005] without fragment merging, which requires the Gaussians along a ray to be nearly-sorted. Although this sorting strategy is easy to implement, it already achieves good results for a resorting window of about 16 to 24, removing the majority of visible popping artifacts in our tested scenes. To confirm the improvement in blending order, we compute a per-ray sort error 𝛿: If two consecutive Gaussians are out of order, we accumulate their difference in 𝑡𝑜𝑝𝑡. We present a visual example in Fig. 4, with corresponding runtimes and 𝛿 in Tab. 1 — evidently, even though 𝛿 decreases with a larger resorting window, there is a non-negligible increase in runtime.

## 3.4 Hierarchical Rendering

Local resorting is already able to significantly improve the per-pixel sort order, which greatly reduces popping artifacts. To tackle the imposed performance overhead, we insert additional resorting levels

![Image block](images/radl2024_stopthepop_p5_b14.png)

(a) w/o tile-based culling

![Image block](images/radl2024_stopthepop_p5_b16.png)

(b) w/ tile-based culling

Fig. 6. Number of Gaussians per tile with and without tile-based culling for the Mip-NeRF 360 Garden scene. The average number of Gaussians per tile is reduced by ∼ 44%.

Table 1. Maximum sort error over all pixels and average sort error for two representative example views from Fig. 4. A full sort per ray increases rendering times (relative to 3DGS) by more than 100×. Local resorting with a sort window of 16 to 24 removes the majority of visible popping artifacts, yet increases rendering time 2 to 6×. Our hierarchical approach improves sort quality further and keeps processing time low. Note that a larger sorting window may lead to more Gaussians being fetched and thus our measurement of $\delta _ { \mathrm { m a x } }$ may increase with larger sort windows.

<table><tr><td rowspan="2" colspan="2"></td><td rowspan="2">3DGS</td><td rowspan="2">Full</td><td colspan="4">Resorting Window</td><td rowspan="2">Ours</td></tr><tr><td>4</td><td>8</td><td>16</td><td>24</td></tr><tr><td rowspan="3">Train</td><td> $\delta_{max}$ </td><td>28.445</td><td>0.000</td><td>5.867</td><td>3.882</td><td>3.544</td><td>4.580</td><td>0.575</td></tr><tr><td> $\delta_{avg}$ </td><td>3.688</td><td>0.000</td><td>0.124</td><td>0.045</td><td>0.014</td><td>0.007</td><td>0.003</td></tr><tr><td>time[ms]</td><td>1.00</td><td>142.03</td><td>1.21</td><td>1.66</td><td>2.70</td><td>4.22</td><td>0.92</td></tr><tr><td rowspan="3">Bonsai</td><td> $\delta_{max}$ </td><td>33.543</td><td>0.000</td><td>12.786</td><td>8.954</td><td>6.391</td><td>5.595</td><td>3.098</td></tr><tr><td> $\delta_{avg}$ </td><td>3.786</td><td>0.000</td><td>0.265</td><td>0.110</td><td>0.039</td><td>0.019</td><td>0.006</td></tr><tr><td>time[ms]</td><td>1.00</td><td>179.70</td><td>1.76</td><td>2.58</td><td>4.33</td><td>6.88</td><td>1.47</td></tr></table>

between tiles and individual threads, creating a sort hierarchy. In this way, we can share sorting efforts between neighboring rays, while incrementally refining the sort order as we move towards individual rays. By additionally culling non-contributing Gaussians at every level of the hierarchy, we can drastically reduce sorting costs. We propose a hierarchical rendering pipeline that relies on the innate memory and execution hierarchy of the GPU to minimize the number of memory access operations, as outlined in Fig. 7. For a fair comparison, we intentionally only alter the blend order of Gaussians and leave the other parts of 3DGS untouched, including the 2D splatting approximation from Zwicker et al. [2002].

Tile-based culling. We propose a fast tile-based culling approach that bounds Gaussians to exactly those tiles they contribute to. For each ray, Kerbl et al. [2023] disregard Gaussians with a contribution below $\epsilon _ { O }   =   1 / 2 5 5$ , which forms an exact culling condition. Like 3DGS, we start with an axis-aligned bounding rectangle using the largest eigenvalue of the 2D covariance matrix to determine which tiles may potentially be touched during both Preprocess and Duplication. This conservative estimate gives very large bounds for highly anisotropic Gaussians.

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 6 of 17 -->

64:6 • Radl and Steiner et al

![Image block](images/radl2024_stopthepop_p6_b2.png)

Fig. 7. Overview of the detailed steps in our pipeline. We add load balancing, tile culling and per-tile depth evaluation to the first two stages of 3DGS. Our hierarchical rasterizer utilizes three sorted queues, going from 4×4 tiles over 2×2 tiles to individual rays. The queues store only id and the tile’s $t _ { o p t }$ per Gaussian, while additional information is re-fetched from global memory on demand, and shared between threads via shuffle operations. Depending on the queue fill levels, we switch between different cooperative group sizes while ensuring the queues remain filled for effective sorting. Our pipeline achieves an overall sorting window of 25-72 elements.

For exact culling, we then calculate the point xˆ inside each tile 𝑋 that maximizes the 2D Gaussian’s contribution $G _ { 2 } ( \mathbf { x } )$ :

$$
\hat {\mathbf {x}} = \underset {\mathbf {x} \in X} {\arg \max} G _ {2} (\mathbf {x}) = \underset {\mathbf {x} \in X} {\arg \min} (\mathbf {x} - \mu_ {2}) ^ {T} \Sigma_ {2} ^ {- 1} (\mathbf {x} - \mu_ {2}).\tag{5}
$$

If $\mu _ { 2 } \in X \Rightarrow { \hat { \mathbf { x } } } = \mu _ { 2 }$ . If 𝜇<sub>2</sub> ∉ 𝑋, then xˆ must lie on one of the two tile edges closest to $\mu _ { 2 } ,$ due to Gaussians being monotonic along rays pointing away from $\mu _ { 2 }$ . We can then compute the maximum along those two edges (similar to Eqn. (4), but in 2D) and clamp the resulting values to obtain xˆ (see the Appendix B.1 for the full algorithm). Finally, we evaluate $G _ { 2 } ( \hat { \mathbf { x } } )$ to perform the comparison with $\epsilon _ { O } ,$ , which significantly reduces the number of Gaussians per tile (cf. Fig. 6).

Tile-depth Adjustment. For pre-sorting we require a representative $t _ { o p t }$ per tile. Intuitively, the center ray of the tile should be a valid compromise for all rays in the tile. However, this completely ignores the fact that a Gaussian in general does not uniformly contribute to all rays in a tile. Especially for small Gaussians whose main extent is approximately parallel to the view rays, the center ray may result in depth estimates far away from any contribution made by the Gaussian.

Arguably, the weighted integral $\begin{array} { r } { \int _ { X } G _ { 2 } ( \mathbf { x } ) t _ { o p t } } \end{array}$ (x)𝑑x is a better estimate. Yet, even a numerical approximation considering all rays in the tile 𝑋 is too compute-intensive. Thus, we approximate it with a single sample: the one with the highest weight within a tile, i.e., xˆ. Since xˆ was already calculated during culling, we only need to construct the corresponding ray to evaluate $t _ { o p t }$ . The optimized depth location reduces $( \delta _ { \mathrm { m a x } } , \delta _ { \mathrm { a v g } } )$ from (1.553, 0.006) to (0.575, 0.003) and (3.917, 0.014) to (3.098, 0.006) for the views in Tab. 1.

Load Balancing. Similar to other compute-mode rasterization methods, primitives that cover a large portion of the screen may become an issue if a single thread evaluates their coverage. For 3DGS, this is the case in the first two stages of the rendering pipeline, which operate on a per-Gaussian basis. For our method, tile-culling and per-tile depth calculations increase the workload of these stages, which further amplifies this problem.

To remedy this issue, we propose a two-stage load balancing scheme: In the first phase, each thread responsible for a Gaussian which covers fewer than a predetermined maximum number of tiles, performs its own processing. We empirically determined that a maximum of 32 tiles results in good performance. Most threads are typically idle after this initial phase. In the second phase, we distribute the remaining workload within each warp using warp voting and shuffle instructions. For close-ups and high-resolution rendering, where single Gaussians often cover a large portion of the screen, our approach can speed up Preprocess and Duplication by up to 10×.

Hierarchically Sorted Rendering. With the goal of establishing a hierarchical rendering pipeline, a naïve approach is to design one kernel per hierarchy level. However, such an approach would require communication via slow global memory between the levels and would prohibit early ray termination after reaching the opacity threshold. Thus, we opt for combining the final three levels of our rendering hierarchy in a single kernel, where multiple threads co operatively sort and manage shared queues, as detailed in Fig. 7. We use a large 4×4 tile-queue of 64 elements (managed by 16 threads), feeding into four eight-element 2×2 tile-queues. Finally, each 2×2

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 7 of 17 -->

StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering

64:7

tile-queue feeds into four per-pixel queues with four elements, managed by one thread each. For one 16×16 tile, we thus start 256 threads, allocate 16 4×4 tile-queues and 64 2×2 tile-queues in shared memory as well as one per-pixel queue per thread in registers. Each queue stores only the Gaussian’s id and the current level’s depth $t _ { o p t }$ . Additional information is loaded on demand from global memory and shared between threads of the hierarchical level via shuffle operations, $e . g .   \mu , \Sigma ^ { - 1 }$ during depth calculation, or $\mu _ { 2 } , \Sigma _ { 2 } ^ { - 1 }$ during culling and blending.

The queues follow a push methodology to keep queue fill rates as high as possible, ensuring that resorting remains effective. While 16 threads (a halfwarp) are assigned to each 4×4 tile-queue, we load and feed batches of 32 into two 4×4 tile-queues at once, allowing all threads within a warp to load data together. After loading, each thread performs tile-based culling (as described before, but for a 4×4 tile), followed by computing $t _ { o p t }$ . For culled Gaussians, we set $t _ { o p t } = \infty$ . Then, each halfwarp sorts the 32 newly loaded elements using Batcher Merge Sort [Batcher 1968] before writing them to the back of the 4×4 tile-queue. Typically, there are now two individually sorted parts in the 4×4 tile-queue: the already present elements (up to 32) and the newly added (up to 32). As both are sorted, we use efficient merge sort to combine them. Culled Gaussians are now at the back of the queue and can be discarded.

While there are more than 32 elements in the 4×4 tile-queue, we push batches of size 16 into the 2×2 tile-queue. Each thread in the halfwarp re-fetches the data needed for computing $t _ { o p t }$ for a single Gaussian. Each group of four threads then pushes sub-batches of size four into their 2×2 tile-queue, relying on shuffle instructions to update $t _ { o p t }$ for each 2×2 tile. We follow the same approach as before: we sort the four new entries according to depth, for which we use a simple coordination using shuffle instructions. We then use merge sort to combine the new elements with the existing ones.

After the 2×2 tile-queue is filled, we draw four elements from it and insert them into the per-pixel queue. Again, we batch-load the needed data using the four threads assigned to the respective 2×2 tile-queue, and again use shuffle instructions to communicate all relevant information for each Gaussian to all other threads in the 2×2 tile. We evaluate $t _ { o p t }$ and 𝛼 for the respective rays and insert the newly computed data into the per-pixel queue. If the Gaussian’s 𝛼 is below $\epsilon _ { O }$ , we simply discard it. As we add elements one by one into the per-pixel queue, we rely on simple insertion sort. Only if the per-pixel queue is full, we take one element from it and perform blending, freeing up space for the next element from the 2×2 tile-queue.

Due to the hierarchical structure, we effectively construct an overall sort window varying between 25 and 72, where the minimum is hit if the 4×4 tile-queue is drained down to 17 elements, with 4 elements remaining in the other queues. 72 elements are sorted if we fill the 4×4 tile-queue with 64 elements and then move 4 elements through the half-filled 2×2 tile-queue and the filled per-pixel queue. While our sort setup typically achieves better sorting than a simple per-thread sort window of 25, we may occasionally achieve worse sorting, as the higher-level queues are shared between threads.

The sizes of the three queues are variable, with some restrictions. The 4×4 tile-queue size is constrained to 32𝑛 + 32, with $n   \in   \mathbb { Z } ^ { + }$ as this enables efficient warp-wide merge sort. Similarly, the 2×2

tile-queue must be of size 4𝑚 + 4, with $m \in \mathbb { Z } ^ { + }$ , as it is managed by four threads. The per-pixel queue size can be chosen arbitrarily. We heuristically decided on $( 6 4 / 8 / 4 )$ for the three queue sizes, as this achieves a large enough sort window, while limiting shared memory requirements and register pressure, ultimately leading to better performance. We provide ablations for our chosen queue sizes and load balancing thresholds in Appendix E.

## 3.5 Backward Pass

Contrary to 3DGS, we perform gradient computations in front-to-back blending order, avoiding the large memory overhead required for storing per-pixel sorted Gaussians—which would be needed to restore the correct blending order.

Gradient computation in 3DGS, independent of direction, requires the final accumulated transmittance $\begin{array} { r } { T _ { N _ { \mathbf { r } } } = \prod _ { j = 1 } ^ { N _ { r } } \bigl ( 1 - \alpha _ { j } \bigr ) } \end{array}$ and the final per-pixel color 𝐶(r). To compute gradients for the 𝑖-th Gaussian along a view ray, we require the contribution of all subsequently blended Gaussians. Crucially, rather than accumulating the contribution of subsequent Gaussians back-to-front, we use subtraction and division, i.e.

$$
\begin{array}{c} \sum_ {j = i + 1} ^ {N _ {\mathrm{r}}} \mathbf {c} _ {j} \alpha_ {j} \prod_ {k = 1} ^ {j - 1} (1 - \alpha_ {k}) = C (\mathbf {r}) - C _ {i}, \\ \prod_ {k = i} ^ {N _ {\mathrm{r}}} (1 - \alpha_ {k}) = \frac {T _ {N _ {\mathrm{r}}}}{T _ {i}}, \end{array}\tag{6}
$$

(7)

where $C _ { i }$ is the accumulated output color including the 𝑖-th Gaussian in front-to-back order. As we perform the same rendering routine as in the forward pass, including early stopping, the backward pass is equally efficient. Note that this does not change the stability of the gradient computations; 3DGS also relies on a division. Arguably, our approach may even lead to more accurate gradients as the Gaussians blended first along a ray have a higher contribution to the final color and computing those first, will accumulate less floating point errors compared to reversing the computation.

It is imperative that the same exact sort order is used between forward and backward pass to ensure correct gradients. Like 3DGS, we keep the global sort order in memory, which ensures that potentially equal depth values do not lead to different sorting results. In our implementation, we use stable sorting routines throughout: Batcher Merge Sort [Batcher 1968] is stable by design, our merge sort routines rely on each thread’s rank to establish sort orders among equal depths, and our insertion sort is trivially stable.

## 4 EVALUATION

For evaluation, we follow Kerbl et al. [2023] and use 13 real-world scenes from Mip-NeRF 360 [Barron et al. 2022], Deep Blending [Hedman et al. 2018] and Tanks & Temples [Knapitsch et al. 2017].

Opacity Decay. A viable approach to reduce the total number of Gaussians after optimization is replacing 3DGS’s opacity reset with a standard Opacity Decay during training. Every 50 iterations, we multiply each Gaussian’s opacity with a constant $\epsilon _ { \mathrm { d e c a y } } = 0 . 9 9 9 5$ We find that this modification results in significantly fewer, but larger Gaussians, potentially causing exacerbated popping.

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 8 of 17 -->

64:8

• Radl and Steiner et al

Table 2. Image metrics for our method, 3DGS and related work. Results with dagger (†) are reproduced from Kerbl et al. [2023] to facilitate cross-method comparisons. Our quality is comparable to 3DGS. With Opacity Decay, our approach loses slightly less quality than 3DGS.

| Dataset |  | Deep B | lending |  | M | ip-NeRF | 360 Indoo | r | Mi | p-NeRF 3 | 60 Outdo | or |  | Tanks &amp; | Temples |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Metric | PSNR↑ | SSIM↑ | LPIPS↓ | FLIP ↓ | PSNR↑ | SSIM↑ | LPIPS↓ | FLIP ↓ | PSNR↑ | SSIM↑ | LPIPS↓ | FLIP ↓ | PSNR↑ | SSIM↑ | LPIPS↓ | FLIP ↓ |
| Mip-NeRF 360† | 29.40 | 0.900 | 0.245 | 0.138 | 31.57 | 0.914 | 0.182 | 0.088 | 24.42 | 0.691 | 0.286 | 0.170 | 22.22 | 0.758 | 0.256 | 0.232 |
| Instant-NGP (base)† | 23.62 | 0.797 | 0.423 | 0.258 | 28.65 | 0.840 | 0.281 | 0.120 | 22.63 | 0.536 | 0.444 | 0.203 | 21.72 | 0.723 | 0.330 | 0.245 |
| Instant-NGP (big)† | 24.96 | 0.817 | 0.390 | 0.222 | 29.14 | 0.863 | 0.241 | 0.114 | 22.75 | 0.567 | 0.403 | 0.200 | 21.92 | 0.745 | 0.304 | 0.241 |
| Plenoxels† | 23.09 | 0.794 | 0.425 | 0.244 | 24.84 | 0.765 | 0.366 | 0.182 | 21.69 | 0.513 | 0.467 | 0.229 | 21.09 | 0.719 | 0.344 | 0.262 |
| 3DGS | 29.46 | 0.900 | 0.247 | 0.131 | 30.98 | 0.922 | 0.189 | 0.094 | 24.59 | 0.727 | 0.240 | 0.167 | 23.71 | 0.845 | 0.178 | 0.199 |
| Ours | 29.86 | 0.904 | 0.234 | 0.127 | 30.62 | 0.921 | 0.186 | 0.099 | 24.60 | 0.728 | 0.235 | 0.167 | 23.21 | 0.843 | 0.173 | 0.216 |
| 3DGS (Opacity Decay) | 28.94 | 0.894 | 0.262 | 0.134 | 30.57 | 0.918 | 0.198 | 0.097 | 24.45 | 0.718 | 0.261 | 0.169 | 23.52 | 0.839 | 0.194 | 0.205 |
| Ours (Opacity Decay) | 29.84 | 0.905 | 0.241 | 0.126 | 30.03 | 0.917 | 0.194 | 0.103 | 24.46 | 0.722 | 0.254 | 0.169 | 23.18 | 0.839 | 0.184 | 0.214 |

## 4.1 Quantitative Evaluation

Image Metrics. For our quantitative evaluation, we report PSNR, SSIM, LPIPS [Zhang et al. 2018] and FLIP [Andersson et al. 2020] in Tab. 2. To facilitate cross-method comparisons, we reproduce the results from Kerbl et al. [2023] for Mip-NeRF 360 [Barron et al. 2022], Instant-NGP [Müller et al. 2022] and Plenoxels [Fridovich-Keil et al. 2022]. For Deep Blending and Mip-NeRF 360 Outdoor, we outperform 3DGS. For Tanks & Temples and Mip-NeRF 360 Indoor, our model performs slightly worse, which we attribute to 3DGS’s ability to fake view-dependent effects with popping. When enabling Opacity Decay, which results in ∼50% fewer Gaussians, our method retains more quality than 3DGS. In general, our approach performs comparably to 3DGS in terms of standard image quality metrics.

Popping. View inconsistencies between subsequent frames, such as popping, cannot be detected with standard image quality metrics. To detect such artifacts, we follow recent best practice in 3D style transfer [Nguyen-Phuoc et al. 2022] and measure the consistency between novel views and warped novel views with optical flow [Lai et al. 2018]. While ground-truth images or videos may seem attractive, they vary significantly in location and thus view-dependent effects or only exist for a small subset of our used datasets. For our method and 3DGS, we capture videos from three separate camera paths per scene, exhibiting both rotation and translation. We then directly warp each frame $\mathbf { F } _ { i }$ to a subsequent frame $\mathbf { F } _ { i + t }$ with offset 𝑡 using optical flow predictions from state-of-the-art RAFT [Teed and Deng 2020].

Measuring the error between the warped frame $\hat { \mathbf { F } } _ { i + t }$ and the rendered frame $\mathbf { F } _ { i + t }$ with MSE does not prove effective to detect popping artifacts (see Fig. 9). MSE tends to weigh small inaccuracies that originate from warping higher than popping artifacts. FLIP [Andersson et al. 2020] proves significantly more reliable in our experiments, as it approximates the difference perceived by humans when flipping between images — a scenario in which popping artifacts are particularly disturbing. For each frame, we calculate a consistency error $E _ { i + t } = \mathrm { \mathfrak { T } L I P } ( \hat { \mathbf { F } } _ { i + t } , \mathbf { F } _ { i + t } )$ . For each video, consisting of $N _ { F }$ frames, we then compute the mean FLIP error as

$$
\mathbb {T} \mathrm{LIP} _ {t} = \frac {1}{N _ {F} - t} \sum_ {i = 0} ^ {N _ {F} - t} E _ {i + t}.\tag{8}
$$

Note that the error metric includes a base error floor due to disocclusions under translation and correct view-dependent shading.

To mitigate these issues, we use an occlusion detection method from Ruder et al. [2016], do not consider the outermost 20 pixels, and subtract the per-pixel minimum $\mathrm { { \mathfrak { T } } L I P } _ { t }$ score — clearly, this does not perturb the inter-method differences.

We use 𝑡 = 1 and 𝑡 = 7 to measure short-range and long-range consistency, following Nguyen-Phuoc et al. [2022]. Tab. 3 shows our obtained results. The large margins, particularly for FLIP<sub>7</sub>, highlight that our method is more view-consistent than 3DGS. We argue that $\mathrm { { \mathfrak { T } } L I P _ { 7 } }$ is a more reliable metric, allowing errors due to popping to accumulate over multiple frames, as can be seen in Fig. 8. Please see the supplementary video for further evidence. With Opacity Decay, our approach achieves virtually identical results, indicating that our method can handle large Gaussians. For 3DGS, popping is significantly increased, indicating that 3DGS may increase the number of Gaussians to hide imperfections in the renderer, while our approach achieves comparable view-consistency scores.

Table 3. View-consistency metrics for videos. We measure FLIP<sub>𝑡</sub> for timesteps 𝑡 ∈ {1, 7} (lower is better). Our method outperforms 3DGS with and without Opacity Decay.

<table><tr><td rowspan="2">Dataset Metric</td><td colspan="2">DB</td><td colspan="2">M360 Indoor</td><td colspan="2">M360 Outdoor</td><td colspan="2">T&amp;T</td></tr><tr><td> $\mathcal{F}LIP_1$ </td><td> $\mathcal{F}LIP_7$ </td><td> $\mathcal{F}LIP_1$ </td><td> $\mathcal{F}LIP_7$ </td><td> $\mathcal{F}LIP_1$ </td><td> $\mathcal{F}LIP_7$ </td><td> $\mathcal{F}LIP_1$ </td><td> $\mathcal{F}LIP_7$ </td></tr><tr><td colspan="9">Without Opacity Decay</td></tr><tr><td rowspan="2">3DGS Ours</td><td>0.0061</td><td>0.0114</td><td>0.0069</td><td>0.0134</td><td>0.0083</td><td>0.0148</td><td>0.0102</td><td>0.0286</td></tr><tr><td>0.0053</td><td>0.0059</td><td>0.0060</td><td>0.0077</td><td>0.0085</td><td>0.0122</td><td>0.0076</td><td>0.0113</td></tr><tr><td colspan="9">With Opacity Decay</td></tr><tr><td rowspan="2">3DGS Ours</td><td>0.0063</td><td>0.0122</td><td>0.0072</td><td>0.0149</td><td>0.0083</td><td>0.0154</td><td>0.0107</td><td>0.0315</td></tr><tr><td>0.0052</td><td>0.0055</td><td>0.0060</td><td>0.0073</td><td>0.0083</td><td>0.0115</td><td>0.0076</td><td>0.0114</td></tr></table>

Depth Evaluation. 3DGS enables efficient extraction of depth values $\zeta \in \mathbb { R } _ { + }$ with volumetric rendering:

$$
\zeta = \sum_ {i = 1} ^ {N _ {\mathrm{r}}} \phi (\mu_ {i}; \mathbf {o}, \mathbf {d}) \alpha_ {i} \prod_ {j = 1} ^ {i - 1} (1 - \alpha_ {j}),\tag{9}
$$

where $\phi ( \cdot )$ describes the depth of a single Gaussian with location $\cdot \mu$ (in 3DGS’s case, $\phi ( \boldsymbol { \mu } ; \mathbf { o } , \mathbf { d } ) = \| \boldsymbol { \mu } - \mathbf { o } \| _ { 2 } )$ . Clearly, this depth estimate is dependent on the sort order, leading to problems for 3DGS’s approximate global sort. Our approach improves sort quality and places 2D splats at the points of maximum contribution $\begin{array} { r l } { ( \phi ( \mu ; \mathbf { o } , \mathbf { d } ) = } & { { } } \end{array}$ 𝑡𝑜𝑝𝑡 , cf. Eqn. (4)).

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 9 of 17 -->

StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering

64:9

Table 4. Depth-consistency metric $E _ { d e p t h }$ for 3D points $\bar { \mathcal { P } }$ from COLMAP [Schönberger and Frahm 2016] (lower is better). We report the mean results over all test set views. Our method outperforms 3DGS with and without Opacity Decay In total, we consider $| \bar { \mathcal { P } } | = 1 7 4 0 4$ points without opacity decay and $| \bar { \mathcal { P } } | = 1 1 3 0 6$ with opacity decay.

<table><tr><td>Dataset</td><td>DB</td><td>M360 Indoor</td><td>M360 Outdoor</td><td>T&amp;T</td><td>Average</td></tr><tr><td>Method</td><td colspan="5">Without Opacity Decay</td></tr><tr><td>3DGS</td><td>0.133</td><td>0.219</td><td>0.764</td><td>1.108</td><td>0.552</td></tr><tr><td>Ours</td><td>0.122</td><td>0.242</td><td>0.387</td><td>0.947</td><td>0.388</td></tr><tr><td colspan="6">With Opacity Decay</td></tr><tr><td>3DGS</td><td>0.095</td><td>0.127</td><td>0.637</td><td>0.967</td><td>0.447</td></tr><tr><td>Ours</td><td>0.073</td><td>0.168</td><td>0.408</td><td>0.916</td><td>0.361</td></tr></table>

We establish a metric to compare multi-view consistency in depth estimates, leveraging the sparse point cloud $\mathcal { P } = \{ \mathbf { p } _ { i } \}$ from COLMAP [Schönberger and Frahm 2016], which serves as initialization for 3DGS. $\mathrm { I f }   \mathbf { p } _ { i }$ is visible from a camera with position $\mathbf { o } ,$ we reconstruct the estimated location $\hat { \mathbf { p } } _ { i } = \mathbf { o } + \zeta \cdot \mathbf { d } ,$ with rendered depth $\zeta$ and view direction d of the corresponding pixel of $\mathbf { p } i$ . The black background for real-world scenes used by 3DGS enables cheating by not fully accumulating opacity and blending the background color. For a fair comparison, if any of the tested methods has $\bar { T _ { N _ { \mathrm { r } } } } > 1   \times   1 0 ^ { - 2 }$ for a point $\mathfrak { p } i ;$ we do not consider this point in our set of tested points $\bar { \mathcal { P } } .$ To minimize errors due to resolution, we render at the resolution used for COLMAP when computing $\hat { \mathbf { p } } _ { i }$ . Finally, we establish the depth error $E _ { d e p t h }$ as

$$
E _ {d e p t h} = \frac {1}{| \bar {\mathcal {P}} |} \sum_ {\mathbf {p} _ {i} \in \bar {\mathcal {P}}} \| \hat {\mathbf {p}} _ {i} - \mathbf {p} _ {i} \| _ {2}.\tag{10}
$$

We compute $E _ { d e p t h }$ for all test set views and report our results in Tab. 4. On average, our method achieves better scores than 3DGS, especially for the outdoor scenes of Mip-NeRF 360 [Barron et al. 2022]. Opacity decay leads to significantly fewer and larger Gaussians, resulting often in lower accumulated opacity and, consequently, more discarded points. Both methods achieve better results for $E _ { d e p t h }$ in this case, as these removed points often correspond to the background, where depth estimates are generally less precise.

## 4.2 Qualitative Evaluation

To complement our quantitative evaluation, we provide image comparisons in Fig. 10 and conduct a user study to verify the effectiveness of our approach and our proposed popping detection method.

4.2.1 User Study. 18 participants were presented with pairs of videos from our approach and 3DGS, following the same camera path. The captured scenes exhibit rotation, translation, as well as a combination of the two. We instructed the participants to rate the videos concerning view-consistency and popping artifacts. The participants then indicated whether either of the techniques performed better or equal, which we translated into scores $s \in$ (−1, 0, +1). On average, the results showed a clear preference for

Table 5. Performance timings for different configurations of our method and 3DGS. The number of Gaussians is roughly the same for all methods (scene average ∼2.98M). Applying Opacity Decay during training leads to ∼ 50% fewer Gaussians (scene average ∼1.54M).

<table><tr><td>Timings in ms</td><td>Preprocess</td><td>Duplicate</td><td>Sort</td><td>Render</td><td>Total</td></tr><tr><td></td><td colspan="5">Without Opacity Decay</td></tr><tr><td>3DGS</td><td>0.451</td><td>0.567</td><td>1.645</td><td>2.134</td><td>4.797</td></tr><tr><td>(A) Ours</td><td>0.649</td><td>0.437</td><td>0.301</td><td>3.599</td><td>4.986</td></tr><tr><td>(B) Ours w/o per-tile depth</td><td>0.658</td><td>0.283</td><td>0.301</td><td>3.599</td><td>4.841</td></tr><tr><td>(C) Ours w/o load balancing</td><td>0.847</td><td>2.059</td><td>0.415</td><td>3.505</td><td>6.827</td></tr><tr><td>(D) Ours w/o tile-based culling</td><td>0.610</td><td>0.479</td><td>1.180</td><td>5.346</td><td>7.614</td></tr><tr><td>(E) Ours w/o hier. culling</td><td>0.649</td><td>0.437</td><td>0.301</td><td>5.967</td><td>7.364</td></tr><tr><td></td><td colspan="5">With Opacity Decay</td></tr><tr><td>3DGS</td><td>0.215</td><td>0.378</td><td>0.626</td><td>1.059</td><td>2.276</td></tr><tr><td>Ours</td><td>0.366</td><td>0.223</td><td>0.161</td><td>2.227</td><td>2.976</td></tr></table>

our approach $( s _ { m e a n }   =   0 . 4 2 )$ , which is statistically significant according to Wilcoxon Signed Rank tests $( Z   =   2276.5,   p   <   .0001 )$ ). Details about the study can be found in Appendix D.

## 4.3 Performance and Ablation

In the following, we provide a detailed performance analysis for different configurations of our method. For our timings, we take all available COLMAP poses and interpolate a camera path between them (30 frames per pose), ensuring a variety of plausible viewpoints. All timings were measured for Full HD rendering and averaged over 4 runs, where we used an NVIDIA RTX 4090 with CUDA 11.8.

Performance for different configurations. We provide a performance comparison between 3DGS and our renderer with different configurations in Tab. 5. On average, the Render stage takes considerably longer for our hierarchical renderer (A-E) due to additional per-ray sorting. Not computing the per-tile depth (B) only marginally speeds up the Duplicate stage. Without our load balancing scheme (C), Duplicate takes 5× longer, as it is mostly dominated by very large Gaussians. Disabling tile-based culling (D) slightly accelerates Preprocess but leads to many more entries in the global sorting data structure, which increases Sort and Render times. Disabling hierarchical culling inside the render kernel (E) leads to a drastic increase in Render time as all Gaussians move through the en tire pipeline. Our final approach (A) with all optimizations achieves competitive runtimes on all evaluated scenes. Both methods see a drastic performance increase with Opacity Decay due to the significantly lower number of Gaussians—however, while our approach stays view-consistent, 3DGS shows even more popping artifacts.

Scene Comparison. Individual scenes with a similar number of Gaussians can exhibit sharp differences in runtime behavior. In Tab. 6 and Tab. 7, we show detailed timings and metrics for two exemplary scenes - Bonsai and Train - which display the largest inter-method differences in performance, despite their comparable number of Gaussians 𝑁. Even though the Train scene contains slightly fewer Gaussians than Bonsai, the average number of visible (inside the view-frustum) Gaussians $N _ { V } ,$ as well as their average screen-space size (indicated by avg./std. corresponding image tiles $N _ { t } )$ , is considerably larger.

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 10 of 17 -->

64:10 • Radl and Steiner et al

![Image block](images/radl2024_stopthepop_p10_b2.png)

Fig. 8. Visualization of our proposed popping detection method with detailed views inset. We warp view F𝑖 to $\hat { \mathbf { F } } _ { i + 1 } , \hat { \mathbf { F } } _ { i + 7 }$ using optical flow and use FLIP to measure errors between warped and non-warped views. While FLIP<sub>1</sub> is able to effectively detect popping artifacts, the obtained errors are only accumulated over a single frame. On the contrary, FLIP<sub>7</sub> is able to accumulate errors due to popping over multiple frames, making this metric more reliable. We increased contrast for the zoomed-in views to better highlight view-inconsistencies.

![Image block](images/radl2024_stopthepop_p10_b4.png)

Fig. 9. Comparison between FLIP and MSE to measure differences between rendered frames $\mathbf { F } _ { i + 1 }$ and warped frames $\hat { \mathbf { F } } _ { i + 1 }$ for 3DGS. Notably, using MSE does not yield large errors even when disturbing popping artefacts are encountered — FLIP, on the other hand, weighs such artifacts accordingly.

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 11 of 17 -->

StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering

64:11

![Image block](images/radl2024_stopthepop_p11_b3.png)

Fig. 10. Image comparisons of our method and 3DGS. In most configurations, our rendered images are virtually indistinguishable from 3DGS. For each scene, we show a result where our method performs better on the left, and a result where 3DGS performs better on the right.

Table 6. Performance timings for different configurations of our method and 3DGS for the exemplary scenes Bonsai & Train, which show contrary runtime behaviors. Times in ms for Full HD resolution.

<table><tr><td>Timings in ms</td><td>Preprocess</td><td>Duplicate</td><td>Sort</td><td>Render</td><td>Total</td></tr><tr><td colspan="6">Bonsai, ~1.25M Gaussians</td></tr><tr><td>3DGS</td><td>0.224</td><td>0.384</td><td>0.700</td><td>1.266</td><td>2.574</td></tr><tr><td>(A) Ours</td><td>0.295</td><td>0.321</td><td>0.173</td><td>2.610</td><td>3.399</td></tr><tr><td>(C) Ours w/o load balancing</td><td>0.467</td><td>1.920</td><td>0.272</td><td>2.592</td><td>5.251</td></tr><tr><td>(D) Ours w/o tile-based culling</td><td>0.282</td><td>0.331</td><td>0.554</td><td>3.680</td><td>4.846</td></tr><tr><td colspan="6">Train, ~1.05M Gaussians</td></tr><tr><td>3DGS</td><td>0.288</td><td>0.811</td><td>2.451</td><td>1.998</td><td>5.548</td></tr><tr><td>(A) Ours</td><td>0.409</td><td>0.495</td><td>0.270</td><td>3.052</td><td>4.225</td></tr><tr><td>(C) Ours w/o load balancing</td><td>0.647</td><td>2.336</td><td>0.333</td><td>2.899</td><td>6.215</td></tr><tr><td>(D) Ours w/o tile-based culling</td><td>0.323</td><td>0.542</td><td>1.550</td><td>5.054</td><td>7.469</td></tr></table>

Table 7. Metrics of our method and 3DGS for exemplary scenes Bonsai & Train, highlighting the effect of our tile-based culling. Columns include total vs. visible (in view-frustum) number of Gaussians (𝑁 vs. 𝑁<sub>𝑉</sub> ), as well as standard deviation and average number of 16×16 tiles covered by each visible Gaussian (𝑁<sub>𝑡</sub> ). We additionally include an approximate number of sort entries as 𝑁<sub>𝑉</sub> · avg(𝑁<sub>𝑡</sub> ).

| Scene Method | 𝑁 𝑁<sub>𝑉</sub> | avg(𝑁<sub>𝑡</sub>) | std(𝑁<sub>𝑡</sub>) | Sort Entries |
| --- | --- | --- | --- | --- |
| Ours | 1.26M 0.41M | 4.198 | 15.282 | 1.72M |
| Bonsai |  |  |  |  |
| 3DGS | 1.24M 0.40M | 10.801 | 52.236 | 4.36M |
| Ours | 1.05M 0.57M | 5.004 | 20.127 | 2.85M |
| Train |  |  |  |  |
| 3DGS | 1.08M 0.59M | 17.282 | 89.891 | 10.2M |

As larger Gaussian splats provide more opportunities for culling, our tile-based culling results in a larger reduction of avg. 𝑁<sub>𝑡</sub> for Train than Bonsai (∼3.5× vs. ∼2.5×). The resulting lower number of sort entries allows Train to amortize the slower Render stage with a much faster Sort, while Bonsai does not experience the same gains.

Backward Pass Performance. The relative performance of our backward Render pass compared to 3DGS is only 1.1× compared to the 1.5× we see for the forward Render stage. This is mostly due to the backward Render executing a large number of atomics, which

are equal between both approaches. Although the backward pass skips Duplicate and Sort—which are faster in our renderer—the final change in training time is only about 3%. The backward Render pass is only a single step in the entire training pipeline and thus, the overall time loss is close to negligible. Again, if we turn on Opacity Decay, training becomes proportionally faster.

## 5 CONCLUSION, LIMITATIONS, AND FUTURE WORK

In this paper, we took a closer look at the way 3D Gaussian Splatting orders splats during blending. A detailed analysis of the splat’s depth computation revealed the reason for popping artifacts of 3DGS: the computed depth is highly inconsistent under rotation. A per-ray depth computation which considers the highest contribution along the ray as optimal blending depth, removes all popping artifacts but is 100× more costly. With our hierarchical renderer, which includes multiple culling and resorting stages, we are only 1.04× slower than 3DGS on average. While it is difficult to identify popping in standard quality metrics, we provided a view-consistency metric based on optical flow and FLIP, which shows that our approach significantly reduces popping. We could also confirm this fact in a user study and provided an additional metric confirming increased view-consistency and more accurate depth estimates for our method. Furthermore, our approach remains view-consistent even when constructing the scene with half the Gaussians; for which 3DGS shows a significant increase in popping artifacts. As such, our approach can reduce memory by 2× and render times by 1.6× compared to 3DGS in this configuration, while reducing popping artifacts and achieving virtually indistinguishable quality.

While our approach typically removes all artifacts in our tests, resorting does not guarantee the right blend order, and thus could still lead to popping or flickering for very complex geometric relationships. Furthermore, our approach still ignores overlaps between Gaussians along the view ray. A fully correct volume rendering of Gaussians may not only remove artifacts completely but could lead to better scene reconstructions—a direction certainly worth exploring in the future. Both our renderer and our optimizations for 3DGS are publicly available at [https://github.com/r4dl/StopThePop.](https://github.com/r4dl/StopThePop)

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 12 of 17 -->

64:12 • Radl and Steiner et al

## REFERENCES

Pontus Andersson, Jim Nilsson, Tomas Akenine-Möller, Magnus Oskarsson, Kalle Åström, and Mark D. Fairchild. 2020. FLIP: A Difference Evaluator for Alternating Images. Proceedings of the ACM on Computer Graphics and Interactive Techniques 3, 2, Article 15 (2020), 23 pages.

Jonathan T. Barron, Ben Mildenhall, Matthew Tancik, Peter Hedman, Ricardo Martin-Brualla, and Pratul P. Srinivasan. 2021. Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields. In Proceedings of the IEEE/CVF International Conference on Computer Vision.

Jonathan T. Barron, Ben Mildenhall, Dor Verbin, Pratul P. Srinivasan, and Peter Hedman. 2022. Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition.

Jonathan T. Barron, Ben Mildenhall, Dor Verbin, Pratul P. Srinivasan, and Peter Hedman. 2023. Zip-NeRF: Anti-Aliased Grid-Based Neural Radiance Fields. In Proceedings of the IEEE/CVF International Conference on Computer Vision.

Kenneth E. Batcher. 1968. Sorting Networks and Their Applications. In Proceedings of the Spring Joint Computer Conference.

Louis Bavoil, Steven P. Callahan, Aaron Lefohn, João L. D. Comba, and Cláudio T. Silva. 2007. Multi-fragment effects on the GPU using the k-buffer. In Proceedings of the ACM SIGGRAPH Symposium on Interactive 3D Graphics and Games.

Michael Broxton, John Flynn, Ryan Overbeck, Daniel Erickson, Peter Hedman, Matthew DuVall, Jason Dourgarian, Jay Busch, Matt Whalen, and Paul Debevec. 2020. Immersive Light Field Video with a Layered Mesh Representation. ACM Transactions on Graphics 39, 4, Article 86 (2020), 15 pages.

Daniel J. Butler, Jonas Wulff, Garrett B. Stanley, and Michael J. Black. 2012. A Naturalistic Open Source Movie for Optical Flow Evaluation. In Proceedings of the European Conference on Computer Vision.

Steven P. Callahan, Milan Ikits, João L. D. Comba, and Cláudio T. Silva. 2005. Hardware-Assisted Visibility Sorting for Unstructured Volume Rendering. IEEE Transactions on Visualization and Computer Graphics 11, 3 (2005), 285–295.

Loren Carpenter. 1984. The A-buffer, an Antialiased Hidden Surface Method. In ACM SIGGRAPH Conference Proceedings.

Anpei Chen, Zexiang Xu, Andreas Geiger, Jingyi Yu, and Hao Su. 2022. TensoRF: Tensorial Radiance Fields. In Proceedings of the European Conference on Computer Vision.

Yiwen Chen, Zilong Chen, Chi Zhang, Feng Wang, Xiaofeng Yang, Yikai Wang, Zhongang Cai, Lei Yang, Huaping Liu, and Guosheng Lin. 2023. GaussianEditor: Swift and Controllable 3D Editing with Gaussian Splatting. arXiv preprint arXiv:2311.14521 (2023).

Matthew Eldridge, Homan Igehy, and Pat Hanrahan. 2000. Pomegranate: A Fully Scalable Graphics Architecture. In ACM SIGGRAPH Conference Proceedings.

Jiemin Fang, Junjie Wang, Xiaopeng Zhang, Lingxi Xie, and Qi Tian. 2023. GaussianEditor: Editing 3D Gaussians Delicately with Text Instructions. arXiv preprint arXiv:2311.16037 (2023).

Sara Fridovich-Keil, Alex Yu, Matthew Tancik, Qinhong Chen, Benjamin Recht, and Angjoo Kanazawa. 2022. Plenoxels: Radiance Fields without Neural Networks. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition.

Peter Hedman, Julien Philip, True Price, Jan-Michael Frahm, George Drettakis, and Gabriel Brostow. 2018. Deep Blending for Free-viewpoint Image-based Rendering. ACM Transactions on Graphics 37, 6, Article 257 (2018), 15 pages.

Ajay Jain, Ben Mildenhall, Jonathan T. Barron, Pieter Abbeel, and Ben Poole. 2022. Zero-Shot Text-Guided Object Generation with Dream Fields. (2022).

Clément Jambon, Bernhard Kerbl, Georgios Kopanas, Stavros Diolatzis, George Drettakis, and Thomas Leimkühler. 2023. NeRFshop: Interactive Editing of Neural Radiance Fields. Proceedings of the ACM on Computer Graphics and Interactive Techniques 6, 1, Article 1 (2023), 21 pages.

Brian Karis, Rune Stubbe, and Graham Wihlidal. 2021. A Deep Dive into Nanite Virtualized Geometry. In ACM SIGGRAPH Conference Proceedings.

Michael Kenzel, Bernhard Kerbl, Dieter Schmalstieg, and Markus Steinberger. 2018. A High-Performance Software Graphics Pipeline Architecture for the GPU. ACM Transactions on Graphics 37, 4, Article 140 (2018), 15 pages.

Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, and George Drettakis. 2023. 3D Gaussian Splatting for Real-Time Radiance Field Rendering. ACM Transactions on Graphics 42, 4 (2023).

Arno Knapitsch, Jaesik Park, Qian-Yi Zhou, and Vladlen Koltun. 2017. Tanks and Temples: Benchmarking Large-Scale Scene Reconstruction. ACM Transactions on Graphics 36, 4, Article 78 (2017), 13 pages.

Zhengfei Kuang, Fujun Luan, Sai Bi, Zhixin Shu, Gordon Wetzstein, and Kalyan Sunkavalli. 2023. PaletteNeRF: Palette-based Appearance Editing of Neural Radiance Fields. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition.

Wei-Sheng Lai, Jia-Bin Huang, Oliver Wang, Eli Shechtman, Ersin Yumer, and Ming-Hsuan Yang. 2018. Learning Blind Video Temporal Consistency. In Proceedings of the European Conference on Computer Vision.

Samuli Laine and Tero Karras. 2011. High-Performance Software Rasterization on GPUs. In Proceedings of the ACM SIGGRAPH Symposium on High Performance Graphics.

Fang Liu, Meng-Cheng Huang, Xue-Hui Liu, and En-Hua Wu. 2010. FreePipe: a Programmable Parallel Rendering Architecture for Efficient Multi-Fragment Effects. In Proceedings of the ACM SIGGRAPH Symposium on Interactive 3D Graphics and Games.

Jonathon Luiten, Georgios Kopanas, Bastian Leibe, and Deva Ramanan. 2024. Dynamic 3D Gaussians: Tracking by Persistent Dynamic View Synthesis. In International Conference on 3D Vision.

Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, and Ren Ng. 2020. NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis. In Proceedings of the European Conference on Computer Vision.

Thomas Müller, Alex Evans, Christoph Schied, and Alexander Keller. 2022. Instant Neural Graphics Primitives with a Multiresolution Hash Encoding. ACM Transactions on Graphics 41, 4, Article 102 (2022), 15 pages.

Thu Nguyen-Phuoc, Feng Liu, and Lei Xiao. 2022. SNeRF: Stylized Neural Implicit Representations for 3D Scenes. ACM Transactions on Graphics 41, 4, Article 142 (2022), 11 pages.

Keunhong Park, Utkarsh Sinha, Jonathan T. Barron, Sofien Bouaziz, Dan B Goldman, Steven M. Seitz, and Ricardo Martin-Brualla. 2021. Nerfies: Deformable Neural Radiance Fields. Proceedings of the IEEE/CVF International Conference on Computer Vision.

Anjul Patney, Stanley Tzeng, Kerry A Seitz Jr, and John D Owens. 2015. Piko: A Framework for Authoring Programmable Graphics Pipelines. ACM Transactions on Graphics 34, 4, Article 147 (2015), 13 pages.

Ben Poole, Ajay Jain, Jonathan T. Barron, and Ben Mildenhall. 2022. DreamFusion: Textto-3D using 2D Diffusion. Proceedings of the International Conference on Learning Representations.

Albert Pumarola, Enric Corona, Gerard Pons-Moll, and Francesc Moreno-Noguer. 2020. D-NeRF: Neural Radiance Fields for Dynamic Scenes. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition.

Amit Raj, Srinivas Kaza, Ben Poole, Michael Niemeyer, Ben Mildenhall, Nataniel Ruiz, Shiran Zada, Kfir Aberman, Michael Rubenstein, Jonathan Barron, Yuanzhen Li, and Varun Jampani. 2023. DreamBooth3D: Subject-Driven Text-to-3D Generation. In Proceedings of the IEEE/CVF International Conference on Computer Vision.

Manuel Ruder, Alexey Dosovitskiy, and Thomas Brox. 2016. Artistic Style Transfer for Videos. In Proceedings of the German Conference on Pattern Recognition.

Marco Salvi, Jefferson Montgomery, and Aaron Lefohn. 2011. Adaptive Transparency. In Proceedings of the ACM SIGGRAPH Symposium on High Performance Graphics.

Marco Salvi and Karthik Vaidyanathan. 2014. Multi-Layer Alpha Blending. In Proceedings of the ACM SIGGRAPH Symposium on Interactive 3D Graphics and Games.

Johannes L. Schönberger and Jan-Michael Frahm. 2016. Structure-from-Motion Revisited. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition.

Markus Schütz, Bernhard Kerbl, and Michael Wimmer. 2021. Rendering Point Clouds with Compute Shaders and Vertex Order Optimizationn. Computer Graphics Forum 40, 4 (2021), 115–126.

Larry Seiler, Doug Carmean, Eric Sprangle, Tom Forsyth, Michael Abrash, Pradeep Dubey, Stephen Junkins, Adam Lake, Jeremy Sugerman, Robert Cavin, et al. 2008. Larrabee: A Many-Core x86 Architecture for Visual Computing. ACM Transactions on Graphics 27, 3 (2008), 1–15.

Noah Snavely, Steven M. Seitz, and Richard Szeliski. 2006. Photo Tourism: Exploring Photo Collections in 3D. ACM Transactions on Graphics 25, 3 (2006), 835–846.

Jiaxiang Tang, Xiaokang Chen, Jingbo Wang, and Gang Zeng. 2022. Compressiblecomposable NeRF via Rank-residual Decomposition. Advances in Neural Information Processing Systems.

Jiaxiang Tang, Jiawei Ren, Hang Zhou, Ziwei Liu, and Gang Zeng. 2023. DreamGaussian: Generative Gaussian Splatting for Efficient 3D Content Creation. arXiv preprint arXiv:2309.16653 (2023).

Zachary Teed and Jia Deng. 2020. RAFT: Recurrent All-Pairs Field Transforms for Optical Flow. In Proceedings of the European Conference on Computer Vision.

Stanley Tzeng, Anjul Patney, and John D Owens. 2010. Task Management for Irregular-Parallel Workloads on the GPU. In Proceedings of the ACM SIGGRAPH Symposium on High Performance Graphics.

R. F. Woolson. 2008. Wilcoxon Signed-Rank Test. John Wiley & Sons, Ltd, 1–3.

Guanjun Wu, Taoran Yi, Jiemin Fang, Lingxi Xie, Xiaopeng Zhang, Wei Wei, Wenyu Liu, Qi Tian, and Wang Xinggang. 2023. 4D Gaussian Splatting for Real-Time Dynamic Scene Rendering. arXiv preprint arXiv:2310.08528 (2023).

Chris Wyman. 2016. Exploring and Expanding the Continuum of OIT Algorithms. In Proceedings of the ACM SIGGRAPH Symposium on High Performance Graphics.

Taoran Yi, Jiemin Fang, Junjie Wang, Guanjun Wu, Lingxi Xie, Xiaopeng Zhang, Wenyu Liu, Qi Tian, and Xinggang Wang. 2023. GaussianDreamer: Fast Generation from Text to 3D Gaussians by Bridging 2D and 3D Diffusion Models. arXiv preprint arXiv:2310.08529 (2023).

Zehao Yu, Anpei Chen, Binbin Huang, Torsten Sattler, and Andreas Geiger. 2023. Mip-Splatting: Alias-free 3D Gaussian Splatting. arXiv preprint arXiv::2311.16493 (2023).

Richard Zhang, Phillip Isola, Alexei A Efros, Eli Shechtman, and Oliver Wang. 2018. The Unreasonable Effectiveness of Deep Features as a Perceptual Metric. In Proceedings

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 13 of 17 -->

StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering

64:13

Kun Zhou, Qiming Hou, Zhong Ren, Minmin Gong, Xin Sun, and Baining Guo. 2009. RenderAnts: Interactive Reyes Rendering on GPUs. ACM Transactions on Graphics 28, 5 (2009), 1–11.

Wojciech Zielonka, Timo Bolkart, and Justus Thies. 2023. Instant Volumetric Head Avatars. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition.

Matthias Zwicker, Hanspeter Pfister, Jeroen Van Baar, and Markus Gross. 2002. EWA Splatting. IEEE Transactions on Visualization and Computer Graphics 8, 3 (2002), 223–238.

## A DERIVING DEPTH FOR 3D GAUSSIANS ALONG A RAY

In order to get an accurate depth estimate for our sort order of 3D Gaussians along a view ray $\mathbf { r } ( t ) \; = \; \mathbf { o }   +   t \mathbf { d }$ , we compute the $t _ { o p t }$ which maximizes the Gaussian’s contribution along the ray, i.e. arg max<sub>𝑡</sub> $G ( \mathbf { r } ( t ) )$ . This optimum can be found through the following derivation:

$$
\left| \begin{array}{l} \frac {d G (\mathbf {r} (t))}{d t} = - \frac {1}{2} G (\mathbf {r} (t)) \cdot \left((\mathbf {r} (t) - \mu) \Sigma^ {- 1} \mathbf {d} + \mathbf {d} ^ {T} \Sigma^ {- 1} (\mathbf {r} (t) - \mu)\right) \\ = - \frac {1}{2} G (\mathbf {r} (t)) \cdot \left(2 \cdot \mathbf {d} ^ {T} \Sigma^ {- 1} (\mathbf {r} (t) - \mu)\right) \\ = - G (\mathbf {o} + t \mathbf {d}) \cdot \left(\mathbf {d} ^ {T} \Sigma^ {- 1} (\mathbf {o} + t \mathbf {d} - \mu)\right) \stackrel {!} {=} 0 \\ \Rightarrow \mathbf {d} ^ {T} \Sigma^ {- 1} (\mathbf {o} + t \mathbf {d} - \mu) = 0 \\ \Rightarrow \mathbf {d} ^ {T} \Sigma^ {- 1} \mathbf {d} \cdot t + \mathbf {d} ^ {T} \Sigma^ {- 1} (\mathbf {o} - \mu) = 0 \\ t _ {o p t} = \frac {\mathbf {d} ^ {T} \Sigma^ {- 1} (\mu - \mathbf {o})}{\mathbf {d} ^ {T} \Sigma^ {- 1} \mathbf {d}}. \end{array} \right. \tag {1}\tag{11}
$$

The simplification from the first to the second line relies on the fact that $\Sigma ^ { - 1 }$ is symmetric and thus both expressions are identical. $\Sigma ^ { - 1 }$ can be efficiently computed:

$$
\Sigma^ {- 1} = \left(R S S R ^ {T}\right) ^ {- 1} = R S ^ {- 1} S ^ {- 1} R ^ {T} = R \left( \begin{array}{c c c} s _ {x} ^ {- 2} & 0 & 0 \\ 0 & s _ {y} ^ {- 2} & 0 \\ 0 & 0 & s _ {z} ^ {- 2} \end{array} \right) R ^ {T}.
$$

## B ADDITIONAL IMPLEMENTATION DETAILS

This section contains a more thorough description of our implementation and various optimization strategies to make our hierarchical rasterizer viable for real-time rendering.

## B.1 Tile-based Culling

In Algorithm 1, we describe how to find the maximally contributing point xˆ of a 2D Gaussian $G _ { 2 }$ parameterized by $\mu _ { 2 } , \Sigma _ { 2 } ^ { - 1 }$ inside an axis-aligned tile 𝑋. $\mathrm { H }   \mu _ { 2 }$ lies inside $X ,$ then it is consequently also the maximum. Otherwise, the maximum has to lie on one of the two edges that are reachable from $\mu _ { 2 }$ . Those are the two edges that originate from the tile corner point pˆ closest to $\mu _ { 2 }$ . We can then find the optimum by performing the same computation as in Eqn. (11), but in 2D. By checking if $\mu _ { 2 _ { x } } , \mu _ { 2 _ { y } }$ are in range of the tile in $x , y$ direction, as well as clamping the values of $t _ { x } , t _ { y }$ to [0, 1], we ensure that the final point will lie on one of these two edges. The fact that the 𝑦 coordinate of $\mathbf { d } _ { x }$ and the 𝑥 coordinate of $\mathbf { d } _ { y }$ are zero, allows for further simplifications in the final implementation.

<div class="docvortex-algorithm" style="white-space: pre-wrap; font-family:monospace;">
ALGORITHM 1: Finding maximum of 2D Gaussian inside AABB $\mu_2, \Sigma_2^{-1}$: mean and inverse covariance matrix of 2D Gaussian $G_2$ $x_{\min}, x_{\max}, y_{\min}, y_{\max}$: AABB dimensions
Data: $X = \{\forall \mathbf{x} \in \mathbb{R}^2 | x_{\min} \leq \mathbf{x}_x \leq x_{\max} \land y_{\min} \leq \mathbf{x}_y \leq y_{\max}\}$
Result: $\hat{\mathbf{x}} = \arg \min_{\mathbf{x} \in X} (\mathbf{x} - \mu_2)^T \Sigma_2^{-1}(\mathbf{x} - \mu_2)$
if $\mu_2 \in X$ then
    $\hat{\mathbf{x}} \leftarrow \mu_2$;
else
    $\hat{\mathbf{p}} \leftarrow$ Corner closest to $\mu_2$;
    $\mathbf{d}_x, \mathbf{d}_y \leftarrow$ vectors to next AABB corners in $x$, $y$ direction;
    $t_x, t_y \leftarrow 0$;
    if $\mu_{2x} &lt; x_{\min} \lor \mu_{2x} &gt; x_{\max}$ then
        $t_y \leftarrow \min \left(1, \max \left(0, \frac{\mathbf{d}_y^{\mathrm{T}} \Sigma_2^{-1}(\mu_2 - \hat{\mathbf{p}})}{\mathbf{d}_y^{\mathrm{T}} \Sigma_2^{-1} \mathbf{d}_y}\right)\right)$;
    end
    if $\mu_{2y} &lt; y_{\min} \lor \mu_{2y} &gt; y_{\max}$ then
        $t_x \leftarrow \min \left(1, \max \left(0, \frac{\mathbf{d}_x^{\mathrm{T}} \Sigma_2^{-1}(\mu_2 - \hat{\mathbf{p}})}{\mathbf{d}_x^{\mathrm{T}} \Sigma_2^{-1} \mathbf{d}_x}\right)\right)$;
    end
    $\hat{\mathbf{x}} \leftarrow \hat{\mathbf{p}} + t_x \mathbf{d}_x + t_y \mathbf{d}_y$;
end
</div>

## B.2 Tighter Bounding of 2D Gaussians

For computing the bounding rectangle of touched tiles on screen, Kerbl et al. [2023] first bound each 2D Gaussian with a circle of radius $r = 3 \cdot \lambda _ { \operatorname* { m a x } }$ , where $\lambda _ { \mathrm { m a x } }$ denotes the largest eigenvalue of the 2D covariance matrix $\Sigma _ { 2 }$ . They use a constant factor $t _ { O } = 3$ as a bound for a Gaussian, effectively clipping it at 0.3% of its peak value. We instead calculate an exact bound by considering the Gaussian’s actual opacity value 𝛼 and compute $t _ { O } = \sqrt { 2 \log ( \frac { \alpha } { \epsilon _ { O } } ) } ,$ , which is itself upper bounded by $t _ { O \mathrm { m a x } } \approx 3 . 3 2 9 0$ (since 𝛼 ∈ [0, 1]). Therefore, we conclude that the bound of $t _ { O } = 3$ by Kerbl et al. [2023] was actually chosen too small for the opacity threshold $\epsilon _ { O } \; = \; { \textstyle { \frac { 1 } { 2 5 5 } } }$ used in the renderer. Additionally, our calculated bound allows us to fit a tighter circular bound around Gaussians with $\alpha < 1$

## B.3 Global Sort

Using a giant global sort for all combined (tile/depth) keys seems wasteful. Sorting would be more efficient if the entries of each tile would be sorted individually, using a global partitioned sort. However, this requires all the entries of a tile to be continuous in memory, with each tile knowing the range of its respective entries. We can create such a setup by counting the number of entries per tile during the Preprocess stage with an atomic counter per tile and computing tile ranges with a prefix sum. In the Duplication stage, another atomic counter per tile can be used to retrieve offsets for each entry inside this range. While this reduces sorting costs to less than half in our experiments, the allocation using atomic operations adds an overhead that is about equal to the time saved in sorting. Thus, we opted to keep the original sorting approach.

## B.4 Per-stage details

Preprocess and Duplication. Similarly to 3DGS, we also prepare common values for each Gaussian during Preprocess: We compute

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 14 of 17 -->

64:14

Radl and Steiner et al

and store $G _ { 2 }$ for every Gaussian, evaluate Spherical Harmonics relying on the direction from the camera to the Gaussians center as view direction, establish $\Sigma ^ { - 1 }$ relying on the specifics of 𝑅 and 𝑆, and precompute $\Sigma ^ { - 1 } ( \boldsymbol { \mu } - \mathbf { o } )$ for the current camera position o, packing the 6 unique coefficients of $\Sigma ^ { - 1 }$ with the precomputed vector for efficient loading.

We found that activating “fast math” in combination with rescheduling in Preprocess and Duplication may lead to slightly different ordering of floating point instructions. Thus, there may be slight differences in the number of tiles contributed by each Gaussian. As we already store the number of tiles contributed by every Gaussian for memory allocation, we rely on the following simple solution: during Preprocess we use a slightly lower threshold for culling, providing a slightly more conservative bound. During Duplication, we recheck whether the right number of tile contributions have been written. If this is not the case, we simply add a dummy entry that sets a higher tile id and depth to ∞. For training, we suggest to disable “fast math”, ensuring that gradient computations are as stable as possible. However, for rendering using “fast math” may be beneficial to squeeze even more performance.

For load balancing in both Preprocess and Duplication, we rely on the ballot instruction to determine which threads still require computations. We use shuffle operations to broadcast already loaded register values, so each thread can perform culling and depth evaluation without additional memory loads. We assign successive potential tiles to each thread according to their thread rank in the warp. For every iteration of the inner loop we again ballot to determine which threads in the warp still want to write to a tile, i.e. did not cull away their tile. We can then mask all ballot bits of lower ranked threads, compute their sum via popc and determine the write location for each thread.

Render. Our hierarchical rasterizer is constructed from many steps, which are interleaved in their operation. Due to the setup, there are special optimizations we can perform based on the current state of the pipeline: The pipeline starts out with an initialize phase for each level, establishing a minimal fill level for each where no merge sort is performed. In this phase, blending is not taking place either. During the main operation, we ensure that we maintain a minimal fill level for each queue. Finally, the pipeline is drained where the number of elements in each queue will eventually drop to zero. Furthermore, we know that certain parts of the pipeline will always be executed a specific number of times. The combination of these facts allows for a significant amount of specialization and loop unrolling. However, we found that excessive code specialization and unrolling leads to a significant amount of stalls due to instruction fetches. Thus, relying on less specialized code is overall beneficial although up to 15% more instructions are required for the increased control logics.

For Batcher Merge Sort, we use a trivial implementation adapted from the NVIDIA CUDA examples<sup>1</sup>. For Merge Sort, we use a custom implementation that is adapted for our use case: each thread holds the to-be-inserted elements in registers and runs a binary search through the existing array to find where the new element should be placed with respect to the existing data. In combination

with the thread’s rank, this yields the position in the final sorted array. Still, we need to update the position of the existing data. To this end, we switch the roles and memory locations of both data arrays and perform the exact same binary search, only switching strict comparison to non-strict comparison. Also note that we are operating on a small fixed size array, enabling loop unrolling and leading to very few memory accesses. For local presorting of four elements, we simply run three circular shuffles, revealing all ele ments among all threads to directly yield the right order via simple counting of smaller elements. In our tests this was faster than any other method.

As we reevaluate $t _ { o p t }$ many times for many different ray directions, constructing and normalizing view rays can become a bottleneck. Precomputing all view directions a single thread will need throughout the hierarchy (two for the 4×4 tile-queue, one for the 2×2 tile-queue and one for the per-pixel queue) would result in significant register pressure. Fortunately, the same directions are needed by different threads and we can store the directions in shared memory and fetch them on demand, leading to significant perfor mance improvements.

Obviously, we need to take some care to ensure that threads do not diverge, especially, we can only retire queues if all threads in the associated tile are done. Also note that the loaded batches remain in registers for a potentially long time — a 16 batch loaded by a half warp remains in registers while four 4-thread batches are loaded and potentially up to 16 elements are blended. However, when the 32-wide batch is loaded, no smaller batches are kept alive, somewhat reducing register pressure.

## C POPPING DETECTION METRIC

For our popping detection metric, we use the RAFT [Teed and Deng 2020] model pre-trained on SINTEL [Butler et al. 2012], which is publicly available. We also compute the optical flow separately for each method for a fair comparison. We follow Nguyen-Phuoc et al. [2022] with timesteps $t   \in   \{ 1 , 7 \}$ to measure short-range and long-range view-consistency, respectively. We provide an additional ablation study for different $t \in \{ 3 , 5 , 9 \}$ in Tab. 8, with three camera paths for the Garden scene of Mip-NeRF 360 [Barron et al. 2022]. As can be seen, the consistency error grows almost linearly with increasing 𝑡. Further, our method outperforms 3DGS for all timesteps.

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>1</sup>[https://github.com/NVIDIA/cuda-samples](https://github.com/NVIDIA/cuda-samples)</span></small>

Table 8. FLIP<sub>𝑡</sub> comparison for 𝑡 ∈ {1, 3, 5, 7, 9} for three camera paths for the Garden scene of Mip-NeRF 360 [Barron et al. 2022]. As can be seen, our method outperforms 3DGS for each 𝑡, and FLIP<sub>𝑡</sub> scales almost linearly with increasing 𝑡.

| Method | FLIP<sub>1</sub> | FLIP<sub>3</sub> | FLIP<sub>5</sub> | FLIP<sub>7</sub> | FLIP<sub>9</sub> |
| --- | --- | --- | --- | --- | --- |
| 3DGS | 0.0080 | 0.0109 | 0.0134 | 0.0157 | 0.0180 |
| Ours | 0.0075 | 0.0080 | 0.0082 | 0.0085 | 0.0087 |

Per-Frame Results. To gain more insight into our proposed popping detection metric, we additionally provide per-frame plots for a video of the Garden scene in Fig. 11. As can clearly be seen, there are significant peaks in $\mathrm { { \mathfrak { T } } L I P _ { 1 } }$ for 3DGS, caused by popping. Our

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 15 of 17 -->

StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering

64:15

method, on the other hand, does not suffer from such issues. When analyzing the plot for FLIP<sub>7</sub>, 3DGS obtains significantly higher error rates — using $t = 7$ accumulates artifacts over several iterations, therefore more clearly indicating popping when averaged over the complete video sequence.

![Image block](images/radl2024_stopthepop_p15_b4.png)

Fig. 11. Per-frame FLIP<sub>𝑡</sub> scores for $t \in \{ 1 , 7 \}$ for a complete video sequence from the Garden scene. Popping in 3DGS causes significant peaks, as can be seen in the results for F LIP<sub>1</sub>.

3DGS Cheating. To support our claim that 3DGS indeed cheats with popping to produce view-dependent effects, we provide additional images in Fig. 12. We choose a ground-truth view from Train and Garden and sample a random rotation from $[ - 0 . 5 ^ { \circ } , 0 . 5 ^ { \circ } ] ^ { 3 }$ which we apply to the ground-truth camera rotation. Subsequently, we compare the rendering from the ground-truth camera pose and the rendering from the slightly rotated pose for 3DGS, as well as our method.

As can be seen, our approach produces more consistent results under view rotation. Due to 3DGS’s popping, the appearance changes significantly around test set views, which results in better image metrics in some configurations. In Fig. 12, we increase contrast for the zoomed-in views and provide FLIP comparisons to more clearly illustrate view inconsistencies.

## D USER STUDY

For our user study we recruited 18 participants from a local university, age 26 to 34, all normal or corrected vision, no color blindness. All participants indicated that they are familiar with computer graphics (3-5 on a 5-point Likert scale).

We pre-recorded camera paths for all 13 scenes, looking at the main object present in the scene. For 3DGS and ours, we used the version specifically trained for these approaches without Opacity Decay. The paths all exhibit translation and rotation. The recorded video clips were between 8 and 19 seconds long.

After a pre-questionnaire, we instructed the participants that they will be presented with video pairs and they should specifically look for consistency in the rendering and then rate whether either of the video clips was more consistent than the other. If they did not consider any clip more consistent, they were allowed to rate them

![Image block](images/radl2024_stopthepop_p15_b12.png)

Fig. 12. 3DGS can fake view-dependent effects with popping. We slightly rotate test set views, and 3DGS’s results are significantly less consistent compared to our results. We increase contrast for zoomed-in views and include a FLIP view for a better comparison.

as equal. We mapped those answers onto scores 𝑠:

$$
s = \left\{ \begin{array}{c l} - 1 & \text {3DGS is more consistent,} \\ 0 & \text {both are equal,} \\ 1 & \text {ours is more consistent.} \end{array} \right.
$$

We presented both videos side-by-side and played them in a loop. We did not restrict the answer times, allowing participants to watch the clips repeatedly. We randomized the order of videos (left, right) as well as the order of scenes.

Overall, participants considered our method more consistent in 54.3% of the cases, voted for equal in 33.3% and preferred 3DGS in 12.4%, leading to an average preference score of $s _ { m e a n }   =   0 . 4 2 .$ The result is statistically significant according to Wilcoxon Signed Rank tests $( Z \; = \; 2 2 7 6 . 5 , \; p \; < \; . 0 0 0 1 )$ [Woolson 2008]. As can be seen in Fig. 13, we observe inter-scene differences. For scenes with mostly small Gaussians, like in Bonsai or Kitchen, we expected less difference in the voted scores, as there is also less popping. In contrast, for scenes with large Gaussians, where popping occurs more often, like Room, Train or Truck, it is not surprising that our method is preferred by a large margin. We were not able to assess why participants slightly preferred 3DGS for Bicycle.

## E DETAILED PERFORMANCE TIMINGS

In this section, we provide additional performance ablation studies. We follow the evaluation setup from the main material, interpolating between all available COLMAP poses (30 frames per pose), and rendering in Full HD on an NVIDIA RTX 4090 with CUDA 11.8.

Per-Scene Performance Timings. In Tab. 9, we show per-scene performance timings for the total render time in ms. For the Mip-NeRF 360 [Barron et al. 2022] Indoor and Outdoor scenes, our method is slightly slower than 3DGS. For the Tanks & Temples [Knapitsch et al. 2017] and Deep Blending [Hedman et al. 2018] datasets, we achieve higher performance than 3DGS for most scenes. Analyzing

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 16 of 17 -->

64:16

• Radl and Steiner et al

![Chart block](images/radl2024_stopthepop_p16_b3.png)

Fig. 13. Average per-scene user study score. A positive score indicates a preference for our method, whereas a negative score indicates a preference for 3DGS. Our method clearly outperforms 3DGS.

the performance in more detail, we could verify that our method outperforms 3DGS when Gaussian are larger and/or more anisotropic, as our culling and load balancing can speed up rendering. If Gaussians are small and uniformly sized, the main load stems from the final stages of the render kernel, where sorting of course creates an overhead compared to 3DGS.

Table 9. Total performance timings for different configurations of our method and 3DGS, with the respective number of Gaussians per scene for comparison. Although scenes may exhibit a similar number of Gaussians, performance timings vary significantly.

| Scene#Gaussians | Bicycle5.95M | Flowers3.60M | Garden5.49M | Stump4.84M | Treehill3.85M |
| --- | --- | --- | --- | --- | --- |
| (A) Ours | 6.829 | 4.921 | 7.247 | 4.693 | 5.012 |
| (B) Ours w/o per-tile depth | 6.730 | 4.693 | 7.160 | 4.509 | 4.879 |
| (C) Ours w/o load balancing | 8.482 | 6.732 | 9.167 | 6.496 | 6.919 |
| (D) Ours w/o tile-based culling | 10.066 | 7.338 | 9.796 | 6.584 | 7.884 |
| (E) Ours w/o hier. culling | 11.087 | 7.589 | 11.788 | 7.178 | 7.773 |
| 3DGS | 7.438 | 4.002 | 6.034 | 3.708 | 4.492 |

| Scene #Gaussians | Bonsai 1.25M | Counter 1.20M | Kitchen 1.81M | Room 1.55M |
| --- | --- | --- | --- | --- |
| (A) Ours | 3.399 | 4.390 | 5.695 | 3.990 |
| (B) Ours w/o per-tile depth | 3.285 | 4.250 | 5.587 | 3.844 |
| (C) Ours w/o load balancing | 5.251 | 6.217 | 7.558 | 5.843 |
| (D) Ours w/o tile-based culling | 4.846 | 6.977 | 8.214 | 6.155 |
| (E) Ours w/o hier. culling | 4.608 | 6.142 | 8.916 | 5.450 |
| 3DGS | 2.574 | 4.043 | 4.783 | 4.180 |

| Dataset | Deep Bl | ending | Tanks &amp; | Temples |
| --- | --- | --- | --- | --- |
| Scene | DrJohnson | Playroom | Train | Truck |
| #Gaussians | 3.28M | 2.33M | 1.05M | 2.56M |
| (A) Ours | 4.763 | 4.549 | 4.225 | 5.100 |
| (B) Ours w/o per-tile depth | 4.612 | 4.373 | 4.099 | 4.898 |
| (C) Ours w/o load balancing | 6.648 | 6.275 | 6.215 | 6.942 |
| (D) Ours w/o tile-based culling | 7.998 | 7.295 | 7.469 | 8.363 |
| (E) Ours w/o hier. culling | 6.418 | 5.999 | 5.675 | 7.113 |
| 3DGS | 5.752 | 4.303 | 5.548 | 5.506 |

Relative Performance Timings. In Tab. 10, we report per-stage performance timings of our method relative to 3DGS for each scene.

Preprocess is generally slower due to the additional workload of tilebased culling and computation of ${ { ^ \mathrm { { ! } } \Sigma ^ { - 1 } } }$ . Due to our load balancing strategy, our Duplicate stage is faster for every tested scene, except for Flowers — here, our load balancing scheme is not able to amortize the additional workload of per-tile depth evaluations and tile-based culling. Sort is accelerated drastically, as the modifications for the previous stages result in fewer 2D splats to sort. The Render stage is naturally slower due to the overhead of our hierarchical rasterizer.

Table 10. Relative per-scene performance timings of our method with respect to 3DGS for each stage. Shades of blue indicate scenes where our method performed favorably, whereas shades of red indicate the opposite. We also report average percentages in the final row (not average runtime).

<table><tr><td>Dataset</td><td>Scene</td><td>#Gaussians</td><td>Preprocess</td><td>Duplicate</td><td>Sort</td><td>Render</td><td>Total</td></tr><tr><td rowspan="5">M360 Outdoor</td><td>Bicycle</td><td>5.95M</td><td>1.38</td><td>0.65</td><td>0.19</td><td>1.40</td><td>0.92</td></tr><tr><td>Flowers</td><td>3.60M</td><td>1.53</td><td>1.21</td><td>0.25</td><td>1.71</td><td>1.23</td></tr><tr><td>Garden</td><td>5.49M</td><td>1.27</td><td>0.78</td><td>0.29</td><td>2.04</td><td>1.20</td></tr><tr><td>Stump</td><td>4.84M</td><td>1.52</td><td>0.90</td><td>0.26</td><td>1.82</td><td>1.27</td></tr><tr><td>Treehill</td><td>3.85M</td><td>1.45</td><td>0.88</td><td>0.22</td><td>1.70</td><td>1.12</td></tr><tr><td rowspan="4">M360 Indoor</td><td>Bonsai</td><td>1.25M</td><td>1.32</td><td>0.84</td><td>0.25</td><td>2.06</td><td>1.32</td></tr><tr><td>Counter</td><td>1.20M</td><td>1.46</td><td>0.75</td><td>0.17</td><td>1.80</td><td>1.09</td></tr><tr><td>Kitchen</td><td>1.81M</td><td>1.25</td><td>0.66</td><td>0.25</td><td>2.02</td><td>1.19</td></tr><tr><td>Room</td><td>1.55M</td><td>1.60</td><td>0.70</td><td>0.13</td><td>1.53</td><td>0.95</td></tr><tr><td rowspan="2">DB</td><td>DrJohnson</td><td>3.28M</td><td>1.60</td><td>0.62</td><td>0.12</td><td>1.36</td><td>0.83</td></tr><tr><td>Playroom</td><td>2.33M</td><td>1.70</td><td>0.93</td><td>0.14</td><td>1.63</td><td>1.06</td></tr><tr><td rowspan="2">T&amp;T</td><td>Train</td><td>1.05M</td><td>1.42</td><td>0.61</td><td>0.11</td><td>1.53</td><td>0.76</td></tr><tr><td>Truck</td><td>2.56M</td><td>1.57</td><td>0.79</td><td>0.13</td><td>1.69</td><td>0.93</td></tr><tr><td colspan="2">Average</td><td>2.98M</td><td>1.47</td><td>0.79</td><td>0.19</td><td>1.71</td><td>1.07</td></tr></table>

As previously discussed, Bonsai and Train exhibit the biggest inter-method differences despite the similar number of Gaussians due to differently sized splats in screen space. Bicycle is the only scene of Mip-NeRF 360 Outdoor where our approach outperforms 3DGS. Although Garden has a similarly high number of Gaussians, Bicycle allows for more excessive culling and, therefore, has a sig nificantly lower avg. 𝑁<sub>𝑡</sub> for our method (2.7 vs. 2.41) compared to 3DGS (6.24 vs. 4.45).

Hyperparameter Performance Ablation. In Tab. 11, we compare timings for the Render stage for different size combinations of the 2×2 tile-queue and per-pixel queue. As expected, our final chosen values (8 and 4) perform best, since they have the lowest memory and compute requirements. Runtime increases significantly for very large per-pixel queue sizes, as register pressure increases and spills into local memory. In Tab. 11, we also show performance timings of the Preprocess and Duplicate stages for different load balancing tile thresholds (∞ = no load balancing). Gaussians whose 2D splat covers more tiles than this threshold will be computed cooperatively by all threads of a warp. Our chosen value of 32 performs well for both stages. Preprocess, which only performs tile-based culling, does not show large differences and is even slightly faster for small thresholds. Duplicate shows significant improvements, as it performs many more computations per tile, i.e. tile-based culling, per-tile depth calculation, and key/value writes. Choosing a value of 32 also fits GPU warp sizes, and allows for better warp utilization, as well as fast concurrent memory writes.

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.

<!-- page 17 of 17 -->

StopThePop: Sorted Gaussian Splatting for View-Consistent Real-time Rendering

64:17

## F PER-SCENE QUALITY METRICS

We provide per-scene results for Mip-NeRF 360 [Barron et al. 2022], Tanks and Temples [Knapitsch et al. 2017] and Deep Blending [Hedman et al. 2018] in Tabs. 12 and 13. Results with dagger (†) were reproduced from Kerbl et al. [2023]: this includes results for Mip-NeRF 360 [Barron et al. 2022], Instant-NGP [Müller et al. 2022] and Plenoxels [Fridovich-Keil et al. 2022]. We evaluate our final hierarchical rasterizer (“Ours”), as well as the fixed-size head sorting method for two different resorting window sizes (“Head 8” and “Head 16”), with and without per-tile depth (“w/o PTD”).

Table 11. Ablation of our method for different sizes of the 2×2 tile-queue and the per-pixel queue in addition to different load balancing thresholds, with the same underlying model (no retraining).

| 2×2 tile-queue per-pixel queue |  | 84 | 88 | 124 | 128 | 208 | 2016 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Render |  | 3.646 | 4.000 | 4.052 | 4.364 | 4.470 | 8.549 |
| Threshold | 1 | 4 | 16 | 32 | 64 | 256 | ∞ |
| Preprocess | 0.644 | 0.643 | 0.648 | 0.648 | 0.649 | 0.652 | 0.847 |
| Duplicate | 0.607 | 0.541 | 0.437 | 0.435 | 0.447 | 0.515 | 2.059 |

Table 12. Combined per-scene scores for PSNR, SSIM, LPIPS and FLIP for Tanks & Temples and Deep Blending.

<table><tr><td>Metric</td><td colspan="4">PSNR</td><td colspan="4">SSIM</td></tr><tr><td>Dataset</td><td colspan="2">Tanks &amp; Temples</td><td colspan="2">Deep Blending</td><td colspan="2">Tanks &amp; Temples</td><td colspan="2">Deep Blending</td></tr><tr><td>Scene</td><td>Truck</td><td>Train</td><td>DrJ.</td><td>Playroom</td><td>Truck</td><td>Train</td><td>DrJ.</td><td>Playroom</td></tr><tr><td>Mip-NeRF  $360^†$ </td><td>24.91</td><td>19.52</td><td>29.14</td><td>29.66</td><td>0.857</td><td>0.660</td><td>0.901</td><td>0.900</td></tr><tr><td>Instant-NGP (base) $^†$ </td><td>23.26</td><td>20.17</td><td>27.75</td><td>19.48</td><td>0.779</td><td>0.666</td><td>0.839</td><td>0.754</td></tr><tr><td>Instant-NGP (big) $^†$ </td><td>23.38</td><td>20.46</td><td>28.26</td><td>21.67</td><td>0.800</td><td>0.689</td><td>0.854</td><td>0.780</td></tr><tr><td>Plenoxels</td><td>23.23</td><td>18.94</td><td>23.16</td><td>23.02</td><td>0.774</td><td>0.663</td><td>0.787</td><td>0.802</td></tr><tr><td>3DGS</td><td>25.39</td><td>22.04</td><td>29.06</td><td>29.86</td><td>0.878</td><td>0.813</td><td>0.898</td><td>0.901</td></tr><tr><td>Head 8 w/o PTD</td><td>24.79</td><td>21.52</td><td>29.40</td><td>30.29</td><td>0.877</td><td>0.809</td><td>0.902</td><td>0.905</td></tr><tr><td>Head 8</td><td>24.81</td><td>21.41</td><td>29.51</td><td>30.31</td><td>0.878</td><td>0.810</td><td>0.904</td><td>0.905</td></tr><tr><td>Head 16 w/o PTD</td><td>24.84</td><td>21.60</td><td>29.40</td><td>30.36</td><td>0.878</td><td>0.810</td><td>0.904</td><td>0.905</td></tr><tr><td>Head 16</td><td>24.81</td><td>21.36</td><td>29.44</td><td>30.31</td><td>0.877</td><td>0.809</td><td>0.903</td><td>0.906</td></tr><tr><td>Ours w/o PTD</td><td>24.93</td><td>21.53</td><td>29.44</td><td>30.31</td><td>0.878</td><td>0.810</td><td>0.903</td><td>0.905</td></tr><tr><td>Ours</td><td>24.93</td><td>21.48</td><td>29.42</td><td>30.31</td><td>0.878</td><td>0.808</td><td>0.903</td><td>0.905</td></tr><tr><td>3DGS (Opacity Decay)</td><td>25.31</td><td>21.73</td><td>28.18</td><td>29.69</td><td>0.874</td><td>0.804</td><td>0.888</td><td>0.899</td></tr><tr><td>Ours (Opacity Decay)</td><td>24.90</td><td>21.46</td><td>29.38</td><td>30.30</td><td>0.875</td><td>0.804</td><td>0.903</td><td>0.907</td></tr></table>

<table><tr><td rowspan="2">Dataset</td><td colspan="4">LPIPS</td><td colspan="4"> $\mathcal{E}LIP$ </td></tr><tr><td colspan="2">Tanks &amp; Temples</td><td colspan="2">Deep Blending</td><td colspan="2">Tanks &amp; Temples</td><td colspan="2">Deep Blending</td></tr><tr><td>Scene</td><td>Truck</td><td>Train</td><td>DrJ.</td><td>Playroom</td><td>Truck</td><td>Train</td><td>DrJ.</td><td>Playroom</td></tr><tr><td>Mip-NeRF  $360^{\dagger}$ </td><td>0.159</td><td>0.354</td><td>0.237</td><td>0.252</td><td>0.162</td><td>0.302</td><td>0.117</td><td>0.158</td></tr><tr><td>Instant-NGP (base) $^{\dagger}$ </td><td>0.274</td><td>0.386</td><td>0.381</td><td>0.465</td><td>0.194</td><td>0.297</td><td>0.141</td><td>0.375</td></tr><tr><td>Instant-NGP (big) $^{\dagger}$ </td><td>0.249</td><td>0.360</td><td>0.352</td><td>0.428</td><td>0.190</td><td>0.291</td><td>0.133</td><td>0.311</td></tr><tr><td>Plenoxels</td><td>0.308</td><td>0.379</td><td>0.433</td><td>0.418</td><td>0.196</td><td>0.328</td><td>0.222</td><td>0.266</td></tr><tr><td>3DGS</td><td>0.148</td><td>0.208</td><td>0.247</td><td>0.246</td><td>0.148</td><td>0.250</td><td>0.119</td><td>0.143</td></tr><tr><td>Head 8 w/o PTD</td><td>0.143</td><td>0.204</td><td>0.236</td><td>0.237</td><td>0.165</td><td>0.265</td><td>0.116</td><td>0.140</td></tr><tr><td>Head 8</td><td>0.142</td><td>0.203</td><td>0.234</td><td>0.235</td><td>0.166</td><td>0.266</td><td>0.114</td><td>0.139</td></tr><tr><td>Head 16 w/o PTD</td><td>0.142</td><td>0.203</td><td>0.234</td><td>0.236</td><td>0.166</td><td>0.262</td><td>0.115</td><td>0.138</td></tr><tr><td>Head 16</td><td>0.142</td><td>0.203</td><td>0.234</td><td>0.235</td><td>0.164</td><td>0.267</td><td>0.116</td><td>0.139</td></tr><tr><td>Ours w/o PTD</td><td>0.142</td><td>0.204</td><td>0.234</td><td>0.235</td><td>0.163</td><td>0.264</td><td>0.115</td><td>0.139</td></tr><tr><td>Ours</td><td>0.142</td><td>0.204</td><td>0.234</td><td>0.235</td><td>0.164</td><td>0.267</td><td>0.115</td><td>0.138</td></tr><tr><td>3DGS (Opacity Decay)</td><td>0.160</td><td>0.228</td><td>0.265</td><td>0.260</td><td>0.148</td><td>0.261</td><td>0.124</td><td>0.144</td></tr><tr><td>Ours (Opacity Decay)</td><td>0.151</td><td>0.218</td><td>0.241</td><td>0.241</td><td>0.160</td><td>0.267</td><td>0.115</td><td>0.138</td></tr></table>

Table 13. Combined per-scene scores for PSNR, SSIM, LPIPS & FLIP for the Mip-NeRF 360 dataset.

<table><tr><td>Dataset</td><td colspan="5">Mip-NeRF 360 Outdoor</td><td colspan="4">Mip-NeRF 360 Indoor</td></tr><tr><td>Scene</td><td>Bicycle</td><td>Flowers</td><td>Garden</td><td>Stump</td><td>Treehill</td><td>Room</td><td>Counter</td><td>Kitchen</td><td>Bonsai</td></tr><tr><td colspan="10">PSNR</td></tr><tr><td>Mip-NeRF  $360^†$ </td><td>24.30</td><td>21.65</td><td>26.88</td><td>26.36</td><td>22.93</td><td>31.47</td><td>29.45</td><td>31.99</td><td>33.40</td></tr><tr><td>Instant-NGP (base) $^†$ </td><td>22.19</td><td>20.35</td><td>24.60</td><td>23.63</td><td>22.36</td><td>29.27</td><td>26.44</td><td>28.55</td><td>30.34</td></tr><tr><td>Instant-NGP (big) $^†$ </td><td>22.17</td><td>20.65</td><td>25.07</td><td>23.47</td><td>22.37</td><td>29.69</td><td>26.69</td><td>29.48</td><td>30.69</td></tr><tr><td>Plenoxels</td><td>21.90</td><td>20.10</td><td>23.50</td><td>20.68</td><td>22.26</td><td>27.57</td><td>23.64</td><td>23.43</td><td>24.71</td></tr><tr><td>3DGS</td><td>25.18</td><td>21.48</td><td>27.24</td><td>26.62</td><td>22.45</td><td>31.49</td><td>28.98</td><td>31.35</td><td>32.10</td></tr><tr><td>Head 8 w/o PTD</td><td>25.18</td><td>21.49</td><td>27.14</td><td>26.64</td><td>22.41</td><td>30.77</td><td>28.83</td><td>31.06</td><td>31.85</td></tr><tr><td>Head 8</td><td>25.19</td><td>21.50</td><td>27.20</td><td>26.62</td><td>22.52</td><td>30.88</td><td>28.78</td><td>31.04</td><td>31.98</td></tr><tr><td>Head 16 w/o PTD</td><td>25.20</td><td>21.48</td><td>27.18</td><td>26.62</td><td>22.45</td><td>30.84</td><td>28.84</td><td>30.89</td><td>31.63</td></tr><tr><td>Head 16</td><td>25.22</td><td>21.55</td><td>27.12</td><td>26.59</td><td>22.50</td><td>30.81</td><td>28.78</td><td>31.06</td><td>31.88</td></tr><tr><td>Ours w/o PTD</td><td>25.21</td><td>21.45</td><td>27.17</td><td>26.68</td><td>22.47</td><td>30.84</td><td>28.70</td><td>31.23</td><td>31.90</td></tr><tr><td>Ours</td><td>25.20</td><td>21.50</td><td>27.16</td><td>26.69</td><td>22.43</td><td>30.83</td><td>28.59</td><td>31.13</td><td>31.93</td></tr><tr><td>3DGS (Opacity Decay)</td><td>24.93</td><td>21.30</td><td>27.05</td><td>26.57</td><td>22.39</td><td>31.03</td><td>28.64</td><td>31.07</td><td>31.52</td></tr><tr><td>Ours (Opacity Decay)</td><td>25.00</td><td>21.30</td><td>26.95</td><td>26.67</td><td>22.39</td><td>30.58</td><td>28.33</td><td>30.46</td><td>30.76</td></tr><tr><td colspan="10">SSIM</td></tr><tr><td>Mip-NeRF  $360^†$ </td><td>0.685</td><td>0.584</td><td>0.809</td><td>0.745</td><td>0.631</td><td>0.910</td><td>0.892</td><td>0.917</td><td>0.938</td></tr><tr><td>Instant-NGP (base) $^†$ </td><td>0.491</td><td>0.450</td><td>0.649</td><td>0.574</td><td>0.518</td><td>0.855</td><td>0.798</td><td>0.818</td><td>0.890</td></tr><tr><td>Instant-NGP (big) $^†$ </td><td>0.512</td><td>0.486</td><td>0.701</td><td>0.594</td><td>0.542</td><td>0.871</td><td>0.817</td><td>0.858</td><td>0.906</td></tr><tr><td>Plenoxels</td><td>0.495</td><td>0.432</td><td>0.606</td><td>0.523</td><td>0.510</td><td>0.840</td><td>0.758</td><td>0.648</td><td>0.814</td></tr><tr><td>3DGS</td><td>0.763</td><td>0.603</td><td>0.862</td><td>0.772</td><td>0.632</td><td>0.917</td><td>0.906</td><td>0.925</td><td>0.939</td></tr><tr><td>Head 8 w/o PTD</td><td>0.766</td><td>0.602</td><td>0.862</td><td>0.773</td><td>0.633</td><td>0.917</td><td>0.905</td><td>0.925</td><td>0.939</td></tr><tr><td>Head 8</td><td>0.766</td><td>0.604</td><td>0.862</td><td>0.773</td><td>0.634</td><td>0.916</td><td>0.905</td><td>0.924</td><td>0.939</td></tr><tr><td>Head 16 w/o PTD</td><td>0.767</td><td>0.603</td><td>0.861</td><td>0.773</td><td>0.633</td><td>0.917</td><td>0.905</td><td>0.922</td><td>0.939</td></tr><tr><td>Head 16</td><td>0.767</td><td>0.604</td><td>0.861</td><td>0.773</td><td>0.635</td><td>0.917</td><td>0.905</td><td>0.925</td><td>0.939</td></tr><tr><td>Ours w/o PTD</td><td>0.767</td><td>0.603</td><td>0.862</td><td>0.775</td><td>0.635</td><td>0.917</td><td>0.904</td><td>0.925</td><td>0.939</td></tr><tr><td>Ours</td><td>0.767</td><td>0.604</td><td>0.862</td><td>0.775</td><td>0.635</td><td>0.917</td><td>0.903</td><td>0.925</td><td>0.939</td></tr><tr><td>3DGS (Opacity Decay)</td><td>0.749</td><td>0.592</td><td>0.854</td><td>0.770</td><td>0.626</td><td>0.914</td><td>0.899</td><td>0.921</td><td>0.937</td></tr><tr><td>Ours (Opacity Decay)</td><td>0.756</td><td>0.593</td><td>0.855</td><td>0.775</td><td>0.629</td><td>0.914</td><td>0.898</td><td>0.920</td><td>0.935</td></tr></table>

<table><tr><td>Dataset</td><td colspan="5">Mip-NeRF 360 Outdoor</td><td colspan="4">Mip-NeRF 360 Indoor</td></tr><tr><td>Scene</td><td>Bicycle</td><td>Flowers</td><td>Garden</td><td>Stump</td><td>Treehill</td><td>Room</td><td>Counter</td><td>Kitchen</td><td>Bonsai</td></tr><tr><td colspan="10">LPIPS</td></tr><tr><td>Mip-NeRF  $360^†$ </td><td>0.305</td><td>0.346</td><td>0.171</td><td>0.261</td><td>0.347</td><td>0.213</td><td>0.207</td><td>0.128</td><td>0.179</td></tr><tr><td>Instant-NGP (base) $^†$ </td><td>0.487</td><td>0.481</td><td>0.312</td><td>0.450</td><td>0.489</td><td>0.301</td><td>0.342</td><td>0.254</td><td>0.227</td></tr><tr><td>Instant-NGP (big) $^†$ </td><td>0.446</td><td>0.441</td><td>0.257</td><td>0.421</td><td>0.450</td><td>0.261</td><td>0.306</td><td>0.205</td><td>0.193</td></tr><tr><td>Plenoxels</td><td>0.490</td><td>0.506</td><td>0.374</td><td>0.468</td><td>0.495</td><td>0.344</td><td>0.378</td><td>0.404</td><td>0.336</td></tr><tr><td>3DGS</td><td>0.213</td><td>0.338</td><td>0.109</td><td>0.216</td><td>0.327</td><td>0.221</td><td>0.202</td><td>0.127</td><td>0.206</td></tr><tr><td>Head 8 w/o PTD</td><td>0.207</td><td>0.336</td><td>0.107</td><td>0.211</td><td>0.322</td><td>0.216</td><td>0.199</td><td>0.126</td><td>0.203</td></tr><tr><td>Head 8</td><td>0.207</td><td>0.335</td><td>0.107</td><td>0.211</td><td>0.320</td><td>0.217</td><td>0.199</td><td>0.126</td><td>0.202</td></tr><tr><td>Head 16 w/o PTD</td><td>0.206</td><td>0.336</td><td>0.107</td><td>0.211</td><td>0.321</td><td>0.216</td><td>0.198</td><td>0.128</td><td>0.203</td></tr><tr><td>Head 16</td><td>0.206</td><td>0.335</td><td>0.107</td><td>0.211</td><td>0.319</td><td>0.216</td><td>0.199</td><td>0.126</td><td>0.202</td></tr><tr><td>Ours w/o PTD</td><td>0.205</td><td>0.335</td><td>0.107</td><td>0.210</td><td>0.319</td><td>0.216</td><td>0.199</td><td>0.126</td><td>0.203</td></tr><tr><td>Ours</td><td>0.206</td><td>0.335</td><td>0.107</td><td>0.210</td><td>0.319</td><td>0.216</td><td>0.200</td><td>0.126</td><td>0.202</td></tr><tr><td>3DGS (Opacity Decay)</td><td>0.244</td><td>0.358</td><td>0.125</td><td>0.232</td><td>0.347</td><td>0.230</td><td>0.215</td><td>0.137</td><td>0.210</td></tr><tr><td>Ours (Opacity Decay)</td><td>0.232</td><td>0.354</td><td>0.122</td><td>0.224</td><td>0.336</td><td>0.224</td><td>0.211</td><td>0.135</td><td>0.207</td></tr><tr><td colspan="10">TLIP</td></tr><tr><td>Mip-NeRF  $360^†$ </td><td>0.169</td><td>0.217</td><td>0.124</td><td>0.156</td><td>0.184</td><td>0.095</td><td>0.100</td><td>0.088</td><td>0.069</td></tr><tr><td>Instant-NGP (base) $^†$ </td><td>0.203</td><td>0.260</td><td>0.155</td><td>0.209</td><td>0.189</td><td>0.118</td><td>0.144</td><td>0.123</td><td>0.093</td></tr><tr><td>Instant-NGP (big) $^†$ </td><td>0.201</td><td>0.251</td><td>0.146</td><td>0.213</td><td>0.189</td><td>0.112</td><td>0.139</td><td>0.113</td><td>0.089</td></tr><tr><td>Plenoxels</td><td>0.211</td><td>0.271</td><td>0.181</td><td>0.276</td><td>0.206</td><td>0.143</td><td>0.201</td><td>0.218</td><td>0.165</td></tr><tr><td>3DGS</td><td>0.158</td><td>0.225</td><td>0.118</td><td>0.150</td><td>0.186</td><td>0.093</td><td>0.105</td><td>0.096</td><td>0.082</td></tr><tr><td>Head 8 w/o PTD</td><td>0.160</td><td>0.223</td><td>0.120</td><td>0.150</td><td>0.184</td><td>0.102</td><td>0.107</td><td>0.100</td><td>0.086</td></tr><tr><td>Head 8</td><td>0.159</td><td>0.223</td><td>0.119</td><td>0.150</td><td>0.181</td><td>0.101</td><td>0.108</td><td>0.099</td><td>0.083</td></tr><tr><td>Head 16 w/o PTD</td><td>0.159</td><td>0.224</td><td>0.119</td><td>0.151</td><td>0.182</td><td>0.101</td><td>0.107</td><td>0.103</td><td>0.086</td></tr><tr><td>Head 16</td><td>0.159</td><td>0.222</td><td>0.121</td><td>0.151</td><td>0.183</td><td>0.102</td><td>0.108</td><td>0.099</td><td>0.085</td></tr><tr><td>Ours w/o PTD</td><td>0.160</td><td>0.225</td><td>0.120</td><td>0.149</td><td>0.183</td><td>0.101</td><td>0.110</td><td>0.099</td><td>0.085</td></tr><tr><td>Ours</td><td>0.159</td><td>0.224</td><td>0.119</td><td>0.149</td><td>0.184</td><td>0.101</td><td>0.111</td><td>0.099</td><td>0.084</td></tr><tr><td>3DGS (Opacity Decay)</td><td>0.162</td><td>0.228</td><td>0.120</td><td>0.151</td><td>0.182</td><td>0.096</td><td>0.107</td><td>0.099</td><td>0.085</td></tr><tr><td>Ours (Opacity Decay)</td><td>0.162</td><td>0.228</td><td>0.122</td><td>0.148</td><td>0.182</td><td>0.103</td><td>0.112</td><td>0.106</td><td>0.090</td></tr></table>

ACM Trans. Graph., Vol. 43, No. 4, Article 64. Publication date: July 2024.