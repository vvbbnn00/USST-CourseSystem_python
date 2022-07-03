# _*_ coding: utf-8 _*_
"""
Time:     2022/6/22 20:46
Author:   不做评论(vvbbnn00)
Version:  0.1
File:     course_data.py
Describe: 课程信息模块
"""
import datetime
import json
import math
import re

import exceptions.auth_exceptions
import exceptions.course_exceptions
import exceptions.init_exceptions
import exceptions.request_exceptions
import exceptions.user_exceptions
from annotations import RequestContext
from config.pattern import *
from mysql import pool
from scripts.load_cache import loadCourse, reloadAllCourses
from service.semester.semester_data import getCurrentSemester
from utils.redis_pool import redis_pool

QUERY_ORDER_BY = {
    0: "course_id DESC",
    1: "points DESC",
    2: "points ASC"
}
WEEKDAY_DICT = " 一二三四五六日"


def getCourseList(context: RequestContext) -> RequestContext:
    """
    获取课程列表

    :param context: 上下文
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    page, page_size, semester, search_kw, sort_method = \
        request.content.get("page"), \
        request.content.get("size"), \
        request.content.get("semester"), \
        request.content.get("kw"), \
        request.content.get("sort_method")
    if page is None or page_size is None or sort_method is None:
        raise exceptions.request_exceptions.BadRequestException("缺少参数")
    try:
        page = int(page)
        page_size = int(page_size)
        sort_method = int(sort_method)
        if semester:
            semester = str(semester)
        assert page > 0, 'page需为大于0的整数'
        assert 1 <= page_size <= 20, 'pageSize需在1~20之间'
        assert sort_method in [0, 1, 2], 'sortMethod不符合规范'
    except AssertionError as e:
        raise exceptions.request_exceptions.BadRequestException(str(e))
    except:
        raise exceptions.request_exceptions.BadRequestException("参数类型错误")

    if request.content.get('manage'):
        if request.user_data.get('role') == 0:
            raise exceptions.auth_exceptions.PermissionException()

    logger.info(f'查询 page={page}, page_size={page_size}, semester={semester},'
                f' search_kw={search_kw}, sort_method={sort_method}, user={request.user_data.get("username")}')

    where_condition = []
    where_param = []
    if search_kw:
        search_kw = f"%{search_kw}%"
        where_condition.append("(course_id like %s)or(description like %s)or(title like %s)")
        where_param.extend([search_kw, search_kw, search_kw])
    if semester:
        where_condition.append("semester like %s")
        where_param.append(semester)
    pool.getconn()
    total = pool.getOne(f"SELECT count(course_id) from courses "
                        f"{'where (' + ')and('.join(where_condition) + ')' if len(where_condition) > 0 else ''}",
                        where_param)
    total = total['count(course_id)']
    if math.ceil(total / page_size) < page:
        page = math.ceil(total / page_size)
    if page == 0:
        page = 1
    max_score_data = [0, 0]
    if request.content.get('course_selection'):
        if semester != getCurrentSemester():  # 仅能对当前学期课程进行选课
            raise exceptions.auth_exceptions.PermissionException()
        max_score_info = pool.getOne(f"""select sum(courses.points) as current_score, semester_limits.max_score from 
            courses, semester_limits, selections where selections.uid=%s and 
            selections.course_id=courses.course_id and semester_limits.semester=%s 
            and courses.semester=%s;""", [request.user_data.get('username'), semester, semester])
        if max_score_info['max_score'] is None:
            raise exceptions.course_exceptions.CourseSettingError("该学期的选课尚未配置，无法选课")
        max_score_data = [max_score_info['current_score'], max_score_info['max_score']]
        req_sql = f"SELECT course_id, title, description, `type`, semester, schedule, " \
                  f"week_start, week_end, points, " \
                  f"users.uid as teacher_uid, users.name as teacher_name, " \
                  f"max_members," \
                  f"(select count(id) from selections where selections.course_id=courses.course_id) " \
                  f"as current_members," \
                  f"((select select_date from selections where selections.course_id=courses.course_id and " \
                  f"selections.uid=%s)) as selection_time" \
                  f" from courses, users where (teacher=users.uid) " \
                  f"{'and(' + ')and('.join(where_condition) + ')' if len(where_condition) > 0 else ''}" \
                  f" ORDER BY {QUERY_ORDER_BY[sort_method]} " \
                  f"LIMIT {page_size} OFFSET {(page - 1) * page_size};"
        where_param = [request.user_data.get('username')] + where_param
    elif request.content.get('manage'):
        req_sql = f"SELECT course_id, title, description, `type`, semester, schedule, " \
                  f"week_start, week_end, points, " \
                  f"users.uid as teacher_uid, users.name as teacher_name, " \
                  f"max_members," \
                  f"(select count(id) from selections where selections.course_id=courses.course_id) " \
                  f"as current_members" \
                  f" from courses, users where (teacher=users.uid) and (courses.teacher=%s) " \
                  f"{'and(' + ')and('.join(where_condition) + ')' if len(where_condition) > 0 else ''}" \
                  f" ORDER BY {QUERY_ORDER_BY[sort_method]} " \
                  f"LIMIT {page_size} OFFSET {(page - 1) * page_size};"
        where_param = [request.user_data.get('username')] + where_param
    else:
        req_sql = f"SELECT course_id, title, description, `type`, semester, schedule, " \
                  f"week_start, week_end, points, " \
                  f"users.uid as teacher_uid, users.name as teacher_name, " \
                  f"max_members," \
                  f"(select count(id) from selections where selections.course_id=courses.course_id) " \
                  f"as current_members" \
                  f" from courses, users where (teacher=users.uid) " \
                  f"{'and(' + ')and('.join(where_condition) + ')' if len(where_condition) > 0 else ''}" \
                  f" ORDER BY {QUERY_ORDER_BY[sort_method]} " \
                  f"LIMIT {page_size} OFFSET {(page - 1) * page_size};"
    # print(req_sql)
    ret = pool.getAll(req_sql, where_param)
    if not ret:
        ret = []
    pool.dispose()

    ret_data = []
    for item in ret:
        append_data = {
            'course_id': bytes(item.get('course_id')).decode("utf8"),
            'title': bytes(item.get('title')).decode("utf8"),
            'description': bytes(item.get('description')).decode("utf8"),
            'type': int(item.get('type')),
            'semester': bytes(item.get('semester')).decode("utf8"),
            'schedule': json.loads(bytes(item.get('schedule'))),
            'week_start': int(item.get('week_start')),
            'week_end': int(item.get('week_end')),
            'points': float(item.get('points')),
            'teacher': {
                'uid': bytes(item.get('teacher_uid')).decode("utf8"),
                'name': bytes(item.get('teacher_name')).decode("utf8"),
            },
            'max_members': int(item.get('max_members')),
            'current_members': int(item.get('current_members')),
        }
        if request.content.get("course_selection"):
            append_data.update({
                'status': 1 if item.get('selection_time') is not None else 2 if int(item.get('max_members')) <= int(
                    item.get('current_members')) else 0,
                'locked_reason': '您当前已选择该课' if item.get('selection_time') is not None else '该课已选满'
                if int(item.get('max_members')) <= int(item.get('current_members')) else '',
                'selection_time': int(item.get('selection_time').timestamp()) if item.get(
                    'selection_time') is not None else 0
            })
        ret_data.append(append_data)
    context.response.message.update({
        "total": total,
        "page": page,
        "current_total": len(ret),
        "current_score": max_score_data[0],
        "max_score": max_score_data[1],
        "max_page": math.ceil(total / page_size),
        "page_size": page_size,
        "data": ret_data
    })
    return context


def getStuCourseTable(context: RequestContext) -> RequestContext:
    """
    获取学生某学期课表

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    semester = request.content.get("semester")

    if semester is None:
        raise exceptions.request_exceptions.BadRequestException("学期不能为空")

    cache = redis_pool.getRedis(f"cache_stuTable_{request.user_data.get('username')}_{semester}")
    if cache is not None:
        ret_data = json.loads(cache)
        context.response.message.update(ret_data)
        logger.info("Hit Cache")
        return context

    pool.getconn()
    req_sql = f"""SELECT courses.course_id, title, description, `type`, semester, schedule, 
    week_start, week_end, points, 
    users.uid as teacher_uid, users.name as teacher_name
    from courses, users, selections where courses.teacher=users.uid 
    and selections.course_id=courses.course_id and 
    selections.uid=%s and courses.semester=%s;"""
    ret = pool.getAll(req_sql, [request.user_data.get('username'), semester])
    if not ret:
        ret = []
    ret_data = []
    score_total = 0.0
    for item in ret:
        score_total += float(item.get('points'))
        append_data = {
            'course_id': bytes(item.get('course_id')).decode("utf8"),
            'title': bytes(item.get('title')).decode("utf8"),
            'description': bytes(item.get('description')).decode("utf8"),
            'type': int(item.get('type')),
            'semester': bytes(item.get('semester')).decode("utf8"),
            'schedule': json.loads(bytes(item.get('schedule'))),
            'week_start': int(item.get('week_start')),
            'week_end': int(item.get('week_end')),
            'max_members': 0,
            'current_members': 0,
            'points': float(item.get('points')),
            'teacher': {
                'uid': bytes(item.get('teacher_uid')).decode("utf8"),
                'name': bytes(item.get('teacher_name')).decode("utf8"),
            }
        }
        ret_data.append(append_data)

    return_data = {
        "total": len(ret_data),
        "score_total": score_total,
        "data": ret_data
    }

    context.response.message.update(return_data)
    redis_pool.setRedis(f"cache_stuTable_{request.user_data.get('username')}_{semester}",
                        json.dumps(return_data),
                        10)

    return context


