# _*_ coding: utf-8 _*_
"""
Time:     2022/6/21 22:23
Author:   不做评论(vvbbnn00)
Version:  0.1
File:     global_logger.py
Describe: 通用日志
"""
import logging
import os
import time

# create logger
logger_name = "socket_serv"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

# create file handler
try:
    os.mkdir('./log')
except:
    pass
log_path = f"./log/{logger_name}_{time.strftime('%Y-%m-%d', time.localtime())}.log"
fh = logging.FileHandler(log_path)
fh.setLevel(logging.INFO)

# create stream handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
fmt = "%(asctime)-15s,%(msecs)03d [%(levelname)s] %(filename)s<%(process)d> %(funcName)s.%(lineno)d %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(fmt, datefmt)

# add handler and formatter to logger
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

if __name__ == '__main__':
    # print log info
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')
