#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/3/2
# @File    : database.py
# @Desc    : ""

from fuxi.web.flask_app import flask_app
from flask_pymongo import PyMongo

mongo = PyMongo(flask_app).db

T_TESTS = "fuxi_tests"

T_CONFIG = "fuxi_configuration"
T_SYSTEM_INFO = "fuxi_system_info"

T_ADMIN = "fuxi_admin_v1"
T_POC_TASKS = "poc_tasks"
T_POC_PLUGINS = "poc_plugins"
T_POC_VULS = "poc_vuls"
T_SQLMAP_TASKS = "sqlmap_tasks"
T_SQLMAP_RESULT = "sqlmap_result"

T_HTTP_REQUEST_LOG = "http_req"
T_JSON_HIJACKER_TASK = 'json_hijacker_task'
T_JSON_HIJACKER_RES = 'json_hijacker_res'
T_XSS_TASKS = 'xss_tasks'
T_XSS_PAYLOADS = 'xss_payloads'
T_XSS_RES = 'xss_res'

T_PORT_TASKS = 'port_scan_tasks'
T_PORT_RESULT = 'port_scan_result'
T_WHATWEB_TASK = 'whatweb_tasks'
T_WEB_FP = 'web_fingerprint'
T_SUBDOMAIN_TASK = 'subdomain_tasks'
T_SUBDOMAIN_RESULT = 'subdomain_result'
