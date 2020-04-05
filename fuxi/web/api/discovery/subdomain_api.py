#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/3/21
# @File    : subdomain_api.py
# @Desc    : ""
import tempfile
import time
from flask_restful import Resource, reqparse
from flask import session, send_from_directory, make_response

from fuxi.common.utils.random_str import random_str
from fuxi.common.libs.export_file import ExportData
from fuxi.common.utils.logger import logger
from fuxi.common.utils.time_format import timestamp_to_str
from fuxi.core.auth.token import auth
from fuxi.core.data.response import Response
from fuxi.core.tasks.discovery.subdomain_task import t_subdomain_task
from fuxi.core.databases.orm.discovery.subdomain_orm import DBSubdomainTask, DBSubdomainResult

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('target', type=str)
parser.add_argument('threads', type=int)
parser.add_argument('brute', type=bool)
parser.add_argument('info', type=bool)
parser.add_argument('keyword', type=str)
parser.add_argument('value', type=str)
parser.add_argument('action', type=str)


class SubdomainTasksV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            items = DBSubdomainTask.get_list().sort("date", -1)
            for item in items:
                count = DBSubdomainResult.get_count_by_tid(item['_id'])
                data.append({
                    "tid": str(item['_id']),
                    'name': item['name'],
                    'target': item['target'],
                    'status': item['status'],
                    'threads': item['threads'],
                    'info': item['info'],
                    'brute': item['brute'],
                    'count': count,
                    'date': timestamp_to_str(item['date']),
                    'end_date': timestamp_to_str(item['end_date']),
                    'op': item['op']
                })
            return Response.success(data=data)
        except Exception as e:
            msg = "get subdomain scan task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)

    @auth
    def post(self):
        try:
            args = parser.parse_args()
            name = args['name'].strip()
            target = args['target'].strip().split("\n")
            brute = args['brute']
            info = args['info']
            threads = args['threads']
            tid = DBSubdomainTask.add(name, target, brute, info, threads)
            cid = t_subdomain_task.delay(tid)
            DBSubdomainTask.update_celery_id(tid, cid)
            logger.success("{} created the subdomain scan task: {}".format(session.get('user'), tid))
            return Response.success(message="The task was created successfully")
        except Exception as e:
            msg = "subdomain task creation failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class SubdomainTaskManageV1(Resource):
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
                DBSubdomainResult.delete_by_tid(tid)
                # update task info
                DBSubdomainTask.update_by_id(tid, {
                    "date": int(time.time()),
                    "status": "waiting",
                    "end_date": 0
                })
                # celery task
                cid = t_subdomain_task.delay(tid)
                DBSubdomainTask.update_celery_id(tid, cid)
                logger.info("{} {} subdomain scan task rescan".format(session.get('user'), tid))
            return Response.success(message="successfully {}".format(action))
        except Exception as e:
            msg = "rescan subdomain scan task failed: {}".format(e)
            logger.warning(tid + msg)
            return Response.failed(message=msg)

    @auth
    def delete(self, tid):
        """
        delete task by task_id
        DELETE /api/v1/discovery/subdomain/task/<tid>
        :param tid:
        :return:
        """
        try:
            op = session.get('user')
            DBSubdomainTask.delete_by_id(tid)
            DBSubdomainResult.delete_by_tid(tid)
            logger.info("{} deleted the subdomain scan task: {}".format(op, tid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete subdomain scan task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class SubdomainResultV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            args = parser.parse_args()
            keyword = args['keyword']
            value = args['value']
            if keyword and value:
                if keyword == "tid":
                    items = DBSubdomainResult.get_list_by_tid(value)
                else:
                    items = DBSubdomainResult.get_list()
            else:
                items = DBSubdomainResult.get_list()
            for item in items:
                task_info = DBSubdomainTask.find_by_id(item['task_id'])
                if not task_info:
                    continue
                data.append({
                    "rid": str(item['_id']),
                    "tid": str(item['task_id']),
                    'name': task_info['name'],
                    'domain': item['domain'],
                    'subdomain': item['subdomain'],
                    'title': item['title'] if item['title'] else "-",
                    'response': item['response'],
                    'ip': item['ip'],
                    'date': timestamp_to_str(item['date']),
                })
            return Response.success(data=data)
        except Exception as e:
            msg = "get subdomain scan result failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)


class SubdomainResultManageV1(Resource):
    @auth
    def delete(self, rid):
        """
        delete task by task_id
        DELETE /api/v1/discovery/subdomain/res/<rid>
        :param rid:
        :return:
        """
        try:
            op = session.get('user')
            DBSubdomainResult.delete_by_id(rid)
            logger.info("{} deleted the subdomain scan result: {}".format(op, rid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete subdomain scan task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class SubdomainResultExportV1(Resource):
    @auth
    def get(self, tid):
        data = []
        try:
            items = DBSubdomainResult.get_list_by_tid(tid).sort("date", -1)
            for item in items:
                task_info = DBSubdomainTask.find_by_id(item['task_id'])
                if not task_info:
                    continue
                data.append({
                    "tid": str(item['task_id']),
                    'name': task_info['name'],
                    'domain': item['domain'],
                    'subdomain': item['subdomain'],
                    'title': item['title'],
                    'response': item['response'],
                    'ip': item['ip'],
                    'op': task_info['op'],
                    'date': timestamp_to_str(item['date']),
                })
            export = ExportData(data)
            filename = "subdomain_task_" + random_str(6) + ".csv"
            export.csv(["name", "domain", "subdomain", "title", "ip", "response", "op", "date"], tempfile.gettempdir() + "/" + filename)
            response = make_response(send_from_directory(tempfile.gettempdir(), filename, as_attachment=True))
            response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
            return response
        except Exception as e:
            msg = "get port scan result failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)
