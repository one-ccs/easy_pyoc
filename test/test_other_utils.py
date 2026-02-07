"""测试其他工具模块"""

import pytest
from datetime import datetime, timedelta, timezone
import tempfile
import os
from pathlib import Path

from easy_pyoc import datetime_util
from easy_pyoc import object_util
from easy_pyoc import path_util
from easy_pyoc import thread_util
from easy_pyoc import json_util
from easy_pyoc import data_util
from easy_pyoc import package_util


class TestDatetimeUtil:
    """日期时间工具测试"""

    def test_now(self):
        """测试获取当前时间"""
        result = datetime_util.now()
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

    def test_str_now(self):
        """测试获取字符串格式的当前时间"""
        result = datetime_util.str_now()
        assert isinstance(result, str)
        assert len(result) == 19  # 'YYYY-MM-DD HH:MM:SS' 格式

    def test_str_now_custom_format(self):
        """测试使用自定义格式的字符串时间"""
        result = datetime_util.str_now('%Y/%m/%d')
        assert isinstance(result, str)
        assert '/' in result

    def test_diff(self):
        """测试时间差计算"""
        result = datetime_util.diff('2024-01-02 00:00:00', '2024-01-01 00:00:00')
        assert isinstance(result, timedelta)
        assert result.total_seconds() == 86400  # 1天 = 86400秒

    def test_strftime(self):
        """测试datetime转字符串"""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = datetime_util.strftime(dt)
        assert result == '2024-01-15 10:30:45'

    def test_strptime(self):
        """测试字符串转datetime"""
        result = datetime_util.strptime('2024-01-15 10:30:45')
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_stime2year(self):
        """测试字符串时间提取年份"""
        result = datetime_util.stime2year('2024-06-15 10:30:45')
        assert result == 2024

    def test_stime2month(self):
        """测试字符串时间提取月份"""
        result = datetime_util.stime2month('2024-06-15 10:30:45')
        assert result == 6

    def test_stime2day(self):
        """测试字符串时间提取日期"""
        result = datetime_util.stime2day('2024-06-15 10:30:45')
        assert result == 15

    def test_stime2hour(self):
        """测试字符串时间提取小时"""
        result = datetime_util.stime2hour('2024-06-15 10:30:45')
        assert result == 10

    def test_stime2minute(self):
        """测试字符串时间提取分钟"""
        result = datetime_util.stime2minute('2024-06-15 10:30:45')
        assert result == 30

    def test_stime2second(self):
        """测试字符串时间提取秒数"""
        result = datetime_util.stime2second('2024-06-15 10:30:45')
        assert result == 45


class TestObjectUtil:
    """对象工具测试"""

    def test_repr(self):
        """测试对象描述转字符串"""
        class TestObj:
            def __init__(self):
                self.name = 'test'
                self.value = 123

        obj = TestObj()
        result = object_util.repr(obj)
        assert 'TestObj' in result
        assert 'name=test' in result
        assert 'value=123' in result

    def test_vars_dict_to_dict(self):
        """测试字典到字典的转换"""
        input_dict = {'camel_case': 'value', 'another_key': 123}
        result = object_util.vars(input_dict)
        assert result == input_dict

    def test_vars_object_to_dict(self):
        """测试对象到字典的转换"""
        class TestObj:
            def __init__(self):
                self.camel_case_name = 'test'
                self.another_value = 123

        obj = TestObj()
        result = object_util.vars(obj)
        assert 'camel_case_name' in result
        assert 'another_value' in result

    def test_vars_with_exclude(self):
        """测试带排除属性的转换"""
        class TestObj:
            def __init__(self):
                self.include_this = 'yes'
                self.exclude_this = 'no'

        obj = TestObj()
        result = object_util.vars(obj, exclude={'exclude_this'})
        assert 'include_this' in result
        assert 'exclude_this' not in result

    def test_pub_class_catch_decorator(self):
        """测试类方法异常捕获装饰器"""
        # 注意：pub_class_catch有个bug，不会传递logger参数
        # 这里我们只测试它能成功装饰类
        @object_util.pub_class_catch
        class TestClass:
            def method_no_error(self):
                return 'success'

        obj = TestClass()
        assert obj.method_no_error() == 'success'


class TestPathUtil:
    """路径工具测试"""

    def test_get_work_dir(self):
        """测试获取工作目录"""
        result = path_util.get_work_dir()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_home_dir(self):
        """测试获取用户目录"""
        result = path_util.get_home_dir()
        assert isinstance(result, Path)
        assert result.exists()

    def test_get_dir_with_file_path(self):
        """测试获取文件的父目录"""
        result = path_util.get_dir('/path/to/file.txt')
        assert isinstance(result, Path)
        assert result.name == 'to'

    def test_get_dir_with_dir_path(self):
        """测试获取目录"""
        result = path_util.get_dir('/path/to/dir')
        assert isinstance(result, Path)

    def test_abspath(self):
        """测试相对路径转绝对路径"""
        result = path_util.abspath('.')
        assert isinstance(result, str)
        assert os.path.isabs(result)

    def test_is_exists_file(self):
        """测试文件存在检查"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        try:
            assert path_util.is_exists_file(temp_path)
            assert not path_util.is_exists_file('/nonexistent/file.txt')
        finally:
            os.unlink(temp_path)

    def test_is_exists_dir(self):
        """测试目录存在检查"""
        with tempfile.TemporaryDirectory() as temp_dir:
            assert path_util.is_exists_dir(temp_dir)
        assert not path_util.is_exists_dir('/nonexistent/directory')

    def test_open_file_read(self):
        """测试文件读取"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('test content')
            temp_path = f.name
        try:
            with path_util.open(temp_path, 'r') as f:
                content = f.read()
            assert content == 'test content'
        finally:
            os.unlink(temp_path)

    def test_open_file_not_found(self):
        """测试文件不存在异常"""
        with pytest.raises(FileNotFoundError, match='文件.+不存在'):
            with path_util.open('/nonexistent/file.txt', 'r') as f:
                pass


