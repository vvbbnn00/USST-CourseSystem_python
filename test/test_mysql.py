# _*_ coding: utf-8 _*_
"""
Time:     2022/6/29 11:09
Author:   不做评论(vvbbnn00)
Version:  
File:     mysql.py
Describe: 
"""

from mysql import pool

if __name__ == '__main__':
    sql = "select * from courses"
    pool.getconn()  # 每次都重新获取连接
    ret = pool.getOne(sql)  # 执行sql获取结果
    print(ret)
    pool.dispose()  # commit sql 并将conn重新放回连接池
