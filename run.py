# _*_ coding: utf-8 _*_
"""
Time:     2022/6/21 14:46
Author:   不做评论(vvbbnn00)
Version:  1.0
File:     run.py
Describe: socket服务器主程序
"""

import socketserver
import threading
import traceback
import uuid

import exceptions.request_exceptions
import middleware.request_parser
import middleware.response_parser
import service.router
from utils.global_logger import logger

HOST = '0.0.0.0'
PORT = 2333
ADDRESS = (HOST, PORT)


class RequestTCPHandler(socketserver.BaseRequestHandler):
    data: str
    req_uuid: str

    def handle(self):
        self.req_uuid = str(uuid.uuid4())
        logger.info(f'[{self.client_address[0]}:{self.client_address[1]},{self.req_uuid}] Received Request.')
        try:
            self.data = ''
            try:
                # 接收物理层传入数据
                data = self.request.recv(1024000)
                print(data)
                self.data = data.decode()
                if len(self.data) > 1024000:
                    raise exceptions.request_exceptions.RequestTooLargeException()
                if len(self.data) == 0:
                    raise exceptions.request_exceptions.BadRequestException()
                # 解析传入数据，判断是否符合协议
                request = middleware.request_parser.parseRequestData(self.data)
                request.client_ip, request.client_port = self.client_address
                # 符合协议的数据走router，进行进一步的操作
                resp = service.router.Pipeline(self.req_uuid, request).run()
                # 返回处理后的结果
                self.request.sendall(str(resp).encode())
            except Exception as e:
                # 不符合协议或无效的数据丢弃
                logger.warning(
                    f'[{self.client_address[0]}:{self.client_address[1]},{self.req_uuid}] {traceback.format_exc()}')
                resp = middleware.response_parser.dealExceptionData(e)
                self.request.sendall(resp)
        except Exception as e:
            logger.info(f'[{self.client_address[0]}:{self.client_address[1]},{self.req_uuid}] Disconnected({str(e)}).')
        finally:
            self.request.close()

    def setup(self):
        pass

    def finish(self):
        pass


if __name__ == "__main__":
    logger.info(f'El Psy Congroo.')
    logger.info(f'服务器开始在IP为{HOST},端口为{PORT}监听')
    server = socketserver.ThreadingTCPServer(ADDRESS, RequestTCPHandler, bind_and_activate=False)
    server.allow_reuse_address = True
    server.server_bind()
    server.server_activate()
    server.serve_forever()
