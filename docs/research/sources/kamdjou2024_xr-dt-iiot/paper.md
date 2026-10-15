<!-- page 1 of 23 -->

IEEE IEEE Open Journal of the EEE Comnications Society Communications Society

Received 14 December 2023; revised 12 January 2024; accepted 16 January 2024. Date of publication 19 January 2024; date of current version 6 February 2024. Digital Object Identifier 10.1109/OJCOMS.2024.3356508

# Resource-Constrained EXtended Reality Operated With Digital Twin in Industrial Internet of Things

**HUGUES M. KAMDJOU , DAVID BAUDRY , VINCENT HAVARD, AND SAMIR OUCHANI**

CESI LINEACT, 92074 Paris, France

CORRESPONDING AUTHOR: H. M. KAMDJOU (e-mail: hmkamdjou@cesi.fr)

This work was supported by CESI LINEACT.

**ABSTRACT** EXtended Reality (XR) alongside the Digital Twin (DT) in Industrial Internet of Things (IIoT) emerges as a promising next-generation technology. Its diverse applications hod the potential to revolutionize multiple facets of Industry 4.0 and serve as a cornerstone for the rise of Industry 5.0. However, current systems are still not effective in providing a high-quality experience for users due to various factors, one of which is their limited resources for processing and transmitting complex data and big data. To overcome these challenges, this paper presents an in-depth analysis of performance optimization techniques for resource-constrained Augmented Reality (AR) and/or Virtual Reality (VR) environments operating with DT, with a specific focus on Quality of Service (QoS), Quality of Experience (QoE), Edge-Cloud architectures and future research directions. Furthermore, this study delves into the intricate complex trade-off relationships involving optimization factors, including system quality, information quality, and QoE. In addition, it also explores potential solutions based on powerful emerging technological tools, including data compression, blockchain, cloud computing, quantum computing, Artificial Intelligence (AI) / Machine Learning (ML), and cybersecurity in the Cyber-Physical Systems (CPS). The insights provided in this comprehensive survey can inspire and guide researchers and industrial practitioners in optimizing performance for XR with DT applications in resource-constrained Smart Manufacturing System (SMS).

**INDEX TERMS** Augmented reality, digital twin, EXtended Reality, IIoT, optimization, resourceconstrained, virtual reality, visualization.

## I. INTRODUCTION

NDUSTRY 4.0, also known as the Fourth Industrial I Revolution, has brought about significant transformations in the Smart Manufacturing System (SMS) sector. However, at its current stage, Industry 4.0 is still at a transition point [7], paving the way for a new era of technological advancement known as Industry 5.0 [95]. This emerging paradigm will revolutionize the way humans interact with machines and reshape the relationship between the physical and virtual realms [6].

SMS encompasses the implementation of Industry 4.0 technologies and principles within manufacturing operations, aiming to create interconnected systems and processes that harness the power of data-driven insights, automation, and advanced analytics to elevate manufacturing efficiency, flexibility, and overall performance [8]. Key foundational technologies supporting SMS include Cyber-Physical Systems (CPS), Digital Twins (DT), metaverse and

eXtended Reality (XR) [64]. CPS involves the integration of physical and digital components, enabling real-time monitoring, control, and optimization of manufacturing processes. DT provides a virtual representation of physical assets, facilitating simulation, analysis, and predictive maintenance. The metaverse is a term used to describe a virtual reality space or a collective virtual shared space where users can interact with a computer-generated environment and other users in realtime [64], [96]. XR is an umbrella term that encompasses various immersive technologies, including Virtual Reality (VR), Augmented Reality (AR), and Mixed Reality (MR). These latter stand out as particularly promising, with a wide range of applications that could transform our daily lives [7]. They offer immersive experiences and visualization tools that enhance collaboration, training, and design processes in manufacturing. These technologies collectively contribute to the advancement and realization of SMS, revolutionizing the way manufacturing operations are conducted.

928

-c 2024 The Authors. This work is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 License. For more information, see https://creativecommons.org/licenses/by-nc-nd/4.0/

VOLUME 5, 2024

<!-- page 2 of 23 -->

ComSoc Communications Society IEEE Open Journal of the

![Image block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p2_b2.png)

FIGURE 1. Digital Twin with XR in Edge/Cloud platform.

The purpose of VR technologies is to provide users with a complete immersion experience in a virtual environment [5]. However, this type of immersion prevents users from perceiving and interacting with their actual physical environment. In contrast, AR enables users to perceive and interact with both their physical and virtual environments simultaneously [5]. In other words, AR/VR involves the use of computer technology to create the effect of an interactive multidimensional world in which virtual and real objects have a sense of spatial presence. Then, Augmented Reality/Virtual Reality (AR/VR) or XR is a paradigm through which digital information is added to the real-life perceptions, another definition is I<sup>3</sup>: Immersion + Imagination + Interaction [7]. There are two types of classifications of augmented reality systems, respectively Augmented Virtuality, where the environment is basically virtual with the injection of real objects; Augmented Reality, where the environment is real with the injection of virtual objects [5]. The display devices used in AR/VR can be divided into four categories such as monitorbased displays, projection-based displays, handheld display devices, and Head-Mounted Displays (HMD) [63].

DT as presented in Figure 1 is a digital model of a physical system and its ongoing processes deployed through a data connection that allows converting the physical system into a virtual system whereas maintaining a high level of synchronization between them. During the past few decades, XR coupled with DT has gained widespread usage as a means to effectively immerse oneself in a virtual environment,

enabling the visualization and interactive exploration of relevant information. This powerful combination facilitates the scaling up of data, enabling comprehensive evaluations, expediting and predicting business processes, enhancing productivity, fostering faster innovation, whereas concurrently reducing costs, interventions, risk analysis, and supporting informed decision-making.

XR coupled with DT is widely used for understanding information of interest, for scaling up data, for the purpose of performing appropriate evaluations, predictions, interventions, risk analysis and/or decision-making, etc [8].

These technologies are transforming the way people interact with digital content and enabling new applications in various fields of Industry 4.0. as illustrated in Figure 2, among others, there are: entertainment, business, education, and so on [7].

The aforementioned fields share several common performance problems and characteristics that bind them together. One significant aspect is the processing and transmission of large volumes of data, frequently in realtime or near real-time scenarios. Furthermore, these domains commonly involve multiple entities, including users, devices, and servers, necessitating efficient and secure interaction and information exchange among them. Consequently, algorithms and techniques developed and validated in one field can often be adapted and applied to others with similar attributes. These immersive technologies must ensure minimal delay for user interactions whereas maintaining

VOLUME 5, 2024

929

<!-- page 3 of 23 -->

KAMDJOU et al.: RESOURCE-CONSTRAINED XR OPERATED WITH DT IN IIoT

![Image block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p3_b2.png)

FIGURE 2. Various fields of XR with DT and CPS in Industry 4.0.

consistency and synchronization among multiple users. Resource constraints, particularly in terms of computing power, energy consumption, memory, and battery lifespan, continue to pose significant challenges for wireless devices in mobile environments, potentially limiting the ability to provide a high-quality user experience.

## A. BACKGROUND AND MOTIVATION

According to International Data Corporation (IDC) FutureScape [2], by 2024 the cloud will surpass on-premises infrastructure as the primary location where operational data is stored, managed, and analyzed for 50% of G2000 organizations. Besides, the potential market for mobile XR has grown considerably in recent years. Goldman Sachs has predicted that the AR/VR market ecosystem will be around \$80 billion by 2025, roughly the size of the PC market in 2016. Furthermore, by 2027, the use of XR technology, including AR/VR/MR tools, will increase by 40%, creating a new breed of digital worker and reducing operator/field worker errors by 30% as indicated by IDC FutureScape. However, wireless mobile AR/VR systems require heavy processing for object recognition, voice recognition, hand gesture recognition, and camera pose estimation with limited battery and computation capability. In addition, new technologies such as the Internet of Everything (IoE), Vehicle to Everything (V2X), Vehicle to Infrastructure (V2I), Autonomous Vehicles (AGV) and 5G/6G bring new demands

and opportunities for AR/VR in Industrial Internet of Things (IIoT) platform [33].

As shown in Figure 2, the problem of poor Quality of Experience (QoE) in these environments is linked to Quality of Service (QoS) factors, which have considerable impact. In a context of limited resources, one of the main research challenges is latency, which refers to the delay between a user’s request and the response from the network.

The motivation of this paper is to investigate how performance optimization approaches can be employed to address the challenges of XR systems, and to enhance the quality of service, information, and system performance for users in Industry 4.0.

As XR technologies continue to evolve, addressing performance weaknesses and gaps is critical to unlocking their full potential in Industry 5.0, which envisions a future where immersive workers collaborate with robots and intelligent machines.

## B. RELATED SURVEYS

This section provides an overview of existing surveys and reviews concerning Resource-Constrained XR operated with DT in the IIoT, along with their associated research and application areas. A comparative analysis is presented in Table 1, considering twelve criteria: Background, Application, XR+DT, Quality of Service (QoS), Quality of Experience (QoE), Security, Artificial Intelligence/Machine Learning (AI/ML), Edge/Cloud, Optimization, Collaboration,

930

VOLUME 5, 2024

<!-- page 4 of 23 -->

IEEE IEEE Open Journal of the EEE Comnications Society Communications Society

TABLE 1. Comparative summary of reviews and surveys.

|  | Related ref. | Year | Topics covered and scope | Background | Application | XR+DT | QoS | QoE | Security | AI/ML | Edge/Cloud | Optimization | Collaboration | Resources | Comparison |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [11] | 2022 | Mobile edge computing for video streaming | ○ | ○ | ○ | ● | ○ | ○ | ○ | ● | ○ | ○ | ○ | ● |
| 2 | [17] | 2022 | Immersive virtual reality for digital twins | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 3 | [21] | 2021 | The road towards 6G wireless systems | ● | ○ | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ● |
| 4 | [32] | 2016 | Ultra-dense networks | ○ | ○ | ○ | ● | ○ | ○ | ○ | ○ | ● | ○ | ○ | ● |
| 5 | [33] | 2017 | Mobile augmented reality | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 6 | [36] | 2020 | Internet of things toward 5G wireless systems | ○ | ○ | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 7 | [37] | 2020 | Vision of 6G wireless communication systems | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ● |
| 8 | [55] | 2020 | QoE management of multimedia streaming | ○ | ○ | ○ | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | ● |
| 9 | [58] | 2022 | Integrated sensing and communication systems | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 10 | [95] | 2023 | Navigating industry 5.0 | ● | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| - | Current paper | - | Extended reality with digital twin in IIoT | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |

Constrained Resources, and Comparison of the studied Surveys.

• Background: Indicates whether the survey provides the necessary background information required to comprehend XR, DT, and their utilization in IIoT contexts.

• Application: Specifies if applications and related use cases are addressed within the survey.

• XR+DT: Assesses whether the survey addressed the combined utilization of extended reality and digital twin technologies.

• QoS: Examines whether QoS metrics are detailed and examined within the survey.

• QoE: Indicates if QoE characteristics are considered as a feature to examine, understand and/or compare the surveyed contributions.

• Security: Determines if DT-related attacks and security issues are presented and included within the cited survey paper.

• AI/ML: Checks if the selected survey explores the integration of AI/ML technologies within the context of XR and DT.

• Edge/cloud: Evaluates whether the survey explores the implications of utilizing Edge/Cloud architectures in the context of Resource-Constrained XR.

• Optimization: Assesses whether the studied survey delves into optimization techniques and covers the exploration of strategies, algorithms, or methodologies aimed at enhancing the overall performance.

• Collaboration: Examines whether the surveyed content explores collaborative aspects, including humanmachine interaction, multi-robot cooperation, and other forms of collaborative behaviors within the IIoT settings.

• Constrained Resources: Examines if the survey addresses the challenges and strategies related to constrained resources in the context of XR and DT.

• Comparison: Indicates if the survey provides a comparison of the reviewed papers.

In the provided comparison in Table 1, the symbol - signifies that the survey does not consider the specified criteria, while  denotes the opposite. Additionally, - indicates that the authors of the cited work addressed only a portion of the criteria.

First, our particular focus on ultra-low latency and high-performance services, ultimately leading to a better user experience [21], [37], and [36]. Jiang et al. [21] and Chowdhury et al. [37] look at how 6G is deployed in communication systems and their requirements. Also, Chettri and Bera [36] surveyed the use of IoT toward 5G wireless systems. However, various algorithms and techniques [11], [17], [32] have been proposed to address challenges related to performance optimization, including software, infrastructure, architectural, and hardware solutions. For example, Khan et al. [11] surveyed works related to computing for video streaming at the level of mobile end users. Also, Pirker et al. [17] presented a review about virtual reality for virtual and digital twins.

Generally, Resource-Constrained XR operated with DT in the IIoT has sparked significant interest in exploring potential techniques. Thus, the literature encompasses a wide range of strategies, among the prominent techniques being investigated are AI, information prediction, data compression and aggregation, computation offloading, reliable offloading, joint computation offloading, collaborative edge computing, intelligent edge/cloud, multi-access mobile edge, information prediction, resource allocation, caching, energy consumption, security, and privacy protection [33], [55], [58], [95]. For example, Chatzopoulos et al. [33] studied mobile augmented reality. Barakabitze et al. [55] analyzed QoE management of multimedia streaming. Further, Liu et al. [58] studied integrated sensing and communication systems. Also, Tallat et al. [95] studied challenges and advances related to enabling Industry 5.0.

VOLUME 5, 2024

931

<!-- page 5 of 23 -->

KAMDJOU et al.: RESOURCE-CONSTRAINED XR OPERATED WITH DT IN IIoT

![Image block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p5_b2.png)

FIGURE 3. Paper organization.

The comparative analysis presented in Table 1 indicates that the majority of the discussed surveys provide only a brief or incomplete survey concerning the specified criteria. This survey aims to bridge the identified gap by offering an in-depth exploration of essential backgrounds, various terminologies related to Resource-Constrained eXtended Reality operated with Digital Twin in the Industrial Internet of Things (IIoT), use cases, metrics employed for evaluation, properties, attacks specific to this domain, existing visualization techniques, and a comprehensive survey and comparison of contributions related to Resource-Constrained eXtended Reality with Digital Twin in the IIoT. The current comprehensive survey performs a meticulous examination of these seminal works to identify potential solution approaches for addressing the challenges posed by XR coupled with DT in the context of SMS.

## C. OBJECTIVES AND CONTRIBUTIONS

XR with DT technologies hold tremendous promise for revolutionizing productivity in smart manufacturing factories. These immersive technologies offer unprecedented opportunities to enhance efficiency, safety, and collaboration within manufacturing processes. However, to fully unlock their potential, it is crucial to address the existing challenges and bridge performance gaps in order to deliver high-quality XR experiences.

