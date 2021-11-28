#!/usr/bin/env python 
# -*- coding:utf-8 -*-

"""
author: sean
created: 2021/2/3 16:34
生成身份证，姓名，电话号码，等等信息
"""

import random
import re
from datetime import datetime, timedelta
from envlib.env_resources.constant import AREA_INFO, FIRST_NAME, LAST_NAME, NATION, ID_NUMBER_18_REGEX, \
    ID_NUMBER_15_REGEX


def random_chinese_name():
    """生成随机中文名字，二到三字

    Returns:
        str: 随机名字
    """

    long = random.randint(2, 3)
    first_name = random.choice(FIRST_NAME)
    last_name = random.choice(LAST_NAME) if long == 2 else "{}{}".format(random.choice(LAST_NAME),
                                                                         random.choice(LAST_NAME))
    name = first_name + last_name
    return name


def random_nation():
    """返回随机名族

    Returns:
        str: 名族
    """

    return random.choice(NATION)


def random_phone_number():
    """随机生成电话号码

    Returns:
        随机电话号码
    """

    # 第二位数字
    second = [3, 4, 5, 7, 8][random.randint(0, 4)]

    # 第三位数字
    third = {
        3: random.randint(0, 9),
        4: [5, 7, 9][random.randint(0, 2)],
        5: [i for i in range(10) if i != 4][random.randint(0, 8)],
        7: [i for i in range(10) if i not in [4, 9]][random.randint(0, 7)],
        8: random.randint(0, 9),
    }[second]

    # 最后八位数字
    suffix = random.randint(9999999, 100000000)

    # 拼接手机号
    return "1{}{}{}".format(second, third, suffix)


class IdNumber(str):
    """
    身份类

    Attributes:
        id: 身份证号
        area_id: 区域编号
        birth_year: 身份证年
        birth_month: 身份证月
        birth_day: 身份证日
    """

    def __init__(self, id_number):
        """传入{id_number}身份证号生成身份证实例"""
        super(IdNumber, self).__init__()
        self.id = id_number
        self.area_id = int(self.id[0:6])
        self.birth_year = int(self.id[6:10])
        self.birth_month = str(self.id[10:12])
        self.birth_day = str(self.id[12:14])

    def get_area_name(self):
        """根据区域编号取出区域名称"""
        return AREA_INFO[self.area_id]

    def get_residence(self):
        """对象管理-人员管理居住地编码"""
        q = self.id[0:2]
        z = self.id[2:4]
        h = self.id[4:6]
        if z == '00' and h == '00':
            return q + '0000'
        else:
            if h == '00':
                return q + '0000' + '-' + q + z + '00'
            else:
                return q + '0000' + '-' + q + z + '00' + '-' + q + z + h

    def get_birthday(self):
        """通过身份证号获取出生日期"""
        return "{0}-{1}-{2}".format(self.birth_year, self.birth_month, self.birth_day)

    def get_birthday_timestamp(self, stamp13=True):
        """转换生日为时间戳
        Args:
            stamp13: bool 默认为13位，毫秒级

        Returns:
            int
        """

        birthday = datetime.strptime(self.id[6:14], "%Y%m%d")
        if not stamp13:
            return int((birthday - datetime.strptime('19700101', "%Y%m%d")).total_seconds())
        return int((birthday - datetime.strptime('19700101', "%Y%m%d")).total_seconds() * 1000)

    def get_age(self):
        """通过身份证号获取年龄"""
        now = (datetime.now() + timedelta(days=1))
        year, month, day = now.year, now.month, now.day

        if year == self.birth_year:
            return 0
        else:
            if self.birth_month > month or (self.birth_month == month and self.birth_day > day):
                return year - self.birth_year - 1
            else:
                return year - self.birth_year

    def get_sex(self):
        """通过身份证号获取性别， 女生：0，男生：1"""
        return int(self.id[16:17]) % 2

    def get_sex_cn(self):
        """通过身份证号获取性别， 女生：女，男生：男"""
        sex = int(self.id[16:17]) % 2
        return '男' if sex else '女'

    def get_check_digit(self):
        """通过身份证号获取校验码"""
        check_sum = 0
        for i in range(0, 17):
            check_sum += ((1 << (17 - i)) % 11) * int(self.id[i])
        check_digit = (12 - (check_sum % 11)) % 11
        return check_digit if check_digit < 10 else 'X'

    @classmethod
    def verify_id(cls, id_number):
        """校验身份证是否正确"""
        if re.match(ID_NUMBER_18_REGEX, id_number):
            check_digit = cls(id_number).get_check_digit()
            return str(check_digit) == id_number[-1]
        else:
            return bool(re.match(ID_NUMBER_15_REGEX, id_number))

    @classmethod
    def generate_id(cls, sex=1):
        """类方法，随机生成身份证号，默认生成男性的身份证

        Args:
            sex: sex = 0表示女性，sex = 1表示男性

        Returns:
            str: 身份证号
        """

        # 随机生成一个区域码(6位数)
        id_number = str(random.choice(list(AREA_INFO.keys())))
        # 限定出生日期范围(8位数)
        start, end = datetime.strptime("1960-01-01", "%Y-%m-%d"), datetime.strptime("2016-12-30", "%Y-%m-%d")
        birth_days = datetime.strftime(start + timedelta(random.randint(0, (end - start).days + 1)), "%Y%m%d")
        id_number += str(birth_days)
        # 顺序码(2位数)
        id_number += str(random.randint(10, 99))
        # 性别码(1位数)
        id_number += str(random.randrange(sex, 10, step=2))
        # 校验码(1位数)
        return id_number + str(cls(id_number).get_check_digit())


def id_info():
    """生成常见身份证信息

    Returns:
        id_information字典::

            {
                'id': id_number,
                'name': name,
                'sex': sex,
                'nation': nation,
                'area': area,
                'phone': phone
            }
    """

    random_sex = random.randint(0, 1)  # 随机生成男(1)或女(0)
    id_number = IdNumber.generate_id(random_sex)
    name = random_chinese_name()
    sex = IdNumber(id).get_sex_cn()
    nation = random_nation()
    area = IdNumber(id).get_area_name()
    phone = random_phone_number()
    id_information = {
        'id': id_number,
        'name': name,
        'sex': sex,
        'nation': nation,
        'area': area,
        'phone': phone
    }
    return id_information


def object_id_info(name_=None, sex_=2, user_code=None):
    """随机生成对象管理-人像管理-基本信息

    Args:
        name_:str 输入人名，不输入则随机生成
        sex_:int 1男，其他女, 默认为女性
        user_code: str or int, 自定义用户编号，默认使用身份证号

    Returns:
        可供对象管理-人像管理-基本信息使用的body.data, json
    """

    _id = IdNumber.generate_id(sex_)
    user_code = user_code if user_code else _id
    _gender = '1' if sex_ == 1 else '2'
    _name = name_ if name_ else random_chinese_name()
    _phone = random_phone_number()
    _jzd = IdNumber(_id).get_residence()
    _birth = IdNumber(_id).get_birthday_timestamp()
    _address = IdNumber(_id).get_area_name()
    return {
        "user_code": user_code,
        "user_image": "/file/mg/2021/0121/20210121172515469.jpg",
        "gender": _gender,
        "is_construct": 0,
        "user_name": _name,
        "cell_phone": _phone,
        "identity_type": 111,
        "residence": _jzd,
        "identity_no": _id,
        "birthday": _birth,
        "address": _address,
        "country": 156,
        "nation": 1,
        "formId": "omperson",
        "org_id": 98,
        "org_index": "225",
        "index_path": "0/1/"
    }


if __name__ == '__main__':
    pass
