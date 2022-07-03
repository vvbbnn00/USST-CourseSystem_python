# _*_ coding: utf-8 _*_
"""
Time:     2022/6/21 14:46
Author:   不做评论(vvbbnn00)
Version:  0.1
File:     request_parser.py
Describe: 请求解析模块

目前暂定请求格式如下
socket 0.1\n # 此处socket为签名，版本号为识别不同版本协议的基础
<client_name> <os> <timestamp> <version> <sign>\n # 第二行为客户端信息，用空格分割
<client_token|null>\n # 第三行为客户端鉴权信息，使用jwt，如无则传入null
<ACTION>\n # 第四行为传入的操作信息
<content>\n # JSON传入信息
"""
import hashlib
import hmac
import json
import time

import exceptions.auth_exceptions
import exceptions.request_exceptions
from utils.jwt_parser import JWT


class RequestData:
    """
    请求数据类
    """
    action: str = None
    client_name: str = None
    client_os: str = None
    client_ip: str = None
    client_port: int = 0
    request_timestamp: int = None
    request_version: str = None
    content: dict = None
    user_data: dict or None

    def __init__(self, client_name, client_os, request_timestamp, request_version):
        self.client_name, self.client_os, self.request_timestamp, self.request_version = \
            client_name, client_os, request_timestamp, request_version


def parseRequestData(request_data: str):
    """
    解析请求的数据，按照0.1版本的解析规范
    :param request_data: 请求数据，为str格式
    :return: 解析成功的数据
    """
    request_data = request_data.strip().split('\n')
    socket_info = request_data[0]
    if socket_info.find('HTTP/') > -1:
        raise exceptions.request_exceptions.HttpRequestException()
    if socket_info != 'socket 0.1':
        raise exceptions.request_exceptions.BadRequestException('无效的请求格式或不支持的版本')
    try:
        client_name, client_os, request_timestamp, request_version, sign = request_data[1].split(' ')  # 客户端基础信息
        # print(sign, request_timestamp)
        if time.time() - int(request_timestamp) > 60:
            raise exceptions.request_exceptions.BadRequestException('请求已过期，请重新发起')
        action = request_data[3]
        json_payload = '\n'.join(request_data[4:])
        request = RequestData(client_name, client_os, int(request_timestamp), request_version)
        request.action = action
        user_info = None
        if action != 'user.login':
            user_info = None if request_data[2] == 'null' else JWT()
            if user_info:
                user_info.loadJWT(request_data[2])
        # print(json_payload)
        # print(json_payload.encode())
        if user_info:
            secret = user_info.get('device_uuid')
            sign_data = json_payload + str(request_timestamp)
            hmac_sha256 = hmac.new(secret.encode(), sign_data.encode(), digestmod=hashlib.sha256).hexdigest()
            # print(secret, sign_data, hmac_sha256)
            if hmac_sha256 != sign:
                raise exceptions.request_exceptions.BadRequestException('请求验证失败，疑似被篡改')
        json_payload = json.loads(json_payload)
        request.content = json_payload
        request.user_data = user_info
        return request
    except exceptions.SoftwareException:
        raise
    except Exception:
        raise exceptions.request_exceptions.BadRequestException('请求内容解析失败')


if __name__ == '__main__':
    test_request = parseRequestData("""socket 0.1
test_platform MacOS 0 1.0
eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJIUzI1NiJ9.eyJ1aWQiOiAiMDAxIiwgInBlcm1pc3Npb24iOiAiYWRtaW4iLCAiZXhwIjogMTY1NTgxMjI5OCwgImlhdCI6IDE2NTU4MDUwOTh9.qNt1Sk0lSz2ScDj28nvtOR6kF5uFlwjfc370aFcVatk
test
{"message": "hello"}""")
    print(test_request.action)
