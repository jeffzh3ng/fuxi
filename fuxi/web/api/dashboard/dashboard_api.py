#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/3/20
# @File    : dashboard_api.py
# @Desc    : ""
import time

from bson import ObjectId
from flask_restful import Resource, reqparse
from fuxi.web.flask_app import fuxi_celery

from fuxi.core.data.response import Response
from fuxi.core.auth.token import auth
from fuxi.core.databases.db_mongo import mongo
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

from fuxi.core.tasks.scanner.sqlmap_task import Sqlmap

parser = reqparse.RequestParser()
parser.add_argument('tid', type=str)
parser.add_argument('table', type=str)

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
                    "table": DBPocsuiteTask.table,
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "status": item['status'],
                    "op": item['op'],
                    "date": item['date'],
                    "celery_id": item['celery_id'] if item.__contains__("celery_id") else "0000",
                })
            for item in DBSqlmapTask.find({"status": "running"}):
                data.append({
                    "module": "sqlmap scanner",
                    "table": DBSqlmapTask.table,
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "status": item['status'],
                    "op": item['op'],
                    "date": item['date'],
                    "celery_id": item['celery_id'] if item.__contains__("celery_id") else "0000",
                })
            for item in DBPortScanTasks.find({"status": "running"}):
                data.append({
                    "module": "port scanner",
                    "table": DBPortScanTasks.table,
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "status": item['status'],
                    "op": item['op'],
                    "date": item['date'],
                    "celery_id": item['celery_id'] if item.__contains__("celery_id") else "0000",
                })
            for item in DBSubdomainTask.find({"status": "running"}):
                data.append({
                    "module": "subdomain scanner",
                    "table": DBSubdomainTask.table,
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "status": item['status'],
                    "op": item['op'],
                    "date": item['date'],
                    "celery_id": item['celery_id'] if item.__contains__("celery_id") else "0000",
                })
            for item in DBWhatwebTask.find({"status": "running"}):
                data.append({
                    "module": "whatweb scanner",
                    "table": DBWhatwebTask.table,
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "status": item['status'],
                    "op": item['op'],
                    "date": item['date'],
                    "celery_id": item['celery_id'] if item.__contains__("celery_id") else "0000",
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


class DashboardCeleryTaskStopV1(Resource):
    @auth
    def delete(self, cid):
        try:
            args = parser.parse_args()
            fuxi_celery.control.revoke(cid, terminate=True)
            if args.get("table") and args.get("tid"):
                mongo[args.get("table")].update_many({"_id": ObjectId(args.get("tid"))}, {"$set": {"status": "completed"}})
            return Response.success(message="The task has stopped")
        except Exception as e:
            msg = "Stop task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


def kill_sqlmap_task(task_id):
    scanner = Sqlmap()
    sqlmap_ids = DBSqlmapTask.find_by_id(task_id)['sqlmap_id']
    for sqlmap_id in sqlmap_ids:
        scanner.kill_task(sqlmap_id)
