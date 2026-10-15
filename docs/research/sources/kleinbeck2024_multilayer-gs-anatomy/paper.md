<!-- page 1 of 14 -->

arXiv:2410.16978v1 [cs.GR] 22 Oct 2024

# Multi-Layer Gaussian Splatting for Immersive Anatomy Visualization

Constantin Kleinbeck\* Technical University of Munich, Clinic for Orthopedics and Sports Orthopedics, TUM University Hospital, Munich, Germany

Klaus Engel‡ Siemens Healthineers AG, Erlangen, Germany

Hannah Schieber†

Technical University of Munich, Clinic for Orthopedics and Sports Orthopedics, TUM University Hospital, Munich, Germany

Ralf Gutjahr§ Siemens Healthineers AG, Forchheim, Germany

Daniel Roth¶

Technical University of Munich, Clinic for Orthopedics and Sports Orthopedics, TUM University Hospital, Munich, Germany

![Image block](images/kleinbeck2024_multilayer-gs-anatomy_p1_b10.png)

Figure 1: Our layered gaussian splatting (GS) model is consecutively trained on multiple renderings of the same computed tomography (CT) scan, visualizing different parts of the anatomy. It can be viewed in real-time in virtual reality (VR), and the trained anatomies can selectively be shown and cut to create engaging visuals and bridge the interactivity gap to full path tracing.

## ABSTRACT

In medical image visualization, path tracing of volumetric medical data like computed tomography (CT) scans produces lifelike threedimensional visualizations. Immersive virtual reality (VR) displays can further enhance the understanding of complex anatomies. Going beyond the diagnostic quality of traditional 2D slices, they enable interactive 3D evaluation of anatomies, supporting medical education and planning. Rendering high-quality visualizations in real-time, however, is computationally intensive and impractical for compute-constrained devices like mobile headsets.

We propose a novel approach utilizing gaussian splatting (GS) to create an efficient but static intermediate representation of CT scans. We introduce a layered GS representation, incrementally including different anatomical structures while minimizing overlap and extending the GS training to remove inactive Gaussians. We further compress the created model with clustering across layers.

Our approach achieves interactive frame rates while preserving anatomical structures, with quality adjustable to the target hardware. Compared to standard GS, our representation retains some of

the explorative qualities initially enabled by immersive path tracing. Selective activation and clipping of layers are possible at rendering time, adding a degree of interactivity to otherwise static GS models. This could enable scenarios where high computational demands would otherwise prohibit using path-traced medical volumes.

**Index Terms:** Virtual reality, Visualization, Volumetric models, Reconstruction, Gaussian Splatting, Computed Tomography.

## 1 INTRODUCTION

CT scanning is a widely used imaging technique that provides exceptionally high-resolution volumetric data, allowing detailed examinations of the human body and its complex structures. Traditionally, clinicians and radiologists rely on 2D slice views of such volumetric data for diagnosis and treatment planning. Yet, 3D visualization techniques have been a research subject for around four decades [14, 26]. Today, they are increasingly finding their way into medical applications in fields like education, training, surgical planning, and decision-making [58].

Volumetric path tracing is a modern alternative to traditional ray marching for 3D medical data visualization [13, 10]. This computationally intensive technique models photons’ path and interactions, producing realistic renderings, including improved lighting and shadows. The resulting visual fidelity particularly benefits medical education and training [3, 4], making complex anatomical structures more comprehensible. When presented on immersive headsets, the stereoscopic environment clearly conveys spatial relationships and context. This can create an engaging, explorative learning environment.

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>\*</sup>e-mail: constantin.kleinbeck@tum.de</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">¶e-mail: daniel.roth@tum.de</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">§e-mail: ralf.gutjahr@siemens-healthineers.com</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">‡e-mail: engel.klaus@siemens-healthineers.com</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">†e-mail: hannah.schieber@tum.de</span></small>

<!-- page 2 of 14 -->

Direct volume rendering using ray marching has been a longstanding technique for visualizing volumetric medical data [13]. While effective, it often struggles to produce realistic renderings. Volumetric path tracing, a technique borrowed from the special effects industry, has emerged as a promising alternative [10]. This method invests more computing time to model photons’ interactions and path through the scene. Rendered medical volumes boast better physical properties, including realistic lighting and shadows, enhancing the overall visual fidelity. This enhanced realism is particularly beneficial for educational and training purposes [3], by making complex anatomical structures easier to understand [4]. Immersive 3D displays can present this inherently three-dimensional data in a stereoscopic environment. This makes relationships and context readily apparent, providing an engaging and explorative learning environment.

Yet, these advancements come with their own set of challenges. With their increasing resolution, modern CT scanners can produce file sizes in the hundreds to thousands of MB, with specialized devices getting into tens of GB per scan [48]. While not problematic for workstations, distribution to and storage on mobile devices can quickly get complicated. Path tracing, while capable of producing high-quality outputs, requires substantial computational power, especially for real-time rendering. This presents a particular problem for head mounted displays (HMDs), if one wants to benefit from the 3D rendering to break down spatial complexity in the medical data. They utilize high-resolution displays needing low-latency rendering to deliver immersive experiences and a smooth user experience, often without the benefit of being tethered to high-performance workstations. In many situations, like education or clinical settings, powerful workstations and tethered devices are difficult to utilize. Standalone immersive HMD are affordable and easy to deploy and handle but severely constrained in storage and render performance, making it hard to maintain fast render speeds and high quality.

To address these challenges, it is crucial to find a way to display medical volumetric data suitable for less powerful, mobile immersive devices. Rather than compromising rendering quality by opting for faster but less visually compelling techniques, lowering the resolution, or relying on aggressive denoising, we explore GS as an intermediate representation for high-quality renderings of volumetric medical data. In our approach, the target anatomy or tissue is pre-rendered to high-quality images using volumetric path tracing, which in turn are used to optimize a GS model. This representation can reproduce fine details, be compressed, and efficiently rendered in real-time on VR systems, making it well-suited for mobile and immersive environments. Still, it has certain limitations. The GS representation is inherently static, imposing several constraints: Color and transparency, commonly adjusted through transfer functions, are fixed at rendering time. Displaying different parts of the scanned anatomy would require multiple pre-trained, standalone GS representations. Techniques like cutting, slicing, and isolating regions of interest are technically possible but produce visually incorrect results. The GS optimization process primarily approximates surfaces and externally visible regions, with the dense inner parts of the volume largely missing. Mixing GS representations can lead to visual artifacts, as the different volumes have not been optimized together and need to be globally sorted.

We propose a layered GS representation to overcome these issues. Our Gaussian representation consists of multiple layers consecutively trained on top of each other, mitigating limitations associated with the static nature of GS. With a layered representation, we can display anatomy with multiple embedded visualizations for the same structure. For example, a leg can be visualized with only the bone, bone and muscle, or bone, muscle, and soft tissue in one representation, as shown in Figure 2. The upper layers, such as muscle and soft tissue, would consist of Gaussians encoding only the additional information, while Gaussians from lower layers re-

main present and untouched. This allows for seamless switching and cutting between layers, similar to what is shown in Figure 1, and the conditional display of additional information like highlighted areas with variable opacity. Our layered representation is more compact and faster to render than traditional path tracing of a CT volume. It offers more dynamism and flexibility than normal GS and can be more compact than storing multiple single representations with overlapping content.

**Contribution.** Our work makes the following contributions: 1. Insights into anatomy visualization using GS on mobile and immersive display devices, with performance indications.

2. A method for training and layering multiple GS renderings on top of each other, storing them in a single splat asset.

3. A technique for rendering these layered GS representations in the Unity game engine, with the ability to cut and display them individually or in combination.

4. Openly available training & rendering code and datasets.

## 2 RELATED WORK

This section explores key techniques in medical volume visualization, discussing the evolution from direct volume rendering (DVR) to path tracing. We then examine recent advancements in novel view synthesis (NVS) techniques, particularly GS, highlighting their applications and limitations in medical imaging contexts, and introducing alternative incremental training approaches.

## 2.1 Volumetric Rendering

Among various approaches to render volumetric medical data, DVR has emerged as the most widely applied algorithm. It allows to render volumes as shaded 3D images without the need for intermediate representations [55]. DVR typically involves sampling along rays through the volume, filtering, and mapping volume density to RGBA values. These values are then blended to create the final image [13]. Colorization of the volume data usually occurs through the use of transfer functions. While more complex multi-dimensional transfer functions exist, most at least map from a sampled volume density to an RGBA color [32]. Path tracing is an evolution of this rendering approach. It simulates physically based light transport by following the path of light around the scene after scattering events. This technique has been successfully applied to medical data, resulting in highly realistic and finely detailed imagery [25, 11, 10]. Clinicians have rated path-traced renderings better than traditional DVR renderings [6], although improved diagnostic value is not always clear [43]. While there is interest in using volume rendering with immersive displays [23, 51, 41], the high computational requirements, especially for path tracing, impose constraints on image quality. A common approach to accelerate rendering is the use of denoising techniques [18]. Real-time capable approaches for medical data visualization exist [19, 46], alongside offline methods targeting higher quality [17]. Real-time methods typically require powerful hardware and often compromise on quality to maintain performance. Notably, none of these approaches deliver acceptable quality on mobile immersive devices. The benefits of using path-traced volume visualizations include more realistic rendering [15], improved surface detail [43], and enhanced perception of complex anatomic spatial relationships [7], making path tracing a valuable tool in medical visualization, despite its computational challenges.

## 2.2 Novel View Synthesis

NVS refers to the generation of new viewpoints of a scene from a set of existing images or viewpoints. Pioneered around 30 years ago, it has evolved from techniques like light field rendering and view interpolation [27]. Today, most NVS techniques involve neural networks (NNs) in some form. Neural radiance fields (NeRF) have brought a leap in quality and realism to NVS [35], however,

