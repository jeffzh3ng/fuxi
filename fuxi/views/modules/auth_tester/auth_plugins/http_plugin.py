#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-5-29
# @File    : http_plugin.py
# @Desc    : ""

import requests
from flask import Flask
from requests.auth import HTTPBasicAuth
from multiprocessing import Pool
from fuxi.views.lib.mongo_db import connectiondb, db_name_conf
from instance import config_name

config_db = db_name_conf()['config_db']


class HttpPlugin:

    def __init__(self, target_list, username_list, password_list, plugin):
        self.target_list = target_list
        self.username_list = username_list
        self.password_list = password_list
        self.plugin = plugin
        self.result = []
        self.result_tmp = []
        self.processes = connectiondb(config_db).find_one({"config_name": config_name})['auth_tester_thread']

    def http_scan(self):
        if self.plugin == "Basic Auth":
            pool = Pool(processes=self.processes)
            for target in self.target_list:
                if "http://" not in target and "https://" not in target:
                    target = "http://" + target
                for username in self.username_list:
                    for password in self.password_list:
                        self.result_tmp.append(pool.apply_async(basic_auth, (target, username, password)))
            pool.close()
            pool.join()
            for res in self.result_tmp:
                if type(res.get()) == dict:
                    self.result.append(res.get())

        return self.result


def basic_auth(target, username, password):
    try:
        response = requests.get(target, auth=HTTPBasicAuth(username, password), timeout=10)
        if response.status_code == 200:
            result = {
                "target": target,
                "username": username,
                "password": password,
            }
            return result
        else:
            return False
    except Exception as e:
        return False
