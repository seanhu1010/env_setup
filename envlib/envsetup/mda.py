#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @File:    mda.py
"""
Mda推图预置库
"""

import os
import json as json_tool
import random
import time

from envlib.env.envlogging import logger

from envlib.rest import Rest
from envlib.env.globals import current_app as app
from envlib.util import get_time, random_plate_no, time_type_change, random_number

from resources.data import SMB_SHARE_PATH, headers, HOST_IP

__all__ = ['Mda', ]


class Mda(object):
    """Mda推图的类"""

    @classmethod
    def push_face_data_to_mda_by_rest_via_kw(cls, channel_id, base_64, **kwargs):
        """模拟推送人脸小图数据到mda

        Args:
            channel_id(str): 卡口通道id
            base_64(str): 人脸小图的base_64编码
            **kwargs: 可选字典项

        Returns:
            None

        """
        _time = get_time(is_time_stamp=False, time_type="%Y%m%d%H%M%S")

        body = {
            "FaceListObject": {
                "FaceObject": [
                    {
                        "FaceID": f"{channel_id}02{_time}000620{random.randint(100000, 999998)}",
                        "DeviceID": channel_id,
                        "LocationMarkTime": _time,
                        "PersonAppearTime": _time,
                        "LeftTopX": 0,
                        "LeftTopY": 0,
                        "RightBtmX": 0,
                        "RightBtmY": 0,
                        "IsDriver": 2,
                        "SourceID": 11111111111111111111111111111111111111111,
                        "IsSuspectedTerrorist": 2,
                        "IsCriminalInvolved": 2,
                        "IsDetainees": 2,
                        "IsVictim": 2,
                        "IsSuspiciousPerson": 2,
                        "IsForeigner": 2,
                        "InfoKind": 1,
                        "SubImageList": {
                            "SubImageInfoObject": [
                                {
                                    "ImageID": 11111111111111111111111111111111111111111,
                                    "DeviceID": channel_id,
                                    "EvenSort": 1,
                                    "Type": "11",
                                    "FileFormat": "Jpeg",
                                    "Data": base_64
                                }
                            ]
                        }
                    }
                ]
            }
        }
        body["FaceListObject"]["FaceObject"][0].update(kwargs)

        url = "/demo/Faces@post"
        res = Rest(host=f"http://{HOST_IP}:2530").send(url=url, headers=headers, json=body)
        if res.status_code != 201:
            logger.debug(f"状态码校验失败，期望值为200，实际值为{res.status_code}，接口响应为{res.content}")
        logger.debug(f"人脸推图成功，通道id为{channel_id}")

    @classmethod
    def push_single_face_data_to_mda_via_kw(cls, channel_id, file_name="person.jpg", file_relative_path="images", **kwargs):
        """模拟推送单张人脸小图数据到mda,读取远端目录文件夹下的某个小图文件，依次推送

        Args:
            channel_id (str): 卡口通道id
            file_name (str): 人脸小图文件名
            file_relative_path (str): 相对远程目录，根目录为env.ini文件中的smb_share
                ``\\\\1.1.1.1\\info\\auto\\`` , (Default value = "images")

        Returns:
            None

        """

        base_64 = app.smb_get_base64(file_name, file_relative_path)
        cls.push_face_data_to_mda_by_rest_via_kw(channel_id=channel_id, base_64=base_64, **kwargs)

    @classmethod
    def batch_push_face_data_to_mda_via_kw(cls, channel_id, file_relative_path="auto_faces", slot=0, **kwargs):
        """批量推送一个文件夹下的人脸小图数据到mda, 读取远端目录文件夹下的某个小图文件，依次推送

        Args:
            channel_id (str): 卡口通道id
            file_relative_path (str): 相对远程目录，根目录为env.ini文件中的smb_share
                ``\\\\1.1.1.1\\info\\auto\\``, (Default value = "auto_faces")
            slot (int): 推图时间间隔(s), (Default value = 0)

        Returns:
            None

        """
        _pics = app.smb.scandir(os.path.join(SMB_SHARE_PATH, file_relative_path))
        for _pic in _pics:
            time.sleep(slot)
            _base_64 = app.smb_get_base64(_pic.name, file_relative_path)
            cls.push_face_data_to_mda_by_rest_via_kw(channel_id=channel_id, base_64=_base_64, **kwargs)

    @classmethod
    def push_vehicle_data_to_mda_by_rest_via_kw(cls, channel_id, base_64, **kwargs):
        """模拟推送车辆数据到mda

        Args:
            channel_id (str): 通道id
            base_64 (str): 图片base64
            **kwargs: 可选字典项

        Keyword Args:
            tollgate_id (str): 卡口id，不是卡口可不传
            plate_no (str): 车牌号
            lane_no (int):车道编号 1~8，车道1~车道8
            direction (str): 方向，1~8，1东、2西、3南、4北、5东北、6西南、7东南、8西北

        Returns:
            None

        """

        _timestamp = get_time(stamp13=True)
        _time = time_type_change(_timestamp, is_time_stamp=False, time_type="%Y%m%d%H%M%S")
        _number_5 = random_number(number=5)
        _motor_vehicle_id = f"{channel_id}02{_time}{_number_5}02{_number_5}"
        _source_id = f"{channel_id}02{_time}{_number_5}"
        _plate_no = random_plate_no()

        body = [
            {
                "MotorVehicleID": _motor_vehicle_id,
                "InfoKind": 1,
                "SourceID": _source_id,
                "TollgateID": channel_id,
                "DeviceID": channel_id,
                "storageUrlCloseShot": "6125/4/featurevehicles/dn@0_0/1/65-3a50644d-3774a",
                "storageUrlPlate": "/featurevehicles/dn@07/1/1-0-2b2a",
                "storageUrlDistantShot": "/featurevehicles/dn@07/1/1-0-2b2a",
                "storageUrlCompound": "/featurevehicles/dn@07/1/1-0-2b2a",
                "storageUrlBreviary": "/featurevehicles/dn@07/1/1-0-2b2a",
                "LeftTopX": 722,
                "LeftTopY": 28,
                "RightBtmX": 1382,
                "RightBtmY": 696,
                # "MarkTime": "20180102101213",
                # "AppearTime": "20180102101213",
                # "DisappearTime": "20180102101214",
                "LaneNo": 1,
                "HasPlate": "1",
                "PlateClass": "02",
                "PlateColor": "5",
                "PlateNo": _plate_no,
                "PlateNoAttach": "",
                "PlateDescribe": "",
                "IsDecked": "1",
                "IsAltered": "0",
                "IsCovered": "0",
                "Speed": 100,
                "Direction": "2",
                "DrivingStatusCode": "0001",
                "VehicleClass": "K33",
                "VehicleBrand": "1",
                "VehicleModel": "迈腾",
                "VehicleStyles": "2019",
                "VehicleLength": 4500,
                "VehicleWidth": 2200,
                "VehicleHeight": 2233,
                "VehicleColor": "1",
                "VehicleColorDepth": "0",
                "VehicleHood": "",  # 车前盖
                "VehicleTrunk": "",  # 车后盖
                "VehicleWheel": "",  # 车轮
                "WheelPrintedPattern": "",
                "VehicleWindow": "",
                "VehicleRoof": "",
                "VehicleDoor": "",
                "SideOfVehicle": "",
                "CarOfVehicle": "",
                "RearviewMirror": "有车内后视镜",
                "VehicleChassis": "",
                "VehicleShielding": "",
                "FilmColor": "",
                "IsModified": "0",
                "HitMarkInfo": "",
                "PlateReliability": "100",
                "PlateCharReliability": "0;0;0;0;0;0;0;",
                "BrandReliability": "80",
                "VehicleBodyDesc": "",
                "VehicleFrontItem": "3",
                "DescOfFrontItem": "挂饰",
                "VehicleRearItem": "",
                "DescOfRearItem": "",
                "NumOfPassenger": 2,
                "PassTime": _timestamp,
                "NameOfPassedRoad": "通天路",
                "IsSuspicious": "0",
                "Sunvisor": 0,
                "SafetyBelt": 1,
                "Calling": 1,
                "SubImageList": [{
                    "ImageID": _source_id,
                    "DeviceID": channel_id,
                    "StoragePath": "6125/4/featurevehicles/dn@0_0/1/65-3a50644d-3774a",
                    "Type": "01",
                    "FileFormat": "Jpeg",
                    "ShotTime": _time,
                    "Width": "1718",
                    "Height": "813",
                    "Data": base_64}]
            }
        ]

        for k, v in kwargs.items():
            k = "".join(string.title() for string in k.split("_"))
            body[0][k] = v

        url = "/demo/MotorVehicles@post"
        res = Rest(host=f"http://{HOST_IP}:2530").send(url=url, headers=headers, data=json_tool.dumps(body))
        if res.status_code != 201:
            logger.debug(f'车辆推图失败, 状态码为{res.status_code}, 接口响应为: {res.content}')
        logger.debug(f"车辆推图成功，过车通道为{channel_id}，过车时间为{_time},车牌号为{_plate_no}")

    @classmethod
    def push_single_vehicle_data_to_mda_via_kw(cls, channel_id, file_name="car001.jpg", file_relative_path="images", **kwargs):
        """模拟推送车辆近景图数据到mda, 读取远端目录文件夹下的某个车辆近景图文件，依次推送

        Args:
            channel_id (str): 卡口通道id
            file_name (str): 车辆近景图文件名
            file_relative_path (str): 相对远程目录，根目录为env.ini文件中的smb_share
                ``\\\\1.1.1.1\\info\\auto\\``, (Default value = "images")
            **kwargs: 可选字典项

        Keyword Args:
            tollgate_id (str): 卡口id，不是卡口可不传
            plate_no (str): 车牌号
            lane_no (int):车道编号 1~8，车道1~车道8
            direction (str): 方向，1~8，1东、2西、3南、4北、5东北、6西南、7东南、8西北

        Returns:
            None

        """

        base_64 = app.smb_get_base64(file_name, file_relative_path)
        cls.push_vehicle_data_to_mda_by_rest_via_kw(channel_id=channel_id, base_64=base_64, **kwargs)

    @classmethod
    def batch_push_vehicle_data_to_mda_via_kw(cls, channel_id, file_relative_path="auto_vehicles", slot=0, **kwargs):
        """批量推送一个文件夹下的车辆近景图数据到mda, 读取远端目录文件夹下的某个车辆近景图文件，依次推送

        Args:
            channel_id (str): 卡口通道id
            file_relative_path (str): 相对远程目录，根目录为env.ini文件中的smb_share
                ``\\\\1.1.1.1\\info\\auto\\``, (Default value = "auto_vehicles")
            slot (int): 推图时间间隔(s), (Default value = 0)
            **kwargs: 可选字典项

        Keyword Args:
            tollgate_id (str): 卡口id，不是卡口可不传
            plate_no (str): 车牌号
            lane_no (int):车道编号 1~8，车道1~车道8
            direction (str): 方向，1~8，1东、2西、3南、4北、5东北、6西南、7东南、8西北

        Returns:
            None

        """

        _pics = app.smb.scandir(os.path.join(SMB_SHARE_PATH, file_relative_path))
        for _pic in _pics:
            time.sleep(slot)
            _base_64 = app.smb_get_base64(_pic.name, file_relative_path)
            cls.push_vehicle_data_to_mda_by_rest_via_kw(channel_id=channel_id, base_64=_base_64, **kwargs)


if __name__ == '__main__':
    pass
