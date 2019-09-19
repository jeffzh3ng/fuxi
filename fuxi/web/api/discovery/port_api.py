#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/9/6
# @File    : port_api.py
# @Desc    : ""

from flask import session
from flask_restful import Resource, reqparse
from fuxi.core.databases.orm.discovery.port_orm import DBPortScanTasks
from fuxi.common.utils.logger import logger
from fuxi.core.auth.token import auth
from fuxi.common.utils.time_format import timestamp_to_str
from fuxi.core.data.response import Response

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('target', type=str)
parser.add_argument('port', type=str)
parser.add_argument('option', type=str)
parser.add_argument('threat', type=int)


class PortScanTasksV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            items = DBPortScanTasks.get_list().sort("date", -1)
            for item in items:
                tmp_data = {
                    "tid": str(item['_id']),
                    'name': item['name'],
                    'target': item['target'],
                    'port': item['port'],
                    'threat': item['threat'],
                    'option': item['option'],
                    'status': item['status'],
                    'date': timestamp_to_str(item['date']),
                    'op': item['op']
                }
                data.append(tmp_data)
            return Response.success(data=data)
        except Exception as e:
            msg = "get port scan task list failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)

    @auth
    def post(self):
        try:
            op = session.get('user')
            args = parser.parse_args()
            name = args['name']
            target_list = [target.strip() for target in args['target'].split(',')]
            port_list = [int(port.strip()) for port in args['port'].split(',')] if args['port'] else []
            option = args['option']
            threat = args['threat']
            tid = DBPortScanTasks.add(
                name=name, target=target_list, port=port_list, option=option, threat=threat, op=op
            )
            logger.success("{} created the port scan task: {}".format(op, tid))
            return Response.success(message="The task was created successfully")
        except Exception as e:
            msg = "created the port scan task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)
