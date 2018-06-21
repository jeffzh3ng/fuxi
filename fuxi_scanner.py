#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-5-9
# @File    : fuxi.py
# @Desc    : ""

import threading
from flask import Flask
from fuxi.app import app
from gevent.pywsgi import WSGIServer
from fuxi.views.modules.scanner.poc_scanner import PoCScannerLoop
from fuxi.views.modules.auth_tester.auth_scanner import AuthTesterLoop
from fuxi.views.modules.discovery.asset_discovery import DiscoveryLoop
from instance import config

ProductionConfig = config.ProductionConfig
flask_app = Flask(__name__)
flask_app.config.from_object(ProductionConfig)
host = flask_app.config.get('WEB_HOST')
port = flask_app.config.get('WEB_PORT')
thread_pool = []


def web_server():
    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()


def scanner_loop():
    PoCScannerLoop().task_schedule()


def auth_tester_loop():
    AuthTesterLoop().task_schedule()


def discovery_loop():
    DiscoveryLoop().task_schedule()


if __name__ == '__main__':
    print("* Running on http://" + host + ":" + str(port))
    thread_pool.append(threading.Thread(target=web_server, args=()))
    thread_pool.append(threading.Thread(target=scanner_loop, args=()))
    thread_pool.append(threading.Thread(target=auth_tester_loop, args=()))
    thread_pool.append(threading.Thread(target=discovery_loop, args=()))
    try:
        for t in thread_pool:
            t.start()
        for t in thread_pool:
            t.join()
    except Exception as e:
        print(e)


