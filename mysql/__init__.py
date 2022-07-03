# _*_ coding: utf-8 _*_
"""
Time:     2022/6/29 11:08
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py
Describe: 
"""
from mysql import db_config
from mysql.db_connection import MyPymysqlPool

pool = MyPymysqlPool(db_config)  # config_db 为配置的数据库参数文件
