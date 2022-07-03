# _*_ coding: utf-8 _*_
"""
Time:     2022/7/2 16:35
Author:   不做评论(vvbbnn00)
Version:  0.1
File:     semester_data.py
Describe: 学期信息模块
"""
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

QUERY_ORDER_BY = {
    0: "semester DESC",
    1: "semester ASC"
}


def getCurrentSemester():
    """
    获取当前学期
    :return:
    """
    pool.getconn()
    ret = pool.getOne("select `value` from settings where `key`='current_semester';")
    if ret['value'] is None:
        pool.dispose()
        raise exceptions.course_exceptions.CourseSettingError("未设置当前学期")
    return ret['value'].decode()


def getSchoolName():
    """
    获取当前学校名称
    :return:
    """
    pool.getconn()
    ret = pool.getOne("select `value` from settings where `key`='school_name';")
    if ret['value'] is None:
        pool.dispose()
        raise exceptions.course_exceptions.CourseSettingError("未设置学校名称")
    return ret['value'].decode()


def getLimitList(context: RequestContext) -> RequestContext:
    """
    获取学期学分限制列表

    :param context: 上下文
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    page, page_size, search_kw, sort_method = \
        request.content.get("page"), \
        request.content.get("size"), \
        request.content.get("kw"), \
        request.content.get("sort_method")
    if request.user_data.get('role') != 2:
        raise exceptions.auth_exceptions.PermissionException()
    if page is None or page_size is None or sort_method is None:
        raise exceptions.request_exceptions.BadRequestException("缺少参数")
    try:
        page = int(page)
        page_size = int(page_size)
        sort_method = int(sort_method)
        assert page > 0, 'page需为大于0的整数'
        assert 1 <= page_size <= 20, 'pageSize需在1~20之间'
        assert sort_method in [0, 1], 'sortMethod不符合规范'
    except AssertionError as e:
        raise exceptions.request_exceptions.BadRequestException(str(e))
    except:
        raise exceptions.request_exceptions.BadRequestException("参数类型错误")

    logger.info(f'查询学期限制数据 page={page}, page_size={page_size},'
                f' search_kw={search_kw}, sort_method={sort_method}, user={request.user_data.get("username")}')

    where_condition = []
    where_param = []
    if search_kw:
        search_kw = f"%{search_kw}%"
        where_condition.append("(semester like %s)")
        where_param.extend([search_kw])
    pool.getconn()
    total = pool.getOne(f"SELECT count(semester) from semester_limits "
                        f"{'where (' + ')and('.join(where_condition) + ')' if len(where_condition) > 0 else ''}",
                        where_param)
    total = total['count(semester)']
    if math.ceil(total / page_size) < page:
        page = math.ceil(total / page_size)
    if page == 0:
        page = 1
    req_sql = f"SELECT semester, max_score from semester_limits " \
              f"{'where (' + ')and('.join(where_condition) + ')' if len(where_condition) > 0 else ''}" \
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
            'semester': bytes(item.get('semester')).decode("utf8"),
            'max_points': float(item.get('max_score'))
        }
        ret_data.append(append_data)
    context.response.message.update({
        "total": total,
        "page": page,
        "current_total": len(ret),
        "current_semester": getCurrentSemester(),
        "school": getSchoolName(),
        "max_page": math.ceil(total / page_size),
        "page_size": page_size,
        "data": ret_data
    })
    return context


def submitSemester(context: RequestContext) -> RequestContext:
    """
    提交学期信息，若学期不存在，则新建，若存在，则修改

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    if request.user_data.get('role') not in [2]:
        logger.warn("无权限")
        raise exceptions.auth_exceptions.PermissionException()
    action, semester, max_points = \
        request.content.get("action"), \
        request.content.get("semester"), \
        request.content.get("max_points")
    # 参数需符合规则
    try:
        assert action in [0, 1], "Action需为0或1"
        max_points = float(max_points)
        assert re.match(SEMESTER_PATTERN, semester) is not None, "无效的学期"
        assert max_points > 0 and re.match(POINTS_PATTERN, str(max_points)) is not None, "无效的最大学分"
    except AssertionError as e:
        logger.warn(f"[参数错误] {str(e)}")
        raise exceptions.request_exceptions.BadRequestException(str(e))
    except Exception as e:
        logger.warn(f"[参数错误] {str(e)}")
        raise exceptions.request_exceptions.BadRequestException("参数错误")

    pool.getconn()

    # 须拥有权限
    if action == 1:  # 新增
        # 学期不能重复
        semester_data = pool.getOne(f"""select count(semester) from semester_limits where semester=%s;""", [semester])
        if semester_data['count(semester)'] > 0:
            pool.dispose()
            raise exceptions.request_exceptions.BadRequestException(f"学期重复")
        sql_req = f"""insert into semester_limits (semester, max_score) values (%s,%s)"""
        sql_param = [semester, max_points]
    else:
        sql_req = f"""update semester_limits set max_score=%s where semester=%s"""
        sql_param = [max_points, semester]
    # 检测无误，执行更新语句
    pool.update(sql_req, sql_param)
    pool.dispose()

    return context


def deleteSemester(context: RequestContext) -> RequestContext:
    """
    管理员删除学期

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    if request.user_data.get('role') != 2:
        raise exceptions.auth_exceptions.PermissionException()
    semester = request.content.get('semester')
    if semester is None:
        raise exceptions.request_exceptions.BadRequestException("semester不能为空")
    if semester == getCurrentSemester():
        raise exceptions.request_exceptions.BadRequestException("不能删除当前所在的学期")
    pool.getconn()
    req_sql = f"""select semester from semester_limits where semester=%s;"""
    course_data = pool.getOne(req_sql, [semester])
    if not course_data:
        pool.dispose()
        raise exceptions.course_exceptions.CourseNotExist("要删除的学期不存在")
    pool.delete(f"""delete from semester_limits where `semester`=%s;""",
                [semester])
    pool.dispose()
    return context


def changeSemester(context: RequestContext) -> RequestContext:
    """
    管理员修改当前学期

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    if request.user_data.get('role') not in [2]:
        raise exceptions.auth_exceptions.PermissionException()
    semester = request.content.get('semester')
    if semester is None:
        raise exceptions.request_exceptions.BadRequestException("学期不能为空")
    pool.getconn()
    ret = pool.getOne("select semester from semester_limits where `semester`=%s;", semester)
    if not ret:
        pool.dispose()
        raise exceptions.request_exceptions.BadRequestException("学期不存在")
    pool.update(f"update settings set `value`=%s where `key`=%s", [semester, 'current_semester'])
    pool.dispose()
    return context


def changeSchool(context: RequestContext) -> RequestContext:
    """
    管理员修改当前学校

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    if request.user_data.get('role') not in [2]:
        raise exceptions.auth_exceptions.PermissionException()
    school_name = request.content.get('school_name')
    if school_name is None:
        raise exceptions.request_exceptions.BadRequestException("校名不能为空")
    if re.match(SCHOOL_NAME_PATTERN, school_name) is None:
        raise exceptions.request_exceptions.BadRequestException("无效的校名")
    pool.getconn()
    pool.update(f"update settings set `value`=%s where `key`=%s", [school_name, 'school_name'])
    pool.dispose()
    return context
