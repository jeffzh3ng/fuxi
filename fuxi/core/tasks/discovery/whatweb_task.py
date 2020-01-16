#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/01/14
# @File    : whatweb_task.py 
# @Desc    : ""

import time
from fuxi.web.flask_app import fuxi_celery
from fuxi.core.databases.orm.discovery.whatweb_orm import DBWhatwebTask, DBWebFingerPrint
from fuxi.core.databases.orm.configuration.config import DBFuxiConfiguration
from fuxi.common.utils.logger import logger
from fuxi.common.utils.whatweb import Whatweb


class WhatwebScanner:
    def __init__(self):
        self.result = []
        self.whatweb_exe = ""

    def run(self, target, level, threads, option, header, cookie, plugin):
        if not self.get_whatweb_exe():
            logger.warning("whatweb cannot found, please install and configure")
        scanner = Whatweb(self.whatweb_exe)
        if header:
            scanner.set_header(header)
        if cookie:
            scanner.set_cookie(cookie)
        if plugin:
            # developing
            pass
        try:
            self.result = scanner.whatweb(target=target, level=level, threads=threads, option=option)
        except Exception as e:
            logger.warning("whatweb scanner: {}".format(e))
        return self.result

    def get_whatweb_exe(self):
        self.whatweb_exe = DBFuxiConfiguration.get_config("whatweb_exe")
        if not self.whatweb_exe:
            return False
        return True


@fuxi_celery.task()
def t_whatweb_task(task_id):
    try:
        _item = DBWhatwebTask.find_by_id(task_id)
        target = _item['target']
        level = _item['level']
        threads = _item['threads']
        option = _item['option']
        header = _item['header']
        cookie = _item['cookie']
        plugin = _item['plugin']
        DBWhatwebTask.update_by_id(task_id, {
            "status": "running"
        })
        try:
            scanner = WhatwebScanner()
            scanner.run(target=target, level=level, threads=threads, option=option,
                        header=header, cookie=cookie, plugin=plugin)
            try:
                data = []
                for i in scanner.result:
                    i['task_id'] = task_id
                    data.append(i)
                DBWebFingerPrint.add_multiple(data)
            except Exception as e:
                logger.warning("save website fingerprint failed: {}".format(e))
        except Exception as e:
            logger.warning("start whatweb failed: {}".format(e))
        DBWhatwebTask.update_by_id(task_id, {
            "status": "completed",
            "end_date": int(time.time())
        })
        logger.success("whatweb: {} the task completed".format(task_id))
    except Exception as e:
        logger.warning("{} start whatweb task failed: {}".format(task_id, e))
