#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/4/4
# @File    : sqlmap_orm.py
# @Desc    : ""

import time
from flask import session
from fuxi.core.databases.orm.database_base import DatabaseBase
from fuxi.core.databases.db_mongo import mongo, T_SQLMAP_TASKS, T_SQLMAP_RESULT
from fuxi.common.utils.logger import logger
from fuxi.core.databases.db_error import DatabaseError


class _DBSqlmapTask(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_SQLMAP_TASKS

    def add(self, name, target, method, body, level, threads, timeout, cookie, headers, db_banner):
        op = session.get('user')
        if name and target and method and level and threads:
            inserted_id = mongo[self.table].insert_one({
                "name": name.strip(), "target": target, "method": method, "level": level,
                "threads": threads, "timeout": timeout,
                "body": body, "cookie": cookie, "headers": headers, "db_banner": db_banner,
                "date": int(time.time()), "end_date": 0,
                "status": "waiting", "op": str(op)
            }).inserted_id
            return str(inserted_id)
        else:
            logger.warning("sqlmap task insert failed: invalid data")
            raise DatabaseError("invalid data")


class _DBSqlmapResult(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_SQLMAP_RESULT

    def filter_by_tid(self, tid):
        return mongo[self.table].find({"task_id": tid})

    def add_multiple(self, result):
        data = []
        for item in result:
            if item.get("task_id") and item.get("target") and item.get("sqlmap_tid") and item.get("method"):
                task_id = item.get("task_id")
                target = item.get("target")
                sqlmap_tid = item.get("sqlmap_tid")
                method = item.get("method")
            else:
                continue
            data.append({
                "task_id": task_id, "target": target, "sqlmap_tid": sqlmap_tid,
                "method": method,
                "body": item.get("body") if item.get("body") else "",
                "result": item.get("result"),
                "dbms": item.get("dbms"),
                "dbms_version": item.get("dbms_version"),
                "os": item.get("os"),
                "payload": item.get("payload"),
                "parameter": item.get("parameter"),
                "place": item.get("place"),
                "date": int(time.time())
            })
        if data:
            x = mongo[self.table].insert_many(data)
            return [str(i) for i in x.inserted_ids]
        else:
            return []

    def update_by_sqlmap_id(self, sqlmap_id, data):
        return mongo[self.table].update_one({"sqlmap_id": sqlmap_id}, {"$set": data})


DBSqlmapTask = _DBSqlmapTask()
DBSqlmapResult = _DBSqlmapResult()
