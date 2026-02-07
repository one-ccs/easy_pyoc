from typing import TYPE_CHECKING, TypeVar, Optional, Literal, Callable, Union, Any
from typing_extensions import Self
from pathlib import Path
from copy import deepcopy

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

from ..utils import path_util
from .magic import Magic


class Config(Magic):
    """将配置文件转为 dict 并让其可以像访问对象属性一样访问配置属性"""

    hook = TypeVar('hook', bound=Callable[[Self, Any], Any])

    def __init__(
        self,
        config: Union[dict, 'FileDescriptorOrPath'],
        *,
        decoder: Optional[Literal['yaml', 'toml', 'json']] = None,
        default_map: dict = {},
        hook: Optional['Config.hook'] = None,
        **kw: Any,
    ):
        """
        Args:
            config (Union[dict, 'FileDescriptorOrPath']):
                配置，可以是字典或文件路径.
            decoder (Optional[Literal[&#39;yaml&#39;, &#39;toml&#39;, &#39;json&#39;]], optional):
                当 *config* 参数为文件路径时的解码器. 默认为 None.
            default_map (dict, optional):
                根据 *default_map* 参数设置配置项默认值. 默认为 {}.
            hook (Optional[Callable[[Self, Any], Any]], optional):
                设置属性时的钩子函数, 传入(对象实例, 属性值), 返回
                属性值设置对应属性. 默认为 None.

        Raises:
            ValueError: 参数错误, *config* 必须为字典或路径.
        """
        if decoder and decoder not in {'yaml', 'toml', 'json'}:
            raise ValueError(f'参数错误, 不支持的解码器类型 "{decoder}"')
        if not isinstance(default_map, dict):
            raise ValueError('参数错误, default_map 必须为字典.')
        if hook and not callable(hook):
            raise ValueError('参数错误, hook 必须为可调用对象')

        self.__hook           = hook
        self.__path           = kw.get('path', 'Config')
        self.__name           = kw.get('name', 'Config')
        self.__value          = kw.get('value', None)
        self.__original_value = deepcopy(config)
        self.__file_path      = None

        if config is not None and decoder is not None:
            self.__file_path = path_util.abspath(config)
            if not isinstance((_config := self.__load(config, decoder)), dict):
                raise ValueError(f'配置文件 "{self.__file_path}" 无法解析为字典.')
            self.__init_with_dict(_config, default_map)
        elif isinstance(config, dict):
            self.__init_with_dict(config, default_map)
        elif isinstance(config, list):
            if self.__path == 'Config':
                raise ValueError('参数错误, "list" 类型不能作为根配置.')
            self.__init_with_list(config)
        else:
            if self.__path == 'Config':
                raise ValueError(f'参数错误, "{type(config).__name__}" 类型不能作为根配置.')
            self.__init_with_other(config)

    @property
    def path(self) -> str:
        return self.__path

    @property
    def name(self) -> str:
        return self.__name

    @property
    def value(self) -> Any:
        return self.__value

    @property
    def original_value(self) -> Any:
        return self.__original_value

    @property
    def file_path(self) -> Optional[Path]:
        return self.__file_path

    def get_config(self, path: str, default: Any = None) -> Optional['Config']:
        if not str or not isinstance(path, str):
            raise ValueError('参数错误, path 必须为字符串.')

        parts = path.replace('[', '.').replace(']', '').split('.')
        obj = None

        for part in parts:
            if part == 'Config':
                obj = self
                continue

            if not isinstance(obj, Config):
                return default

            if part.isdigit():
                part = int(part)

            if part not in obj:
                return default

            obj = obj[part]

        return obj

    def set_config(self, name: str, value: Any) -> Self:
        self.__dict__[name] = Config(
            value,
            hook=self.__hook,
            path=f'{self.__path}.{name}',
            name=name,
        )
        self.__original_value[name] = value

        return self

    def __getattr__(self, name: str):
        raise AttributeError(f'没有配置属性 "{self.__path}.{name}".')

    def __getattribute__(self, name: str) -> Union['Config', Any]:
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any):
        if not name.startswith('_Config__'):
            raise AttributeError('请使用 Config.set_config 方法设置配置属性.')
        return super().__setattr__(name, value)

    def __getitem__(self, name: str | int) -> Union['Config', Any]:
        if isinstance(name, str) and hasattr(self, name):
            return getattr(self, name)
        return self.__value[name]

    def __setitem__(self, name: str, value: Any) -> None:
        if isinstance(name, str):
            _name = f'.{name}'
        if isinstance(name, int):
            _name = f'[{name}]'
        raise ValueError(f'不允许修改配置项 "{self.__path}{_name}".')

    def __delitem__(self, name: str) -> None:
        del self.__value[name]

    def __len__(self) -> int:
        return len(self.__value)

    def __iter__(self):
        return iter(self.__value)

    def __contains__(self, item: Any):
        if isinstance(self.original_value, dict):
            return hasattr(self, item)
        if isinstance(self.original_value, list):
            return item < len(self.__value)
        return False

    def __load(
        self,
        fp: 'FileDescriptorOrPath',
        decoder: Literal['yaml', 'toml', 'json'],
    ) -> Any:
        match decoder:
            case 'yaml':
                from ..utils import yaml_util

                return yaml_util.load(fp)
            case 'toml':
                from ..utils import toml_util

                return toml_util.load(fp)
            case 'json':
                from ..utils import json_util

                return json_util.load(fp)

    def __init_with_other(self, config: Any):
        if self.__hook:
            config = self.__hook(self, config)

        if config is ...:
            return

        self.__value = config

    def __init_with_list(self, config: list):
        self.__value = []

        for index, item in enumerate(config):
            self.__value.append(Config(
                item,
                hook=self.__hook,
                path=f'{self.__path}[{index}]',
                name=f'{self.__name}[{index}]',
            ))

    def __init_with_dict(self, config: dict, default_map: dict):
        self.__value = self

        # 设置默认值
        for attr, value in default_map.items():
            self.set_config(attr, value)

        for attr, value in config.items():
            self.set_config(attr, value)
