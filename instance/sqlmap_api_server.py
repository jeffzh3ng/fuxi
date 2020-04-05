#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/4/5
# @File    : sqlmap_api_server.py
# @Desc    : ""

import getopt
import sys

from sqlmap.lib.utils.api import server as sqlmap_restful_server

def sqlmap_server(argv):
    port = 0
    try:
        opts, args = getopt.getopt(argv, "hp:", ["port="])
    except getopt.GetoptError:
        print("sqlmap_api_server.py --port 8778")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("sqlmap_api_server.py --port 8778")
            sys.exit()
        elif opt in ("-p", "--port"):
            port = arg
    if port != 0:
        sqlmap_restful_server("127.0.0.1", int(port))


if __name__ == '__main__':
    sqlmap_server(sys.argv[1:])
