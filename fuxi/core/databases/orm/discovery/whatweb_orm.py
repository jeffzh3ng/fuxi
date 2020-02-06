#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/01/11
# @File    : whatweb_orm.py 
# @Desc    : ""

import time
from flask import session
from fuxi.core.databases.db_error import DatabaseError
from fuxi.core.databases.orm.database_base import DatabaseBase
from fuxi.core.databases.db_mongo import mongo, T_WEB_FP, T_WHATWEB_TASK
from fuxi.common.utils.logger import logger


class _DBWhatwebTask(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_WHATWEB_TASK

    def add(self, name, target, level, threads, plugin, option, header, cookie):
        op = session.get('user')
        if target and op:
            inserted_id = mongo[self.table].insert_one({
                "op": op, "date": int(time.time()),  "end_date": 0, "status": "waiting",
                "name": name, "target": target, "level": level, "threads": threads, "plugin": plugin,
                "option": option, "header": header, "cookie": cookie
            }).inserted_id
            return str(inserted_id)
        else:
            logger.warning("insert failed: invalid data")
            raise DatabaseError("invalid data")


class _DBWebFingerPrint(DatabaseBase):
    """
    :parameter
    domain [string]
    http_status [int]
    title [string]
    country [string]
    c_code [string]
    ip [string]
    summary [string]
    request [dict]
    fingerprint [list[dict]] [{"plugin": "", "string": ""}]
    """
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_WEB_FP

    def add(self, target, http_status, title, country, c_code, ip, summary, request, fingerprint):
        pass
        # op = session.get('user')
        # if target and http_status and op:
        #     inserted_id = mongo[self.table].insert_one({
        #         "op": op, "date": int(time.time()),
        #         "target": target, "http_status": http_status, "title": title, "country": country,
        #         "c_code": c_code, "ip": ip, "summary": summary, "request": request,
        #         "fingerprint": fingerprint
        #     }).inserted_id
        #     return str(inserted_id)
        # else:
        #     logger.warning("insert failed: invalid data")
        #     raise DatabaseError("invalid data")

    def add_multiple(self, data):
        d = []
        for item in data:
            if item.get("task_id") and item.get("target"):
                task_id = item.get("task_id")
                target = item.get("target")
                http_status = item.get("http_status")
                title = item.get("title")
                country = item.get("country")
                c_code = item.get("c_code")
                ip = item.get("ip")
                summary = item.get("summary")
                request = item.get("request")
                fingerprint = item.get("fingerprint")
            else:
                continue
            d.append({
                "date": int(time.time()), "task_id": task_id,
                "target": target, "http_status": http_status, "title": title, "country": country,
                "c_code": c_code, "ip": ip, "summary": summary, "request": request,
                "fingerprint": fingerprint
            })
        if d:
            x = mongo[self.table].insert_many(d)
            return [str(i) for i in x.inserted_ids]
        else:
            return []

    def search(self, keyword):
        keyword = keyword.lower()
        return mongo[self.table].find({
            "$or": [
                {"target": {'$regex': keyword, '$options': 'i'}}, {"title": {'$regex': keyword, '$options': 'i'}},
                {"country": {'$regex': keyword, '$options': 'i'}}, {"ip": {'$regex': keyword, '$options': 'i'}},
                {"summary": {'$regex': keyword, '$options': 'i'}},
                {"fingerprint.plugin": {'$regex': keyword, '$options': 'i'}},
            ]
        })


DBWhatwebTask = _DBWhatwebTask()
DBWebFingerPrint = _DBWebFingerPrint()
