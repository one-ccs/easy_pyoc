from typing import Callable, Literal
from threading import Thread
from multiprocessing import Process
import socket

from ..classes.logger import Logger


class ClientSocket():
    def __init__(
            self,
            *,
            protocol: Literal['TCP', 'UDP', 'MULTICAST'],
            target: tuple[str, int],
            bind: tuple[str, int] | None = None,
            bufsize: int = 1024,
            on_recv: Callable[[bytes, tuple[str, int]], None] | None = None,
            timeout: float | None = None,
            is_process: bool = False,
        ):
        """客户端套接字

        发送 TCP/UDP/MULTICAST 数据并接收响应。

        Args:
            protocol (str): 协议
            target (tuple[str, int]): 服务器地址和端口
            bind (tuple[str, int] | None, optional): 绑定地址, 端口为 `0` 时随机分配端口. 默认为 None.
            bufsize (int, optional): 接收缓冲区大小. 默认为 1024.
            on_recv (Callable[[tuple[str, int], bytes], None] | None, optional): 接收到数据时的回调函数, 参数为 (数据, 地址). 默认为 None.
            timeout (float | None, optional): TCP 连接超时时间, 单位为秒. 默认为 None.
            is_process (bool, optional): 是否使用进程模式接收数据, 即在子进程中运行. 默认为 False.

        Raises:
            ValueError: 无效的协议类型, 应为 [TCP, UDP, MULTICAST]
            ValueError: 无效的端口号, 应为 [1-65535]
            ValueError: 无效的绑定端口号, 应为 [1-65535]
        """
        self.__active = False
        self.__socked = False

        if protocol not in ['TCP', 'UDP', 'MULTICAST']:
            raise ValueError(f'ClientSocket 无效的协议类型 "{protocol}"')
        if target[1] < 1 or target[1] > 65535:
            raise ValueError(f'ClientSocket 无效的端口号 "{target[1]}"')
        if bind and (bind[1] < 0 or bind[1] > 65535):
            raise ValueError(f'ClientSocket 无效的绑定端口号 "{bind[1]}"')
        if on_recv and not callable(on_recv):
            raise ValueError(f'ClientSocket on_recv 必须为可调用对象')

        self.logger     = Logger()
        self.protocol   = protocol
        self.target     = target
        self.bind       = bind
        self.on_recv    = on_recv
        self.bufsize    = bufsize
        self.timeout    = timeout
        self.is_process = is_process
        self.sock: socket.socket | None = None
        self.thread: Thread | Process | None = None

    def __str__(self) -> str:
        if self.bind:
            return f'ClientSocket({self.protocol}, {self.target[0]}:{self.target[1]}, bind {self.bind[0]}:{self.bind[1]})'
        return f'ClientSocket({self.protocol}, {self.target[0]}:{self.target[1]})'

    def __del__(self):
        self.close()

    def __create_socket(self) -> bool:
        if self.__socked:
            return True

        try:
            match self.protocol:
                case 'TCP':
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    if self.bind:
                        self.sock.bind(self.bind)
                    self.sock.settimeout(self.timeout)
                    self.sock.connect((self.target[0], self.target[1]))
                case 'UDP':
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    if self.bind:
                        self.sock.bind(self.bind)
                    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    if self.target[0].endswith('.255'): # 设置 SO_BROADCAST 为 1, 允许发送广播数据包
                        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                case 'MULTICAST':
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                    self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
                    if self.bind:
                        self.sock.bind(self.bind)
                    self.sock.setsockopt(
                        socket.IPPROTO_IP,
                        socket.IP_ADD_MEMBERSHIP,
                        socket.inet_aton(self.target[0]) + socket.inet_aton('0.0.0.0'),
                    )
            if not self.bind or not self.bind[1]:
                self.bind = self.sock.getsockname()

            self.__socked = True
        except ConnectionRefusedError:
            self.logger.warning(f'{self} 无法连接: {self.target[0]}:{self.target[1]}')
        except Exception as e:
            self.logger.error(f'{self} 创建失败: \n{e}')

        return self.__socked

    def __recv_thread(self) -> None:
        self.__active = True

        while self.__active:
            try:
                data, addr = self.sock.recvfrom(self.bufsize)

                self.logger.debug(f'{self} 收到 {addr} 的数据: {data}')
                try:
                    self.on_recv(data, addr)
                except Exception as e:
                    self.logger.error(f'{self} "on_recv" 回调函数发生异常: \n{e}')
            except OSError as e:
                if e.errno == 10057:
                    self.logger.debug(f'{self} 接收失败连接未建立')
                    break
                elif e.errno == 10038: # 调用了 close() 方法
                    pass
                else:
                    self.logger.error(f'{self} 接收失败: \n{e}')

    def getpeername(self) -> tuple[str | None, int | None]:
        """返回套接字连接到的远程地址。"""
        if self.__create_socket():
            return self.sock.getpeername()
        return (None, None)

    def getsockname(self) -> tuple[str | None, int | None]:
        """返回套接字本身的地址。"""
        if self.__create_socket():
            return self.sock.getsockname()
        return (None, None)

    def send(self, data: bytes) -> None:
        if not self.__create_socket():
            self.logger.warning(f'{self} 未连接, 无法发送数据')
            return

        try:
            if self.protocol == 'TCP':
                self.sock.sendall(data)
            else:
                self.sock.sendto(data, (self.target[0], self.target[1]))
            self.logger.debug(f'{self} 发送数据: {data}')

            if self.on_recv and not self.thread:
                if self.is_process:
                    self.thread = Process(target=self.__recv_thread, daemon=True)
                else:
                    self.thread = Thread(target=self.__recv_thread, daemon=True)
                self.thread.start()
        except OSError as e:
            if e.errno == 10057:
                self.logger.debug(f'{self} 发送失败连接未建立')
            else:
                self.logger.error(f'{self} 发送失败: \n{e}')

    def close(self) -> bool:
        if self.__socked:
            try:
                self.__active = False
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                self.__socked = False
                self.logger.debug(f'{self} 已关闭')
            except Exception as e:
                self.logger.error(f'{self} 关闭失败: \n{e}')
        return not self.__socked
