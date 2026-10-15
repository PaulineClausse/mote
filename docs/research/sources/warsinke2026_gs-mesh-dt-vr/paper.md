<!-- page 1 of 7 -->

arXiv:2608.01969v1 [cs.HC] 3 Aug 2026

© 2026 IEEE. This is the author’s version of the article that was accepted to the Hype-XR workshop and will be published in the proceedings of IEEE ISMAR 2026 conference (adjunct). The DOI of the final version will be added upon publication.

# 3D Gaussian Splatting and Mesh-Based Digital Twins: An Exploratory Study for Virtual Reality Tourism

Maximilian Warsinke Quality and Usability Lab, Technische Universitat Berlin, ¨ Berlin, Germany Tanja Kojić§ Quality and Usability Lab, Technische Universitat Berlin, ¨ Berlin, Germany

Francesco Vona† Immersive Reality Lab, Hochschule Hamm-Lippstadt, Lippstadt, Germany Jan-Niklas Voigt-Antons¶ Immersive Reality Lab, Hochschule Hamm-Lippstadt, Lippstadt, Germany

Abm Tariqul Islam ‡ DigitalTwin Technology GmbH, Koln, Germany ¨

Sebastian Moller ¨ || Quality and Usability Lab, Technische Universitat Berlin, ¨ DFKI, Berlin, Germany

![Image block](images/warsinke2026_gs-mesh-dt-vr_p1_b8.png)

Figure 1: Screenshots of the Mesh version (left) and the 3DGS version (right) of the application.

## ABSTRACT

Digital Twins (DTs) are increasingly used for immersive experiences in virtual tourism. Virtual Reality (VR) enables remote visits to replicated locations for promotional purposes or access to fragile and rural cultural heritage sites. However, developing high-fidelity DTs of tourist destinations is costly, due to the manual creation of 3D environments. Novel 3D rendering techniques, such as 3D Gaussian splatting (3DGS), pose a promising approach to creating immersive experiences. This study investigates the user experience (UX) of a 3D-mesh-based scene and a 3DGS-based scene within a VR tourism application. In a laboratory study, 20 participants engaged with both versions and rated UX, cybersickness, presence and affect through standardized questionnaires. A custom questionnaire was created to measure the perception of the DTs. The collected data suggests that both versions were enjoyed and induced positive affect, with the Mesh version receiving good UX ratings. While the 3DGS version scored higher in terms of experienced realism, it showed clear weaknesses in pragmatic quality. Further, the results suggest that the feeling of presence could be enhanced and cybersickness reduced in both versions. Overall, the study contributes to the understanding of UX in VR tourism applications by implementing mesh-based and 3DGS-based DTs and raising important questions about the perception of realism.

**Index Terms:** Virtual Reality, 3D Gaussian Splatting, Realism,

Digital Twin, Virtual Tourism, User Experience

## 1 INTRODUCTION

The increased interest in using immersive technology in the tourism and cultural heritage sectors can be summarized as virtual tourism [20, 27]. It encompasses enriching on-site experiences with augmented reality (AR) technology and remote exploration through virtual reality (VR) [15, 2]. The main aspect of VR is its immersive capability, which gives users the sensation of “being there”, leading to a positive evaluation of the destination [29]. VR tourism can be used either for promotional purposes to foster travel intentions or to replace a physical visit entirely [34]. For example, it can be used to visit fragile or rural historical sites or as an inclusive, barrier-free opportunity [21, 24].

The digitally replicated cities, buildings, and sites are more frequently referred to as digital twins (DTs). While the vision behind DTs is the synchronization of physical and digital entities through a continuous, bidirectional data stream [11], current implementations in VR tourism are often static or unidirectional [5]. A convergence of VR and DTs is observable due to the synergy between the immersive VR interaction and the practical functionalities of DT technology [25, 7, 16].

DTs in immersive experiences require high-fidelity visualizations to provide users with an authentic experience [27]. Therefore, a substantial bottleneck is the visual reconstruction of tourist places and cultural heritage sites, which is currently predominantly achieved through a combination of laser scanning and photogrammetry [17]. For real-time VR applications, these captures require manual post-processing to clean up the 3D models, which increases costs and development time.

However, novel reconstruction methods, such as 3D Gaussian splatting (3DGS), could be promising for fast and scalable immersive experiences [9, 33, 34]. These approaches allow for highfidelity 3D content generation from a set of 2D images. On a technical level, these visualization approaches differ fundamentally from

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>\*</sup>e-mail: warsinke@tu-berlin.de †e-mail: Francesco.Vona@hshl.de ‡e-mail: tariqul.islam@digitaltwin.technology §e-mail: tanja.kojic@tu-berlin.de ¶e-mail: jan-niklas.voigt-antons@hshl.de ||e-mail: sebastian.moeller@tu-berlin.de</span></small>

1

<!-- page 2 of 7 -->

© 2026 IEEE. This is the author’s version of the article that was accepted to the Hype-XR workshop and will be published in the proceedings of IEEE ISMAR 2026 conference (adjunct). The DOI of the final version will be added upon publication.

polygonal representations, such as traditional 3D-meshes [13]. This raises the question of how 3DGS are perceived by users and how they shape the user experience (UX) [34]. Important areas for investigation include cybersickness, realism perception, and sense of presence [12].

To investigate these dynamics, we developed and evaluated a VR tourism application in a two-part usability study. The application was designed as a demonstrator for remote pre-visit exploration and included two DTs of real locations: Etteln in Germany and Vilanova i la Geltru in Spain. Both locations were captured using ´ drone imagery but were presented through different reconstruction approaches. Etteln was implemented as a polygonal mesh-based environment, while Vilanova i la Geltru was reconstructed using ´ 3DGS. Participants explored both versions in VR and rated their experiences using standardized questionnaires covering affect, cybersickness, presence, and UX, complemented by a custom questionnaire assessing perceived DT qualities. By gathering user data from the two versions with a focus on ecological validity, the study contributes to the understanding of UX dimensions in VR tourism and gathers preliminary data on the perception of 3DGS.

