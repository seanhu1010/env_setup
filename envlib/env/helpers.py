#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    helpers.py
# @Time:    2021/06/11
"""
一此实用的工具Mixin类
"""
import collections
import inspect
import re
from pprint import pprint

from envlib.env.envlogging import logger


class HelpersMixin(object):
    """Helpers mixin.  For internal use only.

    参考assertpy.helpers
    为类 mixin一些检查方法
    """

    def _check_dict_like(self, d, check_keys=True, check_values=True, check_getitem=True, name='val',
                         return_as_bool=False):
        """Helper to check if given val has various dict-like attributes."""
        if not isinstance(d, collections.Iterable):
            if return_as_bool:
                return False
            else:
                raise TypeError('%s <%s> is not dict-like: not iterable' % (name, type(d).__name__))
        if check_keys:
            if not hasattr(d, 'keys') or not callable(getattr(d, 'keys')):
                if return_as_bool:
                    return False
                else:
                    raise TypeError('%s <%s> is not dict-like: missing keys()' % (name, type(d).__name__))
        if check_values:
            if not hasattr(d, 'values') or not callable(getattr(d, 'values')):
                if return_as_bool:
                    return False
                else:
                    raise TypeError('%s <%s> is not dict-like: missing values()' % (name, type(d).__name__))
        if check_getitem:
            if not hasattr(d, '__getitem__'):
                if return_as_bool:
                    return False
                else:
                    raise TypeError('%s <%s> is not dict-like: missing [] accessor' % (name, type(d).__name__))
        if return_as_bool:
            return True

    def _check_iterable(self, l, check_getitem=True, name='val'):
        """Helper to check if given val has various iterable attributes."""
        if not isinstance(l, collections.Iterable):
            raise TypeError('%s <%s> is not iterable' % (name, type(l).__name__))
        if check_getitem:
            if not hasattr(l, '__getitem__'):
                raise TypeError('%s <%s> does not have [] accessor' % (name, type(l).__name__))


