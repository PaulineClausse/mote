<!-- page 1 of 17 -->

1

arXiv:1708.03852v1 [cs.RO] 13 Aug 2017

# VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator

Tong Qin, Peiliang Li, and Shaojie Shen

**Abstract—A monocular visual-inertial system (VINS), consisting of a camera and a low-cost inertial measurement unit (IMU), forms the minimum sensor suite for metric six degreesof-freedom (DOF) state estimation. However, the lack of direct distance measurement poses significant challenges in terms of IMU processing, estimator initialization, extrinsic calibration, and nonlinear optimization. In this work, we present VINS-Mono: a robust and versatile monocular visual-inertial state estimator. Our approach starts with a robust procedure for estimator initialization and failure recovery. A tightly-coupled, nonlinear optimization-based method is used to obtain high accuracy visual-inertial odometry by fusing pre-integrated IMU measurements and feature observations. A loop detection module, in combination with our tightly-coupled formulation, enables relocalization with minimum computation overhead. We additionally perform four degrees-of-freedom pose graph optimization to enforce global consistency. We validate the performance of our system on public datasets and real-world experiments and compare against other state-of-the-art algorithms. We also perform onboard closed-loop autonomous flight on the MAV platform and port the algorithm to an iOS-based demonstration. We highlight that the proposed work is a reliable, complete, and versatile system that is applicable for different applications that require high accuracy localization. We open source our implementations for both PCs**<sup>1</sup>**and iOS mobile devices**<sup>2</sup>.

**Index Terms—Monocular visual-inertial systems, state estimation, sensor fusion, simultaneous localization and mapping**

## I. INTRODUCTION

TATE estimation is undoubtedly the most fundamental module for a wide range of applications, such as robotic navigation, autonomous driving, virtual reality (VR), and augmented reality (AR). Approaches that use only a monocular camera have gained significant interests by the community due to their small size, low-cost, and easy hardware setup [1]– [5]. However, monocular vision-only systems are incapable of recovering the metric scale, therefore limiting their usage in real-world robotic applications. Recently, we see a growing trend of assisting the monocular vision system with a lowcost inertial measurement unit (IMU). The primary advantage of this monocular visual-inertial system (VINS) is to have the metric scale, as well as roll and pitch angles, all observable. This enables navigation tasks that require metric state estimates. In addition, the integration of IMU measurements can dramatically improve motion tracking performance by bridging the gap between losses of visual tracks due to

![Image block](images/qin2018_vins-mono_p1_b9.png)

(a) Trajectory (blue) and feature locations (red)

![Image block](images/qin2018_vins-mono_p1_b11.png)

(b) Trajectory overlaid with Google Map for visual comparison

Fig. 1. Outdoor experimental results of the proposed monocular visual-inertial state estimator. Data is collected by a hand-held monocular camera-IMU setup under normal walking condition. It includes two complete circles inside the field and two semicircles on the nearby driveway. Total trajectory length is 2.5 km. A video of the experiment can be found in the multimedia attachment.

illumination change, texture-less area, or motion blur. In fact, the monocular VINS not only widely available on mobile robots, drones, and mobile devices, it is also the minimum sensor setup for sufficient self and environmental perception.

However, all these advantages come with a price. For monocular VINS, it is well known that acceleration excitation is needed to make metric scale observable. This implies that monocular VINS estimators cannot start from a stationary condition, but rather launch from an unknown moving state. Also recognizing the fact that visual-inertial systems are highly nonlinear, we see significant challenges in terms of estimator initialization. The existence of two sensors also makes camera-IMU extrinsic calibration critical. Finally, in order to eliminate long-term drift within an acceptable processing window, a complete system that includes visual-inertial odometry, loop detection, relocalization, and global optimization has to be developed.

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">T. Qin, P. Li, and S. Shen are with the Department of Electronic and Computer Engineering, Hong Kong University of Science and Technology. e-mail: {tqinab, pliap}@connect.ust.hk, eeshaojie@ust.hk</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>1</sup>https://github.com/HKUST-Aerial-Robotics/VINS-Mono</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>2</sup>https://github.com/HKUST-Aerial-Robotics/VINS-Mobile</span></small>

<!-- page 2 of 17 -->

2

To address all these issues, we propose VINS-Mono, a robust and versatile monocular visual-inertial state estimator. Our solution starts with on-the-fly estimator initialization. The same initialization module is also used for failure recovery. The core of our solution is a robust monocular visual-inertial odometry (VIO) based on tightly-coupled sliding window non-linear optimization. The monocular VIO module not only provides accurate local pose, velocity, and orientation estimates, it also performs camera-IMU extrinsic calibration and IMU biases correction in an online fashion. Loops are detected using DBoW2 [6]. Relocalization is done in a tightly-coupled setting by feature-level fusion with the monocular VIO. This enables robust and accurate relocalization with minimum computation overhead. Finally, geometrically verified loops are added into a pose graph, and thanks to the observable roll and pitch angles from the monocular VIO, a four degrees-of-freedom (DOF) pose graph is performed to ensure global consistency.

VINS-Mono combines and improves the our previous works on monocular visual-inertial fusion [7]–[10]. It is built on top our tightly-coupled, optimization-based formulation for monocular VIO [7], [8], and incorporates the improved initialization procedure introduced in [9]. The first attempt of porting to mobile devices was given in [10]. Further improvements of VINS-Mono comparing to our previous works include improved IMU pre-integration with bias correction, tightly-coupled relocalization, global pose graph optimization, extensive experimental evaluation, and a robust and versatile open source implementation.

The whole system is complete and easy-to-use. It has been successfully applied to small-scale AR scenarios, mediumscale drone navigation, and large-scale state estimation tasks. Superior performance has been shown against other state-of-the-art methods. To this end, we summarize our contributions as follow:

• A robust initialization procedure that is able to bootstrap the system from unknown initial states.

• A tightly-coupled, optimization-based monocular visualinertial odometry with camera-IMU extrinsic calibration and IMU bias estimation.

• Online loop detection and tightly-coupled relocalization.

• Four DOF global pose graph optimization.

• Real-time performance demonstration for drone navigation, large-scale localization, and mobile AR applications.

• Open-source release for both the PC version that is fully integrated with ROS, as well as the iOS version that runs on iPhone6s or above.

The rest of the paper is structured as follows. In Sect. II, we discuss relevant literature. We give an overview of the complete system pipeline in Sect. III. Preprocessing steps for both visual and pre-integrated IMU measurements are presented in Sect. IV. In Sect. V, we discuss the estimator initialization procedure. A tightly-coupled, self-calibrating, nonlinear optimization-based monocular VIO, is presented in Sect. VI. Tightly-coupled relocalization and global pose graph optimization are presented in Sect. VII and Sect. VIII respectively. Implementation details and experimental results are shown in Sect. IX. Finally, the paper is concluded with a

discussion and possible future research directions in Sect. X.

## II. RELATED WORK

Scholarly works on monocular vision-based state estimation/odometry/SLAM are extensive. Noticeable approaches include PTAM [1], SVO [2], LSD-SLAM [3], DSO [5], and ORB-SLAM [4]. It is obvious that any attempts to give a full relevant review would be incomplete. In this section, however, we skip the discussion on vision-only approaches, and only focus on the most relevant results on monocular visual-inertial state estimation.

The simplest way to deal with visual and inertial measurements is loosely-coupled sensor fusion [11], [12], where IMU is treated as an independent module to assist vision-only pose estimates obtained from the visual structure from motion. Fusion is usually done by an extended Kalman filter (EKF), where IMU is used for state propagation and the vision-only pose is used for the update. Further on, tightly-coupled visualinertial algorithms are either based on the EKF [13]–[15] or graph optimization [7], [8], [16], [17], where camera and IMU measurements are jointly optimized from the raw measurement level. A popular EKF based VIO approach is MSCKF [13], [14]. MSCKF maintains several previous camera poses in the state vector, and uses visual measurements of the same feature across multiple camera views to form multi-constraint update. SR-ISWF [18], [19] is an extension of MSCKF. It uses squareroot form [20] to achieve single-precision representation and avoid poor numerical properties. This approach employs the inverse filter for iterative re-linearization, making it equal to optimization-based algorithms. Batch graph optimization or bundle adjustment techniques maintain and optimize all measurements to obtain the optimal state estimates. To achieve constant processing time, popular graph-based VIO methods [8], [16], [17] usually optimize over a bounded-size sliding window of recent states by marginalizing out past states and measurements. Due to high computational demands of iterative solving of nonlinear systems, few graph-based can achieve real-time performance on resource-constrained platforms, such as mobile phones.

For visual measurement processing, algorithms can be categorized into either direct or indirect method according to the definition of visual residual models. Direct approaches [2], [3], [21] minimize photometric error while indirect approaches [8], [14], [16] minimize geometric displacement. Direct methods require a good initial guess due to their small region of attraction, while indirect approaches consume extra computational resources on extracting and matching features. Indirect approaches are more frequently found in real-world engineering deployment due to its maturity and robustness. However, direct approaches are easier to be extended for dense mapping as they are operated directly on the pixel level.

In practice, IMUs usually acquire data at a much higher rate than the camera. Different methods have been proposed to handle the high rate IMU measurements. The most straightforward approach is to use the IMU for state propagation in EKF-based approaches [11], [13]. In a graph optimization formulation, an efficient technique called IMU pre-integration is developed in

<!-- page 3 of 17 -->

3

![Image block](images/qin2018_vins-mono_p3_b2.png)

Fig. 2. A block diagram illustrating the full pipeline of the proposed monocular visual-inertial state estimator.

order to avoid repeated IMU re-integration This technique was first introduced in [22], which parametrize rotation error using Euler angles. An on-manifold rotation formulation for IMU-preintegration was developed in our previous work [7]. This work derived the covariance propagation using continuoustime IMU error state dynamics. However, IMU biases were ignored. The pre-integration theory was further improved in [23] by adding posterior IMU bias correction.

Accurate initial values are crucial to bootstrap any monocular VINS. A linear estimator initialization method that leverages relative rotations from short-term IMU pre-integration was proposed in [8], [24]. However, this method does not model gyroscope bias, and fails to model sensor noise in raw projection equations. In real-world applications, this results in unreliable initialization when visual features are far away from the sensor suite. A closed-form solution to the monocular visual-inertial initialization problem was introduced in [25]. Later, an extension to this closed-form solution by adding gyroscope bias calibration was proposed in [26]. These approaches fail to model the uncertainty in inertial integration since they rely on the double integration of IMU measurements over an extended period of time. In [27], a re-initialization and failure recovery algorithm based on SVO [2] was proposed. This is a practical method based on a loosely-coupled fusion framework. However, an additional downward-facing distance sensor is required to recover the metric scale. An initialization algorithm built on top of the popular ORB-SLAM [4] was introduced in [17]. An initial estimation of the scale, gravity direction, velocity and IMU biases are computed for the visual-inertial full BA given a set of keyframes from ORB-SLAM. However, it is reported that the time required for scale convergence can be longer than 10 seconds. This can pose problems for robotic navigation tasks that require scale estimates right at the beginning.

VIO approaches, regardless the underlying mathematical formulation that they rely on, suffer from long term drifting

in global translation and orientation. To this end, loop closure plays an important role for long-term operations. ORB-SLAM [4] is able to close loops and reuse the map, which takes advantage of Bag-of-World [6]. A 7 DOF [28] (position, orientation, and scale) pose graph optimization is followed loop detection. In contrast, for monocular VINS, thanks to the addition of IMU, drift only occurs in 4 DOF, which is the 3D translation, and the rotation around the gravity direction (yaw angle). Therefore, in this paper, we choose to optimize the pose graph with loop constraints in the minimum 4 DOF setting.

## III. OVERVIEW

