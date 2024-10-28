#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest


def pytest_terminal_summary():
    import os
    if os.path.exists('temp'):
        os.remove('temp')
