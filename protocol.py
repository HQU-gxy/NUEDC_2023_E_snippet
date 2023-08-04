BROADCAST_ADDR = 0x00
END_BYTE = 0x6b

## ACTION
## S means short (2 bytes, int16_t)
ACTION_ENCODER_CALIBRATE_S = 0x0645
ACTION_SET_CURRENT_ZERO_S = 0x0a6d
ACTION_PROTECTION_DISABLE_S = 0x0e52
# read param

## READ

READ_ENCODER = 0x30
# @ret <device_id> int32_t <end_byte>
READ_INPUT_PULSE_COUNT = 0x33
# @ret <device_id> int16_t <end_byte>
# @note `servo turned in deg = position_error * 360 / 65536`
READ_POSITION_ERROR = 0x39
# @ret <device_id> uint8_t (bool) <end_byte>
READ_EN_CLOSE_LOOP = 0x3a
# 读取单圈上电自动回零状态标志/闭环电机的堵转标志
# @ret <device_id> uint8_t (bool) <end_byte>
READ_AUTO_ZERO_ERR = 0x3f

## SET

# @param <device_id> <flag> <division>[uint8_t] <end_byte>
SET_DIVISION = 0x84
# @param <device_id> <flag> <id>[uint8_t][1-247] <end_byte>
SET_DEVICE_ID = 0xae

## CTRL

# @param <device_id> <flag> <en>[bool] <end_byte>
CTRL_EN_CLOSE_LOOP = 0xf3

# @param <device_id> <flag> <direction&speed>[int16_t] <accel>[uint8_t] <end_byte>
# @note <direction&speed> high 4 bits is direction, low 12 bits is speed (max
# value 0x04ff i.e. 1279)
# @note <accel> 0xff means no acceleration limit
# @note <direction> 0x0 means clockwise, 0x1 means counter-clockwise
CTRL_SPEED = 0xf6
# 存储/清除闭环电机正反转，即速度模式当前的参数，上电会自动运行
CTRL_SPEED_HOLD_S = 0xffca
CTRL_SPEED_HOLD_CLR_S = 0xffc8

# @param <device_id> <flag> <direction&speed>[int16_t] <accel>[uint8_t] <pulse_count>[uint24_t] <end_byte>
# @note see also [CTRL_SPEED]. run to the specified pulse count
# @ret <device_id> <flag>[0x02, 0x9f] <end_byte>
#  0x02 means start running, 0x9f means running finished
CTRL_POSITION = 0xfd