This paper aims to provide a comprehensive survey and analysis of performance optimization techniques in resourceconstrained XR environments, with a particular focus in Industry 4.0.

The contribution of this paper is five main directions, which is summarized as follows:

• Study and in-depth review of relevant journal and conference papers from 1981 until now, exploring the research path, issues, and approaches over these years, along with the presentation and explicit illustration of basic concepts, their importance and performance measures in the context of XR environment in IIoT;

• Presentation and analysis of different edge/cloud architectures for performance optimization in a resource constrained XR environment;

• Presentation of an overview classification of different XR performance optimization techniques based on QoS, coding schemes, data type and applications;

• Proposition of a general framework of combinatorial optimization model for quantifying and analyzing the trade-off between different XR performance metrics;

• Suggestion of several open questions after discussing state-of-the-art approaches, with the aim of exploring possible future trends and emerging technologies in XR performance optimization according to their recent advancements.

## D. PAPER FORMULATION

The systematic organization of the paper is presented in Figure 3 as follows. Section II presents the bibliometric analysis of XR performance optimization related research works. Section III presents the main contribution of this paper, which includes an in-depth literature review, a taxonomy of studied articles in various aspects, with respect to the QoS, coding schemes, data type and its applications. Section IV begins with investigation of the preliminaries of the performance optimization factors in order to establish the trade-offs between them in XR environments with DT. In addition, it is provide a wide range of research problems and challenges. Section V, presents the potential areas of research, the contribution of the algorithms, methods, techniques, and the possible future research directions as a guideline for other researchers in this area. Finally, Section VI, concludes the paper and creates research interest focusing on performance optimization in resource constrained XR environment.

## II. BIBLIOMETRIE ANALYSIS

To fully leverage the benefits of XR in SMS factories, it becomes crucial to explore, sort out, and conduct research on optimizing the performance of these technologies. This analysis serves as a comprehensive guide for readers to navigate the existing corpus of work, understand its evolution, and gain insights into the key terms and trends shaping the field.

932

VOLUME 5, 2024

<!-- page 6 of 23 -->

ComSoc Communications Society IEEE Open Journal of the

![Image block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p6_b2.png)

FIGURE 4. Bibliometric analysis phases.

A deep literature search is conducted in the research database by seeking related keywords in document metadata. IEEE Xplore Digital Library is a comprehensive database for scientific and technical research, including XR-related topics. It provides access to a wide range of scholarly articles, conference papers, and technical standards in the field of XR. The collected literature is further refined by following three phases shown in the Figure 4.

The first phase is to screen related papers via keyword retrieving. Then, the metadata is extracted from the online database into the local Microsoft Excel CSV database. In other to cover the entire range of documents, a detailed search from IEEE Xplore Digital Library is carried out, with the respectively keywords:

((“Augmented Reality” OR “Virtual Reality” OR “Mixed Reality” OR “Extended Reality”) OR “Digital twin”) AND (“Performance” OR “Optimization” OR “Quality of Service” OR “Quality of Experience”) AND (“Industry” OR “Cyber Physical System” OR “Resource-constrained” OR “Low Resource” OR “Edge” OR “Cloud”).

The second phase involves transferring metadata from Microsoft Excel database into Power BI Desktop (PBI), where the data is cleaned up and modeled. Then, the third phase consists of querying the data, filtering, analyzing and visualizing the results using PBI.

The extraction result includes 2432 published papers between 1981 and Juin 2023. The retrieving yields 1706 conferences, 566 journal papers, 85 magazines, 64 early access articles and 11 books.

## A. PUBLICATION TYPE PER YEAR

Analysis of these 2432 papers by publication per year reveals an evolution of the research landscape, showcasing temporal trends, research focus, and the impact of industry trends. The result depicted in Figure 5 highlights the ongoing research trends and unequivocally demonstrates that interest in research is steadily increasing in crescendo. There has been a remarkable surge in published articles from 2017

onward, indicative of a notable increase in scientific output attributed to the transformative influence of Industry 4.0, significantly advancing XR with DT. Notably, in the past 32 years, 2022 accounted for 19.94% of total scientific publications, playing a substantial role in propelling the momentum of Industry 5.0.

## B. PUBLICATION BY TERMS

Network analysis is performed to enrich the understanding of co-occurring terms and presenting the findings in the form of visualizations. This refers to providing insights into relationships between terms. Figure 6 illustrates the relationships between co-occurring terms within articles. Each individual point or entity in the network visualization represents an article. The size of each node indicates the frequency or occurrence of the term keyword within the article. Connection links between nodes represent the co-occurrence of specific keywords in different articles. The thickness of the links between nodes signifies the frequency of co-occurrences between terms. Thicker links indicate a higher frequency of co-occurrence. Different thematic clusters are represented by distinct colors. Nodes and links within the same color-coded cluster are thematically related.

## III. LITERATURE REVIEW

## A. SCOPE OF WORK

Within the corpus of 2432 articles extracted, the focus turns to an in-depth study of 51 key research papers, predominantly drawn from the top journals and conferences on IEEE Xplore Digital Library. This selection was completed by the addition of pertinent articles identified in Google Scholar through screening references in corpus articles and those citing corpus articles. This selection criteria included best citation score, most recent publication date, and considerations of various aspects such as architectural design, performance optimization techniques, QoS and QoE, data types utilized, application use cases within the Industry 4.0 area, and potential future research directions. This analysis aims to provide a comprehensive up-to-date overview of the current state-of-the-art in the implementation of XR operated with DT within resource-constrained IIoT environments.

## B. CHALLENGES AND LANDSCAPE

According to this study, XR with DT has offered tangible benefits in many industrial applications, such as visualization [9], logistic, supply chain [11], maintenance [12], product design and assembly [13], Aerospace simulation [14], automotive [10], navigation [15], maritime [16], and general-purpose engineering training tools [17], [76], were notably more prevalent.

These applications include advanced training and simulation modules where XR facilitates immersive learning experiences by merging physical and virtual realms. The integration of Physical and virtual robotic cells with XR in the transition from Industry 4.0 to Industry 5.0, along with

VOLUME 5, 2024

933

<!-- page 7 of 23 -->

KAMDJOU et al.: RESOURCE-CONSTRAINED XR OPERATED WITH DT IN IIoT

![Chart block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p7_b2.png)

FIGURE 5. Number of publication type per year from 1981 to June 2023.

![Image block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p7_b4.png)

FIGURE 6. Co-terms network visualization.

DT, heralds transformative industrial applications [89]. Realtime monitoring and control of robotic cells are enriched through XR interfaces, enabling operators to engage with DT for dynamic process visualization. Collaborative robotics sees a paradigm shift, with XR bridging the gap between human and robot interactions in shared workspaces, facilitated by the insights from DT [90]. As illustrated in Figure 1, maintenance and troubleshooting activities leverage XR-guided interventions on DT, minimizing downtime and optimizing efficiency. Despite these promising applications, challenges such as integration complexity, data security, skill requirements, and ethical considerations need meticulous attention for a seamless transition to Industry 5.0. Effectively

addressing these challenges will unlock the full potential of XR-integrated Physical and Virtual Robotic Cells along with DT in shaping the future of industry.

XR coupled with the DT models are widely used for training simulators, preparing learners for real-life scenarios in real-world industrial or space technology situations, as well as to allowing them to make anticipated and adaptive in-design decisions in a cost-effective manner. In addition, it helps to reduce the time and cost factors that plague many Industry 4.0 design processes.

However, several challenges and issues related to performance need to be addressed [24]. XR applications often involve complex High Performance Computing (HPC), such as real-time tracking, rendering of virtual objects, and image processing [19]. These calculations are resource-intensive and require powerful hardware capabilities. Ensuring efficient and optimized algorithms is crucial to deliver a smooth and responsive XR experience [18].

XR in CPS applications may require high-quality rendering of realistic virtual objects or overlays [23]. Achieving high-fidelity rendering in real-time is demanding on the hardware, especially for complex scenes with multiple objects and dynamic lighting conditions [22]. Striking a balance between rendering quality and performance is essential [21].

Industrial SMS often require real-time responsiveness to provide accurate and timely information to users [39]. Any significant latency or delay between real-world actions and corresponding XR overlays can hinder productivity and usability [27]. Minimizing latency is crucial, which requires efficient processing, rendering, and communication between devices [20].

934

VOLUME 5, 2024

<!-- page 8 of 23 -->

IEEE IEEE Open Journal of the IEEE Comeunications Society Communications Society

Some XR applications are power-hungry due to intensive computations, graphics rendering, and constant use of sensors [25]. For industrial use cases that involve prolonged usage, energy efficiency becomes vital [29]. Optimizing algorithms and implementing power-saving strategies aim to extend battery life and ensure sustainable usage [30].

Industrial XR systems may rely on edge/cloud-based processing [28], data streaming, or remote collaboration, which requires a stable and high-bandwidth network connection [31]. In environments with limited network infrastructure or unstable connections, ensuring a consistent and reliable network becomes a challenge [32].

Industrial settings may have a diverse range of devices with varying hardware capabilities, operating systems, and software versions [33]. Ensuring compatibility and consistent performance across different devices is a challenge [26]. Developers need to consider device fragmentation and optimize their applications accordingly [38].

Constantly monitoring and detecting potential cyber threats, and implementing preventive measures to secure industrial systems and networks [36], is critical to safeguard against attacks [35]. Identifying and addressing vulnerabilities in industrial control systems and network infrastructure to prevent unauthorized access and data breaches [34]. XR coupled with DT helps operators, physicians and learners to improve qualifications, competencies and skills or knowledge through real-life scenarios from real situations, which provide an opportunity to learn-by-doing via hands-on practice. In today’s rapidly evolving technological landscape, the combination of XR and DT in edge/cloud framework for resource-constrained environment has emerged as a powerful paradigm with immense potential. These technologies open up new possibilities for collaboration, visualization, and decision-making in a wide range of new generation industries.

The exploration of the key findings, methodologies, and contributions of each study, aims to offer an overview of the advances, challenges and issues of these technologies.

Several articles present performance optimization models that are tailored to specific deployment scenarios in IIoT. The architecture of these models can vary depending on the characteristics and requirements of the particular scenario.

Some studies from authors [18], [20], [23], [40], [41], [42], [43], [44], [45], [46], [47], highlight the benefits, challenges, and trade-offs associated with distinct characteristics computing paradigms (edge computing, fog computing, cloudlet, and cloud computing). Edge computing focuses on processing data locally at the edge of the network, fog computing extends edge computing with additional layers of computing nodes, cloudlet provides mini-cloud deployments at the edge for localized processing, and cloud computing offers centralized and scalable computing services over the Internet. The hybrid model draws the compromise from the fact that each paradigm serves different use cases and contributes to creating a distributed and efficient computing ecosystem.

They delve into topics such as resource allocation, performance anomalies, virtual machine management, and security. These studies also provide valuable insights into optimizing resource utilization, enhancing scalability, efficiency, accessibility, and ensuring the security.

As a mater of fact, efficient resource management is crucial for maximizing the utilization of XR resourceconstrained environment, and achieving desired performance levels.

Works by [9], [12], [19], [28], [30], [31], [48], [49], delve into resource allocation, scheduling, energy optimization, and QoS provisioning based on Machine Learning (ML) algorithms and energy-efficient offloading techniques. They propose techniques such as dynamic scaling, workload prediction, and energy-aware offloading, contributing to resource optimization strategies in cloud computing. These studies offer valuable insights into improving resource management efficiency and performance in XR resourceconstrained environments. As a result, efficient workflow management systems are vital for orchestrating and executing scientific workflows.

In these frameworks, ensuring security and privacy remains a significant concern. References [21], [27], [32], [34], [35], [36], [37], [50], [51], [52], examine different aspects of security for XR with DT in edge/cloud resourceconstrained environment, including data protection, access control, intrusion detection, and privacy preservation. Their works highlight the challenges and propose approaches to mitigate security risks, contributing to the development of secure edge/cloud computing frameworks. These studies provide relevant insights into safeguarding sensitive data and maintaining privacy in cloud environments.

## C. PERFORMANCE EVALUATION AND BENCHMARKING

Assessing the performance, benchmarking, and analyzing scientific workflows are crucial to comprehending the capabilities and limitations of XR technologies. Authors in [25], [27], [33], [49], [53], [54], [55], [60] conduct performance evaluations, comparing different cloud platforms, workflow systems, and resource allocation strategies. Their works contribute to performance analysis, evaluation methodologies and provide benchmarks for assessing the efficiency and effectiveness, for system designers and users, aiding in the selection and optimization of edge/cloud-based workflows. In the most common cases, XR performance evaluation focuses on five main areas, such as efficiency, flexibility/reconfigurability, robustness, adaptivity and sustainability.

## 1) EFFICIENCY EVALUATION

Efficiency evaluation is assessed by optimizing rendering content, network, and hardware equipment [27]. This involves designing and enhancing XR rendering content, reducing computational needs through strategies like polygon count optimization, texture size adjustment, and asset compression [74]. Network optimization focuses on minimizing

VOLUME 5, 2024

935

<!-- page 9 of 23 -->

KAMDJOU et al.: RESOURCE-CONSTRAINED XR OPERATED WITH DT IN IIoT

latency and bandwidth requirements by refining network protocols, data compression, and caching mechanisms, ensuring a smooth XR experience [95]. Hardware optimization aims to maximize performance by leveraging hardware capabilities effectively and ensuring compatibility between XR devices and software [55].

## 2) FLEXIBILITY, RECONFIGURABILITY AND ADAPTIVITY EVALUATION

Flexibility and reconfigurability evaluation of software and hardware components involve adopting a modular design and ensuring scalability [56]. A modular software design allows for easy integration, customization, and reconfiguration of XR applications, enabling quick adaptation to evolving needs. On the hardware side, a modular approach facilitates the seamless integration and interchangeability of components, ensuring scalability and flexibility in the physical XR setup.

By breaking down the system into independent modules, it becomes easier to modify, replace, or add new components as needed, enhancing flexibility and adaptability. Component-based systems enable developers to assemble and configure XR setups based on specific requirements and preferences. Scalability is achieved by designing XR systems with scalability in mind, enabling the addition or removal of XR components as needed without significant disruptions.

Adaptivity evaluation refers to the ability of the system, to take into accomodation different factors and respond to different users specifications, contexts and requirements in order to provide optimal user experiences and outcomes [25]. This includes considering user preferences, needs, and capabilities during XR design to provide customizable settings, adaptive interfaces, and personalized content, enhancing user engagement and satisfaction (user-centric design). Additionally, it involves utilizing sensors, location tracking, and environmental data to create adaptive XR experiences that dynamically adjust based on the user’s context and surroundings (context awareness design).

