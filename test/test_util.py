#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from easy_pyoc import StringUtil
from easy_pyoc import ObjectUtil



def test_string_util_its2():
    assert StringUtil.int_to_str(123, 2) == '1111011'
    assert StringUtil.int_to_str(123, 2, length=5) == '1111011'
    assert StringUtil.int_to_str(123, 2, length=8) == '01111011'
    assert StringUtil.int_to_str(0, 2) == '0'
    assert StringUtil.int_to_str(0, 2, length=5) == '00000'
    assert StringUtil.int_to_str(-123, 2) == '-1111011'
    assert StringUtil.int_to_str(123456789, 2) == '111010110111100110100010101'


def test_string_util_its8():
    assert StringUtil.int_to_str(123, 8) == '173'
    assert StringUtil.int_to_str(123, 8, length=5) == '00173'
    assert StringUtil.int_to_str(0, 8) == '0'
    assert StringUtil.int_to_str(0, 8, length=5) == '00000'
    assert StringUtil.int_to_str(-123, 8) == '-173'
    assert StringUtil.int_to_str(123456789, 8) == '726746425'


def test_string_util_its10():
    assert StringUtil.int_to_str(123) == '123'
    assert StringUtil.int_to_str(123, length=5) == '00123'
    assert StringUtil.int_to_str(0) == '0'
    assert StringUtil.int_to_str(0, length=5) == '00000'
    assert StringUtil.int_to_str(-123) == '-123'
    assert StringUtil.int_to_str(123456789) == '123456789'


def test_string_util_its16():
    assert StringUtil.int_to_str(123, base=16) == '7b'
    assert StringUtil.int_to_str(123, base=16, length=5) == '0007b'
    assert StringUtil.int_to_str(0, base=16) == '0'
    assert StringUtil.int_to_str(0, base=16, length=5) == '00000'
    assert StringUtil.int_to_str(123456789, base=16) == '75bcd15'


def test_string_util_sti2():
    assert StringUtil.str_to_int('1111011', 2) == 123
    assert StringUtil.str_to_int('01111011', 2) == 123
    assert StringUtil.str_to_int('-1111011', 2) == -123


def test_string_util_fh():
    assert StringUtil.format_hex('7b') == '7b'
    assert StringUtil.format_hex('7bcd15') == '7b cd 15'


def test_string_util_ith():
    assert StringUtil.ip_to_hex('192.168.1.1') == 'c0a80101'
    assert StringUtil.ip_to_hex('255.255.255.255') == 'ffffffff'
    assert StringUtil.ip_to_hex('0.0.0.0') == '00000000'


def test_string_util_hti():
    assert StringUtil.hex_to_ip('c0a80101') == '192.168.1.1'
    assert StringUtil.hex_to_ip('ffffffff') == '255.255.255.255'
    assert StringUtil.hex_to_ip('00000000') == '0.0.0.0'


def test_string_util_mth():
    assert StringUtil.mac_to_hex('00:11:22:33:44:55') == '001122334455'
    assert StringUtil.mac_to_hex('ff:ff:ff:ff:ff:ff') == 'ffffffffffff'
    assert StringUtil.mac_to_hex('00:00:00:00:00:00') == '000000000000'


def test_string_util_htm():
    assert StringUtil.hex_to_mac('001122334455') == '00:11:22:33:44:55'
    assert StringUtil.hex_to_mac('ffffffffffff') == 'ff:ff:ff:ff:ff:ff'
    assert StringUtil.hex_to_mac('000000000000') == '00:00:00:00:00:00'


def test_object_util_config_class():
    with pytest.raises((ImportError, FileNotFoundError), match='(无法导入|文件.+不存在)'):
        ObjectUtil.ConfigClass('test.toml', decoder='toml')

    with pytest.raises(FileNotFoundError, match='文件 .+ 不存在'):
        ObjectUtil.ConfigClass('test.json', decoder='json')

    with pytest.raises(ValueError, match='不支持的解码器类型 .+'):
        ObjectUtil.ConfigClass('test.txt', decoder='txt')

    assert ObjectUtil.ConfigClass({'a': 1, 'b': [2, 3]}).a == 1
    assert ObjectUtil.ConfigClass({'a': 1, 'b': [2, {'c': 3}, [4, {'d': 5}]]}).b[0] == 2
    assert ObjectUtil.ConfigClass({'a': 1, 'b': [2, {'c': 3}, [4, {'d': 5}]]}).b[1].c == 3
    assert ObjectUtil.ConfigClass({'a': 1, 'b': [2, {'c': 3}, [4, {'d': 5}]]}).b[2][0] == 4
    assert ObjectUtil.ConfigClass({'a': 1, 'b': [2, {'c': 3}, [4, {'d': 5}]]}).b[2][1].d == 5
    assert ObjectUtil.ConfigClass({'a': ['*']}).a == ['*']

    assert ObjectUtil.ConfigClass({'a': 1, 'b': True}, default_map={'b': False}).b is True
    assert ObjectUtil.ConfigClass({'a': 1, 'b': None}, default_map={'c': 123}).c == 123

    assert ObjectUtil.ConfigClass({'a': 1, 'b': 2}, hook=lambda k, v, _: (v * 2)).a == 2

    _ = ObjectUtil.ConfigClass({'a': 1, 'b': 2}, hook=lambda k, v, _: (v if k == 'a' else v * 2))
    assert _.a == 1
    assert _.b == 4

    _ = ObjectUtil.ConfigClass({'a': 1, 'b': 2}, hook=lambda k, v, _: (v if k == 'a' else ...))
    assert _.a == 1
    with pytest.raises(AttributeError):
        _.b

    def hook(k, v, _):
        if k == 'a':
            _.a1 = 'a1'
        return v
    _ = ObjectUtil.ConfigClass({'a': 1, 'b': 2}, hook=hook)
    assert _.a == 1
    assert _.a1 == 'a1'


def test_toml_util():
    import sys

    from easy_pyoc import TOMLUtil

    if sys.version_info < (3, 11):
        with pytest.raises(AttributeError):
            TOMLUtil.loads('')

        with pytest.raises(ImportError, match='没有成功导入'):
            _ = TOMLUtil()
    else:
        assert TOMLUtil.loads('') == {}
