#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/9/6
# @File    : port_orm.py
# @Desc    : ""

import time

from bson import ObjectId
from flask import session
from fuxi.core.databases.db_error import DatabaseError
from fuxi.core.databases.orm.database_base import DatabaseBase
from fuxi.core.databases.db_mongo import mongo, T_PORT_TASKS, T_PORT_RESULT
from fuxi.common.utils.logger import logger


class _DBPortScanTasks(DatabaseBase):
    """
    :parameter
    name:
    target:
    port:
    option:
    op:
    status:
    date:
    end_date:
    """

    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_PORT_TASKS

    def add(self, name, target, port, option):
        op = session.get('user')
        if name and target and op:
            inserted_id = mongo[self.table].insert_one({
                "name": name.strip(), "target": target, "port": port, "option": option,
                "op": op, "status": "waiting", "date": int(time.time()), "end_date": 0
            }).inserted_id
            return str(inserted_id)
        else:
            logger.warning("port scan task insert failed: invalid data")
            raise DatabaseError("invalid data")

    def search(self, keyword):
        keyword = keyword.lower()
        return mongo[self.table].find({
            "$or": [
                {"name": {'$regex': keyword}}, {"target": {'$regex': keyword}},
                {"date": {'$regex': keyword}}, {"option": {'$regex': keyword}},
                {"status": {'$regex': keyword}}, {"op": {'$regex': keyword}},
            ]
        })

    def update_celery_id(self, task_id, celery_id):
        return mongo[self.table].update_one(
            {"_id": ObjectId(task_id)}, {"$set": {"celery_id": str(celery_id)}}
        )


class _DBPortScanResult(DatabaseBase):
    """
    :parameter
    """

    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_PORT_RESULT

    def get_list_by_tid(self, tid):
        return mongo[self.table].find({"task_id": str(tid)})

    def add(self, task_id, host, hostname, port, detail):
        inserted_id = mongo[self.table].insert_one({
            "task_id": task_id, "host": host, "hostname": hostname, "port": port,
            "detail": detail, "date": int(time.time())
        }).inserted_id
        return str(inserted_id)

    def add_multiple(self, result):
        data = []
        for item in result:
            if item.get("task_id") and item.get("host"):
                task_id = item.get("task_id")
                host = item.get("host")
                port = item.get("port")
                port_detail = item.get("detail")
            else:
                continue
            data.append({
                "task_id": task_id, "host": host, "hostname": item.get("hostname"),
                "port": port, "detail": port_detail, "date": int(time.time())
            })
        if data:
            x = mongo[self.table].insert_many(data)
            return [str(i) for i in x.inserted_ids]
        else:
            return []

    def delete_by_tid(self, tid):
        return mongo[self.table].delete_many({"task_id": str(tid)})

    def search(self, tid, keyword):
        keyword = keyword.lower()
        return mongo[self.table].find({
            "task_id": tid,
            "$or": [
                {"host": {'$regex': keyword}}, {"hostname": {'$regex': keyword}},
                {"port": {'$regex': keyword}}, {"detail.detail.name": {'$regex': keyword}}
            ]
        })


DBPortScanTasks = _DBPortScanTasks()
DBPortScanResult = _DBPortScanResult()

