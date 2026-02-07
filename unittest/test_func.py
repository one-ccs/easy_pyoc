import unittest
from unittest.mock import Mock, call
from time import sleep, time
from easy_pyoc.func import debounced, throttle


class TestFuncDecorators(unittest.TestCase):

    def test_debounced_happy_path(self):
        mock_func = Mock()
        debounced_func = debounced(0.1)(mock_func)
        debounced_func()
        sleep(0.2)
        mock_func.assert_called_once()

    def test_debounced_multiple_calls(self):
        mock_func = Mock()
        debounced_func = debounced(0.1)(mock_func)
        debounced_func()
        debounced_func()
        debounced_func()
        sleep(0.2)
        mock_func.assert_called_once()

    def test_debounced_with_custom_delay(self):
        mock_func = Mock()
        debounced_func = debounced(lambda args, kwargs: 0.1)(mock_func)
        debounced_func()
        sleep(0.2)
        mock_func.assert_called_once()

    def test_debounced_with_variable_delay(self):
        mock_func = Mock()
        debounced_func = debounced(lambda args, kwargs: args[0])(mock_func)
        debounced_func(0.1)
        debounced_func(0.2)
        sleep(0.3)
        mock_func.assert_called_once_with(0.2)

    def test_throttle_happy_path(self):
        mock_func = Mock()
        throttled_func = throttle(0.1)(mock_func)
        throttled_func()
        sleep(0.2)
        mock_func.assert_called_once()

    def test_throttle_multiple_calls_within_wait(self):
        mock_func = Mock()
        throttled_func = throttle(0.2)(mock_func)
        throttled_func()
        throttled_func()
        throttled_func()
        sleep(0.3)
        mock_func.assert_called_once()

    def test_throttle_multiple_calls_after_wait(self):
        mock_func = Mock()
        throttled_func = throttle(0.1)(mock_func)
        throttled_func()
        sleep(0.2)
        throttled_func()
        sleep(0.2)
        mock_func.assert_has_calls([call(), call()])

    def test_throttle_with_custom_wait(self):
        mock_func = Mock()
        throttled_func = throttle(lambda args, kwargs: 0.1)(mock_func)
        throttled_func()
        sleep(0.2)
        mock_func.assert_called_once()

    def test_throttle_with_variable_wait(self):
        mock_func = Mock()
        throttled_func = throttle(lambda args, kwargs: args[0])(mock_func)
        throttled_func(0.1)
        sleep(0.2)
        throttled_func(0.2)
        sleep(0.3)
        mock_func.assert_has_calls([call(0.1), call(0.2)])

    def test_debounced_no_delay(self):
        mock_func = Mock()
        debounced_func = debounced(0)(mock_func)
        debounced_func()
        debounced_func()
        debounced_func()
        sleep(0.1)
        self.assertGreater(mock_func.call_count, 1)

    def test_throttle_no_wait(self):
        mock_func = Mock()
        throttled_func = throttle(0)(mock_func)
        throttled_func()
        throttled_func()
        throttled_func()
        sleep(0.1)
        self.assertGreater(mock_func.call_count, 1)

    def test_debounced_negative_delay(self):
        mock_func = Mock()
        debounced_func = debounced(-0.1)(mock_func)
        debounced_func()
        sleep(0.2)
        mock_func.assert_called_once()

    def test_throttle_negative_wait(self):
        mock_func = Mock()
        throttled_func = throttle(-0.1)(mock_func)
        throttled_func()
        throttled_func()
        throttled_func()
        sleep(0.2)
        self.assertGreater(mock_func.call_count, 1)

    def test_debounced_callable_delay_returns_negative(self):
        mock_func = Mock()
        debounced_func = debounced(lambda args, kwargs: -0.1)(mock_func)
        debounced_func()
        sleep(0.2)
        mock_func.assert_called_once()

    def test_throttle_callable_wait_returns_negative(self):
        mock_func = Mock()
        throttled_func = throttle(lambda args, kwargs: -0.1)(mock_func)
        throttled_func()
        throttled_func()
        throttled_func()
        sleep(0.2)
        self.assertGreater(mock_func.call_count, 1)

    def test_debounced_callable_delay_returns_zero(self):
        mock_func = Mock()
        debounced_func = debounced(lambda args, kwargs: 0)(mock_func)
        debounced_func()
        debounced_func()
        debounced_func()
        sleep(0.1)
        self.assertGreater(mock_func.call_count, 1)

    def test_throttle_callable_wait_returns_zero(self):
        mock_func = Mock()
        throttled_func = throttle(lambda args, kwargs: 0)(mock_func)
        throttled_func()
        throttled_func()
        throttled_func()
        sleep(0.1)
        self.assertGreater(mock_func.call_count, 1)

    def test_debounced_callable_delay_returns_none(self):
        mock_func = Mock()
        debounced_func = debounced(lambda args, kwargs: None)(mock_func)
        with self.assertRaises(TypeError):
            debounced_func()

    def test_throttle_callable_wait_returns_none(self):
        mock_func = Mock()
        throttled_func = throttle(lambda args, kwargs: None)(mock_func)
        with self.assertRaises(TypeError):
            throttled_func()

    def test_debounced_callable_delay_returns_non_float(self):
        mock_func = Mock()
        debounced_func = debounced(lambda args, kwargs: '0.1')(mock_func)
        with self.assertRaises(TypeError):
            debounced_func()

    def test_throttle_callable_wait_returns_non_float(self):
        mock_func = Mock()
        throttled_func = throttle(lambda args, kwargs: '0.1')(mock_func)
        with self.assertRaises(TypeError):
            throttled_func()

    def test_debounced_with_args(self):
        mock_func = Mock()
        debounced_func = debounced(0.1)(mock_func)
        debounced_func(1, 2, 3)
        sleep(0.2)
        mock_func.assert_called_once_with(1, 2, 3)

    def test_debounced_with_kwargs(self):
        mock_func = Mock()
        debounced_func = debounced(0.1)(mock_func)
        debounced_func(a=1, b=2, c=3)
        sleep(0.2)
        mock_func.assert_called_once_with(a=1, b=2, c=3)

    def test_throttle_with_args(self):
        mock_func = Mock()
        throttled_func = throttle(0.1)(mock_func)
        throttled_func(1, 2, 3)
        sleep(0.2)
        mock_func.assert_called_once_with(1, 2, 3)

    def test_throttle_with_kwargs(self):
        mock_func = Mock()
        throttled_func = throttle(0.1)(mock_func)
        throttled_func(a=1, b=2, c=3)
        sleep(0.2)
        mock_func.assert_called_once_with(a=1, b=2, c=3)

    def test_debounced_with_exception(self):
        mock_func = Mock(side_effect=Exception("Test exception"))
        debounced_func = debounced(0.1)(mock_func)
        with self.assertRaises(Exception) as context:
            debounced_func()
            sleep(0.2)
        self.assertTrue('Test exception' in str(context.exception))

    def test_throttle_with_exception(self):
        mock_func = Mock(side_effect=Exception("Test exception"))
        throttled_func = throttle(0.1)(mock_func)
        with self.assertRaises(Exception) as context:
            throttled_func()
            sleep(0.2)
        self.assertTrue('Test exception' in str(context.exception))

    def test_debounced_no_args(self):
        mock_func = Mock()
        debounced_func = debounced(0.1)(mock_func)
        debounced_func()
        sleep(0.2)
        mock_func.assert_called_once()

    def test_throttle_no_args(self):
        mock_func = Mock()
        throttled_func = throttle(0.1)(mock_func)
        throttled_func()
        sleep(0.2)
        mock_func.assert_called_once()

    def test_debounced_no_kwargs(self):
        mock_func = Mock()
        debounced_func = debounced(0.1)(mock_func)
        debounced_func()
        sleep(0.2)
        mock_func.assert_called_once()

    def test_throttle_no_kwargs(self):
        mock_func = Mock()
        throttled_func = throttle(0.1)(mock_func)
        throttled_func()
        sleep(0.2)
        mock_func.assert_called_once()

    def test_debounced_with_mixed_args_and_kwargs(self):
        mock_func = Mock()
        debounced_func = debounced(0.1)(mock_func)
        debounced_func(1, 2, a=3, b=4)
        sleep(0.2)
        mock_func.assert_called_once_with(1, 2, a=3, b=4)

    def test_throttle_with_mixed_args_and_kwargs(self):
        mock_func = Mock()
        throttled_func = throttle(0.1)(mock_func)
        throttled_func(1, 2, a=3, b=4)
        sleep(0.2)
        mock_func.assert_called_once_with(1, 2, a=3, b=4)

    def test_debounced_with_none_delay(self):
        with self.assertRaises(TypeError):
            debounced(None)(Mock())

    def test_throttle_with_none_wait(self):
        with self.assertRaises(TypeError):
            throttle(None)(Mock())

    def test_debounced_with_non_callable_delay(self):
        mock_func = Mock()
        with self.assertRaises(TypeError):
            debounced('0.1')(mock_func)

    def test_throttle_with_non_callable_wait(self):
        mock_func = Mock()
        with self.assertRaises(TypeError):
            throttle('0.1')(mock_func)

    def test_debounced_with_delay_function_error(self):
        mock_func = Mock()
        debounced_func = debounced(lambda args, kwargs: args[10])(mock_func)
        debounced_func()
        sleep(0.2)
        mock_func.assert_not_called()

    def test_throttle_with_wait_function_error(self):
        mock_func = Mock()
        throttled_func = throttle(lambda args, kwargs: args[10])(mock_func)
        throttled_func()
        sleep(0.2)
        mock_func.assert_not_called()


if __name__ == '__main__':
    unittest.main()
