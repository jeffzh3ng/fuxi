#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/22
# @File    : config.py.py
# @Desc    : ""

import os

LOGGER_PATH = os.path.abspath(os.path.dirname(__file__)) + '/../logs/'


class BaseConfig(object):
    # Base configuration
    DEBUG = False
    AUTH = True
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 50020
    SECRET_KEY = 'B10ySw1nPL8JBo6z'


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    AUTH = False
    # Redis configuration
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = ""
    REDIS_PASSWORD = ""
    REDIS_DB = 0
    # MongoDB configuration
    MONGO_HOST = '127.0.0.1'
    MONGO_PORT = 27017
    MONGO_DB = 'fuxi_dev'


class ProductionConfig(BaseConfig):
    """docstring for ProductionConfig"""
    # Base configuration
    pass


config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
