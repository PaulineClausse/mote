<!-- page 1 of 14 -->

arXiv:2508.08624v2 [cs.RO] 3 Sep 2025

1

# Communication Efficient Robotic Mixed Reality with Gaussian Splatting Cross-Layer Optimization

Chenxuan Liu<sup>∗</sup>, He Li∗, Zongze Li, Shuai Wang†, Wei Xu, Kejiang Ye, Derrick Wing Kwan Ng, Fellow, IEEE, and Chengzhong Xu, Fellow, IEEE

**Abstract—Realizing low-cost communication in robotic mixed reality (RoboMR) systems presents a challenge, due to the necessity of uploading high-resolution images through wireless channels. This paper proposes Gaussian splatting (GS) RoboMR (GSMR), which enables the simulator to opportunistically render a photo-realistic view from the robot’s pose by calling “memory” from a GS model, thus reducing the need for excessive image uploads. However, the GS model may involve discrepancies compared to the actual environments. To this end, a GS cross-layer optimization (GSCLO) framework is further proposed, which jointly optimizes content switching (i.e., deciding whether to upload image or not) and power allocation (i.e., adjusting to content profiles) across different frames by minimizing a newly derived GSMR loss function. The GSCLO problem is addressed by an accelerated penalty optimization (APO) algorithm that reduces computational complexity by over** 10**x compared to traditional branch-and-bound and search algorithms. Moreover, variants of GSCLO are presented to achieve robust, low-power, and multi-robot GSMR. Extensive experiments demonstrate that the proposed GSMR paradigm and GSCLO method achieve significant improvements over existing benchmarks on both wheeled and legged robots in terms of diverse metrics in various scenarios. For the first time, it is found that RoboMR can be achieved with ultra-low communication costs, and mixture of data is useful for enhancing GS performance in dynamic scenarios.**

**Index Terms—Cross-layer optimization, Gaussian splatting, mixed reality, resource allocation.**

## I. INTRODUCTION

Embodied artificial intelligence has greatly benefited from leveraging simulation to train and test robot learning systems [2]. Indeed, simulators are capable of computing robot motions, state evolutions, and sensor measurements that arise

from interactions between robots and environments. However, a significant gap exists between the simulated and real-world data [3], [4], and it is imperative to integrate real data into simulations to enhance the realism of scenarios that can be studied.

Robotic mixed reality (RoboMR) [4]–[6], which facilitates interactions between real robots and virtual agents in a shared symbiotic world, emerges as a promising solution to address the above issue. By synchronizing digital twins across simulation servers and robotic devices, RoboMR harmonizes spatial representations, leading to a paradigm shift where previously isolated virtual and real agents can now collaborate seamlessly in a metaverse space. However, challenges persist as simulators at the server and robots at the edge remain physically isolated, and establishing low-cost communication between them is non-trivial [4]–[9], due to the vast data volume of highfrequency high-resolution sensor data (e.g., images). Existing RoboMR resource allocation approaches [8]–[17] involve the following drawbacks: 1) They fail in fully exploiting the memory information recorded at previous RobotMR executions; 2) They ignore the inter-dependency between highlevel data encoding/decoding at the application layer and lowlevel communication design at the physical layer; 3) They are mostly tested in simulation, with a significant lack of testing on real-world RoboMR datasets.

This paper proposes the concept of Gaussian splatting (GS) RoboMR (or GSMR for short), which leverages a GS model to opportunistically generate a photo-realistic view from the robot’s pose, thus avoiding excessive uploading of images. This GS model acts as a “memory system” for RoboMR, but its rendering may involve discrepancies compared to the actual environments (i.e., termed “memory bias”), primarily due to the variations in illuminations and changes of environments. To this end, we propose a GS cross-layer optimization (GSCLO) framework to jointly optimize content switching (i.e., whether to upload image or not) and transmit power (i.e., adjusting to content profiles) across different frames, by minimizing a newly derived GSMR loss. We further propose an accelerated penalty optimization (APO) algorithm to solve the GSCLO problem, which reduces computational complexity by orders of magnitude compared to conventional branch-and-bound [18] and local search [19] algorithms, while achieving close-to-optimal performance as evidenced by experiments. In addition, we extend the method to the cases under imperfect channel states, power minimization criteria, and multi-robot interference. Finally, we implement RoboMR in Robot Operation System (ROS) and evaluate the performance gain

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">A preliminary version of this paper was presented at the 2025 IEEE International Conference on Computer Communications (INFOCOM) Workshop on NetRobiCS [1].</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">This work is supported by the National Natural Science Foundation of China (Grant No. 62371444), Guangdong Basic and Applied Basic Research Foundation (No. 2023B1515130002), Guangdong Special Support Plan (No. 2021TQ06X990), and the Shenzhen Science and Technology Program (Grant No. JCYJ20241202124934046, JCYJ20220818101610023, RCYX20231211090206005, RCBS20231211090517022).</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">Chenxuan Liu, Shuai Wang, and Kejiang Ye are with the Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences, Shenzhen, China. Chenxuan Liu is also with the University of Chinese Academy of Sciences.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">He Li and Chengzhong Xu are with the State Key Laboratory of IOTSC, Department of Computer and Information Science, University of Macau, Macau, China.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">Zongze Li is with Peng Cheng Laboratory, Shenzhen, China.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">Wei Xu is with the Manifold Tech Limited, Hong Kong, China.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">Derrick Wing Kwan Ng is with the School of Electrical Engineering and Telecommunications, the University of New South Wales, Australia.</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">Corresponding author: Shuai Wang (s.wang@siat.ac.cn).</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>∗</sup>These authors contribute equally.</span></small>

<!-- page 2 of 14 -->

2

TABLE I: Summary of Important Variables and Parameters

| Symbol | Type | Description |
| --- | --- | --- |
| p<sub>t</sub> ∈ R+ | Variable | Transmit power (in Watt) of frame t. |
| x<sub>t</sub> ∈ R+ | Variable | Content switching (∈ {0,1}) of frame t. |
| s<sub>t</sub> ∈ R<sup>3</sup> | Data | Robot pose s<sub>t</sub> = (a<sub>t</sub>,b<sub>t</sub>,θ<sub>t</sub>), where (a<sub>t</sub>,b<sub>t</sub>) and θ<sub>t</sub> are position and orientation, respectively. |
| u<sub>t</sub> ∈ R<sup>2</sup> | Data | Robot action u<sub>t</sub> = (v<sub>t</sub>,ψ<sub>t</sub>), where v<sub>t</sub> and ψ<sub>t</sub> are linear and angular velocities, respectively. |
| (r<sub>t</sub>,v<sub>t</sub>,m<sub>t</sub>) | Data | Real, virtual, and MR images. |
| (br<sub>t</sub>,mb <sub>t</sub>) | Data | Recovered real and MR images. |
| (c<sub>t</sub>,d<sub>t</sub>) | Data | Encoded image and mask vector. |
| (E<sub>t</sub>,D<sub>t</sub>) | Function | Encoder and decoder functions. |
| L | Function | Loss function of the RoboMR system. |
| T | Parameter | Number of frames. |
| τ | Parameter | Duration between consecutive time slots (in s). |
| (L,W) | Parameter | Image length and width. |
| (h<sub>t</sub>,h˜t,∆h<sub>t</sub>) | Parameter | Uplink channel, estimated channel, and estimation error of frame t. |
| B | Parameter | Bandwidth allocated to the robot (in Hz). |
| σ<sup>2</sup> | Parameter | External interference plus noise power (in Watt). |
| R<sub>t</sub> | Parameter | Achievable rate (in bps) of the robot. |
| P | Parameter | Power budget (in Watt) of the robot. |
| L<sub>t</sub> | Parameter | GS loss of frame t. |
| (I,S) | Parameter | Data size (in bits) of robot image and robot state, respectively. |

brought by GSMR and GSCLO compared to existing RoboMR systems [5], [6] and resource allocation algorithms [10]–[12]. Specifically, GSMR reduces the power consumption by 75 % compared with RoboMR, and the PSNR of GSCLO is at least 5 dB higher than those without cross-layer optimization.

Our contributions are summarized as follows:

• We introduce the concept of GS to support MR with ultralow communication costs (< 200 bits/frame), leading to a paradigm shift towards mixture of data for robot learning.

• A cross-layer optimization framework, termed GSCLO, is proposed, which effectively mitigates the discrepancies between GS-rendered images and real-world environments, thereby improving the image quality compared to existing GS.

• A robust GSCLO algorithm is proposed to ensure reliable GSMR under channel uncertainties and a closed-form GS power saving factor is derived, which theoretically quantifies the benefits brought by our approach.

• We implement the GSMR system in ROS on both wheeled and legged robots. Extensive experimental results show significant improvements over existing schemes in terms of diverse metrics.

The remainder of this paper is organized as follows. Section II reviews related work. Section III states the problem. Section IV describes the GSCLO scheme and APO algorithm. Subsequently, Section V presents the robust GSCLO under channel uncertainties. Section VI presents the power minimization GSCLO and multi-robot GSCLO schemes. Section VII presents experimental results. Finally, Section VIII concludes this work.

Notation. Italic, simple bold, capital bold, and curlicue letters represent scalars, vectors, matrices, and sets, respectively. ∇f represents the gradient of a function $f .   \mathcal { U } ( x , y )$ represents a uniform distribution within interval [x, y] and $\mathcal { C N } ( 0 , 1 )$

is standard normal distribution. R and C represent real and complex fields, respectively. Finally, ∥ · ∥ denotes the vector norm function and ⊙ is the Hadamard product for elementwise matrix multiplication. Important variables and parameters are summarized in Table I.

## II. RELATED WORK

RoboMR systems can be categorized into non-interactive [20], [21] and interactive approaches [2], [5], [6], [22], [23]. Non-interactive RoboMR processes off-the-shelf datasets without virtual reality synchronization, which are adopted for perception data augmentation [20], [21]. On the other hand, interactive RoboMR leads to a paradigm shift where previous isolated virtual and real agents are now synchronized for cooperation and competition in a shared scenario [2], [5], [22], [23]. However, interactive RoboMR systems require a large volume of sensor data sharing between the server and robot, which poses a great challenge to communication.

To address the above challenge, resource allocation for RoboMR becomes imperative [8]. In contrast to conventional communication systems, RoboMR systems aim to maximize the MR fidelity instead of the communication throughput. Therefore, RoboMR resource allocation becomes very different from traditional resource allocation schemes that merely consider the wireless channel state information [10], [11]. For instance, the water-filling scheme allocates more resources to better channels for throughput maximization [11], and the max-min fairness scheme allocates more resources to worse channels to maintain certain quality of service [10]. Indeed, these schemes could lead to poor performance in RoboMR systems because they do not account for the MR factors such as video complexities and quality of experience (QoE). This ignites research efforts [13]–[17] on MR oriented resource allocators. For instance, an intelligent digital twin

<!-- page 3 of 14 -->

3

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p3_b2.png)

Fig. 1: System model of RoboMR with cross-layer optimization of $\{ E _ { t } , D _ { t } \} _ { t = 1 } ^ { T }$ and $\{ p _ { t } \} _ { t = 1 } ^ { T }$

communication framework was proposed for DT synchronization within resource-constrained networks [13]. Also, a joint resource allocation and service selection scheme was designed to maximize the QoE utility for MR systems [14]. Furthermore, learning-based resource allocators have also been exploited for optimizing the frame rate, user association, and link allocation in MR systems [9], [15]–[17].

Nonetheless, existing methods mainly focus on image compression and rate control paradigms, which fail in fully exploit ing the memory recorded at previously RoboMR executions. Leveraging these memories and the recent advancements in building world models (i.e., GS [24], [25]), the server is able to “imagine” an image from a new viewpoint adjacent to the recording position. Therefore, no image uploading is needed when the memory is clear enough. Furthermore, current RoboMR resource allocation algorithms either focus on the physical layer [10], [11] or the high-level layers [8], [9], [13]–[17], without forming a unified cross-layer framework. Finally, current methods are mostly tested in simulation. To verify the effectiveness and robustness of RoboMR, it is necessary to develop real-time algorithms and evaluate the methods in real-world RoboMR systems.

Here, we propose a novel memory-assisted RoboMR paradigm, termed GSMR, which leverages a GS model to avoid excessive image uploads. We further propose a GSCLO framework to jointly optimize physical layer and application layer variables across different frames. Finally, we implement the GSMR paradigm and GSCLO algorithm in ROS, and aim to provide a concrete step toward RoboMR in the real world.

