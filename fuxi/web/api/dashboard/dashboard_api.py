#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/3/20
# @File    : dashboard_api.py
# @Desc    : ""
import time

from flask_restful import Resource

from fuxi.core.data.response import Response
from fuxi.core.auth.token import auth
from fuxi.core.databases.orm.scanner.pocsuite_orm import DBPocsuiteVul, DBPocsuiteTask
from fuxi.core.databases.orm.other.system_orm import DBHSystemInfo
from fuxi.core.databases.orm.exploit.jsonp_orm import DBExploitJsonpRes
from fuxi.core.databases.orm.exploit.xss_orm import DBXssResult
from fuxi.core.databases.orm.exploit.http_log_orm import DBHttpRequestLog
from fuxi.core.databases.orm.scanner.sqlmap_orm import DBSqlmapResult, DBSqlmapTask
from fuxi.core.databases.orm.discovery.whatweb_orm import DBWhatwebTask
from fuxi.core.databases.orm.discovery.subdomain_orm import DBSubdomainTask
from fuxi.core.databases.orm.discovery.port_orm import DBPortScanTasks
from fuxi.common.utils.logger import logger
from fuxi.common.utils.time_format import second_to_str, timestamp_to_str


class DashboardResCount(Resource):
    @auth
    def get(self):
        data = {"vuls": 0, "jsonp": 0, "xss": 0, "http": 0}
        try:
            data['vuls'] = DBPocsuiteVul.get_count({"status": "success"})
            data['jsonp'] = DBExploitJsonpRes.get_count()
            data['xss'] = DBXssResult.get_count()
            data['http'] = DBHttpRequestLog.get_count()
            data['sqlmap'] = DBSqlmapResult.get_count({"result": 1})
            return Response.success(data=data)
        except Exception as e:
            msg = "get dashboard result count failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)


class DashboardRunningTasksV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            for item in DBPocsuiteTask.find({"status": "running"}):
                data.append({
                    "module": "poc scanner",
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "status": item['status'],
                    "op": item['op'],
                    "date": item['date'],
                })
            for item in DBSqlmapTask.find({"status": "running"}):
                data.append({
                    "module": "sqlmap scanner",
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "status": item['status'],
                    "op": item['op'],
                    "date": item['date'],
                })
            for item in DBPortScanTasks.find({"status": "running"}):
                data.append({
                    "module": "port scanner",
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "status": item['status'],
                    "op": item['op'],
                    "date": item['date'],
                })
            for item in DBSubdomainTask.find({"status": "running"}):
                data.append({
                    "module": "subdomain scanner",
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "status": item['status'],
                    "op": item['op'],
                    "date": item['date'],
                })
            for item in DBWhatwebTask.find({"status": "running"}):
                data.append({
                    "module": "whatweb scanner",
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "status": item['status'],
                    "op": item['op'],
                    "date": item['date'],
                })
            for item in data:
                item['elapsed_time'] = second_to_str(time.time() - int(item['date']))
                item['date'] = timestamp_to_str(item['date'])
            return Response.success(data=data)
        except Exception as e:
            msg = "get dashboard running task list failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)


class DashboardSystemInfoV1(Resource):
    @auth
    def get(self):
        data = {
            "memory_percent": [],
            "cpu_percent": [],
        }
        try:
            count = 0
            for item in DBHSystemInfo.find({}).sort("date", -1):
                data["memory_percent"].append(item['memory_percent'])
                data["cpu_percent"].append(item['cpu_percent'])
                count += 1
                if count > 10:
                    break
            return Response.success(data=data)
        except Exception as e:
            msg = "get dashboard running task list failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)
