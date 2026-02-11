"""对象工具"""

from typing import Literal, Container
from functools import reduce
from operator import getitem

from . import string_util


def repr(obj: object, exclude: Container[str] = {}, include: Container[str] = {}) -> str:
    """将对象转为描述属性的字符串

    Args:
        obj (object): _description_
        exclude (Container[str], optional): 忽略属性列表. 默认为 {}.
        include (Container[str], optional): 包含属性列表. 默认为 {}.

    Returns:
        str: 对象详情字符串
    """
    class_name = obj.__class__.__name__
    attributes = [
        f'{k}={f"{v}" if isinstance(v, str) else v}'
        for k, v in obj.__dict__.items()
        if k not in exclude
            and not k.startswith('_')
            or k in include
    ]
    attributes_str = ', '.join(attributes)
    return f'{class_name}({attributes_str})'


def vars(obj: object, exclude: Container[str] = {}, include: Container[str] = {}, style='snake') -> dict:
    """将对象的属性转为字典形式

    Args:
        obj (object): 对象实例
        exclude (Container[str], optional): 忽略属性列表. 默认为 {}.
        include (Container[str], optional): 包含属性列表. 默认为 {}.
        style (str, optional): 键名命名风格，为 None 不转换. 默认为 'snake'.

    Returns:
        dict: 对象 { 属性: 值 } 组成的字典
    """
    dict_items = {}
    if isinstance(obj, dict):
        dict_items = obj.items()
    if hasattr(obj, '__dict__'):
        dict_items = obj.__dict__.items()

    if style == 'snake':
        return {
            string_util.camel_to_snake(k): v
            for k, v in dict_items
            if k not in exclude
                and not k.startswith('_')
                or k in include
        }
    if style == 'camel':
        return {
            string_util.snake_to_camel(k): v
            for k, v in dict_items
            if k not in exclude
                and not k.startswith('_')
                or k in include
        }
    return {
        k: v
        for k, v in dict_items
        if k not in exclude
            and not k.startswith('_')
            or k in include
    }


def update_with_dict[T](obj: T, *, exclude: Container[str] = {}, style: Literal['snake', 'camel'] = 'snake', **kw) -> T:
    """用关键字参数将对象赋值, 并忽略对象上不存在的属性

    Args:
        obj (T): 对象实例
        exclude (set[str], optional): 忽略属性列表. 默认为 {}.
        style (Literal[&#39;snake&#39;, &#39;camel&#39;], optional): 键名命名风格. 默认为 'snake'.
        **kw: 关键字参数

    Returns:
        T: 更新数据后的对象实例
    """
    for k, v in kw.items():
        if style == 'snake':
            k = string_util.camel_to_snake(k)
        if style == 'camel':
            k = string_util.snake_to_camel(k)
        if hasattr(obj, k) and k not in exclude:
            setattr(obj, k, v)
    return obj


def get_value_from_dict[T](data: dict, path: str, default: T = None) -> T:
    """根据带点字符串的层级取出字典中的数据

    Args:
        data (dict): 类字典类型
        path (str): 以英文句号分隔的字符串
        default (T, optional): 默认值. 默认为 None.

    Returns:
        T: 字典中对应的值
    """
    keys = path.split('.')
    try:
        return reduce(getitem, keys, data)
    except:
        return default


def set_value_to_dict(data: dict, path: str, value) -> dict:
    """根据带点字符串的层级设置字典中的数据

    Args:
        data (dict): 类字典类型
        path (str): 以英文句号分隔的字符串
        value (Any): 要设置的值
    """
    keys = path.split('.')
    for key in keys[:-1]:
        data = data.setdefault(key, {})
    try:
        data[keys[-1]] = value
    finally:
        return data
