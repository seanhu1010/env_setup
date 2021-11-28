#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# @File:    app.py
# @Time:    2021/06/10

"""
    envlib.app
    ~~~~~~~~~~

    实用应用程序集合
"""
import os
import re
import base64
import json
from threading import Lock
from copy import deepcopy
from hashlib import md5
from requests_toolbelt.multipart.encoder import MultipartEncoder

from envlib.env.envlogging import logger
from envlib.database import Database
from envlib.ssh import Ssh
from envlib.smb import Smb
from envlib.env.ctx import EnvContext
from envlib.rest import Rest
from envlib.env.config import Config
from envlib.env.globals import ctx_stack
from envlib.env.globals import g
from envlib.env.globals import env_pools
from envlib.env.globals import current_app
from resources.data import HOST_IP, SSH_NAME, SSH_PASSWORD, SMB_SHARE_PATH


def _assure_keys_in_request_parameters(key_set: set):
    """检查传入的key_set是允许的options

    Args:
        key_set: set: 请求参数集合

    Tip:
        允许的options有::

            'method', 'url', 'params', 'data', 'headers', 'cookies', 'files', 'auth', 'timeout',
            'allow_redirects', 'proxies', 'hooks', 'stream', 'verify', 'cert', 'json'

    Returns:
        Bool
    """

    req_param_set = {  # 允许的options
        'method', 'url', 'params', 'data', 'headers', 'cookies', 'files', 'auth', 'timeout',
        'allow_redirects', 'proxies', 'hooks', 'stream', 'verify', 'cert', 'json', 'check'
    }
    if key_set <= req_param_set:
        return True
    else:
        wrong_req_param_set = key_set - req_param_set
        assert wrong_req_param_set is None, f"请求参数错误! 错误请求参数为:{wrong_req_param_set}, 可选类型为:{req_param_set}"
        return False


