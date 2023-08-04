from dataclasses import dataclass
from .pkt import *
from typing import Optional
from .protocol import MotorProtocol, Direction
from .mapper import PiecewiseLinearParams, ExtremumParams, piecewise_linear_mapper
from .utils import Instance
from loguru import logger
import asyncio


@dataclass
class Motion:
    speed: float
    direction: Direction


def reverse_direction(direction: Direction):
    return Direction.CCW if direction == Direction.CW else Direction.CW


class Motor:
    id: int
    protocol: MotorProtocol
    last_motion: Optional[Motion]
    last_position_deg: float
    last_write: Instance
    spd_ex: ExtremumParams
    spd_piece: PiecewiseLinearParams
    delay_ex: ExtremumParams
    delay_piece: PiecewiseLinearParams
    precision: float

    def __init__(self, id: int, protocol: MotorProtocol) -> None:
        MAX_POS_ABS = 18
        self.id = id
        self.protocol = protocol
        self.last_motion = None
        self.last_position_deg = 0.0
        self.last_write = Instance()
        self.spd_ex = ExtremumParams(0, MAX_POS_ABS, 0, 10)
        self.spd_piece = PiecewiseLinearParams(10, 0.5, 0.8, 2.5)
        self.delay_ex = ExtremumParams(0, MAX_POS_ABS, 0.005, 0.05)
        self.delay_piece = PiecewiseLinearParams(10, 0.5, 0.8, 2.5)
        self.precision = 0.1

    async def to_degree(self, degree: float, precision):
        # 5ms
        D = 0.005

        def is_in_range(pos: int | float, target: int | float, err: int | float):
            return abs(pos - target) < err

        def pos_spd_map(pos): return piecewise_linear_mapper(
            pos, self.spd_ex, self.spd_piece)
        def pos_delay_map(pos): return piecewise_linear_mapper(
            pos, self.delay_ex, self.delay_piece)

        self.last_position_deg = await self.protocol.read_position_deg(self.id)
        spd = pos_spd_map(self.last_position_deg)
        await asyncio.sleep(D)
        while True:
            assert isinstance(self.last_position_deg, float)
            if is_in_range(self.last_position_deg, degree, precision):
                err = await self.protocol.read_position_err(self.id)
                # will this work?
                if err < precision:
                    break
                else:
                    continue
            diff = degree - self.last_position_deg
            direction: Direction
            if diff > degree:
                direction = Direction.CCW
            else:
                direction = Direction.CW
            spd = pos_spd_map(self.last_position_deg)
            self.protocol.ctrl_speed(self.id, direction, int(spd))
            self.last_motion = Motion(spd, direction)
            await asyncio.sleep(pos_delay_map(self.last_position_deg))
            self.last_position_deg = await self.protocol.read_position_deg(self.id)
            logger.debug("pos: {}".format(self.last_position_deg))
        self.protocol.ctrl_stop(self.id)

    async def delta_degree(self, delta: float, precision: float | None = None):
        deg = await self.protocol.read_position_deg(self.id)
        self.last_position_deg = deg
        assert isinstance(self.last_position_deg, float)
        if precision is None:
            precision = self.precision
        await self.to_degree(self.last_position_deg + delta, self.precision)


class RotateTiltMotor:
    rotate_motor: Motor
    tilt_motor: Motor

    def __init__(self, rotate_motor: Motor, tilt_motor: Motor) -> None:
        self.rotate_motor = rotate_motor
        self.tilt_motor = tilt_motor

    # https://stackoverflow.com/questions/34377319/combine-awaitables-like-promise-all
    async def delta_degree(self, rotate_delta: float, tilt_delta: float):
        await asyncio.gather(
            self.rotate_motor.delta_degree(rotate_delta),
            self.tilt_motor.delta_degree(tilt_delta)
        )
