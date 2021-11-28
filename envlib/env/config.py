#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    config.py
# @Time:    2021/06/23


class ConfigAttribute(object):
    """Makes an attribute forward to the config"""

    def __init__(self, name):
        self.__name__ = name

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.config[self.__name__]

    def __set__(self, obj, value):
        obj.config[self.__name__] = value


class Config(dict):
    """Works exactly like a dict but provides ways to fill it from files
    or special dictionaries.  There are two common patterns to populate the
    config.

    Either you can fill the config from a config file::

        app.config.update(DEBUG=True)
    """

    def __init__(self, defaults=None):
        dict.__init__(self, defaults or {})

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, dict.__repr__(self))


if __name__ == '__main__':
    pass
