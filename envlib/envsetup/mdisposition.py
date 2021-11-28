#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File:    mdidposition.py
"""
多维布控类预置库
"""

from copy import deepcopy
from loguru import logger

from envlib.envsetup.udm import Udm
from envlib.env.globals import current_app as app
from envlib.env.globals import g
from envlib.env.helpers import GetKeysMixin

from envlib.env_resources.preset_data import multi_face_national_data, multi_vehice_data

__all__ = ['MDisposition', ]


class MDisposition(GetKeysMixin):
    """多维布控类"""

    def __init__(self):
        """初始化参数"""
        pass

    @classmethod
    def query_tree_node_by_rest(cls):
        """查询配置中心平台下各类型id

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='mdiposition_tree_node_list', value=平台下各类型id

        Returns:
            rest平台下各类型id

        """

        res = app.send_by_rest('/api/demo@get', check=False)
        app.bind_to_g(key='mdiposition_tree_node_list', value=res[0].get('childs'), lock=False)
        return res[0].get('childs')  # 默认平台下各类型id

    @classmethod
    def create_vehicle_disposition_by_rest(cls, task_name="", before="0d", after="30d", notify=0, plat_no="渝A123456",
                                           org_name="黄竹路28号1栋", device_name="mipc_10.4.32.131"):
        """新建车辆布控任务

        Args:
            task_name(str): 布控任务名称 (Default value = "")
            before(str): 布控开始时间，默认0为当前时间 (Default value = "0d")
            after(str): 布控结束时间，默认布控30天有效 (Default value = "30d")
            notify(int): 是否有告警弹窗，默认0无弹窗，1有弹窗 (Default value = 0)
            plat_no(str): 车牌号 (Default value = "渝A123456")
            org_name(str): 设备所属组织，默认为multi_disposition (Default value = "multi_disposition")
            device_name(str): 布控设备的名称 (Default value = "multi_vehilce")

        Returns:
            rest接口返回值

        """
        begin_mills, end_mills = app.ssh.get_time_quantum_stamp(before=before, after=after, accuracy="ms")
        Udm.query_vehicle_tollgate_channel_list_by_rest_via_org_name(org_name=org_name)
        source_id = g.getk('udm_vehicle_channel_list').extracting('ape_id',
                                                                  filter={'owner_aps_name': device_name + "_设备_1"})

        data = deepcopy(multi_vehice_data)
        notify_type_list = [1] if notify else [0]
        MDisposition.query_tree_node_by_rest()
        node_id = g.getk('mdiposition_tree_node_list').extracting('node_id', filter={'node_name': '车辆维度'})
        data["node_id"] = node_id
        data["device_ids"] = [source_id]
        data["begin_mills"] = str(begin_mills)
        data["end_mills"] = str(end_mills)
        data["name"] = task_name
        data["notify_type_list"] = notify_type_list
        data["differentiated_info"]["plate_info"]["number"] = plat_no[1:]
        data["differentiated_info"]["plate_info"]["plate"] = plat_no
        data["differentiated_info"]["plate_info"]["plate_no"] = plat_no
        res = app.send_by_rest('/api/demo@post', json=data, check=False)
        logger.info(res)
        return res

    @classmethod
    def create_face_national_disposition_by_rest(cls, task_name="", before="0d", after="30d", notify=True, ):

        """新建人像民族布控任务, 并绑定到环境变量'multi_disposition' tag下

        Args:
            task_name(str): 布控任务名称 (Default value = "")
            before(str): 布控开始时间，默认0为当前时间 (Default value = "0d")
            after(str): 布控结束时间，默认布控30天有效 (Default value = "30d")
            notify(int): 是否有告警弹窗，默认0无弹窗，1有弹窗 (Default value = True)

        Returns:
            rest接口返回值

        """
        data = deepcopy(multi_face_national_data)
        begin_mills, end_mills = app.ssh.get_time_quantum_stamp(before=before, after=after, accuracy="ms", )
        '''人脸算法ID获取'''
        algorithm_id = ""
        data_algorithm = {'page_num': 0, 'page_size': 20, 'algorithm_type': 0}
        res_algorithm = app.send_by_rest('/api/demo@get', params=data_algorithm,
                                         check=False)
        for res_algorithm in res_algorithm.get("data"):
            if res_algorithm.get("is_run") == 1:  # 1表示算法运行
                algorithm_id = res_algorithm.get("algorithm_id")
        algorithm_version = list()
        if algorithm_id:
            algorithm_version.append(algorithm_id)
        else:
            return logger.error("人脸算法不存在，无法创建人像布控任务")
        notify_type_list = [1] if notify else [0]

        MDisposition.query_tree_node_by_rest()
        node_id = g.getk('mdiposition_tree_node_list').extracting('node_id', filter={'node_name': '人像维度'})
        data["node_id"] = node_id
        data["begin_mills"] = str(begin_mills)
        data["end_mills"] = str(end_mills)
        data["name"] = task_name
        data["notify_type_list"] = notify_type_list
        data["differentiated_info"]["algorithm_version"] = algorithm_version

        res = app.send_by_rest('/api/demo@post', json=data, check=False)
        app.bind_to_g(key='multi_disposition_task_id', value=res, lock=False)
        return res

    @classmethod
    def query_multi_disposition_task_by_rest(cls, task_name=""):
        """根据布控任务名称查询布控任务信息

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='mdisposition_task_list', value=布控任务信息

        Args:
            task_name(str): 查询任务名称 (Default value = "")

        Returns:
            rest布控任务信息

        """

        json_data = {
            "search": task_name,
            "page_num": 1,
            "page_size": 1000,
            "begin": "",
            "end": ""
        }

        res = app.send_by_rest('/api/demo@post', json=json_data, check=False)
        app.bind_to_g(key='mdisposition_task_list', value=res.get('data'), lock=False)  # app.send_by_rest默认剥离第一层data
        return res.get('data')

    @classmethod
    def delete_mult_disposition_task_by_rest(cls, task_name=''):
        """删除指定布控任务

        Args:
            task_name(str): 查询任务名称 (Default value = "")

        Returns:
            rest查询结果

        """

        task_ids = list()
        MDisposition.query_multi_disposition_task_by_rest()
        task_id = g.getk('mdisposition_task_list').extracting('id', filter={'name': task_name})
        task_ids.append(task_id)
        json_data = {"ids": task_ids}
        res = app.send_by_rest('/api/demo@delete', json=json_data, check=True)
        return res


if __name__ == '__main__':
    pass