The structure of proposed monocular visual-inertial state estimator is shown in Fig. 2. The system starts with measurement preprocessing (Sect. IV), in which features are extracted and tracked, and IMU measurements between two consecutive frames are pre-integrated. The initialization procedure (Sect. V provides all necessary values, including pose, velocity, gravity vector, gyroscope bias, and 3D feature location, for bootstrapping the subsequent nonlinear optimization-based VIO. The VIO (Sect. VI) with relocalization (Sect. VII) modules tightly fuses pre-integrated IMU measurements, feature observations, and re-detected features from loop closure. Finally, the pose graph optimization module (Sect. VIII) takes in geometrically verified relocalization results, and perform global optimization to eliminate drift. The VIO, relocalization, and pose graph optimization modules run concurrently in a multi-thread setting. Each module has different running rates and real-time guarantees to ensure reliable operation at all times.

We now define notations and frame definitions that we use throughout the paper. We consider $( \cdot ) ^ { w }$ as the world frame. The direction of the gravity is aligned with the z axis of the world frame. $( \cdot ) ^ { b }$ is the body frame, which we define it to be the same as the IMU frame. $( \cdot ) ^ { c }$ is the camera frame. We use both rotation matrices R and Hamilton quaternions

<!-- page 4 of 17 -->

4

q to represent rotation. We primarily use quaternions in state vectors, but rotation matrices are also used for convenience rotation of 3D vectors. $\mathbf { q } _ { b } ^ { w } , \mathbf { p } _ { b } ^ { w }$ are rotation and translation from the body frame to the world frame. $b _ { k }$ is the body frame while taking the $k ^ { t h }$ image. $c _ { k }$ is the camera frame while taking the $\bar { k } ^ { t h }$ image. ⊗ represents the multiplication operation between two quaternions. $\mathbf { g } ^ { w } \; = \; [ 0 , 0 , g ] ^ { \dot { T } }$ is the gravity vector in the world frame. Finally, we denote ˆ(·) as the noisy measurement or estimate of a certain quantity.

## IV. MEASUREMENT PREPROCESSING

This section presents preprocessing steps for both inertial and monocular visual measurements. For visual measurements, we track features between consecutive frames and detect new features in the latest frame. For IMU measurements, we pre-integrate them between two consecutive frames. Note that the measurements of the low-cost IMU that we use are affected by both bias and noise. We therefore especially take bias into account in the IMU pre-integration process.

## A. Vision Processing Front-end

For each new image, existing features are tracked by the KLT sparse optical flow algorithm [29]. Meanwhile, new corner features are detected [30] to maintain a minimum number (100-300) of features in each image. The detector enforces a uniform feature distribution by setting a minimum separation of pixels between two neighboring features. 2D Features are firstly undistorted and then projected to a unit sphere after passing outlier rejection. Outlier rejection is performed using RANSAC with fundamental matrix model [31].

Keyframes are also selected in this step. We have two criteria for keyframe selection. The first one is the average parallax apart from the previous keyframe. If the average parallax of tracked features is between the current frame and the latest keyframe is beyond a certain threshold, we treat frame as a new keyframe. Note that not only translation but also rotation can cause parallax. However, features cannot be triangulated in the rotation-only motion. To avoid this situation, we use shortterm integration of gyroscope measurements to compensate rotation when calculating parallax. Note that this rotation compensation is only used to keyframe selection, and is not involved in rotation calculation in the VINS formulation. To this end, even if the gyroscope contains large noise or is biased, it will only result in suboptimal keyframe selection results, and will not directly affect the estimation quality. Another criterion is tracking quality. If the number of tracked features goes below a certain threshold, we treat this frame as a new keyframe. This criterion is to avoid complete loss of feature tracks.

## B. IMU Pre-integration

IMU Pre-integration was first proposed in [22], which parametrized rotation error in Euler angle. An on-manifold rotation formulation for IMU pre-integration was developed in our previous work [7]. This work derived the covariance propagation using continuous-time IMU error state dynamics.

However, IMU biases were ignored. The pre-integration theory was further improved in [23] by adding posterior IMU bias correction. In this paper, we extend the IMU pre-integration proposed in our previous work [7] by incorporating IMU bias correction.

The raw gyroscope and accelerometer measurements from IMU, $\hat { \omega }$ and â, are given by:

$$
\begin{array}{r l} & {\hat {\mathbf {a}} _ {t} = \mathbf {a} _ {t} + \mathbf {b} _ {a _ {t}} + \mathbf {R} _ {w} ^ {t} \mathbf {g} ^ {w} + \mathbf {n} _ {a}} \\ & {\hat {\boldsymbol {\omega}} _ {t} = \boldsymbol {\omega} _ {t} + \mathbf {b} _ {w _ {t}} + \mathbf {n} _ {w}.} \end{array}\tag{1}
$$

IMU measurements, which are measured in the body frame, combines the force for countering gravity and the platform dynamics, and are affected by acceleration bias $\mathbf { b } _ { a } ,$ gyroscope bias $\mathbf { b } _ { w }$ , and additive noise. We assume that the additive noise in acceleration and gyroscope measurements are Gaussian, $\mathbf { n } _ { a } \sim \mathcal { N } ( \mathbf { 0 } , \pmb { \sigma } _ { a } ^ { 2 } ) , \mathbf { n } _ { w } \sim \mathcal { N } ( \mathbf { 0 } , \pmb { \sigma } _ { w } ^ { 2 } )$ . Acceleration bias and gyroscope bias are modeled as random walk, whose derivatives are Gaussian, $\mathbf { n } _ { b _ { a } } \sim \mathcal { N } ( \mathbf { 0 } , \pmb { \sigma } _ { b _ { a } } ^ { 2 } ) ,   \mathbf { n } _ { b _ { w } } \sim \mathcal { N } ( \mathbf { 0 } , \pmb { \sigma } _ { b _ { w } } ^ { 2 } )$

$$
\dot {\mathbf {b}} _ {a _ {t}} = \mathbf {n} _ {b _ {a}}, \quad \dot {\mathbf {b}} _ {w _ {t}} = \mathbf {n} _ {b _ {w}}.\tag{2}
$$

Given two time instants that correspond to image frames $b _ { k }$ and $b _ { k + 1 }$ , position, velocity, and orientation states can be propagated by inertial measurements during time interval $[ t _ { k } , t _ { k + 1 } ]$ in the world frame:

$$
\begin{array}{l} \mathbf {p} _ {b _ {k + 1}} ^ {w} = \mathbf {p} _ {b _ {k}} ^ {w} + \mathbf {v} _ {b _ {k}} ^ {w} \Delta t _ {k} \\ \qquad \qquad + \iint_ {t \in [ t _ {k}, t _ {k + 1} ]} \left(\mathbf {R} _ {t} ^ {w} (\hat {\mathbf {a}} _ {t} - \mathbf {b} _ {a _ {t}} - \mathbf {n} _ {a}) - \mathbf {g} ^ {w}\right) d t ^ {2} \\ \mathbf {v} _ {b _ {k + 1}} ^ {w} = \mathbf {v} _ {b _ {k}} ^ {w} + \int_ {t \in [ t _ {k}, t _ {k + 1} ]} \left(\mathbf {R} _ {t} ^ {w} (\hat {\mathbf {a}} _ {t} - \mathbf {b} _ {a _ {t}} - \mathbf {n} _ {a}) - \mathbf {g} ^ {w}\right) d t \\ \mathbf {q} _ {b _ {k + 1}} ^ {w} = \mathbf {q} _ {b _ {k}} ^ {w} \otimes \int_ {t \in [ t _ {k}, t _ {k + 1} ]} \frac {1}{2} \boldsymbol {\Omega} (\hat {\boldsymbol {\omega}} _ {t} - \mathbf {b} _ {w _ {t}} - \mathbf {n} _ {w}) \mathbf {q} _ {t} ^ {b _ {k}} d t, \end{array}\tag{3}
$$

where

$$
\boldsymbol {\Omega} (\boldsymbol {\omega}) = \left[ \begin{array}{c c} - \lfloor \boldsymbol {\omega} \rfloor_ {\times} & \boldsymbol {\omega} \\ - \boldsymbol {\omega} ^ {T} & 0 \end{array} \right], \lfloor \boldsymbol {\omega} \rfloor_ {\times} = \left[ \begin{array}{c c c} 0 & - \omega_ {z} & \omega_ {y} \\ \omega_ {z} & 0 & - \omega_ {x} \\ - \omega_ {y} & \omega_ {x} & 0 \end{array} \right].\tag{4}
$$

$\Delta t _ { k }$ is the duration between the time interval $[ t _ { k } , t _ { k + 1 } ]$

It can be seen that the IMU state propagation requires rotation, position and velocity of frame $b _ { k } .$ When these starting states change, we need to re-propagate IMU measurements. Especially in the optimization-based algorithm, every time we adjust poses, we will need to re-propagate IMU measurements between them. This propagation strategy is computationally demanding. To avoid re-propagation, we adopt pre-integration algorithm.

After change the reference frame from the world frame to the local frame $b _ { k } ,$ , we can only pre-integrate the parts which are related to linear acceleration â and angular velocity ωˆ as follows:

$$
\begin{array}{c} \mathbf {R} _ {w} ^ {b _ {k}} \mathbf {p} _ {b _ {k + 1}} ^ {w} = \mathbf {R} _ {w} ^ {b _ {k}} (\mathbf {p} _ {b _ {k}} ^ {w} + \mathbf {v} _ {b _ {k}} ^ {w} \Delta t _ {k} - \frac {1}{2} \mathbf {g} ^ {w} \Delta t _ {k} ^ {2}) + \boldsymbol {\alpha} _ {b _ {k + 1}} ^ {b _ {k}} \\ \mathbf {R} _ {w} ^ {b _ {k}} \mathbf {v} _ {b _ {k + 1}} ^ {w} = \mathbf {R} _ {w} ^ {b _ {k}} (\mathbf {v} _ {b _ {k}} ^ {w} - \mathbf {g} ^ {w} \Delta t _ {k}) + \boldsymbol {\beta} _ {b _ {k + 1}} ^ {b _ {k}} \\ \mathbf {q} _ {w} ^ {b _ {k}} \otimes \mathbf {q} _ {b _ {k + 1}} ^ {w} = \boldsymbol {\gamma} _ {b _ {k + 1}} ^ {b _ {k}}, \end{array}\tag{5}
$$

<!-- page 5 of 17 -->

5

![Image block](images/qin2018_vins-mono_p5_b2.png)

Fig. 3. An illustration of the sliding window monocular VIO with relocalization. It is a tightly-coupled formulation with IMU, visual, and loop measurements.

where,

$$
\left| \begin{array}{l} \boldsymbol {\alpha} _ {b _ {k + 1}} ^ {b _ {k}} = \iint_ {t \in [ t _ {k}, t _ {k + 1} ]} \mathbf {R} _ {t} ^ {b _ {k}} (\hat {\mathbf {a}} _ {t} - \mathbf {b} _ {a _ {t}} - \mathbf {n} _ {a}) d t ^ {2} \\ \beta_ {b _ {k + 1}} ^ {b _ {k}} = \int_ {t \in [ t _ {k}, t _ {k + 1} ]} \mathbf {R} _ {t} ^ {b _ {k}} (\hat {\mathbf {a}} _ {t} - \mathbf {b} _ {a _ {t}} - \mathbf {n} _ {a}) d t \\ \boldsymbol {\gamma} _ {b _ {k + 1}} ^ {b _ {k}} = \int_ {t \in [ t _ {k}, t _ {k + 1} ]} \frac {1}{2} \boldsymbol {\Omega} (\hat {\boldsymbol {\omega}} _ {t} - \mathbf {b} _ {w _ {t}} - \mathbf {n} _ {w}) \boldsymbol {\gamma} _ {t} ^ {b _ {k}} d t. \end{array} \right.\tag{6}
$$

It can be seen that the pre-integration terms (6) can be obtained solely with IMU measurements by taking $b _ { k }$ as the reference frame. $\alpha _ { b _ { k + 1 } } ^ { b _ { k } } , \beta _ { b _ { k + 1 } } ^ { b _ { k } } , \gamma _ { b _ { k + 1 } } ^ { b _ { k } }$ are only related to IMU biases instead of other states in $b _ { k }$ and $b _ { k + 1 }$ . When the estimation of bias changes, if the change is small, we adjust $\alpha_{b_{k + 1}}^{b_{k}}, \beta_{b_{k + 1}}^{b_{k}}, \gamma_{b_{k + 1}}^{b_{k}}$ by their first-order approximations with respect to the bias, otherwise we do re-propagation. This strategy saves a significant amount of computational resources for optimization-based algorithms, since we do not need to propagate IMU measurements repeatedly.

For discrete-time implementation, different numerical integration methods such as Euler, mid-point, RK4 integration can be applied. Here Euler integration is chosen to demonstrate the procedure for easy understanding (we use mid-point integration in the implementation code).

At the beginning, $\pmb { \alpha } _ { b _ { k } } ^ { b _ { k } } , \pmb { \beta } _ { b _ { k } } ^ { b _ { k } }$ is 0, and $\gamma _ { b _ { k } } ^ { b _ { k } }$ is identity quaternion. The mean of $\alpha , \beta , \gamma$ in (6) is propagated step by step as follows. Note that the additive noise terms $\mathbf { n } _ { a } , \mathbf { n } _ { w }$ are unknown, and is treated as zero in the implementation. This results in estimated values of the pre-integration terms, marked by ˆ(·):

$$
\begin{array}{l} \hat {\boldsymbol {\alpha}} _ {i + 1} ^ {b _ {k}} = \hat {\boldsymbol {\alpha}} _ {i} ^ {b _ {k}} + \hat {\boldsymbol {\beta}} _ {i} ^ {b _ {k}} \delta t + \frac {1}{2} \mathbf {R} (\hat {\boldsymbol {\gamma}} _ {i} ^ {b _ {k}}) (\hat {\mathbf {a}} _ {i} - \mathbf {b} _ {a _ {i}}) \delta t ^ {2} \\ \hat {\boldsymbol {\beta}} _ {i + 1} ^ {b _ {k}} = \hat {\boldsymbol {\beta}} _ {i} ^ {b _ {k}} + \mathbf {R} (\hat {\boldsymbol {\gamma}} _ {i} ^ {b _ {k}}) (\hat {\mathbf {a}} _ {i} - \mathbf {b} _ {a _ {i}}) \delta t \\ \hat {\boldsymbol {\gamma}} _ {i + 1} ^ {b _ {k}} = \hat {\boldsymbol {\gamma}} _ {i} ^ {b _ {k}} \otimes \left[ \begin{array}{c} 1 \\ \frac {1}{2} (\hat {\boldsymbol {\omega}} _ {i} - \mathbf {b} _ {w _ {i}}) \delta t \end{array} \right] \end{array} .\tag{7}
$$

i is discrete moment corresponding to a IMU measurement within $[ t _ { k } , t _ { k + 1 } ]$ . δt is the time interval between two IMU measurements i and $i + 1$

Then we deal with the covariance propagation. Since the four-dimensional rotation quaternion $\tilde { \gamma _ { t } ^ { b _ { k } } }$ is overparameterized, we define its error term as a perturbation around its mean:

$$
\boldsymbol {\gamma} _ {t} ^ {b _ {k}} \approx \hat {\boldsymbol {\gamma}} _ {t} ^ {b _ {k}} \otimes \left[ \begin{array}{c} 1 \\ \frac {1}{2} \delta \boldsymbol {\theta} _ {t} ^ {b _ {k}} \end{array} \right],\tag{8}
$$

where $\delta \pmb { \theta } _ { t } ^ { b _ { k } }$ is three-dimensional small perturbation.

We can derive continuous-time linearized dynamics of error terms of (6):

$$
\left[ \begin{array}{c} \delta \dot {\boldsymbol {\alpha}} _ {t} ^ {b _ {k}} \\ \delta \dot {\boldsymbol {\beta}} _ {t} ^ {b _ {k}} \\ \delta \dot {\boldsymbol {\theta}} _ {t} ^ {b _ {k}} \\ \delta \dot {\mathbf {b}} _ {a _ {t}} \\ \delta \dot {\mathbf {b}} _ {w _ {t}} \end{array} \right] = \left[ \begin{array}{c c c c c} 0 & \mathbf {I} & 0 & 0 & 0 \\ 0 & 0 & - \mathbf {R} _ {t} ^ {b _ {k}} \lfloor \hat {\mathbf {a}} _ {t} - \mathbf {b} _ {a _ {t}} \rfloor_ {\times} & - \mathbf {R} _ {t} ^ {b _ {k}} & 0 \\ 0 & 0 & - \lfloor \hat {\boldsymbol {\omega}} _ {t} - \mathbf {b} _ {w _ {t}} \rfloor_ {\times} & 0 & - \mathbf {I} \\ 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 \end{array} \right] \left[ \begin{array}{c} \delta \boldsymbol {\alpha} _ {t} ^ {b _ {k}} \\ \delta \boldsymbol {\beta} _ {t} ^ {b _ {k}} \\ \delta \boldsymbol {\theta} _ {t} ^ {b _ {k}} \\ \delta \mathbf {b} _ {a _ {t}} \\ \delta \mathbf {b} _ {w _ {t}} \end{array} \right]
$$

$$
+ \left[ \begin{array}{c c c c} 0 & 0 & 0 & 0 \\ - \mathbf {R} _ {t} ^ {b _ {k}} & 0 & 0 & 0 \\ 0 & - \mathbf {I} & 0 & 0 \\ 0 & 0 & \mathbf {I} & 0 \\ 0 & 0 & 0 & \mathbf {I} \end{array} \right] \left[ \begin{array}{c} \mathbf {n} _ {a} \\ \mathbf {n} _ {w} \\ \mathbf {n} _ {b _ {a}} \\ \mathbf {n} _ {b _ {w}} \end{array} \right] = \mathbf {F} _ {t} \delta \mathbf {z} _ {t} ^ {b _ {k}} + \mathbf {G} _ {t} \mathbf {n} _ {t},\tag{9}
$$

$\mathbf { P } _ { b _ { k + 1 } } ^ { b _ { k } }$ can be computed recursively by first-order discrete-time covariance update with the initial covariance $\mathbf { P } _ { b _ { k } } ^ { b _ { k } } = \mathbf { 0 } ;$

$$
\begin{array}{c} \mathbf {P} _ {t + \delta t} ^ {b _ {k}} = (\mathbf {I} + \mathbf {F} _ {t} \delta t) \mathbf {P} _ {t} ^ {b _ {k}} (\mathbf {I} + \mathbf {F} _ {t} \delta t) ^ {T} + (\mathbf {G} _ {t} \delta t) \mathbf {Q} (\mathbf {G} _ {t} \delta t) ^ {T}, \\ \hline t \in [ k, k + 1 ], \end{array}\tag{10}
$$

where $\mathbf { Q }$ is the diagonal covariance matrix of noise $( \pmb { \sigma } _ { a } ^ { 2 } , \pmb { \sigma } _ { w } ^ { 2 } , \pmb { \sigma } _ { b _ { a } } ^ { 2 } , \pmb { \sigma } _ { b _ { w } } ^ { 2 } )$

Meanwhile, the first-order Jacobian matrix $\mathbf { J } _ { b _ { k + 1 } }$ of $\delta \mathbf { z } _ { b _ { k + 1 } } ^ { b _ { k } }$ with respect to $\delta \mathbf { z } _ { b _ { k } } ^ { b _ { k } }$ can be also compute recursively with the initial Jacobian $\mathbf { J } _ { b _ { k } } \overset { \cdot \cdot } { = } \mathbf { I }$

$$
\mathbf {J} _ {t + \delta t} = (\mathbf {I} + \mathbf {F} _ {t} \delta t) \mathbf {J} _ {t}, t \in [ k, k + 1 ].\tag{11}
$$

Using this recursive formulation, we get the covariance matrix $\mathbf { P } _ { b _ { k + 1 } } ^ { b _ { k } }$ and the Jacobian $\mathbf { J } _ { b _ { k + 1 } }$ . The first order approximation of $\mathbf{\alpha}_{b_{k+1}}^{\tau}, \mathbf{\beta}_{b_{k+1}}^{b_k}, \mathbf{\gamma}_{b_{k+1}}^{b_k}$ with respect to biases can be write as:

$$
\begin{array}{c} \boldsymbol {\alpha} _ {b _ {k + 1}} ^ {b _ {k}} \approx \hat {\boldsymbol {\alpha}} _ {b _ {k + 1}} ^ {b _ {k}} + \mathbf {J} _ {b _ {a}} ^ {\alpha} \delta \mathbf {b} _ {a _ {k}} + \mathbf {J} _ {b _ {w}} ^ {\alpha} \delta \mathbf {b} _ {w _ {k}} \\ \boldsymbol {\beta} _ {b _ {k + 1}} ^ {b _ {k}} \approx \hat {\boldsymbol {\beta}} _ {b _ {k + 1}} ^ {b _ {k}} + \mathbf {J} _ {b _ {a}} ^ {\beta} \delta \mathbf {b} _ {a _ {k}} + \mathbf {J} _ {b _ {w}} ^ {\beta} \delta \mathbf {b} _ {w _ {k}} \\ \boldsymbol {\gamma} _ {b _ {k + 1}} ^ {b _ {k}} \approx \hat {\boldsymbol {\gamma}} _ {b _ {k + 1}} ^ {b _ {k}} \otimes \left[ \begin{array}{c} 1 \\ \frac {1}{2} \mathbf {J} _ {b _ {w}} ^ {\gamma} \delta \mathbf {b} _ {w _ {k}} \end{array} \right] \end{array}\tag{12}
$$

where $\mathbf { J } _ { b _ { a } } ^ { \alpha }$ and is the sub-block matrix in $\mathbf { J } _ { b _ { k + 1 } }$ whose location is corresponding to $\frac { \delta \mathbf { \alpha } _ { b _ { k + 1 } } ^ { b _ { k } } } { \delta \mathbf { b } _ { a _ { k } } }$ . The same meaning is also used for $\mathbf { J } _ { b _ { w } } ^ { \alpha } , \mathbf { J } _ { b _ { a } } ^ { \beta } , \mathbf { J } _ { b _ { w } } ^ { \beta } , \mathbf { J } _ { b _ { w } } ^ { \gamma }$ . When the estimation of bias changes

<!-- page 6 of 17 -->

6

![Image block](images/qin2018_vins-mono_p6_b2.png)

Fig. 4. An illustration of the visual-inertial alignment process for estimator initialization.

slightly, we use (12) to correct pre-integration results approximately instead of re-propagation.

Now we are able to write down the IMU measurement model with its corresponding covariance $\mathbf { P } _ { b _ { k + 1 } } ^ { b _ { k } }$

$$
\left[ \begin{array}{c} \hat {\boldsymbol {\alpha}} _ {b _ {k + 1}} ^ {b _ {k}} \\ \hat {\boldsymbol {\beta}} _ {b _ {k + 1}} ^ {b _ {k}} \\ \hat {\boldsymbol {\gamma}} _ {b _ {k + 1}} ^ {b _ {k}} \\ \mathbf {0} \\ \mathbf {0} \end{array} \right] = \left[ \begin{array}{c} \mathbf {R} _ {w} ^ {b _ {k}} (\mathbf {p} _ {b _ {k + 1}} ^ {w} - \mathbf {p} _ {b _ {k}} ^ {w} + \frac {1}{2} \mathbf {g} ^ {w} \Delta t _ {k} ^ {2} - \mathbf {v} _ {b _ {k}} ^ {w} \Delta t _ {k}) \\ \mathbf {R} _ {w} ^ {b _ {k}} (\mathbf {v} _ {b _ {k + 1}} ^ {w} + \mathbf {g} ^ {w} \Delta t _ {k} - \mathbf {v} _ {b _ {k}} ^ {w}) \\ \mathbf {q} _ {b _ {k}} ^ {w ^ {- 1}} \otimes \mathbf {q} _ {b _ {k + 1}} ^ {w} \\ \mathbf {b} _ {a b _ {k + 1}} - \mathbf {b} _ {a b _ {k}} \\ \mathbf {b} _ {w b _ {k + 1}} - \mathbf {b} _ {w b _ {k}} \end{array} \right].\tag{13}
$$

## V. ESTIMATOR INITIALIZATION

Monocular tightly-coupled visual-inertial odometry is a highly nonlinear system. Since the scale is not directly observable from a monocular camera, it is hard to directly fuse these two measurements without good initial values. One may assume a stationary initial condition to start the monocular VINS estimator. However, this assumption is inappropriate as initialization under motion is frequently encountered in real-world applications. The situation becomes even more complicated when IMU measurements are corrupted by large bias. In fact, initialization is usually the most fragile step for monocular VINS. A robust initialization procedure is needed to ensure the applicability of the system.

We adopt a loosely-coupled sensor fusion method to get initial values. We find that vision-only SLAM, or Structure from Motion (SfM), has a good property of initialization. In most cases, a visual-only system can bootstrap itself by derived initial values from relative motion methods, such as the eight-point [32] or five-point [33] algorithms, or estimating the homogeneous matrices. By aligning metric IMU pre-integration with the visual-only SfM results, we can roughly recover scale, gravity, velocity, and even bias. This is sufficient for bootstrapping a nonlinear monocular VINS estimator, as shown in Fig. 4.

In contrast to [17], which simultaneously estimates gyroscope and accelerometer bias during the initialization phase, we choose to ignore accelerometer bias terms in the initial step. Accelerometer bias is coupled with gravity, and due to the large magnitude of the gravity vector comparing to platform dynamics, and the relatively short during of the initialization phase, these bias terms are hard to be observed. A detailed analysis of accelerometer bias calibration is presented in our previous work [34].

## A. Sliding Window Vision-Only SfM

The initialization procedure starts with a vision-only SfM to estimate a graph of up-to-scale camera poses and feature positions.

We maintain a sliding window of frames for bounded computational complexity. Firstly, we check feature correspondences between the latest frame and all previous frames. If we can find stable feature tracking (more than 30 tracked features) and sufficient parallax (more than 20 rotation-compensated pixels) between the latest frame and any other frames in the sliding window. we recover the relative rotation and up-to-scale translation between these two frames using the Five-point algorithm [33]. Otherwise, we keep the latest frame in the window and wait for new frames. If the five-point algorithm success, we arbitrarily set the scale and triangulate all features observed in these two frames. Based on these triangulated features, a perspective-n-point (PnP) method [35] is performed to estimate poses of all other frames in the window. Finally, a global full bundle adjustment [36] is applied to minimize the total reprojection error of all feature observations. Since we do not yet have any knowledge about the world frame, we set the first camera frame $( \cdot ) ^ { c _ { 0 } }$ as the reference frame for SfM. All frame poses $( \bar { \mathbf { p } } _ { c _ { k } } ^ { c _ { 0 } } , \mathbf { q } _ { c _ { k } } ^ { c _ { 0 } } )$ and feature positions are represented with respect to $\tilde { ( \cdot ) } ^ { c _ { 0 } }$ . Suppose we have a rough measure extrinsic parameters $( \mathbf { p } _ { c } ^ { b } , \mathbf { q } _ { c } ^ { b } )$ between the camera and the IMU, we can translate poses from camera frame to body (IMU) frame,

$$
\begin{array}{c} \mathbf {q} _ {b _ {k}} ^ {c _ {0}} = \mathbf {q} _ {c _ {k}} ^ {c _ {0}} \otimes (\mathbf {q} _ {c} ^ {b}) ^ {- 1} \\ s \bar {\mathbf {p}} _ {b _ {k}} ^ {c _ {0}} = s \bar {\mathbf {p}} _ {c _ {k}} ^ {c _ {0}} - \mathbf {R} _ {b _ {k}} ^ {c _ {0}} \mathbf {p} _ {c} ^ {b}, \end{array}\tag{14}
$$

where s the scaling parameter that aligns the visual structure to the metric scale. Solving this scaling parameter is the key to achieve successful initialization.

## B. Visual-Inertial Alignment

1) Gyroscope Bias Calibration: Consider two consecutive frames $b _ { k }$ and $b _ { k + 1 }$ in the window, we get the rotation $\mathbf { q } _ { b _ { k } } ^ { c _ { 0 } }$ and $\mathbf { q } _ { b _ { k + 1 } } ^ { c _ { 0 } }$ from the visual SfM, as well as the relative constraint $\hat { \boldsymbol { \gamma } } _ { b _ { k + 1 } } ^ { b _ { k } }$ from IMU pre-integration. We linearize the IMU pre-integration term with respect to gyroscope bias and minimize the following cost function:

