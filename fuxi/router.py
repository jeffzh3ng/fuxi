#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : router.py
# @Desc    : ""

from fuxi import app
from flask_restful import Api
from fuxi.views.blue_views import blue_views
from fuxi.libs.core.data import SecurityModule
from fuxi.apis.auth.access_control import AccessControl
from fuxi.apis.auth.get_token import GetToken, AddAdmin
from fuxi.apis.index.index_api import HelloIndex, WhoAreYou
from fuxi.apis.scanner.poc_scanner import NewPoCScanTask, PocPluginList, \
    PocPluginAction, PocTaskList, PocTaskAction, QuickPocScan, PocVulList, \
    PocVulAction, PocTaskListFilter, PocVulListFilter, PocPluginListFilter
from fuxi.apis.tools.http_req import HttpLogTask, HttpLogAction, HttpLogFilter
from fuxi.apis.tools.json_hijacker import JsonHijackingTask, JsonPhishingData, \
    JsonHijackerAction, JsonHijackerDataAction
from fuxi.apis.tools.xss import NewXssProject, XssProjects, NewXssPayload, XssPayloads, \
    XssPayloadAction, XssProjectAction, XssResultAction

#
from fuxi.apis.discovery.geoip_api import GeoAPI
#
app.register_blueprint(blue_views)
route_rule_list = [
    (AccessControl, "/api/v1/acl"),
    (HelloIndex, "/api/v1/hello"),
    (GetToken, "/api/v1/token"),
    (AddAdmin, "/api/v1/user"),
    (WhoAreYou, "/api/v1/who"),
    (NewPoCScanTask, "/api/v1/scanner/poc/task"),
    (PocTaskList, "/api/v1/scanner/poc/tasks"),
    (PocTaskListFilter, "/api/v1/scanner/poc/tasks/filter"),
    (PocTaskAction, "/api/v1/scanner/poc/task/<tid>"),
    (PocPluginList, "/api/v1/scanner/poc/plugins"),
    (PocPluginListFilter, "/api/v1/scanner/poc/plugins/filter"),
    (PocPluginAction, "/api/v1/scanner/poc/plugin/<pid>"),
    (QuickPocScan, "/api/v1/scanner/poc/scan"),
    (PocVulList, "/api/v1/scanner/poc/vuls"),
    (PocVulListFilter, "/api/v1/scanner/poc/vuls/filter"),
    (PocVulAction, "/api/v1/scanner/poc/vul/<vid>"),
    (HttpLogTask, "/api/v1/tools/xss/httplog"),
    (HttpLogAction, "/api/v1/tools/xss/httplog/<hid>"),
    (HttpLogFilter, "/api/v1/tools/xss/httplog/search"),
    (JsonHijackingTask, "/api/v1/tools/json/task"),
    (JsonPhishingData, "/api/v1/tools/json/data"),
    (JsonHijackerAction, "/api/v1/tools/json/task/<tid>"),
    (JsonHijackerDataAction, "/api/v1/tools/json/data/<vid>"),
    (NewXssProject, "/api/v1/tools/xss/project"),
    (XssProjects, "/api/v1/tools/xss/projects"),
    (NewXssPayload, "/api/v1/tools/xss/payload"),
    (XssPayloads, "/api/v1/tools/xss/payloads"),
    (XssProjectAction, "/api/v1/tools/xss/project/<pid>"),
    (XssPayloadAction, "/api/v1/tools/xss/payload/<pid>"),
    (XssResultAction, "/api/v1/tools/xss/result/<pid>"),
]

api = Api(app)
# 特殊模块单独注册
api.add_resource(GeoAPI, "/api/v1/lib/geoip/<ip>/<language>", "/api/v1/lib/geoip/<ip>")
# 批量注册
for item in route_rule_list:
    api.add_resource(item[0], item[1], endpoint="{}|{}".format(
        item[0].__name__, item[0].desc if 'desc' in dir(item[0]) else "-"
    ))

# # 把所有模块注册到安全模块的权限控制列表中去
for rule in app.url_map.iter_rules():
    for method in list(rule.methods):
        if method not in ['HEAD', 'OPTIONS'] and '/api/' in rule.rule and "blue_views":
            endpoint = rule.endpoint.split("|")
            module = endpoint[0] + '.' + method
            desc = "-" if len(endpoint) == 1 else endpoint[1]
            SecurityModule.ALL_MODULE.append(module)
            if not SecurityModule.MODULE_DESC.__contains__(endpoint[0]):
                SecurityModule.MODULE_DESC[endpoint[0]] = desc
