<!-- page 1 of 25 -->

1

arXiv:2402.13255v3 [cs.CV] 27 Mar 2025

# How NeRFs and 3D Gaussian Splatting are Reshaping SLAM: a Survey

Fabio Tosi<sup>1</sup>

Youmin Zhang<sup>1,2</sup>

Stefano Mattoccia<sup>1</sup>

Ziren Gong<sup>1</sup>

Martin R. Oswald<sup>3,4</sup>

Erik Sandstrom¨ <sup>3</sup>

Matteo Poggi<sup>1</sup>

<sup>1</sup>University of Bologna, Italy <sup>2</sup>[Rock Universe, China](https://twitter.com/hi_rockuniverse) <sup>3</sup>ETH Zurich, Switzerland <sup>4</sup>University of Amsterdam, Netherlands

![Image block](images/tosi2024_nerf-gs-slam-survey_p1_b12.png)

Fig. 1: Timeline SLAM Evolution. This timeline shows the evolution from hand-crafted to deep learning SLAM, with key surveys marking both periods. A significant shift occurs in 2021 with iMap [1], introducing radiance-field-based approaches. Circle sizes on the right indicate yearly publication volumes, with 2024’s outer circle projecting increased interest in NeRF and 3DGS-based SLAM.

**Abstract—Over the past two decades, research in the field of Simultaneous Localization and Mapping (SLAM) has undergone a significant evolution, highlighting its critical role in enabling autonomous exploration of unknown environments. This evolution ranges from hand-crafted methods, through the era of deep learning, to more recent developments focused on Neural Radiance Fields (NeRFs) and 3D Gaussian Splatting (3DGS) representations. Recognizing the growing body of research and the absence of a comprehensive survey on the topic, this paper aims to provide the first comprehensive overview of SLAM progress through the lens of the latest advancements in radiance fields. It sheds light on the background, evolutionary path, inherent strengths and limitations, and serves as a fundamental reference to highlight the dynamic progress and specific challenges.**

**Index Terms—SLAM, Deep Learning, Neural Radiance Field, NeRF, 3D Gaussian Splatting**

## I. INTRODUCTION

Simultaneous Localization and Mapping (SLAM) is a fundamental concept in the fields of computer vision and robotics. It addresses the challenge of enabling machines to autonomously navigate and incrementally build a map of unknown environments (mapping) while simultaneously determining their own position and orientation (tracking).

Originally conceived for robotics and automated systems, the demand for SLAM has expanded into a variety of domains, including augmented reality (AR), visual surveillance, medical applications, and beyond. To meet these needs, researchers have focused on developing methods for machines to autonomously construct increasingly highly accurate scene representations, influenced by the convergence of robotics, computer vision, sensor technology, and the recent progress in artificial intelligence (AI).

Typically, SLAM techniques rely on the integration of diverse sensing technologies, including cameras, laser range instruments, inertial devices, and GPS, to effectively accomplish the task at hand. Initially, sonar and LiDAR sensors were prevalent choices due to their high precision, despite being cumbersome and costly. Subsequently, the focus shifted towards visual sensors such as monocular/stereo or RGB-D cameras, which offer advantages in terms of portability, cost-effectiveness, and deployment ease. These visual sensors enable Visual Simultaneous Localization and Mapping (VSLAM) systems to capture more detailed environmental information, improve precise positioning in complex scenarios, and deliver versatile and accessible solutions.

As we outline the ideal SLAM criteria, several key aspects emerge. These include global consistency, robust camera tracking, accurate surface modeling, real-time performance, accurate prediction in unobserved regions, scalability to large scenes, and robustness to noisy data.

Over the years, SLAM methodologies have evolved significantly to meet these specific requirements. At the outset, hand crafted algorithms [2], [10], [25]–[27] demonstrated remarkable real-time performance and scalability. However, they face challenges in strong illumination, radiometric changes, and dynamic/poorly textured environments, resulting in unsatisfactory performance. The incorporation of advanced techniques, employing deep learning methodologies [3], [4], [11], [28], became crucial in improving the precision and reliability of localization and mapping. This integration takes advantage of the robust feature extraction capabilities of deep neural networks, which are particularly effective in challenging conditions. Nonetheless, their dependence on extensive training

<!-- page 2 of 25 -->

2

data and accurate ground truth annotations limits their ability to generalize to unseen scenarios. Furthermore, both handcrafted and deep learning-based methods encounter limitations related to using discrete surface representations (point/surfel clouds [29], [30], voxel hashing [31], voxel-grids [2], octrees [32]), which lead to challenges such as sparse 3D modeling, limited spatial resolution and distortion during the reconstruction process. Additionally, accurately estimating geometries in unobserved areas remains an ongoing hurdle.

Driven by the need to overcome existing obstacles and influenced by the success of recent Neural Radiance Fields (NeRF) [33] and 3D Gaussian Splatting (3DGS) [34] representations in novel view synthesis, along with the introduction of learned representations for modeling geometric fields – extensively discussed in [35] – a revolution is reshaping SLAM. Leveraging insights from contemporary research, these approaches offer several advantages over previous methods, including continuous surface modeling, reduced memory requirements, improved noise/outlier handling, and enhanced hole filling and scene inpainting capabilities for occluded or sparse observations. In addition, they have the potential to produce denser and more compact maps that can be reconstructed as 3D meshes at arbitrary resolutions. However, at this early stage, each technique presents both strengths and specific limitations. As such, the field is constantly evolving and requires ongoing research and innovation to make further progress.

In response to the lack of SLAM surveys focusing on the latest developments and the growing interest in research exploring this paradigm <sup>1</sup>, this paper conducts a thorough review of contemporary radiance field-inspired SLAM techniques. Specifically, we undertake an in-depth investigation of 80 SLAM systems that have been published in the past three years<sup>2</sup>, reflecting the rapid pace of progress in the field. This evolution is illustrated in Figure 1, which provides a visual timeline of the current state of SLAM advancements. Our aim is to fill the existing gap in the survey literature by closely examining and analyzing these cutting-edge techniques, and by highlighting the rapid emergence of innovative solutions aimed at improving their inherent weaknesses. Through a detailed exploration, we intend to categorize these methods, trace their progression, and offer insights that are tailored to the specific requirements of SLAM. By serving as a valuable resource for both novices and experts, we believe that this survey represents a significant cornerstone for the future of this paradigm.

The upcoming sections are organized as follows:

• Section II reviews existing SLAM surveys (II-A), covers basics of radiance-field rendering theory (II-B), introduces key datasets and benchmarks (II-C), and describes main evaluation metrics used in this context (II-D).

• Section III is the core of our paper, focusing on key NeRF and 3DGS-inspired SLAM techniques and our structured taxonomy for organizing these advancements.

• Section IV presents quantitative results evaluating SLAM frameworks in tracking, mapping, rendering, and performance analysis across diverse scenarios.

• Sections V and VI focus on limitations, future research directions, and summarize the survey comprehensively.

## II. BACKGROUND

## A. Existing SLAM Surveys

SLAM has seen significant growth, resulting in a variety range of comprehensive survey papers. In the early stages, Durrant-Whyte and Bailey introduced the probabilistic nature of the SLAM problem and highlighted key methods, alongside implementations [36], [37]. Grisetti et al. [19] further delved into the graph-based SLAM problem, emphasizing its role in navigating in unknown environments. In the field of visual SLAM, Yousif [20] provided an overview of localization and mapping techniques, incorporating basic methods and advances in visual odometry and SLAM. The advent of multiple-robot systems led to Saeedi and Clark [38] reviewing state-of-the-art approaches, with a focus on multiple-robot SLAM challenges and solutions. Cadena et al. [21] presented a comprehensive reflection on the history, robustness, and new frontiers of SLAM, addressing its evolving significance across real-world applications. Taketomi et al. [22] categorized and summarized VSLAM algorithms from 2010 to 2016, classifying them based on feature-based, direct, and RGB-D camera approaches. Saputra et al. [39] addressed the challenge of dynamic environments in VSLAM and Structure from Motion (SfM), presenting a taxonomy of techniques for reconstruction, segmentation and tracking of dynamic objects. The integration of deep learning with SLAM was meticulously examined by Duan et al. [23], highlighting the progression of deep learning methods in visual SLAM. In sensor-specific contexts, Zaffar et al. [40] discussed sensors employed in SLAM, while Yang et al. [41] and Zhao et al. [42] explored the applications of LiDAR and underwater SLAM, respectively. In recent years, deep learning-based VSLAM has gained considerable attention, extensively covered in [43]–[46]. Notably, [47] delves into recent advancements in RGB-D scene reconstruction. Ongoing developments in SLAM are explored in surveys like [48], focusing on active SLAM strategies for precise mapping through motion planning.

Despite the extensive body of work describing SLAM systems covering traditional and deep learning-based approaches, there is no comprehensive exploration of the advancing frontiers in SLAM techniques rooted in the latest progress in radiance fields. Nonetheless, within the existing literature of our interest, notably in influential works like [49], two principal SLAM strategies emerge as the frame-to-frame and frame-to-model tracking approaches, which are influencing the development of new methodologies based on radiance fields. Typically, the former strategy is used in real-time systems, often involving further optimization of the estimated poses through loop-closure (LC) or global Bundle Adjustment (BA), whereas the latter estimates camera poses from the reconstructed 3D model, often avoiding further optimizations, yet resulting less scalable to large scenes. These strategies, often associated with the concepts of decoupled and coupled methods in recent SLAM research, serve as the foundation for the methodologies we will explore. Decoupled methods

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>1</sup>[https://github.com/DoongLi/awesome-Implicit-NeRF-SLAM](https://github.com/DoongLi/awesome-Implicit-NeRF-SLAM)</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>2</sup>with a cut-off date on ECCV/IROS 2024</span></small>

<!-- page 3 of 25 -->

3

![Image block](images/tosi2024_nerf-gs-slam-survey_p3_b2.png)

ig. 2: Illustration comparing implicit, explicit and hybrid scene representation methods. a) Implicit utilizes a neural networkd h b id  t ti th d . ) I li it tili  l t kFig. 2: Illustration comparing implicit, explicit and hybrid scene representation methods. a) Fig. 2: Comparison of Scene Representations: Implicit, Explicit, and Hybrid. From left to right: Implicit uses a neural o approximate a radiance field, while b) Explicit models conduct volume rendering directly on learned spatial features –it models conduct volume rendering directly on learned spatial features –o approx ma e a ra ance e , w e ) xp c mo e s con uc vo ume ren er ng renetwork to approximate a radiance field, explicit conducts volume rendering directly on learned spatial feature (voxels, hash voxels, hash grids, neural points, and more – excluding neural components. Finally, c) hybrid models incorporate learnedxcluding neural components. Finally, c) hybrid models incorporate learned,  g ,  p ,   – g  p . y, ) ygrids, etc.), excluding neural components, and hybrid incorporates learned spatial features ψ with neural networks. Both hybrid pa a ea ures w neura ne wor s. o y r an exp c approac es ena e acce era e ra n ng an renbrid and explicit approaches enable accelerated training and rendering butd d ddi i l  . SWAP FIG RESand explicit approaches enable accelerated training and rendering but require additional memory resources.

employ separate frameworks for tracking and mapping, treate represented implicitly, by encoding it entirely within the t p ping them as independent tasks, while coupled methods utilize weights of a neural network or explicitly, by mapping lightlati li ht 1a unified representation for both tasks, allowing for a more within a discrete spatids. Explicit Thintegrated approach.

## hile implicitB. Progress in Radiance Field Theory

entially higher rendering computational needs. Hybridg Ni−1The term radiance field refers to a representation that pproaches take advantage of both by using a combinationr  αi ici, i  exp σof explicitly storeddescribes the behavior and distribution of light within a threef explicitly stored local latent features and shallow neuralll l networks, using vdimensional space. It encapsulates how light interacts with, g     p ll where, δ<sub>i</sub> denotes the interval between consehashing grids [51],surfaces, materials, and the surrounding environment. It can g g [ ], [ ], -   g anvoxel grids ples t<sub>i</sub> and t<sub>i+1</sub>. The parameters (σ<sub>i</sub>, ci) indicate[ ], oc ree no es [be represented implicitly, by encoding it entirely within the tivgrids [55], or    p p  g   weights of a neural network or explicitly, by mapping light opstrates thesey. y, i  i i within a discrete spatial structure such as voxel grids. Explicit nfluenced advances in SLAM methodologies, particularly significantly      through the use ofrepresentations typically offer faster access but require more hrough the use of implicit models such as NeRF and more a particularlyrecent explicit methmemory and have resolution constraints, while implicit repreecent explicit methods such as 3DGS. Brief but informative  descriptions of thessentations provide a compact scene encoding with potentially escriptions of these techniques are given below. d T( ) · ( ( )) ·  dhigher rendering computational needs. Hybrid approaches take t1 2.2.1 Neural Radiadvantage of both by using a combination of explicitly stored Similarly to Eq. 2, this can be approximatedlocal latent features and shallow neural networks, using various, structures such as sparse voxel hashing grids [50], [51], multi-n 2020, Mildenhall et al. [33] introduced NeRF, an implicit,ˆ resolution dense voxel grids [52], unordered point sets [53], p , g   explicit volumetricand more. Figure 2 visually illustrates these representations, set of input viewswhich have recently had a significant impact on SLAM,    scene function, repmethodologies, primarily through the incorporation of models cene function, representing three-dimensional scenes viavolumetric a radiance field. Fderived from NeRF and more recent explicit methods such a radiance field. Formally expressed as f(x, d) → (c, σ),l scenes via h i  t d f i d th  gas 3DGS. Below, we briefly describe NeRF – for image he model leverages an MLP (Multi-Layer Perceptron) withem) → (c, σ),For optimization, a square error photomrendering and surface reconstruction – and 3DGS, essential weights Θ, denoted as f<sub>Θ</sub> , approximating a 5D functioeptron) withemployed, represented as L = Px = (x,for understanding the upcoming SLAM approaches.

wing direction d = (θ, ϕ) and in-scene 3D coordinatesassunction ofHere, C (r) denotes the ground truth color fview consistency b1) Neural Radiance Field (NeRF): In 2020, Mildenhall et x = (x, y, z). ota y, t e representat on ensures mu t - ba coordinatesassociated with r in the training image, and R dependently of vieal. [33] introduced NeRF, an implicit, continuous volumetric y y p g   y  sures mu ti- batch of rays for synthesizing the target image.depends on both virepresentation, setting a new standard for novel view synthesis. n  While NeRF achieved success, challenges likThe NeRF workIn contrast to conventional explicit volumetric models, this ing/rendering speeds persist. Follow-up methog  ymethod employs a sparse set of input views to optimize asting camera rays through the scene to generate samplingy y  [ ],    qa continuous volumetric scene function, representing threepoints per pixel, computing local color and density usingg/ g g q   volume rendering tdimensional scenes via a radiance field. To achieve this, he NeRF MLP(s) for each sampling point, and employing itythe computation ofthe original NeRF implementation requires knowledge of the olume rendering to synthesize the 2D image. Specifically,imd employing ray r(t) = o + td incamera poses and intrinsic parameters corresponding to each he computation of the color C(r) resulting from a cameraSpecifically, i d d i dinput view, which are estimated using the COLMAP structurey ( )       g 2.2m a camerafrom-motion package [54], [55]. This approach has become the Deion:2.2.2 Surface Reconstruction from Neural Fielcommon practice in subsequent research building upon the 2Despite the potential of NeRNeRF framework. Formally expressed as $f ( \mathbf { x } , \mathbf { d } )   \rightarrow   ( \mathbf { c } , \sigma )$ <sub>t1</sub>the 3D geometry of a scene, these models arthe model leverages an MLP (Multi-Layer Perceptron) with (1)defined iweights Θ, denoted as $f _ { \varTheta } ,$ e weights of the neural network. O approximating a 5D function of viewing direction $\mathbf { d } \; = \; ( \theta , \phi )$ and in-scene 3D coordinates $\mathbf { x } = ( x , y , z )$ . Notably, the representation ensures multi-view

consistency by predicting the volume density σ independently ere, T(t) = exp −R σ(r(s))dsy, y g  y  of viewing direction, while color $\mathbf { c } = ( r , g , b )$ cumu-   −Rt1depends on both transmittance from t<sub>1</sub> to t along the ray.viewing direction and 3D coordinates.

integral computation uses quadrature by dividingidioffer faster access but require more h  i N lThe NeRF workflow for novel view synthesis involves y into N evenly-spaced bins:solution constraints, while implicitcasting camera rays through the scene to generate sampling de a compact scene encoding withNpoints per pixel, computing local color and density using Ni−1dering computational needs. HybridC(r) = X α<sub>i</sub>T<sub>i</sub>c<sub>i</sub>,the NeRF MLP(s) for each sampling point, and employing X i i i, i  p −X j j  (2)g   y g  i=1volume rendering to synthesize the 2D image. Specifically, where, δ<sub>i</sub> denotes the inthe computation of the color C(r) resulting from a camera tive2], mray $\mathbf { r } ( t ) = \mathbf { o } +$ e n erva e ween consecu ve sam-n dense voxel grids ples ti and t<sub>i+1</sub>.td involves an integral formulation:

$$
C (\mathbf {r}) = \int_ {t _ {1}} ^ {t _ {2}} T (t) \sigma (\mathbf {r} (t)) \mathbf {c} (\mathbf {r} (t), \mathbf {d}) \mathrm{d} t\tag{1}
$$

p p g  y, ,   calcu-it models such as NeRF and more g  Here, dt denotes the differential distance traveled by the s suc as . r e u n orma veray at each integration step. The terms $\sigma ( \mathbf { r } ( t ) )$ and $\mathbf { c } ( \mathbf { r } ( t ) , \mathbf { d } )$.t<sub>1</sub>represent the volume density and color at point r(t) along t1(3)Similarly to Eq. 2, this cthe camera ray with viewing direction d, respectively. Addimilarly te Field (tionally, $\begin{array} { r } { T ( t )   =   \exp \left( - \int _ { t _ { 1 } } ^ { t } \sigma ( \mathbf { r } ( s ) ) , \mathsf { d } s \right) } \end{array}$ :is the accumulated al. [33] introduced Ntransmittance from $t _ { 1 }$ F, an ito t.

Dˆ (r) = X α t T . (4)epresentation, setting a new stan-The integral computation uses quadrature by dividing the i=1(4)ynthesis. In contrast to conventioray into N evenly-spaced bins:

$$
C (\mathbf {r}) = \sum_ {i = 1} ^ {N} \alpha_ {i} T _ {i} \mathbf {c} _ {i}, \quad T _ {i} = \exp \left(- \sum_ {j = 1} ^ {i - 1} \sigma_ {j} \delta_ {j}\right)\tag{2}
$$

p fΘ , apwhere, $\delta _ { i }$ ,  q  p  ˆoximating a 5D function ofHere, C<sub>gt</sub>(r) denotes thdenotes the interval between consecutive samples $t _ { i }$,and $t _ { i + 1 }$ n n-sc, while $\sigma _ { i }$ e and $\mathbf { c } _ { i }$ Pr∈R ∥ − gt ∥2.or na esassociated with r in the trindicate the density and color evalu-2,    atc o rays or synt es zated at sample point i along the ray, respectively. Additionally, $\alpha _ { i } = ( 1 { - } \mathsf { e x p } ( - \sigma _ { i } \delta _ { i } ) )$ g the target image.b    characterizes the opacity resulting from hile NeRF achieved success, challengesng direction and 3D coordinates.alpha compositing at sample point i.

dering speeds persist. Follow-up methods, compre-train-for novel view synthesis involves training/rendering using teThe expected depth along a ray, instead, can be calculated vely surveyed in [60], seek to enhance qcompre-rough the scene to generate samplingsusing the accumulated transmittance:

$$
d (\mathbf {r}) = \int_ {t _ {1}} ^ {t _ {2}} T (t) \cdot \sigma (\mathbf {r} (t)) \cdot t d t,\tag{3}
$$

de rendering speeds.lves an integral formulation:2.2.2 SurfaSimilarly to Eq. 2, this can be approximated as:

$$
\hat {D} (\mathbf {r}) = \sum_ {i = 1} ^ {N} \alpha_ {i} t _ {i} T _ {i}.\tag{4}
$$

g    . g plicitlyIn this context, some methods propose using expected depth aining anto either impose depth supervision from external priors [56], [57] or apply regularization techniques [58], enhancing scene geometry and enforcing depth smoothness.

<!-- page 4 of 25 -->

4

For optimization, a square error photometric loss is employed, represented as $\begin{array} { r } { \widetilde { L   } =   \sum _ { r \in R } \| \hat { C } ( \mathbf { r } )   -   C _ { g t } ( \mathbf { r } ) \| _ { 2 } ^ { 2 } } \end{array}$ . Here, $C _ { g t } ( r )$ denotes the ground truth color for the pixel associated with r in the training image, and R denotes the batch of rays for synthesizing the target image.

While NeRF achieved success, challenges like slow training/rendering speeds persist. Follow-up methods, comprehensively surveyed in [59]–[61], seek to enhance quality or faster training/rendering using techniques such as hashing [50] or sparse 3D grids [62]. However, these methods still struggle to accurately represent empty spaces and face image quality limitations due to structured grids, which significantly impede rendering speeds. Other works [63]–[65], instead, aims to reduce the reliance on external tools like COLMAP for camera pose estimation. While these approaches share the goal of joint pose estimation and scene reconstruction with SLAM, they differ in their processing paradigm. SLAM typically processes images sequentially as they are captured, enabling real-time operation. In contrast, these NeRF-based pose estimation methods often require a set of images to be processed simultaneously, limiting their applicability in real-time scenarios. Moreover, they either need a pre-trained neural implicit network or cannot optimize poses and the network concurrently, further constraining their use in SLAM applications.

2) Surface Reconstruction from Neural Fields: Despite the potential of NeRF and its variants to capture the 3D geometry of a scene, these models are implicitly defined in the weights of the neural network. Obtaining an explicit representation of the scene through 3D meshes is desirable for 3D reconstruction applications. Starting with NeRF, a basic approach to achieving coarse scene geometry is to threshold the density predicted by the MLP. More advanced solutions explore three main representations.

**Occupancy.** This representation models free versus occupied space by replacing alpha values $\alpha _ { i }$ along the ray with a learned discrete function $o ( x ) \in \{ 0 , 1 \}$ . Specifically, an occupancy probability $\in   [ 0 , 1 ]$ is estimated and surfaces are obtained by running the marching cubes algorithm [66].

**Signed Distance Function (SDF).** An alternative method for scene geometry is the signed distance from any point to the nearest surface, yielding negative values inside objects and positive values outside. NeuS [67] was the first to revisit the NeRF volumetric rendering engine, predicting the SDF with an MLP as $f ( \mathbf { r } ( t ) )$ and replacing α with $\rho ( t )$ , derived from the SDF as follows:

$$
\rho (t) = \max \left(\frac {- \frac {d \Phi}{d t} (f (\mathbf {r} (t)))}{\Phi (f (\mathbf {r} (t)))}, 0\right)\tag{5}
$$

with Φ being the sigmoid function and $\frac { d \Phi } { d t }$ its derivative.

**Truncated Signed Distance Function (TSDF).** Finally, predicting a truncated SDF with the MLP allows for removing the contribution by any SDF value too far from individual surfaces during rendering. In [68], pixel color is obtained as a weighted sum of colors sampled along the ray:

$$
C (\mathbf {r}) = \frac {\sum_ {i = 1} ^ {N} w _ {i} \mathbf {c} _ {i}}{\sum_ {i = 1} ^ {N} w _ {i}}\tag{6}
$$

![Image block](images/tosi2024_nerf-gs-slam-survey_p4_b11.png)

Fig. 3: NeRF and 3DGS differ conceptually. (left) NeRF queries an MLP along the ray, while (right) 3DGS blends Gaussians for the given ray.

with $w _ { i }$ defined, according to truncation distance $t _ { r }$ , as

$$
w _ {i} = \Phi \big (\frac {f (\mathbf {r} (t))}{t _ {r}} \big) \cdot \Phi \big (- \frac {f (\mathbf {r} (t))}{t _ {r}} \big)\tag{7}
$$

