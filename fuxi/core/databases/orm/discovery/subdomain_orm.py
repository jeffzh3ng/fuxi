#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/3/21
# @File    : subdomain_orm.py
# @Desc    : ""

import time

from bson import ObjectId
from flask import session
from fuxi.core.databases.db_error import DatabaseError
from fuxi.core.databases.orm.database_base import DatabaseBase
from fuxi.core.databases.db_mongo import mongo, T_SUBDOMAIN_TASK, T_SUBDOMAIN_RESULT
from fuxi.common.utils.logger import logger


class _DBSubdomainTask(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_SUBDOMAIN_TASK

    def add(self, name, target, brute, info, threads):
        op = session.get('user')
        if target and op:
            inserted_id = mongo[self.table].insert_one({
                "op": op, "date": int(time.time()),  "end_date": 0, "status": "waiting",
                "name": name, "target": target, "brute": brute, "info": info, "threads": threads,
            }).inserted_id
            return str(inserted_id)
        else:
            logger.warning("insert failed: invalid data")
            raise DatabaseError("invalid data")

    def update_celery_id(self, task_id, celery_id):
        return mongo[self.table].update_one(
            {"_id": ObjectId(task_id)}, {"$set": {"celery_id": str(celery_id)}}
        )


class _DBSubdomainResult(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_SUBDOMAIN_RESULT

    def get_list_by_tid(self, tid):
        return mongo[self.table].find({"task_id": str(tid)})

    def get_count_by_tid(self, tid):
        return mongo[self.table].find({"task_id": str(tid)}).count()

    def add_multiple(self, data):
        d = []
        for item in data:
            item['date'] = int(time.time())
            d.append(item)
        if d:
            x = mongo[self.table].insert_many(d)
            return [str(i) for i in x.inserted_ids]
        else:
            return []

    def update_web_info(self, subdomain, data):
        return mongo[self.table].update_many({"subdomain": subdomain}, {"$set": data})
        # return mongo[self.table].update_one(query, {"$set": data})


DBSubdomainTask = _DBSubdomainTask()
DBSubdomainResult = _DBSubdomainResult()
