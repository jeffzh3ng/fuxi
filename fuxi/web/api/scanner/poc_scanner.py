#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : poc_scanner.py
# @Desc    : ""
import tempfile
import time
from flask import session, request, make_response, send_from_directory
from bson import ObjectId
from flask_restful import Resource, reqparse

from fuxi.common.libs.export_file import ExportData
from fuxi.common.utils.random_str import random_str
from fuxi.common.utils.poc_handler import poc_parser
from fuxi.core.auth.token import auth
from fuxi.common.utils.time_format import timestamp_to_str
from fuxi.common.utils.logger import logger
from fuxi.core.data.response import Response
from fuxi.core.databases.orm.scanner.pocsuite_orm import DBPocsuitePlugin, DBPocsuiteTask, DBPocsuiteVul
from fuxi.core.tasks.scanner.poc_task import t_poc_scanner, quick_poc_scanner


parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('target', type=str)
parser.add_argument('freq', type=str)
parser.add_argument('threads', type=int)
parser.add_argument('poc', type=str)
parser.add_argument('quick', type=bool)

parser.add_argument('task_id', type=str)
parser.add_argument('plugin_id', type=str)
parser.add_argument('search', type=str)
parser.add_argument('action', type=str)
parser.add_argument('keyword', type=str)
parser.add_argument('value', type=str)


class PocsuiteTasksV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            args = parser.parse_args()
            if args['search']:
                task_items = DBPocsuiteTask.filter_by_keyword(args['search']).sort("date", -1)
            else:
                task_items = DBPocsuiteTask.get_list().sort("date", -1)
            for item in task_items:
                data.append({
                    "tid": str(item['_id']),
                    "name": item['name'],
                    "freq": str(item['freq']).lower(),
                    "status": item['status'],
                    "vul_count": item['vul_count'],
                    "op": item['op'],
                    "date": timestamp_to_str(item['date']),
                    "end_date": timestamp_to_str(item['end_date']),
                })
            return Response.success(data=data)
        except Exception as e:
            msg = "get pocsuite tasks failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

    @auth
    def post(self):
        """
        新建 poc 扫描任务
        POST /api/v1/scanner/poc/task
        :return:
        """
        try:
            op = session.get('user')
            args = parser.parse_args()
            name = args['name']
            target = args['target'].split(',')
            poc_id = args['poc'].split(',')
            thread = args['threads'] if args['threads'] else 10
            freq = args['freq']
            if not args['quick']:
                tid = DBPocsuiteTask.add(
                    name=name, target=target, poc=poc_id,
                    thread=thread, freq=freq, op=op
                )
                t_poc_scanner.delay(tid)
                logger.success("{} created the poc scan task {}".format(op, tid))
                return Response.success(message="The task was created successfully")
            else:
                result = quick_poc_scanner(target, poc_id)
                return Response.success(data=result)
        except Exception as e:
            msg = "Failed to create task: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class PocsuiteTaskManageV1(Resource):
    @auth
    def get(self, tid):
        data = {}
        try:
            data = DBPocsuiteTask.get_detail_by_id(tid)
            if data:
                data['poc_name'] = []
                data['_id'] = str(data['_id'])
                data['date'] = timestamp_to_str(data['date'])
                data['end_date'] = timestamp_to_str(data['end_date'])
                poc_items = DBPocsuitePlugin.get_list(
                    {"$or": [{"_id": ObjectId(x)} for x in data['poc']]},
                    {"name": 1}
                )
                for poc in poc_items:
                    data['poc_name'].append(poc['name'])
                return Response.success(data=data)
            else:
                return Response.failed(message="can't find task", data={})
        except Exception as e:
            msg = "get pocsuite task detail failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

    @auth
    def delete(self, tid):
        """
        通过任务 id 删除任务
        DELETE /api/v1/scanner/poc/task/<tid>
        :param tid:
        :return:
        """
        try:
            op = session.get('user')
            DBPocsuiteTask.delete_by_id(tid)
            logger.info("{} deleted the pocsuite task: {}".format(op, tid))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete poc task failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)

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
                DBPocsuiteVul.delete_by_tid(tid)
                # update task info
                DBPocsuiteTask.update_by_id(tid, {
                    "date": int(time.time()),
                    "status": "waiting",
                    "end_date": 0
                })
                # celery task
                t_poc_scanner.delay(tid)
                logger.info("{} {} rescan poc scan task".format(session.get('user'), tid))
            return Response.success(message="successfully {}".format(action))
        except Exception as e:
            msg = "rescan the task failed: {}".format(e)
            logger.warning(tid + msg)
            return Response.failed(message=msg)


class PocsuitePluginsV1(Resource):
    desc = "The module will return to the poc list"

    @auth
    def get(self):
        """
        获取 poc 插件列表
        GET /api/v1/scanner/poc/plugin
        :return: all plugin [list]
        """
        data = []
        try:
            args = parser.parse_args()
            if args['search']:
                poc_items = DBPocsuitePlugin.filter_by_keyword(args['search']).sort("date", -1)
            else:
                poc_items = DBPocsuitePlugin.get_list().sort("date", -1)
            for item in poc_items:
                data.append({
                    "pid": str(item['_id']),
                    "name": item['name'],
                    "type": item['type'],
                    "app": item['app'],
                    "op": item['op'],
                    "date": timestamp_to_str(item['date']),
                })
            return Response.success(data=data)
        except Exception as e:
            logger.warning("get pocsuite plugin failed: {}".format(e))
            return Response.failed(message=e, data=data)

    @auth
    def post(self):
        # 插件上传
        try:
            op = session.get('user')
            file = request.files['file']
            filename = file.filename
            poc_str = file.read().decode("UTF-8")
            # 调 poc_parser 方法正则匹配出插件信息
            poc_data = poc_parser(poc_str)
            pid = DBPocsuitePlugin.add(
                name=poc_data['name'], poc_str=poc_str, filename=filename,
                app=poc_data['app'], poc_type=poc_data['type'], op=op
            )
            if pid:
                msg = "{} pocsuite plugin upload successful: {}".format(op, pid)
                logger.success(msg)
                return Response.success(message=msg)
            else:
                return Response.failed(message="pocsuite plugin upload failed")
        except Exception as e:
            logger.warning("pocsuite plugin upload failed: {}".format(e))
            return Response.failed(message=e)