## III. SYSTEM MODEL AND PROBLEM FORMULATION

## A. System Overview

As shown in Fig. 1, a RoboMR system consists of a mobile robot acting as a real agent and a simulation server constructing the virtual world. The operation of RoboMR is discretized into T time slots, where the duration of each time slot is τ . At the t-th time slot, $t \; \in \; \{ 1 , \ldots , T \}$ , the robot state is $\mathbf { s } _ { t } \; = \; ( a _ { t } , b _ { t } , \theta _ { t } )$ , where $( a _ { t } , b _ { t } )$ and $\theta _ { t }$ denote the two-dimensional position and orientation, respectively. The interaction between the robot and the simulator involves four consecutive stages:

1) Sensing: A pair of real $\mathbf { r } _ { t } \; \in \; \mathbb { R } ^ { 3 L W }$ and virtual $\mathbf { v } _ { t } \in$ $\mathbb { R } ^ { 3 L W }$ camera images are generated at the robot and the server, respectively, where L and W are the image length

and width respectively, and the coefficient 3 accounts for the red green blue (RGB) channels.

2) Communication: The robot uploads $\mathbf { r } _ { t }$ to the server, which is detailed in Section III-B.

3) Fusion: The image $\mathbf { r } _ { t }$ is aggregated with $\mathbf { v } _ { t }$ to generate MR image $\mathbf { m } _ { t } = \mathbf { d } _ { t } \odot \mathbf { r } _ { t }   +   ( \mathbf { 1 }   -   \mathbf { d } _ { t } ) \odot \mathbf { v } _ { t }$ , where $\mathbf { d } _ { t }$ is the mask (binary vector) of a real image for extracting the background and $( \mathbf { 1 } - \mathbf { d } _ { t } )$ is the mask of a virtual image for extracting the virtual object.

4) Control: The MR image m<sub>t</sub> is fed to the robot for generating control command $\mathbf { u } _ { t } = ( v _ { t } , \phi _ { t } )$ , where $v _ { t }$ and $\phi _ { t }$ represent the linear and angular velocities, respectively.<sup>1</sup>

After the above interaction, the subsequent state is $\mathbf { s } _ { t + 1 } =$ $\mathbf { s } _ { t }   +   F ( \mathbf { s } _ { t } , \mathbf { u } _ { t } ) \tau$ , where $F ( \mathbf { s } _ { t } , \mathbf { u } _ { t } )$ is the discrete-time kinematic model of the robot [26]. This completes one loop of RoboMR and the time index is updated as $t \leftarrow t + 1$ . The entire procedure terminates when $t \; = \; T .$ , and the robot learning dataset collected in RoboMR is $\{ \mathbf { m } _ { t } , \mathbf { u } _ { t } \} _ { t = 1 } ^ { T }$

## B. Communication Model

To generate m<sub>t</sub>, streaming data $\{ \mathbf { r } _ { t } \} _ { t = 1 } ^ { T }$ needs to be uploaded over wireless communication, as the robot and simulator are physically isolated. This requires a pair of image encoder and decoder functions $( E _ { t } , D _ { t } )$ , where the encoded vector $\mathbf { c } _ { t } = E _ { t } ( \mathbf { r } _ { t } )$ and the decoded vector $\widehat { \mathbf { r } } _ { t } = D _ { t } ( \mathbf { c } _ { t } )$ , such that $\widehat { \mathbf { r } } _ { t }$ is close to $\mathbf { r } _ { t } .$ Accordingly, the MR image is

$$
\widehat {\mathbf {m}} _ {t} (E _ {t}, D _ {t}) = \mathbf {d} _ {t} \odot \widehat {\mathbf {r}} _ {t} + (\mathbf {1} - \mathbf {d} _ {t}) \odot \mathbf {v} _ {t}.\tag{1}
$$

This $\widehat { \mathbf { m } } _ { t }$ may differ from the desired image $\mathbf { m } _ { t }$ . To measure their difference, we adopt loss function

$$
\mathcal {L} \left(\mathbf {m} _ {t}, \widehat {\mathbf {m}} _ {t}\right) = (1 - \lambda) \| \mathbf {m} _ {t} - \widehat {\mathbf {m}} _ {t} \| _ {1} + \lambda   \mathrm{DS} (\mathbf {m} _ {t}, \widehat {\mathbf {m}} _ {t}),\tag{2}
$$

where the weight $\lambda \in [0,1]$ is set to $\lambda = 0 . 2$ according to [24] and the DSSIM function DS is

$$
\mathrm{DS} (\mathbf {m} _ {t}, \widehat {\mathbf {m}} _ {t}) = 1 - \text {SSIM} (\mathbf {m} _ {t}, \widehat {\mathbf {m}} _ {t}),\tag{3}
$$

with SSIM being the structural similarity index measure (SSIM) function detailed in [27, Eqn. 5].

The wireless channels are assumed to be quasi-static during each time slot, and vary in different time slots. Let $h _ { t } \in \mathbb { C }$ and $| h _ { t } | ^ { 2 }$ denote the uplink channel coefficient and gain from the

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">ut</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>1</sup>Note that robot control needs to avoid any potential collision with both virtual and real agents in the MR image mt.</span></small>

<!-- page 4 of 14 -->

4

robot to the server at time slot t. The channel gains $\{ | h _ { t } | ^ { 2 } \} _ { t = 1 } ^ { T }$ can be pre-determined as detailed in Section V. The achievable rate in bits/s between the robot and the server at time slot t is

$$
R _ {t} (p _ {t}) = B \log_ {2} \left(1 + \frac {| h _ {t} | ^ {2} p _ {t}}{\sigma^ {2}}\right),\tag{4}
$$

where $p _ { t }$ and B denote the transmit power and bandwidth of the robot at time slot t, respectively, and $\sigma ^ { 2 }$ denotes the power of external interference plus additive white Gaussian noise (AWGN) at the server. Let $C _ { t }$ denote the data volume of $\mathbf { c } _ { t } ,$ which is a function of the encoder $E _ { t }$ . To guarantee successful transmission of $\mathbf { c } _ { t } ,$ , we must have $\tau R _ { t } ( p _ { t } ) \geq C _ { t } ( E _ { t } )$ , ∀t.

## C. Cross-Layer Optimization

Having the communication workload satisfied, our goal is to minimize the average distortion between the ground truth MR images $\{ \mathbf { m } _ { t } \} _ { t = 1 } ^ { T }$ and the actual MR images $\{ \widehat { \mathbf { m } } _ { t } \} _ { t = 1 } ^ { T }$ , by jointly planning the power $\mathcal { P } = \{ p _ { t } \} _ { t = 1 } ^ { T } ( \mathbf { p } = [ \widetilde { p _ { 1 } , \cdots , p _ { T } } ] ^ { T } )$ across all time slots and designing encoder-decoder functions $\mathcal { F } = \{ ( E _ { t } , D _ { t } ) \} _ { t = 1 } ^ { T }$ . This is realized by solving the following cross-layer optimization problem:

$$
\mathsf {P}: \min _ {\mathcal {P}, \mathcal {F}} \frac {1}{T} \sum_ {t = 1} ^ {T} \mathcal {L} \left(\mathbf {m} _ {t}, \widehat {\mathbf {m}} _ {t} (E _ {t}, D _ {t})\right)\tag{5a}
$$

$$
\text {s.t.} \tau B \log_ {2} \left(1 + \frac {| h _ {t} | ^ {2} p _ {t}}{\sigma^ {2}}\right) \geq C _ {t} (E _ {t}), \forall t,\tag{5b}
$$

$$
\left| \frac {1}{T} \sum_ {t = 1} ^ {T} p _ {t} \leq P, p _ {t} \geq 0, \forall t, \right.\tag{5c}
$$

where constraint (5b) is the transmission requirement, and (5c) is the power constraint, with P being the power budget.

Problem P is defined as the implicit CLO problem, since it involves the implicit functions $\{ E _ { t } , D _ { t } \}$ . Existing methods design $\{ E _ { t } , D _ { t } \}$ exploiting compression (e.g., JPEG) or caching [7]. However, they still lead to high data rate requirements, e.g., each $C _ { t }$ is in the range of hundreds of KBytes or more.

## IV. GAUSSIAN SPLATTING ROBOMR

This paper proposes GSMR, which adopts a GS model as a “memory system” for RoboMR. This enables the server to opportunistically generate a photo-realistic image from a pose key as shown in Fig. 2. Since this key is only tens of Bytes, the data rate requirements $\{ C _ { t } \}$ could be reduced by orders of magnitude compared to existing approaches.

## A. Gaussian Splatting and Content Switching

In particular, the GS model, Φ, is operated on a given robot pose $\mathbf { s } _ { t } ,$ and outputs a synthesis image $\mathbf { y } _ { t } = \Phi ( \mathbf { s } _ { t } )$ . The model Φ is obtained as follows.

• First, we represent the scene as numerous 3D Gaussians $\mathcal { S } = \{ \mathcal { G } _ { 1 } , \mathcal { G } _ { 2 } , \cdots \}$ , where each $\mathcal { G } _ { i }$ is characterized by a set of trainable parameters.

• Next, with Gaussians S, RGB images can then be efficiently rendered by alpha-compositing the splatted 2D projection of each Gaussian in order in pixel space. The GS-rendered image is represented by a vector $\mathbf { y } _ { t } .$

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p4_b18.png)

Historical images recorded at previous Robot MR executions

Fig. 2: Leverage GS model to render images.

• Finally, given a set of GS generated pose-image pairs $\{ ( \mathbf { s } _ { t } , \mathbf { y } _ { t } ) \} _ { t = 1 } ^ { H }$ and ground truth pose-image pairs $\{ ( \mathbf { s } _ { t } , \mathbf { y } _ { t } ^ { * } ) \} _ { t = 1 } ^ { H }$ , where H is the number of training data, we train GS parameters S through back propagation of the gradient of loss function $\mathcal { L } ( \mathbf { y } _ { t } , \mathbf { y } _ { t } ^ { * } )$ with respect to S.

In general, the rendered image $\mathbf { y } _ { t } = \Phi ( \mathbf { s } _ { t } )$ may mismatch the ground truth image $\mathbf { y } _ { t } ^ { * }$ . To address such mismatch, we further propose a content switching scheme shown in Fig. 3. Consequently, the proposed method designs the encoder function $E _ { t }$ as

$$
\mathbf {c} _ {t} = E _ {t} (\mathbf {r} _ {t}) = x _ {t} \mathbf {r} _ {t} + (1 - x _ {t}) \mathbf {s} _ {t},\tag{6}
$$

where $x _ { t } \in \{ 0 , 1 \}$ denotes the content switching variable to be optimized, $x _ { t }   =   1$ represents transmitting image, and $x _ { t } = 0$ represents transmitting pose. Accordingly, the decoder function is

$$
\widehat {\mathbf {r}} _ {t} = D _ {t} (\mathbf {c} _ {t}) = x _ {t} \mathbf {r} _ {t} + (1 - x _ {t}) \Phi (\mathbf {s} _ {t}).
$$

The loss function $\mathcal { L } \left( \mathbf { m } _ { t } , \widehat { \mathbf { m } } _ { t } \right)$ in P is thus

(7)

$$
\mathcal {L} \left(\mathbf {m} _ {t}, \widehat {\mathbf {m}} _ {t}\right) = L _ {t} (1 - x _ {t}) := \Theta_ {t} (x _ {t}),\tag{8}
$$

where we have defined

$$
\begin{array}{c} L _ {t} := \mathcal {L} \Big (\mathbf {d} _ {t} \odot \mathbf {r} _ {t} + (\mathbf {1} - \mathbf {d} _ {t}) \odot \mathbf {v} _ {t}, \\ \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \qquad \mathbf {d} _ {t} \odot \Phi (\mathbf {s} _ {t}) + (\mathbf {1} - \mathbf {d} _ {t}) \odot \mathbf {v} _ {t} \Big). \end{array}\tag{9}
$$

On the other hand, since the data volume is $C _ { t } ( E _ { t } ) = x _ { t } I +$ $( 1   -   x _ { t } ) S$ , where I and S (with $S \ll I )$ are the data volumes in bits of image and pose, respectively, constraint (5b) becomes

$$
\tau B \log_ {2} \left(1 + \frac {\left| h _ {t} \right| ^ {2} p _ {t}}{\sigma^ {2}}\right) \geq x _ {t} I + (1 - x _ {t}) S, \forall t.\tag{10}
$$

## B. GSCLO Problem Formulation

