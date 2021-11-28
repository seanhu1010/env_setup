#!/usr/bin/python
# -*- coding=utf-8 -*-
"""
工具库，提供随机数，Md5，等方法
description: common
"""
import base64
import os
import random
import hashlib
import shutil
import datetime
import time
import zipfile
import re
import requests

from envlib.env.envlogging import logger
from pypinyin import lazy_pinyin
from requests_toolbelt.multipart.encoder import MultipartEncoder

from envlib.ssh import Ssh
from envlib.id_info import IdNumber
from resources.data import HOST_IP, SSH_NAME, SSH_PWD


def random_number(number, start=0, end=9):
    """生成随机数字
    
    author: sean@2021/2/3 15:09

    Args:
      number: int: 位数
      start: int: 起始数字，默认0 (Default value = 0)
      end: int: 最大数字，默认9 (Default value = 9)

    Returns:
      : str类型的多位数值

    """

    if start > end:
        logger.debug(f"start: {start} > end: {end}")
        return False
    return "".join(str(random.randint(start, end)) for _ in range(number))


def random_str(number=None, lower=False, upper=False, title=False):
    """随机不重复字符串

    Args:
      number: int: 字符串长度 (Default value = None)
      lower: bool: 是否全小写 (Default value = False)
      upper: bool: 是否全大写 (Default value = False)
      title: bool: 是否首字母大写 (Default value = False)

    Returns:
      : str类型的多位字符

    """
    import string
    if number is None:
        number = random.randint(5, 10)
    str_ = "".join(random.sample(string.ascii_letters, number))
    if lower:
        return str_.lower()
    elif upper:
        return str_.upper()
    elif title:
        return str_.title()
    else:
        return str_


def random_str_number(number):
    """随机字符串（大小写字母、数字）

    Args:
      number: int: 位数

    Returns:
      : 指定{number}位数的大小写字母、数字组成的字符串

    """
    ret = ""
    for i in range(number):
        num = random.randint(0, 9)
        letter1 = chr(random.randint(97, 122))
        letter2 = chr(random.randint(65, 90))
        s = str(random.choice([num, letter1, letter2]))
        ret += s

    return ret


def random_ip_list(ip_heads=None, ip_tail=None, number=500):
    """随机生成ip地址

    Args:
      ip_heads: str: ip固定开头，默认以10.xx.xx.xx形式 (Default value = None)
      ip_tail: str: ip固定结尾，默认不传，取随机2~254 (Default value = None)
      number: int: 生成ip的数量 (Default value = 500)

    Returns:
      : ip列表

    """

    def add(num):
        """

        Args:
          num: 

        Returns:

        """
        return [str(random.randint(2, 254)) for _ in range(num)]

    if not ip_heads:
        ip_heads = "10"

    ip_list = list()
    while len(ip_list) < number:
        heads = list()
        tail = list()
        if ip_heads:
            heads = list(filter(lambda s: s != '', ip_heads.split('.')))

        if ip_tail:
            tail = list(filter(lambda s: s != '', ip_tail.split('.')))

        add_num = 4 - len(heads) - len(tail)
        if add_num < 0:
            logger.debug("传参ip_heads或者ip_tail有误")
            return False
        add_list = add(num=add_num)
        ip_l = heads + add_list + tail
        ip_str = ".".join(ip_l)
        if ip_str not in ip_list:
            ip_list.append(ip_str)
    return ip_list


def os_remove(del_list):
    """删除文件和文件夹

    Args:
      del_list: list: 待删除的文件路径

    Returns:
      : 无

    """

    for file_path in del_list:
        if type(file_path) == str:
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"已删除文件{file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path, True)
                logger.info(f"已删除文件夹{file_path}")
        else:
            logger.debug(f"{type(file_path)}不是str")


def time_type_change(input_time, is_time_stamp=True, stamp13=False, time_type="%Y-%m-%d %H:%M:%S"):
    """时间格式-时间戳互相转换

    Args:
      input_time: 格式时间或者10位时间戳，超过10位的只取前10位
      is_time_stamp: True转换成时间戳，False转换成时间格式 (Default value = True)
      stamp13: is_time_stamp为True时生效，False转换为10位时间戳，转换为True13位时间戳 (Default value = False)
      time_type: 时间格式type，默认格式"%Y-%m-%d %H:%M:%S"，如2019-05-21 18:03:48 (Default value = "%Y-%m-%d %H:%M:%S")

    Returns:
      : 转换后的时间

    """

    if is_time_stamp:
        stamp = time.strptime(input_time, time_type)
        time_stamp = str(int(time.mktime(stamp)))
        if stamp13:
            dt = datetime.datetime.strptime(input_time, time_type)
            data_microsecond = str("%06d" % dt.microsecond)[0:3]
            return int(time_stamp + data_microsecond)
        else:
            return int(time_stamp)
    else:
        time_array = time.localtime(int(str(input_time)[:10]))
        return time.strftime(time_type, time_array)


def random_longitude(start=105.5, end=106.5):
    """随机经度

    Args:
        start (float): 起始经度
        end (float): 终止经度

    Returns:
        小数点后8位

    """

    return str(round(random.uniform(start, end), 8))