$$
\begin{array}{c} \min _ {\delta b _ {w}} \sum_ {k \in \mathcal {B}} \left\| \mathbf {q} _ {b _ {k + 1}} ^ {- 1} \otimes \mathbf {q} _ {b _ {k}} ^ {c _ {0}} \otimes \boldsymbol {\gamma} _ {b _ {k + 1}} ^ {b _ {k}} \right\| ^ {2} \\ \hline \boldsymbol {\gamma} _ {b _ {k + 1}} ^ {b _ {k}} \approx \hat {\boldsymbol {\gamma}} _ {b _ {k + 1}} ^ {b _ {k}} \otimes \left[ \begin{array}{c} 1 \\ \frac {1}{2} \mathbf {J} _ {b _ {w}} ^ {\gamma} \delta \mathbf {b} _ {w} \end{array} \right], \end{array}\tag{15}
$$

where $\mathcal { B }$ indexes all frames in the window. We have the first order approximation of $\hat { \gamma } _ { b _ { k + 1 } } ^ { b _ { k } }$ with respect to the gyroscope bias using the bias Jacobian derived in Sect. IV-B. In such way, we get an initial calibration of the gyroscope bias $\mathbf { b } _ { w } .$ Then we re-propagate all IMU pre-integration terms $\hat { \alpha } _ { b _ { k + 1 } } ^ { b _ { k } } , \hat { \beta } _ { b _ { k + 1 } } ^ { b _ { k } } ,$ and $\hat { \gamma } _ { b _ { k - } } ^ { b _ { k } }$ using the new gyroscope bias. +1

