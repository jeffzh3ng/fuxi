#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : manage.py
# @Desc    : ""

from fuxi.web.router import flask_app

if __name__ == '__main__':
    flask_app.run(
        host=flask_app.config.get('SERVER_HOST'),
        port=int(flask_app.config.get('SERVER_PORT'))
    )
