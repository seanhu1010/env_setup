#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    envlogging.py
# @Time:    2021/06/18
"""
统一logging模块
    
"""

import logging

import allure
from loguru import logger


class AllureLogger(logging.Handler):
    """allure日志模块

    引自 https://stackoverflow.com/questions/65380164/pytest-best-practices-for-logging-using-allure
    """
    def emit(self, record):
        if logging.DEBUG < record.levelno:  # 只打印DEBUG以上级别的日志, 并在allure报告中形成单独步骤
            with allure.step(f'LOG ({record.levelname}): {record.getMessage()}'):
                pass  # No need for content, since the step context is doing the work.


logger.add(AllureLogger(), format="{time} - {level} - {message}")


if __name__ == '__main__':
    pass
