#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/4/14
# @File    : xss.py
# @Desc    : ""

import time
import random
from bson import ObjectId
from flask_restful import Resource, reqparse
from fuxi.common.utils.logger import logger
from fuxi.core.databases.database import MongoDB, T_XSS_PROJECTS, T_XSS_PAYLOADS, T_XSS_RES
from fuxi.common.libs.core.data import RANDOM_SEED_LOW, ERROR_MESSAGE

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('payload', type=str)
parser.add_argument('value', type=str)


class NewXssProject(Resource):
    def post(self):
        try:
            args = parser.parse_args()
            name = args['name'].strip()
            payload_id = args['payload']
            payload_item = MongoDB(T_XSS_PAYLOADS).find_one({"_id": ObjectId(payload_id)})
            if not payload_item:
                return {'code': 10501, 'status': 'error', 'message': "Can't found the payload"}
            salt = ''.join(random.sample(RANDOM_SEED_LOW, 5))
            payload = "var salt='{}';\n".format(salt) + payload_item['value']
            _save_data = {
                "name": name,
                "payload": payload,
                "payload_name": payload_item['name'],
                "path": salt,
                "count": 0,
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }
            t_id = MongoDB(T_XSS_PROJECTS).insert_one(_save_data)
            logger.success("created the xss project: {}".format(t_id))
            return {'code': 10200, 'status': 'success', 'message': 'The project was created successfully', 'data': ""}
        except Exception as e:
            logger.error("created the xss project failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': ERROR_MESSAGE}


class XssProjects(Resource):
    def get(self):
        try:
            data = []
            _items = MongoDB(T_XSS_PROJECTS).find().sort("date", -1)
            for _item in _items:
                data.append({
                    "id": str(_item['_id']),
                    "name": _item['name'],
                    "payload_name": _item['payload_name'],
                    "count": _item['count'],
                    "path": _item['path'],
                    "date": _item['date'],
                })
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get the xss project failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': ERROR_MESSAGE}


class XssProjectAction(Resource):
    def get(self, pid):
        data = []
        try:
            items = MongoDB(T_XSS_RES).find({"salt": pid})
            for item in items:
                item['_id'] = str(item['_id'])
                data.append(item)
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("delete xss project failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': ERROR_MESSAGE}

    def delete(self, pid):
        try:
            MongoDB(T_XSS_PROJECTS).delete_one({"_id": ObjectId(pid)})
            return {'code': 10200, 'status': 'success', 'message': 'deleted successfully'}
        except Exception as e:
            logger.error("delete xss project failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': ERROR_MESSAGE}


class XssResultAction(Resource):
    def delete(self, pid):
        try:
            MongoDB(T_XSS_RES).delete_one({"_id": ObjectId(pid)})
            return {'code': 10200, 'status': 'success', 'message': 'deleted successfully'}
        except Exception as e:
            logger.error("delete xss result failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': ERROR_MESSAGE}


class NewXssPayload(Resource):
    def post(self):
        try:
            args = parser.parse_args()
            name = args['name'].strip()
            value = args['value']
            _save_data = {
                "name": name,
                "value": value,
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }
            t_id = MongoDB(T_XSS_PAYLOADS).insert_one(_save_data)
            logger.success("created the xss payload: {}".format(t_id))
            return {'code': 10200, 'status': 'success', 'message': 'The payload was created successfully', 'data': ""}
        except Exception as e:
            logger.error("created the xss payload failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': ERROR_MESSAGE}


class XssPayloads(Resource):
    def get(self):
        try:
            data = []
            _items = MongoDB(T_XSS_PAYLOADS).find().sort("date", -1)
            for _item in _items:
                data.append({
                    "id": str(_item['_id']),
                    "name": _item['name'],
                    "value": _item['value'],
                    "date": _item['date'],
                })
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get the xss payload failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': ERROR_MESSAGE}


class XssPayloadAction(Resource):
    def put(self, pid):
        try:
            args = parser.parse_args()
            value = args['value']
            MongoDB(T_XSS_PAYLOADS).update_one({"_id": ObjectId(pid)}, {
                "value": value,
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            })
            return {'code': 10200, 'status': 'success', 'message': 'updated successfully'}
        except Exception as e:
            logger.error("update xss payload failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': ERROR_MESSAGE}

    def delete(self, pid):
        try:
            MongoDB(T_XSS_PAYLOADS).delete_one({"_id": ObjectId(pid)})
            return {'code': 10200, 'status': 'success', 'message': 'deleted successfully'}
        except Exception as e:
            logger.error("delete xss payload failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': ERROR_MESSAGE}


