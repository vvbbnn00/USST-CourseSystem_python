# _*_ coding: utf-8 _*_
"""
Time:     2022/6/22 20:46
Author:   不做评论(vvbbnn00)
Version:  0.1
File:     login.py
Describe: 用户登录模块
"""
import datetime
import hashlib
import hmac
import time

import exceptions.auth_exceptions
import exceptions.request_exceptions
import utils.jwt_parser
from annotations import RequestContext
from config.security import HMAC_PASSWORD_KEY
from mysql import pool
from utils.redis_pool import redis_pool

USER_PATTERN = r"^[a-zA-Z0-9]{3,15}$"
PASSWD_PATTERN = r"^(?=.*\d)(?=.*[a-zA-Z]).{8,20}$"


def login(context: RequestContext) -> RequestContext:
    """
    获取服务器状态，默认返回请求IP、ok和当前时间戳

    :param context: 上下文
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    username, password, device_uuid = request.content.get('username'), request.content.get(
        'password'), request.content.get('device_uuid')

    # 登录请求限速
    request_limiter = redis_pool.getRedis(f"rate_limiter__{request.client_ip}")
    if request_limiter is not None:
        raise exceptions.request_exceptions.RequestTooFast
    redis_pool.setRedis(f"rate_limiter__{request.client_ip}", 1, 5)

    if username is None or password is None:
        raise exceptions.request_exceptions.BadRequestException("用户名或密码不能为空")
    if device_uuid is None:
        raise exceptions.request_exceptions.BadRequestException("设备信息为空")
    logger.info(f"用户尝试登录，username=" + username)
    password = hmac.new(HMAC_PASSWORD_KEY.encode(), password.encode(), digestmod=hashlib.sha256).hexdigest()
    pool.getconn()
    ret = pool.getOne(f"""select `name`, `role` from users where `uid`=%s and `passwd`=%s and `status`=0""",
                      [username, password])
    if not ret:
        pool.dispose()
        logger.info(f"登录失败")
        raise exceptions.auth_exceptions.PasswordErrorException()
    pool.update(f"""update users set last_login_time=%s, last_login_ip=%s where uid=%s""",
                [datetime.datetime.now(), request.client_ip, username])
    pool.dispose()
    name = bytes(ret['name']).decode()
    role = int(ret['role'])

    # 生成并发放JWT
    jwt = utils.jwt_parser.JWT({
        'username': username,
        'name': name,
        'role': role,
        'device_uuid': device_uuid
    })
    logger.info(f"登陆成功，发放JWT，过期时间：{int(time.time()) + 86400}")

    context.response.message.update({
        'username': username,
        'name': name,
        'role': role,
        'expire': int(time.time()) + 86400,
        'jwt': jwt.generateJWT(),
        'message': 'ok'
    })
    return context


def getUserInfo(context: RequestContext) -> RequestContext:
    """
    获取服务器状态，默认返回请求IP、ok和当前时间戳

    :param context: 上下文
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    pool.getconn()
    ret = pool.getOne(f"""select count(uid) from users where `uid`=%s and `status`=0""",
                      [request.user_data.get("username")])
    if not ret:
        pool.dispose()
        raise exceptions.auth_exceptions.JWTInvalidException()
    if ret['count(uid)'] <= 0:
        pool.dispose()
        raise exceptions.auth_exceptions.AccountLockedException()
    pool.dispose()
    if not ret:
        raise exceptions.auth_exceptions.AccountLockedException()
    logger.info(f'用户{request.user_data.get("username")}通过JWT登录成功')
    return context


def changePassword(context: RequestContext) -> RequestContext:
    """
    修改用户密码

    :param context:
    :return:
    """
    request, logger, response = context.request, context.logger, context.response
    username, password, new_password = request.user_data.get('username'), request.content.get(
        'ori_password'), request.content.get('new_password')
    if password is None or new_password is None:
        raise exceptions.request_exceptions.BadRequestException("密码不能为空")
    if new_password == password:
        raise exceptions.request_exceptions.BadRequestException("新密码不能和旧密码相同")
    logger.info(f'用户{request.user_data.get("username")}尝试修改密码')
    password = hmac.new(HMAC_PASSWORD_KEY.encode(), password.encode(), digestmod=hashlib.sha256).hexdigest()
    new_password = hmac.new(HMAC_PASSWORD_KEY.encode(), new_password.encode(), digestmod=hashlib.sha256).hexdigest()
    pool.getconn()
    ret = pool.getOne(f"""select passwd from users where uid=%s and passwd=%s;""", [username, password])
    if not ret:
        pool.dispose()
        raise exceptions.auth_exceptions.OriPasswordErrorException()
    pool.update(f"""update users set passwd=%s where `uid`=%s""", [new_password, username])
    pool.dispose()
    return context
