#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

try:
    import yaml
except ModuleNotFoundError:
    raise ModuleNotFoundError('使用该模块前，请先安装 PyYAML 库：`pip install PyYAML`')

from .path_util import PathUtil


class YAMLUtil:
    """YAML 工具类"""

    @staticmethod
    def loads(text: str) -> dict:
        """将 yaml 字符串转换为 dict"""
        return yaml.safe_load(text)

    @staticmethod
    def dumps(data: dict) -> str:
        """将 dict 转换为 yaml 字符串"""
        return yaml.safe_dump(data)

    @staticmethod
    def load(fp: 'FileDescriptorOrPath', encoding='utf-8') -> dict:
        """读取 yaml 文件"""
        with PathUtil.open(fp, 'r', encoding=encoding) as f:
            data = yaml.safe_load(f)
        return data

    @staticmethod
    def dump(fp: 'FileDescriptorOrPath', data: dict, encoding='utf-8') -> None:
        """写入 yaml 文件"""
        with PathUtil.open(fp, 'w', encoding=encoding) as f:
            yaml.safe_dump(data, f)
