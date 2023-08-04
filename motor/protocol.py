from loguru import logger
import asyncio
from asyncio_channel import create_channel
from asyncio_channel._channel import Channel
from .utils import hex_bytes
from .pkt import *
from typing import Optional, Tuple, Union, List, Dict, Callable, TypeVar

T = TypeVar('T')


class MotorProtocol(asyncio.Protocol):
    _chans: Dict[int, Tuple[bool, Channel]]

    def __init__(self) -> None:
        super().__init__()
        self._chans = {}

    def connection_made(self, transport):
        self.transport = transport
        logger.info('port opened')
        transport.serial.rts = False  # type: ignore

    def data_received(self, data):
        logger.debug("[received] {}".format(hex_bytes(data)))
        id = data[0]
        if (id in self._chans):
            ok, chan = self._chans[id]
            if ok:
                chan.offer(data)
            else:
                logger.warning("{:02x} channel not ready".format(id))
        else:
            logger.warning("{:02x} channel not registered".format(id))

    def connection_lost(self, exc):
        logger.info('port closed')
        self.transport.loop.stop()  # type: ignore

    def pause_writing(self):
        logger.debug('pause writing; buffer size {}',
                     self.transport.get_write_buffer_size())  # type: ignore

    def resume_writing(self):
        logger.debug('resume writing; buffer size {}',
                     self.transport.get_write_buffer_size())  # type: ignore

    def register_device(self, id: int):
        logger.info("register device {:02x}".format(id))
        self._chans[id] = (False, create_channel())

    async def read_wrapper(self, id: int, write_cb: Callable[[], None], handler: Callable[[bytes], T], timeout: float = 0.1):
        if (id not in self._chans):
            raise Exception("device {:02x} not registered".format(id))
        try:
            _, chan = self._chans[id]
            self._chans[id] = (True, chan)
            write_cb()
            res = await self._chans[id][1].take(timeout=timeout)
            assert isinstance(res, bytes)
            self._chans[id] = (False, chan)
            return handler(res)
        except KeyboardInterrupt:
            _, chan = self._chans[id]
            self._chans[id] = (False, chan)
            raise KeyboardInterrupt
        except Exception as e:
            _, chan = self._chans[id]
            self._chans[id] = (False, chan)
            logger.error(e)
            await asyncio.sleep(0.02)
            return await self.read_encoder(id)

    async def read_encoder(self, id: int):
        return await self.read_wrapper(id, lambda: self.transport.write(read_encoder_pkt(id)),
                                       lambda res: struct.unpack("!BH", res)[1])

    async def read_input_pulse_count(self, id: int):
        return await self.read_wrapper(id, lambda: self.transport.write(read_input_pulse_count_pkt(id)),
                                       lambda res: struct.unpack("!BI", res)[1])

    # unit: max_uint16_t / 360
    # i.e. 65535 for a full circle
    # 655350 for 10 circles
    async def read_position(self, id: int, timeout: float = 0.1):
        return await self.read_wrapper(id, lambda: self.transport.write(read_position_pkt(id)),
                                       lambda res: struct.unpack("!Bi", res)[1], timeout=timeout)

    async def read_position_deg(self, id: int):
        pos = await self.read_position(id)
        return pos / 65535 * 360

    # unit: max_uint16_t / 360
    async def read_position_err(self, id: int):
        return await self.read_wrapper(id, lambda: self.transport.write(read_position_err_pkt(id)),
                                       lambda res: struct.unpack("!BH", res)[1])

    # 0: error
    # 1: enabled
    # 2: disabled
    async def read_en_close_loop(self, id: int):
        raise NotImplementedError

    async def read_stuck_flag(self, id: int):
        raise NotImplementedError

    def ctrl_speed(self, id: int, direction: Direction, speed: int):
        speed = int(speed)
        data = ctrl_speed_pkt(id, direction, speed)
        logger.debug("[{:02x}] direction:{} speed:{}".format(
            id, direction, speed))
        self.transport.write(data)

    def ctrl_en_close_loop(self, id: int, en: bool):
        data = ctrl_en_close_loop_pkt(id, en)
        self.transport.write(data)

    def ctrl_stop(self, id: int):
        data = ctrl_stop_pkt(id)
        self.transport.write(data)

    def ctrl_speed_with_pulse_count(self, id: int, direction: Direction, speed: int, pulse_count: int):
        assert(pulse_count > 0)
        data = ctrl_speed_with_pulse_count_pkt(
            id, direction, speed, pulse_count)
        logger.debug("data: {}".format(hex_bytes(data)))
        logger.debug("[{:02x}] direction:{} speed:{} pulse_count:{}".format(
            id, direction, speed, pulse_count))
        self.transport.write(data)

    def set_division(self, id: int, division: int):
        data = set_division_pkt(id, division)
        self.transport.write(data)
