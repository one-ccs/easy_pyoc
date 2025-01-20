#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Callable, TypeVar, ParamSpecArgs, ParamSpecKwargs, Any
from traceback import format_exc
from functools import wraps
from inspect import signature


_T = TypeVar('_T')


class FuncUtil(object):
    """函数工具类"""

    @staticmethod
    def is_arg(func: Callable, name: str) -> bool:
        """判断函数是否有指定名称的位置参数

        Args:
            func (Callable): 函数
            name (str): 参数名称

        Returns:
            bool: 是否有指定名称的位置参数
        """
        sig = signature(func)

        if param := sig.parameters.get(name):
            return param.kind == param.POSITIONAL_ONLY or '=' not in str(param)

        return False

    @staticmethod
    def is_kwarg(func: Callable, name: str) -> bool:
        """判断函数是否有指定名称的关键字参数

        Args:
            func (Callable): 函数
            name (str): 参数名称

        Returns:
            bool: 是否有指定名称的关键字参数
        """
        sig = signature(func)

        if param := sig.parameters.get(name):
            return param.kind == param.KEYWORD_ONLY or '=' in str(param)

        return False

    @staticmethod
    def log(logger: Callable = print):
        """装饰器，打印函数调用信息

        Args:
            logger (Callable, optional): 日志输出函数. 默认为 `print`.
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                msg = f'调用 "{func.__name__}" 函数'
                if args:   msg += f', 位置参数: {args}'
                if kwargs: msg += f', 关键字参数: {kwargs}'

                logger(msg)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def catch(logger: Callable = print, *, is_raise: bool = False, on_except: Callable | None = None):
        """装饰器，捕获函数异常并打印日志

        Args:
            logger (Callable, optional): 日志输出函数. 默认为 `print`.
            is_raise (bool, optional): 是否抛出异常. 默认为 False.
            on_except (Callable | None, optional): 异常回调函数. 默认为 None.
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    fmt_exc = format_exc()
                    _, exc = fmt_exc.split('\n')[-3:-1]

                    call_fn, raise_fn = func.__name__, 'unknown'

                    if _.strip().startswith('File "<string>"'):
                        raise_fn = _.split(' ')[-1]
                        line      = _.split(' ')[-3][:-1]
                        msg = f'函数 {raise_fn} ({line})'
                    else:
                        msg = f'函数 {call_fn}'

                    msg += f', 发生异常: {exc}'
                    msg += f', 调用者: {call_fn}'

                    if args:   msg += f', 位置参数: {args}'
                    if kwargs: msg += f', 关键字参数: {kwargs}'

                    tb = f'错误回溯开始 {call_fn} -> {raise_fn} ' + '+' * 32 + '\n'
                    if args:   tb += f'位置参数: {args}\n'
                    if kwargs: tb += f'关键字参数: {kwargs}\n'
                    tb += f'{fmt_exc}\n'
                    tb += f'错误回溯结束 {call_fn} -> {raise_fn} ' + '+' * 32 + '\n'
                    logger(msg, tb)

                    if callable(on_except): on_except(e)
                    if is_raise: raise
            return wrapper
        return decorator

    @staticmethod
    def hook(hook: Callable[[str, ParamSpecArgs, ParamSpecKwargs], bool | Any]):
        """装饰器，在函数调用前后执行 hook 函数

        Args:
            hook (Callable[[str, ParamSpecArgs, ParamSpecKwargs], bool  |  Any]):
                钩子函数, 将调用两次.
                第一次参数为 ('before', None, *args, **kwargs), 返回 `...` 则跳过函数调用,
                第二次参数为 ('after', result, *args, **kwargs), 返回非 None 值将作为函数调用结果返回.
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if callable(hook) and hook('before', None, *args, **kwargs) is ...:
                    return None

                try:
                    result = func(*args, **kwargs)
                finally:
                    if callable(hook) and (_ := hook('after', result, *args, **kwargs)) is not None:
                        return _

                return result
            return wrapper
        return decorator

    @staticmethod
    def call(target: Callable[..., _T], *args, **kwargs) -> _T:
        """调用函数，并忽略多余参数

        Args:
            target (Callable[..., _T]): 目标函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            _T: 目标函数返回值
        """
        sig = signature(target)

        _args = 0
        _kwargs = {}
        for param in sig.parameters.values():
            if FuncUtil.is_kwarg(target, param.name):
                _kwargs[param.name] = kwargs.get(param.name, param.default)
            else:
                _args += 1
        _args = args[:_args]

        return target(*_args, **_kwargs)
