#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : logger.py
# @Desc    : ""


import logging
import time
import sys
import os
import inspect
from instance.config import LOGGER_PATH


def _format_message(level, message):
    """
    对日志进行格式化
    :param level: 日志等级
    :param message: 日志内容
    :return: 返回格式化后日志
    """

    frame = inspect.currentframe().f_back.f_back
    frame_info = inspect.getframeinfo(frame)
    line_no = frame_info.lineno
    file_name = frame_info.filename
    module_name = os.path.splitext(os.path.split(file_name)[1])[0]
    message = "{time} {level} - {module}.py[{line}] {message}".format(
        time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        module=module_name, line=line_no, level=level, message=message,
    )
    return message


class Logger:
    def __init__(self):
        try:
            # 从上下文中获取配置文件中的日志路径配置
            self._log_file = LOGGER_PATH + '/' + "fuxi_{}.log".format(
                time.strftime("%Y_%m_%d", time.localtime())
            )
            if not os.path.exists(LOGGER_PATH):
                os.makedirs(LOGGER_PATH)
            self._logger = logging.getLogger("fuxi")
            self._logger.setLevel(logging.DEBUG)
            # 日志保存到日志目录
            file_handler = logging.FileHandler(self._log_file)
            self._logger.addHandler(hdlr=file_handler)
            # 日志打印在终端 (标准输出)
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(hdlr=stream_handler)
        except Exception as e:
            raise e

    def info(self, message):
        self._logger.info(_format_message("INFO", message))

    def success(self, message):
        self._logger.info(_format_message("SUCCESS", message))

    def warning(self, message):
        self._logger.warning(_format_message("WARNING", message))

    def error(self, message):
        self._logger.error(_format_message("ERROR", message))

    def debug(self, message):
        self._logger.info(_format_message("DEBUG", message))

    def access(self, message):
        """
        埋个口子 后期可能要做流量统计
        :param message:
        :return:
        """
        self._logger.info("{time} ACCESS - {message}".format(
            time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            message=message
        ))


logger = Logger()
