#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    some_principles.py
# @Time:    2021/07/20
"""
测试驱动库的一般准则
"""

# 基础标准：
# 1）绑定绝大多数发生在query函数, 可以使用模块名.get_keys获取绑定值列表，如
# Uuv.get_keys()
# {'uuv_department_list': '函数名: query_uuv_department_by_rest, 含义: '
#                         '传入params，查询部门信息',
#  'uuv_organization_list': '函数名: query_uuv_organization_by_rest, 含义: '
#                           '传入params，查询组织list'}

# 2）绑定的值和函数的返回值保持一致，允许对res的进行加工，如以下函数bind_to_g中绑定的value与return应一致
# @classmethod
# def query_uuv_organization_by_rest(cls, check=False, **kwargs):
#     """传入params，查询组织list"""
#     params = {'type': 0, 'page_index': 1, 'page_size': 200}
#     params.update(**kwargs)
#
#     res = app.send_by_rest('/api/demo@get', params=params, check=check)
#     app.bind_to_g(key='uuv_organization_list', value=res.get('data'), lock=False)
#     return res.get('data')

# 3）key命名方式:
# 绑定的key以 “类名_key实际含义_数据类型”进行命名，value数据类型为字典时，数据类型可省略，如cms_archive_config

# 4）函数命名方式:
# 统一使用 “操作 + 函数实际作用 + 方式 + 方法 + [via_条件]/[from_配置文件]” 的格式来作为函数名称
#       其中“操作”可用字段：添加：create,删除：delete，修改：modify，查询：query，配置，config，操作：do,校验:check，[可选副词batch]
#       “函数实际作用”
#       “方式”可用字段：通过：by，伴随数据：with
#       “方法”可用字段：日志：log，接口：rest，界面：web，抓包：patch，数据库：database，远程共享目录：smb
#       ”可选“，[via_条件]/[from_配置文件]，条件可用字段：单个条件：something, 多个条件：kw, json体：json, data体：data
# 示例:
# 通过rest方法，传入单个条件org_name,查询组织下编码器,人脸卡口，车辆卡口通道列表
# query_encoder_face_tollgate_vehicle_tollgate_channel_list_by_rest_via_org_name
# 通过rest方法，传入json体，检索对象管理-人员列表
# query_person_manage_person_list_via_json
# 通过rest方法，传入多个参数，新建分组
# add_object_group_by_rest_via_kw

# 5）区分函数是否可直接调用：
# 不含via及含单个条件如(query_encoder_channel_list_by_rest_via_org_name)的函数能直接调用
# 含多个条件via_kw, 及传入特定数据via_json, via_data, via_params的函数不推荐直接调用
