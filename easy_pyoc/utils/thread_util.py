"""线程工具"""

from typing import Callable, Any, TypeAlias, ParamSpecArgs, ParamSpecKwargs
from threading import Thread, Event, Semaphore, Lock, current_thread, active_count, enumerate, get_ident
from traceback import extract_stack
from concurrent.futures import Executor, Future
from concurrent.futures._base import LOGGER
from queue import PriorityQueue, Empty
import os
import itertools
from concurrent.futures import ThreadPoolExecutor

from . import func_util


Task: TypeAlias = Callable[..., Any]


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


@func_util.singleton
class _ShutdownSentinel:
    """线程池关闭信号的哨兵对象"""

    def __lt__(self, other):
        return False


class _PriorityWorkItem:
    """包装优先级任务的工作项"""

    __slots__ = ('priority', 'future', 'task', 'args', 'kwargs')

    def __init__(self, priority: int, future: Future, task: Task, args: tuple, kwargs: dict):
        self.priority = priority
        self.future = future
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def __lt__(self, other):
        """用于优先级队列的比较，优先级小的任务优先执行"""
        return self.priority < other.priority

    def run(self):
        """执行任务并设置 future 的结果"""
        if not self.future.set_running_or_notify_cancel():
            return

        try:
            result = self.task(*self.args, **self.kwargs)
        except BaseException as exc:
            self.future.set_exception(exc)
            # 打破异常和 self 的引用循环
            self = None
        else:
            self.future.set_result(result)


