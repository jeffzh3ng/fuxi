#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/7/5
# @File    : token.py
# @Desc    : ""

from flask import request
from functools import wraps
from fuxi.web.flask_app import flask_app
from fuxi.common.utils.logger import logger
from fuxi.core.databases.orm.user import DBFuxiAdmin
from fuxi.core.data.response import Response, StatusCode


def auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not flask_app.config.get("AUTH"):
            return func(*args, **kwargs)
        token = request.headers.get('token')
        if not token:
            token = request.args.get('token')
        if not token:
            token = request.form.get('token')
        if not token:
            return Response.failed(StatusCode.AUTH_FAILED)
        try:
            if DBFuxiAdmin.token_check(token):
                return func(*args, **kwargs)
            else:
                return Response.failed(StatusCode.AUTH_FAILED)
        except Exception as e:
            logger.warning("auth token unknown error: {}".format(e))
            return Response.failed()
    return wrapper
