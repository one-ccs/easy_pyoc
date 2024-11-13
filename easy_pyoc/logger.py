#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging


class Logger:
    """单例 Logger 类"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = logging.getLogger(kwargs.get('name', 'easy_pyoc'))
            cls._instance.setLevel(logging.INFO)

            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(levelname)-7s : %(message)s'))

            cls._instance.addHandler(handler)
        return cls._instance
