"""测试 PriorityThreadPoolExecutor"""

import time
import pytest
from easy_pyoc.utils.thread_util import PriorityThreadPoolExecutor


class TestPriorityThreadPoolExecutor:
    """PriorityThreadPoolExecutor 的测试类"""

    def test_basic_submit(self):
        """测试基本的提交和执行"""
        with PriorityThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(lambda x: x * 2, 5)
            result = future.result(timeout=2)
            assert result == 10

    def test_priority_execution_order(self):
        """测试优先级执行顺序"""
        execution_order = []

        def record_task(task_id, delay=0):
            if delay:
                time.sleep(delay)
            execution_order.append(task_id)

        with PriorityThreadPoolExecutor(max_workers=1) as executor:
            # 提交优先级不同的任务
            f1 = executor.submit(record_task, 1, priority=10)
            f2 = executor.submit(record_task, 2, priority=1)
            f3 = executor.submit(record_task, 3, priority=5)
            f4 = executor.submit(record_task, 4, priority=0)

            f1.result()
            f2.result()
            f3.result()
            f4.result()

        # 期望执行顺序：4(优先级0)、2(优先级1)、3(优先级5)、1(优先级10)
        assert execution_order == [4, 2, 3, 1]

    def test_fifo_for_same_priority(self):
        """测试相同优先级的任务按提交顺序执行"""
        execution_order = []

        def record_task(task_id):
            execution_order.append(task_id)

        with PriorityThreadPoolExecutor(max_workers=1) as executor:
            # 提交相同优先级的任务
            futures = []
            for i in range(1, 5):
                f = executor.submit(record_task, i, priority=0)
                futures.append(f)

            # 等待所有任务完成
            for f in futures:
                f.result()

        # 期望执行顺序：1、2、3、4（提交顺序）
        assert execution_order == [1, 2, 3, 4]

    def test_exception_handling(self):
        """测试异常处理"""
        def failing_task():
            raise ValueError("Test error")

        with PriorityThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(failing_task)
            with pytest.raises(ValueError, match="Test error"):
                future.result(timeout=2)

    def test_initializer(self):
        """测试线程初始化函数"""
        initialized_threads = []

        def init_worker(thread_id):
            initialized_threads.append(thread_id)

        with PriorityThreadPoolExecutor(
            max_workers=2,
            initializer=init_worker,
            initargs=(1,),
        ) as executor:
            # 提交任务触发线程创建
            f1 = executor.submit(lambda: 1)
            f2 = executor.submit(lambda: 2)
            f1.result()
            f2.result()

        # 应该有初始化调用
        assert len(initialized_threads) > 0

    def test_context_manager(self):
        """测试上下文管理器"""
        results = []

        with PriorityThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(lambda: 1)
            f2 = executor.submit(lambda: 2)
            results.append(f1.result())
            results.append(f2.result())

        assert results == [1, 2]

    def test_cancel_futures(self):
        """测试任务取消"""
        with PriorityThreadPoolExecutor(max_workers=1) as executor:
            futures = []
            for i in range(5):
                f = executor.submit(time.sleep, 0.1)
                futures.append(f)

            # 立即关闭并取消待执行任务
            executor.shutdown(wait=False, cancel_futures=True)

            # 检查是否有任务被取消
            cancelled_count = sum(1 for f in futures if f.cancelled())
            assert cancelled_count > 0

    def test_multiple_workers(self):
        """测试多线程执行"""
        import threading

        thread_ids = []

        def record_thread_id():
            thread_ids.append(threading.current_thread().ident)
            time.sleep(0.01)

        with PriorityThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(record_thread_id) for _ in range(6)]
            for f in futures:
                f.result()

        # 应该使用多个线程
        unique_threads = len(set(thread_ids))
        assert unique_threads > 1

    def test_invalid_max_workers(self):
        """测试无效的 max_workers"""
        with pytest.raises(ValueError):
            PriorityThreadPoolExecutor(max_workers=0)

        with pytest.raises(ValueError):
            PriorityThreadPoolExecutor(max_workers=-1)

    def test_invalid_initializer(self):
        """测试无效的初始化函数"""
        with pytest.raises(TypeError):
            PriorityThreadPoolExecutor(initializer="not_callable")

    def test_shutdown_after_submission(self):
        """测试关闭后无法提交任务"""
        executor = PriorityThreadPoolExecutor(max_workers=2)
        executor.shutdown(wait=True)

        with pytest.raises(RuntimeError):
            executor.submit(lambda: 1)

    def test_thread_name_prefix(self):
        """测试自定义线程名称前缀"""
        import threading

        thread_names = []

        def record_thread_name():
            thread_names.append(threading.current_thread().name)

        with PriorityThreadPoolExecutor(
            max_workers=2,
            thread_name_prefix="TestWorker"
        ) as executor:
            f1 = executor.submit(record_thread_name)
            f1.result()

        # 线程名称应该包含自定义前缀
        assert any("TestWorker" in name for name in thread_names)

    def test_large_number_of_tasks(self):
        """测试大量任务提交"""
        with PriorityThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i in range(100):
                f = executor.submit(lambda x=i: x * 2, priority=i % 10)
                futures.append(f)

            results = [f.result() for f in futures]

        assert len(results) == 100
        assert all(isinstance(r, int) for r in results)
