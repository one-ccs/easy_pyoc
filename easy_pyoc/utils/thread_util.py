"""线程工具"""

from typing import Optional
from threading import Thread, Event, Semaphore, Condition, Lock, current_thread, active_count, enumerate, get_ident
from traceback import extract_stack
from concurrent.futures import Executor, Future
from queue import PriorityQueue
import os


class StackThread(Thread):
    """跨线程记录调用栈

    使用该类可以在多线程环境下记录和获取线程的调用栈信息。
    """

    ignore_functions = (
        '_bootstrap', '_bootstrap_inner', 'run', 'get_brief_stack', 'get_fn', 'push_summary'
    )
    """调用栈中忽略的函数名"""

    ignore_prefix = ('__', )
    """调用栈中忽略的函数名前缀"""

    _stack_tree = {}
    """调用树"""

    _summary    = {}
    """调用栈"""

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        StackThread.push_summary()

    def start(self):
        super().start()
        StackThread._stack_tree[self.ident] = get_ident()

    def set_parent(self, ident: int):
        """设置父线程标识符

        用于记录线程之间的调用关系，比如在消费者线程中手动设置父线程标识符。
        """
        StackThread._stack_tree[self.ident] = ident

    @staticmethod
    def get_fn():
        """获取当前线程调用栈"""
        return [
            f.name for f in extract_stack()
            if f.name not in StackThread.ignore_functions and not any(f.name.startswith(p) for p in StackThread.ignore_prefix)
        ]

    @staticmethod
    def push_summary():
        """记录当前线程调用栈

        用于在线程切换时手动记录调用栈，比如在生产者线程中手动记录调用栈。
        """
        StackThread._summary[get_ident()] = StackThread.get_fn()

    @staticmethod
    def get_brief_stack():
        """获取当前线程完整调用栈"""
        stack = StackThread.get_fn()
        _ftt = get_ident()
        while _ftt := StackThread._stack_tree.get(_ftt, None):
            if _ftt in StackThread._summary:
                stack = StackThread._summary[_ftt] + stack
        return stack


class StackTimer(StackThread):

    def __init__(self, interval, function, args=None, kwargs=None):
        StackThread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()

    def cancel(self):
        self.finished.set()

    def run(self):
        self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()


class PriorityThreadPoolExecutor(Executor):
    """一个基于线程池的执行器，支持任务优先级调度"""

    def __init__(self, max_workers: Optional[int] = None):
        """
        Args:
            max_workers (Optional[int], optional): 最大线程数. 默认为 None (自动根据处理器设置).

        Raises:
            ValueError: 当 'max_workers' 小于等于 0 时抛出异常.
        """
        max_workers = max_workers or os.cpu_count() or 1

        if max_workers <= 0:
            raise ValueError("'max_workers' 必须大于 0")

        self._max_workers = max_workers
        self._queue = PriorityQueue()
        self._idle_semaphore = Semaphore(0)
        self._threads = set()
        self._shutdown = False
        self._shutdown_lock = Lock()
        self._condition = Condition(Lock())

        for _ in range(self._max_workers):
            t = Thread(target=self._worker)
            t.daemon = True
            t.start()
            self._threads.append(t)

    def submit(self, fn, *args, **kwargs):
        """提交一个任务到线程池

        Args:
            fn (function): 要提交到线程池执行的函数
            *args: 传递给函数的位置参数
            **kwargs: 传递给函数的关键字参数

        Raises:
            RuntimeError: 当线程池已关闭时抛出异常

        Returns:
            _type_: concurrent.futures.Future 对象，表示异步执行的任务结果
        """
        with self._condition:
            if self._shutdown:
                raise RuntimeError('无法提交新任务，线程池已关闭。')

            f = Future()
            w = (self._queue.qsize(), fn, args, kwargs, f)
            self._queue.put(w)
            self._condition.notify()

        return f

    def _worker(self):
        while True:
            with self._condition:
                if self._shutdown and self._queue.empty():
                    return
                elif not self._queue.empty():
                    work = self._queue.get()
                else:
                    self._condition.wait()

            if work is not None:
                func, args, kwargs, future = work[1], work[2], work[3], work[4]
                try:
                    result = func(*args, **kwargs)
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)
                finally:
                    self._queue.task_done()

    def shutdown(self, wait: bool = True):
        """关闭线程池
        Args:
            wait (bool, optional): 是否等待所有线程完成. 默认为 True.
        """
        with self._shutdown_lock:
            self._shutdown = True

        with self._condition:
            self._condition.notify_all()

        if wait:
            for t in self._threads:
                t.join()


def get_current_name():
    """获取当前线程的名称"""
    return current_thread().name


def get_current_id():
    """获取当前线程的 id"""
    return current_thread().ident


def get_count():
    """获取活动线程的数量"""
    return active_count()


def get_list():
    """获取活动线程的列表"""
    return enumerate()