Based on the scheme in Section IV-A, problem P is explicitly formulated as

$$
\left| \mathsf {P} _ {\mathrm{GS}}: \min _ {\mathcal {P}, \mathcal {X}} \frac {1}{T} \sum_ {t = 1} ^ {T} \Theta_ {t} (x _ {t}) \right|\tag{11a}
$$

$$
\text {s.t.} \tau B \log_ {2} \left(1 + \frac {\left| h _ {t} \right| ^ {2} p _ {t}}{\sigma^ {2}}\right) \geq x _ {t} I + (1 - x _ {t}) S, \forall t,\tag{11b}
$$

<!-- page 5 of 14 -->

5

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p5_b2.png)

Fig. 3: Architecture of content switching GSMR.

$$
\left| \frac {1}{T} \sum_ {t = 1} ^ {T} p _ {t} \leq P, p _ {t} \geq 0, \forall t, \right.\tag{11c}
$$

$$
x _ {t} \in \{0, 1 \}, \forall t,\tag{11d}
$$

where $\begin{aligned} { \mathcal { X } = \{ x _ { t } \} ( \mathbf { x } = [ x _ { 1 } , \cdots , x _ { T } ] ^ { T } ) . } \\ \end{aligned}$

Problem $\mathsf { P } _ { \mathrm { G S } }$ is defined as the GSCLO problem, since it leverages the GS model to design functions $\{ E _ { t } , D _ { t } \}$ in the CLO problem P. Note that $\mathsf { P } _ { \mathrm { G S } }$ is a mixed integer nonlinear programming (MINLP) problem, which can be solved by branch-and-bound (B&B) via Mosek [18]. However, the complexity is exponential in $T ,$ which is time-consuming when the number of frames T is large. On the other hand, P<sub>GS</sub> can be addressed by continuous relaxation and rounding [28], but this would lead to non-negligible performance loss. Lastly, existing power allocation algorithms, e.g., water-filling [11], max-min fairness [10], fail in directly minimizing the GSMR loss in $\mathsf { P } _ { \mathrm { G S } }$

## C. Penalty Continuous Reformulation

To tackle the discontinuity, we first relax the binary constraint $x _ { t } \in \{ 0 , 1 \}$ into a linear constraint $0 \; \leq \; x _ { t } \; \leq \; 1$ , ∀t. However, the relaxation is not tight and the solution to the relaxed problem could be $0 \; < \; x _ { t } \; < \; 1$ . To promote a binary solution for the relaxed variable $\{ x _ { t } \}$ , we augment the objective function with a penalty term as in [29]. Accordingly, the approximate reformulation with regularized penalty term of $\mathsf { P } _ { \mathsf { G S } }$ is given by

$$
\mathsf {P} _ {\text {Penalty}}: \min _ {\mathcal {P}, \mathcal {X}} \frac {1}{T} \sum_ {t = 1} ^ {T} \Theta_ {t} (x _ {t}) + \varphi (\mathbf {x})\tag{12a}
$$

$$
\text {s.t. constraints} (1 1 b), (1 1 c),\tag{12b}
$$

$$
0 \leq x _ {t} \leq 1, \forall t,\tag{12c}
$$

where $\varphi ( \mathbf { x } )$ is a penalty function to penalize the violation of the zero-one integer constraints. A celebrated penalty function was introduced in [30], where the penalty function is set as

$$
\varphi (\mathbf {x}) = \frac {1}{\beta} \sum_ {t = 1} ^ {T} x _ {t} (1 - x _ {t}),\tag{13}
$$

where $\beta \; > \; 0$ is the penalty parameter. According to [30, Proposition 1], with the penalty term in (13), there exists an upper bound $\bar { \beta } > 0$ such that for any $\beta \in [ 0 , \bar { \beta } ] ,   \mathsf { P } _ { \mathrm { P e n a l t y } }$ and $\mathsf { P } _ { \mathsf { G S } }$ have the same minimum points, i $1 . \mathsf { e } . ,   \mathsf { P } _ { \mathrm { P e n a l t y } }$ and $\mathsf { P } _ { \mathsf { G S } }$ are equivalent with a proper choice of β [30].

## D. Difference of Convex Algorithm

It can be seen from problem $\mathsf { P } _ { \mathrm { P e n a l t y } }$ that the constraints in (11b) are convex, since the function $- \log _ { 2 } ( \cdot )$ is convex. Besides, the constraints in (11c) are all affine. The only nonconvex term in the objective function is the penalty $\varphi ( \mathbf { x } ) .$ . However, by expanding $\varphi ( \mathbf { x } )$ as $\begin{array} { r } { \varphi ( \mathbf { x } ) = \frac { 1 } { \beta } \sum _ { t = 1 } ^ { \hat { T } } x _ { t } - \frac { 1 } { \beta } \sum _ { t = 1 } ^ { T } x _ { t } ^ { 2 } , } \end{array}$ we find that $\varphi ( \mathbf { x } )$ is a difference of convex (DC) function [31], and such DC functions enjoy excellent surrogate properties. Specifically, given a certain solution $\{ x _ { t } ^ { \star } \}$ , we apply the firstorder Taylor expansion on $\varphi ( \mathbf { x } )$ and obtain $\varphi ( \mathbf { x } ) \approx \widehat { \varphi } ( \mathbf { x } | \mathbf { x } ^ { \star } )$ where

$$
\widehat {\varphi} (\mathbf {x} | \mathbf {x} ^ {\star}) = \sum_ {t = 1} ^ {T} \left(\frac {1}{\beta} x _ {t} - \frac {2}{\beta} x _ {t} ^ {\star} x _ {t} + \frac {1}{\beta} x _ {t} ^ {\star^ {2}}\right).\tag{14}
$$

Using the properties of DC functions, the following proposition can be established.

**Proposition 1.** $\widehat { \varphi } ( \mathbf { x } | \mathbf { x } ^ { \star } )$ satisfy the following conditions:

(i) Convexity: $\widehat { \varphi } ( \mathbf { x } | \mathbf { x } ^ { \star } )$ is convex in x.

(ii) Upper bound: $\widehat { \varphi } ( \mathbf { x } | \mathbf { x } ^ { \star } ) \geq \varphi ( \mathbf { x } ) \; \mathit { f o r \; a n y } \; \mathbf { x } .$ (iii) Local equivalence: $\widehat { \varphi } ( \mathbf { x } ^ { \star } | \mathbf { x } ^ { \star } ) = \varphi ( \mathbf { x } ^ { \star } )$ and $\nabla \widehat { \varphi } ( \mathbf { x } ^ { \star } | \mathbf { x } ^ { \star } ) =$ $\nabla \varphi ( \mathbf { x } ^ { \star } )$

Proof. Part (i) is proved by checking the semi-definiteness of the Hessian of $\widehat { \varphi } .$ In particular, $\nabla _ { \mathbf { x } } ^ { \bar { 2 } } \widehat { \varphi } \; = \; \mathbf { 0 }$ , which is semi-definite. Part (ii) is proved by checking

$$
\begin{array}{c} \widehat {\varphi} (\mathbf {x} | \mathbf {x} ^ {\star}) - \varphi (\mathbf {x}) = \frac {1}{\beta} \sum_ {t = 1} ^ {T} x _ {t} ^ {2} - \sum_ {t = 1} ^ {T} \frac {2}{\beta} x _ {t} ^ {\star} x _ {t} + \sum_ {t = 1} ^ {T} \frac {1}{\beta} x _ {t} ^ {\star^ {2}} \\ = \frac {1}{\beta} \sum_ {t = 1} ^ {T} (x _ {t} - x _ {t} ^ {\star}) ^ {2} \geq 0. \end{array} \tag {9}\tag{15}
$$

Part (iii) is proved by computing and comparing the function and gradient values of $\widehat { \varphi }$ and $\varphi .$ . □

