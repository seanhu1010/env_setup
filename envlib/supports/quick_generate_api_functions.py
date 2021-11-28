#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @Author:  sean
# 根据模板快捷生成api相关函数
# 依赖pandas与openpyxl

import logging
import pandas as pd

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_lib_file(resource_file):
    df = pd.read_excel(resource_file)
    for row in df.iterrows():
        description = row[1].description
        func_name = row[1].func_name if not pd.isna(row[1].func_name) else ''
        func_params = row[1].func_params + ', ' if not pd.isna(row[1].func_params) else ''
        uri = row[1].uri if not pd.isna(row[1].uri) else ''
        method = row[1].method if not pd.isna(row[1].method) else ''
        json = row[1].json if not pd.isna(row[1].json) else ''
        params = row[1].params if not pd.isna(row[1].params) else ''
        data = row[1].data if not pd.isna(row[1].data) else ''
        if_bind = row[1].if_bind if not pd.isna(row[1].if_bind) else ''
        key = row[1].key if not pd.isna(row[1].key) else ''
        value = row[1].value if not pd.isna(row[1].value) else 'res'
        lock = True if not pd.isna(row[1].lock) and row[1].lock == '是' else False
        ret = row[1].ret if not pd.isna(row[1].ret) else 'res'

        if ', **kwargs' in func_params:
            fu1 = f'@classmethod\ndef {func_name}(cls, {func_params.strip(", **kwargs")}check=True, **kwargs):\n    """{description}"""\n\n'
        elif func_params == '**kwargs, ':
            fu1 = f'@classmethod\ndef {func_name}(cls, check=True, **kwargs):\n    """{description}"""\n\n'
        else:
            fu1 = f'@classmethod\ndef {func_name}(cls, {func_params}check=True):\n    """{description}"""\n\n'

        if json != '':
            fu2 = f'    res = app.send_by_rest(\'{uri}@{method}\', json={json}, check=check)\n'
        elif params != '':
            fu2 = f'    res = app.send_by_rest(\'{uri}@{method}\', params={params}, check=check)\n'
        elif data != '':
            fu2 = f'    res = app.send_by_rest(\'{uri}@{method}\', data={data}, check=check)\n'
        else:
            fu2 = f'    res = app.send_by_rest(\'{uri}@{method}\', check=check)\n'

        fu3 = '    \n'
        if if_bind == '是':
            fu3 = f'    app.bind_to_g(key=\'{key}\', value={value}, lock={lock})\n'

        fu4 = f'    return {ret}\n'

        print(fu1 + fu2 + fu3 + fu4)


if __name__ == '__main__':
    # 根据模板修改对应接口函数信息，自动生成接口函数
    # generate_lib_file('template.xlsx')
    pass
