#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import threading
import multiprocessing
from typing import Callable

from ..logger import Logger


class ServerSocket():
    def __init__(self, *, protocol: str, bind: tuple[str, int], group: str | None = None, on_recv: Callable):
        """服务端套接字

        在新线程中创建 TCP/UDP/MULTICAST 协议的服务端套接字，接收客户端的
        连接请求或数据，并调用 on_recv 回调函数处理数据。

        TCP 断开连接的情况：

        - TCP 正常断开
            + 客户端主动断开连接
            + 通信期间正常交换数据 (若服务端返回了响应, 则客户端应该接收响应)
        - TCP 连接已重置
            + 客户端主动断开连接
            + 服务端返回了响应，但客户端未接收
        - TCP 连接已终止
            + 未通信完毕就已经断开了连接

        Args:
            protocol (str): 协议
            bind (tuple[str, int]): 绑定的地址, 注: 当多网卡, 且 ip 为 "0.0.0.0" 时, 有可能接收不到数据.
            group (tuple[str, int] | None, optional): 组播地址, 仅在协议类型为 "MULTICAST" 时有效. 默认为 None.
            on_recv (Callable, optional): 接收到数据时的回调函数, 参数为 (data: bytes, client_name: str, send_back: Callable). 默认为 None.

        Raises:
            ValueError: 无效的协议类型, 应为 [TCP, UDP, MULTICAST]
            ValueError: 组播协议必须指定组播地址
            ValueError: 协议类型为非 "MULTICAST" 时请勿设置 group 参数
            ValueError: 绑定地址 (bind[0]) 不能为空
            ValueError: 无效的端口号, 应为 [1-65535]
        Examples:
        """
        self.__active = False

        if protocol not in ['TCP', 'UDP', 'MULTICAST']:
            raise ValueError(f'ServerSocket 无效的协议类型 "{protocol}"')
        if protocol == 'MULTICAST' and not group:
            raise ValueError(f'ServerSocket 组播协议必须指定组播地址')
        if protocol != 'MULTICAST' and group:
            raise ValueError(f'ServerSocket 协议类型为 "{protocol}" 时请勿设置 group 参数')
        if not bind[0]:
            raise ValueError(f'ServerSocket 绑定地址不能为空')
        if bind[1] < 1 or bind[1] > 65535:
            raise ValueError(f'ServerSocket 无效的端口号 "{bind[1]}"')

        self.logger = Logger()
        self.protocol = protocol
        self.bind = bind
        self.group = group
        self.on_recv = on_recv
        self.sock: socket.socket | None = None
        self.tcp_sub_socks: list[socket.socket] = []
        self.thread: threading.Thread | None = None

    def __str__(self) -> str:
        if self.protocol == 'MULTICAST':
            return f'ServerSocket({self.protocol}, bind {self.bind[0]}:{self.bind[1]}, group {self.group})'
        return f'ServerSocket({self.protocol}, bind {self.bind[0]}:{self.bind[1]})'

    def __del__(self) -> None:
        if self.is_active():
            self.close()

    def __create_socket(self) -> None:
        match self.protocol:
            case 'TCP':
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.bind(self.bind)
                self.sock.listen(10)
            case 'UDP':
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind(self.bind)
            case 'MULTICAST':
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind(self.bind)
                self.sock.setsockopt(
                    socket.IPPROTO_IP,
                    socket.IP_ADD_MEMBERSHIP,
                    socket.inet_aton(self.group) + socket.inet_aton(self.bind[0]),
                )

    def __send_back(self, client_addr: tuple[str, int], client_sock: socket.socket | None = None) -> Callable:
        def send_back(data: bytes):
            self.logger.debug(f'{self} 向 {client_addr} 返回数据: {data}')

            if self.protocol == 'TCP':
                return client_sock.sendto(data, client_addr)
            return self.sock.sendto(data, client_addr)

        return send_back

    def __tcp_sub_thread(self, client_sock: socket.socket, client_addr: tuple[str, int]) -> None:
        while self.is_active():
            try:
                if not (data := client_sock.recv(1024)):
                    self.logger.debug(f'{self} TCP 子线程 {client_addr} 正常断开')
                    break

                self.logger.debug(f'{self} TCP 子线程 {client_addr} 接收到数据: {data}')
                self.on_recv and self.on_recv(
                    data=data,
                    client_addr=client_addr,
                    send_back=self.__send_back(client_addr, client_sock),
                )
            except ConnectionResetError:
                self.logger.debug(f'{self} TCP 子线程 {client_addr} 连接已重置')
                break
            except ConnectionAbortedError:
                self.logger.debug(f'{self} TCP 子线程 {client_addr} 连接已终止')
                break
            except Exception as e:
                if self.is_active():
                    self.logger.error(f'{self} TCP 子线程 {client_addr} 异常: \n{e}')
                break
        if self.is_active(): # 断开或异常断开
            self.tcp_sub_socks.remove(client_sock)
            client_sock.close()

    def __main_thread(self) -> None:
        self.__active = True

        while self.is_active():
            try:
                if self.protocol == 'TCP':
                        client_sock, client_addr = self.sock.accept()
                        self.logger.debug(f'{self} 与 {client_addr} 建立 TCP 连接')
                        self.tcp_sub_socks.append(client_sock)
                        threading.Thread(target=self.__tcp_sub_thread, args=(client_sock, client_addr), daemon=True).start()
                else:
                    data, client_addr = self.sock.recvfrom(1024)

                    self.logger.debug(f'{self} 收到 {client_addr} 的数据: {data}')
                    self.on_recv and self.on_recv(
                        data=data,
                        client_addr=client_addr,
                        send_back=self.__send_back(client_addr),
                    )
            except Exception as e:
                if self.is_active():
                    self.logger.error(f'{self} 主线程异常 : \n{e}')
                    break

    def send(self, data: bytes, client_addr: tuple[str, int]) -> int:
        """向指定客户端发送数据

        Args:
            data (bytes): 要发送的数据
            client_addr (tuple[str, int]): 客户端地址

        Returns:
            int: 实际发送的字节数, 为 -1 表示 socket 未建立或已关闭
        """
        if not self.is_active():
            return -1

        if self.protocol == 'TCP':
            for client_sock in self.tcp_sub_socks:
                if client_sock.getpeername() == client_addr:
                    return client_sock.sendall(data)
            return 0
        return self.sock.sendto(data, client_addr)

    def start(self, is_process: bool = False) -> bool:
        """启动服务端

        将在新线程中运行，直到调用 close() 关闭，TCP 协议下会创建子线程处理 TCP 连接

        Args:
            is_process (bool, optional): 是否以子进程运行. 默认为 False.

        Returns:
            bool: 是否启动成功
        """
        try:
            self.__create_socket()
        except Exception as e:
            self.logger.error(f'{self} 创建失败: \n{e}')
            return False

        if is_process:
            self.thread = multiprocessing.Process(target=self.__main_thread, daemon=True)
        else:
            self.thread = threading.Thread(target=self.__main_thread, daemon=True)
        self.thread.start()
        return True

    def close(self) -> bool:
        """关闭服务端

        Returns:
            bool: 是否关闭成功
        """
        try:
            self.__active = False
            if self.protocol == 'TCP':
                for client_sock in self.tcp_sub_socks:
                    client_sock.shutdown(socket.SHUT_RDWR)
                    client_sock.close()
                self.tcp_sub_socks.clear()
            try:
                # windows 平台 TCP 无需 shutdown (此时 shutdown 会导致 10057 错误)
                # linux 平台非 TCP shutdown 会报 107 错误
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError as e:
                if e.errno != 107 and e.errno != 10057:
                    raise e
            self.sock.close()
            if isinstance(self.thread, multiprocessing.Process):
                self.thread.terminate()
            else:
                self.thread.join()
        except Exception as e:
            self.logger.error(f'{self} 关闭失败: \n{e}')
            return False
        return True

    def is_active(self) -> bool:
        """返回服务端是否处于活动状态

        Returns:
            bool: 是否处于活动状态
        """
        return self.__active
