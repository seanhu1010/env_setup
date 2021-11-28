#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File:    fullanalysis.py
"""
全量解析类预置库
"""
import os
import time
from loguru import logger

from envlib.envsetup.udm import Udm

from envlib.rest import Rest
from envlib.util import random_str_number

from envlib.env.globals import current_app as app
from envlib.env.globals import g
from envlib.env.helpers import GetKeysMixin
from envlib.envsetup.udm import *

from resources.data import SMB_SHARE_PATH, headers, HOST_IP

__all__ = ['FullAnalysis', ]


class FullAnalysis(GetKeysMixin):
    """全量解析类"""
    # 创建解析任务类型
    __task_source_type = {
        "实时视频流": 1,
        "实时图片流": 2,
        "在线录像解析": 3,
        "离线解析": 4
    }

    def __init__(self):
        """初始化参数"""

    @classmethod
    def query_fullanalysis_task_detail_by_rest(cls, task_id, ):
        """根据task_id查询解析任务详情

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='analysis_task_detail_dict', value=查询接口返回值，解析任务详情

        Args:
            task_id (str): 任务id

        Returns:
            rest接口返回值，解析任务详情

        """

        res = app.send_by_rest(f'/api/demo@get', check=False)  # res为字典
        app.bind_to_g(key='analysis_task_detail_dict', value=res, lock=False)
        return res  # res为字典

    @classmethod
    def query_fullanalysis_task_by_rest(cls, source_type=__task_source_type.get("实时视频流"), search=None, check=False,
                                        **kwargs):
        """查询各类解析任务列表

        查询结果绑定到 当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g`` 下::

            key='analysis_realtime_video_task_list', value=接口返回值，解析任务列表
            key='analysis_realtime_image_task_list', value=接口返回值，解析任务列表
            key='analysis_online_video_task_list', value=接口返回值，解析任务列表
            key='analysis_offline_video_task_list', value=接口返回值，解析任务列表

        Args:
            source_type (int): 任务类型
            search (str, None): 搜索过滤项
            check (bool): 接口返回状态码校验，默认不校验
            **kwargs: 可选字典项

        Returns:
            rest接口返回值，解析任务列表

        """
        params = {"page": 1, "size": 100, "source_type": source_type}
        if search is not None:
            params["search"] = search
        params.update(kwargs)
        res = app.send_by_rest('/api/demo@get', params=params, check=check)
        if source_type == 1:
            app.bind_to_g(key='analysis_realtime_video_task_list', value=res.get("data"), lock=False)
        if source_type == 2:
            app.bind_to_g(key='analysis_realtime_image_task_list', value=res.get("data"), lock=False)
        if source_type == 3:
            app.bind_to_g(key='analysis_online_video_task_list', value=res.get("data"), lock=False)
        if source_type == 4:
            app.bind_to_g(key='analysis_offline_video_task_list', value=res.get("data"), lock=False)

        return res.get("data")

    @classmethod
    def add_fullanalysis_realtime_video_task_by_rest(cls, task_name=random_str_number(number=5),
                                                     device_name='realtime_video', **kwargs):
        """创建视频流解析任务

        Args:
            task_name(str): 任务名称,可自定义，默认随机生成5位字符串名称
            device_name(str): 设备名称 (Default value = 'realtime_video')
            **kwargs: 其他请求关键字

        Returns:
            rest接口返回值

        """

        Udm.query_encoder_channel_list_by_rest_via_org_name(org_name="本域")  # 查询通道并绑定用于后续解析任务获取设备通道编码
        device_info_list = g.getk('udm_encoder_channel_list').extracting('name', 'ape_id', 'sub_type', 'resource_type',
                                                                         filter={'owner_aps_name': device_name})
        device_info_dict = dict(zip(('name', 'ape_id', 'sub_type', 'resource_type'), device_info_list))

        body = {

            "source_type": cls.__task_source_type.get("实时视频流"),
            "sources": [
                {
                    "source_id": device_info_dict.get('ape_id'),
                    "source_name": device_info_dict.get('name'),
                    "type": device_info_dict.get('resource_type'),
                    "sub_type": device_info_dict.get('sub_type'),
                    "cascaded_id": "-1"
                }
            ],
            "task_name": task_name,
            "speed": "0",
            "extend_info": {"face": 1, "nonvehicle": 1, "person": 1, "vehicle": 1},
        }
        for k, v in kwargs.items():
            body[k] = v
        res = app.send_by_rest('/api/demo@post', json=body, check=False)
        return res

    @classmethod  # new
    def add_fullanalysis_online_video_task_by_rest(cls, task_name=random_str_number(number=5),
                                                   device_name='m_ipc_10.4.48.2', before="0m", after="5m", **kwargs):
        """创建在线录像解析任务

        Args:
            task_name (str): 任务名称,可自定义，默认随机生成5位字符串名称
            device_name (str): 设备名称 (Default value = 'realtime_video')
            before (str): 前x分钟，如'0m'
            after (str): 后x分钟， 如'5m'
            **kwargs: 其他请求关键字

        Returns:
            rest接口返回值

        """

        Udm.query_encoder_channel_list_by_rest_via_org_name(org_name="本域")  # 查询通道并绑定用于后续解析任务获取设备通道编码
        device_info_list = g.getk('udm_encoder_channel_list').extracting('name', 'ape_id', 'sub_type', 'resource_type',
                                                                         filter={'owner_aps_name': device_name})
        device_info_dict = dict(zip(('name', 'ape_id', 'sub_type', 'resource_type'), device_info_list))

        begin_mills, end_mills = app.ssh.get_time_quantum_stamp(before=before, after=after, accuracy="ms")
        body = {

            "source_type": cls.__task_source_type.get("在线录像解析"),
            "sources": [
                {
                    "source_id": device_info_dict.get('ape_id'),
                    "source_name": device_info_dict.get('name'),
                    "type": device_info_dict.get('resource_type'),
                    "sub_type": device_info_dict.get('sub_type'),
                    "cascaded_id": "-1"
                }
            ],
            "task_name": task_name,
            "speed": "2",
            "priority_level": 2,
            "extend_info": {"face": 1, "nonvehicle": 1, "person": 1, "vehicle": 1},
            "video_start_time": begin_mills,
            "video_end_time": end_mills
        }
        for k, v in kwargs.items():
            body[k] = v
        res = app.send_by_rest('/api/demo@post', json=body, check=False)
        return res

    @classmethod  # new
    def add_fullanalysis_realtime_image_task_by_rest(cls, task_name=random_str_number(number=5),
                                                     device_name='realtime_image', **kwargs):
        """创建实时图片流解析任务

        Args:
            task_name(str): 任务名称,可自定义，默认随机生成5位字符串名称
            device_name(str): 设备名称 (Default value = 'realtime_video')
            **kwargs: 其他请求关键字

        Returns:
            rest接口返回值

        """
        Udm.query_tollgate_device_list_by_rest_via_org_name(org_name="本域")  # 查询通道并绑定用于后续解析任务获取设备通道编码
        device_info_list = g.getk('udm_tollgate_device_list').extracting('name', 'tollgate_id', 'sub_type',
                                                                         'resource_type', filter={'name': device_name})
        device_info_dict = dict(zip(('name', 'tollgate_id', 'sub_type', 'resource_type'), device_info_list))
        body = {

            "source_type": cls.__task_source_type.get("实时图片流"),
            "sources": [
                {
                    "source_id": device_info_dict.get('tollgate_id'),
                    "source_name": device_info_dict.get('name'),
                    "type": "6",
                    "sub_type": device_info_dict.get('sub_type'),
                    "cascaded_id": "-1"
                }
            ],
            "task_name": task_name,
            "speed": "0",
            "extend_info": {"face": 1, "nonvehicle": 1, "person": 1, "vehicle": 1, "use_coordinate": 1},
        }
        for k, v in kwargs.items():
            body[k] = v
        res = app.send_by_rest('/api/demo@post', json=body, check=False)
        return res

    @classmethod
    def query_wait_fullanalysis_task_status(cls, task_name, source_type=__task_source_type.get("实时视频流"),
                                            except_status=None, timeout=10, sleep_time=1):
        """超时时间内校验解析任务状态

        Args:
            task_name (str): 解析任务名称
            source_type (int): 任务类型
            except_status (int):  预期状态列表, 0等待，1运行，2异常，4完成 (Default value = None)
            timeout (int): 超时时间 (Default value = 10)
            sleep_time (int):  间隔查询时间 (Default value = 1)

        Returns:
            (bool)

        """

        FullAnalysis.query_fullanalysis_task_by_rest(source_type=source_type, search=None, check=False)
        task_id = ""
        if source_type == 1:
            task_id = g.getk('analysis_realtime_video_task_list').extracting('id', filter={'task_name': task_name})
        if source_type == 2:
            task_id = g.getk('analysis_realtime_image_task_list').extracting('id', filter={'task_name': task_name})
        if source_type == 3:
            task_id = g.getk('analysis_online_video_task_list').extracting('id', filter={'task_name': task_name})
        if source_type == 4:
            task_id = g.getk('analysis_offline_video_task_list').extracting('id', filter={'task_name': task_name})

        if except_status is None:
            except_status = 1
        i = 0
        while i * sleep_time <= timeout:
            query = FullAnalysis.query_fullanalysis_task_detail_by_rest(task_id=task_id)
            if not bool(query):
                logger.error("未检查到任务名为%s的任务" % task_name)
                return False
            if query.get("status") == except_status:
                logger.info("名为%s的任务为预期状态" % task_name)
                return True
            logger.debug("未达预期状态，%d秒后检查下一次" % sleep_time)
            time.sleep(sleep_time)
            i += 1

        logger.debug("timeout，%d秒内任务状态未达预期" % timeout)

        return False

    @classmethod
    def delete_fullanalysis_task_by_rest(cls, task_name='', source_type=__task_source_type.get("实时视频流")):
        """删除指定全量解析任务

        Args:
            task_name (str): 任务名称
            source_type (int): 任务类型

        Returns:
            rest任务删除成功ID

        """

        FullAnalysis.query_fullanalysis_task_by_rest(source_type=source_type, search=None, check=False)
        task_id = ""
        if source_type == 1:
            task_id = g.getk('analysis_realtime_video_task_list').extracting('id', filter={'task_name': task_name})
        if source_type == 2:
            task_id = g.getk('analysis_realtime_image_task_list').extracting('id', filter={'task_name': task_name})
        if source_type == 3:
            task_id = g.getk('analysis_online_video_task_list').extracting('id', filter={'task_name': task_name})
        if source_type == 4:
            task_id = g.getk('analysis_offline_video_task_list').extracting('id', filter={'task_name': task_name})

        task_ids = list()
        task_ids.append(task_id)
        json_data = {"ids": task_ids, 'source_type': source_type}
        res = app.send_by_rest('/api/demo@post', json=json_data, check=True)
        return res

    @classmethod
    def add_offline_task(cls, task_name=random_str_number(number=5), file_name='ac-personvehicle.ts', speed=5,
                         **kwargs):
        """创建离线解析任务

        Args:
            task_name(str): 离线任务名称 可自定义，默认随机生成5位字符串名称
            speed(int): 算力值 (Default value = 5)
            file_name(str): 离线文件名称 (Default value = 'ac-personvehicle.ts')
            **kwargs: 其他请求关键字

        Returns:
            rest接口返回值

        """

        cls.query_analysis_file_info(file_name=file_name)
        file_info_list = g.getk("fullanalysys_files_info_list").extracting('file_key', 'file_id', 'file_name',
                                                                           filter={'file_name': file_name})

        file_info_dict = dict(zip(('file_key', 'file_id', 'file_name', 'resource_type'), file_info_list))
        body = {

            "source_type": cls.__task_source_type.get("离线解析"),
            "sources": [
                {
                    "file_key": file_info_dict.get("file_key"),
                    "source_id": file_info_dict.get("file_id"),
                    "source_name": file_name,
                    "cascaded_id": "-1"  # 是否级联(-1不级联)
                }
            ],
            "task_name": task_name,
            "speed": speed,
            "priority_level": 2,
            "extend_info": {"face": 1, "nonvehicle": 1, "person": 1, "vehicle": 1},
        }
        for k, v in kwargs.items():
            body[k] = v
        res = app.send_by_rest('/api/demo@post', json=body, check=False)
        return res

    @classmethod
    def query_analysis_file_info(cls, file_name="", ):
        """查询离线文件信息

        Args:
            file_name(str): 查询离线文件名称 (Default value = "")

        Returns:
            rest接口返回值

        """

        query_data = "page_num=1&page_size=100&search={}".format(file_name)
        res = app.send_by_rest('/api/demo@get', params=query_data, check=False)
        app.bind_to_g(key='fullanalysys_files_info_list', value=res.get('data'), lock=False)
        return res.get('data')  # getk进行列表查询，res[0]非列表

    @classmethod
    def upload_offline_file(cls, file_name="ac-personvehicle.ts", size=31457280, file_relative_path=None,
                            ):
        """离线文件上传入口方法

        Args:
            file_name(str): 上传文件名称 (Default value = "ac-personvehicle.ts")
            size(int): 上传文件分片大小 (Default value = 31457280)
            file_relative_path(str): 视频文件smb共享服务器上路径 (Default value = None)

        Returns:
            rest接口返回值

        """

        _absolute_path = os.path.join(SMB_SHARE_PATH, file_relative_path) if file_relative_path else SMB_SHARE_PATH
        file_path = os.path.join(_absolute_path, file_name)
        # 数据库新增数据
        with app.smb.open_file(file_path, mode='rb') as _fd:
            fp = _fd.read()

        import hashlib
        maker = hashlib.md5()
        maker.update(fp)
        file_md5 = maker.hexdigest()
        file_size_class = app.smb.stat(file_path)
        file_size = getattr(file_size_class, 'st_size', '没有st_size查看smb文件大小属性')
        file_info = FullAnalysis._add_configuration_files(file_path=file_path, file_size=file_size, file_md5=file_md5)
        # 上传i/o流
        try:
            start_size = 0
            with app.smb.open_file(file_path, mode='rb') as _fd:

                while start_size < file_size:
                    _fd.seek(start_size)
                    if start_size + size >= file_size:
                        FullAnalysis._upload_file_by_size(fp=_fd, start_size=start_size, size=file_size - start_size,
                                                          file_size=file_size, file_info=file_info)
                        break
                    else:
                        FullAnalysis._upload_file_by_size(fp=_fd, start_size=start_size, size=size, file_size=file_size,
                                                          file_info=file_info)
                        start_size = start_size + size

        except Exception as e:
            logger.debug(f"{e}")
            return False

        # 更新离线文件状态
        update = FullAnalysis._update_offline_files_status(file_info_id=file_info["id"])
        if bool(update):
            file_info = file_info
            return file_info
        else:
            logger.debug("更新文件状态失败")
            return False

    @classmethod
    def _upload_file_by_size(cls, fp, start_size, size, file_size, file_info):
        """全量解析上传视频文件入口函数

        Args:
            fp(byte): 打开文件句柄
            start_size(int): 文件分片中开始位置
            size(int): 读取文件分片大小
            file_size(str): 文件容量
            file_info(dict): 文件其他属性信息

        Returns:
            Bool

        """

        upload_url = file_info.get("upload_url") + "@post"
        content_disposition = 'attachment;filename={}'.format(file_info.get("file_name"))
        payload = fp.read(size)
        content_range = f"bytes {start_size}-{start_size + size - 1}/{file_size}"
        headers_ = {'Content-Disposition': content_disposition, 'Content-Type': 'application/octet-stream',
                    'X-Content-Range': content_range, 'Session-ID': file_info.get("file_id"),
                    'Content-Length': str(size), 'Storage-Info': file_info.get("storage_info")}
        res = Rest(host="http://{}:5091".format(HOST_IP)).send(url=upload_url, data=payload, headers=headers_)
        if res.status_code not in range(200, 202):
            logger.debug(f"状态码校验失败，期望值为200，实际值为{res.status_code}，接口响应为{res.content}")
            return False
        return True

    @classmethod
    def _add_configuration_files(cls, file_path, file_size, file_md5):
        """全量解析页面上传视频文件创建任务信息(暂未上传视频)

        Args:
            file_path(str): 视频文件smb共享服务器上路径
            file_size(str): 文件容量
            file_md5(str): 文件MD5信息

        Returns:
            rest接口返回值

        """
        file_name = os.path.basename(file_path)
        file_size = file_size
        check_param = file_md5
        body = {"file_name": file_name, "file_size": file_size, "check_param": check_param, "description": file_name,
                "start_time": 0, "longitude": 0, "latitude": 0, "file_source": 1, "file_code": "", "location": "",
                "group_id": 1}
        res = app.send_by_rest(f"/api/demo@post", json=body, headers=headers, check=True)
        return res

    @classmethod
    def _update_offline_files_status(cls, file_info_id):
        """更新视频文件状态

        Args:
            file_info_id(str): 文件id值

        Returns:
            rest接口返回值

        """
        body = {"upload_status": 3, "upload_progress": 100}
        res = app.send_by_rest(f"/api/demo@put", json=body,
                               headers=headers, check=True)
        return res


if __name__ == '__main__':
    pass
    # from envlib.envsetup.uuv import Uuv
    #
    # Uuv.batch_add_uuv_organization_from_env_ini()
