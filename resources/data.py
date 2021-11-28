# -*- coding=utf-8 -*-
import configparser
import os

# 路径常量
resources_path = os.path.dirname(__file__)
root_path = os.path.split(resources_path)[0]

# 解析env.ini
config = configparser.ConfigParser()
config_file = os.path.join(root_path, 'env.ini')
config.read(config_file, encoding='utf-8')

# 主机变量
HOST_IP = config.get('host', 'ip')
PLATFORM_PORT = config.get('host', 'platform_port')

# ssh信息
SSH_NAME = config.get('host', 'user')
SSH_PASSWORD = config.get('host', 'pwd')
SSH_PWD = config.get('host', 'pwd')

# 默认常量
DEFAULT_PLATFORM_IP = HOST_IP  # 默认平台地址
BASE_PLATFORM_URL = "http://{}:{}".format(HOST_IP, PLATFORM_PORT)  # 平台URL
REST_USERNAME = config.get('host', 'api_user')
REST_USERCODE = config.get('host', 'api_user_code')
REST_PASSWORD = config.get('host', 'api_password')

# 默认headers（临时鉴权）
headers = {
    "Content-Type": "application/json",
    "charset": "utf-8",
    "User": "username%253Aadmin%2526usercode%253Aadmin"
}
HEADERS = {  # 正常登录后的的header
    "Authorization": f"username:{REST_USERNAME}&usercode:{REST_USERCODE}",
    "User": f"username:{REST_USERNAME}&usercode:{REST_USERCODE}",
    "Content-Type": "application/json;charset=utf-8"
}

# 自动化通用配置
AUTO_CONFIG = dict(config.items('auto_config'))

# 存储配置
STORAGE_CONFIG = dict(config.items(AUTO_CONFIG.get('storage_type')))

# Tag列表，英中文对应
TAG_LIST = dict(config.items('tag_list'))

# smb协议访问远端路径 相关参数
SMB_SERVER = config.get('smb_client', 'server')
SMB_USERNAME = config.get('smb_client', 'username')
SMB_PASSWORD = config.get('smb_client', 'password')
SMB_SHARE_PATH = config.get('smb_client', 'share_path')
