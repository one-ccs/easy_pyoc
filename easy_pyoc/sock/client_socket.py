#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket


class ClientSocket:
    def __init__(self, *, protocol: str, ip: str, port: int, recv_timeout: float = 1.5):
        """客户端套接字

        发送 TCP/UDP/MULTICAST 数据并接收响应。

        Args:
            protocol (str): 协议
            ip (str): ip 地址
            port (int): 端口号
            recv_timeout (float, optional): 接收超时时间. Defaults to 1.5.

        Raises:
            ValueError: 无效的端口号, 应为 [1-65535]
            ValueError: 无效的协议类型, 应为 [TCP, UDP, MULTICAST]
        """
        if port < 1 or port > 65535:
            raise ValueError(f'ServerSocket 无效的端口号 "{port}"')
        if protocol not in ['TCP', 'UDP', 'MULTICAST']:
            raise ValueError(f'ServerSocket 无效的协议类型 "{protocol}"')

        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.recv_timeout = recv_timeout
        self.sock: socket.socket | None = None
        self.__connected = False

    def __str__(self) -> str:
        return f"ClientSocket({self.ip}:{self.port})"

    def __del__(self):
        self.close()

    def connect(self) -> bool:
        if not self.__connected:
            try:
                match self.protocol:
                    case 'TCP':
                        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.sock.connect((self.ip, self.port))
                    case 'UDP':
                        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        if self.ip.endswith('.255'): # 设置 SO_BROADCAST 为 1, 允许发送广播数据包
                            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    case 'MULTICAST':
                        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
                        self.sock.bind(('', self.port))
                        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.ip) + socket.inet_aton('0.0.0.0'))
                self.sock.settimeout(self.recv_timeout)
                self.__connected = True
            except ConnectionRefusedError:
                print(f'{self} 无法连接: {self.ip}:{self.port}')
            except Exception as e:
                print(f'{self} 创建失败: {e}')
        return self.__connected

    def send(self, data: bytes) -> None:
        try:
            print(f'{self} 发送数据: {data}')

            if self.protocol == 'TCP':
                self.sock.sendall(data)
            else:
                self.sock.sendto(data, (self.ip, self.port))
        except OSError as e:
            if e.errno == 10057:
                print(f'{self} 发送失败连接未建立')
            else:
                print(f'{self} 发送失败: {e}')

    def recv(self) -> bytes | None:
        try:
            data, _ = self.sock.recvfrom(1024)
            print(f'{self} 收到数据: {data}')
            return data
        except TimeoutError:
            return None
        except OSError as e:
            if e.errno == 10057:
                print(f'{self} 接收失败连接未建立')
            else:
                print(f'{self} 接收失败: {e}')

    def close(self) -> bool:
        if self.__connected:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                self.__connected = False
            except Exception as e:
                print(f'{self} 关闭失败: {e}')
        return not self.__connected
