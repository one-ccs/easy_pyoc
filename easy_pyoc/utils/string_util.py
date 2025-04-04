#!/usr/bin/env python
# -*- coding: utf-8 -*-
from re import compile
from string import ascii_letters, digits, hexdigits


class StringUtil(object):

    base_table = digits + ascii_letters
    """基础字符表"""

    @staticmethod
    def camel_to_snake(camel_str: str) -> str:
        """将驼峰形式命名的字符串转换为下划线形式"""
        pattern = compile(r'(?<!^)(?=[A-Z])')
        return pattern.sub('_', camel_str).lower()

    @staticmethod
    def snake_to_camel(snake_str: str) -> str:
        """将下划线形式命名的字符串转换为驼峰形式"""
        if snake_str[0] == '_':
            components = snake_str.split('_')
            return '_' + ''.join(v.title() if i > 0 else v for i, v in enumerate(components[1:]))
        if snake_str[0] == '__':
            components = snake_str.split('_')
            return '__' + ''.join(v.title() if i > 0 else v for i, v in enumerate(components[1:]))
        components = snake_str.split('_')
        return components[0] + ''.join(v.title() for v in components[1:])

    @staticmethod
    def ishex(s: str) -> bool:
        """判断字符串是否为 16 进制字符串。"""
        return all(c in hexdigits for c in s) and len(s) % 2 == 0

    @staticmethod
    def format_hex(hex_str: str, reverse: bool = False) -> str:
        """格式化 16 进制字符串，每 8 位插入一个空格。

        Args:
            hex_str (str): 16 进制字符串.
            reverse (bool, optional): 是否反转字节顺序。 默认为 False.

        Returns:
            str: 格式化后的 16 进制字符串.
        """
        groups = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]

        if reverse:
            groups.reverse()

        return ' '.join(groups)

    @staticmethod
    def int_to_str(num: int, base: int = 10, length: int = 1) -> str:
        """将整数转换为指定进制的字符串，并在左侧填充 0 到指定长度。

        Args:
            num (int): 整数.
            base (int, optional): 进制. 默认为 10.
            length (int, optional): 填充长度. 默认为 1.

        Returns:
            str: 转换后的字符串.
        """
        result = ''

        if num == 0:
            result = '0' * length
        elif num > 0:
            while num > 0:
                result = StringUtil.base_table[num % base] + result
                num //= base
        else:
            result = '-'
            result += StringUtil.int_to_str(abs(num), base, length - 1)

        if length > 0:
            result = '0' * (length - len(result)) + result

        return result

    @staticmethod
    def str_to_int(string: str, base: int = 10) -> int:
        """将字符串转换为整数，并以指定进制进行计算。

        Args:
            string (str): 字符串.
            base (int, optional): 进制. 默认为 10.

        Returns:
            int: 转换后的整数.
        """
        return int(string, base)

    @staticmethod
    def ip_to_hex(ip_str: str) -> str:
        """将 IP 地址转换为 16 进制字符串。

        Args:
            ip_str (str): IP 地址.

        Returns:
            str: 转换后的 16 进制字符串.
        """
        split_ip = ip_str.split('.')

        if not len(split_ip) == 4 or not all(i.isdigit() and 0 <= int(i) <= 255 for i in split_ip):
            raise ValueError(f'ip_str ({ip_str}) 格式错误')

        return ''.join([StringUtil.int_to_str(int(i), 16, 2) for i in split_ip])

    @staticmethod
    def hex_to_ip(hex_str: str) -> str:
        """将 16 进制字符串转换为 IP 地址。

        Args:
            hex_str (str): 16 进制字符串.

        Returns:
            str: 转换后的 IP 地址.
        """
        if len(hex_str)!= 8:
            raise ValueError(f'hex_str ({hex_str}) 长度必须为 8')
        if not StringUtil.ishex(hex_str):
            raise ValueError(f'hex_str ({hex_str}) 格式错误')

        return '.'.join([str(int(hex_str[i:i+2], 16)) for i in range(0, 8, 2)])
