#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : token.py
# @Desc    : ""


from functools import wraps
from flask import request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from fuxi import app
from fuxi.libs.data.error import AUTH_FAILED_INVALID_SESSION, API_FAILED
from fuxi.libs.common.logger import logger


def access_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not app.config.get("AUTH"):
            return func(*args, **kwargs)
        if 'Access-Token' not in request.headers:
            return {'code': 10401, 'status': 'failed', 'message': AUTH_FAILED_INVALID_SESSION}
        token = request.headers['Access-Token']
        s = Serializer(app.config.get('SECRET_KEY'))
        try:
            data = s.loads(token)
            if data:
                return func(*args, **kwargs)
        except SignatureExpired:
            logger.info("{} token expired".format(request.remote_addr))
            return {'code': 10401, 'status': 'failed', 'message': 'Expired token', 'data': ''}
        except BadSignature:
            logger.info("{} token useless".format(request.remote_addr))
            return {'code': 10401, 'status': 'failed', 'message': 'Useless token', 'data': ''}
        except Exception as e:
            logger.info("access token unknown error: {}".format(e))
            return {'code': 10401, 'status': 'failed', 'message': API_FAILED}
    return wrapper
