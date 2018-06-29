#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-5-15
# @File    : db_init.py
# @Desc    : ""

import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from instance import config_name
from fuxi.views.lib.mongo_db import connectiondb, db_name_conf

tasks_db = db_name_conf()['tasks_db']
asset_db = db_name_conf()['asset_db']
server_db = db_name_conf()['server_db']
subdomain_db = db_name_conf()['subdomain_db']
vul_db = db_name_conf()['vul_db']
plugin_db = db_name_conf()['plugin_db']
config_db = db_name_conf()['config_db']


def config():
    subdomain_dict = []
    subdomain_dict_path = os.getcwd() + '/tests/domain.dict'
    try:
        with open(subdomain_dict_path) as file_read:
            for i in file_read:
                subdomain_dict.append(i.strip())
    except Exception as e:
        print(e)
        subdomain_dict = ['www', 'mail', 'test']
    if not connectiondb(config_db).find_one({"config_name": config_name}):
        config_data = {
            'poc_thread': 50,
            'discovery_thread': 50,
            'subdomain_thread': 50,
            'port_thread': 50,
            'config_name': config_name,
            'poc_frequency': 15,
            'port_list': [20, 21, 22, 23, 80, 81, 443, 445, 544, 873, 1080, 1433, 1434, 1521, 2100, 3306, 3389, 4440, 5671,
                          5672, 5900, 5984, 6379, 7001, 8080, 8081, 8089, 8888, 9090, 9200, 11211, 15672, 27017, 50070],
            'subdomain_dict_2': subdomain_dict,
            'subdomain_dict_3': ['www', 'mail', 'test'],
            'username_dict': ['admin', 'root', 'administrators'],
            'password_dict': ['123456', 'password', '12345678', 'admin', 'admin123'],
            'auth_tester_thread': 50,
            'discovery_time': "10:30:00",
            'auth_service': ['asterisk', 'cisco', 'cisco-enable', 'cvs', 'firebird', 'ftp', 'ftps', 'http-proxy',
                             'http-proxy-urlenum', 'icq', 'imap', 'irc', 'ldap2', 'mssql', 'mysql', 'nntp',
                             'oracle-listener', 'oracle-sid', 'pcanywhere', 'pcnfs', 'pop3', 'postgres', 'rdp', 'redis',
                             'rexec', 'rlogin', 'rsh', 's7-300', 'sip', 'smb', 'smtp', 'smtp-enum', 'snmp', 'socks5',
                             'ssh', 'sshkey', 'svn', 'teamspeak', 'telnet', 'vmauthd', 'vnc', 'xmpp'],
        }
        connectiondb(config_db).insert_one(config_data)


if __name__ == '__main__':
    config()
