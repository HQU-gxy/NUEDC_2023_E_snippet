from enum import Enum, auto
from .constant import *
import struct


class FlagWidth(Enum):
    CHAR = auto()
    SHORT = auto()


class Direction(Enum):
    CW = 0x00
    CCW = 0x01


def get_flag_width(flag: int) -> FlagWidth:
    if flag <= 0xff:
        return FlagWidth.CHAR
    elif flag <= 0xffff:
        return FlagWidth.SHORT
    else:
        raise ValueError("invalid flag: {}".format(flag))


def serialize(id: int, flag: int, data: bytes):
    assert id >= 0 and id <= 255
    fmt: str
    # check if is python 3.10 or above
    import sys
    if sys.version_info >= (3, 10):
        match get_flag_width(flag):
            case FlagWidth.CHAR:
                fmt = ">BB{}s".format(len(data))
            case FlagWidth.SHORT:
                fmt = ">BH{}s".format(len(data))
    else:
        if flag <= 0xff:
            fmt = ">BB{}s".format(len(data))
        elif flag <= 0xffff:
            fmt = ">BH{}s".format(len(data))
        else:
            raise ValueError("invalid flag: {}".format(flag))
    packet = struct.pack(fmt, id, flag, data)
    return packet


def read_encoder_pkt(id: int):
    return serialize(id, READ_ENCODER, b'')


def read_input_pulse_count_pkt(id: int):
    return serialize(id, READ_INPUT_PULSE_COUNT, b'')


def read_position_pkt(id: int):
    return serialize(id, READ_POSITION, b'')


def read_position_error_pkt(id: int):
    return serialize(id, READ_POSITION_ERROR, b'')


def read_en_close_loop_pkt(id: int):
    return serialize(id, READ_EN_CLOSE_LOOP, b'')


def read_stuck_flag_pkt(id: int):
    return serialize(id, READ_STUCK_FLAG, b'')


def set_division_pkt(id: int, division: int):
    assert division >= 0 and division <= 255
    return serialize(id, SET_DIVISION, struct.pack('>B', division))


def ctrl_en_close_loop_pkt(id: int, en: bool):
    return serialize(id, CTRL_EN_CLOSE_LOOP, struct.pack('>B', int(en)))


def ctrl_speed_pkt(id: int, direction: Direction, speed: int):
    direction = direction.value
    assert (speed >= 0 and speed < 128)
    s = ((direction & 0x01) << 7) | (speed & 0xff)
    data = struct.pack('>B', s)
    return serialize(id, CTRL_SPEED, data)


def ctrl_speed_with_pulse_count_pkt(id: int, direction: Direction, speed: int, pulse_count: int):
    direction = direction.value
    assert (speed >= 0 and speed < 128)
    s = ((direction & 0x01) << 7) | (speed & 0xff)
    data = struct.pack('>B3s', s, pulse_count.to_bytes(3, 'big'))
    return serialize(id, CTRL_SPEED_WITH_PULSE_CNT, data)


def ctrl_stop_pkt(id: int):
    return serialize(id, CTRL_STOP, b'')


def ctrl_speed_hold_pkg(id: int, clear: bool = False):
    if clear:
        serialize(id, CTRL_SPEED_HOLD_CLR_S, b'')
    else:
        serialize(id, CTRL_SPEED_HOLD_S, b'')
