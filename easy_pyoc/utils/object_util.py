#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TypeVar
from functools import reduce
from operator import getitem

from .string_util import StringUtil


_T = TypeVar('_T')


class ObjectUtil(object):

    class MagicClass(object):
        _str_exclude = {}
        _repr_exclude = {}
        _call_exclude = {}
        _str_include = {}
        _repr_include = {}
        _call_include = {}


        def __str__(self) -> str:
            return ObjectUtil.repr(self, self._str_exclude, self._str_include)

        def __repr__(self) -> str:
            return ObjectUtil.repr(self, self._repr_exclude, self._repr_include)

        def __call__(self) -> dict:
            return ObjectUtil.vars(self, self._call_exclude, self._call_include)

    @staticmethod
    def repr(obj: object, exclude: set[str] = {}, include: set[str] = {}) -> str:
        """将对象转为描述属性的字符串
        :param obj 对象
        :param exclude (可选) 忽略属性列表
        :param include (可选) 包含属性列表
        :return 对象详情字符串
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
        :param obj 对象
        :param exclude (可选) 忽略属性列表
        :param include (可选) 包含属性列表
        :param style (可选 'camel',  默认 'snake') 键名命名风格，为 None 不转换
        :return 对象 { 属性: 值 } 组成的字典
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
    def update_with_dict(obj: _T, **kw) -> _T:
        """用关键字参数将对象赋值, 并忽略对象上不存在的属性
        :param obj 对象
        :param **kw 关键字参数
        :param exclude (可选) 忽略属性列表
        :param style (可选 'camel',  默认 'snake') 键名命名风格
        :return 更新数据后的对象
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
        :param data_dict 类字典类型
        :param key_string 以英文句号分隔的字符串
        :param default 默认值
        """
        keys = key_string.split('.')
        try:
            return reduce(getitem, keys, data_dict)
        except:
            return default
