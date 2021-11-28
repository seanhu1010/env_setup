#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File:    storage.py
"""
存储预置库
"""

import json

from envlib.rest import Rest

from resources.data import STORAGE_CONFIG


__all__ = ['Storage', ]


class Storage(object):
    """Storage存储类"""

    # TODO: 目前仅支持y3000
    rest_3000 = Rest(host="http://{}:9003".format(STORAGE_CONFIG.get('cm_ip')))  # y3000私有接口

    def __init__(self):
        """初始化Storage类，包括连接vms,cms的Rest和y3000的Ssh"""
        pass

    @classmethod
    def query_y3000_bucket_storage_quota_via_bucket_name(cls, bucket_name):
        """传入存储空间目录名，查询当前配额空间

        Args:
            bucket_name(str): 存储空间目录名

        Returns:
            int: 配额空间

        """
        url = "/api/demo@post"
        res = cls.rest_3000.send(url, json={"iaas_bucket_name": bucket_name})
        assert res.status_code in [200, 201, 202,
                                   502], f"状态码校验失败，期望值为200或201或202，实际值为{res.status_code}，接口响应为{res.content}"
        return json.loads(res.content).get('iaas_bucket_storage_quota')


if __name__ == '__main__':
    pass
