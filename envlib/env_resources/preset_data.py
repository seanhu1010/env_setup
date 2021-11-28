#!/usr/bin/python
# -*- coding=utf-8 -*-
"""
预置body
"""

import configparser
import os

from resources.data import HOST_IP

# ========解析env.ini,路径常量========
resources_path = os.path.dirname(__file__)
resources_path_super = os.path.split(resources_path)[0]
root_path = os.path.split(resources_path_super)[0]
config = configparser.ConfigParser()
config_file = os.path.join(root_path, 'env.ini')
config.read(config_file, encoding='utf-8')

# ========设备添加相关========
# 枚举变量-资源类型
RESOURCE_TYPE = {
    "编码器": "xyz",
    "解码器": "xyz",
    "卡口": "xyz",
    "通道": "xyz",
    "门禁设备": "xyz",
    "报警设备": "xyz",
    "RFID": "xyz",
    "流量设备": "xyz",
    "诱导屏": "xyz",
    "信号机": "xyz",
    "移动警务": "xyz",
    "采集设备": "xyz",
    "采集系统": "xyz",
    "访客机": "xyz",
    "网络键盘": "xyz",
    "拼控器": "xyz",
}

# 枚举变量-设备子类型
SUB_TYPE = {
    "IPC": "xyz",
    "NVR": "xyz",
    "DVR": "xyz",
    "MDVR": "xyz",
    "MTU300": "xyz",
    "拼控器": "xyz",
    "编码器": "xyz",
    "解码器": "xyz",
    "报警输入": "xyz",
    "人脸卡口": "xyz",
    "车辆卡口": "xyz",
    "门禁设备": "xyz",
    "访客机": "xyz",
}

# 枚举变量-厂商类型
PRODUCER = {
    "UVW": "xyz",
    "海康": "xyz",
    "大华": "xyz",
    "艾礼富": "xyz",
    "宇视": "xyz",
    "科达": "xyz",
    "旷世": "xyz",
    "其他厂商": "-1",
    "不存在的厂商1": "xyz",
    "不存在的厂商2": "xyz"
}

# 枚举变量-接入方式
ACCESS_TYPE = {
    "私有SDK": "xyz",
    "主动注册": "xyz",
    "Onvif": "xyz",
    "GB28181": "xyz"
}

# 枚举变量-在线状态
IS_ONLINE = {
    "在线/启用": "xyz",
    "离线/停用": "xyz",
    "登录中": "xyz",
    "登陆失败": "-2",
    "其他/异常": "xyz",
}

# 枚举变量-报警主机设备子类型
SUB_TYPE_ALARM = {
    "TNW-9400": "xyz",
    "Other": "xyz"
}

# 枚举变量-协议类型
SDK_TYPE = {
    "SDK": "xyz",
    "UVW-M1": "xyz",
    "UVW-M2": "xyz",
    "UVW-Y": "xyz"
}

# 文件格式转换字典
content_type_dict = {
    "xls": "application/vnd.ms-excel",
    "zip": "application/x-zip-compressed",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "jpg": "image/jpeg",
    "png": "image/png",
    "jpeg": "image/jpeg",
}

# ========门禁相关========
# REGISTER_ID = config.get('visitor', 'register_id')

# 门禁相关
GUARD_TYPE = {
    "人脸门禁": "xyz",
    "门禁控制器": "xyz",
    "IPC": "xyz"
}

# ========视图库相关========
# 修改平台GB编码，传参
last_ip_string = ''.join(HOST_IP.split('.')[-2:])  # 取平台IP后2段组成字符串，如1.1.1.1
VMS_GB_DEFAULT_CODE = '50010000002000000001'
VMS_GB_CODE = VMS_GB_DEFAULT_CODE[:20 - len(last_ip_string)] + last_ip_string  # 用11694替换默认平台编码后5位

# ========VMS相关========
# VMS门禁设置，传参，默认设置上报综合安防地址，门禁数据推送视图库
VMS_GUARD_UPLOAD_IP = HOST_IP + ":40087"

# ========对象管理相关========
# 各对象分组类型
OBJECT_GROUP_TYPE = {
    "人员": {
        "静态库": "xyz",
        "黑名单": "xyz",
        "白名单": "xyz",
        "普通分组": "xyz",
        "客流密度底库": "-1",
        "无感考勤": "xyz",
        "门禁考勤": "xyz"
    },
    "车辆": {
        "黑名单": "xyz",
        "白名单": "xyz",
        "红名单": "xyz",
    },
    "房屋": {"普通分组": "xyz"},
}