## 3) ROBUSTNESS EVALUATION

Robustness evaluation refers to the ability of a system to maintain its performance and functionality without significant degradation even in the presence of uncertain or imprecise disturbances or failures [53]. This includes implementing robust error handling mechanisms for unexpected situations like network disruptions or hardware failures to ensure graceful handling, providing fallback options and error recovery strategies to minimize the impact on the user experience, and incorporating monitoring tools for continuous performance tracking, issue detection, and proactive problem resolution in XR systems. Incorporating monitoring tools for continuous performance tracking, potential issue prediction, issue detection, and proactive problem resolution in XR systems.

TABLE 2. Performance metrics recommendation.

| Metric | Recommendation | Tolerance |
| --- | --- | --- |
| Frame rate | ≥ 60 fps |  |
| Latency | ≥ 20 ms | ≤ 50 ms |
| Tracking accuracy | [0.05 mm, 0.5 mm] |  |
| Visual fidelity | ≥ 4K | ≥ 720 p |
| Audio quality | [50 Mbps, 500 Mbps] |  |
| Network stability | {32 kHz, 44.1 kHz, 48 kHz} |  |
| RAM | ≤ 80-90% used |  |
| CPU | 20-30% used | 70-80% used |
| GPU | ≤ 90-95% used |  |
| Battery | ≥ 10-20% |  |

## 4) SUSTAINABILITY EVALUATION

Sustainability evaluation in XR entails the consideration and implementation of environmentally and socially responsible practices in the development, deployment, and use of XR in order to minimizing the negative environmental impact, promoting ethical and inclusive practices, and ensuring longterm viability and positive outcomes for individuals and communities [57]. This involves developing energy-efficient XR systems, optimizing resource usage, reducing storage and computation needs, and implementing power-saving features. Furthermore, it includes a focus on environmentally friendly materials in XR hardware, aiming to minimize waste and embrace sustainable manufacturing processes. Lifecycle management is crucial, emphasizing proper disposal options, recycling for XR devices, and the reduction of electronic waste. The concept of frugality underlines sustainable development by encouraging resource-efficient practices, minimizing waste, and optimizing resource utilization to meet present needs without compromising the ability of future generations to meet their own needs.

## IV. TRADE-OFFS AND CHALLENGES A. PERFORMANCE METRIC

To perform an objective analysis of the trade-offs between optimization factors, a performance metric analysis is necessary. However, measuring XR performance is challenging due to the combination of the various factors relative to the specificity of each user, environment and application [27], [32]. Nevertheless, the main key common metrics used to evaluate and measure XR performances are presented in Table 2 [58], [59], [60].

These metrics include frame rate, measuring the number of frames per second (fps) rendered by an XR system. Higher frame rates result in smoother and more immersive experiences. Monitoring and adaptively optimizing frame rates help ensure a seamless and comfortable XR experience.

Latency denotes to the delay between user input and XR environment response; tracking accuracy, ensuring precise user movement tracking for realistic experiences. Lower latency is crucial for maintaining the feeling of presence and responsiveness in XR applications. In fact, optimizing

936

VOLUME 5, 2024

<!-- page 10 of 23 -->

IEEE IEEE Open Journal of the EEE Comnications Society Communications Society

latency improves user engagement and reduce post traumatic stress of XR sickness.

Load time measures the time it takes for an XR application or content to load and start running. Optimizing load times improves user engagement and reduce frustration. Measuring and optimizing load times involves analyzing factors such as file sizes, asset optimization, and data streaming efficiency. Tracking accuracy relies on accurate tracking of user movements and interactions to provide realistic experiences. Assessing the accuracy and precision of tracking systems, such as head tracking or hand tracking, helps to optimize XR performance and ensure accurate virtual object placement and interaction.

Performance profiling involves analyzing system resource usage, such as Battery, CPU, GPU, and memory utilization. Profiling tools and techniques helps to identify performance bottlenecks and help optimize resource allocation and usage in XR applications. Battery lifespan is essential for XR devices that are battery-powered; longer battery life allows users to engage in XR experiences for extended periods. Monitoring power consumption and optimizing resource usage helps to enhance battery life in XR applications.

QoS focuses on the objective assessment of the technical performance and reliability of the XR system. It measures the system’s ability to meet certain predefined parameters or specifications. QoS metrics include factors such as network latency, bandwidth, frame rate, resolution, tracking accuracy, data transmission speed, reliability, availability, and resource utilization. QoS metrics are typically collected through performance monitoring tools, system logs, or network analysis. QoE focuses on the subjective assessment of the user’s experience with the XR system. Collecting and evaluating user experience feedback through surveys, interviews, or user testing sessions help to provide valuable insights into the perceived performance and optimization of XR experiences. User feedback help to identify pain points, areas for improvement, and validate the effectiveness of performance optimization efforts. QoE metrics include factors such as visual realism, social interaction, comfort and ease of use.

## B. TRADE-OFFS BETWEEN OPTIMIZATION FACTORS

In the context of XR performance optimization, there are often trade-offs that need to be considered. These tradeoffs involve making decisions that balance different aspects or objectives, as optimizing one aspect may come at the expense of another. As presented in Figure 7, some common trade-offs for performance optimization are described in the following sub-sections.

## 1) QOE VS QOS

QoE and QoS metrics are complementary in the evaluation of XR systems. In fact, the quality of the underlying technical aspects, such as tracking accuracy, graphics rendering, and network performance, directly affects the user’s perception and satisfaction. Higher QoS levels contribute to improved

![Image block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p10_b10.png)

FIGURE 7. Dependency trade-offs between performance factors.

QoE, as a well-performing system enhances the user’s overall experience.

## 2) PERFORMANCE VS. VISUAL QUALITY

Achieving high visual quality in XR experiences often requires more computational resources, which can impact performance. Increasing visual fidelity through higher resolution textures, complex lighting, or detailed models can strain the hardware, potentially leading to lower frame rates or increased latency. Finding the right balance between performance and visual quality is crucial to deliver immersive and smooth immersive experiences.

## 3) MEMORY AND PROCESSING POWER VS. BATTERY LIFESPAN

XR experiences typically require significant processing power, which can drain the battery life of mobile XR devices. Compressing and streaming assets (textures, 3D models, etc.) can also reduce the memory footprint and loading times. However, lossy data compression/aggregation or streaming methods may impact the quality of the assets. Choosing the right compression and streaming strategies is crucial for balancing quality and performance. Balancing the need for computational performance with optimizing power consumption is essential to ensure a satisfactory user experience without excessive battery drain. Techniques like data compression, efficient rendering, resource management, frugal AI and power-saving optimizations can help strike this balance.

## 4) REALISM VS. INTERACTIVITY

Creating highly realistic XR environments often requires complex and detailed simulations, which can impact interactivity and responsiveness. Real-time interactivity may require simplifying or optimizing certain aspects of the simulation to ensure smooth user interactions and maintain acceptable performance. Balancing the level of realism with the need for interactive and responsive XR experiences is critical. As a matter of fact, one of the key challenges on XR is the lack of visual realism and realism of the dynamics perception and interaction of users. Psycho-visually, the human brain’s construction allows us to detect even slightest unrealistic

VOLUME 5, 2024

937

<!-- page 11 of 23 -->

KAMDJOU et al.: RESOURCE-CONSTRAINED XR OPERATED WITH DT IN IIoT

fictional details, which can easily break the immersion. Optimizing the appearance of reality remains a permanent scientific research challenge to mitigate the physical sideeffects of immersion, such as anxiety, post-traumatic stress, addiction-induced isolation and mood swings.

## 5) LATENCY VS. PERFORMANCE

Balancing the latency of XR systems while concurrently striving for optimal performance constitutes a complex challenge that demands a nuanced approach. Latency, in the context of XR, directly influences the QoS and then the user’s experience, with lower latency leading to more seamless and immersive interactions. The delicate equilibrium between latency and performance optimization must consider factors such as network bandwidth, computational capabilities of edge and cloud resources, rendering efficiency, data transmission protocols, and user interactions. Techniques like data compression, predictive analytics, cutting-edge computing, context-aware computing, including 5G networks, and AI-driven optimization can help strike balance between latency reduction and performance enhancement.

## 6) COMPLEXITY VS. EASE OF USE

XR applications that offer extensive features and functionalities may provide more flexibility, adaptability and possibilities but can also introduce complexity for users. Striking a balance between providing advanced features and maintaining a user-friendly interface is essential for ensuring accessibility and ease of use. Simplifying user interactions and streamlining workflows can contribute to a more intuitive and enjoyable immersive experiences.

## C. PROBLEM ANALYSIS AND FORMULATION OF PERFORMANCE TRADE-OFF

XR performance optimization involves trade-offs between different metrics. The interactions and dependencies among these components create a complex decision space [55]. This problem is further compounded by its classification as an NP-hard problem [58]. To overcome these challenging issues, a combinatorial optimization model is needed for quantifying and analyzing these trade-offs, enabling decision-makers to make informed choices and strike a balance that maximizes performance and user satisfaction [10]. However, it’s important to note that developing a specific optimization model depends on the specific context, objectives, and constraints of the XR application in SMS [57], [61]. A general framework to represent the trade-offs as decision parameters can be defined as follow:

• QoE: Vector of different metric of a Quality of Experience (subjective measure of user satisfaction)

• QoS: Vector of different metric of a Quality of Service (objective measure of technical performance)

• Resource: Vector of different metric a resource utilization of the XR device application (objective measure)

$f , g ,$ h: Functions of different parameters QoS and QoE and Resource respectively

• Quality of Experience Weight $( W _ { Q o E } ) ;$ A variable representing the weight or importance given to QoE in the overall performance optimization. This variable can range from 0 to 1, with 0 indicating no importance and 1 indicating maximum importance.

• Quality of Service Weight $( W _ { Q o S } )$ : A variable representing the weight or importance given to QoS in the overall performance optimization. Similar to QoE weight, it can range from 0 to 1.

• Resource Weight $( W _ { R e s } ) ;$ A variable representing the weight or importance given to resource utilization (e.g., Buttery, Memory, CPU and GPU utilization) in the performance optimization. It can range from 0 to 1, indicating the significance of performance.

• Development Time Weight $( W _ { D e v T } )$ : A variable representing the weight or importance given to development time in the performance optimization. It can range from 0 to 1, indicating the significance of development time.

The objective function would aim to optimize the overall Performance (P) of XR considering the trade-offs. It can be defined as a weighted sum of the various measures, such as:

$$
\begin{array}{l} \text {maximize} P = f (Q o S) \cdot W _ {Q o S} + g (Q o E) \\ \qquad \cdot W _ {Q o E} + h (R e s) \cdot W _ {R e s} \\ \text {subject to:} W _ {Q o E} + W _ {Q o S} + W _ {R e s} = 1, \\ \qquad Q o S _ {(i)} \geq \text {Target\_QoS} _ {(i)}, \\ \qquad Q o E _ {(i)} \geq \text {Target\_QoE} _ {(i)}, \\ \qquad R e s _ {(i)} \leq \text {Max\_power} _ {(i)} \end{array}\tag{1}
$$

Where i is the different metric item. Each weight $( W _ { Q o E } +$ $W _ { Q o S }   +   W _ { R e s } )$ should be adjusted based on the relative importance of each metric in the overall system performance and user satisfaction. It should be noted that these constraints (Target\_ $\mathcal { Q } o S _ { ( i ) }$ , Target\_ $\underline { { { \mathcal { Q } } } } o E _ { ( i ) }$ , Max $p o w e r _ { ( i ) } )$ depend on the specific requirements, expectations and priorities of the XR application. Depending on the specific requirements and constraints, additional variables and constraints may need to be incorporated. On the basis of Table 2, the subsequent sections comprehensively describe the functions of the commonly used parameters.

## 1) DEFINITION OF QOS FUNCTION F(QOS)

To provide a high immersive XR experience, a minimum level of QoS is required. The specific QoS requirements can vary depending on the type of XR experience, the application, and the user’s expectations.

Achieving a highly immersive XR experience $( Q o S _ { ( i ) } )$ involves careful consideration of several critical metrics. The frame rate, ideally maintained at 60 frames per second (FPS) or higher, plays a pivotal role in ensuring smooth and fluid XR experiences, minimizing motion sickness, and providing a realistic sense of presence. Low latency, below 20 milliseconds (ms) for real-time or near-real-time responsiveness and within the acceptable range of 20 to 50 ms, is crucial to reducing the delay between user actions and system feedback.

938

VOLUME 5, 2024

<!-- page 12 of 23 -->

IEEE IEEE Open Journal of the EEE Comnications Society Communications Society

Accurate tracking is paramount in XR, relying on precise and reliable tracking of head movements and controller inputs within a range of 0.05 mm to 0.5 mm. Visual fidelity contributes to the immersive nature of XR, balancing performance and quality with specified requirements like 720 pixels (p) for High Definition (HD) or 3840x2160 pixels for Ultra HD or 4K resolution.

Immersive audio quality, with accurate positioning of sound sources, is crucial for a truly immersive XR experience, with acceptable metrics specified in Megabits per second (Mbps). Load time, measuring the duration for an XR application to start and load necessary assets, significantly contributes to a better user experience. Faster load times are achieved through efficient initialization and asset loading processes.

For networked XR experiences, a stable and highbandwidth network connection is necessary to maintain real-time interactions, multiplayer capabilities, and content streaming. The sample rate for audio, indicating the number of samples carried per second, can vary (e.g., 32 kHz, 44.1 kHz, or 48 kHz). These metrics collectively define the quality and performance of the XR experience, offering guidelines for optimal user satisfaction.

## 2) DEFINITION OF QOE FUNCTION G(QOE)

The function g(QoE) refers to the overall subjective quality and satisfaction experienced by the end user whereas using an XR application. It encompasses various perceptual factors that influence the user’s perception of the application’s quality, including visual and auditory immersion, responsiveness, interactivity, comfort, and absence of disturbances or artifacts. QoE is subjective and varies from user to user, as it depends on personal preferences, expectations, and individual perception.

Factors influencing XR quality of experience (QoE(i)) encompass various dimensions that significantly impact user satisfaction. Visual Quality and Audio Immersion involve evaluating realism and fidelity through user studies, feedback, and participant ratings on aspects like resolution, clarity, texture detail, lighting, color accuracy, and overall appeal. Similarly, subjective evaluations of audio quality, spatialization, clarity, and realism are considered.

Ensuring smoothness and Stability of Motion is crucial to prevent motion sickness and provide a comfortable XR experience. Consistent frame rates, reduced latency, and minimized jitters or stutters contribute to smoother interactions. Users’ subjective feedback on the perceived smoothness and stability of motion is collected through surveys and questionnaires.

