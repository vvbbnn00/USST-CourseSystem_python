# _*_ coding: utf-8 _*_
"""
Time:     2022/6/22 20:57
Author:   不做评论(vvbbnn00)
Version:  
File:     init_exceptions.py
Describe: 
"""
import exceptions


class InitException(exceptions.SoftwareException):
    code = -100
    message = '内部错误'
    detail = '未知错误'


class DuplicatedRouteException(InitException):
    code = -101
    detail = '路由路径有重复'

    def __init__(self, route: str):
        self.detail = '路由路径有重复:"' + route + '"已存在'


class WrongRouteType(InitException):
    code = -102
    detail = '路由类型有误'

    def __init__(self, err_type: str):
        self.detail = '错误的路由目的地类型:"' + err_type + '", 应为function(Context)->Context'


class SemesterNotExist(InitException):
    code = -103
    detail = '该学期限制信息未配置或学期不存在'


class RedisNotLoaded(InitException):
    code = -104
    detail = '缓存服务器未加载成功，请检查自动任务是否配置正确'
