#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    globals.py
# @Time:    2021/06/18
"""
    定义全局变量代理到当前激活的上下文环境

    ``ctx_stack``: Env运行的堆栈

    ``current_app``: 代理到当前运行的Env实例

    ``g``: 代理到当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例，支持getk来extracting快捷提取所需字段, 详见ExtractingMixin类说明

    ``env_pools``: 基于import实现单例Rest实例池
"""

from functools import partial

from envlib.env.local import LocalStack
from envlib.env.local import LocalProxy


def _lookup_app_object(name):
    top = ctx_stack.top
    if top is None:
        raise RuntimeError("Working outside of ctx context.")
    return getattr(top, name)


def _find_app():
    top = ctx_stack.top
    if top is None:
        raise RuntimeError("Working outside of ctx context.")
    return top.app


# Env运行的堆栈
ctx_stack = LocalStack()

# 代理到当前运行的Env实例
current_app = LocalProxy(_find_app)

# 代理到当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例，支持getk来extracting快捷提取所需字段
# 详见ExtractingMixin类说明
g = LocalProxy(partial(_lookup_app_object, "g"))

# 基于import实现单例Rest实例池
env_pools = {}  # import单例，全局变量


if __name__ == '__main__':
    pass