class PriorityThreadPoolExecutor(Executor):

    # 用于生成唯一的执行器 ID
    _counter = itertools.count().__next__

    def __init__(
        self,
        max_workers: int | None = None,
        thread_name_prefix: str = '',
        initializer: Callable[..., None] | None = None,
        initargs: tuple = (),
    ):
        """基于优先级队列的线程池执行器

        支持任务优先级调度、线程初始化、自定义线程名称等高级特性。
        优先级值越小的任务越优先执行；优先级相同时按提交顺序执行。

        Args:
            max_workers (int, optional): 最大工作线程数，默认为 CPU 核数 + 4（最多32个）
            thread_name_prefix (str, optional): 线程名称前缀，用于调试和日志记录
            initializer (Callable[..., None], optional): 可选的初始化函数，在每个工作线程启动时调用
            initargs (tuple, optional): 传递给初始化函数的参数元组

        Raises:
            ValueError: 当 max_workers <= 0 时抛出
            TypeError: 当 initializer 不可调用时抛出

        Examples:

            >>> # 基本用法
            >>> executor = PriorityThreadPoolExecutor(max_workers=4)
            >>> future = executor.submit(print, "normal task", priority=0)
            >>> future = executor.submit(print, "high priority", priority=-1)
            >>> executor.shutdown(wait=True)

            >>> # 使用 with 语句
            >>> with PriorityThreadPoolExecutor(max_workers=4) as executor:
            ...     f1 = executor.submit(len, [1, 2, 3], priority=1)
            ...     f2 = executor.submit(sum, [1, 2, 3], priority=-1)
            ...     print(f1.result(), f2.result())

            >>> # 使用初始化函数
            >>> def init_worker(name):
            ...     print(f"Worker {name} initialized")
            >>> executor = PriorityThreadPoolExecutor(
            ...     max_workers=2,
            ...     thread_name_prefix='WorkerPool',
            ...     initializer=init_worker,
            ...     initargs=('thread-1',)
            ... )
        """
        if max_workers is None:
            max_workers = min(32, (os.cpu_count() or 1) + 4)
        if max_workers <= 0:
            raise ValueError('max_workers 必须大于 0')
        if initializer is not None and not callable(initializer):
            raise TypeError('initializer 必须是 callable 对象')

        self._max_workers = max_workers
        self._queue = PriorityQueue[tuple[int, int, _PriorityWorkItem | _ShutdownSentinel] | _ShutdownSentinel]()
        self._idle_semaphore = Semaphore(0)
        self._threads = set()
        self._shutdown = False
        self._shutdown_lock = Lock()
        self._thread_name_prefix = (
            thread_name_prefix or
            ("PriorityThreadPoolExecutor-%d" % self._counter())
        )
        self._initializer = initializer
        self._initargs = initargs
        self._broken = False
        self._task_counter = 0  # 用于同优先级任务的 FIFO 排序
        self._task_wrapper = None

        # 在初始化时创建所有工作线程
        for i in range(self._max_workers):
            thread_name = '%s_%d' % (self._thread_name_prefix, i)
            t = Thread(
                name=thread_name,
                target=self._worker,
                daemon=True
            )
            t.start()
            self._threads.add(t)

    def task_wrapper(self, wrapper: Callable[[Task, ParamSpecArgs, ParamSpecKwargs], Any]):
        """装饰器，设置任务包装函数

        该函数在每个任务执行前调用，可以用于在线程中执行任务前做一些额外的处理。

        Examples:

            >>> @executor.task_wrapper
            >>> def wrapper(task, args, kwargs):
            ...     with app.app_context():
            ...         return task(*args, **kwargs)
        """
        if not callable(wrapper):
            raise TypeError("wrapper 必须是 callable 对象")

        self._task_wrapper = wrapper

    def submit(
        self,
        task: Task,
        *args,
        priority: int = 0,
        **kwargs
    ) -> Future:
        """提交任务到线程池

        Args:
            task: 要执行的可调用对象
            *args: 传递给 task 的位置参数
            priority: 任务优先级，值越小越优先执行。默认为 0
            **kwargs: 传递给 task 的关键字参数

        Returns:
            Future: 表示异步执行的任务

        Raises:
            RuntimeError: 当线程池已关闭或线程初始化失败时

        例子：
            >>> executor = PriorityThreadPoolExecutor()
            >>> f1 = executor.submit(lambda x: x * 2, 5, priority=0)
            >>> f2 = executor.submit(lambda x: x + 10, 3, priority=-1)
            >>> print(f1.result(), f2.result())
        """
        with self._shutdown_lock:
            if self._broken:
                raise RuntimeError(self._broken)
            if self._shutdown:
                raise RuntimeError('线程池已关闭，无法提交任务')

            def wrapped_task(*args, **kwargs):
                if callable(self._task_wrapper):
                    return self._task_wrapper(task, *args, **kwargs)

                return task(*args, **kwargs)

            f = Future()
            w = _PriorityWorkItem(priority, f, wrapped_task, args, kwargs)

            # 将任务和计数器一起放入队列，确保同优先级任务按提交顺序执行
            self._queue.put((priority, self._task_counter, w))
            self._task_counter += 1

            return f

    def _worker(self):
        """工作线程的主循环"""
        try:
            # 调用初始化函数
            print(5666, self._initializer)
            if self._initializer:
                try:
                    self._initializer(*self._initargs)
                except BaseException:
                    LOGGER.critical('initializer 中出现异常：', exc_info=True)
                    with self._shutdown_lock:
                        self._broken = (
                            'initializer 执行异常，线程池不再可用'
                        )
                    # 唤醒其他等待中的工作线程
                    self._queue.put((-1, -1, _ShutdownSentinel()))
                    return

            while True:
                # 尝试获取任务
                try:
                    work_item = self._queue.get_nowait()
                except Empty:
                    # 队列为空，尝试增加空闲信号量
                    with self._shutdown_lock:
                        # 再检查一次队列不为空且未关闭
                        if self._queue.empty() and not self._shutdown:
                            self._idle_semaphore.release()
                    # 阻塞等待任务
                    work_item = self._queue.get(block=True)

                # 如果收到哨兵对象，说明线程池关闭或初始化失败
                if isinstance(work_item, _ShutdownSentinel):
                    # 把哨兵对象放回去，以便其他线程也能收到关闭信号
                    self._queue.put((-1, -1, work_item))
                    return

                if isinstance(work_item, tuple):
                    priority, counter, actual_item = work_item

                    if isinstance(actual_item, _ShutdownSentinel):
                        # 把哨兵对象放回去，以便其他线程也能收到关闭信号
                        self._queue.put(work_item)
                        return

                    work_item = actual_item

                try:
                    work_item.run()
                finally:
                    del work_item

        except BaseException:
            LOGGER.critical('Exception in worker', exc_info=True)

    def shutdown(self, wait: bool = True, cancel_futures: bool = False):
        """关闭线程池

        Args:
            wait: 是否等待所有线程完成。默认为 True
            cancel_futures: 是否取消所有待执行的任务。默认为 False

        例子：
            >>> executor = PriorityThreadPoolExecutor()
            >>> executor.submit(print, "task")
            >>> executor.shutdown(wait=True, cancel_futures=False)
        """
        with self._shutdown_lock:
            self._shutdown = True
            if cancel_futures:
                # 取消所有队列中的任务
                while True:
                    try:
                        item = self._queue.get_nowait()
                    except Empty:
                        break

                    if item is not None:
                        if isinstance(item, tuple):
                            _, _, work_item = item

                            if not isinstance(work_item, _ShutdownSentinel):
                                work_item.future.cancel()
                        elif not isinstance(item, _ShutdownSentinel):
                            work_item = item
                            work_item.future.cancel()

            # 发送哨兵信号告知所有工作线程关闭
            self._queue.put((-1, -1, _ShutdownSentinel()))

        if wait:
            for t in self._threads:
                t.join()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """自动关闭线程池"""
        self.shutdown(wait=True)
        return False


def get_current_name():
    """获取当前线程的名称"""
    return current_thread().name


def get_current_id():
    """获取当前线程的 id"""
    return current_thread().ident


def get_active_count():
    """获取活动线程的数量"""
    return active_count()


def get_active_list():
    """获取活动线程的列表"""
    return enumerate()