3) 3D Gaussian Splatting (3DGS): Introduced by Kerbl et al. [34] in 2023, 3DGS is an explicit radiance field technique for efficient and high-quality rendering of 3D scenes. Unlike conventional explicit volumetric representations, such as voxel grids, it provides a continuous and flexible representation for modeling 3D scenes in terms of differentiable 3D Gaussianshaped primitives. These primitives are used to parameterize the radiance field and can be rendered to produce novel views. In addition, in contrast to NeRF, which relies on computationally expensive volumetric ray sampling, 3DGS achieves real-time rendering through a tile-based rasterizer. This conceptual difference is highlighted in Figure 3. This approach offers improved visual quality and faster training without relying on neural components, while also avoiding computation in empty space. More specifically, starting from multi-view images with known camera poses, 3DGS learns a set $\mathcal { G } = \{ g _ { 1 } , g _ { 2 } , \ldots , g _ { N } \}$ of 3D Gaussians, where N denotes the number of Gaussians in the scene. Each primitive $g _ { i }$ , with $1 < i < N$ , is parameterized by a full 3D covariance matrix $\mathbf { \Sigma } _ { i } \in \mathbb { R } ^ { 3 \times 3 }$ , the mean or center position $\pmb { \mu } _ { i } \in \mathbb { R } ^ { 3 }$ , the opacity $o _ { i }   \in   [ 0 , 1 ]$ , and color $\mathbf { c } _ { i }$ represented by spherical harmonics (SH) for view-dependent appearance, where all the properties are learnable and optimized through back-propagation. This allows for the compact expression of the spatial influence of an individual Gaussian primitive as:

$$
g _ {i} (\mathbf {x}) = e ^ {- \frac {1}{2} (\mathbf {x} - \boldsymbol {\mu} _ {i}) ^ {\top} \boldsymbol {\Sigma} _ {i} ^ {- 1} (\mathbf {x} - \boldsymbol {\mu} _ {i})}\tag{8}
$$

Here, the spatial covariance Σ defines an ellipsoid and it is computed as $\mathbf { \Sigma } = \mathbf { R } \mathbf { S } \mathbf { S } ^ { \top } \mathbf { R } ^ { \top }$ , where $\mathbf { S } \in \mathbb { R } ^ { 3 }$ is the spatial scale and $\mathbf { R }   \in   \mathbb { R } ^ { 3 \times 3 }$ represents the rotation, parameterized by a quaternion. For rendering, 3DGS operates akin to NeRF but diverges significantly in the computation of blending co-efficients. Specifically, the process involves first projecting 3D Gaussian points onto a 2D image plane, a process commonly referred to as “splatting”. This is done expressing the projected 2D covariance matrix and center as $\mathbf { \Sigma ^ { \prime } } = \mathbf { J } \mathbf { W } \mathbf { \Sigma } \mathbf { W } ^ { \mathbf { T } } \mathbf { J } ^ { \mathbf { T } }$ and $\pmb { \mu } ^ { \prime } = \mathbf { J } \mathbf { W } \pmb { \mu } ,$ where W represents the viewing transformation, and J is the Jacobian of the affine approximation of the projective transformation. Consequently, 3DGS computes the final pixel color C by blending 3D Gaussian splats that overlap at a given pixel, sorted by their depth:

<!-- page 5 of 25 -->

5

$$
C = \sum_ {i \in \mathcal {N}} \mathbf {c} _ {i} \alpha_ {i} \prod_ {j = 1} ^ {i - 1} (1 - \alpha_ {j})\tag{9}
$$

where the final opacity $\alpha _ { i }$ is the multiplication result of the learned opacity $o _ { i }$ and the Gaussian:

$$
\alpha_ {i} = o _ {i} \exp \left(- \frac {1}{2} (\mathbf {x} ^ {\prime} - \boldsymbol {\mu} _ {i} ^ {\prime}) ^ {\top} \boldsymbol {\Sigma} _ {i} ^ {\prime - 1} (\mathbf {x} ^ {\prime} - \boldsymbol {\mu} _ {i} ^ {\prime})\right)\tag{10}
$$

where $\mathbf { x } ^ { \prime }$ and $\mu _ { i } ^ { \prime }$ are coordinates in the projected space. Similarly, the depth D is rendered as:

$$
D = \sum_ {i \in \mathcal {N}} d _ {i} \alpha_ {i} \prod_ {j = 1} ^ {i - 1} (1 - \alpha_ {j})\tag{11}
$$

Here, $d _ { i }$ refers to the depth of the center of the i-th 3D Gaussian, obtained by projecting onto the z-axis in the camera coordinate system. For optimization, instead, the process begins with parameter initialization from SfM point clouds or random values, followed by Stochastic Gradient Descent (SGD) using an L1 and D-SSIM loss function against ground truth and render views. Additionally, periodic adaptive densification handles under- and over-reconstruction by adjusting points with significant gradients and removing low-opacity points, refining scene representation and reducing rendering errors. For more details on 3DGS and related works, refer to [69]–[71].

## C. Datasets

This section summarizes datasets commonly used in recent SLAM methodologies, covering various attributes such as sensors, ground truth accuracy, and other key factors, in both indoor and outdoor environments. Figure 4 presents qualitative examples from diverse datasets, which will be introduced in the remainder.

The **TUM RGB-D [72]**<sup>3</sup> dataset comprises RGB-D sequences with annotated camera trajectories, recorded using two platforms: handheld and robot, providing a diverse range of motions. The dataset features 39 sequences, some with loop closures. Core elements include color and depth images from a Microsoft Kinect sensor, captured at 30 Hz and 640×480 resolution. Ground-truth trajectories are derived from a motioncapture system with eight high-speed cameras operating at 100 Hz. The versatility of the dataset is demonstrated through various trajectories in typical office environments and an industrial hall, encompassing diverse translational and angular velocities.

The **ScanNet [73]**<sup>4</sup> dataset provides a collection of realworld indoor RGB-D acquisitions, featuring 2.5 million images from 1513 scans in 707 unique spaces. In particular, it includes estimated calibration parameters, camera poses, 3D surface reconstructions, textured meshes, detailed semantic segmentations at the object-level, and aligned CAD models.

The development process involved the creation of a userfriendly capture pipeline using a custom RGB-D capture

![Image block](images/tosi2024_nerf-gs-slam-survey_p5_b13.png)

![Image block](images/tosi2024_nerf-gs-slam-survey_p5_b14.png)

(b) ScanNet [73]

(a) ETH3D-SLAM [30]

![Image block](images/tosi2024_nerf-gs-slam-survey_p5_b17.png)

![Image block](images/tosi2024_nerf-gs-slam-survey_p5_b18.png)

(c) TUM RGB-D [72]

(d) Replica [74]

Fig. 4: Qualitative Comparison of Key SLAM Datasets. RGB-D images from: (a) ETH3D-SLAM [30], (b) ScanNet [73], (c) TUM RGB-D [72], and (d) Replica [74].

setup with structure sensors attached to handheld devices such as iPads. The subsequent offline processing phase resulted in comprehensive 3D scene reconstructions, complete with available 6-DoF camera poses and semantic labels. Note that camera poses in ScanNet are derived from the BundleFusion system [49], which may not be as accurate as alternatives such as TUM RGB-D.

The **Replica [74]**<sup>5</sup> dataset features 18 photorealistic 3D indoor scenes with dense meshes, HDR textures, semantic data, and reflective surfaces. It spans different scene categories, includes 88 semantic classes, and incorporates 6 scans of a single space capturing different furniture arrangements and temporal snapshots. Reconstruction involved a custom-built RGB-D capture rig with synchronized IMU, RGB, IR, and wide-angle grayscale sensors, accurately fusing raw depth data through 6 degrees of freedom (DoF) poses. Although the original data was captured in the real world, the portion of the dataset used for SLAM evaluation is synthetically generated from the accurate meshes produced during reconstruction. Consequently, synthetic sequences lack real-world characteristics like specular highlights, autoexposure, blur, and more.

The **KITTI [75]**<sup>6</sup> dataset serves as a popular benchmark for evaluating stereo, optical flow, visual odometry/SLAM algorithms, among others. Acquired from a vehicle equipped with stereo cameras, Velodyne LiDAR, GPS and inertial sensors, the dataset contains 42,000 stereo pairs and LiDAR pointclouds from 61 scenes representing autonomous driving scenarios. The KITTI odometry dataset, with 22 LiDAR scan sequences, contributes to the evaluation of odometry methods using LiDAR data.

The **Newer College [76]**<sup>7</sup> dataset comprises sensor data captured during a 2.2 km walk around New College, Oxford. It includes information from a stereoscopic-inertial camera, a multi-beam 3D LiDAR with inertial measurements, and

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>3</sup>[https://cvg.cit.tum.de/data/datasets/RGB-D-dataset](https://cvg.cit.tum.de/data/datasets/RGB-D-dataset)</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>5</sup>[https://github.com/facebookresearch/Replica-Dataset](https://github.com/facebookresearch/Replica-Dataset)</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>4</sup>[http://www.scan-net.org/](http://www.scan-net.org/)</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>6</sup>[https://www.cvlibs.net/datasets/kitti/](https://www.cvlibs.net/datasets/kitti/)</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>7</sup>[https://arxiv.org/pdf/ori.ox.ac.uk/datasets/newer-college-dataset](https://arxiv.org/pdf/ori.ox.ac.uk/datasets/newer-college-dataset)</span></small>

<!-- page 6 of 25 -->

6

a tripod-mounted survey-grade LiDAR scanner, generating a detailed 3D map with around 290 million points. The dataset provides a 6 DoF ground truth pose for each LiDAR scan, accurate to approximately 3 cm. The dataset encompasses diverse environments, including built spaces, open areas, and vegetated zones.

1) Other Datasets: Moreover, we draw attention to lessutilized alternative datasets in recent SLAM research.

The **ETH3D-SLAM** [30]<sup>8</sup> dataset includes videos from a custom camera rig, suitable for assessing visual-inertial mono, stereo, and RGB-D SLAM. It features 56 training datasets, 35 test datasets, and 5 independently captured training sequences using SfM techniques for ground truth.

The **EuRoC MAV [77]**<sup>9</sup> dataset offers synchronized stereo images, IMU, and accurate ground truth for a micro aerial vehicle. It supports visual-inertial algorithm design and evaluation in diverse conditions, including an industrial setting with millimeter-accurate ground truth and a room for 3D environment reconstruction.

The **7-scenes [78]**<sup>10</sup> dataset, created for relocalization performance evaluation, was recorded using a Kinect at 640×480 resolution. Ground truth poses were obtained through Kinect-Fusion [2]. Sequences from different users were divided into two sets—one for simulating keyframe harvesting and the other for error calculation. The dataset presents challenges such as specularities, motion blur, lighting conditions, flat surfaces, and sensor noise.

The **ScanNet++ [79]**<sup>11</sup> dataset comprises 460 highresolution 3D indoor scene reconstructions, dense semantic annotations, DSLR images, and iPhone RGB-D sequences. Captured with a high-end laser scanner at sub-millimeter resolution, each scene includes annotations for over 1,000 semantic classes, addressing label ambiguities and introducing new benchmarks for 3D semantic scene understanding and novel view synthesis.

The **NeuralRGBD [68]**<sup>12</sup> dataset consists of 10 synthetic scenes with varying complexity and materials. It provides color and depth images rendered using BlenderProc [80], simulating real-world depth sensor artifacts. Camera trajectories, initially estimated with BundleFusion [49], are designed to scan only portions of scenes, mimicking real-world scanning behavior.

The **Bonn Dataset [81]**<sup>13</sup> offers 24 highly dynamic and 2 static RGB-D sequences featuring people manipulating objects. Recorded with an ASUS Xtion Pro LIVE sensor and an Optitrack Prime 13 system for ground truth trajectories, it follows the TUM RGB-D format. A Leica BLK360 provides ground truth 3D pointclouds of the static environment, specifically designed for evaluating SLAM in dynamic scenes.

**Additional Datasets.** For an exhaustive survey of specialized SLAM-related datasets beyond those mentioned, readers can refer to the work by Liu et al. [82]. This paper provides

an in-depth exploration of a wide range of datasets designed to facilitate research and benchmarking.

## D. Evaluation Metrics

The evaluation of SLAM systems typically employs several metrics across domains like 3D reconstruction, 2D depth estimation, trajectory estimation, and view synthesis to assess the effectiveness of methods against ground truth data.

A. Mapping. Metrics assessing the quality of 3D reconstruction and 2D depth estimation include:

• **Accuracy (cm)**↓: Computes the average distance between sampled points from the reconstructed mesh and the nearest ground-truth point.

• **Completion (cm)**↓: Measures the average distance between sampled points from the ground-truth mesh and the nearest reconstructed.

• **Precision (**%)↑: Indicates the proportion of points within the reconstructed mesh with Accuracy under a distance threshold d.

• **Recall (**%)↑: Indicates the proportion of points within the reconstructed mesh with Completion under a distance d. It is often referred to as Completion Ratio.

• **F-Score (**%)↑: An aggregate score defined as the harmonic mean between Precision and Recall.

• **L1-Depth (cm)**↓: Following [5], it computes the absolute difference between depth maps obtained from randomly sampled viewpoints from the reconstructed and the corresponding ground truth meshes respectively.

B. Tracking. Metrics for pose estimation, crucial for tracking performance, primarily include:

• **Absolute Trajectory Error (ATE)(cm)** ↓: Evaluates trajectory estimation accuracy by measuring the average Euclidean translation distance between corresponding poses in estimated and ground truth trajectories, often reported in terms of Root Mean Square Error (RMSE). As both trajectories can be specified in arbitrary coordinate frames, alignment is required. Importantly, this metric focuses solely on the translation component.

C. View Synthesis. The evaluation of view synthesis relies mainly on three visual quality assessment metrics:

• **Peak Signal to Noise Ratio (PSNR)**↑: Measures image quality by evaluating the ratio between the maximum pixel value and the root mean squared error, usually expressed in terms of the logarithmic decibel scale.

• **Structural Similarity Index Measure (SSIM [182])**↑: Assesses image quality by examining the similarities in luminance, contrast, and structural information among patches of pixels.

• **Learned Perceptual Image Patch Similarity (LPIPS [183])**↓ : Utilizes learned convolutional features to assess image quality based on feature map mean squared error across layers.

D. Semantic Segmentation. For SLAM methods that additionally estimate semantic information of the scene, the following metric is included to evaluate the performance of the semantic segmentation:

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>8</sup>[https://www.eth3d.net/slam overview](https://www.eth3d.net/slam_overview)</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>9</sup>[https://projects.asl.ethz.ch/datasets/doku.php?id= kmavvisualinertialdatasets](https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets)</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">10<a href="http://research.microsoft.com/7-scenes/"><sub>http</sub>://research.microsoft.com/7-scenes/</a></span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">11<a href="https://cy94.github.io/scannetpp/"><sub>https</sub>://cy94.github.io/scannetpp/</a></span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">12<a href="https://github.com/dazinovic/neural-rgbd-surface-reconstruction"><sub>https</sub>://github.com/dazinovic/neural-rgbd-surface-reconstruction</a></span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">13<a href="https://www.ipb.uni-bonn.de/data/rgbd-dynamic-dataset/"><sub>https</sub>://www.ipb.uni-bonn.de/data/rgbd-dynamic-dataset/</a></span></small>

<!-- page 7 of 25 -->

7

TABLE I: SLAM Systems Overview. We categorize the different methods into main RGB-D, RGB, and LiDAR-based frameworks. In the leftmost column, we identify sub-categories of methods sharing specific properties, detailed in Sections III-B1 to III-C2. Then, for each method, we report, from the second leftmost column to the second rightmost, the method name and publication venue, followed by (a) the input modalities they can process: RGB, RGB-D, D (e.g. LiDAR, ToF, Kinect, etc.), stereo, IMU, or events; (b) mapping properties: scene encoding and geometry representations learned by the model; (c) additional outputs learned by the method, such as object/semantic segmentation, or uncertainty modeling (Uncert.); (d) tracking properties related to the adoption of a frame-to-frame or frame-to-model approach, the utilization of external trackers, Global Bundle Adjustment (BA), or Loop Closure; (e) advanced design strategies, such as modeling sub-maps or dealing with dynamic environments (Dyn. Env.); (f) the use of additional priors. Finally, we report the link to the project page or source code in the rightmost column. † indicates code or webpage not released yet.

<table><tbody><tr><td>Section</td><td>Method</td><td>Venue</td><td>Event RGB-D RGB D Stereo IMU Camera</td><td>Scene Geometry Encoding Representation</td><td>Obj/Sem.Uncert. Segment.</td><td>Frame-to Frame-to External Global Loop Model Frame Tracker BA Closure</td><td>Sub- Dyn. Maps Env.</td><td>Extra Priors</td><td>Link</td></tr><tr><td colspan="10">RGB-D (Sec. III-A)</td></tr><tr><td>Sec. III-A1</td><td>iMAP [1] NICE-SLAM [5] Vox-Fusion [83] ESLAM [84] Co-SLAM [85] GO-SLAM [86] Point-SLAM [88] ToF-SLAM [89] ADFP [90] MLM-SLAM [91] Plenoxel-SLAM [92] Structerf-SLAM [93] KN-SLAM [96] SLAIM [99] IBD-SLAM [100] VPE-SLAM [104] HERO-SLAM [105] LRSLAM [106] LCP-Fusion [107]</td><td>ICCV 2021 CVPR 2022 ISMAR 2022 CVPR 2023 CVPR 2023 ICCV 2023 ICCV 2023 ICCV 2023 NeurIPS 2023 RAL 2023 WACV 2024 C .&amp; G. 2024 TIM 2024 CVPRW 2024 CVPR 2024 ICRA 2024 ICRA 2024 ECCV 2024 IROS 2024</td><td>✓✓✓✓✓✓ ✓ ✓✓✓✓✓✓✓✓✓✓✓✓✓✓</td><td>MLP Density Hier. Grid + MLP Occupancy Octree Grid + MLP SDF Feature Planes + MLP TSDF Hash Grid + MLP SDF Hash Grid + MLP SDF Neural Points + MLP Occupancy Hier. Grid + MLP SDF Hier. Grid + MLP Occupancy MLP Occupancy Plenoxels Density Hier. Grid Occupancy Hier. Grid Occupancy Hier. Grid + MLP Density Image Feat. + MLP Density Octree Grid + MLP TSDF Hash Grid + MLP TSDF Feature Planes + MLP SDF Octree Grid + MLP SDF</td><td></td><td>✓✓✓✓✓ ✓✓ DROID [87] ✓ ✓✓✓✓✓✓✓ ORB2 [94] ✓ EPNP [97] ✓✓ ✓✓ SuperPoint [101] &amp; SuperGlue [102]✓ ✓✓✓✓ ✓</td><td></td><td>Super-pixel Segmentation [95] HF-Net [98] GMFLow [103]</td><td>WebPage Code Code Code Code Code Code WebPage Code Code WebPage WebPage† Code† WebPage Code†</td></tr><tr><td>Sec. III-A2</td><td>MonoGS [108] Photo-SLAM [109] SplaTAM [111] GS-SLAM [12] GS-ICP SLAM [112] HF-GS SLAM [114] CG-SLAM [115] MM3DGS-SLAM [117] RTG-SLAM [119]</td><td>CVPR 2024 CVPR 2024 CVPR 2024 CVPR 2024 ECCV 2024 IROS 2024 ECCV 2024 IROS 2024 SIGGRAPH 2024</td><td>✓ ✓✓ ✓ ✓✓✓✓✓✓✓ ✓ ✓✓</td><td>3D Gaussians Density 3D Gaussians Density 3D Gaussians Density 3D Gaussians Density 3D Gaussians Density 3D Gaussians Density 3D Gaussians Density 3D Gaussians Density 3D Gaussians Density</td><td>✓</td><td>✓✓ ORB3 [110] ✓✓✓✓ G-ICP [113]✓✓✓✓</td><td></td><td>NetVLAD [116] DPT [118]</td><td>WebPage Code Code Code WebPage Code</td></tr><tr><td>Sec. III-A3</td><td>MeSLAM [6] CP-SLAM [121] NISB-Map [122] Multiple-SLAM [123] MIPS-Fusion [124] NGEL-SLAM [125] PLGSLAM [126] Loopy-SLAM [9] NEWTON [127] MAN-SLAM [128]</td><td>SMC 2022 NeurIPS 2023 RAL 2023 TIV 2023 TOG 2023 ICRA 2024 CVPR 2024 CVPR 2024 RAL 2024 IROSw 2024</td><td>✓✓✓✓✓✓✓✓✓ ✓✓</td><td>MLP Density Neural Points + MLP Occupancy MLP Density Octree Grid + MLP SDF MLP TSDF Octree Grid + MLP Occupancy Feature Planes + MLP SDF Neural Points + MLP Occupancy Hash Grid + MLP Density Features Planes + MLP</td><td>✓✓TSDF</td><td>✓ C-ICP [120]✓ ✓ ✓✓ Any✓✓ ✓✓ ORB3 [110] ✓ ✓✓✓ ✓✓ ORB2 [94] ✓ ✓ DROID [87] ✓ ✓</td><td>✓✓✓✓✓✓✓✓✓✓</td><td></td><td>Code</td></tr><tr><td>Sec. III-A4</td><td>iLabel [7] FR-Fusion [129] vMap [132] SNI-SLAM [133] DNS-SLAM [135] SGS-SLAM [8] NEDS-SLAM [136] GS3LAM [138] NIS-SLAM [139]</td><td>RAL 2023 ICRA 2023 CVPR 2023 CVPR 2024 IROS 2024 ECCV 2024 RAL 2024 MM 2024 TVCG 2024</td><td>✓✓✓✓✓✓✓✓✓</td><td>MLP Density MLP Density MLP Occupancy Hier. Grid + MLP TSDF Hash Grid + MLP Occupancy 3D Gaussians Density 3D Gaussians Density 3D Gaussians Density Tetra. Features + MLP SDF</td><td>✓ ✓✓✓✓✓✓✓✓✓</td><td>✓✓✓✓✓ ✓✓ ✓✓✓✓ ✓</td><td></td><td>User User &amp; EfficientNet [130]/DINO [131] Dinov2 [134] GT semantics GT semantics Depth Anything [137] + GT semantics GT semantics Mask2Former [140]</td><td>WebPage WebPage Code Code WebPage</td></tr><tr><td>Sec. III-A5</td><td>DN-SLAM [13] DynaMoN [142] NID-SLAM [144] TivNe-SLAM [145] RoDyn-SLAM [147] DG-SLAM [149] ONeK-SLAM [151]</td><td>Sensors J. 2023 RAL 2024 ICME 2024 IROS 2024 RAL 2024 NeurIPS 2024 ICRA 2024</td><td>✓✓ ✓✓✓✓✓✓</td><td>Hash Grid + MLP Density HexPlane + MLP Density Hier. Grid + MLP Occupancy Octree Grid + MLP SDF Hash Grid + MLP TSDF 3D Gaussians Density Hier. Grid + MLP Occupancy</td><td>✓✓✓✓</td><td>✓ ORB3 [110] ✓ DROID [87]✓✓✓ ✓✓ DROID [87] ✓ SIFT matching [152]</td><td>✓✓✓✓✓✓✓</td><td>SAM [141] DeepLabV3 [143] Mask R-CNN [146] Oneformer&amp;RAFT-GMA [148] Oneformer [150] SAM-Track [153]</td><td>Code Code Code</td></tr><tr><td>Sec. III-A6</td><td>OpenWorld-SLAM [154] UncLe-SLAM [17] NVINS [155] CDA [156]</td><td>CRV 2023 ICCVW 2023 IROS 2024 T-ITS 2024</td><td>✓ ✓✓ ✓✓ ✓✓</td><td>Hier. Grid + MLP Occupancy Hier. Grid + MLP Occupancy Hash Grid + MLP Density Hash Grid + MLP Density</td><td>✓✓✓✓</td><td>✓✓✓ Custom PoseNet ✓ ORB3 [110]</td><td></td><td></td><td>Code</td></tr><tr><td>Sec. III-A7</td><td>EN-SLAM [14]</td><td>CVPR 2024</td><td>✓ ✓</td><td>Hier. Grid + MLP TSDF</td><td></td><td>✓ ✓</td><td></td><td></td><td></td></tr><tr><td colspan="10">RGB (Sec. III-B)</td></tr><tr><td>Sec. III-B1</td><td>DIM-SLAM [16] Orbeez-SLAM [157] TT-HO-SLAM [158]</td><td>ICLR 2023 ICRA 2023 IROS 2024</td><td>✓✓✓</td><td>Hier. Grid + MLP Density Hash Grid + MLP Density Hier. Grid + MLP Density</td><td></td><td>✓✓ ORB2 [94]✓</td><td></td><td></td><td>Code Code</td></tr><tr><td>Sec. III-B2</td><td>MonoGS++ [159]</td><td>BMVC 2024</td><td>✓</td><td>3D Gaussians Density</td><td></td><td>✓ DPVO [160]</td><td></td><td></td><td></td></tr><tr><td>Sec. III-B3</td><td>iMode [161] Hi-SLAM [163] NICER-SLAM [18] NeRF-VO [165] MoD-SLAM [166] Q-SLAM [168] MGS-SLAM [169]</td><td>ICRA 2023 RAL 2023 3DV 2024 RAL 2024 RAL 2024 CoRL 2024 RAL 2024</td><td>✓✓✓✓✓ ✓✓ ✓✓</td><td>MLP Density Hash Grid + MLP TSDF Hier. Grid + MLP SDF Hash Grid + MLP Density Hash Grid + MLP SDF Grid Fact. + MLP Density 3D Gaussians Density</td><td>✓</td><td>✓ ORB [10] ✓ DROID [87] ✓ ✓✓✓ DPVO [160] ✓ DROID [87] ✓ ✓ DROID [87] ✓ DPVO [160]</td><td></td><td>Sparse-to-dense [162] Omnidata [164] GMFlow [103] &amp; Omnidata [164] Omnidata [164] DPT [118] &amp; ZoeDepth [167] Segmentation Network</td><td>WebPage Code†</td></tr><tr><td>Sec. III-B4</td><td>RO-MAP [170] 3DIML [171]</td><td>RAL 2023 ICRA 2024</td><td>✓✓</td><td>Hash Grid + MLP Occupancy Hash Grid + MLP Density</td><td>✓✓</td><td>✓ ORB2 [94] ✓ NetVLAD &amp; LoFTR [172]</td><td></td><td>YOLOv8 Mask2Former [140]</td><td>Code</td></tr><tr><td>Sec. III-B5</td><td>NeRF-SLAM [173]</td><td>IROS 2023</td><td>✓</td><td>Hash Grid + MLP Density</td><td>✓</td><td>✓ DROID [87]</td><td></td><td></td><td>Code</td></tr><tr><td colspan="10">LiDAR (Sec. III-C)</td></tr><tr><td>Sec. III-C1</td><td>NeRF-LOAM [15] LONER [174] PIN-SLAM [176] TNDF-Fusion [177]</td><td>ICCV 2023 RAL 2023 T-RO 2024 RAL 2024</td><td>✓✓✓ ✓✓</td><td>Octree Grid + MLP SDF Hier. Grid + MLP Density Neural Points + MLP SDF Features Planes + MLP TNDF</td><td>✓</td><td>✓✓ P2P-ICP [175]✓ ✓✓</td><td>✓</td><td></td><td>Code Code Code</td></tr><tr><td>Sec. III-C2</td><td>LIV-GaussMap [178] MM-Gaussian [179]</td><td>RAL 2024 IROS 2024</td><td>✓ ✓✓</td><td>3D Gaussians Density 3D Gaussians Density</td><td></td><td>✓✓ Kiss-ICP [180]</td><td></td><td>SuperPoint [101] &amp; LightGlue [181]</td><td>Code†</td></tr></tbody></table>

• **Mean Intersection over Union (mIoU)**↑: mIoU is a widely used metric for evaluating semantic segmentation performance. It is computed by calculating the IoU for each class and then taking the average across all classes. IoU is defined as the ratio of the intersection between the predicted and ground truth segmentation masks to their union. A higher mIoU indicates better semantic segmentation accuracy.

## III. SIMULTANEOUS LOCALIZATION AND MAPPING

This section introduces SLAM systems that leverage recent progress in radiance field representations. The papers are categorized by their sensor type: RGB-D (III-A), RGB (III-B), and LiDAR (III-C), with methods organized chronologically

by publication date in major conferences and journals. While the field is rapidly evolving with numerous preprints appearing regularly on arXiv, we focus on peer-reviewed publications to provide a curated overview of established approaches. We encourage readers to explore recent arXiv submissions for the latest developments in this active research area.

For a more advanced understanding, Table I offers a detailed overview of the surveyed methods. This table provides an indepth summary, highlighting key features of each method, and includes references to project pages or source code whenever available. For further details or method specifics, please refer to the original papers.

<!-- page 8 of 25 -->

8

![Image block](images/tosi2024_nerf-gs-slam-survey_p8_b2.png)

Fig. 5: Overview of iMap [1], the Pioneering Approach in Neural Implicit-based SLAM. (Left) The illustration depicts two concurrent processes: tracking, optimizing the current frame’s pose within the locked network; mapping, jointly refining the network and camera poses of selected keyframes. (Right) Jointly optimizing scene network parameters and camera poses for keyframes using differentiable rendering functions. Figure from [1].

## A. RGB-D SLAM Approaches

Here we focus on dense SLAM techniques using RGB-D cameras that capture both color images and per-pixel depth information of the environment. These techniques fall into distinct categories: NeRF-style SLAM solutions (III-A1) and alternatives based on the 3D Gaussian Splatting representation (III-A2). Specialized solutions derived from both approaches include submap-based SLAM methods for large scenes (III-A3), frameworks that address semantics (III-A4), and those tailored for dynamic scenarios (III-A5). Within this classification, some techniques assess reliability through uncertainty (III-A6), while others explore the integration of additional sensors like event-based cameras (III-A7).

1) NeRF-style RGB-D SLAM: Advances in implicit neural representations have enabled accurate and dense 3D surface reconstruction. This has led to novel SLAM systems derived from or inspired by NeRF, initially designed for offline use with known camera poses. **iMAP [1]**, illustrated in Fig.5, marks the first attempt to leverage implicit neural representations for SLAM. This groundbreaking achievement not only pushes the boundaries of SLAM but also establishes a new direction for the field. Specifically, this framework uses an MLP to map 3D coordinates into color and volume density, allowing for rendering depth and color images through network queries. Joint optimization of photometric and geometric losses for a fixed set of keyframes refines network parameters and camera poses. A parallel process ensures close-to-framerate camera tracking, with dynamic keyframe selection based on information gain. In contrast to the use of a single MLP by iMAP, **NICE-SLAM [5]** optimizes a hierarchical representation using three pre-trained MLPs, by encoding geometry into three voxel grids of varying resolutions, each associated with its corresponding pre-trained MLP — coarse, mid, and fine levels. Moreover, a dedicated feature grid and decoder are utilized for capturing scene appearance. **Vox-Fusion [83]**, instead, combines traditional volumetric fusion methods with neural implicit representations, by leveraging a voxel-based neural implicit surface representation and using an octreebased structure to enable dynamic voxel allocation. Local scene geometry is modeled within individual voxels using a continuous SDF, encoded by an MLP along with shared feature embeddings. Furthermore, Vox-Fusion introduces an

