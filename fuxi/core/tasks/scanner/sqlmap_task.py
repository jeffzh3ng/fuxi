#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/4/4
# @File    : sqlmap_task.py
# @Desc    : ""


import random
import time
import requests
import concurrent.futures
from fuxi.web.flask_app import fuxi_celery
from fuxi.core.databases.orm.configuration.config import DBFuxiConfiguration
from fuxi.core.databases.orm.scanner.sqlmap_orm import DBSqlmapTask, DBSqlmapResult
from fuxi.common.utils.logger import logger


class Sqlmap(object):
    def __init__(self):
        self.task_data = {}
        self.sqlmap_api = ""
        self.sqlmap_tid = ""
        if not self.set_sqlmap_api():
            raise Exception("can not found sqlmap server")

    def run(self, target, is_async=False, timeout=300):
        # Request ERROR: 'Connection aborted.', BrokenPipeError(32, 'Broken pipe')
        time.sleep(random.randint(1, 3))
        sqlmap_tid = self.init()
        if not sqlmap_tid:
            raise Exception("can not create sqlmap task")

        self.task_data['url'] = target
        try:
            response = self._do_request("POST", "/scan/{}/start".format(sqlmap_tid), self.task_data)
            if not response['success']:
                return None
            if is_async:
                return self.sqlmap_tid
            else:
                if sqlmap_tid:
                    count = 0
                    freq = random.randint(1, 3)
                    while count < timeout / freq:
                        count += 1
                        time.sleep(freq)
                        task_status = self.get_status(sqlmap_tid)
                        if task_status == "terminated":
                            return self.get_result(sqlmap_tid)
                    return self.get_result(sqlmap_tid)
                else:
                    return None
        except Exception as e:
            raise Exception(e)

    def init(self):
        try:
            response = self._do_request("GET", "/task/new")
            if response["taskid"] != "":
                return response["taskid"]
            else:
                logger.warning("can not get sqlmap task id")
                return ""
        except Exception as e:
            logger.warning("get sqlmap task id failed: {}".format(e))
            return ""

    def get_result(self, sqlmap_tid):
        data = {
            "sqlmap_tid": sqlmap_tid, "result": 0, "dbms": "", "dbms_version": "", "os": "",
            "payload": "", "parameter": "", "place": ""
        }
        response = self._do_request("GET", "/scan/{}/data".format(sqlmap_tid))
        for i in response['data']:
            if i.__contains__("status") and i['status'] == 1:
                data['result'] = 1
            if i.__contains__("type") and i['type'] == 1:
                if i.__contains__("value"):
                    for value in i['value']:
                        data['place'] = value['place'] if value['place'] else ""
                        data['dbms'] = value['dbms'] if value['dbms'] else ""
                        data['dbms_version'] = value['dbms_version'][0] if value['dbms_version'] else ""
                        data['os'] = value['os'] if value['os'] else ""
                        data['parameter'] = value['parameter']
                        for d in value['data']:
                            if value['data'][d].__contains__("payload"):
                                data['payload'] = value['data'][d]['payload']
                        break
        return data

    def get_status(self, sqlmap_tid):
        response = self._do_request("GET", "/scan/{}/status".format(sqlmap_tid))
        return response['status']

    def set_sqlmap_api(self):
        self.sqlmap_api = DBFuxiConfiguration.get_config("sqlmap_api")
        if not self.sqlmap_api:
            return False
        return True

    def set_cookie(self, cookie):
        if len(cookie):
            self.task_data['cookie'] = cookie

    def set_headers(self, headers):
        if len(headers):
            self.task_data['headers'] = headers

    def set_banner(self):
        self.task_data['getBanner'] = True

    def set_body_data(self, body):
        self.task_data['data'] = body

    def set_level(self, level):
        self.task_data['level'] = level

    def _do_request(self, method, url, body=None):
        if method.lower() == "get":
            r = requests.get(self.sqlmap_api + url)
            return r.json()
        elif method.lower() == "post":
            r = requests.post(self.sqlmap_api + url, json=body)
            return r.json()
        return None

def _save_result(data):
    try:
        DBSqlmapResult.add_multiple(data)
    except Exception as e:
        logger.warning("save sqlmap result failed: {}".format(e))


@fuxi_celery.task()
def t_sqlmap_task(task_id):
    """
    :param task_id: get the task information
    :return:
    """
    try:
        task_item = DBSqlmapTask.find_by_id(task_id)
        if not task_item:
            return
        DBSqlmapTask.update_by_id(task_id, {
            "status": "running"
        })
        target_list = task_item['target']
        method = task_item['method']
        threads = task_item['threads']
        timeout = task_item['timeout']

        scanner = Sqlmap()
        scanner.set_level(task_item['level'])
        if method.lower() == "post":
            scanner.set_body_data(task_item['body'])
        if task_item['cookie']:
            scanner.set_cookie(task_item['cookie'])
        if task_item['headers']:
            scanner.set_headers(task_item['headers'])
        if task_item['db_banner']:
            scanner.set_banner()

        try:
            result = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=int(threads)) as threat_pool:
                future_dict = {
                    threat_pool.submit(
                        scanner.run, target, False, timeout
                    ): target for target in target_list
                }
                for future in concurrent.futures.as_completed(future_dict):
                    target = future_dict[future]
                    res = future.result()
                    try:
                        result.append({
                            "task_id": task_id, "target": target, "sqlmap_tid": res['sqlmap_tid'],
                            "method": method,
                            "body": task_item.get("body"),
                            "result": res['result'],
                            "dbms": res['dbms'],
                            "dbms_version": res['dbms_version'],
                            "os": res['os'],
                            "payload": res['payload'],
                            "parameter": res['parameter'],
                            "place": res['place'],
                        })
                    except Exception as e:
                        logger.warning("sqlmap scanner task: {}".format(e))
            _save_result(result)
        except Exception as e:
            logger.warning("sqlmap scanner error: {}".format(e))

        DBSqlmapTask.update_by_id(task_id, {
            "status": "completed",
            "end_date": int(time.time())
        })
        logger.success("{} sqlmap scan task completed".format(task_id))
    except Exception as e:
        logger.warning("{} sqlmap scan failed: {}".format(task_id, e))


if __name__ == '__main__':
    t_sqlmap_task("5e88b01ced5a7b44adfc872f")
