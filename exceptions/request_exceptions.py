# _*_ coding: utf-8 _*_
"""
Time:     2022/6/21 15:30
Author:   不做评论(vvbbnn00)
Version:  
File:     request.py
Describe: 请求错误
"""
import exceptions


class RequestException(exceptions.SoftwareException):
    code = 400
    message = '请求错误'
    detail = '未知错误'


class BadRequestException(RequestException):
    code = 400
    message = '无效的请求'

    def __init__(self, detail=None):
        if detail:
            self.detail = detail


class HttpRequestException(RequestException):
    code = 401
    message = 'HTTP请求不被支持'


class RequestTooLargeException(RequestException):
    code = 402
    message = '请求内容过大，已被丢弃'


class RouteNotFoundException(RequestException):
    code = 404
    message = '请求路径不存在'


class RequestTooFast(RequestException):
    code = 405
    message = '请求超过速率限制，请稍后再试'
