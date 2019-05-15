#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/3/31
# @File    : pocsuite_api.py
# @Desc    : ""

from pocsuite3.api import init_pocsuite
from pocsuite3.api import start_pocsuite
from pocsuite3.api import get_results


def pocsuite_scanner(_poc_config):
    init_pocsuite(_poc_config)
    start_pocsuite()
    result = get_results()
    return result
