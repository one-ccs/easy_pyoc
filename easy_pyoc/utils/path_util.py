#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, TypeVar, Optional
from pathlib import Path
from contextlib import contextmanager
import sys
import os


if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath


T = TypeVar('T')


class PathUtil(object):
    """路径工具类"""

    Path = Path
    sys_path = sys.path

    @staticmethod
    def get_env(key: str, default: Optional[T] = None) -> str | T:
        """获取环境变量"""
        return os.getenv(key, default)

    @staticmethod
    def get_work_dir() -> str:
        """获取工作目录"""
        return os.getcwd()

    @staticmethod
    def set_work_dir(path: 'FileDescriptorOrPath') -> None:
        """设置工作目录"""
        os.chdir(path)

    @staticmethod
    def get_home_dir() -> Path:
        """获取用户目录"""
        return Path.home()

    @staticmethod
    def get_dir(path: str) -> Path:
        """获取路径的目录"""
        p = Path(path)
        return p if p.is_dir() else p.parent

    @staticmethod
    def abspath(path: str = '') -> str:
        """返回路径的绝对路径"""
        return str(Path(path).absolute())

    @staticmethod
    def is_exists_file(path: str) -> bool:
        """判断文件是否存在"""
        _path = Path(path)
        return _path.exists() and _path.is_file()

    @staticmethod
    def is_exists_dir(path: str) -> bool:
        """判断路径是否是个存在"""
        _path = Path(path)
        return _path.exists() and _path.is_dir()

    @staticmethod
    @contextmanager
    def open(fp: 'FileDescriptorOrPath', mode: str, buffering: int = -1, encoding: str = 'utf-8'):
        """打开文件"""
        try:
            with open(fp, mode=mode, buffering=buffering, encoding=encoding) as f:
                yield f
        except FileNotFoundError:
            raise FileNotFoundError(f'文件 "{PathUtil.abspath(fp)}" 不存在')