efficient keyframe selection strategy tailored for sparse voxels, further enhancing its capability for efficient map management. **ESLAM [84]**, on the other hand, uses multi-scale axisaligned feature planes, diverging from traditional voxel grids. This approach optimizes memory usage through quadratic scaling, in contrast to the cubic growth exhibited by voxelbased models. Furthermore, ESLAM adopts TSDF as the geometric representation, increasing both convergence speed and reconstruction quality. **Co-SLAM [85]** combines the smoothness of coordinate encodings (using one-blob encoding [184]) with the fast convergence and local detail advantages of sparse parametric encodings – such as hash grids [50]. In addition, Co-SLAM introduces global bundle adjustment by sampling few rays from all previous keyframes (around 5% of pixels for each keyframe). Taking optimization a step further, **GO-SLAM [86]** is designed for real-time global optimization of camera poses and 3D reconstructions, integrating efficient LC and online full BA that utilizes the full history of input frames. Specifically, the architecture operates through three parallel threads: front-end tracking, responsible for iterative pose and depth updates along with efficient loop closing; backend tracking, focused on generating globally consistent pose and depth predictions via full BA; and instant mapping, which updates the 3D reconstruction based on the latest available poses and depths. Notably, GO-SLAM supports monocular, stereo, and RGB-D cameras. Unlike grid-based or networkbased methods, **Point-SLAM [88]** introduces a dynamic neural point cloud representation, adjusting point density based on input data information, ensuring more points in areas with higher detail and fewer points in less informative regions, based on image gradients. Color and depth are rendered by processing the neural points features through pre-trained MLPs, as in [5]. The neural point cloud expands incrementally during exploration and stabilizes as all relevant regions are incorporated, thus optimizing memory usage by compressing areas with fewer details and removing the need to model free space. In a different direction, **ToF-SLAM [89]** is the first framework tailored to lightweight ToF sensors providing very few depth measurements. It uses a multi-modal feature grid enabling both zone-level rendering tailored for ToF sparse measurements and pixel-level suited for high-resolution signals (e.g. RGB). A coarse-to-fine optimization strategy

<!-- page 9 of 25 -->

9

improves the learning of the implicit representation, while temporal information is incorporated to handle noisy ToF sensor signals. Addressing the challenge of incomplete data, **ADFP**

**[90]** incorporates an attentive depth fusion prior, derived from a TSDF obtained by fusing multiple depth images. This allows neural networks to directly utilize learned geometry and TSDFs during volume rendering to better deal with holes and unawareness of occluded structures. Overall, ADFP uses classical ray tracing, feature interpolation, occupancy prediction priors, and an attention mechanism to balance the contributions of learned geometry and the depth fusion prior. **MLM-SLAM [91]** introduces a multi-MLP hierarchical scene representation that utilizes different levels of decoders to extract detailed features. Additionally, it implements a refined tracking strategy and keyframe selection approach, enhancing system reliability, especially in challenging dynamic environments.

**Plenoxel-SLAM [92]**, instead, builds upon the Plenoxel radiance field model [62], devoid of neural networks, by using a voxel grid representation and trilinear interpolation for efficient dense mapping and tracking. It is worth mentioning that no explicit 3D mesh is currently reconstructed from the learned representation. **Structerf-SLAM [93]** uses two-layer feature grids and pre-trained decoders to decode interpolated features into RGB and depth values. During the tracking phase, three-dimensional planar features based on the Manhattan assumption improve stability and overcome the lack of texture. In the mapping stage, a planar consistency constraint is applied to rendered depth, resulting in smoother reconstructions. **KN-SLAM [96]** integrates sparse featurebased localization using HF-Net [98] with a hierarchical neural implicit representations. It consists of three concurrent threads: 1) tracking, which extracts local and global features for initial pose estimation; 2) mapping, which updates the scene representation and jointly optimizes camera poses and implicit mapping; and 3) optimization, which performs loop detection, pose graph optimization, and global refinement. **SLAIM [99]** implements a Gaussian pyramid filter on top of NeRF to perform coarse-to-fine tracking and mapping, and introduces a KL regularizer on the ray termination distribution to distinguish empty space from opaque surfaces in the scene geometry. Finally, it implements both local and global bundle adjustment. Advancing generalization, **IBD-SLAM [100]** is the first generalizable SLAM solution based on neural implicit representations, which learns an image-based depth fusion model that fuses depth maps of multiple reference views into an xyz-map representation. This model is pretrained and then applied to new RGBD videos of unseen scenes without any retraining, only requiring a light-weight pose optimization procedure. To enhance scene representation, **VPE-SLAM [104]** proposes voxel-permutohedral encoding, which can incrementally reconstruct maps of unknown scenes. It combines a sparse voxel feature grid created by an octree and multi-resolution permutohedral tetrahedral feature grids to represent the scene effectively. Furthermore, it proposes a novel local bundle adjustment module managing adjacent keyframes over a sliding window. **HERO-SLAM [105]** combines the benefits of neural implicit field and feature-metric optimization, offering increased robustness in challenging en-

vironments, such as in the presence of sudden viewpoint changes or sparsely collected frames. This, together with a hybrid optimization pipeline tailored to optimize the multi-resolution implicit fields, allows for improved performance in very challenging scenarios. Tackling computational efficiency, **LRSLAM [106]** uses low-rank tensor decomposition methods to reduce the complexity and memory required for storing the features processed by the MLPs, by leveraging Six-axis and CP decompositions. Finally, **LCP-Fusion [107]** uses a sparse voxel octree structure containing feature grids and SDF priors as a hybrid scene representation. It also proposes a sliding window selection strategy based on visual overlap to perform loop-closure, a warping loss to constrain relative poses, and SDF priors as coarse initialization for implicit features.

2) 3DGS-style RGB-D SLAM: These approaches typically exploit the advantages of 3D Gaussian Splatting, such as faster and more photorealistic rendering compared to other existing scene representations. They also offer the flexibility to increase map capacity by adding more Gaussian primitives, complete utilization of per-pixel dense photometric losses, and direct parameter gradient flow to facilitate fast optimization.

**MonoGS [108]** is the first introducing a paradigm shift in the field, by leveraging 3D Gaussians as the representation coupled with splatting rendering techniques using a single moving RGB or RGB-D camera. The framework includes several key components, such as tracking and camera pose optimization, Gaussian shape verification and regularization, mapping and keyframing, and resource allocation and pruning. The tracking phase adopts a direct optimization scheme against the 3D Gaussians. For mapping and keyframing, MonoGS integrates techniques for efficient online optimization and keyframe management, which involves selecting and maintaining a small window of keyframes based on inter-frame covisibility. Additionally, resource allocation and pruning methods are used to eliminate unstable Gaussians and avoid artifacts in the model.

Concurrently, **Photo-SLAM [109]** integrates explicit geometric features and implicit texture representations within a hyper primitives map, combining ORB features [185], rotation, scaling, density, and spherical harmonic coefficients. The framework leverages geometry-based densification and Gaussian-Pyramid-based learning to optimize camera poses while minimizing a photometric loss.

On the same track, **SplaTAM [111]** represents the scene as a collection of simplified 3D Gaussians, enabling high-quality color and depth image rendering, and includes the following key steps: Camera Tracking, minimizing re-rendering errors for precise camera pose estimation; Gaussian Densification, adding new Gaussians to the scene; Map Updating, which refines gaussian parameters across the scene.

**GS-SLAM [12]**, using 3D Gaussians together with opacity and spherical harmonics to encapsulate both scene geometry and appearance, introduces an adaptive expansion strategy that dynamically manages the addition or removal of 3D Gaussians, and a coarse-to-fine tracking technique that iteratively refines estimated camera poses. Focusing more on tracking accuracy, **GS-ICP SLAM [112]** combines two techniques - Generalized Iterative Closest Point (G-ICP) [113] and 3DGS, to

<!-- page 10 of 25 -->

10

![Image block](images/tosi2024_nerf-gs-slam-survey_p10_b2.png)

Fig. 6: 3D Gaussian Visualization. (Left) Rasterized Gaussians, (Right) Gaussians shaded to highlight the underlying geometry. Images adapted from [108].

directly use the 3D Gaussian map representation for tracking, without the need for additional post-processing. Covariances matrices are computed during the G-ICP tracking and used to initialize the 3DGS mapping, while the 3D Gaussians in the map are in turn used as 3D points and their covariances for the G-ICP tracking. This bidirectional exchange of information, facilitated by scale alignment techniques, minimizes redundant computations and enables an efficient and high-performance SLAM system.

To better address mapping challenges, **HF-GS SLAM [114]** proposes a Gaussian densification strategy guided by the rendering loss to map unobserved areas and refine reobserved regions, and incorporates regularization parameters during mapping to mitigate the forgetting problem. A regularization term is proposed to prevent overfitting and preserve details of previously visited areas. **CG-SLAM [115]** uses a novel uncertainty-aware 3D Gaussian field, by analyzing camera pose derivatives in the EWA (Elliptical Weighted Average) splatting process. To reduce overfitting and achieve a consistent Gaussian field, CG-SLAM employs techniques such as scale regularization, depth alignment, and a depth uncertainty model to guide the selection of informative Gaussian primitives. Expanding to multi-modal inputs, **MM3DGS-SLAM [186]** takes inputs from a monocular camera or RGB-D camera, along with inertial measurements. The camera pose is optimized using a combined tracking loss incorporating depth measurements and IMU pre-integration. Keyframe selection is based on image covisibility and the Naturalness Image Quality Evaluator (NIQE) metric across a sliding window. New 3D Gaussians are initialized for keyframes with low opacity and high depth error, with positions initialized using depth measurements or estimates. Scale ambiguity is tackled by solving for scaling and shift values fitting the depth estimate to the current map.

Finally, **RTG-SLAM [119]** is a real-time system for largescale environments, forcing each Gaussian to be either opaque or nearly transparent, with the opaque ones fitting the surface and dominant colors, and transparent ones fitting residual colors. Depth and color are rendered in different ways, letting single Gaussians fit a local surface alone. New gaussians are added on the fly for newly observed pixels and pixels with large color or depth errors, and are classified as stable or unstable – with the latter only being optimized to reduce complexity.

3) Submaps-based SLAM: In this category, we examine methods addressing catastrophic forgetting and scalability limitations of dense radiance field SLAM systems in large environments. Among them, **MeSLAM [6]** introduces a novel SLAM framework for large-scale environment mapping with a minimal memory footprint. By using distributed MLP networks, a global mapping module facilitates the segmentation of the environment into distinct regions, mapped by single MLPs, and coordinates the stitching of these regions during the reconstruction process. A key aspect relies upon the integration with external odometry [120], allowing for robust tracking in regions where maps intersect. Both neural network parameters and poses are optimized simultaneously.

**CP-SLAM [121]**, instead, leverages a neural point-based 3D scene representation associated with keyframes and employs a distributed-to-centralized approach to ensure consistency and cooperation among multiple agents, where frontend modules use neural point clouds and differentiable volume rendering to achieve efficient odometry, mapping, and tracking. CP-SLAM also implements loop detection and sub-map alignment techniques to mitigate pose drift and concludes with global optimization techniques such as pose graph optimization and map refinement. Focusing on spatial organization, **NISB-Map [122]** uses multiple small MLP networks to represent the large-scale environment in compact spatial blocks. A distillation procedure for overlapping Neural Implicit Spatial Block (NISBs) is implemented, minimizing density variations and ensuring geometric consistency. In this process, knowledge from the last trained NISB serves as the teacher and is distilled only within overlapping regions with the current NISB. This ensures continuity while reducing computation and training time compared to training a global NISB. Similarly, **Multiple-SLAM [123]** employs multiple SLAM agents to process scenes in blocks. Agents are deployed in the frontend to operate independently, while also facilitating the sharing and fusion of map information through the backend server. The pose estimation process efficiently determines relative poses between agents using a two-stage approach: matching keyframes through a NetVLAD-based [116] global descriptor extraction model and fine-tuning inter-agent poses through an implicit relocalization process. Conversely, the map fusion stage integrates local maps using a floating-point sparse voxel octree. Overlapping regions are handled by removing redundant voxels based on observation confidence and a reconstruction loss. **MIPS-Fusion [124]** uses a grid-free, purely neural approach with incremental allocation and on-the-fly learning of multiple neural submaps, as depicted in Figure 7. It also incorporates efficient on-the-fly learning through local bundle adjustment, distributed refinement with back-end optimization, global optimization through loop closure, and a hybrid tracking scheme, combining gradient-based and randomized optimizations via particle filtering to ensure robust performance, particularly under fast camera motions. Key features include a depth-to-TSDF loss for efficient fitness evaluation, a lightweight network for classification-based TSDF prediction, and support for parallel submap fine-tuning. Loop closure is implemented through covisibility thresholds, not allowing for correcting large drifts. **NGEL-SLAM [125]** deploys two

<!-- page 11 of 25 -->

11

tracking and mapping submodules to integrate the robust tracking capabilities of ORB-SLAM3 [110] with the scene representation provided by multiple implicit neural maps. Operating through three concurrent processes—tracking, dynamic local mapping, and loop closing—the system ensures global consistency and low latency. Loop closing optimizes poses using global BA, and the use of multiple local maps minimizes re-training time. NGEL-SLAM also incorporates uncertaintybased image rendering for optimal sub-map selection, and its scene representation is based on a sparse octree-based grid with implicit neural maps. Addressing memory efficiency, **PLGSLAM [126]** utilizes axis-aligned triplanes for highfrequency features and an MLP for global low-frequency features. This reduces memory growth from cubic to square with respect to the scene size, enhancing scene representation efficiency. PLGSLAM also integrates traditional SLAM with an end-to-end pose estimation network, introducing a localto-global BA algorithm to mitigate cumulative errors in largescale indoor scenes. The efficient management of keyframe databases enables seamless BA across all past observations. **Loopy-SLAM [9]** leverages neural point clouds in the form of submaps for local mapping and tracking. It employs frameto-model tracking with a data-driven, point-based submap generation approach, dynamically growing submaps based on camera motion during scene exploration. Global place recognition triggers loop closures online, enabling robust pose graph optimization for global alignment of submaps and trajectory, with the point-based representation facilitating efficient map corrections. **NEWTON [127]** introduces a view-centric neural field-based mapping method designed to overcome the limitations of a single world-centric map, such as the inability to capture dynamic content, by constructing multiple neural field models based on real-time observations and allowing camera pose updates through loop closures and scene boundary adjustments. Each neural field is represented as a multi-resolution feature grid [50] in a spherical coordinate system. This is facilitated by the coordination with the camera tracking component of ORB-SLAM2 [94]. **MAN-SLAM [128]** is a multi-agent collaborative SLAM framework with joint scene representation, distributed camera tracking, intra-to-inter loop closure, and sub-map fusion. Specifically, the intra-to-inter loop closure method is designed to achieve local (singleagent) while ensuring global map consistency. MAN-SLAM is flexible and supports single-agent and multi-agent modes. Furthermore, the authors introduce a real-world dataset suited for both settings, providing continuous-time trajectories and high-accuracy 3D meshes as ground truth.

4) Semantic RGB-D SLAM: Operating as SLAM systems, these methodologies inherently include mapping and tracking processes while also incorporating semantic information to enhance the understanding of the environment. Tailored for tasks such as object recognition or semantic segmentation, these frameworks provide a holistic approach to scene analysis - identifying and classifying objects and/or efficiently categorizing image regions into specific semantic classes (e.g. tables, chairs, etc.). Early developments focused on interactive understanding: **iLabel [7]** introduced a framework mapping 3D coordinates to color, density, and semantic values, built

![Image block](images/tosi2024_nerf-gs-slam-survey_p11_b4.png)

Fig. 7: Submaps Visualization. Neural submaps, allocated incrementally along the scanning trajectory, encode precise scene geometry and colors in their dedicated local coordinate frames. Figure from [124].

![Image block](images/tosi2024_nerf-gs-slam-survey_p11_b6.png)

(a) Room1

![Image block](images/tosi2024_nerf-gs-slam-survey_p11_b8.png)

(b) Office1

Fig. 8: Semantic Visualization. 3D semantic mesh (bottom) and its decomposition with RGB colors (top) for two scenes from the Replica [74] dataset. Images from [135].

upon iMAP. The system supports both manual user-click annotations and automatic label proposals based on semantic uncertainty, achieving efficient interactive labeling without pre-existing training data. **FR-Fusion [129]**, on the other hand, integrated neural feature fusion into iMAP by incorporating 2D feature extractors (EfficientNet or DINO-based) with latent volumetric rendering, enabling efficient feature map fusion for dynamic open-set segmentation while maintaining low computational requirements.

Object-centric frameworks introduced a transformative shift in the area. Among them, **vMap [132]** introduced a novel approach to object-level dense SLAM, representing each object with dedicated MLPs for watertight and complete object models, even with partial observations. The system efficiently handles object masks for segmentation while leveraging ORB-SLAM3 for tracking. **SNI-SLAM [133]** employs neural im-

<!-- page 12 of 25 -->

12

plicit representation with hierarchical semantic encoding, featuring cross-attention mechanisms for integrating appearance, geometry, and semantic features, while its novel decoder ensures unidirectional interaction to prevent mutual interference. **DNS-SLAM [135]**, instead, leverages 2D semantic priors for stable camera tracking while training class-wise scene representations. By integrating semantic information with multi-view geometry, it achieves comprehensive semantic mesh reconstruction (Figure 8), while employing a novel realtime tracking strategy using lightweight coarse scene representation. The advent of 3D Gaussian Splatting introduced new approaches: **SGS-SLAM [8]** implements multi-channel optimization during mapping for visual, geometric, and semantic constraints, embedding semantic information in 3D Gaussians through additional color channels. **NEDS-SLAM [136]** employs Spatially Consistent Feature Fusion combining semantic features with Depth Anything features, using a lightweight encoder-decoder for 3D Gaussian representation and Virtual Camera View Pruning. **GS3LAM [138]** introduces Semantic Gaussian Fields with Depth-adaptive Scale Regularization and Random Sampling-based Keyframe Mapping to address scaleinvariance and forgetting challenges. Lastly, **NIS-SLAM [139]** combines high-frequency tetrahedron-based features with lowfrequency positional encoding, implementing semantic probability fusion and confidence-based pixel sampling.

5) SLAM in Dynamic Environments: Most SLAM methods fundamentally assume static environments with rigid, non-moving objects. While effective in static scenes, their performance deteriorates significantly in dynamic environments, limiting real-world applicability. In this section, we provide an overview of the methods that are specifically designed to address the challenges of accurate mapping and localization estimation in dynamic settings.

