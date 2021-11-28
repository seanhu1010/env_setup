#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File:    udm.py
"""
设备管理预置库
"""

from envlib.env.envlogging import logger
from envlib.env.globals import current_app as app
from envlib.env.globals import g
from envlib.env.helpers import GetKeysMixin
from envlib.env_resources.preset_data import SUB_TYPE, RESOURCE_TYPE, ACCESS_TYPE, PRODUCER, func_encoder_body, \
    func_tollgate_body, TOLLGATE_TYPE
from envlib.envsetup.uuv import Uuv

__all__ = ['Udm', ]


class Udm(GetKeysMixin):
    """设备管理类"""

    @classmethod
    def query_encoder_device_list_by_rest_via_org_name(cls, org_name="本域", check=False, **kwargs):
        """查询编码器设备列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='udm_encoder_device_list', value=查询接口返回值，编码器设备列表

        Args:
            org_name (str): 组织名
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，编码器设备列表

        """

        org_index = Uuv.query_organization_index_via_org_name(org_name=org_name)

        para = {
            "resource_type": RESOURCE_TYPE.get('编码器'),
            "org_index": org_index,
            "include_child": True,  # 默认包含叶子列表
            "page_num": 1,
            "page_size": 2000,
            "order_field": 'ape_id',
            "order_rule": 'asc',
            "enabled": 1,
        }
        para.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=para, check=check)
        app.bind_to_g(key='udm_encoder_device_list', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def query_decoder_device_list_by_rest_via_org_name(cls, org_name="本域", check=False, **kwargs):
        """查询解码器设备列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='udm_decoder_device_list', value=查询接口返回值，解码器设备列表

        Args:
            org_name (str): 组织名
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，解码器设备列表

        """

        org_index = Uuv.query_organization_index_via_org_name(org_name=org_name)

        para = {
            "resource_type": RESOURCE_TYPE.get('解码器'),
            "org_index": org_index,
            "include_child": True,  # 默认包含叶子列表
            "page_num": 1,
            "page_size": 2000,
            "order_field": 'ape_id',
            "order_rule": 'asc',
            "enabled": 1,
        }
        para.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=para, check=check)
        app.bind_to_g(key='udm_decoder_device_list', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def query_tollgate_device_list_by_rest_via_org_name(cls, org_name="本域", check=False, **kwargs):
        """查询卡口设备列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='udm_tollgate_device_list', value=查询接口返回值，卡口设备列表

        Args:
            org_name (str): 组织名
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，卡口设备列表

        """

        org_index = Uuv.query_organization_index_via_org_name(org_name=org_name)

        para = {
            "resource_type": RESOURCE_TYPE.get('卡口'),
            "org_index": org_index,
            "include_child": True,  # 默认包含叶子列表
            "page_num": 1,
            "page_size": 2000,
            "order_field": 'tollgate_id',
            "order_rule": 'asc',
        }
        para.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=para, check=check)
        app.bind_to_g(key='udm_tollgate_device_list', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def query_video_capture_device_list_by_rest_via_org_name(cls, org_name="本域", check=False, **kwargs):
        """查询采集设备列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='udm_video_capture_device_list', value=查询接口返回值，采集设备列表

        Args:
            org_name (str): 组织名
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，采集设备列表

        """

        org_index = Uuv.query_organization_index_via_org_name(org_name=org_name)

        para = {
            "resource_type": RESOURCE_TYPE.get('采集设备'),
            "org_index": org_index,
            "include_child": True,  # 默认包含叶子列表
            "page_num": 1,
            "page_size": 2000,
            "order_field": 'ape_id',
            "order_rule": 'asc',
            "enabled": 1,
        }
        para.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=para, check=check)
        app.bind_to_g(key='udm_video_capture_device_list', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def query_encoder_channel_list_by_rest_via_org_name(cls, org_name="本域", check=False, **kwargs):
        """查询编码器通道列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='udm_encoder_channel_list', value=查询接口返回值，编码器通道列表

        Args:
            org_name (str): 组织名
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，编码器通道列表

        """

        org_index = Uuv.query_organization_index_via_org_name(org_name=org_name)

        para = {
            "sub_type": SUB_TYPE.get("编码器"),
            "resource_type": RESOURCE_TYPE.get("通道"),
            "org_index": org_index,
            "include_child": True,  # 默认包含叶子列表
            "page_num": 1,
            "page_size": 2000,
            "order_field": 'ape_id',
            "order_rule": 'asc',
            "enabled": 1,
        }
        para.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=para, check=check)
        app.bind_to_g(key='udm_encoder_channel_list', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def query_encoder_face_tollgate_vehicle_tollgate_channel_list_by_rest_via_org_name(cls, org_name="本域", check=False,
                                                                                       **kwargs):
        """查询编码器,人脸卡口，车辆卡口通道列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='udm_encoder_face_tollgate_vehicle_tollgate_channel_list', value=查询接口返回值，编码器,人脸卡口，车辆卡口通道列表

        Args:
            org_name (str): 组织名
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，编码器,人脸卡口，车辆卡口通道列表

        """

        org_index = Uuv.query_organization_index_via_org_name(org_name=org_name)

        para = {
            "sub_type": f'{SUB_TYPE.get("编码器")},{SUB_TYPE.get("人脸卡口")},{SUB_TYPE.get("车辆卡口")}',
            "resource_type": RESOURCE_TYPE.get("通道"),
            "org_index": org_index,
            "include_child": True,  # 默认包含叶子列表
            "page_num": 1,
            "page_size": 2000,
            "order_field": 'ape_id',
            "order_rule": 'asc',
            "enabled": 1,
        }
        para.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=para, check=check)
        app.bind_to_g(key='udm_encoder_face_tollgate_vehicle_tollgate_channel_list', value=res.get('data'), lock=False)
        # 还有一种接口是同时列出channel和device,/api/infra-udm/v0.1/channel/listChannelAndDevice
        return res.get('data')

    @classmethod
    def query_decoder_channel_list_by_rest_via_org_name(cls, org_name="本域", check=False, **kwargs):
        """查询解码器通道列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='udm_decoder_channel_list', value=查询接口返回值，解码器通道列表

        Args:
            org_name (str): 组织名
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，解码器通道列表

        """

        org_index = Uuv.query_organization_index_via_org_name(org_name=org_name)

        para = {
            "sub_type": SUB_TYPE.get("解码器"),
            "resource_type": RESOURCE_TYPE.get("通道"),
            "org_index": org_index,
            "include_child": True,  # 默认包含叶子列表
            "page_num": 1,
            "page_size": 2000,
            "order_field": 'ape_id',
            "order_rule": 'asc',
            "enabled": 1,
        }
        para.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=para, check=check)
        app.bind_to_g(key='udm_decoder_channel_list', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def query_face_tollgate_channel_list_by_rest_via_org_name(cls, org_name="本域", check=False, **kwargs):
        """查询人脸卡口通道列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='udm_face_tollgate_channel_list', value=查询接口返回值，人脸卡口通道列表

        Args:
            org_name (str): 组织名
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，人脸卡口通道列表

        """

        org_index = Uuv.query_organization_index_via_org_name(org_name=org_name)

        para = {
            "sub_type": SUB_TYPE.get("人脸卡口"),
            "resource_type": RESOURCE_TYPE.get("通道"),
            "org_index": org_index,
            "include_child": True,  # 默认包含叶子列表
            "page_num": 1,
            "page_size": 2000,
            "order_field": 'ape_id',
            "order_rule": 'asc',
            "enabled": 1,
        }
        para.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=para, check=check)
        app.bind_to_g(key='udm_face_tollgate_channel_list', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def query_vehicle_tollgate_channel_list_by_rest_via_org_name(cls, org_name="本域", check=False, **kwargs):
        """查询车辆卡口通道列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='udm_vehicle_channel_list', value=查询接口返回值，车辆卡口通道列表

        Args:
            org_name (str): 组织名
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，车辆卡口通道列表

        """

        org_index = Uuv.query_organization_index_via_org_name(org_name=org_name)

        para = {
            "sub_type": SUB_TYPE.get("车辆卡口"),
            "resource_type": RESOURCE_TYPE.get("通道"),
            "org_index": org_index,
            "include_child": True,  # 默认包含叶子列表
            "page_num": 1,
            "page_size": 2000,
            "order_field": 'ape_id',
            "order_rule": 'asc',
            "enabled": 1,
        }
        para.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=para, check=check)
        app.bind_to_g(key='udm_vehicle_channel_list', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def query_tollgate_channel_list_detail_by_rest_via_org_name(cls, org_name="本域", check=False, **kwargs):
        """查询卡口设备列表，包含设备详细信息

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='udm_tollgate_channel_list_detail', value=卡口设备列表，包含设备详细信息

        Args:
            org_name (str): 组织名
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，卡口设备列表，包含设备详细信息

        """

        org_index = Uuv.query_organization_index_via_org_name(org_name=org_name)

        para = {
            "sub_type": f'{SUB_TYPE.get("人脸卡口")},{SUB_TYPE.get("车辆卡口")}',
            "resource_type": RESOURCE_TYPE.get("通道"),
            "org_index": org_index,
            "include_child": True,  # 默认包含叶子列表
            "page_num": 1,
            "page_size": 2000,
            "order_field": 'ape_id',
            "order_rule": 'asc',
            "enabled": 1,
        }
        para.update(**kwargs)

        res = app.send_by_rest('/api/demo@get', params=para, check=check)
        app.bind_to_g(key='udm_tollgate_channel_list_detail', value=res.get('data'), lock=False)
        return res.get('data')

    @classmethod
    def add_encoder_device_by_rest_via_kw(cls, ip_port,
                                          device_name=None,
                                          user='admin',
                                          password='admin123',
                                          org_name="本域",
                                          access_type='Onvif',
                                          producer="UVW",
                                          se_longitude=(105.5, 106.5),
                                          se_latitude=(29.0, 30.0),
                                          check=False):
        """添加编码器设备列表

        Args:
            ip_port (str): '1.1.1.1_80'形式
            device_name (str): 设备名
            user (str): 设备登陆用户名
            password (str): 设备登陆密码
            org_name (str): 组织名
            access_type (str): 设备接入协议
            producer (str): 设备厂商
            se_longitude (tuple): 经度范围，如(105.5, 106.5)
            se_latitude (tuple): 纬度范围，如(29.0, 30.0)
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        # 设备已添加不重复添加
        cls.query_encoder_device_list_by_rest_via_org_name()
        query = list(filter(lambda x: x["ip_addr"] == ip_port.split(":")[0] and x["port"] == int(ip_port.split(":")[1]),
                            g.get("udm_encoder_device_list")))
        if query:
            logger.debug(f"设备{ip_port}已存在")
            return

        org_info = Uuv.query_organization_info_via_org_name(org_name=org_name,
                                                            info=('org_name', 'org_index', 'region_code'))
        # 确保目标组织存在
        if org_info is None:
            return

        # 添加设备
        org_info_dict = dict(zip(('org_name', 'org_index', 'place_code'), org_info))
        body = func_encoder_body(ip_port=ip_port,
                                 name=device_name,
                                 user_id=user,
                                 password=password,
                                 **org_info_dict,
                                 access_type=ACCESS_TYPE.get(access_type),
                                 producer=PRODUCER.get(producer),
                                 se_longitude=se_longitude,
                                 se_latitude=se_latitude,
                                 )

        res = app.send_by_rest('/api/demo@post', json=body, check=check)

        return res

    @classmethod
    def add_onvif_encoder_device(cls, ip_port,
                                 device_name=None,
                                 user='admin',
                                 password='admin123',
                                 org_name="本域",
                                 producer="UVW",
                                 se_longitude=(105.5, 106.5),
                                 se_latitude=(29.0, 30.0),
                                 check=False):
        """添加onvif类型的编码器设备列表

        Args:
            ip_port (str): '1.1.1.1_80'形式
            device_name (str): 设备名
            user (str): 设备登陆用户名
            password (str): 设备登陆密码
            org_name (str): 组织名
            producer (str): 设备厂商
            se_longitude (tuple): 经度范围，如(105.5, 106.5)
            se_latitude (tuple): 纬度范围，如(29.0, 30.0)
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        return cls.add_encoder_device_by_rest_via_kw(ip_port=ip_port,
                                                     device_name=device_name,
                                                     user=user,
                                                     password=password,
                                                     org_name=org_name,
                                                     access_type='Onvif',
                                                     producer=producer,
                                                     se_longitude=se_longitude,
                                                     se_latitude=se_latitude,
                                                     check=check)

    @classmethod
    def add_tollgate_device_by_rest_via_kw(cls, ip_port, device_name=None, org_name="本域", device_type="人脸卡口",
                                           se_longitude=(105.5, 106.5), se_latitude=(29.0, 30.0), check=False):
        """添加卡口设备列表

        Args:
            ip_port (str): '1.1.1.1_80'形式
            device_name (str): 设备名
            org_name (str): 组织名
            se_longitude (tuple): 经度范围，如(105.5, 106.5)
            se_latitude (tuple): 纬度范围，如(29.0, 30.0)
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        # 设备已添加不重复添加
        cls.query_tollgate_channel_list_detail_by_rest_via_org_name()
        query = list(filter(lambda x: x.get("ip_addr") == ip_port.split(":")[0],
                            g.get("udm_tollgate_channel_list_detail")))
        if query:
            logger.debug(f"设备{ip_port}已存在")
            return

        org_info = Uuv.query_organization_info_via_org_name(org_name=org_name,
                                                            info=('org_name', 'org_index', 'region_code'))
        # 确保目标组织存在
        if org_info is None:
            return

        # 添加设备
        if device_name is None:
            device_name = f"face_{ip_port.split(':')[0]}"
        org_info_dict = dict(zip(('org_name', 'org_index', 'place_code'), org_info))
        body = func_tollgate_body(ip_port=ip_port,
                                  name=device_name,
                                  sub_type=TOLLGATE_TYPE.get(device_type),
                                  channel_sub_type=SUB_TYPE.get(device_type),
                                  **org_info_dict,
                                  se_longitude=se_longitude,
                                  se_latitude=se_latitude,
                                  )

        res = app.send_by_rest('/api/demo@post', json=body, check=check)

        return res

    @classmethod
    def add_face_tollgate_device(cls, ip_port, device_name=None, org_name="本域",
                                 se_longitude=(105.5, 106.5), se_latitude=(29.0, 30.0), check=False):
        """添加人脸卡口设备列表

        Args:
            ip_port (str): '1.1.1.1_80'形式
            device_name (str): 设备名
            org_name (str): 组织名
            se_longitude (tuple): 经度范围，如(105.5, 106.5)
            se_latitude (tuple): 纬度范围，如(29.0, 30.0)
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        return cls.add_tollgate_device_by_rest_via_kw(ip_port=ip_port, device_name=device_name, org_name=org_name,
                                                      device_type="人脸卡口",
                                                      se_longitude=se_longitude, se_latitude=se_latitude, check=check)

    @classmethod
    def add_vehicle_tollgate_device(cls, ip_port, device_name=None, org_name="本域",
                                    se_longitude=(105.5, 106.5), se_latitude=(29.0, 30.0), check=False):
        """添加车辆卡口设备列表

        Args:
            ip_port (str): '1.1.1.1_80'形式
            device_name (str): 设备名
            org_name (str): 组织名
            se_longitude (tuple): 经度范围，如(105.5, 106.5)
            se_latitude (tuple): 纬度范围，如(29.0, 30.0)
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        return cls.add_tollgate_device_by_rest_via_kw(ip_port=ip_port, device_name=device_name, org_name=org_name,
                                                      device_type="车辆卡口",
                                                      se_longitude=se_longitude, se_latitude=se_latitude, check=check)


if __name__ == '__main__':
    pass
