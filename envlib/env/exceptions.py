#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    exceptions.py
# @Time:    2021/06/11
"""
统一异常类定义
"""

import sys


class BadRequest(Exception):
    """*400* `Bad Request`

    Raise if the browser sends something to the application the application
    or server cannot handle.
    """

    code = 400
    description = (
        "The browser (or proxy) sent a request that this server could "
        "not understand."
    )

    def __init__(self, description=None, response=None):
        super(BadRequest, self).__init__()
        if description is not None:
            self.description = description
        self.response = response

    @classmethod
    def wrap(cls, exception, name=None):
        """Create an exception that is a subclass of the calling HTTP
        exception and the ``exception`` argument.

        The first argument to the class will be passed to the
        wrapped ``exception``, the rest to the HTTP exception. If
        ``e.args`` is not empty and ``e.show_exception`` is ``True``,
        the wrapped exception message is added to the HTTP error
        description.

        .. versionchanged:: 0.15.5
            The ``show_exception`` attribute controls whether the
            description includes the wrapped exception message.

        .. versionchanged:: 0.15.0
            The description includes the wrapped exception message.
        """

        class newcls(cls, exception):
            _description = cls.description
            show_exception = False

            def __init__(self, arg=None, *args, **kwargs):
                super(cls, self).__init__(*args, **kwargs)

                if arg is None:
                    exception.__init__(self)
                else:
                    exception.__init__(self, arg)

            @property
            def description(self):
                if self.show_exception:
                    return "{}\n{}: {}".format(
                        self._description, exception.__name__, exception.__str__(self)
                    )

                return self._description

            @description.setter
            def description(self, value):
                self._description = value

        newcls.__module__ = sys._getframe(1).f_globals.get("__name__")
        name = name or cls.__name__ + exception.__name__
        newcls.__name__ = newcls.__qualname__ = name
        return newcls


#: An exception that is used to signal both a :exc:`KeyError` and a
#: :exc:`BadRequest`. Used by many of the datastructures.
BadRequestKeyError = BadRequest.wrap(KeyError)


if __name__ == '__main__':
    pass
