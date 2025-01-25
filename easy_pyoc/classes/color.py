#!/usr/bin/env python
# -*- coding: utf-8 -*-

class AnsiColor:
    """控制台 ASCII 颜色类"""

    FORE_BLACK   = '\033[30m'
    FORE_RED     = '\033[31m'
    FORE_GREEN   = '\033[32m'
    FORE_YELLOW  = '\033[33m'
    FORE_BLUE    = '\033[34m'
    FORE_MAGENTA = '\033[35m'
    FORE_CYAN    = '\033[36m'
    FORE_WHITE   = '\033[37m'
    FORE_RESET   = '\033[39m'

    BACK_BLACK   = '\033[40m'
    BACK_RED     = '\033[41m'
    BACK_GREEN   = '\033[42m'
    BACK_YELLOW  = '\033[43m'
    BACK_BLUE    = '\033[44m'
    BACK_MAGENTA = '\033[45m'
    BACK_CYAN    = '\033[46m'
    BACK_WHITE   = '\033[47m'
    BACK_RESET   = '\033[49m'

    RESET_ALL    = '\033[00m'
    BOLD         = '\033[01m'
    DIM          = '\033[02m'
    NORMAL       = '\033[22m'
