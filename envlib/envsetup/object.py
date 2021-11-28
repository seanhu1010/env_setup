#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File:    object.py
"""
MG对象管理预置库
"""
import os

from envlib.env.envlogging import logger

from envlib.env.globals import current_app as app
from envlib.env.globals import g
from envlib.env.helpers import GetKeysMixin
from envlib.env_resources.preset_data import OBJECT_TYPE, OBJECT_GROUP_TYPE
from envlib.envsetup.uuv import Uuv
from envlib.id_info import object_id_info
from resources.data import SMB_SHARE_PATH

__all__ = ['Object', ]


class Object(GetKeysMixin):
    """对象管理类"""

    def __init__(self):
        pass

    @classmethod
    def query_object_bookmark_by_rest(cls, check=False):
        """查询收藏夹

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='object_bookmark_list', value=查询接口返回值，收藏夹列表

        Args:
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值，收藏夹列表

        """

        res = app.send_by_rest('/api/demo@get', check=check)
        app.bind_to_g(key='object_bookmark_list', value=res, lock=False)
        return res

    @classmethod
    def query_group_list_by_rest_via_kw(cls, group_name, object_type, check=False, **kwargs):
        """查询分组列表

        Args:
            group_name (str): 分组名
            object_type (str): 对象类型
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，分组列表

        """

        body = {"page_num": 1, "page_size": 10000, "object_type": object_type}
        body.update(kwargs)

        res = app.send_by_rest('/api/demo@post', json=body, check=check).get('data')

        if group_name is not None:
            group_list = [item for item in res if item.get('group_name') == group_name]
        else:
            group_list = res

        return group_list

    @classmethod
    def query_person_group_list_by_rest_via_group_name(cls, group_name=None, **kwargs):
        """查询人员分组列表，以及名单库列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='object_person_group_list', value=查询接口返回值，人员分组列表，以及名单库列表

        Args:
            group_name (str): 分组名
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，人员分组列表，以及名单库列表

        """

        object_type = OBJECT_TYPE.get("人员")

        res = cls.query_group_list_by_rest_via_kw(group_name=group_name, object_type=object_type, **kwargs)
        app.bind_to_g(key='object_person_group_list', value=res, lock=False)
        return res

    @classmethod
    def query_group_list_detail_by_rest_via_kw(cls, group_id, object_type, search, check=False, **kwargs):
        """查询分组里的对象列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='object_person_group_list_detail', value=查询接口返回值，分组里的对象列表

        Args:
            group_id (str): 分组id
            object_type (str): 对象类型
            search (str): 模糊搜索关键字
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，分组里的对象列表

        """

        body = {
            # "total": 1,
            # "total_num": 1,
            "page_num": 1,
            "page_size": 1000,
            "group_id": group_id,
            "search": search,
            "form_code": object_type
        }
        body.update(kwargs)

        res = app.send_by_rest('/api/demo@post', json=body, check=check)
        app.bind_to_g(key='object_person_group_list_detail', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def query_person_group_list_detail_by_rest_via_group_name(cls, group_name, search="", **kwargs):
        """查询人员分组里的对象列表

        Args:
            group_name(str): 分组名字
            search(str, optional): 搜索内容 (Default value = "")
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，人员分组里的对象列表

        """
        object_type = OBJECT_TYPE.get("人员")

        group_list = cls.query_person_group_list_by_rest_via_group_name(group_name=group_name)

        if len(group_list) == 1:  # 有且仅查到一个为正确结果
            group_id = group_list[0].get('id')
            res = cls.query_group_list_detail_by_rest_via_kw(group_id=group_id, object_type=object_type,
                                                             search=search, **kwargs)
            return res
        else:
            logger.warning(f'组织列表不存在或有误，查询结果为 {group_list} ')
            return None

    @classmethod
    def query_person_manage_person_list_via_json(cls, json, check=False):
        """检索对象管理-人员列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='object_person_manage_person_list', value=查询接口返回值，对象管理-人员列表

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值，对象管理-人员列表

        """

        res = app.send_by_rest('/api/demo@post', json=json, check=check)
        app.bind_to_g(key='object_person_manage_person_list', value=res.get('data'), lock=False)
        return res

    @classmethod
    def query_object_person_detail_list_by_dep_name(cls, dep_name=None):
        """根据部门名，检索对象管理-人员管理-某部门下的人员列表

        Args:
            dep_name (str): 部门名

        Returns:
            rest接口返回值，某部门下的人员列表

        """

        # TODO: 默认至多只查询1w条数据

        body = {
            "page_num": 1,
            "page_size": 10000,
            "query_columns": [
                {
                    "table_name": "tb_person",
                    "columns": "id,is_construct,user_image,user_name,user_code,gender,birthday,cell_phone,nation,\
                    user_object_type,country,residence,address,identity_type,identity_no,org_index,description,\
                    plate_num,plate_color,access_card_num,access_password,org_id,index_path,"
                }
            ],
            "super_query_params": [
                {
                    "rule": "eq",
                    "val": "api",
                    "field": "tb_person.org_index"
                }
            ]
        }
        org_index = Uuv.query_department_index_via_dep_name(dep_name=dep_name)
        if not org_index:
            logger.warning(f'传入的部门 "{dep_name}" 不存在，将返回全部人员信息')
            body.update(super_query_params=[])
        else:
            body.get('super_query_params')[0].update(val=org_index)

        return cls.query_person_manage_person_list_via_json(json=body).get('data')

    @classmethod
    def add_object_group_by_rest_via_kw(cls, group_name, object_type, group_type, send_lib=2, check=False, **kwargs):
        """新建分组,包括人员分组,车辆分组,房屋分组等

        Args:
            group_name (str): 分组名
            object_type (str): 对象类型
            group_type (str): 分组类型
            send_lib (int): 下发flag
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值

        """

        query = cls.query_group_list_by_rest_via_kw(group_name=group_name, object_type=object_type)

        if query:  # 重复则跳过
            logger.warning(f'分组名称{group_name}重复，请勿重复添加')
            return query
        else:
            body = {
                "form_id": "",
                "req": {
                    "parent": 0,
                    "object_type": object_type,
                    "send_lib": send_lib,  # 1下发名单库 2不下发名单库
                    "group_name": group_name,
                    "type": group_type,
                    "description": "",
                    "tab_type": "05",
                    "domain": ""
                }
            }
            body["req"].update(**kwargs)
            res = app.send_by_rest('/api/demo@post', json=body, check=check)
            return res

    @classmethod
    def add_person_group_normal_via_group_name(cls, group_name, **kwargs):
        """新建人员分组-普通分组

        Args:
            group_name (str): 分组名
            **kwargs: 可选字典项

        Keyword Args:
            send_lib(int): 是否下发，1下发 2不下发，默认不下发
            description(str): 描述

        Returns:
            rest接口返回值

        """

        object_type = OBJECT_TYPE.get("人员")
        group_type = OBJECT_GROUP_TYPE.get("人员").get("普通分组")

        res = cls.add_object_group_by_rest_via_kw(group_name=group_name, object_type=object_type,
                                                  group_type=group_type,
                                                  **kwargs)
        return res

    @classmethod
    def add_namelist_static_via_group_name(cls, group_name, send_lib=1, **kwargs):
        """新建人员分组-静态库

        Args:
            group_name (str): 分组名
            **kwargs: 可选字典项

        Keyword Args:
            send_lib(int): 是否下发，1下发 2不下发，默认不下发
            description(str): 描述

        Returns:
            rest接口返回值

        """

        object_type = OBJECT_TYPE.get("人员")
        group_type = OBJECT_GROUP_TYPE.get("人员").get("静态库")

        res = cls.add_object_group_by_rest_via_kw(group_name=group_name, object_type=object_type,
                                                  group_type=group_type,
                                                  send_lib=send_lib,
                                                  **kwargs)
        return res

    @classmethod
    def add_namelist_black_via_group_name(cls, group_name, send_lib=1, **kwargs):
        """新建人员分组-黑名单

        Args:
            group_name (str): 分组名
            **kwargs: 可选字典项

        Keyword Args:
            send_lib(int): 是否下发，1下发 2不下发，默认不下发
            description(str): 描述

        Returns:
            rest接口返回值

        """

        object_type = OBJECT_TYPE.get("人员")
        group_type = OBJECT_GROUP_TYPE.get("人员").get("黑名单")

        res = cls.add_object_group_by_rest_via_kw(group_name=group_name, object_type=object_type,
                                                  group_type=group_type,
                                                  send_lib=send_lib,
                                                  **kwargs)
        return res

    @classmethod
    def add_namelist_white_via_group_name(cls, group_name, send_lib=1, **kwargs):
        """新建人员分组-白名单

        Args:
            group_name (str): 分组名
            **kwargs: 可选字典项

        Keyword Args:
            send_lib(int): 是否下发，1下发 2不下发，默认不下发
            description(str): 描述

        Returns:
            rest接口返回值

        """

        object_type = OBJECT_TYPE.get("人员")
        group_type = OBJECT_GROUP_TYPE.get("人员").get("白名单")

        res = cls.add_object_group_by_rest_via_kw(group_name=group_name, object_type=object_type,
                                                  group_type=group_type,
                                                  send_lib=send_lib,
                                                  **kwargs)
        return res

    @classmethod
    def delete_object_group_by_rest_via_json(cls, json, check=False):
        """删除分组

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@delete', json=json, check=check)

        return res

    @classmethod
    def modify_object_group_by_rest_via_json(cls, json, check=False):
        """修改分组

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@put', json=json, check=check)

        return res

    @classmethod
    def export_object_group_by_rest_via_json(cls, json, check=False):
        """导出分组

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', json=json, check=check)

        return res

    @classmethod
    def upload_object_image_by_rest_via_kw(cls, data, headers, check=False):
        """添加人员对象上传的图片

        Args:
            data (any): 接口data数据结构
            headers (dict): rest请求headers
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', data=data, headers=headers, check=check)

        return res

    @classmethod
    def upload_object_image_by_smb_via_file(cls, file_relative_path, file_name):
        """SMB连接添加人员对象上传的图片

        Args:
            file_relative_path (str): 相对 env.ini指定share_path ``\\\\1.1.1.1\\info\\auto\\`` 路径，
                如 '照片'
            file_name (str): jpg文件名，如'somebody.jpg'

        Returns:
            rest接口返回值

        """

        data, _headers = app.smb_upload_jpg(file_relative_path=file_relative_path, file_name=file_name)
        res = cls.upload_object_image_by_rest_via_kw(data=data, headers=_headers)
        return res

    @classmethod
    def add_person_object_to_department_by_smb(cls, user_code=None, user_name=None, sex=2, file_relative_path='images',
                                               file_name='person.jpg', is_construct=0, dep_name='common'):
        """向部门中添加人员对象

        Args:
            user_code (str): 用户编号, (Default value = None), 默认采用随机身份证
            user_name (str): (Default value = None)，不传参时，随机生成中文姓名
            sex (int): (Default value = 2)，1:男，2:女
            file_relative_path (str): 相对env.ini指定share_path ``\\\\1.1.1.1\\info\\auto\\`` 路径，如'照片'
            file_name (str): jpg文件名，如'somebody.jpg'
            is_construct (int): 是否提取特征，int: 0:不提取,1:提取
            dep_name (str): 对象添加的部门

        Returns:
            rest接口返回值

        """

        org_info = Uuv.query_department_info_via_dep_name(dep_name=dep_name, info=('org_index', 'org_id'))
        org_info_dict = dict(zip(('org_index', 'org_id'), org_info))

        body = {
            "table_name": "tb_person",
            "data": {
                "user_code": "130202196405089358",
                "user_image": "/file/mg/2021/0121/20210121172515469.jpg",
                "gender": "1",
                "is_construct": 0,
                "user_name": "someone",
                "cell_phone": "13588089942",
                "identity_type": 111,
                "residence": "110000-110100-110102",
                "birthday": -178329600000,
                "nation": 1,
                "country": 156,
                "address": "北京",
                "identity_no": "130202196405089358",
                "description": "for test only",
                "formId": "omperson",
                "org_id": 98,
                "org_index": "225",
                "index_path": "0/1/"
            }
        }
        data = object_id_info(name_=user_name, sex_=sex, user_code=user_code)
        data.update(is_construct=is_construct, **org_info_dict)
        _res = cls.upload_object_image_by_smb_via_file(file_relative_path=file_relative_path, file_name=file_name)
        data.update(user_image=_res.get('url'))
        body.get('data').update(**data)

        # 查所有人员列表，受限只查1w条
        person_list = cls.query_object_person_detail_list_by_dep_name()
        for person in person_list:
            if person['tb_person$user_code'] == data.get('user_code'):
                logger.warning(f'用户编号{data.get("user_code")}重复，将跳过')
                return person

        res = cls.add_person_object_by_rest_via_json(json=body)
        return res

    @classmethod
    def batch_add_person_object_to_department_by_smb(cls, file_relative_path, dep_name='common', sex=1):
        """SMB批量向部门中添加人员对象

        Args:
            file_relative_path (str): 相对env.ini指定share_path ``\\\\1.1.1.1\\info\\auto\\`` 路径，如'照片'
            dep_name (str, optional): 部门名称 (Default value = 'common')
            sex (int, optional): 性别，默认1为男性，2为女性 (Default value = 1)

        Returns:
            rest接口返回值

        """
        _pics = app.smb.scandir(os.path.join(SMB_SHARE_PATH, file_relative_path))
        for _pic in _pics:
            cls.add_person_object_to_department_by_smb(
                user_name=_pic.name.split('.')[0],
                sex=sex,
                file_relative_path=file_relative_path,
                file_name=_pic.name,
                dep_name=dep_name,
            )
        res = cls.query_object_person_detail_list_by_dep_name(dep_name=dep_name)
        return res

    @classmethod
    def add_person_object_to_group_by_smb(cls, group_name, user_code=None, user_name=None, sex=2,
                                          file_relative_path='images',
                                          file_name='person.jpg', is_construct=0):
        """向分组(名单库)中添加人员对象

        Args:
            group_name (str): 分组或名单库的名称
            user_code (str, optional): 用户编号, (Default value = None), 默认采用随机身份证
            user_name (str): (Default value = None)，不传参时，随机生成中文姓名
            sex (int): (Default value = 2)，1:男，2:女
            file_relative_path (str): 相对 env.ini指定share_path ``\\\\1.1.1.1\\info\\auto\\`` 路径，如'照片'
            file_name (str): jpg文件名，如'somebody.jpg'
            is_construct (int): 是否提取特征，int: 0:不提取,1:提取 (Default value = 0)

        Returns:
            rest接口返回

        """

        group_info = cls.query_person_group_list_by_rest_via_group_name(group_name=group_name)

        assert len(group_info) == 1, f'分组或名单库查询失败，无此分组，查询结果为 {group_info}'

        body = {
            "table_name": "tb_person",
            "data": {
                "user_code": "130202196405089358",
                "user_image": "/file/mg/2021/0121/20210121172515469.jpg",
                "gender": "1",
                "is_construct": is_construct,
                "user_name": "someone",
                "cell_phone": "13588089942",
                "identity_type": 111,
                "residence": "110000-110100-110102",
                "birthday": -178329600000,
                "nation": 1,
                "country": 156,
                "address": "北京",
                "identity_no": "130202196405089358",
                "description": "for test only",
                "formId": "omperson",
                "org_id": 1,
                "org_index": "1",
                "index_path": "0/",
                "group_id": group_info[0].get('id'),
            }
        }
        data = object_id_info(name_=user_name, sex_=sex, user_code=user_code)
        _res = Object.upload_object_image_by_smb_via_file(file_relative_path=file_relative_path, file_name=file_name)
        data.update(user_image=_res.get('url'))
        body.get('data').update(**data)

        # 查所有人员列表，受限只查1w条
        person_list = cls.query_object_person_detail_list_by_dep_name()

        for person in person_list:
            if person['tb_person$user_code'] == data.get('user_code'):
                logger.warning(f'用户编号{data.get("user_code")}重复，将跳过')
                return person

        res = cls.add_person_object_by_rest_via_json(json=body)
        return res

    @classmethod
    def batch_add_object_person_to_group_by_smb(cls, group_name, file_relative_path, sex=1):
        """SMB批量向分组(名单库)中添加人员对象

        Args:
            group_name (str): 分组或名单库的名称
            file_relative_path (str): 相对 env.ini指定share_path ``\\\\1.1.1.1\\info\\auto\\`` 路径，如'照片'
            sex (int): 性别，默认1为男性，2为女性 (Default value = 1)

        Returns:
            rest接口返回

        """
        _pics = app.smb.scandir(os.path.join(SMB_SHARE_PATH, file_relative_path))
        for _pic in _pics:
            cls.add_person_object_to_group_by_smb(
                group_name=group_name,
                user_name=_pic.name.split('.')[0],
                sex=sex,
                file_relative_path=file_relative_path,
                file_name=_pic.name,
            )
        res = cls.query_person_group_list_detail_by_rest_via_group_name(group_name=group_name)
        return res

    @classmethod
    def add_person_object_by_rest_via_json(cls, json, check=False):
        """添加人员对象

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', json=json, check=check)

        return res

    @classmethod
    def add_vehicle_object_by_rest_via_json(cls, json, check=False):
        """添加车辆对象

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', json=json, check=check)

        return res

    @classmethod
    def add_house_object_by_rest_via_json(cls, json, check=False):
        """添加房屋对象

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', json=json, check=check)

        return res

    @classmethod
    def delete_person_object_by_rest_via_json(cls, json, check=False):
        """删除人员对象

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@delete', json=json, check=check)

        return res

    @classmethod
    def delete_vehicle_object_by_rest_via_json(cls, json, check=False):
        """删除车辆对象

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@delete', json=json, check=check)

        return res

    @classmethod
    def delete_house_object_by_rest_via_json(cls, json, check=False):
        """删除房屋对象

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@delete', json=json, check=check)

        return res


if __name__ == '__main__':
    pass
