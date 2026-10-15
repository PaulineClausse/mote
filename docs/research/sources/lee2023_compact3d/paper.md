<!-- page 1 of 14 -->

arXiv:2311.13681v2 [cs.CV] 15 Feb 2024

# Compact 3D Gaussian Representation for Radiance Field

Joo Chan Lee<sup>1</sup> Daniel Rho<sup>2</sup> Xiangyu Sun<sup>1</sup>Jong Hwan Ko<sup>1B</sup> Eunbyung Park<sup>1B</sup>

Sungkyunkwan University<sup>1</sup>, KT<sup>2</sup>

![Image block](images/lee2023_compact3d_p1_b5.png)

Figure 1. Our method achieves reduced storage and faster rendering speed while maintaining high-quality reconstruction of 3DGS [18]. The core idea is to effectively remove the redundant Gaussians that do not significantly contribute to the overall performance (the sparser distribution of Gaussian points and reduced ellipsoid redundancy shown in the figure). We also introduce a more compact representation of Gaussian attributes, resulting in markedly improved storage efficiency and rendering speed.

## Abstract

Neural Radiance Fields (NeRFs) have demonstrated remarkable potential in capturing complex 3D scenes with high fidelity. However, one persistent challenge that hinders the widespread adoption of NeRFs is the computational bottleneck due to the volumetric rendering. On the other hand, 3D Gaussian splatting (3DGS) has recently emerged as an alternative representation that leverages a 3D Gaussisan-based representation and adopts the rasterization pipeline to render the images rather than volumetric rendering, achieving very fast rendering speed and promising image quality. However, a significant drawback arises as 3DGS entails a substantial number of 3D Gaussians to maintain the high fidelity of the rendered images, which requires a large amount of memory and storage. To address this critical issue, we place a specific emphasis on two key objectives: reducing the number of Gaussian points without sacrificing performance and compressing the Gaussian attributes, such as view-dependent color and covariance. To this end, we propose a learnable mask strategy that significantly reduces the number of Gaussians while preserving high performance. In addition, we propose a compact but effective representation of view-dependent color by employing a grid-based neural

field rather than relying on spherical harmonics. Finally, we learn codebooks to compactly represent the geometric attributes of Gaussian by vector quantization. With model compression techniques such as quantization and entropy coding, we consistently show over 25× reduced storage and enhanced rendering speed, while maintaining the quality of the scene representation, compared to 3DGS. Our work provides a comprehensive framework for 3D scene representation, achieving high performance, fast training, compactness, and real-time rendering. Our project page is available at [https://maincold2.github.io/c3dgs/](https://maincold2.github.io/c3dgs/).

## 1. Introduction

The field of neural rendering has witnessed substantial advancements in recent years, driven by the pursuit of rendering photorealistic 3D scenes from limited input data. Among the pioneering approaches, Neural Radiance Field (NeRF) [28] has gained considerable attention for its remarkable ability to generate high-fidelity images and 3D reconstructions of scenes from only a collection of 2D images in diverse applications. Follow-up research efforts have been dedicated to improving image quality [2, 30], accelerating training and rendering speed [7, 8, 10, 11, 30, 34], and reducing memory and storage footprints [35, 40].

1

<!-- page 2 of 14 -->

Despite the massive efforts, one persistent challenge that hinders the widespread adoption of NeRFs is the computational bottleneck due to the volumetric rendering. Since it demands dense point sampling along the ray to render a pixel, which requires significant computational resources, NeRFs often fail to achieve real-time rendering on handheld devices or low-end GPUs. This challenge limits their use in practical scenarios where fast rendering speed is essential, such as various interactive 3D applications.

3D Gaussian splatting (3DGS) [18] has recently emerged as an alternative representation that achieved very fast rendering speed and promising image quality. This approach leverages a point-based representation associated with 3D Gaussian attributes and adopts the rasterization pipeline to render the images rather than volumetric rendering. Highly optimized customized cuda kernels to maximize the parallelism and clever algorithmic tricks enable unprecedented rendering speed without compromising the image quality. However, a significant drawback arises as 3DGS entails a substantial number of 3D Gaussians to maintain the highfidelity of the rendered images (Fig. 1), which requires a large amount of memory and storage (e.g., often > 1GB for representing a large real-world scene).

To address the critical large memory and storage issue in 3DGS, we propose a compact 3D Gaussian representation framework. This approach significantly improves memory and storage efficiency while showing high-quality reconstruction, fast training speed, and real-time rendering, as shown in Fig. 1. We place a specific emphasis on two key objectives. First, we aim to reduce the number of Gaussian points required for scene representation without sacrificing performance. The number of Gaussians increases with regular densification processes consisting of cloning and splitting Gaussians, and it was a crucial component in representing the fine details of scenes. However, we observed that the current densification algorithm produces many redundant and unnecessary Gaussians, resulting in high memory and storage requirements. We introduce a novel volume-based masking strategy that identifies and removes non-essential Gaussians that have minimal impact on overall performance. With the proposed masking method, we learn to reduce the number of Gaussians while achieving high performance during training. In addition to the efficient memory and storage usage, we can achieve faster rendering speed since the computational complexity is linearly proportional to the number of Gaussians.

Second, we propose compressing the Gaussian attributes, such as view-dependent color and covariance. In the original 3DGS, each Gaussian has its own attributes, and it does not exploit spatial redundancy, which has been widely utilized for various types of signal compression. For example, neighboring Gaussians may share similar color attributes, and we can reuse similar colors from neighboring

Gaussians. Given this motivation, we incorporate a gridbased neural field to efficiently represent view-dependent colors rather than using per Gaussian color attributes. When provided with the query Gaussian points, we extract the color attribute from the compact grid representation, avoiding the need to store it for each Gaussian separately. For our initial approach, we opt for a hash-based grid representation (Instant NGP [30]) from among several candidates due to its compactness and fast processing speed. This choice has led to a significant reduction in the spatial complexity of 3DGS.

In contrast to the color attribute, the majority of Gaussians exhibit similar geometry, with limited variation in scale and rotation attributes. 3DGS represents a scene with numerous small Gaussians collectively, and each Gaussian primitive is not expected to show high diversity. Therefore, we introduce a codebook-based approach for modeling the geometry of Gaussians. It learns to find similar patterns or geometry shared across each scene and only stores the codebook index for each Gaussian, resulting in a very compact representation. Moreover, because the codebook size can be quite small, the spatial and computational overhead during training are not significant.

We have extensively tested our proposed compact 3D Gaussian representation on various datasets including real and synthetic scenes. Throughout the experiments regardless of dataset, we consistently showed about 15× reduced storage and enhanced rendering speed, while maintaining the quality of the scene representation, compared to 3DGS. Furthermore, our method can benefit from simple post-processings such as quantization and entropy coding, consequently achieving over 25× compression throughout the datasets. Especially for the evaluation on Deep Blending [16], a real-world dataset, we outperform 3DGS in terms of the reconstruction quality (measured in PSNR), notably with over 28× enhancement in storage efficiency and nearly 40% increase in rendering speed, setting a new state-of-the-art benchmark.

## 2. Related Work

## 2.1. Neural Radiance Fields

Neural radiance fields (NeRFs) have significantly expanded the horizons of 3D scene reconstruction and novel view synthesis. NeRF [28] introduced a novel approach to synthesizing novel views of 3D scenes, representing volume features by utilizing Multilayer Perceptrons (MLPs) and introducing volumetric rendering. Since its inception, various works have been proposed to enhance performance in diverse scenarios, such as different resolutions of reconstruction [2, 3], the reduced number of training samples [32, 36, 42, 44, 47], and reconstruction of large realistic scenes [29, 41] and dy namic scenes [12, 23, 24, 33]. However, NeRF’s reliance on MLP has been a bottleneck, particularly causing slow

2

<!-- page 3 of 14 -->

training and inference.

In an effort to address the limitations, grid-based methods emerged as a promising alternative. These approaches using explicit voxel grid structures [4, 9, 10, 25, 26, 39] have demonstrated a significant improvement in training speed compared to traditional MLP-based NeRF methods. Nevertheless, despite this advancement, grid-based methods still suffer from relatively slow inference speeds and, more importantly, require large amounts of memory. This has been a substantial hurdle in advancing towards more practical and widely applicable solutions.

Subsequent research efforts have been directed toward the reduction of the memory footprint while maintaining or even enhancing the performance quality by grid factorization [6, 7, 11, 13, 15, 31], hash grids [30], grid quantization [38, 40] or pruning [10, 35]. These methods have also been instrumental in the fast training of 3D scene representation, thereby making more efficient use of computational resources. However, a persistent challenge that remains is the ability to achieve real-time rendering of large-scale scenes. The volumetric sampling inherent in these methods, despite their advancements, still poses a limitation.

## 2.2. Point-based Rendering and Radiance Field

Point-NeRF [45] employed points to represent a radiance field with volumetric rendering. Although it shows promising performance, the volume rendering hinders the realtime rendering. NeRF-style volumetric rendering and pointbased α-blending fundamentally share the same model for rendering images but differ significantly in their rendering algorithms [18]. NeRFs offer a continuous feature representation of the entire volume as empty or occupied spaces, which necessitate costly volumetric sampling to render a pixel, leading to high computational demands. In contrast, points provide an unstructured, discrete representation of a volume geometry by the creation, destruction, and movement of points, and a pixel is rendered by blending several ordered points overlapping the pixel. This is achieved by optimizing opacity and positions [20], thus bypassing the limitations inherent in full volumetric representations and achieving remarkably fast rendering.

Point-based methods have been widely used in rendering 3D scenes, where the simplest form is point clouds. However, point clouds can lead to visual artifacts such as holes and aliasing. To mitigate this, point-based neural rendering methods have been proposed, processing the points through rasterization-based point splatting and differentiable rasterization [22, 43, 46]. The points were represented by neural features and rendered with CNNs [1, 20, 27]. However, these methods heavily rely on Multi-View Stereo (MVS) for initial geometry, inheriting its limitations, especially in challenging scenarios like areas lacking features, shiny surfaces, or fine structures.

Neural Point Catacaustics [21] addressed the issue of view-dependent effect through the use of an MLP, yet it still depends on MVS geometry for its input. Without the need for MVS, Zhang et al. [49] incorporated Spherical Harmonics (SH) for directional control. However, this method is constrained to managing scenes with only a single object and requires the use of masks during its initialization phase. Recently, 3D Gaussian Splatting (3DGS) [18] proposed using 3D Gaussians as primitives for real-time neural rendering. 3DGS utilized highly optimized custom CUDA kernels and ingenious algorithmic approaches, it achieves unparalleled rendering speed without sacrificing image quality.

While 3DGS does not require dense sampling for each ray, it does require a substantial number of 3D Gaussians to maintain a high level of quality in the resulting rendered images. Additionally, since each Gaussian consists of several rendering-related attributes like covariance matrices and SH with high degrees, 3DGS demands significant memory and storage resources, e.g., exceeding 1GB for a realistic scene. Our work aims to alleviate this parameter-intensive requirement while preserving high rendering quality, fast training, and real-time rendering.

## 3. Method

**Background.** In our approach, we build upon the foundation of 3D Gaussian Splatting (3DGS) [18], a point-based representation associated with 3D Gaussian attributes for representing 3D scenes. Each Gaussian represents 3D position, opacity, geometry (3D scale and 3D rotation represented as a quaternion), and spherical harmonics (SH) for view-dependent color. 3DGS constructs initial 3D Gaussians derived from the sparse data points obtained by Structure-from-Motion (SfM), such as COLMAP [37]. These Gaussians are cloned, split, pruned, and refined towards enhancing the anisotropic covariance for a precise depiction of the scene. This training process is based on the gradients from the differentiable rendering without unnecessary computation in empty space, which accelerates training and rendering. However, 3DGS’s high-quality reconstruction comes at the cost of memory and storage requirements, particularly with numerous Gaussians increased during training and their associated attributes.

**Overall architecture.** Our primary objectives are to 1) reduce the number of Gaussians and 2) represent attributes compactly while retaining the original performance. To this end, along with the optimization process, we mask out Gaussians that minimally impact performance and represent geometric attributes by codebooks, as shown in Fig. 2. We represent the color attributes using a grid-based neural field rather than storing them directly per each Gaussian. For geometry attributes, such as scale and rotation, we propose using a codebook-based method that can fully exploit the limited variations of these attributes. Finally, a small number

