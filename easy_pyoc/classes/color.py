#!/usr/bin/env python
# -*- coding: utf-8 -*-

class AnsiColor:
    """控制台 ASCII 颜色类"""

    FORE_BLACK   = 30
    FORE_RED     = 31
    FORE_GREEN   = 32
    FORE_YELLOW  = 33
    FORE_BLUE    = 34
    FORE_MAGENTA = 35
    FORE_CYAN    = 36
    FORE_WHITE   = 37
    FORE_RESET   = 39

    BACK_BLACK   = 40
    BACK_RED     = 41
    BACK_GREEN   = 42
    BACK_YELLOW  = 43
    BACK_BLUE    = 44
    BACK_MAGENTA = 45
    BACK_CYAN    = 46
    BACK_WHITE   = 47
    BACK_RESET   = 49

    def __init__(self, fore_color: int | None = None, back_color: int | None = None, bold: bool = False):
        if fore_color is None and back_color is None:
            raise ValueError('前景色和背景色不能同时为空')

        self.fore_color = fore_color
        self.back_color = back_color
        self.bold = bold

    def __str__(self):
        color = '\033['

        if self.fore_color:
            color += str(self.fore_color)
        if self.back_color:
            color += ';' + str(self.back_color)

        color += ';1' if self.bold else ';0'
        color +='m'

        return color