<!-- page 3 of 14 -->

![Image block](images/kleinbeck2024_multilayer-gs-anatomy_p3_b1.png)

Figure 2: Visualization of the three layers in the leg scene from the high quality reconstruction, rendered with Unity. Comparison to default reconstruction with clustering compression and ground truth. Small details are lost or blurred in the reconstructions.

at the cost of long training times, slow rendering, and extensive storage requirements. Numerous approaches inspired by or derived from NeRF have emerged, many aiming to optimize its performance shortcomings [37, 29]. Despite these efforts, there is no silver bullet for addressing all limitations simultaneously, which makes immersive applications particularly challenging due to the massive performance requirements [28, 12, 42]. Falling back to mesh exports to leverage existing rendering pipelines can bring neural reconstructions to immersive mobile displays, however, with losses in image quality [24].

## 2.2.1 Gaussian Splatting

Kerbl et al. [21] introduced an explicit Gaussian representation for radiance fields, known as GS. It is a variant of NVS initialized from a sparse point cloud, followed by optimization of the Gaussians. The final image is then created by splatting these optimized Gaussians [60]. Unlike NeRF, GS does not require a NN and uses efficient rasterization to render the optimized scene representation. This generally results in faster runtime performance compared to NeRF, making it a promising candidate for VR applications [20]. Yet, the original implementation also comes with substantial storage requirements, which has triggered the development of various compression approaches [2, 36]. Some of these approaches have also improved rendering speed [38] and fidelity [8]. GS has been extended with anti-aliasing through a low-pass and 2D Mip filter, improving visual quality at focal lengths and rendering distances different from the original training data [54]. Similar to our layering approach exist works that store Gaussians in somewhat independent chunks, enabling smooth transitions between them [22]. They do target large-scale scenes by employing a hierarchical structure, though different from our overlapping data. Given the approach’s novelty, further speed and quality improvements will likely emerge.

In the medical field, many GS approaches focus on minimally endoscopic images with deformable structures. Some represent the structures and changes over time using a multilayer perceptron (MLP) [30, 52, 57]. Utilizing depth generated from a foun-

dation model [53] can be useful to optimize GS for similar structures in endoscopic images [31, 57]. These approaches focus on the deformability of the Gaussians due to the anatomical structure of organs such as the gallbladder. Another recent work has explored combining cinematic rendering [11], a form of path tracing, with GS for anatomy visualization [39]. They integrate view selection algorithms, alpha channel training, and anti-aliasing for quality improvements. The study evaluated GS using more powerful hardware focusing on highly detailed, static representations, finding the approach suitable for anatomy visualization.

## 2.2.2 Continual Learning for Novel View Synthesis

In NVS, works exploring consecutive training approaches usually fall within the domain of continual learning. One challenge in continual learning is catastrophic forgetting [34]. To prevent this, the parameters are isolated in updating learning step [45, 33]. An approach in NeRF uses chamber loss instead of the classical photometric loss [9]. Other approaches query a pre-trained neural graphics primitives (NGP) for pseudo ground truth and train a new MLP for the current scene [40], or use a replay buffer to address this issue [5]. While our approach shares similarities with existing continual learning NVS approaches, our main goal is to maintain distinct scenes by freezing previous layers. We aim for a full layered representation of anatomy instead of the same scene with various differences over time or a consecutive capturing setup.

## 2.3 Summary

Recognizing the limitations of static GS representations, particularly their inability to adjust in real-time, we explore the training of multiple visualizations of the same medical volume into a single GS representation. The original GS training process was primarily designed for natural scenes without transparent backgrounds. Although it supports synthetic data with transparency, the alpha channel is flattened during loading. This behavior can lead to artifacts and loss of detail in semi-transparent areas in front of transparent backgrounds, as demonstrated in Figure 5.

<!-- page 4 of 14 -->

![Image block](images/kleinbeck2024_multilayer-gs-anatomy_p4_b1.png)

Layer 1

Layer 2

Layer 3

Combined layers

Figure 3: Synthetic three layer scene. Top row show the three layers of ground truth data. Bottom row shows the active layer trained from the corresponding images, without previous layers, and a combined view. Each layer consists predominantly of newly added elements and areas where existing elements are shadowed.

## 3 METHOD

To bring high-quality and realistic anatomical visualizations to moderately powered hardware, such as mobile VR headsets, our approach utilizes precomputed high-quality path-traced images to train a GS intermediate representation. Specifically, we propose a layered GS model, where lower layers act as a ”background” for subsequent layers, creating a composite representation, as shown in Figure 1. Our anatomy rendering approach is structured into three distinct steps, each of which can occur at different points in time: (i) image generation with a path tracer, (ii) train the layered GS representation using the rendered images, (iii) render the trained GS anatomy representation on the target device. These three steps are described in more detail in the following sections.

## 3.1 Image generation

For this experiment, we adapted an open-source path tracer<sup>1</sup>. For image generation, we scripted the path tracer to capture images from multiple angles around the object of interest. The renderer employs Monte Carlo volume path tracing. Color and density are accumulated along the traced paths in the medical volume via RGBA values defined by a transfer function. Scattering events are modeled using a Henyey-Greenstein phase function, and lighting contributions are sampled from a high dynamic range environment light map. The final rendered images are tone-mapped before saving to ensure proper dynamic range and brightness for downstream applications. We note that some features found in other path tracers, such as specularity, can be approximated by GS through spherical harmonics. In contrast, others, like depth of field, cannot be encoded and should be disabled.

GS starts optimizing from an initial (sparse) point cloud. Typically, this would be either a random point cloud for synthetic images or generated by a structure-from-motion approach like COLMAP [44] for real images. Since we have full control over the volumetric data used to render the training images, we directly generate the initial point cloud. We place points where the approximate surface of the volume will be to ensure an effective basis for Gaussian color and position. Directly translating volume voxels into a point cloud would result in most points being located inside the volume rather than on its surface. Instead, we sample points from outside the volume inward, stopping and creating a point as soon as a minimum transfer function opacity al pha treshold = 0.2 is reached. This approach results in a surface approximation of the

volume close to where the final Gaussians will be located, with correct point color. We export this point cloud, along with the created images and their corresponding camera positions and descriptions, in COLMAP format to enable the direct use in GS training.

## 3.2 Layered Training

We extend conventional GS with a layering system, enabling the inclusion of multiple distinct visual representations within a single GS point cloud. Our layering technique is particularly useful for anatomical visualization, where, for instance, layers can be trained sequentially to represent bone, muscle, and soft tissue. This is achieved through consecutive training iterations utilizing the pre-viously optimized GS as a base. In our approach, the previously optimized GS layers remain static, functioning similarly to frozen layers in NNs [45, 33]. During the training of each new layer, the existing layers are excluded from adjustments by the optimizer, ensuring they maintain their visual integrity even in the absence of the newly added layer.

The pre-optimized point clouds serve as an advanced 3D background in the rendering process, contributing to the image loss. All layers are finally consolidated into a single GS .ply file, with layer membership information stored as a property alongside attributes like color and scale. As progressive layers are optimized with pre-vious layers present, the optimization process primarily adjusts the Gaussians to represent new information, while existing lower layers contribute visual information when possible. Consequently, each new layer effectively contains a differential representation, encoding only the new data not captured by earlier layers.

## 3.2.1 Alpha Channel Training

In addition to layering, we extended the training process to preserve and utilize the alpha channel of input data. We employ two strategies: randomizing the background color for each frame instead of flattening it at the start and incorporating the alpha channel into the loss calculation. Randomized background colors improve detail in semi-transparent areas, while including the alpha channel ensures that the number of Gaussians needed to achieve this detail remains manageable.

## 3.2.2 Inactive Pruning

