#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : manage.py
# @Desc    : ""

from fuxi.apis.router import app

if __name__ == '__main__':
    host = app.config.get('SERVER_HOST')
    port = int(app.config.get('SERVER_PORT'))
    app.run(host, port)
