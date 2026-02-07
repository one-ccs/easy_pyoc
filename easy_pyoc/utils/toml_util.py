"""toml 工具, 仅提供 toml 解析功能."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

try:
    import tomllib
except ModuleNotFoundError:
    raise ModuleNotFoundError('无法导入 "tomllib" 模块, 该模块仅 Python 3.11+ 版本支持.')

from . import path_util


def loads(text: str):
    return tomllib.loads(text)


def load(fp: 'FileDescriptorOrPath', encoding: str = 'utf-8'):
    with path_util.open(fp, 'r', encoding=encoding) as f:
        return tomllib.load(f)
