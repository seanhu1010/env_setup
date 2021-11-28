#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    _compat.py
# @Time:    2021/06/11
"""

    envlib._compat
    ~~~~~~~~~~~~~~

    py2/py3兼容模块，代码段引自flask
"""

from functools import partial
import sys

PY2 = sys.version_info[0] == 2
_identity = lambda x: x

try:  # Python 2
    text_type = unicode
    string_types = (str, unicode)
    integer_types = (int, long)
except NameError:  # Python 3
    text_type = str
    string_types = (str,)
    integer_types = (int,)

if PY2:

    iterkeys = lambda d, *args, **kwargs: d.iterkeys(*args, **kwargs)
    itervalues = lambda d, *args, **kwargs: d.itervalues(*args, **kwargs)
    iteritems = lambda d, *args, **kwargs: d.iteritems(*args, **kwargs)
    iterlists = lambda d, *args, **kwargs: d.iterlists(*args, **kwargs)


    def implements_iterator(cls):
        cls.next = cls.__next__
        del cls.__next__
        return cls


    def implements_bool(cls):
        cls.__nonzero__ = cls.__bool__
        del cls.__bool__
        return cls
else:

    iterkeys = lambda d, *args, **kwargs: iter(d.keys(*args, **kwargs))
    itervalues = lambda d, *args, **kwargs: iter(d.values(*args, **kwargs))
    iteritems = lambda d, *args, **kwargs: iter(d.items(*args, **kwargs))
    iterlists = lambda d, *args, **kwargs: iter(d.lists(*args, **kwargs))
    implements_iterator = _identity
    implements_bool = _identity


@implements_iterator
class ClosingIterator(object):
    """The WSGI specification requires that all middlewares and gateways
    respect the `close` callback of the iterable returned by the application.
    Because it is useful to add another close action to a returned iterable
    and adding a custom iterable is a boring task this class can be used for
    that::

        return ClosingIterator(app(environ, start_response), [cleanup_session,
                                                              cleanup_locals])

    If there is just one close function it can be passed instead of the list.

    A closing iterator is not needed if the application uses response objects
    and finishes the processing if the response is started::

        try:
            return response(environ, start_response)
        finally:
            cleanup_session()
            cleanup_locals()
    """

    def __init__(self, iterable, callbacks=None):
        iterator = iter(iterable)
        self._next = partial(next, iterator)
        if callbacks is None:
            callbacks = []
        elif callable(callbacks):
            callbacks = [callbacks]
        else:
            callbacks = list(callbacks)
        iterable_close = getattr(iterable, "close", None)
        if iterable_close:
            callbacks.insert(0, iterable_close)
        self._callbacks = callbacks

    def __iter__(self):
        return self

    def __next__(self):
        return self._next()

    def close(self):
        for callback in self._callbacks:
            callback()


if __name__ == '__main__':
    pass
