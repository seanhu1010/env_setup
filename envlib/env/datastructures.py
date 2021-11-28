#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    datastructures.py
# @Time:    2021/06/11
"""
    werkzeug.datastructures
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module provides mixins and classes with an immutable interface.
    一些扩展的数据结构，如MultiDict, ImmutableDict等

    :copyright: 2007 Pallets
    :license: BSD-3-Clause
"""

from copy import deepcopy

from envlib.env import exceptions
from envlib.env._compat import iteritems
from envlib.env._compat import iterkeys
from envlib.env._compat import iterlists
from envlib.env._compat import itervalues
from envlib.env._compat import PY2
from envlib.env._internal import _missing
from envlib.env._internal import _proxy_repr


def native_itermethods(names):
    if not PY2:
        return lambda x: x

    def setviewmethod(cls, name):
        viewmethod_name = "view%s" % name
        repr_name = "view_%s" % name

        def viewmethod(self, *a, **kw):
            return ViewItems(self, name, repr_name, *a, **kw)

        viewmethod.__name__ = viewmethod_name
        viewmethod.__doc__ = "`%s()` object providing a view on %s" % (
            viewmethod_name,
            name,
        )
        setattr(cls, viewmethod_name, viewmethod)

    def setitermethod(cls, name):
        itermethod = getattr(cls, name)
        setattr(cls, "iter%s" % name, itermethod)

        def listmethod(self, *a, **kw):
            return list(itermethod(self, *a, **kw))

        listmethod.__name__ = name
        listmethod.__doc__ = "Like :py:meth:`iter%s`, but returns a list." % name
        setattr(cls, name, listmethod)

    def wrap(cls):
        for name in names:
            setitermethod(cls, name)
            setviewmethod(cls, name)
        return cls

    return wrap


def iter_multi_items(mapping):
    """Iterates over the items of a mapping yielding keys and values
    without dropping any from more complex structures.
    """
    if isinstance(mapping, MultiDict):
        for item in iteritems(mapping, multi=True):
            yield item
    elif isinstance(mapping, dict):
        for key, value in iteritems(mapping):
            if isinstance(value, (tuple, list)):
                for v in value:
                    yield key, v
            else:
                yield key, value
    else:
        for item in mapping:
            yield item


def is_immutable(self):
    raise TypeError('%r objects are immutable' % self.__class__.__name__)


class ViewItems(object):
    def __init__(self, multi_dict, method, repr_name, *a, **kw):
        self.__multi_dict = multi_dict
        self.__method = method
        self.__repr_name = repr_name
        self.__a = a
        self.__kw = kw

    def __get_items(self):
        return getattr(self.__multi_dict, self.__method)(*self.__a, **self.__kw)

    def __repr__(self):
        return "%s(%r)" % (self.__repr_name, list(self.__get_items()))

    def __iter__(self):
        return iter(self.__get_items())


class TypeConversionDict(dict):
    """Works like a regular dict but the :meth:`get` method can perform
    type conversions.  :class:`MultiDict` and :class:`CombinedMultiDict`
    are subclasses of this class and provide the same feature.

    .. versionadded:: 0.5
    """

    def get(self, key, default=None, type=None):
        """Return the default value if the requested data doesn't exist.
        If `type` is provided and is a callable it should convert the value,
        return it or raise a :exc:`ValueError` if that is not possible.  In
        this case the function will return the default as if the value was not
        found:

        >>> d = TypeConversionDict(foo='42', bar='blub')
        >>> d.get('foo', type=int)
        42
        >>> d.get('bar', -1, type=int)
        -1

        :param key: The key to be looked up.
        :param default: The default value to be returned if the key can't
                        be looked up.  If not further specified `None` is
                        returned.
        :param type: A callable that is used to cast the value in the
                     :class:`MultiDict`.  If a :exc:`ValueError` is raised
                     by this callable the default value is returned.
        """
        try:
            rv = self[key]
        except KeyError:
            return default
        if type is not None:
            try:
                rv = type(rv)
            except ValueError:
                rv = default
        return rv


