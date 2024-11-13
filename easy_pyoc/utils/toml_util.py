#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

try:
    import tomllib
except ModuleNotFoundError:
    raise ModuleNotFoundError('无法导入 "tomllib" 模块, 该模块仅 Python 3.11+ 版本支持.')

from .path_util import PathUtil


class TOMLUtil(object):
    """TOML 工具类, 仅提供 TOML 解析功能."""

    @staticmethod
    def loads(text: str) -> dict[str, Any]:
        return tomllib.loads(text)

    @staticmethod
    def load(fp: 'FileDescriptorOrPath', encoding: str = 'utf-8') -> dict[str, Any]:
        with PathUtil.open(fp, 'r', encoding=encoding) as f:
            return tomllib.load(f)
