#!/usr/bin/env python
# -*- coding: utf-8 -*-
from easy_pyoc import NetworkUtil


def test_send_WOL():
    NetworkUtil.send_WOL('001122334455')
