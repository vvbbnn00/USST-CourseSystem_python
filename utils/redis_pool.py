# _*_ coding: utf-8 _*_
"""
Time:     2022/7/3 13:26
Author:   不做评论(vvbbnn00)
Version:  
File:     redis_pool.py
Describe: 
"""
import redis

from config.redis_config import *


class RedisClient:
    def __init__(self):
        if not hasattr(RedisClient, 'pool'):
            RedisClient.getRedisCoon()  # 创建redis连接
        self.conn = redis.Redis(connection_pool=RedisClient.pool)

    @staticmethod
    def getRedisCoon():
        RedisClient.pool = redis.ConnectionPool(host=REDIS_HOST, password=REDIS_PASSWD,
                                                port=REDIS_PORT, db=REDIS_DB)

    def setRedis(self, key, value, time=None):
        """
        设置Redis键
        :param key:
        :param value:
        :param time:
        :return:
        """
        # 非空即真非0即真
        if time:
            res = self.conn.setex(key, time, value)
        else:
            res = self.conn.set(key, value)
        return res

    def getRedis(self, key):
        """
        获取Redis值
        :param key:
        :return:
        """
        res = self.conn.get(key)
        if res is None:
            return None
        return res.decode()

    def delRedis(self, key):
        """
        删除Redis值
        :param key:
        :return:
        """
        res = self.conn.delete(key)
        return res

    def lua(self, script):
        """
        执行脚本

        :param script:
        :return:
        """
        cmd = self.conn.register_script(script)
        res = cmd()
        return res


redis_pool = RedisClient()

if __name__ == '__main__':
    # 测试
    course_id = "2022-01-000001-01"
    req = redis_pool.lua(f"""
    local now_member = redis.call('get','now_member__{course_id}')
    local total_member = redis.call('get','total_member__{course_id}')
    if (not now_member or not total_member) then
        return -2
        -- 未初始化
    else
        if (tonumber(now_member)>=tonumber(total_member)) then
            return -1
            -- 已满
        end
    end
    redis.call('incr', 'now_member__{course_id}')
    return 1""")

    print(req)
