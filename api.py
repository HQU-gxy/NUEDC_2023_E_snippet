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

    async def send_test():
        ID = 0xe2
        while True:
          protocol.ctrl_speed(ID, Direction.CW, 100)
          await asyncio.sleep(1)
          protocol.ctrl_speed(ID, Direction.CCW, 100)
          await asyncio.sleep(1)
          protocol.ctrl_stop(ID)
          await asyncio.sleep(0.05)
          pos = await  protocol.read_position(ID)
          logger.info("pos: {}".format(pos))
          
          await asyncio.sleep(2)

    loop.create_task(send_test())
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    main()
