#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/4/4
# @File    : sqlmap_api.py
# @Desc    : ""
import tempfile
import time
from flask import session, make_response, send_from_directory
from flask_restful import Resource, reqparse

from fuxi.common.libs.export_file import ExportData
from fuxi.common.utils.random_str import random_str
from fuxi.core.auth.token import auth
from fuxi.common.utils.time_format import timestamp_to_str
from fuxi.common.utils.logger import logger
from fuxi.core.data.response import Response
from fuxi.core.tasks.scanner.sqlmap_task import t_sqlmap_task
from fuxi.core.databases.orm.scanner.sqlmap_orm import DBSqlmapTask, DBSqlmapResult

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('target', type=str)
parser.add_argument('method', type=str)
parser.add_argument('body', type=str)
parser.add_argument('cookie', type=str)
parser.add_argument('headers', type=str)
parser.add_argument('level', type=int)
parser.add_argument('threads', type=int)
parser.add_argument('timeout', type=int)
parser.add_argument('db_banner', type=bool)

parser.add_argument('action', type=str)
parser.add_argument('keyword', type=str)
parser.add_argument('value', type=str)

class SqlmapTasksV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            task_items = DBSqlmapTask.get_list().sort("date", -1)
            for item in task_items:
                data.append({
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "target": item['target'],
                    "level": item['level'],
                    "method": item['method'],
                    "status": item['status'],
                    "result": DBSqlmapResult.get_count({"task_id": str(item['_id']), "result": 1}),
                    "op": item['op'],
                    "date": timestamp_to_str(item['date']),
                    "end_date": timestamp_to_str(item['end_date']),
                })
            return Response.success(data=data)
        except Exception as e:
            msg = "get sqlmap tasks failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

    @auth
    def post(self):
        """
        POST /api/v1/scanner/sqlmap/task
        :return:
        """
        try:
            op = session.get("user")
            args = parser.parse_args()
            name = args['name']
            method = args['method']
            level = args['level']
            threads = args['threads'] if args.get("threads") else 10
            timeout = args['timeout'] if args.get("timeout") else 300
            cookie = args['cookie']
            body = args['body']
            db_banner = args['db_banner']
            headers = args['headers']
            target = args['target'].split(',')
            tid = DBSqlmapTask.add(name, target, method, body, level, threads, timeout, cookie, headers, db_banner)
            celery_id = t_sqlmap_task.delay(tid)
            DBSqlmapTask.update_celery_id(tid, celery_id)
            logger.success("{} created the sqlmap task {}".format(op, tid))
            return Response.success(message="The task was created successfully")
        except Exception as e:
            msg = "Failed to create task: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)

class SqlmapTaskManageV1(Resource):
    @auth
    def get(self, tid):
        data = {}
        try:
            data = DBSqlmapTask.find_by_id(tid)
            if data:
                data['_id'] = str(data['_id'])
                data['result'] = DBSqlmapResult.get_count({"task_id": str(data['_id']), "result": 1})
                data['date'] = timestamp_to_str(data['date'])
                data['end_date'] = timestamp_to_str(data['end_date'])
                return Response.success(data=data)
            else:
                return Response.failed(message="can't find task", data={})
        except Exception as e:
            msg = "get sqlmap task detail failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

    @auth
    def delete(self, tid):
        """
        DELETE /api/v1/scanner/sqlmap/task/<tid>
        :param tid:
        :return:
        """
        try:
            op = session.get('user')
            DBSqlmapTask.delete_by_id(tid)
            logger.info("{} deleted the sqlmap task: {}".format(op, tid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete sqlmap task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)

    @auth
    def put(self, tid):
        """
        task rescan
        """
        try:
            args = parser.parse_args()
            action = args['action']
            if action == "rescan":
                # delete old data
                DBSqlmapResult.delete_by_tid(tid)
                # update task info
                DBSqlmapTask.update_by_id(tid, {
                    "date": int(time.time()),
                    "status": "waiting",
                    "result": 0,
                    "end_date": 0
                })
                # celery task
                celery_id = t_sqlmap_task.delay(tid)
                DBSqlmapTask.update_celery_id(tid, celery_id)
                logger.info("{} {} rescan sqlmap scan task".format(session.get('user'), tid))
            elif action == "stop":
                item = DBSqlmapTask.find_by_id(tid)
                if item and item.__contains__("celery_id"):
                    print(item.__contains__("celery_id"))
            return Response.success(message="successfully {}".format(action))
        except Exception as e:
            msg = "rescan the task failed: {}".format(e)
            logger.warning(tid + msg)
            return Response.failed(message=msg)


class SqlmapResultsV1(Resource):
    @auth
    def get(self):
        """
        """
        data = []
        try:
            args = parser.parse_args()
            keyword = args.get("keyword")
            value = args.get("value")
            if keyword and value:
                if keyword == "tid":
                    items = DBSqlmapResult.filter_by_tid(value).sort("date", -1)
                else:
                    items = []
            else:
                items = DBSqlmapResult.get_list().sort("date", -1)
            for item in items:
                task_item = DBSqlmapTask.find_by_id(item['task_id'])
                if not task_item:
                    continue
                # if item['result'] != 1:
                #     continue
                item['task_name'] = task_item['name']
                item['rid'] = str(item['_id'])
                item['date'] = timestamp_to_str(item['date'])
                del item['_id']
                data.append(item)
            return Response.success(data=data)
        except Exception as e:
            logger.warning("get sqlmap data failed: {}".format(e))
            return Response.failed(message=e, data=data)


class SqlmapResultManageV1(Resource):
    @auth
    def get(self, rid):
        """
        GET /api/v1/scanner/sqlmap/result/<rid>
        :return: all plugin [list]
        """
        data = {}
        try:
            data = DBSqlmapResult.find_by_id(rid)
            if data:
                task_item = DBSqlmapTask.find_by_id(data['task_id'])
                data['task_name'] = task_item['name'] if task_item else "-"
                data['rid'] = str(data['_id'])
                del data['_id']
                data['date'] = timestamp_to_str(data['date'])
                return Response.success(data=data)
            else:
                return Response.failed(message="can't find the result", data={})
        except Exception as e:
            msg = "get sqlmap result failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

    @auth
    def delete(self, rid):
        """
        DELETE /api/v1/scanner/sqlmap/result/<rid>
        :param rid:
        :return:
        """
        try:
            op = session.get('user')
            DBSqlmapResult.delete_by_id(rid)
            logger.info("{} deleted the sqlmap result: {}".format(op, rid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete sqlmap result failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class SqlmapTaskResultExportV1(Resource):
    @auth
    def get(self, tid):
        data = []
        title = []
        try:
            items = DBSqlmapResult.filter_by_tid(tid).sort("date", -1)
            for item in items:
                item['vid'] = str(item['_id'])
                task_item = DBSqlmapTask.find_by_id(item['task_id'])
                item['task_name'] = task_item['name'] if task_item else "-"
                item['date'] = timestamp_to_str(item['date'])
                del item['_id']
                data.append(item)
            if len(data) > 0:
                title = [str(i) for i in data[0]]
            export = ExportData(data)
            filename = "sqlmap_" + random_str(6) + ".csv"
            export.csv(title, tempfile.gettempdir() + "/" + filename)
            response = make_response(send_from_directory(tempfile.gettempdir(), filename, as_attachment=True))
            response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
            return response
        except Exception as e:
            msg = "export sqlmap scan result failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)
