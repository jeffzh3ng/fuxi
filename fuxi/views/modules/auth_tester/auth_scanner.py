#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-6-19
# @File    : auth_scanner.py
# @Desc    : ""

import time
from threading import Thread
from datetime import datetime
from multiprocessing import Pool
from fuxi.views.lib.mongo_db import connectiondb, db_name_conf
from fuxi.views.modules.auth_tester.hydra_plugin import HydraScanner
from fuxi.views.lib.parse_target import parse_target
from apscheduler.schedulers.blocking import BlockingScheduler
from instance import config_name

config_db = db_name_conf()['config_db']
weekpasswd_db = db_name_conf()['weekpasswd_db']
auth_db = db_name_conf()['auth_db']


def hydra_scanner(args):
    start = HydraScanner(args)
    result = start.scanner()
    return result


def host_check(args):
    start = HydraScanner(args)
    result = start.host_check()
    return result


class AuthCrack:

    def __init__(self, task_id):
        self.task_id = task_id
        self.db_cursor = connectiondb(auth_db).find_one({"_id": self.task_id})
        self.processes = connectiondb(config_db).find_one({"config_name": config_name})['auth_tester_thread']
        self.task_name = self.db_cursor['task_name']
        self.username_list = self.db_cursor['username']
        self.password_list = self.db_cursor['password']
        self.target_list = parse_target(self.db_cursor['target'])
        self.online_target = []
        self.service_list = self.db_cursor['service']
        self.args = self.db_cursor['args']
        self.result_pool = []
        self.result = []
        self.week_count = 0

    def start_scan(self):
        tmp_result = []
        args = self.args
        connectiondb(auth_db).update_one({"_id": self.task_id}, {"$set": {"status": "Processing"}})
        for service in self.service_list:
            # Filter online host
            pool_a = Pool(processes=self.processes)
            args_check = self._args_parse(service, 'check')
            for args in args_check:
                tmp_result.append(pool_a.apply_async(host_check, (args,)))
            pool_a.close()
            pool_a.join()
            for res_a in tmp_result:
                if res_a.get():
                    self.online_target.append(res_a.get())
            # start crack
            pool_b = Pool(processes=self.processes)
            args_crack = self._args_parse(service, 'crack')
            for args in args_crack:
                self.result.append(pool_b.apply_async(hydra_scanner, (args,)))
            pool_b.close()
            pool_b.join()
            self.online_target = []
        for res_b in self.result:
            if res_b.get():
                target = res_b.get()['target']
                service = res_b.get()['service']
                username = res_b.get()['username']
                password = res_b.get()['password']
                self.save_result(target, service, username, password)
        connectiondb(auth_db).update_one({"_id": self.task_id}, {"$set": {
            "status": "Completed",
            "week_count": self.week_count,
        }})

    def save_result(self, target, service, username, password):
        data = {
            "target": target,
            "service": service,
            "username": username,
            "password": password,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task_id": self.task_id,
            "task_name": self.task_name,
            "tag": ""
        }
        self.week_count += 1
        connectiondb(weekpasswd_db).insert_one(data)

    def _args_parse(self, service, opt):
        args_list = []
        if opt == 'check':
            for target in self.target_list:
                if ":" in target:
                    target_l = target.split(":")
                    if target_l[-1].isdigit():
                        port = target_l[-1]
                        del target_l[-1]
                        target = ''.join(target_l)
                        self.args = self.args + '-s %s' % port
                if service in ['redis', 'cisco', 'oracle-listener', 's7-300', 'snmp', 'vnc']:
                    if len(self.args) > 0:
                        command = ['hydra', '-t', '1', '-p', ''] + [self.args] + [target] + [service]
                    else:
                        command = ['hydra', '-t', '1', '-p', ''] + [target] + [service]
                else:
                    if len(self.args) > 0:
                        command = ['hydra', '-t', '1', '-l', '', '-p', ''] + [self.args] + [target] + [service]
                    else:
                        command = ['hydra', '-t', '1', '-l', '', '-p', ''] + [target] + [service]
                args_list.append(command)
        elif opt == 'crack':
            for target in self.online_target:
                if ":" in target:
                    target_l = target.split(":")
                    if target_l[-1].isdigit():
                        port = target_l[-1]
                        del target_l[-1]
                        target = ''.join(target_l)
                        self.args = self.args + '-s %s' % port
                if service in ['redis', 'cisco', 'oracle-listener', 's7-300', 'snmp', 'vnc']:
                    for password in self.password_list:
                        if len(self.args) > 0:
                            command = ['hydra', '-t', '1', '-p', password] + [self.args] + [target] + [service]
                        else:
                            command = ['hydra', '-t', '1', '-p', password] + [target] + [service]
                        args_list.append(command)
                else:
                    for username in self.username_list:
                        for password in self.password_list:
                            if len(self.args) > 0:
                                command = ['hydra', '-t', '1', '-l', username, '-p', password] + [self.args] + [target] + [service]
                            else:
                                command = ['hydra', '-t', '1', '-l', username, '-p', password] + [target] + [service]
                            args_list.append(command)
        return args_list


class AuthTesterLoop:

    def __init__(self):
        self.recursion = ''
        self.status = ''
        self.scan_date = ''
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
            self.task_id = task_info['_id']
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
        scanner = AuthCrack(self.task_id)
        if scanner:
            t1 = Thread(target=scanner.start_scan, args=())
            t1.start()
            return True
