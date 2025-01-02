#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ..utils.object_util import ObjectUtil


class Magic(object):
    """魔法类，简单实现了 __str__、__repr__、__call__ 方法"""
    _str_exclude = {}
    _repr_exclude = {}
    _call_exclude = {}
    _str_include = {}
    _repr_include = {}
    _call_include = {}

    def __str__(self) -> str:
        return ObjectUtil.repr(self, self._str_exclude, self._str_include)

    def __repr__(self) -> str:
        return ObjectUtil.repr(self, self._repr_exclude, self._repr_include)

    def __call__(self) -> dict:
        return ObjectUtil.vars(self, self._call_exclude, self._call_include)
