#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/24
# @File    : access_control.py
# @Desc    : ""

from flask_restful import Resource
from fuxi.libs.core.token import access_token
from fuxi.libs.common.logger import logger
from fuxi.libs.core.data import SecurityModule


class AccessControl(Resource):
    desc = "Access control module"

    @access_token
    def get(self):
        try:
            data = {
                "all": SecurityModule.ALL_MODULE,
                "white": SecurityModule.WHITE_MODULE,
                "desc": SecurityModule.MODULE_DESC
            }
            return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
        except Exception as e:
            logger.error("get SecurityModule failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': 'get SecurityModule failed'}