3

<!-- page 4 of 14 -->

![Image block](images/lee2023_compact3d_p4_b1.png)

Figure 2. The detailed architecture of our proposed compact 3D Gaussian.

![Chart block](images/lee2023_compact3d_p4_b3.png)

Figure 3. Visualization of the varying count of Gaussians during training (Bonsai scene). ‘# Gaussians’ denotes the number of Gaussians.

of Gaussians with compact attributes are then used for the subsequent rendering steps, including projection and rasterization to render images.

## 3.1. Gaussian Volume Mask

3DGS originally densifies Gaussians with large gradients by cloning or splitting. To regulate the increase in the number of Gaussians, opacities are set to a small number at every specific interval, and after some iterations, those with still minimal opacities are removed. Although this opacity-based control effectively eliminates some floaters, we empirically found that redundant Gaussians still exist significantly (×2.42 Gaussians show similar performance in Fig. 3).

The scale attribute of each Gaussian determines its 3D volume, which is then reflected in the rendering process. Small-sized Gaussians, due to their minimal volume, have a negligible contribution to the overall rendering quality, often to the point where their effect is essentially imperceptible. In such cases, it becomes highly beneficial to identify and remove such unessential Gaussians.

To this end, we propose a learnable masking of Gaussians based on their volume as well as transparency. We apply binary masks not only on the opacities $\boldsymbol { o }   \in   [ 0 , 1 ] ^ { N }$ but also on the non-negative scale attributes $s \in \mathbb { R } _ { + } ^ { N \check { \times } \check { 3 } }$ that determine the volume geometry of N Gaussians, where N may vary with densification of Gaussians. We introduce an

additional mask parameter $m   \in   \mathbb { R } ^ { N }$ , based on which we generate binary masks $M   \in   \{ 0 , 1 \} ^ { N }$ . As it is not feasible to calculate gradients from binarized masks, we employ the straight-through estimator [5]. More specifically, the masked scale $\hat { s } \in \tilde { \mathbb { R } } _ { + } ^ { N \times 3 }$ and the masked opacity $\dot { \boldsymbol { o } } \in [ \dot { 0 } , 1 ] ^ { N }$ are formulated as follows,

$$
M _ {n} = \mathrm{sg} (\mathbb {1} [ \sigma (m _ {n}) > \epsilon ] - \sigma (m _ {n})) + \sigma (m _ {n}),\tag{1}
$$

$$
\hat {s} _ {n} = M _ {n} s _ {n}, \quad \hat {o} _ {n} = M _ {n} o _ {n},\tag{2}
$$

where n is the index of the Gaussian, ϵ is the masking threshold, sg(·) is the stop gradient operator, and 1[·] and $\sigma ( \cdot )$ are indicator and sigmoid function, respectively. This method allows for the incorporation of masking effects based on Gaussian volume and transparency in rendering. Considering both aspects together leads to more effective masking compared to considering either aspect alone.

We balance the accurate rendering and the number of Gaussians eliminated during training by adding masking loss $L _ { m }$ as follows,

$$
L _ {m} = \frac {1}{N} \sum_ {n = 1} ^ {N} \sigma (m _ {n}).\tag{3}
$$

At every densification, we eliminate the Gaussians according to the binary mask. Furthermore, unlike the original 3DGS that stops densifying in the middle of the training and retains the number of Gaussians to the end, we consistently mask out along with the entire training process, reducing unessential Gaussians effectively and ensuring efficient computation with low GPU memory throughout the training phase (Fig. 3). Once training is completed, the mask parameter m does not need to be stored since we removed the masked Gaussians.

## 3.2. Geometry Codebook

A number of Gaussians collectively construct a single scene, where similar geometric components can be shared throughout the entire volume. We have observed that the geometrical shapes of most Gaussians are very similar, showing only minor differences in scale and rotation characteristics. In addition, a scene is composed of many small Gaussians, and each Gaussian primitive is not expected to exhibit a wide range of diversity. Given this motivation, we

4

<!-- page 5 of 14 -->

![Image block](images/lee2023_compact3d_p5_b1.png)

Figure 4. The detailed process of R-VQ to represent the scale and rotation of Gaussians. In the first stage, the scale and rotation vectors are compared to codes in each codebook, with the closest code identified as the result. In the next stage, the residual between the original vector and the first stage’s result is compared with another codebook. This process is repeated up to the final stage, as a result, the selected indices and the codebook from each stage collectively represent the original vector.

propose a codebook learned to represent representative geometric attributes, including scale and rotation, by employing vector quantization (VQ) [14]. As naively applying vector quantization requires computational complexity and large GPU memory [48], we adopt residual vector quantization (R-VQ) [48] that cascades L stages of VQ with codebook size C (Fig. 4), formulated as follows,

