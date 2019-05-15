#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : index_api.py
# @Desc    : ""

from flask_restful import Resource
from fuxi.libs.common.logger import logger
from fuxi.libs.core.user_info import get_user_info
from fuxi.libs.core.token import access_token


class HelloIndex(Resource):
    @access_token
    def get(self):
        """
        测试用的
        GET /api/v1/hello
        :return:
        """
        try:
            logger.success("req hello index")
            return {'code': 10200, 'status': 'success', 'message': 'ok', 'data': ''}
        except Exception as e:
            logger.error("req hello index failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': str(e)}


class WhoAreYou(Resource):
    desc = "This module will return the current user identity"

    @access_token
    def get(self):
        """
        通过解密 token 获取当前用户存在 token 中的信息
        GET /api/v1/who
        :return: 返回当前访问用户 username nick 等信息
        """
        try:
            data = get_user_info()
            if data['username']:
                return {'code': 10200, 'status': 'success', 'message': 'ok', 'data': data}
            else:
                return {'code': 10401, 'status': 'success', 'message': 'Signature expired'}, 401
        except Exception as e:
            logger.error("get user info failed: {}".format(e))