Among them, **DN-SLAM** [13] addresses this problem through integration of ORB features for object tracking, employing semantic segmentation, optical flow, and the Segment Anything Model (SAM) for precise dynamic object identification and segregation. The system preserves static regions through careful feature extraction and utilizes NeRF for dense map generation. Building upon DROID-SLAM, **DynaMoN** [142] enhances performance through integrated motion and semantic segmentation in dense bundle adjustment. It employs DeepLabV3 for semantic refinement of known object classes while incorporating motion-based filtering for unknown dynamic elements. The framework introduces a 4D scene representation using NeRF, combining implicit and explicit representations with Total Variation loss for regularization. **NID-SLAM** [144], instead, implements depthguided semantic mask enhancement for edge region consistency and accurate dynamic object detection. The system performs intelligent background inpainting using static information from previous viewpoints, while its strategic keyframe selection minimizes dynamic object presence for optimized efficiency. The framework employs multi-resolution geometric and color feature grids, jointly optimizing scene representation and camera parameters through geometric and photometric losses. **TivNe-SLAM** [145] advances dynamic scene handling through parallel tracking and mapping processes with time-

varying representation. Its two-stage optimization first associates time with 3D positions for deformation field conversion, then links time to canonical field embeddings for color and SDF computation. The system employs motion masks for dynamic object discrimination and implements an overlap-based keyframe selection strategy. **RoDyn-SLAM** [147] proposes a fusion of optical flow and semantic masks for motion detection, implementing a divide-and-conquer pose optimization that distinguishes between keyframe and non-keyframe frames. Furthermore, the system’s edge warp loss strengthens geometric constraints between adjacent frames. **DG-SLAM** [149] pioneers robust dynamic visual SLAM using 3D Gaussians, achieving precise pose estimation through adaptive Gaussian point management and hybrid camera tracking while maintaining real-time rendering capabilities. Lastly, **ONeK-SLAM [151]** integrates feature points with neural radiance fields at the object level, employing joint information for improved localization accuracy and reconstruction detail. The system effectively handles both dynamic objects and illumination variations through joint error analysis.

6) Uncertainty Estimation: Analyzing uncertainties in input data, particularly depth sensor noise, is crucial for robust SLAM processing. This includes both filtering unreliable measurements and incorporating depth uncertainty into optimization processes to prevent inaccuracies that could impact system performance. The field has begun exploring both epistemic and aleatoric uncertainty integration to enhance SLAM reliability, particularly in challenging scenarios. **OpenWorld-SLAM [154]** makes significant progress in this direction by improving upon NICE-SLAM through depth uncertainty integration from RGB-D images, IMU motion information utilization, and a novel division between foreground and background grids for diverse environment handling. This approach enhances tracking precision while maintaining NeRFbased advantages, though it highlights the need for specialized datasets with outdoor mesh models and well-characterized sensors. **UncLe-SLAM [17]** introduces a novel joint learning approach for scene geometry and aleatoric depth uncertainties using the Laplacian error distribution of input depth sensors. Its distinctive feature lies in adaptively weighting different image regions based on confidence levels, achieved without ground truth depth requirements. This adaptive mechanism not only prioritizes reliable sensor information but also accommodates various sensor configurations with distinct noise characteristics. **NVINS [155]** tackles NeRF’s computational challenges in real-time robotics applications. By combining NeRF-derived localization with Visual-Inertial Odometry under a Bayesian framework, it effectively addresses positional drift while maintaining system reliability. **CDA-SLAM [156]** bridges the gap between explicit and implicit representations through a novel uncertainty modeling approach. Its multi-level feature selection process, combining Bayesian estimation for explicit representation with ray sampling for implicit refinement, demonstrates superior performance in both quantitative and qualitative evaluations while optimizing rendering costs.

7) Event-based SLAM: While radiance field-inspired VS-LAM methods offer advantages in accurate dense reconstruction, practical scenarios involving motion blur and lighting

<!-- page 13 of 25 -->

13

![Image block](images/tosi2024_nerf-gs-slam-survey_p13_b2.png)

(a) RGB

(b) Event Input

(c) Ground Truth

Fig. 9: Overview of the DEV-Indoors Dataset [14]. (a) RGB images depicting normal, motion blur, and dark scenes with corresponding (b) event streams and (c) ground truth meshes. Images from [14].

variations pose significant challenges that affect the robustness of the mapping and tracking processes. In this section, we explore systems that utilize event cameras, leveraging their dynamic range and temporal resolution. The asynchronous event generation mechanism, triggered by a logarithmic change in luminance at a given pixel, offers advantages in low latency and high temporal resolution, potentially improving neural VSLAM’s robustness in extreme environments. While event camera-based SLAM systems are still emerging, they show promise in overcoming traditional RGB-based limitations. **EN-SLAM [14]**, as the first work to bridge event cameras with neural implicit representations, exemplifies this potential by integrating event data alongside RGB-D through an implicit neural paradigm. Its novel approach centers on a differentiable Camera Response Function (CRF) rendering technique, unifying event and RGB camera representations. The system decodes scene encoding, establishes a unified geometry and radiance representation, and decomposes shared radiance fields via differentiable CRF Mappers, while implementing optimization strategies for tracking and BA. To validate its effectiveness, EN-SLAM introduces two challenging datasets—DEV-Indoors and DEV-Reals—featuring practical motion blur and lighting variations, as shown in Fig. 9.

## B. RGB-based SLAM Methodologies

This section explores SLAM approaches that rely exclusively on color images, addressing scenarios where depth sensors prove impractical due to their limitations in outdoor environments, sensitivity to lighting conditions, and cost constraints. RGB-only SLAM, using monocular or stereo cameras, offers broader applicability across diverse environments. However, particularly in monocular setups, these methods face unique challenges due to depth ambiguity and the absence of geometric priors, resulting in slower optimization convergence. We organize these approaches into distinct categories: core NeRF-style techniques (III-B1), 3DGS-style techniques (III-B2), systems leveraging external frameworks as supervision during optimization (III-B3), methods incorporating

semantic estimation (III-B4), and those addressing system uncertainty (III-B5).

1) NeRF-style RGB SLAM: **DIM-SLAM [16]** presents a SLAM system that employs neural implicit map representation alongside multi-resolution volume encoding and an MLP decoder for depth and color prediction. The framework dynamically learns scene features and decoders on-the-fly, while optimizing occupancies in a single step by fusing features across scales for improved efficiency. The introduced photometric warping loss, inspired by multi-view stereo, enforces alignment between synthesized and observed images while addressing view-dependent intensity variations. Merging classical and neural approaches, **Orbeez-SLAM [157]** integrates ORB feature-based tracking with neural radiance field modeling. The system achieves real-time performance through parallel tracking and mapping, where ORB-SLAM2- derived visual odometry handles pose estimation while Instant-NGP powers efficient map point generation and bundle adjustment optimization. On the other hand, **TT-HO-SLAM [158]** introduces an alternative ternary opacity model to overcome the limitations of binary-type opacity priors in rigid 3D scenes. The system’s hybrid odometry scheme combines volumetric and warping-based image renderings during tracking for enhanced efficiency, while implementing soft binarization of decoder networks during map initialization. Fine camera odometry adjustments occur during bundle adjustment, jointly optimized with mapping, resulting in superior speed and accuracy through theoretically-grounded opacity optimization.

2) 3DGS-style RGB SLAM: **MonoGS++ [159]** extends MonoGS to exploit DPVO [160] as an external tracker, used to estimate initial camera poses and 3D points from which 3D Gaussians are bootstrapped. Then, new Gaussians are inserted in new areas guided by planar regularization.

3) Aided Supervision: In this section, we explore RGB-based SLAM methods that use external frameworks to integrate regularization information into the optimization process, referred to as aided supervision. These frameworks include various techniques, such as supervision derived from depth estimates obtained from single or multi-view images, surface normal estimation, optical flow, and more. The incorporation of external signals is crucial for disambiguating the optimization process and to significantly improve the performance of SLAM systems using only RGB images as input.

Early efforts focused on multi-threaded architectures and depth supervision. **iMODE [161]** utilizes a multi-threaded architecture with three core processes: a localization process running ORB-SLAM2 on CPU for real-time camera pose estimation and keyframe selection, a semi-dense mapping process enhancing reconstruction through depth-rendered geometry supervision using monocular multi-view stereo methods, and a GPU-based dense reconstruction process optimizing an MLP-based neural field with view dependency and frequency separation features. The system incorporates view dependency for photometric consistency and frequency separation, using lower frequency embedding for initial input and higher frequency for the color head. Addressing similar challenges, **Hi-SLAM [163]** tackles low texture, rapid movement, and scale ambiguity through DROID-SLAM-based dense correspondence and

<!-- page 14 of 25 -->

14

monocular depth priors. Its joint depth and scale adjustment module resolves scale ambiguity during BA optimization, while Sim(3)-based pose graph bundle adjustment ensures global consistency through online loop closure.

End-to-end approaches led to innovations in feature representation and loss functions. **NICER-SLAM [18]** introduces hierarchical feature grids for SDF and color modeling, combining RGB rendering, warping, and optical flow losses with monocular depth and normal supervision. Building on this foundation, **NeRF-VO [165]** implements a two-stage approach: first combining DPVO sparse tracking with DPT and Omnidata for comprehensive depth and normal estimation, then employing Nerfacto for dense scene representation with uncertainty-aware optimization.

Recent advances have focused on sophisticated depth pro cessing and geometric modeling. **MoD-SLAM [166]** enhances depth estimation through DPT and ZoeDepth architectures with dedicated refinement, while employing multivariate Gaussian encoding for unbounded scenes. Geometric understanding has been further advanced by **Q-SLAM [168]**, which integrates quadric representations throughout its pipeline, combining DROID-SLAM tracking with quadric-based depth correction and semantic supervision. The latest developments include **MGS-SLAM [169]**, which unifies sparse visual odometry with 3D Gaussian Splatting through MVS-derived depth supervision, introducing novel depth smooth loss and adjustment mechanisms to maintain cross-representation consistency.

4) Semantic RGB SLAM: **RO-MAP** [170] breaks new ground in multi-object mapping without depth priors, integrating lightweight object-centric SLAM with individual NeRF models for each object. The system achieves real-time performance through efficient loss function design and CUDA implementation, enabling simultaneous localization and object reconstruction from monocular input. Advancing instancelevel understanding, **3DIML [171]** introduces a novel twophase approach to neural label field learning. The system first employs InstanceMap to associate 2D segmentation masks across images, creating 3D-consistent pseudo-labels, followed by InstanceLift for neural field training that resolves ambiguities and interpolates missing regions. Its InstanceLoc component enables near real-time localization, demonstrating significant speed improvements while maintaining high-quality 3D scene understanding across diverse environments.

5) Uncertainty Estimation: **NeRF-SLAM [173]** employs real-time implementations of DROID-SLAM [28] as the tracking module and Instant-NGP [50] as the hierarchical volumetric neural radiance field map. Moreover, it incorporates depth uncertainty estimation to address inherent noise in the input depth maps, used to weight the loss according to depth’s marginal covariance.

## C. LiDAR-Based SLAM Strategies

While VSLAM systems discussed so far operate successfully in smaller indoor scenarios where both RGB and dense depth data are available, their limitations become apparent in large outdoor environments where RGB-D cameras are impractical. LiDAR sensors, which provide sparse yet accurate

depth information over long distances and in a variety of outdoor conditions, play a critical role in ensuring robust mapping and localization in these settings. However, the sparsity of LiDAR data and the lack of RGB information pose challenges for dense SLAM approaches in outdoor environments. We now explore novel methodologies that exploit the precision of 3D incremental LiDAR data while leveraging radiance fieldbased scene representations to achieve dense, smooth map reconstruction, even in areas with sparse sensor coverage. Given the limited studies in this domain, we categorize the methodologies into NeRF (III-C1) and 3DGS-style (III-C2) LiDAR-based SLAM approaches.

1) NeRF-style LiDAR-based SLAM: **NeRF-LOAM [15]** pioneered this direction by introducing a framework that integrates neural odometry for 6-DoF pose estimation with neural mapping using dynamic voxel embeddings in an octree architecture. Its efficiency derives from a dynamic voxel embedding look-up table and key-scans refinement strategy, effectively addressing catastrophic forgetting during incremental mapping. Building upon this groundwork, **LONER [174]** enhanced the approach through parallel tracking and mapping threads, combining Point-to-Plane ICP for odometry with a hierarchical feature grid-encoded MLP for scene representation. Its novel dynamic margin loss function integrates multiple components to enable adaptive learning while preserving existing geometry. Recent developments have further pushed the boundaries of LiDAR-based neural SLAM. In this direction, **PIN-SLAM [176]** introduced an elastic point-based implicit neural map representation, alternating between incremental learning of local implicit signed distance fields and correspondence-free registration while incorporating efficient loop closure detection. Addressing the critical challenge of large-scale applications, **TNDF-Fusion [177]** developed a compact Tri-Pyramid implicit neural map representation with enhanced supervision through TNDF label rectification. This approach has demonstrated remarkable success in reducing memory consumption while maintaining mapping quality across scales, from roomsized environments to entire city landscapes.

2) 3DGS-style LiDAR-based SLAM: The advent of 3D Gaussian Splatting techniques has opened new possibilities for multimodal sensor fusion in SLAM applications. In this context, **LIV-GaussMap** [178] develops an integrated LiDAR-Inertial-Visual system using adaptive voxelization for surface representation. This methodology transforms LiDAR data into Gaussian distributions through voxel partitioning, while enhancing reconstruction quality by optimizing spherical harmonics and geometric structures using photometric cues. Extending these advances, **MM-Gaussian [179]** introduces a refined fusion architecture that seamlessly integrates LiDAR and visual data streams. The framework orchestrates point cloud registration with image-based refinement, while incorporating a relocalization mechanism to maintain robust tracking. By continuously refining Gaussian attributes via keyframe processing, the system achieves consistent and accurate mapping.

## IV. EXPERIMENTS AND ANALYSIS

In this section, we compare methods across datasets, focusing on tracking (visual in IV-A1, LiDAR in IV-B1) and 3D re-

<!-- page 15 of 25 -->

15

TABLE II: TUM RGB-D [72] Camera Tracking Results. ATE RMSE [cm] (↓) is used as the evaluation metric.

<table><tr><td>Method</td><td>Tracker Based on</td><td>Global BA</td><td>Loop Closure</td><td>fr1/desk</td><td>fr2/xyz</td><td>fr3/office</td><td>Avg (↓)</td></tr><tr><td colspan="8">RGB-D</td></tr><tr><td>Kintinuous [2]</td><td></td><td></td><td></td><td>3.7</td><td>2.9</td><td>3.0</td><td>3.2</td></tr><tr><td>BAD-SLAM [30]</td><td></td><td>✓</td><td>✓</td><td>1.7</td><td>1.1</td><td>1.7</td><td>1.5</td></tr><tr><td>ORB-SLAM2 [94]</td><td></td><td>✓</td><td>✓</td><td>1.6</td><td>0.4</td><td>1.0</td><td>1.0</td></tr><tr><td>Vox-Fusion [83]</td><td></td><td></td><td></td><td>3.5</td><td>1.5</td><td>26.0</td><td>10.3</td></tr><tr><td>MeSLAM [6]</td><td></td><td></td><td></td><td>6.0</td><td>6.5</td><td>7.8</td><td>6.8</td></tr><tr><td>iMAP [1]</td><td></td><td></td><td></td><td>4.9</td><td>2.0</td><td>5.8</td><td>4.2</td></tr><tr><td>GS-SLAM [187]</td><td></td><td></td><td></td><td>3.3</td><td>1.3</td><td>6.6</td><td>3.7</td></tr><tr><td>SplaTAM [111]</td><td></td><td></td><td></td><td>3.4</td><td>1.2</td><td>5.2</td><td>3.3</td></tr><tr><td>HF-GS SLAM [114]</td><td></td><td></td><td></td><td>3.4</td><td>-</td><td>5.1</td><td>-</td></tr><tr><td>MIPS-Fusion [124]</td><td></td><td></td><td>✓</td><td>3.0</td><td>1.4</td><td>4.6</td><td>3.0</td></tr><tr><td>Point-SLAM [88]</td><td></td><td></td><td></td><td>4.3</td><td>1.3</td><td>3.5</td><td>3.0</td></tr><tr><td>Loopy-SLAM [9]</td><td></td><td></td><td>✓</td><td>3.8</td><td>1.6</td><td>3.4</td><td>2.9</td></tr><tr><td>NICE-SLAM [5]</td><td></td><td></td><td></td><td>2.7</td><td>1.8</td><td>3.0</td><td>2.5</td></tr><tr><td>GS-ICP SLAM [112]</td><td>G-ICP [113]</td><td></td><td></td><td>2.7</td><td>1.8</td><td>2.7</td><td>2.4</td></tr><tr><td>vMAP [132]</td><td>ORB3 [110]</td><td></td><td></td><td>2.6</td><td>1.6</td><td>3.0</td><td>2.4</td></tr><tr><td>Co-SLAM [85]</td><td></td><td>✓</td><td></td><td>2.4</td><td>1.7</td><td>2.4</td><td>2.2</td></tr><tr><td>NIS-SLAM [139]</td><td></td><td>✓</td><td></td><td>2.3</td><td>1.6</td><td>2.4</td><td>2.1</td></tr><tr><td>LRSLAM [106]</td><td></td><td></td><td></td><td>2.5</td><td>1.0</td><td>2.8</td><td>2.1</td></tr><tr><td>ESLAM [84]</td><td></td><td></td><td></td><td>2.5</td><td>1.1</td><td>2.4</td><td>2.0</td></tr><tr><td>CG-SLAM [115]</td><td></td><td></td><td></td><td>2.4</td><td>1.2</td><td>2.5</td><td>2.0</td></tr><tr><td>IBD-SLAM [100]</td><td>SuperPoint [101] &amp; SuperGlue [102]</td><td></td><td></td><td>1.7</td><td>1.6</td><td>2.6</td><td>2.0</td></tr><tr><td>SLAIM [99]</td><td></td><td>✓</td><td></td><td>2.1</td><td>1.5</td><td>2.3</td><td>2.0</td></tr><tr><td>MonoGS [108]</td><td></td><td></td><td></td><td>1.5</td><td>1.6</td><td>1.7</td><td>1.6</td></tr><tr><td>GO-SLAM [86]</td><td>DROID [87]</td><td>✓</td><td>✓</td><td>1.5</td><td>0.6</td><td>1.3</td><td>1.1</td></tr><tr><td>RTG-SLAM [119]</td><td></td><td></td><td></td><td>1.7</td><td>0.4</td><td>1.1</td><td>1.1</td></tr><tr><td>Q-SLAM [168]</td><td>DROID [87]</td><td></td><td></td><td>1.4</td><td>0.5</td><td>1.1</td><td>1.0</td></tr><tr><td>NGEL-SLAM [125]</td><td>ORB3 [110]</td><td>✓</td><td>✓</td><td>1.5</td><td>0.5</td><td>1.0</td><td>1.0</td></tr><tr><td>ONeK-SLAM [151]</td><td>SIFT matching [152]</td><td></td><td></td><td>1.5</td><td>0.3</td><td>1.1</td><td>1.0</td></tr><tr><td colspan="8">RGB</td></tr><tr><td>DROID-SLAM [87]</td><td>-</td><td>✓</td><td></td><td>1.8</td><td>0.5</td><td>2.8</td><td>1.7</td></tr><tr><td>ORB-SLAM2 [94]</td><td>-</td><td>✓</td><td>✓</td><td>1.9</td><td>0.6</td><td>2.4</td><td>1.6</td></tr><tr><td>MonoGS [108]</td><td></td><td></td><td></td><td>4.2</td><td>4.8</td><td>4.4</td><td>4.4</td></tr><tr><td>DDN-SLAM [188]</td><td>ORB3 [110]</td><td>✓</td><td>✓</td><td>1.9</td><td>2.4</td><td>2.9</td><td>2.4</td></tr><tr><td>MGS-SLAM [169]</td><td>DPVO [160]</td><td>✓</td><td></td><td>2.3</td><td>0.4</td><td>3.0</td><td>1.9</td></tr><tr><td>DIM-SLAM [16]</td><td></td><td></td><td></td><td>2.0</td><td>0.6</td><td>2.3</td><td>1.6</td></tr><tr><td>l2-SLAM [189]</td><td></td><td></td><td></td><td>1.6</td><td>0.3</td><td>2.0</td><td>1.3</td></tr><tr><td>GO-SLAM [86]</td><td>DROID [87]</td><td>✓</td><td>✓</td><td>1.6</td><td>0.6</td><td>1.5</td><td>1.2</td></tr><tr><td>Orbez-SLAM [157]</td><td>ORB2 [94]</td><td></td><td></td><td>1.9</td><td>0.3</td><td>1.0</td><td>1.1</td></tr><tr><td>MoD-SLAM [166]</td><td>DROID [87]</td><td></td><td>✓</td><td>1.5</td><td>0.7</td><td>1.1</td><td>1.1</td></tr><tr><td>MonoGS++ [159]</td><td>DPVO [160]</td><td></td><td></td><td>1.8</td><td>0.4</td><td>0.4</td><td>0.9</td></tr></table>

construction (visual in IV-A2, LiDAR in IV-B2). Additionally, we explore novel view synthesis (IV-A3), semantic segmentation (IV-A4), and analyze performance in terms of runtime and memory usage (IV-C). In each subsequent table, we emphasize the best results within a subcategory using **bold** and highlight the absolute best in **purple**. In our analysis, we organized quantitative data from papers with a common evaluation protocol and cross-verified the results. Our priority was to include papers with consistent benchmarks, ensuring a reliable basis for comparison across multiple sources. Although not exhaustive, this approach guarantees the inclusion of methods with verifiable results and a shared evaluation framework in our tables. For performance analysis, we utilized methods with available code to report runtime and memory requirements on a common hardware platform, a single NVIDIA 3090 GPU. For specific implementation details of each method, readers are encouraged to refer to the original papers.

## A. Visual SLAM Evaluation

In line with existing protocols, this section compares SLAM systems using RGB-D or RGB data. We evaluate tracking, 3D reconstruction, rendering, and consider runtime and memory usage. Additionally, for methods that estimate semantic segmentation, we assess the quality of the semantic segmentation using the mIoU metric. Specifically, results are presented on the TUM-RGB-D [72], Replica [74], and ScanNet [73] datasets. For semantic segmentation evaluation, we focus on the Replica dataset, as it provides ground truth semantic labels, allowing for a comprehensive comparison of the semantic segmentation performance.

1) Tracking: **TUM-RGB-D.** Table II provides a thorough analysis of camera tracking results on three scenes of the TUM RGB-D dataset, marked by challenging conditions such

TABLE III: ScanNet [73] Camera Tracking Results. ATE RMSE [cm] (↓) is used as the evaluation metric.

