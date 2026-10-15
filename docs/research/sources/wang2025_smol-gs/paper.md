<!-- page 1 of 23 -->

arXiv:2512.00850v3 [cs.CV] 18 Jun 2026

# Smol-GS: Compact Representations for Abstract 3D Gaussian Splatting

**Haishan Wang Mohammad Hassan Vali Arno Solin** ELLIS Institute Finland and Aalto University, Espoo, Finland {haishan.wang, mohammad.vali, arno.solin}@aalto.fi

## Abstract

We present Smol-GS, a novel method for learning compact representations for 3D Gaussian Splatting (3DGS). Our approach learns highly efficient splat-wise features to model 3D space, which capture abstracted cues, including color, opacity, transformation, and material properties. We propose octree-derived positional encoding, which explicitly models spatial locality and enhances representation efficiency. We further apply entropy-based compression to exploit feature redundancy and compress splat coordinates using a recursive voxel hierarchy. This design enables orders-of-magnitude reductions in storage while preserving representation flexibility. Smol-GS achieves state-of-the-art compression performance on standard benchmarks with high-level rendering quality.

Project page: [https://aaltoml.github.io/Smol-GS](https://aaltoml.github.io/Smol-GS)

![Image block](images/wang2025_smol-gs_p1_b7.png)

Figure 1: Smol-GS learns a compact representation of the 3D scene that (i) stores coordinates in an efficient octree structure, (ii) learns local positional encodings, and (iii) abstracts away viewdependent splat features such as color, shape, and material cues. On MIP-NERF 360, this gives state-of-the-art results in size/PSNR: 4.87 MB/27.61 dB.

## 1 Introduction

3D Gaussian Splatting (3DGS, [1]) is a paradigm for novel view synthesis that models a scene as a set of rasterized Gaussian splats. It achieves real-time speed and high rendering quality through rasterization techniques [2]. However, 3DGS suffers from memory inefficiency; it often requires several gigabytes of storage with millions of splats to represent complex scenes. This issue of large memory footprint has been tackled extensively in recent works [3–20]. These methods improve compactness to varying degrees, yet the coordinate data and high-dimensional appearance cues remain hard to store efficiently at scale.

Two main directions dominate current 3DGS compression research: (i) Signal-processing approaches quantize splat attributes and deliver considerable storage savings [6–9, 11, 19]; (ii) Learning-based approaches compress by sharing structure across splats, with anchor-offset hierarchies from Scaffold-GS [21] forming the backbone of the most competitive results [3–5, 12]. However, signal-processing

Preprint.

<!-- page 2 of 23 -->

![Image block](images/wang2025_smol-gs_p2_b1.png)

Figure 2: Qualitative results on the MIP-NERF 360 data set. Smol-GS provides high-fidelity reconstructions competitive with vanilla 3DGS-30K. Smol-GS preserves sharp shadow edges and material effects (specular highlights, glass, flat walls) while using an orders-of-magnitude smaller model. We include quantitative summary results in Table 2.

pipelines do not fully exploit local spatial correlations and repeated patterns among splats, and anchoroffset designs can introduce transparent or invisible offsets and extra heuristics. These approaches often sidestep coordinate compression because reconstruction is sensitive to spatial errors. We revisit this premise in our work (see Fig. 1) that hinges on the realization that keeping the spatial structure explicit (but efficiently packed) and abstracting the splat-wise visual features away can result in highly efficient compression.

In this paper, we propose Smol-GS by disentangling geometry from appearance and introducing positional encodings to splats. Our method learns a compact representation with splat-wise abstract features and locality-aware embeddings. Inspired by prior works [3, 21, 22], in Smol-GS coordinates are stored with an occupancy-octree encoding and entropy coding; features (color, opacity, transformation, and material cues) and scaling controllers are quantized and entropy-coded with distributions predicted from hashed spatial descriptors. Our design avoids anchor-offset complications, which introduce storage redundancy and rendering latency. Qualitative (Fig. 2) and quantitative (Fig. 6 and Table 2) results and inference speed comparison (Table 3) show that Smol-GS achieves higher reconstruction quality and rendering speed while pushing model size down to the smallest among strong baselines.

**Contributions** Our contributions can be summarized as:

• We introduce Smol-GS, a 3DGS compression model that learns an explicit and highly efficient representation. Our design avoids the structural overhead of anchor-based methods, exploits the representational redundancy to compress scenes further, and accelerates rendering.

• We propose a novel positional encoding $f _ { o c t }$ using an octree hierarchy. These locality-aware features enhance reconstruction quality.

• Experiments on standard benchmarks show that Smol-GS substantially reduces the storage requirements for 3DGS while maintaining high reconstruction fidelity and rendering speed, competitive with state-of-the-art approaches, making Smol-GS well-suited for real-time applications.

## 2 Related work

**3D Gaussian splatting** The 3DGS paradigm represents a scene as a collection of Gaussian splats initialized via structure-from-motion (SfM, [23]), based on computer graphics research [24, 25]. Each splat is associated with a location, covariance (via scale and rotation), opacity, color, and view-dependent material properties (spherical harmonics, SH). The explicit primitive and Gaussian rasterization allow real-time rendering, while the continuous representation yields high-quality reconstructed images. These advantages make 3DGS a promising framework for broad applications, such as SLAM [26–29], 3D editing [30–33], and VR [34–37].

**Compaction vs. attribute compression** Efforts to address the challenging memory footprint of storing the splat-wise parameters has mainly focused on two lines of research. Compaction reduces the number of splats via pruning and regularization, often guided by opacity, scale, importance

2

<!-- page 3 of 23 -->

![Image block](images/wang2025_smol-gs_p3_b1.png)

Figure 3: Method overview of Smol-GS: We train (trainable parameters in blue) neural splats with tiny MLP-decoders for view-dependent rendering (Sec. 3.3). The coordinates are compressed with occupancy-octree coordinate coding (Sec. 3.1). We also learn the quantization of splat features f and scaling controllers s with NLL rate terms (Sec. 3.4), and employ adaptive density control with stage-wise training (loss-terms in red) to balance fidelity and size (Secs. 3.5 and 3.6).

estimation [13–17]. This can save memory but risks losing thin structures and requires heuristics. Attribute compression keeps the splat set but encodes attributes more efficiently, balancing rate and fidelity. For example, vector-quantization [38–40] based methods utilize clustering algorithms [41, 42] to compress per-splat attributes (e.g., color/SH, opacity, scale/rotation) using codebooks [6–9, 11]. However, traditional tools cannot eliminate the information redundancy hidden in continuity and correlation in 3D space.

**Learned compact representations** Anchor-offset hierarchies introduced by Scaffold-GS [21] condense local neighborhoods into shared anchor embeddings and reconstruct splat features with small MLPs. Follow-ups add stronger coding: HAC++ [4] and HEMGS [5] use entropy models, and ContextGS [12] leverages autoregressive anchors to reduce storage further. These methods are effective because they share structure across splats and model statistics. However, the anchors always introduce a certain ratio of transparent offsets, and the recovery of splat coordinates requires the composition of three factors: anchor location, relative coordinates, and scaling control. These design drawbacks, stemming from heuristic complications, limit the compression ratio and flexibility for downstream applications. Additionally, the methods typically avoid coordinate compression due to quality sensitivity, which limits the efficiency of compression.

**Coordinate compression and geometry coding** Point-cloud geometry compression shows that hierarchical occupancy enables compact, often lossless storage of 3D locations via octrees [22, 43–45]. This perspective suggests that 3DGS coordinates—despite their importance for fidelity—can also be stored efficiently using an occupancy-octree with entropy coding [46], leaving appearance and view-dependent effects to be learned by low-dimensional features.

Smol-GS is different from previous anchor-offset designs by (i) adopting an individual neural splat formulation that eliminates anchor-offset bookkeeping; (ii) encoding splat coordinates with an occupancy-octree combined with entropy coding; and (iii) introducing an octree-derived positional encoding to enhance splat representation efficiency. Smol-GS aims to enhance the data exploitation capability of learning-based methods.

## 3 Methods

Smol-GS consists of five parts that work together (see Fig. 3 for an overview): (i) Coordinate compression (Sec. 3.1): Splat coordinates are stored with an occupancy-octree and entropy coding, leveraging spatial sparsity while avoiding anchor-offset overhead. (ii) Positional encoding (Sec. 3.2): Each splat inherits a unique identifier derived from the corresponding finest-level octree cell. This octree-derived positional encoding improves representation compactness and structural consistency. (iii) Tiny decoders (Sec. 3.3): Small MLPs reconstruct view-dependent color and transformation from abstract features, viewing direction, and positional embeddings, keeping rendering fast. (iv) Feature compression (Sec. 3.4): Per-splat features are quantized using learned step sizes and encoded arithmetically. (v) Adaptive density control and training (Secs. 3.5 and 3.6): Gradient-based densification and pruning, together with stage-wise optimization, balance reconstruction fidelity and model size.

3

<!-- page 4 of 23 -->

## 3.1 Coordinate compression: Occupancy-octree encoding

Many 3DGS compression methods skip coordinate quantization due to the sensitivity of reconstruction to geometry. In Fig. A9, we show that this precision requirement could be relaxed: 16-bit per-axis quantization yields an imperceptible quality drop. Therefore, we use an octree structure to capture the occupancy of splats in 3D space such that the tree is built recursively (see Fig. 4), drawing intuition from [22, 43–45].

We begin from the axis-aligned bounding box covering all splats and, at recursion $r = 1$ , subdivide it into 8 equal sub-boxes. At each subsequent recursion, only non-empty boxes (those containing at least one splat) are subdivided again into 8 equal children. The boundary of the coarsest-level box is defined by the minimum and maximum of all splat coordinates: $x _ { \mathrm { m i n } }$ and $x _ { \mathrm { m a x } }$ . A box at depth $r \in \mathbb { N }$ has size $b _ { r } = ( \pmb { x } _ { \mathrm { m a x } } - \pmb { x } _ { \mathrm { m i n } } ) / 2 ^ { r }$ . Each subdivision emits an 8-bit occupancy byte indicating which children are non-empty (1) or empty (0), with child order given by the Morton space-filling curve [47]. After R recursions, the resulting occupancy-octree explicitly represents the spatial layout of all splats such that the center of each finest-level box at depth R provides the quantized coordinate, with at most one splat in each finest-level box. Excessive splats that fall into the same finest-level cell are pruned. This correspondence quantizes the coordinate of the splat x to be

$$
\hat {\boldsymbol {x}} = b _ {R} \cdot \operatorname{floor} ((\boldsymbol {x} - \boldsymbol {x} _ {\min}) / b _ {R}) + 0. 5 b _ {R} + \boldsymbol {x} _ {\min}.\tag{1}
$$

**Coordinate storage** then reduces to recording the sequence of occupancy bytes for all non-empty internal tree nodes, plus the boundaries of the coarsest bounding box and recursion depth R. Because these bytes are highly sparse (most nodes have few occupied children, see Sec. B.4), we apply Huffman coding [46] for an entropy-based compression, yielding compact lossless-within-grid storage of coordinates relative to the chosen quantization grid.

## 3.2 Positional encoding: Index from space division

During the spatial partitioning described in Sec. 3.1, each splat is assigned to a unique finest-level bounding box. At each recursion, every box is subdivided into eight sub-boxes. Therefore, there are at most $\widetilde { 8 } ^ { R }$ possible finest-level boxes available for assignment. Each finest-level box can then be encoded by a 3R-bit sequence, which serves as the **positional embedding** $\pmb { f } _ { o c t } \in \{ 0 , 1 \} ^ { 3 R }$ of the splat contained within that box. Mathematically, $f _ { o c t }$ represents the binary data of the Morton code (Z-order index) [47] of the associated finest-level box.

Suppose a splat is located in box B at recursion depth $r - 1$ . Then, the $( 3 r - 2 ) ^ { \mathrm { t h } }$ through $3 r ^ { \mathrm { t h } }$ elements of $f _ { o c t }$ indicate which sub-box at recursion depth r, contained within $B ,$ includes the splat. For example, when there is only one recursion level, $\pmb { f } _ { o c t } = ( 1 , 0 , 0 )$ indicates that the splat is located at the $4 ^ { \mathrm { t h } }$ sub-box of the entire space, since $^ \circ 1 0 0 ^ { \circ }$ is the binary representation of $^ { \circ } 4 ^ { \prime }$

## 3.3 Neural Gaussian splats

Smol-GS models the 3D scene as a set of neural Gaussian splats with the support of a few MLPs $( \mathrm { M L P } _ { o } , \mathrm { M L P } _ { c } , \mathrm { M L P } _ { s } , \mathrm { M L P } _ { r } ,$ and $\mathrm { M L P } _ { o c t } )$ . Each splat has a coordinate x $\widehat { \in \mathbb { R } ^ { 3 } }$ , a feature vector $\pmb { f } \in \mathbb { R } ^ { n _ { f } }$ (we use $n _ { f } = 8$ in practice, see Sec. 4.1), and a scaling controller $s \in \mathbb { R } ^ { 3 }$ . The feature f encodes abstract, splat-wise cues including optical information, geometric transformation, and orientation-induced material properties.

**Feature generation** Given the camera center $x _ { c }$ during rendering, the augmented feature $f ^ { * }$ is constructed by concatenating the splat feature $f$ with viewing information and positional encoding,

$$
\boldsymbol {f} ^ {*} = \operatorname{concat} \left(\boldsymbol {f}, \frac {\boldsymbol {x} _ {c} - \boldsymbol {x}}{\| \boldsymbol {x} _ {c} - \boldsymbol {x} \|}, \| \boldsymbol {x} _ {c} - \boldsymbol {x} \|, \mathrm{MLP} _ {o c t} (\boldsymbol {f} _ {o c t})\right),\tag{2}
$$

where $\scriptstyle { \frac { { \pmb x } _ { c } - { \pmb x } } { \| { \pmb x } _ { c } - { \pmb x } \| } }$ defines viewing direction, $\| \pmb { x } _ { c } - \pmb { x } \|$ is the camera-to-splat distance and $f _ { o c t }$ is the positional embedding defined in Sec. 3.2. The per-splat optical attributes are then predicted as

$$
\left. o = \left| \mathrm{MLP} _ {o} \left(\boldsymbol {f} ^ {*}\right) \right|, \quad (\text {opacity}) \quad \boldsymbol {c} = \mathrm{MLP} _ {c} \left(\boldsymbol {f} ^ {*}\right), \quad \text {(color)} \right\}\tag{3}
$$

