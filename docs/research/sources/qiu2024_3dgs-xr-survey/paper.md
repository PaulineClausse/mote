<!-- page 1 of 6 -->

arXiv:2412.06257v2 [cs.CV] 12 Dec 2024

# Advancing Extended Reality with 3D Gaussian Splatting: Innovations and Prospects

Shi Qiu, Binzhu Xie, Qixuan Liu, Pheng-Ann Heng

Department of Computer Science and Engineering, The Chinese University of Hong Kong, HKSAR China Institute of Medical Intelligence and XR, The Chinese University of Hong Kong, HKSAR China

**Abstract—3D Gaussian Splatting (3DGS) has attracted significant attention for its potential to revolutionize 3D representation, rendering, and interaction. Despite the rapid growth of 3DGS research, its direct application to Extended Reality (XR) remains underexplored. Although many studies recognize the potential of 3DGS for XR, few have explicitly focused on or demonstrated its effectiveness within XR environments. In this paper, we aim to synthesize innovations in 3DGS that show specific potential for advancing XR research and development. We conduct a comprehensive review of publicly available 3DGS papers, with a focus on those referencing XR-related concepts. Additionally, we perform an in-depth analysis of innovations explicitly relevant to XR and propose a taxonomy to highlight their significance. Building on these insights, we propose several prospective XR research areas where 3DGS can make promising contributions, yet remain rarely touched. By investigating the intersection of 3DGS and XR, this paper provides a roadmap to push the boundaries of XR using cutting-edge 3DGS techniques.**

**Index Terms—3D Gaussian Splatting, Neural Rendering, XR.**

## I. INTRODUCTION

Extended Reality (XR), which includes Virtual Reality (VR), Augmented Reality (AR), and Mixed Reality (MR), represents a frontier in immersive technologies, aiming to seamlessly blend the physical and digital worlds. Achieving truly immersive XR experiences relies on advancements in 3D representation, rendering, and interaction techniques. In recent years, Neural Radiance Fields (NeRF) [1] have led the way in neural rendering research, enabling photorealistic depiction of complex scenes from multi-view observations. However, NeRF-based methods [2]–[4] often face challenges in real-time performance and effective integration into XR systems due to their high computational complexity and reliance on implicit scene representations through Multi-Layer Perceptrons (MLPs). This implicit representation, while powerful, makes it difficult to directly manipulate or interact with the underlying 3D geometry, further complicating their integration into XR systems. Recently, 3D Gaussian Splatting (3DGS) [5] has emerged as a promising alternative for effective 3D representations. By explicitly modeling scenes using learnable, parameterized 3D Gaussians, real-time rendering and manipulation can be achieved, offering a significant improvement in performance over NeRF approaches. The inherent efficiency and flexibility of

![Image block](images/qiu2024_3dgs-xr-survey_p1_b9.png)

Fig. 1: Word cloud extracted from recent 3DGS literature that references XR-related keywords. The size of each word reflects its frequency of occurrence, highlighting key concepts and trends in the intersection of 3DGS and XR technologies.

3DGS make it an ideal candidate for XR, where both responsive interaction and synergistic system integration are essential.

Despite rapid advancements and an increasing number of studies on 3DGS, its direct application within XR environments remains notably underexplored. To address this gap, we conduct a comprehensive review of the 3DGS literature, based on 272 publicly available papers<sup>1</sup>that cover recent published works in top-tier AI venues such as CVPR, ECCV, SIGGRAPH, and NeurIPS, etc. We systematically examine each paper, screening for XR-related content to assess their relevance to XR domains. Our preliminary analysis shows that more than half of these papers (i.e., 152 out of 272) explicitly mention XR concepts. Fig. 1 presents a word cloud visualizing the frequency of XR-related terms within the collected papers, highlighting common associations such as “virtual reality”, “novel scene”, “rendering”, “reconstruction”, etc.

Although many studies acknowledge the potential relevance of 3DGS to XR, our investigation reveals that the majority do not specifically exploit 3DGS techniques in XR environments. Instead, they often reference XR in a general and superficial

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">This work was supported in part by The Chinese University of Hong Kong (Project No.: 4055212); and in part by the Research Grants Council of the Hong Kong Special Administrative Region, China (Project No.: T45-401/22-N).</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">{shiqiu, bzxie, qxliu, pheng}@cse.cuhk.edu.hk</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>1</sup>Our collected papers span from the very first 3DGS publication [5] in July 2023 to those available as of late-October 2024.</span></small>

<!-- page 2 of 6 -->

manner, mentioning it as a potential application area without providing specific XR-based implementations or evaluations. The lack of studies that concretely apply 3DGS in XR settings presents both a challenge and an opportunity: the challenge of effectively integrating emerging 3DGS innovations into XR systems, and the opportunity to enhance XR experiences through the state-of-the-art 3DGS techniques. In this paper, we synthesize existing innovations, explore opportunities for future research and development, and provide a roadmap for exploiting the synergies between 3DGS and XR technologies. By doing so, we aim to inspire and guide future efforts in leveraging 3DGS to push the boundaries of XR, contributing to more immersive, interactive, and intelligent experiences.

