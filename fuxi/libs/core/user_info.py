#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : user_info.py
# @Desc    : ""

from flask import request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from fuxi import app
from fuxi.libs.common.logger import logger


def get_user_info():
    user_info_data = {'username': '', 'nick': '', 'email': '', 'authority': []}
    try:
        token = request.headers['Access-Token']
        s = Serializer(app.config.get('SECRET_KEY'))
        _data = s.loads(token)
        user_info_data['username'] = _data['username']
        user_info_data['nick'] = _data['nick']
        user_info_data['email'] = _data['email']
        user_info_data['authority'] = _data['authority']
        return user_info_data
    except Exception as e:
        logger.error("token decode failed: {}".format(e))
        return user_info_data
