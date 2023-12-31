from typing import Optional
from motor.protocol import MotorProtocol, Direction
from loguru import logger
import asyncio
import serial_asyncio
import click
from dataclasses import dataclass
from datetime import datetime
from motor.motor import Motor

# https://stackoverflow.com/questions/29269370/how-to-properly-create-and-run-concurrent-tasks-using-pythons-asyncio-module
@click.command()
@click.option("--port", "-p", help='Serial port', required=True)
@click.option("--baudrate", "-b", default=38400, help='Baudrate')
def main(port: str, baudrate: int):
    loop = asyncio.get_event_loop()
    routine = serial_asyncio.create_serial_connection(
        loop, MotorProtocol, port, baudrate=baudrate)
    protocol: MotorProtocol
    _, protocol = loop.run_until_complete(routine)
    ID = 0xe0
    motor = Motor(ID, protocol)
    motor.begin()

    async def send_test():
        import random
        rnd_direction = random.choice([Direction.CW, Direction.CCW])
        rnd_spd = random.randint(20, 120)
        rnd_time = random.randint(3, 8)
        protocol.ctrl_speed(ID, rnd_direction, rnd_spd)
        await asyncio.sleep(rnd_time)
        await motor.to_degree_with_new_reading(100, 0)

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
