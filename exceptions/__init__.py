# _*_ coding: utf-8 _*_
"""
Time:     2022/6/21 21:37
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py
Describe: 通用错误
"""


class SoftwareException(Exception):
    code = -1
    message = '未知错误'
    detail = '未知错误'
