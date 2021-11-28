#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File:    uuv.py
"""
综合管理操作类预置库
"""

from envlib.env.envlogging import logger

from envlib.env.globals import current_app as app
from envlib.env.globals import g
from envlib.env.helpers import GetKeysMixin
from envlib.util import Md5
from resources.data import SMB_SHARE_PATH, TAG_LIST

__all__ = ['Uuv', ]


class Uuv(GetKeysMixin):
    """综合管理操作类"""

    def __init__(self):
        pass

    @classmethod
    def query_uuv_department_by_rest(cls, check=False, **kwargs):
        """传入params，查询部门信息

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='uuv_department_list', value=查询接口返回值，部门信息

        Args:
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，部门信息

        """

        params = {"path": True, "type": 1}
        params.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=params, check=check)
        app.bind_to_g(key='uuv_department_list', value=res[0].get('child'), lock=False)
        return res[0].get('child')

    @classmethod
    def query_department_index_via_dep_name(cls, dep_name="api"):
        """传入部门名，查询部门org_index

        Args:
            dep_name (str): 部门名称

        Returns:
            部门org_index

        """

        cls.query_uuv_department_by_rest()
        dep_info = g.getk('uuv_department_list').extracting('org_index', filter={'org_name': dep_name})
        return dep_info

    @classmethod
    def query_department_info_via_dep_name(cls, dep_name="api", info=('org_index',)):
        """传入部门名及可选参数，查询部门info

        Args:
            dep_name (str): 部门名称
            info (tuple): 部门信息元组，例如 ('org_index',)

        Returns:
            部门info

        """

        cls.query_uuv_department_by_rest()
        logger.info(f"查询组织 {dep_name} 的 {info} 信息")
        dep_info = g.getk('uuv_department_list').extracting(*info, filter={'org_name': dep_name})
        return dep_info

    @classmethod
    def add_uuv_department_by_rest_via_json(cls, json, check=False):
        """传入json，添加部门信息

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', json=json, check=check)
        cls.query_uuv_department_by_rest()
        return res

    @classmethod
    def import_uuv_department_by_rest_via_smb(cls, data, headers, check=False):
        """读取 env.ini指定share_path ``\\\\1.1.1.1\\info\\auto\\`` 下的 ``部门导入模板.xlsx`` 导入部门信息

        Args:
            data (any): 接口data数据结构
            headers (dict): rest请求headers
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', data=data, headers=headers,
                               check=check)
        cls.query_uuv_department_by_rest()
        return res

    @classmethod
    def add_uuv_department_by_rest_via_dep_name(cls, dep_name):
        """传入部门名称，添加部门信息

        Args:
            dep_name(str): 组织名称，约定只用数字、字母、中划线

        Returns:
            rest接口返回值

        """

        _department_list = cls.query_uuv_department_by_rest()
        _exist_department_list = [dept for dept in _department_list if dept.get('org_name') == dep_name]

        if not _exist_department_list:  # 未添加
            _json = {
                "parent_id": 1,
                "org_parent_index": "1",
                "org_name": dep_name,
                "org_index": Md5.md5_str(dep_name),
                "type": "1"
            }
            cls.add_uuv_department_by_rest_via_json(json=_json)
        else:
            logger.warning(f'所添加的部门 "{dep_name}" 重复，将跳过')

        return cls.query_uuv_department_by_rest()

    @classmethod
    def batch_add_uuv_department_from_env_ini(cls):
        """批量从env的配置文件中，添加tag_list下的部门信息

        Returns:
            rest接口返回值

        """

        for org_name in TAG_LIST:
            cls.add_uuv_department_by_rest_via_dep_name(dep_name=org_name)

    @classmethod
    def import_uuv_department_from_excel(cls):
        """读取 env.ini指定share_path ``\\\\1.1.1.1\\info\\auto\\`` 下的 ``部门导入模板.xlsx`` 导入部门信息

        Returns:
            rest接口返回值

        """

        # 查询部门
        _department_list = cls.query_uuv_department_by_rest()
        _exist_department_list = [dept for dept in _department_list if dept.get('org_name') == 'common']

        if not _exist_department_list:  # 未导入部门
            _department_xlsx_file = '部门导入模板.xlsx'
            _department_xlsx_file_path = SMB_SHARE_PATH + _department_xlsx_file
            data, headers = app.smb_upload_excel(file_name=_department_xlsx_file_path)
            cls.import_uuv_department_by_rest_via_smb(data=data, headers=headers)

    @classmethod
    def query_uuv_organization_by_rest(cls, check=False, **kwargs):
        """查询组织list

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='uuv_organization_list', value=查询接口返回值，组织信息

        Args:
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，组织信息

        """

        params = {'type': 0, 'page_index': 1, 'page_size': 200}
        params.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=params, check=check)
        app.bind_to_g(key='uuv_organization_list', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def query_organization_index_via_org_name(cls, org_name="本域"):
        """传入组织名，查询组织id

        Args:
            org_name (str): 组织名

        Returns:
            组织index值

        """

        cls.query_uuv_organization_by_rest()
        org_index = g.getk('uuv_organization_list').extracting('org_index', filter={'org_name': org_name})
        return org_index

    @classmethod
    def query_organization_info_via_org_name(cls, org_name="本域", info=('org_index',)):
        """传入组织名及可选参数，查询组织info

        Args:
            org_name (str): 组织名
            info (tuple): 组织信息元组，例如 ('org_index',)

        Returns:
            org_info

        """

        cls.query_uuv_organization_by_rest()
        logger.info(f"查询组织 {org_name} 的 {info} 信息")
        org_info = g.getk('uuv_organization_list').extracting(*info, filter={'org_name': org_name})
        return org_info

    @classmethod
    def add_uuv_organization_by_rest_via_json(cls, json, check=False):
        """添加组织

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', json=json, check=check)
        cls.query_uuv_organization_by_rest()
        return res

    @classmethod
    def import_uuv_organization_via_smb(cls, data, headers, check=False):
        """读取 env.ini指定share_path ``\\\\1.1.1.1\\info\\auto\\`` 下的 ``组织表.xlsx`` 导入组织信息

        Args:
            data (any): 接口data数据结构
            headers (dict): rest请求headers
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', data=data, headers=headers,
                               check=check)
        cls.query_uuv_organization_by_rest()
        return res

    @classmethod
    def add_uuv_organization_via_org_name(cls, org_name):
        """添加组织信息

        Args:
            org_name(str): 组织名称

        Returns:
            None or rest接口返回值

        """

        _organization_list = cls.query_uuv_organization_by_rest()
        _exist_organization_list = [org for org in _organization_list if org.get('org_name') == org_name]

        if not _exist_organization_list:  # 未导入组织  # 未添加
            _json = {
                "type": "0",
                "parent_id": 2,
                "org_name": org_name,
                "region_code": "500100",
                "description": "",
                "street": "",
                "is_region": False
            }
            cls.add_uuv_organization_by_rest_via_json(json=_json)
        else:
            logger.warning(f'所添加的组织 "{org_name}" 重复，将跳过')

    @classmethod
    def batch_add_uuv_organization_from_env_ini(cls):
        """批量从env的配置文件中，添加tag_list下的组织信息，并绑定到 ``common`` tag下

        Returns:
            rest接口返回值

        """

        for org_name in TAG_LIST:
            cls.add_uuv_organization_via_org_name(org_name=org_name)

    @classmethod
    def import_uuv_organization_from_excel(cls):
        """读取 env.ini指定share_path ``\\\\1.1.1.1\\info\\auto\\`` 下的 ``组织表.xlsx`` 导入组织信息

        Returns:
            rest接口返回值

        """

        # 查询组织
        _organization_list = cls.query_uuv_organization_by_rest()
        _exist_organization_list = [org for org in _organization_list if org.get('org_name') == 'common']

        if not _exist_organization_list:  # 未导入组织
            _organization_xlsx_file = '组织表.xlsx'
            _organization_xlsx_file_path = SMB_SHARE_PATH + _organization_xlsx_file
            data, headers = app.smb_upload_excel(file_name=_organization_xlsx_file_path)
            cls.import_uuv_organization_via_smb(data=data, headers=headers)


if __name__ == '__main__':
    pass