Interactivity and responsiveness entail evaluating the effectiveness of interactive elements within XR applications. This includes assessing user interactions, ease of use, and feedback mechanisms, whether visual, auditory, or haptic. The responsiveness and intuitiveness of the application’s interaction mechanisms are gauged through users’ subjective feedback.

Comfort and absence of motion sickness are key considerations in XR applications to minimize discomfort and motion sickness. Strategies like reducing motion blur, optimizing visual cues, and lowering latency contribute to user comfort. Users’ self-reported symptoms of discomfort or motion sickness during or after the XR experience are gathered through surveys, questionnaires, or interviews.

Flexibility, usability, and intuitive interactions are crucial for a satisfying XR experience. Intuitive and user-friendly interfaces, alongside customization options, contribute to a seamless and immersive user experience. User testing, usability studies, and feedback evaluate users’ ease of use, ability to perform tasks, and overall satisfaction with the interaction design.

## 3) DEFINITION OF RESOURCE FUNCTION H(RES)

Optimizing resource utilization often involves considering algorithm complexity. By selecting or designing algorithms that have lower time and space complexity, developers can reduce the computational resources required by the application. Resource utilization assesses how efficiently the XR application utilizes the device’s computational resources, such as Battery, CPU (Central Processing Unit), GPU (Graphics Processing Unit), and memory (RAM). Optimized resource utilization ensures efficient performance and prevents resource bottlenecks.

Resource utilization metrics are fundamental for delivering a highly immersive XR experience $( R e s _ { ( i ) } )$ . These encompass various aspects. RAM is crucial for storing and manipulating the virtual environment, assets, and textures in XR applications. To avoid performance problems like excessive swapping or memory constraints, it’s advisable to keep memory utilization below 80-90%. CPU efficiency is paramount for responsive XR applications. A generally acceptable range is 20-30%, with the recommendation to maintain CPU utilization below 70-80% for optimal performance. GPU engagement varies based on capacity, power constraints, and application complexity. While no specific minimum threshold is defined, keeping GPU utilization below 90-95% prevents performance bottlenecks. Battery consumption, measuring power used by the XR device during application usage, is vital for user satisfaction and device longevity. Optimizing battery utilization ensures a satisfactory experience, typically maintaining usage above 10-20%.

## D. CHALLENGES AND ISSUES IN OPTIMIZING PERFORMANCE

In the realm of performance optimization problem, building an unified holistic optimizing performance model across multiple disciplines in the context of XR is challenging [58]. Only XR encompasses various technologies, including VR, AR, and MR; each with its own unique characteristics and requirements; and involves multiple disciplines such as computer graphics, human-computer interaction, networking, computer vision, data processing, cognitive science, physics,

VOLUME 5, 2024

939

<!-- page 13 of 23 -->

KAMDJOU et al.: RESOURCE-CONSTRAINED XR OPERATED WITH DT IN IIoT

and more. Each discipline has its own unique considerations and optimization techniques.

The research literature explores various approaches aimed at reducing complexity and attaining optimal or near-optimal solutions. In this context, a comprehensive investigation of the literature reveals three commonly adopted approaches: the classic approach, heuristic approach, and AI approach [65], [66], [67]. However, some challenges involved in building a unified optimizing performance model across multi-disciplines in XR are as follows:

## 1) COMPLEXITY MANAGEMENT

XR systems involve a combination of hardware components, rendering settings, computational resources, tracking systems, and network management. The interactions and dependencies among these components create a complex decision space. For example, the visual quality of the graphics subsystem may impact the rendering performance, which in turn can affect the tracking accuracy or audio processing. Another challenge is the rapid evolution and diversity of XR technologies [62]. The XR landscape is continuously evolving with advancements in hardware, software, and interaction paradigms. Keeping up with these advancements and incorporating them into a unified performance model can be challenging due to the need for ongoing research and development.

## 2) DIVERSE PERFORMANCE METRICS

Different disciplines in XR have their own performance metrics and optimization goals, the optimization of performance metrics across multiple disciplines requires reconciling conflicting objectives and constraints [59]. For example, optimizing computational efficiency may have trade-offs with visual quality or network latency. For instance, graphics optimization focuses on frame rate and visual quality, whereas audio optimization emphasizes latency and audio fidelity [60]. Balancing and integrating these diverse metrics into an unified generic model in order to achieve an optimal performance model across disciplines is a non-trivial task.

## 3) RESOURCE CONSTRAINTS

XR experiences often run on various devices with different capabilities and resource-constrained like HMD, smartphones or standalone headsets [63]. These devices have limitations in terms of processing power, memory, battery life, and thermal constraints. Optimizing performance across multiple disciplines whereas considering these resource constraints requires careful management and trade-offs [67]. Thus, designing a performance model that is adaptable and optimized for a wide range of platforms and devices requires careful consideration of hardware limitations and system requirements.

## V. FUTURE RESEARCH AGENDA

It has been proven in this survey that, the integration of XR with DT technology holds immense potential for

various SMS applications. However, although as long as it is a new exciting technology for knowledge sharing, it presents important gaps and drawback areas that involves scientific challenges that require further research, to outline the remaining research questions as well as new questions and directions regarding potential solutions; in order to fully leverage the capabilities of XR coupled with DT in resourceconstrained environments. These future research agenda sheds light on potential advancements and directions for future exploration, offering valuable insights into upcoming trends and challenges in scientific workflows in the issues of QoS, coding schemes, data type and applications.

## A. POTENTIAL RESEARCH AREA AND SOLUTION STRATEGIES

This section explores key open challenges within XR with DT and articulates corresponding solution strategies aimed at tackling emerging challenges. Establishing a comprehensive understanding across various disciplines becomes pivotal in constructing a unified performance optimization model that spans multiple disciplines in XR and DT. The identified potential research areas encompass subjects like edge computing, serverless computing, federated clouds, and data-intensive workflows. These areas signify promising directions for further research and development in the field.

To address the imperative of devising solutions for optimizing permanence in resource-constrained environments, it is crucial to recognize that the development of a unified performance model in XR necessitates an indepth comprehension of each discipline. This undertaking calls for effective collaboration and an iterative approach, emphasizing the interdependence of diverse disciplines. The subsequent enumeration highlights potential solution strategies designed to untangle optimization challenges within the XR in IIoT with DT.

## 1) CONTEXT-AWARENESS AND PERSONALIZATION

Context-awareness is one of the most important research area. Most of XR systems often have limited flexibility and adaptability in terms of accommodating different user preferences, needs, and application requirements [70]. The ability to customize and adapt the XR experience to individual users or specific use cases is crucial for maximizing user satisfaction QoE and achieving optimal performance. Designing flexible and adaptable XR systems remains an ongoing challenge for researchers and developers [68].

Moreover there is the problem of lack of visual realism and the realism of the dynamics perception and interaction in XR experiences. As result there are physiological and psychological side effects called VR-sickness such as anxiety, post-traumatic stress, addiction, isolation, and mood changes that can arise from prolonged or excessive use of XR systems [10]. The human brain is highly sensitive to even the slightest unrealistic details, which can disrupt the sense of immersion and presence in VR experiences. Achieving high levels of visual fidelity and accurately simulating real-world

940

VOLUME 5, 2024

<!-- page 14 of 23 -->

IEEE IEEE Open Journal of the EEE Comnications Society Communications Society

dynamics is essential to enhance user immersion and provide a more compelling XR experience. Additionally, another significant challenge is related to human factors associated with XR technology [6]. In fact, human factors such as comfort, ergonomics, and ease usability play a crucial role in user acceptance and adoption of XR devices [9]. It is important to design XR systems that prioritize user comfort and minimize physical discomfort during prolonged use. Maximizing the appearance of reality in VR environments remains an ongoing challenge.

Some studies have focused on the potential of combining transcranial direct current stimulation (tDCS) with VR to recover cybersickness [78], reduce motor impairment, and enhance the therapeutic effects by leveraging the benefits of both modalities [79].

## 2) CONTEXT-AWARE INTERACTION AND COLLABORATION

Interaction and collaboration play a pivotal role in XR coupled with DT environments, leveraging data from the DT and harnessing edge/cloud resources. To achieve efficient optimization, it is essential to distribute tasks by performing simpler operations on the edge whereas offloading complex operations to the cloud [28]. This includes investigating methodologies, algorithms, and frameworks that enable realtime collaborative design reviews, virtual prototyping, and simulation-based analysis in resource-constrained edge/cloud environments. Researchers can focus on developing intelligent interaction techniques that adapt to the user’s context, facilitating seamless collaboration experiences in resourceconstrained environments.

These intelligent interaction techniques enable various forms of collaboration, including human-machine-robot collaboration and remote collaboration scenarios [50]. This will be essential for XR to be effective in Industry 5.0. By leveraging the capabilities of the XR and DT technologies, researchers can create immersive training simulations that allow users to engage in realistic training scenarios. Utilizing collaborative work and design platforms that leverage XR coupled with DT to enable remote collaboration, design reviews, and immersive team interactions. These platforms facilitate distributed teamwork, allowing users to collaborate in real-time regardless of their physical locations. Furthermore, augmented telepresence experiences can be developed, enabling individuals to virtually participate in remote locations and interact with their surroundings as if they were physically present.

The potential research directions aim to contribute to the advancement of multi-robot collaboration, Industry 5.0 applications, and the effective integration of humans and robots in collaborative environments [98]. Researchers have the opportunity to explore decentralized approaches, enabling robots to dynamically allocate tasks and collaborate autonomously [97]. Advanced algorithms merit investigation to enhance the efficiency and coordination of multi-robot systems across diverse environments [99], [100]. Moreover,

there is a need to explore strategies for the seamless integration of robots into workplaces, addressing challenges related to employee collaboration, acceptance, and productivity. The development of collaborative algorithms and techniques is crucial, facilitating efficient data synchronization, conflict resolution, and real-time collaboration among multiple users interacting with XR and DT systems [77]. These approaches facilitate seamless collaboration and ensure consistency and accuracy of shared information in XR resource-constrained environments.

## 3) EFFICIENT RESOURCE MANAGEMENT

This is another important potential research area, focused on developing efficient resource optimization and allocation strategies for XR coupled with DT in resource-constrained edge/cloud environments [71]. This involves exploring techniques to effectively utilize computing resources, network bandwidth, minimize latency, reduce energy consumption, and storage capacity to ensure seamless XR experiences whereas minimizing resource consumption [30]. This area is vital for ensuring better QoS and therefore more effective QoE.

Channel reservation and bandwidth are imperative for ensuring the efficiency of XR coupled with DT [93]. This involves optimizing channel allocation to improve resource utilization. The prospect of enhancing QoS in mobile communications deployments using High Altitude Platforms (HAPs) is on the horizon [94].

Serverless Computing, with its inherent scalability, costefficiency, and event-driven architecture, emerges as a compelling solution. This architecture accommodates the dynamic computational demands of real-time data processing and rendering in XR applications. Moreover, its ability to deploy functions near the edge minimizes latency, a critical factor in ensuring a responsive user experience. In parallel, the adoption of Federated Clouds holds promise for addressing challenges in distributed processing, data privacy, security, and interoperability [28]. By distributing computing tasks across multiple cloud providers or data centers, Federated Clouds facilitate efficient processing and analysis of distributed datasets in XR with DT applications.

In resource-constrained environments, future research should investigate energy optimization techniques, aiming to reduce the energy consumption of XR devices and edge/cloud platforms [44]. This can involve developing energy-aware algorithms, power-saving mechanisms, and intelligent energy management approaches to prolong the battery life and improve the sustainability of XR applications.

## 4) DATA TYPE MANAGEMENT AND DATA PROCESSING

XR applications generate a diverse range of data types, including visual, audio, haptic and textual data [3]. Visual data encompasses the visual elements of the XR experience, such as 2D/3D models, textures, colors, and lighting [74]. Examples include virtual objects, environments, and visual

VOLUME 5, 2024

941

<!-- page 15 of 23 -->

KAMDJOU et al.: RESOURCE-CONSTRAINED XR OPERATED WITH DT IN IIoT

effects that immerse users in virtual or augmented realities [4]. Audio data refers to the sound elements in XR applications, including spatial audio, background music, voiceovers, and sound effects. Examples include realistic 2D/3D audio that enhances the immersive experience and provides directional audio cues. Haptic data feedback involves the sense of touch and physical sensations in XR interactions. Examples include vibrations, force feedback, or pressure applied to the user’s haptic devices or controllers to simulate the sense of touch or texture in virtual objects. Textual data encompasses any textual information presented in XR applications, such as instructions, labels, menus, or dialogue boxes. Examples include text overlays, subtitles, or captions that provide additional information or guidance to the user.

Research efforts can focus on designing adaptive data processing techniques that efficiently handle and prioritize different data types based on their relevance and importance to the XR experience. This can help optimize resource utilization and improve the overall performance of XR applications.

As a matter of fact, nowadays, data is the common factor to all new technologies in new generation industry [81]. Further, data is an integral part of humanity. According to IDC FutureScape [2], data volumes have grown exponentially, and the number of digital bits can be comparable to the number of stars in the universe. Of late, Big Data processing and visualization has become economically more profitable for companies from the point of view of the revenue generated compared to the cost of acquisition. As a result, developing efficient coding schemes specifically tailored for XR-DT data transmission in edge/cloud environments is another promising research direction. These coding schemes can improve the data compression, data fusion, data transmission, data decoding and visualization of XR content, allowing for reduced bandwidth requirements and enhanced streaming performance and hence QoS [9], [82].

The recent surge in XR data processing research has unveiled innovative solutions that address critical challenges and redefine the landscape of immersive technologies. A notable breakthrough is semantic data compression [83]. This solution maintains high resolution by transmitting motion keypoints. To tackle transmission errors, a new semantic error detector is integrated, including expected false-positive error probability and distance tail uplift ratio [87], and improving the efficiency of semantic wireless communications. In the realm of volumetric video delivery, an AI-powered compression and semantic-aware transmission method is envisioned [84]. Wireless semantic delivery focuses on high-performance feature extraction and semantic recovery, significantly reducing compression time and communication latency for efficient and reliable XR delivery [85], [86], [88]. These innovative solutions bear the promise of shaping the landscape of the next generation of communication networks, paving the way for

exponential-scale reductions in traffic volumes dedicated to the synchronization of XR-DT.

## 5) DATA PRIVACY, SECURITY AND INTEGRITY