def studentCancelCourse(context: RequestContext) -> RequestContext:
    """
    学生退课

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    course_id = request.content.get("course_id")
    if course_id is None:
        raise exceptions.request_exceptions.BadRequestException("course_id不能为空")
    pool.getconn()
    req_sql = f"""select courses.course_id from courses, selections where selections.uid=%s and 
    selections.course_id=%s and courses.course_id=%s and courses.semester=%s;"""
    course_data = pool.getOne(req_sql, [request.user_data.get('username'), course_id, course_id, getCurrentSemester()])
    if not course_data:
        raise exceptions.course_exceptions.CourseCancelFailed("您未选择该课程或课程不属于当前学期")
    pool.delete(f"""delete from selections where `course_id`=%s and `uid`=%s;""",
                [course_id, request.user_data.get('username')])
    pool.dispose()
    loadCourse(course_id)
    return context


def selectCourse(username: str, course_id: str, semester: str or None):
    """
    执行用户选课操作
    :param username: 用户名
    :param course_id: 课程ID
    :param semester: 学期
    :return:
    """
    pool.getconn()
    req_sql = f"""
    select courses.schedule, courses.week_start, courses.week_end, courses.semester,
    (select count(id) from selections where selections.course_id=courses.course_id and selections.uid=%s) 
    as selected from courses where courses.course_id=%s {'and courses.semester=%s' if semester is not None else ''};"""
    course_data = pool.getOne(req_sql, [username, course_id] + ([] if semester is None else [semester]))
    user_data = pool.getOne(f"""select count(uid) from users where uid=%s and `role`=0""", [username])
    if not user_data:
        pool.dispose()
        raise exceptions.course_exceptions.CourseSelectFailed("用户不存在或角色非学生")
    if user_data['count(uid)'] <= 0:
        pool.dispose()
        raise exceptions.course_exceptions.CourseSelectFailed("用户不存在或角色非学生")
    if not course_data:
        pool.dispose()
        raise exceptions.course_exceptions.CourseSelectFailed("课程不存在或当前学期不可选")
    if course_data['selected'] > 0:
        pool.dispose()
        raise exceptions.course_exceptions.CourseSelectFailed("该课程已选择")

    course_semester = course_data['semester']
    course_data['schedule'] = json.loads(course_data['schedule'])
    # 判断学生课表是否有冲突
    ret = pool.getAll(f"""select courses.schedule as schedule, 
    courses.title as title, courses.course_id as course_id from selections, courses 
    where selections.uid=%s and courses.semester=%s and courses.course_id=selections.course_id and
    ((courses.week_start>=%s and courses.week_start<=%s)or(courses.week_end>=%s and courses.week_end<=%s));""",
                      [username, course_semester, course_data['week_start'], course_data['week_end'],
                       course_data['week_start'], course_data['week_end']])
    if not ret:
        ret = []

    for course in ret:
        schedule = json.loads(course['schedule'])
        for key, value in schedule.items():
            course_schedule = set(course_data['schedule'][key])
            selected_course_schedule = set(value)
            conflicted_schedule = [str(item) for item in course_schedule & selected_course_schedule]

            if len(conflicted_schedule) > 0:
                pool.dispose()
                raise exceptions.course_exceptions.CourseSelectFailed(
                    f"选择的课程与课程:[{course['title'].decode()}]在周{WEEKDAY_DICT[int(key)]}的第"
                    f"{','.join(conflicted_schedule)}节课有冲突")

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
    if req == -1:
        raise exceptions.course_exceptions.CourseSelectFailed("该课程已选满")
    elif req == -2:
        raise exceptions.init_exceptions.RedisNotLoaded()

    pool.insert(f"""insert into selections (uid, course_id, select_date) value (%s,%s,%s);""",
                [username, course_id, datetime.datetime.now()])
    pool.dispose()


def studentSelectCourse(context: RequestContext) -> RequestContext:
    """
    学生选课

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    course_id = request.content.get("course_id")
    semester = getCurrentSemester()
    username = request.user_data.get('username')
    if course_id is None:
        raise exceptions.request_exceptions.BadRequestException("course_id不能为空")
    selectCourse(username, course_id, semester)
    return context


