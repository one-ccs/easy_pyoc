#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Mapping
import logging


class Logger:
    """单例 Logger 类"""
    _instance: Mapping[str, logging.Logger] = {}

    def __new__(cls, *args, **kwargs):
        name      = kwargs.get('name', 'easy_pyoc')
        formatter = kwargs.get('formatter', '[%(asctime)s] %(levelname)7s : %(message)s')

        if name not in cls._instance:
            cls._instance[name] = logging.getLogger(name)
            cls._instance[name].setLevel(logging.INFO)

            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(formatter))

            cls._instance[name].addHandler(handler)
        return cls._instance[name]
