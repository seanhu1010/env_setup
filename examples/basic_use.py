#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    basic_use.py
# @Time:    2021/07/20
"""
基本使用
"""

# level0
from envlib.envsetup.k8s import K8s  # k8s模块
from envlib.envsetup.storage import Storage  # 存储模块
from envlib.envsetup.uuv import Uuv  # 综合管理模块
from envlib.envsetup.kafka import Kafka  # Kafka操作模块

# level1
from envlib.envsetup.cms import Cms  # 视图配置模块
from envlib.envsetup.vms import Vms  # Vms配置模块

# level2
from envlib.envsetup.object import Object  # 对象管理模块
from envlib.envsetup.udm import Udm  # 设备管理模块

# level3
# from envlib.envsetup.fullanalysis import FullAnalysis  # 全量解析模块
# from envlib.envsetup.mdisposition import MDisposition  # 多维布控模块
from envlib.envsetup.mda import Mda  # Mda推图模块

# env
from envlib.env.app import Env  # app类
from envlib.env.globals import ctx_stack  # app的上下文堆栈，全局变量
from envlib.env.globals import current_app  # 代理指向当前线程的app实例，全局变量
from envlib.env.globals import g  # 代理指向当前app的存储空间，使用bind_to_g的k,v会存储到此
from envlib.env.globals import env_pools  # Env实例池，主要用于同一session的维持

# env
from envlib.env.app import Env

with Env(8018, 'admin', '123456') as app:
    # 以用户admin进入8018平台，with语句触发上下文，
    # 等同于
    # app=Env(8018, 'admin', '123456')
    # app.push_context()
    # 以下操作和人工使用admin账号，登录8018平台后，查询相关信息无异
    K8s.check_pod_status_by_ssh_via_pod_name(pod_name_key='pg')
    Storage.query_y3000_bucket_storage_quota_via_bucket_name(bucket_name='StoragePath')
    Uuv.query_uuv_department_by_rest()
    Cms.query_cms_platform_config_by_rest()
    Vms.query_vms_config_by_rest()
    Object.get_keys()
    Object.query_person_group_list_by_rest_via_group_name()
    Udm.query_encoder_device_list_by_rest_via_org_name()
# with外自动释放上下文，等同于app.pop_context()，此时会释放掉g


# 如果需要在使用一个用户时，全局保持g，此时需要打开app的debug模式


with Env(8018, 'admin', '123456') as bpp:
    bpp.debug = True
    # 以用户admin进入8018平台，with语句触发上下文，
    # 等同于
    # app=Env(8018, 'admin', '123456')
    # app.push_context()
    # 以下操作和人工使用admin账号，登录8018平台后，查询相关信息无异
    K8s.check_pod_status_by_ssh_via_pod_name(pod_name_key='pg')
    Storage.query_y3000_bucket_storage_quota_via_bucket_name(bucket_name='StoragePath')
    Uuv.query_uuv_department_by_rest()
    Cms.query_cms_platform_config_by_rest()
    Vms.query_vms_config_by_rest()
    Object.get_keys()
    Object.query_person_group_list_by_rest_via_group_name()
    Udm.query_encoder_device_list_by_rest_via_org_name()
# with外自动释放上下文，等同于app.pop_context()
# debug模式下g会暂时存储，只要还是以同一用户同一平台进行操作，g还会维持；反之会释放g

with Env(8018, 'admin', '123456') as cpp:
    cpp.debug = True
    print(1)  # 打断点观察，此时会维持上一Env实例bpp上下文的g