$$
\boldsymbol {r} = \operatorname{MLP} _ {r} \left(\boldsymbol {f} ^ {*}\right), \quad (\text {rotation}) \quad \boldsymbol {s} ^ {*} = \boldsymbol {s} \odot \operatorname{sigmoid} \left(\operatorname{MLP} _ {s} \left(\boldsymbol {f} ^ {*}\right)\right), \quad (\text {scaling})
$$

where $o   \in   \mathbb { R } ,   c   \in   \mathbb { R } ^ { 3 } , r   \in   \mathbb { R } ^ { 4 }$ , and $\pmb { s } ^ { * }   \in   \mathbb { R } ^ { 3 }$ denote the predicted opacity, color, rotation, and scaling, respectively, and $\odot$ denotes element-wise multiplication. Generating scaling parameters $s ^ { * }$

4

<!-- page 5 of 23 -->

![Image block](images/wang2025_smol-gs_p5_b1.png)

Figure 4: Occupancy-octree coordinate coding: Given a point cloud (left), we recursively divide the bounding box into eight sub-boxes. Only the non-empty sub-boxes (gray) are further divided (middle). Each division is represented by an 8-bit binary code (1=non-empty, 0=empty). $C _ { r i }$ denotes the code of the $i ^ { \mathrm { t h } }$ division at $r ^ { \mathrm { t h } }$ recursion. The occupancy octree (right) is encoded by arranging all bits in a breadth-first manner. Finally, we apply Huffman coding to further compress the octree bits.

by relying solely on the MLP would cause instability and training collapses. To mitigate this issue, the parameter s is introduced as a splat size bound, and the MLP<sub>s</sub> predicts a modulation factor via a sigmoid activation. The scaling matrix S and rotation matrix R defined by $s ^ { * }$ and r reconstruct the covariance Σ of the splat:

$$
\boldsymbol {\Sigma} = \boldsymbol {R} \boldsymbol {S} \boldsymbol {S} ^ {\top} \boldsymbol {R} ^ {\top}.\tag{4}
$$

**Rasterization** The pixel-wise rasterization follows the α-blending in the original 3DGS [1]. For each pixel $\pmb { x } ^ { \prime } \in \mathbb { R } ^ { 2 }$ in the 2D plane, the color $C ( { \pmb x } ^ { \prime } )$ is obtained by projecting all neural splats onto the image plane and compositing them along the ray by blending:

$$
C (\boldsymbol {x} ^ {\prime}) = \sum_ {i = 1} ^ {N _ {\mathrm{ray}}} T _ {i} o _ {i} G _ {i} (\boldsymbol {x} ^ {\prime}) \boldsymbol {c} _ {i}, \quad T _ {i} = \prod_ {j = 1} ^ {i - 1} (1 - o _ {j} G _ {j} ^ {\prime} (\boldsymbol {x} ^ {\prime})),\tag{5}
$$

where $N _ { \mathrm { r a y } }$ is the number of splats along the ray where they are ordered by the distance to the camera center, $o _ { i }$ and $c _ { i }$ are the predicted splat opacity and color, respectively. $\dot { G } ( \pmb { x } ^ { \prime } )$ denotes the projected Gaussian weight:

$$
G (\boldsymbol {x} ^ {\prime}) = \exp \big (- \frac {1}{2} (\boldsymbol {x} ^ {\prime} - \boldsymbol {\mu} ^ {\prime}) ^ {\top} \boldsymbol {\Sigma} ^ {\prime - 1} (\boldsymbol {x} ^ {\prime} - \boldsymbol {\mu} ^ {\prime}) \big).\tag{6}
$$

Here, $\mu ^ { \prime }$ and $\mathbf { \Sigma } ^ { \prime } = J W \mathbf { \Sigma } W ^ { \top } J ^ { \top }$ are the splat coordinate and covariance after projection onto the 2D plane [48, 49], where J denotes the Jacobian of projective transformation and W is the view matrix. Overall, the parametrization in Smol-GS keeps the geometry explicit, view effects compact, and shares learned spatial information via the positional embeddings.

## 3.4 Splat-wise feature compression: Arithmetic coding

Each splat carries the scaling controller s $\in \mathbb { R } ^ { 3 }$ and an abstract feature $\pmb { f } \in \mathbb { R } ^ { n _ { f } }$ encoding color, opacity, transformation, and material cues (see Sec. 3.3). We compress them by hash-grid assisted arithmetic coding and a Gaussian distribution prior [3]. Smol-GS uses low-dimensional features $n _ { f }   =   8$ (more details in Sec. B.1), much smaller than the 50 dimensions in most anchor-based methods [4, 21].

First, we condition feature coding on spatial hash descriptors by predicting a distribution and a per-dimension step size with a tiny network ${ \mathrm { M L P } } _ { h } { \mathrm { : ~ } } { \boldsymbol { \mu } } _ { f } ^ { \mathrm { ~ \bf \hat { ~ } } } , { \boldsymbol { \Sigma } } _ { f } , { \boldsymbol { \Delta } } _ { f } ^ { \mathrm { ~ \bf \hat { ~ } } } { \mathrm { ~ = ~ } } { \mathrm { M L P } } _ { h } ( { \mathrm { H a s h } } ( { \boldsymbol { x } } ) )$ , where Hash(·) denotes the hash encoding function of InstantNGP [50]. For better compression, the parameters of Hash(·) are quantized as binary. We then quantize the feature $f$ with the learned steps, $\hat { \pmb { f } } = \Delta _ { f } \odot \mathrm { r o u n d } ( \pmb { f } / \Delta _ { f } )$ , and assume the quantized features follow a Gaussian distribution of $\mathcal { \tilde { N } } ( \mathbf { \dot { \boldsymbol { f } } } ; \mathbf { \mu } _ { f } , \mathbf { \dot { \Sigma } } _ { f } )$ (with diagonal $\Sigma _ { f } )$ . The negative log-likelihood (NLL) of the quantization bin provides a rate proxy:

$$
\mathrm{NLL} (\boldsymbol {f}) = - \log \int_ {\hat {\boldsymbol {f}} - \Delta_ {f}} ^ {\hat {\boldsymbol {f}} + \Delta_ {f}} \mathcal {N} (\boldsymbol {f} ^ {\prime}; \boldsymbol {\mu} _ {\boldsymbol {f}}, \boldsymbol {\Sigma} _ {\boldsymbol {f}})   \mathrm{d} \boldsymbol {f} ^ {\prime}.\tag{7}
$$

The NLL is the theoretical lower bound for the number of bits needed to encode the features. The average NLL over all N splats serves as the training loss to encourage reducing the storage for

5

<!-- page 6 of 23 -->

![Chart block](images/wang2025_smol-gs_p6_b1.png)

Figure 5: Training curves over different stages: We log the number of splats (left axis), PSNR (middle), and compressed model size (right) over different stages of training, showing how the compaction and compression do not degrade the overall quality. The number of splats increases steadily during densification (0.5k–15k), then decreases rapidly during compaction (15k–20k).

encoding the features: $\begin{array} { r } { \mathcal { L } _ { \mathrm { N L L } } ( \pmb { f } ) = \frac { 1 } { N } \sum _ { i = 1 } ^ { N } \mathrm { N L L } ( \pmb { f } _ { i } ) } \end{array}$ . We use arithmetic coding [51] to compress both features $f$ and the scaling controller s of the splats. The loss function $\mathcal { L } _ { \mathrm { N L L } } ( s )$ and quantization ŝ of the scaling controller s are defined similarly to the above.