## II. RELATED WORKS

## A. Representative 3DGS Works Targeting XR

Unlike most existing 3DGS studies that superficially mention XR, we have identified three representative works that specifically leverage 3DGS to advance XR research and development.

**VR-GS** [13]: Interacting with 3D models in VR is timeconsuming and complex due to the need for real-time synchronization of distinct geometry representations for simulation and rendering. Jiang et al. introduce VR-GS, a physics-aware system based on 3DGS for smooth creation, editing, and interaction experiences in VR [13]. (i) To ensure real-time deformation, VR-GS employs eXtended Position-based Dynamics (XPBD) [85]. (ii) To address the geometry mismatch between simulation and rendering, VR-GS constructs tetrahedral cages embedding GS kernel groups, driven by XPBD to guide deformation. By using a two-level embedding to prevent undesirable deformations and enabling offline preparation, VR-GS is ideal for VR content editing, significantly enhancing the immersive experience with realistic dynamics.

**DualGS** [12]: Volumetric videos provide a 6-DoF immersive experience in XR, but their creation, storage, and rendering often demand extensive manual intervention. Jiang et al. reduce storage and rendering demands for volumetric videos by introducing Dual Gaussian Splatting (DualGS) to realize efficient, high-fidelity real-time rendering of human performance in XR environments [12]. (i) To reduce motion redundancy and enhance temporal coherence, DualGS decouples motion and appearance using joint and skin Gaussians [86], employing a coarse-to-fine optimization to improve temporal coherence and tracking. (ii) For the compression strategy, DualGS uses entropy encoding and lookup table compression to reduce storage to ∼350KB per frame, realizing immersive user experiences like feeling present at a musician’s concert in XR.

**RGCA** [14]: Virtual avatar rendering shows great potential for XR-based gaming and telecommunication. To tackle lighting and detail challenges in virtual avatars for enhanced realism, Saito et al. introduce Relightable Gaussian Codec Avatars (RGCA), leveraging 3D Gaussians for high-fidelity, realtime rendering under various lighting conditions [14]. (i) To overcome the challenges of light scattering and reflection in complex materials: RGCA presents a relightable appearance model with learnable radiance transfer, utilizing spherical

harmonics and Gaussians; and invents a novel parameterization for specular reflection to accurately approximate complex light effects. (ii) For accurate hair rendering, RGCA uses convolutional layers to encode driving signals that captures fine hair details. (iii) For eye representation, RGCA develops an explicit eye model to improve realism and gaze control. These innovations tackle the complexities and challenges of human head rendering in XR applications.

## B. 3DGS Surveys

In this year of 2024, several surveys [87]–[92] have comprehensively explored the latest advancements from various perspectives of the 3DGS technology. Specifically, [88], [89] conduct systematic analyses of 3DGS, covering its foundational theories, optimization methods, applications, and future research directions. In addition, [91] reviews the rapid progress of 3DGS methods, classifying them into 3D reconstruction, 3D editing, and other downstream applications. Furthermore, some reviews focus on specific downstream applications of 3DGS: (i) [87] provides a detailed review of 3DGS development in 3D human modeling; (ii) [90] explores the evolution of simultaneous localization and mapping (SLAM) technology, highlighting its recent progress in radiance fields including 3DGS; and (iii) [92] concentrates on the latest techniques in 3D reconstruction and novel view synthesis, where 3DGS also plays an important role. While these surveys recognize the potential connections between 3DGS and XR, they do not specifically elaborate on their synergies and prospects, which are the primary focus of this paper.

## III. INNOVATIONS IN 3D GAUSSIAN SPLATTING FOR XR

To understand the impact of 3DGS on XR related areas, we have analyzed the collected literature and key innovations relevant to XR. As illustrated in Fig. 2, we identify five key areas where innovations significantly align with XR applications, forming the basis of our proposed taxonomy.

**3D Content Creation:** In human avatar modeling, 3DGS can enhance XR applications by enabling rapid, high-fidelity creation of animatable avatars, which are essential for immersive and personalized XR experiences in telepresence, virtual meetings, and interactive VR [8], [9], [11]. 3DGS also facilitates the reconstruction of realistic human avatars from minimal input data, such as monocular videos, directly addressing the demand driven by AR/VR wearables [15], [17], [20]. Additionally, 3DGS can support real-time rendering of high-quality human performances on VR headsets, enhancing accessibility and user engagement in XR collaborations [6], [7], [10]. In scene reconstruction, 3DGS provides efficient modeling of large-scale and complex scenes, which is essential for immersive navigation and interaction in virtual environments [22], [29]. 3DGS also allows for real-time rendering of extensive scenes from sparse views, facilitating free-viewpoint exploration and virtual tours in VR [23], [28], [39]. In textto-3D generation, 3DGS simplifies the pipeline of creating immersive virtual contents from textual descriptions [42], [44], [48]. This capability enhances interactivity and personalization

<!-- page 3 of 6 -->

