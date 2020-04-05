#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/4/5
# @File    : network.py
# @Desc    : ""

import random
import socket


def get_free_port():
    try:
        sock = socket.socket()
        sock.bind(('', 0))
        ip, port = sock.getsockname()
        sock.close()
        return port
    except Exception as e:
        return random.randint(3000, 5000)