## 3.5 Adaptive density control

Smol-GS employs an adaptive density control (ADC) strategy to maintain high-fidelity while keeping a sparse distribution of splats. **Initialization:** Following 3DGS [1], we initialize coordinates x and scaling controllers s from SfM point clouds [23]. Because SfM points are sparse and non-uniformly scattered, some regions require densification. The features f are initialized randomly. **Densification:** Splats with a high magnitude of the coordinate gradient are densified during training [21]. We choose threshold $\tau _ { g }$ such that the splat whose coordinate’s gradient magnitude is higher than $\tau _ { g }$ will be cloned as a new splat. The newly introduced splat inherits the feature $f$ from the parent splat, while its coordinate is randomly sampled from a Gaussian $\mathcal { N } ( \pmb { x } , \pmb { \Sigma } )$ , where x and Σ are the coordinate and covariance of the parent splat, respectively. This process defines new splats and adds detail to under-represented regions of the scene, improving reconstruction quality while increasing overall density. **Pruning:** During training, an individual splat is pruned when either its average opacity is less than the threshold $\tau _ { o } ,$ or if it remains consistently invisible. **Opacity regularization:** To encourage sparsity in the splat distribution, we apply an $L _ { 1 }$ regularization loss on the opacity of all N splats during specific stages of training (see Sec. 3.6): $\begin{array} { r } { \mathcal { L } _ { o } = \sum _ { i = 1 } ^ { N } \left| \operatorname { M L P } _ { o } ( \pmb { f } _ { i } ^ { * } ) \right| } \end{array}$

## 3.6 Training pipeline for Smol-GS

We provide a consistent training pipeline, where Smol-GS is trained with the following five stages: (1) Warm-up stage (0–0.5k): The splat coordinates x and scaling controllers s are initialized from SfM, and abstract features f are randomly initialized. (2) Densification stage (0.5k–15k): The number of splats is controlled mutually by densification and pruning as described in Sec. 3.5. (3) Compaction stage (15k–20k): Both opacity regularization and pruning modules further reduce the number of splats. (4) Feature compression stage (20k–30k): Both features f and scaling controllers s of the splats are quantized and compressed via arithmetic coding. (5) Coordinate compression stage (30k–35k): All splat coordinates are quantized and stored by the occupancy-octree technique. In Fig. 5, we provide training curves for an example scene (Garden), which gives an idea of the influence of the different stages. Note that the proposed training schedule is not tuned on a per-scene or per-dataset basis.

**Optimization objective** We optimize a photometric objective combining the $L _ { 1 }$ loss $\mathcal { L } _ { 1 }$ and SSIM loss $\mathcal { L } _ { \mathrm { s } }$ between the rendered image and the ground truth, the opacity regularization loss ${ \mathcal { L } } _ { o } ,$ , and the quantization regularization losses of $\mathcal { L } _ { \mathrm { N L L } } ( \tilde { \pmb { f } ) } + \mathcal { L } _ { \mathrm { N L L } } ( \pmb { s } )$ such that

$$
\mathcal {L} = (1 - \lambda_ {\mathrm{s}}) \mathcal {L} _ {1} + \lambda_ {\mathrm{s}} \mathcal {L} _ {\mathrm{s}} + \lambda_ {o} \mathcal {L} _ {o} + \lambda_ {q} \left[ \mathcal {L} _ {\mathrm{NLL}} (\boldsymbol {f}) + \mathcal {L} _ {\mathrm{NLL}} (\boldsymbol {s}) \right].\tag{8}
$$

Here $\lambda _ { \mathrm { s } } , \lambda _ { o } ,$ and $\lambda _ { q }$ are hyperparameters to control the optimization priorities of the SSIM loss, opacity regularization, and quantization regularization. The opacity regularization is only effective $( i . e . ,   \lambda _ { o }   >   0 )$ in the compaction stage $( 3 )$ , and the quantization regularization is only active $( i . e .$ $\lambda _ { q } > 0 )$ during the compression stages of (4) and (5).

6

<!-- page 7 of 23 -->

## 4 Experiments

We evaluate Smol-GS as a full 3DGS compression pipeline. Concretely, we demonstrate our rendering quality vs. model size both quantitatively and qualitatively under the well-known 3DGS.zip survey benchmark setup [52]. Additionally, we demonstrate storage size per module, analyze the inference speed, and ablate central parts of our model.

**Data sets** We benchmark our Smol-GS on standard permissively-licensed real-world 3D reconstruction data sets: nine scenes from MIP-NERF 360 [53], two scenes from TANKS AND TEMPLES [54], and two scenes from DEEP BLENDING [55]. The training–testing split follows the original settings of 3DGS [1] and Mip-NeRF 360 [53]: Every $\mathrm { \bar { 8 } ^ { t h } }$ image is used for testing, and the rest are for training.

**Evaluation metrics** The reconstruction quality is evaluated by three widely used metrics: the Peak Signal-to-Noise Ratio (PSNR), the Structural Similarity Index Measure (SSIM), and the Learned Perceptual Image Patch Similarity (LPIPS) [56]. The compression is measured by the final model size in megabytes (MB). The reported reconstruction quality metrics represent the average value computed between the ground-truth images (from test sets) and the rendered images from the model.

**Storage** Smol-GS is stored as multi-ple components: (i) occupancy-octree data as bit strings to represent quantized co-ordinates xˆ, (ii) binary arithmetic codes representing compressed features $\hat { f }$ and scaling controllers ŝ, (iii) MLP architecture/weights $\widehat { \mathrm { ( M L P _ { o } , M L P _ { c } , M L P _ { s } , } }$ $\mathrm { M L P } _ { r } , \; \mathrm { M L P } _ { o c t } , \; \mathrm { M L P } _ { h } ) ,$ and (iv) addi-

Table 1: The size of components of Smol-GS-base (in MB), averaged over all scenes.

|  | Total | x | f | s | MLPs | Others |
| --- | --- | --- | --- | --- | --- | --- |
| MIP-NERF 360 | 5.860 | 1.186 | 2.753 | 1.751 | 0.157 | 0.013 |
| DEEP BLENDING | 2.860 | 0.739 | 1.097 | 0.846 | 0.169 | 0.009 |
| TANKS AND TEMPLES | 4.784 | 0.843 | 2.260 | 1.526 | 0.143 | 0.012 |

tional metadata (i.e., the lower and upper bounds of the scene, the recursion depth R and $H a s h ( \cdot ) )$ The total Smol-GS size reported in this paper is the size of a single zip file containing all these four components (following the 3DGS.zip survey [52]). Table 1 showns the size of each component in Smol-GS averaged over scenes.

**Implementation details** Smol-GS is implemented in PyTorch [57] using the Inria 3DGS repository [1] as a starting point. Parameters of the model are trained using the Adam optimizer [58]. The loss coefficients in Eq. (8) are set to $\lambda _ { s } = 0 . 2$ , and $\lambda _ { q }   =   5 \times 1 0 ^ { - 4 }$ The thresholds for densification and pruning are set to $\tau _ { g }   =   2 \times 1 0 ^ { - 4 }$ and $\tau _ { o }   =   0 . 0 0 5$ We fix the feature $f$ dimensionality to $n _ { f } = 8$ , and all scenes are discretized with $R = 1 6$ recursion depth for coordinate compression and positional encoding. Additional implementation details, including learning rate (lr) values, lr schedulers, and MLP architectures, are provided in Sec. A. **Smol-GS variants:** We include three variants of Smol-GS (small, base, large) in the results with different compaction hyperparameters $\lambda _ { o }$ (small: $\lambda _ { o } = 4 { \times } 1 0 ^ { - 7 }$ , base: $\lambda _ { o } = \bar { 3 \times } 1 0 ^ { - 7 }$ , large: $\lambda _ { o } = 1 { \times } 1 0 ^ { - 7 } )$ . **Baselines:** We compare Smol-GS with the most efficient and recent 3DGS compression methods of Compact3DGS [7], SOG [10], Reducing3DGS [9], Compressed3D [8], CompGS [6], HAC [3], ContextGS [12], HEMGS [5], and HAC++ [4]. We also provide the original vanilla 3DGS results as the prototype baseline.

## 4.1 Results on 3DGS compression benchmarks

**Quantitative results** We compare Smol-GS with the baselines on three benchmark data sets using the four evaluation metrics mentioned earlier. The quantitative results are summarized in Table 2 and Fig. 6. The baseline results are collected from the 3DGS.zip compression survey [52]. In Table 2, Smol-GS achieves the highest compression ratio of all baselines with a considerable margin, reducing the model size by about 150× compared to vanilla 3DGS while maintaining high reconstruction fidelity. In the scatter plots in Fig. 6, Smol-GS outperforms all current state-of-the-art baselines in terms of the trade-off between compression ratio and reconstruction quality. We include further scatter plots for TANKS AND TEMPLES and DEEP BLENDING data sets in Fig. A14 in the Appendix.

**Qualitative results** Fig. 2 (MIP-NERF 360) and Fig. 7 (TANKS AND TEMPLES and DEEP BLEND-ING) show qualitative comparison of Smol-GS-base, vanilla 3DGS, and the ground-truth (GT) test views for different scenes. We highlight specific regions by providing zoomed-in views for better subjective comparison, especially for challenging objects such as the white wall in the Bonsai and Playroom scenes, the sky in the Train scene, and the rocket sticker in the Playroom scene.

7

<!-- page 8 of 23 -->

Table 2: Smol-GS provides state-of-the-art quality–size trade-off: We report PSNR/SSIM/LPIPS and the total model size in MBs following the 3DGS.zip survey benchmark [52]. Across MIP-NERF 360, TANKS AND TEMPLES, and DEEP BLENDING, Smol-GS has the smallest sizes with better or similar quality to the strongest baselines, indicating a better rate–distortion trade-off.

