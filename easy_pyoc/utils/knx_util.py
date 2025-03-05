#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from select import select
from dataclasses import dataclass
import socket

from .string_util import StringUtil
from .network_util import NetworkUtil


class KNXUtil(object):
    """KNXnet/IP 工具类"""

    KNX_PORT      = 3671
    """KNXnet/IP 端口号"""
    KNX_MULTICAST = ('224.0.23.12', KNX_PORT)
    """KNXnet/IP 多播地址"""
    KNX_MX        = 2
    """KNXnet/IP 多播 TTL"""
    H_S_REQ_EXT   = b'\x02\x0b'
    """KNXnet/IP 发现请求扩展头"""
    H_S_REQ       = b'\x02\x01'
    """KNXnet/IP 发现请求头"""
    H_S_RES       = b'\x02\x02'
    """KNXnet/IP 发现响应头"""
    DIBS          = b'\x08\x04\x01\x02\x08\x06\x07\x00'
    """KNXnet/IP 发现请求 DIBS"""

    @dataclass
    class ControlDevice(object):
        """KNX 网关设备信息

        Attributes:
            host (str): 网关设备 IP 地址
            port (int): 网关设备端口号
            inad (tuple[int, int, int]): 网关设备地址
            sn (str): 网关设备序列号
            mac (str): 网关设备 MAC 地址
            name (str): 网关设备名称
        """
        host: str
        port: int
        inad: tuple[int, int, int]
        sn: str
        mac: str
        name: str

    @staticmethod
    def discover(timeout: int = 5) -> list[ControlDevice]:
        """发现 KNX 网关设备

        Args:
            timeout (int, optional): 发现超时时间. 默认为 5.

        Returns:
            list[KNXUtil.ControlDevice]: 网关设备列表
        """
        devices = {}
        for res in _scan(timeout):
            if res in devices:
                continue

            mac = res[32: 38].hex()
            device = {
                'host': StringUtil.hex_to_ip(res[8: 12].hex()),
                'port': StringUtil.str_to_int(res[12: 14].hex(), 16),
                'inad': (res[18] & 0x0f, res[18] >> 4 & 0x0f, res[19]),
                'sn':   f'{res[22: 24].hex()}:{res[24: 28].hex()}',
                'mac':  ':'.join([mac[i:i+2] for i in range(0, len(mac), 2)]),
                'name': res[38:12+res[14]].decode(),
            }
            devices[mac] = KNXUtil.ControlDevice(**device)

        return list(devices.values())


def _make_header(identifier: bytes, length: int):
    return b'\x06\x10' + identifier + (length).to_bytes(2, 'big')


def _make_hpai(ip: str, port: int) -> bytes:
    return b'\x08\x01' + bytes.fromhex(
        StringUtil.ip_to_hex(ip) +
        StringUtil.int_to_str(port, 16, 4)
    )


def _scan(timeout: int = 5):
    stop_wait = datetime.now() + timedelta(seconds=timeout)
    h_s_req_ext = _make_header(KNXUtil.H_S_REQ_EXT, 22)
    h_s_req     = _make_header(KNXUtil.H_S_REQ, 14)

    sockets: list[socket.socket] = []
    for ip in NetworkUtil.get_local_ips():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, KNXUtil.KNX_MX)
            sock.bind((ip, 0))
            sockets.append(sock)
        except socket.error:
            pass

    for sock in sockets:
        hpai_de = _make_hpai(*sock.getsockname())
        knx_s_reqs = [h_s_req_ext + hpai_de + KNXUtil.DIBS, h_s_req + hpai_de]
        try:
            for req in knx_s_reqs:
                sock.sendto(req, KNXUtil.KNX_MULTICAST)
            sock.setblocking(False)
        except socket.error:
            sockets.remove(sock)
            sock.close()

    responses = []
    try:
        while sockets:
            time_diff = stop_wait - datetime.now()
            seconds_left = time_diff.total_seconds()
            if seconds_left <= 0:
                break

            ready = select(sockets, [], [], seconds_left)[0]

            for sock in ready:
                try:
                    data, addr = sock.recvfrom(1024)
                except socket.error:
                    sockets.remove(sock)
                    sock.close()
                    continue

                if data.startswith(b'\x06\x10\x02\x02'):
                    responses.append(data)
    finally:
        for sock in sockets:
            sock.close()

    return set(responses)
