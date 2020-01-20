#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/01/15
# @File    : config.py 
# @Desc    : ""

import time
from fuxi.core.databases.db_error import DatabaseError
from fuxi.core.databases.orm.database_base import DatabaseBase
from fuxi.core.databases.db_mongo import mongo, T_CONFIG
from fuxi.common.utils.logger import logger


class _DBFuxiConfiguration(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_CONFIG

    def config_init(self):
        inserted_id = mongo[self.table].insert_one({
            "whatweb_exe": "", "nmap_exe": "",
            "date": int(time.time())
        }).inserted_id
        return str(inserted_id)

    def get_config(self, key):
        item = mongo[self.table].find_one()
        if item and item.get(key):
            return item[key]
        else:
            return ""

    def setting_item_check(self, key):
        return mongo[self.table].find_one({key: {"$exists": True}})


DBFuxiConfiguration = _DBFuxiConfiguration()
