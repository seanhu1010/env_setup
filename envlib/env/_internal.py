#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    _internal.py
# @Time:    2021/06/11
"""
    envlib._internal
    ~~~~~~~~~~~~~~~~~~

    This module provides internally used helpers and constants.

"""


class _Missing(object):
    def __repr__(self):
        return "no value"

    def __reduce__(self):
        return "_missing"


_missing = _Missing()


def _proxy_repr(cls):
    def proxy_repr(self):
        return '%s(%s)' % (self.__class__.__name__, cls.__repr__(self))
    return proxy_repr


if __name__ == '__main__':
    pass