class ExtractingMixin(object):
    """Collection flattening mixin

    参考assertpy.extracting
    当前接口返回的数据json千奇百怪, 对json的处理通常会使用字典或列表的一些操作, 并结合一些
    map/reduce/lambda等来提取，再作为功能或端到端自动化接口的入参,重复单调！
    这里借鉴assertpy的思路，来针对性地处理保存在 class: ``TagCtxGlobals`` 中复杂的json,
    如嵌套字典和字典列表等，提供了一个统一的 ``extracting()`` 方法

    Tip:
        假设示例均保存在当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下

    **extracting**

    1) ``extracting()`` 的值为非可迭代对象，非列表、元组、字符串、字典等，直接返回::

        users = { 'item': not_Iterable_obj }

        g.getk('users').extracting('item')

        Returns: not_Iterable_obj

    2) ``extracting()`` 值是字符串，直接返回::

        users = { 'item': str }

        g.getk('users').extracting('item')

        Returns: str

    3)如果 ``extracting()`` 值是字典，查names，递归查找后返回list::

            json_nested_dict = {
                "name": "208_1.1.1.1_SDK",
                "ape_id": "50010000001181000003",
                "org_name": "illegal_system",
                "org_index": "50010000002160000006",
                "channel_list": [
                {
                  "ape_id": "50010000001311000021",
                  "name": "208_1.1.1.1_SDK_通道_1"
                },
                {
                  "ape_id": "50010000001311000022",
                  "name": "208_1.1.1.1_SDK_通道_2"
                }
                ]
            }

            g.getk('json_nested_dict').extracting('ape_id')

            Returns: ["50010000001181000003", "208_1.1.1.1_SDK_通道_1", "208_1.1.1.1_SDK_通道_2"]

    Warning:
        关键字{names}数量 不等于 提取值{extracted}数量, 会有 `critical` 提醒

    4)如果 ``extracting()`` 值是单层元组，直接返回::

        users = { 'item': (a,b,c) }

        g.getk('users').extracting('item')

        Returns: (a,b,c)

    5)如果 ``extracting()`` 值是list of dicts [{},{},{}],将批量提取::

        users = [
            {'user': 'Alice', 'age': 36, 'active': True},
            {'user': 'Bob', 'age': 40, 'active': False},
            {'user': 'Charlie', 'age': 13, 'active': True}
        ]

        g.getk('users').extracting('user')

        Returns: ['Alice', 'Bob', 'Charlie']

        g.getk('users').extracting('user','age')

        Returns: [('Alice',36), ('Bob',40), ('Charlie',13)]

    **Filtering**

    Warning:

        *filter* 仅在所提取对象是 形如 ``list of dicts`` 生效

    ``extracting()`` 方法可以接受 *filter* 来过滤并提取*filter*的条件为true时的items

    For example::

        users = [
            {'user': 'Alice', 'age': 36, 'active': True},
            {'user': 'Bob', 'age': 40, 'active': False},
            {'user': 'Charlie', 'age': 13, 'active': True}
        ]

        # filter the active users
        g.getk('users').extracting('user', filter='active')

    *filter* 也可以接受一个/一组 *dict-like* 对象, 过滤并提取*filter*与相应的key-value pairs相等的items::

        g.getk('users').extracting('user', filter={'active': False})
        g.getk('users').extracting('user', filter={'age': 36, 'active': True})

    *filter* 还可以接受function (including an in-line ``lambda``) that accepts as its single
    argument each item in the collection, and the extracted items are kept if the function
    evaluates to ``True`` ::

        g.getk('users').extracting('user', filter=lambda x: x['age'] > 20)

    """

    def extracting(self, *names, **kwargs):
        """提取元素，类似assertpy，支持元素及filter

        :author: sean
        :created: 2021/2/3 20:31

        Args:
            *names: the attribute to be extracted (or property or zero-arg method)
            **kwargs: see below

        Keyword Args:
            filter: extract only those items where filter is truthy

        Tip:
            假设示例均保存在 ``common`` 的tag下

        Example:
            1) ``extracting()`` 的值为非可迭代对象（如非列表、非元组、非字符串、非字典），或字符串，或单层元组，直接返回::

                g.getk('users').extracting('item')

            2)如果 ``extracting()`` 值是字典，查names，递归查找后返回list::

                json_nested_dict = {
                    "name": "208_1.1.1.1_SDK",
                    "ape_id": "50010000001181000003",
                    "org_name": "illegal_system",
                    "org_index": "50010000002160000006",
                    "channel_list": [
                    {
                      "ape_id": "50010000001311000021",
                      "name": "208_1.1.1.1_SDK_通道_1"
                    },
                    {
                      "ape_id": "50010000001311000022",
                      "name": "208_1.1.1.1_SDK_通道_2"
                    }
                    ]
                }

                g.getk('json_nested_dict').extracting('ape_id')

                Returns: ["50010000001181000003", "208_1.1.1.1_SDK_通道_1", "208_1.1.1.1_SDK_通道_2"]

            关键字{names}数量 不等于 提取值{extracted}数量, 会有 ``critical`` 提醒

            3)如果 ``extracting()`` 值是list of dicts ``[{}, {}, {}]`` ,将批量提取::

                users = [
                    {'user': 'Alice', 'age': 36, 'active': True},
                    {'user': 'Bob', 'age': 40, 'active': False},
                    {'user': 'Charlie', 'age': 13, 'active': True}
                ]

                g.getk('users').extracting('user')

                g.getk('users').extracting('user','age')

            Filter::

                g.getk('users').extracting('user', filter={'active': False})

        Returns:
            a list of values
        """
        if not isinstance(self.val, collections.Iterable):  # 值为非可迭代对象，非列表、元组、字符串、字典等，直接返回
            logger.warning(f'{self.val} is not Iterable, 将直接返回{self.val}')
            return self.val
        if isinstance(self.val, str):
            logger.debug(
                f'{self.val} is string, 将直接返回{self.val}')  # 是字符串，直接返回
            return self.val
        if len(names) == 0:
            raise ValueError('one or more name args must be given！！')

        def _extract(x, name):
            if self._check_dict_like(x, check_values=False, return_as_bool=True):
                if name in x:
                    return x[name]
                else:
                    raise ValueError('item keys %s did not contain key <%s>' % (list(x.keys()), name))
            elif isinstance(x, collections.Iterable):
                self._check_iterable(x, name='item')
                return x[name]
            elif hasattr(x, name):
                attr = getattr(x, name)
                if callable(attr):
                    try:
                        return attr()
                    except TypeError:
                        raise ValueError('val method <%s()> exists, but is not zero-arg method' % name)
                else:
                    return attr
            else:
                raise ValueError('val does not have property or zero-arg method <%s>' % name)

        def _filter(x):
            if 'filter' in kwargs:
                if isinstance(kwargs['filter'], str):
                    return bool(_extract(x, kwargs['filter']))
                elif self._check_dict_like(kwargs['filter'], check_values=False, return_as_bool=True):
                    for k in kwargs['filter']:
                        if isinstance(k, str):
                            if _extract(x, k) != kwargs['filter'][k]:
                                return False
                    return True
                elif callable(kwargs['filter']):
                    return kwargs['filter'](x)
                return False
            return True

        def _get_nested_dict_value(d, names):
            for key in names:
                try:
                    yield d[key]
                except:
                    pass
                for k, v in d.items():
                    if isinstance(v, dict):
                        yield from _get_nested_dict_value(v, key)
                        try:
                            yield v[k]
                        except:
                            pass

        if isinstance(self.val, dict):  # 如果是字典，查names，递归查找后返回list
            logger.debug(f'{self.val} is dict or nested dict,将递归提取{names}')
            extracted = list(_get_nested_dict_value(self.val, names))
            if len(names) != len(extracted):  # bug，无法识别key1对应2个值， key2对应0个值的情况
                logger.critical(f'提取数据不符合预期, 关键字{names}数量 不等于 提取值{extracted}数量，请谨慎处理！')
            logger.info(f'所提取的值 {extracted} 只有一个，将直接提取为 {extracted[0]} !!')
            extracted = extracted[0]
            return extracted
        elif isinstance(self.val, (tuple,)) and len(self.val) == 1:  # 单层元组，直接返回
            logger.debug(f'{self.val} is 单层元组,将直接返回')
            return self.val
        else:  # 如果是list of dicts [{},{},{}] 或 list of list[[],[],[]]，将批量提取
            logger.debug(f'{self.val} is list of dicts OR list of list, 将批量提取{names}')
            extracted = []
            for i in self.val:
                if _filter(i):
                    items = [_extract(i, name) for name in names]
                    # extracted.append(tuple(items) if len(items) > 1 else items[0])
                    extracted.append(items[0]) if len(items) == 1 else extracted.append(tuple(items))
            if len(extracted) == 0:
                logger.info(f'未找到符合条件 {names, kwargs}的值 !!')
                return None
            if len(extracted) == 1:
                logger.info(f'所提取的值 {extracted} 只有一个，将直接提取为 {extracted[0]} !!')
                extracted = extracted[0]
            return self._builder(extracted).val


class GetKeysMixin(object):
    """获取类的key列表"""

    @classmethod
    def get_keys(cls):
        func_list = [func for func in dir(cls) if not func.startswith('__')]
        kv = {}
        for func in func_list:
            try:
                key = re.search(r'bind_to_g\(key=\'(.*?)\'', inspect.getsource(getattr(cls, func))).group(1)
                doc = inspect.getdoc(getattr(cls, func))
                kv[key] = f'函数名: {func}, 含义: {doc}'
            except AttributeError:
                pass
        pprint(kv)


if __name__ == '__main__':
    pass
