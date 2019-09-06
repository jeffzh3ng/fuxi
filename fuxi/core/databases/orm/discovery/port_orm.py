#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/9/6
# @File    : port_orm.py
# @Desc    : ""

import time
from fuxi.core.databases.db_error import DatabaseError
from fuxi.core.databases.orm.database_base import DatabaseBase
from fuxi.core.databases.db_mongo import mongo, T_PORT_TASKS
from fuxi.common.utils.logger import logger


class _DBPortScanTasks(DatabaseBase):
    def __init__(self):
        DatabaseBase.__init__(self)
        self.table = T_PORT_TASKS

    def add(self, name, target, port, threat, args, op):
        if name and target and port and threat and op:
            inserted_id = mongo[self.table].insert_one({
                "name": name.strip(), "target": target, "port": port, "args": args,
                "threat": threat, "op": op, "status": "waiting", "date": int(time.time())
            }).inserted_id
            return str(inserted_id)
        else:
            logger.warning("port scan task insert failed: invalid data")
            raise DatabaseError("invalid data")


DBPortScanTasks = _DBPortScanTasks()
