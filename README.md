# Code snippets of NUEDC 2023 E

- finding the origin point and border or rectangle [`origin_point.ipynb`](origin_point.ipynb)
- finding the vertex of inner rectangle [`rect.ipynb`](rect.ipynb)
- finding the inner and outer borders of inner rectangle, and construct a path to follow [`pp.ipynb`](pp.ipynb)
- filter out the background of captured video that is not right on target with [M-LSD](https://github.com/navervision/mlsd) and [MiDaS](https://github.com/isl-org/MiDaS) [`depth.ipynb`](depth.ipynb)
- a async driver of a step motor controller that communicates by UART: [`motor`](motor)

I'm too lazy to build the whole project/system but I believe you can finish it with these code snippets.

~~By the way I don't have much knowledge on step motor/servo motor. I just focus on vision processing.~~

## Possible improvements

### Low light image enhancement

- [低照度图像增强传统算法简介](https://zhuanlan.zhihu.com/p/602311030) ([Archived](https://archive.md/Dg8Kh))
- [EnlightenGAN: Deep Light Enhancement without Paired Supervision](https://arxiv.org/abs/1906.06972)
- [用于SLAM的图像增强算法 ](http://luohanjie.com/2018-11-01/image-enhancement-for-slam.html) ([Archived](https://archive.md/t99fi))
- [一文读懂14种低照度图像增强算法——原理+对比效果图 ](https://juejin.cn/post/7236028062872469564) ([Archived](https://archive.md/TSqv5))

### Super resolution

- [Real-Time Super-Resolution for Real-World Images on Mobile Devices](https://arxiv.org/abs/2206.01777)

### Kalman filter

using Kalman to predict the position of the target. But how the state we estimated be useful for control the movement of the motor/laser?

The answer is... just filter out the noise/error in sensor/the result of image processing. Should find a way to filter out the outliers.

The current implementation won't retain the state of the previous frame.

> The job of a PID controller is to minimize the error, keeping your robot as close to the target as possible.

- [PID and Kalman filters](https://robotics.stackexchange.com/questions/16409/pid-and-kalman-filters)
- [Beyond linear: the Extended Kalman Filter](https://quantdare.com/beyond-linear-the-extended-kalman-filter/)
- [Output feedback control using LQR and extended Kalman filtering](https://python-control.readthedocs.io/en/latest/pvtol-outputfbk.html)
- [Why is the Kalman filter a filter and not a control system?](https://robotics.stackexchange.com/questions/18592/why-is-the-kalman-filter-a-filter-and-not-a-control-system)

### PID control

Current implementation is a P only controller. Or maybe a Constant controller. (only changes the direction of the motor, not even the magnitude)
so we need fast frame rate to feedback the position of the target.

- [Two-Degree-of-Freedom PID Controllers](https://www.mathworks.com/help/control/ug/two-degree-of-freedom-2-dof-pid-controllers.html)
- [PID Settings | Proportional-Only Control ](https://www.youtube.com/watch?v=E780BPOjKwM)

### Increase the frame rate

The feature of target is obvious, so we can use a lower resolution to increase the frame rate.
30 FPS for now but we can do 60 FPS or even higher with RK3588.

The increase of frame rate would make the fresh rate of the target position higher and thus make the control more accurate
without fancy prediction algorithms like Kalman filter.
