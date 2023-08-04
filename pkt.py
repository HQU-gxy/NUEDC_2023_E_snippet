from enum import Enum, auto
from .protocol import *
import struct

class FlagWidth(Enum):
  CHAR = auto()
  SHORT = auto()

class Direction(Enum):
  CLOCKWISE = 0
  COUNTER_CLOCKWISE = 1
  
def get_flag_width(flag:int) -> FlagWidth:
  if flag <= 0xff:
    return FlagWidth.CHAR
  elif flag <= 0xffff:
    return FlagWidth.SHORT
  else:
    raise ValueError('invalid flag: %d' % flag)

def serialize(id:int, flag:int, data:bytes):
  assert id >= 0 and id <= 255
  fmt:str
  match get_flag_width(flag):
    case FlagWidth.CHAR:
      fmt = ">BB%{}sB".format(len(data))
    case FlagWidth.SHORT:
      fmt = ">BH%{}sB".format(len(data))
  packet = struct.pack(fmt, id, flag, data, END_BYTE)
  return packet

def action_encoder_calibrate_pkt(id:int):
  return serialize(id, ACTION_ENCODER_CALIBRATE_S, b'')

def action_set_current_zero_pkt(id:int):
  return serialize(id, ACTION_SET_CURRENT_ZERO_S, b'')

def action_protection_disable_pkt(id:int):
  return serialize(id, ACTION_PROTECTION_DISABLE_S, b'')

def read_encoder_pkt(id:int):
  return serialize(id, READ_ENCODER, b'')

def read_input_pulse_count_pkt(id:int):
  return serialize(id, READ_INPUT_PULSE_COUNT, b'')

def read_position_error_pkt(id:int):
  return serialize(id, READ_POSITION_ERROR, b'')

def read_en_close_loop_pkt(id:int):
  return serialize(id, READ_EN_CLOSE_LOOP, b'')

def read_auto_zero_err_pkt(id:int):
  return serialize(id, READ_AUTO_ZERO_ERR, b'')

def set_division_pkt(id:int, division:int):
  assert division >= 1 and division <= 255
  return serialize(id, SET_DIVISION, struct.pack('>B', division))

def set_device_id_pkt(id:int, new_id:int):
  assert new_id >= 1 and new_id <= 247
  return serialize(id, SET_DEVICE_ID, struct.pack('>B', new_id))

def ctrl_en_close_loop_pkt(id:int, en:bool):
  return serialize(id, CTRL_EN_CLOSE_LOOP, struct.pack('>B', int(en)))

def ctrl_speed_pkt(id:int, direction:Direction, speed:int, accel:int):
  direction = direction.value
  assert speed >= 0 and speed <= 1279
  assert accel >= 0 and accel <= 255
  data = struct.pack('>HB', (direction << 12) | speed, accel)
  return serialize(id, CTRL_SPEED, data)

def ctrl_position_pkt(id:int, direction:Direction, position:int, speed:int, accel:int):
  direction = direction.value
  assert position >= 0 and position <= 4095
  assert speed >= 0 and speed <= 1279
  assert accel >= 0 and accel <= 255
  data = struct.pack('>HBB', (direction << 12) | position, speed, accel)
  return serialize(id, CTRL_POSITION, data)

def ctrl_speed_hold_pkg(id:int, clear:bool = False):
  if clear:
    serialize(id, CTRL_SPEED_HOLD_CLR_S, b'')
  else:
    serialize(id, CTRL_SPEED_HOLD_S, b'')