class PocsuitePluginManageV1(Resource):
    @auth
    def get(self, plugin_id):
        """
        获取 poc 插件详情
        GET /api/v1/scanner/poc/plugin/<plugin_id>
        :return: all plugin [list]
        """
        data = {}
        try:
            data = DBPocsuitePlugin.get_detail_by_id(plugin_id)
            if data:
                data['pid'] = str(data['_id'])
                del data['_id']
                return Response.success(data=data)
            else:
                return Response.failed(message="can't find the pocsuite plugin", data={})
        except Exception as e:
            msg = "get pocsuite plugin detail failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

    @auth
    def delete(self, plugin_id):
        """
        通过 id 删除插件
        DELETE /api/v1/scanner/poc/plugin/<plugin_id>
        :param plugin_id:
        :return:
        """
        try:
            op = session.get('user')
            DBPocsuitePlugin.delete_by_id(plugin_id)
            logger.info("{} deleted the pocsuite plugin: {}".format(op, plugin_id))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete pocsuite plugin failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class PocsuiteResultsV1(Resource):
    @auth
    def get(self):
        """
        获取 vulnerability 列表
        GET /api/v1/scanner/poc/vul
        :return: all vulnerability [list]
        """
        data = []
        try:
            # 这段代码太绕了 抽空优化一下
            args = parser.parse_args()
            if args['task_id'] and args['search']:
                items = DBPocsuiteVul.filter_by_keyword_and_task(
                    args['task_id'], args['search']
                ).sort("date", -1)
            elif args['plugin_id'] and args['search']:
                items = DBPocsuiteVul.filter_by_keyword_and_plugin(
                    args['task_id'], args['search']
                ).sort("date", -1)
            elif args['task_id']:
                items = DBPocsuiteVul.filter_by_tid(args['task_id']).sort("date", -1)
            elif args['plugin_id']:
                items = DBPocsuiteVul.filter_by_plugin(args['plugin_id']).sort("date", -1)
            elif args['search']:
                items = DBPocsuiteVul.filter_by_keyword(args['search']).sort("date", -1)
            else:
                items = DBPocsuiteVul.get_list().sort("date", -1)
            for item in items:
                if item['status'] != "success":
                    continue
                item['vid'] = str(item['_id'])
                item['date'] = timestamp_to_str(item['date'])
                del item['_id']
                data.append(item)
            return Response.success(data=data)
        except Exception as e:
            logger.warning("get pocsuite vulnerability failed: {}".format(e))
            return Response.failed(message=e, data=data)


class PocsuiteResultManageV1(Resource):
    @auth
    def get(self, vul_id):
        """
        GET /api/v1/scanner/poc/vul/<vul_id>
        :return: all plugin [list]
        """
        data = {}
        try:
            data = DBPocsuiteVul.get_detail_by_id(vul_id)
            if data:
                data['vid'] = str(data['_id'])
                del data['_id']
                data['date'] = timestamp_to_str(data['date'])
                return Response.success(data=data)
            else:
                return Response.failed(message="can't find the vulnerability", data={})
        except Exception as e:
            msg = "get pocsuite vulnerability failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

    @auth
    def delete(self, vul_id):
        """
        通过 id 删除漏洞
        DELETE /api/v1/scanner/poc/vul/<vul_id>
        :param vul_id:
        :return:
        """
        try:
            op = session.get('user')
            DBPocsuiteVul.delete_by_id(vul_id)
            logger.info("{} deleted the vulnerability: {}".format(op, vul_id))
            return Response.success(message="successfully deleted")
        except Exception as e:
            msg = "delete pocsuite vulnerability failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class PocsuiteResultExportV1(Resource):
    @auth
    def get(self):
        data = []
        title = []
        try:
            args = parser.parse_args()
            if args['keyword'] == "tid":
                items = DBPocsuiteVul.filter_by_tid(args['value']).sort("date", -1)
            elif args['keyword'] == "pid":
                items = DBPocsuiteVul.filter_by_plugin(args['value']).sort("date", -1)
            else:
                items = DBPocsuiteVul.get_list().sort("date", -1)
            for item in items:
                item['vid'] = str(item['_id'])
                item['date'] = timestamp_to_str(item['date'])
                del item['_id']
                del item['poc']
                data.append(item)
            if len(data) > 0:
                title = [str(i) for i in data[0]]
            export = ExportData(data)
            filename = "poc_task_" + random_str(6) + ".csv"
            export.csv(title, tempfile.gettempdir() + "/" + filename)
            response = make_response(send_from_directory(tempfile.gettempdir(), filename, as_attachment=True))
            response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
            return response
        except Exception as e:
            msg = "export poc scan result failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)
