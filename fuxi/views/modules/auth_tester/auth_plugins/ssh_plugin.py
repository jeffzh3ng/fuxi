#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-5-30
# @File    : ssh_plugin.py
# @Desc    : ""

import socket
from pexpect import pxssh
from multiprocessing import Pool
from fuxi.views.lib.mongo_db import connectiondb, db_name_conf
from instance import config_name

config_db = db_name_conf()['config_db']


class SSHPlugin:
    def __init__(self, target_list, username_list, password_list):
        self.target_list = target_list
        self.username_list = username_list
        self.password_list = password_list
        self.ssh_target = []
        self.result = []
        self.result_check = []
        self.result_auth = []
        self.processes = connectiondb(config_db).find_one({"config_name": config_name})['auth_tester_thread']

    def ssh_scan(self):
        pool_1 = Pool(processes=self.processes)
        for target in self.target_list:
            self.result_check.append(pool_1.apply_async(target_check, (target,)))
        pool_1.close()
        pool_1.join()
        for res in self.result_check:
            if res.get():
                self.ssh_target.append(res.get())
        pool_2 = Pool(processes=self.processes)
        for target in self.target_list:
            for username in self.username_list:
                for password in self.password_list:
                    self.result_auth.append(pool_2.apply_async(ssh_crack, (target, username, password)))
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
        port = 22
        host = target
    s = socket.socket()
    s.settimeout(5)
    try:
        s.connect((host, port))
        result = s.recv(1024)
        s.close()
        if "ssh" in result.lower():
            return target
        else:
            return False
    except Exception as e:
        return False


def ssh_crack(target, username, password):
    if ":" in target:
        port = target.split(":")[1]
        host = target.split(":")[0]
    else:
        port = 22
        host = target
    try:
        s = pxssh.pxssh()
        s.login(server=host, username=username, password=password, port=port)
        s.logout()
        result = {
            "target": target,
            "username": username,
            "password": password,
        }
        return result
    except Exception as e:
        # print(e)
        return False



