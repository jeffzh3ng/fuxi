#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : __init__.py.py
# @Desc    : ""

import sys
from flask import Flask
from flask_cors import CORS
from secrets import token_urlsafe
from celery import Celery
from instance.config import config


def create_app(config_name):
    try:
        _app = Flask(__name__, static_folder="../dist/", static_url_path='', template_folder="../dist")
        _app.config.from_object(config[config_name])
        _app.config['CELERY_BROKER_URL'] = "redis://{}:{}/{}".format(
            _app.config.get("REDIS_HOST"), _app.config.get("REDIS_PORT"), _app.config.get("REDIS_DB"),
            )
        _app.config['MONGO_URI'] = "mongodb://{}:{}/{}".format(
            _app.config.get("MONGO_HOST"), _app.config.get("MONGO_PORT"), _app.config.get("MONGO_DB"),
            )
        if config_name == "prod":
            _app.config['SECRET_KEY'] = token_urlsafe()
        CORS(_app, supports_credentials=True)
        return _app
    except Exception as e:
        print("create flask app error: {}".format(e))
        sys.exit(0)


app = create_app('dev')
fuxi_celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
fuxi_celery.conf.update(app.config)
app.app_context().push()
