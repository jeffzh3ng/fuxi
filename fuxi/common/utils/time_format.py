#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/7/6
# @File    : time_format.py
# @Desc    : ""

import time
from fuxi.common.utils.logger import logger


def timestamp_to_str(timestamp):
    time_str = "-"
    try:
        if int(timestamp) == 0:
            return "-"
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp)))
    except Exception as e:
        logger.error("time format failed: timestamp to str, %s".format(e))
    return time_str
