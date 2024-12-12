#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import ipaddress

from ..sock.client_socket import ClientSocket


class NetworkUtil(object):

    @staticmethod
    def is_ip(ip_addr: str) -> bool:
        """判断是否为合法的 IP 地址

        Args:
            ip_addr (str): IP 地址

        Returns:
            bool: 是否为合法的 IP 地址
        """
        try:
            ipaddress.ip_address(ip_addr)
            return True
        except ValueError:
            return False

    @staticmethod
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

    @staticmethod
    def classify_ip(ip_addr: str) -> str:
        """根据 IP 地址的第一个字节判断 IP 地址的分类

        Args:
            ip_addr (str): IP 地址

        Raises:
            ValueError: 无效的 IP 地址

        Returns:
            str: IP 地址分类 {'A', 'B', 'C', 'D', 'E', None}
        """
        if not NetworkUtil.is_ip(ip_addr):
            raise ValueError('无效的 IP 地址')
        first_octet = int(ip_addr.split('.')[0])

        if 1 <= first_octet <= 126:
            return 'A'
        elif 128 <= first_octet <= 191:
            return 'B'
        elif 192 <= first_octet <= 223:
            return 'C'
        elif 224 <= first_octet <= 239:
            return 'D'
        elif 240 <= first_octet <= 255:
            return 'E'
        else:
            raise ValueError('无效的 IP 地址')

    @staticmethod
    def get_hostname() -> str:
        """返回一个字符串，包含当前正在运行 Python 解释器的机器的主机名。

        Returns:
            str: 主机名
        """
        return socket.gethostname()

    @staticmethod
    def get_host_by_name(hostname: str) -> str:
        """将主机名转换为 IPv4 地址格式。IPv4 地址以字符串格式返回，如 '100.50.200.5'。
        如果主机名本身是 IPv4 地址，则原样返回。

        Args:
            hostname (str): 主机名

        Returns:
            str: IP 地址
        """
        return socket.gethostbyname(hostname)

    @staticmethod
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

    @staticmethod
    def get_local_ip(nth: int = 0) -> str:
        """获取本地 IP 地址

        Args:
            nth (int, optional): 多网卡时获取第 nth 个网卡的 IP 地址. 默认为 0.

        Raises:
            ValueError: 无效的网卡序号

        Returns:
            _type_: 本地 IP 地址
        """
        hostname = socket.gethostname()

        if nth == 0:
            ip = socket.gethostbyname(hostname)
        else:
            ips = socket.gethostbyname_ex(hostname)[2]
            if nth >= len(ips):
                raise ValueError(f'无效的网卡序号: {nth}')
            ip = ips[nth]
        return ip

    @staticmethod
    def get_local_ips() -> list[str]:
        """获取本地 IP 地址列表

        Returns:
            _type_: 本地 IP 地址列表
        """
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2]
        return ips

    @staticmethod
    def get_broadcast_address(ip_network: str) -> str:
        """返回对应 IP 地址的广播地址

        Example:
            >>> NetworkUtil.get_broadcast_address('192.168.1.100/24')
            '192.168.1.255'

            >>> NetworkUtil.get_broadcast_address('192.168.1.100')
            '192.168.1.255'

        Args:
            ip_addr (str): IP 地址

        Returns:
            str: 广播地址
        """
        if not '/' in ip_network:
            if classify := NetworkUtil.classify_ip(ip_network):
                netmask = {'A': '/8', 'B': '/16', 'C': '/24', 'D': '/24', 'E': '/32'}[classify]
                ip_network = f'{ip_network}{netmask}'

        ip_network = ipaddress.ip_network(ip_network, strict=False)
        return str(ip_network.broadcast_address)

    @staticmethod
    def send_WOL(mac_hex: str, *, port: int = 9527) -> None:
        """向本机的所有网卡发送网络唤醒包

        Args:
            mac_hex (str): mac 地址
            port (int, optional): 发送广播的端口. 默认为 9527.
        """
        mac_hex      = mac_hex.replace(':', '').replace('-', '')
        magic_packet = bytes.fromhex('ff' * 6 + mac_hex * 16)

        for local_ip in NetworkUtil.get_local_ips():
            broadcast_host = NetworkUtil.get_broadcast_address(local_ip)

            client_socket = ClientSocket(protocol="UDP", server=(broadcast_host, port), bind=(local_ip, 0))
            client_socket.send(magic_packet)
            client_socket.close()
