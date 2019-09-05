#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/7/5
# @File    : flask_app.py
# @Desc    : ""

import sys
from flask import Flask
from celery import Celery
from flask_cors import CORS
from secrets import token_urlsafe
from instance.config import config
from fuxi.common.utils.logger import logger


def create_app(config_name):
    try:
        _app = Flask(__name__, static_folder="../../dist/", static_url_path='', template_folder="../../dist")
        _app.config.from_object(config[config_name])
        _app.config['CELERY_BROKER_URL'] = "redis://{}:{}/{}".format(
            _app.config.get("REDIS_HOST"), _app.config.get("REDIS_PORT"), _app.config.get("REDIS_DB"),
            )
        _app.config['MONGO_URI'] = "mongodb://{}:{}/{}".format(
            _app.config.get("MONGO_HOST"), _app.config.get("MONGO_PORT"), _app.config.get("MONGO_DB"),
            )
        _app.config['SECRET_KEY'] = token_urlsafe()
        CORS(_app, supports_credentials=True)
        return _app
    except Exception as e:
        logger.error("create flask app error: {}".format(e))
        sys.exit(0)


flask_app = create_app('dev')
fuxi_celery = Celery(flask_app.name, broker=flask_app.config['CELERY_BROKER_URL'])
fuxi_celery.conf.update(flask_app.config)
flask_app.app_context().push()