class Env(object):
    """运行环境类，只有用户+端口不同的才创建新的实例"""

    _instance_lock = Lock()

    #: The debug flag.  Set this to `True` to enable debugging of the
    #: application.  In debug mode the debugger will kick in when an unhandled
    #: exception ocurrs and the integrated server will automatically reload
    #: the application if changes in the code are detected.
    debug = False

    def __init__(self, port, user, password):

        #: 平台port, 如'8000'
        self.port = port

        #: 登陆用户
        self.user = user

        #: 登陆密码
        self.password = password

        #: 当前的Rest实例
        self.rest = self._fetch_appropriate_rest()  # proxy指向 session_pool的字典项

        #: 初始化SSH连接为集群的业务虚ip
        self.ssh = Ssh(host=HOST_IP, username=SSH_NAME, password=SSH_PASSWORD)

        #: 初始化pgsql连接
        self.pgsql = Database('pgsql')

        #: 初始化pgsql连接
        self.vertica = Database('vertica')

        #: 初始化smb client连接
        self.smb = Smb()

        #: 预留config设置模式选项
        self.config = Config()

        #: 预留扩展模块
        self.extensions = {}

    @property
    def current_context(self):
        """返回当前环境上下文实例"""
        if ctx_stack.top is not None:
            if self.debug is True and ctx_stack.top.app is self:
                return ctx_stack.top
            else:
                return EnvContext(self)
        else:
            return EnvContext(self)

    def _get_restful_response(self, **options):
        """ 对restful接口的返回值，做状态判断，并尝试以json形式返回

        Tip:
            新接口有标准的接口规范，response示例 {"error_code":"0000000000", "message":"XXX处理成功", "data": {业务自定义json格式}}
            使用老接口时有warning信息, 新接口将自动提取data

        Args:
            **options: 可选'method', 'url', 'params', 'data', 'headers', 'cookies', 'files', 'auth', 'timeout',
                'allow_redirects', 'proxies', 'hooks', 'stream', 'verify', 'cert', 'json'

        Keyword Args:
            check: 是否强制断言接口返回值为[200, 201, 204]状态之一，默认开启，强制校验接口返回若非2XX状态，程序会有中断

        Returns:
            content or data json, 接口返回
            新接口将自动提取data json片断
        """
        _check = True
        if _assure_keys_in_request_parameters(set(options.keys())):
            if 'check' in options:
                _check = options.get('check')
                options.pop('check')
            res = self.rest.send(**options)

            # 如果会话失效会返回登陆页面，重试登陆
            if "<!DOCTYPE html>" == res.text[:15]:
                self._re_login()
                res = self.rest.send(**options)

            # 尝试将返回值用json解析
            try:
                content = json.loads(res.content)
            except json.JSONDecodeError:
                content = res.content

            if _check is True:
                assert res.status_code in [200, 201,
                                           204], f" ERROR 状态码校验失败，期望值为200,201或204，实际值为{res.status_code}，接口响应为{content}"

            # 新接口有标准的接口规范，response示例 {"error_code":"0000000000", "message":"XXX处理成功", "data":{业务自定义json格式}}
            # 使用老接口时有warning信息, 新接口将自动提取data
            try:
                if 'data' in list(content.keys()) and 'error_code' in list(content.keys()):
                    logger.info(f"新式接口:{options.get('url')}, 即将提取data中的信息")
                    content = content.get('data')
                else:
                    logger.warning(f"可能是老式接口,请检查接口规范:{options.get('url')}")
            except AttributeError:
                logger.warning(f"可能是老式接口,请检查接口规范:{options.get('url')}")
            return content

    def send_by_rest(self, url, **kwargs):
        """rest请求封装

        Args:
            url (str): url, 'api@options'形式, 如'/api/demo@get'
            **kwargs: 可选'method', 'url', 'params', 'data', 'headers', 'cookies', 'files', 'auth', 'timeout',
                'allow_redirects', 'proxies', 'hooks', 'stream', 'verify', 'cert', 'json'

        Keyword Args:
            check: 是否强制断言接口返回值为[200, 201, 204]状态之一，默认开启，强制校验接口返回若非2XX状态，程序会有中断

        Returns:
            接口返回内容content的data，兼容新老接口，新接口将自动提取 *data* ，老接口会有warning提示，返回原 *content*
        """

        # 因装饰器形式不易理解，舍弃之
        # @wrapt.decorator
        # def wrapper(wrapped, instance, args, kwargs):
        #     options = dict({'url': url}, **kwargs)  # 格式化拼接后的request options
        #     restful_response = self._get_restful_response(**options)
        #     g[wrapped.__name__] = restful_response
        #     return restful_response
        #
        # return wrapper
        options = dict({'url': url}, **kwargs)
        restful_response = self._get_restful_response(**options)
        return restful_response

    def bind_to_g(self, key, value, lock=False):
        """绑定单个value到环境变量，以key,value的形式绑定到当前运行的Env实例关联的上下文环境信息AppCtxGlobals实例的代理 ``g``

        适用于循环/批量处理值的绑定

        Args:
            key: key
            value: 待绑定的value
            lock: 是否加锁，加锁且值存在，将不修改原值

        Returns:
            None
        """

        if lock is False and key in g:
            logger.warning(f'g.{key}的键重复，其value将被修改为 {value} !!')
            g.__dict__[key] = value
        elif key not in g:
            g.__dict__[key] = value
            logger.debug(f'保存g k,v项为 => {key}:{value}!')
        else:  # lock is True and key in,不修改
            logger.info(f'g.{key} is locked, 将不修改其value!')

    def smb_upload_excel(self, file_name, file_relative_path=None, file_type='application/vnd.ms-excel', **kwargs):
        """SMB连接上传excel

        smb远程读文件转化为multipart/form-data请求所需的data 和 header

        Args:
            file_name (str): 文件名
            file_relative_path (str):
                相对远程目录，根目录为env.ini文件中的smb_share ``\\\\1.1.1.1\\info\\auto\\``
            file_type (str):
                文件类型，默认为excel类型，'application/vnd.ms-excel'
                可能用到的例如，具体可抓包查找

                'doc[x]'   :  'application/msword'

                'xls[x]'   :  'application/vnd.ms-excel'

                'zip'      :  'application/zip'

                'jpeg|jpg':  'image/jpeg'

                'png'      :  'image/png'

            **kwargs:
                可选参数，以字典形式传入
                用来表示除了'file': file_tuple，以外的其他参数

                .. code:: python

                    MultipartEncoder(
                        fields={'file': file_tuple, **kwargs}
                    )

        Returns:
            data, headers
        """

        _absolute_path = os.path.join(SMB_SHARE_PATH, file_relative_path) if file_relative_path else SMB_SHARE_PATH
        _file_path = os.path.join(_absolute_path, file_name)
        with self.smb.open_file(_file_path, mode='rb') as _fd:
            file_pointer = _fd.read()
        file_tuple = (file_name, file_pointer, file_type)
        fields_dicts = dict({'file': file_tuple}, **kwargs)
        data = MultipartEncoder(fields=fields_dicts)
        _headers = deepcopy(self._headers())
        _headers.update({'Content-Type': data.content_type})
        return data, _headers

    def smb_upload_zip(self, file_name, file_relative_path=None, file_type='application/x-zip-compressed', **kwargs):
        """SMB连接上传zip文件，需要额外传入tab_id=tab_id

        smb远程读文件转化为multipart/form-data请求所需的data 和 header

        Args:
            file_name (str): 文件名
            file_relative_path (str):
                相对远程目录，根目录为env.ini文件中的smb_share ``\\\\1.1.1.1\\info\\auto\\``
            file_type (str):
                文件类型，默认为excel类型，'application/vnd.ms-excel'
                可能用到的例如，具体可抓包查找

                'doc[x]'   :  'application/msword'

                'xls[x]'   :  'application/vnd.ms-excel'

                'zip'      :  'application/zip'

                'jpeg|jpg':  'image/jpeg'

                'png'      :  'image/png'

            **kwargs:
                可选参数，以字典形式传入, 'tab_id': tab_id
                用来表示除了'file': file_tuple，以外的其他参数

                .. code:: python

                    MultipartEncoder(
                        fields={'file': file_tuple, **kwargs}
                    )

        Returns:
            data, headers
        """
        _absolute_path = os.path.join(SMB_SHARE_PATH, file_relative_path) if file_relative_path else SMB_SHARE_PATH
        _file_path = os.path.join(_absolute_path, file_name)
        with self.smb.open_file(_file_path, mode='rb') as _fd:
            file_pointer = _fd.read()
        file_tuple = (file_name, file_pointer, file_type)
        fields_dicts = dict({'zip': file_tuple}, **kwargs)
        data = MultipartEncoder(fields=fields_dicts)
        _headers = deepcopy(self._headers())
        _headers.update({'Content-Type': data.content_type})
        return data, _headers

    def smb_upload_jpg(self, file_name, file_relative_path=None, file_type='image/jpeg', **kwargs):
        """SMB连接上传jpg,jpeg文件

        smb远程读文件转化为multipart/form-data请求所需的data 和 header

        Args:
            file_name (str): 文件名
            file_relative_path (str):
                相对远程目录，根目录为env.ini文件中的smb_share ``\\\\1.1.1.1\\info\\auto\\``
            file_type (str):
                文件类型，默认为excel类型，'application/vnd.ms-excel'
                可能用到的例如，具体可抓包查找

                'doc[x]'   :  'application/msword'

                'xls[x]'   :  'application/vnd.ms-excel'

                'zip'      :  'application/zip'

                'jpeg|jpg':  'image/jpeg'

                'png'      :  'image/png'

            **kwargs:
                可选参数，以字典形式传入
                用来表示除了'file': file_tuple，以外的其他参数

                .. code:: python

                    MultipartEncoder(
                        fields={'file': file_tuple, **kwargs}
                    )

        Returns:
            data, headers
        """
        _absolute_path = os.path.join(SMB_SHARE_PATH, file_relative_path) if file_relative_path else SMB_SHARE_PATH
        _file_path = os.path.join(_absolute_path, file_name)
        with self.smb.open_file(_file_path, mode='rb') as _fd:
            file_pointer = _fd.read()
        file_tuple = (file_name, file_pointer, file_type)
        fields_dicts = dict({'file': file_tuple}, **kwargs)
        data = MultipartEncoder(fields=fields_dicts)
        _headers = deepcopy(self._headers())
        _headers.update({'Content-Type': data.content_type})
        return data, _headers

    def smb_get_base64(self, file_name, file_relative_path=None):
        """SMB读取远端图片数据路径，并返回base64

        Args:
            file_name (str): 文件名
            file_relative_path (str):
                相对远程目录，根目录为env.ini文件中的smb_share ``\\\\1.1.1.1\\info\\auto\\``

        Returns:
            (str) base64编码

        """
        _absolute_path = os.path.join(SMB_SHARE_PATH, file_relative_path) if file_relative_path else SMB_SHARE_PATH
        _file_path = os.path.join(_absolute_path, file_name)
        with self.smb.open_file(_file_path, mode='rb') as _fd:
            file_pointer = _fd.read()
        base64_data = base64.b64encode(file_pointer)
        image = base64_data.decode('ascii')
        return image

    def _rest_login(self, rest, begin_url, username, password):
        """会话登录, 保存session, cookies

        Args:
            rest (str): 需要登录的会话
            begin_url (str): 登录初始url
            username (str): 登录用户名
            password (str): 登录密码

        Returns:
            None
        """

        # 计算密码md5
        logger.info(f"用户{username}进行登陆操作")
        m = md5()
        m.update(password.encode('utf-8'))
        pwd_md5 = m.hexdigest()

        login_page = rest.get(url=begin_url)
        # 提取登录页隐藏编码
        execution = re.search(r'<input type="hidden" name="execution" value="(\S+?)"', login_page.text)
        head = {"Content-Type": "application/x-www-form-urlencoded"}
        req_json = {"username": username,
                    "password": pwd_md5,
                    "execution": execution.group(1),
                    "_eventId": "submit",
                    "submit": "%E7%99%BB%E5%BD%95",
                    "geolocation": ""}
        req_data = "&".join([f"{k[0]}={k[1]}" for k in req_json.items()])

        # 集群登录存在跳转，可能实际登录IP不是输入的host ip，替换请求IP
        req_port = rest.host.split(":")[-1]
        new_ip = login_page.url.split("/")[2].split(":")[0]
        rest.host = f"http://{new_ip}:{req_port}"

        # 登录
        rest.post(url=login_page.url, headers=head, data=req_data)

        # 校验登录结果，校验session的cookies
        sso_cookies = rest.cookies._cookies.get(new_ip).get('/sso/')
        rest.headers = self._headers()
        if not sso_cookies:
            logger.error("登录失败")

    def _re_login(self):
        """重新登陆rest会话"""
        self._rest_login(rest=self.rest, begin_url=self.rest.host, username=self.user, password=self.password)

    def _fetch_appropriate_rest(self):
        """从单例Rest实例池获取缓存的实例，否则新建"""
        if not hasattr(self, 'rest'):
            _rest = Rest(f'http://{HOST_IP}:{self.port}')
            self._rest_login(rest=_rest, begin_url=_rest.host, username=self.user, password=self.password)
        else:
            _rest = env_pools.get(self.user + str(self.port)).rest
        return _rest

    def _headers(self):
        """登录后的的header"""
        return {  # 正常登录后的的header
            "Authorization": f"username:{self.user}&usercode:{self.user}",
            "User": f"username:{self.user}&usercode:{self.user}",
            "Content-Type": "application/json;charset=utf-8"
        }

    def push_context(self):
        """调用方式触发上下文"""
        self.current_context.push()

    def pop_context(self):
        """调用方式弹出上下文"""
        self.current_context.pop()

    def __enter__(self):
        """with方式触发上下文"""
        self.current_context.push()
        return current_app

    def __exit__(self, exc_type, exc_val, exc_tb):
        """自动释放上下文"""
        self.current_context.__exit__(exc_type, exc_val, exc_tb)

    def __new__(cls, port, user, password):
        """基于元类的实例产生"""
        if not hasattr(cls, "_instance"):
            with Env._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super().__new__(cls)
                    env_pools[user + str(port)] = cls._instance
        else:
            with Env._instance_lock:
                if user + str(port) not in env_pools:
                    cls._instance = super().__new__(cls)
                    env_pools[user + str(port)] = cls._instance
                else:
                    cls._instance = env_pools.get(user + str(port))
        return cls._instance


if __name__ == '__main__':
    pass
