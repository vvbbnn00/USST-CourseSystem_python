# _*_ coding: utf-8 _*_
"""
Time:     2022/6/22 20:46
Author:   不做评论(vvbbnn00)
Version:  0.1
File:     server_status.py
Describe: 返回服务器状态，用于测试路由模块是否工作正常
"""
import time

from annotations import RequestContext
from service.semester.semester_data import getCurrentSemester, getSchoolName


def getServerStatus(context: RequestContext) -> RequestContext:
    """
    获取服务器状态，默认返回请求IP、ok和当前时间戳

    :param context: 上下文
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    logger.info('正常接收到信息，准备返回')
    logger.info(request.content)
    context.response.message.update({
        'request_ip': request.client_ip,
        'timestamp': int(time.time()),
        'school': getSchoolName(),
        'semester': getCurrentSemester()
    })
    return context