# 对象字典
OBJECT_TYPE = {
    "人员": "omperson",
    "车辆": "omvehicle",
    "房屋": "omhouse",
}

# ========CMS相关========
# cms_platform
cms_system_config_data = {
    "localCode": "xyz",
    "orgCode": "xyz",
    "placeCode": "xyz",
    "username": "admin",
    "password": "MTIzNDU2",
    "ip": HOST_IP,
    "port": "xyz",
    "placeName": "500000,500100"
}

# cms一人一档配置
cms_archive_config_data = {
    "threshold": 0,  # 聚档阈值75
    "confirm_threshold": 0,  # 置信阈值75
    "confirm_type": 0,
    "algorithm_id": "xyz",
    "mode": 0  # 置信模式全库
}

CMS_STORAGE_DIRECTORY = {
    "scenefaces": {"storage_id": "xyz",
                   "storage_info": [{"data_type": 0, "capacity": 0, "params": "{\"strategy\":\"0\"}"}]},
    "featurefaces": {"storage_id": "xyz",
                     "storage_info": [{"data_type": 0, "capacity": 0, "params": "{\"strategy\":\"0\"}"}]},
}

CMS_STORAGE_TYPE = {
    "scenefaces": 0,
}

# ========多维布控任务========
# 新建车辆布控任务
multi_vehice_data = {
    "name": "vehicle_auto_1",
    "node_id": "e684a66609d54f6595bb29c8677b1f44",
    "resource_type": "xyz",
    "target_type": 0,
    "auth_user_code_list": [],
    "notify1": "true",
    "differentiated_info": {
        "disposition_type": "E_Car_1",
        "priority_level": "xyz",
        "plate_info": {
            "local": "xyz",
            "number": "A123456",
            "colorList": [{
                "code": "xyz",
                "name": "黄",
                "remark": "#ffcc00"
            }, {
                "code": "xyz",
                "name": "蓝",
                "remark": "#188feb"
            }, {
                "code": "xyz",
                "name": "绿",
                "remark": "#36c13c"
            }, {
                "code": "xyz",
                "name": "黑",
                "remark": "#000000"
            }, {
                "code": "xyz",
                "name": "白",
                "remark": "#ffffff"
            }],
            "plate": "渝A123456",
            "plate_no": "渝A123456",
            "plate_ownership_code": "xyz"
        }
    },
    "device_ids": ["xyz"],
    "begin_mills": 0,
    "end_mills": 0,
    "disposition_to": 0,
    "notify_type_list": [1]
}

# 新建人像民族布控
multi_face_national_data = {
    "name": "民族布控",
    "node_id": "9f1a99187f2d4c149af754199cdf4e9a",
    "resource_type": "xyz",
    "target_type": 0,
    "auth_user_code_list": [],
    "notify1": "true",
    "differentiated_info": {
        "disposition_type": "E_Per_1",
        "priority_level": "xyz",
        "algorithm_version": ["xyz"],
        "nation": "xyz"
    },
    "begin_mills": 0,
    "end_mills": 0,
    "disposition_to": 0,
    "notify_type_list": [1]
}

# 新建人像单对象布控
multi_face_single_data = {
    "name": "单人布控",
    "node_id": "9f1a99187f2d4c149af754199cdf4e9a",
    "resource_type": "xyz",
    "target_type": 0,
    "auth_user_code_list": [],
    "notify1": "true",
    "differentiated_info": {
        "disposition_type": "E_Per_1",
        "priority_level": "xyz",
        "algorithm_version": ["xyz"],
        "threshold": 0,
        "target_image_uri": "data:image/jpeg;base64,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",
        "name": "face",
        "gender": "xyz",
        "birthday": ""
    },
    "begin_mills": 0,
    "end_mills": 0,
    "disposition_to": 0,
    "notify_type_list": [1]
}

# 白名单布控
multi_face_tab_data = {
    "name": "人像白名单布控",
    "node_id": "9f1a99187f2d4c149af754199cdf4e9a",
    "resource_type": "xyz",
    "target_type": 0,
    "auth_user_code_list": [],
    "notify1": "true",
    "differentiated_info": {
        "disposition_type": "E_Per_1",
        "priority_level": "xyz",
        "algorithm_version": ["xyz"],
        "threshold": 0
    },
    "tab_id_type": 0,
    "tab_id_list": ["xyz"],
    "begin_mills": 0,
    "end_mills": 0,
    "disposition_to": 0,
    "notify_type_list": [1]
}

