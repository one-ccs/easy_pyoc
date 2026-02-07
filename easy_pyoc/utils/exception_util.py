"""异常工具"""

from traceback import format_exc as _format_exc


def format_exc() -> str:
    """返回异常调用信息"""
    return _format_exc()


def get_message() -> str:
    """返回异常信息"""
    return _format_exc().split('\n')[-2].strip()
