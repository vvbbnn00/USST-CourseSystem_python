# _*_ coding: utf-8 _*_
"""
Time:     2022/6/23 22:49
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py
Describe: 
"""


class RouteInfo:
    ROUTE_NAME = 'user'
    BEFORE_MIDDLEWARE = []
    AFTER_MIDDLEWARE = []

    import service.user.login as user_login
    import service.user.manage as user_manage

    ROUTE_LIST = {
        'login': {
            'disable_super_before': True,  # 禁用父类的before中间件
            'before': [],
            'fun': user_login.login,
            'after': [],
            'disable_super_after': True,  # 禁用父类的after中间件
        },
        'getUserInfo': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': user_login.getUserInfo,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'changePassword': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': user_login.changePassword,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'getUserList': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': user_manage.getUserList,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'submit': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': user_manage.submitUser,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
    }