## 2 RELATED WORK

## 2.1 Virtual Reality Tourism

While interest in virtual tourism is rising, the idea of using VR and AR technology in tourism contexts has been around for decades. Loureiro et al. provide a comprehensive overview of the usage of VR and AR technology in tourism research that dates back to 1995 [15]. They discuss the application of VR in planning, managing, promoting, educating, and creating or transforming tourist experiences. In a more recent review, Rifqi observes an increase in VR tourism studies in 2018, which steadily grew and peaked in 2024 [20]. He suggests that this may have been driven by the pandemic, the emergence of AI, and the metaverse. Tromp et al. review 10 use case studies in the intersection of XR and cultural heritage for similar purposes (e.g., pre-visit planning, on-site exploration) [27]. They identified six key topics as positive effects while also discussing their challenges: enhanced engagement, broader accessibility, economic benefits for local communities, preservation and promotion, educational impact, and sustainability. In the broader context of the metaverse, Baker et al. investigated UX factors for virtual heritage tourism [2]. They identified five positive factors, such as presence and authenticity, and eight negative factors, among others: convenience, comfort, and resolution. Additionally, they identified three major dilemmas: the higher costs of more sophisticated hardware and content, the risk of cybersickness from more immersive experiences, and the greater engagement and complexity of gamification. There is empirical evidence on the benefits of using VR to foster travel intentions. In a two-part study with over 900 participants, Tussyadiah et al. found that feeling present in VR and enjoyment both lead to a positive attitude change, which, in turn, increases the intention to travel [29]. Anwar et al. conducted a user study comparing a VR condition to 2D on a smartphone [1]. Participants experienced a gamified replication of the UNESCO World Heritage site Jabal Al-Ahmar. The results indicate that the VR version outperformed the smartphone version in UX and presence metrics, underlining the benefits of immersive experiences. The pre-sented studies show the viability digital experience in the tourism domain.

## 2.2 Digital Twins

The concept of a DT originated in product lifecycle management and has been applied to almost all disciplines and industries [35]. While there are many definitions, a DT is generally a digital replica of a physical object, place, or system that is synchronized via bidirectional data flow. Kritzinger et al. proposed a classification of DTs with different levels of integration: a digital model (DM) for

the absence of data flow, a digital shadow (DS) for unidirectional data flow, and a digital twin (DT) for bidirectional data flow [11]. In a recent review of DT definitions, Wuni et al. rejected this classification and proposed that bidirectional data flow should be a strict requirement, fostering a consistent and cohesive definition [35]. Despite this critique, this study adopts the DT term as an umbrella concept to facilitate discussion of different levels of digitalphysical integration within a unified framework. According to Tang et al., the convergence of DTs and the metaverse is evident and is driven by AI and extended reality (XR) [25]. This would allow for persistent virtual worlds, enhanced by Internet of Things (IoT) data and perceivable through VR headsets. Girginova describes a co-evolution in which DTs could provide the usefulness that popular XR technologies often lack [7], and Pandey et al. focus on use cases in the convergence of DT and XR [16]. The authors identified manufacturing, healthcare, education, urban planning, and entertainment as the areas that would benefit most from the symbiosis of DTs and XR. Almeida et al. focus on the literature on DTs in the tourism industry and also discuss XR use cases [5]. They observe the trend that the current DT integration level in virtual tourism is mainly static or unidirectional. A prime example was presented in a study by Pekridou et al., who built an XR DT application with the highest level of integration (bidirectional data flow) [18]. Participants could interact with energy, temperature, and $CO_{2}$ metrics in real time, enabling human-in-the-loop control. Subjective user data indicated an excellent UX, underlining high engagement, acceptance, and usability. In summary, XR has the potential to serve as an interface to interact with DTs.

## 2.3 3D Representations

There are different ways to visualize 3D content in a virtual scene, with polygonal 3D models being the most widespread. In the broader context of 3D representations, 3D-meshes are categorized as explicit representations, along with voxels and point clouds [14]. Another type of representation is the implicit representation, such as neural radiance fields (NeRF). Explicit representations have clearly defined geometry, while implicit representations utilize mathematical functions to describe their properties [13]. 3DGS combines those properties, working similarly to NeRFs but with explicit 3D scene representations [9]. In cultural heritage, authentic 3D reconstructions are achieved through a combination of photogrammetry and laser scanning [3]. While these approaches produce high-fidelity meshes, they are too complex for real-time applications and require extensive post-processing, such as retopology and texture mapping. This approach was also used by Pavelkajr et al., who first captured the Old Town Bridge Tower in Prague and then optimized the mesh for use in VR and AR [17]. Using normal maps, depth perception can be mimicked while reducing the number of polygons. Using 3DGS for 3D representation is expected to become increasingly widespread [32]. Li et al. reviewed the literature on the usage of radiance fields (NeRF and 3DGS) within the field of XR [12]. They discuss opportunities and challenges across topics such as content generation and optimization, and advocate conducting in-depth research on user-centric benchmarks for quality perception, presence, and cybersickness. Wang et al. compared 3DGS to traditional 3D modeling and 360-degree panoramic imagery in a user study in the context of virtual tourism [34]. Their findings reveal that 3DGS outperformed the other conditions across all dimensions, including realism, emotional arousal, immersion, information credibility, cognitive appraisal, and travel intention. Vachha et al. developed Dreamcrafter, a tool for the ad hoc generation and editing of 3D radiance field representations in VR [30]. The application was evaluated in a user study in which participants generated and edited mostly 3DGS using voice input and a user interface. Tu et al. identified three key challenges of 3DGS in VR: artifacts, distortions, and reduced frame rates [28]. They tackled