$$
\hat {r} _ {n} ^ {l} = \sum_ {k = 1} ^ {l} \mathcal {Z} ^ {k} [ i ^ {k} ], \quad l \in \{1, \dots , L \},\tag{4}
$$

$$
i _ {n} ^ {l} = \underset {k} {\mathrm{argmin}} | | \mathcal {Z} ^ {l} [ k ] - (r _ {n} - \hat {r} _ {n} ^ {l - 1}) | | _ {2} ^ {2}, \hat {r} _ {n} ^ {0} = \vec {0}\tag{5}
$$

where $r \in \mathbb { R } ^ { N \times 4 }$ is the input rotation vector, $\hat { r } ^ { l } \in \mathbb { R } ^ { N \times 4 }$ is the output rotation vector after l quantization stages, and n is the index of the Gaussian. $\dot { \mathcal { Z } ^ { l } \in \mathbb { R } ^ { C \times 4 } }$ is the codebook at the stage $l ,   i ^ { l } \in \{ 0 , \ldots , C - 1 \} ^ { N }$ is the selected indices of the codebook at the stage l, and $\mathcal { Z } [ i ] \in \mathbb { R } ^ { 4 }$ represents the vector at index i of the codebook $\mathcal { Z } ,$

The objective function for training the codebooks is as follows,

$$
L _ {r} = \frac {1}{N C} \sum_ {k = 1} ^ {L} \sum_ {n = 1} ^ {N} | | \operatorname{sg} [ r _ {n} - \hat {r} _ {n} ^ {k - 1} ] - \mathcal {Z} ^ {k} [ i _ {n} ^ {k} ] | | _ {2} ^ {2},\tag{6}
$$

where sg[·] is the stop-gradient operator. We use the output from the final stage $\hat { r } ^ { L }$ (we will omit the superscript L for brevity from now onwards), and the R-VQ process is similarly applied to scale s before masking (we also similarly use the objective function for scale $L _ { s } )$

## 3.3. Compact View-dependent Color

Each Gaussian in 3DGS requires 48 of the total 59 parameters to represent SH (max 3 degrees) to model the different colors according to the viewing direction. Instead of using the naive and parameter-inefficient approach, we propose representing the view-dependent color of each Gaussian by exploiting a grid-based neural field. To this end, we contract the unbounded positions $p \; \in \; \mathbb { R } ^ { N \times 3 }$ to the bounded range, motivated by mip-NeRF 360 [3], and compute the 3D view direction d $\in \mathbb { R } ^ { 3 }$ for each Gaussian based on the

camera center point. We exploit hash grids [30] followed by a tiny MLP to represent color. Here, we input positions into the hash grids, and then the resulting feature and the view direction are fed into the MLP. More formally, viewdependent color $c _ { n } ( \cdot )$ of Gaussian at position $p _ { n } \in \mathbb { R } ^ { 3 }$ can be expressed as,

$$
c _ {n} (d) = f (\text {contract} (p _ {n}), d; \theta),\tag{7}
$$

