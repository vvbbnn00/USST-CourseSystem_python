# _*_ coding: utf-8 _*_
"""
Time:     2022/7/3 13:52
Author:   不做评论(vvbbnn00)
Version:  
File:     load_cache.py
Describe: 加载课程信息缓存，请将此文件添加至cron，周期建议不高于24小时
"""
from mysql import pool
from service.semester.semester_data import getCurrentSemester
from utils.redis_pool import redis_pool


def loadCourse(course_id):
    """
    刷新某个课程的缓存

    :param course_id:
    :return:
    """
    course_sql = f"SELECT course_id, max_members," \
                 f"(select count(id) from selections where selections.course_id=courses.course_id) " \
                 f"as current_members" \
                 f" from courses where course_id=%s;"
    pool.getconn()
    course_data = pool.getAll(course_sql, [course_id])
    pool.dispose()
    if not course_data:
        course_data = []
    for c in course_data:
        redis_pool.setRedis(f'now_member__{bytes(c["course_id"]).decode()}',
                            c["current_members"],
                            86400)  # 总量
        redis_pool.setRedis(f'total_member__{bytes(c["course_id"]).decode()}',
                            c["max_members"],
                            86400)  # 当前人数


def reloadAllCourses():
    """
    重载所有课程信息
    :return:
    """
    current_semester = getCurrentSemester()  # 当前学期
    req_sql = f"SELECT course_id, max_members," \
              f"(select count(id) from selections where selections.course_id=courses.course_id) " \
              f"as current_members" \
              f" from courses where semester=%s;"
    pool.getconn()
    course_list = pool.getAll(req_sql, [current_semester])
    pool.dispose()
    if not course_list:
        course_list = []
    for course in course_list:
        redis_pool.setRedis(f'now_member__{bytes(course["course_id"]).decode()}',
                            course["current_members"],
                            86400)  # 总量
        redis_pool.setRedis(f'total_member__{bytes(course["course_id"]).decode()}',
                            course["max_members"],
                            86400)  # 当前人数


if __name__ == '__main__':
    reloadAllCourses()
