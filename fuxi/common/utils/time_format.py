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
            return time_str
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp)))
    except Exception as e:
        logger.warning("time format failed: timestamp to str, %s".format(e))
    return time_str

def second_to_str(seconds):
    time_m, time_s = divmod(int(seconds), 60)
    time_h, time_m = divmod(time_m, 60)
    if time_h:
        return "%dh %02dm %02ds" % (time_h, time_m, time_s)
    elif time_m:
        return "%02dm %02ds" % (time_m, time_s)
    else:
        return "%02ds" % time_s