<table><tr><td>Method</td><td>Tracker Based on</td><td>Global BA</td><td>Loop Closure</td><td>0000</td><td>0059</td><td>0106</td><td>0169</td><td>0181</td><td>0207</td><td>Avg (↓)</td></tr><tr><td colspan="11">RGB-D</td></tr><tr><td>DROID-SLAM (VO) [87]</td><td></td><td></td><td></td><td>8.00</td><td>11.30</td><td>9.97</td><td>8.64</td><td>7.38</td><td>-</td><td>-</td></tr><tr><td>DROID-SLAM [87]</td><td></td><td>✓</td><td></td><td>5.36</td><td>7.72</td><td>7.06</td><td>8.01</td><td>6.97</td><td>-</td><td>-</td></tr><tr><td>iMAP [1]</td><td></td><td></td><td></td><td>55.95</td><td>32.06</td><td>17.50</td><td>70.51</td><td>32.10</td><td>11.91</td><td>36.67</td></tr><tr><td>ADFP [90]</td><td></td><td></td><td></td><td>-</td><td>10.50</td><td>7.48</td><td>9.31</td><td>-</td><td>5.67</td><td>-</td></tr><tr><td>Point-SLAM [88]</td><td></td><td></td><td></td><td>10.24</td><td>7.81</td><td>8.65</td><td>22.16</td><td>14.77</td><td>9.54</td><td>12.19</td></tr><tr><td>SplaTAM [11]</td><td></td><td></td><td></td><td>12.83</td><td>10.10</td><td>17.72</td><td>12.08</td><td>11.10</td><td>7.46</td><td>11.88</td></tr><tr><td>MIPS-Fusion [124]</td><td></td><td></td><td>✓</td><td>7.9-</td><td>10.7-</td><td>9.7-</td><td>9.7-</td><td>14.2-</td><td>7.8-</td><td>10.0-</td></tr><tr><td>Vox-Fusion [83]</td><td></td><td></td><td></td><td>8.39</td><td>-</td><td>7.44</td><td>6.53</td><td>12.20</td><td>5.57</td><td>-</td></tr><tr><td>NEDS-SLAM [136]</td><td></td><td></td><td></td><td>12.34</td><td>-</td><td>-</td><td>11.21</td><td>10.35</td><td>6.56</td><td>-</td></tr><tr><td>NeuV-SLAM [190]</td><td></td><td></td><td></td><td>12.71</td><td>9.70</td><td>8.50</td><td>8.92</td><td>12.72</td><td>5.61</td><td>9.68</td></tr><tr><td>NICE-SLAM [5]</td><td></td><td></td><td></td><td>8.64</td><td>12.25</td><td>8.09</td><td>10.28</td><td>12.93</td><td>5.59</td><td>9.63</td></tr><tr><td>Co-SLAM [85]</td><td></td><td>✓</td><td></td><td>7.18</td><td>12.29</td><td>9.57</td><td>6.62</td><td>13.43</td><td>7.13</td><td>9.37</td></tr><tr><td>DG-SLAM</td><td>DROID [87]</td><td>✓</td><td></td><td>7.9-</td><td>11.5-</td><td>8.0-</td><td>8.3-</td><td>7.3-</td><td>8.2-</td><td>8.6-</td></tr><tr><td>VPE-SLAM [104]</td><td></td><td></td><td></td><td>9.24</td><td>9.22</td><td>7.37</td><td>6.06</td><td>14.51</td><td>4.91</td><td>8.55</td></tr><tr><td>CG-SLAM [115]</td><td></td><td></td><td></td><td>7.09</td><td>7.46</td><td>8.88</td><td>8.16</td><td>11.60</td><td>5.34</td><td>8.08</td></tr><tr><td>NIS-SLAM [139]</td><td></td><td>✓</td><td></td><td>-</td><td>8.70</td><td>9.62</td><td>8.35</td><td>5.64</td><td>7.10</td><td>7.88</td></tr><tr><td>Loopsy-SLAM [9]</td><td></td><td></td><td>✓</td><td>4.2-</td><td>7.5-</td><td>8.3-</td><td>7.5-</td><td>10.6-</td><td>7.9-</td><td>7.7-</td></tr><tr><td>ESLAM [84]</td><td></td><td></td><td></td><td>7.3-</td><td>8.5-</td><td>7.5-</td><td>6.5-</td><td>9.0-</td><td>5.7-</td><td>7.4-</td></tr><tr><td>IBD-SLAM [99]</td><td>SuperPoint [101] &amp; SuperGlue [102]</td><td></td><td></td><td>6.69</td><td>9.07</td><td>7.17</td><td>6.34</td><td>-</td><td>-</td><td>-</td></tr><tr><td>ONeK-SLAM [151]</td><td>SIFT matching [152]</td><td></td><td></td><td>5.36</td><td>5.86</td><td>8.82</td><td>8.08</td><td>-</td><td>6.76</td><td>-</td></tr><tr><td>LCP-Fusion [107]</td><td></td><td></td><td></td><td>-</td><td>7.56</td><td>-</td><td>5.91</td><td>10.18</td><td>6.29</td><td>-</td></tr><tr><td>Structerf-SLAM [93]</td><td>ORB2 [94]</td><td></td><td></td><td>7.28</td><td>6.07</td><td>8.50</td><td>7.35</td><td></td><td>7.28</td><td></td></tr><tr><td>Vox-Fusion+ [191]</td><td></td><td></td><td>✓</td><td>6.38</td><td>7.28</td><td>6.75</td><td>5.86</td><td>13.68</td><td>4.73</td><td>7.44</td></tr><tr><td>NGEL-SLAM [125]</td><td>ORB3 [110]</td><td>✓</td><td>✓</td><td>7.23</td><td>6.98</td><td>7.95</td><td>6.12</td><td>10.14</td><td>6.27</td><td>7.44</td></tr><tr><td>DNS-SLAM [135]</td><td></td><td>✓</td><td></td><td>5.42</td><td>5.20</td><td>9.11</td><td>7.70</td><td>10.12</td><td>4.91</td><td>7.07</td></tr><tr><td>LRSLAM [106]</td><td></td><td></td><td></td><td>5.8-</td><td>8.2-</td><td>7.6-</td><td>6.5-</td><td>8.4-</td><td>5.6-</td><td>7.0-</td></tr><tr><td>SNI-SLAM [133]</td><td></td><td></td><td></td><td>6.90</td><td>7.38</td><td>7.19</td><td>4.70</td><td>-</td><td>-</td><td>-</td></tr><tr><td>GO-SLAM [86]</td><td>DROID [87]</td><td>✓</td><td>✓</td><td>5.35</td><td>7.52</td><td>7.03</td><td>7.74</td><td>6.84</td><td>4.78</td><td>6.54</td></tr><tr><td>Q-SLAM [168]</td><td>DROID [87]</td><td></td><td></td><td>5.23</td><td>7.63</td><td>7.02</td><td>7.66</td><td>6.52</td><td>-</td><td>-</td></tr><tr><td>SLAIM [99]</td><td></td><td>✓</td><td></td><td>4.56</td><td>6.12</td><td>6.9</td><td>5.82</td><td>8.88</td><td>5.69</td><td>6.32</td></tr><tr><td>MoD-SLAM [166]</td><td>DROID [87]</td><td></td><td>✓</td><td>5.27</td><td>7.44</td><td>6.73</td><td>6.48</td><td>6.14</td><td>5.31</td><td>6.23</td></tr><tr><td colspan="11">RGB</td></tr><tr><td>DROID-SLAM (VO) [87]</td><td>-</td><td></td><td></td><td>11.05</td><td>67.26</td><td>11.20</td><td>16.21</td><td>9.94</td><td>-</td><td>-</td></tr><tr><td>DROID-SLAM [87]</td><td>-</td><td>✓</td><td></td><td>5.48</td><td>9.00</td><td>6.76</td><td>7.86</td><td>7.41</td><td>-</td><td>-</td></tr><tr><td>Orbeez-SLAM [157]</td><td>ORB2 [94]</td><td></td><td></td><td>7.22</td><td>7.15</td><td>8.05</td><td>6.58</td><td>15.77</td><td>7.16</td><td>8.66</td></tr><tr><td>Hi-SLAM [163]</td><td>DROID [87]</td><td>✓</td><td>✓</td><td>6.40</td><td>7.20</td><td>6.50</td><td>8.50</td><td>7.60</td><td>8.40</td><td>7.40</td></tr><tr><td>GO-SLAM [86]</td><td>DROID [87]</td><td>✓</td><td>✓</td><td>5.94</td><td>8.27</td><td>8.07</td><td>8.42</td><td>8.29</td><td>5.31</td><td>7.38</td></tr><tr><td>Q-SLAM [168]</td><td>DROID [87]</td><td></td><td></td><td>5.77</td><td>8.46</td><td>8.38</td><td>8.74</td><td>8.76</td><td>-</td><td>-</td></tr><tr><td>MoD-SLAM [166]</td><td>DROID [87]</td><td></td><td>✓</td><td>5.39</td><td>7.78</td><td>7.64</td><td>6.79</td><td>6.58</td><td>5.63</td><td>6.64</td></tr></table>

as sparse depth sensor information and high motion blur in RGB images. Key benchmarks include established methods like Kintinuous, BAD-SLAM, and ORB-SLAM2, representing traditional hand-crafted baselines.

In the RGB-D setting, it is evident that most methods based on radiance field representations generally exhibit lower performance compared to reference methods like BAD-SLAM and ORB-SLAM2. One notable observation, however, is that decoupled methods using external trackers such as ORB3 and DROID, along with advanced strategies such as Global BA and LC, emerge as top performers. Specifically, NGEL-SLAM, Q-SLAM, and GO-SLAM demonstrate superior accuracy.

When shifting the focus to the RGB scenario, ORB-SLAM2 and DROID-SLAM serve as baselines, with ORB-SLAM2 exhibiting superior tracking accuracy. Orbeez-SLAM, MoD-SLAM, and MonoGS++, jointly with external tracking components, such as ORB-SLAM2, DROID-SLAM, or DPVO, leads with an ATE RMSE comparable to the one achieved by the best RGB-D methods.

These results emphasize the varied performance of SLAM frameworks, with approaches based on the latest radiance field representations exhibiting effective results in RGB-D scenarios by separating mapping and tracking processes through external tracking approaches and additional optimization strategies. However, when these latter are not applied, most methods still struggle with trajectory drift and sensitivity to noise.

**ScanNet.** Table III presents the evaluation of camera tracking methods on six scenes of the ScanNet dataset. In the RGB-D domain, standout performers are the frame-to-frame models MoD-SLAM and GO-SLAM. Both leverage wellcrafted visual odometries (such as DROID-SLAM) and LC strategies, with GO-SLAM incorporating also Global BA. Significantly, MoD-SLAM achieves the best average ATE RMSE result of 6.23. It’s worth noting that the frame-to-model system SLAIM achieves a competitive 6.32 without requiring additional trackers and by leveraging Global BA. A similar trend can be observed in the RGB case, where once again, the best results are achieved by methods employing

<!-- page 16 of 25 -->

16

![Image block](images/tosi2024_nerf-gs-slam-survey_p16_b2.png)

NICE-SLAM [5]

![Image block](images/tosi2024_nerf-gs-slam-survey_p16_b4.png)

Co-SLAM [85]

![Image block](images/tosi2024_nerf-gs-slam-survey_p16_b6.png)

ESLAM [84]

![Image block](images/tosi2024_nerf-gs-slam-survey_p16_b8.png)

PLGSLAM [126]

Fig. 10: SLAM Methods Comparison on the ScanNet [73] Dataset – Surface Reconstruction and Localization Accuracy. Ground truth trajectory in blue, estimated trajectory in orange. ATE visualized with a color bar.

TABLE IV: Replica [74] Camera Tracking Results. ATE RMSE [cm] (↓) is used as the evaluation metric.

<table><tbody><tr><td>Method</td><td>Tracker Global Loop Based on BA Closure</td><td>R0 R1 R2 O0 O1 O2 O3 O4</td><td>Avg (↓)</td></tr><tr><td colspan="4">RGB-D</td></tr><tr><td>iMAP [1] NICE-SLAM [5] ADFP [90] MIPS-Fusion [124] LCP-Fusion [107] Co-SLAM [85] ESLAM [84] MonoGS [108] Vox-Fusion [83] Point-SLAM [88] GS-SLAM [12] Vox-Fusion++ [191] SNI-SLAM [133] ONeK-SLAM [151] NIS-SLAM [139] DNS SLAM [135] VPE-SLAM [104] GS3LAM [138] SplaTAM [111] NEDS-SLAM [136] GO-SLAM [86] MoD-SLAM [166] Loopy-SLAM [9] CG-SLAM [115] HF-GS SLAM [114] GS-ICP SLAM [112]</td><td>✓✓✓SIFT matching [152]✓✓DROID [87] ✓ ✓ DROID [87] ✓✓G-ICP [113]</td><td>3.12 2.54 2.31 1.69 1.03 3.99 4.05 1.931.69 2.04 1.55 0.99 0.90 1.39 3.97 3.081.39 1.55 2.60 1.09 1.23 1.61 3.61 1.421.10 1.20 1.10 0.70 0.80 1.30 2.20 1.100.54 1.02 0.78 - 1.08 0.92 0.66 0.850.65 1.13 1.43 0.55 0.50 0.46 1.40 0.770.71 0.70 0.52 0.57 0.55 0.58 0.72 0.630.76 0.37 0.23 0.66 0.72 0.30 0.19 1.460.40 0.54 0.54 0.50 0.46 0.75 0.50 0.600.61 0.41 0.37 0.38 0.48 0.54 0.72 0.630.48 0.53 0.33 0.52 0.41 0.59 0.46 0.700.38 0.47 0.49 0.44 0.42 0.62 0.41 0.590.50 0.55 0.45 0.35 0.41 0.33 0.62 0.50- - - - - - - -0.30 0.40 0.36 0.29 0.31 0.92 0.67 0.440.49 0.46 0.38 0.34 0.35 0.39 0.62 0.600.32 0.26 0.42 0.42 0.41 0.39 0.47 0.330.27 0.25 0.28 0.67 0.21 0.33 0.30 0.650.31 0.40 0.29 0.47 0.27 0.29 0.32 0.55- - - - - - - -0.32 0.30 0.39 0.39 0.46 0.34 0.29 0.29- - - - - - - -0.24 0.24 0.28 0.26 0.40 0.29 0.22 0.350.29 0.27 0.25 0.33 0.14 0.28 0.31 0.290.19 0.34 0.16 0.21 0.26 0.23 0.21 0.380.15 0.16 0.11 0.18 0.12 0.17 0.16 0.21</td><td>2.581.951.811.19-0.860.630.580.540.520.500.480.460.460.460.450.380.370.360.350.340.330.290.270.250.16</td></tr><tr><td colspan="4">RGB</td></tr><tr><td>DROID-SLAM [87]</td><td>- ✓</td><td>- - - - - - - -</td><td>0.42</td></tr><tr><td>TT-HO-SLAM [158] NICER-SLAM [18] DIM-SLAM [16] GO-SLAM [86] MoD-SLAM [166] MGS-SLAM [169] MonoGS++ [159]</td><td>DROID [87] ✓ ✓ DROID [87] ✓ DPVO [160] ✓ DPVO [160]</td><td>4.51 0.91 7.49 0.59 1.74 1.70 0.81 3.471.36 1.60 1.14 2.12 3.23 2.12 1.42 2.010.48 0.78 0.35 0.67 0.37 0.36 0.33 0.36- - - - - - - -0.28 0.29 0.30 0.40 0.45 0.50 0.31 0.270.36 0.35 0.32 0.35 0.28 0.26 0.32 0.340.20 0.17 0.22 0.29 0.13 0.42 0.20 0.42</td><td>2.651.880.460.390.350.320.26</td></tr></tbody></table>

external trackers. Nevertheless, it is worth noting that these solutions manage to be comparable or even superior to many other SLAM methods that leverage depth information from RGB-D sensors. In Figure 10, we report some qualitative results from selected RGB-D SLAM systems on ScanNet, highlighting recent improvements in trajectory error compared to the seminal systems.

**Replica.** Table IV evaluates camera tracking across eight scenes from Replica, using higher-quality images compared to challenging counterparts like ScanNet and TUM RGB-D. The evaluation includes the reporting of ATE RMSE results for each individual scene, alongside the averaged outcomes.

On top, we report the evaluation concerning RGB-D methods. In line with observations from TUM RGB-D and Scan-Net datasets, the highest accuracy is achieved by leveraging external tracking and methodologies involving Global BA and/or LC. In particular, GO-SLAM, Loopy-SLAM, and MoD-SLAM (in its RGB-D version) once again stand out on Replica, confirming their effectiveness in optimizing camera tracking accuracy. Additionally, promising results are evident for methods utilizing 3D Gaussian Splatting, with the best results among all achieved with CG-SLAM, HF-GS SLAM and GS-ICP SLAM. This suggests that these approaches strug-

TABLE V: Replica [74] Mapping Results. L1-Depth (↓), Acc. [cm] (↓), Comp. [cm] (↓) and Comp. Ratio [%] (↑) with 5 cm threshold are used as the evaluation metrics. \* evaluates on ground truth poses.

<table><tr><td>Method</td><td>L1-Depth ↓</td><td>Acc. [cm] ↓</td><td>Comp. [cm]↓</td><td>Comp. Ratio [%]↑</td></tr><tr><td colspan="5">RGB-D</td></tr><tr><td>COLMAP [55]</td><td>-</td><td>8.69</td><td>12.12</td><td>67.62</td></tr><tr><td>TSDF [192]</td><td>7.57</td><td>1.60</td><td>3.49</td><td>86.08</td></tr><tr><td>iMAP [1]</td><td>7.64</td><td>6.95</td><td>5.33</td><td>66.60</td></tr><tr><td>GO-SLAM [86]</td><td>4.68</td><td>2.50</td><td>3.74</td><td>88.09</td></tr><tr><td>NICE-SLAM [5]</td><td>3.53</td><td>2.85</td><td>3.00</td><td>89.33</td></tr><tr><td>GO-SLAM* [86]</td><td>3.38</td><td>2.50</td><td>3.74</td><td>88.09</td></tr><tr><td>DNS SLAM [135]</td><td>3.16</td><td>2.76</td><td>2.74</td><td>91.73</td></tr><tr><td>MoD-SLAM [166]</td><td>3.11</td><td>2.13</td><td>-</td><td>-</td></tr><tr><td>ADFP [90]</td><td>3.01</td><td>2.77</td><td>2.45</td><td>92.79</td></tr><tr><td>NID-SLAM [144]</td><td>2.87</td><td>2.72</td><td>2.56</td><td>91.16</td></tr><tr><td>Vox-Fusion [83]</td><td>-</td><td>2.37</td><td>2.28</td><td>92.86</td></tr><tr><td>Vox-Fusion++ [191]</td><td>-</td><td>1.44</td><td>2.43</td><td>92.37</td></tr><tr><td>Q-SLAM [9]</td><td>1.87</td><td>-</td><td>-</td><td>-</td></tr><tr><td>CG-SLAM [115]</td><td>-</td><td>1.01</td><td>2.84</td><td>88.51</td></tr><tr><td>VPE-SLAM [104]</td><td>1.52</td><td>2.14</td><td>-</td><td>93.61</td></tr><tr><td>Co-SLAM [85]</td><td>1.51</td><td>-</td><td>-</td><td>-</td></tr><tr><td>HERO-SLAM [105]</td><td>1.41</td><td>2.62</td><td>2.15</td><td>93.22</td></tr><tr><td>NGEL-SLAM [125]</td><td>1.28</td><td>-</td><td>-</td><td>-</td></tr><tr><td>ESLAM [84]</td><td>1.18</td><td>-</td><td>-</td><td>-</td></tr><tr><td>SplaTAM [111]</td><td>0.72</td><td>-</td><td>-</td><td>-</td></tr><tr><td>HF-GS SLAM [114]</td><td>0.52</td><td>-</td><td>-</td><td>-</td></tr><tr><td>NEDS-SLAM [136]</td><td>0.47</td><td>-</td><td>-</td><td>-</td></tr><tr><td>Point-SLAM [88]</td><td>0.44</td><td>1.41</td><td>3.10</td><td>88.89</td></tr><tr><td>NIS-SLAM [139]</td><td>-</td><td>1.48</td><td>2.44</td><td>92.49</td></tr><tr><td>Loopy-SLAM [9]</td><td>0.35</td><td>-</td><td>-</td><td>-</td></tr><tr><td colspan="5">RGB</td></tr><tr><td>MGS-SLAM [169]</td><td>7.77</td><td>7.51</td><td>3.64</td><td>82.71</td></tr><tr><td>NeRF-SLAM [173]</td><td>4.49</td><td>-</td><td>-</td><td>-</td></tr><tr><td>DIM-SLAM [16]</td><td>-</td><td>4.03</td><td>4.20</td><td>79.60</td></tr><tr><td>GO-SLAM [86]</td><td>4.39</td><td>3.81</td><td>4.79</td><td>78.00</td></tr><tr><td>NICER-SLAM [18]</td><td>-</td><td>3.65</td><td>4.16</td><td>79.37</td></tr><tr><td>Hi-SLAM [163]</td><td>3.63</td><td>3.62</td><td>4.59</td><td>80.60</td></tr><tr><td>MoD-SLAM [166]</td><td>3.23</td><td>2.48</td><td>-</td><td>-</td></tr><tr><td>Q-SLAM [9]</td><td>2.76</td><td>-</td><td>-</td><td>-</td></tr></table>

gle with noise and work best in simpler situations, showing less reliability in complex conditions – similarly to what was observed in the TUM RGB-D and ScanNet datasets.

At the bottom, we collect results achieved by RGB-only frameworks. Again, we observe a substantial superiority of frame-to-frame models that exploit external trackers such as DROID-SLAM or DPVO, with MonoGS++ standing among the others in terms of average accuracy.

2) Mapping: **Replica.** In Table V, we provide mapping results according to the evaluation protocol proposed in [5], highlighting the performance in terms of both 3D reconstruction and 2D depth estimation on the Replica dataset. Examining the table, a noticeable progression in both 3D reconstruction and 2D depth estimation metrics is observed, showing an improvement from iMap to more recent methods such as VPE-SLAM and HERO-SLAM. Notably, Loopy-SLAM leads in the L1-Depth metric, closely followed by Point-SLAM. This

<!-- page 17 of 25 -->

17

![Image block](images/tosi2024_nerf-gs-slam-survey_p17_b2.png)

ESLAM [84]

![Image block](images/tosi2024_nerf-gs-slam-survey_p17_b4.png)

GO-SLAM [86]

![Image block](images/tosi2024_nerf-gs-slam-survey_p17_b6.png)

Point-SLAM [88]

![Image block](images/tosi2024_nerf-gs-slam-survey_p17_b8.png)

Loopy-SLAM [9]

![Image block](images/tosi2024_nerf-gs-slam-survey_p17_b10.png)

Ground-Truth

Fig. 11: SLAM Methods Comparison on the Replica [74] Dataset – Mapping. Images sourced from [9].

suggests that the neural point representation holds significant promise for generating highly accurate scene reconstructions. In terms of 3D error metrics, Vox-Fusion++, NIS-SLAM, HERO-SLAM and VPE-SLAM outperform other methods, even surpassing hand-crafted approaches like COLMAP and TSDF. Point-SLAM performs comparably, excelling in the Accuracy metric with a value of 1.41, while CG-SLAM achieves the best overall performance with a score of 1.01. Notably, despite GO-SLAM’s notable achievements in tracking, it holds a relatively low position in this ranking, indicating challenges for the mapping process. In Figure 11, qualitatives from a subset of reviewed systems on Replica are presented, emphasizing specific improvements achieved by recent methods in the mapping process.

Shifting the focus to RGB methods, NICER-SLAM and Hi-SLAM show a balanced performance with competitive scores in both Accuracy and Completion metrics. However, among these, MoD-SLAM stands out as the most accurate, while MGS-SLAM achieves the highest completion rate. Notably, Q-SLAM achieves the best L1-Depth metric with a score of 2.76. Nonetheless, the distinction among different methods in the RGB context is less pronounced compared to RGB-D scenarios. As expected, methods relying solely on RGB perform less favorably than those leveraging depth sensor information, with iMAP being the only exception to this trend. This emphasizes the crucial role of depth sensors in SLAM and points towards the potential for advancements in RGB-only methodologies.

3) Image Rendering: **Replica.** Table VI presents the rendering quality evaluation on Replica’s training input views, following the standard evaluation protocol established by Point-SLAM and NICE-SLAM.

On top, we focus on RGB-D frameworks: recent solutions, particularly those based on Gaussian Splatting or neural points such as Point-SLAM, achieve significantly better average metrics in PSNR, SSIM, and LPIPS compared to earlier neural SLAM methods (showing an improvement of over 10dB in PSNR). These earlier approaches relied on multi-resolution feature grids like NICE-SLAM or voxel-based neural implicit surface representations like Vox-Fusion. This demonstrates that paradigms based on explicit Gaussian primitives or neural points lead to substantial improvements in image rendering. Among these, GS-ICP SLAM achieves the highest performance with an average PSNR of 38.83, highlighting the effectiveness of Gaussian-based approaches for high-quality image rendering. Regarding RGB-only methods, the adoption of the 3DGS framework enables Photo-SLAM and MonoGS++ to produce novel view renderings with superior quality compared

TABLE VI: Replica [74] Train View Rendering Results. We report the PSNR ↑ as main error metric.

<table><tbody><tr><td>Method</td><td>R0 R1 R2 O0 O1 O2 O3 O4</td><td>Avg</td></tr><tr><td colspan="3">RGB-D</td></tr><tr><td>Vox-Fusion [83] NICE-SLAM [5] GO-SLAM [86] ESLAM [84] MoD-SLAM [166] SplaTAM [111] GS-SLAM [12] NEDS-SLAM [136] Point-SLAM [88] Q-SLAM [168] Loopy-SLAM [9] NIDS-SLAM [193] HF-GS SLAM [114] GS3LAM [138] MonoGS [108] GS-ICP SLAM [112]</td><td>22.39 22.36 23.92 27.79 29.83 20.33 23.47 25.2122.12 22.47 24.52 29.07 30.34 19.66 22.23 24.94- - - - - - - -- - - - - - - -- - - - - - - -32.86 33.89 35.25 38.26 39.17 31.97 29.70 31.8131.56 32.86 32.59 38.70 41.17 32.36 32.03 32.9235.23 34.86 35.16 37.53 39.71 32.68 31.07 31.8232.40 34.08 35.50 38.26 39.16 33.99 33.48 33.4933.24 34.81 34.16 39.32 39.51 34.08 32.65 34.93- - - - - - - -33.16 35.18 36.49 40.22 38.90 34.22 34.74 33.2433.06 35.74 37.21 41.12 41.11 33.56 33.21 34.4833.67 35.80 35.96 40.28 41.21 34.30 34.27 34.5934.83 36.43 37.49 39.95 42.09 36.24 36.70 36.0735.37 37.80 38.50 43.13 43.26 36.93 36.90 38.75</td><td>24.4124.4227.3827.8029.9534.1134.2734.7635.1735.3435.4735.7636.1936.2637.5038.83</td></tr><tr><td colspan="3">RGB</td></tr><tr><td>GO-SLAM [86] NICER-SLAM [18] MoD-SLAM [166] MGS-SLAM [169] Q-SLAM [168] Photo-SLAM [109] MonoGS++ [159]</td><td>- - - - - - - -25.33 23.92 26.12 28.54 25.86 21.95 26.13 25.47- - - - - - - -29.91 31.06 31.49 35.51 34.25 30.83 31.86 34.3829.58 32.74 31.25 36.31 37.22 30.68 30.21 31.96- - - - - - - -33.75 36.47 37.01 42.31 43.05 36.11 36.34 37.28</td><td>22.1325.4127.3132.4132.4933.3037.79</td></tr></tbody></table>

