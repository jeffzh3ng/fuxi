#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/9/6
# @File    : port_api.py
# @Desc    : ""

import time
from flask import session
from flask_restful import Resource, reqparse
from fuxi.core.databases.orm.discovery.port_orm import DBPortScanTasks, DBPortScanResult
from fuxi.common.utils.logger import logger
from fuxi.core.auth.token import auth
from fuxi.common.utils.time_format import timestamp_to_str
from fuxi.core.data.response import Response
from fuxi.core.tasks.discovery.port_scan_task import t_port_scan

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('target', type=str)
parser.add_argument('port', type=str)
parser.add_argument('option', type=str)
parser.add_argument('action', type=str)
parser.add_argument('search', type=str)

OPTIONS = {
    "10001": "-sT -T4",
    "10002": "-Pn"
}


class PortScanTasksV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            args = parser.parse_args()
            if args.get('search'):
                items = DBPortScanTasks.search(args['search']).sort("date", -1)
            else:
                items = DBPortScanTasks.get_list().sort("date", -1)
            # items = DBPortScanTasks.get_list().sort("date", -1)
            for item in items:
                online = DBPortScanResult.get_count({"task_id": str(item['_id'])})
                tmp_data = {
                    "tid": str(item['_id']),
                    'name': item['name'],
                    'target': item['target'],
                    'port': item['port'],
                    'option': item['option'],
                    'status': item['status'],
                    'online': online,
                    'date': timestamp_to_str(item['date']),
                    'end_date': timestamp_to_str(item['end_date']),
                    'op': item['op']
                }
                data.append(tmp_data)
            return Response.success(data=data)
        except Exception as e:
            msg = "get port scan task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)

    @auth
    def post(self):
        try:
            args = parser.parse_args()
            name = args['name']
            target_list = [target.strip() for target in args['target'].split(',')]
            port_list = [int(port.strip()) for port in args['port'].split(',')] if args['port'] else []
            option = OPTIONS.get(args['option'])
            tid = DBPortScanTasks.add(
                name=name, target=target_list, port=port_list, option=option
            )
            t_port_scan.delay(tid)
            logger.success("{} created the port scan task: {}".format(session.get('user'), tid))
            return Response.success(message="The task was created successfully")
        except Exception as e:
            msg = "task creation failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class PortScanTaskManageV1(Resource):
    @auth
    def get(self, tid):
        data = {}
        try:
            data = DBPortScanTasks.find_by_id(tid)
            data['task_id'] = str(data['_id'])
            data['date'] = timestamp_to_str(data['date'])
            data['end_date'] = timestamp_to_str(data['end_date'])
            # data['target'] = "\n".join(data['target'])
            # data['port'] = ",".join([str(i) for i in data['port']]) if data['port'] else "default"
            data['online'] = DBPortScanResult.get_count({"task_id": data['task_id']})
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
                DBPortScanResult.delete_by_tid(tid)
                # update task info
                DBPortScanTasks.update_by_id(tid, {
                    "date": int(time.time()),
                    "status": "running",
                    "end_date": 0
                })
                # celery task
                t_port_scan.delay(tid)
                logger.info("{} {} port scan task rescan".format(session.get('user'), tid))
            return Response.success(message="successfully {}".format(action))
        except Exception as e:
            msg = "rescan port scan task failed: {}".format(e)
            logger.warning(tid + msg)
            return Response.failed(message=msg)

    @auth
    def delete(self, tid):
        """
        delete task by task id
        DELETE /api/v1/discovery/port/task/<tid>
        :param tid:
        :return:
        """
        try:
            op = session.get('user')
            DBPortScanTasks.delete_by_id(tid)
            DBPortScanResult.delete_by_tid(tid)
            logger.info("{} deleted the port scan task: {}".format(op, tid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete port scan task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class PortScanResultV1(Resource):
    @auth
    def get(self, tid):
        data = []
        try:
            args = parser.parse_args()
            if args.get('search'):
                items = DBPortScanResult.search(tid, args['search']).sort("date", -1)
            else:
                items = DBPortScanResult.get_list_by_tid(tid).sort("date", -1)
            # items = DBPortScanResult.get_list_by_tid(tid).sort("date", -1)
            task_name = DBPortScanTasks.find_by_id(tid)['name']
            for item in items:
                tmp_data = {
                    "hid": str(item['_id']),
                    "tid": tid,
                    'name': task_name,
                    'host': item['host'],
                    'hostname': item['hostname'] if item['hostname'] else "-",
                    'port': item['port'],
                    'port_str': ",".join([str(i) for i in item['port']]) if item['port'] else "-",
                    'date': timestamp_to_str(item['date']),
                }
                data.append(tmp_data)
            return Response.success(data=data)
        except Exception as e:
            msg = "get port scan result failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)


class PortScanHostV1(Resource):
    @auth
    def get(self, hid):
        data = []
        try:
            item = DBPortScanResult.find_by_id(hid)
            for port in item['detail']:
                name = port['detail'].get("name")
                del port['detail']['name']
                del port['detail']['conf']
                del port['detail']['reason']
                del port['detail']['state']
                data.append({
                    "host": item['host'],
                    "hostname": item['hostname'],
                    "task_id": item['task_id'],
                    "date": item['date'],
                    "port": port['port'],
                    "name": name,
                    "extrainfo": port['detail']
                })
            return Response.success(data=data)
        except Exception as e:
            msg = "get host detail failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

    @auth
    def delete(self, hid):
        """
        delete host by id
        DELETE /api/v1/discovery/port/host/<hid>
        :param hid:
        :return:
        """
        try:
            op = session.get('user')
            DBPortScanResult.delete_by_id(hid)
            logger.info("{} deleted the host: {}".format(op, hid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete host failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)