2

<!-- page 3 of 7 -->

© 2026 IEEE. This is the author’s version of the article that was accepted to the Hype-XR workshop and will be published in the proceedings of IEEE ISMAR 2026 conference (adjunct). The DOI of the final version will be added upon publication.

those topics with their VRSplat solution, which they validated in a user study. To conclude, novel 3D representation methods are being evaluated with users and have already been applied in the field of virtual tourism.

## 2.4 Research Gap

The reviewed literature points to a growing convergence of DTs and XR technologies using novel 3D rendering techniques. This is highly relevant for VR tourism: DTs can extend immersive experiences through contextual and potentially real-time information, while emerging 3D reconstruction methods, such as 3DGS, offer a fast, scalable way to generate visually rich 3D environments. While there is ongoing research in the virtual tourism area with meshbased approaches, 3DGS representations are still largely underexplored. As a result, it remains unclear what implications 3DGS-based DTs can have on UX and perception in real-world use cases.

## 3 METHODOLOGY

## 3.1 Study Design

The study tested the two versions of the application in a withinsubjects design with repeated measurements. The order of the versions was varied using an AB/BA design to minimize order effects. The study was approved by the ethics committee of [removed for double-blind review]. The study was conducted in a controlled laboratory environment at [removed for double-blind]. The experiment took around 30 minutes, and participants received [removed for double-blind] in compensation.

## 3.2 Application

The application ran on an external PC tethered to a Meta Quest 3 headset via a Meta Link Cable. The PC specifications were an NVIDIA GeForce GTX 1080, an Intel(R) Core(TM) i7-7700K CPU @ 4.20GHz, and 16 GB RAM. Participants interacted with the virtual environments using the standard Meta Quest 3 controllers. The application was developed as part of the [removed for doubleblind review] project using Unity 6. User locomotion was implemented using the Unity XR Interaction Toolkit. Two locomotion modes were enabled: continuous movement and teleportation. Continuous movement allows the user to navigate the environment using the joystick on the left controller, while teleportation is controlled via the right controller joystick and repositions the user to a target location by pointing in the environment. To reduce potential motion sickness, a screen fade (“blink”) effect is applied during teleportation transitions. Over an interface, users could teleport directly to different points of interest (POIs). In the main menu, two unique versions of the application could be selected.

## 3.2.1 3D Gaussian Splatting Version

The 3DGS version consists of a DT of Vilanova i la Geltru, gener- ´ ated using novel 3D reconstruction techniques and rendered using a 3DGS representation (see Fig. 1). Visual data were collected using drone-based image acquisition. Camera poses and sparse scene geometry were first estimated using Structure-from-Motion (SfM), after which the scene was optimized into a representation composed of 3D Gaussian primitives. This representation approximates the radiance and geometry of the environment, enabling efficient realtime rendering of the reconstructed scene. In this version, the environment consists of several isolated POIs, such as the Church of Sant Antoni and Plaça dels Lledoners. Each scene is reconstructed and rendered independently, rather than integrated into a single spatially continuous urban model. Consequently, users are not able to freely traverse the city environment. Instead, navigation between POIs is performed via an interactive menu provided within the application interface. The DT of Vilanova i la Geltru can be classified ´ as a digital model in terms of integration.

Table 1: Metrics and questions of the DT questionnaire.

| Metric | Question |
| --- | --- |
| Enjoyment | "How much did you enjoy the experi-ence?" |
| Understanding | "The application has helped me better understand a place or a system." |
| Information | "The application provides information that would otherwise be difficult or im-possible to access." |
| Reliability | "The application reliably reflects the current status of a place or system." |
| Simulation | "The application allows me to simulate processes or scenarios." |
| Comments | "Additional comments (optional)." |

## 3.2.2 3D Mesh Version

The Mesh version consists of a DT of Etteln, generated through a drone imagery-based mesh generation pipeline combined with neural radiance field-based reconstruction techniques (see Fig. 1). High-overlap multi-view drone images were first used to optimize a NeRF model for each selected POI. An explicit surface mesh was subsequently extracted from the learned density field using isosurface extraction (e.g., Marching Cubes) and further optimized to produce a high-fidelity mesh representation suitable for realtime rendering. Key landmarks were further refined through post-processing steps, including tools such as 3ds Max. These enhancements included geometry corrections, higher levels of detail, and improved texture quality to increase visual realism and semantic recognizability within the DT. In contrast to the 3DGS version, the mesh-based reconstruction produces a continuous, spatially coherent virtual environment. This enables users to freely explore the village in a natural way while still allowing teleportation between POIs if desired. All POIs are embedded within the unified spatial model. Additionally, selected POIs include information panels that display real-time data from IoT sensors in Etteln, such as the windmill’s charging power. The level of integration of the Etteln DT is therefore in the digital shadow category (unidirectional data flow).

## 3.3 Metrics

The demographic questionnaire was designed to collect basic information about participants, including gender, age, and profession. Additionally, their expertise was assessed using three questions targeting different relevant categories: experience with XR, experience with 3D modeling, and video game experience. The reason for including the expertise was the possibility of conducting correlation analysis with the dependent variables.

The Affinity for Technological Interaction (ATI) scale was used to assess participants’ general tech affinity [6]. The questionnaire includes questions regarding the willingness and motivation to engage with novel technical systems. Nine Likert scale answers must be provided in the range of 1 to 6. The average ATI score helps to estimate how tech-prone the sample group is, while individual scores can be used in a correlation analysis.

The Affective Slider [4] was employed to measure arousal and valence. The authors suggest using at least 100 steps to maintain slider continuity. Due to the questionnaire format, a 1 to 10 scale was used.

