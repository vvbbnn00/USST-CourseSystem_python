# _*_ coding: utf-8 _*_
"""
Time:     2022/6/29 14:43
Author:   不做评论(vvbbnn00)
Version:
File:     course.py
Describe:
"""
import exceptions


class CourseException(exceptions.SoftwareException):
    code = 200
    message = '课程系统错误'
    detail = '未知错误'


class CourseSettingError(CourseException):
    code = 201
    message = '课程系统配置有误'

    def __init__(self, detail: str):
        if detail:
            self.detail = detail


class CourseCancelFailed(CourseException):
    code = 202
    message = '退课失败'

    def __init__(self, detail: str):
        if detail:
            self.detail = detail


class CourseSelectFailed(CourseException):
    code = 203
    message = '选课失败'

    def __init__(self, detail: str):
        if detail:
            self.detail = detail


class CourseNotExist(CourseException):
    code = 204
    message = '课程不存在'

    def __init__(self, detail: str):
        if detail:
            self.detail = detail


class CourseExists(CourseException):
    code = 205
    message = '课程已存在'

    def __init__(self, detail: str):
        if detail:
            self.detail = detail
