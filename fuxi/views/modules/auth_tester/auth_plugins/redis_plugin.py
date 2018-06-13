#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-5-29
# @File    : redis_plugin.py
# @Desc    : ""

import socket
from multiprocessing import Pool
from fuxi.views.lib.mongo_db import connectiondb, db_name_conf
from instance import config_name
config_db = db_name_conf()['config_db']


class RedisPlugin:

    def __init__(self, target_list, password_list):
        self.target_list = target_list
        self.password_list = password_list
        self.redis_target = []
        self.result_check = []
        self.result_auth = []
        self.result = []
        self.processes = connectiondb(config_db).find_one({"config_name": config_name})['auth_tester_thread']

    def redis_scan(self):
        pool_1 = Pool(processes=self.processes)
        for target in self.target_list:
            self.result_check.append(pool_1.apply_async(target_check, (target,)))
        pool_1.close()
        pool_1.join()
        for res in self.result_check:
            if type(res.get()) == dict:
                self.result.append(res.get())
            elif type(res.get()) != bool:
                self.redis_target.append(res.get())
        pool_2 = Pool(processes=self.processes)
        for target in self.redis_target:
            for password in self.password_list:
                self.result_auth.append(pool_2.apply_async(redis_auth, (target, password)))
        pool_2.close()
        pool_2.join()
        for res_auth in self.result_auth:
            try:
                if type(res_auth.get()) != bool:
                    self.result.append(res_auth.get())
            except Exception as e:
                # print(e)
                pass
        return self.result


def target_check(target):
    if ":" in target:
        port = int(target.split(":")[1])
        host = target.split(":")[0]
    else:
        port = 6379
        host = target
    s = socket.socket()
    s.settimeout(5)
    try:
        s.connect((host, port))
        s.send("INFO\r\n")
        result = s.recv(1024)
        s.close()
        if "redis_version" in result:
            result = {
                "target": target,
                "username": "None",
                "password": "Unauthorized",
            }
            return result
        elif "Authentication" in result:
            return target
    except socket.error, msg:
        # print(msg)
        return False


def redis_auth(target, password):
    if ":" in target:
        port = int(target.split(":")[1])
        host = target.split(":")[0]
    else:
        port = 6379
        host = target
    s = socket.socket()
    s.settimeout(5)
    try:
        s.connect((host, port))
        s.send("AUTH %s\r\n" % password)
        result = s.recv(1024)
        s.close()
        if '+OK' in result:
            result = {
                "target": target,
                "username": "None",
                "password": password,
            }
            return result
        else:
            return False
    except socket.error, msg:
        # print(msg)
        return False
