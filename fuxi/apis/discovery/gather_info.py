#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/25
# @File    : gather_info.py
# @Desc    : ""

from flask_restful import Resource, reqparse
from fuxi.libs.core.token import access_token
from fuxi.databases import db, FuxiDiscoveryTask, FuxiDiscoveryPort
from fuxi.libs.common.logger import logger
from fuxi.libs.core.user_info import user_info
from fuxi.tasks.discovery.discovery_task import t_discovery_task
from fuxi.libs.core.data import ERROR_MESSAGE

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('target', type=str)
parser.add_argument('plugin', type=str)
parser.add_argument('desc', type=str)


class DiscoveryTasks(Resource):
    desc = "This module will return the discovery task information"

    @access_token
    def get(self):
        """
        获取 discovery task 插件列表
        GET /api/v1/discovery/tasks
        :return:
        """
        data = []
        try:
            db.session.commit()
            # 按 date 倒序取数据
            task_items = FuxiDiscoveryTask.query.order_by(FuxiDiscoveryTask.date.desc()).all()
            for item in task_items:
                data.append({
                    "tid": item.t_id,
                    "name": item.name,
                    "plugin": item.plugin,
                    "status": item.status,
                    "desc": item.desc,
                    "date": item.date,
                    "end_date": item.end_date,
                })
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get discovery task failed: {}".format(e))
            return {'code': 10501, 'status': 'failed', 'message': 'get discovery task failed', 'data': data}


class NewDiscoveryTask(Resource):
    desc = "Used to create discovery task"

    @access_token
    def post(self):
        """
        新建 discovery 任务
        POST /api/v1/discovery/task
        :return:
        """
        try:
            username = user_info()['username']
            args = parser.parse_args()
            task_data = {
                "name": args['name'],
                "target": args['target'],
                "plugin": args['plugin'],
                "desc": args['desc'],
            }
            t_id = FuxiDiscoveryTask(task_data).save()
            # 异步执行服务发现任务
            t_discovery_task.delay(t_id)
            logger.success("{} created the discovery task: {}".format(username, t_id))
            return {'code': 10200, 'status': 'success', 'message': 'The task was created successfully', 'data': ""}
        except Exception as e:
            logger.error("failed to create task: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': 'Failed to create task', 'data': ""}


class DiscoveryTaskAction(Resource):
    desc = "Discovery task management module"

    @access_token
    def get(self, tid):
        try:
            db.session.commit()
            host = []
            task_item = FuxiDiscoveryTask.query.filter_by(t_id=tid).first()
            host_items = FuxiDiscoveryPort.query.filter_by(t_id=tid).all()
            for item in host_items:
                if item.host not in host:
                    host.append(item.host)
            data = {
                "tid": task_item.t_id,
                "name": task_item.name,
                "target": task_item.target.split('\n'),
                "plugin": task_item.plugin.split(','),
                "host": host,
                "desc": task_item.desc,
                "status": task_item.status,
                "date": task_item.date,
                "end_date": task_item.end_date,
            }
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get discovery detail failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': 'An error occurred, please try again later'}

    @access_token
    def delete(self, tid):
        """
        通过插件 id 获取删除任务
        DELETE /api/v1/discovery/task/<tid>
        :param tid:
        :return:
        """
        try:
            username = user_info()['username']
            item = FuxiDiscoveryTask.query.filter_by(t_id=tid).first()
            db.session.delete(item)
            db.session.commit()
            logger.info("{} deleted the discovery task: {}".format(username, tid))
            return {'code': 10200, 'status': 'success', 'message': 'successfully deleted'}
        except Exception as e:
            logger.error("delete poc failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': ERROR_MESSAGE}


class DiscoveryHostAction(Resource):
    @access_token
    def get(self, tid):
        try:
            db.session.commit()
            data = []
            host_items = FuxiDiscoveryPort.query.filter_by(t_id=tid).all()
            for item in host_items:
                data.append({
                    "hid": item.p_id,
                    "host": item.host,
                    "port": item.port,
                    "hostname": item.hostname,
                    "res": item.res,
                    "date": item.date,
                })
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get host detail failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': 'An error occurred, please try again later'}