def random_latitude(start=29.0, end=30.0):
    """随机纬度

    Args:
        start (float): 起始纬度
        end (float): 终止纬度

    Returns:
        小数点后8位

    """

    return str(round(random.uniform(start, end), 8))


def create_file_by_binary(content, file_path):
    """根据二进制流，生成文件

    Args:
      content: 二进制流
      file_path: 文件生成路径（带文件名）

    Returns:
      : True or False

    """

    file_dir = os.path.dirname(file_path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    with open(file_path, 'wb') as f:
        f.write(content)
    if os.path.exists(file_path):
        return True
    else:
        logger.debug("文件生成失败！")
        return False


def unzip_file(zip_path, unzip_dir=None):
    """解压zip文件到目的路径

    Args:
      zip_path: zip压缩包生成路径（带文件名）
      unzip_dir: zip压缩包解压目的文件夹,默认解压到压缩包同级目录 (Default value = None)

    Returns:
      file_xls_return: 含图片压缩包解压后xls电子表格文件名称

    """

    if not os.path.exists(zip_path):
        raise FileNotFoundError("zip文件不存在！")
    if not unzip_dir:
        unzip_dir = os.path.dirname(zip_path)
    if not os.path.exists(unzip_dir):
        os.makedirs(unzip_dir)
    zf = zipfile.ZipFile(zip_path)
    unzip_list = zf.namelist()
    return_list = list()
    for file in unzip_list:
        file_return = os.path.join(unzip_dir, file).replace("/", "\\")
        return_list.append(file_return)
    zf.extractall(path=unzip_dir)
    return return_list


def import_list_by_xls(file_path, url,
                       content_type='application/vnd.ms-excel', **kwargs):
    """通过url上传xls

    Args:
      file_path: file_path
      url: url
      content_type: 'application/vnd.ms-excel' (Default value = 'application/vnd.ms-excel')
      **kwargs: list_type

    Returns:
      : res.json

    """

    file = os.path.basename(file_path)
    file_tup = (file, open(file_path, 'rb'), content_type)

    fields = {"file": file_tup}
    for k, v in kwargs.items():
        fields[k] = v
    data = MultipartEncoder(
        fields=fields
    )
    res = requests.post(url=url, data=data, headers={'Content-Type': data.content_type,
                                                     "User": "usercode:admin&username:admin"})
    remote_result = res.status_code
    if remote_result == 200:
        logger.debug("上传文件success")
        return res.json()
    else:
        logger.debug("上传文件failed")
    return res.json()


def random_identity_no_list(number, limit=1000):
    """随机不重复身份证列表

    Args:
      number: 身份证号个数
      limit: 循环次数，防止死循环 (Default value = 1000)

    Returns:
      : list, {number}个身份证号

    """

    idt_no = list()
    i = 0
    while len(idt_no) < number:
        if i > limit:
            break
        no = IdNumber.generate_id(sex=random.choice([0, 1]))
        if no not in idt_no:
            idt_no.append(no)
        i += 1
        if len(idt_no) == number:
            return idt_no

    return False


class Md5(object):
    """md5工具"""
    maker = hashlib.md5()

    def __init__(self):
        """初始化参数"""
        pass

    @classmethod
    def md5_str(cls, message):
        """生成字符串的md5
        
        :author: sean@2021/2/3 15:09

        Args:
          message: str: 字符串

        Returns:
          rel: 字符串的md5值

        """

        cls.maker.update(bytes(message, encoding="utf-8"))
        rel = cls.maker.hexdigest()
        cls.maker = hashlib.md5()
        return rel

    @classmethod
    def md5_file(cls, file_path):
        """根据文件内容生成md5
        
        :author: sean@2021/2/3 15:09

        Args:
          file_path: str: 文件路径

        Returns:
          str: md5 value

        """

        a_file = open(file_path, 'rb')
        cls.maker.update(a_file.read())
        a_file.close()
        return cls.maker.hexdigest()


def base64_by_path(path, header=False):
    """base64转换

    Args:
      path: str: 图片路径
      header: bool: 是否带头，例如："data:image/png;base64,..." (Default value = False)

    Returns:
      : 图片base64

    """
    try:
        with open(path, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            image = base64_data.decode('ascii')
        if header:
            file_name = os.path.basename(path)
            file_type = file_name.split(".")[-1]
            return f"data:image/{file_type};base64," + image
        else:
            return image
    except Exception as e:
        logger.debug(e)


def get_time(time_unit="hour", start_to_now=0, is_time_stamp=True, time_type="%Y-%m-%d %H:%M:%S", stamp13=False):
    """获取时间戳或时间格式
    :modify: yinjia@2021.02.05修改为获取服务器时间

    Args:
      start_to_now: 当前时刻前多少小时,start_time=now - start_to_now，不支持小数(Default value = 0)
      time_unit: 时间单位，year, month，day, hour, minute, second等，兼容老版本复数形式（例如hours） (Default value = "hour")
      time_type: 时间格式 (Default value = "%Y-%m-%d %H:%M:%S")
      is_time_stamp: True转换成时间戳，False转换成时间格式 (Default value = True)
      stamp13: bool: False10位时间戳 True13位时间戳 (Default value = False)

    Returns:
      int

    """
    ssh = Ssh(host=HOST_IP, username=SSH_NAME, password=SSH_PWD)
    time_unit = time_unit.split("s")[0]
    if is_time_stamp:
        time_type = "%s"
    sh = f'date -d "{-int(start_to_now)} {time_unit}" "+{time_type}"'
    ret, _ = ssh.exec_cmd_and_return(sh)
    ssh.close()
    if is_time_stamp:
        if stamp13:
            return int(ret) * 1000
        else:
            return int(ret)
    else:
        return ret


def random_plate_no(area='渝'):
    """随机车牌号(6位)
    
    :created: yf_yinjia@2020.11.14

    Args:
      area: 省份中文简称，默认为'渝' (Default value = '渝')

    Returns:
      : str, 车牌号

    """

    plate_no_char0 = '京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽赣粤青藏川宁琼'
    plate_no_char1 = 'ABCDEFGHJKLMNPQRSTUVWXYZ'  # 车牌号中没有I和O，可自行百度
    plate_no_char2 = '1234567890ABCDEFGHJKLMNPQRSTUVWXYZ'

    if area is None:
        area = random.choice(plate_no_char0)

    return area + random.choice(plate_no_char1) + "".join([random.choice(plate_no_char2) for _ in range(5)])


def reboot(node, username, password, ):
    """重启节点

    Args:
      node: 主机ip
      username: 登录用户名
      password: 登录密布

    Returns:
      : None

    """

    ssh = Ssh()
    cmds = [("reboot -f", "ing")]
    ssh.connect(node, username, password)
    ssh.exec_cmds_with_expect(cmds)
    wait_until_unreachable(node)
    wait_until_reachable(node)


def ping(ip, count=1):
    """ping 检查

    Args:
      ip: ip
      count: ping检查次数 (Default value = 1)

    Returns:
      Bool: ping检查通过与否

    """

    import platform
    # 根据平台适配不同的ping命令
    if "linux" == platform.system().lower():
        status = os.system("ping -c {} {}".format(count, ip))
    else:
        status = os.system("ping -n {} {}".format(count, ip))

    # ping命令会返回未ping通的次数，这里为1说明ping失败，为0则ping通
    if 0 == status:
        return True
    else:
        return False


def wait_until_unreachable(ip, timeout=None):
    """等待直到节点不可达

    Args:
      ip: 主机IP
      timeout:  (Default value = None)

    Returns:
        Bool: 状态

    """

    if not timeout:
        while True:
            if not ping(ip):
                print("{}已ping不通".format(ip))
                break
    else:
        endtime = time.time() + timeout
        while time.time() < endtime:
            status = ping(ip)
            if status:
                return True

        raise TimeoutError


def wait_until_reachable(ip, timeout=None):
    """等待直到节点可达

    Args:
      ip: 主机IP
      timeout:  (Default value = None)

    Returns:
        Bool: 状态

    """

    if not timeout:
        while True:
            if ping(ip):
                print("{}已ping通".format(ip))
                break
        return True
    else:
        endtime = time.time() + timeout
        while time.time() < endtime:
            status = ping(ip)
            if not status:
                return True

        raise TimeoutError


def wait_until_k8s_normal(node, username, password, timeout=None):
    """等待直到k8s集群正常

    Args:
      node: 节点IP
      username: 登陆用户名
      password: 登陆密码
      timeout:  (Default value = None)

    Returns:
        Bool: 状态

    """

    ssh = Ssh()
    cmd = "kubectl get pod |grep Running |wc -l"
    ssh.connect(node, username, password)
    if not timeout:
        while True:
            out, err = ssh.exec_cmd_and_return(cmd)
            if int(out) > 69:  # SINGLE_NORMAL_PODS=69
                break
        return True
    else:
        endtime = time.time() + timeout
        while time.time() < endtime:
            status = ping(node)
            if not status:
                return True

        raise TimeoutError


def validate_url(url):
    """检查url是否合规

    Args:
      url: url

    Returns:
      : bool

    """

    url_pattern = r"(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?"
    pattern = re.compile(url_pattern)
    res = re.findall(pattern=pattern, string=str(url))
    res = True if res else False
    return res


def validate_str_like_alphabet(i_str):
    """检查str模式是否只含大小写字母，以及下划线

    Args:
      i_str: str

    Returns:
      : bool

    """

    url_pattern = r"^[\w_]+$"
    pattern = re.compile(url_pattern)
    res = re.findall(pattern=pattern, string=str(i_str))
    res = True if res else False
    return res


def get_last_ip_str(ip):
    """返回一个ipv4地址的后2位组合的ip string
    Args:
        ip: ipv4地址，如'1.1.1.1'

    Returns:
        str: ie: '111222'
    """
    return ''.join(ip.split('.')[-2:])


def cn_to_en(i_str):
    """中文文本返回英文样式拼音

    Args:
        i_str: str

    Returns:
        str
    """
    return ''.join(lazy_pinyin(i_str))


if __name__ == '__main__':
    pass
