<!-- page 1 of 2 -->

# Beyond Digital Twins: 3D Gaussian Splatting, Game Engines and Crossmedia Cultural Heritage Representations

[Lukasz Mirocha](https://orcid.org/0000-0001-7723-6191)

Hong Kong Baptist University

Visualization Research Centre

Kowloon, Hong Kong

Omni Lucenti

Hong Kong, Hong Kong

mirocha.lukasz@gmail.com

## Abstract

This paper explores the use of 3D Gaussian Splatting (3DGS) for cultural heritage representation, integrating real-time game engines to create immersive cross-media experiences. Using a historic Hakka mansion in Hong Kong as a case study, the research examines the technical and aesthetic challenges of 3DGS, particularly its limitations in lighting, geometry accuracy, and artifact generation. By embracing these constraints, the project investigates new modes of representing historical spaces beyond traditional digital twins. The study highlights how 3DGS, combined with SLAM-based scanning and game engine workflows, can offer novel approaches to interactive storytelling, site documentation, and artistic reinterpretation in digital heritage preservation and other use cases.

## CCS Concepts

• Media Arts; • Software Evolution;

## Keywords

3D Gaussian Splatting, digital twins, immersive media, real-time 3D, game engines, virtual cinematography, cultural heritage preservation, cross-media

## ACM Reference Format:

Lukasz Mirocha. 2025. Beyond Digital Twins: 3D Gaussian Splatting, Game Engines and Crossmedia Cultural Heritage Representations. In Special Interest Group on Computer Graphics and Interactive Techniques Conference Talks (SIGGRAPH Talks ’25), August 10–14, 2025, Vancouver, BC, Canada. ACM, New York, NY, USA, 2 pages. [https://doi.org/10.1145/3721239.3734094](https://doi.org/10.1145/3721239.3734094)

## 1 Introduction and project GOALS

This pilot and exploratory research is situated at the intersection of material cultural heritage preservation [Kantaros, 2023; Kęsik, 2023], narrative design [Dubbelman, 2011], novel 3D reconstruction methods [Kerbl, 2023], and virtual cinematography [Mirocha 2021]. It leverages advancements in computer vision, deep neural networks, and real-time 3D engines to explore streamlined approaches for digitizing culturally significant sites. Specifically, the

project utilizes neural radiance fields (e.g., 3D Gaussian Splatting), Structure-from-Motion (SfM) [Arican, 2023] and Simultaneous Localization and Mapping (SLAM) techniques [Lou, 2023] to generate 3D reconstructions from 2D image sequences and sensor data (Li-DAR).

The research asks how novel methods of capturing, processing, and displaying 3D reconstructions can contribute to designing immersive and interactive real-time experiences. It investigates the limitations of 3DGS technology and how the conceptual and aesthetic space between digital twins and visual representations can foster new cross-media image sensibilities in material cultural heritage preservation. Rather than resisting constraints, this project embraces the evolving imagery of neural radiance fields, engaging with glitches, imperfections, and unstable software pipelines as creative opportunities. It examines the emergent aesthetics at the intersection of engineering and art, considering image artifacts and fractured workflows as vehicles for exploring indeterminate outcomes.

## 2 Project Overview: Pun Uk Mansion

The project focuses on an individual historical site and is divided into three major stages. In the first stage several data capturing sessions were undertaken at the location, where different scanning equipment was used as well as various lighting, and weather conditions were experienced. In the second stage, several software solutions for data processing were tested to explore a rapid evolving landscape for 3D Gaussian Splatting and SLAM point-clouds reconstruction [Jawset, 2024], [LumaLabs, 2024], [Niantic, 2024]. In the third step, the processed data (3DGS spatial imagery) provided a basis for creative exploratory design practices, leveraging game engines (e.g., Unity 3D, Unreal Engine 5) and their ability to output various 3D-based media content. The project focuses on Pun Uk Mansion, a historically significant yet abandoned Hakka mansion in Hong Kong [Aab, 2024; Fac, 2024; Amo, 2024]. Built in 1932 by affluent merchant Kwan-min Pun, it spans over 600 square meters with three halls, courtyards, auxiliary blocks, and intricate carvings and paintings. While prior documentation focused on detailed photo archives, this project extends heritage preservation into spatial dimensions through novel digital methods, capturing the mansion’s current state of decay in 2024. The reconstructed 3D space also serves as a foundation for historical and fictional narrative-building, integrating real-time 3D and XR technologies.

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page. Copyrights for third-party components of this work must be honored. For all other uses, contact the owner/author(s).</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">SIGGRAPH Talks ’25, Vancouver, BC, Canada</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">© 2025 Copyright held by the owner/author(s).</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">ACM ISBN 979-8-4007-1541-9/2025/08</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">[https://doi.org/10.1145/3721239.3734094](https://doi.org/10.1145/3721239.3734094)</span></small>

<!-- page 2 of 2 -->

SIGGRAPH Talks ’25, August 10–14, 2025, Vancouver, BC, Canada

Lukasz Mirocha

## 3 Data Capture and 3DGS Processing

Data capture and processing occurred from August to December 2024 across five scanning visits, employing diverse imaging devices. A Canon DSLR captured details like ceiling paintings and tiles, while iPhones (13 Pro, 16 Pro) recorded high-definition videos of rooms and courtyards. A high-end SLAM (LixelKity K1 by Xgrids), equipped with dual 48MP panoramic vision modules and LiDAR, captured the entire mansion and selected exterior sections [Xgrids, 2024]. Processing followed a rapid feedback loop, refining workflows based on results. Captures were processed using an RTX 3080 GPU in Postshot, except for Xgrids scanner data, which required Lixel CyberColor, a proprietary software. Post-processing involved clearing data in Postshot [Jawset, 2024] and SuperSplat [PlayCanvas, 2024], refining 3DGS scenes by removing splat groups, culling unnecessary areas, and cleaning artifacts caused by lighting inconsistencies or data gaps.

## 4 Creative Results and Game Engines Integration

The third stage involved integrating 3DGS scans into Unity 3D and Unreal Engine 5 to evaluate real-time rendering feasibility. Multiple third-party 3DGS plug-ins were tested, including Luma AI (Unreal) [LumaAI, 2024], XVERSE 3D-GS UE Plugin [Xverse, 2024], Postshot Plugin [Jawset, 2024], LCC Unreal SDK [Xgrids, 2024], LCC Unity SDK [Xgrids, 2024] and UnityGaussianSplatting [ArasP, 2024]. While these plug-ins enable 3DGS rendering and basic adjustments (scale, opacity), current limitations prevent splats from casting or receiving dynamic shadows, locking them into a”baked” state that preserves the lighting and atmospheric conditions of the original scans. Moreover, lens-based 3DGS reconstructions lack digital twin-level geometric accuracy and may suffer from scale and orientation misalignment. Only the SLAM-enhanced LixelKity dataset, integrating LiDAR with optical data, achieves both high-fidelity visual representation and precise geometric accuracy. Despite these constraints, 3DGS offers unparalleled photorealism akin to digital photography, enriched by spatial perspectives that enable cinematic exploration and novel visualization techniques. Three distinct creative works were designed to examine different virtual camera modalities and aesthetic affordances of 3DGS technology: Unity-based immersive LED Volume Installation: Comprising over a dozen individual scans of various mansion sections and three 360-degree captures, this work leverages an interactive, spatial experience in an LED display environment; Unreal-based interactive exploration: a PC-based third-person exploration expe rience reconstructs the mansion using 10 interlinked 3DGS scans, loosely aligning with real-world positioning., leveraging a stylized re-imagining of the site; Unity-based SLAM-enhanced flythrough animation: built from a complete SLAM-generated scan, this animation offers a digital twin-level representation, capturing both geometric accuracy and atmospheric fidelity, making it suitable for architectural documentation.

Aesthetically, the first two works juxtapose photorealistic details with artifacts, blurs, and halos at scan edges, crafting an ethereal, fragmented vision of Pun Uk. The interplay between specular effects and glitchy surfaces from underexposed footage fosters a dreamlike revisitation of the site. In contrast, the third piece, rooted

in SLAM-processed data, presents a more indexical reconstruction, emphasizing structural integrity over interpretative abstraction.

## 5 Conclusion: Working with Technological Constraints

This research does not seek a flawless digital twin but rather explores the evolving visual language of 3DGS. By embracing techno logical limitations—image artifacts, broken geometries, and non-indexical representations—it engages with material cultural heritage through a process-driven aesthetic. The work challenges conventional modes of documentation, suggesting that digital preservation need not be confined to hyper-accurate replicas but can also exist as evocative, generative image-making practices. As 3DGS and neural radiance fields continue to advance, their potential for cultural heritage preservation will expand, enabling new forms of interactive storytelling and spatial engagement. This talk contributes to that trajectory by critically examining the medium’s affordances, limitations, and aesthetic possibilities in an interdisciplinary space bridging media arts, computer graphics, and heritage conservation.

## References

Aab. 2024. List of the 1,444 Historic Buildings with Assessment Results, The Antiquities Advisory Board, accessed November 15, 2024. [https://www.aab.gov.hk/filemanager/aab/en/content\_29/AAB-](https://www.aab.gov.hk/filemanager/aab/en/content_29/AAB-) SM-chi.pdf

Amo. 2024. Definition of Grading, The Antiquities Advisory Board, ac- cessed November 15, 2024. [https://www.amo.gov.hk/en/historic-](https://www.amo.gov.hk/en/historic-) buildings/historic-buildingshk/assessment/index.html

Duygu Arican, Ferat Furkan Göksu, Nursu Tunalioglu, Taylan Ocalan. 2023. Research on 3D reconstruction of small size objects using struc- ture from motion photogrammetry via smartphone images. Journal of Geodesy and Geoinformation, 10, 112-123. doi: 10.9733/JGG.2023R0008.E.

Teun Dubbelman. 2011. Designing stories: practices of narrative in 3D computer games. In Proceedings of the 2011 ACM SIGGRAPH Symposium on Video Games (Sandbox ’11). Association for Computing Machinery, New York, NY, USA, 37–41. [https://doi.org/10.1145/2018556.2018564.](https://doi.org/10.1145/2018556.2018564)

LumaAI Fab Unreal Plugin. 2024. [https://www.fab.com/listings/b52460e0-3ace-465e-a378-](https://www.fab.com/listings/b52460e0-3ace-465e-a378-) 495a5531e318

Fac. 2024. Hands-on Heritage: Shared Conservation of a Historic Hakka Mansion, accessed November 15, 2024. [https://fac.arch.hku.hk/aclab/research/PunUk/\[12\]](https://fac.arch.hku.hk/aclab/research/PunUk/%20[12])

Jawset Postshot (Beta). 2024.

Antreas Kantaros, Theodore Ganetsos, Florian Ion Tiberiu. 2023. Three-Dimensional Printing and 3D Scanning: Emerging Technologies Exhibiting High Potential in the Field of Cultural Heritage. In Applied Sciences, 13(8), 4777. [https://doi.org/10.3390/app13084777](https://doi.org/10.3390/app13084777).

Jacek Kęsik, Kamil Żyła, Jerzy Montusiewicz, Marek Miłosz, Calin Neamtu, Marta Juszczyk. 2023. A Methodical Approach to 3D Scanning of Heritage Objects Being under Continuous Display. In Applied Sciences, 13(1), 441. [https://doi.org/10.3390/app13010441](https://doi.org/10.3390/app13010441).

Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, George Drettakis, G. 2023. 3D Gaussian Splatting for Real-Time Radiance Field Rendering, In ACM Transactions on Graphics, 42(4), July. [https://repo-sam.in-ria.fr/fungraph/3d-gaussian-splatting/](https://repo-sam.in-ria.fr/fungraph/3d-gaussian-splatting/)

Lu Lou, Yitian Li, Qi Zhang, Hanbing Wei. 2023. SLAM and 3D Semantic Reconstruction Based on the Fusion of Lidar and Monocular Vision. Sensors, 23(3), 1502. [https://doi.org/10.3390/s23031502](https://doi.org/10.3390/s23031502)

Lukasz Mirocha. 2021. Virtual Cameras and General-Purpose Game Engines: On Hybrid and Programmable Aesthetics of 3D Real-Time Environments.Ph.D. Dissertation. City University of Hong Kong.

ArasP. 2024. UnityGaussianSplatting. [https://github.com/aras-p/UnityGaussianSplatting](https://github.com/aras-p/UnityGaussianSplatting)

PlayCanvas. 2024. SuperSplat. [https://playcanvas.com/supersplat/editor/](https://playcanvas.com/supersplat/editor/)

Xgrids LCC Unreal SDK. 2024. [https://developer.xgrids.com/#/](https://developer.xgrids.com/#/)

Xgrids LixelKity K1. 2024. [https://xgrids.com/lixelk1](https://xgrids.com/lixelk1)

Xgrids LCC Unity SDK. 2024. [https://developer.xgrids.com/#/](https://developer.xgrids.com/#/)

Xverse XV3DGS-UEPlugin. 2024. [https://github.com/xverse-engine/XV3DGS-UEPlugin](https://github.com/xverse-engine/XV3DGS-UEPlugin)