Based on part (ii) of Proposition 1, an upper bound problem, denoted as $\mathsf { P } _ { \mathrm { P e n a l t y } } ^ { \prime } ,$ can be directly obtained if we replace the function $\varphi ( \mathbf { x } )$ by $\left( \widehat { \varphi } ( \mathbf { x } | \mathbf { x } ^ { \star } ) \right.$ expanded around a feasible point $\mathbf { x } ^ { \star }$ for the problem $\mathsf { P } _ { \mathrm { P e n a l t y } }$ . Moreover, according to part (i) of Proposition 1, this $\mathsf { P } _ { \mathrm { P e n a l t y } } ^ { \prime }$ is guaranteed to be a solvable convex problem. Finally, according to part (iii) of Proposition 1, a tighter upper bound can be achieved if we treat the obtained solution as another feasible point and continue to construct the next round surrogate function. This leads to the DC algorithm [31], which solves a sequence of convex optimization problems $\left\{ \mathsf { P } _ { \mathrm { D C } } ^ { [ 0 ] } , \mathsf { P } _ { \mathrm { D C } } ^ { [ 1 ] } , \mathsf { P } _ { \mathrm { D C } } ^ { [ 2 ] } , \cdots \right\}$ , where $\mathsf { P } _ { \mathrm { D C } } ^ { [ n + 1 ] }$ is the optimization problem in the $( n + 1 )$ -th iteration of the DC algorithm, and is given by

$$
\begin{array}{l} \mathsf {P} _ {\mathrm{DC}} ^ {[ n + 1 ]}: \quad \min _ {\mathcal {P}, \mathcal {X}} \frac {1}{T} \sum_ {t = 1} ^ {T} \Theta_ {t} (x _ {t}) + \widehat {\varphi} (\mathbf {x} | \mathbf {x} ^ {[ n ]}) \\ \quad \text {s.t.} \quad \text {constraints} (1 1 b), (1 1 c), (1 2 c) \end{array}\tag{16}
$$

Here, $\mathcal { X } ^ { [ n ] } \: = \: \{ x _ { t } ^ { [ n ] } \}$ is the optimal solution of $\mathcal { X }$ to $\mathsf { P } _ { \mathrm { D C } } ^ { [ n ] }$ Each $\mathsf { P } _ { \mathrm { D C } } ^ { [ n + 1 ] }$ is a convex problem and can be solved via off-the-shelf toolbox (e.g., CVXPY) with a complexity of $\mathcal { O } ( ( 2 T ) ^ { 3 . 5 } )$ . According to **Proposition 1** and [32], any limit point of the sequence $\widetilde { \{ ( \mathcal { P } ^ { [ n ] } , \mathcal { X } ^ { [ n ] } \} _ { n = 0 , 1 , \cdots } }$ · is a Karush-Kuhn-

<!-- page 6 of 14 -->

6

Tucker (KKT) solution to the problem $\mathsf { P } _ { \mathrm { P e n a l t y } }$ for any feasible starting point $( \mathcal { P } ^ { [ 0 ] } , \mathcal { X } ^ { [ 0 ] } )$ .

## E. Initialization via Ranking

The APO algorithm requires a feasible initialization. Initialization using $\{ x _ { t } = \delta , \forall t \}$ with $\delta > 0 \; ( \mathrm { e . g . , } \; \delta = 0 . 5 )$ may lead to violations of constraints (11b) and (11c). A conservative initialization is $\{ x _ { t }   =   0 , \forall t \}$ . However, this easily leads to slow convergence of the DC algorithm. Here, we propose a ranking-based algorithm to accelerate the convergence while guaranteeing feasibility.

Specifically, the ranking algorithm sorts the list of GS losses $\mathcal { R }   =   \{ L _ { t } \} _ { t = 1 } ^ { T }$ in descending order, and the reordered list is denoted as $\mathcal { R } ^ { \prime } = \{ L _ { g ( 1 ) } , L _ { g ( 2 ) } , \cdots \}$ , where $g ( j )$ is an index mapping $j \rightarrow g ( j )$ such that $L _ { g ( j ) }   \geq   L _ { g ( j + 1 ) }$ for all $j$ and g(1) is the index corresponding to the largest value among all $\{ L _ { t } \}$ . The ranking solution is given by:

$$
(x _ {t} ^ {\text {Rank}}, p _ {t} ^ {\text {Rank}}) = \left\{ \begin{array}{l l} (1, \frac {\sigma^ {2}}{| h _ {t} | ^ {2}} 2 ^ {\frac {I}{\tau B}} - \frac {\sigma^ {2}}{| h _ {t} | ^ {2}}), & \text {if} g (t) \leq \mu \\ (0, \frac {\sigma^ {2}}{| h _ {t} | ^ {2}} 2 ^ {\frac {S}{\tau B}} - \frac {\sigma^ {2}}{| h _ {t} | ^ {2}}), & \text {if} g (t) > \mu \end{array} \right.\tag{17}
$$

where $\mu = \operatorname { a r g } \operatorname { m a x } _ { x \in \mathbb { Z } } \{ x : \Xi ( x ) \leq T P \}$ and

$$
\Xi (x) = \sum_ {t = 1} ^ {x} \frac {\sigma^ {2} 2 ^ {\frac {I}{\tau B}} - \sigma^ {2}}{| h _ {g (t)} | ^ {2}} + \sum_ {t = x + 1} ^ {T} \frac {\sigma^ {2} 2 ^ {\frac {S}{\tau B}} - \sigma^ {2}}{| h _ {g (t)} | ^ {2}}.\tag{18}
$$

The insight of solution (17) is that $L _ { t }$ represents how much loss can be reduced by switching from pose to image, and $x _ { t } = 1$ should be assigned to the frame that may reduce the loss to the maximum extent. Moreover, given the values of $x _ { t } \quad = \quad 1 \quad \mathrm { o r } \quad x _ { t } \quad = \quad 0 ,$ , the optimal transmit power at time t must activate constraint (11c), so as to reserve more power for the remaining frames. The following proposition can be established to confirm the above insight.

**Proposition 2.** The ranking-based solution $\{ x _ { t } ^ { \mathrm { R a n k } } , p _ { t } ^ { \mathrm { R a n k } } \}$ is optimal to PGS $\mathit { i f } \: | h _ { 1 } | ^ { 2 } = \dot { \dots } = | h _ { T } | ^ { 2 } .$

Proof. First, it can be proved that constraint (11c) always activates at the optimal $\{ x _ { t } ^ { * } , p _ { t } ^ { * } \}$ . This gives $\begin{array} { r } { p _ { t } ^ { * } = \frac { \sigma ^ { 2 } } { | h _ { t } | ^ { 2 } } 2 ^ { \frac { I } { \tau B } } - \frac { \sigma ^ { 2 } } { | h _ { t } | ^ { 2 } } } \end{array}$ if $x _ { t } ^ { * } = 1$ and $\begin{array} { r } { p _ { t } ^ { * }   =   \frac { \sigma ^ { 2 } } { | h _ { t } | ^ { 2 } } 2 ^ { \frac { S } { \tau B } } - \frac { \sigma ^ { 2 } } { | h _ { t } | ^ { 2 } } } \end{array}$ if $x _ { t } ^ { * } = 0$ . Putting the above equations and $| \overset { \cdot \cdot \cdot \cdot } { h _ { 1 } } | ^ { 2 }   =   \cdots \overset { \cdot \cdot \cdot \cdot \cdot } { = } | h _ { T } | ^ { 2 }$ into $\mathsf { P } _ { \mathsf { G S } }$ , we can prove $\textstyle \sum x _ { t } ^ { * } = \mu$ by contradiction. Assuming $\begin{array} { r } { \sum x _ { t } ^ { * } < \mu , } \end{array}$ then we can always decrease the objective value $\textstyle \sum _ { t } L _ { t } ( 1 - x _ { t } )$ by setting $\textstyle \sum x _ { t } ^ { * } \leftarrow \sum x _ { t } ^ { * } + 1$ and $x _ { t } ^ { * } \gets 1 - x _ { t } ^ { * }$ for any $x _ { t } ^ { * } = 0 .$ This contradicts the optimality of $\{ x _ { t } ^ { * } , p _ { t } ^ { * } \}$ □

To efficiently compute the threshold $\mu ,$ it is observed that $\Xi ( x )$ is an increasing function of x. Therefore, $\mu$ can be obtained from checking $\Xi ( x ) \leq T P$ using bisection method within interval [1, T]. The bisection method exhibits an iteration complexity of $\mathcal { O } ( \log ( T ) )$ .

**Proposition 2** shows that the performance of ranking-based algorithm depends on the variation of $\{ h _ { t } \}$ . It is in general suboptimal to $\mathsf { P } _ { \mathrm { G S } }$ , since it assumes equal channel gains. Based on **Proposition 2**, the proposed initialization for APO is $\{ x _ { t } ^ { [ 0 ] } = x _ { t } ^ { \mathrm { \hat { R a n k } } } , p _ { t } ^ { [ 0 ] } = \hat { p _ { t } ^ { \mathrm { R a n k } } } \}$ , and the entire APO algorithm is summarized in Algorithm 1.

<div class="docvortex-algorithm" style="white-space: pre-wrap; font-family:monospace;">
Algorithm 1: GSCLO via APO.
Input Parameters ($\{L_t\}, \tau, B, \{h_t\}, \sigma^2, I, S, P$).
Initialize $\{x_t^{[0]}, p_t^{[0]}\}$ according to (17) and set $n = 0$.
Repeat
    Solve $\mathsf{P}_{\mathsf{DC}}^{[n+1]}$ and obtain its solution $\{x_t^*, p_t^*\}$.
    $\{x_t^{[n+1]}, p_t^{[n+1]}\} \leftarrow \{x_t^*, p_t^*\}$ and $n \leftarrow n + 1$.
Until convergence and set $\{\mathbf{x}^\diamond = \mathbf{x}^{[n]}, \mathbf{p}^\diamond = \mathbf{p}^{[n]}\}$.
Output $(\mathbf{x}^\diamond, \mathbf{p}^\diamond)$.
</div>

## V. ROBUST GSCLO UNDER CHANNEL UNCERTAINTY

To realize GSCLO in practical RoboMR systems, we need to estimate the channel gains $| h _ { t } | ^ { 2 }$ . This implies that the parameters $| h _ { t } | ^ { 2 }$ in $\mathsf { P } _ { \mathrm { G S } }$ may involve estimation errors. However, the APO algorithm in Section IV is based on the assumption of perfect channel estimation, which may lead to performance degradation. Hence, this section investigates the robust GSCLO problem in RoboMR networks by considering the uncertainty of channel gain.

Specifically, under channel uncertainty, the actual channel is given by

$$
h _ {t} = \tilde {h} _ {t} + \Delta h _ {t},\tag{19}
$$

where $\tilde { h } _ { t }$ is the estimated channel known at the server, and $\Delta h _ { t }$ is the estimation error, which is independent of $h _ { t } .$ According to [33], $\Delta h _ { t }$ can be modeled as Gaussian distribution $\Delta h _ { t } \sim \mathcal { C N } ( 0 , \omega ^ { 2 } )$ with zero mean and variance $\omega ^ { 2 }$ . By measuring the robot-server channel samples, the server can acquire the value of $\omega ^ { 2 }$ . Therefore, given channel estimate h˜t, h<sub>t</sub> can be regarded as a complex Gaussian variable with mean $\tilde { h } _ { t }$ and variance $\omega ^ { 2 }$ . Therefore, $| h _ { t } | ^ { 2 }$ given $\tilde { h } _ { t }$ follows a non-central $\chi ^ { 2 }$ distribution with two degrees of freedom, and the conditional PDF is

$$
\begin{array}{c} f (| h _ {t} | ^ {2} | \tilde {h} _ {t}) = \frac {1}{\omega^ {2}} \exp \left(- \frac {| \tilde {h} _ {t} | ^ {2} + | h _ {t} | ^ {2}}{\omega^ {2}}\right) I _ {0} \left(\frac {\sqrt {| h _ {t} | ^ {2} | \tilde {h} _ {t} | ^ {2}}}{\omega^ {2} / 2}\right), \\ \forall | h _ {t} | ^ {2} \geq 0, \end{array} \tag {20}
$$

where $I _ { 0 } ( x )$ is the zero-th order modified Bessel function of the first kind.

The channel gain distribution (20) implies that the achievable rate $R _ { t } ( p _ { t } )$ which is conditioned on $| h _ { t } | ^ { 2 }$ , is also random [34], [35]. Consequently, the data transmission outage event occurs at the server when constraint (11b) is not satisfied. Mathematically, this outage event can be characterized by the outage probability (OP), which is given by

$$
P _ {t} ^ {\mathrm{out}} = \Pr \left\{| h _ {t} | ^ {2} <   \left[ 2 ^ {\frac {x _ {t} I + (1 - x _ {t}) S}{\tau B}} - 1 \right] \frac {\sigma^ {2}}{p _ {t}} \Big | \tilde {h} _ {t} \right\}\tag{21}
$$

$$
= \int_ {0} ^ {\left[ 2 \frac {x _ {t} I + (1 - x _ {t}) S}{\tau B} - 1 \right] \frac {\sigma^ {2}}{p _ {t}}} f (| h _ {t} | ^ {2} | \tilde {h} _ {t}) d | h _ {t} | ^ {2}\tag{22}
$$

$$
= \underbrace 1 - Q _ {1} \left(\frac {\sqrt {| \tilde {h} _ {t} | ^ {2}}}{\sqrt {\omega^ {2} / 2}} , \frac {\sqrt {(2 ^ {\frac {x _ {t} I + (1 - x _ {t}) S}{\tau B}} - 1) \frac {\sigma^ {2}}{p _ {t}}}{\sqrt {\omega^ {2} / 2}}\right)} _ {:= \Gamma_ {t} (x _ {t}, p _ {t})},\tag{23}
$$

<!-- page 7 of 14 -->

7

where $Q _ { 1 } ( x , y )$ is the first-order Marcum Q-function [33, eqn. 4-33]. With the introduction of OP, the nominal transmission constraint (11b) becomes forcing the OP below a certain threshold, i.e., $P _ { t } ^ { \mathrm { o u t } } \leq \epsilon ,$ where $\epsilon ~ \in ~ ( 0 , 1 )$ is the target OP requirement [35]. This new OP-based data transmission constraint is written as $\Gamma _ { t } ( x _ { t } , p _ { t } ) \leq \epsilon .$

Hence, under channel uncertainty, the robust GSCLO problem is

$$
\left| P _ {\mathrm{GS}} ^ {\prime}: \min _ {\mathcal {P}, \mathcal {X}} \frac {1}{T} \sum_ {t = 1} ^ {T} \Theta_ {t} (x _ {t}) \right|\tag{24a}
$$

$$
\begin{array}{l} \text {s.t.} \Gamma_ {t} (x _ {t}, p _ {t}) \leq \epsilon , \forall t, \end{array}\tag{24b}
$$

$$
\left| \frac {1}{T} \sum_ {t = 1} ^ {T} p _ {t} \leq P, p _ {t} \geq 0, \forall t. \right|\tag{24c}
$$

$$
x _ {t} \in \{0, 1 \}, \forall t.\tag{24d}
$$

The above problem is nontrivial to solve due to the numerical Marcum Q-function $Q _ { 1 }$ . The APO algorithm that directly conducts joint optimization over $\{ \mathcal { P } , \mathcal { X } \}$ becomes inapplicable. Thus, we decompose $\mathsf { P } _ { \mathrm { G S } } ^ { \prime }$ into a two-layer optimization problem, with the outer iteration solving $\mathcal { X } ^ { \flat } \mathrm { s }$ subproblem and the inner iteration solving $\mathcal { P } ^ { \prime } \mathbf { s }$ subproblem.

The $\mathcal { X } ^ { \flat } \mathbf { s }$ subproblem is solved via iterative local search [19], which is guaranteed to achieve a local optimal solution. First, we start from the APO solution to $\mathsf { P } _ { \mathrm { G S } }$ , denoted as $\mathbf { x } ^ { [ 0 ] }$ . This $\mathbf { x } ^ { [ 0 ] }$ is over-confident and may lead to violation of constraints (24b) for some t, thus failure of image uploads. To this end, we define the neighborhood of $\mathbf { x } ^ { [ 0 ] }$ as:

$$
\mathcal {N} (\mathbf {x} ^ {[ 0 ]}) = \{\mathbf {x}: \| \mathbf {x} - \mathbf {x} ^ {[ 0 ]} \| _ {0} \leq \eta , \mathbf {x} \in \{0, 1 \} ^ {T} \},\tag{25}
$$

which $1 \leq \eta \leq T$ is the variable size. Second, we randomly flip η elements of $\mathbf { x } ^ { [ 0 ] }$ , to generate a new feasible solution $\mathbf { x } ^ { \prime } \in \mathcal { N } ( \mathbf { x } ^ { [ 0 ] } )$ . Third, with the choice of x fixed to $\mathbf { x } = \mathbf { x } ^ { \prime }$ , we check the feasibility of $\mathsf { P } _ { \mathrm { G S } } ^ { \prime }$ by solving the $\mathcal { P } ^ { \prime } \mathbf { s }$ subproblem, and obtain the associated feasibility flag feasible. Fourth, we consider the following two branches:

(i) If feasible = 1 and $\textstyle \frac { 1 } { T } \sum _ { t = 1 } ^ { T } \Theta _ { t } ( x _ { t } ^ { \prime } ) \leq \frac { 1 } { T } \sum _ { t = 1 } ^ { T } \Theta _ { t } ( x _ { t } ^ { [ 0 ] } )$ , we update $\mathbf { x } ^ { [ 1 ] } \leftarrow \mathbf { x } ^ { \vec { \prime } }$ and construct the neighborhood of $\mathcal { N } ( \mathbf { x } ^ { [ 1 ] } )$ to execute the next iteration;

(ii) Otherwise, we execute the random flipping process repeatedly to generate another feasible solution within the $\tilde { \mathcal { N } } ( \mathbf { x } ^ { [ 0 ] } )$ until condition (i) is satisfied.

This process is executed iteratively until the maximum number of iterations $\overline { { \mathcal { I } } }$ is reached, generating a sequence $\{ \mathbf { x } ^ { [ 1 ] } , \mathbf { x } ^ { [ 2 ] } , \cdots \}$

Now, the remaining problem is how to solve the $\mathcal { P } ^ { \prime } \mathbf { s }$ subproblem given fixed $\mathbf { x } = \mathbf { x } ^ { \prime }$ . An efficient way to provide a feasibility check of $\mathsf { P } _ { \mathrm { G S } } ^ { \prime }$ given $\mathbf { x } = \mathbf { x } ^ { \prime }$ is to first minimize the total transmit power via the following problem

$$
\left| \mathsf {F} _ {\mathrm{GS}}: \min _ {\mathcal {P}} \frac {1}{T} \sum_ {t = 1} ^ {T} p _ {t} \right|\tag{26a}
$$

$$
\text {s.t.} \Gamma (x _ {t} ^ {\prime}, p _ {t}) \leq \epsilon , p _ {t} \geq 0, \forall t,\tag{26b}
$$

and then check whether the optimal $\mathcal { P } ^ { * }$ to $\mathsf { F } _ { \mathrm { G S } }$ satisfies $\textstyle { \frac { 1 } { T } } \sum _ { t = 1 } ^ { T } p _ { t } ^ { * } ~ \leq ~ P$ . If so, problem $\mathsf { P } _ { \mathrm { G S } } ^ { \prime }$ given $\textbf { x } = \textbf { x } ^ { \prime }$ is

<div class="docvortex-algorithm" style="white-space: pre-wrap; font-family:monospace;">
Algorithm 2: Robust GSCLO via BILS.
Initialize $\mathbf{x}^{[0]} = \mathbf{x}^{\text{APO}}$ and $\eta = 5$.
Set $i = 0$ and iteration counter $n = 0$.
Repeat
    Sample a solution $\mathbf{x}' \in \mathcal{N}(\mathbf{x}^{[i])}$.
    Solve $F_{\text{GS}}$ using bisection and obtain solution $\{p_t^*\}$.
    If $\frac{1}{T} \sum_t p_t^* \leq P \&amp; \frac{1}{T} \sum_t \Theta_t(x_t') \leq \frac{1}{T} \sum_t \Theta_t(x_t^{[i]})$:
        $\mathbf{x}^{[i+1]} \leftarrow \mathbf{x}', \mathbf{p}^{[i+1]} \leftarrow \mathbf{p}^*, i \leftarrow i + 1$.
    $n \leftarrow n + 1$.
Until $n = \overline{\mathcal{I}}$ and set $\{x^\diamond = x^{[i]}, p^\diamond = p^{[i]}\}$
Output $\{x^\diamond, p^\diamond\}$.
</div>

feasible; otherwise, the transmit power budget cannot support MR message exchanges and $\mathsf { P } _ { \mathrm { G S } } ^ { \prime }$ given $\mathbf { x } = \mathbf { x } ^ { \prime }$ is infeasible.

The benefit of transforming $\mathsf { P } _ { \mathrm { G S } } ^ { \prime }$ into $\mathsf { F } _ { \mathrm { G S } }$ is that power variables $\{ p _ { t } \}$ at different frames are decoupled in $\mathsf { F } _ { \mathrm { G S } }$ which can be optimized in parallel. Specifically, minimizing $\textstyle { \frac { 1 } { T } } \sum _ { t = 1 } ^ { T } p _ { t }$ is equivalent to minimizing $p _ { t }$ for all t. For each $p _ { t } ,$ it must be bounded by $0 \leq p _ { t } \leq P$ . Moreover, the marcum $\mathbf { Q }$ function $Q _ { 1 }$ is a monotonically increasing function of $p _ { t }$ . Consequently, we can conduct a bisection search of $p _ { t }$ within interval [0, P], so as to find the minimum $p_{t}^{*}$ satisfying constraint (26b). The complexity of bisection for solving $\mathsf { F } _ { \mathrm { G S } }$ is O(Tlog(P)). The entire bisection-in-the-loop iterated local search (BILS) algorithm is summarized in Algorithm 2.

To execute the proposed Algorithm 1 (i.e., APO GSCLO) and Algorithm $2 \mathrm { ~ \bf ~ ( i . e . }$ , Robust GSCLO), we only need to know the large-scale fading (i.e., channel gain) as seen from problems $\mathsf { P } _ { \mathrm { G S } }$ and $\mathsf { P } _ { \mathrm { G S } } ^ { \prime } .$ Given the server position, channel gains can be pre-determined by a radio map RM, which is a function that maps the robot location $( a _ { t } , b _ { t } )$ to the corresponding signal attenuation as $| h _ { t } | ^ { 2 } = \dot { \mathsf { R M } } ( a _ { t } , \dot { b } _ { t } )$ . This radio map can be obtained by learning from radio measurements in various positions [36]. The variance of radio measurements can be adopted to compute channel uncertainties $\omega ^ { 2 }$ [37]. Note that to reduce the cost of radio measurements, it is possible to combine ray tracing [38], e.g., Nvidia sionna (https://developer.nvidia.com/sionna) with the measurement dataset for faster radio mapping.

## VI. MORE EXTENSIONS OF GSCLO

This section presents more variants of GSCLO to achieve low-power GSMR and multi-robot GSMR.

## A. Low-Power GSCLO

The nominal problem $\mathsf { P } _ { \mathrm { G S } }$ minimizes the GSMR loss under a given power budget, which is often adopted in resourceconstrained systems. In QoE constrained systems, it is necessary to minimize the total power consumption under RoboMR QoE constraints, which leads to the following related problem of $\mathsf { P } _ { \mathrm { G S } } ;$

$$
\left| \mathsf {Q} _ {\mathrm{GS}}: \min _ {\mathcal {P}, \mathcal {X}} \frac {1}{T} \sum_ {t = 1} ^ {T} p _ {t} \right|\tag{27a}
$$

<!-- page 8 of 14 -->

8

$$
\text {s.t.} \quad \frac {1}{T} \sum_ {t = 1} ^ {T} \Theta_ {t} (x _ {t}) \leq L _ {\mathrm{th}},\tag{27b}
$$

$$
\text {constraints} (1 1 b), (1 1 d), p _ {t} \geq 0, \forall t,\tag{27c}
$$

where $L _ { \mathrm { t h } }$ is a threshold to guarantee desired QoE. According to $[ 2 4 ]$ and our own experiments, to ensure satisfactory image qualities, the PSNR should be controlled between 30 dB to 40 dB, which corresponds to a loss between 0.02 and 0.04. Therefore, we can set $L _ { \mathrm { t h } } \in [ 0 . 0 2 , 0 . 0 4 ]$ . The above problem $\mathrm { Q _ { G S } }$ can be solved by following a similar APO approach in Section IV.

Problem Q<sub>GS</sub> guarantees the average QoE over all images. In practice, one may also consider individual QoE constraints for each image frame, which leads to

$$
\left| \mathrm{Q} _ {\mathrm{GS}} ^ {\prime}: \min _ {\mathcal {P}, \mathcal {X}} \frac {1}{T} \sum_ {t = 1} ^ {T} p _ {t} \right|\tag{28a}
$$

$$
\text {s.t.} \Theta_ {t} (x _ {t}) \leq L _ {\mathrm{th}}, \forall t\tag{28b}
$$

$$
\text {constraints} (1 1 b), (1 1 d), p _ {t} \geq 0, \forall t.\tag{28c}
$$

This problem has a closed-form solution, which is given in the following proposition.

**Proposition 3.** The optimal solution $\{ x _ { t } ^ { \star } , p _ { t } ^ { \star } \}$ to $\mathrm { Q _ { G S } ^ { \prime } }$ is

$$
(x _ {t} ^ {*}, p _ {t} ^ {*}) = \left\{ \begin{array}{l l} (1, \frac {\sigma^ {2}}{| h _ {t} | ^ {2}} 2 ^ {\frac {I}{\tau B}} - \frac {\sigma^ {2}}{| h _ {t} | ^ {2}}), & \text {if} L _ {t} > L _ {\text {th}} \\ (0, \frac {\sigma^ {2}}{| h _ {t} | ^ {2}} 2 ^ {\frac {S}{\tau B}} - \frac {\sigma^ {2}}{| h _ {t} | ^ {2}}), & \text {if} L _ {t} \leq L _ {\text {th}} \end{array} \right.,\tag{29}
$$

Proof. We first observe that the optimal solution must activate constraint (11b), which gives

$$
p _ {t} = \frac {\sigma^ {2} \left[ 2 ^ {\frac {(I - S) x _ {t} + S}{\tau B}} - 1 \right]}{| h _ {t} | ^ {2}}.\tag{30}
$$

Substituting this equation into the cost function of $\mathrm { Q _ { G S } ^ { \prime } }$ , the problem is equivalently rewritten as

$$
\min _ {\mathcal {X}} \frac {1}{T} \sum_ {t = 1} ^ {T} \frac {\sigma^ {2} \left[ 2 ^ {\frac {(I - S) x _ {t} + S}{\tau B}} - 1 \right]}{| h _ {t} | ^ {2}}\tag{31a}
$$

$$
\text {s.t.} L _ {t} (1 - x _ {t}) - L _ {\mathrm{th}} \leq 0, x _ {t} (1 - x _ {t}) = 0, \forall t.\tag{31b}
$$

The objective function is a monotonically increasing function of $\scriptstyle { \left[ x _ { t } \right. }$ . This implies that changing $x _ { t }$ from 1 to 0 always reduces the power. Combining the constraints (31b), we immediately obtain (29), and the proof is completed. □

According to **Proposition 3**, the frame transmit power p<sub>t</sub> is inversely proportional to the wireless channel gain $| h _ { t } | ^ { 2 }$ However, it is exponentially dependent on the content data volume (I, S), which is further controlled by GS losses $\{ L _ { t } \}$ The above observations disclose that in GSMR systems, the GS parameters will have more significant impacts on the physical layer design than those of the wireless channels. Therefore, the principle of GSMR is to allocate more power to frames associated with high GS losses.

**Proposition 3** can be used to evaluate the communication overhead saving brought by GSMR compared to RoboMR. Specifically, we compute the power consumption of $\sum p _ { t } ^ { \mathrm { M R } }$

where $p _ { t } ^ { \mathrm { M R } }$ is the solution to $\mathrm { Q _ { G S } }$ under condition $\{ x _ { t }   =$ $1 \| \forall t \}$ . This gives

$$
p _ {t} ^ {\mathrm{MR}} = \frac {\sigma^ {2} (2 ^ {\frac {I}{\tau B}} - 1)}{| h _ {t} | ^ {2}}.\tag{32}
$$

Thus, we have

$$
\begin{array}{c} \hline \Delta P = \sum_ {t = 1} ^ {T} p _ {t} ^ {\mathrm{MR}} - \sum_ {t = 1} ^ {T} p _ {t} ^ {*} \\ = \sum_ {t = 1} ^ {T} \frac {\mathbb {I} _ {L _ {t} \leq L _ {\mathrm{th}}} (L _ {t}) (2 ^ {\frac {I}{\tau B}} - 2 ^ {\frac {S}{\tau B}})}{| h _ {t} | ^ {2}}, \end{array}\tag{33}
$$

where indicator function $\mathbb { I } _ { \mathcal { C } } ( x ) = 1   \mathrm { ~ i f ~ }   x \in \mathcal { C }$ and zero otherwise. We refer to this quantity as **GS power saving factor**. It can be seen that this factor is proportional to $\textstyle \sum _ { t = 1 } ^ { T } \frac { \mathbb { I } _ { L _ { t } \leq L _ { \operatorname { t h } } } ( L _ { t } ) } { | h _ { t } | ^ { 2 } }$ , meaning that the power saving is determined by the percentage of qualified GS images.

## B. Multi-Robot GSCLO

In multi-robot settings, the key is to avoid multi-user interference during data uploading. A common way is to adopt multi-antenna signal processing at the server [39], and the aggregated signal received at edge server at time t becomes

$$
\mathbf {z} _ {t} = \sum_ {k = 1} ^ {K} x _ {k, t} \mathbf {h} _ {k, t} s _ {k, t} + \mathbf {n} _ {t},\tag{34}
$$

where N is the number of antennas, K is the number of robots, $\begin{array} { l } { { { \bf { z } } _ { t } } = [ { z _ { 1 , t } } , \cdots , { z _ { N , t } } ] ^ { T } \in { \mathbb { C } ^ { N \times 1 } } } \\ \end{array}$ is the received signal, $\mathbf { h } _ { k , t } \in \mathbb { C } ^ { N \times 1 }$ denotes the channel from the k-th robot to the edge server, and $\mathbf { n } _ { t } \in \mathbb { C } ^ { N \times 1 }$ is noise vector with zero mean and covariance $\mathbb { E } \{ \mathbf { n } _ { t } \mathbf { n } _ { t } ^ { H } \} = \sigma ^ { 2 } \mathbf { I } _ { N } ( \mathbf { I } _ { N }$ is the identity matrix of size $N \times N )$ . Let $\mathbf { H } _ { t }   =   [ \mathbf { h } _ { 1 , t } , \ldots , \mathbf { h } _ { K , t } ] ,$ ∀k. By applying the zero-forcing receiver $\stackrel { \triangledown } { [ 3 9 ] } ~ [ \mathbf { w } _ { 1 , t } ^ { H } , \mathbf { \widetilde { w } } _ { 2 , t } ^ { H } , . . . , \mathbf { w } _ { K , t } ^ { H } ] ^ { T } ~ =$ $( \mathbf { \tilde { H } } _ { t } ^ { H } \mathbf { H } _ { t } ) ^ { - 1 } \mathbf { H } _ { t } ^ { H }$ to recover the uplink signal, i.e., $\widehat { z } _ { k , t }   =   \mathbf { \widetilde { w } } _ { k , t } ^ { H } \mathbf { z } _ { b }$ we have w $\mathbf { \sigma } _ { i , t } ^ { H } \mathbf { h } _ { j , t } = 0 , \forall i \neq j$ . Therefore, the data-rate of robot k is

$$
R _ {k, t} (p _ {k, t}) = B \log_ {2} \left(1 + \frac {H _ {k , t} p _ {k , t}}{\sigma^ {2}}\right).\tag{35}
$$

where

$$
H _ {k, t} = \frac {| \mathbf {w} _ {k , t} ^ {H} \mathbf {h} _ {k , t} | ^ {2}}{\| \mathbf {w} _ {k , t} ^ {H} \| _ {2} ^ {2}}.\tag{36}
$$

Accordingly, problem $\mathsf { P } _ { \mathrm { G S } }$ in multi-robot settings is formulated as

$$
\mathrm{M} _ {\mathrm{GS}}: \quad \min _ {\left\{p _ {k, t}, x _ {k, t} \right\}} \frac {1}{T} \sum_ {t = 1} ^ {T} \sum_ {k = 1} ^ {K} L _ {k, t} \left(1 - x _ {k, t}\right)\tag{37a}
$$

$$
\begin{array}{l} \text {s.t.} \quad \tau R _ {k, t} (p _ {k, t}) \geq x _ {k, t} I + (1 - x _ {k, t}) S, \forall k, t, \end{array}\tag{37b}
$$

$$
\frac {1}{T} \sum_ {t = 1} ^ {T} p _ {k, t} \leq P, p _ {k, t} \geq 0, \forall k, t,\tag{37c}
$$

$$
x _ {k, t} \in \{0, 1 \}, \forall k, t.\tag{37d}
$$

Problem $M _ { \mathrm { G S } }$ has the same structure as problem $\mathsf { P } _ { \mathrm { G S } }$ , and can be readily solved using the APO algorithm.

<!-- page 9 of 14 -->

9

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p9_b2.png)

(a) Real AGX.

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p9_b4.png)

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p9_b5.png)

(c) LIMO robot.

(b) Virtual AGX.

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p9_b8.png)

(d) Robot route.

Fig. 4: Implementation of the RoboMR platform. In (d), the blue line represents robot trajectory, red boxes represent start and end positions, green boxes represent image poses, and blue boxes represent positions of virtual agents, respectively.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p9_b11.png)

(a) APO.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p9_b13.png)

(b) BILS.

Fig. 5: Convergence analysis. (a) $\| \Delta \mathbf { x } \|$ and $\phi ( \mathbf { x } )$ versus n for $\mathrm { A P O } ;$ (b) GSMR loss versus n for BILS.

## VII. EXPERIMENTS

We implement the RoboMR system exploiting C++ and Python in ROS. The real 4 m × 4 m Agilex (AGX) sandbox platform is shown in Fig. 4a. The virtual world constructed using the CARLA simulator [40] is shown in Fig. 4b, where two additional virtual objects (marked in white boxes) are added to the virtual world. The CARLA simulator is implemented on a workstation with a 3.7 GHZ AMD Ryzen 9 5900X CPU and an NVIDIA 3090 Ti GPU.

As shown in Fig. 4c, we adopt a robot named LIMO, which has a 2D lidar, an RGBD camera, and an onboard NVIDIA Jetson Nano computing platform for executing the localization and navigation packages. To realize RoboMR, the robot is connected to the CARLA simulator via ROS bridge [41]. The robot route is marked as the blue line in Fig. 4d. We navigate the LIMO robot along the route for two rounds. In the first round, the robot collects $H = 2 8 8$ frames (including images and poses) for training a GS model [24]. In the second round, the robot collects $T = 2 8 8$ frames for evaluation. Each image has a data volume of $I = 5 3 7 . 6   \mathrm { K }$ bits (i.e., 67.2 KBytes). The robot pose has 6 floating-point numbers, with $S = 1 9 2   \mathrm { { \sf b i t s } }$

Without otherwise specified, the time step $\tau \quad = \quad 0 . 1   \mathrm { s } ,$ bandwidth $B   =   1   \mathrm { M H z } ,$ noise power $\sigma ^ { 2 } \: = \: - 6 0   \mathrm { d B m } \: \left[ 3 9 \right]$

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p9_b20.png)

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p9_b21.png)

