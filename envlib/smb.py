#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @File:    smb.py
# @Modify Time      @Author     @Version    @Description
# ------------      -------     --------    -----------
# 2021/1/19 17:04   sean      1.0         None
"""
python smbprotocol SMB访问简单封装
"""

from smbclient import register_session, listdir, mkdir, rmdir, scandir, open_file, stat_volume, stat
from resources.data import SMB_SERVER, SMB_USERNAME, SMB_PASSWORD

__all__ = ['Smb', ]


class Smb(object):
    """SMB轻量连接与操作

    Attributes:
        register_session: SMB连接
        listdir: 路径浏览
        mkdir: 创建目录
        rmdir: 删除目录
        scandir: 路径浏览迭代器版本
        open_file: 类似os.open，
        stat_volume: Get stat of a volume
        stat: Get the status of a file
    """

    def __init__(self, server=SMB_SERVER, username=SMB_USERNAME, password=SMB_PASSWORD):
        register_session(server=server, username=username, password=password)
        self.register_session = register_session
        self.listdir = listdir
        self.mkdir = mkdir
        self.rmdir = rmdir
        self.scandir = scandir
        self.open_file = open_file
        self.stat_volume = stat_volume
        self.stat = stat


if __name__ == '__main__':
    pass
