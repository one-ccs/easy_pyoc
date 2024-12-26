#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock, call

from easy_pyoc import FuncUtil


def test_is_args():
    def test_func(a, b, c=10):
        pass

    assert FuncUtil.is_arg(test_func, 'a')
    assert FuncUtil.is_arg(test_func, 'b')
    assert not FuncUtil.is_arg(test_func, 'c')
    assert not FuncUtil.is_arg(test_func, 'd')

def test_is_kwarg():
    def test_func(a, b, c=10):
        pass

    assert not FuncUtil.is_kwarg(test_func, 'd')
    assert not FuncUtil.is_kwarg(test_func, 'a')
    assert not FuncUtil.is_kwarg(test_func, 'b')
    assert FuncUtil.is_kwarg(test_func, 'c')


def test_log_decorator():
    logger = MagicMock()

    @FuncUtil.log(logger=logger)
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)
    assert result == 3
    logger.assert_called_once_with('调用 "test_func" 函数, 位置参数: (1, 2)')


def test_catch_decorator_no_exception():
    logger = MagicMock()

    @FuncUtil.catch(logger=logger)
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)
    assert result == 3
    logger.assert_not_called()


def test_catch_decorator_with_exception():
    logger = MagicMock()

    @FuncUtil.catch(logger=logger, is_raise=True)
    def test_func(a, b):
        raise ValueError('test error')

    with pytest.raises(ValueError, match='test error'):
        test_func(1, 2)
    logger.assert_called_once()


def test_catch_decorator_with_exception_callback():
    logger = MagicMock()
    on_except = MagicMock()

    e = ValueError('test error')

    @FuncUtil.catch(logger=logger, is_raise=True, on_except=on_except)
    def test_func(a, b):
        raise e

    with pytest.raises(ValueError):
        test_func(1, 2)
    logger.assert_called_once()
    on_except.assert_called_with(e)


def test_catch_decorator_with_exception_no_raise():
    logger = MagicMock()

    @FuncUtil.catch(logger=logger, is_raise=False)
    def test_func(a, b):
        raise ValueError('test error')

    result = test_func(1, 2)
    assert result is None
    logger.assert_called_once()


def test_hook_decorator_before():
    hook = MagicMock(return_value=...)

    @FuncUtil.hook(hook=hook)
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

    @FuncUtil.hook(hook=hook)
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)
    assert result == 10
    hook.assert_has_calls([call('before', None, 1, 2), call('after', 3, 1, 2)])


def test_hook_decorator_after_no_return():
    hook = MagicMock(return_value=None)

    @FuncUtil.hook(hook=hook)
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)
    assert result == 3
    hook.assert_has_calls([call('before', None, 1, 2), call('after', 3, 1, 2)])


def test_call_ignore_extra_params():
    def test_func(a, b, *, c=10):
        return a + b + c

    result = FuncUtil.call(test_func, 1, 2, 3, 4, c=5)
    assert result == 8
    result = FuncUtil.call(test_func, 1, 2, 3, 4)
    assert result == 13


def test_call_ignore_extra_params_keyword_only():
    def test_func(*, a, b, c=10):
        return a + b + c

    result = FuncUtil.call(test_func, 1, 2, a=3, b=4, d=5)
    assert result == 17
