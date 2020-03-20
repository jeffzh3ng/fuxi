#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/01/07
# @File    : whatweb_api.py 
# @Desc    : ""
import mimetypes
import tempfile
import time
from flask import session, make_response, send_from_directory
from flask_restful import Resource, reqparse
from fuxi.core.databases.orm.discovery.whatweb_orm import DBWebFingerPrint, DBWhatwebTask
from fuxi.common.utils.logger import logger
from fuxi.core.auth.token import auth
from fuxi.common.utils.time_format import timestamp_to_str
from fuxi.common.utils.random_str import random_str
from fuxi.core.data.response import Response
from fuxi.core.tasks.discovery.whatweb_task import t_whatweb_task
from fuxi.common.libs.export_file import ExportData

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('target', type=str)
parser.add_argument('level', type=int)   # 1: stealthy 3: aggressive 4: heavy
parser.add_argument('threads', type=int)
parser.add_argument('option', type=str)
parser.add_argument('header', type=str)
parser.add_argument('plugin', type=str)
parser.add_argument('cookie', type=str)
parser.add_argument('keyword', type=str)
parser.add_argument('value', type=str)
parser.add_argument('action', type=str)

LEVEL_MAP = {1: "stealthy", 3: "aggressive", 4: "heavy"}


class WhatwebTasksV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            items = DBWhatwebTask.get_list().sort("date", -1)
            for i in items:
                if not i.get("name"):
                    continue
                i['tid'] = str(i['_id'])
                del i['_id']
                i['date'] = timestamp_to_str(i['date'])
                i['count'] = DBWebFingerPrint.get_count({"task_id": i['tid']})
                i['end_date'] = timestamp_to_str(i['end_date'])
                i['level'] = LEVEL_MAP.get(i['level'])
                data.append(i)
            return Response.success(data=data)
        except Exception as e:
            msg = "get task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)

    @auth
    def post(self):
        # todo: User input should be checked for security
        # developing: (plugin, option, args security... )
        # I don't want to make ！！！ <T_T>
        try:
            args = parser.parse_args()
            name = args.get("name")
            target = [t.strip() for t in args['target'].split(',')] if args.get("target") else []
            # 1: stealthy 3: aggressive 4: heavy ( default 3 )
            level = args.get("level") if args.get("level") in [1, 3, 4] else 3
            threads = args.get("threads") if args.get("threads") else 25
            option = args.get("option") if args.get("option") else ""
            header = args.get("header") if args.get("header") else ""
            plugin = [i.strip() for i in args['plugin'].split(',')] if args.get("plugin") else []
            cookie = args.get("cookie") if args.get("cookie") else ""
            tid = DBWhatwebTask.add(
                name=name, target=target, level=level, threads=threads, option=option,
                header=header, plugin=plugin, cookie=cookie
            )
            t_whatweb_task.delay(tid)
            logger.success("{} created the whatweb task: {}".format(session.get('user'), tid))
            return Response.success(message="The task was created successfully")
        except Exception as e:
            msg = "task creation failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class WhatwebScanTestV1(Resource):
    @auth
    def post(self):
        # todo: User input should be checked for security
        data = []
        try:
            args = parser.parse_args()
            target = [t.strip() for t in args['target'].split(',')] if args.get("target") else []
            tid = DBWhatwebTask.add(
                name="Temporary task", target=target, level=3, threads=25, option=None,
                header=None, plugin=None, cookie=None
            )
            items = t_whatweb_task(tid, True)
            for item in items:
                tmp_data = {
                    'domain': item['target'],
                    'title': item['title'],
                    'http_status': item['http_status'],
                    'country': item['country'],
                    'c_code': item['c_code'].lower() if item.get('c_code') else "zz",
                    'ip': item['ip'],
                    'summary': item['summary'],
                    'request': item['request'],
                    'fingerprint': item['fingerprint'],
                }
                data.append(tmp_data)
            return Response.success(data=data)
        except Exception as e:
            msg = "test failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)


