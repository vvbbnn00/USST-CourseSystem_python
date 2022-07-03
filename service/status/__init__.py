# _*_ coding: utf-8 _*_
"""
Time:     2022/6/22 20:49
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py
Describe: 
"""


class RouteInfo:
    ROUTE_NAME = 'status'
    BEFORE_MIDDLEWARE = []
    AFTER_MIDDLEWARE = []

    import service.status.server_status as server_status

    ROUTE_LIST = {
        'get_server_status': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': server_status.getServerStatus,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        }
    }
