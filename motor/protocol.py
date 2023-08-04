from loguru import logger
import asyncio
from asyncio_channel import create_channel
from asyncio_channel._channel import Channel
from .utils import hex_bytes
from .pkt import *


class MotorProtocol(asyncio.Protocol):
    _chan_recv_flag:bool = False
    _chan: Channel

    def __init__(self) -> None:
        super().__init__()
        self._chan = create_channel()

    def connection_made(self, transport):
        self.transport = transport
        logger.info('port opened')
        transport.serial.rts = False

    def data_received(self, data):
        flag_str = "T" if self._chan_recv_flag else "F"
        logger.debug("[{}] received: {}".format(flag_str, hex_bytes(data)))
        if (self._chan_recv_flag):
            self._chan.offer(data)

    def connection_lost(self, exc):
        logger.info('port closed')
        self.transport.loop.stop()

    def pause_writing(self):
        logger.debug('pause writing; buffer size {}',
                     self.transport.get_write_buffer_size())

    def resume_writing(self):
        logger.debug('resume writing; buffer size {}',
                     self.transport.get_write_buffer_size())

    async def read_encoder(self, id: int):
        try:
            data = read_encoder_pkt(id)
            self._chan_recv_flag = True
            self.transport.write(data)
            res = await self._chan.take()
            self._chan_recv_flag = False
            fmt = "!BH"
            encoder: int
            _, encoder = struct.unpack(fmt, res)
            return encoder
        except KeyboardInterrupt:
            self._chan_recv_flag = False
            raise KeyboardInterrupt
        except Exception as e:
            self._chan_recv_flag = False
            logger.error(e)
            asyncio.sleep(0.02)
            return await self.read_encoder(id)

    async def read_input_pulse_count(self, id: int):
        try:
            data = read_input_pulse_count_pkt(id)
            self._chan_recv_flag = True
            self.transport.write(data)
            res = await self._chan.take()
            self._chan_recv_flag = False
            fmt = "!BI"
            input_pulse_count: int
            _, input_pulse_count = struct.unpack(fmt, res)
            return input_pulse_count
        except KeyboardInterrupt:
            self._chan_recv_flag = False
            raise KeyboardInterrupt
        except Exception as e:
            self._chan_recv_flag = False
            logger.error(e)
            asyncio.sleep(0.02)
            return await self.read_input_pulse_count(id)

    # unit: max_uint16_t / 360
    # i.e. 65535 for a full circle
    # 655350 for 10 circles
    async def read_position(self, id: int):
        try:
            data = read_position_pkt(id)
            self._chan_recv_flag = True
            self.transport.write(data)
            res = await self._chan.take()
            self._chan_recv_flag = False
            # signed
            # positive: CW
            # negative: CCW
            # i.e. CW would make the position decrease
            fmt = "!Bi"
            position: int
            _, position = struct.unpack(fmt, res)
            return position
        except KeyboardInterrupt:
            self._chan_recv_flag = False
            raise KeyboardInterrupt
        except Exception as e:
            self._chan_recv_flag = False
            logger.error(e)
            asyncio.sleep(0.02)
            return await self.read_position(id)
    
    async def read_position_deg(self, id: int):
        pos = await self.read_position(id)
        return pos / 65535 * 360

    # unit: max_uint16_t / 360
    async def read_position_err(self, id: int):
        try:
            data = read_position_error_pkt(id)
            self._chan_recv_flag = True
            self.transport.write(data)
            res = await self._chan.take()
            self._chan_recv_flag = False
            fmt = "!BH"
            position_err: int
            _, position_err = struct.unpack(fmt, res)
            return position_err
        except KeyboardInterrupt:
            self._chan_recv_flag = False
            raise KeyboardInterrupt
        except Exception as e:
            self._chan_recv_flag = False
            logger.error(e)
            asyncio.sleep(0.02)
            return await self.read_position_err(id)

    # 0: error
    # 1: enabled
    # 2: disabled
    async def read_en_close_loop(self, id: int):
        data = read_en_close_loop_pkt(id)
        self._chan_recv_flag = True
        self.transport.write(data)
        res = await self._chan.take()
        self._chan_recv_flag = False
        fmt = "!BB"
        en_close_loop: int
        _, en_close_loop = struct.unpack(fmt, res)
        return en_close_loop

    async def read_stuck_flag(self, id: int):
        data = read_stuck_flag_pkt(id)
        self._chan_recv_flag = True
        self.transport.write(data)
        res = await self._chan.take()
        self._chan_recv_flag = False
        fmt = "!BB"
        stuck_flag: int
        _, stuck_flag = struct.unpack(fmt, res)
        return stuck_flag

    def ctrl_speed(self, id: int, direction: Direction, speed: int):
        data = ctrl_speed_pkt(id, direction, speed)
        logger.debug("direction:{} speed:{}".format(direction, speed))
        self.transport.write(data)

    def ctrl_en_close_loop(self, id: int, en: bool):
        data = ctrl_en_close_loop_pkt(id, en)
        self.transport.write(data)

    def ctrl_stop(self, id: int):
        data = ctrl_stop_pkt(id)
        self.transport.write(data)

    def ctrl_speed_with_pulse_count(self, id: int, direction: Direction, speed: int, pulse_count: int):
        data = ctrl_speed_with_pulse_count_pkt(
            id, direction, speed, pulse_count)
        logger.debug("direction:{} speed:{} pulse_count:{}".format(
            direction, speed, pulse_count))
        self.transport.write(data)

    def set_division(self, id: int, division: int):
        data = set_division_pkt(id, division)
        self.transport.write(data)
