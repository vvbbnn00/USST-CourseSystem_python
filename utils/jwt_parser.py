# _*_ coding: utf-8 _*_
"""
Time:     2022/6/21 15:25
Author:   不做评论(vvbbnn00)
Version:  
File:     jwt_parser.py
Describe: 解析JWT信息，包括是否过期等内容
"""
import base64
import hashlib
import hmac
import json
import time

import exceptions.auth_exceptions
from config.security import JWT_KEY


def _decode(b64_data):
    """
    base64解密
    :param b64_data: 原始数据
    :return:
    """
    return base64.b64decode(b64_data).decode()


class JWT:
    """
    JWT对象
    """
    exp: int
    data: dict

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data

    def __genSignature(self, headers=None):
        """
        生成JWT签名
        :return:
        """
        if headers is None:
            headers = {
                "typ": "JWT",
                "alg": "HS256"
            }
            headers = base64.b64encode(json.dumps(headers).encode('utf8')).decode()
        payload = base64.b64encode(json.dumps(self.data).encode('utf8')).decode()
        signature = base64.urlsafe_b64encode(
            hmac.new(JWT_KEY.encode('utf-8'), f'{headers}.{payload}'.encode('utf-8'), hashlib.sha256).digest()).decode(
            'utf-8').replace('=', '')
        return signature

    def loadJWT(self, raw_token: str):
        """
        通过JWT加载数据

        :param raw_token:
        :return:
        """
        try:
            header_raw, payload, signature = raw_token.split('.')
            header, payload = json.loads(_decode(header_raw)), json.loads(_decode(payload))
            if header.get('typ') != 'JWT' or header.get('alg') != 'HS256':
                raise exceptions.auth_exceptions.JWTInvalidException()
            self.data = payload
            self.exp = int(payload['exp'])
            if time.time() > self.exp:
                raise exceptions.auth_exceptions.JWTExpiredException()
            signature_raw = self.__genSignature(header_raw)
            if signature_raw != signature:
                raise exceptions.auth_exceptions.JWTInvalidException()
        except exceptions.auth_exceptions.AuthException:
            raise
        except Exception:
            raise exceptions.auth_exceptions.JWTInvalidException()

    def get(self, key, default=None):
        """
        获取JWT内容

        :param key:
        :param default:
        :return:
        """
        r = self.data.get(key)
        if r is None:
            return default
        return r

    def generateJWT(self, exp=86400):
        """
        生成JWT

        :param exp: 过期时间，单位秒
        :return:
        """
        self.data['exp'] = int(time.time()) + exp
        self.data['iat'] = int(time.time())
        headers = {
            "typ": "JWT",
            "alg": "HS256"
        }
        headers = base64.b64encode(json.dumps(headers).encode('utf8')).decode()
        payload = base64.b64encode(json.dumps(self.data).encode('utf8')).decode()
        return f'{headers}.{payload}.{self.__genSignature(headers)}'


if __name__ == '__main__':
    jwt = JWT({
        'uid': '001',
        'permission': 'admin'
    })
    print(jwt.generateJWT())

    jwt1 = JWT()
    jwt1.loadJWT('eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJIUzI1NiJ9.eyJ1aWQiOiAiMDAxIiwgInBlcm1pc3Npb24iOiAiYWRtaW4iLCAiZXhwI'
                 'jogMTY1NTgxMjI4MiwgImlhdCI6IDE2NTU4MDUwODJ9.lFGc6eNf5PlEZTnTgnDiZYQnLMLZpQxRBj54xdJI9Bw')
    print(jwt1.exp)
