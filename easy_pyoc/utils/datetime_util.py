"""
日期时间工具
"""

from datetime import timedelta, datetime, timezone


def now() -> datetime:
    """返回 datetime 格式的当前时间"""
    return datetime.now(tz=timezone.utc)


def str_now(format=r'%Y-%m-%d %H:%M:%S') -> str:
    """返回字符串格式的当前时间"""
    return datetime.now(tz=timezone.utc).strftime(format)


def diff(minuend: str, minus: str, format=r'%Y-%m-%d %H:%M:%S') -> timedelta:
    """返回 minuend 减去 minus 的时间差 (单位 s)"""
    return (datetime.strptime(minuend, format) - datetime.strptime(minus, format))


def strftime(time: datetime, format=r'%Y-%m-%d %H:%M:%S') -> str:
    """datetime 时间格式转字符串"""
    return datetime.strftime(time, format)


def strptime(stime: str, format=r'%Y-%m-%d %H:%M:%S') -> datetime:
    """字符串时间格式转 datetime"""
    return datetime.strptime(stime, format)


def stime2year(stime: str, format=r'%Y-%m-%d %H:%M:%S') -> int:
    """返回字符串时间格式中的 年"""
    return datetime.strptime(stime, format).year


def stime2month(stime: str, format=r'%Y-%m-%d %H:%M:%S') -> int:
    """返回字符串时间格式中的 月"""
    return datetime.strptime(stime, format).month


def stime2day(stime: str, format=r'%Y-%m-%d %H:%M:%S') -> int:
    """返回字符串时间格式中的 日"""
    return datetime.strptime(stime, format).day


def stime2hour(stime: str, format=r'%Y-%m-%d %H:%M:%S') -> int:
    """返回字符串时间格式中的 时"""
    return datetime.strptime(stime, format).hour


def stime2minute(stime: str, format=r'%Y-%m-%d %H:%M:%S') -> int:
    """返回字符串时间格式中的 分"""
    return datetime.strptime(stime, format).minute


def stime2second(stime: str, format=r'%Y-%m-%d %H:%M:%S') -> int:
    """返回字符串时间格式中的 秒"""
    return datetime.strptime(stime, format).second
