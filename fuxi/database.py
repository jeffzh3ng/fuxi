#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/3/2
# @File    : database.py
# @Desc    : ""

from fuxi import app
from flask_pymongo import PyMongo

mongo = PyMongo(app)


class MongoDB:
    def __init__(self, db_name):
        self.db_name = db_name

    def insert_one(self, data):
        return mongo.db[self.db_name].insert_one(data).inserted_id

    def insert(self, data):
        return mongo.db[self.db_name].insert(data)

    def find(self, query=None, _filter=None):
        return mongo.db[self.db_name].find(query, _filter)

    def find_one(self, query=None, _filter=None):
        return mongo.db[self.db_name].find_one(query, _filter)

    def delete_one(self, query=None):
        return mongo.db[self.db_name].delete_one(query)

    def delete_many(self, query):
        return mongo.db[self.db_name].delete_many(query)

    def update_one(self, query=None, new_values=None):
        return mongo.db[self.db_name].update_one(query, {"$set": new_values})

    def update_many(self, query=None, new_values=None):
        return mongo.db[self.db_name].update_many(query, {"$set": new_values})


T_ADMIN = "fuxi_admin"
T_POC_TASKS = "poc_tasks"
T_POC_PLUGINS = "poc_plugins"
T_POC_VULS = "poc_vuls"

T_HTTP_REQUESTS = "http_req"
T_JSON_HIJACKER_TASK = 'json_hijacker_task'
T_JSON_HIJACKER_RES = 'json_hijacker_res'
T_XSS_PROJECTS = 'xss_projects'
T_XSS_PAYLOADS = 'xss_payloads'
T_XSS_RES = 'xss_res'

T_PORT_TASKS = 'port_scan_tasks'