(a) Computation time.

(b) Loss comparison.

Fig. 6: Comparison of computation time and GSMR loss.

The channel is assumed to be Rician fading, i.e., [39]

$$
h _ {t} = \sqrt {\varrho_ {0} d _ {t} ^ {- \alpha}} \Big (\sqrt {\frac {\mathcal {K}}{1 + \mathcal {K}}} g _ {t} ^ {\mathrm{LOS}} + \sqrt {\frac {1}{1 + \mathcal {K}}} g _ {t} ^ {\mathrm{NLOS}} \Big),\tag{38}
$$

where $\varrho _ { 0 }   =   - 3 0   \mathrm { d B }$ is the pathloss at 1 m, $d _ { t }$ is the robotserver distance (i.e., 10 m), and $\alpha \quad = \quad 3$ is the pathloss exponent. Notice that K is the Rician K-factor accounting for propagation effects of the ling-of-sight $( \mathrm { L o S } )$ and non-LoS links. The LoS component is $\overline { { g _ { t } ^ { \mathrm { L O S } } } } ^ { - } = \exp { ( }$ (−jπ sin ψt) with $\psi _ { t } \in \mathcal { U } ( - \pi , \pi )$ being the phase angle, and the non-LoS component is $g _ { t } ^ { \mathrm { N L O \dot { S } } } \sim \mathcal { C N } ( 0 , 1 )$ [39]. All quantitative results are obtained by averaging over 50 random simulation runs, with independent channels in each run.

We compare GSMR with APO to the following baselines:

1) **RoboMR**: Vanilla RoboMR [6] uploading all images $( \mathrm { i . e . , ~ } \{ x _ { t } = 1 \} )$ ;

