# _*_ coding: utf-8 _*_
"""
Time:     2022/7/2 14:09
Author:   不做评论(vvbbnn00)
Version:  
File:     manage.py
Describe: 用户管理模块
"""
import hashlib
import hmac
import math
import re

import exceptions.auth_exceptions
import exceptions.init_exceptions
import exceptions.request_exceptions
import exceptions.user_exceptions
from annotations import RequestContext
from config.pattern import *
from config.security import HMAC_PASSWORD_KEY
from mysql import pool

QUERY_ORDER_BY = {
    0: "`users`.`uid` ASC",
    1: "`users`.`uid` DESC",
    2: "`users`.`role` ASC",
    3: "`users`.`role` DESC"
}


def getUserList(context: RequestContext) -> RequestContext:
    """
    获取用户列表

    :param context: 上下文
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    page, page_size, search_kw, sort_method = \
        request.content.get("page"), \
        request.content.get("size"), \
        request.content.get("kw"), \
        request.content.get("sort_method")
    if page is None or page_size is None or sort_method is None:
        raise exceptions.request_exceptions.BadRequestException("缺少参数")
    try:
        page = int(page)
        page_size = int(page_size)
        sort_method = int(sort_method)
        assert page > 0, 'page需为大于0的整数'
        assert 1 <= page_size <= 20, 'pageSize需在1~20之间'
        assert sort_method in [0, 1, 2, 3], 'sortMethod不符合规范'
    except AssertionError as e:
        raise exceptions.request_exceptions.BadRequestException(str(e))
    except:
        raise exceptions.request_exceptions.BadRequestException("参数类型错误")

    if request.user_data.get('role') != 2:
        raise exceptions.auth_exceptions.PermissionException()

    logger.info(f'查询用户列表 page={page}, page_size={page_size},'
                f' search_kw={search_kw}, sort_method={sort_method}, user={request.user_data.get("username")}')

    where_condition = []
    where_param = []
    if search_kw:
        search_kw = f"%{search_kw}%"
        where_condition.append("(uid like %s)or(name like %s)")
        where_param.extend([search_kw, search_kw])
    pool.getconn()
    total = pool.getOne(f"SELECT count(uid) from users "
                        f"{'where (' + ')and('.join(where_condition) + ')' if len(where_condition) > 0 else ''}",
                        where_param)
    if not total:
        total = 0
    else:
        total = total['count(uid)']
    if math.ceil(total / page_size) < page:
        page = math.ceil(total / page_size)
    if page == 0:
        page = 1

    req_sql = f"SELECT `uid`, `name`, `role`, `last_login_ip`, `last_login_time`, `status`" \
              f" from users " \
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
            'uid': bytes(item.get('uid')).decode("utf8"),
            'name': bytes(item.get('name')).decode("utf8"),
            'last_login_ip': bytes(
                b'(null)' if item.get('last_login_ip') is None else item.get('last_login_ip')).decode(
                "utf8"),
            'role': int(item.get('role')),
            'status': int(item.get('status')),
            'last_login_time': int(
                item.get('last_login_time').timestamp() if item.get('last_login_time') is not None else 0),
        }
        ret_data.append(append_data)
    context.response.message.update({
        "total": total,
        "page": page,
        "current_total": len(ret),
        "max_page": math.ceil(total / page_size),
        "page_size": page_size,
        "data": ret_data
    })
    return context


def submitUser(context: RequestContext) -> RequestContext:
    """
    提交用户信息，若用户不存在，则新建，若存在，则修改

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    if request.user_data.get('role') not in [2]:
        logger.warn("无权限")
        raise exceptions.auth_exceptions.PermissionException()
    action, uid, passwd, name, role, status = \
        request.content.get("action"), request.content.get("uid"), \
        request.content.get("passwd"), request.content.get("name"), \
        request.content.get("role"), request.content.get("status")
    # 参数需符合规则
    try:
        assert action in [0, 1], "Action需为0或1"
        assert re.match(USER_PATTERN, uid) is not None, "无效的uid"
        assert re.match(USER_NAME_PATTERN, name) is not None, "无效的用户姓名"

        assert role in [0, 1, 2], "无效的用户角色"
        assert status in [0, 1], "无效的用户状态"
    except AssertionError as e:
        logger.warn(f"[参数错误] {str(e)}")
        raise exceptions.request_exceptions.BadRequestException(str(e))
    except Exception as e:
        logger.warn(f"[参数错误] {str(e)}")
        raise exceptions.request_exceptions.BadRequestException("参数错误")

    pool.getconn()

    # 须拥有权限
    if action == 1:  # 新增
        if len(passwd) != 64:
            raise exceptions.request_exceptions.BadRequestException("无效的密码")
        password = hmac.new(HMAC_PASSWORD_KEY.encode(), passwd.encode(), digestmod=hashlib.sha256).hexdigest()
        # uid不能重复
        base_user_dta = pool.getOne(f"""select uid from users where uid=%s;""", [uid])
        if base_user_dta:
            if base_user_dta['uid'] is not None:
                pool.dispose()
                raise exceptions.user_exceptions.UserExistsException()
        sql_req = f"""insert into users (uid, passwd, `name`, `role`, `status`) values (%s,%s,%s,%s,%s)"""
        sql_param = [uid, password, name, role, status]
    else:
        if len(passwd) == 64:
            password = hmac.new(HMAC_PASSWORD_KEY.encode(), passwd.encode(), digestmod=hashlib.sha256).hexdigest()
        else:
            password = None
        sql_req = f"""update users set `name`=%s, `role`=%s, `status`=%s{',`passwd`=%s' if password else ''} 
        where uid=%s"""
        sql_param = [name, role, status]
        if password:
            sql_param.append(password)
        sql_param.append(uid)

    # 检测无误，执行更新语句
    pool.update(sql_req, sql_param)
    pool.dispose()

    return context
