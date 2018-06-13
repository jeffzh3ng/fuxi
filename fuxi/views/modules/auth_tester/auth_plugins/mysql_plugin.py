#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-5-30
# @File    : mysql_plugin.py
# @Desc    : ""

import socket
import MySQLdb
from multiprocessing import Pool
from fuxi.views.lib.mongo_db import connectiondb, db_name_conf
from instance import config_name


config_db = db_name_conf()['config_db']


class MySQLPlugin:
    def __init__(self, target_list, username_list, password_list):
        self.target_list = target_list
        self.username_list = username_list
        self.password_list = password_list
        self.mysql_target = []
        self.result = []
        self.result_check = []
        self.result_auth = []
        self.processes = connectiondb(config_db).find_one({"config_name": config_name})['auth_tester_thread']

    def mysql_scan(self):
        pool_1 = Pool(processes=self.processes)
        for target in self.target_list:
            self.result_check.append(pool_1.apply_async(target_check, (target,)))
        pool_1.close()
        pool_1.join()
        for res in self.result_check:
            if type(res.get()) != bool:
                self.mysql_target.append(res.get())
        pool_2 = Pool(processes=self.processes)
        for target in self.mysql_target:
            for username in self.username_list:
                for password in self.password_list:
                    self.result_auth.append(pool_2.apply_async(mysql_crack, (target, username, password)))
        pool_2.close()
        pool_2.join()
        for res_auth in self.result_auth:
            try:
                if res_auth.get():
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
        port = 3306
        host = target
    s = socket.socket()
    s.settimeout(5)
    try:
        s.connect((host, port))
        result = s.recv(1024)
        s.close()
        # Return two results:
        # 1. Host 'UBUNTU' is not allowed ... this MySQL server
        # 2. ubuntu0.16.04.1 ... mysql_native_password
        if "mysql" in result.lower():
            return target
        else:
            return False

    except socket.error, msg:
        # print(msg)
        pass


def mysql_crack(target, username, password):
    if ":" in target:
        port = int(target.split(":")[1])
        host = target.split(":")[0]
    else:
        port = 3306
        host = target
    try:
        db = MySQLdb.connect(host=host, user=username, passwd=password, db="", port=port)
        result = {
            "target": target,
            "username": username,
            "password": password,
        }
        db.close()
        return result
    except MySQLdb.Error, msg:
        pass


if __name__ == '__main__':
    mysql_crack('127.0.0.1', 'root', 'kali@1234')