$$
\text {contract} (p _ {n}) = \left\{ \begin{array}{l l} p _ {n} & | | p _ {n} | | \leq 1 \\ \left(2 - \frac {1}{| | p _ {n} | |}\right) \left(\frac {p _ {n}}{| | p _ {n} | |}\right) & | | p _ {n} | | > 1, \end{array} \right.\tag{8}
$$

where $f ( \cdot ; \theta )$ , contract(·) : $\mathbb { R } ^ { 3 }   \rightarrow   \mathbb { R } ^ { 3 }$ stand for the neural field with parameters $\theta ,$ and the contraction function, respectively. We use the 0-degree components of SH (the same number of channels as RGB, but not view-dependent) and then convert them into RGB colors due to the slightly increased performance compared to representing the RGB color directly.

## 3.4. Training

Here, we have N Gaussians and their attributes, position $p _ { n } ,$ opacity $o _ { n } ,$ rotation $\hat { r } _ { n }$ , scale $\hat { s } _ { n }$ , and view-dependent color $c _ { n } ( \cdot )$ , which are used to render images. The entire model is trained end-to-end based on the rendering loss $L _ { r e n }$ , the weighted sum of the L1 and SSIM loss between the GT and rendered images. By adding the loss for masking $L _ { m }$ and geometry codebooks $L _ { r } , L _ { s } ,$ the overall loss L is as follows,

$$
L = L _ {r e n} + \lambda_ {m} L _ {m} + L _ {r} + L _ {s},\tag{9}
$$

where $\lambda _ { m }$ is a hyperparameter to regularize the number of Gaussians. To avoid heavy computations and ensure fast and optimal training, we apply R-VQ and learn codebooks with K-means initialization, only for the last 1K training iterations. Except for that period, we set $L _ { r } , L _ { s }$ to zero.

## 4. Experiment

## 4.1. Implementation Details

We tested our approach on three real-world datasets (Mip-NeRF 360 [3], Tanks&Temples [19], and

5

<!-- page 6 of 14 -->

Table 1. Qualitative results of the proposed method evaluated on Mip-NeRF 360 and Tanks&Temples datasets. We reported the numbers of baselines from the original paper (denoted as 3DGS), which were run on an NVIDIA A6000 GPU. For a fair comparison, we re-evaluate 3DGS with the same training configurations as our method using an NVIDIA A100 GPU (denoted as 3DGS\*).

<table><tr><td rowspan="2">DatasetMethod</td><td colspan="6">Mip-NeRF 360</td><td colspan="6">Tanks&amp;Temples</td></tr><tr><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>Train</td><td>FPS</td><td>Storage</td><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>Train</td><td>FPS</td><td>Storage</td></tr><tr><td>Plenoxels</td><td>23.08</td><td>0.626</td><td>0.463</td><td>25m 49s</td><td>6.79</td><td>2.1 GB</td><td>21.08</td><td>0.719</td><td>0.379</td><td>25m 05s</td><td>13.0</td><td>2.3 GB</td></tr><tr><td>INGP-base</td><td>25.30</td><td>0.671</td><td>0.371</td><td>05m 37s</td><td>11.7</td><td>13 MB</td><td>21.72</td><td>0.723</td><td>0.330</td><td>05m 26s</td><td>17.1</td><td>13 MB</td></tr><tr><td>INGP-big</td><td>25.59</td><td>0.699</td><td>0.331</td><td>07m 30s</td><td>9.43</td><td>48 MB</td><td>21.92</td><td>0.745</td><td>0.305</td><td>06m 59s</td><td>14.4</td><td>48 MB</td></tr><tr><td>Mip-NeRF 360</td><td>27.69</td><td>0.792</td><td>0.237</td><td>48h</td><td>0.06</td><td>8.6 MB</td><td>22.22</td><td>0.759</td><td>0.257</td><td>48h</td><td>0.14</td><td>8.6 MB</td></tr><tr><td>3DGS</td><td>27.21</td><td>0.815</td><td>0.214</td><td>41m 33s</td><td>134</td><td>734 MB</td><td>23.14</td><td>0.841</td><td>0.183</td><td>26m 54s</td><td>154</td><td>411 MB</td></tr><tr><td>3DGS*</td><td>27.46</td><td>0.812</td><td>0.222</td><td>24m 07s</td><td>120</td><td>746 MB</td><td>23.71</td><td>0.845</td><td>0.178</td><td>13m 51s</td><td>160</td><td>432 MB</td></tr><tr><td>Ours</td><td>27.08</td><td>0.798</td><td>0.247</td><td>33m 06s</td><td>128</td><td>48.8 MB</td><td>23.32</td><td>0.831</td><td>0.201</td><td>18m 20s</td><td>185</td><td>39.4 MB</td></tr><tr><td>Ours+PP</td><td>27.03</td><td>0.797</td><td>0.247</td><td>-</td><td>-</td><td>29.1 MB</td><td>23.32</td><td>0.831</td><td>0.202</td><td>-</td><td>-</td><td>20.9 MB</td></tr></table>

Table 2. Qualitative results of the proposed method evaluated on Deep Blending dataset. We re-evaluate 3DGS\* same with our method.

<table><tr><td rowspan="2">DatasetMethod</td><td colspan="6">Deep Blending</td></tr><tr><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>Train</td><td>FPS</td><td>Storage</td></tr><tr><td>Plenoxels</td><td>23.06</td><td>0.795</td><td>0.510</td><td>27m 49s</td><td>11.2</td><td>2.7 GB</td></tr><tr><td>INGP-base</td><td>23.62</td><td>0.797</td><td>0.423</td><td>06m 31s</td><td>3.26</td><td>13 MB</td></tr><tr><td>INGP-big</td><td>24.96</td><td>0.817</td><td>0.390</td><td>08m 00s</td><td>2.79</td><td>48 MB</td></tr><tr><td>Mip-NeRF 360</td><td>29.40</td><td>0.901</td><td>0.245</td><td>48h</td><td>0.09</td><td>8.6 MB</td></tr><tr><td>3DGS</td><td>29.41</td><td>0.903</td><td>0.243</td><td>36m 02s</td><td>137</td><td>676 MB</td></tr><tr><td>3DGS*</td><td>29.46</td><td>0.900</td><td>0.247</td><td>21m 52s</td><td>132</td><td>663 MB</td></tr><tr><td>Ours</td><td>29.79</td><td>0.901</td><td>0.258</td><td>27m 33s</td><td>181</td><td>43.2MB</td></tr><tr><td>Ours+PP</td><td>29.73</td><td>0.900</td><td>0.258</td><td>-</td><td>-</td><td>23.8MB</td></tr></table>

Table 3. Qualitative results of the proposed method evaluated on NeRF-Synthetic dataset. \* denotes the reported value in the original paper.

<table><tr><td>Dataset</td><td colspan="4">NeRF-Synthetic</td></tr><tr><td>Method</td><td>PSNR</td><td>Train Time</td><td>Storage FPS</td><td>FPS</td></tr><tr><td>3DGS</td><td>33.32*</td><td>68.1 MB</td><td>6m 14s</td><td>359</td></tr><tr><td>Ours</td><td>33.33</td><td>5.55 MB (×0.08)</td><td>8m 04s (×1.29)</td><td>545 (×1.52)</td></tr><tr><td>Ours+PP</td><td>32.88</td><td>2.67 MB (×0.04)</td><td>-</td><td>-</td></tr></table>

Deep Blending [16]) and a synthetic dataset (NeRF-Synthetic [28]). Following 3DGS, we chose two scenes from Tanks&Temples and Deep Blending. The models with the proposed method (denoted as Ours) were trained during 30K iterations, where we stored positions p and opacities o with 16-bit precision using half-tensors. Additionally, we implemented straightforward post-processing techniques on the model attributes, a variant we denote as Ours+PP. These post-processing steps include:

• Applying 8-bit min-max quantization to opacity and hash grid parameters.

• Pruning hash grid parameters with values below 0.1.

• Applying Huffman encoding [17] on the quantized opacity and hash parameters, and R-VQ indices.

Further implementation details are provided in the supplementary materials.

## 4.2. Performance Evaluation

**Real-world scenes.** Tab. 1 and Tab. 2 show the qualitative results evaluated on real-world scenes. Our approach consistently reduces the storage requirements significantly and enhances the rendering speed, while performing accu rate reconstruction comparable to 3DGS. Especially for the Deep Blending dataset (Tab. 2), our method even outperforms the original 3DGS in terms of visual quality (measured in PSNR and SSIM), achieving state-of-the-art performance with the fastest rendering speed as well as compactness (almost 40% faster rendering and over 15× compactness compared to 3DGS). The qualitative results in Fig. 5 also show the high-quality reconstruction with significantly reduced storage of our method, compared to 3DGS.

**Synthetic scenes.** We also evaluate our method on synthetic scenes. As 3DGS has proven its effectiveness in visual quality, rendering speed, and training time compared to other baselines, we focus on comparing our method with 3DGS, highlighting the improvements from our method. As shown in Tab. 3, although our approach requires slightly more training duration, we achieve over 10× compression and 50% faster rendering compared to 3DGS, maintaining high-quality reconstruction.

**With post-processings,** our model is further downsized by over 40 % regardless of dataset. Consequently, we achieve more than 25× compression from 3DGS, while maintaining high performance.

## 4.3. Ablation Study

**Learnable volume masking.** As shown in Tab. 4, the proposed volume-based masking reduces the number of Gaussians significantly while retaining (even slightly increasing) the visual quality, demonstrating its effective removal of redundant and unessential Gaussians. The reduced Gaussians show several additional advantages: reducing training time, storage, and testing time. Specifically on Playroom scene, the volume-mask shows a 140% increase in storage effi-

6

<!-- page 7 of 14 -->

Ours

3DGS

GT

Ours+PP

![Image block](images/lee2023_compact3d_p7_b5.png)

Figure 5. Qualitative results of our approach compared to 3DGS. We present the rendering PSNR and storage on the results.

![Image block](images/lee2023_compact3d_p7_b7.png)

Figure 6. Effect of the proposed learnable volume masking, compared to the original 3DGS. We visualize Gaussian center points, ellipsoids, and rendered results using Playroom scene.

ciency and a 65% increase in rendering speed. Furthermore, we validate the actual impact in rendering by visualizing Gaussians in Fig. 6. Although the number of Gaussians is noticeably reduced demonstrated by the sparser points in visualization, the rendered result retains high quality without visible difference. These results quantitatively and qualitatively demonstrate the effectiveness and efficiency of the proposed method.

**Compact view-dependent color.** The proposed color representation based on the neural field offers more than a threefold improvement in storage efficiency with a slightly reduced number of Gaussians compared to the directly storing high-degree SH, despite necessitating slightly more

time for training and rendering. Nonetheless, when compared to 3DGS, the proposed color representation with the masking strategy demonstrates either a faster or comparable rendering speed.

**Geometry codebook.** Our proposed geometry codebook approach achieves a reduction in storage requirements by approximately 30% while maintaining the quality of reconstruction, training time, and rendering speed. To delve deeper into the reasons for this improved performance, we start by visualizing the Gaussians, as depicted in Fig. 7-(a). It is observed that the majority of Gaussians maintain identical geometry in the visualizations regardless of the application of R-VQ, with only a few exhibiting very subtle geo-

7

<!-- page 8 of 14 -->

![Image block](images/lee2023_compact3d_p8_b1.png)

![Image block](images/lee2023_compact3d_p8_b2.png)

![Image block](images/lee2023_compact3d_p8_b3.png)

![Image block](images/lee2023_compact3d_p8_b4.png)

(a) Rendered results

![Chart block](images/lee2023_compact3d_p8_b6.png)

Stage1 (Norm 0.9752) Stage2 (Norm 0.1893) Stage3 (Norm 0.0765)

![Chart block](images/lee2023_compact3d_p8_b8.png)

![Chart block](images/lee2023_compact3d_p8_b9.png)

![Chart block](images/lee2023_compact3d_p8_b10.png)

Stage5 (Norm 0.0156) 80000

Stage6 (Norm 0.0074)

![Chart block](images/lee2023_compact3d_p8_b13.png)

(b) Learned codebook indices for rotation

![Chart block](images/lee2023_compact3d_p8_b15.png)

Figure 7. Effect of the proposed geometry codebook. We visualize (a) ellipsoids and rendered results and (b) learned codebook indices for rotation using Stump scene. ‘Norm’ denotes the average norm of all code vectors in each codebook (representing magnitude).

Table 4. Ablation study on the proposed contributions. ‘M’, ‘C’, ‘G’, and ‘H’ denote masking, color representation, geometry codebook, and half tensor for positions and opacities, respectively. ‘#Gauss’ means the number of Gaussians.

<table><tbody><tr><td colspan="2">Method \Dataset</td><td colspan="4">Playroom</td><td colspan="5">Bonsai</td></tr><tr><td>M C G</td><td>H PSNR</td><td>Train time</td><td>#Gauss</td><td>Storage</td><td>FPS</td><td>PSNR</td><td>Train time</td><td>#Gauss</td><td>Storage</td><td>FPS</td></tr><tr><td>3DGS</td><td>29.87</td><td>19m 22s</td><td>2.34 M</td><td>553 MB</td><td>154</td><td>32.16</td><td>19m 18s</td><td>1.25 M</td><td>295 MB</td><td>200</td></tr><tr><td>✓</td><td>29.91</td><td>17m 51s</td><td>967 K</td><td>228 MB</td><td>254</td><td>32.22</td><td>18m 50s</td><td>643 K</td><td>152 MB</td><td>247</td></tr><tr><td>✓ ✓</td><td>30.33</td><td>23m 56s</td><td>770 K</td><td>59 MB</td><td>210</td><td>32.08</td><td>23m 09s</td><td>592 K</td><td>51 MB</td><td>196</td></tr><tr><td>✓ ✓ ✓</td><td>30.33</td><td>24m 58s</td><td>761 K</td><td>44 MB</td><td>204</td><td>32.08</td><td>24m 06s</td><td>598 K</td><td>40 MB</td><td>198</td></tr><tr><td>✓ ✓ ✓</td><td>✓ 30.32</td><td>24m 35s</td><td>778 K</td><td>38 MB</td><td>206</td><td>32.08</td><td>24m 16s</td><td>601 K</td><td>35 MB</td><td>196</td></tr></tbody></table>

metric distortions that are hardly noticeable. Although these results prove the effectiveness of our method, we also explore the patterns of learned indices across each stage of R-VQ, shown in Fig. 7-(b). The initial stage exhibits an even distribution with a large magnitude of codes. As the stages progress, the magnitude of codes decreases, indicating that the residuals of each stage have been effectively trained to represent geometry.

Table 5. Avarge storage (MB) for each Gaussian attribute, evaluated on Mip-NeRF 360 dataset. f, 8b, H, and P mean floatingpoint, min-max quantization to 8-bit, Huffman encoding, and pruning parameters below 0.1, respectively.

<table><tr><td></td><td>Pos.</td><td>Opa.</td><td>Sca.</td><td>Rot.</td><td colspan="2">Col.</td><td>Tot.</td></tr><tr><td rowspan="2">3DGS</td><td colspan="6">32f</td><td rowspan="2">746</td></tr><tr><td>37.9</td><td>12.6</td><td>37.9</td><td>50.6</td><td colspan="2">606.9</td></tr><tr><td rowspan="2">Ours</td><td colspan="2">16f</td><td colspan="2">R-VQ</td><td>Hash(16f)</td><td>MLP(16f)</td><td rowspan="2">48.8</td></tr><tr><td>8.3</td><td>2.8</td><td>6.3</td><td>6.3</td><td>25.2</td><td>0.016</td></tr><tr><td rowspan="2">Ours +PP</td><td>16f</td><td>8b+H</td><td colspan="2">+H</td><td>+8b+P+H</td><td>MLP(16f)</td><td rowspan="2">29.1</td></tr><tr><td>8.3</td><td>1.2</td><td>5.9</td><td>6.2</td><td>7.4</td><td>0.016</td></tr></table>

Effect of post-processing. Tab. 5 describes the size of each

attribute with and without the application of post-processing techniques. While our end-to-end trainable framework demonstrates significant effectiveness, it requires relatively large storage for color representation. Nonetheless, as indicated in the table, this can be effectively reduced through simple post-processings.

## 5. Conclusion

We have proposed a compact 3D Gaussian representation for 3D scenes, reducing the number of Gaussian points without performance decrease through a novel volumebased masking. Furthermore, this work proposed combining the neural field and exploiting the learnable codebooks to represent Gaussian attributes compactly. In the extensive experiments, our approach demonstrated more than a tenfold reduction in storage and a marked increase in rendering speed while retaining the high-quality reconstruction compared to 3DGS. This result sets a new benchmark with high performance, fast training, compactness, and real-time rendering. Our framework thus stands as a comprehensive solution, paving the way for broader adoption and application in various fields requiring efficient and high-quality 3D scene representation.

8

<!-- page 9 of 14 -->

## References

[1] Kara-Ali Aliev, Artem Sevastopolsky, Maria Kolos, Dmitry Ulyanov, and Victor Lempitsky. Neural point-based graphics. In Computer Vision–ECCV 2020: 16th European Conference, Glasgow, UK, August 23–28, 2020, Proceedings, Part XXII 16, pages 696–712. Springer, 2020. 3

[2] Jonathan T. Barron, Ben Mildenhall, Matthew Tancik, Peter Hedman, Ricardo Martin-Brualla, and Pratul P. Srinivasan. Mip-nerf: A multiscale representation for anti-aliasing neural radiance fields. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 5855–5864, 2021. 1, 2

[3] Jonathan T. Barron, Ben Mildenhall, Dor Verbin, Pratul P. Srinivasan, and Peter Hedman. Mip-nerf 360: Unbounded anti-aliased neural radiance fields. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 5470–5479, 2022. 2, 5

[4] Jonathan T Barron, Ben Mildenhall, Dor Verbin, Pratul P Srinivasan, and Peter Hedman. Zip-nerf: Anti-aliased grid-based neural radiance fields. arXiv preprint arXiv:2304.06706, 2023. 3

[5] Yoshua Bengio, Nicholas Leonard, and Aaron Courville. ´ Estimating or propagating gradients through stochastic neurons for conditional computation. arXiv preprint arXiv:1308.3432, 2013. 4

[6] Eric R. Chan, Connor Z. Lin, Matthew A. Chan, Koki Nagano, Boxiao Pan, Shalini De Mello, Orazio Gallo, Leonidas J. Guibas, Jonathan Tremblay, Sameh Khamis, Tero Karras, and Gordon Wetzstein. Efficient geometryaware 3d generative adversarial networks. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 16123–16133, 2022. 3

[7] Anpei Chen, Zexiang Xu, Andreas Geiger, Jingyi Yu, and Hao Su. Tensorf: Tensorial radiance fields. In European Conference on Computer Vision, 2022. 1, 3

[8] Kangle Deng, Andrew Liu, Jun-Yan Zhu, and Deva Ramanan. Depth-supervised nerf: Fewer views and faster training for free. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 12882–12891, 2022. 1

[9] Jiemin Fang, Taoran Yi, Xinggang Wang, Lingxi Xie, Xiaopeng Zhang, Wenyu Liu, Matthias Nießner, and Qi Tian. Fast dynamic radiance fields with time-aware neural voxels. In SIGGRAPH Asia 2022 Conference Papers, 2022. 3

[10] Sara Fridovich-Keil, Alex Yu, Matthew Tancik, Qinhong Chen, Benjamin Recht, and Angjoo Kanazawa. Plenoxels: Radiance fields without neural networks. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 5501–5510, 2022. 1, 3

[11] Sara Fridovich-Keil, Giacomo Meanti, Frederik Rahbæk Warburg, Benjamin Recht, and Angjoo Kanazawa. K-planes: Explicit radiance fields in space, time, and appearance. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 12479–12488, 2023. 1, 3

[12] Chen Gao, Ayush Saraf, Johannes Kopf, and Jia-Bin Huang. Dynamic view synthesis from dynamic monocular video. In

Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), pages 5712–5721, 2021. 2

