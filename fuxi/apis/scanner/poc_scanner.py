#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : poc_scanner.py
# @Desc    : ""

import time
from bson import ObjectId
from flask_restful import Resource, reqparse
from fuxi.libs.core.token import access_token
from fuxi.libs.common.logger import logger
from fuxi.libs.core.user_info import get_user_info
from fuxi.libs.data.error import API_FAILED
from fuxi.database import MongoDB, T_POC_TASKS, T_POC_PLUGINS, T_POC_VULS
from fuxi.tasks.scanner.poc_task import t_poc_scanner, quick_poc_scanner


parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('target', type=str)
parser.add_argument('freq', type=str)
parser.add_argument('thread', type=int)
parser.add_argument('poc_id', type=str)
parser.add_argument('poc_name', type=str)
parser.add_argument('other', type=bool)
parser.add_argument('tid', type=str)
parser.add_argument('filter_type', type=str)
parser.add_argument('filter_key', type=str)


class NewPoCScanTask(Resource):
    @access_token
    def post(self):
        """
        新建 poc 扫描任务
        POST /api/v1/scanner/poc/task
        :return:
        """
        try:
            username = get_user_info()['username']
            args = parser.parse_args()
            task_data = {
                "name": args['name'],
                "target": args['target'],
                "poc_id": args['poc_id'],
                "poc_name": args['poc_name'],
                "thread": args['thread'],
                "freq": args['freq'],
                "status": "waiting",
                "end_date": "-",
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "vul_count": 0,
                "username": username
            }
            t_id = MongoDB(T_POC_TASKS).insert_one(task_data)
            t_poc_scanner.delay(str(t_id), args['thread'])
            logger.success("{} created the poc scan task {}".format(username, t_id))
            return {'code': 10200, 'status': 'success', 'message': 'The task was created successfully', 'data': ""}
        except Exception as e:
            logger.error("Failed to create task: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': API_FAILED, 'data': ""}


class PocTaskList(Resource):
    desc = "The module will return to the task list"

    @access_token
    def get(self):
        """
        获取 poc task 插件列表
        GET /api/v1/scanner/poc/tasks
        :return: all task [list]
        """
        data = []
        task_items = MongoDB(T_POC_TASKS).find().sort("date", -1)
        for item in task_items:
            data.append({
                "tid": str(item['_id']),
                "name": item['name'],
                "freq": item['freq'],
                "status": item['status'],
                "vul_count": item['vul_count'],
                "date": item['date'],
                "end_date": item['end_date'],
            })
        return {'code': 10200, 'status': 'success', 'message': '', 'data': data}


class PocTaskListFilter(Resource):
    @access_token
    def get(self):
        """
        筛选任务列表
        :return: 漏洞扫描结果 (list)
        """
        try:
            data = []
            username = get_user_info()['username']
            args = parser.parse_args()
            keyword = args['filter_key']
            task_items = MongoDB(T_POC_TASKS).find(
                {"$or": [
                    {"name": {'$regex': keyword}}, {"target": {'$regex': keyword}},
                    {"poc_name": {'$regex': keyword}}, {"freq": {'$regex': keyword}},
                    {"user": keyword}, {"status": keyword}
                ]}
            ).sort("date", -1)
            for item in task_items:
                data.append({
                    "tid": str(item["_id"]),
                    "name": item['name'],
                    "freq": item['freq'],
                    "status": item['status'],
                    "vul_count": item['vul_count'],
                    "date": item['date'],
                    "end_date": item['end_date'],
                })
            logger.success("{} get poc vul list".format(username))
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get poc vul list failed: {}".format(e))
            return {'code': 10200, 'status': 'failed', 'message': API_FAILED}


class PocPluginList(Resource):
    desc = "The module will return to the poc list"

    @access_token
    def get(self):
        """
        获取 poc 插件列表
        GET /api/v1/scanner/poc/plugins
        :return: all plugin [list]
        """
        data = []
        poc_items = MongoDB(T_POC_PLUGINS).find().sort("date", -1)
        for item in poc_items:
            data.append({
                "pid": str(item['_id']),
                "name": item['name'],
                "type": item['type'],
                "app": item['app'],
                "date": item['date'].split(' ')[0],
            })
        return {'code': 10200, 'status': 'success', 'message': '', 'data': data}


class PocPluginListFilter(Resource):
    desc = "The module will return to the poc list"

    @access_token
    def get(self):
        """
        通过关键字筛选出插件列表
        :param filter_key: redis
        :return:
        """
        data = []
        args = parser.parse_args()
        keyword = args['filter_key']
        poc_items = MongoDB(T_POC_PLUGINS).find(
            {"$or": [
                {"name": {'$regex': keyword}}, {"filename": {'$regex': keyword}},
                {"type": {'$regex': keyword}}, {"desc": {'$regex': keyword}},
                {"date": {'$regex': keyword}}, {"poc": {'$regex': keyword}}, {"date": keyword}
            ]}
        ).sort("date", -1)
        for item in poc_items:
            data.append({
                "pid": str(item['_id']),
                "name": item['name'],
                "type": item['type'],
                "app": item['app'],
                "date": item['date'].split(' ')[0],
            })
        return {'code': 10200, 'status': 'success', 'message': '', 'data': data}


class PocTaskAction(Resource):
    desc = "Poc task management module"

    @access_token
    def delete(self, tid):
        """
        通过插件 id 获取删除任务
        DELETE /api/v1/scanner/poc/task/<tid>
        :param tid:
        :return:
        """
        try:
            username = get_user_info()['username']
            MongoDB(T_POC_TASKS).delete_one({"_id": ObjectId(tid)})
            logger.info("{} deleted the poc: {}".format(username, tid))
            return {'code': 10200, 'status': 'success', 'message': 'successfully deleted'}
        except Exception as e:
            logger.error("delete poc failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': API_FAILED}


class PocPluginAction(Resource):
    desc = "Poc management module"

    @access_token
    def get(self, pid):
        """
        通过插件 id 获取插件内容
        GET /api/v1/scanner/poc/plugin/<pid>
        :param pid:
        :return: data = {"filename": "", "poc": "}
        """
        try:
            item = MongoDB(T_POC_PLUGINS).find_one({"_id": ObjectId(pid)})
            data = {
                "filename": item['filename'],
                "poc": item['poc'],
            }
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get poc detail failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': API_FAILED}

    @access_token
    def delete(self, pid):
        """
        通过插件 id 获取删除插件
        DELETE /api/v1/scanner/poc/plugin/<pid>
        :param pid:
        :return:
        """
        try:
            username = get_user_info()['username']
            MongoDB(T_POC_PLUGINS).delete_one({"_id": ObjectId(pid)})
            logger.info("{} deleted the poc: {}".format(username, pid))
            return {'code': 10200, 'status': 'success', 'message': 'successfully deleted'}
        except Exception as e:
            logger.error("delete poc failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': API_FAILED}


class QuickPocScan(Resource):
    desc = "Create a temporary task"

    @access_token
    def post(self):
        """
        进行一次快速扫描 阻塞形式 不存数据库 建议前端传任务不要太多
        POST /api/v1/scanner/poc/scan
        :return: 原始扫描结果 (list)
        """
        try:
            username = get_user_info()['username']
            args = parser.parse_args()
            target = args['target']
            poc_id = args['poc_id']
            result = quick_poc_scanner(target.split("\n"), poc_id.split('\n'))
            if result:
                logger.success("{} quick poc scan completed".format(username))
                return {'code': 10200, 'status': 'success', 'message': '', 'data': result}
            else:
                return {'code': 10500, 'status': 'failed', 'message': API_FAILED, 'data': ""}
        except Exception as e:
            logger.error("quick poc scan failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': API_FAILED, 'data': str(e)}


class PocVulList(Resource):
    desc = "Poc scan results"

    @access_token
    def get(self):
        """
        获取 poc 扫描漏洞列表
        GET /api/v1/scanner/poc/vuls
        :return: 漏洞扫描结果 (list)
        """
        try:
            data = []
            username = get_user_info()['username']
            res_items = MongoDB(T_POC_VULS).find().sort("date", -1)
            for item in res_items:
                tmp_data = {
                    "vid": str(item['_id']),
                    "task_name": "【{}】".format(item['task_name']),
                    "target": item['target'],
                    "poc_name": item['poc_name'],
                    "app": item['app'],
                    "status": item['status'],
                    "date": item['date'],
                }
                data.append(tmp_data)
            logger.success("{} get poc vul list".format(username))
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get poc vul list failed: {}".format(e))
            return {'code': 10200, 'status': 'failed', 'message': API_FAILED}


class PocVulAction(Resource):
    desc = "Poc scan result management"

    @access_token
    def delete(self, vid):
        """
        通过漏洞 id 获取删除漏洞
        DELETE /api/v1/scanner/poc/vul/<pid>
        :param vid: 漏洞 id
        :return:
        """
        try:
            username = get_user_info()['username']
            MongoDB(T_POC_VULS).delete_one({"_id": ObjectId(vid)})
            logger.info("{} deleted the vul: {}".format(username, vid))
            return {'code': 10200, 'status': 'success', 'message': 'successfully deleted'}
        except Exception as e:
            logger.error("delete poc vul failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': API_FAILED}


class PocVulListFilter(Resource):
    @access_token
    def get(self):
        """
        GET /api/v1/scanner/poc/vuls/filter
        筛选漏洞列表 一个是从tasks 列表过来 筛选出当前任务扫描结果
        filter_type=task&filter_key=5ca08e6442ca730c7e96000d
        然后就是关键字搜索 key_success
        filter_type=search&filter_key=Redis
        还有在当前任务结果下进行搜索
        tid=5ca08e6442ca730c7e96000d&filter_type=task_filter&filter_key=192
        :return: 漏洞扫描结果 (list)
        """
        try:
            data = []
            res_items = []
            username = get_user_info()['username']
            args = parser.parse_args()
            filter_type = args['filter_type']
            filter_key = args['filter_key']
            if filter_type == 'task':
                res_items = MongoDB(T_POC_VULS).find({"t_id": filter_key}).sort("date", -1)
            elif filter_type == 'search':
                res_items = MongoDB(T_POC_VULS).find(
                    {"$or": [
                        {"task_name": {'$regex': filter_key}}, {"poc_name": {'$regex': filter_key}},
                        {"target": {'$regex': filter_key}}, {"result": {'$regex': filter_key}},
                        {"app": {'$regex': filter_key}}, {"status": {'$regex': filter_key}},
                        {"date": {'$regex': filter_key}}
                    ]}
                ).sort("date", -1)
            elif filter_type == "task_filter":
                task_id = args['tid']
                res_items = MongoDB(T_POC_VULS).find(
                    {
                        "t_id": task_id,
                        "$or": [
                            {"task_name": {'$regex': filter_key}}, {"poc_name": {'$regex': filter_key}},
                            {"target": {'$regex': filter_key}}, {"result": {'$regex': filter_key}},
                            {"app": {'$regex': filter_key}}, {"status": {'$regex': filter_key}},
                            {"date": {'$regex': filter_key}}
                        ]
                    }
                ).sort("date", -1)
            for item in res_items:
                tmp_data = {
                    "vid": str(item['_id']),
                    "task_name": "【{}】".format(item['task_name']),
                    "target": item['target'],
                    "poc_name": item['poc_name'],
                    "app": item['app'],
                    "status": item['status'],
                    "date": item['date'],
                }
                data.append(tmp_data)
            logger.success("{} get poc vul list".format(username))
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get poc vul list failed: {}".format(e))
            return {'code': 10200, 'status': 'failed', 'message': API_FAILED}

