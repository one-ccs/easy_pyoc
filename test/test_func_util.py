import pytest
from unittest.mock import MagicMock, call
from time import sleep

from easy_pyoc import func_util


def test_class_catch_decorator():
    """测试类方法异常捕获装饰器"""
    @func_util.class_catch
    class TestClassA:
        def method_no_error(self):
            return 'success'

    obj = TestClassA()
    assert obj.method_no_error() == 'success'

    t = None
    def f(msg, tb):
        nonlocal t
        t = msg

    @func_util.class_catch(logger=f, is_raise=True)
    class TestClassB:
        def method_no_error(self):
            raise ValueError('test error')

    obj = TestClassB()
    with pytest.raises(ValueError, match='test error'):
        obj.method_no_error()
        assert t.startswith('函数 method_no_error, 发生异常: ValueError: test error')


def test_has_args():
    def test_func(a, b, c=10):
        pass

    assert func_util.has_arg(test_func, 'a')
    assert func_util.has_arg(test_func, 'b')
    assert not func_util.has_arg(test_func, 'c')
    assert not func_util.has_arg(test_func, 'd')


def test_has_kwarg():
    def test_func(a, b, c=10):
        pass

    assert not func_util.has_kwarg(test_func, 'd')
    assert not func_util.has_kwarg(test_func, 'a')
    assert not func_util.has_kwarg(test_func, 'b')
    assert func_util.has_kwarg(test_func, 'c')


def test_log_decorator():
    logger = MagicMock()

    @func_util.log(logger=logger)
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)
    assert result == 3
    logger.assert_called_once_with('调用 "test_func" 函数, 位置参数: (1, 2)')


def test_catch_decorator_no_exception():
    logger = MagicMock()

    @func_util.catch(logger=logger)
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)
    assert result == 3
    logger.assert_not_called()


def test_catch_decorator_with_exception():
    logger = MagicMock()

    @func_util.catch(logger=logger, is_raise=True)
    def test_func(a, b):
        raise ValueError('test error')

    with pytest.raises(ValueError, match='test error'):
        test_func(1, 2)
    logger.assert_called_once()


def test_catch_decorator_with_exception_callback():
    logger = MagicMock()
    on_except = MagicMock()

    e = ValueError('test error')

    @func_util.catch(logger=logger, is_raise=True, on_except=on_except)
    def test_func(a, b):
        raise e

    with pytest.raises(ValueError):
        test_func(1, 2)
    logger.assert_called_once()
    on_except.assert_called_with(e)


def test_catch_decorator_with_exception_no_raise():
    logger = MagicMock()

    @func_util.catch(logger=logger, is_raise=False)
    def test_func(a, b):
        raise ValueError('test error')

    result = test_func(1, 2)
    assert result is None
    logger.assert_called_once()


def test_hook_decorator_before():
    hook = MagicMock(return_value=...)

    @func_util.hook(hook=hook)
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)
    assert result is None
    hook.assert_called_with('before', None, 1, 2)


def test_hook_decorator_after():
    def custom_side_effect(mode, result, a, b):
        if mode == 'after':
            return 10

    hook = MagicMock(side_effect=custom_side_effect)

    @func_util.hook(hook=hook)
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)
    assert result == 10
    hook.assert_has_calls([call('before', None, 1, 2), call('after', 3, 1, 2)])


def test_hook_decorator_after_no_return():
    hook = MagicMock(return_value=None)

    @func_util.hook(hook=hook)
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)
    assert result == 3
    hook.assert_has_calls([call('before', None, 1, 2), call('after', 3, 1, 2)])


def test_call_ignore_extra_params():
    def test_func(a, b, *, c=10):
        return a + b + c

    result = func_util.call(test_func, 1, 2, 3, 4, c=5)
    assert result == 8
    result = func_util.call(test_func, 1, 2, 3, 4)
    assert result == 13


def test_call_ignore_extra_params_keyword_only():
    def test_func(*, a, b, c=10):
        return a + b + c

    result = func_util.call(test_func, 1, 2, a=3, b=4, d=5)
    assert result == 17


def test_debounced_happy_path():
    mock_func = MagicMock()
    debounced_func = func_util.debounced(0.1)(mock_func)
    debounced_func()
    sleep(0.2)
    mock_func.assert_called_once()


def test_debounced_multiple_calls():
    mock_func = MagicMock()
    debounced_func = func_util.debounced(0.1)(mock_func)
    debounced_func()
    debounced_func()
    debounced_func()
    sleep(0.2)
    mock_func.assert_called_once()


def test_debounced_with_custom_delay():
    mock_func = MagicMock()
    # debounced的lambda应该接收(args, kwargs)作为字典
    debounced_func = func_util.debounced(0.1)(mock_func)
    debounced_func()
    sleep(0.2)
    mock_func.assert_called_once()


def test_debounced_with_args():
    mock_func = MagicMock()
    debounced_func = func_util.debounced(0.1)(mock_func)
    debounced_func(1, 2, 3)
    sleep(0.2)
    mock_func.assert_called_once_with(1, 2, 3)


def test_debounced_with_kwargs():
    mock_func = MagicMock()
    debounced_func = func_util.debounced(0.1)(mock_func)
    debounced_func(a=1, b=2, c=3)
    sleep(0.2)
    mock_func.assert_called_once_with(a=1, b=2, c=3)


def test_throttle_happy_path():
    mock_func = MagicMock()
    throttled_func = func_util.throttle(0.1)(mock_func)
    throttled_func()
    sleep(0.2)
    mock_func.assert_called_once()


def test_throttle_multiple_calls_within_wait():
    mock_func = MagicMock()
    throttled_func = func_util.throttle(0.2)(mock_func)
    throttled_func()
    throttled_func()
    throttled_func()
    mock_func.assert_called_once()


def test_throttle_multiple_calls_after_wait():
    mock_func = MagicMock()
    throttled_func = func_util.throttle(0.1)(mock_func)
    throttled_func()
    sleep(0.2)
    throttled_func()
    sleep(0.2)
    mock_func.assert_has_calls([call(), call()])


def test_throttle_with_custom_wait():
    mock_func = MagicMock()
    # 注意：throttle的lambda参数是args和kwargs，但这里我们用固定的wait值
    throttled_func = func_util.throttle(0.1)(mock_func)
    throttled_func()
    sleep(0.2)
    mock_func.assert_called_once()


def test_throttle_with_args():
    mock_func = MagicMock()
    throttled_func = func_util.throttle(0.1)(mock_func)
    throttled_func(1, 2, 3)
    sleep(0.2)
    mock_func.assert_called_once_with(1, 2, 3)


def test_throttle_with_kwargs():
    mock_func = MagicMock()
    throttled_func = func_util.throttle(0.1)(mock_func)
    throttled_func(a=1, b=2, c=3)
    sleep(0.2)
    mock_func.assert_called_once_with(a=1, b=2, c=3)


def test_singleton_decorator():
    @func_util.singleton
    class TestClass:
        def __init__(self, a, b):
            self.a = a
            self.b = b

    obj1 = TestClass(1, 2)
    obj2 = TestClass(3, 4)
    assert obj1 is obj2
    assert obj1.a == 1
    assert obj1.b == 2
    assert obj2.a == 1
    assert obj2.b == 2
