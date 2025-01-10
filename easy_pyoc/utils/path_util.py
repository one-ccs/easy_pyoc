#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING
from pathlib import Path
from contextlib import contextmanager
import sys
import os


if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath


class PathUtil(object):
    """路径工具类"""

    sys_path = sys.path

    @staticmethod
    def get_work_dir() -> str:
        """获取工作目录"""
        return os.getcwd()

    @staticmethod
    def set_work_dir(path: 'FileDescriptorOrPath') -> None:
        """设置工作目录"""
        os.chdir(path)

    @staticmethod
    def get_project_root(root_name: str, join_path: str | None = None) -> str:
        """返回项目根目录的绝对地址

        :param root_name 跟文件夹名称
        :param join_path 拼接路径
        """
        root_path = __file__[:__file__.index(root_name) + len(root_name)]

        if join_path:
            return str(Path(root_path).joinpath(join_path))
        return root_path

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