2) Velocity, Gravity Vector and Metric Scale Initialization: After the gyroscope bias is initialized, we move on to initialize

<!-- page 7 of 17 -->

7

![Image block](images/qin2018_vins-mono_p7_b2.png)

Fig. 5. Illustration of 2 DOF parameterization of gravity. Since the magnitude of gravity is known, g lies on a sphere with radius $\stackrel { \leftrightarrow } { g }   \approx   9 . 8 1 m / \stackrel { \leftrightarrow } { s ^ { 2 } }$ . The gravity is parameterized around current estimate as $g \cdot { \hat { \bar { \mathbf { g } } } } \cdot$ + w<sub>1</sub>b<sub>1</sub> + w<sub>2</sub>b<sub>2</sub>, where b<sub>1</sub> and b<sub>2</sub> are two orthogonal basis spanning the tangent space.

other essential states for navigation, namely velocity, gravity vector, and metric scale:

$$
\mathcal {X} _ {I} = \left[ \mathbf {v} _ {b _ {0}} ^ {b _ {0}}, \mathbf {v} _ {b _ {1}} ^ {b _ {1}}, \dots \mathbf {v} _ {b _ {n}} ^ {b _ {n}}, \mathbf {g} ^ {c _ {0}}, s \right],\tag{16}
$$

where $\mathbf { v } _ { b _ { k } } ^ { b _ { k } }$ is velocity in the body frame while taking the $k ^ { t h }$ image, $\mathbf { g } ^ { \tilde { c } _ { 0 } }$ is the gravity vector in the $c _ { 0 }$ frame, and s scales the monocular SfM to metric units.

Consider two consecutive frames $b _ { k }$ and $b _ { k + 1 }$ in the window, then (5) can be written as:

$$
\left| \begin{array}{l} \boldsymbol {\alpha} _ {b _ {k + 1}} ^ {b _ {k}} = \mathbf {R} _ {c _ {0}} ^ {b _ {k}} (s (\bar {\mathbf {p}} _ {b _ {k + 1}} ^ {c _ {0}} - \bar {\mathbf {p}} _ {b _ {k}} ^ {c _ {0}}) + \frac {1}{2} \mathbf {g} ^ {c _ {0}} \Delta t _ {k} ^ {2} - \mathbf {R} _ {b _ {k}} ^ {c _ {0}} \mathbf {v} _ {b _ {k}} ^ {b _ {k}} \Delta t _ {k}) \\ \boldsymbol {\beta} _ {b _ {k + 1}} ^ {b _ {k}} = \mathbf {R} _ {c _ {0}} ^ {b _ {k}} (\mathbf {R} _ {b _ {k + 1}} ^ {c _ {0}} \mathbf {v} _ {b _ {k + 1}} ^ {b _ {k + 1}} + \mathbf {g} ^ {c _ {0}} \Delta t _ {k} - \mathbf {R} _ {b _ {k}} ^ {c _ {0}} \mathbf {v} _ {b _ {k}} ^ {b _ {k}}). \end{array} \right|\tag{17}
$$

We can combine (14) and (17) into the following linear measurement model:

$$
\hat {\mathbf {z}} _ {b _ {k + 1}} ^ {b _ {k}} = \left[ \begin{array}{c} \hat {\boldsymbol {\alpha}} _ {b _ {k + 1}} ^ {b _ {k}} - \mathbf {p} _ {c} ^ {b} + \mathbf {R} _ {c _ {0}} ^ {b _ {k}} \mathbf {R} _ {b _ {k + 1}} ^ {c _ {0}} \mathbf {p} _ {c} ^ {b} \\ \hat {\boldsymbol {\beta}} _ {b _ {k + 1}} ^ {b _ {k}} \end{array} \right] = \mathbf {H} _ {b _ {k + 1}} ^ {b _ {k}} \mathcal {X} _ {I} + \mathbf {n} _ {b _ {k + 1}} ^ {b _ {k}}\tag{18}
$$

where,

$$
\mathbf {H} _ {b _ {k + 1}} ^ {b _ {k}} = \left[ \begin{array}{c c c c} - \mathbf {I} \Delta t _ {k} & \mathbf {0} & \frac {1}{2} \mathbf {R} _ {c _ {0}} ^ {b _ {k}} \Delta t _ {k} ^ {2} & \mathbf {R} _ {c _ {0}} ^ {b _ {k}} (\bar {\mathbf {p}} _ {c _ {k + 1}} ^ {c _ {0}} - \bar {\mathbf {p}} _ {c _ {k}} ^ {c _ {0}}) \\ - \mathbf {I} & \mathbf {R} _ {c _ {0}} ^ {b _ {k}} \mathbf {R} _ {b _ {k + 1}} ^ {c _ {0}} & \mathbf {R} _ {c _ {0}} ^ {b _ {k}} \Delta t _ {k} & \mathbf {0} \end{array} \right]\tag{19}
$$

It can be seen that $\mathbf { R } _ { b _ { k } } ^ { c _ { 0 } } , \mathbf { R } _ { b _ { k + 1 } } ^ { c _ { 0 } } , \bar { \mathbf { p } } _ { c _ { k } } ^ { c _ { 0 } } , \bar { \mathbf { p } } _ { c _ { k + 1 } } ^ { c _ { 0 } }$ are obtained from the up-to-scale monocular visual SfM. $\Delta t _ { k }$ is the time interval between two consecutive frames. By solving this linear least square problem:

$$
\min _ {\mathcal {X} _ {I}} \sum_ {k \in \mathcal {B}} \left\| \hat {\mathbf {z}} _ {b _ {k + 1}} ^ {b _ {k}} - \mathbf {H} _ {b _ {k + 1}} ^ {b _ {k}} \mathcal {X} _ {I} \right\| ^ {2},\tag{20}
$$

we can get body frame velocities for every frame in the window, the gravity vector in the visual reference frame $( \cdot ) ^ { c _ { 0 } }$ as well as the scale parameter.

3) Gravity Refinement: The gravity vector obtained from the previous linear initialization step can be refined by constraining the magnitude. In most cases, the magnitude of gravity vector is known. This results in only 2 DOF remaining for the gravity vector. We therefore re-parameterize the gravity with two variables on its tangent space. Our parameterization represents the gravity vector as $g \cdot \bar { \hat { \mathbf { g } } } + w _ { 1 } \mathbf { b } _ { 1 } + w _ { 2 } \mathbf { b } _ { 2 }$ , where $g$ is the know magnitude of the gravity, $\hat { \bf g }$ is a unit vector representing the gravity direction. $\mathbf { b } _ { 1 }$ and $\mathbf { b } _ { 2 }$ are two orthogonal basis spanning the tangent plane, as shown in Fig. 5. w<sub>1</sub>

and $w _ { 2 }$ are corresponding displacements towards $\mathbf { b } _ { 1 }$ and $\mathbf { b } _ { 2 } ,$ respectively. We can find one set of $\mathbf { b } _ { 1 } ,   \mathbf { b } _ { 2 }$ by cross products operations using Algorithm 1. Then we substitute $\mathbf { g }$ in (17) by $g \cdot \hat { \bar { \mathbf { g } } } + w _ { 1 } \mathbf { b } _ { 1 } + w _ { 2 } \mathbf { b } _ { 2 }$ , and solve for $w _ { 1 }$ and $w _ { 2 }$ together with other state variables. This process iterates until $\hat { \bf g }$ converges.

<div class="docvortex-algorithm" style="white-space: pre-wrap; font-family:monospace;">
Algorithm 1: Finding $\mathbf{b}_1$ and $\mathbf{b}_2$
if $\hat{\mathbf{g}} \neq [1, 0, 0]$ then
    $\mathbf{b}_1 \leftarrow normalize(\hat{\mathbf{g}} \times [1, 0, 0])$;
else
    $\mathbf{b}_1 \leftarrow normalize(\hat{\mathbf{g}} \times [0, 0, 1])$;
end
$\mathbf{b}_2 \leftarrow \hat{\mathbf{g}} \times \mathbf{b}_1$;
</div>

4) Completing Initialization: After refining the gravity vector, we can get the rotation $\mathbf { q } _ { c _ { 0 } } ^ { w }$ between the world frame and the camera frame $c _ { 0 }$ by rotating the gravity to the z-axis. We then rotate all variables from reference frame $( \cdot ) ^ { c _ { 0 } }$ <sub>to</sub> the world frame $( \cdot ) ^ { w }$ . The body frame velocities will also be rotated to world frame. Translational components from the visual SfM will be scaled to metric units. At this point, the initialization procedure is completed and all these metric values will be fed for a tightly-coupled monocular VIO.

## VI. TIGHTLY-COUPLED MONOCULAR VIO

After estimator initialization, we proceed with a sliding window-based tightly-coupled monocular VIO for highaccuracy and robust state estimation. An illustration of the sliding window formulation is shown in Fig. 3.

## A. Formulation

The full state vector in the sliding window is defined as:

$$
\begin{array}{l} \mathcal {X} = \left[ \mathbf {x} _ {0}, \mathbf {x} _ {1}, \dots \mathbf {x} _ {n}, \mathbf {x} _ {c} ^ {b}, \lambda_ {0}, \lambda_ {1}, \dots \lambda_ {m} \right] \\ \mathbf {x} _ {k} = \left[ \mathbf {p} _ {b _ {k}} ^ {w}, \mathbf {v} _ {b _ {k}} ^ {w}, \mathbf {q} _ {b _ {k}} ^ {w}, \mathbf {b} _ {a}, \mathbf {b} _ {g} \right], k \in [ 0, n ] \\ \mathbf {x} _ {c} ^ {b} = \left[ \mathbf {p} _ {c} ^ {b}, \mathbf {q} _ {c} ^ {b} \right], \end{array}\tag{21}
$$

where $\mathbf { x } _ { k }$ is the IMU state at the time that the $k ^ { t h }$ image is captured. It contains position, velocity, and orientation of the IMU in the world frame, and acceleration bias and gyroscope bias in the IMU body frame. n is the total number of keyframes, and $m$ is the total number of features in the sliding window. $\lambda _ { l }$ is the inverse depth of the $l ^ { t h }$ feature from its first observation.

