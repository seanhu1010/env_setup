#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File:    cms.py
"""
    envlib.cms
    ~~~~~~~~~~

    Cms配置类预置库
"""

import json as json_tool
from copy import deepcopy

from envlib.env.envlogging import logger
from envlib.env.globals import current_app as app
from envlib.env.globals import g
from envlib.env.helpers import GetKeysMixin
from envlib.env_resources.preset_data import CMS_STORAGE_DIRECTORY, CMS_STORAGE_TYPE, cms_system_config_data, \
    cms_archive_config_data
from envlib.envsetup.storage import Storage
from envlib.util import get_last_ip_str
from resources.data import STORAGE_CONFIG

__all__ = ['Cms', ]


class Cms(GetKeysMixin):
    """Cms配置类"""

    def __init__(self):
        pass

    @classmethod
    def query_cms_platform_config_by_rest(cls, check=False):
        """查询cms，系统配置，平台配置

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='cms_platform_config', value=查询接口返回值，cms，系统配置，平台配置

        Args:
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值，cms，系统配置，平台配置

        """

        res = app.send_by_rest('/api/demo@get')
        app.bind_to_g(key='cms_platform_config', value=json_tool.loads(res.get('value')), lock=False)
        return json_tool.loads(res.get('value'))

    @classmethod
    def config_cms_platform_by_rest(cls, json=cms_system_config_data, check=False):
        """cms,系统配置,平台配置

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        _config_cms_platform_json = {
            "key": "viid",
            "value": json_tool.dumps(json)
        }

        res = app.send_by_rest('/api/demo@post', json=_config_cms_platform_json, check=check)
        cls.query_cms_platform_config_by_rest()
        return res

    @classmethod
    def query_cms_archive_config_by_rest(cls, check=False):
        """查询cms，系统配置，一人一档配置

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='cms_archive_config', value=查询接口返回值，cms，系统配置，一人一档配置

        Args:
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值，cms，系统配置，一人一档配置

        """

        res = app.send_by_rest('/api/demo@get', check=check)
        app.bind_to_g(key='cms_archive_config', value=res, lock=False)
        return res

    @classmethod
    def config_cms_archive_by_rest(cls, json=cms_archive_config_data, check=False):
        """cms,系统配置,一人一档

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@put', json=json, check=check)
        cls.query_cms_archive_config_by_rest()
        return res

    @classmethod
    def query_cms_cloud_storage_list_by_rest(cls, check=False):
        """cms-查询存储集群列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='cms_cloud_storage_list', value=查询接口返回值，cms-查询存储集群列表

        Args:
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值，cms-查询存储集群列表

        """

        res = app.send_by_rest('/api/demo@get', check=check)
        app.bind_to_g(key='cms_cloud_storage_list', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def add_cms_cloud_storage_by_rest_via_json(cls, json, check=False):
        """cms系统配置-云存储配置-添加存储集群

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', json=json, check=check)

        return res

    @classmethod
    def query_cms_cloud_storage_capacity_by_rest(cls, ip=STORAGE_CONFIG.get('cm_ip'), check=False):
        """

        Args:
            ip (str): ip
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@get', params=f'ip={ip}&port=9001&protocal=0',
                               check=check)

        return res.get('capacity')

    @classmethod
    def config_cms_cloud_storage_directory_by_rest_via_json(cls, json, check=False):
        """cms-存储集群存储目录配置

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', json=json, check=check)

        return res

    @classmethod
    def query_cms_cloud_storage_directory_by_rest_via_params(cls, params, check=False):
        """cms-查询存储集群存储目录配置

        Args:
            params (any): params数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@get', params=params, check=check)

        return res

    @classmethod
    def config_cms_cloud_storage_from_env_ini(cls):
        """cms,系统配置-云存储配置，根据env_ini中预设的存储集群，添加存储集群

        Returns:
            rest接口返回值

        """

        _storage_list = cls.query_cms_cloud_storage_list_by_rest().get('data')
        _exist_storage = [_storage for _storage in _storage_list if
                          _storage.get('storage_name') == STORAGE_CONFIG.get('cms_storage_name')]

        if _exist_storage:
            logger.warning(f"CMS已添加存储{STORAGE_CONFIG.get('cms_storage_name')},请勿重复添加！！")
        else:
            _storage_capacity = cls.query_cms_cloud_storage_capacity_by_rest(
                ip=STORAGE_CONFIG.get('cm_ip'))
            _set_storage_capacity = _storage_capacity if _storage_capacity else 30000
            _cms_storage_add_json = {
                "read_write_permission": 1,
                "storage_id": get_last_ip_str(STORAGE_CONFIG.get('cm_ip')),
                "storage_name": STORAGE_CONFIG.get('cms_storage_name'),
                "storage_ip": STORAGE_CONFIG.get('cm_ip'),
                "storage_port": 9001,
                "storage_protocal": 0,
                "storage_capacity": _set_storage_capacity,
                "storage_desc": None
            }
            cls.add_cms_cloud_storage_by_rest_via_json(json=_cms_storage_add_json)

        res = cls.query_cms_cloud_storage_list_by_rest()
        return res

    @classmethod
    def get_storage_id_via_cm_ip(cls, cm_ip=STORAGE_CONFIG.get('cm_ip')):
        """通过cm ip获取存储id

        Args:
            cm_ip (str): cm ip

        Returns:
            rest接口返回值, 存储id

        """
        cls.query_cms_cloud_storage_list_by_rest()
        _storage_id = g.getk('cms_cloud_storage_list').extracting('storage_id', filter={'storage_ip': cm_ip})
        if _storage_id is None:
            cls.config_cms_cloud_storage_from_env_ini()
            _storage_id = g.getk('cms_cloud_storage_list').extracting('storage_id', filter={'storage_ip': cm_ip})
        return _storage_id

    @classmethod
    def config_cms_cloud_storage_directory_from_env_ini(cls):
        """cms,系统配置-云存储配置，根据env_ini中预设的存储集群，进行目录配置

        Returns:
            rest接口返回值

        """

        _storage_id = cls.get_storage_id_via_cm_ip(cm_ip=STORAGE_CONFIG.get('cm_ip'))

        for _bucket_name in CMS_STORAGE_DIRECTORY:
            _quota = Storage.query_y3000_bucket_storage_quota_via_bucket_name(bucket_name=_bucket_name)
            _quota = 200 if _quota == 0 else _quota
            _bucket_id = CMS_STORAGE_TYPE.get(_bucket_name)
            _query_storage_set = cls.query_cms_cloud_storage_directory_by_rest_via_params(
                params=f'data_type={_bucket_id}&storage_id={_storage_id}')
            _json = deepcopy(CMS_STORAGE_DIRECTORY.get(_bucket_name))
            _json.update(storage_id=_storage_id)
            _json.get('storage_info')[0].update(capacity=_quota)

            if not _query_storage_set:  # 未设置则调接口设置
                cls.config_cms_cloud_storage_directory_by_rest_via_json(json=_json)


if __name__ == '__main__':
    pass
