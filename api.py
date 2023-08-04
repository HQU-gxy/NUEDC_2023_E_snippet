from motor.protocol import MotorProtocol, Direction
from loguru import logger
import asyncio
import serial_asyncio
import click

@click.command()
@click.option("--port", "-p", help='Serial port', required=True)
@click.option("--baudrate", "-b", default=38400, help='Baudrate')
def main(port: str, baudrate: int):
    loop = asyncio.get_event_loop()
    routine = serial_asyncio.create_serial_connection(
        loop, MotorProtocol, port, baudrate=baudrate)
    protocol: MotorProtocol
    transport, protocol = loop.run_until_complete(routine)

    def reverse_direction(direction:Direction):
      return Direction.CCW if direction == Direction.CW else Direction.CW

    async def to_zero(id:int):
        direction = Direction.CCW
        spd = 10
        MAP_SPD = 120
        MIN_SPD = 1
        MAP_POS = 1080

        protocol.ctrl_speed(id, direction, spd)
        while True:
            ERR = 0.1
            await asyncio.sleep(0.01)
            pos = await protocol.read_position_deg(id)
            logger.debug("pos: {}".format(pos))
            await asyncio.sleep(0.01)
            if abs(pos) < 1:
              break
            if pos > 0:
              if direction == Direction.CCW:
                direction = reverse_direction(direction)
                protocol.ctrl_speed(id, direction, spd)
                await asyncio.sleep(0.01)
            else:
              if direction == Direction.CW:
                direction = reverse_direction(direction)
                protocol.ctrl_speed(id, direction, spd)
                await asyncio.sleep(0.01)
            await asyncio.sleep(0.5)
        protocol.ctrl_stop(id)

    async def send_test():
        ID = 0xe2
        await to_zero(ID)

        await asyncio.sleep(1)
        while True:
          pos = await  protocol.read_position(ID)
          pos_deg = (pos / 65536) * 360
          logger.info("pos: {}. deg: {}".format(pos, pos_deg))
          await asyncio.sleep(2)

    loop.create_task(send_test())
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    main()
