#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-5-10
# @File    : config.py
# @Desc    : ""

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    def __init__(self):
        pass

    WEB_USER = 'admin'  # Web Auth User
    WEB_PASSWORD = 'whoami'  # Web Auth Password
    POCSUITE_PATH = basedir + '/../fuxi/views/modules/scanner/pocsuite_plugin/'
    AWVS_REPORT_PATH = basedir + '/../fuxi/static/download/'  # static file download
    WEB_HOST = '127.0.0.1'  # Web Server Host
    WEB_PORT = 5000  # Web Server Port
    UPDATE_URL = "https://fuxi.hook.ga/update"  # check update
    VERSION = '1.2.0'  # scanner version
    AWVS_URL = 'https://192.168.56.2:3443'  # Acunetix Web Vulnerability Scanner Url
    AWVS_API_KEY = ""  # Acunetix Web Vulnerability Scanner API Key


class ProductionConfig(Config):
    DB_HOST = '127.0.0.1'  # MongoDB Host
    DB_PORT = 27017  # MongoDB Port (int)
    DB_NAME = 'fuxi'  # MongoDB Name
    DB_USERNAME = 'fuxi_scanner'  # MongoDB User
    DB_PASSWORD = 'W94MRYDqOZ'  # MongoDB Password

    CONFIG_NAME = 'fuxi'  # Scanner config name
    PLUGIN_DB = 'dev_plugin_info'  # Plugin collection
    TASKS_DB = 'dev_tasks'  # Scan tasks collection
    VULNERABILITY_DB = 'dev_vuldb'  # Vulnerability collection
    ASSET_DB = 'dev_asset'  # Asset collection
    CONFIG_DB = 'dev_config'  # Scanner config collection
    SERVER_DB = 'dev_server'  # Asset server collection
    SUBDOMAIN_DB = 'dev_subdomain'  # Subdomain server collection
    DOMAIN_DB = 'dev_domain'  # Domain server collection
    PORT_DB = 'dev_port_scanner'  # Port scan collection
    AUTH_DB = 'dev_auth_tester'  # Auth tester tasks collection
    ACUNETIX_DB = 'dev_acunetix'  # Acunetix scanner tasks collection
    WEEKPASSWD_DB = 'dev_week_passwd'  # Week password collection