# ========解析相关========
# 算力查询-解析类型
product_type = {
    "人脸": 0,
    "结构化": 0,
    "车辆": 0
}

# 算力查询-解析类型
service_type = {
    "图片流": 0,
    "视频流": 0,
    "特征对比": 0
}

# 解析任务类型
analysis_type = {
    "人脸实时图片流": 0,
    "人脸实时视频流": 0,
    "人脸在线录像": 0,
    "人脸本地文件": 0,
    "人脸人体实时视频流": 0,
    "人脸人体在线录像": 0,
    "人脸人体本地文件": 0,
    "结构化实时视频流": 0,
    "结构化在线录像": 0,
    "结构化本地文件": 0,
    "结构化图片流": 0,
    "车辆二次解析": 0,
}

# 解析定时设置
cycle_type = {
    "无": 0,
    "按日循环": 0,
    "按周循环": 0,
    "按月循环": 0,
    "定时不循环": 0

}

# 任务优先级
priority_level = {
    "紧急": 0,
    "常规": 0,
    "闲时": 0
}

# 解析类型
source_type = {
    "实时视频流": 0,
    "实时图片流": 0,
    "在线录像": 0,
    "离线文件": 0
}

# ========车辆相关========
# 车牌颜色
VEHICLE_PLATE_COLOR = {
    "绿色": "xyz",
    "蓝色": "xyz",
    "黑色": "xyz",
    "不限": ""
}

# 车辆类型
VEHICLE_CLASS = {
    "客车": "xyz",
    "轿车": "xyz",
    "不限": ""
}

# 车牌类型
PLATE_CLASS = {
    "小型汽车牌号": "xyz"
}

# 车辆品牌
VEHICLE_BRANDS = {
    "奇瑞": ["xyz"],
    "铃木": ["xyz"],
    "马自达": ["xyz"],
    "不限": []
}

# 查询数据类型
VEHICLE_PLATE_RECOGNITION_TYPE = {
    "图像识别": "xyz",
    "rfid识别": "xyz",
    "双基识别": "xyz"
}

# 布控等级
VEHICLE_BASE_PRIORITY_LEVEL = {
    "一级布控": 0,
    "二级布控": 0,
    "三级布控": 0,
}

# 车牌
VEHICLE_PLATE_NO = {
    "不限": ""
}

# 卡口类型
TOLLGATE_TYPE = {
    "人脸卡口": "xyz",
    "车辆卡口": "xyz"
}


# ========添加设备相关========
def func_encoder_body(ip_port, name=None, user_id='admin', password='admin123',
                      org_name="本域", org_index="10", place_code="100000",
                      resource_type=RESOURCE_TYPE.get("编码器"),
                      access_type=ACCESS_TYPE.get("Onvif"),
                      producer=PRODUCER.get("华智"),
                      se_longitude=(105.5, 106.5),
                      se_latitude=(29.0, 30.0),
                      ):
    pass  # demonstrate


def func_visitor_body(ip_port, name, register_id, org_name, org_index, place_code="100000", se_longitude=(105.5, 106.5),
                      se_latitude=(29.0, 30.0), ):
    pass  # demonstrate


def func_guard_body(ip_port, name, password, org_name, org_index, sub_type, place_code="100000",
                    se_longitude=(105.5, 106.5),
                    se_latitude=(29.0, 30.0), ):
    pass  # demonstrate


def func_tollgate_body(ip_port, name, sub_type, channel_sub_type, org_name, org_index, place_code="100000",
                       se_longitude=(105.5, 106.5),
                       se_latitude=(29.0, 30.0), ):
    pass  # demonstrate


# 默认headers（临时鉴权）
headers = {
    "Content-Type": "application/json",
    "charset": "utf-8",
    "User": "username%253Aadmin%2526usercode%253Aadmin"
}

if __name__ == '__main__':
    pass
    resources_path = os.path.dirname(__file__)
    resources_path_super = os.path.split(resources_path)[0]
    root_path = os.path.split(resources_path_super)[0]
    print(root_path)
    config = configparser.ConfigParser()


if __name__ == '__main__':
    pass