[13] Quankai Gao, Qiangeng Xu, Hao Su, Ulrich Neumann, and Zexiang Xu. Strivec: Sparse tri-vector radiance fields. In Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), pages 17569–17579, 2023. 3

[14] Robert Gray. Vector quantization. IEEE Assp Magazine, 1 (2):4–29, 1984. 5

[15] Kang Han and Wei Xiang. Multiscale tensor decomposition and rendering equation encoding for view synthesis. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 4232–4241, 2023. 3

[16] Peter Hedman, Julien Philip, True Price, Jan-Michael Frahm, George Drettakis, and Gabriel Brostow. Deep blending for free-viewpoint image-based rendering. ACM Transactions on Graphics (ToG), 37(6):1–15, 2018. 2, 6

[17] David A Huffman. A method for the construction of minimum-redundancy codes. Proceedings of the IRE, 40(9): 1098–1101, 1952. 6

[18] Bernhard Kerbl, Georgios Kopanas, Thomas Leimkuhler, ¨ and George Drettakis. 3d gaussian splatting for real-time radiance field rendering. ACM Transactions on Graphics (ToG), 42(4):1–14, 2023. 1, 2, 3

[19] Arno Knapitsch, Jaesik Park, Qian-Yi Zhou, and Vladlen Koltun. Tanks and temples: Benchmarking large-scale scene reconstruction. ACM Transactions on Graphics (ToG), 36 (4):1–13, 2017. 5

[20] Georgios Kopanas, Julien Philip, Thomas Leimkuhler, and ¨ George Drettakis. Point-based neural rendering with perview optimization. In Computer Graphics Forum, pages 29–43, 2021. 3

[21] Georgios Kopanas, Thomas Leimkuhler, Gilles Rainer, ¨ Clement Jambon, and George Drettakis. Neural point cata- ´ caustics for novel-view synthesis of reflections. ACM Transactions on Graphics (TOG), 41(6):1–15, 2022. 3

[22] Christoph Lassner and Michael Zollhofer. Pulsar: Efficient sphere-based neural rendering. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 1440–1449, 2021. 3