to other NeRF-style SLAM systems.

In Figure 12, we present qualitative results for image rendering from selected RGB-D SLAM systems on Replica. The latest frameworks demonstrate improved rendering of fine details, with GS-SLAM showing superior rendering quality due to its 3DGS representation.

In our analysis, we concur with the concerns raised in the SplaTAM paper regarding the evaluation of rendering results on the Replica dataset. Assessing the same training views used as input may introduce biases due to high model capacity and potential overfitting. We support exploring alternative methods for evaluating novel view rendering in this context, acknowledging the limitations of current SLAM benchmarks.

4) Semantic Segmentation Results: **Replica.** Table VII presents a comparative analysis of state-of-the-art RGB-D semantic SLAM methods on the Replica dataset [74], using the mIoU metric for evaluating the semantic segmentation performance of input views, following the evaluation protocol from SemGauss-SLAM [194]. The table highlights the use of external priors, such Dinov2 [134] or hand-made semantic segmentation masks [138], by some of these methods to improve their semantic understanding capabilities. Among the compared methods, SemGauss-SLAM achieves the highest mIoU scores across all eight scenes of Replica, demonstrating its superior performance in semantic segmentation.

<!-- page 18 of 25 -->

18

![Image block](images/tosi2024_nerf-gs-slam-survey_p18_b2.png)

NICE-SLAM [5]

Co-SLAM [85]

ESLAM [84]

GS-SLAM [12]

Ground-Truth

Fig. 12: SLAM Methods Comparison on the Replica [74] Dataset– Image Rendering. Images sourced from [12].

TABLE VII: Replica [74] Semantic Results. Quantitative comparison of input views semantic segmentation performance on the Replica dataset [74] using the mIoU metric.

| Method | External Priors | R0 | R1 | R2 | O0 | O1 | O2 | O3 | O4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | RGB-D |  |  |  |  |  |  |
| DNS-SLAM [135] | GT semantics | 88.32 | 84.90 | 81.20 | 84.66 | - | - | - | - |
| SNI-SLAM [133] | Dinov2 [134] | 88.42 | 87.43 | 86.16 | 87.63 | 78.63 | 86.49 | 74.01 | 80.22 |
| NEDS-SLAM [136] | DINO [134] | 90.73 | 91.20 | - | 90.42 | - | - | - | - |
| SemGauss-SLAM [194] | Dinov2 [134] | 92.81 | 94.10 | 94.72 | 95.23 | 90.11 | 94.93 | 92.93 | 94.82 |
| GS3LAM [138] | GT semantics | 96.83 | 96.68 | 96.40 | 96.61 | - | - | - | - |

## B. LiDAR SLAM/Odometry Evaluation

1) Tracking: **KITTI**. Table VIII presents the evaluation of LiDAR SLAM strategies on the KITTI dataset, detailing odometry accuracy at the top and SLAM performance metrics at the bottom. The odometry section reports the average relative translational drift error (%) and highlights the performance of PIN-LO, a variant of PIN-SLAM that disables the loop closure detection correction and pose graph optimization modules. PIN-LO outperforms several LiDAR odometry systems using different map representations (feature points [195], denser voxel downsampling points [196], normal distribution transformation [197], surfels [198] and triangle meshes [199]) achieving an impressive translation error of 0.5%, competing with CT-ICP and outperforming the neural implicit approach Nerf-LOAM due to improved SDF training and robust point-to-SDF registration.

In the LiDAR SLAM evaluation at the bottom of the table VIII, the ATE RMSE [m] is used as the evaluation metric. As a representative of implicit LiDAR-based SLAM strategies, PIN-SLAM consistently outperforms state-of-the-art LiDAR SLAM systems. Specifically, PIN-SLAM achieves an average RMSE of 1.1 m on sequences with loop closure and 1.0 m over all eleven sequences. The results of PIN-LO underscore the significant improvement of PIN-SLAM in ensuring global trajectory consistency.

**Newer College**. Table IX reports the tracking accuracy on the Newer College dataset, measured in terms of ATE RMSE [cm]. Again, we can observe how PIN-SLAM consistently outperforms PIN-LO, with an average RMSE of 0.19 cm over the whole set of sequences, which is 5× lower compared to PIN-LO. This further confirms the superiority of PIN-SLAM at global trajectory tracking.

2) Mapping: **Newer College**. Table X collects the results concerning the quality of 3D reconstruction on the New College dataset – specifically, on Quad and Math Institute sequences. Accuracy and Completeness scores are used to assess the effectiveness of Nerf-LOAM and PIN-SLAM, with the latter confirming again as the best LiDAR-based SLAM system among those evaluating on this dataset. In particular,

TABLE VIII: KITTI [75] LiDAR Odometry/SLAM Results. † indicates sequences with loops and Avg.† denotes the average metric for such sequences.

<table><tr><td>Method</td><td>00</td><td>01</td><td>02</td><td>03</td><td>04</td><td>05</td><td>06</td><td>07</td><td>08</td><td>09</td><td>10</td><td>Avg.</td><td>11-21</td></tr><tr><td colspan="14">LiDAR Odometry Evaluation</td></tr><tr><td>MULLS [195]</td><td>0.56</td><td>0.64</td><td>0.55</td><td>0.71</td><td>0.41</td><td>0.30</td><td>0.30</td><td>0.38</td><td>0.78</td><td>0.48</td><td>0.59</td><td>0.52</td><td>0.65</td></tr><tr><td>CT-ICP [196]</td><td>0.49</td><td>0.76</td><td>0.52</td><td>0.72</td><td>0.39</td><td>0.25</td><td>0.27</td><td>0.31</td><td>0.81</td><td>0.49</td><td>0.48</td><td>0.50</td><td>0.59</td></tr><tr><td>SuMa-LO [198]</td><td>0.72</td><td>1.71</td><td>1.06</td><td>0.66</td><td>0.38</td><td>0.50</td><td>0.41</td><td>0.55</td><td>1.02</td><td>0.48</td><td>0.71</td><td>0.75</td><td>1.39</td></tr><tr><td>Litamin-LO [197]</td><td>0.78</td><td>2.10</td><td>0.95</td><td>0.96</td><td>1.05</td><td>0.55</td><td>0.55</td><td>0.48</td><td>1.01</td><td>0.69</td><td>0.80</td><td>0.88</td><td>-</td></tr><tr><td>Nerf-LOAM [15]</td><td>1.34</td><td>2.07</td><td>-</td><td>2.22</td><td>1.74</td><td>1.40</td><td>-</td><td>1.00</td><td>-</td><td>1.63</td><td>2.08</td><td>1.69</td><td>-</td></tr><tr><td>PIN-LO [176]</td><td>0.55</td><td>0.54</td><td>0.52</td><td>0.74</td><td>0.28</td><td>0.29</td><td>0.32</td><td>0.36</td><td>0.83</td><td>0.56</td><td>0.47</td><td>0.50</td><td></td></tr><tr><td></td><td>00†</td><td>01</td><td>02†</td><td>03</td><td>04</td><td>05†</td><td>06†</td><td>07†</td><td>08†</td><td>09†</td><td>10</td><td>Avg.†</td><td>Avg.</td></tr><tr><td colspan="14">LiDAR SLAM Evaluation</td></tr><tr><td>MULLS [195]</td><td>1.1</td><td>1.9</td><td>5.4</td><td>0.7</td><td>0.9</td><td>1.0</td><td>0.3</td><td>0.4</td><td>2.9</td><td>2.1</td><td>1.1</td><td>1.9</td><td>1.6</td></tr><tr><td>SuMa [198]</td><td>1.0</td><td>13.8</td><td>7.1</td><td>0.9</td><td>0.4</td><td>0.6</td><td>0.6</td><td>1.0</td><td>3.4</td><td>1.1</td><td>1.3</td><td>2.1</td><td>3.2</td></tr><tr><td>Litamin2 [197]</td><td>1.3</td><td>15.9</td><td>3.2</td><td>0.8</td><td>0.7</td><td>0.6</td><td>0.8</td><td>0.5</td><td>2.1</td><td>2.1</td><td>1.0</td><td>1.5</td><td>2.4</td></tr><tr><td>HLBA [200]</td><td>0.8</td><td>1.9</td><td>5.1</td><td>0.6</td><td>0.8</td><td>0.4</td><td>0.2</td><td>0.3</td><td>2.7</td><td>1.3</td><td>1.1</td><td>1.5</td><td>1.4</td></tr><tr><td>PIN-LO [176]</td><td>4.3</td><td>2.0</td><td>7.3</td><td>0.7</td><td>0.1</td><td>2.1</td><td>0.7</td><td>0.4</td><td>3.5</td><td>1.8</td><td>0.6</td><td>2.9</td><td>2.1</td></tr><tr><td>PIN-SLAM [176]</td><td>0.8</td><td>2.0</td><td>3.3</td><td>0.7</td><td>0.1</td><td>0.2</td><td>0.4</td><td>0.3</td><td>1.7</td><td>1.0</td><td>0.6</td><td>1.1</td><td>1.0</td></tr></table>

TABLE IX: Newer College [76] Camera Tracking Results. ATE RMSE [cm] (↓) is used as the evaluation metric.

| Method | 01 | 02 | quad | math_e | ug_e | cloister_e | stairs | Avg. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MULLS [195] | 2.51 | 8.39 | 0.12 | 0.35 | 0.86 | 0.41 | - | 2.11 |
| SuMa [198] | 2.03 | 3.65 | 0.28 | 0.16 | 0.09 | 0.20 | 1.85 | 1.18 |
| PIN-LO [176] | 2.21 | 4.93 | 0.09 | 0.10 | 0.07 | 0.41 | 0.06 | 1.12 |
| PIN-SLAM [176] | 0.43 | 0.30 | 0.09 | 0.09 | 0.07 | 0.18 | 0.06 | 0.19 |

TABLE X: Newer College [76] Mapping Results. Acc. [cm] (↓) and Comp. [cm] (↓) are used as the evaluation metrics.

| Method | Q Acc. [cm] ↓ | uad Comp. [cm] ↓ | Math Acc. [cm] ↓ | Institute Comp. [cm] ↓ |
| --- | --- | --- | --- | --- |
| SLAMesh [199] | 19.21 | 48.83 | 12.80 | 23.50 |
| Nerf-LOAM [15] | 12.89 | 22.21 | - | - |
| PIN-SLAM [176] | 11.55 | 15.25 | 13.70 | 21.91 |

on Quad we can appreciate a large margin in terms of completeness between PIN-SLAM and Nerf-LOAM – i.e., about 7 cm.

## C. Performance Analysis

We conclude the experimental studies by considering the efficiency of the SLAM systems reviewed so far. For this purpose, we run methods with source code publicly available and measure 1) the GPU memory requirements (as the peak memory use in GB) and 2) the average FPS (computed as the total time required to process a single sequence, divided by the total amount of frames in it) achieved on a single NVIDIA RTX 3090 board. Table XI collects the outcome of our benchmark for RGB-D and RGB systems running on Replica, sorted in increasing order of average FPS. On top, we consider RGB-D frameworks: we can notice how SplaTAM, despite its high efficiency at rendering images, is however much slower at processing both tracking and mapping simultaneously. This is also the case for hybrid methods using

<!-- page 19 of 25 -->

19

TABLE XI: Performance Evaluation: GPU memory requirements (GB) and average FPS efficiency on Replica room0 (RGB/RGB-D) and KITTI 00 sequence (LiDAR).

<table><tr><td>Method</td><td>Scene Encoding</td><td>GPU Mem. [G] ↓</td><td>Avg. FPS ↑</td></tr><tr><td colspan="4">RGB-D</td></tr><tr><td>iMAP [1]</td><td>MLP</td><td>6.44</td><td>0.13</td></tr><tr><td>SplaTAM [111]</td><td>3D Gaussians</td><td>18.54</td><td>0.14</td></tr><tr><td>Point-SLAM [88]</td><td>Neural Points + MLP</td><td>7.11</td><td>0.23</td></tr><tr><td>UncLe-SLAM [17]</td><td>Hier. Grid + MLP</td><td>8.24</td><td>0.24</td></tr><tr><td>NICE-SLAM [5]</td><td>Hier. Grid + MLP</td><td>4.70</td><td>0.61</td></tr><tr><td>ADFP [90]</td><td>Hier. Grid + MLP</td><td>3.76</td><td>0.74</td></tr><tr><td>Vox-Fusion [83]</td><td>Sparse Voxels + MLP</td><td>21.22</td><td>0.74</td></tr><tr><td>Plenoxel-SLAM [92]</td><td>Plenoxels</td><td>13.04</td><td>1.25</td></tr><tr><td>ESLAM [84]</td><td>Feature Planes + MLP</td><td>13.04</td><td>4.62</td></tr><tr><td>Co-SLAM [85]</td><td>Hash Grid + MLP</td><td>3.56</td><td>7.97</td></tr><tr><td>GO-SLAM [86]</td><td>Hash Grid + MLP</td><td>18.50</td><td>8.36</td></tr><tr><td colspan="4">RGB</td></tr><tr><td>DIM-SLAM [16]</td><td>Hier. Grid + MLP</td><td>4.78</td><td>3.14</td></tr><tr><td>Orbeez-SLAM [157]</td><td>Voxels + MLP</td><td>7.55</td><td>17.70</td></tr><tr><td>NeRF-SLAM [173]</td><td>Hash Grid + MLP</td><td>9.38</td><td>20.00</td></tr><tr><td colspan="4">LiDAR</td></tr><tr><td>Nerf-LOAM [15]</td><td>Sparse Voxel + MLP</td><td>11.58</td><td>0.24</td></tr><tr><td>PIN-SLAM [176]</td><td>Neural Points + MLP</td><td>6.93</td><td>6.67</td></tr></table>

hierarchical feature grids, on the other hand require much less GPU memory – 4 to 5× lower compared to SplaTAM. Finally, the use of more advanced representations such as hash grids or point features allows for much faster processing. This is confirmed also by the studies on the RGB-only methods, in the middle, with NeRF-SLAM resulting 6× faster than DIM-SLAM. Finally, concerning LiDAR SLAM systems, we can observe how PIN-SLAM is much more efficient than Nerf-LOAM, requiring as few as 7 GB of GPU memory while running at nearly 7 FPS, compared to the nearly 12 GB and 4 seconds per frame required by Nerf-LOAM.

This analysis highlights how, despite the great promise brought by this new generation of SLAM systems, most of them are still unsatisfactory in terms of hardware and runtime requirements, making them not yet ready for real-time applications.

## V. DISCUSSION

In this section we focus on highlighting the key findings of the survey. We will outline the main advances achieved through the most recent methodologies examined, while identifying ongoing challenges and potential avenues for future research in this area.

**Scene Representation.** The choice of scene representation is critical in current SLAM solutions, significantly affecting mapping/tracking accuracy, rendering quality, and computation. Early approaches, such as iMAP [1], used network-based methods, implicitly modeling scenes with coordinate-based MLP(s). While these provide compact, continuous modeling of the scene, they struggle with real-time reconstruction due to challenges in updating local regions and scaling for large scenes. In addition, they tend to produce over-smoothed scene reconstructions. Subsequent research has explored grid-based representations, such as multi-resolution hierarchical [5], [85] and sparse octree grids [83], [123], which have gained popularity. Grids allow for fast neighbor lookups, but require a pre-specified grid resolution, resulting in inefficient memory use in empty space and a limited ability to capture fine

details constrained by the resolution. Recent advances, such as Point-SLAM [88] and Loopy-SLAM [9], favor hybrid neural point-based representations. Unlike grids, point densities vary naturally and need not be pre-specified. Points concentrate efficiently around surfaces while assigning higher density to details, facilitating scalability and local updates compared to network-based methods. At present, point-based methods have demonstrated superior performance in 3D reconstruction, yielding highly accurate 3D surfaces, as evidenced by experiments conducted on the Replica dataset. However, similar to other NeRF-style approaches, volumetric ray sampling significantly restricts its efficiency.

Promising techniques include explicit representations based on the 3D Gaussian Splatting paradigm. Explicit representations based on 3DGS have been shown to achieve state-of-the-art rendering accuracy compared to other representations while also exhibiting faster rendering. However, these methods have several limitations, including a heavy reliance on initialization and a lack of control over primitive growth in unobserved regions. Furthermore, the original 3DGS-based scene representation requires a large number of 3D Gaussian primitives to achieve high-fidelity reconstruction, resulting in substantial memory consumption.

Despite significant progress over the past three years, ongoing research is still actively engaged in overcoming existing scene representation limitations and finding ever more effective alternatives to improve accuracy and real-time performance in SLAM.

**Catastrophic Forgetting.** Existing methods often exhibit a tendency to forget previously learned information, particularly in large scenarios or extended video sequences. In the case of network-based methods, this is attributed to their reliance on single neural networks or global models with fixed capacity, which are affected by global changes during optimization. One common approach to alleviate this problem is to train the network using sparse ray sampling with current observations while replaying keyframes from historical data. However, in large-scale incremental mapping, such a strategy results in a cumulative increase in data, requiring complex resampling procedures for memory efficiency. The forgetting problem extends to grid-based approaches. Despite efforts to address this issue, obstacles arise due to quadratic or cubic spatial complexity, which poses scalability challenges. Similarly, while explicit representations, such as 3DGS-style solutions, offer a practical workaround for catastrophic forgetting, they face challenges due to increased memory requirements and slow processing, especially in large scenes. Some methods attempt to mitigate these limitations by employing sparse frame sampling, but this leads to inefficient information sampling across 3D space, resulting in slower and less uniform model updates compared to approaches that integrate sparse ray sampling.

Eventually, some strategies recommend dividing the envi ronment into submaps and assigning local SLAM tasks to different agents. However, this introduces additional challenges in handling multiple distributed models and devising efficient strategies to manage overlapping regions while preventing the occurrence of map fusion artifacts.

**Real-Time Constraints**. Many of the techniques reviewed

<!-- page 20 of 25 -->

20

face challenges in achieving real-time processing, often failing to match the sensor frame rate. This limitation is mainly due to the chosen map data structure or the computationally intensive ray-wise rendering-based optimization, which is especially noticeable in NeRF-style SLAM methods. In particular, hybrid approaches using hierarchical grids require less GPU memory but exhibit slower runtime performance. On the other hand, advanced representations such as hash grids or sparse voxels allow for faster computation, but with higher memory requirements. Finally, despite their advantages in fast image rendering, current 3DGS-style methods still struggle to efficiently handle simultaneous tracking and mapping processing, preventing their effective use in real-time applications.

**Global Optimization.** Implementing LC and global BA requires significant computational resources, risking performance bottlenecks, especially in real-time applications. Many reviewed frame-to-model methods (e.g., iMap [1], NICE-SLAM [5], etc.) face challenges with loop closure and global bundle adjustment due to the prohibitive computational complexity of updating the entire 3D model. In contrast, frameto-frame techniques (e.g., GO-SLAM [86], etc.) facilitate global correction by executing the global BA in a background thread, which significantly improves tracking accuracy, as demonstrated in the reported experiments, although at a slower computational speed compared to real-time rates. For both approaches, the computational cost is largely due to the lack of flexibility of latent feature grids to accommodate pose corrections from loop closures. Indeed, this requires re-allocating feature grids and retraining the entire map once a loop is corrected and poses are updated. However, this challenge becomes more pronounced as the number of frames processed increases, leading to the accumulation of camera drift errors and eventually either an inconsistent 3D reconstruction or a rapid collapse of the reconstruction process.

Overall, decoupled methods, which separate the mapping and tracking processes, tend to achieve better tracking performance compared to coupled approaches. By allowing the tracking module to focus solely on camera pose estimation without the added complexity of simultaneously updating the map representation, decoupled methods can achieve more accurate and robust tracking. However, this improved accuracy and robustness come at the cost of increased computational overhead, as the independent mapping and tracking stages require separate processing pipelines and memory allocation, which may impact the overall efficiency of the SLAM system.

**NeRF vs. 3DGS in SLAM.** NeRF-style SLAM, which relies mostly on MLP(s), is well suited for novel view synthesis, mapping and tracking but faces challenges such as oversmoothing, susceptibility to catastrophic forgetting, and computational inefficiency due to its reliance on per-pixel ray marching. 3DGS bypasses per-pixel ray marching and exploits sparsity through differentiable rasterization over primitives. This benefits SLAM with an explicit volumetric representation, fast rendering, rich optimization, direct gradient flow, increased map capacity, and explicit spatial extent control. Thus, while NeRF shows a remarkable ability to synthesize novel views, its slow training speed and difficulty in adapting to SLAM are significant drawbacks. 3DGS, with its efficient

rendering, explicit representation, and rich optimization capabilities, emerges as a powerful alternative. Despite its advantages, current 3DGS-style SLAM approaches have limitations. These include scalability issues for large scenes, the lack of a direct mesh extraction algorithm (although recent methods such as [201] have been proposed), the inability to accurately encode precise geometry and, among others, the potential for uncontrollable Gaussian growth into unobserved areas, causing artifacts in rendered views and the underlying 3D structure. Moreover, the computational complexity of 3DGS-based SLAM systems is significantly higher than NeRF-based methods, which can hinder real-time performance and practical deployment, especially on resource-constrained devices. In order to mitigate these issues, recent research efforts, such as Compact-GSSLAM [202], have focused on developing compact 3D Gaussian scene representations that optimize storage efficiency while maintaining high-quality reconstruction, rapid training convergence, and real-time rendering capabilities.

**Evaluation Inconsistencies.** The lack of standardized benchmarks or online servers with well-defined evaluation protocols results in inconsistent evaluation methods, making it difficult to conduct fair comparisons between approaches and introducing inconsistencies within the methodologies pre-sented in different research papers. This is exemplified by challenges in datasets such as ScanNet [73], where ground truth poses are derived from BundleFusion [49], raising concerns about the reliability and generalizability of evaluation results. Xu et al. [203] and Hua et al. [204] both acknowledge these inconsistencies and propose solutions to address them. Xu et al. [203] introduce a comprehensive taxonomy of perturbations for SLAM in dynamic and unstructured environments, along with the Robust-SLAM dataset<sup>14</sup>, created using 3D scene models sourced from Replica, which includes diverse perturbation types and offers a consistent evaluation protocol. Similarly, Hua et al. [204] establish an open-source benchmark framework<sup>15</sup> to evaluate the performance of a wide spectrum of commonly used implicit neural representations and geometric rendering functions for examining their effectiveness in mapping and localization. They propose a novel RGB-D SLAM benchmark framework, featuring a unified evaluation protocol to assess different NeRF components effectively. These works highlight the importance of standardized benchmarks and evaluation protocols in mitigating inconsistencies and enabling more reliable and generalizable research outcomes in SLAM. However, to further address these issues, we believe it is crucial to establish online evaluation platforms with welldefined protocols, error metrics, and leaderboards for tracking, mapping, similar in spirit to the ETH3D benchmark [30]. These online benchmarks should provide high-quality ground truth data for both mapping and tracking, ensuring that the proposed methods are evaluated against reliable and accurate reference data. Moreover, we consider that they should include a dedicated evaluation protocol for novel view rendering to address overfitting risks and promote more generalizable rendering methods. In summary, by adopting standardized

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">14<a href="https://github.com/Xiaohao-Xu/SLAM-under-Perturbation/"><sub>https</sub>://github.com/Xiaohao-Xu/SLAM-under-Perturbation/</a></span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">15<a href="https://vlis2022.github.io/nerf-slam-benchmark/"><sub>https</sub>://vlis2022.github.io/nerf-slam-benchmark/</a></span></small>

<!-- page 21 of 25 -->

21

benchmarks, well-defined protocols, and high-quality ground truth data, we believe that the research community can make more informed and fair comparisons between different approaches.

