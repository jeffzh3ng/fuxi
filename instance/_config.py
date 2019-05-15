#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/22
# @File    : config.py.py
# @Desc    : ""

import os


class BaseConfig(object):
    # Base configuration
    DEBUG = False
    AUTH = True
    SECRET_KEY = 'B10ySw1nPL8JBo6z'
    LOGGER_PATH = os.path.abspath(os.path.dirname(__file__)) + '/../logs/'


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    AUTH = False
    # Redis configuration
    REDIS_HOST = ""
    REDIS_PORT = ""
    REDIS_PASSWORD = ""
    REDIS_DB = 0
    # MongoDB configuration
    MONGO_HOST = ''
    MONGO_PORT = 0
    MONGO_DB = ''


class ProductionConfig(BaseConfig):
    """docstring for ProductionConfig"""
    # Base configuration
    pass


config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