[23] Tianye Li, Mira Slavcheva, Michael Zollhofer, Simon Green, ¨ Christoph Lassner, Changil Kim, Tanner Schmidt, Steven Lovegrove, Michael Goesele, Richard Newcombe, and Zhaoyang Lv. Neural 3d video synthesis from multi-view video. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 5521–5531, 2022. 2

[24] Zhengqi Li, Simon Niklaus, Noah Snavely, and Oliver Wang. Neural scene flow fields for space-time view synthesis of dynamic scenes. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 6498–6508, 2021. 2

[25] Jia-Wei Liu, Yan-Pei Cao, Weijia Mao, Wenqiao Zhang, David Junhao Zhang, Jussi Keppo, Ying Shan, Xiaohu Qie, and Mike Zheng Shou. Devrf: Fast deformable voxel radiance fields for dynamic scenes. Advances in Neural Information Processing Systems, 35:36762–36775, 2022. 3

[26] Lingjie Liu, Jiatao Gu, Kyaw Zaw Lin, Tat-Seng Chua, and Christian Theobalt. Neural sparse voxel fields. Advances

9

<!-- page 10 of 14 -->

in Neural Information Processing Systems, pages 15651–15663, 2020. 3

[27] Moustafa Meshry, Dan B. Goldman, Sameh Khamis, Hugues Hoppe, Rohit Pandey, Noah Snavely, and Ricardo Martin-Brualla. Neural rerendering in the wild. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2019. 3

[28] Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, and Ren Ng. Nerf: Representing scenes as neural radiance fields for view synthesis. In European Conference on Computer Vision, page 405–421, 2020. 1, 2, 6

[29] Ben Mildenhall, Peter Hedman, Ricardo Martin-Brualla, Pratul P. Srinivasan, and Jonathan T. Barron. Nerf in the dark: High dynamic range view synthesis from noisy raw images. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 16190–16199, 2022. 2

[30] Thomas Muller, Alex Evans, Christoph Schied, and Alexan- ¨ der Keller. Instant neural graphics primitives with a multiresolution hash encoding. ACM Trans. Graph., 41(4), 2022. 1, 2, 3, 5

[31] Seungtae Nam, Daniel Rho, Jong Hwan Ko, and Eunbyung Park. Mip-grid: Anti-aliased grid representations for neural radiance fields. In Thirty-seventh Conference on Neural Information Processing Systems, 2023. 3

[32] Michael Niemeyer, Jonathan T Barron, Ben Mildenhall, Mehdi SM Sajjadi, Andreas Geiger, and Noha Radwan. Regnerf: Regularizing neural radiance fields for view synthesis from sparse inputs. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 5480–5490, 2022. 2

[33] Albert Pumarola, Enric Corona, Gerard Pons-Moll, and Francesc Moreno-Noguer. D-nerf: Neural radiance fields for dynamic scenes. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 10318–10327, 2021. 2

[34] Christian Reiser, Songyou Peng, Yiyi Liao, and Andreas Geiger. Kilonerf: Speeding up neural radiance fields with thousands of tiny mlps. In Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), pages 14335–14345, 2021. 1

[35] Daniel Rho, Byeonghyeon Lee, Seungtae Nam, Joo Chan Lee, Jong Hwan Ko, and Eunbyung Park. Masked wavelet representation for compact neural radiance fields. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 20680–20690, 2023. 1, 3

[36] Barbara Roessle, Jonathan T. Barron, Ben Mildenhall, Pratul P. Srinivasan, and Matthias Nießner. Dense depth priors for neural radiance fields from sparse input views. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 12892–12901, 2022. 2

[37] Johannes L. Schonberger and Jan-Michael Frahm. Structurefrom-motion revisited. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016. 3

[38] Seungjoo Shin and Jaesik Park. Binary radiance fields. In Thirty-seventh Conference on Neural Information Processing Systems, 2023. 3

[39] Cheng Sun, Min Sun, and Hwann-Tzong Chen. Direct voxel grid optimization: Super-fast convergence for radiance fields reconstruction. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 5459–5469, 2022. 3

[40] Towaki Takikawa, Alex Evans, Jonathan Tremblay, Thomas Muller, Morgan McGuire, Alec Jacobson, and Sanja Fidler. ¨ Variable bitrate neural fields. In ACM SIGGRAPH 2022 Conference Proceedings, 2022. 1, 3

[41] Matthew Tancik, Vincent Casser, Xinchen Yan, Sabeek Pradhan, Ben Mildenhall, Pratul P. Srinivasan, Jonathan T. Barron, and Henrik Kretzschmar. Block-nerf: Scalable large scene neural view synthesis. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 8248–8258, 2022. 2

[42] Qianqian Wang, Zhicheng Wang, Kyle Genova, Pratul P. Srinivasan, Howard Zhou, Jonathan T. Barron, Ricardo Martin-Brualla, Noah Snavely, and Thomas Funkhouser. Ibrnet: Learning multi-view image-based rendering. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 4690–4699, 2021. 2

[43] Olivia Wiles, Georgia Gkioxari, Richard Szeliski, and Justin Johnson. Synsin: End-to-end view synthesis from a single image. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2020. 3

[44] Dejia Xu, Yifan Jiang, Peihao Wang, Zhiwen Fan, Humphrey Shi, and Zhangyang Wang. Sinnerf: Training neural radiance fields on complex scenes from a single image. In European Conference on Computer Vision, pages 736–753, 2022. 2

[45] Qiangeng Xu, Zexiang Xu, Julien Philip, Sai Bi, Zhixin Shu, Kalyan Sunkavalli, and Ulrich Neumann. Point-nerf: Point-based neural radiance fields. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 5438–5448, 2022. 3

[46] Wang Yifan, Felice Serena, Shihao Wu, Cengiz Oztireli, ¨ and Olga Sorkine-Hornung. Differentiable surface splatting for point-based geometry processing. ACM Transactions on Graphics (TOG), 38(6):1–14, 2019. 3

[47] Alex Yu, Vickie Ye, Matthew Tancik, and Angjoo Kanazawa. pixelnerf: Neural radiance fields from one or few images. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 4578–4587, 2021. 2

[48] Neil Zeghidour, Alejandro Luebs, Ahmed Omran, Jan Skoglund, and Marco Tagliasacchi. Soundstream: An endto-end neural audio codec. IEEE/ACM Transactions on Audio, Speech, and Language Processing, 30:495–507, 2021. 5

[49] Qiang Zhang, Seung-Hwan Baek, Szymon Rusinkiewicz, and Felix Heide. Differentiable point-based radiance fields for efficient view synthesis. In SIGGRAPH Asia 2022 Conference Papers, pages 1–12, 2022. 3

10

<!-- page 11 of 14 -->

## Appendix

## 6. Implementation Detail

We retained all hyper-parameters of 3DGS and trained models during 30K iterations, and we set the codebook size C and the number of stages L of R-VQ to 64 and 6, respectively. The neural field for view-dependent color uses hash grids with 2-channel features across 16 different resolutions (16 to 4096) and a following 2-layer 64-channel MLP. Due to the different characteristics between the real and synthetic scenes, we adjusted the maximum hash map size and the hyper-parameters for learning the neural field and the mask. For the real scenes, we set the max size of hash maps to $2 ^ { 1 9 }$ , the control factor for the number of Gaussians $\lambda _ { m }$ to $5 e ^ { - 4 }$ , and the learning rate of the mask parameter and the neural fields to $1 e ^ { - 2 }$ . The learning rate of the neural fields is decreased at 5K, 15K, and 25K iterations by multiplying a factor of 0.33. For the synthetic scenes, the maximum hash map size and the control factor $\lambda _ { m }$ were set to $2 ^ { 1 6 }$ and $4 e ^ { - 3 }$ , respectively. The learning rate of the mask parameter and the neural fields were set to $1 e ^ { - 3 }$ , where the learning rate of the neural fields was reduced at 25K iteration with a factor of 0.33.

## 7. Fast inference pipeline

The main paper’s analysis shows that our method extends the overall training time slightly more than 3DGS, owing to the time for iterating neural fields and for R-VQ search. However, our approach effectively reduces rendering time for several reasons. First, the proposed masking strategy significantly effectively reduces the number of Gaussians, as demonstrated in our results, leading to reduced training and rendering times. Second, by precomputing grid features at the testing phase, we minimize the operational time of the neural field. Since these grid features, which precede the subsequent MLP input, are not dependent on the view direction itself, they can be prepared in advance of testing. This allows our method to simply process a small MLP for generating view-dependent colors during testing. Third, in the testing phase, the time spent searching for suitable geometry is eliminated. In a manner similar to precomputing grid features, we can index the closest codes from multi-stage codebooks before testing. These strategies collectively enable us to achieve a notably faster rendering speed.

