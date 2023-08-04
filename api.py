from motor.protocol import MotorProtocol
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
        # await asyncio.sleep(0.1)
        # data = ctrl_en_close_loop_pkt(ID, True)
        # transport.write(data)
        # await asyncio.sleep(0.1)
        # data = read_en_close_loop_pkt(ID)
        # await asyncio.sleep(0.1)
        # data = set_division_pkt(ID, 255)
        # while True:
        #     data = ctrl_speed_pkt(ID, Direction.CCW, 100)
        #     transport.write(data)
        #     await asyncio.sleep(2)
        #     data = ctrl_speed_pkt(ID, Direction.CCW, 120)
        #     transport.write(data)
        #     await asyncio.sleep(2)
        #     data = ctrl_speed_pkt(ID, Direction.CCW, 127)
        #     transport.write(data)
        #     await asyncio.sleep(2)
        #     data = ctrl_stop_pkt(ID)
        #     transport.write(data)
        #     await asyncio.sleep(3)

    loop.create_task(send_test())
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    main()