def getStudentSelectionList(context: RequestContext) -> RequestContext:
    """
    获取学生某节课选课的列表
    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    course_id = request.content.get("course_id")
    username = request.user_data.get('username')
    role = request.user_data.get('role')
    logger.info(f"course_id: {course_id}, username: {username}, role: {role}")
    if course_id is None:
        raise exceptions.request_exceptions.BadRequestException("course_id不能为空")
    pool.getconn()
    course_data = pool.getOne(f"""select teacher from courses where course_id=%s""", [course_id])
    if not course_data:
        pool.dispose()
        raise exceptions.course_exceptions.CourseNotExist("您查找的课程不存在")
    if role != 2 and bytes(course_data['teacher']).decode() != username:
        pool.dispose()
        raise exceptions.auth_exceptions.PermissionException()
    student_list_raw = pool.getAll(f"""select users.name as name, users.uid as uid, selections.select_date as 
    selection_time from selections, users where
    selections.course_id=%s and users.uid=selections.uid order by selections.uid ASC;""", [course_id])
    if not student_list_raw:
        student_list_raw = []
    student_list = []
    for student in student_list_raw:
        student_list.append({
            'name': bytes(student['name']).decode(),
            'uid': bytes(student['uid']).decode(),
            'selection_time': student['selection_time'].timestamp()
        })

    context.response.message.update({
        'total': len(student_list_raw),
        'data': student_list
    })
    return context


def submitCourse(context: RequestContext) -> RequestContext:
    """
    提交课程信息，若课程ID不存在，则新建，若存在，则修改（修改时需判断权限）

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    action, course_id, \
    title, teacher, \
    semester, description, \
    max_members, points, \
    week_start, week_end, \
    course_type, schedule = request.content.get("action"), request.content.get("course_id"), \
                            request.content.get("title"), request.content.get("teacher"), \
                            request.content.get("semester"), \
                            request.content.get("description"), request.content.get("max_members"), \
                            request.content.get("points"), \
                            request.content.get("week_start"), request.content.get("week_end"), \
                            request.content.get("type"), request.content.get("schedule")
    # 参数需符合规则
    try:
        assert action in [0, 1], "Action需为0或1"
        assert re.match(COURSE_ID_PATTERN, course_id) is not None, "无效的course_id"
        assert re.match(COURSE_TITLE_PATTERN, title) is not None, "无效的课程标题"
        course_type = int(course_type)
        assert re.match(COURSE_TYPE_PATTERN, str(course_type)) is not None, "无效的课程类型"
        assert re.match(COURSE_DESCRIPTION_PATTERN, description) is not None, "无效的课程描述"
        assert re.match(SEMESTER_PATTERN, semester) is not None, "无效的学期"
        points = float(points)
        assert re.match(POINTS_PATTERN, str(points)) is not None, "无效的学分"
        assert points > 0, "学分需>0"
        week_start, week_end, max_members = int(week_start), int(week_end), int(max_members)
        assert week_end >= week_start > 0, "开始周需大于0且小于等于结束周"
        assert max_members > 0, "最大可报名人数应>0"
        assert re.match(USER_PATTERN, teacher) is not None, "用户UID无效"
        d = dict(json.loads(schedule))
        assert len(set(d.keys()) & {'1', '2', '3', '4', '5', '6', '7'}) == 7, "schedule无效"
    except AssertionError as e:
        logger.warn(f"[参数错误] {str(e)}")
        raise exceptions.request_exceptions.BadRequestException(str(e))
    except Exception as e:
        logger.warn(f"[参数错误] {str(e)}")
        raise exceptions.request_exceptions.BadRequestException("参数错误")

    pool.getconn()

    # 须拥有权限
    if action == 1:  # 新增
        if request.user_data.get('role') not in [1, 2]:
            logger.warn("无权限")
            raise exceptions.auth_exceptions.PermissionException()
        # 课程id不能重复
        base_course_data = pool.getOne(f"""select title from courses where course_id=%s;""", [course_id])
        if base_course_data:
            if base_course_data['title'] is not None:
                raise exceptions.course_exceptions.CourseExists(
                    f"COURSE_ID与已有课程 {bytes(base_course_data['title']).decode()} 重复，请重新设置")
        sql_req = f"""insert into courses (course_id, title, description, `type`, semester, schedule, week_start,week_end,
        points, teacher, max_members) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        sql_param = [course_id, title, description, course_type, semester, schedule, week_start, week_end, points,
                     teacher, max_members]
    else:
        if request.user_data.get('role') == 1:  # 教师权限
            if teacher != request.user_data.get('username'):
                logger.warn("教师不能转让课程")
                raise exceptions.auth_exceptions.PermissionException()
            course_data = pool.getOne(f"""select count(course_id) from courses where course_id=%s and teacher=%s""",
                                      [course_id, teacher])
            if course_data['count(course_id)'] <= 0:
                logger.warn("没有找到该课程或无权限修改")
                raise exceptions.auth_exceptions.PermissionException()
        elif request.user_data.get('role') == 2:  # 管理员权限
            pass
        else:
            logger.warn("学生无法修改")
            raise exceptions.auth_exceptions.PermissionException()
        sql_req = f"""update courses set title=%s, description=%s, `type`=%s, semester=%s,
         schedule=%s, week_start=%s,week_end=%s, points=%s, teacher=%s, max_members=%s where course_id=%s"""
        sql_param = [title, description, course_type, semester, schedule, week_start, week_end, points,
                     teacher, max_members, course_id]
    # 判断用户是否存在
    if teacher != request.user_data.get('username'):
        user_data = pool.getOne(f"""select count(uid) from users where uid=%s and (role=1 or role=2);""", [teacher])
        if user_data['count(uid)'] <= 0:
            logger.warn("没有找到符合要求的用户")
            raise exceptions.user_exceptions.UserNotFoundException()

    # 学期需已配置
    semester_data = pool.getOne(f"""select count(semester) from semester_limits where semester=%s""", [semester])
    if semester_data['count(semester)'] <= 0:
        logger.warn("学期不存在")
        raise exceptions.init_exceptions.SemesterNotExist()

    # 检测无误，执行更新语句
    pool.update(sql_req, sql_param)
    pool.dispose()

    if action == 0:
        loadCourse(course_id)

    return context


def adminAddCourse(context: RequestContext) -> RequestContext:
    """
    管理员批量导入课程名单

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    if request.user_data.get('role') != 2:
        raise exceptions.auth_exceptions.PermissionException()
    data = request.content.get('data')
    failed_list = []
    success = 0
    for item in data:
        course_id = item.get('course_id')
        uid = item.get('uid')
        try:
            assert re.match(USER_PATTERN, uid) is not None, "无效的UID"
            assert re.match(COURSE_ID_PATTERN, course_id) is not None, "无效的CourseId"
        except AssertionError as e:
            failed_list.append(f"""{uid}({course_id}):{str(e)}""")
        except Exception as e:
            failed_list.append(f"""{uid}({course_id}):解析失败""")

        try:
            selectCourse(uid, course_id, None)
            success += 1
        except exceptions.course_exceptions.CourseSelectFailed as e:
            failed_list.append(f"""{uid}({course_id}):{e.detail}""")
        except Exception as e:
            logger.warn(e)
            failed_list.append(f"""{uid}({course_id}):未知错误""")
    context.response.status_code = 0 if len(failed_list) == 0 else 200
    str_ = ';'.join(failed_list)
    if len(failed_list) != 0:
        context.response.message.update({
            'message': f"导入{success}条数据，其余数据导入失败: {str_}"
        })
    reloadAllCourses()
    return context


