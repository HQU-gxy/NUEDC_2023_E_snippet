from dataclasses import dataclass
from .pkt import *
from typing import Optional
from .protocol import MotorProtocol, Direction
from .utils import Instant
from loguru import logger
import asyncio
from typing import Optional, Tuple, Union


@dataclass
class Motion:
    speed: float
    direction: Direction


def reverse_direction(direction: Direction):
    return Direction.CCW if direction == Direction.CW else Direction.CW


def degree_to_pulse(degree: float, division: int, step_angle: float = 1.8):
    # origin_div = 360 / step_angle
    # enhanced_div = origin_div * division
    # one_deg_pulse = enhanced_div / 360
    one_deg_pulse = step_angle / division
    return int(degree * one_deg_pulse)


class Motor:
    id: int
    protocol: MotorProtocol
    last_position_deg: Optional[float] 
    last_write: Instant
    degree_max: Optional[float]
    degree_min: Optional[float]
    division: int
    _positive_direction: Direction

    def __init__(self, id: int, protocol: MotorProtocol, division: int = 16) -> None:
        MAX_POS_ABS = 18
        self.id = id
        self.protocol = protocol
        self.last_position_deg = None
        self.last_write = Instant()
        self.degree_max = None
        self.degree_min = None
        self.division = division
        self.protocol.register_device(self.id)
        self._positive_direction = Direction.CW

    def set_positive_direction(self, direction: Direction):
        self._positive_direction = direction

    def begin(self):
        self.set_division(self.division)

    def set_division(self, division: int):
        assert 0 < division <= 255
        logger.info("[{:02x}] set division to {}".format(self.id, division))
        self.division = division
        self.protocol.set_division(self.id, division)

    def to_degree(self, speed:int, degree:float):
        assert self.last_position_deg is not None
        if self.degree_max is not None and degree > self.degree_max:
            degree = self.degree_max
        if self.degree_min is not None and degree < self.degree_min:
            degree = self.degree_min
        delta_angle = degree - self.last_position_deg
        delta_pulse = degree_to_pulse(delta_angle, self.division)
        self.protocol.ctrl_speed_with_pulse_count(
            self.id, Direction.CW, speed, delta_pulse)

    async def to_degree_with_new_reading(self, speed: int, degree: float, timeout=0.1, max_retry_times=3):
        self.last_position_deg = await self.protocol.read_position_deg(self.id, timeout=timeout, max_retry_times=max_retry_times)
        if self.degree_max is not None and degree > self.degree_max:
            degree = self.degree_max
        if self.degree_min is not None and degree < self.degree_min:
            degree = self.degree_min
        delta_angle = degree - self.last_position_deg
        delta_pulse = degree_to_pulse(delta_angle, self.division)
        self.protocol.ctrl_speed_with_pulse_count(
            self.id, Direction.CW, speed, delta_pulse)

    def delta_degree(self, speed: int, delta_deg: float):
        # 在 16 细分下，发送 e0 fd 00 0c 80，表示电机以 0 档速度正转 360°
        # (00 表示 0 档速度正转，0c 80 表示 3200(0x0c80)个脉冲 = 360°)
        # assume using 1.8 degree motor
        # 360 / 1.8 = 200
        # 16 division
        # 200 * 16 = 3200
        # so it can be used to improve precision

        # 在 16 细分下，发送 e0 fd 88 00 10，表示电机以 8 档速度反转 1.8°
        # (88 表示 8 档速度反转，00 10 表示 16(0x0010)个脉冲 = 1.8°)
        # 输入累计位置，根据你设定的细分和你发送的累计脉冲数计算出来的位置，
        # 即你想要控制电机到达的累计目标位置。
        # http://www.zgbjdj.com/news2.asp?id=17148

        # 根据自己的步进电机类型进行选择，修改该选项后，在闭环模式下需要
        # 重新对编码器进行校准。
        # 0.9°:电机是 0.9 度的步进电机
        # 1.8°:电机是 1.8 度的步进电机

        # https://blog.csdn.net/android_lover2014/article/details/53462089
        # http://www.uimotion.com/news/253.html
        # 什么是步距角呢，简单点说就是我们的步进电机每一个脉冲所走的角度
        # 我这个电机的步距角是 1.8 度，所以走一圈是需要 200 个脉冲的

        # 支持 1~256 任意细分
        # 设置细分步数(默认16细分)
        assert self.last_position_deg is not None
        self.last_position_deg = self.last_position_deg + delta_deg
        pulse = abs(degree_to_pulse(delta_deg, self.division)) 
        direction = self._positive_direction if delta_deg > 0 else reverse_direction(
            self._positive_direction)
        self.protocol.ctrl_speed_with_pulse_count(
            self.id, direction, speed, pulse)

    def set_degree_range(self, degree_min: float, degree_max: float):
        assert degree_min < degree_max
        self.degree_min = degree_min
        self.degree_max = degree_max

    async def get_degree(self, timeout=0.1, max_retry_times=3):
        self.last_position_deg = await self.protocol.read_position_deg(self.id, timeout, max_retry_times)
        return self.last_position_deg


class RotateTiltMotor:
    rotate_motor: Motor
    tilt_motor: Motor

    def __init__(self, rotate_motor: Motor, tilt_motor: Motor) -> None:
        self.rotate_motor = rotate_motor
        self.tilt_motor = tilt_motor

    def begin(self):
        self.rotate_motor.begin()
        self.tilt_motor.begin()

    # https://stackoverflow.com/questions/34377319/combine-awaitables-like-promise-all
    async def delta_degree(self, speed: int, rotate_delta: float, tilt_delta: float):
        self.rotate_motor.delta_degree(speed, rotate_delta)
        await asyncio.sleep(0.0025)
        self.tilt_motor.delta_degree(speed, tilt_delta)

    def to_degree(self, speed: int, rotate_degree: float, tilt_degree: float):
        self.rotate_motor.to_degree(speed, rotate_degree)
        self.tilt_motor.to_degree(speed, tilt_degree)

    async def to_degree_with_new_reading(self, speed: int, rotate_degree: float, tilt_degree: float, timeout=0.1, max_retry_times=3):
        asyncio.gather(
            self.rotate_motor.to_degree_with_new_reading(speed, rotate_degree, timeout, max_retry_times),
            self.tilt_motor.to_degree_with_new_reading(speed, tilt_degree, timeout, max_retry_times),
        )

    def set_degree_range(self, rotate_degree_range: Tuple[float, float], tilt_degree_range: Tuple[float, float]):
        self.rotate_motor.set_degree_range(*rotate_degree_range)
        self.tilt_motor.set_degree_range(*tilt_degree_range)

    async def get_degree(self, timeout=0.1, max_retry_times=3):
        # should not get the degree at the same time
        r = await self.rotate_motor.get_degree(timeout, max_retry_times)
        t = await self.tilt_motor.get_degree(timeout, max_retry_times)
        return (r, t)