We use a visual-inertial bundle adjustment formulation. We minimize the sum of prior and the Mahalanobis norm of all measurement residuals to obtain a maximum posteriori estimation:

$$
\left| \begin{array}{c} \min _ {\mathcal {X}} \left\{\| \mathbf {r} _ {p} - \mathbf {H} _ {p} \mathcal {X} \| ^ {2} + \sum_ {k \in \mathcal {B}} \left\| \mathbf {r} _ {\mathcal {B}} (\hat {\mathbf {z}} _ {b _ {k + 1}} ^ {b _ {k}}, \mathcal {X}) \right\| _ {\mathbf {P} _ {b _ {k + 1}} ^ {b _ {k}}} ^ {2} + \right. \\ \left. \sum_ {(l, j) \in \mathcal {C}} \rho (\left\| \mathbf {r} _ {\mathcal {C}} (\hat {\mathbf {z}} _ {l} ^ {c _ {j}}, \mathcal {X}) \right\| _ {\mathbf {P} _ {l} ^ {c _ {j}}} ^ {2}) \right\}, \end{array} \right.\tag{22}
$$

where the Huber norm [37] is defined as:

$$
\rho (s) = \left\{ \begin{array}{l l} 1 & s \geq 1, \\ 2 \sqrt {s} - 1 & s <   1. \end{array} \right.\tag{23}
$$

<!-- page 8 of 17 -->

8

$\mathbf { r } _ { \mathcal { B } } ( \hat { \mathbf { z } } _ { b _ { k + 1 } } ^ { b _ { k } } ,   \mathcal { X } )$ and $\mathbf { r } _ { \mathcal { C } } ( \hat { \mathbf { z } } _ { l } ^ { c _ { j } } ,   \mathcal { X } )$ are residuals for IMU and visual measurements respectively. Detailed definition of the residual terms will be presented in Sect. VI-B and Sect. VI-C. B is the set of all IMU measurements, $\mathcal { C }$ is the set of features which have been observed at least twice in the current sliding window. $\{ \mathbf { r } _ { p } ,   \mathbf { H } _ { p } \}$ is the prior information from marginalization. Ceres Solver [38] is used for solving this nonlinear problem.

## B. IMU Measurement Residual

Consider the IMU measurements within two consecutive frames $b _ { k }$ and $b _ { k + 1 }$ in the sliding window, according to the IMU measurement model defined in (13), the residual for pre-integrated IMU measurement can be defined as:

$$
\begin{array}{l} \mathbf {r} _ {\mathcal {B}} (\hat {\mathbf {z}} _ {b _ {k + 1}} ^ {b _ {k}}, \mathcal {X}) = \left[ \begin{array}{c} \delta \boldsymbol {\alpha} _ {b _ {k + 1}} ^ {b _ {k}} \\ \delta \boldsymbol {\beta} _ {b _ {k + 1}} ^ {b _ {k}} \\ \delta \boldsymbol {\theta} _ {b _ {k + 1}} ^ {b _ {k}} \\ \delta \mathbf {b} _ {a} \\ \delta \mathbf {b} _ {g} \end{array} \right] \\ = \left[ \begin{array}{c} \mathbf {R} _ {w} ^ {b _ {k}} (\mathbf {p} _ {b _ {k + 1}} ^ {w} - \mathbf {p} _ {b _ {k}} ^ {w} + \frac {1}{2} \mathbf {g} ^ {w} \Delta t _ {k} ^ {2} - \mathbf {v} _ {b _ {k}} ^ {w} \Delta t _ {k}) - \hat {\boldsymbol {\alpha}} _ {b _ {k + 1}} ^ {b _ {k}} \\ \mathbf {R} _ {w} ^ {b _ {k}} (\mathbf {v} _ {b _ {k + 1}} ^ {w} + \mathbf {g} ^ {w} \Delta t _ {k} - \mathbf {v} _ {b _ {k}} ^ {w}) - \hat {\boldsymbol {\beta}} _ {b _ {k + 1}} ^ {b _ {k}} \\ 2 \left[ \mathbf {q} _ {b _ {k}} ^ {w ^ {- 1}} \otimes \mathbf {q} _ {b _ {k + 1}} ^ {w} \otimes (\hat {\boldsymbol {\gamma}} _ {b _ {k + 1}} ^ {b _ {k}}) ^ {- 1} \right] _ {x y z} \\ \mathbf {b} _ {a b _ {k + 1}} - \mathbf {b} _ {a b _ {k}} \\ \mathbf {b} _ {w b _ {k + 1}} - \mathbf {b} _ {w b _ {k}} \end{array} \right], \end{array}\tag{24}
$$

where $\left[ \cdot \right] _ { x y z }$ extracts the vector part of a quaternion q for error state representation. $\delta \pmb { \theta } _ { b _ { k + 1 } } ^ { b _ { k } }$ is the three dimensional errorstate representation of quaternion. $[ \hat { \alpha } _ { b _ { k + 1 } } ^ { b _ { k } } ,   \hat { \beta } _ { b _ { k + 1 } } ^ { b _ { k } } ,   \hat { \gamma } _ { b _ { k + 1 } } ^ { b _ { k } } ] ^ { \mathrm { T } }$ are pre-integrated IMU measurement terms using only noisy accelerometer and gyroscope measurements within the time interval between two consecutive image frames. Accelerometer and gyroscope biases are also included in the residual terms for online correction.

## C. Visual Measurement Residual

In contrast to traditional pinhole camera models that define reprojection errors on a generalized image plane, we define the camera measurement residual on a unit sphere. The optics for almost all types of cameras, including wide-angle, fisheye or omnidirectional cameras, can be modeled as a unit ray connecting the surface of a unit sphere. Consider the $l ^ { t h }$ feature that is first observed in the $i ^ { t h }$ image, the residual for the feature observation in the $j ^ { t h }$ image is defined as:

$$
\begin{array}{l} \mathbf {r} _ {\mathcal {C}} (\hat {\mathbf {z}} _ {l} ^ {c _ {j}}, \mathcal {X}) = \left[ \begin{array}{c c} \mathbf {b} _ {1} & \mathbf {b} _ {2} \end{array} \right] ^ {T} \cdot (\hat {\mathcal {P}} _ {l} ^ {c _ {j}} - \frac {\mathcal {P} _ {l} ^ {c _ {j}}}{\| \mathcal {P} _ {l} ^ {c _ {j}} \|}) \\ \hat {\hat {\mathcal {P}}} _ {l} ^ {c _ {j}} = \pi_ {c} ^ {- 1} (\left[ \begin{array}{c} \hat {u} _ {l} ^ {c _ {j}} \\ \hat {v} _ {l} ^ {c _ {j}} \end{array} \right]) \\ \mathcal {P} _ {l} ^ {c _ {j}} = \mathbf {R} _ {b} ^ {c} (\mathbf {R} _ {w} ^ {b _ {j}} (\mathbf {R} _ {b _ {i}} ^ {w} (\mathbf {R} _ {c} ^ {b} \frac {1}{\lambda_ {l}} \pi_ {c} ^ {- 1} (\left[ \begin{array}{c} u _ {l} ^ {c _ {i}} \\ v _ {l} ^ {c _ {i}} \end{array} \right]) \\ \qquad \qquad \qquad + \mathbf {p} _ {c} ^ {b}) + \mathbf {p} _ {b _ {i}} ^ {w} - \mathbf {p} _ {b _ {j}} ^ {w}) - \mathbf {p} _ {c} ^ {b}), \end{array}\tag{25}
$$

where $[ u _ { l } ^ { c _ { i } } ,   v _ { l } ^ { c _ { i } } ]$ is the first observation of the $l ^ { t h }$ feature that happens in the $i ^ { t h }$ image. $[ \hat { u } _ { l } ^ { c _ { j } } ,   \hat { v } _ { l } ^ { c _ { j } } ]$ is the observation of the

![Image block](images/qin2018_vins-mono_p8_b11.png)

Fig. 6. An illustration of the visual residual on a unit sphere. $\hat { \mathcal { P } } _ { l } ^ { c _ { j } }$ is the unit vector for the observation of the $l ^ { t h }$ feature in the $j ^ { t h }$ frame. $\mathcal { P } _ { l } ^ { c _ { j } }$ is predicted feature measurement on the unit sphere by transforming its first observation in the $i ^ { t h }$ frame to the $j ^ { t h }$ frame. The residual is defined on the tangent plane of $\hat { \bar { \mathcal { P } } } _ { l } ^ { c _ { j } }$ P¯.

![Image block](images/qin2018_vins-mono_p8_b13.png)

Fig. 7. An illustration of our marginalization strategy. If the second latest frame is a keyframe, we will keep it in the window, and marginalize the oldest frame and its corresponding visual and inertial measurements. Marginalized measurements are turned into a prior. If the second latest frame is not a keyframe, we will simply remove the frame and all its corresponding visual measurements. However, pre-integrated inertial measurements are kept for non-keyframes, and the pre-integration process is continued towards the next frame.

same feature in the $j ^ { t h }$ image. $\pi _ { c } ^ { - 1 }$ is the back projection function which turns a pixel location into a unit vector using camera intrinsic parameters. Since the degrees-of-freedom of the vision residual is two, we project the residual vector onto the tangent plane. $\mathbf { b } _ { 1 } , \mathbf { b } _ { 2 }$ are two arbitrarily selected orthogonal bases that span the tangent plane of $\hat { \mathcal { P } } _ { l } ^ { c _ { j } }$ , as shown in Fig. 6. We can find one set of $\mathbf { b } _ { 1 } , \mathbf { b } _ { 2 }$ easily, as shown in Algorithm 1. $\mathbf { P } _ { l } ^ { c _ { j } }$ , as used in (22), is the standard covariance of a fixed length in the tangent space.

## D. Marginalization

In order to bound the computational complexity of our optimization-based VIO, marginalization is incorporated. We selectively marginalize out IMU states $\mathbf { x } _ { k }$ and features $\lambda _ { l }$ from the sliding window, meanwhile convert measurements corresponding to marginalized states into a prior.

As shown in the Fig. 7, when the second latest frame is a keyframe, it will stay in the window, and the oldest frame is marginalized out with its corresponding measurements. Otherwise, if the second latest frame is a non-keyframe, we throw visual measurements and keep IMU measurements that connect to this non-keyframe. We do not marginalize out all measurements for non-keyframes in order to maintain sparsity of the system. Our marginalization scheme aims to keep spatially separated keyframes in the window. This ensures

<!-- page 9 of 17 -->

9

![Image block](images/qin2018_vins-mono_p9_b2.png)

Fig. 8. An illustration of motion-only bundle adjustment for camera-rate outputs.

sufficient parallax for feature triangulation, and maximize the probability of maintaining accelerometer measurements with large excitation.

The marginalization is carried out using the Schur complement [39]. We construct a new prior based on all marginalized measurements related to the removed state. The new prior is added onto the existing prior.

We do note that marginalization results in the early fix of linearization points, which may result in suboptimal estimation results. However, since small drifting is acceptable for VIO, we argue that the negative impact caused by marginalization is not critical.

## E. Motion-only Visual-Inertial Bundle Adjustment for Camera-Rate State Estimation

For devices with low computational power, such as mobile phones, the tightly-coupled monocular VIO cannot achieve camera-rate outputs due to the heavy computation demands for the nonlinear optimization. To this end, we employ a lightweight motion-only visual-inertial bundle adjustment to boost the state estimation to camera-rate ( 30 Hz).

The cost function for the motion-only visual-inertial bundle adjustment is the same as the one for monocular VIO in (22). However, instead of optimizing all states in the sliding window, we only optimize the poses and velocities of a fixed number of latest IMU states. We treat feature depth, extrinsic parameters, bias, and old IMU states that we do not want to optimize as constant values. We do use all visual and inertial measurements for the motion-only bundle adjustment. This results in much smoother state estimates than single frame PnP methods. An illustration of the proposed strategy is shown in Fig. 8. In contrast to the full tightly-coupled monocular VIO, which may cause more than 50ms on state-of-the-art embedded computers, the motion-only visual-inertial bundle adjustment only takes about 5ms to compute. This enables the low-latency camera-rate pose estimation that is particularly beneficial for drone and AR applications.

## F. IMU Forward Propagation for IMU-Rate State Estimation

IMU measurements come at a much higher rate than visual measurements. Although the frequency of our VIO is limited by image capture frequency, we can still directly propagate the latest VIO estimate with the set of most recent IMU measurements to achieve IMU-rate performance. The highfrequency state estimates can be utilized as state feedback for closed loop closure. An autonomous flight experiment utilizing this IMU-rate state estimates is presented in Sect. IX-D.

## G. Failure Detection and Recovery

Although our tightly-coupled monocular VIO is robust to various challenging environments and motions. Failure is still unavoidable due to violent illumination change or severely aggressive motions. Active failure detection and recovery strategy can improve the practicability of proposed system. Failure detection is an independent module that detects unusual output from the estimator. We are currently using the following criteria for failure detection:

• The number of features being tracking in the latest frame is less than a certain threshold;

• Large discontinuity in position or rotation between last two estimator outputs;

• Large change in bias or extrinsic parameters estimation;

Once a failure is detected, the system switches back to the initialization phase. Once the monocular VIO is successfully initialized, a new and separate segment of the pose graph will be created.

## VII. RELOCALIZATION

Our sliding window and marginalization scheme bound the computation complexity, but it also introduces accumulated drifts for the system. To be more specific, drifts occur in global 3D position (x, y, z) and the rotation around the gravity direction (yaw). To eliminate drifts, a tightly-coupled relocalization module that seamlessly integrates with the monocular VIO is proposed. The relocalization process starts with a loop detection module that identifies places that have already been visited. Feature-level connections between loop closure candidates and the current frame are then established. These feature correspondences are tightly integrated into the monocular VIO module, resulting in drift-free state estimates with minimum computation overhead. Multiple observations of multiple features are directly used for relocalization, resulting in higher accuracy and better state estimation smoothness. A graphical illustration of the relocalization procedure is shown in Fig. 9(a).

## A. Loop Detection

We utilize DBoW2 [6], a state-of-the-art bag-of-word place recognition approach, for loop detection. In addition to the corner features that are used for the monocular VIO, 500 more corners are detected and described by the BRIEF descriptor [40]. The additional corner features are used to achieve better recall rate on loop detection. Descriptors are treated as the visual word to query the visual database. DBoW2 returns loop closure candidates after temporal and geometrical consistency check. We keep all BRIEF descriptors for feature retrieving, but discard the raw image to reduce memory consumption.

We note that our monocular VIO is able to render roll and pitch angles observable. As such, we do not need to rely on rotation-invariant features, such as the ORB feature used in ORB SLAM [4].

<!-- page 10 of 17 -->

![Chart block](images/qin2018_vins-mono_p10_b1.png)

10

![Image block](images/qin2018_vins-mono_p10_b3.png)

(b) Global Pose Graph optimization

Fig. 9. A diagram illustrating the relocalization and pose graph optimization procedure. Fig. 9(a) shows the relocalization procedure. It starts with VIO-only pose estimates (blue). Past states are recorded (green). If a loop is detected for the newest keyframe (Sect. VII-A), as shown by the red line in the second plot, a relocalization occurred. Note that due to the use of feature-level correspondences for relocalization, we are able to incorporate loop closure constraints from multiple past keyframes (Sect. VII-C), as indicated in the last three plots. The pose graph optimization is illustrated in Fig. 9(b). A keyframe is added into the pose graph when it is marginalized out from the sliding window. If there is a loop between this keyframe and any other past keyframes, the loop closure constraints, formulated as 4-DOF relative rigid body transforms, will also be added to the pose graph. The pose graph is optimized using all relative pose constraints (Sect. VIII-B) in a separate thread, and the relocalization module always runs with respect to the newest pose graph configuration.

## B. Feature Retrieval

When a loop is detected, the connection between the local sliding window and the loop closure candidate is established by retrieving feature correspondences. Correspondences are found by BRIEF descriptor matching. Directly descriptor matching may cause a large number a lot of outliers. To this end, we use two-step geometric outlier rejection, as illustrated in Fig. 10.

• 2D-2D: fundamental matrix test with RANSAC [31]. We use 2D observations of retrieved features in the current image and loop closure candidate image to perform fundamental matrix test.

• 3D-2D: PnP test with RANSAC [35]. Based on the known 3D position of features in the local sliding window, and 2D observations in the loop closure candidate

![Image block](images/qin2018_vins-mono_p10_b10.png)

(a) BRIEF descriptor matching results

![Image block](images/qin2018_vins-mono_p10_b12.png)

(b) First step: 2D-2D outlier rejection results

![Image block](images/qin2018_vins-mono_p10_b14.png)

(c) Second step: 3D-2D outlier rejection results.

Fig. 10. Descriptor matching and outlier removal for feature retrieval during loop closure.

image, we perform PnP test.

When the number of inliers beyond a certain threshold, we treat this candidate as a correct loop detection and perform relocalization.

## C. Tightly-Coupled Relocalization

The relocalization process effectively aligns the current sliding window maintained by the monocular VIO (Sect. VI) to the graph of past poses. During relocalization, we treat poses of all loop closure frames as constants. We jointly optimize the sliding window using all IMU measurements, local visual measurement measurements, and retrieved feature correspondences from loop closure. We can easily write the visual measurement model for retrieved features observed by a loop closure frame v to be the same as those for visual measurements in VIO, as shown in (25). The only difference is that the pose $( \hat { \mathbf { q } } _ { v } ^ { w } , \hat { \mathbf { p } } _ { v } ^ { w } )$ of the loop closure frame, which is taken from the pose graph (Sect. VIII), or directly from past odometry output (if this is the first relocalization), is treated as a constant. To this end, we can slightly modify the nonlinear cost function in (22) with additional loop terms:

$$
\begin{array}{c} \hline \min _ {\mathcal {X}} \left\{\| \mathbf {r} _ {p} - \mathbf {H} _ {p} \mathcal {X} \| ^ {2} + \sum_ {k \in \mathcal {B}} \left\| \mathbf {r} _ {\mathcal {B}} (\hat {\mathbf {z}} _ {b _ {k + 1}} ^ {b _ {k}}, \mathcal {X}) \right\| _ {\mathbf {P} _ {b _ {k + 1}} ^ {b _ {k}}} ^ {2} \right. \\ \qquad \qquad \qquad + \sum_ {(l, j) \in \mathcal {C}} \rho (\left\| \mathbf {r} _ {\mathcal {C}} (\hat {\mathbf {z}} _ {l} ^ {c _ {j}}, \mathcal {X}) \right\| _ {\mathbf {P} _ {l} ^ {c _ {j}}} ^ {2}) \\ \qquad \qquad + \sum_ {(l, v) \in \mathcal {L}} \rho (\left\| \mathbf {r} _ {\mathcal {C}} (\hat {\mathbf {z}} _ {l} ^ {v}, \mathcal {X}, \hat {\mathbf {q}} _ {v} ^ {w}, \hat {\mathbf {p}} _ {v} ^ {w}) \right\| _ {\mathbf {P} _ {l} ^ {c _ {v}}} ^ {2} \Bigg \}, \end{array}\tag{26}
$$

where $\mathcal { L }$ is the set of the observation of retrieved features in the loop closure frames. $( l , v )$ means $l ^ { t h }$ feature observed in

<!-- page 11 of 17 -->

11

the loop closure frame v. Note that although the cost function is slightly different from (22), the dimension of the states to be solved remains the same, as poses of loop closure frames are considered as constants. When multiple loop closures are established with the current sliding window, we optimize using all loop closure feature correspondences from all frames at the same time. This gives multi-view constraints for relocalization, resulting in higher accuracy and better smoothness. Note that the global optimization of past poses and loop closure frames happens after relocalization, and will be discussed in Sect. VIII.

## VIII. GLOBAL POSE GRAPH OPTIMIZATION

After relocalization, the local sliding window shifts and aligns with past poses. Utilizing the relocalization results, this additional pose graph optimization step is developed to ensure the set of past poses are registered into a globally consistent configuration.

Since our visual-inertial setup renders roll and pitch angles fully observable, the accumulated drift only occurs in four degrees-of-freedom $( \mathrm { x } ,   \mathrm { y } ,$ z and yaw angle). To this end, we ignore estimating the drift-free roll and pitch states, and only perform 4-DOF pose graph optimization.

## A. Adding Keyframes into the Pose Graph

When a keyframe is marginalized out from the sliding window, it will be added to pose graph. This keyframe serves as a vertex in the pose graph, and it connects with other vertexes by two types of edges:

1) Sequential Edge: a keyframe will establish several sequential edges to its previous keyframes. A sequential edge represents the relative transformation between two keyframes in the local sliding window, which value is taken directly from VIO. Considering a newly marginalized keyframe i and one of its previous keyframes $j ,$ the sequential edge only contains relative position $\hat { \mathbf { p } } _ { i j } ^ { i }$ and yaw angle $\hat { \psi } _ { i j }$

$$
\begin{array}{l} \hat {\mathbf {p}} _ {i j} ^ {i} = \hat {\mathbf {R}} _ {i} ^ {w - 1} (\hat {\mathbf {p}} _ {j} ^ {w} - \hat {\mathbf {p}} _ {i} ^ {w}) \\ \hat {\psi} _ {i j} = \hat {\psi} _ {j} - \hat {\psi} _ {i}. \end{array}\tag{27}
$$

2) Loop Closure $E d g e \cdot$ If the newly marginalized keyframe has a loop connection, it will be connected with the loop closure frame by a loop closure edge in the pose graph. Similarly, the loop closure edge only contains 4-DOF relative pose transform that is defined the same as (27). The value of the loop closure edge is obtained using results from relocalization.

