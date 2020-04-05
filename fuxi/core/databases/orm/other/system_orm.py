#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/4/5
# @File    : system.py
# @Desc    : ""

import time
from fuxi.core.databases.orm.database_base import DatabaseBase
from fuxi.core.databases.db_mongo import mongo, T_SYSTEM_INFO


class _DBHSystemInfo(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_SYSTEM_INFO

    def add(self, data):
        date = int(time.time()) - 24*60*60*2
        data['date'] = date
        inserted_id = mongo[self.table].insert_one(data).inserted_id
        return inserted_id


DBHSystemInfo = _DBHSystemInfo()
