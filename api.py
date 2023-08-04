from typing import Optional
from motor.protocol import MotorProtocol, Direction
from motor.mapper import PiecewiseLinearParams, ExtremumParams, piecewise_linear_mapper
from loguru import logger
import asyncio
import serial_asyncio
import click
from dataclasses import dataclass
from datetime import datetime


class Instance:
    time: datetime

    def __init__(self) -> None:
        self.time = datetime.now()

    def elapsed(self) -> float:
        return (datetime.now() - self.time).total_seconds()

    def reset(self) -> None:
        self.time = datetime.now()

    def elapsed_reset(self) -> float:
        elapsed = self.elapsed()
        self.reset()
        return elapsed


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

    def __init__(self, id: int, protocol: MotorProtocol) -> None:
        self.id = id
        self.protocol = protocol
        self.last_motion = None
        self.last_position_deg = 0.0
        self.last_write = Instance()

    async def to_degree(self, degree: float, precision: float = 0.6):
        def is_in_range(pos: int | float, target: int | float, err: int | float):
            return abs(pos - target) < err

        MAX_POS_ABS = 18
        spd_ex = ExtremumParams(0, MAX_POS_ABS, 0, 10)
        spd_piece = PiecewiseLinearParams(10, 0.5, 0.8, 2.5)
        delay_ex = ExtremumParams(0, MAX_POS_ABS, 0.005, 0.05)
        delay_piece = PiecewiseLinearParams(10, 0.5, 0.8, 2.5)

        def pos_spd_map(pos): return piecewise_linear_mapper(
            pos, spd_ex, spd_piece)
        def pos_delay_map(pos): return piecewise_linear_mapper(
            pos, delay_ex, delay_piece)

        self.last_position_deg = await self.protocol.read_position_deg(self.id)
        spd = pos_spd_map(self.last_position_deg)
        await asyncio.sleep(0.01)
        while True:
            assert isinstance(self.last_position_deg, float)
            if is_in_range(self.last_position_deg, degree, precision):
                break
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

@click.command()
@click.option("--port", "-p", help='Serial port', required=True)
@click.option("--baudrate", "-b", default=38400, help='Baudrate')
def main(port: str, baudrate: int):
    loop = asyncio.get_event_loop()
    routine = serial_asyncio.create_serial_connection(
        loop, MotorProtocol, port, baudrate=baudrate)
    protocol: MotorProtocol
    transport, protocol = loop.run_until_complete(routine)
    ID = 0xe0
    ERR = 0.04
    motor = Motor(ID, protocol)

    async def send_test():
        import random
        rnd_direction = random.choice([Direction.CW, Direction.CCW])
        rnd_spd = random.randint(20, 120)
        rnd_time = random.randint(3, 8)
        protocol.ctrl_speed(ID, rnd_direction, rnd_spd)
        await asyncio.sleep(rnd_time)
        await motor.to_degree(0, ERR)

        await asyncio.sleep(1)
        while True:
            pos = await protocol.read_position(ID)
            pos_deg = (pos / 65536) * 360
            logger.info("pos: {}. deg: {}".format(pos, pos_deg))
            await asyncio.sleep(2)

    loop.create_task(send_test())
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    main()
