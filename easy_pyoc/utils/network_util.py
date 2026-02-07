"""网络工具"""

from typing import Callable, Literal
from threading import Lock
import socket
import ipaddress

from ..sock.server import ServerSocket
from ..sock.client import ClientSocket


lock = Lock()


def is_ip(ip: str) -> bool:
    """判断是否为合法的 IP 地址

    Args:
        ip (str): IP 地址

    Returns:
        bool: 是否为合法的 IP 地址
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_host(host: str) -> bool:
    """判断是否为合法的主机名或 IP 地址

    Args:
        host (str): 主机名或 IP 地址

    Returns:
        bool: 是否为合法的主机名或 IP 地址
    """
    try:
        socket.gethostbyname(host)
        return True
    except socket.gaierror:
        return False


def classify_ip(ipv4: str) -> Literal['A', 'B', 'C', 'D', 'E']:
    """根据 IPv4 地址的第一个字节判断 IPv4 地址的分类

    Args:
        ipv4 (str): IPv4 地址

    Raises:
        ValueError: 无效的 IPv4 地址

    Returns:
        str: IPv4 地址分类 {'A', 'B', 'C', 'D', 'E'}
    """
    if not is_ip(ipv4):
        raise ValueError('无效的 IPv4 地址')
    first_octet = int(ipv4.split('.')[0])

    if 1 <= first_octet <= 126:
        return 'A'
    elif 128 <= first_octet <= 191:
        return 'B'
    elif 192 <= first_octet <= 223:
        return 'C'
    elif 224 <= first_octet <= 239:
        return 'D'
    else:
        return 'E'


def get_hostname() -> str:
    """返回一个字符串，包含当前正在运行 Python 解释器的机器的主机名。

    Returns:
        str: 主机名
    """
    return socket.gethostname()


def get_host_by_name(hostname: str) -> str:
    """将主机名转换为 IPv4 地址格式。IPv4 地址以字符串格式返回，如 '100.50.200.5'。
    如果主机名本身是 IPv4 地址，则原样返回。

    Args:
        hostname (str): 主机名

    Returns:
        str: IP 地址
    """
    return socket.gethostbyname(hostname)


def get_host_by_name_ex(hostname: str) -> tuple[str, list[str], list[str]]:
    """将一个主机名转换为 IPv4 地址格式的扩展接口。 返回一个 3 元组 (hostname, aliaslist, ipaddrlist)
    其中 hostname 是主机的首选主机名，aliaslist 是同一地址的备选主机名列表（可能为空），而 ipaddrlist
    是同一主机上同一接口的 IPv4 地址列表（通常为单个地址但并不总是如此）。

    Args:
        hostname (str): 主机名

    Returns:
        tuple[str, list[str], list[str]]: 3 元组 (hostname, aliaslist, ipaddrlist)
    """
    return socket.gethostbyname_ex(hostname)


def get_local_ip(error: Literal['ignore', 'raise'] = 'ignore') -> str:
    """获取本地 IP 地址

    Args:
        error (Literal['ignore', 'raise'], optional): 错误处理方式. 默认为 'ignore'.

    Returns:
        str: 本地 IP 地址或 ""
    """
    local_ip = ''

    try:
        # 通过路由表获取本地 IP 地址
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        local_ip = sock.getsockname()[0]
        sock.close()
    except:
        if error == 'raise': raise

        try:
            # 通过主机名获取本地 IP 地址
            hostname = socket.gethostname()
            if not(_local_ip := socket.gethostbyname(hostname)).startswith('127.'):
                local_ip = _local_ip
        except:
            if error == 'raise': raise

    return local_ip


def get_local_ips() -> list[str]:
    """获取本地 IP 地址列表

    Returns:
        _type_: 本地 IP 地址列表
    """
    hostname = socket.gethostname()
    ips = socket.gethostbyname_ex(hostname)[2]
    return ips


def get_broadcast_address(ip_network: str) -> str:
    """返回对应 IPv4 地址的广播地址

    Example:
        >>> get_broadcast_address('192.168.1.100/24')
        '192.168.1.255'

        >>> get_broadcast_address('192.168.1.100')
        '192.168.1.255'

    Args:
        ip_network (str): IPv4 地址

    Returns:
        str: 广播地址
    """
    if not '/' in ip_network:
        if classify := classify_ip(ip_network):
            netmask = {'A': '/8', 'B': '/16', 'C': '/24', 'D': '/24', 'E': '/32'}[classify]
            ip_network = f'{ip_network}{netmask}'

    ip_network = ipaddress.ip_network(ip_network, strict=False)
    return str(ip_network.broadcast_address)


def create_multicast_server(
    group: tuple[str, int],
    on_recv: Callable[[bytes, tuple[str, int], Callable[[bytes], int]], None],
) -> ServerSocket:
    """创建一个组播服务端

    Args:
        group (tuple[str, int]): 组播地址
        on_recv (Callable[[bytes, tuple[str, int], Callable[[bytes], int]], None]): 接收到数据时的回调函数

    Returns:
        ServerSocket: 组播服务端套接字
    """
    return ServerSocket(protocol='MULTICAST', bind=('', group[1]), group=group[0], on_recv=on_recv)


def create_multicast_client(
    group: tuple[str, int],
    on_recv: Callable[[bytes, tuple[str, int]], None],
) -> ClientSocket:
    """创建一个组播客户端

    Args:
        group (tuple[str, int]): 组播地址
        on_recv (Callable[[bytes, tuple[str, int]], None]): 接收到数据时的回调函数

    Returns:
        ClientSocket: 组播客户端套接字
    """
    return ClientSocket(protocol='MULTICAST', target=group, on_recv=on_recv)


def send_WOL(mac_hex: str, *, port: int = 9527) -> None:
    """向本机的所有网卡发送网络唤醒包

    Args:
        mac_hex (str): mac 地址
        port (int, optional): 发送广播的端口. 默认为 9527.
    """
    mac_hex      = mac_hex.replace(':', '').replace('-', '')
    magic_packet = bytes.fromhex('ff' * 6 + mac_hex * 16)

    for local_ip in get_local_ips():
        broadcast_host = get_broadcast_address(local_ip)

        client_socket = ClientSocket(protocol="UDP", target=(broadcast_host, port), bind=(local_ip, 0))
        client_socket.send(magic_packet)
        client_socket.close()


def length_stream(data: bytes, len_size: int = 2, *, filter: Callable[[bytes], bool] | None = None) -> list[bytes]:
    """解析带长度前缀的数据，可以应对粘包拆包问题

    Args:
        data (bytes): 带长度前缀的数据
        size_len (int, optional): 长度前缀的字节数. 默认为 2.
        filter (Callable[[bytes], bool] | None, optional): 过滤函数。整包或拆包的第一个包返回 `True`；非拆包的第一个包返回 `False`，将放入 `buffer` 等待接收到足够长度的数据. 默认为 None.

    Attrs:
        buffer (bytes): 缓存数据
        extract (Callable[[bytes, int], tuple[list[bytes], bytes]]): 提取数据包
        clear (Callable[[], None]): 清空缓存

    Returns:
        list[bytes]: 解析后的包列表

    Example:
        >>> def on_recv(data: bytes, addr: tuple[str, int]):
        >>>     for packet in length_stream(data, filter=lambda d: d[:2] == d[4:6]):
        >>>         print(packet)
    """
    if not hasattr(length_stream, 'buffer'):
        with lock:
            if not hasattr(length_stream, 'buffer'):
                def extract(data: bytes, len_size: int):
                    len_data, unpacked, i = len(data), [], 0

                    while i + len_size < len_data:
                        len_packet = int.from_bytes(data[i : i + len_size], 'big')

                        if len_packet == 0:
                            continue
                        if i + len_size + len_packet > len_data:
                            break

                        i += len_size
                        packet_data = data[i : i + len_packet]
                        i += len_packet

                        unpacked.append(packet_data)

                    return unpacked, data[i:]

                def clear():
                    length_stream.buffer = b''

                length_stream.buffer = b''
                length_stream.extract = extract
                length_stream.clear = clear

    if callable(filter) and not filter(data):
        unpacked, length_stream.buffer = length_stream.extract(length_stream.buffer + data, len_size)
        return unpacked

    unpacked, bf = length_stream.extract(data, len_size)
    length_stream.buffer += bf

    if length_stream.buffer:
        _unpacked, length_stream.buffer = length_stream.extract(length_stream.buffer, len_size)
        unpacked.extend(_unpacked)

    return unpacked