2) **RoboGS**: Vanilla GS [24] with no image uploading (i.e., $\{ x _ { t } = 0 \} ) ;$

3) **MaxRate**: GSMR with water-filling power allocation for sum-rate maximization [12];

4) **Fairness**: GSMR with max-min fairness power allocation [10];

5) **Ranking**: GSMR with (17);

6) **Search**: GSMR by solving $\mathsf { P } _ { \mathrm { G S } }$ with iterative local search [19];

7) **Rounding**: GSMR by solving $\mathsf { P } _ { \mathrm { G S } }$ with continuous relaxation and rounding [28];

8) **Mosek**: GSMR by solving $\mathsf { P } _ { \mathrm { G S } }$ with Mosek [18].

## A. Experiment 1: Convergence and Computation Time

First, we conduct numerical experiments to validate the convergence of the proposed Algorithm 1 (i.e., APO GSCLO). Specifically, we consider the case of $P   =   5   \mathrm { m W }$ and $\mathcal { K } =$ 30 dB. The variation between consecutive iterations $\| \Delta \mathbf { x } \|$ with $\Delta \mathbf { x } = \mathbf { x } ^ { [ n ] }   -   \mathbf { x } ^ { [ n - 1 ] }$ versus the iteration count n is shown in Fig. 5a. It can be seen that $\| \Delta \mathbf { x } \|$ falls below $1 0 ^ { - 4 }$ after 35 iterations. This demonstrates the convergence of the proposed APO. The zero-one loss $\begin{array} { r } { \phi ( \mathbf { x } )   =   \frac { 1 } { T } \sum _ { t = 1 } ^ { T } x _ { t } ( 1   -   \overset { \cdot } { x _ { t } } ) } \end{array}$ versus the iteration count n is also shown in ${ \mathrm { F i g . ~ } } 5 { \mathrm { a } } .$ . It can be seen that $\phi ( \mathbf { x } )$ is below 0.01 after 20 iterations, meaning that the APO algorithm converges to a point close to the desired binary solution. On the other hand, the convergence of the Algorithm 2 (i.e., Robust GSCLO) is shown in Fig. 5b. It can be seen

<!-- page 10 of 14 -->

10

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p10_b2.png)

(a) Loss versus P.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p10_b4.png)

(b) PSNR versus P.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p10_b6.png)

(c) SSIM versus P.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p10_b8.png)

(d) Energy efficiency versus P.

Fig. 7: Comparison of loss, PSNR, SSIM, and energy efficiency.

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p10_b11.png)

Fig. 8: Visualization of six image frames, where their positions are marked in Fig. 4d.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p10_b13.png)

(a) APO (Ours).

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p10_b15.png)

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p10_b16.png)

(b) Ranking.

(c) MaxRate.

Fig. 9: Content switching {x<sub>t</sub>} and power profiles {p<sub>t</sub>}.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p10_b20.png)

(a) APO (Ours).

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p10_b22.png)

(b) MaxImg.

Fig. 10: Comparison between APO and MaxImg.

that the average GSMR loss of Algorithm 2 converges and stabilizes after 50 iterations.

Next, we conduct numerical experiments to evaluate the computation time of the proposed APO algorithm. We consider the same setting as Experiment 1 (i.e, $P   =   5   \mathrm { m W }$ and $\mathcal { K }   =   3 0   \mathrm { d B } )$ . The computation time and associated MR loss for the Mosek, Search, and APO schemes are shown in Fig. 6a and Fig. 6b, respectively. The proposed APO reduces the computation time by at least 100x compared to Mosek in Fig. 6a, while guaranteeing close-to-optimal performance in Fig. 6b. The Search scheme leads to moderate computation

time, but the worst MR performance. Note that our method can be further accelerated by multi-core computing, efficient programming languages (e.g., C++), and receding horizon optimization.

## B. Experiment 2: Comparison with Existing Benchmarks

