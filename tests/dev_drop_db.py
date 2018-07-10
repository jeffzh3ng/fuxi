#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-7-10
# @File    : dev_drop_db.py
# @Desc    : "Drop all databases"

import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from fuxi.views.lib.mongo_db import connectiondb, db_name_conf


def drop_database(db_name):
    result = connectiondb(db_name).remove()
    print("[*] Drop database: %s %s" % (db_name, result))


if __name__ == '__main__':
    ask = raw_input('Are you sure you want to delete (yes/no): ')
    if ask == 'yes':
        for key in db_name_conf():
            drop_database(db_name_conf()[key])
        print("[*] Successfully deleted, Please initialize the configuration database (python migration/db_init.py)")
