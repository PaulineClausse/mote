<!-- page 1 of 25 -->

# 3D Gaussian Splatting for Real-Time Radiance Field Rendering

November 20, 2023

Bernhard Kerbl\*, Georgios Kopanas\*, Thomas Leimkühler, George Drettakis In SIGGRAPH 2023

Presenter: Donghwan Kim 20233091

<!-- page 2 of 25 -->

## Contents

1. Background

2. Contribution

3. Method

4. Results

5. Conclusion

2

<!-- page 3 of 25 -->

## 1. Background

## Rasterization

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p3_b3.png)

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p3_b4.png)

[https://darkpgmr.tistory.com/77](https://darkpgmr.tistory.com/77)

[Lecture Slide for <3D Transformation> from CS380 (Spring 2020) Sung-eui Yoon](http://sgvr.kaist.ac.kr/~sungeui/CG/)

3

<!-- page 4 of 25 -->

## 1. Background

## Ray Casting

## • For each pixel, find closest object along the ray and shade pixel accordingly

## Advantages

Conceptually simple

Can be extended to handle global illumination effects

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p4_b7.png)

## • Disadvantages

Renderer must have access to entire retained model

Hard to map to special-purpose hardware

Less efficient than rasterization in terms of utilizing spatial coherence

[Lecture Slide for &lt;Ray tracing&gt; from CS380 (Spring 2020) Sung-eui Yoon](http://sgvr.kaist.ac.kr/~sungeui/CG/Slides/Lecture11_1.pdf)

4

<!-- page 5 of 25 -->

## 1. Background

## NeRF (Neural Radiance Fields): Ray-marching

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p5_b3.png)

[Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, Ren Ng. NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis. In ECCV, 2020.](https://arxiv.org/abs/2003.08934)

<!-- page 6 of 25 -->

## 2. Contribution

## 3D Gaussians

1. preserve **continuous** properties

2. avoid unnecessary computation in **empty space**

3. **rasterization**-based rendering

6

<!-- page 7 of 25 -->

## 3. Method

## Overview

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p7_b3.png)

<!-- page 8 of 25 -->

## 3. Method

## Structure-from-Motion

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p8_b3.png)

8

<!-- page 9 of 25 -->

## 3. Method

## Structure-from-Motion

● Camera calibration for in-the-wild NeRF.

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p9_b4.png)

[https://mvje.tistory.com/92](https://mvje.tistory.com/92)

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p9_b6.png)

[https://woochan-autobiography.tistory.com/944](https://woochan-autobiography.tistory.com/944)

<!-- page 10 of 25 -->

## 3. Method

## Initial spare point cloud

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p10_b3.png)

<!-- page 11 of 25 -->

## 3. Method

## 3D Gaussians

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p11_b3.png)

<!-- page 12 of 25 -->

## 3. Method

## 3D Gaussian Splatting - Geometry

● 3D Gaussian

$$
\mathcal {G} (\mathbf {x} - \mu) = \frac {1}{2 \pi \Sigma (\mathbf {x}) ^ {\frac {1}{2}}} \exp (- \frac {1}{2} (\mathbf {x} - \mu) ^ {T} \Sigma^ {- 1} (\mathbf {x}))
$$

● 2D projection, where W is viewing transformation, and J is the Jacobian of affine projective transformation.

$$
\Sigma^ {\prime} = J W \Sigma W ^ {T} J ^ {T}
$$

● Positive semi-definite covariance, where S is scale and R is rotation matrix.

$$
\left| \boldsymbol {\Sigma} = \boldsymbol {R S S} ^ {T} \boldsymbol {R} ^ {T} \right|
$$

[Matthias Zwicker, Hanspeter Pfister, Jeroen Van Baar, Markus Gross. EWA volume splatting. In Proceedings of IEEE Visualization, 2001.](https://www.cs.umd.edu/~zwicker/publications/EWAVolumeSplatting-VIS01.pdf)

<!-- page 13 of 25 -->

## 3. Method

## 3D Gaussian Splatting - Opacity and Color

● Opacity ɑ

Color - Spherical Harmonics (SH) coefficients

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p13_b5.png)

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p13_b6.png)

