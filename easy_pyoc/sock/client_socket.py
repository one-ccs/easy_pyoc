#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket

from ..logger import Logger


class ClientSocket():
    def __init__(self, *, protocol: str, ip: str, port: int, bind: tuple[str, int] | None = None, recv_timeout: float = 1.5):
        """客户端套接字

        发送 TCP/UDP/MULTICAST 数据并接收响应。

        Args:
            protocol (str): 协议
            ip (str): 服务端 ip 地址
            port (int): 服务端端口号
            bind (tuple[str, int] | None, optional): 绑定地址. 默认为 None.
            recv_timeout (float, optional): 接收超时时间, 0 为无超时. 默认为 1.5.

        Raises:
            ValueError: 无效的协议类型, 应为 [TCP, UDP, MULTICAST]
            ValueError: 无效的端口号, 应为 [1-65535]
            ValueError: 无效的绑定端口号, 应为 [1-65535]
        """
        self.__connected = False

        if protocol not in ['TCP', 'UDP', 'MULTICAST']:
            raise ValueError(f'ServerSocket 无效的协议类型 "{protocol}"')
        if port < 1 or port > 65535:
            raise ValueError(f'ServerSocket 无效的端口号 "{port}"')
        if bind and (bind[1] < 1 or bind[1] > 65535):
            raise ValueError(f'ServerSocket 无效的绑定端口号 "{bind[1]}"')

        self.logger = Logger()
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.bind = bind
        self.recv_timeout = recv_timeout
        self.sock: socket.socket | None = None

    def __str__(self) -> str:
        if self.bind:
            return f"ClientSocket({self.protocol}, {self.ip}:{self.port}, bind {self.bind[0]}:{self.bind[1]})"
        return f"ClientSocket({self.protocol}, {self.ip}:{self.port})"

    def __del__(self):
        self.close()

    def connect(self) -> bool:
        if not self.__connected:
            try:
                match self.protocol:
                    case 'TCP':
                        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        if self.bind:
                            self.sock.bind(self.bind)
                        self.sock.connect((self.ip, self.port))
                    case 'UDP':
                        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        if self.bind:
                            self.sock.bind(self.bind)
                        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        if self.ip.endswith('.255'): # 设置 SO_BROADCAST 为 1, 允许发送广播数据包
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
                            socket.inet_aton(self.ip) + socket.inet_aton('0.0.0.0'),
                        )
                if isinstance(self.recv_timeout, (int, float)) and self.recv_timeout > 0:
                    self.sock.settimeout(self.recv_timeout)
                self.__connected = True
            except ConnectionRefusedError:
                self.logger.debug(f'{self} 无法连接: {self.ip}:{self.port}')
            except Exception as e:
                self.logger.error(f'{self} 创建失败: \n{e}')
        return self.__connected

    def send(self, data: bytes) -> None:
        if self.connect():
            try:
                if self.protocol == 'TCP':
                    self.sock.sendall(data)
                else:
                    self.sock.sendto(data, (self.ip, self.port))
                self.logger.debug(f'{self} 发送数据: {data}')
            except OSError as e:
                if e.errno == 10057:
                    self.logger.debug(f'{self} 发送失败连接未建立')
                else:
                    self.logger.error(f'{self} 发送失败: \n{e}')

    def recv(self) -> bytes | None:
        if not self.__connected:
            self.logger.debug(f'{self} 未连接, 无法接收数据')
            return None

        try:
            data, _ = self.sock.recvfrom(1024)
            self.logger.debug(f'{self} 接收数据: {data}')
            return data
        except TimeoutError:
            self.logger.debug(f'{self} 接收超时')
        except OSError as e:
            if e.errno == 10057:
                self.logger.debug(f'{self} 接收失败连接未建立')
            else:
                self.logger.error(f'{self} 接收失败: \n{e}')
        return None

    def close(self) -> bool:
        if self.__connected:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                self.__connected = False
                self.logger.debug(f'{self} 已关闭')
            except Exception as e:
                self.logger.error(f'{self} 关闭失败: \n{e}')
        return not self.__connected
