# _*_ coding: utf-8 _*_
"""
Time:     2022/6/23 22:49
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py
Describe: 
"""


class RouteInfo:
    ROUTE_NAME = 'course'
    BEFORE_MIDDLEWARE = []
    AFTER_MIDDLEWARE = []

    import service.course.course_data as course_data

    ROUTE_LIST = {
        'getCourseList': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': course_data.getCourseList,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'getStuCourseTable': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': course_data.getStuCourseTable,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'cancel': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': course_data.studentCancelCourse,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'select': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': course_data.studentSelectCourse,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'getStudentSelectionList': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': course_data.getStudentSelectionList,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'submit': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': course_data.submitCourse,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'adminAdd': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': course_data.adminAddCourse,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'adminCancel': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': course_data.adminCancelCourse,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        },
        'deleteCourse': {
            'disable_super_before': False,  # 禁用父类的before中间件
            'before': [],
            'fun': course_data.deleteCourse,
            'after': [],
            'disable_super_after': False,  # 禁用父类的after中间件
        }
    }
