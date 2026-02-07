"""CRC 校验工具"""


def crc16_xmodem(data: bytes, polynomial: int = 0x1021) -> int:
    """计算给定数据的 CRC16-XMODEM 校验值。

    Args:
        data (bytes): 需要计算 CRC 的字节数据。
        polynomial (hexadecimal, optional): CRC16-XMODEM 多项式。默认为 `0x1021`。

    Returns:
        int: 计算得到的 CRC16-XMODEM 校验值。
    """
    crc = 0  # 初始值为0

    for byte in data:
        crc ^= byte << 8  # 将字节移到高位，并与当前CRC值异或

        for _ in range(8):  # 对每个字节的每一位进行处理
            if crc & 0x8000:  # 如果最高位为1
                crc = (crc << 1) ^ polynomial  # 左移一位并与多项式异或
            else:
                crc <<= 1  # 否则左移一位
            crc &= 0xFFFF  # 保持CRC为16位

    return crc

def crc16_modbus(data: bytes, polynomial: int = 0xA001) -> int:
    """计算指定数据的 CRC16-MODBUS 校验值。

    Args:
        data (bytes): 需要计算 CRC 的字节数据。
        polynomial (_type_, optional): CRC16-MODBUS 多项式。默认为 `0xA001`。

    Returns:
        int: 计算得到的 CRC16-MODBUS 校验值。
    """
    crc = 0xFFFF

    for byte in data:
        crc ^= byte  # 异或字节转换为 CRC 的最低有效字节

        for _ in range(8):  # 对每个字节的每一位进行处理
            if (crc & 0x0001):  # 如果设置了 LSB
                crc >>= 1  # 右移一位
                crc ^= polynomial  # 与多项式异或
            else:
                crc >>= 1  # 仅右移一位
            crc &= 0xFFFF  # 保持 CRC 为16位

    return crc
