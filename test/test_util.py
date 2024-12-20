#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest, re

from easy_pyoc import NetworkUtil
from easy_pyoc import StringUtil
from easy_pyoc import ThreadUtil
from easy_pyoc import Config


def test_network_util():
    assert NetworkUtil.is_ip('192.168.1.1')
    assert NetworkUtil.is_ip('255.255.255.255')
    assert NetworkUtil.is_ip('0.0.0.0')
    assert not NetworkUtil.is_ip('192.168.1')
    assert not NetworkUtil.is_ip('192.168.1.1.1')

    assert NetworkUtil.is_host('www.baidu.com')
    assert NetworkUtil.is_host('192.168.1.1')
    assert not NetworkUtil.is_host('www.baidu')

    assert NetworkUtil.classify_ip('10.0.0.1')     == 'A'
    assert NetworkUtil.classify_ip('172.16.0.1')   == 'B'
    assert NetworkUtil.classify_ip('192.168.1.1')  == 'C'
    assert NetworkUtil.classify_ip('224.168.3.11') == 'D'
    assert NetworkUtil.classify_ip('240.168.3.11') == 'E'
    with pytest.raises(ValueError, match='无效的 IP 地址'):
        NetworkUtil.classify_ip('192.168.1')

    assert NetworkUtil.get_local_ip()
    with pytest.raises(ValueError, match='无效的网卡序号'):
        NetworkUtil.get_local_ip(99)

    assert NetworkUtil.get_broadcast_address('192.168.1.0/24') == '192.168.1.255'
    assert NetworkUtil.get_broadcast_address('192.168.1.1/32') == '192.168.1.1'
    with pytest.raises(ValueError):
        NetworkUtil.get_broadcast_address('192.168.1')
    with pytest.raises(ValueError):
        NetworkUtil.get_broadcast_address('192.168.1.0/33')


def test_string_util():
    assert StringUtil.int_to_str(123, 2) == '1111011'
    assert StringUtil.int_to_str(123, 2, length=5) == '1111011'
    assert StringUtil.int_to_str(123, 2, length=8) == '01111011'
    assert StringUtil.int_to_str(0, 2) == '0'
    assert StringUtil.int_to_str(0, 2, length=5) == '00000'
    assert StringUtil.int_to_str(-123, 2) == '-1111011'
    assert StringUtil.int_to_str(123456789, 2) == '111010110111100110100010101'

    assert StringUtil.int_to_str(123, 8) == '173'
    assert StringUtil.int_to_str(123, 8, length=5) == '00173'
    assert StringUtil.int_to_str(0, 8) == '0'
    assert StringUtil.int_to_str(0, 8, length=5) == '00000'
    assert StringUtil.int_to_str(-123, 8) == '-173'
    assert StringUtil.int_to_str(123456789, 8) == '726746425'

    assert StringUtil.int_to_str(123) == '123'
    assert StringUtil.int_to_str(123, length=5) == '00123'
    assert StringUtil.int_to_str(0) == '0'
    assert StringUtil.int_to_str(0, length=5) == '00000'
    assert StringUtil.int_to_str(-123) == '-123'
    assert StringUtil.int_to_str(123456789) == '123456789'

    assert StringUtil.int_to_str(123, base=16) == '7b'
    assert StringUtil.int_to_str(123, base=16, length=5) == '0007b'
    assert StringUtil.int_to_str(0, base=16) == '0'
    assert StringUtil.int_to_str(0, base=16, length=5) == '00000'
    assert StringUtil.int_to_str(123456789, base=16) == '75bcd15'
    assert StringUtil.int_to_str(123456789, base=10) == '123456789'
    assert StringUtil.int_to_str(123456789, base=16, length=8) == '075bcd15'

    assert StringUtil.str_to_int('1111011', 2) == 123
    assert StringUtil.str_to_int('01111011', 2) == 123
    assert StringUtil.str_to_int('-1111011', 2) == -123

    assert StringUtil.format_hex('7b') == '7b'
    assert StringUtil.format_hex('7bcd15') == '7b cd 15'

    assert StringUtil.ip_to_hex('192.168.1.1') == 'c0a80101'
    assert StringUtil.ip_to_hex('255.255.255.255') == 'ffffffff'
    assert StringUtil.ip_to_hex('0.0.0.0') == '00000000'

    assert StringUtil.hex_to_ip('c0a80101') == '192.168.1.1'
    assert StringUtil.hex_to_ip('ffffffff') == '255.255.255.255'
    assert StringUtil.hex_to_ip('00000000') == '0.0.0.0'


def test_thread_util():
    from time import sleep

    n = 0
    def task(stop_flag):
        nonlocal n

        while not stop_flag.is_set():
            print('running...')
            n += 1
            sleep(1)

    task_id = ThreadUtil.execute_task(task)
    sleep(3)
    ThreadUtil.chancel_task(task_id)
    assert n == 3


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