![Image block](images/qiu2024_3dgs-xr-survey_p3_b1.png)

Fig. 2: Taxonomy of 3DGS Innovations Relevant to XR.

by letting users create and modify virtual contents using natural language input [46]. By addressing challenges related to the cost and complexity of developing rich digital worlds, 3DGS contributes to dynamic, user-adaptive functions, as well as more accessible and customizable XR experiences.

**Rendering & Visualization:** In real-time rendering, 3DGS optimizes neural rendering pipelines to facilitate real-time visualization of complex scenes and models, which is critical for interactive XR experiences where latency affects immersion [53], [56]. By efficiently managing streaming resources, 3DGS can enable smooth rendering and visualization of 3D objects on a range of devices, including those with limited hardware capabilities such as mobile AR glasses and VR headsets [12], [52], [54]. In photorealism & special effects, 3DGS can improve visual fidelity by accurately modeling material properties and light interactions for high levels of realism in immersive virtual environments [57], [59]. Additionally, it supports the integration of artistic styles and visual effects, assisting in creating stylized or customized visual experiences in XR [60], [61].

**Interaction & Manipulation:** In interactive scene editing, it is crucial for XR applications to empower users with the ability to interactively modify 3D elements in real-time within the virtual space. By allowing intuitive deformation and editing of 3D models through natural hand gestures or physics-aware interactions, 3DGS facilitates responsive object manipulation and environment customization, which are crucial for XR use

cases like collaborative design, prototyping, and personalized scene creation [13], [64], [66], [67]. In virtual object control, users can leverage 3DGS to generate controllable portraits with detailed expressions and motions, realizing personalized avatar customization and dynamic expression rendering for engaging and responsive XR interactions. [10], [20], [68].

**System Optimization & Efficiency:** In data compression, 3DGS optimizes the storage and rendering of complex 3D scenes by employing compact and efficient data structures, which is crucial for XR applications operating on mobile devices. The network pruning-driven method proposed in [69] achieves up to 15x compression of 3D Gaussians while maintaining rendering speeds over 200 FPS. Furthermore, efficient 3D Gaussian representations for monocular or multi-view dynamic scenes can reduce memory usage and processing demands required for reconstruction, making immersive XR experiences more feasible on hardware with limited capabilities [32]. In hardware acceleration, [26] introduces specialized hardware and algorithmic accelerations to improve real-time 3DGS rendering on mobile devices, addressing computational challenges in resource-constrained XR applications. Additionally, [56], [71] propose advanced optimization algorithms that further reduce memory usage and computational load of 3DGS techniques, aiming to achieve high-quality rendering on lowpower devices such as AR/VR headsets.

**Specialized Applications:** In SLAM, 3DGS serves as an effi-

<!-- page 4 of 6 -->

cient and effective 3D representation for real-time environment mapping and precise camera tracking. By leveraging 3DGS, dense visual SLAM can achieve improved rendering performance and trajectory accuracy, both essential for immersive XR experiences that depend on accurate spatial understanding [74], [76], [77]. Moreover, incorporating semantic and uncertaintyaware processing into 3DGS enhances robustness in dynamic environments, which can be further used in advanced XR applications like augmented reality navigation and interactive scanning [73], [75]. In medical XR, 3DGS leads to highquality and real-time 3D reconstructions and visualizations of anatomical structures, which are crucial for medical diagnostics, surgical planning, and immersive training simulations. For instance, recent [82], [83] apply 3DGS to reconstruct detailed 3D surgical scenes from endoscopic videos, making them useful for surgical simulations and preoperative diagnosis. Furthermore, compressing large medical datasets into compact 3DGS representations can create interactive and photorealistic rendering of anatomical models on light XR devices, giving users access to examine detailed 3D anatomy in real time [84].

## IV. FUTURE PROSPECTS

Despite significant advancements in 3DGS research, most of the studies concentrate on regular neural rendering tasks, such as 3D reconstruction and generation. These developments have improved our ability to create high-quality visual content, building groundwork for XR applications. However, there still remain many opportunities to deeply explore the synergies between 3DGS and XR technologies. The future topics may include, but are not limited to, the following:

• Mesh Modeling. One fundamental 3DGS application in XR is mesh modeling. High-fidelity mesh modeling is essential for creating virtual environments where accurate interactions between users and digital objects are crucial [93], [94]. By representing intricate surface details and complex geometries, we can further devise 3D Gaussians-based models to create more realistic and interactive 3D objects in virtual spaces. For example, GS-VTON [95] enables VR content personalization based on user preferences.

• Dynamic Scene Representation. 4D volumetric video is a valuable representation for dynamic scenes. To more effectively represent XR scenes, our future works should focus on enhancing 3DGS for real-time dynamic content capture, processing, and rendering with minimal latency. Moreover, efforts should target optimizing 3DGS to improve scalability for large-scale virtual spaces. For example, Gracia $\dot { \mathrm { A I } ^ { 2 } }$ develops a platform to create 3DGS-based volumetric videos for mobile VR devices.

