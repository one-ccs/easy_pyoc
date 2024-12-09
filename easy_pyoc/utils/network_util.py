#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket

from ..sock.client_socket import ClientSocket


class NetworkUtil(object):

    @staticmethod
    def send_WOL(mac_hex: str, bind: tuple[str, int] | None = None, ip: str | None = None, port: int = 1234) -> None:
        """发送网络唤醒包

        Args:
            mac_hex (str): mac 地址, 12 位十六进制字符串
            ip (str, optional): 广播地址, 为 None 时自动设置. 默认为 None.
            port (int, optional): 目标端口. 默认为 1234.
            bind (tuple[str, int], optional): 本地绑定地址. 默认为 None.
        """
        localhost = socket.gethostbyname(socket.gethostname())
        broadcast_host = '.'.join(localhost.split('.')[:-1] + ['255']) if ip is None else ip

        magic_packet = bytes.fromhex('ff' * 6 + mac_hex * 16)

        client_socket = ClientSocket(protocol="UDP", ip=broadcast_host, port=port, bind=bind)
        client_socket.send(magic_packet)
        client_socket.close()
