#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TypeVar, Literal
from functools import reduce
from operator import getitem

from .string_util import StringUtil


_T = TypeVar('_T')


class ObjectUtil(object):
    """对象工具类"""

    @staticmethod
    def repr(obj: object, exclude: set[str] = {}, include: set[str] = {}) -> str:
        """将对象转为描述属性的字符串

        Args:
            obj (object): _description_
            exclude (set[str], optional): 忽略属性列表. 默认为 {}.
            include (set[str], optional): 包含属性列表. 默认为 {}.

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

    @staticmethod
    def vars(obj: object, exclude: set[str] = {}, include: set[str] = {}, style='snake') -> dict:
        """将对象的属性转为字典形式

        Args:
            obj (object): 对象实例
            exclude (set[str], optional): 忽略属性列表. 默认为 {}.
            include (set[str], optional): 包含属性列表. 默认为 {}.
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
                StringUtil.camel_to_snake(k): v
                for k, v in dict_items
                if k not in exclude
                    and not k.startswith('_')
                    or k in include
            }
        if style == 'camel':
            return {
                StringUtil.snake_to_camel(k): v
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

    @staticmethod
    def update_with_dict(obj: _T, *, exclude: set[str] = {}, style: Literal['snake', 'camel'] = 'snake', **kw) -> _T:
        """用关键字参数将对象赋值, 并忽略对象上不存在的属性

        Args:
            obj (_T): 对象实例
            exclude (set[str], optional): 忽略属性列表. 默认为 {}.
            style (Literal[&#39;snake&#39;, &#39;camel&#39;], optional): 键名命名风格. 默认为 'snake'.
            **kw: 关键字参数

        Returns:
            _T: 更新数据后的对象实例
        """
        style = kw.get('style', 'snake')
        exclude = kw.get('exclude', [])
        for k, v in kw.items():
            if style == 'snake':
                k = StringUtil.camel_to_snake(k)
            if style == 'camel':
                k = StringUtil.snake_to_camel(k)
            if hasattr(obj, k) and k not in exclude:
                setattr(obj, k, v)
        return obj

    @staticmethod
    def get_value_from_dict(data_dict: dict, key_string: str, default = None) -> any:
        """根据带点字符串的层级取出字典中的数据

        Args:
            data_dict (dict): 类字典类型
            key_string (str): 以英文句号分隔的字符串
            default (_type_, optional): 默认值. 默认为 None.

        Returns:
            any: 字典中对应的值
        """
        keys = key_string.split('.')
        try:
            return reduce(getitem, keys, data_dict)
        except:
            return default
