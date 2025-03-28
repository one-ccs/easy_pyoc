#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Any, Iterable, Mapping, Callable, Optional
from threading import Thread, Event, current_thread, active_count


class ThreadUtil:

    tasks: dict[int, tuple[Thread, Event]] = {}
    """任务字典, key 为任务 id, value 为 (任务对象, 停止事件) """

    @staticmethod
    def get_current_name():
        return current_thread().name

    @staticmethod
    def get_current_id():
        return current_thread().ident

    @staticmethod
    def get_count():
        return active_count()

    @staticmethod
    def get_list():
        return enumerate()

    @staticmethod
    def execute_task(
        target: Callable[[Event], None],
        args: Iterable[Any] = (),
        kwargs: Optional[Mapping[str, Any]] = None,
        daemon: bool = True,
    ) -> Optional[int]:
        """执行一个任务, 该任务应该通过 stop_flag.is_set() 来判断是否需要停止.

        Args:
            target (Callable[[Event], None]): 运行的函数, 第一个位置参数固定为 stop_flag.
            args (Iterable[Any], optional): 位置参数. 默认为 ().
            kwargs (Optional[Mapping[str, Any]], optional): 关键字参数. 默认为 None.
            daemon (bool, optional): 是否是守护线程. 默认为 True.

        Returns:
            Optional[int]: 任务 id
        """
        # 清除未活动的任务
        need_clear = [task_id for task_id, (task, _) in ThreadUtil.tasks.items() if not task.is_alive()]
        for task_id in need_clear:
            ThreadUtil.tasks.pop(task_id, None)

        stop_flag = Event()
        stop_flag.set()

        task = Thread(target=target, args=(stop_flag, *args), kwargs=kwargs, daemon=daemon)
        task.start()

        task_id = task.ident
        ThreadUtil.tasks[task_id] = (task, stop_flag)

        return task_id

    @staticmethod
    def chancel_task(task_id: int):
        """取消一个任务, 并调用 stop_flag.clear()

        Args:
            task_id (int): 任务 id

        Raises:
            ValueError: 任务不存在或已结束
        """
        (task, stop_flag) = ThreadUtil.tasks.get(task_id, (None, None))

        if not task:
            raise ValueError(f'任务 "{task_id}" 不存在')

        stop_flag.clear()
        task.join()
        ThreadUtil.tasks.pop(task_id, None)