def test_config_class():
    with pytest.raises((ImportError, FileNotFoundError), match='(无法导入|文件.+不存在)'):
        Config('test.toml', decoder='toml')

    with pytest.raises(FileNotFoundError, match='文件 .+ 不存在'):
        Config('test.json', decoder='json')

    with pytest.raises(ValueError, match='不支持的解码器类型 .+'):
        Config('test.txt', decoder='txt')

    with pytest.raises(ValueError, match='不能作为根配置'):
        Config([])

    with pytest.raises(ValueError, match='不能作为根配置'):
        Config(1)

    def hook(o: Config, v):
        if isinstance(v, int) and o.path != 'Config.f':
            return v * 2
        if o.path == 'Config.b[1][1].a1':
            return 'aaa'
        if o.path == 'Config.f':
            return 666
        return v

    _ = Config(
        {'a': 333, 'b': [1, [2, {'a1': 'a1'}]], 'c': {'c1': 'c1', 'c2': ['c21', 'c22']}},
        default_map={'a': 123, 'f': 456},
    ).set_config('d', 1).set_config('e', 2)
    # 根测试
    assert _.path == 'Config'
    assert _.name == 'Config'
    assert _.value == _
    assert _.original_value == {'a': 333, 'b': [1, [2, {'a1': 'a1'}]], 'c': {'c1': 'c1', 'c2': ['c21', 'c22']}, 'f': 456, 'd': 1, 'e': 2}
    # 简单子测试
    assert _.a.path == 'Config.a'
    assert _.a.name == 'a'
    assert _.a.value == 333
    assert _.a.original_value == 333
    # 列表测试
    assert _.b.path == 'Config.b'
    assert _.b.name == 'b'
    assert _.b.value == [_.b[0], _.b[1]]
    assert _.b.original_value == [1, [2, {'a1': 'a1'}]]
    # 列表子测试
    assert _.b[0].path == 'Config.b[0]'
    assert _.b[0].name == 'b[0]'
    assert _.b[0].value == 1
    assert _.b[0].original_value == 1
    # 字典测试
    assert _.c.path == 'Config.c'
    assert _.c.name == 'c'
    assert _.c.value == _.c
    assert _.c.original_value
    # 字符串取值测试
    assert _['c'].path == 'Config.c'
    assert _['c'].name == 'c'
    assert _['c'].value == _.c
    assert _['c'].original_value
    # 字典子测试
    assert _.c.c1.path == 'Config.c.c1'
    assert _.c.c1.name == 'c1'
    assert _.c.c1.value == 'c1'
    assert _.c.c1.original_value == 'c1'
    # 嵌套列表测试
    assert _.b[1][1].path == 'Config.b[1][1]'
    assert _.b[1][1].name == 'b[1][1]'
    assert _.b[1][1].value == _.b[1][1]
    assert _.b[1][1].original_value == {'a1': 'a1'}
    # 嵌套字典测试
    assert _.b[1][1].a1.path == 'Config.b[1][1].a1'
    assert _.b[1][1].a1.name == 'a1'
    assert _.b[1][1].a1.value == 'a1'
    assert _.b[1][1].a1.original_value == 'a1'
    # 自定义属性测试
    assert _.d.path == 'Config.d'
    assert _.d.name == 'd'
    assert _.d.value == 1
    assert _.d.original_value == 1
    assert _.e.path == 'Config.e'
    assert _.e.name == 'e'
    assert _.e.value == 2
    assert _.e.original_value == 2
    # 默认值测试
    assert _.a.value == 333
    assert _.f.value == 456
    # 递归取值测试
    assert _.get_config('Config.a').value == 333
    assert _.get_config('Config.b[0]').value == 1
    assert _.get_config('Config.b[1][0]').value == 2
    assert _.get_config('Config.b[1][1].a1').value == 'a1'
    assert _.get_config('Config.c.c1').value == 'c1'
    # hook 测试
    _ = Config(
        {'a': 333, 'b': [1, [2, {'a1': 'a1'}]], 'c': {'c1': 'c1', 'c2': ['c21', 'c22']}},
        default_map={'a': 123, 'f': 456},
        hook=hook,
    ).set_config('d', 1).set_config('e', 2)
    assert _.a.value == 666
    assert _.a.original_value == 333
    assert _.b[1][1].a1.value == 'aaa'
    assert _.b[1][1].a1.original_value == 'a1'
    assert _.f.value == 666
    # 未知属性测试
    with pytest.raises(AttributeError, match=re.escape('没有配置属性 "Config.x".')):
        _.x
    with pytest.raises(AttributeError, match=re.escape('没有配置属性 "Config.b[1][1].a2".')):
        _.b[1][1].a2
    # 字典属性修改测试
    with pytest.raises(AttributeError, match=re.escape('请使用 Config.set_config 方法设置配置属性.')):
        _.t1 = 123
    with pytest.raises(ValueError, match=re.escape('不允许修改配置项 "Config.c.c1".')):
        _.c['c1'] = 12345
    with pytest.raises(ValueError, match=re.escape('不允许修改配置项 "Config.b[0]".')):
        _.b[0] = 12345


if __name__ == '__main__':
    _ = Config(
        {'a': 333, 'b': [1, [2, {'a1': 'a1'}]], 'c': {'c1': 'c1', 'c2': ['c21', 'c22']}},
        default_map={'a': 123, 'f': 456},
    ).set_config('d', 1).set_config('e', 2)
    _.get_config('Config.a').value == 333