• Open-world Scene Understanding. In AR and MR domains, open-world scene understanding is critical for seamless integration of virtual content with the real world. 3DGS can make contributions to topic by leveraging open-vocabulary 3D segmentation, which allows systems to recognize and interpret various objects and scenes without

being limited to a predefined set of categories. With the latest advancements in visual foundation models like SAM, it is now easier to enhance the scene understanding capabilities of AR/MR applications, leading to more intuitive and context-aware user experiences.

• Hand Tracking. By efficiently capturing and rendering the fine details of hand movements and gestures in real time, 3DGS can provide more accurate and fluid hand tracking, essential for XR interactions. Also, 3DGS can be leveraged to estimate hand pose with high precision, leading to precise recognition of complex gestures and finger movements. With reduced latency and improved dynamic motion capture in hand tracking, XR gaming, remote collaboration and virtual training, can benefit.

Passthrough Capabilities. For XR devices, this function aims to blend physical and virtual worlds, improving safety and immersion given appropriate interactions between virtual content and real-world surroundings. Following a similar technical approach used for novel view synthesis, 3DGS can enhance pass-through capabilities by delivering accurate real-time reconstructions of the user’s immediate environment. Simultaneously, practical challenges may arise, such as representing novel objects, maintaining high visual fidelity across various lighting conditions, etc.

• Immersive Visualization. By representing complex datasets as efficient 3D Gaussians with rich attributes, users can explore and interact with data more intuitively in immersive XR applications. 3DGS-based visualization approaches hold significant promise for fields such as scientific research, medical education, and statistical analytics, where processing and understanding complex, high-dimensional data is a fundamental problem.

## V. CONCLUSION

In this paper, we explore the intersection of 3DGS and XR, synthesizing key innovations in 3DGS that hold promise for advancing XR research and development. Through a comprehensive analysis of 3DGS literature, we highlight XR research directions where 3DGS could have a transformative impact. We expect this study to inspire further 3DGS research and push the boundaries of XR. Due to the rapid progress in both fields, we may have omitted some works that could also contribute to the discussion. In future work, we aim to deliver a comprehensive survey covering the entire spectrum of 3DGS advancements and their implications for XR.

## REFERENCES

[1] B. Mildenhall, P. P. Srinivasan, M. Tancik, J. T. Barron, R. Ramamoorthi, and R. Ng, “Nerf: Representing scenes as neural radiance fields for view synthesis,” Communications of the ACM, vol. 65, no. 1, pp. 99–106, 2021.

[2] A. Pumarola, E. Corona, G. Pons-Moll, and F. Moreno-Noguer, “Dnerf: Neural radiance fields for dynamic scenes,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2021, pp. 10 318–10 327.

[3] J. T. Barron, B. Mildenhall, M. Tancik, P. Hedman, R. Martin-Brualla, and P. P. Srinivasan, “Mip-nerf: A multiscale representation for anti-aliasing neural radiance fields,” in Proceedings of the IEEE/CVF international conference on computer vision, 2021, pp. 5855–5864.

