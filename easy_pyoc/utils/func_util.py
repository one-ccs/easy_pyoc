"""函数工具"""

from typing import Callable, ParamSpecArgs, ParamSpecKwargs, Any
from traceback import format_exc
from functools import wraps
from inspect import signature
from threading import Timer
from time import time


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


def catch(logger: Callable = print, *, is_raise: bool = False, on_except: Callable[[Exception], None] | None = None):
    """装饰器，捕获函数异常并输出日志

    Args:
        logger (Callable, optional): 日志输出函数. 默认为 `print`.
        is_raise (bool, optional): 是否抛出异常. 默认为 False.
        on_except (Callable[[Exception], None] | None, optional): 异常回调函数. 默认为 None.
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


def debounced(delay: float | Callable[[tuple, dict], float], diff_params: bool = False):
    """装饰器，给函数添加防抖功能

    防抖是指在函数被连续调用时，只有最后一次调用会生效，在延迟时间内再次调用会重置延迟时间。

    Args:
        delay (float | Callable[[tuple, dict], float]): 延迟时间 (秒)
        diff_params (bool, optional): 是否对参数进行比较, 相同参数才会进行防抖. 默认为 False.
    """
    timers = {}

    def make_key(args, kwargs):
        return (args, tuple(sorted(kwargs.items())))

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal delay, timers

            _delay = delay(*args, **kwargs) if callable(delay) else delay
            key = make_key(args, kwargs) if diff_params else None

            if key in timers:
                timers[key].cancel()

            if _delay > 0:
                timers[key] = Timer(_delay, func, args=args, kwargs=kwargs)
                timers[key].start()
            else:
                func(*args, **kwargs)

        return wrapper
    return decorator


def throttle(wait: float | Callable[[tuple, dict], float]):
    """装饰器，给函数添加节流功能

    节流是指在函数被连续调用时，只有第一次调用会生效，超过执行间隔后才会再次调用。

    Args:
        wait (float | Callable[[tuple, dict], float]): 执行间隔 (秒)
    """
    last_time = 0

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal wait, last_time

            _wait = wait(*args, **kwargs) if callable(wait) else wait
            now   = time()

            if now - last_time > _wait:
                last_time = now
                return func(*args, **kwargs)
            return None

        return wrapper
    return decorator


def has_arg(func: Callable, name: str) -> bool:
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


def has_kwarg(func: Callable, name: str) -> bool:
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


def call[T](target: Callable[..., T], *args, **kwargs) -> T:
    """调用函数，并忽略多余参数

    Args:
        target (Callable[..., T]): 目标函数
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        T: 目标函数返回值
    """
    sig = signature(target)

    _args = 0
    _kwargs = {}
    for param in sig.parameters.values():
        if has_kwarg(target, param.name):
            _kwargs[param.name] = kwargs.get(param.name, param.default)
        else:
            _args += 1
    _args = args[:_args]

    return target(*_args, **_kwargs)
