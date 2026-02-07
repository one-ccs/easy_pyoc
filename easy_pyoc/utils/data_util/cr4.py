"""CR4 算法工具"""


def cr4(key: str | bytes, data: str | bytes, encoding: str = 'utf-8') -> str | bytes:
    """使用 CR4 算法加密 (str) 或解密 (bytes) 数据

    Args:
        key (str | bytes): 密钥
        data (str | bytes): 待加密或解密的数据
        encoding (str, optional): 编码格式. 默认为 'utf-8'.

    Returns:
        str | bytes: 加密 (bytes) 或解密 (str) 后的数据
    """
    _key = bytes(key, encoding) if isinstance(key, str) else key
    _data = bytes(data, encoding) if isinstance(data, str) else data

    S, j = list(range(256)), 0
    for i in range(256):
        j = (j + S[i] + _key[i % len(_key)]) % 256
        S[i], S[j] = S[j], S[i]

    i, j, result = 0, 0, []
    for char in _data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        result.append(char ^ S[(S[i] + S[j]) % 256])

    return bytes(result) if isinstance(data, str) else bytes(result).decode(encoding)


def encrypt(key: str | bytes, data: str, encoding: str = 'utf-8') -> bytes:
    """加密数据

    Args:
        key (str | bytes): 密钥
        data (str): 待加密的数据
        encoding (str, optional): 编码格式. 默认为 'utf-8'.

    Returns:
        bytes: 加密后的数据
    """
    return cr4(key, data, encoding)


def decrypt(key: str | bytes, data: bytes, encoding: str = 'utf-8') -> str:
    """解密数据

    Args:
        key (str | bytes): 密钥
        data (bytes): 待解密的数据
        encoding (str, optional): 编码格式. 默认为 'utf-8'.

    Returns:
        str: 解密后的数据
    """
    return cr4(key, data, encoding)