|  |  | MIP-N | ERF 360 |  |  | TANKS AN | D TEMPLE | S |  | DEEP B | LENDING |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Methods | PSNR↑ | SSIM↑ | LPIPS↓ | Size↓ | PSNR↑ | SSIM↑ | LPIPS↓ | Size↓ | PSNR↑ | SSIM↑ | LPIPS↓ | Size↓ |
| 3DGS-30K [1] | 27.21 | 0.815 | 0.214 | 734.000 | 23.14 | 0.841 | 0.183 | 411.000 | 29.41 | 0.903 | 0.243 | 676.000 |
| Compact3DGS [7] | 27.08 | 0.798 | 0.247 | 48.800 | 23.32 | 0.831 | 0.201 | 39.400 | 29.79 | 0.901 | 0.258 | 43.200 |
| SOG [10] | 27.08 | 0.799 | 0.230 | 40.285 | 23.56 | 0.837 | 0.186 | 22.779 | 29.26 | 0.894 | 0.268 | 17.737 |
| Reducing3DGS [9] | 27.10 | 0.809 | 0.226 | 29.000 | 23.57 | 0.840 | 0.188 | 14.000 | 29.63 | 0.902 | 0.249 | 18.000 |
| Compressed3D [8] | 26.98 | 0.801 | 0.238 | 28.803 | 23.32 | 0.832 | 0.194 | 17.282 | 29.38 | 0.898 | 0.253 | 25.299 |
| CompGS [6] | 27.03 | 0.804 | 0.243 | 18.000 | 23.39 | 0.836 | 0.200 | 12.000 | 29.90 | 0.906 | 0.252 | 12.000 |
| HAC [3] | 27.53 | 0.807 | 0.238 | 16.005 | 24.04 | 0.846 | 0.187 | 8.494 | 29.98 | 0.902 | 0.269 | 4.561 |
| ContextGS [12] | 27.62 | 0.808 | 0.237 | 13.297 | 24.12 | 0.849 | 0.186 | 9.902 | 30.09 | 0.907 | 0.265 | 3.655 |
| HEMGS [5] | 27.75 | 0.806 | 0.248 | 12.539 | 24.42 | 0.848 | 0.192 | 6.034 | 30.24 | 0.908 | 0.266 | 2.993 |
| HAC++ [4] | 27.60 | 0.803 | 0.253 | 8.742 | 24.22 | 0.849 | 0.190 | 5.427 | 30.16 | 0.907 | 0.266 | 3.051 |
| Smol-GS-base | 27.76 | 0.807 | 0.248 | 5.860 | 24.25 | 0.843 | 0.199 | 4.784 | 30.12 | 0.905 | 0.262 | 2.860 |
| Smol-GS-small | 27.61 | 0.801 | 0.258 | 4.867 | 24.21 | 0.841 | 0.204 | 4.209 | 29.97 | 0.903 | 0.266 | 2.422 |

![Chart block](images/wang2025_smol-gs_p8_b3.png)

![Chart block](images/wang2025_smol-gs_p8_b4.png)

![Chart block](images/wang2025_smol-gs_p8_b5.png)

Figure 6: Comparison of top methods on MIP-NERF 360. Each curve refers to one method of different variants; the x-axis is the model size in MBs (smaller is better) and the y-axis reports PSNR/SSIM (higher is better) or LPIPS (lower is better). Smol-GS (small–base–large) consistently lies beyond the Pareto frontier, achieving markedly smaller sizes at better quality to strong baselines collected via the 3DGS.zip benchmark. See Fig. A14 in the Appendix for results on TANKS AND TEMPLES and DEEP BLENDING.

Smol-GS clearly generates fewer artefacts than vanilla 3DGS. We link these visual improvements to the neural representation of abstract splats, which is capable of learning the optical properties and material cues of different surfaces adaptively. This representation is substantially more efficient in storing viewdependent cues compared to the expensive-to-store 3<sup>rd</sup>-degree spherical harmonic coefficients in 3DGS.

**Storage size** The required disk space for storing each model component in Smol-GS-base is summarized in Table 1. The splat-wise features f take half of the space, while storing the coordinates x is very efficient thanks to the occupancy-octree encoding. The MLP parameters solely take a negligible portion of the total size due to their tiny architectures. Compared to other methods like HAC++, we save more storage by eliminating the anchor-offset overhead and using low-dimensional features (n<sub>f</sub> = 8).

**Inference speed** The rendering speed of Smol-GS-base surpasses both vanilla 3DGS and the anchorbased HAC++, as shown in Table 3. Compared with 3DGS, the improvement stems from the viewdependent neural representation of splats, which is

Table 3: The comparison of frames per second (FPS) for rendering among Smol-GS-base, vanilla 3DGS, and HAC++. The values are averaged over all scenes.

|  | Smol-GS | 3DGS | HAC++ |
| --- | --- | --- | --- |
| MIP-NERF 360 | 210.0 | 139.3 | 128.0 |
| DEEP BLENDING | 399.9 | 178.8 | 149.8 |
| TANKS AND TEMPLES | 223.3 | 218.9 | 102.7 |

Table 4: Ablation on different modules for compression. We report values on MIP-NERF 360 for Smol-GS-base and its ablated variants: without Huffman coding, coordinate and feature compressions respectively. The rendered test views show that Smol-GS is capable of reconstructing scene details with high fidelity and preserving sharp edges.

| Ablation | Size | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| --- | --- | --- | --- | --- |
| Smol-GS-base | 5.86 | 27.76 | 0.807 | 0.248 |
| w/o Huffman | 7.038 | 27.76 | 0.807 | 0.248 |
| w/o Coordinate Quant | . 10.79 | 27.74 | 0.809 | 0.246 |
| w/o Feature Quant. | 23.71 | 27.72 | 0.805 | 0.250 |

8

<!-- page 9 of 23 -->

![Image block](images/wang2025_smol-gs_p9_b1.png)

Figure 7: Qualitative results on the TANKS AND TEMPLES and DEEP BLENDING data sets. Smol-GS has fewer artefacts and better preservation of scene details under challenging lighting and materials. The learned splat features in Smol-GS capture view-dependent and material cues more compactly than SH, aligning with its smaller size in MBs and competitive metrics in Table 2.

more storage-efficient than the costly $3 ^ { \mathrm { r d } } .$ -degree spherical harmonic coefficients. Compared with HAC++, the gain arises from removing the anchor-offset representation, avoiding the additional complications associated with offset localization and transparent offsets. The high rendering speed further demonstrates the practicality of Smol-GS for real-time applications.

**Ablation studies** The ablation study in Fig. 8 compares our model with/without positional encoding (PE). The proposed PE module improves the reconstruction quality under the same compression ratio through locality awareness. The ablation study in Table 4 compares our model with/without each compression module, showing how much each module contributes to the overall performance. Additional ablation studies on the impact of model hyperparameters, including recursion depth R, feature dimension $n _ { f } ,$ compaction strength $\lambda _ { o } ,$ and arithmetic coding strength $\lambda _ { q }$ , are included in Sec. B.1.

![Chart block](images/wang2025_smol-gs_p9_b5.png)

Figure 8: Ablation study on the positional encoding (PE) module. Our proposed PE improves the trade-off between PSNR and model size on MIP-NERF 360.

## 5 Discussion and conclusion

**Conclusion** We introduce Smol-GS, a compact 3DGS representation that keeps geometry explicit

and efficiently packed, and abstracts view-dependent appearance into low-dimensional, arithmetically coded splat features with locality awareness. Smol-GS achieves the highest compression ratio among existing baseline models and maintains competitive reconstruction quality. The compact storage and fast inference also facilitate real-time rendering and transmission of 3D scenes in resourceconstrained environments. Extensive experiments on standard 3D reconstruction data sets validate the effectiveness of Smol-GS through quantitative and qualitative experiments.

**Limitations** Smol-GS requires training for each scene, which is time-consuming and limits its scalability to large-scale applications. The positional encoding relies on the octree hierarchy, which is sensitive to splat edits and suboptimal for large-scale scenes.

**Future work** The discrete representations of splat features in Smol-GS could serve as 3D information tokens, enabling integration with other learning modalities and language models. The discrete primitive distribution can potentially be improved by depth estimation techniques. The octree hierarchy implies relations among splats, which can improve representation by leveraging prior knowledge of the geometry.

9

<!-- page 10 of 23 -->

## References

[1] Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, and George Drettakis. 3D Gaussian splatting for real-time radiance field rendering. ACM Transactions on Graphics (ToG), 42(4), 2023.

[2] Christoph Lassner and Michael Zollhofer. Pulsar: Efficient sphere-based neural rendering. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pages 1440–1449, 2021.

[3] Yihang Chen, Qianyi Wu, Weiyao Lin, Mehrtash Harandi, and Jianfei Cai. HAC: Hash-grid assisted context for 3D Gaussian splatting compression. In Proceedings of the European Conference on Computer Vision (ECCV), pages 422–438. Springer, 2024.

[4] Yihang Chen, Qianyi Wu, Weiyao Lin, Mehrtash Harandi, and Jianfei Cai. HAC++: Towards 100x compression of 3D Gaussian splatting. arXiv preprint arXiv:2501.12255, 2025.

[5] Lei Liu, Zhenghao Chen, Wei Jiang, Wei Wang, and Dong Xu. HEMGS: A hybrid entropy model for 3D Gaussian splatting data compression. arXiv preprint arXiv:2411.18473, 2024.

[6] KL Navaneet, Kossar Pourahmadi Meibodi, Soroush Abbasi Koohpayegani, and Hamed Pirsiavash. CompGS: Smaller and faster Gaussian splatting with vector quantization. In Proceedings of the European Conference on Computer Vision (ECCV), pages 330–349. Springer, 2024.

[7] Joo Chan Lee, Daniel Rho, Xiangyu Sun, Jong Hwan Ko, and Eunbyung Park. Compact 3D Gaussian representation for radiance field. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 21719–21728, 2024.

[8] Simon Niedermayr, Josef Stumpfegger, and Rüdiger Westermann. Compressed 3D Gaussian splatting for accelerated novel view synthesis. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 10349–10358, 2024.

[9] Panagiotis Papantonakis, Georgios Kopanas, Bernhard Kerbl, Alexandre Lanvin, and George Drettakis. Reducing the memory footprint of 3D Gaussian splatting. Proceedings of the ACM on Computer Graphics and Interactive Techniques, 7(1):1–17, 2024.

[10] Wieland Morgenstern, Florian Barthel, Anna Hilsmann, and Peter Eisert. Compact 3D scene representation via self-organizing Gaussian grids. In Proceedings of the European Conference on Computer Vision (ECCV), pages 18–34. Springer, 2024.

[11] Zhiwen Fan, Kevin Wang, Kairun Wen, Zehao Zhu, Dejia Xu, and Zhangyang Wang. LightGaussian: Unbounded 3D Gaussian compression with 15x reduction and 200+ fps. In Advances in Neural Information Processing Systems (NeurIPS), pages 140138–140158. Curran Associates, Inc., 2024.

[12] Yufei Wang, Zhihao Li, Lanqing Guo, Wenhan Yang, Alex Kot, and Bihan Wen. ContextGS: Compact 3D Gaussian splatting with anchor level context model. In Advances in Neural Information Processing Systems (NeurIPS), volume 37, pages 51532–51551. Curran Associates, Inc., 2024.

[13] Saswat Subhajyoti Mallick, Rahul Goel, Bernhard Kerbl, Markus Steinberger, Francisco Vicente Carrasco, and Fernando De La Torre. Taming 3DGS: High-quality radiance fields with limited resources. In SIGGRAPH Asia 2024 Conference Papers, pages 1–11, 2024.

[14] Guangchi Fang and Bing Wang. Mini-splatting: Representing scenes with a constrained number of Gaussians. In Proceedings of the European Conference on Computer Vision (ECCV), pages 165–181. Springer, 2024.

[15] Yangming Zhang, Wenqi Jia, Wei Niu, and Miao Yin. GaussianSpa: An “optimizingsparsifying" simplification framework for compact and high-quality 3D Gaussian splatting. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 26673–26682, 2025.

10

<!-- page 11 of 23 -->