[https://xoft.tistory.com/50](https://xoft.tistory.com/50)

[Robin Green. Spherical harmonic lighting: The gritty details. In Archives of the game developers conference, 2003.](https://theory.cpe.ku.ac.th/~pramook/files/spherical-harmonic-lighting.pdf)

13

<!-- page 14 of 25 -->

## 3. Method

## 3D Gaussian Optimization

● Position (mean) p

● Covariance Σ

● Opacity ɑ

Color - Spherical Harmonics (SH) coefficients

## → Gradient Descent

There is no neural networks to optimize!

<!-- page 15 of 25 -->

## 3. Method

## Adaptive Control of Gaussians

● **Clone** 3D gaussians: Under-reconstruction (missing geometric features)

● **Split** 3D gaussians: Over-reconstruction (covering large area)

● **Remove** 3D gaussians: Opacity is lower than threshold

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p15_b6.png)

<!-- page 16 of 25 -->

## 3. Method

## Optimization

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p16_b3.png)

## 3D Gaussian Splatting for Real-Time Radiance Field Rendering

SIGGRAPH 2023

Borndsard Kerll»

Georgios Kopanas\*

mpn

<!-- page 17 of 25 -->

## 3. Method

## Tile-based Rasterizer

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p17_b3.png)

17

<!-- page 18 of 25 -->

## 3. Method

## Split Image to 16x16 Tiles

1. Parallelize within GPU cores.

2. Avoid the expense of depth sorting per pixel.

18

<!-- page 19 of 25 -->

## 3. Method

## Rasterization

For NeRF, $\begin{array} { r } { C ( \mathbf { r } ) = \int _ { t _ { n } } ^ { t _ { f } } T ( t ) \sigma ( \mathbf { r } ( t ) ) \mathbf { c } ( \mathbf { r } ( t ) , \mathbf { d } ) d t } \end{array}$

, where $\begin{array} { r } { T ( t ) = \exp ( - \int _ { t _ { n } } ^ { t } \sigma ( \mathbf { r } ( s ) ) d s ) } \end{array}$

For 3D Gaussian Splatting, the color and opacity ɑ are accumulated per pixel

from the closest to farthest gaussian

until opacity threshold

<!-- page 20 of 25 -->

## 4. Results

## Evaluation Metrics

1. PSNR (Peak Signal-to-Noise Ratio) ↑

2. SSIM (Structural Similarity Index Measure) ↑

3. LPIPS (Learned Perceptual Image Patch Similarity) ↓

4. FPS (Frame Per Seconds for inference rendering with A6000) ↑

5. Train (training time for A6000) ↓

## Model Variations

1. Ours7K: 7K iterations

2. Ours30K: 30K iterations

<!-- page 21 of 25 -->

## 4. Results

1. State of the Art Quality (Equivalent to MipNerf360)

2. Real-Time Rendering (More than 100 FPS)

3. Fast Training (Less than 1h)

![Chart block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p21_b5.png)

![Chart block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p21_b6.png)

<!-- page 22 of 25 -->

## 4. Results

## Qualitative Evaluation

![Image block](images/CS482_3D_Gaussian_Splatting_Real-Time_Radiance_Field_Rendering_p22_b3.png)

## 3D Gaussian Splatting for Real-Time Radiance Field Rendering

SIGGRAPH 2023

mpn

22

<!-- page 23 of 25 -->

## 4. Results

## Quantitative Evaluation