The standard GS optimization process also does not account for the complexities introduced by having ”frozen” layers of Gaussians that contribute to the final rendered image but cannot be adjusted

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>1</sup>[https://github.com/nihofm/volren](https://github.com/nihofm/volren)</span></small>

<!-- page 5 of 14 -->

![Image block](images/kleinbeck2024_multilayer-gs-anatomy_p5_b1.png)

Figure 4: Fullbody CT scene consisting of the three layers Bone, Organs and Muscle. Rendered with Unity and clustering compression applied. Structures are largely present, but colors are smoothed.

further. This is particularly problematic when dealing with Gaussians that do not contribute to the scene but are masked by existing layers. We extend the GS adaptive control with an additional pruning step to remove inactive Gaussians from the scene. We track the optimization of each Gaussian (position, color, scale) and remove inactive Gaussians that fail to meet a minimal activity threshold. These Gaussians are assumed to be either obscured by already optimized layers or already very well optimized, which is unlikely to occur early in the training. Gaussian activity is tracked in sync with the existing densification rate and compared against a threshold. After each pruning step, we apply exponential decay.

The average activity is computed as follows, with a densification rate dR = 100, position norm p, color norm c, and scale norm s:

$$
\text {AvgSample} = \frac {1}{d R} \sum_ {i = 1} ^ {d R} \left(2 \cdot p _ {i} + 0. 1 \cdot c _ {i} + 0. 1 \cdot s _ {i}\right)
$$

This average is compared against an initial threshold $T = 0 . 0 1 5 ;$

$$
\text {AvgSample} \leq T
$$

After each comparison, the threshold is updated using exponential decay:

$$
T _ {\text {new}} = 0. 9 7 5 \times T _ {\text {old}}
$$

The three activity components are weighted to have a comparable influence based on our data. The initial threshold and decay rate values were experimentally determined using our datasets. We tested a range of values to strike a balance between the number

![Image block](images/kleinbeck2024_multilayer-gs-anatomy_p5_b11.png)

Figure 5: Two viewpoints of synthetic transparent data trained without (first row) and with (second row) alpha channel training and randomized backgrounds. Both help to reduce visual artifacts while lowering the Gaussian count. Due to different alpha blending between applications, GS can struggle to faithfully recreate translucent regions.

of removed Gaussians and the impact on visual quality. Our approach filters out low-activity Gaussians early on, tapering off to avoid accidental removal of well-optimized Gaussians contributing to the scene. Although our default values were effective for a range of scenes in our tests, they can be fine-tuned for specific scenes to achieve optimal results.

## 3.3 Real-time Rendering

We utilize the Unity game engine in version 2022.3 as our platform for rendering due to its broad compatibility, including most VR headsets. To display our trained layered GS representation, we extend an open-source GS rendering package for Unity2. The rendering process is analogous to that described by Kerbl et al. [21], but implemented platform-agnostically in HLSL and compute shaders. The rendering employs wave operations to achieve real-time rendering, making it incompatible with older devices and OpenGL rendering, but should otherwise export to most modern platforms. Notably, the implementation does not rely on CUDA. The rendering of our GS representations involves two main steps. First, the GS point cloud file is imported, compressed, and transformed into GPU-friendly buffers for rapid access. At runtime, the buffers are transferred to the device’s GPU. The Gaussians are continuously sorted relative to the virtual camera position and rendered as splats. To optimize resource usage, we only transfer actively rendered layers to the GPU, while unused layers are kept in RAM.

While compression is not the primary focus of this work, it is crucial for both reducing storage footprint and GPU memory con-

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>2</sup>[https://github.com/aras-p/UnityGaussianSplatting](https://github.com/aras-p/UnityGaussianSplatting)</span></small>

<!-- page 6 of 14 -->

Table 1: Comparison of sizes between layered and stand-alone training. Standalone does generally incur higher storage requirements compared to layered Gaussians. The reported size are before and after clustering compression, plus the number of Gaussians in parenthesis. The size and Gaussian count for layered representations include all lower layers as they are required for accurate rendering.

<table><tbody><tr><td rowspan="2"></td><td colspan="2">Leg</td><td colspan="2">Fullbody</td><td colspan="2">Synthetic 3Layer</td></tr><tr><td>Layered</td><td>Standalone</td><td>Layered</td><td>Standalone</td><td>Layered</td><td>Standalone</td></tr><tr><td>Layer 1</td><td>14.5/3.4 (57k)</td><td>14.5/3.4 (57k)</td><td>25.0/4.7 (99k)</td><td>25.0/4.7 (99k)</td><td>17.3/3.7 (69k)</td><td>17.3/3.7 (69k)</td></tr><tr><td>Layer 2</td><td>30.8/5.4 (122k)</td><td>17.2/3.8 (68k)</td><td>34.7/5.9 (138k)</td><td>20.4/4.2 (81k)</td><td>40.0/6.5 (159k)</td><td>29.9/5.2 (119k)</td></tr><tr><td>Layer 3</td><td>34.4/5.8 (137k)</td><td>14.9/3.5 (59k)</td><td>49.3/7.6 (196k)</td><td>20.9/4.2 (83k)</td><td>41.7/6.7 (166k)</td><td>25.6/4.7 (102k)</td></tr><tr><td>Combined</td><td>34.4/5.8 (1379k)</td><td>46.6/10.7 (184k)</td><td>49.3/7.6 (196k)</td><td>66.3/13.1 (262k)</td><td>41.7/6.7 (166k)</td><td>72.8/13.6 (291k)</td></tr></tbody></table>

sumption, especially on mobile devices. Through the Unity rendering package, we apply quantization to the Gaussian parameters. Since spherical harmonics coefficients are a significant portion of the file size (approximately 3/4 of the total size) and are the least noticeable when modified, we use K-means clustering to further compress them, similar to [38]. This is particularly effective because we cluster across all input file layers, allowing information to be shared. Volume renderings typically use a limited color palette, further enhancing the effectiveness of this approach. An example of our Unity rendering can be seen in Figure 4.

The Gaussians must be constantly sorted relative to the viewer during rendering to ensure correct display. In VR, this sorting must be performed twice—once for each eye. The sorting of splats can differ slightly between the two eyes; however, it does mostly for splats very close to the rendering camera. We explore an optimization in which the sorting is shared between both eyes, effectively halving the sorting time per frame. We use two sorting algorithms: AMD FidelityFX Parallel Sort (FFXPS) and an implementation derived from OneSweep [1], DeviceRadixSort. DeviceRadixSort is roughly twice as fast as FFXPS but faces compatibility issues with many mobile devices through Unity shader transpilation.

## 4 EVALUATION

Our approach enables the integration of multiple GS representations into a single cohesive scene by overlaying anatomical layers, rather than having isolated representations. In this section, we analyze the storage and computational requirements of our method, along with the impacts of extensions such as inactive pruning and alpha channel training. We evaluate our approach using both realworld CT scans and specifically created synthetic data.

## 4.1 Metrics

To compare the rendering quality of the novel views, we report peak signal-to-noise ratio (PSNR), similarity index measure (SSIM) [49] and learned perceptual image patch similarity (LPIPS) [56]. We report file sizes in MB. Where possible, values are reported with one standard deviation after ± sign.

## 4.2 Datasets

To test our layered approach, we generate two datasets: one from real CT scans and another with synthetic images. The anatomies we use are **Lower Body** [59]<sup>3</sup>, a human lower body CT scan. It has a high resolution of $5 1 2 \times 5 1 2 \times 3 0 0 0$ voxels at $\dot { 0 } . 7 \times 0 . 7 \times 0 . 3$ mm each. The **Legs** scan is one leg isolated from the lower body scan. It has a resolution of $1 9 5 \times \tilde { 2 5 7 } \times 3 0 0 0$ voxels at unchanged dimensions. The **Fullbody** scan4is a near-complete human body scan from neck to ankles. We removed the patient bed and cropped the scan to $3 1 7 \times 1 6 3 \times 8 3 5$ voxels. Each anatomy scene includes

Table 2: Comparison of medical volumes on-disk sizes before and after training and compression. The size of the reconstruction is independent of the original volume resolution and more influenced by the visual complexity of the rendered anatomy.

|  | Leg | Lowerbody | Fullbody |
| --- | --- | --- | --- |
| Original Volume (DICOM) | 304.7 | 1585.1 | 87.4 |
| Compressed (.nii.gz) | 73.5 | 730.8 | 75.5 |
| GS PLY file (ours) | 34.4 | 23.0 | 49.3 |
| Layered GS (default comp.) | 12.8 | 8.6 | 18.2 |
| Layered GS (clustering) | 5.8 | 4.5 | 7.6 |

512 images, of which we use every 8th for testing, each 1600 px × 1600 px, from various poses.

Additionally, we created synthetic scenes to highlight layer reconstruction and investigate potential problematic cases. Each comprises 256 training and 32 test images at 1400 px×1400 px. The **Two Layer** scene contains a plain white cube in the first layer; the outer layer is a 5% bigger cube with a white and blue pattern. The scene allows testing GS approaches for redundant Gaussians or ones located in obscured areas. The **Three Layer** scene assesses the definition of each layer in scenarios with sparse overlap and complex shapes. The first layer is an opaque green and black checkered shape, the second layer is a red and black cube outline around the first layer, and the third layer includes two semi-transparent green rings looping through the second layer. Aside from layering, the **Transparency** scene is a single-layer scene featuring two cubes with varying levels of transparency. The light green cube is 75% transparent, while the light blue cube is 62.5% transparent.

## 4.3 Parametrization Details

Optimizing our GS representations, we balanced image quality and rendering speed to achieve real-time performance on immersive displays. These targets are directly influenced by the number of Gaussians generated during the optimization process, which is, in turn, affected by the training parameters. We train two representations of our anatomic data to gauge the impact of parameter choice and Gaussian count. The default reconstruction uses the default GS parameters; for the training of the high quality (HQ) one, we set densi f y grad threshold = 0.0001 and percent $\begin{array} { r } { d e n s e = 0 . 0 0 5 , } \end{array}$ resulting in a roughly two to fourfold increase in the number of Gaussians created. All anatomy scenes use initial point clouds with approximately 100,000 points.

We further evaluate two compression levels. We either use low compression, converting point cloud parameters to 16-bit floats and reducing spherical harmonics coefficients to 6 bytes per triplet, roughly 10.6 bits per color channel. For high compression, we apply more aggressive quantization and use K-means clustering to compress spherical harmonics coefficients into 16k known variants. This compression level is referred to as clustered throughout the work. Comparisons of file sizes can be found in Table 2.

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>3</sup>TCGA-HNSC dataset, id TCGA-CV-A6JU, [https://www.cancerimagingarchive.net/collection/tcga-hnsc/](https://www.cancerimagingarchive.net/collection/tcga-hnsc/)</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>4</sup>TotalSegmentator dataset [50], id s0287, [https://zenodo.org/records/10047292](https://zenodo.org/records/10047292)</span></small>

<!-- page 7 of 14 -->

Table 3: Rendering time in ms & quality comparison on the leg scene. Images were rendered at 2000 $\mathsf { p x } \times \mathsf { 2 0 0 0 \; p x } \times \mathsf { 2 }$ (exemplary VR device) on a PC with an Nvidia RTX 4090 GPU. Path traces with 4 bounces. Values are reported over all test images with one standard deviation. DVR values are illustrative examples, as the rendered images need to be brightness adjusted and will always be slightly different. Denoising with Open Image Denoise, raw render time parenthesis.

<table><tbody><tr><td rowspan="2"></td><td colspan="3">Path tracer</td><td colspan="3">Layered GS in Unity (Ours)</td></tr><tr><td>1024 samples</td><td>1 sample + denoise</td><td>DVR</td><td>HQ recon/low comp.</td><td>low comp.</td><td>high compression</td></tr><tr><td>Time (ms)</td><td>7116.4 ± 2251.3</td><td>66.0 ± 10.6 (19.9)</td><td>17.9 ± 10.2</td><td>1.7 ± 0.4</td><td>1.3 ± 0.4</td><td>1.4 ± 0.4</td></tr><tr><td>PSNR ↑</td><td>42.399 ± 2.198</td><td>26.658 ± 2.596</td><td>24.258 ± 3.514</td><td>37.662 ± 2.335</td><td>35.463 ± 3.170</td><td>35.258 ± 3.088</td></tr><tr><td>SSIM ↑</td><td>0.988 ± 0.005</td><td>0.945 ± 0.018</td><td>0.914 ± 0.033</td><td>0.969 ± 0.012</td><td>0.964 ± 0.014</td><td>0.963 ± 0.015</td></tr><tr><td>LPIPS ↓</td><td>0.020 ± 0.010</td><td>0.081 ± 0.032</td><td>0.083 ± 0.033</td><td>0.054 ± 0.025</td><td>0.062 ± 0.029</td><td>0.063 ± 0.029</td></tr></tbody></table>

Table 4: Rendering time of Leg scene in ms on different HMD devices at their native resolution. Varjo Aero is a desktop VR system driven by an Nvidia RTX 4090, Meta Quest 3 is a standalone mobile VR system, MacBook is an Apple laptop with M3 Pro CPU/GPU.

| Sort HQ Varjo Aero | Meta Quest 3 | MacBook |
| --- | --- | --- |
| 2.6 ± 0.8 | 17.6 ± 5.9 | 4.8 ± 1.5 |
| 2.5 ± 0.8 | 10.2 ± 2.1 | 4.5 ± 1.3 |
| 3.6 ± 1.0 | 26.6 ± 7.0 | 6.4 ± 1.9 |
| 3.4 ± 0.9 | 16.3 ± 2.2 | 6.0 ± 1.6 |

![Image block](images/kleinbeck2024_multilayer-gs-anatomy_p7_b5.png)

Figure 6: Synthetic two-layer scene, trained without and with inactive pruning. The left and middle segments show only the second layer which does not contain the white pattern, as the lower layer provides them. Notice the colored artifacts of unoptimized Gaussians normally covered by the lower layer, removed by inactive pruning.

## 4.4 Performance Analysis

## 4.4.1 Speed

As shown in Table 3, our GS representation outperforms classical and denoised path tracing, as well as DVR. This performance advantage is notable even though our path tracer uses advanced techniques, such as a multi-level digital differential analyzer, to improve speed and reduce memory usage [16]. It is also important to consider pathological cases: In point cloud rendering, performance is more predictable and depends largely on the Gaussian count. In contrast, volume rendering speed is tied to the number of pixels requiring color calculations, leading to performance breakdowns during close-up views. In worst-case scenarios in our test set, some images can exceed four times the average render time, compared to around 1.6 times for GS. Rendering on mobile and desktop VR devices performs well overall. However, standalone immersive devices like the Quest 3 show performance bottlenecks, as seen in Table 4. We found that sorting Gaussians for the eye center only, rather than both eyes, and reducing sorting frequency can enhance frame rates with minor visual compromises. These findings suggest a potential for high-quality anatomical visualization on hardware with limited capabilities. Note that the Unity GS plugin we built upon has limited compatibility across mobile headset platforms and Unity render pipelines. On platforms supporting both the built-in and URP render pipelines, we observed no significant performance differences.

## 4.4.2 Quality

GS effectively reconstructs complex anatomies from path-traced volumetric inputs in our test scenes, achieving high visual quality scores (see Table 3). Each layer can be rendered independently but should be displayed with all lower layers for optimal results as trained. While internal views of trained GS models may appear messy, frontal and side views can provide interactive, engaging visualizations of otherwise static representations (see Figure 1). Reconstruction quality primarily depends on the number of Gaussians, generally outperforming path tracing at low sample sizes (see Table 3). However, fine details may appear blurry, especially in low-frequency regions. High-contrast features are accurately reconstructed when sufficient contrast is available. In close-ups, individual Gaussians are often visible. The quality of the initial point cloud also influences the optimization process. A well-structured initial point cloud leads to better early visuals and improved overall results. Random initialization may struggle to distribute Gaussians effectively in sparse areas, leading to smudging artifacts. We experimented with antialiasing as described in [54], but observed minimal improvements, likely due to our dataset’s low variation in camera distances.

## 4.4.3 Size

GS offers significant storage advantages over traditional volume files for path tracing, typically stored in DICOM format (see Table 2). File sizes depend primarily on the applied transfer function and visual complexity of the anatomy, rather than volume resolution. Size reductions of up to 99% compared to original DICOM files are achievable. While many small details can be preserved (compare Figure 4), this comes at the cost of spatial accuracy. Still, this reduction can benefit deployment to and storage on mobile devices. Although GS parameters can be adjusted to control quality and size, fine-tuning this balance remains challenging.

## 4.5 Layering

Our layering approach integrates well with the GS optimization process. Gaussians are generally positioned where changes are most needed during optimization, keeping areas already wellrepresented by lower layers relatively free from unnecessary Gaussians (see Figure 3). Layering is particularly efficient when there is minimal overlap between layers. The number of Gaussians required to encode new information depends on how much of the scene is obscured by the new layer and its visual complexity. Generally, this approach results in a smaller file size than training each target scene independently, as shown in Table 1. However, we also identified issues during optimization and subsequent rendering of upper layers, as the presence of background layers containing relevant information was not considered in the original paper. Our inactive pruning approach addresses these issues.

<!-- page 8 of 14 -->

![Image block](images/kleinbeck2024_multilayer-gs-anatomy_p8_b1.png)

Figure 7: Comparison of ours and CLNeRF [5] on the Leg scene.

## 4.6 Inactive Pruning

When optimizing a layer with one or more already finished layers loaded, some areas might be wholly obscured from all camera views. Certain areas may become completely obscured from all camera views, such as the insides of bones. Gaussians inside these areas appear perfectly optimized during the optimization process, even though they add no information to the rendered scene. Since the optimization process does not recognize that these Gaussians are redundant, they are neither pruned nor relocated. Similarly, Gaussians that are close to already optimized layers and happen to look similar are also not pruned or moved, even though they contribute little new information. Our inactive pruning method removes these and other inactive Gaussians, as seen in Figure 6.

## 4.7 Alpha Channel Training

In the original GS training procedure, the alpha channel was not considered. This omission is particularly problematic when dealing with synthetic renders and transparent backgrounds, as it can cause the background color to bleed into semi-transparent areas, causing artifacts. This effect is most pronounced with few views of the semi-transparent area. As shown in Figure 5, training with randomized background colors and including the alpha channel in the loss function improves visual fidelity. Randomized background colors help most to improve visual quality, while including the alpha channel reduces the number of Gaussians needed to achieve this improvement.

## 4.8 Continual Learning and Novel View Synthesis

Since our work can be seen as a part of continual learning, we compared our work to CLNeRF [5] on layered scenes of our synthetic dataset. CLNeRF and other continual learning approaches [9, 40] usually assume a stacking of the scene. Due to the high memory consumption of CLNeRF and high image resolution, we used a subset for comparing to continual learning, adapting the dataset using every 4th image per layer, starting from an incremental index to avoid exactly matching camera poses, which is the commonly used data structure in CLNeRF.

Instant-NGP-based CLNerf is challenged by fine structures of anatomical data and bones show ripple artifacts. Although the results in Table 5 show promising results, our approach can better represent the fine structures, even with fewer images. Moreover, the rendering time increases due to the replay buffer prevent realtime VR use. To compare anatomic data, we use images with a resolution of 1600x1600, following their original implementation.

Table 5: Continual Learning comparison on reduced Leg & Fullbody scenes.

<table><tr><td rowspan="2"></td><td colspan="3">CLNeRF [5]</td><td colspan="3">Ours</td></tr><tr><td>PSNR ↑</td><td>SSIM ↑</td><td>LPIPS ↓</td><td>PSNR ↑</td><td>SSIM ↑</td><td>LPIPS ↓</td></tr><tr><td>Leg</td><td>39.952</td><td>0.974</td><td>0.042</td><td>35.481</td><td>0.974</td><td>0.040</td></tr><tr><td>Fullbody</td><td>35.850</td><td>0.964</td><td>0.064</td><td>37.378</td><td>0.973</td><td>0.041</td></tr></table>

## 5 DISCUSSION

In this work, we demonstrate that GS can create useful representations of path-traced volumetric anatomy data. While a careful balance must be struck regarding reconstruction fidelity and render speed, we have shown that anatomy representations can achieve useful quality levels on mobile and immersive hardware.

Creation and Rendering Our experiments demonstrate that GS can achieve high-quality anatomy visualization on mobile and immersive hardware, even for resource-constrained devices. The visual quality achieved is promising for anatomy rendering, corroborating the findings of Niedermayer et al. [39]. However, the computational demands are significant, particularly when aiming for optimal visual fidelity. Further quality improvements could be achieved through more sophisticated view selection algorithms. Optimizing for voxel visibility gain and view angle diversity can improve quality and generation time without significant runtime impact [47]. We opted for a more straightforward generation approach, rendering more viewpoints in this work as our focus was not on dataset generation. It would also be possible to significantly reduce the time to view new GS visualizations from initial parameter selection by using more conservative parameters, fewer samples, denoising, or super-sampling. We tested our approach mainly on imagery generated from CT data, but the approach should extend to other kinds of volumetric data. CT scans containing contrasting agents, multi-energy data from photon-counting CTs scanners, or magnetic resonance imaging data could be visualized with this approach, possibly with preparation steps like tissue segmentation.

One of the primary challenges in our work stems from the conflicting goals of maximizing visual quality, minimizing file size, and achieving interactive frame rates in rendering. Increasing the quality of the GS anatomy representation is usually achieved by adjusting training parameters to increase the resulting Gaussian count. The increased Gaussian count leads to larger storage requirements and lower rendering performance. To mitigate this, we employ basic compression techniques and clustering. While our approach yields significant reductions in file size compared to industry-standard DICOM files and compressed volumes, further gains could be achieved by adopting more advanced methods from recent literature. Some compression techniques selectively retain relevant Gaussians, akin to our pruning approach. Combining these methods could further benefit mobile platforms by reducing Gaussian count, which is the leading performance bottleneck. Given the importance of Gaussian count in balancing quality and performance, finer control of their creation during the optimization process would be valuable. Currently, it’s challenging to predict and adjust how many Gaussians will be used to encode a given volume.

Layering Approach Our layering approach has potential for bringing more interactivity to GS and complex visualization to VR. However, we identified some inefficiencies that the original 3DGS approach did not consider and that our approach initially exacerbated. To address this, we introduced an inactive pruning technique to remove superfluous Gaussians that don’t significantly contribute to the final rendered image. While this approach reduces clutter and improves efficiency, it faces challenges in differentiating between inactive Gaussians due to being obscured by lower layers and those already optimally positioned. We used pruning with exponential

<!-- page 9 of 14 -->

falloff with the assumption that inactive Gaussians early in the optimization depend on information from the lower layers and can be removed. Still, alternative strategies might handle this trade-off differently. It should be noted that pruning also reduces the jarring experience of seeing unoptimized Gaussians while cutting through layers, which is not captured by our metrics.

The layering technique functions by encoding differences between layers, similar to how video codecs encode frame content as differences from previous frames. However, unlike video codecs, our current implementation doesn’t allow upper layers to override, modify, or hide information from lower layers. Allowing upper layers to modify lower ones might offer more flexibility in representable information. Still, by avoiding interactions between layers, our current system ensures that each layer can be independently displayed and cut with manageable complexity.

A benefit of layering is that it generally results in smaller overall file sizes compared to training each anatomy view separately. However, this storage benefit comes with a potential increase in the number of Gaussians needed at runtime to display the same anatomy properly. The efficiency of the layered approach depends on how much of the lower layer is obscured by new information and how much can be reused. In anatomical data, we observed that adding muscles on top of bones doesn’t result in significant storage savings, as most of the bone is obscured by muscle. However, adding a few blood vessels on top of muscle could be very lightweight. The global illumination effects inherent in path tracing complicate this, as even minor visual changes can affect the luminosity and color of nearby pixels, requiring additional Gaussians for minor visual changes. This challenge suggests that layered representations may be more situational in performance-constrained environments. Still, we observed solid performances on tested devices, suggesting that this approach is feasible for real-world scenarios.

Layering also introduces more interactivity to GS rendering. The ability to cut to lower layers provides a reasonable visualization as long as the viewer doesn’t look ”inside” the cut layer, where optimization hasn’t occurred. This opens opportunities for effects like fading between layers, which would be difficult to achieve with separate GS representations.The visual quality of cutting edges depends on the Gaussian point cloud density at the edge. Smarter cutting algorithms, considering the full area covered by splats, could improve edge sharpness at a minor performance cost.

## 5.1 Limitations

While our layered GS approach demonstrates significant potential for medical volumetric data visualization, it’s important to acknowledge its current limitations. Although slicing layers is an improvement over static representations, there remains considerable room for enhancement to support full interactivity comparable to traditional volume rendering techniques. In cases where an upper layer obscures most of a lower one, both layers are required for accurate rendering, increasing the number of displayed splats. This might be addressed by enhancing the rendering or pruning process to remove redundant Gaussians from lower layers that do not contribute visually. Performance constraints also remain a consideration, particularly on standalone VR devices. While our approach is significantly more real-time capable than path tracing, the amount of detail we can include in a GS representation that runs smoothly on these devices is limited. Zooming in on small structures, especially on low contrast regions, quickly reveals a lack of detail and splatting artifacts. We believe that the achievable detail is sufficient for many practical applications in medical visualization, but performance remains a bottleneck.

## 5.2 Future Work

Future research could focus on increasing the interactivity of GS, especially while using a layered approach. More work is also

needed in improving layer compression to avoid the performance cost of rendering all lower layers, or further refining the layering approach to ensure efficient encoding of new information. Additionally, the concept of layered GS is not restricted to anatomy data. Inclusion of additional information that can be inferred from the existing data could also be explored, like depth maps for depth regularization. Future research could also explore its application in other domains with tight control over data, such as mechanical visualizations, industrial scans, or generative visualizations. These diverse applications could yield new insights and optimization techniques that could, in turn, benefit medical visualization.

## 6 CONCLUSION

We introduce a layered GS reconstruction that can encode multiple visualizations of the same volume data, building upon each other similar to multiple transfer functions in traditional volume rendering. Extending the GS adaptive control, we introduce inactive pruning to remove inactive Gaussians introduced in our layering approach. With this intermediate GS representation, we can use high-quality medical volume rendering to otherwise computeconstrained scenarios, especially VR. Our approach adds opportunities for interactivity to GS rendering, such as the ability to cut through different layers, emulating how volume visualizations are currently used in medical practice. While still more experimentation and work are needed to bring full interactivity to GS, we believe this approach can be useful for planning and educational situations where real-time path tracing is not viable or semi-static representations are sufficient.

## ACKNOWLEDGMENTS

We want to thank Nikolai Hofmann for valuable insights regarding the used path tracer and d.hip for providing a campus stipend.

## SUPPLEMENTARY MATERIAL

Supplemental materials, generated training data, and trained models are available at [https://osf.io/tuwh5/](https://osf.io/tuwh5/). Code is available at [https://github.com/roth-hex-lab/Multi-Layer-Anatomy-GS-Unity-Rendering](https://github.com/roth-hex-lab/Multi-Layer-Anatomy-GS-Unity-Rendering). The original CT volumes used in this work are available from their respective authors.

## REFERENCES

[1] [A. Adinets and D. Merrill. Onesweep: A Faster Least Significant Digit Radix Sort for GPUs](https://doi.org/10.48550/arXiv.2206.01784), [June 2022](https://doi.org/10.48550/arXiv.2206.01784). [doi: 10.48550/arXiv.2206.01784](https://doi.org/10.48550/arXiv.2206.01784) 6

[2] [M. T. Bagdasarian, P. Knoll, F. Barthel, A. Hilsmann, P. Eisert, and W. Morgenstern. 3DGS.zip: A survey on 3D Gaussian Splatting Compression Methods](https://doi.org/10.48550/arXiv.2407.09510), [July 2024](https://doi.org/10.48550/arXiv.2407.09510). [doi: 10.48550/arXiv.2407.09510](https://doi.org/10.48550/arXiv.2407.09510) 3

[3] [J. Binder, C. Krautz, K. Engel, R. Grutzmann, F. A. Fellner, P. H. M. ¨ Burger, and M. Scholz. Leveraging medical imaging for medical edu cation — A cinematic rendering-featured lecture](https://doi.org/10.1016/j.aanat.2018.12.004). [Annals of Anatomy - Anatomischer Anzeiger, 222:159–165](https://doi.org/10.1016/j.aanat.2018.12.004), [Mar. 2019. doi: 10.1016/j. aanat.2018.12.004](https://doi.org/10.1016/j.aanat.2018.12.004) 1, 2

[4] [J. S. Binder, M. Scholz, S. Ellmann, M. Uder, R. Grutzmann, G. F. We- ¨ ber, and C. Krautz. Cinematic Rendering in Anatomy: A Crossover Study Comparing a Novel 3D Reconstruction Technique to Conventional Computed Tomography. Anatomical Sciences Education, 14(1):22–31, 2021. doi: 10.1002/ase.1989](https://doi.org/10.1002/ase.1989) 1, 2

[5] [Z. Cai and M. Muller ¨ . CLNeRF: Continual Learning Meets NeRF. In 2023 IEEE/CVF International Conference on Computer Vision (ICCV), pp. 23128–23137](https://doi.org/10.1109/ICCV51070.2023.02119). [IEEE, Paris, France, Oct. 2023](https://doi.org/10.1109/ICCV51070.2023.02119). [doi: 10. 1109/ICCV51070.2023.02119](https://doi.org/10.1109/ICCV51070.2023.02119) 3, 8

[6] [N. Cardobi, R. Nocini, G. Molteni, V. Favero, A. Fior, D. Marchioni, S. Montemezzi, and M. D’Onofrio. Path Tracing vs. Volume Rendering Technique in Post-Surgical Assessment of Bone Flap in Oncologic Head and Neck Reconstructive Surgery: A Preliminary Study. Journal of Imaging, 9(2):24](https://doi.org/10.3390/jimaging9020024), [Feb. 2023](https://doi.org/10.3390/jimaging9020024). [doi: 10.3390/jimaging9020024](https://doi.org/10.3390/jimaging9020024) 2

<!-- page 10 of 14 -->

[7] [M. T. Caton Jr., W. F. Wiggins, and D. Nunez](https://doi.org/10.1111/jon.12697). [Three-Dimensional Cinematic Rendering to Optimize Visualization of Cerebrovascular Anatomy and Disease in CT Angiography](https://doi.org/10.1111/jon.12697). [Journal of Neuroimaging, 30(3):286–296, 2020. doi: 10.1111/jon.12697](https://doi.org/10.1111/jon.12697) 2

[8] [Y. Chen, Q. Wu, W. Lin, M. Harandi, and J. Cai. HAC: Hash-grid Assisted Context for 3D Gaussian Splatting Compression, July 2024. doi: 10.48550/arXiv.2403.14530](https://doi.org/10.48550/arXiv.2403.14530) 3

[9] [J. Chung, K. Lee, S. Baik, and K. M. Lee](https://doi.org/10.48550/arXiv.2212.08328). [MEIL-NeRF: Memory-Efficient Incremental Learning of Neural Radiance Fields](https://doi.org/10.48550/arXiv.2212.08328), [Dec. 2022. doi: 10.48550/arXiv.2212.08328](https://doi.org/10.48550/arXiv.2212.08328) 3, 8

[10] [D. Comaniciu, K. Engel, B. Georgescu, and T. Mansi. Shaping the future through innovations: From medical imaging to precision medicine. Medical Image Analysis, 33:19–26, Oct. 2016. doi: 10. 1016/j.media.2016.06.016](https://doi.org/10.1016/j.media.2016.06.016) 1, 2

[11] [E. Dappa, K. Higashigaito, J. Fornaro, S. Leschka, S. Wildermuth, and H. Alkadhi](https://doi.org/10.1007/s13244-016-0518-1). [Cinematic rendering – an alternative to volume rendering for 3D computed tomography imaging. Insights into Imaging, 7(6):849–856, Dec. 2016. doi: 10.1007/s13244-016-0518-1](https://doi.org/10.1007/s13244-016-0518-1) 2, 3

[12] [N. Deng, Z. He, J. Ye, B. Duinkharjav, P. Chakravarthula, X. Yang, and Q. Sun. FoV-NeRF: Foveated Neural Radiance Fields for Virtual Reality. IEEE Transactions on Visualization and Computer Graphics, 28(11):3854–3864, Nov. 2022. doi: 10.1109/TVCG.2022.3203102](https://doi.org/10.1109/TVCG.2022.3203102) 3

[13] [K. Engel, M. Hadwiger, J. M. Kniss, and C. Rezk-Salama](https://doi.org/10.2312/egt.20061064). [Real-Time Volume Graphics. In N. Magnenat-Thalmann and K. Buhler, eds., ¨ Eurographics 2006: Tutorials](https://doi.org/10.2312/egt.20061064). [The Eurographics Association, 2006. doi: 10.2312/egt.20061064](https://doi.org/10.2312/egt.20061064) 1, 2

[14] [G. Frieder, D. Gordon, and R. Reynolds. Back-to-Front Display of Voxel Based Objects. IEEE Computer Graphics and Applications, 5(1):52–60, 1985. doi: 10.1109/MCG.1985.276273](https://doi.org/10.1109/MCG.1985.276273) 1

[15] [P. A. Glemser, K. Engel, D. Simons, J. Steffens, H.-P. Schlemmer, and B. Orakcioglu](https://doi.org/10.1016/j.wneu.2018.02.174). [A New Approach for Photorealistic Visualization of Rendered Computed Tomography Images](https://doi.org/10.1016/j.wneu.2018.02.174). [World Neurosurgery, 114:e283–e292, June 2018. doi: 10.1016/j.wneu.2018.02.174](https://doi.org/10.1016/j.wneu.2018.02.174) 2

[16] [N. Hofmann and A. Evans](https://doi.org/10.1007/978-1-4842-7185-8_43). [Efficient Unbiased Volume Path Tracing on the GPU. In A. Marrs, P. Shirley, and I. Wald, eds., Ray Tracing Gems II: Next Generation Real-Time Rendering with DXR, Vulkan, and OptiX](https://doi.org/10.1007/978-1-4842-7185-8_43), [pp. 699–711](https://doi.org/10.1007/978-1-4842-7185-8_43). [Apress](https://doi.org/10.1007/978-1-4842-7185-8_43), [Berkeley, CA](https://doi.org/10.1007/978-1-4842-7185-8_43), [2021](https://doi.org/10.1007/978-1-4842-7185-8_43). [doi: 10.1007/ 978-1-4842-7185-8 43](https://doi.org/10.1007/978-1-4842-7185-8_43) 7

[17] [N. Hofmann, J. Martschinke, K. Engel, and M. Stamminger](https://doi.org/10.1145/3406181). [Neural Denoising for Path Tracing of Medical Volumetric Data](https://doi.org/10.1145/3406181). [Proceedings of the ACM on Computer Graphics and Interactive Techniques, 3(2):1–18, Aug. 2020. doi: 10.1145/3406181](https://doi.org/10.1145/3406181) 2

[18] [Y. Huo and S.-e. Yoon. A survey on deep learning-based Monte Carlo denoising. Computational Visual Media](https://doi.org/10.1007/s41095-021-0209-9), [7(2):169–185](https://doi.org/10.1007/s41095-021-0209-9), [June 2021. doi: 10.1007/s41095-021-0209-9](https://doi.org/10.1007/s41095-021-0209-9) 2

[19] [J. A. Iglesias-Guitian, P. Mane, and B. Moon. Real-Time Denoising of Volumetric Path Tracing for Direct Volume Rendering](https://doi.org/10.1109/TVCG.2020.3037680). [IEEE Transactions on Visualization and Computer Graphics](https://doi.org/10.1109/TVCG.2020.3037680), [28(7):2734–2747, July 2022. doi: 10.1109/TVCG.2020.3037680](https://doi.org/10.1109/TVCG.2020.3037680) 2

[20] [Y. Jiang, C. Yu, T. Xie, X. Li, Y. Feng, H. Wang, M. Li, H. Lau, F. Gao, Y. Yang, and C. Jiang](https://doi.org/10.1145/3641519.3657448). [VR-GS: A Physical Dynamics-Aware Interactive Gaussian Splatting System in Virtual Reality. In ACM SIG-GRAPH 2024 Conference Papers, SIGGRAPH ’24, p. 1](https://doi.org/10.1145/3641519.3657448). [Association for Computing Machinery, New York, NY, USA](https://doi.org/10.1145/3641519.3657448), [July 2024](https://doi.org/10.1145/3641519.3657448). [doi: 10. 1145/3641519.3657448](https://doi.org/10.1145/3641519.3657448) 3

[21] [B. Kerbl, G. Kopanas, T. Leimkuhler, and G. Drettakis ¨ . 3d gaussian splatting for real-time radiance field rendering. ACM Transactions on Graphics, 42(4), July 2023.](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) 3, 5

[22] [B. Kerbl, A. Meuleman, G. Kopanas, M. Wimmer, A. Lanvin, and G. Drettakis](https://doi.org/10.1145/3658160). [A Hierarchical 3D Gaussian Representation for Real-Time Rendering of Very Large Datasets. ACM Transactions on Graphics, 43(4):1–15, July 2024. doi: 10.1145/3658160](https://doi.org/10.1145/3658160) 3

[23] [C. Kleinbeck, M. Smietana, N. Lewis, T. Teufel, J. Kreimeier, C. Heinzl, J. Steiner, C. Anthes, and D. Roth. Adaptive Volumetric Anatomy Visualization in VR with Tangible Control. In 2023 IEEE International Symposium on Mixed and Augmented Reality Adjunct (ISMAR-Adjunct)](https://doi.org/10.1109/ISMAR-Adjunct60411.2023.00131), [pp. 613–614](https://doi.org/10.1109/ISMAR-Adjunct60411.2023.00131), [Oct. 2023. doi: 10.1109/ISMAR -Adjunct60411.2023.00131](https://doi.org/10.1109/ISMAR-Adjunct60411.2023.00131) 2

[24] [C. Kleinbeck, H. Zhang, B. D. Killeen, D. Roth, and M. Unberath. Neural digital twins: reconstructing complex medical environments](https://doi.org/10.1007/s11548-024-03143-w)

[for spatial planning in virtual reality. International Journal of Computer Assisted Radiology and Surgery, May 2024. doi: 10.1007/ s11548-024-03143-w](https://doi.org/10.1007/s11548-024-03143-w) 3

[25] [T. Kroes, F. H. Post, and C. P. Botha. Exposure Render: An Interactive Photo-Realistic Volume Rendering Framework](https://doi.org/10.1371/journal.pone.0038586). [PLOS ONE, 7(7):e38586, July 2012](https://doi.org/10.1371/journal.pone.0038586). [doi: 10.1371/journal.pone.0038586](https://doi.org/10.1371/journal.pone.0038586) 2

[26] [M. Levoy. Display of surfaces from volume data](https://doi.org/10.1109/38.511). [IEEE Computer Graphics and Applications](https://doi.org/10.1109/38.511), [8(3):29–37](https://doi.org/10.1109/38.511), [May 1988. doi: 10.1109/38. 511](https://doi.org/10.1109/38.511) 1

[27] [M. Levoy and P. Hanrahan. Light field rendering](https://doi.org/10.1145/237170.237199). [In Proceedings of the 23rd annual conference on Computer graphics and interactive techniques](https://doi.org/10.1145/237170.237199), [SIGGRAPH ’96](https://doi.org/10.1145/237170.237199), [pp. 31–42](https://doi.org/10.1145/237170.237199). [Association for Computing Machinery, New York, NY, USA](https://doi.org/10.1145/237170.237199), [Aug. 1996. doi: 10.1145/237170. 237199](https://doi.org/10.1145/237170.237199) 2

[28] [C. Li, S. Li, Y. Zhao, W. Zhu, and Y. Lin. RT-NeRF: Real-Time On-Device Neural Radiance Fields Towards Immersive AR/VR Rendering. In Proceedings of the 41st IEEE/ACM International Conference on Computer-Aided Design](https://doi.org/10.1145/3508352.3549380), [ICCAD ’22](https://doi.org/10.1145/3508352.3549380), [pp. 1–9. Association for Computing Machinery](https://doi.org/10.1145/3508352.3549380), [New York, NY, USA](https://doi.org/10.1145/3508352.3549380), [Dec. 2022. doi: 10. 1145/3508352.3549380](https://doi.org/10.1145/3508352.3549380) 3

[29] [L. Li, Z. Shen, Z. Wang, L. Shen, and L. Bo. Compressing Volumetric Radiance Fields to 1 MB, Nov. 2022](https://doi.org/10.48550/arXiv.2211.16386). [doi: 10.48550/arXiv.2211. 16386](https://doi.org/10.48550/arXiv.2211.16386) 3

[30] [H. Liu, Y. Liu, C. Li, W. Li, and Y. Yuan](https://arxiv.org/abs/2406.16073). [Lgs: A light-weight 4d gaussian splatting for efficient surgical scene reconstruction](https://arxiv.org/abs/2406.16073), [2024](https://arxiv.org/abs/2406.16073). 3

[31] [Y. Liu, C. Li, C. Yang, and Y. Yuan. EndoGaussian: Real-time Gaussian Splatting for Dynamic Endoscopic Scene Reconstruction](https://doi.org/10.48550/arXiv.2401.12561), [Feb. 2024. doi: 10.48550/arXiv.2401.12561](https://doi.org/10.48550/arXiv.2401.12561) 3

[32] [P. Ljung, J. Kruger, E. Groller, M. Hadwiger, C. D. Hansen, and ¨ A. Ynnerman. State of the Art in Transfer Functions for Direct Volume Rendering](https://doi.org/10.1111/cgf.12934). [Computer Graphics Forum, 35(3):669–691, 2016. doi: 10.1111/cgf.12934](https://doi.org/10.1111/cgf.12934) 2

[33] [A. Mallya and S. Lazebnik](https://doi.org/10.1109/CVPR.2018.00810). [PackNet: Adding Multiple Tasks to a Single Network by Iterative Pruning. In 2018 IEEE/CVF Conference on Computer Vision and Pattern Recognition](https://doi.org/10.1109/CVPR.2018.00810), [pp. 7765–7773](https://doi.org/10.1109/CVPR.2018.00810), [June 2018. doi: 10.1109/CVPR.2018.00810](https://doi.org/10.1109/CVPR.2018.00810) 3, 4

[34] [M. McCloskey and N. J. Cohen. Catastrophic Interference in Connectionist Networks: The Sequential Learning Problem. In G. H. Bower, ed., Psychology of Learning and Motivation](https://doi.org/10.1016/S0079-7421%2808%2960536-8), [vol. 24, pp. 109–165. Academic Press, Jan. 1989. doi: 10.1016/S0079-7421(08)60536-8](https://doi.org/10.1016/S0079-7421%2808%2960536-8) 3

[35] [B. Mildenhall, P. P. Srinivasan, M. Tancik, J. T. Barron, R. Ramamoorthi, and R. Ng. NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis, Aug. 2020. doi: 10.48550/arXiv.2003.08934](https://doi.org/10.48550/arXiv.2003.08934) 2

[36] [W. Morgenstern, F. Barthel, A. Hilsmann, and P. Eisert. Compact 3D Scene Representation via Self-Organizing Gaussian Grids](https://doi.org/10.48550/arXiv.2312.13299), [May 2024. doi: 10.48550/arXiv.2312.13299](https://doi.org/10.48550/arXiv.2312.13299) 3

[37] [T. Muller, A. Evans, C. Schied, and A. Keller ¨ . Instant neural graphics primitives with a multiresolution hash encoding. ACM Trans. Graph., 41(4):102:1–102:15, July 2022. doi: 10.1145/3528223.3530127](https://doi.org/10.1145/3528223.3530127) 3

[38] [K. L. Navaneet, K. P. Meibodi, S. A. Koohpayegani, and H. Pirsiavash. Compact3D: Smaller and Faster Gaussian Splatting with Vector Quantization, June 2024. doi: 10.48550/arXiv.2311.18159](https://doi.org/10.48550/arXiv.2311.18159) 3, 6

[39] [S. Niedermayr, C. Neuhauser, K. Petkov, K. Engel, and R. Westermann. Application of 3D Gaussian Splatting for Cinematic Anatomy on Consumer Class Devices](https://doi.org/10.48550/arXiv.2404.11285), [June 2024](https://doi.org/10.48550/arXiv.2404.11285). [doi: 10.48550/arXiv.2404. 11285](https://doi.org/10.48550/arXiv.2404.11285) 3, 8

[40] [R. Po, Z. Dong, A. W. Bergman, and G. Wetzstein](https://doi.org/10.1109/ICCVW60793.2023.00358). [Instant Continual Learning of Neural Radiance Fields. In 2023 IEEE/CVF International Conference on Computer Vision Workshops (ICCVW)](https://doi.org/10.1109/ICCVW60793.2023.00358), [pp. 3326–3336, Oct. 2023. doi: 10.1109/ICCVW60793.2023.00358](https://doi.org/10.1109/ICCVW60793.2023.00358) 3, 8

[41] [B. Preim and P. Saalfeld](https://doi.org/10.1016/j.cag.2018.01.005). [A survey of virtual human anatomy education systems](https://doi.org/10.1016/j.cag.2018.01.005). [Computers & Graphics](https://doi.org/10.1016/j.cag.2018.01.005), [71:132–153, Apr. 2018](https://doi.org/10.1016/j.cag.2018.01.005). [doi: 10.1016/j.cag.2018.01.005](https://doi.org/10.1016/j.cag.2018.01.005) 2

[42] [T. Rolff, K. Li, J. Hertel, S. Schmidt, S. Frintrop, and F. Steinicke. Interactive VRS-NeRF: Lightning fast Neural Radiance Field Rendering for Virtual Reality. In Proceedings of the 2023 ACM Symposium on Spatial User Interaction, SUI ’23, pp. 1–3. Association for Computing Machinery, New York, NY, USA](https://doi.org/10.1145/3607822.3618020), [Oct. 2023. doi: 10.1145/3607822. 3618020](https://doi.org/10.1145/3607822.3618020) 3

[43] [S. P. Rowe, L. C. Chu, A. R. Meyer, M. A. Gorin, and E. K. Fish-](https://doi.org/10.1007/s00261-019-02154-5)

<!-- page 11 of 14 -->

[man. The application of cinematic rendering to CT evaluation of upper tract urothelial tumors: principles and practice](https://doi.org/10.1007/s00261-019-02154-5). [Abdominal Radiology, 44(12):3886–3892, Dec. 2019. doi: 10.1007/s00261-019-02154-5](https://doi.org/10.1007/s00261-019-02154-5) 2

[44] [J. L. Schonberger and J.-M. Frahm ¨ . Structure-from-Motion Revisited. In 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)](https://doi.org/10.1109/CVPR.2016.445), [pp. 4104–4113, June 2016](https://doi.org/10.1109/CVPR.2016.445). [doi: 10.1109/CVPR.2016. 445](https://doi.org/10.1109/CVPR.2016.445) 4

[45] [J. Serra, D. Sur \` ´ıs, M. Miron, and A. Karatzoglou](https://doi.org/10.48550/arXiv.1801.01423). [Overcoming catastrophic forgetting with hard attention to the task](https://doi.org/10.48550/arXiv.1801.01423), [May 2018](https://doi.org/10.48550/arXiv.1801.01423). [doi: 10. 48550/arXiv.1801.01423](https://doi.org/10.48550/arXiv.1801.01423) 3, 4

[46] [J. Taibo and J. A. Iglesias-Guitian](https://doi.org/10.1109/VR58804.2024.00123). [Immersive 3D Medical Visualization in Virtual Reality using Stereoscopic Volumetric Path Tracing](https://doi.org/10.1109/VR58804.2024.00123). [In 2024 IEEE Conference Virtual Reality and 3D User Interfaces (VR), pp. 1044–1053, Mar. 2024. doi: 10.1109/VR58804.2024.00123](https://doi.org/10.1109/VR58804.2024.00123) 2

[47] [P.-P. Vazquez, E. Moncl ´ us, and I. Navazo ´ . Representative Views and Paths for Volume Models. In A. Butz, B. Fisher, A. Kruger, P. Olivier, ¨ and M. Christie, eds., Smart Graphics, pp. 106–117. Springer, Berlin, Heidelberg, 2008](https://doi.org/10.1007/978-3-540-85412-8_10). [doi: 10.1007/978-3-540-85412-8 10](https://doi.org/10.1007/978-3-540-85412-8_10) 8

[48] [C. L. Walsh, P. Tafforeau, W. L. Wagner, D. J. Jafree, A. Bellier, C. Werlein, M. P. Kuhnel, E. Boller, S. Walker-Samuel, J. L. Robertus, ¨ D. A. Long, J. Jacob, S. Marussi, E. Brown, N. Holroyd, D. D. Jonigk, M. Ackermann, and P. D. Lee. Imaging intact human organs with local resolution of cellular structures using hierarchical phase-contrast tomography. Nature Methods](https://doi.org/10.1038/s41592-021-01317-x), [18(12):1532–1541, Dec. 2021. doi: 10.1038/s41592-021-01317-x](https://doi.org/10.1038/s41592-021-01317-x) 2

[49] [Z. Wang, A. Bovik, H. Sheikh, and E. Simoncelli](https://doi.org/10.1109/TIP.2003.819861). [Image quality assessment: from error visibility to structural similarity. IEEE Transactions on Image Processing](https://doi.org/10.1109/TIP.2003.819861), [13(4):600–612](https://doi.org/10.1109/TIP.2003.819861), [Apr. 2004. doi: 10.1109/ TIP.2003.819861](https://doi.org/10.1109/TIP.2003.819861) 6

[50] [J. Wasserthal, H.-C. Breit, M. T. Meyer, M. Pradella, D. Hinck, A. W. Sauter, T. Heye, D. T. Boll, J. Cyriac, S. Yang, M. Bach, and M. Segeroth](https://doi.org/10.1148/ryai.230024). [TotalSegmentator: Robust Segmentation of 104 Anatomic Structures in CT Images. Radiology: Artificial Intelligence, 5(5):e230024, Sept. 2023. doi: 10.1148/ryai.230024](https://doi.org/10.1148/ryai.230024) 6

[51] [G. Wheeler, S. Deng, N. Toussaint, K. Pushparajah, J. A. Schnabel, J. M. Simpson, and A. Gomez](https://doi.org/10.1049/htl.2018.5064). [Virtual interaction and visualisation of 3D medical imaging data with VTK and Unity. Healthcare Technology Letters](https://doi.org/10.1049/htl.2018.5064), [5(5):148–153](https://doi.org/10.1049/htl.2018.5064), [Oct. 2018. doi: 10.1049/htl.2018.5064](https://doi.org/10.1049/htl.2018.5064) 2

[52] [W. Xie, J. Yao, X. Cao, Q. Lin, Z. Tang, X. Dong, and X. Guo](https://arxiv.org/abs/2407.05023). [Surgicalgaussian: Deformable 3d gaussians for high-fidelity surgical scene reconstruction](https://arxiv.org/abs/2407.05023), [2024.](https://arxiv.org/abs/2407.05023) 3

[53] [L. Yang, B. Kang, Z. Huang, X. Xu, J. Feng, and H. Zhao](https://doi.org/10.1109/CVPR52733.2024.00987). [Depth Anything: Unleashing the Power of Large-Scale Unlabeled Data](https://doi.org/10.1109/CVPR52733.2024.00987). [In 2024 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)](https://doi.org/10.1109/CVPR52733.2024.00987), [pp. 10371–10381, June 2024. ISSN: 2575-7075](https://doi.org/10.1109/CVPR52733.2024.00987). [doi: 10.1109/CVPR52733.2024.00987](https://doi.org/10.1109/CVPR52733.2024.00987) 3

[54] [Z. Yu, A. Chen, B. Huang, T. Sattler, and A. Geiger](https://doi.org/10.48550/arXiv.2311.16493). [Mip-Splatting: Alias-free 3D Gaussian Splatting, Nov. 2023](https://doi.org/10.48550/arXiv.2311.16493). [doi: 10.48550/arXiv. 2311.16493](https://doi.org/10.48550/arXiv.2311.16493) 3, 7

[55] [Q. Zhang, R. Eagleson, and T. M. Peters](https://doi.org/10.1007/s10278-010-9321-6). [Volume Visualization: A Technical Overview with a Focus on Medical Applications. Journal of Digital Imaging](https://doi.org/10.1007/s10278-010-9321-6), [24(4):640–664, Aug. 2011](https://doi.org/10.1007/s10278-010-9321-6). [doi: 10.1007/s10278 -010-9321-6](https://doi.org/10.1007/s10278-010-9321-6) 2

[56] [R. Zhang, P. Isola, A. A. Efros, E. Shechtman, and O. Wang. The Unreasonable Effectiveness of Deep Features as a Perceptual Metric. In 2018 IEEE/CVF Conference on Computer Vision and Pattern Recognition](https://doi.org/10.1109/CVPR.2018.00068), [pp. 586–595, June 2018. ISSN: 2575-7075. doi: 10. 1109/CVPR.2018.00068](https://doi.org/10.1109/CVPR.2018.00068) 6

[57] [H. Zhao, X. Zhao, L. Zhu, W. Zheng, and Y. Xu](https://arxiv.org/abs/2405.17872). [Hfgs: 4d gaussian splatting with emphasis on spatial and temporal high-frequency components for endoscopic scene reconstruction](https://arxiv.org/abs/2405.17872), [2024](https://arxiv.org/abs/2405.17872). 3

[58] [L. Zhou, M. Fan, C. Hansen, C. R. Johnson, and D. Weiskopf](https://doi.org/10.34133/2022/9840519). [A Review of Three-Dimensional Medical Image Visualization](https://doi.org/10.34133/2022/9840519). [Health Data Science](https://doi.org/10.34133/2022/9840519), [2022:9840519, Apr. 2022](https://doi.org/10.34133/2022/9840519). [Publisher: American Association for the Advancement of Science](https://doi.org/10.34133/2022/9840519). [doi: 10.34133/2022/9840519](https://doi.org/10.34133/2022/9840519) 1

[59] [M. L. Zuley, R. Jarosz, S. Kirk, Y. Lee, R. Colen, K. Garcia, D. Delbeke, M. Pham, P. Nagy, G. Sevinc, M. Goldsmith, S. Khan, J. M. Net, F. R. Lucchesi, and N. D. Aredes. The cancer genome atlas head-](https://doi.org/10.7937/K9/TCIA.2016.LXKQ47MS)

[neck squamous cell carcinoma collection (tcga-hnsc), 2016](https://doi.org/10.7937/K9/TCIA.2016.LXKQ47MS). [doi: 10. 7937/K9/TCIA.2016.LXKQ47MS](https://doi.org/10.7937/K9/TCIA.2016.LXKQ47MS) 6

[60] [M. Zwicker, H. Pfister, J. van Baar, and M. Gross. EWA volume splatting. In Proceedings Visualization, 2001. VIS ’01., pp. 29–538, Oct. 2001. doi: 10.1109/VISUAL.2001.964490](https://doi.org/10.1109/VISUAL.2001.964490) 3

<!-- page 12 of 14 -->

## S7 SUPPLEMENTARY

Supplemental materials, generated training data, and trained models are available at [https://osf.io/tuwh5/](https://osf.io/tuwh5/). Code is available at [https://github.com/roth-hex-lab/Multi-Layer-Anatomy-GS-Unity-Rendering](https://github.com/roth-hex-lab/Multi-Layer-Anatomy-GS-Unity-Rendering). The original CT volumes used in this work are available from their respective authors.

Data generation To ensure noise-free images in our ground truth data, the path tracer uses 4096 samples per pixel and allows up to 100 light bounces. Rendering begins with full-object views and progresses to close-up shots of different anatomical parts from various angles, ensuring a comprehensive representation of the anatomical structures. All images, both anatomical and synthetic, include transparent backgrounds. Note that in the bone scenes, some blood vessels are visible due to their density being similar to that of bony soft tissue.

Layering Layered reconstruction generally works well, even at default GS settings; see metrics in Table S7. Lower layers often reconstruct slightly worse than upper layers. This is possibly due to general increases in visual complexity in upper layers, as well as fixed Gaussians from lower layers that would not usually be in upper layers. This is best avoided in input data generation but can sometimes be cumbersome.

Compression We evaluate the compression performance of our approach against the commonly used DICOM and compressed Nifti file formats, see Table S6. Note that while the internal data structure used by the path tracer is more compact than the on-file representation, it is generally less portable and not typically stored.

Renderings We include additional overview renderings as they would be seen from within the game engine for all anatomy scenes (Figure S9), synthetic scenes (Figure S10), and selective layer cutting (Figure S8).

<!-- page 13 of 14 -->

![Image block](images/kleinbeck2024_multilayer-gs-anatomy_p13_b1.png)

Figure S8: Exemplary scene with layers cut in leg and fullbody scenes, as seen from within the game engine.

Table S6: Comparison of on-disk sizes between different medical volumes before and after training and compression.

<table><tbody><tr><td rowspan="2"></td><td colspan="2">Leg</td><td colspan="2">Lower Body</td><td colspan="2">Fullbody</td></tr><tr><td>Normal</td><td>HQ Recon.</td><td>Normal</td><td>HQ Recon.</td><td>Normal</td><td>HQ Recon.</td></tr><tr><td>Original Volume (DICOM)</td><td>304.7</td><td>304.7</td><td>1585.1</td><td>1585.1</td><td>87.4</td><td>87.4</td></tr><tr><td>Compressed (.nii.gz)</td><td>73.5</td><td>73.5</td><td>730.8</td><td>730.8</td><td>75.5</td><td>75.5</td></tr><tr><td>Reconstructed PLY file</td><td>32.4</td><td>62.2</td><td>22.2</td><td>45.3</td><td>47.6</td><td>92.2</td></tr><tr><td>Unity Comp. (High Quality)</td><td>12.0</td><td>22.9</td><td>8.3</td><td>16.7</td><td>17.6</td><td>33.9</td></tr><tr><td>Unity Comp. (Low Filesize)</td><td>5.6</td><td>9.2</td><td>4.4</td><td>7.1</td><td>7.4</td><td>12.8</td></tr><tr><td>Original compressed up to</td><td>98.16%</td><td>96.98%</td><td>99.72%</td><td>99.55%</td><td>91.53%</td><td>85.35%</td></tr></tbody></table>

Table S7: Comparison of reconstruction quality at default GS settings before import to Unity and compression.

<table><tr><td rowspan="2">Layer</td><td colspan="3">Leg</td><td colspan="3">Lower Body</td><td colspan="3">Fullbody</td></tr><tr><td>1</td><td>2</td><td>3</td><td>1</td><td>2</td><td>3</td><td>1</td><td>2</td><td>3</td></tr><tr><td>PSNR ↑</td><td>38.575</td><td>35.851</td><td>30.367</td><td>38.165</td><td>37.267</td><td>31.028</td><td>36.187</td><td>37.370</td><td>33.559</td></tr><tr><td>SSIM ↑</td><td>0.990</td><td>0.971</td><td>0.957</td><td>0.991</td><td>0.968</td><td>0.940</td><td>0.986</td><td>0.972</td><td>0.970</td></tr><tr><td>LPIPS ↓</td><td>0.023</td><td>0.042</td><td>0.064</td><td>0.022</td><td>0.051</td><td>0.082</td><td>0.024</td><td>0.056</td><td>0.045</td></tr></table>

<!-- page 14 of 14 -->

![Image block](images/kleinbeck2024_multilayer-gs-anatomy_p14_b1.png)

Figure S9: Overview of all CT data scenes used in our anatomy dataset, as seen from within the game engine.

![Image block](images/kleinbeck2024_multilayer-gs-anatomy_p14_b3.png)

Figure S10: Overview of all scenes used in our synthetic dataset, as seen from within the game engine. Some objects can show visual artifacts from previously unseen viewing angles due to the limited variety in camera orientations towards the object in our synthetic datasets.