As XR involves the exchange of sensitive data and interactions with virtual representations of real-world entities, ensuring security and privacy becomes a crucial challenge. This concern measures to be taken to ensure that data is not intercepted/modified by unauthorized users during storage and its transmission over the network. The current security strategies for XR are categorized into five classes input protection, output protection, data access protection, interaction protection, device protection and interaction protection. The security strategy needs to consider privacy for social network data and privacy for XR system objects [35]. Some widely used methods are data encryption, authentication, watermarking, blockchain technologies, etc.

Future research directions should address security challenges, including secure data transmission, authentication, access control, and privacy preservation techniques. This involves exploring new encryption algorithms, secure communication protocols, and privacy-enhancing technologies to protect user data and maintain the data confidentiality and integrity of XR applications. Researcher can investigate encryption and security protocols to balance the transparency of blockchain with data privacy concerns in XR-enhanced DT environments. Research scalability solutions for public blockchain networks to enhance processing times and energy efficiency, particularly crucial for optimal XR experiences. Develop robust privacy frameworks that ensure secure data sharing and collaboration in XR spaces.

## 6) DATA-DRIVEN APPROACHES

Data-driven approaches is to collect, analyze and visualize data from XR applications to understand the performance characteristics and interdependencies [8]. Use this data is use-full to inform the development of the performance model and identify areas for optimization [68].

Nowadays the existing data visualisation methods, techniques and tools are still not flexible enough to effectively capture valuable information in the most efficient way possible. Beyond the effectiveness of the proposed methods, there are among others human perception and cognitive limitations. The method will be based on Gestalt psychology, which suggests that people tend to perceive the world as an ordered holistic configuration rather than as constituent fragments (e.g., a person first perceives the whole and can subsequently identify the isolated elements as part of the whole). A perspective solution can be performed as a combination of multidisciplinary data processing techniques and methods to enable rapid exploration of all data for improving benefits in terms of decision-making, precise correlations between product/sales and customer profiles/users.

The complexity of Big Data analysis presents an undeniable challenge. Many companies and open-source projects are performing predictive analysis of the future of Big Data

942

VOLUME 5, 2024

<!-- page 16 of 23 -->

IEEE IEEE Open Journal of the EEE Comnications Society Communications Society

via Visualization using AI + XR based on the understandings of human perception.

Real-time data synchronization between the XR environment and its DT counterpart in resource-constrained settings is a major challenge these days. This ensures that any changes or updates in the physical environment are accurately reflected in the virtual environment, enabling precise and up-to-date representations of the real world in XR applications. Thus, efficient data compression and transmission techniques can significantly contribute to XR coupled with DT in resource-constrained edge/cloud environments. These techniques aim to reduce the size of XR data and DT information without compromising their quality and fidelity. By effectively compressing and transmitting data, these techniques can minimize bandwidth requirements, reduce latency, and improve the overall responsiveness of XR applications, enabling them to operate smoothly in resourceconstrained settings.

Another contribution could be to develop collaborative computing techniques that enable concurrent editing, sharing, and visualization of XR data and DT information among multiple users. These techniques ensure seamless collaboration and coordination in resource-constrained environments, enhancing productivity and decision-making.

## 7) EQUIPMENT COSTS

XR is a promising technology that holds great potential for the future. Unfortunately, one of the challenges associated with XR is that the solutions leveraging these technologies often demand specialized high-performance computing platforms, which can impact the cost-benefit balance [75]. Thus, a potential area of research is to tackle the cost barrier associated with XR equipment systems. Currently, HMDs that provide an acceptable user experience can be quite expensive, ranging from \$300 to \$450,000. Additionally, these HMDs require computationally powerful PCs to support the immersive XR experience, which further adds to the cost. This affordability issue limits the accessibility of XR technology to a wider audience.

Therefore, an important research direction is to develop cost-effective solutions that make XR hardware more affordable and accessible to the general public. This can involve exploring alternative device designs that reduce production costs without compromising the user experience. It may also involve investigating lightweight, standalone XR devices that do not rely on high-end PCs, enabling users to enjoy XR experiences without the need for expensive hardware.

## 8) ITERATIVE DEVELOPMENT PROCESS

This consist to adopt an iterative development process where each discipline contributes their optimization techniques and metrics. Work towards establishing standards for XR platforms to ensure interoperability across diverse systems [77]. Collaborate with industry stakeholders to create a unified framework for XR development, enabling seamless integration and communication. The model evolves and

improves through iterative feedback and refinement from all disciplines involved.

Developing context-aware interaction models can signifi cantly contribute to XR optimization model. These models consider the context of the user, the physical environment, and the DT simulation to enable more intuitive and immersive interactions. By incorporating context-awareness, such as spatial understanding, object recognition, and user preferences, these models can enhance the realism and usability of XR applications, making them more effective in resource-constrained settings.

Edge intelligence, also known as distributed AI, focuses on deploying AI algorithms and models at the edge devices. It enables local processing and decision-making, reducing the dependency on cloud resources and improving responsiveness in resource-constrained environments. By deploying edge intelligence techniques, XR applications can leverage real-time data analysis and inference, enhancing the overall performance and capabilities of the system.

Researchers can contribute to the field by developing intelligent adaptive rendering techniques. These techniques can dynamically adjust the level of detail, rendering quality, and content streaming based on the available resources and network conditions, ensuring optimal performance and visual fidelity whereas operating within resource constraints.

Developing adaptive resource allocation algorithms can contribute to XR in resource-constrained environments. These algorithms can intelligently allocate computational resources, network bandwidth, and storage capacity based on the dynamic demands of XR with DT simulations. By optimizing resource utilization and ensuring efficient resource allocation, these algorithms can enhance the performance and scalability of XR applications in resource-constrained environments.

Energy-efficient rendering and display techniques can be a valuable contribution to XR coupled with DT in resourceconstrained edge/cloud environments. These techniques aim to reduce the computational and energy requirements of rendering XR content, optimizing the energy consumption of XR devices. By employing advanced rendering algorithms, display technologies, and power-saving mechanisms, and optimization algorithms to extend battery life of XR devices and improve the energy the overall efficiency of XR applications in resource-constrained environments.

Another avenue is to develop intuitive authoring tools that empower users without technical expertise to customize their XR experiences is crucial. User-friendly interfaces and dragand-drop functionalities can enable users to rearrange virtual objects, adjust settings, and personalize their interactions, enhancing adaptability and reconfigurability. Providing a range of customization options, such as object scaling, color customization, and spatial layout adjustments, can further enhance flexibility.

Advancements in sensor technologies, such as motion tracking, eye tracking, depth sensing, and environmental sensing, improve the accuracy and responsiveness of XR

VOLUME 5, 2024

943

<!-- page 17 of 23 -->

KAMDJOU et al.: RESOURCE-CONSTRAINED XR OPERATED WITH DT IN IIoT

systems. These sensors enable precise tracking of user movements, object interactions, and environmental conditions, enhancing the realism and interactivity of XR experiences. Integrating haptic feedback and multi-sensory cues, such as touch, vibration, and spatial audio, can enhance the perception and interaction realism in XR environments [78]. By providing users with tactile feedback and multi-modal sensory inputs that align with their virtual interactions, the sense of presence and immersion can be significantly enhanced, making the XR experience more believable and engaging.

## 9) EXPLAINABLE, ETHICAL, SOCIAL AND ECO-FRIENDLY IMPLICATIONS OF AI

AI and ML technologies play a crucial role in optimizing XR coupled with DT in resource-constrained environments [48]. By leveraging AI and ML algorithms, researchers can develop intelligent resource allocation strategies, adaptive rendering techniques, and context-aware interaction models. These technologies enable efficient use of resources, personalized experiences, and intelligent decision-making in XR applications.

As AI systems become more complex and pervasive, there is a growing need for transparency and explainability in their decision-making processes. The development of robust and explainable ML models is another potential contribution area. Future research should concentrate on developing Explainable Artificial Intelligence (XAI) techniques that can provide understandable explanations for AI/ML models’ predictions and decisions. This includes exploring methods such as rule-based explanations, feature importance analysis, and model-agnostic interpretability approaches. Understanding the inner workings of AI models will not only increase trust and adoption but also enable users to identify biases, potential errors, or unethical behavior.

As AI technologies become more pervasive, it is crucial to address their ethical and social implications. Future research should delve into the ethical considerations of AI, including bias and fairness in algorithmic decision-making, accountability and transparency in AI systems, and the impact of AI on employment and societal structures. This research area should also explore policy and regulatory frameworks for governing AI technologies and ensuring their responsible and ethical use in XR applications. By examining the broader societal implications of AI, researchers can contribute to the development of ethical guidelines and policies that promote the responsible deployment and adoption of AI systems.

The integration of Green IIoT in the context of developing eco-friendly and sustainable XR and DT using AI presents a promising avenue for SMS. The deployment of XR technologies with a focus on environmental sustainability can significantly contribute to the creation of smarter, more efficient society. One of the key aspects involves leveraging IoT sensors and devices for real-time monitoring and management of resources such as energy, water, and waste [91].

## B. EMERGING TECHNOLOGIES FOR PERFORMANCE OPTIMIZATION

Technology evolves rapidly, and new challenges constantly arise as a result. Identifying these challenges enables researchers to develop solutions, adapt our strategies, and push the boundaries of what is possible. This fosters continuous improvement and propels technological advancements. The subsequent enumeration highlights emerging technologies developed to untangle optimization challenges within the XR in IIoT with DT.

## 1) 5G/6G NETWORKS

The high bandwidth and low latency of 5G/6G networks enable faster data transmission, reducing lag and improving real-time XR experiences [36]. This technology allows for seamless streaming of high-quality XR content and enables more responsive interactions.

However the integration of XR-coupled DT applications in edge/cloud brings about diverse requirements, particularly in terms of latency. These applications can be classified into six different levels based on their latency requirements, as depicted in Figure 8. It is crucial for the connection QoS to ensure that these latency levels are met to achieve effective QoE. However, in practice, it is not always the case that the QoS guarantees the required latency levels for these sensitive applications.

Despite the ongoing expansion of 5G networks, achieving seamless coverage in all areas is still challenge these days [57]. One of the main limitations of 5G in XR is the potential for network congestion and limited bandwidth. XR applications, especially those involving augmented reality and virtual reality, require high data throughput and low latency to deliver seamless and immersive experiences. However, the increased demand for bandwidth and the large amounts of data generated by XR applications can strain the 5G network, leading to congestion and reduced performance. Another limitation is the potential for higher latency of 5G, compared to wired connections. 5G may not provide the ultra-low latency required for certain XR applications, such as real-time interactive experiences or precise haptic feedback.

The development of 6G networks is currently underway, building upon the advancements of 5G technology. 6G is ultra-low latency, further reducing the delay between devices and the network [21]. With latency on the order of microseconds, 6G will enable real-time, mission-critical applications that demand immediate responsiveness. SMS will benefit from instantaneous communication, enabling precise control and coordination in time-sensitive environments. This will pave the way for highly immersive and data-intensive applications, such as holographic communication, real-time 8K/16K video streaming, and high-fidelity virtual reality experiences [46]. One potential contribution of 6G to XR is the significant improvement in bandwidth and data transmission speeds [22]. With faster and more reliable connections, XR applications can deliver higher-resolution

944

VOLUME 5, 2024

<!-- page 18 of 23 -->

ComSoc Communications Society IEEE Open Journal of the

![Image block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p18_b2.png)

FIGURE 8. Network latency levels depending on the architecture and location.

visuals, complex virtual environments, and seamless realtime interactions. This will enable users to experience XR content with greater clarity, detail, and realism, enhancing their immersion and engagement [37].

## 2) CLOUD-FOG/EDGE COMPUTING AND IIOT INTEGRATION

By bringing computational resources closer to the XR devices, hybrid cloud-fog/edge computing reduces latency, enables real-time processing and responsive data processing in distributed systems [94]. This technology is particularly beneficial for XR applications that require quick response times and minimal latency, such as interactive gaming or remote collaboration.

By offloading computational tasks and data processing to edge devices and edge servers, these techniques can alleviate the burden on cloud resources and reduce latency. Edge intelligence techniques, such as ML and AI algorithms, can also enable real-time analysis and decision-making within the edge environment, enhancing the responsiveness and autonomy of XR applications.

The IIoT is poised to transform industries and daily life by connecting devices and enabling seamless communication and data exchange. As more devices become interconnected, advancements in IIoT infrastructure, edge computing, and sensor technologies will drive the development of smart cities, smart homes, and various IIoT-enabled services and applications.

The proliferation of IIoT devices and the demand for real-time, low-latency processing has led to the rise of edge computing. Future research should explore efficient integration strategies and architectures that enable seamless interaction and collaboration between edge devices and cloud resources. This includes addressing challenges such as resource allocation, task offloading, energy optimization, and data management in heterogeneous edge-cloud environments. By optimizing the utilization of edge resources and enhancing the coordination between edge and cloud components, researchers can unlock the full potential of IIoT applications.

## 3) ARTIFICIAL INTELLIGENCE (AI)

AI and ML continue to be at the forefront of emerging technologies [69]. Advancements in deep learning, reinforcement learning, federated learning and natural language processing are expected to drive innovations in various domains [69], [70]. AI-powered applications such as autonomous vehicles, virtual, DT assistants, and predictive analytics are anticipated to become more prevalent in the coming years [71], [72].

AI and ML techniques can optimize various aspects of XR performance [73]. For example, AI algorithms can be used for real-time rendering optimization, adaptive streaming, and predictive analytics to anticipate user interactions and enhance XR experiences. AI-driven optimizations are pivotal players in striking the ideal balance between latency and performance optimization. Explore ML and AI techniques can enhance the learning and decision-making capabilities in Human-robot collaborative XR system coupled with DT.

Federated learning has emerged as a promising approach for collaborative and privacy-preserving ML [20]. Research in this area should focus on developing efficient algorithms, protocols, and frameworks for federated learning that can address privacy challenges whereas ensuring highquality model aggregation and learning performance [29]. Techniques such as differential privacy, secure aggregation, and encryption methods can be explored to enhance privacy preservation in federated learning settings.

## 4) QUANTUM COMPUTING ALGORITHMS

Quantum computing represents a promising frontier in computing power. Quantum systems exploit the principles of superposition and entanglement to perform computations at an unprecedented scale. Contributions in this area can focus on developing novel quantum algorithms, error correction techniques, and quantum hardware advancements [80]. By pushing the boundaries of quantum computing, researchers can enable breakthroughs in areas such as optimization, cryptography, materials science, and drug discovery. Continued

VOLUME 5, 2024

945

<!-- page 19 of 23 -->

KAMDJOU et al.: RESOURCE-CONSTRAINED XR OPERATED WITH DT IN IIoT

advancements in quantum computing will pave the way for solving complex problems that are currently intractable for classical computers.