[16] Stéphane Pateux, Matthieu Gendrin, Luce Morin, Théo Ladune, and Xiaoran Jiang. BOGausS: Better optimized Gaussian splatting. arXiv preprint arXiv:2504.01844, 2025.

[17] Kerui Ren, Lihan Jiang, Tao Lu, Mulin Yu, Linning Xu, Zhangkai Ni, and Bo Dai. Octree-GS: Towards consistent real-time rendering with lod-structured 3D Gaussians. arXiv preprint arXiv:2403.17898, 2024.

[18] Sharath Girish, Kamal Gupta, and Abhinav Shrivastava. EAGLES: Efficient accelerated 3D Gaussians with lightweight encodings. In Proceedings of the European Conference on Computer Vision (ECCV), pages 54–71. Springer, 2024.

[19] Haishan Wang, Mohammad Hassan Vali, and Arno Solin. Compressing 3D Gaussian splatting by noise-substituted vector quantization. In Scandinavian Conference on Image Analysis (SCIA), pages 338–352. Springer, 2025.

[20] Vickie Ye, Ruilong Li, Justin Kerr, Matias Turkulainen, Brent Yi, Zhuoyang Pan, Otto Seiskari, Jianbo Ye, Jeffrey Hu, Matthew Tancik, et al. gsplat: An open-source library for Gaussian splatting. Journal of Machine Learning Research (JMLR), 26(34):1–17, 2025.

[21] Tao Lu, Mulin Yu, Linning Xu, Yuanbo Xiangli, Limin Wang, Dahua Lin, and Bo Dai. Scaffold-GS: Structured 3D Gaussians for view-adaptive rendering. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 20654–20664, 2024.

[22] Ruwen Schnabel and Reinhard Klein. Octree-based point-cloud compression. In Proceedings of the 3rd Eurographics / IEEE VGTC Conference on Point-Based Graphics, SPBG’06, page 111–121, Goslar, DEU, 2006. Eurographics Association.

[23] Johannes L Schonberger and Jan-Michael Frahm. Structure-from-motion revisited. In Proceedings of the IEEE conference on Computer Vision and Pattern Recognition (CVPR), pages 4104–4113, 2016.

[24] Lee Alan Westover. Splatting: A Parallel, Feed-Forward Volume Rendering Algorithm. The University of North Carolina at Chapel Hill, 1991.

[25] Matthias Zwicker, Hanspeter Pfister, Jeroen Van Baar, and Markus Gross. EWA splatting. IEEE Transactions on Visualization and Computer Graphics, 8(3):223–238, 2002.

[26] Chi Yan, Delin Qu, Dan Xu, Bin Zhao, Zhigang Wang, Dong Wang, and Xuelong Li. GS-SLAM: Dense visual SLAM with 3D Gaussian splatting. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 19595–19604, 2024.

[27] Nikhil Keetha, Jay Karhade, Krishna Murthy Jatavallabhula, Gengshan Yang, Sebastian Scherer, Deva Ramanan, and Jonathon Luiten. SplaTAM: Splat track & map 3D Gaussians for dense RGB-D SLAM. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 21357–21366, 2024.

[28] Huajian Huang, Longwei Li, Hui Cheng, and Sai-Kit Yeung. Photo-SLAM: Real-time simultaneous localization and photorealistic mapping for monocular stereo and RGB-D cameras. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 21584–21593, 2024.

[29] Jiarui Hu, Xianhao Chen, Boyin Feng, Guanglin Li, Liangjing Yang, Hujun Bao, Guofeng Zhang, and Zhaopeng Cui. CG-SLAM: Efficient dense RGB-D SLAM in a consistent uncertainty-aware 3D Gaussian field. In Proceedings of the European Conference on Computer Vision (ECCV), pages 93–112. Springer, 2024.

[30] Yiwen Chen, Zilong Chen, Chi Zhang, Feng Wang, Xiaofeng Yang, Yikai Wang, Zhongang Cai, Lei Yang, Huaping Liu, and Guosheng Lin. GaussianEditor: Swift and controllable 3D editing with Gaussian splatting. In Proceedings of the IEEE/CVF conference on Computer Vision and Pattern Recognition (CVPR), pages 21476–21485, 2024.

[31] Jing Wu, Jia-Wang Bian, Xinghui Li, Guangrun Wang, Ian Reid, Philip Torr, and Victor Adrian Prisacariu. GaussCtrl: Multi-view consistent text-driven 3D Gaussian splatting editing. In Proceedings of the European Conference on Computer Vision (ECCV), pages 55–71. Springer, 2024.

11

<!-- page 12 of 23 -->

[32] Ruizhi Shao, Jingxiang Sun, Cheng Peng, Zerong Zheng, Boyao Zhou, Hongwen Zhang, and Yebin Liu. Control4D: Efficient 4D portrait editing with text. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 4556–4567, 2024.

[33] Jingyu Zhuang, Di Kang, Yan-Pei Cao, Guanbin Li, Liang Lin, and Ying Shan. Tip-editor: An accurate 3D editor following both text-prompts and image-prompts. ACM Transactions on Graphics (ToG), 43(4):1–12, 2024.

[34] Jiaxiang Tang, Jiawei Ren, Hang Zhou, Ziwei Liu, and Gang Zeng. DreamGaussian: Generative Gaussian splatting for efficient 3D content creation. arXiv preprint arXiv:2309.16653, 2023.

[35] Wojciech Zielonka, Timur Bagautdinov, Shunsuke Saito, Michael Zollhöfer, Justus Thies, and Javier Romero. Drivable 3D Gaussian avatars. In International Conference on 3D Vision (3DV), pages 979–990. IEEE, 2025.

[36] Ying Jiang, Chang Yu, Tianyi Xie, Xuan Li, Yutao Feng, Huamin Wang, Minchen Li, Henry Lau, Feng Gao, Yin Yang, and Jiang Chenfanfu. VR-GS: A physical dynamics-aware interactive Gaussian splatting system in virtual reality. In ACM SIGGRAPH (Conference Paper Track), 2024.

[37] Tianyuan Zhang, Hong-Xing Yu, Rundi Wu, Brandon Y Feng, Changxi Zheng, Noah Snavely, Jiajun Wu, and William T Freeman. PhysDreamer: Physics-based interaction with 3D objects via video generation. In Proceedings of the European Conference on Computer Vision (ECCV), pages 388–406. Springer, 2024.

[38] Aaron Van Den Oord, Oriol Vinyals, and Koray Kavukcuoglu. Neural discrete representation learning. In Advances in Neural Information Processing Systems 30 (NIPS). Curran Associates, Inc., 2017.

[39] Allen Gersho and Robert M Gray. Vector Quantization and Signal Compression, volume 159. Springer Science & Business Media, 2012.

[40] Mohammad Hassan Vali and Tom Bäckström. Stochastic optimization of vector quantization methods in application to speech and image processing. In International Conference on Acoustics, Speech and Signal Processing (ICASSP), pages 1–5, 2023.

[41] Stuart Lloyd. Least squares quantization in PCM. IEEE Transactions on Information Theory, 28(2):129–137, 1982.

[42] Yoseph Linde, Andres Buzo, and Robert Gray. An algorithm for vector quantizer design. IEEE Transactions on Communications, 28(1):84–95, 1980.

[43] Zizheng Que, Guo Lu, and Dong Xu. Voxelcontext-net: An octree based framework for point cloud compression. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 6042–6051, 2021.

[44] Chunyang Fu, Ge Li, Rui Song, Wei Gao, and Shan Liu. Octattention: Octree-based large-scale contexts model for point cloud compression. In Proceedings of the AAAI conference on artificial intelligence, volume 36, pages 625–633, 2022.

[45] Mingyue Cui, Junhua Long, Mingjian Feng, Boyang Li, and Huang Kai. Octformer: Efficient octree-based transformer for point cloud compression with local enhancement. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 37, pages 470–478, 2023.

[46] David A Huffman. A method for the construction of minimum-redundancy codes. Proceedings of the IRE, 40(9):1098–1101, 2007.

[47] Guy M Morton. A Computer Oriented Geodetic Data Base and a New Technique in File Sequencing. International Business Machines Company, 1966.

[48] Georgios Kopanas, Julien Philip, Thomas Leimkühler, and George Drettakis. Point-based neural rendering with per-view optimization. In Computer Graphics Forum, volume 40, pages 29–43. Wiley Online Library, 2021.

12

<!-- page 13 of 23 -->

[49] Wang Yifan, Felice Serena, Shihao Wu, Cengiz Öztireli, and Olga Sorkine-Hornung. Differentiable surface splatting for point-based geometry processing. ACM Transactions on Graphics (ToG), 38(6):1–14, 2019.

[50] Thomas Müller, Alex Evans, Christoph Schied, and Alexander Keller. Instant neural graphics primitives with a multiresolution hash encoding. ACM Transactions on Graphics (ToG), 41(4): 1–15, 2022.

[51] Ian H Witten, Radford M Neal, and John G Cleary. Arithmetic coding for data compression. Communications of the ACM, 30(6):520–540, 1987.

[52] Milena T Bagdasarian, Paul Knoll, Y Li, Florian Barthel, Anna Hilsmann, Peter Eisert, and Wieland Morgenstern. 3DGS.zip: A survey on 3D Gaussian splatting compression methods. In Computer Graphics Forum, volume 44, page e70078. Wiley Online Library, 2025.

[53] Jonathan T. Barron, Ben Mildenhall, Dor Verbin, Pratul P. Srinivasan, and Peter Hedman. Mip-NeRF 360: Unbounded anti-aliased neural radiance fields. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 5470–5479, 2022.

[54] Arno Knapitsch, Jaesik Park, Qian-Yi Zhou, and Vladlen Koltun. Tanks and temples: Benchmarking large-scale scene reconstruction. ACM Transactions on Graphics (ToG), 36(4), July 2017. ISSN 0730-0301.

[55] Peter Hedman, Julien Philip, True Price, Jan-Michael Frahm, George Drettakis, and Gabriel Brostow. Deep blending for free-viewpoint image-based rendering. ACM Transactions on Graphics (ToG), 37(6), December 2018. ISSN 0730-0301.

[56] Richard Zhang, Phillip Isola, Alexei A. Efros, Eli Shechtman, and Oliver Wang. The unreasonable effectiveness of deep features as a perceptual metric. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2018.

[57] Adam Paszke, Sam Gross, Francisco Massa, Adam Lerer, James Bradbury, Gregory Chanan, Trevor Killeen, Zeming Lin, Natalia Gimelshein, Luca Antiga, et al. PyTorch: An imperative style, high-performance deep learning library. Advances in Neural Information Processing Systems (NeurIPS), 32, 2019.

[58] Diederik P Kingma and Jimmy Ba. Adam: A method for stochastic optimization. arXiv preprint arXiv:1412.6980, 2014.

13

<!-- page 14 of 23 -->

## A Implementation details

## A.1 Hardware and software