The short version of the User Experience Questionnaire was used to assess the pragmatic quality and hedonic quality of the experience [22]. Eight word pairs must be rated on a 1 to 7 scale. Pragmatic and hedonic quality scores both consist of four questions, averaged and converted to a −3 to 3 scale. From both sub-dimensions, an overall quality score is derived. The short version was chosen to reduce the length of the questionnaire and avoid overwhelming participants.

3

<!-- page 4 of 7 -->

© 2026 IEEE. This is the author’s version of the article that was accepted to the Hype-XR workshop and will be published in the proceedings of IEEE ISMAR 2026 conference (adjunct). The DOI of the final version will be added upon publication.

Cybersickness was measured using the Cybersickness in Virtual Reality Questionnaire (CSQ-VR) [10], which consists of the dimensions of nausea, oculomotor, and vestibular. Each symptom score is averaged from two questions, each answered on a 1 to 7 scale. Additionally, participants are given the opportunity to describe their symptoms in detail through qualitative answers. The individual scores are not averaged but summed, which results in a scale from 2 to 14 for the subdimensions and from 6 to 42 for the total cybersickness score.

The sense of being present in the virtual environment was measured using the Igroup Presence Questionnaire (IPQ) [19]. It is the most widely adopted questionnaire for this purpose in the literature [26] and encompasses four dimensions: general presence, spatial presence, involvement, and experienced realism. Questions are rated on a scale of 1 to 7 with varying anchors. Responses were later rescaled to match a -3 to 3 scale for benchmark comparisons.

A custom questionnaire was created to evaluate the perceived DT qualities, as no comparable instrument exists to our knowledge. To date, DT-focused applications are evaluated through common questionnaires from the field of Human-Computer Interaction. To gain more insight into the added value from DTs, four main properties were derived from the literature: The ability of the DT to help users understand a place or system, whether there was information that would otherwise be impossible to access, how up-to-date the DT seemed to participants, and finally, the ability of simulation. Additionally, overall enjoyment of the experience was added, along with the option to provide additional open-ended comments. The exact formulation used can be found in Tab. 1. A 1 to 7 scale was used with Likert scale anchors.

## 3.4 Procedure

Before starting the study, participants signed the informed consent form and received a brief explanation of the goals and the experiment’s structure. They were asked to fill in the demographics questionnaire and the ATI. Each participant was then assigned a starting location and began exploring either the Mesh version or the 3DGS version for a total duration of five minutes. During this exploration phase, they were free to navigate the environment and interact with the available elements. After completing the first session, participants removed the VR headset and were guided to the first round of questionnaires. Once the questionnaires were completed, the participants returned to the VR headset and repeated the same procedure at the second location. A final set of questionnaires was completed after exploring the second environment, concluding the study.

## 3.5 Participants

A total of 20 participants took part in the study (9 male, 11 female). The mean age of the sample was 33.8 years (SD = 11.31). Participants reported moderate prior experience with XR technologies of 4.05 out of 7 (SD = 1.57), a lower experience with 3D video gaming of 2.85 (SD = 2.32), and the lowest experience was reported with 3D modeling of 2.6 (SD = 1.41). The mean ATI score was 4.27 (SD = 0.88). All participants were recruited through the [removed for double-blind review] participant portal.

## 3.6 Data Analysis

The questionnaire responses were scored according to the scoring guidelines, which involved the reversal of several question items and the conversion from a 1 to 7 scale to a -3 to 3 scale for both UEQ-S and IPQ responses. Descriptive statistics were calculated using JASP [8]. The standardized questionnaire scores were treated as continuous variables, while the responses to the custom questions were treated as ordinal variables, as they rely on single Likert Scale responses. Therefore, both the median and the arithmetic mean are included in Tab. 2 and Tab. 3.

Table 2: Descriptive statistics for the 3DGS version.

| Metric | Median | Mean | SD |
| --- | --- | --- | --- |
| Valence | 7.00 | 5.95 | 2.63 |
| Arousal | 6.00 | 6.10 | 2.34 |
| Enjoyment | 5.00 | 4.40 | 1.88 |
| Understanding | 4.50 | 3.95 | 1.70 |
| Information | 2.50 | 3.15 | 2.01 |
| Reliability | 4.00 | 3.55 | 1.43 |
| Simulation | 4.50 | 4.30 | 1.69 |
| G. Presence | 0.50 | 0.50 | 1.61 |
| Exp. Realism | -0.63 | -0.71 | 1.06 |
| Involvement | 0.25 | 0.13 | 1.52 |
| Sp. Presence | 0.30 | 0.07 | 1.45 |
| Pragmatic Q. | 0.25 | 0.41 | 1.36 |
| Hedonic Q. | 0.88 | 0.61 | 1.58 |
| Cybersickness | 17.00 | 19.50 | 9.76 |

Table 3: Descriptive statistics for the Mesh version.

| Metric | Median | Mean | SD |
| --- | --- | --- | --- |
| Valence | 7.00 | 6.80 | 1.77 |
| Arousal | 7.00 | 7.10 | 1.48 |
| Enjoyment | 5.00 | 5.35 | 1.50 |
| Understanding | 5.00 | 5.05 | 1.43 |
| Information | 4.00 | 4.15 | 1.76 |
| Reliability | 4.50 | 4.30 | 1.38 |
| Simulation | 5.50 | 5.40 | 1.31 |
| G. Presence | 1.00 | 1.05 | 1.50 |
| Exp. Realism | -1.00 | -0.83 | 0.96 |
| Involvement | 0.38 | 0.51 | 1.21 |
| Sp. Presence | 0.60 | 0.66 | 1.05 |
| Pragmatic Q. | 1.88 | 1.70 | 0.90 |
| Hedonic Q. | 1.13 | 1.16 | 1.19 |
| Cybersickness | 16.00 | 17.80 | 8.92 |

