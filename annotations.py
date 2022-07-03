# _*_ coding: utf-8 _*_
"""
Time:     2022/6/22 21:52
Author:   不做评论(vvbbnn00)
Version:  
File:     annotations.py
Describe: 关键类型声明
"""
import middleware.request_parser
import middleware.response_parser
from utils.global_logger import logger

CRITICAL = 50
ERROR = 40
WARN = 30
INFO = 20
DEBUG = 10


class ServiceLogger:
    """
    服务器日志模块
    """
    request_uuid: str
    request_ip: str
    request_port: int

    def __init__(self, request_uuid: str, request_ip: str, request_port: int):
        self.request_uuid, self.request_ip, self.request_port = request_uuid, request_ip, request_port

    def _log(self, level, msg, *args, **kwargs):
        msg = f'[{self.request_ip}:{self.request_port},{self.request_uuid}] {msg}'
        logger.log(level, msg, *args, **kwargs, stacklevel=3)

    def debug(self, msg, *args, **kwargs):
        self._log(DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log(INFO, msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self._log(WARN, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log(CRITICAL, msg, *args, **kwargs)


class RequestContext:
    """
    请求上下文，包含请求内容和响应内容
    """
    request: middleware.request_parser.RequestData
    response: middleware.response_parser.ResponseData
    logger: ServiceLogger

    def __init__(self, request: middleware.request_parser.RequestData,
                 response: middleware.response_parser.ResponseData, logger_: ServiceLogger):
        self.request, self.response, self.logger = request, response, logger_