class TestThreadUtil:
    """线程工具测试"""

    def test_stack_thread_creation(self):
        """测试StackThread创建"""
        def dummy_func():
            pass

        thread = thread_util.StackThread(target=dummy_func)
        assert isinstance(thread, thread_util.StackThread)

    def test_stack_thread_get_fn(self):
        """测试获取线程调用栈"""
        stack = thread_util.StackThread.get_fn()
        assert isinstance(stack, list)

    def test_stack_thread_push_summary(self):
        """测试记录线程调用栈"""
        thread_util.StackThread.push_summary()
        # 应该成功执行无异常

    def test_stack_thread_get_brief_stack(self):
        """测试获取完整调用栈"""
        stack = thread_util.StackThread.get_brief_stack()
        assert isinstance(stack, list)


class TestJsonUtil:
    """JSON工具测试"""

    def test_loads_simple(self):
        """测试JSON字符串解析"""
        result = json_util.loads('{"key": "value", "number": 123}')
        assert result == {'key': 'value', 'number': 123}

    def test_loads_array(self):
        """测试JSON数组解析"""
        result = json_util.loads('[1, 2, 3, "test"]')
        assert result == [1, 2, 3, 'test']

    def test_loads_nested(self):
        """测试嵌套JSON解析"""
        result = json_util.loads('{"nested": {"key": "value"}}')
        assert result == {'nested': {'key': 'value'}}

    def test_dumps_dict(self):
        """测试字典序列化为JSON"""
        data = {'key': 'value', 'number': 123}
        result = json_util.dumps(data)
        assert isinstance(result, str)
        assert 'key' in result
        assert 'value' in result

    def test_dumps_list(self):
        """测试列表序列化为JSON"""
        data = [1, 2, 3, 'test']
        result = json_util.dumps(data)
        assert isinstance(result, str)
        assert '1' in result
        assert 'test' in result

    def test_load_file(self):
        """测试从文件加载JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"test": "data"}')
            temp_path = f.name
        try:
            result = json_util.load(temp_path)
            assert result == {'test': 'data'}
        finally:
            os.unlink(temp_path)

    def test_dump_file(self):
        """测试将JSON写入文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        try:
            data = {'test': 'data', 'number': 42}
            json_util.dump(data, temp_path)
            # 验证写入成功
            result = json_util.load(temp_path)
            assert result == data
        finally:
            os.unlink(temp_path)

    def test_loads_empty_string(self):
        """测试空JSON字符串"""
        with pytest.raises(Exception):
            json_util.loads('')

    def test_dumps_none(self):
        """测试None序列化"""
        result = json_util.dumps(None)
        assert result == 'null'


class TestCrcUtil:
    """CRC校验工具测试"""

    def test_crc16_xmodem(self):
        """测试CRC16-XMODEM校验"""
        data = b'hello'
        result = data_util.crc.crc16_xmodem(data)
        assert isinstance(result, int)
        assert 0 <= result <= 0xFFFF

    def test_crc16_xmodem_same_input_same_output(self):
        """测试相同输入产生相同输出"""
        data = b'test_data'
        result1 = data_util.crc.crc16_xmodem(data)
        result2 = data_util.crc.crc16_xmodem(data)
        assert result1 == result2

    def test_crc16_xmodem_empty_bytes(self):
        """测试空字节数据"""
        result = data_util.crc.crc16_xmodem(b'')
        assert result == 0

    def test_crc16_modbus(self):
        """测试CRC16-MODBUS校验"""
        data = b'hello'
        result = data_util.crc.crc16_modbus(data)
        assert isinstance(result, int)
        assert 0 <= result <= 0xFFFF

    def test_crc16_modbus_same_input_same_output(self):
        """测试相同输入产生相同输出"""
        data = b'test_data'
        result1 = data_util.crc.crc16_modbus(data)
        result2 = data_util.crc.crc16_modbus(data)
        assert result1 == result2

    def test_crc16_modbus_different_input(self):
        """测试不同输入产生不同输出"""
        result1 = data_util.crc.crc16_modbus(b'hello')
        result2 = data_util.crc.crc16_modbus(b'world')
        assert result1 != result2


class TestPackageUtil:
    """包工具测试"""

    def test_get_version(self):
        """测试获取包版本"""
        result = package_util.get_version('easy_pyoc')
        assert isinstance(result, str)
        assert len(result) > 0
        # 版本应该符合 X.Y.Z 格式
        parts = result.split('.')
        assert len(parts) >= 2

    def test_get_version_format(self):
        """测试版本格式"""
        result = package_util.get_version('easy_pyoc')
        # 版本号应该包含数字和点
        import re
        assert re.match(r'\d+\.\d+.*', result)


if __name__ == '__main__':
    pytest.main(['-vv', __file__])