The user factors assessed through the demographic questionnaire, specifically prior experience, age, and ATI, were tested against the dependent variables using a correlation analysis. A non-parametric approach was chosen because the prior experience measures were ordinal. Therefore, Spearman rank correlation tests were applied using Python and scipy.stats [31]. To account for Type I errors through multiple comparisons, Holm–Bonferroni corrections were applied to control the family-wise error rate using statsmodels.stats.multitest [23]. Each of the five user factors was treated as a separate family, containing the correlations between that score and the 14 dependent variables. For brevity, only remaining statistically significant correlations are reported in the results section. A significance threshold of α < 0.05 was used to determine statistical significance. No statistical tests were conducted to compare the two versions, as the study design did not isolate a single variable.

## 4 RESULTS

Presented are descriptive statistics of the questionnaire responses and the results of correlations between user factors and dependent variables within each version.

## 4.1 3DGS version

The following presents the mean scores of the dependent variables gathered through post-session questionnaires for the 3DGS version. The full descriptive statistics can be found in Tab. 2.

In terms of affect, participants reported a mean Valence score of 5.95 and a slightly higher average Arousal score of 6.10. The UEQ-

4

<!-- page 5 of 7 -->

© 2026 IEEE. This is the author’s version of the article that was accepted to the Hype-XR workshop and will be published in the proceedings of IEEE ISMAR 2026 conference (adjunct). The DOI of the final version will be added upon publication.

S scores show a mean Pragmatic Quality of 0.41, a higher Hedonic Quality score of 0.61, resulting in an average Overall score of 0.51 $( \mathrm { S D } = 1 . 3 1 )$ . The total IPQ score was $-0.\dot{3}9\ ( SD  = 0.97)$ . Participants reported a mean Cybersickness score of 19.50 as scored by the CSQ-VR. For the individual sub-dimensions, Vestibular symptoms were reported as the strongest, with a score of 6.75 (SD = 3.77), followed by Nausea with 6.65 (SD = 3.45) and Oculomotor with $6.10\left (  SD  = 3.71 \right )$ . The qualitative responses highlighted blurry and unclear visuals, flickering, and unnatural locomotion, leading to nausea and discomfort during the experience. The IPQ results showed the highest scores for General Presence at 0.50, followed by Involvement at 0.13 and Spatial Presence at 0.07. Experienced Realism received the lowest score at -0.71. The custom DT Questionnaire showed the best mean ratings in the category Enjoyment with 4.40, followed by Simulation with 4.30. Understanding received a score of 3.95, and Reliability scored 3.55. Lastly, Information received the lowest rating with 3.15.

In the 3DGS version, one significant correlation between user factors and outcome measures remained after applying the Holm–Bonferroni correction. Prior Experience with 3D modeling correlated with perceived Reliability $( r _ { s } = 0 . 6 8 , \; p < 0 . 0 0 1$ $p _ { \mathrm { H o l m } } = 0 . 0 1 2 )$

## 4.2 Mesh version

The following presents the average scores of the dependent variables for the Mesh version. Comprehensive descriptive statistics are presented in Tab. 3.

Participants reported a mean Valence score of 6.80 and a slightly higher average Arousal score of 7.10. The UEQ-S scores indicate a higher mean Pragmatic Quality of 1.70 compared to a Hedonic Quality score of 1.17. On average, this results in an Overall UEQ-S score of 1.43 (SD = 0.87). Participants reported a mean Cybersickness score of 17.80. The individual dimensions were rated as follows: Oculomotor was highest at 6.50 (SD = 3.09), followed by Nausea at 6.10 (SD = 3.78) and Vestibular at 5.20 (SD = 3.53). Qualitative responses attributed symptoms of motion sickness and dizziness primarily to fast movement, snap-view transitions, and navigating confined spaces, such as the windmill. Discomfort was also associated with moving in VR while remaining stationary in the real world, although some participants reported little to no symptoms. In terms of presence scores as assessed by the IPQ, General Presence scores highest with 1.05, followed by Spatial Presence with 0.66 and involvement with 0.51. The lowest score was given to Experienced Realism with an average score of -0.83. This resulted in a total IPQ score of -0.06 (SD = 0.70). Regarding DT Perception, Simulation received the highest score of 5.40, closely followed by Enjoyment with 5.35. Understanding was rated 5.05 on average, Reliability was rated 4.30, and lastly, Information Access was rated 4.15.

In the Mesh version, one significant correlation remained between user factors and outcome measures after applying the Holm-Bonferroni correction. Prior Experience with 3D modeling correlated with Experience Realism $(r_s = 0.65,   p = 0.002,   p_{ Holm } =$ 0.024).

## 5 DISCUSSION

Both arousal and valence showed scores above average in both versions, indicating a positive, arousing experience. In terms of UX, the Mesh version received a higher score in pragmatic quality compared to hedonic quality, indicating that users favored usefulness and usability over enjoyment and appeal. Compared to the official UEQ-S benchmark<sup>1</sup>, pragmatic quality was rated “Good”, whereas hedonic quality was only “Above Average”. The total score is still located in the “Good” category, indicating an overall successful implementation of the use case from the user’s perspective. The scores

![Chart block](images/warsinke2026_gs-mesh-dt-vr_p5_b10.png)

Figure 2: Boxplots showing the distributions of IPQ responses for both versions.

of the 3DGS version only reached the “Below Average” category in terms of hedonic quality and the “Bad” category in pragmatic quality, showing a lack of usability and usefulness in this version. The overall UEQ-S score is also considered “Bad” according to the benchmark, highlighting the negative impact of the usability aspects. Apart from the visual differences, the Mesh version offered a higher degree of interaction through real-time sensor data integration and an interconnected world, which likely improved the UX.

