#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-5-29
# @File    : auth_crack.py
# @Desc    : ""

import time
import sched
from datetime import datetime
from threading import Thread
from apscheduler.schedulers.blocking import BlockingScheduler
from fuxi.views.lib.mongo_db import connectiondb, db_name_conf
from fuxi.views.lib.parse_target import parse_target
from fuxi.views.modules.auth_tester.auth_plugins import redis_plugin, http_plugin, ssh_plugin, mysql_plugin

weekpasswd_db = db_name_conf()['weekpasswd_db']
auth_db = db_name_conf()['auth_db']
schedule = sched.scheduler(time.time, time.sleep)


class AuthCrack:
    def __init__(self, target_list, username_list, password_list, task_id, task_name, plugin):
        self.target_list = parse_target(target_list)
        self.username_list = username_list
        self.password_list = password_list
        self.plugin = plugin
        self.result = ""
        self.task_id = task_id
        self.task_name = task_name
        self.week_count = 0

    def start_scan(self):
        connectiondb(auth_db).update_one({"_id": self.task_id}, {"$set": {"status": "Processing"}})
        if self.plugin == "Redis Auth":
            scanner = redis_plugin.RedisPlugin(self.target_list, self.password_list)
            self.result = scanner.redis_scan()
            for i in self.result:
                self.save_result(i['target'], i['username'], i['password'])

        elif self.plugin == "Basic Auth":
            scanner = http_plugin.HttpPlugin(self.target_list, self.username_list, self.password_list, self.plugin)
            self.result = scanner.http_scan()
            for i in self.result:
                self.save_result(i['target'], i['username'], i['password'])

        elif self.plugin == "SSH Auth":
            scanner = ssh_plugin.SSHPlugin(self.target_list, self.username_list, self.password_list)
            self.result = scanner.ssh_scan()
            for i in self.result:
                self.save_result(i['target'], i['username'], i['password'])

        elif self.plugin == "MySQL Auth":
            scanner = mysql_plugin.MySQLPlugin(self.target_list, self.username_list, self.password_list)
            self.result = scanner.mysql_scan()
            for i in self.result:
                self.save_result(i['target'], i['username'], i['password'])

        connectiondb(auth_db).update_one({"_id": self.task_id}, {"$set": {
            "status": "Completed",
            "week_count": self.week_count
        }})

    def save_result(self, target, username, password):
        data = {
            "target": target,
            "type": self.plugin,
            "username": username,
            "password": password,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task_id": self.task_id,
            "task_name": self.task_name,
            "tag": ""
        }
        self.week_count += 1
        connectiondb(weekpasswd_db).insert_one(data)


class AuthTesterLoop:

    def __init__(self):
        self.recursion = ''
        self.status = ''
        self.scan_date = ''
        self.username_list = ''
        self.password_list = ''
        self.task_name = ''
        self.target_list = ''
        self.task_type = ''
        self.task_id = ''

    def task_schedule(self):
        scheduler = BlockingScheduler()
        try:
            scheduler.add_job(self._get_task, 'interval', seconds=30)
            scheduler.start()
        except Exception as e:
            print(e)

    def _get_task(self):
        for task_info in connectiondb(auth_db).find():
            self.recursion = task_info['recursion']
            self.status = task_info['status']
            self.scan_date = task_info['date']
            self.username_list = task_info['username']
            self.password_list = task_info['password']
            self.task_name = task_info['task_name']
            self.task_id = task_info['_id']
            self.target_list = task_info['target']
            self.task_type = task_info['type']
            start_date = datetime.strptime(self.scan_date, "%Y-%m-%d %H:%M:%S")
            plan_time = (datetime.now() - start_date).total_seconds()
            if self.recursion == 0:
                pass
            # every day
            elif self.recursion == 1 and "Completed" in self.status:
                if plan_time > 60 * 60 * 24 * 1:
                    if self.start_loop_scan():
                        print("[*] Every Day Task Start...", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            # every week
            elif self.recursion == 7 and "Completed" in self.status:
                if plan_time > 60 * 60 * 24 * 7:
                    if self.start_loop_scan():
                        print("[*] Every Week Task Start...", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            # every month
            elif self.recursion == 30 and "Completed" in self.status:
                if plan_time > 60 * 60 * 24 * 30:
                    if self.start_loop_scan():
                        print("[*] Every Month Task Start...", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def start_loop_scan(self):
        connectiondb(weekpasswd_db).update({"task_id": self.task_id}, {"$set": {"tag": "delete"}}, multi=True)
        connectiondb(auth_db).update_one({"_id": self.task_id}, {"$set": {
            "status": "Queued",
            "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "week_count": 0,
        }})
        scan_start = AuthCrack(self.target_list, self.username_list, self.password_list,
                               self.task_id, self.task_name, self.task_type)
        if scan_start:
            t1 = Thread(target=scan_start.start_scan, args=())
            t1.start()
            return True
