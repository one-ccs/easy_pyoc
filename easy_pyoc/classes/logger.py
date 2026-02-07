from typing import Mapping
from re import Match, sub
import logging

from .color import AnsiColor


class ColorFormatter(logging.Formatter):
    """带颜色的日志格式化类"""

    COLOR  = {
        logging.DEBUG: AnsiColor.RESET_ALL,
        logging.INFO: AnsiColor.FORE_GREEN,
        logging.WARNING: AnsiColor.FORE_YELLOW,
        logging.ERROR: AnsiColor.FORE_RED,
        logging.CRITICAL: AnsiColor.FORE_MAGENTA,
    }

    def __init__(self, *args, **kwargs) -> None:
        # 修改格式化 levelname 的长度
        if 'fmt' in kwargs:
            def replace(match: Match) -> str:
                _g1 = match.group(1)
                _g2 = int(match.group(2))
                return f'%(levelname){_g1}{_g2 + 10}s'
            kwargs['fmt'] = sub(r'%\(levelname\)(\S*)(\d)s', replace, kwargs['fmt'])

        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLOR[record.levelno]
        record.levelname = f'{color}{record.levelname}{AnsiColor.RESET_ALL}'
        return super().format(record)


class Logger:
    """日志类

    Args:
        name (str, optional): 日志名称. 默认为 'easy_pyoc'.
        formatter (str, optional): 日志格式. 默认为 '[%(asctime)s] %(levelname)-8s : %(message)s'.
        use_color (bool, optional): 是否使用颜色. 默认为 True.

    Returns:
        logging.Logger: 日志实例
    """
    _instance: Mapping[str, logging.Logger] = {}

    def __new__(cls, *args, **kwargs):
        name      = kwargs.get('name', 'easy_pyoc')
        fmt       = kwargs.get('fmt', '[%(asctime)s] %(levelname)-8s : %(message)s')
        use_color = kwargs.get('use_color', True)

        if name not in cls._instance:
            cls._instance[name] = logging.getLogger(name)
            cls._instance[name].setLevel(logging.INFO)

            if fmt is not None:
                handler   = logging.StreamHandler()
                formatter = ColorFormatter(fmt=fmt) if use_color else logging.Formatter(fmt)
                formatter.default_msec_format = '%s.%03d'
                handler.setFormatter(formatter)
                cls._instance[name].addHandler(handler)

        return cls._instance[name]


if __name__ == '__main__':
    # color 测试，运行前请修改导入
    for use_color in [True, False]:
        logger = Logger(name=f'easy_pyoc_{use_color}', fmt='%(levelname)-8s : %(message)s', use_color=use_color)
        logger.setLevel(logging.DEBUG)

        logger.debug('hello, world')
        logger.info('hello, world')
        logger.warning('hello, world')
        logger.error('hello, world')
        logger.critical('hello, world')
        print('-' * 80)
