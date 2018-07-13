#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-5-19
# @File    : domain_brute.py
# @Desc    : ""

import socket
import gevent
import time
import threading
from gevent import monkey
from gevent import pool as gevent_pool
from datetime import datetime
from random import sample
from string import digits, ascii_lowercase
from fuxi.views.lib.mongo_db import connectiondb, db_name_conf
from fuxi.views.lib.get_title import get_title
from instance import config_name

monkey.patch_all()
socket.setdefaulttimeout(5)
domain_db = db_name_conf()['domain_db']
config_db = db_name_conf()['config_db']
subdomain_db = db_name_conf()['subdomain_db']


def start_domain_brute(domain_list, domain_id):
    time_start = datetime.now()
    print("[*] %s Domain Brute start %s" % (time_start.strftime("%Y-%m-%d %H:%M:%S"), domain_id))
    time.sleep(5)  # Don't delete it
    connectiondb(domain_db).update_one({"_id": domain_id}, {"$set": {
        "status": "Running"
    }})
    try:
        for domain in domain_list:
            scanner = DomainBrute(domain, domain_id)
            scanner.start()
    except Exception as e:
        print("[!] Traversal error %s" % e)
    connectiondb(domain_db).update_one({"_id": domain_id}, {"$set": {
        "status": "Done"
    }})
    time_end = datetime.now()
    print("[*] %s Domain Brute Done %s" % (time_end.strftime("%Y-%m-%d %H:%M:%S"), domain_id))
    print("[*] %s Used Time: %s" % (time_end.strftime("%Y-%m-%d %H:%M:%S"), (time_end - time_start).seconds))


# def get_domain_title(domain_id):
#     pool = Pool(processes=50)
#     result = []
#     for i in connectiondb(subdomain_db).find({"domain_id": domain_id}):
#         result.append(pool.apply_async(get_title, (i['subdomain'], i['_id'])))
#     pool.close()
#     pool.join()
#     for res in result:
#         lock.acquire()
#         try:
#             connectiondb(subdomain_db).update_one({"_id": res.get()["_id"]}, {"$set": {
#                 "title": res.get()['title']
#             }})
#         except Exception as e:
#             print("update title error", e)
#         lock.release()


class DomainBrute:

    def __init__(self, domain, domain_id):
        print("[*] %s %s Brute Start" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), domain))
        self.domain = domain.strip()
        self.domain_id = domain_id
        self.sub_dict = connectiondb(config_db).find_one({"config_name": config_name})['subdomain_dict_2']
        self.next_sub_dict = connectiondb(config_db).find_one({"config_name": config_name})['subdomain_dict_3']
        self.check_domain_list = []
        self.thread = int(connectiondb(config_db).find_one({"config_name": config_name})['subdomain_thread'])
        self.next_domain_opt = connectiondb(domain_db).find_one({"_id": domain_id})['third_domain']
        self.random_subdomain = ''.join(sample(digits + ascii_lowercase, 10)) + '.' + domain
        self.resolver_domain = ''
        self.res_tmp = []

    def _domain_parse(self):
        for sub in self.sub_dict:
            check_domain = sub + '.' + self.domain
            self.check_domain_list.append(check_domain)
        if self.next_domain_opt == 'Enable':
            for next_sub in self.next_sub_dict:
                for sub in self.sub_dict:
                    next_check_domain = next_sub + '.' + sub + '.' + self.domain
                    self.check_domain_list.append(next_check_domain)

    def start(self):
        self._domain_parse()
        self._get_resolver_domain()
        jobs = []
        p = gevent_pool.Pool(self.thread)
        for subdomain in self.check_domain_list:
            jobs.append(p.spawn(self.gethost, subdomain))
        gevent.joinall(jobs)
        print("[*] %s %s Brute Done" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.domain))
        self._result_save()

    def _get_resolver_domain(self):
        try:
            host = socket.gethostbyname(self.random_subdomain)
            if host:
                self.resolver_domain = host
        except Exception as e:
            # print(e)
            pass

    def gethost(self, sub_domain):
        try:
            host = socket.gethostbyname(sub_domain)
            res = {
                "domain": sub_domain,
                "host": host,
            }
            self.res_tmp.append(res)
        except Exception as e:
            # print(e)
            pass

    def _result_save(self):
        save_tmp = []
        for res in self.res_tmp:
            if self.resolver_domain == res['host']:
                pass
            else:
                data = {
                    "subdomain": res['domain'],
                    "domain": self.domain,
                    "domain_id": self.domain_id,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "result": res['host'],
                    "title": '',
                }
                save_tmp.append(data)
        try:
            if save_tmp:
                connectiondb(subdomain_db).insert_many(save_tmp, ordered=True)
        except Exception as e:
            print("[!] %s Saved domain result error: %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), e))