## B. 4-DOF Pose Graph Optimization

We define the residual of the edge between frames i and $j$ minimally as:

$$
\mathbf {r} _ {i, j} (\mathbf {p} _ {i} ^ {w}, \psi_ {i}, \mathbf {p} _ {j} ^ {w}, \psi_ {j}) = \left[ \begin{array}{c} \mathbf {R} (\hat {\phi} _ {i}, \hat {\theta} _ {i}, \psi_ {i}) ^ {- 1} (\mathbf {p} _ {j} ^ {w} - \mathbf {p} _ {i} ^ {w}) - \hat {\mathbf {p}} _ {i j} ^ {i} \\ \psi_ {j} - \psi_ {i} - \hat {\psi} _ {i j} \end{array} \right],\tag{28}
$$

where $\hat { \phi } _ { i } , \hat { \theta } _ { i }$ are the estimates roll and pitch angles, which are obtained directly from monocular VIO.

The whole graph of sequential edges and loop closure edges are optimized by minimizing the following cost function:

$$
\min _ {\mathbf {p}, \psi} \left\{\sum_ {(i, j) \in \mathcal {S}} \| \mathbf {r} _ {i, j} \| ^ {2} + \sum_ {(i, j) \in \mathcal {L}} \rho (\| \mathbf {r} _ {i, j} \| ^ {2}) \right\},\tag{29}
$$

where $\mathcal { S }$ is the set of all sequential edges and L is the set of all loop closure edges. Although the tightly-coupled relocalization already helps with eliminating wrong loop closures, we add another Huber norm $\rho ( \cdot )$ to further reduce the impact of any possible wrong loops. In contrast, we do not use any robust norms for sequential edges, as these edges are extracted from VIO, which already contain sufficient outlier rejection mechanisms.

Pose graph optimization and relocalization (Sect. VII-C) runs asynchronously in two separate threads. This enables immediate use of the most optimized pose graph for relocalization whenever it becomes available. Similarly, even if the current pose graph optimization is not completed yet, relocalization can still take place using the existing pose graph configuration. This process is illustrated in Fig. 9(b).

## C. Pose Graph Management

The size of the pose graph may grow unbounded when the travel distance increases, limiting the real-time performance of the system in the long run. To this end, we implement a downsample process to maintain the pose graph database to a limited size. All keyframes with loop closure constraints will be kept, while other keyframes that are either too close or have very similar orientations to its neighbors may be removed. The probability of a keyframe being removed is proportional to its spatial density to its neighbors.

## IX. EXPERIMENTAL RESULTS

We perform three experiments and two applications to evaluate the proposed VINS-Mono system. In the first experiment, we compare the proposed algorithm with another state-of-the-art algorithm on public datasets. We perform a numerical analysis to show the accuracy of our system. We then test our system in the indoor environment to evaluate the performance in repetitive scenes. A large-scale experiment is carried out to illustrate the long-time practicability of our system. Additionally, we apply the proposed system for two applications. For aerial robot application, we use VINS-Mono for position feedback to control a drone to follow a pre-defined trajectory. We then port our approach onto an iOS mobile device and compare against Google Tango.

## A. Dataset Comparison

We evaluate our proposed VINS-Mono using the EuRoC MAV Visual-Inertial Datasets [41]. The datasets are collected onboard a micro aerial vehicle, which contains stereo images (Aptina MT9V034 global shutter, WVGA monochrome, 20 FPS), synchronized IMU measurements (ADIS16448, 200 Hz), and ground truth states (VICON and Leica MS50). We only use images from the left camera. Large IMU bias and illumination changes are observed in these datasets.

<!-- page 12 of 17 -->

12

![Chart block](images/qin2018_vins-mono_p12_b2.png)

Fig. 11. Trajectory in MH 03 median, compared with OKVIS.

![Chart block](images/qin2018_vins-mono_p12_b4.png)

Fig. 12. Translation error plot in MH 03 median.

In these experiments, we compare VINS-Mono with OKVIS [16], a state-of-the-art VIO that works with monocular and stereo cameras. OKVIS is another optimizationbased sliding-window algorithm. Our algorithm is different with OKVIS in many details, as presented in the technical sections. Our system is complete with robust initialization and loop closure. We use two sequences, MH 03 median and MH 05 difficult, to show the performance of proposed method. To simplify the notation, we use VINS to denote our approach with only monocular VIO, and VINS loop to denote the complete version with relocalization and pose graph optimization. We use OKVIS mono and OKVIS stereo to denote the OKVIS’s results using monocular and stereo images respectively. For the fair comparison, we throw the first 100 outputs, and use the following 150 outputs to align with the ground truth, and compare the remaining estimator outputs.

