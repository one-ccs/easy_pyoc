"""数据校验、加密解密"""

from . import cr4 as cr4
from . import crc as crc


def xor_sum(data: bytes) -> int:
    """计算异或校验和

    Args:
        data (bytes): 数据

    Returns:
        int: 校验和
    """
    if not data: return 0

    size, sum, i = len(data), data[0], 1
    while i < size:
        sum ^= data[i]
        i += 1
    return sum
