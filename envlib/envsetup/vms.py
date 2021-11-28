#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File:    vms.py
"""
Vms操作预置库
"""

from copy import deepcopy

from envlib.env.envlogging import logger
from envlib.env.globals import current_app as app
from envlib.env.globals import g
from envlib.env.helpers import GetKeysMixin
from envlib.env_resources.preset_data import VMS_GB_CODE, VMS_GUARD_UPLOAD_IP
from envlib.envsetup.udm import Udm
from envlib.envsetup.uuv import Uuv
from envlib.util import get_last_ip_str
from resources.data import AUTO_CONFIG, STORAGE_CONFIG, HOST_IP

__all__ = ['Vms', ]


class Vms(GetKeysMixin):
    """Vms操作类"""

    def __init__(self):
        pass

    @classmethod
    def query_vms_config_by_rest(cls, check=False):
        """查询VMS配置-参数设置

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='vms_config',value=查询接口返回值，VMS参数设置

        Args:
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest查询接口返回值，VMS参数设置

        """

        res = app.send_by_rest('/api/demo@get', check=check)
        app.bind_to_g(key='vms_config', value=res.get('result_data'), lock=False)
        return res.get('result_data')

    @classmethod
    def config_vms_config_by_rest_via_json(cls, json, check=False):
        """传入json,配置VMS配置-参数设置

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@get', json=json, check=check)

        return res

    @classmethod
    def config_vms_gb_code(cls):
        """设置VMS配置-参数设置-GB配置

        Returns:
            rest接口返回值

        """

        _vms_gb_code = cls.query_vms_config_by_rest()[30].get('configPar1')  # vms平台国标编码对应配置项30
        if _vms_gb_code == VMS_GB_CODE:  # 已配置
            pass
        else:  # 未配置,则配置
            vms_gb_code_json = [{
                "id": 31,
                "configType": 31,
                "configName": "平台国标编码",
                "configSeq": 1,
                "configPar1": VMS_GB_CODE,
                "configPar2": None,
                "configPar3": None,
                "stat": 1,
                "updated": 1
            }]
            cls.config_vms_config_by_rest_via_json(json=vms_gb_code_json)

    @classmethod
    def config_vms_guard_upload(cls):
        """设置VMS配置-参数设置-门禁设置

        Returns:
            rest接口返回值

        """

        _vms_guard_upload_ip = cls.query_vms_config_by_rest()[27].get(
            'configPar1')  # 对应配置项27
        if _vms_guard_upload_ip == VMS_GUARD_UPLOAD_IP:  # 已配置
            pass
        else:  # 未配置,则配置
            vms_guard_set_json = [
                {
                    "id": 28,
                    "configType": 28,
                }
            ]
            cls.config_vms_config_by_rest_via_json(json=vms_guard_set_json)

    @classmethod
    def add_vms_storage_by_rest_via_json(cls, json, check=False):
        """传入json，配置vms存储

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', json=json, check=check)

        return res

    @classmethod
    def query_vms_storage_list_by_rest(cls, check=False):
        """查询VMS已配置的存储

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='vms_storage_list',value=查询接口返回值, VMS已配置的存储list

        Args:
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值, VMS已配置的存储list

        """

        vms_storage_list_json = {
            "pageSize": "200",
            "pageNo": 1,
            "totalPage": 0,
            "order": "desc",
            "orderBy": "id",
            "condition": {
                "serviceType": 1
            }
        }

        res = app.send_by_rest('/api/demo@post', json=vms_storage_list_json, check=check)
        app.bind_to_g(key='vms_storage_list', value=res.get('result_data'), lock=False)
        return res.get('result_data')

    @classmethod
    def query_vms_evc_storage_info_by_rest(cls, check=False):
        """查询evc存储容量信息

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='vms_evc_storage_info',value=查询接口返回值，evc存储容量信息

        Args:
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值，evc存储容量信息

        """

        vms_get_evc_storage_cap_json = {
            "type": 4,
            "name": "st",
            "serverIP": "{}".format(STORAGE_CONFIG.get('cm_ip')),
            "serverPort": "9001"
        }

        res = app.send_by_rest('/api/demo@post', json=vms_get_evc_storage_cap_json,
                               check=check)
        app.bind_to_g(key='vms_evc_storage_info', value=res.get('result_data'), lock=False)
        return res.get('result_data')

    @classmethod
    def add_vms_storage_plan_template_by_rest(cls, check=False):
        """vms业务设置-录像管理-录像计划模板

        Args:
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        vms_storage_plan_template_alltime_2m_json = {
            "name": AUTO_CONFIG.get('vms_storage_plan_template_name'),
            "streamType": 0,
            "storagePlanTimeIndex": 1,
            "streamRate": 2,
            "reserveDay": "7",
            "oneRouteQuota": 148
        }

        app.send_by_rest('/api/demo@post',
                         json=vms_storage_plan_template_alltime_2m_json, check=check)
        res = cls.query_vms_storage_plan_template_by_rest()

        return res

    @classmethod
    def query_vms_storage_plan_template_by_rest(cls, check=False):
        """查询vms业务设置-录像管理-录像计划模板

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='vms_storage_plan_template',value=查询接口返回值，录像计划模板

        Args:
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值，录像计划模板

        """

        query_vms_storage_plan_template_json = {
            "order": "desc",
            "pageSize": 200,
            "pageNo": 1
        }
        res = app.send_by_rest('/api/demo@post',
                               json=query_vms_storage_plan_template_json, check=check)
        app.bind_to_g(key='vms_storage_plan_template', value=res.get('result_data'), lock=False)
        return res.get('result_data')

    @classmethod
    def query_vms_storageplan_list_by_rest(cls, check=False):
        """查询vms录像计划列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='vms_storageplan_list',value=查询接口返回值，录像计划列表

        Args:
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值，录像计划列表

        """

        _json = {
            "orderBy": "id",
            "order": "desc",
            "pageSize": 200,
            "pageNo": 1
        }

        res = app.send_by_rest('/api/demo@post', json=_json, check=check)
        app.bind_to_g(key='vms_storageplan_list', value=res.get('result_data'), lock=False)
        return res.get('result_data')

    @classmethod
    def query_vms_storageplan_detail_by_rest_via_record_id(cls, record_id, check=False):
        """查询录像计划详情

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='vms_storageplan_detail',value=查询接口返回值，查询录像计划详情

        Args:
            record_id (str): 录像计划id
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值，查询录像计划详情

        """

        res = app.send_by_rest(f'/api/demo@get', check=check)
        app.bind_to_g(key='vms_storageplan_detail', value=res.get('result_data'), lock=False)
        return res.get('result_data')

    @classmethod
    def add_vms_storageplan_by_rest_via_json(cls, json, check=False):
        """添加设备录像

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@post', json=json, check=check)

        return res

    @classmethod
    def modify_vms_storageplan_by_rest_via_json(cls, json, check=False):
        """修改设备录像

        Args:
            json (any): json数据结构
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值

        """

        res = app.send_by_rest('/api/demo@put', json=json, check=check)

        return res

    @classmethod
    def query_vms_storageplan_used_channel_list_by_rest(cls, check=False):
        """查询vms录像计划已使用的通道列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='vms_storage_list',value=查询接口返回值，录像计划已使用的通道列表

        Args:
            check (bool): 接口返回状态码校验，默认不校验

        Returns:
            rest接口返回值，录像计划已使用的通道列表

        """

    @classmethod
    def add_vms_storage_from_env_ini(cls):
        """根据env_ini中预设的存储配置，添加存储，当前仅支持sdk添加转存

        Returns:
            rest接口返回值，录像计划列表

        """

        _vms_storage_list = cls.query_vms_storage_list_by_rest()
        if _vms_storage_list:
            pass
        else:  # 未添加存储
            vms_add_y3000_transit_json = {
                "type": 4,
                "name": STORAGE_CONFIG.get('vms_storage_name'),
                "serverIP": STORAGE_CONFIG.get('cm_ip'),
                "serverPort": "9001",
                "place": STORAGE_CONFIG.get('vms_storage_quota'),
                "storagePath": "StoragePath{}".format(get_last_ip_str(HOST_IP)),
                "diskFullcoverPercent": "99",
                "isDirect": 0,
                "serviceType": 1,
                "installService": False
            }

            _res = cls.add_vms_storage_by_rest_via_json(json=vms_add_y3000_transit_json)
            if _res.get('result_code') != '0':  # 存储目录<6000G,减小容量重新添加,配置为当前可用容量的一半继续添加

                _free_capacity = cls.query_vms_evc_storage_info_by_rest().get('free_capacity')
                _vms_add_y3000_transit_json = deepcopy(vms_add_y3000_transit_json)
                _vms_add_y3000_transit_json.update(place=str(int(_free_capacity / 2)))
                _res = cls.add_vms_storage_by_rest_via_json(json=_vms_add_y3000_transit_json)
            _vms_storage_list = cls.query_vms_storage_list_by_rest()

        return _vms_storage_list

    @classmethod
    def query_vms_storageplan_detail_channel_list_via_record_name(cls, record_name):
        """根据录像计划的名称，查询vms录像计划详详情中的设备列表

        Args:
            record_name (str): 录像计划名称

        Returns:
            rest接口返回值，录像计划详详情中的设备列表

        """

        cls.query_vms_storageplan_list_by_rest()
        try:
            record_id = g.getk('vms_storageplan_list'). \
                extracting('id', filter={'name': record_name})

            storageplan_detail_channel_list = cls.query_vms_storageplan_detail_by_rest_via_record_id(
                record_id=record_id).get('channels')
        except ValueError:
            logger.warning(f'录像计划 "{record_name}" 未创建')
            storageplan_detail_channel_list = []

        return storageplan_detail_channel_list

    @classmethod
    def add_vms_storage_plan_template_from_env_ini(cls):
        """根据env.ini中的 ``vms_storage_plan_template_name`` 设置存储计划模板，默认存7天，全天录制，2M码率

        Returns:
            rest接口返回值

        """

        _vms_storage_plan_template_list = cls.query_vms_storage_plan_template_by_rest()
        if _vms_storage_plan_template_list:
            _exist_storage_plan_template = \
                [_plan_template for _plan_template in _vms_storage_plan_template_list if
                 _plan_template.get('name') == AUTO_CONFIG.get('vms_storage_plan_template_name')]
        else:
            _exist_storage_plan_template = None

        if not _exist_storage_plan_template:  # 未添加存储计划模板
            _res = cls.add_vms_storage_plan_template_by_rest()
            _vms_storage_plan_template_list = cls.query_vms_storage_plan_template_by_rest()
            _exist_storage_plan_template = \
                [_plan_template for _plan_template in _vms_storage_plan_template_list if
                 _plan_template.get('name') == AUTO_CONFIG.get('vms_storage_plan_template_name')]

        return _exist_storage_plan_template

    @classmethod
    def add_vms_storageplan_from_env_ini(cls, record_quantity,
                                         record_name=AUTO_CONFIG.get('vms_storage_plan_record_name'),
                                         org_name='本域'):
        """根据env.ini中的 ``vms_storage_plan_record_name`` 添加默认录像计划

        Args:
            record_quantity (int): 录像计划配额
            record_name (str): 录像计划名称
            org_name (str): 设备所属组织

        Returns:
            rest接口返回值，录像计划详详情中的设备列表

        """

        # 获取组织id
        Uuv.query_uuv_organization_by_rest()
        org_index = g.getk('uuv_organization_list').extracting('org_index',
                                                               filter={'org_name': org_name})

        # 查询已有录像计划的设备通道编码列表
        used_channel_list = cls.query_vms_storageplan_used_channel_list_by_rest().get(org_index)

        # 查询设备列表
        Udm.query_encoder_face_tollgate_vehicle_tollgate_channel_list_by_rest_via_org_name(org_name=org_name,
                                                                                           include_child=False)
        if used_channel_list:  # 已有录像计划
            # 提取有可用的channel_list
            _channel_list = g.getk('udm_encoder_face_tollgate_vehicle_tollgate_channel_list'). \
                extracting('ape_id', 'org_index', filter=lambda x: x['ape_id'] not in used_channel_list)
            if _channel_list is None:
                _channel_list = []
        else:  # 无录像计划
            _channel_list = g.getk('udm_encoder_face_tollgate_vehicle_tollgate_channel_list'). \
                extracting('ape_id', 'org_index')
            if _channel_list is None:
                _channel_list = []

        # 添加存储，并绑定到环境变量
        cls.add_vms_storage_from_env_ini()
        _storage_index = g.getk('vms_storage_list'). \
            extracting('id', filter={'name': STORAGE_CONFIG.get('vms_storage_name')})

        # 添加录像计划模板，并绑定到环境变量
        cls.add_vms_storage_plan_template_by_rest()
        _template_index, _quota = g.getk('vms_storage_plan_template'). \
            extracting('id', 'oneRouteQuota', filter={'name': AUTO_CONFIG.get('vms_storage_plan_template_name')})

        # 查询已存在的录像计划，并绑定到环境变量
        cls.query_vms_storageplan_list_by_rest()

        # post的json模板
        _json = {}

        # 获取录像计划id
        _record_id = g.getk('vms_storageplan_list'). \
            extracting('id', filter={'name': record_name})

        if _record_id:

            logger.debug(f'录像计划 {record_name} 已添加，将修改录像计划')

            # 已添加录像计划，将提取已添加的通道信息，并与预期的数量进行判断
            storageplan_detail_channel_list = cls.query_vms_storageplan_detail_channel_list_via_record_name(
                record_name=record_name)

            assert len(_channel_list) + len(storageplan_detail_channel_list) >= record_quantity, \
                f'{org_name}组织下设备数据少于预期值{record_quantity}, 请调用Device.add_encoder_onvif进行添加'

            if record_quantity <= len(storageplan_detail_channel_list):
                # 预期需要添加的通道数量record_quantity <= 已添加录像计划通道数量, 将调整为所需要的数量
                logger.warning(
                    f'预期需要添加的通道数量{record_quantity} <= 已添加录像计划通道数量{len(storageplan_detail_channel_list)}, 将调整为所需要的数量')
                channels = [{"channelCode": item['channelCode'], "orgIndex": item['orgIndex']} for item in
                            storageplan_detail_channel_list[:record_quantity]]
            else:
                # 预期需要添加的通道数量record_quantity >= 已添加录像计划通道数量, 将从_channel_list中追加
                channels = [{"channelCode": item['channelCode'], "orgIndex": item['orgIndex']} for item in
                            storageplan_detail_channel_list]
                channels = channels + [{"channelCode": item[0], "orgIndex": item[1]} for item in
                                       _channel_list[:record_quantity - len(storageplan_detail_channel_list)]]

            _json.update(channels=channels, id=_record_id)
            cls.modify_vms_storageplan_by_rest_via_json(json=_json)
            cls.query_vms_storageplan_detail_channel_list_via_record_name(record_name=record_name)

        else:
            logger.info(f'录像计划 {record_name} 未添加，将添加录像计划')

            assert len(_channel_list) >= record_quantity, \
                f'{org_name}组织下设备数据少于预期值{record_quantity}, 请调用Device.add_encoder_onvif进行添加'

            channels = [{"channelCode": item[0], "orgIndex": item[1]} for item in _channel_list[:record_quantity]]
            _json.update(channels=channels)
            cls.add_vms_storageplan_by_rest_via_json(json=_json)
            cls.query_vms_storageplan_detail_channel_list_via_record_name(record_name=record_name)


if __name__ == '__main__':
    pass
