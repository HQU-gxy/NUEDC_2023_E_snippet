# Code snippets of NUEDC 2023 E

- a minimal example of OpenCV in C++. See also [`build.md`](build.md), which is not actually be used in the final project. However, if you want some speed and don't have a good rig, you have to squeeze every bit of performance out of your computer (or get a better machine)
- finding the origin point and border or rectangle [`origin_point.ipynb`](origin_point.ipynb)
- finding the vertex of inner rectangle [`rect.ipynb`](rect.ipynb)
- finding the inner and outer borders of inner rectangle, and construct a path to follow [`pp.ipynb`](pp.ipynb)
- filter out the background of captured video that is not right on target with [M-LSD](https://github.com/navervision/mlsd) and [MiDaS](https://github.com/isl-org/MiDaS)
- a async driver of a step motor controller that communicates by UART: [`motor`](motor)

I'm too lazy to build the whole project/system but I believe you can finish it with these code snippets.

~~By the way I don't have much knowledge on step motor/servo motor. I just focus on vision processing.~~
