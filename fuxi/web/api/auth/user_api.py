#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/7/6
# @File    : user_api.py
# @Desc    : ""

from flask import request
from flask_restful import Resource
from fuxi.common.utils.logger import logger
from fuxi.core.databases.orm.user import DBFuxiAdmin
from fuxi.core.data.response import Response, StatusCode


class WhoAreYouV1(Resource):
    @staticmethod
    def get():
        """
        GET /api/v1/who
        :return: 返回当前访问用户 username nick 等信息
        """
        data = {"username": "guest", "nick": "Guest", "email": "guest@fuxi.com"}
        try:
            token = request.headers.get('token')
            if not token:
                token = request.args.get('token')
            if not token:
                token = request.form.get('token')
            if not token:
                return Response.failed(StatusCode.AUTH_FAILED, data=data)
            _item = DBFuxiAdmin.get_user_info_by_token(token)
            data['username'] = _item['username']
            data['nick'] = _item['nick']
            data['email'] = _item['email']
            return Response.success(data=data)
        except Exception as e:
            logger.warning("get user info failed: {}".format(e))
            return Response.failed(message=e, data=data)
