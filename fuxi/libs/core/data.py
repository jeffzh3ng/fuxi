#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/24
# @File    : data.py
# @Desc    : ""


ERROR_MESSAGE = "An error occurred, please try again later"
RANDOM_SEED_LOW = "abcdefghijklmnopqrstuvwxyz"
RANDOM_SEED_STR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
RANDOM_SEED_ALL = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class SecurityModule:
    ALL_MODULE = []
    MODULE_DESC = {}
    WHITE_MODULE = ['WhoAreYou.GET', 'blue_views.upload_poc.POST']

