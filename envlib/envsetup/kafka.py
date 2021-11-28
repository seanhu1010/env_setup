#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File:    kafka.py
"""
数据推送预置库
"""

import json as json_tool
from envlib.env.envlogging import logger

from envlib.env.globals import current_app as app

__all__ = ['Kafka', ]


class Kafka(object):
    """推数据到kafka，ssh方式"""

    kafka_port = 9093

    @classmethod
    def produce_data(cls, body_list, topic="visitor-event-topic", topic_key=None, timeout=60):
        """模拟kafka生产者，发送数据

        Args:
            body_list (list): 发送的数据对象列表
            topic (str, optional): topic名称, (Default value = "visitor-event-topic")
            topic_key (str, optional): 是否带key，例如传topic_key="egs_upload_event" (Default value = None)
            timeout (int, optional): 超时时间, s, (Default value = 60)

        Returns:
            str: 终端打印输出

        """

        cmd3 = f"kafka-console-producer.sh --broker-list kafka-hs:{cls.kafka_port} --topic {topic}"
        if topic_key is not None and type(topic_key) == str:
            cmd3 += " --property \"parse.key=true\" --property \"key.separator=:\""

        commands = [
            ("kubectl exec -it kafka-0 bash", "#"),
            ("cd /opt/kafka_2.12-2.2.1/bin", "#"),
            (cmd3, ">")
        ]

        for body in body_list:
            str_body = json_tool.dumps(body, ensure_ascii=False)
            if topic_key is not None and type(topic_key) == str:
                commands.append((f"{topic_key}:{str_body}", ">"))
            else:
                commands.append((str_body, ">"))
        try:
            out = app.ssh.exec_cmds_with_expect(commands=commands, timeout=timeout)
        except Exception as e:
            logger.warning(f'给topic {topic} 发送数据 {body_list} 超时, 报错信息为:{e}')
            out = None
        return out

    @classmethod
    def consume_data(cls, topic="uss-egs-event", timeout=60, **kwargs):
        """模拟kafka生消费者，消费数据

        Args:
            topic (str, optional): topic名称 (Default value = "uss-egs-event")
            timeout (int, optional): 超时时间, s, (Default value = 60)
            **kwargs: 可选字典项

        Returns:
            str: 终端打印输出

        """
        cmd3 = f"kafka-console-consumer.sh --bootstrap-server kafka-hs:{cls.kafka_port} --topic {topic}"
        for k, v in kwargs.items():
            if type(v) == bool:
                cmd3 += " --%s" % k.replace("_", "-")
            else:
                cmd3 += " --%s %s" % (k.replace("_", "-"), str(v))

        commands = [
            ("kubectl exec -it kafka-0 bash", "#"),
            ("cd /opt/kafka_2.12-2.2.1/bin", "#"),
            (cmd3, "}\r\n")
        ]

        try:
            out = app.ssh.exec_cmds_with_expect(commands=commands, timeout=timeout)
        except Exception as e:
            logger.warning(f'查询topic {topic} 数据超时, 报错信息为:{e}')
            out = None
        return out


if __name__ == '__main__':
    pass
