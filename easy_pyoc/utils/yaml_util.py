"""YAML 工具"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

try:
    import yaml
except ModuleNotFoundError:
    raise ModuleNotFoundError('使用该模块前，请先安装 PyYAML 库：`pip install PyYAML`')

from . import path_util


def loads(text: str):
    """将 yaml 字符串转换为 dict"""
    return yaml.safe_load(text)


def dumps(data: dict):
    """将 dict 转换为 yaml 字符串"""
    return yaml.safe_dump(data)


def load(fp: 'FileDescriptorOrPath', encoding='utf-8'):
    """读取 yaml 文件"""
    with path_util.open(fp, 'r', encoding=encoding) as f:
        data = yaml.safe_load(f)
    return data


def dump(fp: 'FileDescriptorOrPath', data: dict, encoding='utf-8'):
    """写入 yaml 文件"""
    with path_util.open(fp, 'w', encoding=encoding) as f:
        yaml.safe_dump(data, f)