We compare the proposed GSMR with APO to all the benchmark schemes mentioned in Section VII. We consider the case of $P   =   \{ 1 0 , 2 0 , 3 0 , 4 0 \}$ mW and ${ \mathcal { K } }   =   0   \mathbf { d B } .$ . It can be seen from Fig. 7a that as the power budget increases, the losses of all the simulated schemes are reduced. Moreover, no matter how the power budget varies, the proposed GSMR with APO achieves a loss below 0.03, and consistently outperforms all the other schemes. In particular, the loss reduction is at least 10%. The PSNR performance of all the simulated schemes are shown in Fig. 7b. It can be seen that the proposed APO achieves a PSNR above 30 dB under all power budgets. Compared with all the other schemes, the improvement of PSNR is at least 5 dB, which is significant in RoboMR systems. By comparing Fig. 7a and Fig. 7b, we can find that a PSNR from 30 dB to 40 dB roughly corresponds to a loss from 0.035 to 0.02. The SSIM performance of all the simulated schemes are shown in Fig. 7c. Again, the proposed GSMR with APO outperforms all the other schemes in terms of the SSIM metric. Especially at higher power budgets, our SSIM values are very close to 1. This demonstrates the allround ability of APO. Lastly, the energy efficiencies of the simulated schemes are shown in Fig. 7d. It can be seen that the proposed APO achieves an energy efficiency close to the optimal bound<sup>2</sup>, demonstrating its excellent balance between energy efficiency and MR performance. The Ranking scheme only considers the GSMR losses, thus leading to the worst efficiency. Note that the energy efficiencies of all schemes decease as the power budget increases. This is because the transmit power acts as the denominator and the transmission rate increases slower than the transmit power.

## C. Experiment 3: Visualizations

To demonstrate the benefit brought by cross-layer optimization, we consider the case of P = 10 mW and ${ \mathcal { K } }   =   0   \mathrm { d } \mathbf { B }$ and compare APO with the MaxRate and Ranking schemes.

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>2</sup>Under a fixed power consumption, the MaxRate scheme would achieve the optimal energy efficiency, since it maximizes the sum-rate using water-filling power allocation [11]</span></small>

<!-- page 11 of 14 -->

11

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p11_b2.png)

(a) Loss versus P.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p11_b4.png)

(b) PSNR versus P.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p11_b6.png)

(c) Packet loss probability versus P.

Fig. 11: Comparison of loss, PSNR, and packet loss under channel uncertainties.

TABLE II: Comparison Between MaxImg and APO

<table><tr><td rowspan="2">Metric P</td><td colspan="2">Loss</td><td colspan="2">PSNR</td><td colspan="2">SSIM</td></tr><tr><td>MaxImg</td><td>APO (Ours)</td><td>MaxImg</td><td>APO (Ours)</td><td>MaxImg</td><td>APO (Ours)</td></tr><tr><td>5 mW</td><td>0.04324</td><td>0.03766</td><td>26.4852</td><td>26.9486</td><td>0.95488</td><td>0.96125</td></tr><tr><td>6 mW</td><td>0.04142</td><td>0.03694</td><td>27.1953</td><td>27.6038</td><td>0.95670</td><td>0.96201</td></tr><tr><td>7 mW</td><td>0.04016</td><td>0.03537</td><td>27.9208</td><td>28.3188</td><td>0.95812</td><td>0.96362</td></tr><tr><td>8 mW</td><td>0.03870</td><td>0.03411</td><td>28.5713</td><td>29.0831</td><td>0.95992</td><td>0.96506</td></tr></table>

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p11_b11.png)

The MaxRate represents the communication-centric scheme without considering MR requirements, while the Ranking scheme represents the GS-centric scheme without considering communication constraints. The qualitative results are shown in Fig. 8. It can be seen that all the images of APO have high qualities. This corroborates Fig. 9a, where the most images with high GS losses are uploaded. In contrast, images B and F are blurred for the ranking scheme. This is because the ranking scheme allocates more resources to frames with higher GS losses. However, several frames experience bad channel conditions, costing excessive power resources as shown in Fig. 9b. In addition, image E is distorted for the MaxRate scheme. This is because the MaxRate scheme allocates excessive resources to frames with good channel conditions for rate maximization as shown in Fig. 9c, ignoring the MR requirements.

One may wonder whether the superior performance of APO is due to more images uploaded to the server. To see this, we further compare the proposed APO method with the following:

In particular, we consider the case of $P   \mathrm { ~ = ~ }   8   \mathrm { m W }$ and $\mathcal { K }   =   3 0   \mathrm { d B }$ . It can be seen from Fig. 10a and Fig. 10b that the MaxImg scheme uploads more images than our method. However, the MR loss, PSNR, and SSIM performances of the MaxImg scheme are worse than those of our APO, as shown in Table II. This is because the MaxImg waste resources on frames with high GS rendering qualities. These frames should have been rendered at the server side without any image uploading. Our method is aware of the GS model and **focus on the frames that cannot be generated by the GS model**. We also provide the quantitative results for the cases of $P = \{ 5 , 6 , 7 \}$ mW in Table II. The APO method consistently outperforms MaxImg by a large margin.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p11_b15.png)

(a) APO-based GSCLO.

## • MaxImg, a GSMR scheme that maximizes the number of uploaded images.

(b) BILS-based robust GSCLO.

Fig. 12: Content switching {x<sub>t</sub>} and power profiles $\{ p _ { t } \}$ under channel uncertainties.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p11_b20.png)

Fig. 13: Power consumption.

## D. Experiment 4: Evaluation of Robust GSCLO

To evaluate the robustness of GSCLO against channel uncertainties, we compare the proposed BILS in Algorithm 2 of Section V and the APO in Algorithm 1 of Section IV. We consider the case of $P = \{ 1 0 , 2 0 , 3 0 , 4 0 \}$ mW and $\mathcal { K } = 1 0   \mathrm { d B }$ The mean of channel $\tilde { h } _ { t }$ is generated using (38), and the channel uncertainty is set to $\omega ^ { 2 } = 0 . 0 4 | \tilde { h } _ { t } | ^ { 2 }$ . The threshold of chance constraint (24b) is set to $\epsilon = 0 . 1$ . First, by comparing Fig. 7 and Fig. 11, it can be seen that the performance of the proposed APO is degraded when there exists errors in channel estimation. Second, the proposed robust GSCLO with BILS (i.e., Algorithm 2) consistently outperforms the proposed GSCLO with APO (i.e., Algorithm 1), in terms

<!-- page 12 of 14 -->

12

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p12_b2.png)

Fig. 14: The multi-robot GSMR experiment. Left-hand side: Image positions in the multi-robot MR scenario, where red arrow denotes robot 1 and blue arrow denotes robot 2. Right-hand side: Visualization of robots’ images.

TABLE III: Comparison of GS, MaxRate, and APO in Multi-Robot Scenarios

<table><tr><td rowspan="2">Power P</td><td rowspan="2">Robot ID</td><td colspan="3">Loss</td><td colspan="3">PSNR</td><td colspan="3">SSIM</td></tr><tr><td>GS</td><td>MaxRate</td><td>APO (Ours)</td><td>GS</td><td>MaxRate</td><td>APO (Ours)</td><td>GS</td><td>MaxRate</td><td>APO (Ours)</td></tr><tr><td rowspan="2">5 mW</td><td>1</td><td>0.0987</td><td>0.0967</td><td>0.0492</td><td>16.676</td><td>17.309</td><td>33.529</td><td>0.874</td><td>0.877</td><td>0.937</td></tr><tr><td>2</td><td>0.173</td><td>0.170</td><td>0.0848</td><td>13.258</td><td>13.850</td><td>31.137</td><td>0.785</td><td>0.788</td><td>0.896</td></tr><tr><td rowspan="2">10 mW</td><td>1</td><td>0.0987</td><td>0.0779</td><td>0.0298</td><td>16.676</td><td>23.379</td><td>40.522</td><td>0.874</td><td>0.901</td><td>0.961</td></tr><tr><td>2</td><td>0.173</td><td>0.140</td><td>0.0445</td><td>13.258</td><td>20.058</td><td>39.796</td><td>0.785</td><td>0.826</td><td>0.946</td></tr></table>

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p12_b6.png)

(a) Unitree Go2 robotic platform.

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p12_b8.png)

(b) Robot training trajectory.

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p12_b10.png)

(c) Robot testing trajectory.

Fig. 15: The robotic dog platform and its associated trajectories for training and testing.

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p12_b13.png)

Fig. 16: The GS point cloud and 3D GS model.

of both loss and PSNR performances. In particular, the loss is reduced by about 10%, and the PSNR is improved by about 2 dB. This is because the BILS-based robust GSCLO **boosts the transmit powers of key frames to ensure their successful transmission**, by reducing the number of image uploads as shown in Fig. 12. In contrast, the APO-based GSCLO allocates exact transmit powers satisfying constraint (11b), which may fail in satisfying (11b) when $h _ { t } = \tilde { h } _ { t }   +   \Delta h _ { t }$ as in (19), thus failures of transmission when the channel is deteriorated. This also corroborates Fig. 11c, where the packet loss probabilities of the proposed robust GSCLO with BILS are strictly below ϵ = 0.1, while the APO GSCLO leads to

higher packet loss probabilities. The above results demonstrate that the proposed BILS-based robust GSCLO is more resilient to channel uncertainties than the APO-based GSCLO.

## E. Experiment 5: Power Minimization GSCLO

To evaluate the power saving brought by GSCLO, we compare the proposed power minimization GSCLO in Section VI-A and RoboMR. The average transmit power versus the MR loss requirement $L _ { \mathrm { t h } }$ at $\mathcal { K } = 3 0   \mathrm { d B }$ is shown in Fig. 13. According to [24], to ensure satisfactory images, the PSNRs should be controlled between 30 dB and 40 dB. Further leveraging the results in Experiment 2, a threshold $L _ { \mathrm { t h } }$ between 0.01 and 0.04 would be a proper choice for constraining the MR loss in practice. Under $L _ { \mathrm { t h } } \in [ 0 . 0 1 , 0 . 0 4 ]$ it can be seen from Fig. 13 that the power saved by GS is at least 2 dB. Particularly, when the loss threshold is 0.03, the power saved by GSCLO is larger than 6 dB, i.e., equal to 75% power reduction. This result reveals that **robotic mixed reality can be achieved with ultra-low communication costs (**< 200 **bits/frame) if Gaussian splatting is leveraged properly**. With ultra-low communication costs, it is possible

<!-- page 13 of 14 -->

13

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p13_b2.png)

(a) Loss versus P.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p13_b4.png)

(b) PSNR versus P.

![Chart block](images/liu2025_robotic-mr-gs-crosslayer_p13_b6.png)

(c) SSIM versus P.

Fig. 17: Quantitative comparison between the proposed APO and other benchmarks for the robotic dog experiment 7.

![Image block](images/liu2025_robotic-mr-gs-crosslayer_p13_b9.png)

Fig. 18: Visualization for the robotic dog experiment.

to connect massive robots with the virtual world, forming a metaverse space.

## F. Experiment 6: Evaluation of Multi-Robot GSCLO

To evaluate the performance of the proposed method in Section VI-B under multi-robot settings, we consider the case of $N = 4$ and $K = 2$ with $T   =   4 3 3$ in the AGX scenario shown in Fig. 14. We compare APO with the MaxRate and GS schemes under the settings of $P \in \{ 5 , 1 0 \}$ mW and $\mathcal { K } = 0   \mathrm { d B }$ The loss, PSNR, and SSIM results are shown in Table III. Qualitative results are shown in Fig. 14. It can be seen that the solution maintains efficiency with more robots, by mitigating the co-channel interference among different devices via multi-antenna techniques. This also demonstrates that our method works well under longer operation time.

## G. Experiment 7: Robotic Dog in Larger Environments

Finally, we conduct experiments using the Unitree Go2 robotic dog platform shown in Fig. 15a in a larger environment. We navigated the dog for two rounds in an office building. In the first round, the robot collects $H = 4 0 0$ samples (including images and poses) for training a GS model. The trajectory of the training data is shown in Fig. 15b. The obtained GS point cloud and GS model are shown in Fig. 16. In the second round, the robot collects $T \; = \; 3 7 0$ samples for evaluation. The trajectory of the testing data is shown in Fig. 15c. It can be seen that the testing poses are random and different from the training poses. Each image has a data volume of I = 13.84 Mbits (1.73 MBytes).

We simulate the case of B = 20 MHz in non-LoS settings, where the server is marked as purple box in Fig. 15c. The channel is assumed to be Rayleigh fading, i.e.,

$$
h _ {t} = \sqrt {\varrho_ {0} \omega_ {0} d _ {t} ^ {- \alpha}} g _ {t} ^ {\text {NLOS}},\tag{39}
$$