<sup>2</sup>[https://www.gracia.ai/](https://www.gracia.ai/)

<!-- page 5 of 6 -->

[4] P. Wang, L. Liu, Y. Liu, C. Theobalt, T. Komura, and W. Wang, “Neus: Learning neural implicit surfaces by volume rendering for multi-view reconstruction,” arXiv preprint arXiv:2106.10689, 2021.

[5] B. Kerbl, G. Kopanas, T. Leimkuhler, and G. Drettakis, “3d gaussian ¨ splatting for real-time radiance field rendering.” ACM Trans. Graph., vol. 42, no. 4, pp. 139–1, 2023.

[6] A. Moreau, J. Song, H. Dhamo, R. Shaw, Y. Zhou, and E. Perez-Pellitero, ´ “Human gaussian splatting: Real-time rendering of animatable avatars,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 788–798.

[7] H. Pang, H. Zhu, A. Kortylewski, C. Theobalt, and M. Habermann, “Ash: Animatable gaussian splats for efficient and photoreal human rendering,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 1165–1175.

[8] Y. Yuan, X. Li, Y. Huang, S. De Mello, K. Nagano, J. Kautz, and U. Iqbal, “Gavatar: Animatable 3d gaussian avatars with implicit mesh learning,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 896–905.

[9] L. Hu, H. Zhang, Y. Zhang, B. Zhou, B. Liu, S. Zhang, and L. Nie, “Gaussianavatar: Towards realistic human avatar modeling from a single video via animatable 3d gaussians,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024.

[10] H. Dhamo, Y. Nie, A. Moreau, J. Song, R. Shaw, Y. Zhou, and E. Perez- ´ Pellitero, “Headgas: Real-time animatable head avatars via 3d gaussian splatting,” arXiv preprint arXiv:2312.02902, 2023.

[11] Z. Yang, H. Yang, Z. Pan, and L. Zhang, “Real-time photorealistic dynamic scene representation and rendering with 4d gaussian splatting,” arXiv preprint arXiv:2310.10642, 2023.

[12] Y. Jiang, Z. Shen, Y. Hong, C. Guo, Y. Wu, Y. Zhang, J. Yu, and L. Xu, “Robust dual gaussian splatting for immersive human-centric volumetric videos,” arXiv preprint arXiv:2409.08353, 2024.

[13] Y. Jiang, C. Yu, T. Xie, X. Li, Y. Feng, H. Wang, M. Li, H. Lau, F. Gao, Y. Yang et al., “Vr-gs: a physical dynamics-aware interactive gaussian splatting system in virtual reality,” in ACM SIGGRAPH 2024 Conference Papers, 2024, pp. 1–1.

[14] S. Saito, G. Schwartz, T. Simon, J. Li, and G. Nam, “Relightable gaussian codec avatars,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 130–141.

[15] J. Wen, X. Zhao, Z. Ren, A. G. Schwing, and S. Wang, “Gomavatar: Efficient animatable human modeling from monocular video using gaussians-on-mesh,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 2059–2069.

[16] X. Chu and T. Harada, “Generalizable and animatable gaussian head avatar,” arXiv preprint arXiv:2410.07971, 2024.

[17] M. Li, J. Tao, Z. Yang, and Y. Yang, “Human101: Training 100+ fps human gaussians in 100s from 1 view,” arXiv preprint arXiv:2312.15258, 2023.

[18] Z. Qian, S. Wang, M. Mihajlovic, A. Geiger, and S. Tang, “3dgsavatar: Animatable avatars via deformable 3d gaussian splatting,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 5020–5030.

[19] J. Xiang, X. Gao, Y. Guo, and J. Zhang, “Flashavatar: High-fidelity head avatar with efficient gaussian embedding,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 1802–1812.

[20] Y. Chen, L. Wang, Q. Li, H. Xiao, S. Zhang, H. Yao, and Y. Liu, “Monogaussianavatar: Monocular gaussian point-based head avatar,” in ACM SIGGRAPH 2024 Conference Papers, 2024, pp. 1–9.

[21] S. Hong, J. He, X. Zheng, C. Zheng, and S. Shen, “Liv-gaussmap: Lidar-inertial-visual fusion for real-time 3d radiance field map rendering,” IEEE Robotics and Automation Letters, 2024.

[22] J. Lin, Z. Li, X. Tang, J. Liu, S. Liu, J. Liu, Y. Lu, X. Wu, S. Xu, Y. Yan et al., “Vastgaussian: Vast 3d gaussians for large scene reconstruction,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 5166–5175.

[23] J. Bai, L. Huang, J. Guo, W. Gong, Y. Li, and Y. Guo, “360-gs: Layoutguided panoramic gaussian splatting for indoor roaming,” arXiv preprint arXiv:2402.00763, 2024.

[24] L. Radl, M. Steiner, M. Parger, A. Weinrauch, B. Kerbl, and M. Steinberger, “Stopthepop: Sorted gaussian splatting for view-consistent realtime rendering,” ACM Transactions on Graphics (TOG), vol. 43, no. 4, pp. 1–17, 2024.

[25] B. Lee, H. Lee, X. Sun, U. Ali, and E. Park, “Deblurring 3d gaussian splatting,” arXiv preprint arXiv:2401.00834, 2024.

[26] J. Lee, S. Lee, J. Lee, J. Park, and J. Sim, “Gscore: Efficient radiance field rendering via architectural support for 3d gaussian splatting,” in Proceedings of the 29th ACM International Conference on Architectural Support for Programming Languages and Operating Systems, Volume 3, 2024, pp. 497–511.

[27] Z. Yu, A. Chen, B. Huang, T. Sattler, and A. Geiger, “Mip-splatting: Aliasfree 3d gaussian splatting,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 19 447–19 456.

[28] T. Lu, M. Yu, L. Xu, Y. Xiangli, L. Wang, D. Lin, and B. Dai, “Scaffold-gs: Structured 3d gaussians for view-adaptive rendering,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 20 654–20 664.

[29] Y. Liu, H. Guan, C. Luo, L. Fan, J. Peng, and Z. Zhang, “Citygaussian: Real-time high-quality large-scale scene rendering with gaussians,” arXiv preprint arXiv:2404.01133, 2024.

[30] Y. Duan, F. Wei, Q. Dai, Y. He, W. Chen, and B. Chen, “4d gaussian splatting: Towards efficient novel view synthesis for dynamic scenes,” arXiv preprint arXiv:2402.03307, 2024.

[31] Z. Yang, X. Gao, W. Zhou, S. Jiao, Y. Zhang, and X. Jin, “Deformable 3d gaussians for high-fidelity monocular dynamic scene reconstruction,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 20 331–20 341.

[32] K. Katsumata, D. M. Vo, and H. Nakayama, “An efficient 3d gaussian representation for monocular/multi-view dynamic scenes,” arXiv preprint arXiv:2311.12897, 2023.

[33] Q. Liu, Y. Liu, J. Wang, X. Lv, P. Wang, W. Wang, and J. Hou, “Modgs: Dynamic gaussian splatting from causually-captured monocular videos,” arXiv preprint arXiv:2406.00434, 2024.

[34] Z. Lu, X. Guo, L. Hui, T. Chen, M. Yang, X. Tang, F. Zhu, and Y. Dai, “3d geometry-aware deformable gaussian splatting for dynamic view synthesis,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 8900–8910.

[35] R. Zhu, Y. Liang, H. Chang, J. Deng, J. Lu, W. Yang, T. Zhang, and Y. Zhang, “Motiongs: Exploring explicit motion guidance for deformable 3d gaussian splatting,” arXiv preprint arXiv:2410.07707, 2024.

[36] J. Luiten, G. Kopanas, B. Leibe, and D. Ramanan, “Dynamic 3d gaussians: Tracking by persistent dynamic view synthesis,” arXiv preprint arXiv:2308.09713, 2023.

[37] J. Bae, S. Kim, Y. Yun, H. Lee, G. Bang, and Y. Uh, “Per-gaussian embedding-based deformation for deformable 3d gaussian splatting,” arXiv preprint arXiv:2404.03613, 2024.

[38] Y. Lin, Z. Dai, S. Zhu, and Y. Yao, “Gaussian-flow: 4d reconstruction with dynamic 3d gaussian particle,” in Proceedings of the IEEE/CVF CVPR, 2024, pp. 21 136–21 145.

[39] Z. Li, Z. Chen, Z. Li, and Y. Xu, “Spacetime gaussian feature splatting for real-time dynamic view synthesis,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024.

[40] A. Kratimenos, J. Lei, and K. Daniilidis, “Dynmf: Neural motion factorization for real-time dynamic view synthesis with 3d gaussian splatting,” arXiv preprint arXiv:2312.00112, 2023.

[41] Y.-H. Huang, Y.-T. Sun, Z. Yang, X. Lyu, Y.-P. Cao, and X. Qi, “Scgs: Sparse-controlled gaussian splatting for editable dynamic scenes,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 4220–4230.

[42] J. Tang, Z. Chen, X. Chen, T. Wang, G. Zeng, and Z. Liu, “Lgm: Large multi-view gaussian model for high-resolution 3d content creation,” in European Conference on Computer Vision. Springer, 2025, pp. 1–18.

[43] X. He, J. Chen, S. Peng, D. Huang, Y. Li, X. Huang, C. Yuan, W. Ouyang, and T. He, “Gvgen: Text-to-3d generation with volumetric representation,” arXiv preprint arXiv:2403.12957, 2024.

[44] Y. Liang, X. Yang, J. Lin, H. Li, X. Xu, and Y. Chen, “Luciddreamer: Towards high-fidelity text-to-3d generation via interval score matching,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 6517–6526.

[45] X. E. Wang and Z. Sin, “3d gaussian model for animation and texturing,” arXiv preprint arXiv:2402.19441, 2024.

[46] M. Qin, W. Li, J. Zhou, H. Wang, and H. Pfister, “Langsplat: 3d language gaussian splatting,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 20 051–20 060.

[47] H. Li, H. Shi, W. Zhang, W. Wu, Y. Liao, L. Wang, L.-h. Lee, and P. Zhou, “Dreamscene: 3d gaussian-based text-to-3d scene generation via formation pattern sampling,” arXiv preprint arXiv:2404.03575, 2024.

[48] S. Zhou, Z. Fan, D. Xu, H. Chang, P. Chari, T. Bharadwaj, S. You, Z. Wang, and A. Kadambi, “Dreamscene360: Unconstrained text-to-

<!-- page 6 of 6 -->

3d scene generation with panoramic gaussian splatting,” in European Conference on Computer Vision. Springer, 2025, pp. 324–342.

[49] H. Ouyang, K. Heal, S. Lombardi, and T. Sun, “Text2immersion: Generative immersive scene with 3d gaussians,” arXiv preprint arXiv:2312.09242, 2023.

[50] J. Shriram, A. Trevithick, L. Liu, and R. Ramamoorthi, “Realmdreamer: Text-driven 3d scene generation with inpainting and depth diffusion,” arXiv preprint arXiv:2404.07199, 2024.

[51] X. Zhou, X. Ran, Y. Xiong, J. He, Z. Lin, Y. Wang, D. Sun, and M.- H. Yang, “Gala3d: Towards text-to-3d complex scene generation via layout-guided generative gaussian splatting,” arXiv preprint:2402.07207.

[52] Y. Jiang, Z. Shen, P. Wang, Z. Su, Y. Hong, Y. Zhang, J. Yu, and L. Xu, “Hifi4g: High-fidelity human performance rendering via compact gaussian splatting,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 19 734–19 745.

[53] Z. Peng, T. Shao, Y. Liu, J. Zhou, Y. Yang, J. Wang, and K. Zhou, “Rtg-slam: Real-time 3d reconstruction at scale using gaussian splatting,” in ACM SIGGRAPH 2024 Conference Papers, 2024, pp. 1–11.

[54] J. Sun, H. Jiao, G. Li, Z. Zhang, L. Zhao, and W. Xing, “3dgstream: Onthe-fly training of 3d gaussians for efficient streaming of photo-realistic free-viewpoint videos,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 20 675–20 685.

[55] Z. Zhou, F. Ma, H. Fan, and Y. Yang, “Headstudio: Text to animatable head avatars with 3d gaussian splatting,” arXiv preprint:2402.06149.

[56] S. Niedermayr, J. Stumpfegger, and R. Westermann, “Compressed 3d gaussian splatting for accelerated novel view synthesis,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 10 349–10 358.

[57] S. Qian, T. Kirschstein, L. Schoneveld, D. Davoli, S. Giebenhain, and M. Nießner, “Gaussianavatars: Photorealistic head avatars with rigged 3d gaussians,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024.

[58] Z. Yang, X. Gao, Y. Sun, Y. Huang, X. Lyu, W. Zhou, S. Jiao, X. Qi, and X. Jin, “Spec-gaussian: Anisotropic view-dependent appearance for 3d gaussian splatting,” arXiv preprint arXiv:2402.15870, 2024.

[59] Z. Liang, Q. Zhang, Y. Feng, Y. Shan, and K. Jia, “Gs-ir: 3d gaussian splatting for inverse rendering,” in Proceedings of the IEEE/CVF CVPR, 2024, pp. 21 644–21 653.

[60] K. Liu, F. Zhan, M. Xu, C. Theobalt, L. Shao, and S. Lu, “Stylegaussian: Instant 3d style transfer with gaussian splatting,” arXiv preprint arXiv:2403.07807, 2024.

[61] A. Saroha, M. Gladkova, C. Curreli, T. Yenamandra, and D. Cremers, “Gaussian splatting in style,” arXiv preprint arXiv:2403.08498, 2024.

[62] J. Li, L. Cheng, Z. Wang, T. Mu, and J. He, “Loopgaussian: Creating 3d cinemagraph with multi-view images via eulerian motion field,” arXiv preprint arXiv:2404.08966, 2024.

[63] H. Yu, J. Julin, Z. A. Milacski, K. Niinuma, and L. A. Jeni, “Cogs: ´ Controllable gaussian splatting,” in Proceedings of the IEEE/CVF CVPR, 2024, pp. 21 624–21 633.

[64] Y. Wang, X. Yi, Z. Wu, N. Zhao, L. Chen, and H. Zhang, “Viewconsistent 3d editing with gaussian splatting,” in European Conference on Computer Vision. Springer, 2025, pp. 404–420.

[65] V. Jaganathan, H. H. Huang, M. Z. Irshad, V. Jampani, A. Raj, and Z. Kira, “Ice-g: Image conditional editing of 3d gaussian splats,” arXiv preprint arXiv:2406.08488, 2024.

[66] Y. Chen, Z. Chen, C. Zhang, F. Wang, X. Yang, Y. Wang, Z. Cai, L. Yang, H. Liu, and G. Lin, “Gaussianeditor: Swift and controllable 3d editing with gaussian splatting,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 21 476–21 485.

[67] J. Wang, J. Fang, X. Zhang, L. Xie, and Q. Tian, “Gaussianeditor: Editing 3d gaussians delicately with text instructions,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 20 902–20 911.

[68] A. Rivero, S. Athar, Z. Shu, and D. Samaras, “Rig3dgs: Creating controllable portraits from casual monocular videos,” arXiv preprint arXiv:2402.03723, 2024.

[69] Z. Fan, K. Wang, K. Wen, Z. Zhu, D. Xu, and Z. Wang, “Lightgaussian: Unbounded 3d gaussian compression with 15x reduction and 200+ fps,” arXiv preprint arXiv:2311.17245, 2023.

[70] R. Abdal, W. Yifan, Z. Shi, Y. Xu, R. Po, Z. Kuang, Q. Chen, D.-Y. Yeung, and G. Wetzstein, “Gaussian shell maps for efficient 3d human generation,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 9441–9451.

[71] K. Navaneet, K. P. Meibodi, S. A. Koohpayegani, and H. Pirsiavash, “Compgs: Smaller and faster gaussian splatting with vector quantization,” in European Conference on Computer Vision, 2024.

[72] M. Yu, T. Lu, L. Xu, L. Jiang, Y. Xiangli, and B. Dai, “Gsdf: 3dgs meets sdf for improved rendering and reconstruction,” arXiv preprint arXiv:2403.16964, 2024.

[73] Y. Ji, Y. Liu, G. Xie, B. Ma, and Z. Xie, “Neds-slam: A novel neural explicit dense semantic slam framework using 3d gaussian splatting,” arXiv preprint arXiv:2403.11679, 2024.

[74] S. Sun, M. Mielle, A. J. Lilienthal, and M. Magnusson, “High-fidelity slam using gaussian splatting with rendering-guided densification and regularized optimization,” arXiv preprint arXiv:2403.12535, 2024.

[75] J. Hu, X. Chen, B. Feng, G. Li, L. Yang, H. Bao, G. Zhang, and Z. Cui, “Cg-slam: Efficient dense rgb-d slam in a consistent uncertainty-aware 3d gaussian field,” arXiv preprint arXiv:2403.16095, 2024.

[76] L. C. Sun, N. P. Bhatt, J. C. Liu, Z. Fan, Z. Wang, T. E. Humphreys, and U. Topcu, “Mm3dgs slam: Multi-modal 3d gaussian splatting for slam using vision, depth, and inertial measurements,” arXiv preprint arXiv:2404.00923, 2024.

[77] C. Yan, D. Qu, D. Xu, B. Zhao, Z. Wang, D. Wang, and X. Li, “Gs-slam: Dense visual slam with 3d gaussian splatting,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 19 595–19 604.

[78] N. Keetha, J. Karhade, K. M. Jatavallabhula, G. Yang, S. Scherer, D. Ramanan, and J. Luiten, “Splatam: Splat track & map 3d gaussians for dense rgb-d slam,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 21 357–21 366.

[79] C. Pokhariya and N. Ishaan, “Manus: Markerless hand-object grasp capture using articulated 3d gaussians,” in IEEE/CVF CVPR, 2024.

[80] D. Cai, J. Heikkila, and E. Rahtu, “Gs-pose: Cascaded framework ¨ for generalizable segmentation-based 6d object pose estimation,” arXiv preprint arXiv:2403.10683, 2024.

[81] H. Li, Y. Gao, D. Zhang, C. Wu, Y. Dai, C. Zhao, H. Feng, E. Ding, J. Wang, and J. Han, “Ggrt: Towards generalizable 3d gaussians without pose priors in real-time,” arXiv preprint arXiv:2403.10147, 2024.

[82] Y. Liu, C. Li, C. Yang, and Y. Yuan, “Endogaussian: Gaussian splatting for deformable surgical scene reconstruction,” arXiv preprint arXiv:2401.12561, 2024.

[83] S. Bonilla, S. Zhang, D. Psychogyios, D. Stoyanov, F. Vasconcelos, and S. Bano, “Gaussian pancakes: Geometrically-regularized 3d gaussian splatting for realistic endoscopic reconstruction,” in MICCAI, 2024.

[84] S. Niedermayr, C. Neuhauser, K. Petkov, K. Engel, and R. Westermann, “Application of 3d gaussian splatting for cinematic anatomy on consumer class devices,” 2024.

[85] M. Macklin, M. Muller, and N. Chentanez, “Xpbd: position-based ¨ simulation of compliant constrained dynamics,” in Proceedings of the 9th International Conference on Motion in Games, 2016, pp. 49–54.

[86] M. Loper, N. Mahmood, J. Romero, G. Pons-Moll, and M. J. Black, “Smpl: A skinned multi-person linear model,” in Seminal Graphics Papers: Pushing the Boundaries, Volume 2, 2023, pp. 851–866.

[87] S. Bai and J. Li, “Progress and prospects in 3d generative ai: A technical overview including 3d human,” arXiv preprint arXiv:2401.02620, 2024.

[88] G. Chen and W. Wang, “A survey on 3d gaussian splatting,” arXiv preprint arXiv:2401.03890, 2024.

[89] B. Fei, J. Xu, R. Zhang, Q. Zhou, W. Yang, and Y. He, “3d gaussian splatting as new era: A survey,” IEEE Transactions on Visualization and Computer Graphics, p. 1–20, 2024.

[90] F. Tosi, Y. Zhang, Z. Gong, E. Sandstrom, S. Mattoccia, M. R. Oswald, ¨ and M. Poggi, “How nerfs and 3d gaussian splatting are reshaping slam: a survey,” arXiv preprint arXiv:2402.13255, vol. 4, 2024.

[91] T. Wu, Y.-J. Yuan, L.-X. Zhang, J. Yang, Y.-P. Cao, L.-Q. Yan, and L. Gao, “Recent advances in 3d gaussian splatting,” Computational Visual Media, vol. 10, no. 4, pp. 613–642, 2024.

[92] A. Dalal, D. Hagen, K. G. Robbersmyr, and K. M. Knausgard, “Gaussian ˚ splatting: 3d reconstruction and novel view synthesis: A review,” IEEE Access, vol. 12, p. 96797–96820, 2024.

[93] R. Cui, S. Qiu, S. Anwar, J. Zhang, and N. Barnes, “Energy-based residual latent transport for unsupervised point cloud completion,” BMVC, 2022.

[94] R. Zhu, D. Kang, K.-H. Hui, Y. Qian, S. Qiu, Z. Dong, L. Bao, P.-A. Heng, and C.-W. Fu, “Ssp: Semi-signed prioritized neural fitting for surface reconstruction from unoriented point clouds,” in WACV, 2024, pp. 3769–3778.

[95] Y. Cao, M. Hadi, L. Pan, and Z. Liu, “Gs-vton: Controllable 3d virtual try-on with gaussian splatting,” arXiv preprint arXiv:2410.05259, 2024.