## 8. Additional ablation study

## 8.1. Rate-distortion curve based on each proposal

In addition to the ablation study in the main paper, we conduct an in-depth analysis on the impact of our contributions: volume-based masking, compact color representation, and geometry codebook. As illustrated in Fig. 8, we start with

the standard configuration of our approach and adjust the compactness level of the three proposals. We control $\lambda _ { m } ,$ max hashmap size, and the number of R-VQ stages, respectively, by doubling each hyper-parameter. As the performance for the different scenes varies due to their diverse characteristics, we choose three distinct scenes where our approach increases, retains, and decreases visual quality while achieving over 10× compression.

Although the proposed geometry codebook effectively reduces the storage as validated in the main paper, it shows poor performance when the diversity of codebooks is extremely limited. In contrast, our neural field-based color representation demonstrates remarkable robustness even in a low-rate condition across the various scenes, indicating that scaling down the neural field is the best option in environments with severe resource limitations.

These results show that the storage need of our method can be halved with minimal performance loss, and our default configuration is a well-rounded choice for a wide range of scenes.

<table><tr><td>Opacity</td><td>Scale</td><td> $\lambda_m$ </td><td>#Gaussian</td><td>PSNR</td></tr><tr><td rowspan="2">✓</td><td></td><td>0.0005</td><td>311786</td><td>31.50</td></tr><tr><td></td><td>0.0001</td><td>629837</td><td>31.86</td></tr><tr><td rowspan="2"></td><td>✓</td><td>0.0005</td><td>508762</td><td>31.89</td></tr><tr><td></td><td>0.0003</td><td>596449</td><td>31.97</td></tr><tr><td>✓</td><td>✓</td><td>0.0005</td><td>601048</td><td>32.08</td></tr></table>

Table 6. Ablation study on the proposed volume-based masking. #Gaussian denotes the number of Gaussians

## 8.2. Volume-based masking

We have proposed the learnable masking of Gaussians based on their volume as well as transparency. As shown in Tab. 6, masking based on only Gaussian volume outperforms the method that only considers Gaussian opacity. Moreover, the best results are achieved when both volume and transparency are taken into account for masking.

Table 7. Ablation study on represented components by I-NGP.

<table><tr><td colspan="4">I-NGP representation</td><td rowspan="2">PSNR</td><td rowspan="2">Train time</td><td rowspan="2">#Gaussians</td></tr><tr><td>Opa.</td><td>Sca.</td><td>Rot.</td><td>Col.</td></tr><tr><td></td><td colspan="3">3DGS</td><td>32.2</td><td>19:21</td><td>1245 K</td></tr><tr><td></td><td></td><td></td><td>✓</td><td>32.3</td><td>24:42</td><td>1178 K</td></tr><tr><td>✓</td><td></td><td></td><td>✓</td><td>9.3</td><td>29:55</td><td>666 K</td></tr><tr><td></td><td>✓</td><td></td><td>✓</td><td>9.3</td><td>29:55</td><td>559 K</td></tr><tr><td></td><td></td><td>✓</td><td>✓</td><td>25.9</td><td>27.37</td><td>1692 K</td></tr></table>

11

<!-- page 12 of 14 -->

![Chart block](images/lee2023_compact3d_p12_b1.png)

Figure 8. Rate-distortion curves evaluated on diverse scenes. Starting with our default model, we methodically adjust the compactness level of each proposal to evaluate their individual contributions.

<table><tr><td>Scene</td><td colspan="3">bicycle</td><td colspan="3">bonsai</td><td colspan="3">drjohnson</td><td colspan="3">playroom</td></tr><tr><td>Method</td><td>PSNR</td><td>Storage</td><td>Mem.</td><td>PSNR</td><td>Storage</td><td>Mem.</td><td>PSNR</td><td>Storage</td><td>Mem.</td><td>PSNR</td><td>Storage</td><td>Mem.</td></tr><tr><td>3DGS</td><td>25.08</td><td>1.4 GB</td><td>9.4 GB</td><td>32.16</td><td>295 MB</td><td>8.7 GB</td><td>29.06</td><td>774 MB</td><td>7.5 GB</td><td>29.87</td><td>553 MB</td><td>6.4 GB</td></tr><tr><td>Ours</td><td>24.77</td><td>63 MB</td><td>7.6 GB</td><td>32.08</td><td>35 MB</td><td>8.3 GB</td><td>29.26</td><td>48 MB</td><td>6.5 GB</td><td>30.32</td><td>39 MB</td><td>5.6 GB</td></tr></table>

Table 8. Evaluation of GPU memory requirements for our method compared to 3DGS. ’Mem’ indicates the GPU memory requirements.

360 (Tab. 9), Tanks&Temples (Tab. 10), Deep Blending (Tab. 10), and NeRF synthetic (Tab. 11) datasets.

## 8.3. Usage of I-NGP and R-VQ.

Neural fields can represent continuous signals efficiently, whereas VQ works well for repetitive components. In a 3D scene, near Gaussians can be expected to share similar color but are not guaranteed to have a similar shape, rather, similar shapes can be frequently found in the entire scene. Therefore, I-NGP is not successfully trained to represent other attributes except for color, as demonstrated in Tab. 7. Given this intuition, we have proposed an effective representation for each component.

## 9. Inference memory

Throughout the main paper, we analyze the effectiveness of our method in terms of the balance between the visual quality, storage requirement, and rendering speed. Our approach effectively reduces not only storage needs but also memory requirements, both of which are key aspects of efficiency. Tab. 8 depicts the GPU memory requirement for inference with the visual quality and storage need, evaluated on diverse scenes. Our method consistently reduces the GPU memory requirements by a safe margin, demonstrating its efficient usage of computing resources.

## 10. Per-Scene Results

We evaluated the performance on various datasets for novel view synthesis. We provide per-scene results for Mip-NeRF

12

<!-- page 13 of 14 -->

<table><tr><td></td><td>Scene</td><td>bicycle</td><td>flowers</td><td>garden</td><td>stump</td><td>tree hill</td><td>room</td><td>counter</td><td>kitchen</td><td>bonsai</td><td>Avg.</td></tr><tr><td rowspan="7">3DGS</td><td>PSNR</td><td>25.10</td><td>21.33</td><td>27.25</td><td>26.66</td><td>22.53</td><td>31.50</td><td>29.11</td><td>31.53</td><td>32.16</td><td>27.46</td></tr><tr><td>SSIM</td><td>0.747</td><td>0.588</td><td>0.856</td><td>0.769</td><td>0.635</td><td>0.925</td><td>0.914</td><td>0.932</td><td>0.946</td><td>0.812</td></tr><tr><td>LPIPS</td><td>0.244</td><td>0.361</td><td>0.122</td><td>0.243</td><td>0.346</td><td>0.198</td><td>0.184</td><td>0.117</td><td>0.181</td><td>0.222</td></tr><tr><td>Train (mm:ss)</td><td>34:04</td><td>25:33</td><td>33:46</td><td>27:05</td><td>24:51</td><td>22:55</td><td>22:42</td><td>26:08</td><td>19:18</td><td>24:07</td></tr><tr><td>#Gaussians</td><td>5,723,640</td><td>3,414,994</td><td>5,641,235</td><td>4,549,202</td><td>3,470,681</td><td>1,483,653</td><td>1,171,684</td><td>1,744,761</td><td>1,250,329</td><td>3,161,131</td></tr><tr><td>Storage (MB)</td><td>1350.78</td><td>805.94</td><td>1331.33</td><td>1073.60</td><td>819.08</td><td>350.14</td><td>276.52</td><td>411.76</td><td>295.08</td><td>746.03</td></tr><tr><td>FPS</td><td>63.81</td><td>132.03</td><td>77.19</td><td>108.81</td><td>100.92</td><td>132.51</td><td>146.40</td><td>122.07</td><td>199.86</td><td>120.40</td></tr><tr><td rowspan="7">Ours</td><td>PSNR</td><td>24.77</td><td>20.89</td><td>26.81</td><td>26.46</td><td>22.65</td><td>30.88</td><td>28.71</td><td>30.48</td><td>32.08</td><td>27.08</td></tr><tr><td>SSIM</td><td>0.723</td><td>0.556</td><td>0.832</td><td>0.757</td><td>0.638</td><td>0.919</td><td>0.902</td><td>0.919</td><td>0.939</td><td>0.798</td></tr><tr><td>LPIPS</td><td>0.286</td><td>0.399</td><td>0.161</td><td>0.278</td><td>0.363</td><td>0.209</td><td>0.205</td><td>0.131</td><td>0.193</td><td>0.247</td></tr><tr><td>Train (mm:ss)</td><td>42:36</td><td>32:37</td><td>45:36</td><td>33:43</td><td>34:08</td><td>24:18</td><td>27:41</td><td>32:59</td><td>24:16</td><td>33:06</td></tr><tr><td>#Gaussians</td><td>2,221,689</td><td>1,525,598</td><td>2,209,609</td><td>1,732,089</td><td>2,006,446</td><td>529,136</td><td>536,672</td><td>1,131,168</td><td>601,048</td><td>1,388,162</td></tr><tr><td>Storage (MB)</td><td>62.99</td><td>51.15</td><td>62.78</td><td>54.66</td><td>59.33</td><td>34.21</td><td>34.34</td><td>44.45</td><td>35.44</td><td>48.82</td></tr><tr><td>FPS</td><td>76.41</td><td>142.41</td><td>89.49</td><td>120.96</td><td>110.28</td><td>183.03</td><td>119.52</td><td>114.24</td><td>196.08</td><td>128.05</td></tr><tr><td rowspan="4">Ours+PP</td><td>PSNR</td><td>24.73</td><td>20.89</td><td>26.72</td><td>26.31</td><td>22.67</td><td>30.88</td><td>28.63</td><td>30.48</td><td>31.98</td><td>27.03</td></tr><tr><td>SSIM</td><td>0.722</td><td>0.554</td><td>0.831</td><td>0.754</td><td>0.637</td><td>0.918</td><td>0.901</td><td>0.919</td><td>0.937</td><td>0.797</td></tr><tr><td>LPIPS</td><td>0.284</td><td>0.399</td><td>0.158</td><td>0.280</td><td>0.363</td><td>0.209</td><td>0.206</td><td>0.130</td><td>0.193</td><td>0.247</td></tr><tr><td>Storage (MB)</td><td>42.42</td><td>32.05</td><td>43.26</td><td>33.83</td><td>39.08</td><td>15.01</td><td>15.22</td><td>24.39</td><td>16.40</td><td>29.07</td></tr></table>