Our experiments are conducted on NVIDIA H200 GPUs with 141 GB of memory. The code is implemented in Python 3.11 using the PyTorch framework (version 2.4.1) [57] with CUDA 12.4. The Gaussian rasterization module is built on top of the Inria 3DGS repository [1]. The arithmetic coding and hash encoding modules are built upon the implementations from HAC [3]. The average training time of Smol-GS-base is around 26.58 minutes (35k iterations) per scene.

## A.2 Optimization details

**Learning rates and schedulers** The model parameters are optimized using the Adam optimizer [58]. We use an exponential decay scheduler on learning rates of abstract features $f ,$ coordinates x, scaling controller s, all MLPs $( \mathrm { M L P } _ { o } , \mathrm { M L P } _ { c } , \mathrm { M L P } _ { r } , \mathrm { M L P } _ { s } , \mathrm { M L P } _ { h } , \mathrm { M L P } _ { o c t } )$ , and the hash encoder Hash(·). For each parameter, the learning rate η<sub>i</sub> at iteration i is defined as

$$
\eta_ {i} = \exp ((1 - t) \log (\eta_ {0}) + t \log (\eta_ {\mathrm{end}})), \text {where} \quad t = \operatorname{clamp} (\frac {i}{I}, \min = 0, \max = 1).\tag{9}
$$

Here I is the maximum iteration for the learning rate scheduler, $\eta _ { 0 }$ and $\eta _ { \mathrm { e n d } }$ are the initial and final learning rates, respectively. We use $I = 3 0 , 0 0 0$ , and the details of $\eta _ { 0 }$ and $\eta _ { \mathrm { e n d } }$ for different model parameters are shown in Table A5.

Table A5: Learning schedulers of model parameters. Here $\eta _ { 0 }$ and $\eta _ { \mathrm { e n d } }$ denote the initial and final learning rates, and the learning rate follows an exponential decay schedule defined in Eq. (9).

|  | x | f | s | MLP<sub>o</sub> | MLP<sub>c</sub> | MLP<sub>r</sub> | MLP<sub>s</sub> | MLP<sub>h</sub> | MLP<sub>oct</sub> | Hash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| η<sub>0</sub> | 0.0002 | 0.0075 | 0.01 | 0.002 | 0.008 | 0.004 | 0.004 | 0.005 | 0.008 | 0.005 |
| η<sub>end</sub> | 1×10<sup>-5</sup> | 0.0075 | 0.002 | 2×10<sup>-5</sup> | 5×10<sup>-5</sup> | 0.004 | 0.004 | 1×10<sup>-5</sup> | 0.008 | 1×10<sup>-5</sup> |

## A.3 Adaptive density control settings

During the Densification stage (0.5k–15k iterations), the pruning threshold on opacity is set to $\tau _ { o }   =   0 . 0 0 5$ . The densification threshold on the magnitude of coordinate gradients is defined as $\tau _ { g } = 2   \times   1 0 ^ { - 4 }$ . During the Compaction stage (15k–20k iterations), there is no densification module applied, and the pruning threshold on opacity is set to $\tau _ { o } = 0 . 0 0 5$

## A.4 Model hyperparameters

The feature dimension is fixed to $n _ { f } = 8 ,$ and the number of recursions of occupancy-octree for coordinate compression is set to $R = \dot { 1 6 }$ . The parameter selection is based on the ablation experiments in Sec. B.1.

**MLP architectures** The MLP architecture metadata, including the input dimension, output dimension, hidden dimension, number of layers, and activation types of the hidden layer and output layer, is summarized in Table A6. The input dimensions of $\dot { \operatorname { M L P } _ { o } , \operatorname { M L P } _ { c } , \operatorname { M L P } _ { r } , \operatorname { M L P } _ { s } }$ are $n _ { f } + n _ { o c t } + 4$ which is defined by the concatenation of the abstract feature $f$ (dimension $n _ { f }   =   \tilde { 8 ) }$ , the output dimension $n _ { o c t }$ of the octree encoder $\mathrm { M L P } _ { o c t } ,$ , the 3D viewing direction, and the viewing distance. Here $n _ { o c t }$ is fixed to be 8.

**Hash encoder** The hash encoder Hash(·) contains both 2D and 3D hash tables, with size $\mathrm { o f } \; 2 ^ { 1 5 }$ and $2 ^ { 1 3 }$ , respectively. There are 4-dimensional features per level. The resolution lists of 2D and 3D hash tables are defined as (130, 258, 514, 1026) and (18, 24, 33, 44, 59, 80, 108, 148, 201, 275, 376, 514).

**Model hyperparameters** For the default settings (Smol-GS-base), the regularization hyperparameters are set to $\lambda _ { o } = 3   \times   1 0 ^ { - 7 } ,   \lambda _ { g } = 5   \times   1 0 ^ { - 4 }$ and $\lambda _ { s } = 0 . 2 ,$ , and the recursion depth $r = 1 6$ where $\lambda _ { o } , \lambda _ { q }$ and $\lambda _ { s }$ denote the weights for opacity regularization, quantization regularization, and SSIM-loss regularization, respectively.

1

<!-- page 15 of 23 -->

r = 16

![Chart block](images/wang2025_smol-gs_p15_b2.png)

![Image block](images/wang2025_smol-gs_p15_b3.png)

![Image block](images/wang2025_smol-gs_p15_b4.png)

r = 10

![Image block](images/wang2025_smol-gs_p15_b6.png)

r = 14

r = 12

![Image block](images/wang2025_smol-gs_p15_b9.png)

Figure A9: Quantization recursion depth r vs. PSNR. We experiment with quantizing the coordinates of a trained 3DGS-30k model to be the ‘Quantized-30k’ models. These models are fine-tuned with quantized coordinates fixed for an additional 15k iterations to be ‘Quantized-45k’. Left: Quantitative metrics (PSNR) and splat number ratio after quantization vs. quantization recursion on the Garden scene. Right: Qualitative results of Quantized-30k. Higher recursions yield better quality but keep more splats.

Table A6: Details of the MLP architectures in Smol-GS. Here $n _ { f }$ denotes the feature dimension.

|  | Input Dim | Layers | Hidden Dim | Output Dim | Activation(Hidden/Output) |
| --- | --- | --- | --- | --- | --- |
| MLP<sub>o</sub> | nf + n<sub>oct</sub> + 4 | 3 | 128 | 1 | ReLU/Tanh |
| MLP<sub>c</sub> | nf + n<sub>oct</sub> + 4 | 3 | 128 | 3 | ReLU/Sigmoid |
| MLP<sub>r</sub> | nf + n<sub>oct</sub> + 4 | 3 | 128 | 4 | ReLU/None |
| MLP<sub>s</sub> | nf + n<sub>oct</sub> + 4 | 3 | 128 | 3 | ReLU/None |
| MLP<sub>h</sub> | 96 | 3 | 128 | 8 + 2nf | ReLU/None |
| MLP<sub>oct</sub> | 3r | 3 | 64 | noct | ReLU/None |

## B Additional experiments

In this section, we provide ablation studies on different model hyperparameters and optimization hyperparameters in Sec. B.1, additional quantitative results in Sec. B.2, additional qualitative results in Sec. B.3, occupancy-octree analysis in Sec. B.4, encoding and decoding time on each model component per scene in Sec. B.5, and the interpretation of learned abstract features in Sec. B.6.

## B.1 Ablation studies

We conduct ablation studies on four different hyperparameters in Smol-GS, including recursion level R, feature dimension $n _ { f }$ , the regularization weights on opacity and quantization $\lambda _ { o } , \lambda _ { q }$

**Recursion level** R The value of the total recursion depth R controls the compression ratio of splat coordinates. The ablation experiment on recursion level R is presented in Table A7 and Fig. A10, where $R \in \{ 1 4 , 1 5 , 1 6 , 1 7 , 1 \tilde { 8 } \}$ in the experiments. Larger R requires linearly more storage memory of coordinates, and leads to better reconstruction quality. Recursion level $R = 1 6$ provides a good trade-off between compression ratio and reconstruction quality.

**Feature dimension** $n _ { f }$ nf The value of $n _ { f }$ controls the dimensionality of abstract features. The ablation experiment on feature dimension $n _ { f }$ is presented in Table A8 and Fig. A11, where $n _ { f } \in$ $\{ 4 , 6 , 8 , \bar { 1 6 , 2 4 } \}$ in the experiments. Larger $n _ { f }$ requires more storage space for features, while improving the reconstruction quality. We choose feature dimension $n _ { f } = 8$ for compact storage and competitive reconstruction quality, as higher dimensionality yields marginal reconstruction gains while substantially increasing storage costs.

2

<!-- page 16 of 23 -->

Table A7: Ablation study on recursion level R of occupancy-octree encoding. The results show that R = 16 provides sufficient reconstruction quality.

<table><tr><td rowspan="2">Recursion Level</td><td colspan="4">MIP-NERF 360</td><td colspan="4">TANKS AND TEMPLES</td><td colspan="4">DEEP BLENDING</td></tr><tr><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td></tr><tr><td>R=14</td><td>27.36</td><td>0.787</td><td>0.265</td><td>5.132</td><td>23.58</td><td>0.808</td><td>0.244</td><td>3.769</td><td>29.69</td><td>0.901</td><td>0.272</td><td>2.789</td></tr><tr><td>R=15</td><td>27.60</td><td>0.801</td><td>0.252</td><td>5.513</td><td>24.07</td><td>0.829</td><td>0.220</td><td>4.463</td><td>30.17</td><td>0.906</td><td>0.260</td><td>2.798</td></tr><tr><td>R=16</td><td>27.69</td><td>0.806</td><td>0.248</td><td>5.896</td><td>24.23</td><td>0.842</td><td>0.201</td><td>4.8</td><td>30.05</td><td>0.905</td><td>0.263</td><td>2.747</td></tr><tr><td>R=17</td><td>27.68</td><td>0.807</td><td>0.248</td><td>6.084</td><td>24.32</td><td>0.846</td><td>0.199</td><td>4.813</td><td>30.05</td><td>0.905</td><td>0.262</td><td>3.114</td></tr><tr><td>R=18</td><td>27.70</td><td>0.808</td><td>0.248</td><td>6.207</td><td>24.28</td><td>0.847</td><td>0.195</td><td>4.958</td><td>30.07</td><td>0.904</td><td>0.264</td><td>2.851</td></tr></table>

![Chart block](images/wang2025_smol-gs_p16_b3.png)

![Chart block](images/wang2025_smol-gs_p16_b4.png)

![Chart block](images/wang2025_smol-gs_p16_b5.png)

![Chart block](images/wang2025_smol-gs_p16_b6.png)

Figure A10: Ablation study on recursion level R of occupancy-octree encoding. In each subfigure, the x-axis represents different recursion levels R, and the y-axis represents the corresponding metric values: PSNR, SSIM, LPIPS, and Size (in MBs).

Table A8: Ablation study on feature dimension $n _ { f } ,   n _ { f }   =   8$ provides a good trade-off between size and quality.

