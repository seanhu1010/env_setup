#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    ctx.py
# @Time:    2021/06/18
"""
    上下文管理
    
"""

from envlib.env.globals import ctx_stack
from envlib.env.helpers import ExtractingMixin
from envlib.env.helpers import HelpersMixin

# a singleton sentinel value for parameter defaults
_sentinel = object()


class AppCtxGlobals(object):
    """A plain object. Used as a namespace for storing data during an
    application context.

    Creating an app context automatically creates this object, which is
    made available as the :data:`g` proxy.

    .. describe:: 'key' in g

        Check whether an attribute is present.

    .. describe:: iter(g)

        Return an iterator over the attribute names.

    """

    def get(self, name, default=None):
        """Get an attribute by name, or a default value. Like
        :meth:`dict.get`.

        :param name: Name of attribute to get.
        :param default: Value to return if the attribute is not present.

        """
        return self.__dict__.get(name, default)

    def pop(self, name, default=_sentinel):
        """Get and remove an attribute by name. Like :meth:`dict.pop`.

        :param name: Name of attribute to pop.
        :param default: Value to return if the attribute is not present,
            instead of raise a ``KeyError``.

        """
        if default is _sentinel:
            return self.__dict__.pop(name)
        else:
            return self.__dict__.pop(name, default)

    def setdefault(self, name, default=None):
        """Get the value of an attribute if it is present, otherwise
        set and return a default value. Like :meth:`dict.setdefault`.

        :param name: Name of attribute to get.
        :param: default: Value to set and return if the attribute is not
            present.

        """
        return self.__dict__.setdefault(name, default)

    def __contains__(self, item):
        return item in self.__dict__

    def getk(self, item):
        return TagCtxGlobals(self.__dict__.get(item))

    def __iter__(self):
        return iter(self.__dict__)


class TagCtxGlobals(HelpersMixin, ExtractingMixin, object):
    def __init__(self, val):
        self.val = val

    def _builder(self, val):
        return TagCtxGlobals(val)

    def __repr__(self):
        return f"<{object.__repr__(self)} of {self.val}>"


class EnvContext(object):
    def __init__(self, app, g=None):
        self.app = app
        if g is None:
            g = AppCtxGlobals()
        self.g = g

    def copy(self):
        """Creates a copy of this request context with the same request object.
        This can be used to move a request context to a different greenlet.
        Because the actual request object is the same this cannot be used to
        move a request context to a different thread unless access to the
        request object is locked.

        .. versionadded:: 0.10

        .. versionchanged:: 1.1
           The current session object is used instead of reloading the original
           data. This prevents `flask.session` pointing to an out-of-date object.
        """
        return self.__class__(
            self.app,
            g=self.g
        )

    def push(self):
        """绑定Env实例及其运行环境g"""
        if ctx_stack.top is not None:
            if self.app.debug is True and ctx_stack.top.app is self.app:
                pass
            else:
                ctx_stack.push(self)
        else:
            ctx_stack.push(self)

    def pop(self):
        if not self.app.debug:
            ctx_stack.pop()

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        # do not pop the request stack if we are in debug mode and an
        # exception happened.  This will allow the debugger to still
        # access the request object in the interactive shell.  Furthermore
        # the context can be force kept alive for the test client.
        # See flask.testing for how this works.
        if not (tb is None or not self.app.debug):
            self.pop()


if __name__ == '__main__':
    pass
