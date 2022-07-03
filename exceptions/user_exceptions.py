# _*_ coding: utf-8 _*_
"""
Time:     2022/7/1 17:32
Author:   不做评论(vvbbnn00)
Version:  
File:     user_exceptions.py
Describe: 权限模块错误
"""
import exceptions


class UserException(exceptions.SoftwareException):
    code = 600
    detail = '未知错误'
    message = '用户错误'


class UserNotFoundException(UserException):
    code = 601
    detail = '所输入的用户不存在或不符合权限要求'
    message = '用户不存在'


class UserExistsException(UserException):
    code = 602
    detail = '该UID的用户已存在'
    message = '用户一存在'