Cybersickness was reported in both versions at similar low to average level compared to the scales’ full range. However, a few users reported severe symptoms, which could pose a challenge for usage in virtual tourism. Interestingly, the qualitative responses revealed insights into potential causes. In the Mesh version, participants reported discomfort mainly from locomotion, while in the 3DGS version, visual artifacts seemed to have caused symptoms. One explanation could be that the Mesh version with a large virtual environment encouraged more movement. Furthermore, visual disturbances from 3DGS are known to threaten UX in VR [28].

The presence scores were overall low compared to the benchmark from Tran et al. [26]. In the Mesh version, the Involvement and General Presence scores reached the “Moderate” threshold, while the other dimensions received a “Low” score. In the 3DGS version all scores were in the “Low” category. Interestingly, Experienced Realism is the only metric, apart from cybersickness, that scored higher in 3DGS version compared to the Mesh version, likely due to the rendering technique that has an overall more photorealistic appeal (see Fig. 2). Still, the IPQ scores were unexpectedly low in both versions. A two-fold explanation can be considered that reflects two opposite perception dynamics from the rendering techniques. The appearance of the environment in the Mesh version can be classified as low-fidelity, as the point cloud data was reduced to simple mesh geometry during the creation process. Fig. 3 exemplifies the appearance of the buildings with a low level of detail, both in texture and polygon count. On the contrary, the 3DGS version has a more detailed appearance, with a enhanced level of detail and high resolution “textures”. However, the scene has more inconsistencies and imperfect areas with visual artifacts, such as the treetops shown in Fig. 4. Therefore, both approaches could have resulted in low presence and realism scores for their unique reasons.

An attempt to quantify the perception of the DTs was made through the custom questionnaire created for the study. As the question items are not validated, the interpretations shouldn’t be overestimated. Enjoyment, Simulation, and Understanding scored the highest, while Reliability and Information received lower scores in both versions. This aligns with the capabilities of the application, whose aim is to simulate a visit to a destination of choice. Apparently, the experience helped the understanding but did not nec-

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>1</sup>https://www.ueq-online.org/</span></small>

5

<!-- page 6 of 7 -->

© 2026 IEEE. This is the author’s version of the article that was accepted to the Hype-XR workshop and will be published in the proceedings of IEEE ISMAR 2026 conference (adjunct). The DOI of the final version will be added upon publication.

![Image block](images/warsinke2026_gs-mesh-dt-vr_p6_b2.png)

Figure 3: Screenshot from the Mesh version that depicts the simplified 3D-mesh geometry of a building.

![Image block](images/warsinke2026_gs-mesh-dt-vr_p6_b4.png)

Figure 4: Screenshot from the 3DGS version that shows rendering artifacts prominent in the treetops.

essarily provide additional information. In that regard, it must be noted that the sensor data in the Mesh version was possibly not seen by each participant, as they could explore freely without mandatory content. While the geometry was not updated further after the initial DTs were created, users still reported a moderate level of reliability regarding the current status of the places’ representation.

The sample group was evenly distributed by gender and spanned a diverse age range. The average affinity for technology interaction was above average (4.27 out of 6), indicating a technologically interested group. Their prior XR experience was average, while their video game and 3D modeling experiences were low. Compared to the average tourist, the sample group may be slightly more technologically advanced but was still considered suitable for the study.

In the Mesh version, prior 3D modeling experience showed a moderate positive association with experienced realism. This may indicate that users with greater expertise in 3D modeling evaluated the visuals as more realistic, possibly due to a greater awareness of the technical constraints and nuances of 3D content creation. 3D modeling is commonly understood as the manipulation of mesh geometry, which could explain why the relationship was not observed in the 3DGS version. In the 3DGS version 3D modeling experience and reliability showed a moderate positive correlation. Reliability in that regard refers to the ability to reflect the current status of a place or system (see Tab. 1). A possible explanation is that participants with more 3D modeling experience were more familiar with how physical environments are translated into digital models. Consequently, they may have been more confident in the correspondence between the reference location and its DT. However, this interpretation remains speculative, as it is unclear why the same relationship was not observed in the Mesh version.

## 5.1 Limitations and Future Work

Some limitations of the study should be acknowledged. Most importantly, the study was not designed as a controlled experiment with a single manipulated variable. Instead, multiple factors varied simultaneously between the two versions, such as the replicated place or the connectedness of the environment. Consequently, we refrained from performing inferential statistical comparisons between the versions and avoided drawing direct conclusions about their relative performance. Any comparative statements are therefore descriptive only. Additionally, participants could freely explore the application within a given time. Users visited the POIs in a different sequence and for varying durations. Generally, the study’s sample size was small, and the results of the DT questionnaire should be interpreted with caution, as it is not standardized. The questionnaire was used solely because, to our knowledge, no validated instrument currently exists for the subjective assessment of DT perception.

Future work should investigate the exact implications of 3D representation approaches on UX. To gain more nuanced insights, subsequent studies should focus on a subset of metrics and employ a more controlled study design. One approach would be to create DTs of the same environments using different 3D representation methods in a 2-by-2 crossover design to systematically investigate the effect of 3DGS compared to more traditional reconstruction approaches. Furthermore, the discussed differences in visual fidelity and their effects on experienced realism could be promising for efficient resource allocation in DT creation process. Another path could focus on the DT integration aspect by updating the environment or adding bidirectional data flow. Lastly, metrics measuring usefulness to the tourism industry, such as travel intention, should be considered for evaluating the application on a use case level.

## 6 CONCLUSION

