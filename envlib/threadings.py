#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
多线程
"""

import threading
from envlib.env.envlogging import logger

__all__ = ['MyThread', ]


class MyThread(threading.Thread):
    """多线程"""

    def __init__(self, name, function, **kwargs):
        """多线程实例初始化参数

        Args:
            name(str): 线程名称
            function(function): 函数
            **kwargs: 函数参数
        """
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.function = function
        self.kwargs = kwargs

    def run(self):
        logger.info("开始线程：" + self.name)
        self.function(**self.kwargs)
        logger.info("退出线程：" + self.name)