For the sequence MH 03 median, the trajectory is shown

![Chart block](images/qin2018_vins-mono_p12_b8.png)

Fig. 13. Trajectory in MH 05 difficult, compared with OKVIS..

![Chart block](images/qin2018_vins-mono_p12_b10.png)

Fig. 14. Translation error and rotation error plot in MH 05 difficult.

in Fig. 11. We only compare translation error since rotated motion is negligible in this sequence. The x, y, z error versus time, and the translation error versus distance are shown in Fig. 12. In the error plot, VINS-Mono with loop closure has the smallest translation error. We observe similar results in MH 05 difficult. The proposed method with loop function has the smallest translation error. The translation and rotation errors are shown in Fig. 14. Since the movement is smooth without much yaw angle change in this sequence, only position drift occurs. Obviously, the loop closure capability efficiently bound the accumulated drifts. OKVIS performs better in roll and pitch angle estimation. A possible reason is that VINS-Mono uses the pre-integration technique which is the firstorder approximation of IMU propagation to save computation resource.

VINS-Mono performs well in all EuRoC datasets, even in the most challenging sequence, V1 03 difficult, the one includes aggressive motion, texture-less area, and significant illumination change. The proposed method can initialize quickly in V1 03 difficult, due to the dedicated initialization procedure.

For pure VIO, both VINS-Mono and OKVIS have similar accuracy, it is hard to distinguish which one is better. However, VINS-Mono outperforms OKVIS at the system level. It is a complete system with robust initialization and loop closure function to assist the monocular VIO.

<!-- page 13 of 17 -->

13

![Image block](images/qin2018_vins-mono_p13_b2.png)

Fig. 15. The device we used for the indoor experiment. It contains one forward-looking global shutter camera (MatrixVision mvBlueFOX-MLC200w) with 752×480 resolution. We use the built-in IMU (ADXL278 and ADXRS290, 100Hz) for the DJI A3 flight controller.

![Image block](images/qin2018_vins-mono_p13_b4.png)

(a) Pedestrians

![Image block](images/qin2018_vins-mono_p13_b6.png)

(b) texture-less area

![Image block](images/qin2018_vins-mono_p13_b8.png)

(c) Low light condition

![Image block](images/qin2018_vins-mono_p13_b10.png)

(d) Glass and reflection

Fig. 16. Sample images for the challenging indoor experiment.

## B. Indoor Experiment

In the indoor experiment, we choose our laboratory environment as the experiment area. The sensor suite we use is shown in Fig. 15. It contains a monocular camera (20Hz) and an IMU (100Hz) inside the DJI A3 controller<sup>3</sup>. We hold the sensor suite by hand and walk in normal pace in the laboratory. We encounter pedestrians, low light condition, texture-less area, glass and reflection, as shown in Fig. 16. Videos can be found in the multimedia attachment.

We compare our result with OKVIS, as shown in Fig. 17. Fig. 17(a) is the VIO output from OKVIS. Fig. 17(b) is the VIO-only result from proposed method without loop closure. Fig. 17(c) is the result of the proposed method with relocalization and loop closure. Noticeable VIO drifts occurred when we circle indoor. Both OKVIS and the VIO-only version of VINS-Mono accumulate significant drifts in x, y, z, and yaw angle. Our relocalization and loop closure modules efficiently eliminate all these drifts.

## C. Large-scale Environment

1) Go out of the lab: We test VINS-Mono in a mixed indoor and outdoor setting. The sensor suite is the same as the

![Image block](images/qin2018_vins-mono_p13_b18.png)

(a) Trajectory of OKVIS.

![Image block](images/qin2018_vins-mono_p13_b20.png)

(b) Trajectory of VINS-Mono without loop closure.

![Image block](images/qin2018_vins-mono_p13_b22.png)

(c) Trajectory of VINS-Mono with relocalization and loop closure. Red lines indicate loop detection.

Fig. 17. Results of the indoor experiment with comparison against OKVIS.

one shown in Fig. 15. We started from a seat in the laboratory and go around the indoor space. Then we went down the stairs and walked around the playground outside the building. Next, we went back to the building and go upstairs. Finally, we returned to the same seat in the laboratory. The whole trajectory is more than 700 meters and last approximately ten minutes. A video of the experiment can be found in the multimedia attachment.

The trajectory is shown in Fig. 19. Fig. 19(a) is the trajectory from OKVIS. When we went up stairs, OKVIS shows unstable feature tracking, resulting in bad estimation. We cannot see the shape of stairs in the red block. The VIO-only result from VINS-Mono is shown in Fig. 19(b). The trajectory with loop closure is shown in Fig. 19(c). The shape of stairs is clear in proposed method. The closed loop trajectory is aligned with Google Map to verify its accuracy, as shown in Fig. 18.

The final drift for OKVIS is [13.80, -5.26. 7.23]m in x, y and z-axis. The final dirft of VINS-Mono without loop closure is [-5.47, 2.76. -0.29]m, which occupies 0.88% with respect to the total trajectory length, smaller than OKVIS 2.36%. With loop correction. the final drift is bounded to [-0.032, 0.09, - 0.07]m, which is trivial compared to the total trajectory length. Although we do not have ground truth, we can still visually inspect that the optimized trajectory is smooth and can be precisely aligned with the satellite map.

