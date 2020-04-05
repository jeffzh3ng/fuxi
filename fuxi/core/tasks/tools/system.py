#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/4/5
# @File    : system.py
# @Desc    : ""

import psutil
from fuxi.common.utils.logger import logger
from fuxi.core.databases.orm.other.system_orm import DBHSystemInfo
from fuxi.web.flask_app import fuxi_celery

def system_info():
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    return int(memory.percent), int(cpu_percent)

@fuxi_celery.task()
def t_schedule_update_system_info():
    data = {
        "memory_percent": 0,
        "cpu_percent": 0,
    }
    try:
        memory_percent, cpu_percent = system_info()
        data['memory_percent'] = memory_percent
        data['cpu_percent'] = cpu_percent
    except Exception as e:
        logger.warning("get system info failed: {}".format(e))
    try:
        DBHSystemInfo.add(data)
    except Exception as e:
        logger.warning("update system info failed: {}".format(e))