Research in this area should focus on developing quantum algorithms and applications that can harness the power of quantum computing. Areas such as quantum machine learning, quantum cryptography, and quantum simulation offer vast opportunities for exploration. Additionally, research should also investigate methods for error correction, noise mitigation, and scalability to make quantum computing more practical and accessible.

## 5) BLOCKCHAIN TECHNOLOGY

Best known for its association with cryptocurrencies like Bitcoin, Blockchain has far-reaching potential beyond digital currencies [52], [56]. Its decentralized and secure nature makes it suitable for applications such as supply chain management, identity verification, and smart contracts. Ongoing research and development efforts are expected to enhance scalability, privacy, and interoperability of blockchain systems [20].

Integrating XR with decentralized technologies and blockchain in the context of DT collaboration for SMS introduces multifaceted challenges. Scalability concerns arise, particularly in public blockchain networks, impacting processing times and energy efficiency, essential for optimal XR experiences. Achieving interoperability across diverse XR platforms poses another hurdle, necessitating standardization. Balancing transparency inherent in blockchain with data privacy in XR-enhanced DT demands sophisticated encryption. Sustainability considerations, aligning with eco-friendly smart cities, and navigating complex regulatory landscapes add layers of intricacy, emphasizing the need for a holistic approach to ensure the success of XR, decentralization, and blockchain in SMS [92].

This technology offers decentralized and secure data storage and sharing capabilities, which can be valuable for XR coupled with DT in resource-constrained environments [35]. It ensures data integrity, privacy, and transparency, enabling secure transactions, authentication, and collaboration in XR applications [49]. Blockchain can be leveraged to establish trust and enable secure interactions between XR devices, DT platforms, and other stakeholders in resource-constrained edge/cloud environments [50].

## VI. CONCLUSION AND FUTURE WORK

Industry 4.0 presents a transformative approach to enhance traditional industries through the integration of advanced technologies. The combination of IoT, big data analytics, AI/ML, edge/cloud computing, robotics, and XR enables the development of smart factories and processes. Looking ahead, Industry 5.0 emphasizes the collaboration between humans and machines, incorporating technologies such as IoE, HMC, and cognitive computing.

However, when it comes to eXtended Reality (XR) which includes AR and VR technologies in Smart Manufacturing

System (SMS), there are performance limitations that need to be addressed. Achieving a high-quality immersive experience remains a significant challenge. The lack of flexibility in Human-Computer Interaction is a primary challenge, as the ideal devices that cater to user characteristics and uncertainties are not yet available.

Nonetheless, the integration of XR with Digital Twin (DT) holds great potential to enable real-time monitoring, predictive maintenance, and optimization of SMS in futur industry. There are numerous research areas and potential applications that highlight the significance of XR coupled with DT. This focus on addressing the limitations of humancomputer interaction in XR, developing lightweight and accurate devices, improving stereoscopic viewing angles, and ensuring sufficient brightness for outdoor use. Additionally, further exploration of emerging technologies and their integration, along with advancements in 5G/6G networks, AI/ML, Quantum computing, Edge/cloud Computing, IIoT, and blockchain offer significant potential for advancing XR environments. These technologies provide the necessary architecture infrastructure, processing computing, intelligence, and security to enable immersive experiences, real-time synchronization, resource optimization, and secure collaborative workflow in XR applications operating with DT in resource-constrained SMS.

Future research directions should focus on addressing the identified gaps and challenges. Cloud-fog/edge orchestration techniques can enhance XR experiences, particularly in scenarios where real-time with low latency and HPC are required. Collaborative approach and HPC computing are crucial aspects that need to be explored further to enable seamless real-time XR collaboration between humans, robots, machines, and DT. Additionally, the development of cost-effective XR devices accessible to a wider audience will broaden the adoption and impact of XR technologies. By leveraging emerging technologies and considering humancomputer interaction requirements, researchers and industry professionals can work towards optimizing the performance of XR systems in resource-constrained environments, thereby unlocking the full potential of smart factories and collaborative human-machine interactions in SMS coupled with DT.

## REFERENCES