**Additional Challenges.** SLAM approaches, whether traditional, deep learning based, or influenced by radiance field representations, face common challenges. One notable obstacle is the handling of dynamic scenes, which proves difficult due to the underlying assumption of a static environment, leading to artifacts in the reconstructed scene and errors in the tracking process. While some approaches attempt to address this issue, there is still significant room for improvement, especially in highly dynamic environments.

Another challenge is sensitivity to sensor noise, which includes motion blur, depth noise, and aggressive rotation, all of which affect tracking and mapping accuracy. This is further compounded by the presence of non-Lambertian objects in the scene, such as glass or metal surfaces, which introduce additional complexity due to their varying reflective properties. In the context of these challenges, it is noteworthy that many approaches often overlook explicit uncertainty estimation across input modalities, hindering a comprehensive understanding of system reliability.

Additionally, the absence of external sensors, especially depth information, poses a fundamental problem to RGB-only SLAM, leading to depth ambiguity and 3D reconstruction optimization convergence issues.

A less critical but specific issue is the quality of rendered images of the scene. Reviewed techniques often struggle with view-dependent appearance elements, such as specular reflections, due to the lack of modeling of view directions in the model, which affects rendering quality.

## VI. CONCLUSION

In summary, this overview pioneers the exploration of SLAM methods influenced by recent advances in radiance field representations. Ranging from seminal works such as iMap [1] to the latest advances, the review reveals a substantial body of literature that has emerged in just three years. Through structured classification and analysis, it highlights key limitations and innovations, providing valuable insights with comparative results across tracking, mapping, and rendering. It also identifies current open challenges, providing interesting avenues for future exploration.

## REFERENCES

[1] E. Sucar, S. Liu, J. Ortiz, and A. J. Davison, “imap: Implicit mapping and positioning in real-time,” in Proceedings of the IEEE/CVF International Conference on Computer Vision, 2021, pp. 6229–6238.

[2] R. A. Newcombe, S. Izadi, O. Hilliges, D. Molyneaux, D. Kim, A. J. Davison, P. Kohi, J. Shotton, S. Hodges, and A. Fitzgibbon, “Kinectfusion: Real-time dense surface mapping and tracking,” in IEEE ISMAR. IEEE, 2011, pp. 127–136.

[3] K. Tateno, F. Tombari, I. Laina, and N. Navab, “Cnn-slam: Real-time dense monocular slam with learned depth prediction,” in Proceedings of the IEEE conference on computer vision and pattern recognition, 2017, pp. 6243–6252.

[4] Y. Li, N. Brasch, Y. Wang, N. Navab, and F. Tombari, “Structure-slam: Low-drift monocular slam in indoor environments,” IEEE Robotics and Automation Letters, vol. 5, no. 4, pp. 6583–6590, 2020.

[5] Z. Zhu, S. Peng, V. Larsson, W. Xu, H. Bao, Z. Cui, M. R. Oswald, and M. Pollefeys, “Nice-slam: Neural implicit scalable encoding for slam,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 12 786–12 796.

[6] E. Kruzhkov, A. Savinykh, P. Karpyshev, M. Kurenkov, E. Yudin, A. Potapov, and D. Tsetserukou, “Meslam: Memory efficient slam based on neural fields,” in 2022 IEEE International Conference on Systems, Man, and Cybernetics (SMC). IEEE, 2022, pp. 430–435.

[7] S. Zhi, E. Sucar, A. Mouton, I. Haughton, T. Laidlow, and A. J. Davison, “ilabel: Revealing objects in neural fields,” IEEE Robotics and Automation Letters, vol. 8, no. 2, pp. 832–839, 2022.

[8] M. Li, S. Liu, and H. Zhou, “Sgs-slam: Semantic gaussian splatting for neural dense slam,” in European Conference on Computer Vision (ECCV), 2024.

[9] L. Liso, E. Sandstrom, V. Yugay, L. V. Gool, and M. R. Oswald, ¨ “Loopy-slam: Dense neural slam with loop closures,” 2024.

[10] R. Mur-Artal, J. M. M. Montiel, and J. D. Tardos, “Orb-slam: a versatile and accurate monocular slam system,” IEEE transactions on robotics, vol. 31, no. 5, pp. 1147–1163, 2015.

[11] M. Bloesch, J. Czarnowski, R. Clark, S. Leutenegger, and A. J. Davison, “Codeslam—learning a compact, optimisable representation for dense visual slam,” in Proceedings of the IEEE conference on computer vision and pattern recognition, 2018, pp. 2560–2568.

[12] C. Yan, D. Qu, D. Xu, B. Zhao, Z. Wang, D. Wang, and X. Li, “Gsslam: Dense visual slam with 3d gaussian splatting,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2024.

[13] C. Ruan, Q. Zang, K. Zhang, and K. Huang, “Dn-slam: A visual slam with orb features and nerf mapping in dynamic environments,” IEEE Sensors Journal, 2023.

[14] D. Qu, C. Yan, D. Wang, J. Yin, D. Xu, B. Zhao, and X. Li, “Implicit event-rgbd neural slam,” arXiv preprint arXiv:2311.11013, 2023.

[15] J. Deng, Q. Wu, X. Chen, S. Xia, Z. Sun, G. Liu, W. Yu, and L. Pei, “Nerf-loam: Neural implicit representation for large-scale incremental lidar odometry and mapping,” in Proceedings of the IEEE/CVF International Conference on Computer Vision, 2023, pp. 8218–8227.

[16] H. Li, X. Gu, W. Yuan, L. Yang, Z. Dong, and P. Tan, “Dense rgb slam with neural implicit maps,” in Proceedings of the International Conference on Learning Representations, 2023.

[17] E. Sandstrom, K. Ta, L. V. Gool, and M. R. Oswald, “Uncle-SLAM: ¨ Uncertainty learning for dense neural SLAM,” in International Conference on Computer Vision Workshops (ICCVW), 2023.

[18] Z. Zhu, S. Peng, V. Larsson, Z. Cui, M. R. Oswald, A. Geiger, and M. Pollefeys, “Nicer-slam: Neural implicit scene encoding for rgb slam,” in International Conference on 3D Vision (3DV), March 2024.

[19] G. Grisetti, R. Kummerle, C. Stachniss, and W. Burgard, “A tutorial on ¨ graph-based slam,” IEEE Intelligent Transportation Systems Magazine, vol. 2, no. 4, pp. 31–43, 2010.

[20] K. Yousif, A. Bab-Hadiashar, and R. Hoseinnezhad, “An overview to visual odometry and visual slam: Applications to mobile robotics,” Intelligent Industrial Systems, vol. 1, no. 4, pp. 289–311, 2015.

[21] C. Cadena, L. Carlone, H. Carrillo, Y. Latif, D. Scaramuzza, J. Neira, I. Reid, and J. J. Leonard, “Past, present, and future of simultaneous localization and mapping: Toward the robust-perception age,” IEEE Transactions on robotics, vol. 32, no. 6, pp. 1309–1332, 2016.

[22] T. Taketomi, H. Uchiyama, and S. Ikeda, “Visual slam algorithms: A survey from 2010 to 2016,” IPSJ Transactions on Computer Vision and Applications, vol. 9, no. 1, pp. 1–11, 2017.

[23] C. Duan, S. Junginger, J. Huang, K. Jin, and K. Thurow, “Deep learning for visual slam in transportation robotics: A review,” Transportation Safety and Environment, vol. 1, no. 3, pp. 177–184, 2019.

[24] S. Mokssit, D. B. Licea, B. Guermah, and M. Ghogho, “Deep learning techniques for visual slam: A survey,” IEEE Access, vol. 11, pp. 20 026–20 050, 2023.

[25] R. A. Newcombe, S. J. Lovegrove, and A. J. Davison, “Dtam: Dense tracking and mapping in real-time,” in 2011 international conference on computer vision. IEEE, 2011, pp. 2320–2327.

[26] R. F. Salas-Moreno, R. A. Newcombe, H. Strasdat, P. H. Kelly, and A. J. Davison, “Slam++: Simultaneous localisation and mapping at the level of objects,” in Proceedings of the IEEE conference on computer vision and pattern recognition, 2013, pp. 1352–1359.

[27] T. Whelan, S. Leutenegger, R. Salas-Moreno, B. Glocker, and A. Davison, “Elasticfusion: Dense slam without a pose graph.” Robotics: Science and Systems, 2015.

[28] Z. Teed and J. Deng, “Droid-slam: Deep visual slam for monocular, stereo, and rgb-d cameras,” Advances in neural information processing systems, vol. 34, pp. 16 558–16 569, 2021.

<!-- page 22 of 25 -->

22

[29] Q.-Y. Zhou, S. Miller, and V. Koltun, “Elastic fragments for dense scene reconstruction,” in Proceedings of the IEEE International Conference on Computer Vision, 2013, pp. 473–480.

[30] T. Schops, T. Sattler, and M. Pollefeys, “Bad slam: Bundle adjusted direct rgb-d slam,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2019, pp. 134–144.

[31] M. Nießner, M. Zollhofer, S. Izadi, and M. Stamminger, “Real-time ¨ 3d reconstruction at scale using voxel hashing,” ACM Transactions on Graphics (ToG), vol. 32, no. 6, pp. 1–11, 2013.

[32] F. Steinbrucker, C. Kerl, and D. Cremers, “Large-scale multi-resolution surface reconstruction from rgb-d sequences,” in Proceedings of the IEEE International Conference on Computer Vision, 2013, pp. 3264–3271.

[33] B. Mildenhall, P. P. Srinivasan, M. Tancik, J. T. Barron, R. Ramamoorthi, and R. Ng, “Nerf: Representing scenes as neural radiance fields for view synthesis,” Communications of the ACM, vol. 65, no. 1, pp. 99–106, 2021.

[34] B. Kerbl, G. Kopanas, T. Leimkuhler, and G. Drettakis, “3d gaussian ¨ splatting for real-time radiance field rendering,” ACM Transactions on Graphics, vol. 42, no. 4, 2023.

[35] Y. Xie, T. Takikawa, S. Saito, O. Litany, S. Yan, N. Khan, F. Tombari, J. Tompkin, V. Sitzmann, and S. Sridhar, “Neural fields in visual computing and beyond,” in Computer Graphics Forum, vol. 41, no. 2. Wiley Online Library, 2022, pp. 641–676.

[36] H. Durrant-Whyte and T. Bailey, “Simultaneous localization and mapping: part i,” IEEE robotics & automation magazine, vol. 13, no. 2, pp. 99–110, 2006.

[37] T. Bailey and H. Durrant-Whyte, “Simultaneous localization and mapping (slam): Part ii,” IEEE robotics & automation magazine, vol. 13, no. 3, pp. 108–117, 2006.

[38] S. Saeedi, M. Trentini, M. Seto, and H. Li, “Multiple-robot simultaneous localization and mapping: A review,” Journal of Field Robotics, vol. 33, no. 1, pp. 3–46, 2016.

[39] M. R. U. Saputra, A. Markham, and N. Trigoni, “Visual slam and structure from motion in dynamic environments: A survey,” ACM Computing Surveys (CSUR), vol. 51, no. 2, pp. 1–36, 2018.

[40] M. Zaffar, S. Ehsan, R. Stolkin, and K. M. Maier, “Sensors, slam and long-term autonomy: A review,” in 2018 NASA/ESA Conference on Adaptive Hardware and Systems (AHS). IEEE, 2018, pp. 285–290.

[41] J. Yang, Y. Li, L. Cao, Y. Jiang, L. Sun, and Q. Xie, “A survey of slam research based on lidar sensors,” International Journal of Sensors, vol. 1, no. 1, p. 1003, 2019.

[42] W. Zhao, T. He, A. Y. M. Sani, and T. Yao, “Review of slam techniques for autonomous underwater vehicles,” in Proceedings of the 2019 International Conference on Robotics, Intelligent Control and Artificial Intelligence, 2019, pp. 384–389.

[43] C. Chen, B. Wang, C. X. Lu, N. Trigoni, and A. Markham, “A survey on deep learning for localization and mapping: Towards the age of spatial machine intelligence,” arXiv preprint arXiv:2006.12567, 2020.

[44] W. Chen, G. Shang, A. Ji, C. Zhou, X. Wang, C. Xu, Z. Li, and K. Hu, “An overview on visual slam: From tradition to semantic,” Remote Sensing, vol. 14, no. 13, p. 3010, 2022.

[45] I. A. Kazerouni, L. Fitzgerald, G. Dooly, and D. Toal, “A survey of state-of-the-art on visual slam,” Expert Systems with Applications, vol. 205, p. 117734, 2022.

[46] Y. Tang, C. Zhao, J. Wang, C. Zhang, Q. Sun, W. X. Zheng, W. Du, F. Qian, and J. Kurths, “Perception and navigation in autonomous systems in the era of learning: A survey,” IEEE Transactions on Neural Networks and Learning Systems, 2022.

[47] M. Zollhofer, P. Stotko, A. G ¨ orlitz, C. Theobalt, M. Nießner, R. Klein, ¨ and A. Kolb, “State of the art on 3d reconstruction with rgb-d cameras,” in Computer graphics forum, vol. 37, no. 2. Wiley Online Library, 2018, pp. 625–652.

[48] J. A. Placed, J. Strader, H. Carrillo, N. Atanasov, V. Indelman, L. Carlone, and J. A. Castellanos, “A survey on active simultaneous localization and mapping: State of the art and new frontiers,” IEEE Transactions on Robotics, 2023.

[49] A. Dai, M. Nießner, M. Zollhofer, S. Izadi, and C. Theobalt, “Bundle- ¨ fusion: Real-time globally consistent 3d reconstruction using on-the-fly surface reintegration,” vol. 36, no. 4, p. 1, 2017.

[50] T. Muller, A. Evans, C. Schied, and A. Keller, “Instant neural graphics ¨ primitives with a multiresolution hash encoding,” ACM Trans. Graph., vol. 41, no. 4, pp. 102:1–102:15, Jul. 2022.

[51] Z. Li, T. Muller, A. Evans, R. H. Taylor, M. Unberath, M.-Y. Liu, and ¨ C.-H. Lin, “Neuralangelo: High-fidelity neural surface reconstruction,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2023, pp. 8456–8465.

[52] S. Peng, M. Niemeyer, L. Mescheder, M. Pollefeys, and A. Geiger, “Convolutional occupancy networks,” in Computer Vision–ECCV 2020: 16th European Conference, Glasgow, UK, August 23–28, 2020, Proceedings, Part III 16. Springer, 2020, pp. 523–540.

[53] Q. Xu, Z. Xu, J. Philip, S. Bi, Z. Shu, K. Sunkavalli, and U. Neumann, “Point-nerf: Point-based neural radiance fields,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 5438–5448.

[54] J. L. Schonberger and J.-M. Frahm, “Structure-from-motion revisited,” ¨ in Conference on Computer Vision and Pattern Recognition (CVPR), 2016.

[55] J. L. Schonberger, E. Zheng, M. Pollefeys, and J.-M. Frahm, “Pixel- ¨ wise view selection for unstructured multi-view stereo,” in European Conference on Computer Vision (ECCV), 2016.

[56] K. Deng, A. Liu, J.-Y. Zhu, and D. Ramanan, “Depth-supervised nerf: Fewer views and faster training for free,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 12 882–12 891.

[57] B. Roessle, J. T. Barron, B. Mildenhall, P. P. Srinivasan, and M. Nießner, “Dense depth priors for neural radiance fields from sparse input views,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 12 892–12 901.

[58] M. Niemeyer, J. T. Barron, B. Mildenhall, M. S. Sajjadi, A. Geiger, and N. Radwan, “Regnerf: Regularizing neural radiance fields for view synthesis from sparse inputs,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 5480–5490.

[59] K. Gao, Y. Gao, H. He, D. Lu, L. Xu, and J. Li, “Nerf: Neural radiance field in 3d vision, a comprehensive review,” arXiv preprint arXiv:2210.00379, 2022.

[60] A. S. A. Rabby and C. Zhang, “Beyondpixels: A comprehensive review of the evolution of neural radiance fields,” arXiv e-prints, pp. arXiv– 2306, 2023.

[61] A. Tewari, J. Thies, B. Mildenhall, P. Srinivasan, E. Tretschk, W. Yifan, C. Lassner, V. Sitzmann, R. Martin-Brualla, S. Lombardi et al., “Advances in neural rendering,” in Computer Graphics Forum, vol. 41, no. 2. Wiley Online Library, 2022, pp. 703–735.

[62] S. Fridovich-Keil, A. Yu, M. Tancik, Q. Chen, B. Recht, and A. Kanazawa, “Plenoxels: Radiance fields without neural networks,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 5501–5510.

[63] L. Yen-Chen, P. Florence, J. T. Barron, A. Rodriguez, P. Isola, and T.-Y. Lin, “inerf: Inverting neural radiance fields for pose estimation. in 2021 ieee,” in RSJ International Conference on Intelligent Robots and Systems (IROS), pp. 1323–1330.

[64] Z. Wang, S. Wu, W. Xie, M. Chen, and V. A. Prisacariu, “Nerf–: Neural radiance fields without known camera parameters,” arXiv preprint arXiv:2102.07064, 2021.

[65] C.-H. Lin, W.-C. Ma, A. Torralba, and S. Lucey, “Barf: Bundleadjusting neural radiance fields,” in Proceedings of the IEEE/CVF International Conference on Computer Vision, 2021, pp. 5741–5751.

[66] W. E. Lorensen and H. E. Cline, “Marching cubes: A high resolution 3d surface construction algorithm,” in Seminal graphics: pioneering efforts that shaped the field, 1998, pp. 347–353.

[67] P. Wang, L. Liu, Y. Liu, C. Theobalt, T. Komura, and W. Wang, “Neus: Learning neural implicit surfaces by volume rendering for multi-view reconstruction,” arXiv preprint arXiv:2106.10689, 2021.

[68] D. Azinovic, R. Martin-Brualla, D. B. Goldman, M. Nießner, and ´ J. Thies, “Neural rgb-d surface reconstruction,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 6290–6301.

[69] G. Chen and W. Wang, “A survey on 3d gaussian splatting,” arXiv preprint arXiv:2401.03890, 2024.

[70] T. Wu, Y.-J. Yuan, L.-X. Zhang, J. Yang, Y.-P. Cao, L.-Q. Yan, and L. Gao, “Recent advances in 3d gaussian splatting,” arXiv preprint arXiv:2403.11134, 2024.

[71] B. Fei, J. Xu, R. Zhang, Q. Zhou, W. Yang, and Y. He, “3d gaussian as a new vision era: A survey,” arXiv preprint arXiv:2402.07181, 2024.

[72] J. Sturm, N. Engelhard, F. Endres, W. Burgard, and D. Cremers, “A benchmark for the evaluation of rgb-d slam systems,” in 2012 IEEE/RSJ international conference on intelligent robots and systems. IEEE, 2012, pp. 573–580.

[73] A. Dai, A. X. Chang, M. Savva, M. Halber, T. Funkhouser, and M. Nießner, “Scannet: Richly-annotated 3d reconstructions of indoor scenes,” in Proceedings of the IEEE conference on computer vision and pattern recognition, 2017, pp. 5828–5839.

<!-- page 23 of 25 -->

23

[74] J. Straub, T. Whelan, L. Ma, Y. Chen, E. Wijmans, S. Green, J. J. Engel, R. Mur-Artal, C. Ren, S. Verma, A. Clarkson, M. Yan, B. Budge, Y. Yan, X. Pan, J. Yon, Y. Zou, K. Leon, N. Carter, J. Briales, T. Gillingham, E. Mueggler, L. Pesqueira, M. Savva, D. Batra, H. M. Strasdat, R. D. Nardi, M. Goesele, S. Lovegrove, and R. Newcombe, “The Replica dataset: A digital replica of indoor spaces,” arXiv preprint arXiv:1906.05797, 2019.

[75] A. Geiger, P. Lenz, and R. Urtasun, “Are we ready for autonomous driving? the kitti vision benchmark suite,” in Conference on Computer Vision and Pattern Recognition (CVPR), 2012.

[76] M. Ramezani, Y. Wang, M. Camurri, D. Wisth, M. Mattamala, and M. Fallon, “The newer college dataset: Handheld lidar, inertial and vision with ground truth,” in IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS). IEEE, 2020, pp. 4353–4360.

[77] M. Burri, J. Nikolic, P. Gohl, T. Schneider, J. Rehder, S. Omari, M. W. Achtelik, and R. Siegwart, “The euroc micro aerial vehicle datasets,” The International Journal of Robotics Research, vol. 35, no. 10, pp. 1157–1163, 2016.

[78] B. Glocker, S. Izadi, J. Shotton, and A. Criminisi, “Real-time rgbd camera relocalization,” in 2013 IEEE International Symposium on Mixed and Augmented Reality (ISMAR). IEEE, 2013, pp. 173–179.

[79] C. Yeshwanth, Y.-C. Liu, M. Nießner, and A. Dai, “Scannet++: A highfidelity dataset of 3d indoor scenes,” in Proceedings of the IEEE/CVF International Conference on Computer Vision, 2023, pp. 12–22.

[80] M. Denninger, M. Sundermeyer, D. Winkelbauer, Y. Zidan, D. Olefir, M. Elbadrawy, A. Lodhi, and H. Katam, “Blenderproc,” arXiv preprint arXiv:1911.01911, 2019.

[81] E. Palazzolo, J. Behley, P. Lottes, P. Giguere, and C. Stachniss, “Refusion: 3d reconstruction in dynamic environments for rgb-d cameras exploiting residuals,” in 2019 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS). IEEE, 2019, pp. 7855–7862.

[82] Y. Liu, Y. Fu, F. Chen, B. Goossens, W. Tao, and H. Zhao, “Simultaneous localization and mapping related datasets: A comprehensive survey,” arXiv preprint arXiv:2102.04036, 2021.

[83] X. Yang, H. Li, H. Zhai, Y. Ming, Y. Liu, and G. Zhang, “Voxfusion: Dense tracking and mapping with voxel-based neural implicit representation,” in 2022 IEEE International Symposium on Mixed and Augmented Reality (ISMAR). IEEE, 2022, pp. 499–507.

[84] M. M. Johari, C. Carta, and F. Fleuret, “Eslam: Efficient dense slam system based on hybrid representation of signed distance fields,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), June 2023, pp. 17 408–17 419.

[85] H. Wang, J. Wang, and L. Agapito, “Co-slam: Joint coordinate and sparse parametric encodings for neural real-time slam,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), June 2023, pp. 13 293–13 302.

[86] Y. Zhang, F. Tosi, S. Mattoccia, and M. Poggi, “Go-slam: Global optimization for consistent 3d instant reconstruction,” in Proceedings of the IEEE/CVF International Conference on Computer Vision, 2023, pp. 3727–3737.

[87] Z. Teed and J. Deng, “Droid-slam: Deep visual slam for monocular, stereo, and rgb-d cameras,” NeurIPS, vol. 34, pp. 16 558–16 569, 2021.

[88] E. Sandstrom, Y. Li, L. Van Gool, and M. R. Oswald, “Point-slam: ¨ Dense neural point cloud-based slam,” in Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), 2023.

[89] L. Xinyang, L. Yijin, T. Yanbin, B. Hujun, Z. Guofeng, Z. Yinda, and C. Zhaopeng, “Multi-modal neural radiance field for monocular dense slam with a light-weight tof sensor,” in International Conference on Computer Vision (ICCV), 2023.

[90] P. Hu and Z. Han, “Learning neural implicit through volume rendering with attentive depth fusion priors,” in Advances in Neural Information Processing Systems (NeurIPS), 2023.

[91] M. Li, J. He, Y. Wang, and H. Wang, “End-to-end rgb-d slam with multi-mlps dense neural implicit representations,” IEEE Robotics and Automation Letters, 2023.

[92] A. L. Teigen, Y. Park, A. Stahl, and R. Mester, “Rgb-d mapping and tracking in a plenoxel radiance field,” in Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision, 2024, pp. 3342–3351.

[93] H. Wang, Y. Cao, X. Wei, Y. Shou, L. Shen, Z. Xu, and K. Ren, “Structerf-slam: Neural implicit representation slam for structural environments,” Computers & Graphics, p. 103893, 2024.

[94] R. Mur-Artal and J. D. Tardos, “Orb-slam2: An open-source slam ´ system for monocular, stereo, and rgb-d cameras,” IEEE transactions on robotics, vol. 33, no. 5, pp. 1255–1262, 2017.

[95] P. F. Felzenszwalb and D. P. Huttenlocher, “Efficient graph-based image segmentation,” International journal of computer vision, vol. 59, pp. 167–181, 2004.

[96] X. Wu, Z. Liu, Y. Tian, Z. Liu, and W. Chen, “Kn-slam: Keypoints and neural implicit encoding slam,” IEEE Transactions on Instrumentation and Measurement, vol. 73, pp. 1–12, 2024.

