# _*_ coding: utf-8 _*_
"""
Time:     2022/6/21 22:10
Author:   不做评论(vvbbnn00)
Version:  0.1
File:     router.py
Describe: 处理action所属的操作类型
"""

import exceptions.init_exceptions
import exceptions.request_exceptions
import middleware.auth
import middleware.request_parser
import middleware.response_parser
from annotations import ServiceLogger, RequestContext


def fun():
    pass


class Router:
    routes: dict = {}

    def __init__(self):
        """
        初始化，加载路由表
        """
        import service.status
        import service.user
        import service.course
        import service.semester
        _INIT_ROUTE_LIST = [service.status.RouteInfo(), service.user.RouteInfo(),
                            service.course.RouteInfo(), service.semester.RouteInfo()]
        for route in _INIT_ROUTE_LIST:
            for key, value in route.ROUTE_LIST.items():
                route_key = f'{route.ROUTE_NAME}.{key}'
                if self.routes.get(route_key):
                    raise exceptions.init_exceptions.DuplicatedRouteException(route_key)
                if not isinstance(value['fun'], fun.__class__):
                    raise exceptions.init_exceptions.WrongRouteType(str(type(value)))
                self.routes[route_key] = []
                # before中间件
                if value.get('disable_super_before') is not False:
                    self.routes[route_key].extend(list(route.BEFORE_MIDDLEWARE))
                if value.get('before'):
                    self.routes[route_key].extend(list(value.get('before')))

                self.routes[route_key].append(value.get('fun'))
                # after中间件
                if value.get('disable_super_after') is not False:
                    self.routes[route_key].extend(list(route.AFTER_MIDDLEWARE))
                if value.get('after'):
                    self.routes[route_key].extend(list(value.get('after')))
        # print(self.routes)

    def findRoute(self, route: str):
        """
        寻找路由，返回需要执行的函数列表
        :param route:
        :return:
        """
        pipeline = self.routes.get(route)
        # 若路径不存在，则抛出异常
        if not pipeline:
            raise exceptions.request_exceptions.RouteNotFoundException()
        return pipeline


_GLOBAL_ROUTER = Router()


class Pipeline:
    request_uuid: str
    request: middleware.request_parser.RequestData
    logger: ServiceLogger

    def __init__(self, req_uuid: str, request: middleware.request_parser.RequestData):
        self.request_uuid = req_uuid
        self.request = request
        self.logger = ServiceLogger(req_uuid, request.client_ip, request.client_port)

    def run(self):
        self.logger.info(f'Action: {self.request.action}')
        response = middleware.response_parser.ResponseData()
        response.message['req_uuid'] = self.request_uuid
        context = RequestContext(self.request, response, self.logger)
        pipeline = _GLOBAL_ROUTER.findRoute(self.request.action)
        # print(pipeline)
        for action in pipeline:
            context = action(context)
        return context.response