<table><tr><td rowspan="2">DatasetMethod|Metric</td><td colspan="6">Mip-NeRF360</td><td colspan="6">Tanks&amp;Temples</td><td colspan="6">Deep Blending</td></tr><tr><td> $SSIM^{\uparrow}$ </td><td> $PSNR^{\uparrow}$ </td><td> $LPIPS^{\downarrow}$ </td><td>Train</td><td>FPS</td><td>Mem</td><td> $SSIM^{\uparrow}$ </td><td> $PSNR^{\uparrow}$ </td><td> $LPIPS^{\downarrow}$ </td><td>Train</td><td>FPS</td><td>Mem</td><td> $SSIM^{\uparrow}$ </td><td> $PSNR^{\uparrow}$ </td><td> $LPIPS^{\downarrow}$ </td><td>Train</td><td>FPS</td><td>Mem</td></tr><tr><td>Plenoxels</td><td>0.626</td><td>23.08</td><td>0.463</td><td>25m49s</td><td>6.79</td><td>2.1GB</td><td>0.719</td><td>21.08</td><td>0.379</td><td>25m5s</td><td>13.0</td><td>2.3GB</td><td>0.795</td><td>23.06</td><td>0.510</td><td>27m49s</td><td>11.2</td><td>2.7GB</td></tr><tr><td>INGP-Base</td><td>0.671</td><td>25.30</td><td>0.371</td><td>5m37s</td><td>11.7</td><td>13MB</td><td>0.723</td><td>21.72</td><td>0.330</td><td>5m26s</td><td>17.1</td><td>13MB</td><td>0.797</td><td>23.62</td><td>0.423</td><td>6m31s</td><td>3.26</td><td>13MB</td></tr><tr><td>INGP-Big</td><td>0.699</td><td>25.59</td><td>0.331</td><td>7m30s</td><td>9.43</td><td>48MB</td><td>0.745</td><td>21.92</td><td>0.305</td><td>6m59s</td><td>14.4</td><td>48MB</td><td>0.817</td><td>24.96</td><td>0.390</td><td>8m</td><td>2.79</td><td>48MB</td></tr><tr><td>M-NeRF360</td><td> $0.792^{\dagger}$ </td><td> $27.69^{\dagger}$ </td><td> $0.237^{\dagger}$ </td><td>48h</td><td>0.06</td><td>8.6MB</td><td>0.759</td><td>22.22</td><td>0.257</td><td>48h</td><td>0.14</td><td>8.6MB</td><td>0.901</td><td>29.40</td><td>0.245</td><td>48h</td><td>0.09</td><td>8.6MB</td></tr><tr><td>Ours-7K</td><td>0.770</td><td>25.60</td><td>0.279</td><td>6m25s</td><td>160</td><td>523MB</td><td>0.767</td><td>21.20</td><td>0.280</td><td>6m55s</td><td>197</td><td>270MB</td><td>0.875</td><td>27.78</td><td>0.317</td><td>4m35s</td><td>172</td><td>386MB</td></tr><tr><td>Ours-30K</td><td>0.815</td><td>27.21</td><td>0.214</td><td>41m33s</td><td>134</td><td>734MB</td><td>0.841</td><td>23.14</td><td>0.183</td><td>26m54s</td><td>154</td><td>411MB</td><td>0.903</td><td>29.41</td><td>0.243</td><td>36m2s</td><td>137</td><td>676MB</td></tr></table>

## PSNR scores for Synthetic NeRF

|  | Mic | Chair | Ship | Materials | Lego | Drums | Ficus | Hotdog | Avg. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Plenoxels | 33.26 | 33.98 | 29.62 | 29.14 | 34.10 | 25.35 | 31.83 | 36.81 | 31.76 |
| INGP-Base | 36.22 | 35.00 | 31.10 | 29.78 | 36.39 | 26.02 | 33.51 | 37.40 | 33.18 |
| Mip-NeRF | 36.51 | 35.14 | 30.41 | 30.71 | 35.70 | 25.48 | 33.29 | 37.48 | 33.09 |
| Point-NeRF | 35.95 | 35.40 | 30.97 | 29.61 | 35.04 | 26.06 | 36.13 | 37.30 | 33.30 |
| Ours-30K | 35.36 | 35.83 | 30.80 | 30.00 | 35.78 | 26.15 | 34.87 | 37.72 | 33.32 |

<!-- page 24 of 25 -->

## 5. Conclusion

They proposed new radiance field rendering methods using **3D gaussian** as volumetric representation for **real-time rendering** while preserving **state-of-the-art quality**.

<!-- page 25 of 25 -->

## References

[Author’s project page and video](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/)

[https://darkpgmr.tistory.com/77](https://darkpgmr.tistory.com/77)

[https://mvje.tistory.com/92](https://mvje.tistory.com/92)

[https://woochan-autobiography.tistory.com/944](https://woochan-autobiography.tistory.com/944)

[https://xoft.tistory.com/50](https://xoft.tistory.com/50)

[Lecture Slide of CS380 (Spring 2020) Sung-eui Yoon](http://sgvr.kaist.ac.kr/~sungeui/CG/)

[Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, George Drettakis. 3D Gaussian Splatting for Real-Time Radiance Field Rendering. In SIGGRAPH, 2023.](https://arxiv.org/abs/2308.04079)

[Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, Ren Ng. NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis. In ECCV, 2020.](https://arxiv.org/abs/2003.08934)

[Matthias Zwicker, Hanspeter Pfister, Jeroen Van Baar, Markus Gross. EWA volume splatting. In Proceedings of IEEE Visualization, 2001.](https://www.cs.umd.edu/~zwicker/publications/EWAVolumeSplatting-VIS01.pdf)

[Robin Green. Spherical harmonic lighting: The gritty details. In Archives of the game developers conference, 2003.](https://theory.cpe.ku.ac.th/~pramook/files/spherical-harmonic-lighting.pdf)