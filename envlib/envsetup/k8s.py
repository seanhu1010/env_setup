#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File:    k8s.py
"""
K8s类预置库
"""

from envlib.env.envlogging import logger

from envlib.env.globals import current_app as app

from resources.data import SSH_NAME, HOST_IP

__all__ = ['K8s', ]


class K8s(object):
    """K8s类，包含一些pod的交互"""

    def __init__(self):
        pass

    @classmethod
    def check_pod_status_by_ssh_via_pod_name(cls, pod_name_key):
        """根据pod名字的关键字，检查pod状态

        Args:
            pod_name_key(str): pod关键字，ie: base-be等

        Returns:
            bool: pod状态为running返回 True

        """

        cmd = f"kubectl get pod | grep {pod_name_key} |head -1"
        status, error = app.ssh.exec_cmd_and_return(cmd)
        is_running = status.find('Running')
        if is_running:
            logger.debug(f"{pod_name_key} is running")
        else:
            logger.debug(f"{pod_name_key} 状态异常，或请求的pod关键字不正确")
            logger.debug("在主机:{}执行命令成功，命令内容:{}，执行用户:{}".format(HOST_IP, cmd, SSH_NAME))
            logger.debug(status)
        if is_running == -1:  # 状态非运行
            running_status = False
        else:
            running_status = True

        return running_status


if __name__ == '__main__':
    pass