@native_itermethods(["keys", "values", "items", "lists", "listvalues"])
class MultiDict(TypeConversionDict):
    """A :class:`MultiDict` is a dictionary subclass customized to deal with
    multiple values for the same key which is for example used by the parsing
    functions in the wrappers.  This is necessary because some HTML form
    elements pass multiple values for the same key.

    :class:`MultiDict` implements all standard dictionary methods.
    Internally, it saves all values for a key as a list, but the standard dict
    access methods will only return the first value for a key. If you want to
    gain access to the other values, too, you have to use the `list` methods as
    explained below.

    Basic Usage:

    >>> d = MultiDict([('a', 'b'), ('a', 'c')])
    >>> d
    MultiDict([('a', 'b'), ('a', 'c')])
    >>> d['a']
    'b'
    >>> d.getlist('a')
    ['b', 'c']
    >>> 'a' in d
    True

    It behaves like a normal dict thus all dict functions will only return the
    first value when multiple values for one key are found.

    From Werkzeug 0.3 onwards, the `KeyError` raised by this class is also a
    subclass of the :exc:`~exceptions.BadRequest` HTTP exception and will
    render a page for a ``400 BAD REQUEST`` if caught in a catch-all for HTTP
    exceptions.

    A :class:`MultiDict` can be constructed from an iterable of
    ``(key, value)`` tuples, a dict, a :class:`MultiDict` or from Werkzeug 0.2
    onwards some keyword parameters.

    :param mapping: the initial value for the :class:`MultiDict`.  Either a
                    regular dict, an iterable of ``(key, value)`` tuples
                    or `None`.
    """

    def __init__(self, mapping=None):
        if isinstance(mapping, MultiDict):
            dict.__init__(self, ((k, l[:]) for k, l in iterlists(mapping)))
        elif isinstance(mapping, dict):
            tmp = {}
            for key, value in iteritems(mapping):
                if isinstance(value, (tuple, list)):
                    if len(value) == 0:
                        continue
                    value = list(value)
                else:
                    value = [value]
                tmp[key] = value
            dict.__init__(self, tmp)
        else:
            tmp = {}
            for key, value in mapping or ():
                tmp.setdefault(key, []).append(value)
            dict.__init__(self, tmp)

    def __getstate__(self):
        return dict(self.lists())

    def __setstate__(self, value):
        dict.clear(self)
        dict.update(self, value)

    def __getitem__(self, key):
        """Return the first data value for this key;
        raises KeyError if not found.

        :param key: The key to be looked up.
        :raise KeyError: if the key does not exist.
        """

        if key in self:
            lst = dict.__getitem__(self, key)
            if len(lst) > 0:
                return lst[0]
        raise exceptions.BadRequestKeyError(key)

    def __setitem__(self, key, value):
        """Like :meth:`add` but removes an existing key first.

        :param key: the key for the value.
        :param value: the value to set.
        """
        dict.__setitem__(self, key, [value])

    def add(self, key, value):
        """Adds a new value for the key.

        .. versionadded:: 0.6

        :param key: the key for the value.
        :param value: the value to add.
        """
        dict.setdefault(self, key, []).append(value)

    def getlist(self, key, type=None):
        """Return the list of items for a given key. If that key is not in the
        `MultiDict`, the return value will be an empty list.  Just as `get`
        `getlist` accepts a `type` parameter.  All items will be converted
        with the callable defined there.

        :param key: The key to be looked up.
        :param type: A callable that is used to cast the value in the
                     :class:`MultiDict`.  If a :exc:`ValueError` is raised
                     by this callable the value will be removed from the list.
        :return: a :class:`list` of all the values for the key.
        """
        try:
            rv = dict.__getitem__(self, key)
        except KeyError:
            return []
        if type is None:
            return list(rv)
        result = []
        for item in rv:
            try:
                result.append(type(item))
            except ValueError:
                pass
        return result

    def setlist(self, key, new_list):
        """Remove the old values for a key and add new ones.  Note that the list
        you pass the values in will be shallow-copied before it is inserted in
        the dictionary.

        >>> d = MultiDict()
        >>> d.setlist('foo', ['1', '2'])
        >>> d['foo']
        '1'
        >>> d.getlist('foo')
        ['1', '2']

        :param key: The key for which the values are set.
        :param new_list: An iterable with the new values for the key.  Old values
                         are removed first.
        """
        dict.__setitem__(self, key, list(new_list))

    def setdefault(self, key, default=None):
        """Returns the value for the key if it is in the dict, otherwise it
        returns `default` and sets that value for `key`.

        :param key: The key to be looked up.
        :param default: The default value to be returned if the key is not
                        in the dict.  If not further specified it's `None`.
        """
        if key not in self:
            self[key] = default
        else:
            default = self[key]
        return default

    def setlistdefault(self, key, default_list=None):
        """Like `setdefault` but sets multiple values.  The list returned
        is not a copy, but the list that is actually used internally.  This
        means that you can put new values into the dict by appending items
        to the list:

        >>> d = MultiDict({"foo": 1})
        >>> d.setlistdefault("foo").extend([2, 3])
        >>> d.getlist("foo")
        [1, 2, 3]

        :param key: The key to be looked up.
        :param default_list: An iterable of default values.  It is either copied
                             (in case it was a list) or converted into a list
                             before returned.
        :return: a :class:`list`
        """
        if key not in self:
            default_list = list(default_list or ())
            dict.__setitem__(self, key, default_list)
        else:
            default_list = dict.__getitem__(self, key)
        return default_list

    def items(self, multi=False):
        """Return an iterator of ``(key, value)`` pairs.

        :param multi: If set to `True` the iterator returned will have a pair
                      for each value of each key.  Otherwise it will only
                      contain pairs for the first value of each key.
        """

        for key, values in iteritems(dict, self):
            if multi:
                for value in values:
                    yield key, value
            else:
                yield key, values[0]

    def lists(self):
        """Return a iterator of ``(key, values)`` pairs, where values is the list
        of all values associated with the key."""

        for key, values in iteritems(dict, self):
            yield key, list(values)

    def keys(self):
        return iterkeys(dict, self)

    __iter__ = keys

    def values(self):
        """Returns an iterator of the first value on every key's value list."""
        for values in itervalues(dict, self):
            yield values[0]

    def listvalues(self):
        """Return an iterator of all values associated with a key.  Zipping
        :meth:`keys` and this is the same as calling :meth:`lists`:

        >>> d = MultiDict({"foo": [1, 2, 3]})
        >>> zip(d.keys(), d.listvalues()) == d.lists()
        True
        """

        return itervalues(dict, self)

    def copy(self):
        """Return a shallow copy of this object."""
        return self.__class__(self)

    def deepcopy(self, memo=None):
        """Return a deep copy of this object."""
        return self.__class__(deepcopy(self.to_dict(flat=False), memo))

    def to_dict(self, flat=True):
        """Return the contents as regular dict.  If `flat` is `True` the
        returned dict will only have the first item present, if `flat` is
        `False` all values will be returned as lists.

        :param flat: If set to `False` the dict returned will have lists
                     with all the values in it.  Otherwise it will only
                     contain the first value for each key.
        :return: a :class:`dict`
        """
        if flat:
            return dict(iteritems(self))
        return dict(self.lists())

    def update(self, other_dict):
        """update() extends rather than replaces existing key lists:

        >>> a = MultiDict({'x': 1})
        >>> b = MultiDict({'x': 2, 'y': 3})
        >>> a.update(b)
        >>> a
        MultiDict([('y', 3), ('x', 1), ('x', 2)])

        If the value list for a key in ``other_dict`` is empty, no new values
        will be added to the dict and the key will not be created:

        >>> x = {'empty_list': []}
        >>> y = MultiDict()
        >>> y.update(x)
        >>> y
        MultiDict([])
        """
        for key, value in iter_multi_items(other_dict):
            MultiDict.add(self, key, value)

    def pop(self, key, default=_missing):
        """Pop the first item for a list on the dict.  Afterwards the
        key is removed from the dict, so additional values are discarded:

        >>> d = MultiDict({"foo": [1, 2, 3]})
        >>> d.pop("foo")
        1
        >>> "foo" in d
        False

        :param key: the key to pop.
        :param default: if provided the value to return if the key was
                        not in the dictionary.
        """
        try:
            lst = dict.pop(self, key)

            if len(lst) == 0:
                raise exceptions.BadRequestKeyError(key)

            return lst[0]
        except KeyError:
            if default is not _missing:
                return default
            raise exceptions.BadRequestKeyError(key)

    def popitem(self):
        """Pop an item from the dict."""
        try:
            item = dict.popitem(self)

            if len(item[1]) == 0:
                raise exceptions.BadRequestKeyError(item)

            return (item[0], item[1][0])
        except KeyError as e:
            raise exceptions.BadRequestKeyError(e.args[0])

    def poplist(self, key):
        """Pop the list for a key from the dict.  If the key is not in the dict
        an empty list is returned.

        .. versionchanged:: 0.5
           If the key does no longer exist a list is returned instead of
           raising an error.
        """
        return dict.pop(self, key, [])

    def popitemlist(self):
        """Pop a ``(key, list)`` tuple from the dict."""
        try:
            return dict.popitem(self)
        except KeyError as e:
            raise exceptions.BadRequestKeyError(e.args[0])

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        return self.deepcopy(memo=memo)

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, list(iteritems(self, multi=True)))


class ImmutableDictMixin(object):
    """Makes a :class:`dict` immutable.

    .. versionadded:: 0.5

    :private:
    """

    def __reduce_ex__(self, protocol):
        return type(self), (dict(self),)

    def setdefault(self, key, default=None):
        is_immutable(self)

    def update(self, *args, **kwargs):
        is_immutable(self)

    def pop(self, key, default=None):
        is_immutable(self)

    def popitem(self):
        is_immutable(self)

    def __setitem__(self, key, value):
        is_immutable(self)

    def __delitem__(self, key):
        is_immutable(self)

    def clear(self):
        is_immutable(self)


class ImmutableDict(ImmutableDictMixin, dict):
    """An immutable :class:`dict`.

    .. versionadded:: 0.5
    """

    __repr__ = _proxy_repr(dict)

    def copy(self):
        """Return a shallow mutable copy of this object.  Keep in mind that
        the standard library's :func:`copy` function is a no-op for this class
        like for any other python immutable type (eg: :class:`tuple`).
        """
        return dict(self)

    def __copy__(self):
        return self


if __name__ == '__main__':
    pass