where $\omega _ { 0 } ~ = ~ - 1 0   \mathrm { d B }$ is the wall blockage fading, $d _ { t }$ is computed based on the robot trajectory and the server position. The loss, PSNR, and SSIM results are shown in Fig. 17. It can be seen that no matter how power budget changes, the proposed APO outperforms other benchmarks by a large margin in terms of all the performance metrics.

Qualitative results are shown in Fig. 18, where captions A and B represent fisheye cameras A and B. Inside the view of camera A, the screen is playing video and the environment is changing. It can be seen that all the images of our APO-based GSMR have high qualities. This is because if the robot detects a significant discrepancy between the real captured image and the GS rendered view (i.e., “memory bias”)<sup>3</sup>, our method would trigger an image upload. In contrast, the existing GS scheme works poorly in dynamic scenarios. This is due to the inherent limitation of static reconstruction. This result suggests that **mixture of data is useful for enhancing GS performance in dynamic scenarios**.

## VIII. CONCLUSION

This paper presented GSMR, which realizes low-cost communication between the simulation server and the robot via the introduction of GS. A GSCLO framework was proposed

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>3</sup>In practice, such discrepancies can be estimated using pilot images.</span></small>

<!-- page 14 of 14 -->

14

to mitigate the discrepancies between GS-rendered images and real-world environments. Extensive experiments were conducted, which demonstrate the effectiveness, stability, and robustness of GSMR on wheeled-robot, legged-robot, and multi-robot platforms in various scenarios. It is found that the GS model indeed helps MR, but we need to carefully avoid memory bias. Furthermore, under channel uncertainties, we should boost transmit powers of key frames, so as to ensure successful pose and image uploads.

## REFERENCES

[1] C. Liu, H. Li, Z. Li, S. Wang, W. Xu, K. Ye, D. W. K. Ng, and C. Xu, “Green robotic mixed reality with gaussian splatting,” in Proc. INFOCOM Workshop on NetRobiCS, 2025, pp. 1–6.

[2] C. Li, F. Xia, R. Mart´ın-Mart´ın, M. Lingelbach, S. Srivastava, B. Shen, K. Vainio, C. Gokmen, G. Dharan, T. Jain et al., “iGibson 2.0: Objectcentric simulation for robot learning of everyday household tasks,” in Proc. CoRL, 2021.

[3] S. Wang, C. Li, D. W. K. Ng, Y. C. Eldar, H. V. Poor, Q. Hao, and C. Xu, “Federated deep learning meets autonomous vehicle perception: Design and verification,” IEEE Netw., vol. 37, no. 3, pp. 16–25, May/Jun. 2023.

[4] L. Morra, F. Lamberti, F. G. Prattico, S. La Rosa, and P. Montuschi, ´ “Building trust in autonomous vehicles: Role of virtual reality driving simulators in HMI design,” IEEE Trans. Veh. Technol., vol. 68, no. 10, pp. 9438–9450, Oct. 2019.

[5] J. Delmerico, R. Poranne, F. Bogo, H. Oleynikova, E. Vollenweider, S. Coros, J. Nieto, and M. Pollefeys, “Spatial computing and intuitive interaction: Bringing mixed reality and robotics together,” IEEE Robot. Autom. Mag., vol. 29, no. 1, pp. 45–57, Mar. 2022.

[6] H. Li, R. Han, Z. Zhao, W. Xu, Q. Hao, S. Wang, and C. Xu, “Seamless virtual reality with integrated synchronizer and synthesizer for autonomous driving,” IEEE Robot. Autom. Lett., vol. 9, no. 5, May 2024.

[7] F. Guo, F. R. Yu, H. Zhang, H. Ji, V. C. Leung, and X. Li, “An adaptive wireless virtual reality framework in future wireless networks: A distributed learning approach,” IEEE Trans. Veh. Technol., vol. 69, no. 8, pp. 8514–8528, Aug. 2020.

[8] E. Bastug, M. Bennis, M. Medard, and M. Debbah, “Toward intercon- ´ nected virtual reality: Opportunities, challenges, and enablers,” IEEE Commun. Mag., vol. 55, no. 6, pp. 110–117, Jun. 2017.

[9] M. Chen, Y. Zhou, M. Chen, and M. Debbah, “VR over wireless networks: QoS model and learning-based resource management,” IEEE Trans. Commun., vol. 66, no. 11, pp. 5621–5635, Nov. 2018.

[10] L. Zheng, Y.-W. P. Hong, C. W. Tan, C.-L. Hsieh, and C.-H. Lee, “Wireless max–min utility fairness with general monotonic constraints by perron–frobenius theory,” IEEE Trans. Inf. Theory., vol. 62, no. 12, pp. 7283–7298, Jan. 2016.

[11] W. Yu, W. Rhee, S. Boyd, and J. M. Cioffi, “Iterative water-filling for Gaussian vector multiple-access channels,” IEEE Trans. Inf. Theory., vol. 50, no. 1, pp. 145–152, Jan. 2004.

[12] Q. Zhang, M. Shao, T. Zhang, G. Chen, J. Liu, and P. Ching, “An efficient sum-rate maximization algorithm for fluid antenna-assisted ISAC system,” IEEE Commun. Lett., vol. 29, no. 1, pp. 200–204, 2024.

[13] L. V. Cakir, C. J. Thomson, M. Ozdem, B. Canberk, V.-L. Nguyen, and T. Q. Duong, “Intelligent digital twin communication framework for addressing accuracy and timeliness tradeoff in resource-constrained networks,” IEEE Trans. Cogn. Commun. Netw., vol. 11, no. 3, pp. 1954–1965, 2025.

[14] Y. Jiang, J. Kang, X. Ge, D. Niyato, and Z. Xiong, “QoE analysis and resource allocation for wireless metaverse services,” IEEE Trans. Commun., vol. 71, no. 8, pp. 4735–4746, Aug. 2023.

[15] S. Cheng, F. Feng, T. Bi, and T. Jiang, “Resource-aware reinforcement learning-based transmission optimization for mobile augmented reality in edge computing,” IEEE Trans. Cogn. Commun. Netw., vol. 11, no. 4, pp. 2356–2367, 2025.

[16] L. Zhao, Y. Liu, A. Y. Al-Dubai, A. Y. Zomaya, G. Min, and A. Hawbani, “Adaptive swarm intelligent offloading based on digital twin-assisted prediction in vehicular edge computing,” IEEE Trans. Mob. Comput., vol. 23, no. 8, pp. 8158–8174, Aug. 2024.

[17] G. Pan, H. Zhang, S. Xu, S. Zhang, and X. Chen, “Joint optimization of video-based AI inference tasks in MEC-assisted augmented reality systems,” IEEE Trans. Cogn. Commun. Netw., vol. 9, no. 2, pp. 479–493, Apr. 2022.

[18] S. Diamond and S. Boyd, “CVXPY: A python-embedded modeling language for convex optimization,” J. Mach. Learn. Res., vol. 17, no. 1, pp. 2909–2913, Apr. 2016.

[19] F. Neumann and I. Wegener, “Randomized local search, evolutionary algorithms, and the minimum spanning tree problem,” Theor. Comput. Sci., vol. 378, no. 1, pp. 32–40, Jun. 2007.

[20] Z. Yang, Y. Chai, D. Anguelov, Y. Zhou, P. Sun, D. Erhan, S. Rafferty, and H. Kretzschmar, “Surfelgan: Synthesizing realistic sensor data for autonomous driving,” in Proc. CVPR, 2020, pp. 11 118–11 127.

[21] W. Li, C. Pan, R. Zhang, J. Ren, Y. Ma, J. Fang, F. Yan, Q. Geng, X. Huang, H. Gong et al., “AADS: Augmented autonomous driving simulation using data-driven algorithms,” Sci. Robot, vol. 4, no. 28, p. eaaw0863, 2019.

[22] S. Feng, Y. Feng, X. Yan, S. Shen, S. Xu, and H. X. Liu, “Safety assessment of highly automated driving systems in test tracks: A new framework,” Accid. Anal. Prev., vol. 144, p. 105664, Sep. 2020.

[23] S. Feng, H. Sun, X. Yan, H. Zhu, Z. Zou, S. Shen, and H. X. Liu, “Dense reinforcement learning for safety validation of autonomous vehicles,” Nature, vol. 615, no. 7953, pp. 620–627, Mar. 2023.

[24] B. Kerbl, G. Kopanas, T. Leimkuhler, and G. Drettakis, “3D Gaussian ¨ Splatting for real-time radiance field rendering.” ACM Trans. Graph., vol. 42, no. 4, pp. 139–1, Jul. 2023.

[25] N. Keetha, J. Karhade, K. M. Jatavallabhula, G. Yang, S. Scherer, D. Ramanan, and J. Luiten, “Splatam: Splat track & map 3D Gaussians for dense RGB-D SLAM,” in Proc. CVPR, 2024, pp. 21 357–21 366.

[26] R. Han, S. Wang, S. Wang, Z. Zhang, Q. Zhang, Y. C. Eldar, Q. Hao, and J. Pan, “RDA: An accelerated collision free motion planner for autonomous navigation in cluttered environments,” IEEE Robot. Autom. Lett., vol. 8, no. 3, pp. 1715–1722, Mar. 2023.

[27] S. Wang, A. Rehman, Z. Wang, S. Ma, and W. Gao, “SSIM-motivated rate-distortion optimization for video coding,” IEEE Trans. Circuits Syst. Video Technol., vol. 22, no. 4, pp. 516–529, Apr. 2011.

[28] R. Hubner and A. Sch ¨ obel, “When is rounding allowed in integer ¨ nonlinear optimization?” Eur. J. Oper. Res., vol. 237, no. 2, pp. 404–410, Sep. 2014.

[29] F. Rinaldi, “New results on the equivalence between zero-one programming and continuous concave programming,” Optim. Lett., vol. 3, pp. 377–386, Mar. 2009.

[30] S. Lucidi and F. Rinaldi, “Exact penalty functions for nonlinear integer programming problems,” J. Optim. Theory Appl., vol. 145, pp. 479–488, Apr. 2010.

[31] L. T. H. An and P. D. Tao, “The DC (difference of convex functions) programming and DCA revisited with dc models of real world nonconvex optimization problems,” Ann. Oper. Res., vol. 133, pp. 23–46, Apr. 2005.

[32] H. Abbaszadehpeivasti, E. de Klerk, and M. Zamani, “On the rate of convergence of the difference-of-convex algorithm (DCA),” J. Optim. Theory Appl., vol. 202, pp. 475–496, Mar. 2024.

[33] M. K. Simon and M. S. Alouini, Digital Communication over Fading Channels. New Jersey, USA: John Wiley and Sons, Inc., 2005.

[34] Z. Li, S. Wang, P. Mu, and Y. Wu, “Probabilistic constrained secure transmissions: Variable-rate design and performance analysis,” IEEE Trans. Wireless Commun., vol. 19, no. 4, pp. 2543–2557, Apr. 2020.

[35] Z. Li, S. Wang, M. Wen, and Y.-C. Wu, “Secure multicast energyefficiency maximization with massive RISs and uncertain CSI: Firstorder algorithms and convergence analysis,” IEEE Trans. Wireless Commun., vol. 21, no. 9, pp. 6818–6833, Sep. 2022.

[36] R. Levie, Ç . Yapar, G. Kutyniok, and G. Caire, “Radiounet: Fast radio map estimation with convolutional neural networks,” IEEE Transactions on Wireless Communications, vol. 20, no. 6, pp. 4001–4015, Jun. 2021.

[37] M. Malmirchegini and Y. Mostofi, “On the spatial predictability of communication channels,” IEEE Trans. Wireless Commun., vol. 11, no. 3, pp. 964–978, Mar. 2012.

[38] K. Remley, H. Anderson, and A. Weisshar, “Improving the accuracy of ray-tracing techniques for indoor propagation modeling,” IEEE Trans. Veh. Technol., vol. 49, no. 6, pp. 2350–2358, Nov. 2000.

[39] S. Wang, M. Wen, M. Xia, R. Wang, Q. Hao, and Y.-C. Wu, “Angle aware user cooperation for secure massive mimo in rician fading channel,” IEEE J. Sel. Areas Commun., vol. 38, no. 9, pp. 2182–2196, Sep. 2020.

[40] A. Dosovitskiy, G. Ros, F. Codevilla, A. Lopez, and V. Koltun, “CARLA: An open urban driving simulator,” in Proc. CoRL, 2017, pp. 1–16.

[41] CARLA-ROS-Bridge: https://github.com/carla-simulator/ros-bridge.