The study examined two versions of an application for VR tourism in terms of UX, presence, affect, cybersickness, and attempted to quantify DT perception through a custom questionnaire. The Mesh version with an interconnected virtual environment and IoT sensor integration was well received, with good UX ratings and low to moderate presence scores. The 3DGS version with POI-centric exploration and 3DGS rendering showed weaknesses in pragmatic quality and low presence scores. Interestingly, experienced realism received a higher score in the 3DGS version, which may be attributed to the rendering technique. This indicates that increased realism perception alone is not necessarily associated with an increased UX. While cybersickness occurred in both versions, participants reported movement-related issues in the Mesh version, whereas in the 3DGS version, rendering artifacts caused discomfort. Despite symptoms, the VR experience was perceived positively, as indicated by affect and enjoyment ratings. The custom questionnaire responses indicate the strength of simulating the tourist destinations, which improved the understanding of the places. The exploration of user factors revealed that higher 3D modeling experience was positively associated with both perceived realism (Mesh version) and perceived reliability (3DGS version). Overall, the user evaluation suggests that both versions could benefit from higher presence and that the functionalities of the Mesh version likely enhanced pragmatic quality. The results contribute to the understanding of UX in VR tourism and provide preliminary insights into the perception of emerging 3D reconstruction methods.

## 7 ACKNOWLEGEMENTS

This work was supported by the European Union’s Horizon Research and Innovation Program under Grant 101092875 (DIDYMOS-XR: Digital DynaMic and responsible twinS for XR). The Overleaf AI features and Grammarly were used for editing and grammar enhancement during the document writing process.

6

<!-- page 7 of 7 -->

© 2026 IEEE. This is the author’s version of the article that was accepted to the Hype-XR workshop and will be published in the proceedings of IEEE ISMAR 2026 conference (adjunct). The DOI of the final version will be added upon publication.

## REFERENCES

[1] M. S. Anwar, M. Ali, M. Elwardy, S. Ahmad, P. N. Ahmad, and M. Ahmad. Gamified Immersive Learning and User Experience Evaluation of Metaverse-Based Cultural Heritage Education. In Proceedings of the International Workshop on Intelligent Immersification in the Metaverse: AI-Driven Immersive Multimedia, I2M-MM ’25, pages 44–52, New York, NY, USA, Oct. 2025. Association for Computing Machinery. 2

[2] J. Baker, K. Nam, and C. S. Dutt. A user experience perspective on heritage tourism in the metaverse: Empirical evidence and design dilemmas for VR. Information Technology & Tourism, 25(3):265–306, Sept. 2023. 1, 2

[3] M. K. Bekele, R. Pierdicca, E. Frontoni, E. S. Malinverni, and J. Gain. A Survey of Augmented, Virtual, and Mixed Reality for Cultural Heritage. J. Comput. Cult. Herit., 11(2):7:1–7:36, Mar. 2018. 2

[4] A. Betella and P. F. M. J. Verschure. The affective slider: A digital self-assessment scale for the measurement of human emotions. PLOS ONE, 11(2):1–11, 02 2016. 3

[5] D. S. de Almeida, F. B. e Abreu, and I. Boavida-Portugal. Digital twins in tourism: A systematic literature review, Jan. 2025. 1, 2

[6] T. Franke, C. Attig, and D. Wessel. A personal resource for technology interaction: development and validation of the affinity for technology interaction (ati) scale. International Journal of Human-Computer Interaction, 35(6):456–467, 2019. 3

[7] K. Girginova. When XR meets digital twins: Redrawing the conceptual map of extended reality. Frontiers in Virtual Reality, 7:1762601, Feb. 2026. 1, 2

[8] JASP Team. JASP (Version 0.95.4)[Computer software], 2025. 4

[9] B. Kerbl, G. Kopanas, T. Leimkuehler, and G. Drettakis. 3d gaussian splatting for real-time radiance field rendering. ACM Trans. Graph., 42(4), July 2023. 1, 2

[10] P. Kourtesis, J. Linnell, R. Amir, F. Argelaguet, and S. MacPherson. Cybersickness in virtual reality questionnaire (csq-vr): A brief tool for evaluating the virtual reality induced symptoms and effects (vrise), Dec. 2022. 4

[11] W. Kritzinger, M. Karner, G. Traar, J. Henjes, and W. Sihn. Digital Twin in manufacturing: A categorical literature review and classification. IFAC-PapersOnLine, 51(11):1016–1022, Jan. 2018. 1, 2

[12] K. Li, M. Masuda, S. Schmidt, and S. Mori. Radiance fields in xr: A survey on how radiance fields are envisioned and addressed for xr research. IEEE Transactions on Visualization and Computer Graphics, 31(11):9709–9719, 2025. 2

[13] X. Li, Q. Zhang, D. Kang, W. Cheng, Y. Gao, J. Zhang, Z. Liang, J. Liao, Y.-P. Cao, and Y. Shan. Advances in 3D Generation: A Survey, Jan. 2024. 2

[14] J. Liu, X. Huang, T. Huang, L. Chen, Y. Hou, S. Tang, Z. Liu, W. Ouyang, W. Zuo, J. Jiang, and X. Liu. A Comprehensive Survey on 3D Content Generation, Mar. 2024. 2

[15] S. M. C. Loureiro, J. Guerreiro, and F. Ali. 20 years of research on virtual reality and augmented reality in tourism context: A text-mining approach. Tourism Management, 77:104028, Apr. 2020. 1, 2

[16] P. K. Pandey, P. K. Pandey, S. Mahajan, J. Paul, and S. Iyer. Chapter 13 - Digital Twin and Virtual Reality, Augmented Reality, and Mixed Reality. In S. Iyer, A. Nayyar, A. Paul, and M. Naved, editors, Digital Twins for Smart Cities and Villages, pages 273–293. Elsevier, Jan. 2025. 1, 2

