#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/9/6
# @File    : database_base.py
# @Desc    : ""

from bson import ObjectId
from fuxi.core.databases.db_mongo import mongo


class DatabaseBase:
    def __init__(self):
        self.table = ""

    def find_one(self):
        return mongo[self.table].find_one()

    def find_by_id(self, _id):
        return mongo[self.table].find_one({"_id": ObjectId(str(_id))})

    def get_list(self, limit=1000):
        return mongo[self.table].find().limit(limit)

    def get_count(self, query):
        return mongo[self.table].find(query).count()

    def delete_by_id(self, _id):
        return mongo[self.table].delete_one({"_id": ObjectId(str(_id))})

    def delete_by_tid(self, tid):
        return mongo[self.table].delete_many({"task_id": str(tid)})

    def update_by_id(self, _id, data):
        return mongo[self.table].update_one({"_id": ObjectId(str(_id))}, {"$set": data})

