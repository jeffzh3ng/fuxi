#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/3/2
# @File    : database.py
# @Desc    : ""

from fuxi.web.flask_app import flask_app
from flask_pymongo import PyMongo

mongo = PyMongo(flask_app).db

T_ADMIN = "fuxi_admin_v1"
T_POC_TASKS = "poc_tasks"
T_POC_PLUGINS = "poc_plugins"
T_POC_VULS = "poc_vuls"

T_HTTP_REQUEST_LOG = "http_req"
T_JSON_HIJACKER_TASK = 'json_hijacker_task'
T_JSON_HIJACKER_RES = 'json_hijacker_res'
T_XSS_TASKS = 'xss_tasks'
T_XSS_PAYLOADS = 'xss_payloads'
T_XSS_RES = 'xss_res'

T_PORT_TASKS = 'port_scan_tasks'

