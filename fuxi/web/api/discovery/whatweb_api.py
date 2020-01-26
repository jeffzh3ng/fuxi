#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/01/07
# @File    : whatweb_api.py 
# @Desc    : ""

import time
from flask import session
from flask_restful import Resource, reqparse
from fuxi.core.databases.orm.discovery.whatweb_orm import DBWebFingerPrint, DBWhatwebTask
from fuxi.common.utils.logger import logger
from fuxi.core.auth.token import auth
from fuxi.common.utils.time_format import timestamp_to_str
from fuxi.core.data.response import Response
from fuxi.core.tasks.discovery.whatweb_task import t_whatweb_task, WhatwebScanner

parser = reqparse.RequestParser()
parser.add_argument('target', type=str)
parser.add_argument('level', type=int)   # 1: stealthy 3: aggressive 4: heavy
parser.add_argument('threads', type=int)
parser.add_argument('option', type=str)
parser.add_argument('header', type=str)
parser.add_argument('plugin', type=str)
parser.add_argument('cookie', type=str)
parser.add_argument('keyword', type=str)
parser.add_argument('action', type=str)


class WhatwebTasksV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            items = DBWhatwebTask.get_list()
            for i in items:
                i['tid'] = str(i['_id'])
                del i['_id']
                i['date'] = timestamp_to_str(i['date'])
                i['end_date'] = timestamp_to_str(i['end_date'])
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
            target = [t.strip() for t in args['target'].split(',')] if args.get("target") else []
            # 1: stealthy 3: aggressive 4: heavy ( default 3 )
            level = args.get("level") if args.get("level") in [1, 3, 4] else 3
            threads = args.get("threads") if args.get("threads") else 25
            option = args.get("option") if args.get("option") else ""
            header = args.get("header") if args.get("header") else ""
            plugin = [i.strip() for i in args['plugin'].split(',')] if args.get("plugin") else []
            cookie = args.get("cookie") if args.get("cookie") else ""
            tid = DBWhatwebTask.add(
                target=target, level=level, threads=threads, option=option,
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
                target=target, level=3, threads=25, option=None,
                header=None, plugin=None, cookie=None
            )
            data = t_whatweb_task(tid)
            return Response.success(data=data)
        except Exception as e:
            msg = "test failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)


class WhatwebTaskManageV1(Resource):
    @auth
    def get(self, tid):
        data = {}
        try:
            data = DBWhatwebTask.find_by_id(tid)
            if data:
                data['task_id'] = str(data['_id'])
                data['date'] = timestamp_to_str(data['date'])
                data['end_date'] = timestamp_to_str(data['end_date'])
                del data['_id']
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
        try:
            args = parser.parse_args()
            if args.get('keyword'):
                items = DBWebFingerPrint.search(args['keyword']).sort("date", -1)
            else:
                items = DBWebFingerPrint.get_list().sort("date", -1)
            for item in items:
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
                data.append(tmp_data)
            return Response.success(data=data)
        except Exception as e:
            msg = "get website fingerprint failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)

