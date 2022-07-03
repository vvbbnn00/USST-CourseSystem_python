# _*_ coding: utf-8 _*_
"""
Time:     2022/6/21 15:43
Author:   不做评论(vvbbnn00)
Version:  
File:     auth_exceptions.py
Describe: 权限模块错误
"""
import exceptions


class AuthException(exceptions.SoftwareException):
    code = 100
    detail = '未知错误'
    message = '权限错误'


class JWTInvalidException(AuthException):
    code = 101
    detail = '无效的JWT，鉴权失败'
    message = '鉴权失败'


class JWTExpiredException(AuthException):
    code = 102
    detail = '登录已过期，请重新登录'
    message = '登录过期'


class PermissionException(AuthException):
    code = 103
    detail = '您没有权限访问该内容'
    message = '权限不足'


class PasswordErrorException(AuthException):
    code = 104
    detail = '用户名或密码有误，或账号被锁定，请检查后重试'
    message = '登录失败'


class AccountLockedException(AuthException):
    code = 105
    detail = '账号已被锁定，请联系管理员'
    message = '账号被锁定'


class OriPasswordErrorException(AuthException):
    code = 106
    detail = '原始密码错误，请检查后重试'
    message = '修改密码失败'
