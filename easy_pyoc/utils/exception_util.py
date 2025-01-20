#!/usr/bin/env python
# -*- coding: utf-8 -*-
from traceback import format_exc


class ExceptionUtil(object):
    """异常工具栏"""

    @staticmethod
    def format_exc() -> str:
        """返回异常调用信息"""
        return format_exc()

    @staticmethod
    def get_message() -> str:
        """返回异常信息"""
        return format_exc().split('\n')[-2].strip()
