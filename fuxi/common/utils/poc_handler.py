#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/21
# @File    : poc_parser.py
# @Desc    : ""

import re
from fuxi.common.utils.logger import logger


def poc_parser(poc_str):
    name_pattern = re.compile(r'name\s*=\s*[\'\"\[](.*)[\'\"\]]')
    app_pattern = re.compile(r'appName\s*=\s*[\'\"\[](.*)[\'\"\]]')
    type_pattern = re.compile(r'vulType\s*=\s*[\'\"\[](.*)[\'\"\]]')
    plugin_info = {
        "name": 'unknown',
        "type": 'unknown',
        "app": 'unknown',
    }
    try:
        plugin_info['name'] = name_pattern.findall(poc_str)[0]
        plugin_info['type'] = type_pattern.findall(poc_str)[0]
        plugin_info['app'] = app_pattern.findall(poc_str)[0]
    except Exception as e:
        logger.warning("pocsuite plugin parser error: %s" % e)
    return plugin_info
