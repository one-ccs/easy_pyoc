#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Mapping
import logging

from .color import AnsiColor


class ColorFormatter(logging.Formatter):
    """带颜色的日志格式化类"""

    COLOR  = {
        logging.DEBUG: AnsiColor(AnsiColor.FORE_BLUE),
        logging.INFO: AnsiColor(AnsiColor.FORE_RESET, AnsiColor.BACK_RESET),
        logging.WARNING: AnsiColor(AnsiColor.FORE_YELLOW),
        logging.ERROR: AnsiColor(AnsiColor.FORE_RED),
        logging.CRITICAL: AnsiColor(AnsiColor.FORE_MAGENTA),
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLOR[record.levelno]
        return f'{color}{super().format(record)}{AnsiColor(AnsiColor.FORE_RESET, AnsiColor.BACK_RESET)}'


class Logger:
    """单例 Logger 类

    Args:
        name (str, optional): 日志名称. 默认为 'easy_pyoc'.
        formatter (str, optional): 日志格式. 默认为 '[%(asctime)s] %(levelname)8s : %(message)s'.
        use_color (bool, optional): 是否使用颜色. 默认为 True.

    Returns:
        logging.Logger: 日志实例
    """
    _instance: Mapping[str, logging.Logger] = {}

    def __new__(cls, *args, **kwargs):
        name      = kwargs.get('name', 'easy_pyoc')
        formatter = kwargs.get('formatter', '[%(asctime)s] %(levelname)8s : %(message)s')
        use_color = kwargs.get('use_color', True)

        if name not in cls._instance:
            cls._instance[name] = logging.getLogger(name)
            cls._instance[name].setLevel(logging.INFO)

            handler = logging.StreamHandler()
            if use_color:
                handler.setFormatter(ColorFormatter(formatter))
            else:
                handler.setFormatter(logging.Formatter(formatter))

            cls._instance[name].addHandler(handler)
        return cls._instance[name]


if __name__ == '__main__':
    # color 测试，运行前请修改导入
    for use_color in [True, False]:
        logger = Logger(name=f'easy_pyoc_{use_color}', formatter='%(levelname)8s - %(name)s - %(message)s', use_color=use_color)
        logger.setLevel(logging.DEBUG)

        logger.debug('hello, world')
        logger.info('hello, world')
        logger.warning('hello, world')
        logger.error('hello, world')
        logger.critical('hello, world')
