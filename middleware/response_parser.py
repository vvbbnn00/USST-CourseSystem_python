# _*_ coding: utf-8 _*_
"""
Time:     2022/6/21 21:22
Author:   不做评论(vvbbnn00)
Version:  0.1
File:     response_parser.py
Describe: 处理异常情况下的相应

返回格式如下
socket 0.1\n # 此处socket为签名，版本号为识别不同版本协议的基础
<server_name> <resp_start_timestamp> <resp_end_timestamp>\n # 第二行为服务端信息，用空格分割
<status_code>\n # 状态码，正常为0，其他情况均为异常情况
<message>\n # 额外信息，为JSON格式
"""
import datetime
import json
import time

import exceptions
import exceptions.request_exceptions


class ResponseData:
    """
    响应数据
    """
    server_name: str = 'Socket_Server'
    timestamp: int
    status_code: int = 0
    message: dict = {}

    def __init__(self, message: dict = None):
        self.timestamp = int(time.time())
        if message:
            self.message = message
        else:
            self.message = {}

    def __str__(self):
        ret_msg = f"""{self.timestamp},{int(time.time())},{self.status_code},{json.dumps(self.message)}"""
        ret_data = f"""socket 0.1{str(len(bytes(ret_msg.encode('utf8')))).zfill(10)}{ret_msg}"""
        return ret_data


def dealExceptionData(exception: Exception):
    """
    处理异常情况下返回数据
    :param exception:
    :return:
    """
    if type(exception) is exceptions.request_exceptions.HttpRequestException:
        body = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Socket Server</title>
</head>

<body>
    <h1>Socket Server</h1>
    <p>HTTP Protocol Is Not Supported.</p>
    <hr>
    <p>© {datetime.datetime.now().year} <a href=//www.vvbbnn00.cn>vvbbnn00</a>. All rights reserved.</p>
</body>

</html>"""
        return f"""HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: {len(body)}
Server: bzpl-server
{body}
""".encode('utf8')
    elif issubclass(type(exception), exceptions.SoftwareException):
        message = {
            'message': f'{exception.message}({exception.detail})'
        }
        resp = ResponseData(message)
        resp.status_code = exception.code
        return str(resp).encode('utf8')
    else:
        message = {
            'message': f'未知错误({str(exception)})'
        }
        resp = ResponseData(message)
        resp.status_code = -1
        return str(resp).encode('utf8')


if __name__ == '__main__':
    resp_data = ResponseData()
    resp_data.server_name = '111'
    resp_data.status_code = 1
    resp_data.message = {
        'o': 'k'
    }
    print(resp_data)