[1] W. Fang, L. Zheng, H. Deng, and H. Zhang, “Real-time motion tracking for mobile augmented/virtual reality using adaptive visual-inertial fusion,” Sensors, vol. 17, no. 5, p. 1037, 2017, doi: [10.3390/s17051037](http://dx.doi.org/10.3390/s17051037).

[2] L. Eriksen et al., “IDC futurescape: Worldwide future of operations 2023 predictions,” IDC Corp., Needham MA, USA, document #U.S.48669222, 2022.

[3] V. Havard, M. Sahnoun, B. Bettayeb, D. Fabrice, and D. Baudry, “Data architecture and model design for industry 4.0 components integration in cyber-physical production systems,” Proc. Inst. Mech. Eng. B, J. Eng. Manuf., vol. 235, no. 14, pp. 2338–2349, 2020, doi: [10.1177/0954405420979463](http://dx.doi.org/10.1177/0954405420979463).

[4] M. Dallel, V. Havard, Y. Dupuis, and D. Baudry, “Digital twin of an industrial workstation: A novel method of an auto-labeled data generator using virtual reality for human action recognition in the context of human–robot collaboration,” Eng. Appl. Artif. Intell., vol. 118, pp. 2338–2349, Feb. 2023, doi: [10.1016/j.engappai.2022.105655](http://dx.doi.org/10.1016/j.engappai.2022.105655).

946

VOLUME 5, 2024

<!-- page 20 of 23 -->

ComSoc Communications Society IEEE Open Journal of the

[5] M. Farshid, J. Paschen, T. Eriksson, and J. Kietzmann, “Go boldly! Explore augmented reality (AR), virtual reality (VR), and mixed reality (MR) for business,” Bus. Horizons, vol. 61, no. 5, pp. 657–663, 2018, doi: [10.1016/j.bushor.2018.05.009](http://dx.doi.org/10.1016/j.bushor.2018.05.009).

[6] F. Longo, A. Padovano, and S. Umbrello, “Value-oriented and ethical technology engineering in industry 5.0: A human-centric perspective for the design of the factory of the future,” Appl. Sci., vol. 10, no. 12, p. 4182, 2020, doi: [10.3390/app10124182.](http://dx.doi.org/10.3390/app10124182)

[7] L. A. Cardenas-Robledo, O. Hernandez-Uribe, C. Reta, and J. Antonio Cantoral-Ceballos, “Extended reality applications in industry 4.0—A systematic literature review,” Telemat. Inform., vol. 73, Sep. 2022, Art. no. 101863, doi: [10.1016/j.tele.2022.101863.](http://dx.doi.org/10.1016/j.tele.2022.101863)

[8] J. Leng, D. Wang, W. Shen, X. Li, Q. Liu, and X. Chen, “Digital twins-based smart manufacturing system design in industry 4.0: A review,” J. Manuf. Syst., vol. 60, pp. 119–137, Jul. 2021, doi: [10.1016/j.jmsy.2021.05.011.](http://dx.doi.org/10.1016/j.jmsy.2021.05.011)

[9] H. Takagi, “Interactive evolutionary computation: Fusion of the capabilities of EC optimization and human evaluation,” Proc. IEEE, vol. 89, no. 9, pp. 1275–1296, Sep. 2001, doi: [10.1109/5.949485.](http://dx.doi.org/10.1109/5.949485)

[10] C. Keighrey, R. Flynn, S. Murray, and N. Murray, “A physiologybased QoE comparison of interactive augmented reality, virtual reality and tablet-based applications,” IEEE Trans. Multimedia, vol. 21, pp. 333–341, 2021, doi: [10.1109/TMM.2020.2982046.](http://dx.doi.org/10.1109/TMM.2020.2982046)

[11] M. A. Khan et al., “A survey on mobile edge computing for video streaming: Opportunities and challenges,” IEEE Access, vol. 10, pp. 120514–120550, 2022, doi: [10.1109/ACCESS.2022.3220694.](http://dx.doi.org/10.1109/ACCESS.2022.3220694)

[12] V. Ján, B. Lukás, R. Oliver, S. Dana, M. Martin, and L. Milan, “The digital twin of an industrial production line within the industry 4.0 concept,” in Proc. 21st Int. Conf. Process Control (PC), 2017, pp. 258–262, doi: [10.1109/PC.2017.7976223.](http://dx.doi.org/10.1109/PC.2017.7976223)

[13] N. Bazmohammadi et al., “Microgrid digital twins: Concepts, applications, and future trends,” IEEE Access, vol. 10, pp. 2284–2302, 2022, doi: [10.1109/ACCESS.2021.3138990.](http://dx.doi.org/10.1109/ACCESS.2021.3138990)

[14] L. Li, S. Aslam, A. Wileman, and S. Perinpanayagam, “Digital twin in aerospace industry: A gentle introduction,” IEEE Access, vol. 10, pp. 9543–9562, 2022, doi: [10.1109/ACCESS.2021.3136458.](http://dx.doi.org/10.1109/ACCESS.2021.3136458)

[15] S. Kar, A. K. Kar, and M. P. Gupta, “Industrial Internet of Things and emerging digital technologies–modeling professionals’ learning behavior,” IEEE Access, vol. 9, pp. 30017–30034, 2021, doi: [10.1109/ACCESS.2021.3059407](http://dx.doi.org/10.1109/ACCESS.2021.3059407).

[16] M. J. W. Lee, S. Nikolic, P. J. Vial, C. H. Ritz, W. Li, and T. Goldfinch, “Enhancing project-based learning through student and industry engagement in a video-augmented 3-D virtual trade fair,” IEEE Trans. Educ., vol. 59, no. 4, pp. 290–298, Nov. 2016, doi: [10.1109/TE.2016.2546230](http://dx.doi.org/10.1109/TE.2016.2546230).

[17] J. Pirker, E. Loria, S. Safikhani, A. Künz, and S. Rosmann, “Immersive virtual reality for virtual and digital twins: A literature review to identify state of the art and perspectives,” in Proc. IEEE Conf. Virtual Real. 3D User Interfaces Abstracts Workshops (VRW), 2022, pp. 114–115, doi: [10.1109/VRW55335.2022.00035](http://dx.doi.org/10.1109/VRW55335.2022.00035).

[18] X. Ran, H. Chen, X. Zhu, Z. Liu, and J. Chen, “Deepdecision: A mobile deep learning framework for edge video analytics,” in Proc. IEEE INFOCOM, 2018, pp. 1421–1429, doi: [10.1109/INFOCOM.2018.8485905](http://dx.doi.org/10.1109/INFOCOM.2018.8485905).

[19] L. Lin, X. Liao, H. Jin, and P. Li, “Computation offloading toward edge computing,” Proc. IEEE, vol. 107, no. 8, pp. 1584–1607, Aug. 2019, doi: [10.1109/JPROC.2019.2922285](http://dx.doi.org/10.1109/JPROC.2019.2922285).

[20] Y. Lu, X. Huang, K. Zhang, S. Maharjan, and Y. Zhang, “Low-latency federated learning and blockchain for edge association in digital twin empowered 6G networks,” IEEE Trans. Ind. Informat., vol. 17, no. 7, pp. 5098–5107, Jul. 2021, doi: [10.1109/TII.2020.3017668](http://dx.doi.org/10.1109/TII.2020.3017668).

[21] W. Jiang, B. Han, M. A. Habibi, and H. D. Schotten, “The road towards 6G: A comprehensive survey,” IEEE Open J. Commun. Soc., vol. 2, pp. 334–366, 2021, doi: [10.1109/OJCOMS.2021.3057679](http://dx.doi.org/10.1109/OJCOMS.2021.3057679).

[22] H. Viswanathan and P. E. Mogensen, “Communications in the 6G era,” IEEE Access, vol. 8, pp. 57063–57074, 2020, doi: [10.1109/ACCESS.2020.2981745](http://dx.doi.org/10.1109/ACCESS.2020.2981745).

[23] K. Dolui and S. K. Datta, “Comparison of edge computing implementations: Fog computing, cloudlet and mobile edge computing,” in Proc. Global Internet Things Summit (GIoTS), 2017, pp. 1–6, doi: [10.1109/GIOTS.2017.8016213](http://dx.doi.org/10.1109/GIOTS.2017.8016213).

[24] R. Mekuria, K. Blom, and P. Cesar, “Design, implementation, and evaluation of a point cloud codec for tele-immersive video,” IEEE Trans. Circuits Syst. Video Technol., vol. 27, no. 4, pp. 828–842, Apr. 2017, doi: [10.1109/TCSVT.2016.2543039](http://dx.doi.org/10.1109/TCSVT.2016.2543039).

[25] X. Qiao, P. Ren, S. Dustdar, L. Liu, H. Ma, and J. Chen, “Web AR: A promising future for mobile augmented reality-state of the art, challenges, and insights,” Proc. IEEE, vol. 107, no. 4, pp. 651–666, Apr. 2019, doi: [10.1109/JPROC.2019.2895105](http://dx.doi.org/10.1109/JPROC.2019.2895105).

[26] A. Ceselli, M. Premoli, and S. Secci, “Mobile edge cloud network design optimization,” IEEE/ACM Trans. Netw., vol. 25, no. 3, pp. 1818–1831, Jun. 2017, doi: [10.1109/TNET.2017.2652850](http://dx.doi.org/10.1109/TNET.2017.2652850).

[27] M. Shafi et al., “5G: A tutorial overview of standards, trials, challenges, deployment, and practice,” IEEE J. Sel. Areas Commun., vol. 35, no. 6, pp. 1201–1221, Jun. 2017, doi: [10.1109/JSAC.2017.2692307](http://dx.doi.org/10.1109/JSAC.2017.2692307).

[28] M. Chen and Y. Hao, “Task offloading for mobile edge computing in software defined ultra-dense network,” IEEE J. Sel. Areas Commun., vol. 36, no. 3, pp. 587–597, Mar. 2018, doi: [10.1109/JSAC.2018.2815360](http://dx.doi.org/10.1109/JSAC.2018.2815360).

[29] W. Sun, S. Lei, L. Wang, Z. Liu, and Y. Zhang, “Adaptive federated learning and digital twin for Industrial Internet of Things,” IEEE Trans. Ind. Informat., vol. 17, no. 8, pp. 5605–5614, Aug. 2021, doi: [10.1109/TII.2020.3034674](http://dx.doi.org/10.1109/TII.2020.3034674).

[30] A. Al-Shuwaili and O. Simeone, “Energy-efficient resource allocation for mobile edge computing-based augmented reality applications,” IEEE Wireless Commun. Lett., vol. 6, no. 3, pp. 398–401, Jun. 2017, doi: [10.1109/LWC.2017.2696539](http://dx.doi.org/10.1109/LWC.2017.2696539).

[31] Z. Ding, P. Fan, and H. V. Poor, “Impact of non-orthogonal multiple access on the offloading of mobile edge computing,” IEEE Wireless Commun. Lett., vol. 67, no. 1, pp. 375–390, Jan. 2019, doi: [10.1109/TCOMM.2018.2870894](http://dx.doi.org/10.1109/TCOMM.2018.2870894).

[32] M. Kamel, W. Hamouda, and A. Youssef, “Ultradense networks: A survey,” IEEE Commun. Surveys Tuts., vol. 18, no. 4, pp. 2522–2545, 4th Quart., 2016, doi: [10.1109/COMST.2016.2571730](http://dx.doi.org/10.1109/COMST.2016.2571730).

[33] D. Chatzopoulos, C. Bermejo, Z. Huang, and P. Hui, “Mobile augmented reality survey: From where we are to where we go,” IEEE Access, vol. 5, pp. 6917–6950, 2017, doi: [10.1109/ACCESS.2017.2698164](http://dx.doi.org/10.1109/ACCESS.2017.2698164).

[34] C. Gehrmann and M. Gunnarsson, “A digital twin based industrial automation and control system security architecture,” IEEE Trans. Ind. Informat., vol. 16, no. 1, pp. 669–680, Jan. 2020, doi: [10.1109/TII.2019.2938885](http://dx.doi.org/10.1109/TII.2019.2938885).

[35] A. Islam, M. Masuduzzaman, A. Akter, and S. Young Shin, “MR-block: A blockchain-assisted secure content sharing scheme for multi-user mixed-reality applications in Internet of Military Things,” in Proc. Int. Conf. Inf. Commun. Technol. Converg. (ICTC), 2020, pp. 407–411, doi: [10.1109/ICTC49870.2020.9289327](http://dx.doi.org/10.1109/ICTC49870.2020.9289327).

[36] L. Chettri and R. Bera, “A comprehensive survey on Internet of Things (IoT) toward 5G wireless systems,” IEEE Internet Things J., vol. 7, no. 1, pp. 16–32, Jan. 2020, doi: [10.1109/JIOT.2019.2948888](http://dx.doi.org/10.1109/JIOT.2019.2948888).

[37] M. Z. Chowdhury, M. Shahjalal, S. Ahmed, and Y. M. Jang, “6G wireless communication systems: Applications, requirements, technologies, challenges, and research directions,” IEEE Open J. Commun. Soc., vol. 1, no. 1, pp. 957–975, 2020, doi: [10.1109/OJCOMS.2020.3010270](http://dx.doi.org/10.1109/OJCOMS.2020.3010270).

[38] G. N. Schroeder, C. Steinmetz, R. N. Rodrigues, R. V. B. Henriques, A. Rettberg, and C. E. Pereira, “A methodology for digital twin modeling and deployment for industry 4.0,” Proc. IEEE, vol. 109, no. 4, pp. 556–567, Apr. 2021, doi: [10.1109/JPROC.2020.3032444](http://dx.doi.org/10.1109/JPROC.2020.3032444).

[39] L. U. Khan, W. Saad, D. Niyato, Z. Han, and C. S. Hong, “Digital-twin-enabled 6G: Vision, architectural trends, and future directions,” IEEE Commun. Mag., vol. 60, no. 1, pp. 74–80, Jan. 2022, doi: [10.1109/MCOM.001.21143](http://dx.doi.org/10.1109/MCOM.001.21143).

[40] C.-J. Wu et al., “Machine learning at Facebook: Understanding inference at the edge,” in Proc. IEEE Int. Symp. High Perform. Comput. Archit. (HPCA), 2019, pp. 331–344, doi: [10.1109/HPCA.2019.00048](http://dx.doi.org/10.1109/HPCA.2019.00048).

[41] K. Poularakis, J. Llorca, A. M. Tulino, I. Taylor, and L. Tassiulas, “Joint service placement and request routing in multi-cell mobile edge computing networks,” in Proc. IEEE INFOCOM, 2019, pp. 10–18, doi: [10.1109/INFOCOM.2019.8737385](http://dx.doi.org/10.1109/INFOCOM.2019.8737385).

VOLUME 5, 2024

947

<!-- page 21 of 23 -->

KAMDJOU et al.: RESOURCE-CONSTRAINED XR OPERATED WITH DT IN IIoT

[42] R. Cziva, C. Anagnostopoulos, and D. P. Pezaros, “Dynamic, latency-optimal vNF placement at the network edge,” in Proc. IEEE INFOCOM, 2018, pp. 693–701, doi: [10.1109/INFOCOM.2018.8486021](http://dx.doi.org/10.1109/INFOCOM.2018.8486021).

[43] L. Wang, L. Jiao, T. He, J. Li, and M. Mühlhäuser, “Service entity placement for social virtual reality applications in edge computing,” in Proc. IEEE INFOCOM, 2018, pp. 468–476, doi: [10.1109/INFOCOM.2018.8486411](http://dx.doi.org/10.1109/INFOCOM.2018.8486411).

[44] J. Xu, B. Palanisamy, H. Ludwig, and Q. Wang, “Zenith: Utility-aware resource allocation for edge computing,” in Proc. IEEE Int. Conf. Edge Comput. (EDGE), 2017, pp. 47–54, doi: [10.1109/IEEE.EDGE.2017.15](http://dx.doi.org/10.1109/IEEE.EDGE.2017.15).

[45] F. Jiang, K. Wang, L. Dong, C. Pan, W. Xu, and K. Yang, “Deeplearning-based joint resource scheduling algorithms for hybrid MEC networks,” IEEE Internet Things J., vol. 7, no. 7, pp. 6252–6265, Jul. 2020, doi: [10.1109/JIOT.2019.2954503](http://dx.doi.org/10.1109/JIOT.2019.2954503).

[46] V. Farhadi et al., “Service placement and request scheduling for data-intensive applications in edge clouds,” IEEE/ACM Trans. Netw., vol. 29, no. 2, pp. 779–792, Apr. 2021, doi: [10.1109/TNET.2020.3048613](http://dx.doi.org/10.1109/TNET.2020.3048613).

[47] Q. Liu, S. Huang, J. Opadere, and T. Han, “An edge network orchestrator for mobile augmented reality,” in Proc. IEEE INFOCOM, 2018, pp. 756–764, doi: [10.1109/INFOCOM.2018.8486241](http://dx.doi.org/10.1109/INFOCOM.2018.8486241).

[48] Y. Ma, Z. Wang, H. Yang, and L. Yang, “Artificial intelligence applications in the development of autonomous vehicles: A survey,” IEEE/CAA J. Automatica Sinica, vol. 7, no. 2, pp. 315–329, Mar. 2020, doi: [10.1109/JAS.2020.1003021](http://dx.doi.org/10.1109/JAS.2020.1003021).

[49] J. Leng et al., “Manuchain: Combining permissioned blockchain with a holistic optimization model as bi-level intelligence for smart manufacturing,” IEEE Trans. Syst., Man, Cybern., Syst., vol. 50, no. 1, pp. 182–192, Jan. 2020, doi: [10.1109/TSMC.2019.2930418](http://dx.doi.org/10.1109/TSMC.2019.2930418).

[50] P. Lin, Q. Song, F. R. Yu, D. Wang, and L. Guo, “Task offloading for wireless VR-enabled medical treatment with blockchain security using collective reinforcement learning,” IEEE Internet Things J., vol. 8, no. 21, pp. 15749–15761, Nov. 2021, doi: [10.1109/JIOT.2021.3051419](http://dx.doi.org/10.1109/JIOT.2021.3051419).

[51] M. Filer, M. Cantono, A. Ferrari, G. Grammel, G. Galimberti, and V. Curri, “Multi-vendor experimental validation of an open source QoT estimator for optical networks,” J. Lightw. Technol., vol. 36, no. 15, pp. 3073–3082, Aug. 1, 2018, doi: [10.1109/JLT.2018.2818406](http://dx.doi.org/10.1109/JLT.2018.2818406).

[52] S. Rathore, J. H. Park, and H. Chang, “Deep learning and blockchain-empowered security framework for intelligent 5Genabled IoT,” IEEE Access, vol. 9, pp. 90075–90083, 2021, doi: [10.1109/ACCESS.2021.3077069](http://dx.doi.org/10.1109/ACCESS.2021.3077069).

[53] H. Yang, A. Alphones, Z. Xiong, D. Niyato, J. Zhao, and K. Wu, “Artificial-intelligence-enabled intelligent 6G networks,” IEEE Netw., vol. 34, no. 6, pp. 272–280, Nov./Dec. 2020, doi: [10.1109/MNET.011.2000195](http://dx.doi.org/10.1109/MNET.011.2000195).

[54] J. Park, P. A. Chou, and J. -N. Hwang, “Rate-utility optimized streaming of volumetric media for augmented reality,” IEEE J. Emerg. Sel. Topics Circuits Syst., vol. 9, no. 1, pp. 149–162, Mar. 2019, doi: [10.1109/JETCAS.2019.2898622](http://dx.doi.org/10.1109/JETCAS.2019.2898622).

[55] A. A. Barakabitze et al., “Qoe management of multimedia streaming services in future networks: A tutorial and survey,” IEEE Commun. Surveys Tuts., vol. 22, no. 1, pp. 526–565, 1st Quart., 2020, doi: [10.1109/COMST.2019.2958784](http://dx.doi.org/10.1109/COMST.2019.2958784).

[56] C. Zhang, G. Zhou, H. Li, and Y. Cao, “Manufacturing blockchain of things for the configuration of a data and knowledge-driven digital twin manufacturing cell,” IEEE Internet Things J., vol. 7, no. 12, pp. 11884–11894, Dec. 2020, doi: [10.1109/JIOT.2020.3005729](http://dx.doi.org/10.1109/JIOT.2020.3005729).

[57] H.-W. Kao and E. H.-K. Wu, “QoE sustainability on 5G and beyond 5G networks,” IEEE Wireless Commun., vol. 30, no. 1, pp. 118–125, Feb. 2023, doi: [10.1109/MWC.007.2200260](http://dx.doi.org/10.1109/MWC.007.2200260).

[58] A. Liu et al., “A survey on fundamental limits of integrated sensing and communication,” IEEE Commun. Surveys Tuts., vol. 24, no. 2, pp. 994–1034, 2nd Quart., 2022, doi: [10.1109/COMST.2022.3149272](http://dx.doi.org/10.1109/COMST.2022.3149272).

[59] L. U. Khan, Z. Han, W. Saad, E. Hossain, M. Guizani, and C. S. Hong, “Digital twin of wireless systems: Overview, taxonomy, challenges, and opportunities,” IEEE Commun. Surveys Tuts., vol. 24, no. 4, pp. 2230–2254, 4th Quart., 2022, doi: [10.1109/COMST.2022.3198273](http://dx.doi.org/10.1109/COMST.2022.3198273).

[60] L. Chang et al., “6G-enabled edge AI for metaverse: Challenges, methods, and future research directions,” J. Commun. Inf. Netw., vol. 7, no. 2, pp. 107–121, Jun. 2022. doi: [10.23919/JCIN.2022.9815195](http://dx.doi.org/10.23919/JCIN.2022.9815195).

[61] M. Abrar, U. Ajmal, Z. M. Almohaimeed, X. Gui, R. Akram, and R. Masroor, “Energy efficient UAV-enabled mobile edge computing for IoT devices: A review,” IEEE Access, vol. 9, pp. 127779–127798, 2021, doi: [10.1109/ACCESS.2021.3112104](http://dx.doi.org/10.1109/ACCESS.2021.3112104).

[62] E. Waisberg, J. Ong, and M. E. A. Masalkhi, “Apple vision pro and why extended reality will revolutionize the future of medicine,” Iris J. Med. Sci., vol. 193, pp. 531–532, Feb. 2024, doi: [10.1007/s11845-023-03437-z](http://dx.doi.org/10.1007/s11845-023-03437-z).

[63] E. Waisberg, J. Ong, N. Zaman, S. A. Kamran, A. G. Lee, and A. Tavakkoli, “Head-mounted dynamic visual acuity for G-transition effects during interplanetary spaceflight: Technology development and results from an early validation study,” Iris J. Med. Sci., vol. 93, no. 11, pp. 800–805, Nov. 2022, doi: [10.3357/AMHP.6092.2022](http://dx.doi.org/10.3357/AMHP.6092.2022).

[64] S.-M. Park and Y.-G. Kim, “A metaverse: Taxonomy, components, applications, and open challenges,” IEEE Access, vol. 10, pp. 4209–4251, 2022, doi: [10.1109/ACCESS.2021.3140175](http://dx.doi.org/10.1109/ACCESS.2021.3140175).

[65] H. Zhang, Q. Liu, X. Chen, D. Zhang, and J. Leng, “A digital twin-based approach for designing and multi-objective optimization of hollow glass production line,” IEEE Access, vol. 5, pp. 26901–26911, 2017, doi: [10.1109/ACCESS.2017.2766453](http://dx.doi.org/10.1109/ACCESS.2017.2766453).

[66] R. H. Guerra, R. Quiza, A. Villalonga, J. Arenas, and F. Castaño, “Digital twin-based optimization for ultraprecision motion systems with backlash and friction,” IEEE Access, vol. 7, pp. 93462–93472, 2019, doi: [10.1109/ACCESS.2019.2928141](http://dx.doi.org/10.1109/ACCESS.2019.2928141).

[67] A. Mahmood, Y. Hong, M. K. Ehsan, and S. Mumtaz, “Optimal resource allocation and task segmentation in IoT enabled mobile edge cloud,” IEEE Trans. Veh. Technol., vol. 70, no. 12, pp. 13294–13303, Dec. 2021, doi: [10.1109/TVT.2021.3121146](http://dx.doi.org/10.1109/TVT.2021.3121146).

[68] X. Min, W. Zhang, S. Sun, N. Zhao, S. Tang, and Y. Zhuang, “VPModel: High-fidelity product simulation in a virtual-physical environment,” IEEE Trans. Vis. Comput. Graph., vol. 25, no. 11, pp. 3083–3093, Nov. 2019, doi: [10.1109/TVCG.2019.2932276](http://dx.doi.org/10.1109/TVCG.2019.2932276).

[69] T. Ren et al., “Enabling efficient scheduling in largescale UAV-assisted mobile-edge computing via hierarchical reinforcement learning,” IEEE Internet Things J., vol. 9, no. 10, pp. 7095–7109, May 2022, doi: [10.1109/JIOT.2021.3071531.](http://dx.doi.org/10.1109/JIOT.2021.3071531)

[70] T.-V. Nguyen, N.-N. Dao, V. Dat Tuong, W. Noh, and S. Cho, “User-aware and flexible proactive caching using LSTM and ensemble learning in IoT-MEC networks,” IEEE Internet Things J., vol. 9, no. 5, pp. 3251–3269, Mar. 2022, doi: [10.1109/JIOT.2021.3097768.](http://dx.doi.org/10.1109/JIOT.2021.3097768)

[71] T. Liu et al., “Resource allocation in DT-assisted Internet of Vehicles via edge intelligent cooperation,” IEEE Internet Things J., vol. 9, no. 18, pp. 17608–17626, Sep. 2022, doi: [10.1109/JIOT.2022.3156100.](http://dx.doi.org/10.1109/JIOT.2022.3156100)

[72] K. K. Nguyen, T. Q. Duong, N. A. Vien, N.-A. Le-Khac, and L. D. Nguyen, “Distributed deep deterministic policy gradient for power allocation control in D2D-based V2V communications,” IEEE Access, vol. 7, pp. 164533–164543, 2019, doi: [10.1109/ACCESS.2019.2952411](http://dx.doi.org/10.1109/ACCESS.2019.2952411).

[73] M. Yan, B. Chen, G. Feng, and S. Qin, “Federated cooperation and augmentation for power allocation in decentralized wireless networks,” IEEE Access, vol. 8, pp. 48088–48100, 2020, doi: [10.1109/ACCESS.2020.2979323](http://dx.doi.org/10.1109/ACCESS.2020.2979323).

[74] R. Li and D. Xu, “Distribution of landscape architecture based on 3D images and virtual reality rationality study,” IEEE Access, vol. 8, pp. 140161–140170, 2020, doi: [10.1109/ACCESS.2020.3010097](http://dx.doi.org/10.1109/ACCESS.2020.3010097).

[75] A. Alnagrat, R. Che Ismail, S. Z. Syed Idrus, and R. M. A. Alfaqi, “A review of extended reality (XR) technologies in the future of human education: Current trend and future opportunity,” J. Human Centered Technol., vol. 1, no. 2, pp. 81–96, 2022, doi: [10.11113/humentech.v1n2.27](http://dx.doi.org/10.11113/humentech.v1n2.27).

[76] S. Barteit, L. Lanfermann, T. Bärnighausen, F. Neuhann, and C. Beiersmann, “Augmented, mixed, and virtual realitybased head-mounted devices for medical education: Systematic review,” JMIR Serious Games, vol. 9, no. 3, 2021, Art. no. e29080, doi: [10.2196/29080](http://dx.doi.org/10.2196/29080).

948

VOLUME 5, 2024

<!-- page 22 of 23 -->

ComSoc Communications Society IEEE Open Journal of the

[77] V. Havard, A. Courallet, D. Baudry, and H. Delalin, “Digital twin, virtual reality and OPCUA-based architecture for pedagogical scenarios in manufacturing and computer sciences curriculum,” in Proc. 13th Conf. Learn. Factories (CLF), 2023, pp. 1–6, doi: [10.2139/ssrn.4457032](http://dx.doi.org/10.2139/ssrn.4457032).

[78] G. Li et al., “Exploring the feasibility of mitigating VR-HMD-induced cybersickness using cathodal transcranial direct current stimulation,” in Proc. IEEE Int. Conf. Artif. Intell. Virtual Real. (AIVR), 2020, pp. 123–129, doi: [10.1109/AIVR50618.2020.00030](http://dx.doi.org/10.1109/AIVR50618.2020.00030).

[79] X. Yao et al., “Effects of transcranial direct current stimulation with virtual reality on upper limb function in patients with ischemic stroke: A randomized controlled trial,” J. Neuro Eng. Rehabil., vol. 17, p. 73, Jun. 2020, doi: [10.1186/s12984-020-00699-x](http://dx.doi.org/10.1186/s12984-020-00699-x).

[80] P. Lin, Q. Song, D. Wang, F. R. Yu, L. Guo, and V. C. M. Leung, “Resource management for pervasive-edge-computing-assisted wireless VR streaming in Industrial Internet of Things,” IEEE Trans. Ind. Informat., vol. 17, no. 11, pp. 7607–7617, Nov. 2021, doi: [10.1109/TII.2021.3061579](http://dx.doi.org/10.1109/TII.2021.3061579).

[81] E. Tagne et al., “A lossless distributed data compression and aggregation methods for low resources wireless sensors platforms,” Wireless Pers. Commun., vol. 128, pp. 621–643, Jan. 2023, doi: [10.1007/s11277-022-09970-x](http://dx.doi.org/10.1007/s11277-022-09970-x).

[82] E. T. Fute et al., “DDCA-WSN: A distributed data compression and aggregation approach for low resources wireless sensors networks,” Int. J. Wireless Inf. Netw., vol. 29, pp. 80–92, Jan. 2022, doi: [10.1007/s10776-021-00543-6](http://dx.doi.org/10.1007/s10776-021-00543-6).

[83] P. Jiang, C.-K. Wen, S. Jin, and G. Y. Li, “Wireless semantic communications for video conferencing,” IEEE J. Sel. Areas Commun., vol. 41, no. 1, pp. 230–244, Jan. 2023, doi: [10.1109/JSAC.2022.3221968](http://dx.doi.org/10.1109/JSAC.2022.3221968).

[84] Y. Zhu et al., “A semantic-aware transmission with adaptive control scheme for volumetric video service,” IEEE Trans. Multimedia, vol. 25, pp. 7160–7172, 2023, doi: [10.1109/TMM.2022.3217928](http://dx.doi.org/10.1109/TMM.2022.3217928).

[85] L. Xia et al., “WiserVR: Semantic communication enabled wireless virtual reality delivery,” In IEEE Wireless Commun., vol. 30, no. 2, pp. 32–39, Apr. 2023, doi: [10.1109/MWC.004.2200393](http://dx.doi.org/10.1109/MWC.004.2200393).

[86] S. Rezwan, H. Wu, J. A. Cabrera, G. T. Nguyen, M. Reisslein, and F. H. P. Fitzek, “cXR+ Voxel-based semantic compression for networked immersion,” IEEE Access, vol. 11, pp. 52763–52777, 2023, doi: [10.1109/ACCESS.2023.3279503](http://dx.doi.org/10.1109/ACCESS.2023.3279503).

[87] C. von Lengerke, A. Hefele, J. A. Cabrera, M. Reisslein, and F. H. P. Fitzek, “Beyond the bound: A new performance perspective for identification via channels,” IEEE J. Sel. Areas Commun., vol. 41, no. 8, pp. 2687–2706, Aug. 2023, doi: [10.1109/JSAC.2023.3288239](http://dx.doi.org/10.1109/JSAC.2023.3288239).

[88] S. Derebeyoglu, C. Deppe, and R. Ferrara, “Performance analysis of identification codes,” Entropy, vol. 22, no. 10, p. 1067, 2020, doi: [10.3390/e22101067](https://doi.org/10.3390/e22101067).

[89] V. Kuts, M. Singh, S. H. Alsamhi, D. Devine, and N. Murray, “Physical and virtual robotic cells in industry 4.0 towards industry 5.0: An XR-based conceptual framework,” in Proc. ASME Int. Mech. Eng. Congr. Expo., Feb. 2023, Art. no. V02BT02A022, doi: [10.1115/IMECE2022-95021](https://doi.org/10.1115/IMECE2022-95021).

[90] L. Perez, S. Rodriguez-Jimenez, N. Rodriguez, R. Usamentiaga, and D.F. Garcia, “Digital twin and virtual reality based methodology for multi-robot manufacturing cell commissioning,” Appl. Sci., vol. 10, no. 10, p. 3633, 2020, doi: [10.3390/app10103633](https://doi.org/10.3390/app10103633).

[91] F. A. Almalki et al., “Green IoT for Eco-friendly and sustainable smart cities: Future directions and opportunities,” Mobile Netw. Appl., vol. 28, pp. 178–202, Feb. 2023, doi: [10.1007/s11036-021-01790-w.](https://doi.org/10.1007/s11036-021-01790-w)

[92] R. Sahal, S. H. Alsamhi, S. H. Alsamhi, D. O’Shea, C. McCarthy, and M. Guizani, “Blockchain-empowered digital twins collaboration: Smart transportation use case,” Machines, vol. 9, no. 9, p. 193, 2021, doi: [10.3390/machines9090193](https://doi.org/10.3390/machines9090193).

[93] A. Nauman et al., “Empowering smart cities: High-altitude platforms based mobile edge computing and wireless power transfer for efficient IoT data processing,” Internet Things, vol. 24, Dec. 2023, Art. no. 100986, doi: [10.1016/j.iot.2023.100986](https://doi.org/10.1016/j.iot.2023.100986).

[94] D. Zhou, M. Sheng, J. Li, and Z. Han, “Aerospace integrated networks innovation for empowering 6G: A survey and future challenges,” IEEE Commun. Surveys Tuts., vol. 25, no. 2, pp. 975–1019, 2nd Quart., 2023, doi: [10.1109/COMST.2023.3245614](http://dx.doi.org/10.1109/COMST.2023.3245614).

[95] R. Tallat et al., “Navigating industry 5.0: A survey of key enabling technologies, trends, challenges, and opportunities,” IEEE Commun. Surveys Tuts., early access, Nov. 2, 2023, doi: [10.1109/COMST.2023.3329472](http://dx.doi.org/10.1109/COMST.2023.3329472).

[96] S. H. Alsamhi, A. Hawbani, N. Mohsen, S. Kumar, L. Porwol, and E. Curry, “SemCom for metaverse: Challenges, opportunities and future trends,” in Proc. 3rd Int. Conf. Comput. Inf. Technol., 2023, pp. 130–134, doi: [10.1109/ICCIT58132.2023.10273924](http://dx.doi.org/10.1109/ICCIT58132.2023.10273924).

[97] S. H. Alsamhi, A. A. F. Saif, E. Curry, S. Kumar, and A. Hawbani, “Autonomous multi-robot collaboration in virtual environments to perform tasks in industry 4.0,” in Proc. 2nd Int. Conf. Emerg. Smart Technol. Appl., 2022, pp. 1–7, doi: [10.1109/eSmarTA56775.2022.9935421](http://dx.doi.org/10.1109/eSmarTA56775.2022.9935421).

[98] A. Adel, “Future of industry 5.0 in society: Human-centric solutions, challenges and prospective research areas,” J. Cloud Comput., vol. 11, p. 40, Sep. 2022, doi: [10.1186/s13677-022-00314-5](https://doi.org/10.1186/s13677-022-00314-5).

[99] K. A. Demir, G. Döven, and B. Sezen, “Industry 5.0 and human– robot co-working,” Procedia Comput. Sci., vol. 158, pp. 688–695, Oct. 2019, doi: [10.1016/j.procs.2019.09.104](https://doi.org/10.1016/j.procs.2019.09.104).

[100] P. K. R. Maddikunta, “Industry 5.0: A survey on enabling technologies and potential applications,” J. Ind. Inf. Integr., vol. 26, Mar. 2022, Art. no. 100257, doi: [10.1016/j.jii.2021.100257](https://doi.org/10.1016/j.jii.2021.100257).

![Image block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p22_b26.png)

**HUGUES M. KAMDJOU** received the B.S. and M.S. degrees in mathematics and computer science, major on networks and distributed services, domain of science and technology from the Faculty of Science, University of Dschang in 2016, and the Ph.D. degree in computer science, major on networks and distributed services, speciality data compression and aggregation from the University of Dschang in 2022. From 2018 to 2020, he was a member of the Doctoral College of Central Africa and the Great Lakes “MathInBio” of the

Francophonie University Association. Since 2022, he has been a Researcher with CESI LINEACT. His research interests include digital twins, augmented reality, virtual reality, wireless sensor networks, internet of things, data compression and aggregation, uncertainty management, and belief function theory. He is an IPC Member and a reviewer in IEEE conferences.

![Image block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p22_b29.png)

**DAVID BAUDRY** received the Engineering Diploma (equivalent to M.Sc.) degree from the Ecole Nationale Supérieure d’Ingénieur, Caen, France, in 1999, and the Ph.D. degree in electronics from the University of Rouen, France, in 2005.

From 2000 to 2001, he was with SOPRA Group and was involved in software development. In 2001, he joined the Graduate Engineering School ESIGELEC, Rouen, France, where he was a Lecturer and the Deputy Head of the EMC Team of the ESIGELEC Research Institute (IRSEEM).

He was also in charge of the “mechatronic and electrical engineering” major in ESIGELEC. In 2010, he was titled to supervise research. In 2011, he joined the Graduate Engineering School CESI, Rouen, France, where he is currently the Head of the CESI LINEACT Research Team in computer sciences and industrial engineering. From 2015 to 2020, he was also the Head of the Industrial Chair CISCO/CESI/VINCI Energies entitled “Industry and Service of Tomorrow.” He has published more than 100 conference and journal papers. He is involved in conference scientific committees and in several European research projects. His research interests include human-machine interactions and digital twin coupled with augmented or virtual reality environments for training or support on complex system operations. He is also involved in product lifecycle management, cyber-physical system, and complex system modeling and optimization for the smart factory or the smart building.

VOLUME 5, 2024

949

<!-- page 23 of 23 -->

KAMDJOU et al.: RESOURCE-CONSTRAINED XR OPERATED WITH DT IN IIoT

![Image block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p23_b2.png)

**VINCENT HAVARD** received the Ph.D. degree from Rouen University, France, in 2018, and the HDR degree from CNAM, Paris, France, in 2023. He is an Associate Professor with CESI LINEACT Laboratory. He is in charge of the Virtual Reality and Augmented Reality specialization with the School of Computer Science, CESI. His research interests are, in one hand in human machine interaction about modelling of activities within digital twin interface in extended reality. In the other hand, he is working in human system

interaction about human action recognition through deep learning in the context of industry and construction.

![Image block](images/Resource-Constrained_XR_Digital_Twin_IIoT_p23_b5.png)

**SAMIR OUCHANI** received the Ph.D. degree from Concordia University, Canada, in 2013, and the HDR degree from CNAM, Paris, France, in 2022.

He is a Research Director of CESI Linact, Aix-en-Provence, France. His research portfolio focuses on developing robust techniques for securing and ensuring the trustworthiness of systems, with expertise in computer security, software engineering, formal methods, and data mining. His ongoing research endeavors are dedicated to the enhancement of security measures and the

identification of vulnerabilities within extensive interdisciplinary systems, specifically emphasizing cyber-physical systems and interconnected objects. His expertise lies in the development of decentralized techniques grounded in artificial intelligence, strategically employed to elevate decision-making processes within these systems. Furthermore, he employs rigorous formal methods to empirically validate and substantiate the effectiveness and the explainability of these AI-based approaches.

950

VOLUME 5, 2024