<table><tr><td rowspan="2">Feature Dimension</td><td colspan="4">MIP-NERF 360</td><td colspan="4">TANKS AND TEMPLES</td><td colspan="4">DEEP BLENDING</td></tr><tr><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td></tr><tr><td> $n_f = 4$ </td><td>27.37</td><td>0.799</td><td>0.255</td><td>5.038</td><td>23.91</td><td>0.835</td><td>0.207</td><td>4.054</td><td>30.07</td><td>0.905</td><td>0.263</td><td>2.64</td></tr><tr><td> $n_f = 6$ </td><td>27.61</td><td>0.803</td><td>0.252</td><td>5.036</td><td>24.06</td><td>0.835</td><td>0.212</td><td>4.2</td><td>30.03</td><td>0.903</td><td>0.267</td><td>2.316</td></tr><tr><td> $n_f = 8$ </td><td>27.69</td><td>0.806</td><td>0.248</td><td>5.896</td><td>24.23</td><td>0.842</td><td>0.201</td><td>4.8</td><td>30.05</td><td>0.905</td><td>0.263</td><td>2.747</td></tr><tr><td> $n_f = 16$ </td><td>27.80</td><td>0.809</td><td>0.245</td><td>8.398</td><td>24.30</td><td>0.845</td><td>0.200</td><td>6.663</td><td>30.11</td><td>0.905</td><td>0.262</td><td>3.89</td></tr><tr><td> $n_f = 24$ </td><td>27.84</td><td>0.809</td><td>0.245</td><td>10.24</td><td>24.19</td><td>0.838</td><td>0.209</td><td>6.354</td><td>30.10</td><td>0.905</td><td>0.264</td><td>3.775</td></tr></table>

![Chart block](images/wang2025_smol-gs_p16_b10.png)

![Chart block](images/wang2025_smol-gs_p16_b11.png)

![Chart block](images/wang2025_smol-gs_p16_b12.png)

![Chart block](images/wang2025_smol-gs_p16_b13.png)

Figure A11: Ablation study on feature dimension $n _ { f } .$ In each subfigure, the x-axis represents different feature dimensions $n _ { f } ,$ and the y-axis represents the corresponding metric values: PSNR, SSIM, LPIPS, and Size (in MBs).

**Opacity regularization** $\lambda _ { o }$ The value of $\lambda _ { o }$ controls the strength of opacity regularization. The ablation experiment on opacity regularization strength $\lambda _ { o }$ is presented in Table A9 and Fig. A12. The value of $\lambda _ { o }$ is set to $\{ 1  ×  \dot{1}0^{-7}, 2  ×  10^{-7}, 3  ×  10^{-7}, \dot{4}  ×  1\dot{0}^{-7}, \dot{5}  ×  10^{-7} \}$ in the experiments. The larger $\lambda _ { o }$ encourages the model to use fewer splats to represent the scene, resulting in worse reconstruction quality but smaller storage size. And $\lambda _ { o }   \in   [ 3   \times   1 0 ^ { - 7 } , 4   \times   1 0 ^ { - 7 } ]$ maintains proper reconstruction quality. Thus, we select our model variants in this range.

**Quantization regularization** $\lambda _ { q }$ The value of $\lambda _ { q }$ controls the strength of quantization regularization, which encourages the model to use fewer bits to represent the abstract features $f$ and scaling controller s. The ablation experiment on quantization regularization strength $\lambda _ { q }$ is presented in Table A10 and Fig. A13, where $\lambda _ { q }   \in   \{ 2   \times   1 0 ^ { - 4 } , 5   \times   1 0 ^ { - 4 } , 1   \times   1 0 ^ { - 3 } , 2   \times   1 0 ^ { - 3 } , \dot { 3   \times   1 0 ^ { - 3 } } \}$ in the experiments. Larger $\lambda _ { q }$ encourages the model to use fewer bits for feature representation f and scaling controller s, which sacrifices reconstruction quality and reduces the model storage size slowly when $\lambda _ { q } \geq 5 { \times } 1 0 ^ { - 4 }$ Therefore, we choose $\lambda _ { q } = 5   \times   1 0 ^ { - 4 }$ for our default model Smol-GS-base.

3

<!-- page 17 of 23 -->

Table A9: Ablation study on opacity regularization strength $\lambda _ { o } .$ We choose $\lambda _ { o } = 3   \times   1 0 ^ { - 7 }$ for the trade-off on reconstruction quality and model size.

<table><tr><td rowspan="2">Opacity Regularization</td><td colspan="4">MIP-NERF 360</td><td colspan="4">TANKS AND TEMPLES</td><td colspan="4">DEEP BLENDING</td></tr><tr><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td></tr><tr><td> $\lambda = 1e-7$ </td><td>27.85</td><td>0.812</td><td>0.231</td><td>10.31</td><td>24.30</td><td>0.846</td><td>0.189</td><td>7.11</td><td>30.16</td><td>0.906</td><td>0.253</td><td>4.678</td></tr><tr><td> $\lambda = 2e-7$ </td><td>27.78</td><td>0.810</td><td>0.239</td><td>7.563</td><td>24.16</td><td>0.842</td><td>0.196</td><td>5.596</td><td>30.16</td><td>0.906</td><td>0.258</td><td>3.396</td></tr><tr><td> $\lambda = 3e-7$ </td><td>27.69</td><td>0.806</td><td>0.248</td><td>5.896</td><td>24.23</td><td>0.842</td><td>0.201</td><td>4.8</td><td>30.05</td><td>0.905</td><td>0.263</td><td>2.747</td></tr><tr><td> $\lambda = 4e-7$ </td><td>27.59</td><td>0.801</td><td>0.258</td><td>4.825</td><td>24.17</td><td>0.840</td><td>0.204</td><td>4.19</td><td>30.07</td><td>0.904</td><td>0.265</td><td>2.458</td></tr><tr><td> $\lambda = 5e-7$ </td><td>27.44</td><td>0.794</td><td>0.270</td><td>4.033</td><td>24.07</td><td>0.837</td><td>0.209</td><td>3.951</td><td>30.00</td><td>0.903</td><td>0.268</td><td>2.23</td></tr></table>

![Chart block](images/wang2025_smol-gs_p17_b3.png)

![Chart block](images/wang2025_smol-gs_p17_b4.png)

![Chart block](images/wang2025_smol-gs_p17_b5.png)

![Chart block](images/wang2025_smol-gs_p17_b6.png)

Figure A12: Ablation study on opacity regularization strength $\lambda _ { o } .$ In each subfigure, the x-axis represents different opacity regularization strength $\lambda _ { o } ,$ and the y-axis represents the corresponding metric values: PSNR, SSIM, LPIPS, and Size (in MBs).

Table A10: Ablation study on quantization regularization strength $\lambda _ { \mathbf { q } } .$ . We select $\lambda _ { q } = 5   \times   1 0 ^ { - 4 }$ for the best marginal effect on overall metrics.

<table><tr><td rowspan="2">Quantization Regularization</td><td colspan="4">MIP-NERF 360</td><td colspan="4">TANKS AND TEMPLES</td><td colspan="4">DEEP BLENDING</td></tr><tr><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td><td>PSNR↑</td><td>SSIM↑</td><td>LPIPS↓</td><td>Size↓</td></tr><tr><td> $\lambda_q = 2e-4$ </td><td>27.73</td><td>0.807</td><td>0.248</td><td>6.516</td><td>23.67</td><td>0.821</td><td>0.233</td><td>4.666</td><td>30.10</td><td>0.905</td><td>0.262</td><td>3.034</td></tr><tr><td> $\lambda_q = 5e-4$ </td><td>27.69</td><td>0.806</td><td>0.248</td><td>5.896</td><td>24.23</td><td>0.842</td><td>0.201</td><td>4.8</td><td>30.05</td><td>0.905</td><td>0.263</td><td>2.747</td></tr><tr><td> $\lambda_q = 1e-3$ </td><td>27.67</td><td>0.806</td><td>0.249</td><td>5.454</td><td>24.22</td><td>0.841</td><td>0.201</td><td>4.467</td><td>30.06</td><td>0.904</td><td>0.262</td><td>2.651</td></tr><tr><td> $\lambda_q = 2e-3$ </td><td>27.53</td><td>0.804</td><td>0.251</td><td>5.065</td><td>24.08</td><td>0.839</td><td>0.203</td><td>4.089</td><td>29.97</td><td>0.903</td><td>0.265</td><td>2.407</td></tr><tr><td> $\lambda_q = 3e-3$ </td><td>27.42</td><td>0.802</td><td>0.253</td><td>4.797</td><td>24.08</td><td>0.838</td><td>0.205</td><td>3.93</td><td>29.52</td><td>0.898</td><td>0.281</td><td>2.664</td></tr></table>

![Chart block](images/wang2025_smol-gs_p17_b10.png)

![Chart block](images/wang2025_smol-gs_p17_b11.png)

![Chart block](images/wang2025_smol-gs_p17_b12.png)

![Chart block](images/wang2025_smol-gs_p17_b13.png)

Figure A13: Ablation study on quantization regularization strength $\lambda _ { \mathbf { q } } .$ In each subfigure, the x-axis represents different quantization regularization strength $\lambda _ { q } ,$ and the y-axis represents the corresponding metric values: PSNR, SSIM, LPIPS, and Size (in MBs).

## B.2 Additional quantitative results

The overall quantitative comparison among all baselines on three benchmark data sets is presented as a scatter plot in Fig. A14. The results demonstrate that Smol-GS achieves competitive reconstruction quality with the lowest memory footprints compared to other baselines.

## B.3 Additional qualitative results

Additional qualitative comparison among ground truth, 3DGS-30K, Smol-GS-base, and Smol-GS-small is presented in Fig. A15. The results show that Smol-GS preserves scene details with fewer artefacts than 3DGS-30K, even with smaller model sizes. Smol-GS-small loses some fine details compared to Smol-GS-base, but still maintains competitive visual quality.

4

<!-- page 18 of 23 -->

![Chart block](images/wang2025_smol-gs_p18_b1.png)

![Chart block](images/wang2025_smol-gs_p18_b2.png)

![Chart block](images/wang2025_smol-gs_p18_b3.png)

![Chart block](images/wang2025_smol-gs_p18_b4.png)

![Chart block](images/wang2025_smol-gs_p18_b5.png)

![Chart block](images/wang2025_smol-gs_p18_b6.png)

![Chart block](images/wang2025_smol-gs_p18_b7.png)

![Chart block](images/wang2025_smol-gs_p18_b8.png)

← Size [MB]

![Chart block](images/wang2025_smol-gs_p18_b10.png)

Figure A14: Comparison of reconstruction quality across baselines. In each subfigure, the x-axis represents the model size (in MBs), and the y-axis represents the corresponding metric values: PSNR (higher is better), SSIM (higher is better), LPIPS (lower is better). Different rows correspond to different benchmark data sets: MIP-NERF 360, TANKS AND TEMPLES, and DEEP BLENDING. Each line connects the results of a specific model over different hyperparameters (variants).

## B.4 Occupancy-octree analysis