def adminCancelCourse(context: RequestContext) -> RequestContext:
    """
    管理员取消选课

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    if request.user_data.get('role') != 2:
        raise exceptions.auth_exceptions.PermissionException()
    course_id, uid = request.content.get('course_id'), request.content.get('uid')
    if course_id is None or uid is None:
        raise exceptions.request_exceptions.BadRequestException("course_id和uid不能为空")
    pool.getconn()
    req_sql = f"""select courses.course_id from courses, selections where selections.uid=%s and 
    selections.course_id=%s and courses.course_id=%s;"""
    course_data = pool.getOne(req_sql, [uid, course_id, course_id])
    if not course_data:
        pool.dispose()
        raise exceptions.course_exceptions.CourseCancelFailed("该学生未选择该课程")
    pool.delete(f"""delete from selections where `course_id`=%s and `uid`=%s;""",
                [course_id, uid])
    pool.dispose()
    loadCourse(course_id)
    return context


def deleteCourse(context: RequestContext) -> RequestContext:
    """
    管理员或教师删除课程

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    if request.user_data.get('role') != 2 and request.user_data.get('role') != 1:
        raise exceptions.auth_exceptions.PermissionException()
    course_id = request.content.get('course_id')
    if course_id is None:
        raise exceptions.request_exceptions.BadRequestException("course_id不能为空")
    uid = request.user_data.get('username')
    pool.getconn()
    req_sql = f"""select teacher from courses where course_id=%s;"""
    course_data = pool.getOne(req_sql, [course_id])
    if not course_data:
        pool.dispose()
        raise exceptions.course_exceptions.CourseNotExist("要删除的课程不存在")
    if request.user_data.get('role') == 1:  # 教师则需要判断该课程是否属于他
        if bytes(course_data['teacher']).decode() != uid:
            pool.dispose()
            raise exceptions.course_exceptions.CourseNotExist("您无法删除该课程")
    pool.delete(f"""delete from selections where `course_id`=%s;""",
                [course_id])
    pool.delete(f"""delete from courses where `course_id`=%s;""",
                [course_id])
    pool.dispose()
    return context
