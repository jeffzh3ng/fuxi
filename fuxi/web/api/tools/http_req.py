#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/2/1
# @File    : http_req.py
# @Desc    : ""

from bson import ObjectId
from flask_restful import Resource, reqparse
from fuxi.common.libs.core.token import access_token
from fuxi.core.databases.database import MongoDB, T_HTTP_REQUESTS
from fuxi.common.libs.core import get_user_info
from fuxi.common.utils.logger import logger
from fuxi.common.libs.data import API_FAILED

parser = reqparse.RequestParser()
parser.add_argument('filter_key', type=str)


class HttpLogTask(Resource):
    desc = "The module will return to the HTTPLog"

    @access_token
    def get(self):
        """
        获取 http log 数据
        GET /api/v1/tools/xss/httplog
        :return: all result [list]
        """
        data = []
        task_items = MongoDB(T_HTTP_REQUESTS).find().sort("date", -1)
        for item in task_items:
            data.append({
                "hid": str(item['_id']),
                "refer": item['refer'] if item['refer'] else '-',
                "ip": item['ip'],
                "data": item['data'],
                "date": item['date'],
            })
        return {'code': 10200, 'status': 'success', 'message': '', 'data': data}


class HttpLogAction(Resource):
    desc = "Http log module"

    @access_token
    def delete(self, hid):
        """
        通过插件 id 删除 http log
        DELETE /api/v1/tools/xss/httplog/<hid>
        :param hid:
        :return:
        """
        try:
            username = get_user_info()['username']
            MongoDB(T_HTTP_REQUESTS).delete_one({"_id": ObjectId(hid)})
            logger.info("{} deleted the http log: {}".format(username, hid))
            return {'code': 10200, 'status': 'success', 'message': 'successfully deleted'}
        except Exception as e:
            logger.error("delete poc failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': API_FAILED}


class HttpLogFilter(Resource):
    desc = ""

    @access_token
    def get(self):
        """
        通过关键字筛选出 http 日志
        filter_key=aaa
        :param
        :return:
        """
        data = []
        args = parser.parse_args()
        keyword = args['filter_key']
        task_items = MongoDB(T_HTTP_REQUESTS).find(
            {"$or": [
                {"refer": {'$regex': keyword}}, {"data": {'$regex': keyword}},
                {"ip": {'$regex': keyword}}, {"date": {'$regex': keyword}}
            ]}
        ).sort("date", -1)
        for item in task_items:
            data.append({
                "hid": str(item['_id']),
                "refer": item['refer'],
                "ip": item['ip'],
                "data": item['data'],
                "date": item['date'],
            })
        return {'code': 10200, 'status': 'success', 'message': '', 'data': data}

