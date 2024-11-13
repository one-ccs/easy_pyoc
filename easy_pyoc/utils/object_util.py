#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, TypeVar, Optional, Literal, Callable, Any
from typing_extensions import Self
from functools import reduce
from operator import getitem

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

from .string_util import StringUtil
from .path_util import PathUtil


_T = TypeVar('_T')


class ObjectUtil(object):
    """对象工具类"""

    class MagicClass(object):
        """魔法类，用于实现 __str__、__repr__、__call__ 方法"""
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

    class ConfigClass(MagicClass):

        def __init__(
            self,
            config: dict | Callable[[], dict] | 'FileDescriptorOrPath',
            *,
            decoder: Literal['yaml', 'toml', 'json'] = 'yaml',
            default_map: Optional[dict] = None,
            hook: Optional[Callable[[str, Any, Self], Any]] = None,
        ):
            """将配置文件转为 dict 并让其可以像访问对象属性一样访问配置属性

            Args:
                config (dict | Callable[[], dict] | FileDescriptorOrPath):
                    配置文件，可以是字典、函数或文件路径
                decoder (Literal[&#39;yaml&#39;, &#39;toml&#39;, &#39;json&#39;], optional):
                    当 *config* 参数为文件路径时的解码器. 默认为 *yaml*.
                default_map (Optional[dict], optional):
                    根据 *default_map* 参数设置配置项默认值. 默认为 None.
                hook (Optional[Callable[[str, Any, Self], Any]], optional):
                    设置属性时的钩子函数, 传入(属性名称, 属性值, 对象实例), 返回
                    属性值设置对应属性, 若返回 `...` 忽略属性设置. 默认为 None.

            Raises:
                ValueError: 参数错误, *config* 必须为字典或路径.
            """
            if isinstance(config, dict):
                self.__init_dict(config, default_map, hook)
            elif callable(config):
                self.__init_dict(decoder(), default_map, hook)
            elif config is not None and decoder is not None:
                self.config_path= PathUtil.abspath(config)

                if decoder in {'yaml', 'toml', 'json'}:
                    self.__init_dict(self.__load_config(config, decoder), default_map, hook)
                else:
                    raise ValueError(f'不支持的解码器类型 "{decoder}"')
            else:
                raise ValueError('参数错误')

        def __getattr__(self, name):
            raise AttributeError(f'没有名为 "{name}" 的配置属性.')

        def __load_config(self, fp: 'FileDescriptorOrPath', decoder: Literal['yaml', 'toml', 'json']) -> dict:
            match decoder:
                case 'yaml':
                    from .yaml_util import YAMLUtil

                    return YAMLUtil.load(fp) or {}
                case 'toml':
                    from .toml_util import TOMLUtil

                    return TOMLUtil.load(fp) or {}
                case 'json':
                    from json import load

                    with PathUtil.open(fp, 'r') as f:
                        return load(f) or {}

        def __parse_list(self, data: list) -> list:
            _data = []
            for item in data:
                if isinstance(item, dict):
                    _data.append(ObjectUtil.ConfigClass(item))
                elif isinstance(item, list):
                    _data.append(self.__parse_list(item))
                else:
                    _data.append(item)
            return _data

        def __set_attr(self, attr: str, value: Any, hook: Optional[Callable[[str, Any, Self], Any]]):
            if hook is not None:
                value = hook(attr, value, self)

            if value is not ...:
                self.__dict__[attr] = value

        def __init_dict(self, config: dict, default_map: Optional[dict], hook: Optional[Callable[[str, Any, Self], Any]]):
            if not isinstance(config, dict):
                raise ValueError('参数错误, config 必须为字典类型')
            if default_map and not isinstance(default_map, dict):
                raise ValueError('参数错误, default_map 必须为字典类型')
            if hook and not callable(hook):
                raise ValueError('参数错误, hook 必须为可调用对象')

            self.config_dict = config

            # 使用默认值设置配置项
            if isinstance(default_map, dict):
                for attr, value in default_map.items():
                    if isinstance(value, dict):
                        self.__set_attr(attr, ObjectUtil.ConfigClass(value), hook)
                    elif isinstance(value, list):
                        self.__set_attr(attr, self.__parse_list(value), hook)
                    else:
                        self.__set_attr(attr, value, hook)

            # 加载配置项
            for attr, value in self.config_dict.items():
                if isinstance(value, dict):
                    self.__set_attr(attr, ObjectUtil.ConfigClass(value), hook)
                elif isinstance(value, list):
                    self.__set_attr(attr, self.__parse_list(value), hook)
                else:
                    self.__set_attr(attr, value, hook)

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
