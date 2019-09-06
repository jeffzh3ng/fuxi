#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/7/6
# @File    : pocsuite.py
# @Desc    : ""

import time
from bson import ObjectId
from fuxi.core.databases.orm.database_base import DatabaseBase
from fuxi.core.databases.db_mongo import mongo, T_POC_PLUGINS, T_POC_TASKS, T_POC_VULS
from fuxi.common.utils.logger import logger
from fuxi.core.databases.db_error import DatabaseError


class _DBPocsuitePlugin(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_POC_PLUGINS

    def get_detail_by_id(self, _id):
        return mongo[self.table].find_one({"_id": ObjectId(str(_id))})

    def get_list(self, query=None, data_filter=None):
        return mongo[self.table].find(query, data_filter)

    def add(self, name, poc_str, filename, op, app=None, poc_type=None):
        if name and poc_str and filename:
            inserted_id = mongo[self.table].insert_one({
                "name": name.strip(), "poc": poc_str, "app": app,
                "type": poc_type, "filename": filename,
                "date": int(time.time()), "op": op
            }).inserted_id
            return str(inserted_id)
        else:
            logger.error("pocsuite plugin insert failed: invalid data")
            raise DatabaseError("invalid data")

    def filter_by_keyword(self, keyword):
        keyword = keyword.lower()
        return mongo[self.table].find({
            "$or": [
                {"name": {'$regex': keyword}}, {"app": {'$regex': keyword}},
                {"type": {'$regex': keyword}}, {"filename": {'$regex': keyword}},
            ]
        })


class _DBPocsuiteTask(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_POC_TASKS

    def get_detail_by_id(self, _id):
        return mongo[self.table].find_one({"_id": ObjectId(str(_id))})

    def get_list(self, query=None, data_filter=None):
        return mongo[self.table].find(query, data_filter)

    def add(self, name, target, poc, thread, freq, op):
        if name and target and poc and thread and freq:
            inserted_id = mongo[self.table].insert_one({
                "name": name.strip(), "target": target, "poc": poc,
                "thread": thread, "freq": freq,
                "date": int(time.time()), "end_date": 0,
                "status": "waiting", "vul_count": 0, "op": str(op)
            }).inserted_id
            return str(inserted_id)
        else:
            logger.error("pocsuite task insert failed: invalid data")
            raise DatabaseError("invalid data")

    def update_by_id(self, tid, data):
        return mongo[self.table].update_one(
            {"_id": ObjectId(tid)}, {"$set": data}
        )

    def filter_by_keyword(self, keyword):
        keyword = keyword.lower()
        return mongo[self.table].find({
            "$or": [
                {"name": {'$regex': keyword}}, {"poc": {'$regex': keyword}},
                {"target": {'$regex': keyword}}, {"freq": {'$regex': keyword}},
                {"status": {'$regex': keyword}},
            ]
        })


class _DBPocsuiteVul(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_POC_VULS

    def get_detail_by_id(self, _id):
        return mongo[self.table].find_one({"_id": ObjectId(str(_id))})

    def get_list(self, query=None, data_filter=None):
        return mongo[self.table].find(query, data_filter)

    def add(self, tid, poc, task_name, poc_name, status, target, app, op, result=""):
        if tid and poc and task_name and poc_name and status and target and app:
            inserted_id = mongo[self.table].insert_one({
                "tid": tid, "poc": poc, "task_name": task_name,
                "poc_name": poc_name, "status": status,
                "target": target, "app": app, "result": result,
                "date": int(time.time()), "op": op
            }).inserted_id
            return str(inserted_id)
        else:
            logger.error("pocsuite scan result insert failed: invalid data")
            raise DatabaseError("invalid data")

    def update_by_id(self, tid, data):
        return mongo[self.table].update_one(
            {"_id": ObjectId(tid)}, {"$set": data}
        )

    def filter_by_tid(self, tid):
        return mongo[self.table].find({"tid": tid})

    def filter_by_plugin(self, plugin_id):
        return mongo[self.table].find({"poc": plugin_id})

    def filter_by_keyword(self, keyword):
        keyword = keyword.lower()
        return mongo[self.table].find({
            "$or": [
                {"task_name": {'$regex': keyword}}, {"poc_name": {'$regex': keyword}},
                {"target": {'$regex': keyword}}, {"result": {'$regex': keyword}},
                {"app": {'$regex': keyword}}, {"status": {'$regex': keyword}},
            ]
        })

    def filter_by_keyword_and_task(self, task_id, keyword):
        keyword = keyword.lower()
        return mongo[self.table].find({
            "tid": task_id,
            "$or": [
                {"task_name": {'$regex': keyword}}, {"poc_name": {'$regex': keyword}},
                {"target": {'$regex': keyword}}, {"result": {'$regex': keyword}},
                {"app": {'$regex': keyword}}, {"status": {'$regex': keyword}},
            ]
        })

    def filter_by_keyword_and_plugin(self, plugin_id, keyword):
        keyword = keyword.lower()
        return mongo[self.table].find({
            "poc": plugin_id,
            "$or": [
                {"task_name": {'$regex': keyword}}, {"poc_name": {'$regex': keyword}},
                {"target": {'$regex': keyword}}, {"result": {'$regex': keyword}},
                {"app": {'$regex': keyword}}, {"status": {'$regex': keyword}},
            ]
        })


DBPocsuitePlugin = _DBPocsuitePlugin()
DBPocsuiteTask = _DBPocsuiteTask()
DBPocsuiteVul = _DBPocsuiteVul()

