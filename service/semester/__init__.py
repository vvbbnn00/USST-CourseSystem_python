# _*_ coding: utf-8 _*_
"""
Time:     2022/7/2 16:35
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py
Describe: 
"""


class RouteInfo:
    ROUTE_NAME = 'semester'
    BEFORE_MIDDLEWARE = []
    AFTER_MIDDLEWARE = []

    import service.semester.semester_data as semester_data

    ROUTE_LIST = {
        'getLimitList': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': semester_data.getLimitList,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'submit': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': semester_data.submitSemester,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'deleteSemester': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': semester_data.deleteSemester,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'changeSemester': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': semester_data.changeSemester,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'changeSchoolName': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': semester_data.changeSchool,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
    }