2) Go around campus: This very large-scale dataset that goes around the whole HKUST campus was recorded with a handheld VI-Sensor<sup>4</sup>. The dataset covers the ground that is around 710m in length, 240m in width, and with 60m in height changes. The total path length is 5.62km. The data contains the 25Hz image and 200Hz IMU lasting for 1 hour and 34

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>3</sup>[http://www.dji.com/a3](http://www.dji.com/a3)</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>4</sup>http://www.skybotix.com/</span></small>

<!-- page 14 of 17 -->

14

![Image block](images/qin2018_vins-mono_p14_b2.png)

Fig. 18. The estimated trajectory of the mixed indoor and outdoor experiment aligned with Google Map. The yellow line is the final estimated trajectory from VINS-Mono after loop closure. Red lines indicate loop closure.

![Image block](images/qin2018_vins-mono_p14_b4.png)

(a) Estimated trajectory from OKVIS (b) Estimated trajectory from VINS-Mono with loop closure disabled

![Image block](images/qin2018_vins-mono_p14_b6.png)

(c) Estimated trajectory from VINS-Mono with loop closure

Fig. 19. Estimated trajectories for the mixed indoor and outdoor experiment. In Fig. 19(a), results from OKVIS went bad during tracking lost in texture-less region (staircase). Figs. 19(b) 19(c) shows results from VINS-Mono without and with loop closure. Red lines indicate loop closures. The spiral-shaped blue line shows the trajectory when going up and down the stairs. We can see that VINS-Mono performs well (subject to acceptable drift) even without loop closure.

minutes. It is a very significant experiment to test the stability and durability of VINS-Mono.

In this large-scale test, We set the keyframe database size to 2000 in order to provide sufficient loop information and achieve real-time performance. We run this dataset with an Intel i7-4790 CPU running at 3.60GHz. Timing statistics are show in Table. I. The estimated trajectory is aligned with Google map in Fig. 20. Compared with Google map, we can see our results are almost drift-free in this very long-duration test.

## D. Application I: Feedback Control of an Aerial Robot

We apply VINS-Mono for autonomous feedback control of an aerial robot, as shown in Fig. 21(a). We use a forwardlooking global shutter camera (MatrixVision mvBlueFOX-MLC200w) with 752×480 resolution, and equipped it with a 190-degree fisheye lens. A DJI A3 flight controller is used for both IMU measurements and for attitude stabilization control. The onboard computation resource is an Intel i7-5500U CPU running at 3.00 GHz. Traditional pinhole camera model is not suitable for large FOV camera. We use MEI [42] model for this camera, calibrated by the toolkit introduced in [43].

In this experiment, we test the performance of autonomous trajectory tracking under using state estimates from VINS-Mono. Loop closure is disabled for this experiment The quadrotor is commanded to track a figure eight pattern with each circle being 1.0 meters in radius, as shown in Fig. 21(b). Four obstacles are put around the trajectory to verify the accuracy of VINS-Mono without loop closure. The quadrotor follows this trajectory four times continuously during the experiment. The 100 Hz onboard state estimates (Sect. VI-F) enables real-time feedback control of quadrotor.

Ground truth is obtained using OptiTrack<sup>5</sup>. Total trajectory length is 61.97 m. The final drift is [0.08, 0.09, 0.13] m, resulting in 0.29% position drift. Details of the translation and rotation as well as their corresponding errors are shown in Fig. 23.

## E. Application II: Mobile Device

We port VINS-Mono to mobile devices and present a simple AR application to showcase its accuracy and robustness. We name our mobile implementation VINS-Mobile<sup>6</sup>, and we compare it against Google Tango device<sup>7</sup>, which is one of the best commercially available augmented reality solutions on mobile platforms.

VINS-Mono runs on an iPhone7 Plus. we use 30 Hz images with 640 × 480 resolution captured by the iPhone, and IMU data at 100 Hz obtained by the built-in InvenSense MP67B 6-axis gyroscope and accelerometer. As Fig. 24 shows, we mount the iPhone together with a Tango-Enabled Lenovo Phab 2 Pro. The Tango device uses a global shutter fisheye camera and synchronized IMU for state estimation. Firstly, we insert a virtual cube on the plane which is extracted from estimated visual features as shown in Fig. 25(a). Then we hold these

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>5</sup>http://optitrack.com/</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>6</sup>https://github.com/HKUST-Aerial-Robotics/VINS-Mobile</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">TABLE I</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280"><sup>7</sup>http://shopap.lenovo.com/hk/en/tango/</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">TIMING STATISTICS</span></small>

<small><span class="docvortex-page-footnote" data-block-type="page_footnote" style="color:#6b7280">Tread Modules Time (ms) Rate (Hz) Feature detector 15 25 1 KLT tracker 5 25 2 Window optimization 50 10 Loop detection 100 3 Pose graph optimization 130</span></small>

<!-- page 15 of 17 -->

15

![Image block](images/qin2018_vins-mono_p15_b2.png)

Fig. 20. The estimated trajectory of the very large-scale environment aligned with Google map. The yellow line is the estimated trajectory from VINS-Mono. Red lines indicates loop closure.

![Image block](images/qin2018_vins-mono_p15_b4.png)

(a) Aerial robot testbed

![Image block](images/qin2018_vins-mono_p15_b6.png)

(b) Testing environment and desired figure eight pattern

Fig. 21. Fig 21(a): The self-developed aerial robot with a forward-looking fisheye camera (MatrixVision mvBlueFOX-MLC200w, 190 FOV) and an DJI A3 flight controller (ADXL278 and ADXRS290, 100Hz). $\operatorname { F i g . }$ 21(b): The designed trajectory. Four known obstacles are placed. The yellow line is the predefined figure eight-figure pattern which the aerial robot should follow. The robot follows the trajectory four times with loop closure disabled. A video of the experiment can be found in the multimedia attachment.

two devices and walk inside and outside the room in a normal pace. When loops are detected, we use the 4-DOF pose graph optimization (Sect. VIII-B) to eliminate x, y, z and yaw drifts.

Interestingly, when we open a door, Tango’s yaw estimation jumps a big angle, as shown in Fig. 25(b). The reason maybe

![Chart block](images/qin2018_vins-mono_p15_b11.png)

Fig. 22. The trajectory of loop closure-disabled VINS-Mono on the MAV platform and its comparison against the ground truth. The robot follows the trajectory four times. VINS-Mono estimates are used as real-time position feedback for the controller. Ground truth is obtained using OptiTrack. Total length is 61.97m. Final drift is 0.18m.

estimator crash caused by unstable feature tracking or active failure detection and recovery. However, VINS-Mono still works well in this challenging case. After traveling about 264m, we return to the start location. The final result can be seen in Fig. 25(c), the trajectory of Tango suffers drifting in the last lap while our VINS returns to the start point. The drift in total trajectory is eliminated due to the 4-DOF pose graph optimization. This is also evidenced by the fact that the cube is registered to the same place on the image comparing to the beginning.

Admittedly, Tango is more accurate than our implementation especially for local state estimates. However, this exper-

<!-- page 16 of 17 -->

16

![Chart block](images/qin2018_vins-mono_p16_b2.png)

![Chart block](images/qin2018_vins-mono_p16_b3.png)

![Chart block](images/qin2018_vins-mono_p16_b4.png)

![Chart block](images/qin2018_vins-mono_p16_b5.png)

![Chart block](images/qin2018_vins-mono_p16_b6.png)

![Chart block](images/qin2018_vins-mono_p16_b7.png)

![Chart block](images/qin2018_vins-mono_p16_b8.png)

![Chart block](images/qin2018_vins-mono_p16_b9.png)

![Chart block](images/qin2018_vins-mono_p16_b10.png)

![Chart block](images/qin2018_vins-mono_p16_b11.png)

![Chart block](images/qin2018_vins-mono_p16_b12.png)

![Chart block](images/qin2018_vins-mono_p16_b13.png)

Fig. 23. Position, orientation and their corresponding errors of loop closure-disabled VINS-Mono compared with OptiTrack. A sudden in pitch error at the 60s is caused by aggressive breaking at the end of the designed trajectory, and possible time misalignment error between VINS-Mono and OptiTrack.

![Image block](images/qin2018_vins-mono_p16_b15.png)

Fig. 24. A simple holder that we used to mount the Google Tango device (left) and the iPhone7 Plus (right) that runs our VINS-Mobile implementation.

![Image block](images/qin2018_vins-mono_p16_b17.png)

(a) Beginning

![Image block](images/qin2018_vins-mono_p16_b19.png)

(b) Door opening

iment shows that the proposed method can run on general mobile devices and have the potential ability to compare specially engineered devices. The robustness of proposed method is also proved in this experiment. Video can be found in the multimedia attachment.

## X. CONCLUSION AND FUTURE WORK

In this paper, we propose a robust and versatile monocular visual-inertial estimator. Our approach features both state-of-the-art and novel solutions to IMU pre-integration, estimator initialization and failure recovery, online extrinsic calibration, tightly-coupled visual-inertial odometry, relocalization, and efficient global optimization. We show superior performance by comparing against both state-of-the-art open source implementations and highly optimized industry solutions. We open source both PC and iOS implementation for the benefit of the community.

![Image block](images/qin2018_vins-mono_p16_b24.png)

![Image block](images/qin2018_vins-mono_p16_b25.png)

(c) End

Fig. 25. From left to right: AR image from VINS-Mobile, estimated trajectory from VINS-Mono, estimated trajectory from Tango Fig: 25(a): Both VINS-Mobile and Tango are initialized at the start location and a virtual box is inserted on the plane which extracted from estimated features. Fig. 25(b): A challenging case in which the camera is facing a moving door. The drift of Tango trajectory is highlighted. Fig. 25(c): The final trajectory of both VINS-Mobile and Tango. The total length is about 264m.

Although feature-based VINS estimators have already reached the maturity of real-world deployment, we still see many directions for future research. Monocular VINS may

reach weakly observable or even degenerate conditions depending on the motion and the environment. We are most interested in online methods to evaluate the observability properties of monocular VINS, and online generation of motion plans to restore observability. Another research direction concerns the

<!-- page 17 of 17 -->

17

mass deployment of monocular VINS on a large variety of consumer devices, such as mobile phones. This application requires online calibration of almost all sensor intrinsic and extrinsic parameters, as well as the online identification of calibration qualities. Finally, we are interested in producing dense maps given results from monocular VINS. Our first results on monocular visual-inertial dense mapping with application to drone navigation was presented in [44]. However, extensive research is still necessary to further improve the system accuracy and robustness.

## REFERENCES

[1] G. Klein and D. Murray, “Parallel tracking and mapping for small ar workspaces,” in Mixed and Augmented Reality, 2007. ISMAR 2007. 6th IEEE and ACM International Symposium on. IEEE, 2007, pp. 225–234.

[2] C. Forster, M. Pizzoli, and D. Scaramuzza, “SVO: Fast semi-direct monocular visual odometry,” in Proc. of the IEEE Int. Conf. on Robot. and Autom., Hong Kong, China, May 2014.

[3] J. Engel, T. Schops, and D. Cremers, “Lsd-slam: Large-scale di- ¨ rect monocular slam,” in European Conference on Computer Vision. Springer International Publishing, 2014, pp. 834–849.

[4] R. Mur-Artal, J. Montiel, and J. D. Tardos, “Orb-slam: a versatile and accurate monocular slam system,” IEEE Transactions on Robotics, vol. 31, no. 5, pp. 1147–1163, 2015.

[5] J. Engel, V. Koltun, and D. Cremers, “Direct sparse odometry,” IEEE Transactions on Pattern Analysis and Machine Intelligence, 2017.

[6] D. Galvez-L ´ opez and J. D. Tard ´ os, “Bags of binary words for fast ´ place recognition in image sequences,” IEEE Transactions on Robotics, vol. 28, no. 5, pp. 1188–1197, October 2012.

[7] S. Shen, N. Michael, and V. Kumar, “Tightly-coupled monocular visualinertial fusion for autonomous flight of rotorcraft MAVs,” in Proc. of the IEEE Int. Conf. on Robot. and Autom., Seattle, WA, May 2015.

[8] Z. Yang and S. Shen, “Monocular visual–inertial state estimation with online initialization and camera–imu extrinsic calibration,” IEEE Transactions on Automation Science and Engineering, vol. 14, no. 1, pp. 39–51, 2017.

[9] T. Qin and S. Shen, “Robust initialization of monocular visual-inertial estimation on aerial robots.” in Proc. of the IEEE/RSJ Int. Conf. on Intell. Robots and Syst., Vancouver, Canada, 2017, accepted.

[10] P. Li, T. Qin, B. Hu, F. Zhu, and S. Shen, “Monocular visual-inertial state estimation for mobile augmented reality.” in Proc. of the IEEE Int. Sym. on Mixed adn Augmented Reality, Nantes, France, 2017, accepted.

[11] S. Weiss, M. W. Achtelik, S. Lynen, M. Chli, and R. Siegwart, “Realtime onboard visual-inertial state estimation and self-calibration of mavs in unknown environments,” in Robotics and Automation (ICRA), 2012 IEEE International Conference on. IEEE, 2012, pp. 957–964.

[12] S. Lynen, M. W. Achtelik, S. Weiss, M. Chli, and R. Siegwart, “A robust and modular multi-sensor fusion approach applied to mav navigation,” in Proc. of the IEEE/RSJ Int. Conf. on Intell. Robots and Syst. IEEE, 2013, pp. 3923–3929.

[13] A. I. Mourikis and S. I. Roumeliotis, “A multi-state constraint Kalman filter for vision-aided inertial navigation,” in Proc. of the IEEE Int. Conf. on Robot. and Autom., Roma, Italy, Apr. 2007, pp. 3565–3572.

[14] M. Li and A. Mourikis, “High-precision, consistent EKF-based visualinertial odometry,” Int. J. Robot. Research, vol. 32, no. 6, pp. 690–711, May 2013.

[15] M. Bloesch, S. Omari, M. Hutter, and R. Siegwart, “Robust visual inertial odometry using a direct ekf-based approach,” in Proc. of the IEEE/RSJ Int. Conf. on Intell. Robots and Syst. IEEE, 2015, pp. 298–304.

[16] S. Leutenegger, S. Lynen, M. Bosse, R. Siegwart, and P. Furgale, “Keyframe-based visual-inertial odometry using nonlinear optimization,” Int. J. Robot. Research, vol. 34, no. 3, pp. 314–334, Mar. 2014.

[17] R. Mur-Artal and J. D. Tardos, “Visual-inertial monocular SLAM with map reuse,” arXiv preprint arXiv:1610.05949, 2016.

[18] K. Wu, A. Ahmed, G. A. Georgiou, and S. I. Roumeliotis, “A square root inverse filter for efficient vision-aided inertial navigation on mobile devices.” in Robotics: Science and Systems, 2015.

[19] M. K. Paul, K. Wu, J. A. Hesch, E. D. Nerurkar, and S. I. Roumeliotis, “A comparative analysis of tightly-coupled monocular, binocular, and stereo vins,” in Proc. of the IEEE Int. Conf. on Robot. and Autom., Singapore, May 2017.

[20] M. Kaess, H. Johannsson, R. Roberts, V. Ila, J. J. Leonard, and F. Dellaert, “isam2: Incremental smoothing and mapping using the bayes tree,” The International Journal of Robotics Research, vol. 31, no. 2, pp. 216–235, 2012.

[21] V. Usenko, J. Engel, J. Stuckler, and D. Cremers, “Direct visual-inertial ¨ odometry with stereo cameras,” in Proc. of the IEEE Int. Conf. on Robot. and Autom. IEEE, 2016, pp. 1885–1892.

[22] T. Lupton and S. Sukkarieh, “Visual-inertial-aided navigation for highdynamic motion in built environments without initial conditions,” IEEE Trans. Robot., vol. 28, no. 1, pp. 61–76, Feb. 2012.

[23] C. Forster, L. Carlone, F. Dellaert, and D. Scaramuzza, “IMU preintegration on manifold for efficient visual-inertial maximum-a-posteriori estimation,” in Proc. of Robot.: Sci. and Syst., Rome, Italy, Jul. 2015.

[24] S. Shen, Y. Mulgaonkar, N. Michael, and V. Kumar, “Initializationfree monocular visual-inertial estimation with application to autonomous MAVs,” in Proc. of the Int. Sym. on Exp. Robot., Marrakech, Morocco, Jun. 2014.

[25] A. Martinelli, “Closed-form solution of visual-inertial structure from motion,” Int. J. Comput. Vis., vol. 106, no. 2, pp. 138–152, 2014.

[26] J. Kaiser, A. Martinelli, F. Fontana, and D. Scaramuzza, “Simultaneous state initialization and gyroscope bias calibration in visual inertial aided navigation,” IEEE Robotics and Automation Letters, vol. 2, no. 1, pp. 18–25, 2017.

[27] M. Faessler, F. Fontana, C. Forster, and D. Scaramuzza, “Automatic reinitialization and failure recovery for aggressive flight with a monocular vision-based quadrotor,” in Proc. of the IEEE Int. Conf. on Robot. and Autom. IEEE, 2015, pp. 1722–1729.

[28] H. Strasdat, J. Montiel, and A. J. Davison, “Scale drift-aware large scale monocular slam,” Robotics: Science and Systems VI, 2010.

[29] B. D. Lucas and T. Kanade, “An iterative image registration technique with an application to stereo vision,” in Proc. of the Intl. Joint Conf. on Artificial Intelligence, Vancouver, Canada, Aug. 1981, pp. 24–28.

[30] J. Shi and C. Tomasi, “Good features to track,” in Computer Vision and Pattern Recognition, 1994. Proceedings CVPR’94., 1994 IEEE Computer Society Conference on. IEEE, 1994, pp. 593–600.

[31] R. Hartley and A. Zisserman, Multiple view geometry in computer vision. Cambridge university press, 2003.

[32] A. Heyden and M. Pollefeys, “Multiple view geometry,” Emerging Topics in Computer Vision, 2005.

[33] D. Nister, “An efficient solution to the five-point relative pose problem,” ´ IEEE transactions on pattern analysis and machine intelligence, vol. 26, no. 6, pp. 756–770, 2004.

[34] T. Liu and S. Shen, “Spline-based initialization of monocular visualinertial state estimators at high altitude,” IEEE Robotics and Automation Letters, 2017, accepted.

[35] V. Lepetit, F. Moreno-Noguer, and P. Fua, “Epnp: An accurate o (n) solution to the pnp problem,” International journal of computer vision, vol. 81, no. 2, pp. 155–166, 2009.

[36] B. Triggs, P. F. McLauchlan, R. I. Hartley, and A. W. Fitzgibbon, “Bundle adjustmenta modern synthesis,” in International workshop on vision algorithms. Springer, 1999, pp. 298–372.

[37] P. Huber, “Robust estimation of a location parameter,” Annals of Mathematical Statistics, vol. 35, no. 2, pp. 73–101, 1964.

[38] S. Agarwal, K. Mierle, and Others, “Ceres solver,” [http://ceres-solver.org.](http://ceres-solver.org)

[39] G. Sibley, L. Matthies, and G. Sukhatme, “Sliding window filter with application to planetary landing,” J. Field Robot., vol. 27, no. 5, pp. 587–608, Sep. 2010.

[40] M. Calonder, V. Lepetit, C. Strecha, and P. Fua, “Brief: Binary robust independent elementary features,” Computer Vision–ECCV 2010, pp. 778–792, 2010.

[41] M. Burri, J. Nikolic, P. Gohl, T. Schneider, J. Rehder, S. Omari, M. W. Achtelik, and R. Siegwart, “The euroc micro aerial vehicle datasets,” The International Journal of Robotics Research, 2016.

[42] C. Mei and P. Rives, “Single view point omnidirectional camera calibration from planar grids,” in Robotics and Automation, 2007 IEEE International Conference on. IEEE, 2007, pp. 3945–3950.

[43] L. Heng, B. Li, and M. Pollefeys, “Camodocal: Automatic intrinsic and extrinsic calibration of a rig with multiple generic cameras and odometry,” in Intelligent Robots and Systems (IROS), 2013 IEEE/RSJ International Conference on. IEEE, 2013, pp. 1793–1800.

[44] Y. Lin, F. Gao, T. Qin, W. Gao, T. Liu, W. Wu, Z. Yang, and S. Shen, “Autonomous aerial navigation using monocular visual-inertial fusion,” J. Field Robot., vol. 00, pp. 1–29, 2017.