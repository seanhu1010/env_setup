# -*- coding: UTF-8 -*-
import json
import requests

from urllib.parse import urlencode, quote
from envlib.env.envlogging import logger

from envlib.util import validate_url

__all__ = ['Rest', ]


class Rest(object):
    """restful接口操作基础库

    Attributes:
        logger: 日志模块
        session: 会话
        host: str: 平台URL, 例如'http://ip:8000'
        timeout: 超时时间
        headers: 请求头，默认为None
        cookies: cookies
        verify: verify

    Tip:
        有两种使用方法：
        1、使用send方法解析专有格式的uri（uri@method格式的）
        2、使用传统方式，传入完整url和参数
    """

    def __init__(self, host):
        self.logger = logger
        if not validate_url(host):
            self.logger.error("输入的主机地址不符合正则规定，请检查！！")
        self.session = requests.session()
        self.host = host
        self.timeout = 10
        self.headers = None
        self.cookies = self.session.cookies
        self.verify = self.session.verify

    def send(self, url, *args, **kwargs):
        """request send请求, 通过uri中的@判断到对应的post/get等方法

        Args:
            url: 形如"/api/demo@get"这样包含相对uri和method
            *args: 无实际意义
            **kwargs: 允许的options
                'method', 'url', 'params', 'data', 'headers', 'cookies', 'files', 'auth', 'timeout',
                'allow_redirects', 'proxies', 'hooks', 'stream', 'verify', 'cert', 'json'

        Returns:
            接口response对象
        """

        if "@" not in url:
            self.logger.info("URL not contain request METHOD infomation, use other specific method")
            return None
        if kwargs.get("data"):
            data = kwargs.get("data")
            if "{}" in url:
                url = url.format(data.get("url_data"))
        url_info = url.split("@")
        uri = url_info[0]
        host = self.host
        actual_url = None
        if uri:
            slash = '' if uri.startswith('/') else '/'
            actual_url = "{}{}{}".format(host, slash, uri)
        method_name = url_info[-1].lower()
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(actual_url, *args, **kwargs)
        else:
            self.logger.error("解析出的方法不存在，请检查@后的字符")

    def post(self,
             url,
             data=None,
             json=None,
             params=None,
             headers=None,
             files=None,
             allow_redirects=None,
             timeout=None,
             **kwargs):
        """发送post请求

        Args:
            url: 请求地址,形如"/api/demo@get"这样包含相对uri和method
            data: a dictionary of key-value pairs that will be urlencoded
               and sent as POST data
               or binary data that is sent as the raw body content
               or passed as such for multipart form data if ``files`` is also defined
            json: a value that will be json encoded
               and sent as POST data if files or data is not specified
            params: url parameters to append to the uri
            headers: a dictionary of headers to use with the request
            files: a dictionary of file names containing file data to POST to the server
            allow_redirects: Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
            timeout: connection timeout
            **kwargs: 其他允许的options

        Returns:
            接口response对象
        """

        cookies = kwargs.get('cookies') if kwargs.get('cookies') else None
        redir = True if allow_redirects is None else allow_redirects
        headers = headers if headers else self.headers
        response = self.session.post(
            url,
            data,
            json,
            params=params,
            headers=headers,
            files=files,
            allow_redirects=redir,
            timeout=timeout,
            cookies=cookies,
            **kwargs)

        data_str = str(data)[:400]
        json_str = str(json)[:400]
        if files:
            self.logger.debug(f"请求文件：{files}")
        self.logger.debug(f"-------响应状态码---{response.status_code}")
        self.logger.debug(
            f'-------请求路径 : {url}\n-------请求参数 : {json_str}\n-------请求头 : {headers}\n-------请求方式 : POST')
        try:
            self.logger.debug(f'-------请求返回值 : {response.content.decode("utf-8")}')
        except:
            pass
        return response

    def get(self,
            url,
            params=None,
            headers=None,
            json=None,
            allow_redirects=None,
            timeout=None,
            **kwargs):
        """发送get请求

        Args:
            url: 请求地址,形如"/api/demo@get"这样包含相对uri和method
            params: url parameters to append to the uri
            headers: a dictionary of headers to use with the request
            json: a value that will be json encoded
               and sent as POST data if files or data is not specified
            allow_redirects: Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
            timeout: connection timeout
            **kwargs: 其他允许的options

        Returns:
            接口response对象
        """

        redir = True if allow_redirects is None else allow_redirects
        headers = headers if headers else self.headers
        resp = self.session.get(url,
                                headers=headers,
                                json=json,
                                params=self._utf8_urlencode(params),
                                allow_redirects=redir,
                                timeout=self._get_timeout(timeout),
                                cookies=self.cookies,
                                verify=self.verify,
                                **kwargs)

        json_str = str(json)[:200]
        params_str = str(params)[:200] if str(params)[:200] else json_str
        self.logger.debug(
            f'-------请求路径 : {url}\n-------请求参数 : {params_str}\n-------请求头 : {headers}\n-------请求方式 : GET')
        self.logger.debug(f"-------响应状态码---{resp.status_code}")
        try:
            self.logger.debug(f'-------请求返回值 : {resp.content.decode("utf-8")[:500]}')
        except:
            pass
        return resp

    def put(self,
            url,
            data=None,
            json=None,
            params=None,
            files=None,
            headers=None,
            allow_redirects=None,
            timeout=None,
            **kwargs):
        """发送put请求

        Args:
            url: 请求地址,形如"/api/demo@get"这样包含相对uri和method
            data: a dictionary of key-value pairs that will be urlencoded
               and sent as POST data
               or binary data that is sent as the raw body content
               or passed as such for multipart form data if ``files`` is also defined
            json: a value that will be json encoded
               and sent as POST data if files or data is not specified
            params: url parameters to append to the uri
            headers: a dictionary of headers to use with the request
            files: a dictionary of file names containing file data to POST to the server
            allow_redirects: Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
            timeout: connection timeout
            **kwargs: 其他允许的options

        Returns:
            接口response对象
        """

        redir = True if allow_redirects is None else allow_redirects
        headers = headers if headers else self.headers
        response = self.session.put(
            url,
            data,
            json=json,
            params=params,
            headers=headers,
            files=files,
            allow_redirects=redir,
            timeout=timeout,
            **kwargs)
        data_str = str(data)[:200]
        json_str = str(json)[:200]
        params_str = str(params)[:200] if str(params)[:200] else json_str
        if files:
            self.logger.debug(f'请求文件 : {files}')
        self.logger.debug(
            f'-------请求路径 : {url}\n-------请求参数 : {params_str}\n-------请求头 : {headers}\n-------请求方式 : PUT')
        self.logger.debug(f"-------响应状态码---{response.status_code}")
        try:
            self.logger.debug(f'-------请求返回值 : {response.content.decode("utf-8")}')
        except:
            pass
        return response

    def patch(self,
              url,
              data=None,
              json=None,
              params=None,
              files=None,
              headers=None,
              allow_redirects=None,
              timeout=None,
              **kwargs):

        """发送patch请求

        Args:
            url: 请求地址,形如"/api/demo@get"这样包含相对uri和method
            data: a dictionary of key-value pairs that will be urlencoded
               and sent as POST data
               or binary data that is sent as the raw body content
               or passed as such for multipart form data if ``files`` is also defined
            json: a value that will be json encoded
               and sent as POST data if files or data is not specified
            params: url parameters to append to the uri
            headers: a dictionary of headers to use with the request
            files: a dictionary of file names containing file data to POST to the server
            allow_redirects: Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
            timeout: connection timeout
            **kwargs: 其他允许的options

        Returns:
            接口response对象
        """

        redir = True if allow_redirects is None else allow_redirects
        headers = headers if headers else self.headers
        response = self.session.patch(
            url,
            data,
            json=json,
            params=params,
            headers=headers,
            files=files,
            allow_redirects=redir,
            timeout=timeout,
            **kwargs)
        data_str = str(data)[:40]
        json_str = str(json)[:40]
        self.logger.debug(
            f'PATCH Request : uri={url},params={params}, data={data_str}, json={json_str},headers={headers}, '
            f'files={files}, allow_redirects={redir}, timeout={timeout}, {kwargs}')
        try:
            self.logger.debug(f'Patch Response : {response.content.decode("utf-8")}')
        except:
            pass
        return response

    def delete(
            self,
            url,
            data=None,
            json=None,
            params=None,
            headers=None,
            allow_redirects=None,
            timeout=None,
            **kwargs):
        """发送delete请求

        Args:
            url: 请求地址,形如"/api/demo@get"这样包含相对uri和method
            data: a dictionary of key-value pairs that will be urlencoded
               and sent as POST data
               or binary data that is sent as the raw body content
               or passed as such for multipart form data if ``files`` is also defined
            json: a value that will be json encoded
               and sent as POST data if files or data is not specified
            params: url parameters to append to the uri
            headers: a dictionary of headers to use with the request
            allow_redirects: Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
            timeout: connection timeout
            **kwargs: 其他允许的options

        Returns:
            接口response对象
        """

        redir = True if allow_redirects is None else allow_redirects
        headers = headers if headers else self.headers
        response = self.session.delete(url, data=data, json=json, params=params, headers=headers, allow_redirects=redir,
                                       timeout=timeout, **kwargs)

        data_str = str(data)[:40]
        json_str = str(json)[:40]
        params_str = str(params)[:200] if str(params)[:200] else json_str
        self.logger.debug(
            f'-------请求路径 : {url}\n-------请求参数 : {params_str}\n-------请求头 : {headers}\n-------请求方式 : DELETE')
        self.logger.debug(f"-------响应状态码---{response.status_code}")
        try:
            self.logger.debug(f'-------请求返回值 : {response.content.decode("utf-8")}')
        except:
            pass
        return response

    def close(self):
        """关闭session连接"""
        self.session.close()

    @staticmethod
    def _format_data_to_log_string_according_to_header(data, headers):
        dataStr = "<empty>"
        if data is not None and headers is not None and 'Content-Type' in headers:
            if (headers['Content-Type'].find("application/json") != -1) or \
                    (headers['Content-Type'].find("application/x-www-form-urlencoded") != -1):
                if isinstance(data, bytes):
                    dataStr = data.decode('utf-8')
                else:
                    dataStr = data
            else:
                dataStr = "<" + headers['Content-Type'] + ">"

        return dataStr

    def _get_timeout(self, timeout):
        timeout = float(timeout) if timeout is not None else self.timeout
        return timeout

    @staticmethod
    def _get_str_from_bytes(data, coding="utf-8"):
        if isinstance(data, bytes):
            content = data.decode(coding)
            return content
        return data

    @staticmethod
    def _get_base64_from_data(data):
        import base64
        # 如果是二进制内容，直接把二进制编码成base64
        if isinstance(data, bytes):
            data = base64.encode(data)
        # 如果是字符串，尝试判断是不是文件
        elif isinstance(data, str):
            from os import path
            if path.isfile(data):
                with open(data) as f:
                    data = base64.encode(f.read())
        return data

    def _merge_headers(self, headers):
        if headers is None:
            headers = {}
        else:
            headers = headers.copy()
        headers.update(self.headers)

        return headers

    def _utf8_urlencode(self, data):

        if self._is_string_type(data):
            return data.encode('utf-8')

        if not isinstance(data, dict):
            return data

        utf8_data = {}
        for k, v in data.items():
            if self._is_string_type(v):
                v = v.encode('utf-8')
            utf8_data[k] = v
        return urlencode(utf8_data)

    @staticmethod
    def _is_json(data):
        try:
            json.loads(data)
        except (TypeError, ValueError):
            return False
        return True

    @staticmethod
    def _is_string_type(data):
        if isinstance(data, str):
            return True
        return False

    @staticmethod
    def encode_authentication(usercode, username):
        """将用户信息，转换成鉴权Header使用User的字符串，如'User: usercode%253Aadmin%2526username%253Aadmin'

        Args:
            usercode: 用户编号，string
            username: 用户名，string

        Returns:
            Header的User所需字符串
        """

        data = f'usercode:{usercode}&username:{username}'
        data = quote(data)
        data = quote(data)  # twice
        return data


if __name__ == '__main__':
    pass