Table 9. Per-scene results evaluated on Mip-NeRF 360 dataset.

<table><tr><td colspan="2">Dataset</td><td colspan="3">Tanks&amp;Temples</td><td colspan="3">Deep Blending</td></tr><tr><td></td><td>Scene</td><td>train</td><td>truck</td><td>Avg.</td><td>drjohnson</td><td>playroom</td><td>Avg.</td></tr><tr><td rowspan="7">3DGS</td><td>PSNR</td><td>22.07</td><td>25.35</td><td>23.71</td><td>29.06</td><td>29.87</td><td>29.46</td></tr><tr><td>SSIM</td><td>0.812</td><td>0.878</td><td>0.845</td><td>0.899</td><td>0.901</td><td>0.900</td></tr><tr><td>LPIPS</td><td>0.208</td><td>0.148</td><td>0.178</td><td>0.247</td><td>0.247</td><td>0.247</td></tr><tr><td>Train (mm:ss)</td><td>12:18</td><td>15:24</td><td>13:51</td><td>24:22</td><td>19:22</td><td>21:52</td></tr><tr><td>#Gaussians</td><td>1,084,001</td><td>2,579,252</td><td>1,831,627</td><td>3,278,027</td><td>2,343,368</td><td>2,810,698</td></tr><tr><td>Storage (MB)</td><td>255.82</td><td>608.70</td><td>432.26</td><td>773.61</td><td>553.03</td><td>663.32</td></tr><tr><td>FPS</td><td>174.42</td><td>145.14</td><td>159.78</td><td>110.46</td><td>154.47</td><td>132.47</td></tr><tr><td rowspan="7">Ours</td><td>PSNR</td><td>21.56</td><td>25.07</td><td>23.32</td><td>29.26</td><td>30.32</td><td>29.79</td></tr><tr><td>SSIM</td><td>0.792</td><td>0.871</td><td>0.831</td><td>0.900</td><td>0.902</td><td>0.901</td></tr><tr><td>LPIPS</td><td>0.240</td><td>0.163</td><td>0.201</td><td>0.258</td><td>0.258</td><td>0.258</td></tr><tr><td>Train (mm:ss)</td><td>16:03</td><td>20:36</td><td>18:20</td><td>30:31</td><td>24:35</td><td>27:33</td></tr><tr><td>#Gaussians</td><td>710,434</td><td>962,158</td><td>836,296</td><td>1,339,005</td><td>778,353</td><td>1,058,679</td></tr><tr><td>Storage (MB)</td><td>37.29</td><td>41.57</td><td>39.43</td><td>47.98</td><td>38.45</td><td>43.21</td></tr><tr><td>FPS</td><td>185.91</td><td>184.83</td><td>185.37</td><td>155.37</td><td>205.83</td><td>180.60</td></tr><tr><td rowspan="4">Ours+PP</td><td>PSNR</td><td>21.62</td><td>25.02</td><td>23.32</td><td>29.16</td><td>30.30</td><td>29.73</td></tr><tr><td>SSIM</td><td>0.792</td><td>0.870</td><td>0.831</td><td>0.899</td><td>0.900</td><td>0.900</td></tr><tr><td>LPIPS</td><td>0.240</td><td>0.163</td><td>0.202</td><td>0.257</td><td>0.259</td><td>0.258</td></tr><tr><td>Storage (MB)</td><td>19.07</td><td>22.64</td><td>20.86</td><td>28.43</td><td>19.21</td><td>23.82</td></tr></table>

Table 10. Per-scene results evaluated on Tank&Temples and Deep Blending.

13

<!-- page 14 of 14 -->

<table><tr><td></td><td>Scene</td><td>chair</td><td>drums</td><td>ficus</td><td>hotdog</td><td>lego</td><td>materials</td><td>mic</td><td>ship</td><td>Avg.</td></tr><tr><td rowspan="7">Ours</td><td>PSNR</td><td>34.91</td><td>26.18</td><td>35.44</td><td>37.38</td><td>35.48</td><td>29.97</td><td>35.81</td><td>31.51</td><td>33.33</td></tr><tr><td>SSIM</td><td>0.986</td><td>0.953</td><td>0.987</td><td>0.984</td><td>0.981</td><td>0.958</td><td>0.991</td><td>0.905</td><td>0.968</td></tr><tr><td>LPIPS</td><td>0.013</td><td>0.041</td><td>0.013</td><td>0.023</td><td>0.018</td><td>0.042</td><td>0.008</td><td>0.113</td><td>0.034</td></tr><tr><td>Train (m:ss)</td><td>9:19</td><td>8:55</td><td>6:41</td><td>8:20</td><td>8:23</td><td>6:53</td><td>7:12</td><td>8:46</td><td>8:04</td></tr><tr><td>#Gaussians</td><td>153,570</td><td>178,615</td><td>83,910</td><td>64,194</td><td>171,826</td><td>107,188</td><td>56,015</td><td>148,442</td><td>120,470</td></tr><tr><td>Storage (MB)</td><td>6.11</td><td>6.54</td><td>4.93</td><td>4.59</td><td>6.42</td><td>5.32</td><td>4.44</td><td>6.02</td><td>5.55</td></tr><tr><td>FPS</td><td>512.10</td><td>427.56</td><td>706.71</td><td>719.85</td><td>402.15</td><td>638.01</td><td>674.34</td><td>282.72</td><td>545.43</td></tr><tr><td rowspan="4">Ours+PP</td><td>PSNR</td><td>34.58</td><td>26.01</td><td>35.06</td><td>36.71</td><td>34.96</td><td>29.04</td><td>35.57</td><td>31.06</td><td>32.88</td></tr><tr><td>SSIM</td><td>0.985</td><td>0.951</td><td>0.987</td><td>0.983</td><td>0.979</td><td>0.954</td><td>0.991</td><td>0.903</td><td>0.968</td></tr><tr><td>LPIPS</td><td>0.013</td><td>0.042</td><td>0.013</td><td>0.023</td><td>0.020</td><td>0.043</td><td>0.008</td><td>0.115</td><td>0.034</td></tr><tr><td>Storage (MB)</td><td>3.09</td><td>3.56</td><td>2.11</td><td>1.75</td><td>3.45</td><td>2.51</td><td>1.59</td><td>3.28</td><td>2.67</td></tr></table>

Table 11. Per-scene results evaluated on NeRF-synthetic dataset.

14