The occupancy-octree learned in Sec. 3.1 generates a set of byte-codes during the encoding process. The statistical characteristics of the byte-codes are analyzed in Fig. A16. The results show that most divisions generate fewer non-empty sub-boxes, indicating that the byte-codes are highly sparse and thus compressible by entropy coding.

## B.5 Encoding and decoding details

Per-scene encoding time, decoding time, and reconstruction quality for both Smol-GS-base and Smol-GS-small are summarized in Tables A11 to A16.

## B.6 Interpretation of features

The abstract features learned by Smol-GS-base are visualized in Fig. A17. The features are visualized using a dimensionality reduction technique and transformation. Given feature f, the color visualized

5

<!-- page 19 of 23 -->

Ground truth

3DGS-30K

Smol-GS-base

Smol-GS-small

![Image block](images/wang2025_smol-gs_p19_b5.png)

Figure A15: Comparison of qualitative results among the ground truth, 3DGS-30K, Smol-GS-base, and Smol-GS-small.

is defined as $\mathrm { R G B } = \mathrm { s i g m o i d } ( \mathrm { P C A } ( \pmb { f } ) ) \in [ 0 , 1 ] ^ { 3 }$ , where PCA denotes the principal component analysis. We can observe that the learned features capture meaningful optical cues and semantics.

6

<!-- page 20 of 23 -->

![Image block](images/wang2025_smol-gs_p20_b1.png)

Figure A16: Statistical analysis of the occupancy-octree byte-codes on four example scenes: Bonsai, Room, Garden, DrJohnson. The occupancy-octree generates a series of byte-codes during the encoding process. Each byte-code denotes the existence of a splat in the sub-boxes of the corresponding division. The first row shows the histogram of the number of non-empty sub-boxes per division, and the second row shows the histogram of byte-codes (sorted by frequency). Each column corresponds to a specific scene. The histograms indicate the strong sparsity of the occupancy-octree byte-codes shared by different scenes.

Table A11: Encoding time (seconds) of each component of Smol-GS-base per scene.

| Encoding time (s) | Total | x | f | s | MLPs |
| --- | --- | --- | --- | --- | --- |
| Garden | 3.654 | 0.262 | 2.158 | 1.149 | 0.026 |
| Bicycle | 1.845 | 0.152 | 1.044 | 0.595 | 0.022 |
| Stump | 2.297 | 0.156 | 1.314 | 0.761 | 0.022 |
| Bonsai | 1.401 | 0.162 | 0.755 | 0.432 | 0.020 |
| MIP-NERF 360 Counter | 1.442 | 0.128 | 0.815 | 0.454 | 0.017 |
| Kitchen | 1.473 | 0.107 | 0.839 | 0.479 | 0.014 |
| Room | 0.961 | 0.102 | 0.495 | 0.320 | 0.020 |
| Treehill | 1.277 | 0.101 | 0.704 | 0.420 | 0.022 |
| Flowers | 2.988 | 0.223 | 1.704 | 0.970 | 0.024 |
| Drjohnson | 1.315 | 0.120 | 0.764 | 0.354 | 0.048 |
| DEEP BLENDING |  |  |  |  |  |
| Playroom | 0.996 | 0.093 | 0.587 | 0.262 | 0.031 |
| Train | 1.417 | 0.089 | 0.822 | 0.465 | 0.015 |
| TANKS AND TEMPLES |  |  |  |  |  |
| Truck | 1.794 | 0.142 | 0.977 | 0.609 | 0.023 |

7

<!-- page 21 of 23 -->

Table A12: Encoding time (seconds) of each component of Smol-GS-small per scene.

| Encoding time (s) | Total | x | f | s | MLPs |
| --- | --- | --- | --- | --- | --- |
| Garden | 2.938 | 0.219 | 1.690 | 0.943 | 0.024 |
| Bicycle | 1.558 | 0.125 | 0.869 | 0.510 | 0.021 |
| Stump | 1.687 | 0.116 | 0.958 | 0.558 | 0.019 |
| Bonsai | 1.218 | 0.115 | 0.678 | 0.384 | 0.016 |
| MIP-NERF 360 Counter | 1.317 | 0.120 | 0.731 | 0.411 | 0.022 |
| Kitchen | 1.420 | 0.135 | 0.794 | 0.434 | 0.022 |
| Room | 0.831 | 0.088 | 0.419 | 0.277 | 0.023 |
| Treehill | 0.856 | 0.077 | 0.481 | 0.266 | 0.012 |
| Flowers | 2.411 | 0.199 | 1.424 | 0.728 | 0.017 |
| Drjohnson | 0.883 | 0.100 | 0.451 | 0.295 | 0.018 |
| DEEP BLENDING |  |  |  |  |  |
| Playroom | 0.706 | 0.095 | 0.334 | 0.230 | 0.023 |
| Train | 1.297 | 0.085 | 0.746 | 0.428 | 0.013 |
| TANKS AND TEMPLES |  |  |  |  |  |
| Truck | 1.510 | 0.124 | 0.836 | 0.500 | 0.018 |

Table A13: Decoding time (seconds) of each component of Smol-GS-base per scene.

| Decoding time (s) | Total | x | f | s | MLPs |
| --- | --- | --- | --- | --- | --- |
| Garden | 5.507 | 0.230 | 3.216 | 2.030 | 0.019 |
| Bicycle | 2.882 | 0.126 | 1.692 | 1.042 | 0.017 |
| Stump | 3.478 | 0.132 | 2.001 | 1.320 | 0.019 |
| Bonsai | 2.118 | 0.114 | 1.210 | 0.757 | 0.026 |
| MIP-NERF 360 Counter | 2.227 | 0.105 | 1.286 | 0.810 | 0.021 |
| Kitchen | 2.288 | 0.095 | 1.314 | 0.859 | 0.015 |
| Room | 1.439 | 0.095 | 0.758 | 0.552 | 0.028 |
| Treehill | 1.955 | 0.079 | 1.117 | 0.741 | 0.015 |
| Flowers | 4.635 | 0.195 | 2.736 | 1.676 | 0.019 |
| Drjohnson | 1.657 | 0.152 | 0.785 | 0.608 | 0.108 |
| DEEP BLENDING |  |  |  |  |  |
| Playroom | 1.441 | 0.132 | 0.557 | 0.468 | 0.281 |
| Train | 2.180 | 0.064 | 1.284 | 0.814 | 0.014 |
| TANKS AND TEMPLES |  |  |  |  |  |
| Truck | 2.752 | 0.115 | 1.572 | 1.041 | 0.018 |

Table A14: Decoding time (seconds) of each component of Smol-GS-small per scene.

| Decoding time (s) | Total | x | f | s | MLPs |
| --- | --- | --- | --- | --- | --- |
| Garden | 4.485 | 0.192 | 2.634 | 1.630 | 0.019 |
| Bicycle | 2.420 | 0.105 | 1.400 | 0.890 | 0.019 |
| Stump | 2.527 | 0.094 | 1.438 | 0.972 | 0.018 |
| Bonsai | 1.869 | 0.099 | 1.068 | 0.681 | 0.016 |
| MIP-NERF 360 Counter | 1.980 | 0.095 | 1.133 | 0.730 | 0.018 |
| Kitchen | 2.097 | 0.104 | 1.202 | 0.758 | 0.025 |
| Room | 1.237 | 0.072 | 0.660 | 0.484 | 0.017 |
| Treehill | 1.257 | 0.052 | 0.717 | 0.469 | 0.014 |
| Flowers | 3.624 | 0.151 | 2.185 | 1.265 | 0.017 |
| Drjohnson | 1.285 | 0.081 | 0.654 | 0.530 | 0.017 |
| DEEP BLENDING |  |  |  |  |  |
| Playroom | 0.972 | 0.068 | 0.480 | 0.403 | 0.018 |
| Train | 2.004 | 0.059 | 1.184 | 0.744 | 0.013 |
| TANKS AND TEMPLES |  |  |  |  |  |
| Truck | 2.343 | 0.097 | 1.368 | 0.854 | 0.017 |

8

<!-- page 22 of 23 -->

Table A15: Reconstruction quality per scene for Smol-GS-base.

| Reconstruction | PSNR↑ | SSIM↑ | LPIPS↓ | Size↓ |
| --- | --- | --- | --- | --- |
| Garden | 27.327 | 0.844 | 0.157 | 11.283 |
| Bicycle | 24.881 | 0.720 | 0.310 | 5.644 |
| Stump | 26.658 | 0.767 | 0.271 | 7.015 |
| Bonsai | 32.971 | 0.945 | 0.188 | 4.010 |
| MIP-NERF 360 Counter | 29.707 | 0.914 | 0.191 | 4.498 |
| Kitchen | 31.440 | 0.925 | 0.133 | 4.470 |
| Room | 32.088 | 0.924 | 0.206 | 2.858 |
| Treehill | 23.210 | 0.635 | 0.396 | 3.782 |
| Flowers | 21.519 | 0.587 | 0.379 | 9.178 |
| Drjohnson | 29.627 | 0.902 | 0.263 | 3.331 |
| DEEP BLENDING |  |  |  |  |
| Playroom | 30.617 | 0.907 | 0.261 | 2.390 |
| Train | 22.608 | 0.806 | 0.241 | 4.198 |
| TANKS AND TEMPLES |  |  |  |  |
| Truck | 25.889 | 0.879 | 0.157 | 5.369 |

Table A16: Reconstruction quality per scene for Smol-GS-small.

| Reconstruction | PSNR↑ | SSIM↑ | LPIPS↓ | Size↓ |
| --- | --- | --- | --- | --- |
| Garden | 27.158 | 0.836 | 0.171 | 8.976 |
| Bicycle | 24.735 | 0.713 | 0.321 | 4.725 |
| Stump | 26.640 | 0.763 | 0.284 | 5.147 |
| Bonsai | 32.854 | 0.944 | 0.191 | 3.669 |
| MIP-NERF 360 Counter | 29.602 | 0.913 | 0.194 | 4.098 |
| Kitchen | 31.208 | 0.923 | 0.136 | 4.063 |
| Room | 31.912 | 0.922 | 0.210 | 2.530 |
| Treehill | 22.868 | 0.616 | 0.430 | 2.696 |
| Flowers | 21.477 | 0.581 | 0.389 | 7.900 |
| Drjohnson | 29.565 | 0.901 | 0.267 | 2.777 |
| DEEP BLENDING |  |  |  |  |
| Playroom | 30.374 | 0.906 | 0.265 | 2.067 |
| Train | 22.593 | 0.805 | 0.245 | 3.827 |
| TANKS AND TEMPLES |  |  |  |  |
| Truck | 25.823 | 0.877 | 0.163 | 4.590 |

9

<!-- page 23 of 23 -->

View 1

View 1 (feat)

View 2

View 2 (feat)

![Image block](images/wang2025_smol-gs_p23_b5.png)

Figure A17: Visualization of learned abstract features f. For each scene, we show two different views and their corresponding rendering image and feature visualizations. The features are visualized by mapping the 8-dimensional features to RGB colors using RGB = sigmoid(PCA(f)).

10