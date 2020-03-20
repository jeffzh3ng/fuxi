#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/9/6
# @File    : xss_api.py
# @Desc    : ""

from flask import session
from flask_restful import Resource, reqparse
from fuxi.common.utils.logger import logger
from fuxi.core.auth.token import auth
from fuxi.common.utils.time_format import timestamp_to_str
from fuxi.core.data.response import Response
from fuxi.core.databases.orm.exploit.xss_orm import DBXssTasks, DBXssPayloads, DBXssResult

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('payload', type=str)
parser.add_argument('value', type=str)


class XssTasksV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            items = DBXssTasks.get_list().sort("date", -1)
            for item in items:
                count = DBXssResult.get_count({"tid": str(item['_id'])})
                tmp_data = {
                    "tid": str(item['_id']),
                    "salt": item['salt'],
                    'name': item['name'],
                    'payload_name': item['payload_name'],
                    'date': timestamp_to_str(item['date']),
                    'count': count,
                    'op': item['op']
                }
                data.append(tmp_data)
            return Response.success(data=data)
        except Exception as e:
            msg = "get xss task list failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)

    @auth
    def post(self):
        try:
            op = session.get('user')
            args = parser.parse_args()
            name = args['name'].strip()
            payload_id = args['payload']
            payload_item = DBXssPayloads.find_by_id(payload_id)
            if not payload_item:
                return Response.failed("Can't found the payload")
            tid = DBXssTasks.add(name, payload_item['name'], payload_item['value'], op)
            logger.info("created the xss project: {}".format(tid))
            return Response.success(message='The task was created successfully')
        except Exception as e:
            msg = "created the xss task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class XssTaskManageV1(Resource):
    @auth
    def delete(self, tid):
        try:
            op = session.get('user')
            DBXssTasks.delete_by_id(tid)
            logger.info("{} delete xss task: {}".format(op, tid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete xss task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class XssPayloadsV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            items = DBXssPayloads.get_list()
            for item in items:
                data.append({
                    "pid": str(item['_id']),
                    "name": item['name'],
                    "value": item['value'],
                    "date": timestamp_to_str(item['date']),
                })
            return Response.success(data=data)
        except Exception as e:
            msg = "get the xss payload failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)

    @auth
    def post(self):
        try:
            op = session.get('user')
            args = parser.parse_args()
            name = args['name'].strip()
            value = args['value']
            pid = DBXssPayloads.add(name, value)
            logger.success("{} created the xss payload: {}".format(op, pid))
            return Response.success(message='The payload was created successfully')
        except Exception as e:
            msg = "created the xss payload failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class XssPayloadManageV1(Resource):
    @auth
    def delete(self, pid):
        try:
            op = session.get('user')
            DBXssPayloads.delete_by_id(pid)
            logger.info("{} delete xss payload: {}".format(op, pid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete xss task payload failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)

    @auth
    def put(self, pid):
        try:
            op = session.get('user')
            args = parser.parse_args()
            value = args['value']
            DBXssPayloads.update_value_by_id(pid, value)
            logger.info("{} updated xss payload: {}".format(op, pid))
            return Response.success(message="updated successfully")
        except Exception as e:
            msg = "update xss payload failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class XssResultWithTIDV1(Resource):
    @auth
    def get(self, tid):
        data = []
        try:
            task_item = DBXssTasks.find_by_id(tid)
            items = DBXssResult.get_list_by_tid(tid)
            if task_item:
                for item in items:
                    tmp_data = {
                        "rid": str(item['_id']),
                        "tid": item['tid'],
                        "task_name": task_item['name'],
                        "payload_name": task_item['payload_name'],
                        "client": item['client'],
                        "referrer": item['referrer'],
                        "salt": item['salt'],
                        'url': item['url'],
                        'data': item['data'],
                        'extend': item['extend'],
                        'date': timestamp_to_str(item['date']),
                    }
                    data.append(tmp_data)
            return Response.success(data=data)
        except Exception as e:
            msg = "get xss result list failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)


class XssResultListV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            items = DBXssResult.get_list()
            for item in items:
                task_item = DBXssTasks.find_by_id(item['tid'])
                if task_item:
                    tmp_data = {
                        "rid": str(item['_id']),
                        "tid": item['tid'],
                        "task_name": task_item['name'],
                        "payload_name": task_item['payload_name'],
                        "client": item['client'],
                        "referrer": item['referrer'],
                        "salt": item['salt'],
                        'url': item['url'],
                        'data': item['data'],
                        'extend': item['extend'],
                        'date': timestamp_to_str(item['date']),
                    }
                    data.append(tmp_data)
            return Response.success(data=data)
        except Exception as e:
            msg = "get xss result list failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)


class XssResultManageV1(Resource):
    @auth
    def delete(self, rid):
        try:
            op = session.get('user')
            DBXssResult.delete_by_id(rid)
            logger.info("{} delete xss result: {}".format(op, rid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete xss task result failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)
