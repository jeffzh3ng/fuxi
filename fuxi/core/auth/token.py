#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/7/5
# @File    : token.py
# @Desc    : ""

from functools import wraps
from flask import request, session
from fuxi.web.flask_app import flask_app
from fuxi.common.utils.logger import logger
from fuxi.core.databases.orm.auth.user_orm import DBFuxiAdmin
from fuxi.core.data.response import Response, StatusCode


def auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not flask_app.config.get("AUTH"):
            session['user'] = "guest"
            session['nick'] = "guest"
            session['email'] = "guest@fuxi.com"
            session['authority'] = 0
            return func(*args, **kwargs)
        token = request.headers.get('token')
        if not token:
            token = request.args.get('token')
        if not token:
            token = request.form.get('token')
        if not token:
            return Response.failed(StatusCode.AUTH_FAILED)
        try:
            item = DBFuxiAdmin.token_check(token)
            if item:
                session['user'] = item['username']
                session['authority'] = item['role']
                session['nick'] = item['nick']
                session['email'] = item['email']
                session['date'] = item['date']
                return func(*args, **kwargs)
            else:
                return Response.failed(StatusCode.AUTH_FAILED)
        except Exception as e:
            logger.warning("unknown error: auth token {}".format(e))
            return Response.failed()
    return wrapper
