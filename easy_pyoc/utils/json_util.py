"""
JSON 工具
"""

from typing import TYPE_CHECKING, Callable, Any
from re import sub, DOTALL
import json

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

from . import path_util


def loads(
    text: str,
    *,
    cls: type[json.JSONDecoder] | None = None,
    object_hook: Callable[[dict[Any, Any]], Any] | None = None,
    parse_float: Callable[[str], Any] | None = None,
    parse_int: Callable[[str], Any] | None = None,
    parse_constant: Callable[[str], Any] | None = None,
    object_pairs_hook: Callable[[list[tuple[Any, Any]]], Any] | None = None,
    **kw: Any,
):
    """反序列化 JSON 字符串 *text* (*str*, *bytes*, 或 *bytearray*) 为 Python 对象.

    To use a custom `JSONDecoder` subclass, specify it with the `cls`
    kwarg; otherwise `JSONDecoder` is used.

    Args:
        text (str): JSON 字符串
        cls (type[json.JSONDecoder] | None, optional):
            `JSONDecoder` 子类. 默认为 None.
        object_hook (Callable[[dict[Any, Any]], Any] | None, optional):
            `object_hook` is an optional function that will be called with
            the result of any object literal decode (a `dict`). The return
            value of `object_hook` will be used instead of the `dict`.
            This feature can be used to implement custom decoders
            (e.g. JSON-RPC class hinting). 默认为 None.
        parse_float (Callable[[str], Any] | None, optional):
            `parse_float`, if specified, will be called with the string of
            every JSON float to be decoded. By default this is equivalent to
            float(num_str). This can be used to use another datatype or parser
            for JSON floats (e.g. decimal.Decimal). 默认为 None.
        parse_int (Callable[[str], Any] | None, optional):
            `parse_int`, if specified, will be called with the string of every
            JSON int to be decoded. By default this is equivalent to int(num_str).
            This can be used to use another datatype or parser for JSON integers
            (e.g. float). 默认为 None.
        parse_constant (Callable[[str], Any] | None, optional):
            `parse_constant`, if specified, will be called with one of the
            following strings: -Infinity, Infinity, NaN.
            This can be used to raise an exception if invalid JSON numbers
            are encountered. 默认为 None.
        object_pairs_hook (Callable[[list[tuple[Any, Any]]], Any] | None, optional):
            `object_pairs_hook` is an optional function that will be called with
            the result of any object literal decoded with an ordered list of pairs.
            The return value of `object_pairs_hook` will be used instead of the
            `dict`. This feature can be used to implement custom decoders.  If
            `object_hook` is also defined, the `object_pairs_hook` takes
            priority. 默认为 None.

    Returns:
        Any: Python 对象.
    """
    return json.loads(
        text,
        cls=cls,
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        object_pairs_hook=object_pairs_hook,
        **kw,
    )


def dumps(
    obj: Any,
    *,
    indent: int = 4,
    ensure_ascii: bool = False,
    default: Callable[[Any], Any] | None = None,
):
    return json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii, default=default)


def load(fp: 'FileDescriptorOrPath', *, encoding: str = 'utf-8'):
    with path_util.open(fp, 'r', encoding=encoding) as f:
        return json.load(f)


def dump(
    obj: Any,
    fp: 'FileDescriptorOrPath',
    *,
    encoding: str = 'utf-8',
    indent: int = 4,
    ensure_ascii: bool = False,
    default: Callable[[Any], Any] | None = None,
):
    with path_util.open(fp, 'w', encoding=encoding) as f:
        json.dump(obj, f, indent=indent, ensure_ascii=ensure_ascii, default=default)


def loads_json5(text: str):
    """解析 JSON5 格式的字符串"""
    # 移除多行注释
    text = sub(r"/\*.*?\*/", "", text, flags=DOTALL)
    # 移除单行注释
    text = sub(r"//.*?\n", "", text)
    # 将单引号替换为双引号
    # text = sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", r'"\1"', text)
    # 移除尾随逗号
    text = sub(r',\s*(?=[}\]])', '', text)

    return loads(text)
