#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : router.py
# @Desc    : ""

from flask_restful import Api
from fuxi.web.flask_app import flask_app

from migration.db_init import databases_init
from fuxi.web.views.blue_view import blue_view

from fuxi.web.api.demo.demo_api import HelloIndex
from fuxi.web.api.auth.access_auth_api import UserManageV1, TokenManageV1
from fuxi.web.api.auth.user_api import WhoAreYouV1
from fuxi.web.api.scanner.poc_scanner import PocsuiteTasksV1, \
    PocsuitePluginsV1, PocsuiteTaskManageV1, PocsuitePluginManageV1, \
    PocsuiteResultsV1, PocsuiteResultManageV1

flask_app.register_blueprint(blue_view)
api = Api(flask_app)
api.add_resource(HelloIndex, "/api/v1/hello", "/api/v1/demo")
api.add_resource(WhoAreYouV1, "/api/v1/who")
api.add_resource(UserManageV1, "/api/v1/admin")
api.add_resource(TokenManageV1, "/api/v1/token")
api.add_resource(PocsuiteTasksV1, "/api/v1/scanner/poc/task")
api.add_resource(PocsuiteTaskManageV1, "/api/v1/scanner/poc/task/<tid>")
api.add_resource(PocsuitePluginsV1, "/api/v1/scanner/poc/plugin")
api.add_resource(PocsuitePluginManageV1, "/api/v1/scanner/poc/plugin/<plugin_id>")
api.add_resource(PocsuiteResultsV1, "/api/v1/scanner/poc/vul")
api.add_resource(PocsuiteResultManageV1, "/api/v1/scanner/poc/vul/<vul_id>")

# Databases init
databases_init()