[97] V. Lepetit, F. Moreno-Noguer, and P. Fua, “Ep n p: An accurate o (n) solution to the p n p problem,” International journal of computer vision, vol. 81, pp. 155–166, 2009.

[98] P.-E. Sarlin, C. Cadena, R. Siegwart, and M. Dymczyk, “From coarse to fine: Robust hierarchical localization at large scale,” in Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, 2019, pp. 12 716–12 725.

[99] V. Cartillier, G. Schindler, and I. Essa, “Slaim: Robust dense neural slam for online tracking and mapping,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 2862–2871.

[100] M. Yin, S. Wu, and K. Han, “Ibd-slam: Learning image-based depth fusion for generalizable slam,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), June 2024, pp. 10 563–10 573.

[101] D. DeTone, T. Malisiewicz, and A. Rabinovich, “Superpoint: Self-supervised interest point detection and description,” in Proceedings of the IEEE conference on computer vision and pattern recognition workshops, 2018, pp. 224–236.

[102] P.-E. Sarlin, D. DeTone, T. Malisiewicz, and A. Rabinovich, “SuperGlue: Learning feature matching with graph neural networks,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2020.

[103] H. Xu, J. Zhang, J. Cai, H. Rezatofighi, and D. Tao, “Gmflow: Learning optical flow via global matching,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 8121–8130.

[104] Z. Zhang, Y. Zhang, Y. Shen, L. Rong, S. Wang, X. Ouyang, and Y. Li, “Vpe-slam: Neural implicit voxel-permutohedral encoding for slam,” in 2024 IEEE International Conference on Robotics and Automation (ICRA), 2024, pp. 5104–5110.

[105] Z. Xin, Y. Yue, L. Zhang, and C. Wu, “Hero-slam: Hybrid enhanced robust optimization of neural slam,” in 2024 IEEE International Conference on Robotics and Automation (ICRA), 2024, pp. 8610–8616.

[106] H. Park, M. Park, G. Nam, and J. Kim, “Lrslam: Low-rank representation of signed distance fields in dense visual slam system,” in European Conference on Computer Vision. Springer, 2024, pp. 225–240.

[107] J. Wang, Y. Deng, Y. Yang, and Y. Yue, “Lcp-fusion: A neural implicit slam with enhanced local constraints and computable prior,” in IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2024.

[108] H. Matsuki, R. Murai, P. H. J. Kelly, and A. J. Davison, “Gaussian Splatting SLAM,” 2024.

[109] H. Huang, L. Li, H. Cheng, and S.-K. Yeung, “Photo-slam: Real-time simultaneous localization and photorealistic mapping for monocular, stereo, and rgb-d cameras,” arXiv preprint arXiv:2311.16728, 2023.

[110] C. Campos, R. Elvira, J. J. G. Rodr´ıguez, J. M. Montiel, and J. D. Tardos, “Orb-slam3: An accurate open-source library for visual, visual– ´ inertial, and multimap slam,” IEEE Transactions on Robotics, vol. 37, no. 6, pp. 1874–1890, 2021.

[111] N. Keetha, J. Karhade, K. M. Jatavallabhula, G. Yang, S. Scherer, D. Ramanan, and J. Luiten, “Splatam: Splat, track & map 3d gaussians for dense rgb-d slam,” arXiv preprint arXiv:2312.02126, 2023.

[112] S. Ha, J. Yeon, and H. Yu, “Rgbd gs-icp slam,” in European Conference on Computer Vision. Springer, 2024, pp. 180–197.

[113] A. Segal, D. Haehnel, and S. Thrun, “Generalized-icp.” in Robotics: science and systems, vol. 2, no. 4. Seattle, WA, 2009, p. 435.

[114] S. Sun, M. Mielle, A. J. Lilienthal, and M. Magnusson, “High-fidelity slam using gaussian splatting with rendering-guided densification and regularized optimization,” in IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS). IEEE, 2024.

[115] J. Hu, X. Chen, B. Feng, G. Li, L. Yang, H. Bao, G. Zhang, and Z. Cui, “Cg-slam: Efficient dense rgb-d slam in a consistent uncertaintyaware 3d gaussian field,” in European Conference on Computer Vision (ECCV), 2024.

[116] R. Arandjelovic, P. Gronat, A. Torii, T. Pajdla, and J. Sivic, “Netvlad: Cnn architecture for weakly supervised place recognition,” in Proceedings of the IEEE conference on computer vision and pattern recognition, 2016, pp. 5297–5307.

<!-- page 24 of 25 -->

24

[117] Lisong C. Sun, Neel Bhatt, Jonathan C. Liu, Zhiwen Fan, Zhangyang Wang, Todd E. Humphreys, and Ufuk Topcu, “Mm3dgs slam: Multi-modal 3d gaussian splatting for slam using vision, depth, and inertial measurements,” in RSJ International Conference on Intelligent Robots and Systems (IROS), 2024.

[118] R. Ranftl, A. Bochkovskiy, and V. Koltun, “Vision transformers for dense prediction,” ICCV, 2021.

[119] Z. Peng, T. Shao, Y. Liu, J. Zhou, Y. Yang, J. Wang, and K. Zhou, “Rtgslam: Real-time 3d reconstruction at scale using gaussian splatting,” in ACM SIGGRAPH 2024 Conference Papers, 2024, pp. 1–11.

[120] J. Park, Q.-Y. Zhou, and V. Koltun, “Colored point cloud registration revisited,” in Proceedings of the IEEE international conference on computer vision, 2017, pp. 143–152.

[121] J. Hu, M. Mao, H. Bao, G. Zhang, and Z. Cui, “CP-SLAM: Collaborative neural point-based SLAM system,” in Thirty-seventh Conference on Neural Information Processing Systems, 2023.

[122] B. Xiang, Y. Sun, Z. Xie, X. Yang, and Y. Wang, “Nisb-map: Scalable mapping with neural implicit spatial block,” IEEE Robotics and Automation Letters, 2023.

[123] S. Liu and J. Zhu, “Efficient map fusion for multiple implicit slam agents,” IEEE Transactions on Intelligent Vehicles, 2023.

[124] Y. Tang, J. Zhang, Z. Yu, H. Wang, and K. Xu, “Mips-fusion: Multi-implicit-submaps for scalable and robust online neural rgb-d reconstruction,” ACM Transactions on Graphics (TOG), vol. 42, no. 6, pp. 1–16, 2023.

[125] Y. Mao, X. Yu, K. Wang, Y. Wang, R. Xiong, and Y. Liao, “Ngel-slam: Neural implicit representation-based global consistent low-latency slam system,” arXiv preprint arXiv:2311.09525, 2023.

[126] T. Deng, G. Shen, T. Qin, J. Wang, W. Zhao, J. Wang, D. Wang, and W. Chen, “Plgslam: Progressive neural scene represenation with local to global bundle adjustment,” arXiv preprint arXiv:2312.09866, 2023.

[127] H. Matsuki, K. Tateno, M. Niemeyer, and F. Tombari, “Newton: Neural view-centric mapping for on-the-fly large-scale slam,” IEEE Robotics and Automation Letters, 2024.

[128] T. Deng, G. Shen, X. Chen, H. Shen, Y. Wang, J. Wang, and W. Chen, “Multi-agent neural slam for autonomous robots,” in IEEE/RSJ International Conference on Intelligent Robots and Systems Workshops (IROSw), 2024.

[129] K. Mazur, E. Sucar, and A. J. Davison, “Feature-realistic neural fusion for real-time, open set scene understanding,” in 2023 IEEE International Conference on Robotics and Automation (ICRA). IEEE, 2023, pp. 8201–8207.

[130] M. Tan and Q. Le, “Efficientnet: Rethinking model scaling for convolutional neural networks,” in International conference on machine learning. PMLR, 2019, pp. 6105–6114.

[131] M. Caron, H. Touvron, I. Misra, H. Jegou, J. Mairal, P. Bojanowski, and ´ A. Joulin, “Emerging properties in self-supervised vision transformers,” in Proceedings of the IEEE/CVF international conference on computer vision, 2021, pp. 9650–9660.

[132] X. Kong, S. Liu, M. Taher, and A. J. Davison, “vmap: Vectorised object mapping for neural field slam,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), June 2023, pp. 952–961.

[133] S. Zhu, G. Wang, H. Blum, J. Liu, L. Song, M. Pollefeys, and H. Wang, “Sni-slam: Semantic neural implicit slam,” arXiv preprint arXiv:2311.11016, 2023.

[134] M. Oquab, T. Darcet, T. Moutakanni, H. Vo, M. Szafraniec, V. Khalidov, P. Fernandez, D. Haziza, F. Massa, A. El-Nouby et al., “Dinov2: Learning robust visual features without supervision,” arXiv preprint arXiv:2304.07193, 2023.

[135] K. Li, M. Niemeyer, N. Navab, and F. Tombari, “Dns-slam: Dense neural semantic-informed slam,” 2024.

[136] Y. Ji, Y. Liu, G. Xie, B. Ma, Z. Xie, and H. Liu, “Neds-slam: A neural explicit dense semantic slam framework using 3d gaussian splatting,” IEEE Robotics and Automation Letters, 2024.

[137] L. Yang, B. Kang, Z. Huang, X. Xu, J. Feng, and H. Zhao, “Depth anything: Unleashing the power of large-scale unlabeled data,” arXiv preprint arXiv:2401.10891, 2024.

[138] L. Li, L. Zhang, Z. Wang, and Y. Shen, “Gs3lam: Gaussian semantic splatting slam,” in Proceedings of the 32nd ACM International Conference on Multimedia, ser. MM ’24. Association for Computing Machinery, 2024, p. 3019–3027.

[139] H. Zhai, G. Huang, Q. Hu, G. Li, H. Bao, and G. Zhang, “Nisslam: Neural implicit semantic rgb-d slam for 3d consistent scene understanding,” IEEE Transactions on Visualization and Computer Graphics, pp. 1–11, 2024.

[140] B. Cheng, A. Schwing, and A. Kirillov, “Per-pixel classification is not all you need for semantic segmentation,” Advances in neural information processing systems, vol. 34, pp. 17 864–17 875, 2021.

[141] A. Kirillov, E. Mintun, N. Ravi, H. Mao, C. Rolland, L. Gustafson, T. Xiao, S. Whitehead, A. C. Berg, W.-Y. Lo et al., “Segment anything,” arXiv preprint arXiv:2304.02643, 2023.

[142] N. Schischka, H. Schieber, M. A. Karaoglu, M. Gorgulu, F. Grotzner, ¨ A. Ladikos, N. Navab, D. Roth, and B. Busam, “Dynamon: Motionaware fast and robust camera localization for dynamic neural radiance fields,” IEEE Robotics and Automation Letters, 2024.

[143] L.-C. Chen, G. Papandreou, F. Schroff, and H. Adam, “Rethinking atrous convolution for semantic image segmentation,” arXiv preprint arXiv:1706.05587, 2017.

[144] Z. Xu, J. Niu, Q. Li, T. Ren, and C. Chen, “ NID-SLAM: Neural Implicit Representation-based RGB-D SLAM In Dynamic Environments,” 2024.

[145] C. Duan and Z. Yang, “Tivne-slam: Dynamic mapping and tracking via time-varying neural radiance fields,” in IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2024.

[146] K. He, G. Gkioxari, P. Dollar, and R. Girshick, “Mask r-cnn,” in Proceedings of the IEEE International Conference on Computer Vision (ICCV), Oct 2017.

[147] H. Jiang, Y. Xu, K. Li, J. Feng, and L. Zhang, “Rodyn-slam: Robust dynamic dense rgb-d slam with neural radiance fields,” IEEE Robotics and Automation Letters, 2024.

[148] S. Jiang, D. Campbell, Y. Lu, H. Li, and R. Hartley, “Learning to estimate hidden motions with global motion aggregation,” in Proceedings of the IEEE/CVF international conference on computer vision, 2021, pp. 9772–9781.

[149] Y. Xu, H. Jiang, Z. Xiao, J. Feng, and L. Zhang, “DG-SLAM: Robust dynamic gaussian splatting SLAM with hybrid pose optimization,” in The Thirty-eighth Annual Conference on Neural Information Processing Systems, 2024.

[150] J. Jain, J. Li, M. Chiu, A. Hassani, N. Orlov, and H. Shi, “OneFormer: One Transformer to Rule Universal Image Segmentation,” 2023.

[151] Y. Zhuge, H. Luo, R. Chen, Y. Chen, J. Yan, and Z. Jiang, “Onek-slam: A robust object-level dense slam based on joint neural radiance fields and keypoints,” in 2024 IEEE International Conference on Robotics and Automation (ICRA), 2024, pp. 10 245–10 252.

[152] D. G. Lowe, “Distinctive image features from scale-invariant keypoints,” International journal of computer vision, vol. 60, pp. 91–110, 2004.

[153] Y. Cheng, L. Li, Y. Xu, X. Li, Z. Yang, W. Wang, and Y. Yang, “Segment and track anything,” arXiv preprint arXiv:2305.06558, 2023.

[154] D. Lisus, C. Holmes, and S. Waslander, “Towards open world nerfbased slam,” in 2023 20th Conference on Robots and Vision (CRV), 2023, pp. 37–44.

[155] J. Han, L. L. Beyer, G. V. Cavalheiro, and S. Karaman, “Nvins: Robust visual inertial navigation fused with nerf-augmented camera pose regressor and uncertainty quantification,” in IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2024.

[156] S. Chen, X. Luo, Z. Lin, S. Wen, Y. Guan, H. Zhang, and W. Chen, “Bridging the gap between explicit and implicit representations: Cross-data association for vslam,” IEEE Transactions on Intelligent Transportation Systems, vol. 25, no. 12, pp. 21 252–21 266, 2024.

[157] C.-M. Chung, Y.-C. Tseng, Y.-C. Hsu, X.-Q. Shi, Y.-H. Hua, J.-F. Yeh, W.-C. Chen, Y.-T. Chen, and W. H. Hsu, “Orbeez-slam: A real-time monocular visual slam with orb features and nerf-realized mapping,” in 2023 IEEE International Conference on Robotics and Automation (ICRA). IEEE, 2023, pp. 9400–9406.

[158] J. Lin, A. Nachkov, S. Peng, L. Van Gool, and D. P. Paudel, “Ternarytype opacity and hybrid odometry for rgb-only nerf-slam,” in RSJ International Conference on Intelligent Robots and Systems (IROS), 2024.

[159] R.-W. Li, W. Ke, D. Li, L. Tian, and E. Barsoum, “MonoGS++: Fast and accurate monocular rgb gaussian slam,” in British Conference on Machine Vision (BMVC), 2024.

[160] Z. Teed, L. Lipson, and J. Deng, “Deep patch visual odometry,” arXiv preprint arXiv:2208.04726, 2022.

[161] H. Matsuki, E. Sucar, T. Laidow, K. Wada, R. Scona, and A. J. Davison, “imode: Real-time incremental monocular dense mapping using neural field,” in 2023 IEEE International Conference on Robotics and Automation (ICRA). IEEE, 2023, pp. 4171–4177.

[162] F. Ma and S. Karaman, “Sparse-to-dense: Depth prediction from sparse depth samples and a single image,” 2018.

<!-- page 25 of 25 -->

25

[163] W. Zhang, T. Sun, S. Wang, Q. Cheng, and N. Haala, “Hi-slam: Monocular real-time dense mapping with hybrid implicit fields,” IEEE Robotics and Automation Letters, 2023.

[164] A. Eftekhar, A. Sax, J. Malik, and A. Zamir, “Omnidata: A scalable pipeline for making multi-task mid-level vision datasets from 3d scans,” in Proceedings of the IEEE/CVF International Conference on Computer Vision, 2021, pp. 10 786–10 796.

[165] J. Naumann, B. Xu, S. Leutenegger, and X. Zuo, “Nerf-vo: Real-time sparse visual odometry with neural radiance fields,” IEEE Robotics and Automation Letters, 2024.

[166] H. Zhou, Z. Guo, Y. Ren, S. Liu, L. Zhang, K. Zhang, and M. Li, “Mod-slam: Monocular dense mapping for unbounded 3d scene reconstruction,” 2024.

[167] S. F. Bhat, R. Birkl, D. Wofk, P. Wonka, and M. Muller, “Zoedepth: ¨ Zero-shot transfer by combining relative and metric depth,” arXiv preprint arXiv:2302.12288, 2023.

[168] C. Peng, C. Xu, Y. Wang, M. Ding, H. Yang, M. Tomizuka, K. Keutzer, M. Pavone, and W. Zhan, “Q-SLAM: Quadric representations for monocular SLAM,” 2024.

[169] P. Zhu, Y. Zhuang, B. Chen, L. Li, C. Wu, and Z. Liu, “Mgs-slam: Monocular sparse tracking and gaussian mapping with depth smooth regularization,” IEEE Robotics and Automation Letters, 2024.

[170] X. Han, H. Liu, Y. Ding, and L. Yang, “Ro-map: Real-time multi-object mapping with neural radiance fields,” IEEE Robotics and Automation Letters, vol. 8, no. 9, pp. 5950–5957, 2023.

[171] G. Tang, K. M. Jatavallabhula, and A. Torralba, “Efficient 3d instance mapping and localization with neural fields,” 2024.

[172] J. Sun, Z. Shen, Y. Wang, H. Bao, and X. Zhou, “Loftr: Detectorfree local feature matching with transformers,” in Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, 2021, pp. 8922–8931.

[173] A. Rosinol, J. J. Leonard, and L. Carlone, “Nerf-slam: Real-time dense monocular slam with neural radiance fields,” in 2023 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS). IEEE, 2023, pp. 3437–3444.

[174] S. Isaacson, P.-C. Kung, M. Ramanagopal, R. Vasudevan, and K. A. Skinner, “Loner: Lidar only neural representations for real-time slam,” IEEE Robotics and Automation Letters, 2023.

[175] S. Rusinkiewicz and M. Levoy, “Efficient variants of the icp algorithm,” in Proceedings third international conference on 3-D digital imaging and modeling. IEEE, 2001, pp. 145–152.

[176] Y. Pan, X. Zhong, L. Wiesmann, T. Posewsky, J. Behley, and C. Stachniss, “Pin-slam: Lidar slam using a point-based implicit neural representation for achieving global map consistency,” IEEE Transactions on Robotics (TRO), vol. 40, 2024.

[177] Z. Chen, K. Zhang, H. Chen, M. Y. Wang, W. Zhang, and H. Yu, “Tndf-fusion: Implicit truncated neural distance field for lidar dense mapping and localization in large urban environments,” IEEE Robotics and Automation Letters, vol. 9, no. 9, pp. 7445–7452, 2024.

[178] S. Hong and et al., “Liv-gaussmap: Lidar-inertial-visual fusion for realtime 3d radiance field map rendering,” IEEE Robotics and Automation Letters, 2024.

[179] C. Wu, Y. Duan, X. Zhang, Y. Sheng, J. Ji, and Y. Zhang, “Mmgaussian: 3d gaussian-based multi-modal fusion for localization and reconstruction in unbounded scenes,” in RSJ International Conference on Intelligent Robots and Systems (IROS), 2024.

[180] I. Vizzo, T. Guadagnino, B. Mersch, L. Wiesmann, J. Behley, and C. Stachniss, “Kiss-icp: In defense of point-to-point icp–simple, accurate, and robust registration if done the right way,” IEEE Robotics and Automation Letters, vol. 8, no. 2, pp. 1029–1036, 2023.

[181] P. Lindenberger, P. Sarlin, and M. Pollefeys, “Lightglue: Local feature matching at light speed. arxiv 2023,” arXiv preprint arXiv:2306.13643.

[182] Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli, “Image quality assessment: from error visibility to structural similarity,” IEEE transactions on image processing, vol. 13, no. 4, pp. 600–612, 2004.

[183] R. Zhang, P. Isola, A. A. Efros, E. Shechtman, and O. Wang, “The unreasonable effectiveness of deep features as a perceptual metric,” in Proceedings of the IEEE conference on computer vision and pattern recognition, 2018, pp. 586–595.

[184] T. Muller, B. McWilliams, F. Rousselle, M. Gross, and J. Nov ¨ ak, ´ “Neural importance sampling,” ACM Transactions on Graphics (ToG), vol. 38, no. 5, pp. 1–19, 2019.

[185] E. Rublee, V. Rabaud, K. Konolige, and G. Bradski, “Orb: An efficient alternative to sift or surf,” in 2011 International conference on computer vision. Ieee, 2011, pp. 2564–2571.

[186] L. C. Sun, N. P. Bhatt, J. C. Liu, Z. Fan, Z. Wang, T. E. Humphreys, and U. Topcu, “Mm3dgs slam: Multi-modal 3d gaussian splatting for slam using vision, depth, and inertial measurements,” in IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2024.

[187] C. Yan, D. Qu, D. Wang, D. Xu, Z. Wang, B. Zhao, and X. Li, “Gsslam: Dense visual slam with 3d gaussian splatting,” arXiv preprint arXiv:2311.11700, 2023.

[188] M. Li, J. He, G. Jiang, and H. Wang, “Ddn-slam: Real-time dense dynamic neural implicit slam with joint semantic encoding,” arXiv preprint arXiv:2401.01545, 2024.

[189] G. Bae, C. Choi, H. Heo, S. M. Kim, and Y. M. Kim, “I<sup>2</sup>-slam: Inverting imaging process for robust photorealistic dense slam,” in European Conference on Computer Vision. Springer, 2024, pp. 72–89.

[190] W. Guo, B. Wang, and L. Chen, “Neuv-slam: Fast neural multiresolution voxel optimization for rgbd dense slam,” 2024.

[191] H. Zhai, H. Li, X. Yang, G. Huang, Y. Ming, H. Bao, and G. Zhang, “Vox-fusion++: Voxel-based neural implicit dense tracking and mapping with multi-maps,” arXiv preprint arXiv:2403.12536, 2024.

[192] A. Zeng, S. Song, M. Nießner, M. Fisher, J. Xiao, and T. Funkhouser, “3dmatch: Learning local geometric descriptors from rgb-d reconstructions,” in Proceedings of the IEEE conference on computer vision and pattern recognition, 2017, pp. 1802–1811.

[193] Y. Haghighi, S. Kumar, J. P. Thiran, and L. Van Gool, “Neural implicit dense semantic slam,” arXiv preprint arXiv:2304.14560, 2023.

[194] S. Zhu, R. Qin, G. Wang, J. Liu, and H. Wang, “Semgauss-slam: Dense semantic gaussian splatting slam,” arXiv preprint arXiv:2403.07494, 2024.

[195] Y. Pan, P. Xiao, Y. He, Z. Shao, and Z. Li, “Mulls: Versatile lidar slam via multi-metric linear least square,” in 2021 IEEE International Conference on Robotics and Automation (ICRA). IEEE, 2021, pp. 11 633–11 640.

[196] P. Dellenbach, J.-E. Deschaud, B. Jacquet, and F. Goulette, “Cticp: Real-time elastic lidar odometry with loop closure,” in 2022 International Conference on Robotics and Automation (ICRA). IEEE, 2022, pp. 5580–5586.

[197] M. Yokozuka, K. Koide, S. Oishi, and A. Banno, “Litamin2: Ultra light lidar-based slam using geometric approximation applied with kldivergence,” in 2021 IEEE International Conference on Robotics and Automation (ICRA). IEEE, 2021, pp. 11 619–11 625.

[198] J. Behley and C. Stachniss, “Efficient surfel-based slam using 3d laser range data in urban environments.” in Robotics: Science and Systems, vol. 2018, 2018, p. 59.

[199] J. Ruan, B. Li, Y. Wang, and Y. Sun, “Slamesh: Real-time lidar simultaneous localization and meshing,” arXiv preprint arXiv:2303.05252, 2023.

[200] X. Liu, Z. Liu, F. Kong, and F. Zhang, “Large-scale lidar consistent mapping using hierarchical lidar bundle adjustment,” IEEE Robotics and Automation Letters, vol. 8, no. 3, pp. 1523–1530, 2023.

[201] A. Guedon and V. Lepetit, “Sugar: Surface-aligned gaussian splatting ´ for efficient 3d mesh reconstruction and high-quality mesh rendering,” arXiv preprint arXiv:2311.12775, 2023.

[202] T. Deng, Y. Chen, L. Zhang, J. Yang, S. Yuan, D. Wang, and W. Chen, “Compact 3d gaussian splatting for dense visual slam,” arXiv preprint arXiv:2403.11247, 2024.

[203] X. Xu, T. Zhang, S. Wang, X. Li, Y. Chen, Y. Li, B. Raj, M. Johnson-Roberson, and X. Huang, “Customizable perturbation synthesis for robust slam benchmarking,” arXiv preprint arXiv:2402.08125, 2024.

[204] T. Hua and L. Wang, “Benchmarking implicit neural representation and geometric rendering in real-time rgb-d slam,” arXiv preprint arXiv:2403.19473, 2024.