class WhatwebTaskManageV1(Resource):
    @auth
    def get(self, tid):
        # data = {}
        data = []
        try:
            items = DBWebFingerPrint.find_by_tid(tid)
            for item in items:
                plugin = []
                item['rid'] = str(item['_id'])
                del item['_id']
                item['c_code'] = str(item['c_code']).lower() if item.get('c_code') else "us"
                item['date'] = timestamp_to_str(item['date'])
                for p in item['fingerprint']:
                    plugin.append(p['plugin'])
                item['plugin'] = plugin
                data.append(item)
            # data = DBWhatwebTask.find_by_id(tid)
            # if data:
            #     data['task_id'] = str(data['_id'])
            #     data['date'] = timestamp_to_str(data['date'])
            #     data['end_date'] = timestamp_to_str(data['end_date'])
            #     del data['_id']
            return Response.success(data=data)
        except Exception as e:
            msg = "get task detail failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

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
                # this action will delete website fingerprint data
                DBWebFingerPrint.delete_by_tid(tid)
                # update task info
                DBWhatwebTask.update_by_id(tid, {
                    "date": int(time.time()),
                    "status": "running",
                    "end_date": 0
                })
                # celery task
                t_whatweb_task.delay(tid)
                logger.info("{} {}: whatweb task rescan".format(session.get('user'), tid))
            return Response.success(message="successfully {}".format(action))
        except Exception as e:
            msg = "rescan the task failed: {}".format(e)
            logger.warning(tid + msg)
            return Response.failed(message=msg)

    @auth
    def delete(self, tid):
        """
        delete task by task id
        DELETE /api/v1/discovery/whatweb/task/<tid>
        :param tid:
        :return:
        """
        try:
            op = session.get('user')
            DBWhatwebTask.delete_by_id(tid)
            # this action will delete website fingerprint data
            # developer, you can change this
            DBWebFingerPrint.delete_by_tid(tid)
            logger.info("{} deleted the whatweb task: {}".format(op, tid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete the task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class WebsiteFPSearchV1(Resource):
    # this is a demo
    # developing: app, version, ip, domain....
    @auth
    def get(self):
        data = []
        uniq = []
        try:
            args = parser.parse_args()
            if args.get('keyword') and args.get('value'):
                # Developer say on a rainy day: this design sucks !!!!
                keyword = str(args.get('keyword')).lower()
                value = args.get('value').split('||')
                if len(value) == 1:
                    items = DBWebFingerPrint.search(keyword, value[0]).sort("date", -1)
                else:
                    items = DBWebFingerPrint.search(keyword, value[0], value[1]).sort("date", -1)
            else:
                items = DBWebFingerPrint.get_list().sort("date", -1)
            for item in items:
                # domains redupliction removing
                if item['target'] in uniq:
                    continue
                tmp_data = {
                    "tid": str(item['task_id']),
                    'domain': item['target'],
                    'title': item['title'],
                    'http_status': item['http_status'],
                    'country': item['country'],
                    'c_code': str(item['c_code']).lower() if item.get('c_code') else "cn",
                    'ip': item['ip'],
                    'summary': item['summary'],
                    'request': item['request'],
                    'fingerprint': item['fingerprint'],
                    'date': timestamp_to_str(item['date'])
                }
                uniq.append(item['target'])
                data.append(tmp_data)
            return Response.success(data=data)
        except Exception as e:
            msg = "get website fingerprint failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)


class WebsiteFPManageV1(Resource):
    @auth
    def delete(self, rid):
        try:
            op = session.get('user')
            DBWebFingerPrint.delete_by_id(rid)
            logger.info("{} deleted the whatweb result: {}".format(op, rid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete the task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class WebFPExportV1(Resource):
    @auth
    def get(self, file_type):
        data = []
        uniq = []
        try:
            args = parser.parse_args()
            if args.get('keyword') and args.get('value'):
                # Developer say on a rainy day: this design sucks !!!!
                keyword = str(args.get('keyword')).lower()
                value = args.get('value').split('||')
                if len(value) == 1:
                    items = DBWebFingerPrint.search(keyword, value[0]).sort("date", -1)
                else:
                    items = DBWebFingerPrint.search(keyword, value[0], value[1]).sort("date", -1)
            else:
                items = DBWebFingerPrint.get_list().sort("date", -1)
            for item in items:
                # domains redupliction removing
                if item['target'] in uniq:
                    continue
                plugin = []
                for p in item['fingerprint']:
                    plugin.append(p['plugin'])
                item['plugin'] = plugin
                tmp_data = {
                    'domain': item['target'],
                    'title': item['title'],
                    'response': item['http_status'],
                    'country': str(item['country']).lower(),
                    'ip': item['ip'],
                    'app': ",".join(plugin),
                    'date': timestamp_to_str(item['date'])
                }
                uniq.append(item['target'])
                data.append(tmp_data)
            export = ExportData(data)
            filename = "whatweb_" + random_str(6)
            if file_type == "txt":
                filename += ".txt"
                export.txt([], tempfile.gettempdir() + "/" + filename)
            elif file_type == "csv":
                filename += ".csv"
                export.csv(["domain", "title", "response", "country", "ip", "app", "date"], tempfile.gettempdir() + "/" + filename)
            response = make_response(send_from_directory(tempfile.gettempdir(), filename, as_attachment=True))
            response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
            return response
        except Exception as e:
            msg = "export website fingerprint failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class WebFPExportWithTIDV1(Resource):
    @auth
    def get(self, tid):
        data = []
        try:
            items = DBWebFingerPrint.find_by_tid(tid)
            for item in items:
                plugin = []
                for p in item['fingerprint']:
                    plugin.append(p['plugin'])
                item['plugin'] = plugin
                tmp_data = {
                    'domain': item['target'],
                    'title': item['title'],
                    'response': item['http_status'],
                    'country': str(item['country']).lower(),
                    'ip': item['ip'],
                    'app': ",".join(plugin),
                    'date': timestamp_to_str(item['date'])
                }
                data.append(tmp_data)
            export = ExportData(data)
            filename = "whatweb_" + random_str(6) + ".csv"
            export.csv(["domain", "title", "response", "country", "ip", "app", "date"],
                       tempfile.gettempdir() + "/" + filename)
            response = make_response(send_from_directory(tempfile.gettempdir(), filename, as_attachment=True))
            response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
            return response
        except Exception as e:
            msg = "export website fingerprint failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)