[17] K. Pavelka Jr., T. Boucek, and A. Rapuca. Virtual and Augmented ˇ Reality as a Modern Way of Exploring and Analysing Historical Objects in High Quality. The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences, XLVIII-M-9-2025:1161–1166, Oct. 2025. 1, 2

[18] E. Pekridou, C. Hitiris, S. Vasileiou-Kyriakou, V. Karamerou, D. J. Vergados, P. Sarigiannidis, and A. Michalas. LabTwinXR: A Real-Time eXtended Reality Digital Twin Testbed for Smart Buildings. In 2025 IEEE International Smart Cities Conference (ISC2), pages 1–6, Oct. 2025. 2

[19] I.-G. Project. Igroup presence questionnaire (ipq). Online. 4

[20] H. M. Rifqi. Virtual Reality in Tourism Research: A Thematic Literature Review. SBS Journal of Applied Business Research, pages

59–102, Aug. 2025. 1, 2

[21] F. Sang, H. Wu, Z. Liu, and S. Fang. Digital twin platform design for zhejiang rural cultural tourism based on unreal engine. In 2022 International Conference on Culture-Oriented Science and Technology (CoST), pages 274–278, 2022. 1

[22] M. Schrepp, A. Hinderks, and J. Thomaschewski. Design and evaluation of a short version of the user experience questionnaire (ueq-s). International Journal of Interactive Multimedia and Artificial Intelligence, 4:103, Jan. 2017. 3

[23] S. Seabold and J. Perktold. statsmodels: Econometric and statistical modeling with python. In 9th Python in Science Conference, 2010. 4

[24] U. Stankov, M. D. Vujiciˇ c, P. Orero, and U. Gretzel. Accessibility of ´ tourism 4.0—designing more meaningful and inclusive tourist experiences. Universal Access in the Information Society, 23(4):1503–1506, Nov. 2024. 1

[25] M. Tang, M. Nikolaenko, A. Alrefai, and A. Kumar. Metaverse and Digital Twins in the Age of AI and Extended Reality. Architecture, 5(2):36, May 2025. 1, 2

[26] T. Q. Tran, T. Langlotz, J. Young, T. W. Schubert, and H. Regenbrecht. Classifying presence scores: Insights and analysis from two decades of the igroup presence questionnaire (ipq). ACM Trans. Comput.- Hum. Interact., 31(5), Nov. 2024. 4, 5

[27] J. Tromp, D. Schofield, P. Raeisian Parvari, M. Poyade, C. Eagle sham, J. C. Torres, T. Johnson, T. Jurivete, N. Lauer, A. Reyes- ¨ Lecuona, D. Gonzalez-Toledo, M. Cuevas-Rodr ´ ´ıguez, and L. Molina-Tanco. Designing and Evaluating XR Cultural Heritage Applications Through Human–Computer Interaction Methods: Insights from Ten International Case Studies. Applied Sciences, 15(14):7973, Jan. 2025. 1, 2

[28] X. Tu, L. Radl, M. Steiner, M. Steinberger, B. Kerbl, and F. de la Torre. Vrsplat: Fast and robust gaussian splatting for virtual reality. Proc. ACM Comput. Graph. Interact. Tech., 8(1), May 2025. 2, 5

[29] I. P. Tussyadiah, D. Wang, T. H. Jung, and M. C. tom Dieck. Virtual reality, presence, and attitude change: Empirical evidence from tourism. Tourism Management, 66:140–154, June 2018. 1, 2

[30] C. Vachha, Y. Kang, Z. Dive, A. Chidambaram, A. Gupta, E. Jun, and B. Hartmann. Dreamcrafter: Immersive editing of 3d radiance fields through flexible, generative inputs and outputs. In Adjunct Proceedings of the 37th Annual ACM Symposium on User Interface Software and Technology, UIST Adjunct ’24, New York, NY, USA, 2024. As sociation for Computing Machinery. 2

[31] P. Virtanen, R. Gommers, T. E. Oliphant, M. Haberland, T. Reddy, D. Cournapeau, E. Burovski, P. Peterson, W. Weckesser, J. Bright, S. J. van der Walt, M. Brett, J. Wilson, K. J. Millman, N. Mayorov, A. R. J. Nelson, E. Jones, R. Kern, E. Larson, C. J. Carey, İ. Polat, Y. Feng, E. W. Moore, J. VanderPlas, D. Laxalde, J. Perktold, R. Cimrman, I. Henriksen, E. A. Quintero, C. R. Harris, A. M. Archibald, A. H. Ribeiro, F. Pedregosa, P. van Mulbregt, and SciPy 1.0 Contributors. SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python. Nature Methods, 17:261–272, 2020. 4

[32] C. Wang, Z. Li, and L. Wang. P-4.6: Generative AI meets 3D: Exploring cutting-edge advances in AI-generated 3D content. SID Symposium Digest of Technical Papers, 56(S1):935–939, June 2025. 2

[33] L. Wang, W. Xu, Y. Liu, M. Wang, B. Wang, X. Yang, L. Xu, Z. Tan, R. Fan, Z. Wang, C. Wang, H. Zhang, Y. Wen, H. Yang, J. Wu, J. Fan, H. Wang, Q. Zhang, G. Wang, Y. Wang, and Q. Zhao. Artificial intelligence for virtual reality: A review. Science China Information Sciences, 69(1):111101, Sept. 2025. 1

[34] Y. Wang, H. Xu, Y. Li, and F. Tian. High-Fidelity Virtual Reality With 3D Gaussian Splatting: User Experience Pathways and System Performance Evaluation. IEEE Access, 14:8238–8249, 2026. 1, 2

[35] I. Y. Wuni, M. Grieves, M. J. Yamin, and S. A. Koroma. Conceptualising the digital twin: An analysis of 358 definitions. Digital Twin, 0(0):2600763, Dec. 2025. 2

7