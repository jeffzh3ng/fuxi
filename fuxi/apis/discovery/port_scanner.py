#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/4/29
# @File    : port_scanner.py
# @Desc    : ""

from flask_restful import Resource
from fuxi.libs.common.logger import logger
from fuxi.libs.data.error import API_FAILED
from fuxi.libs.core.token import access_token
from fuxi.database import MongoDB, T_PORT_TASKS
from fuxi.tasks.discovery.port_scanner import port_scanner


class PortScannerTasks(Resource):
    desc = "port scanner"

    @access_token
    def get(self):
        data = []
        try:
            items = MongoDB(T_PORT_TASKS).find()
            for item in items:
                data.append({
                    'tid': str(item['_id']),
                    'name': item['name']
                })

            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("generate token error {}".format(e))
            return {'code': 10501, 'status': 'failed', 'message': API_FAILED}

