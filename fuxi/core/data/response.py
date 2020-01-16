#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/7/5
# @File    : response.py
# @Desc    : ""


import time


class _ResponseContext:
    def __init__(self):
        self.data = {
            "status": {"status": "", "code": 0, "message": ""},
            "result": "",
            "timestamp": 0
        }

    def success(self, status=None, message=None, data=""):
        self.data['status']['code'], self.data['status']['message'] = StatusCode.SUCCESS
        self.data['status']['status'] = 'success'
        self.data['result'] = data
        self.data['timestamp'] = int(time.time())
        if status:
            self.data['status']['code'], self.data['status']['message'] = status
        if message:
            self.data['status']['message'] = str(message)
        return self.data

    def failed(self, status=None, code=0, message=None, data=""):
        self.data['status']['code'], self.data['status']['message'] = StatusCode.FAILED
        self.data['status']['status'] = 'failed'
        self.data['result'] = data
        self.data['timestamp'] = int(time.time())
        if status:
            self.data['status']['code'], self.data['status']['message'] = status
        if code > 0:
            self.data['status']['code'] = int(code)
        if message:
            self.data['status']['message'] = str(message)
        return self.data


class StatusCode:
    # success
    SUCCESS = (10200, "")
    # failed
    AUTH_FAILED = (10401, "The access token is invalid")
    NOT_FOUND = (10404, "The requested URL was not found on the server")
    FAILED = (10503, "Unknown error, Please try again later")
    SERVER_ERROR = (10500, "Internal Server Error")


Response = _ResponseContext()

