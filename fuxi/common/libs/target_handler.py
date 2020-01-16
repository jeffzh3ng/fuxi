#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/3/31
# @File    : target_parser.py
# @Desc    : ""

import re
from urllib.parse import urlparse, urlunparse
from fuxi.common.libs.ip_handler import IP
from fuxi.common.utils.logger import logger


def target_parse(target_list):
    new_target_list = []
    for target in target_list:
        if target in new_target_list:
            continue
        target = target.strip()
        re_ip = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        re_ips = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$')
        re_url = re.compile('[^\s]*.[a-zA-Z]')
        re_ip_port = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$')
        re_url_port = re.compile('[^\s]*.[a-zA-Z]:\d{1,5}')

        if re_ip.match(target):
            new_target_list.append(target)

        # 如果是网络段 转换成IP
        elif re_ips.match(target):
            try:
                ip_list = IP(target)
                for ip in ip_list:
                    new_target_list.append(str(ip))
            except Exception as e:
                logger.warning("ips parser failed: {}".format(e))

        elif re_url.match(target):
            new_target_list.append(_url_parse(target))

        elif re_ip_port.match(target):
            new_target_list.append(target)

        elif re_url_port.match(target):
            new_target_list.append(target)
    return new_target_list


def _url_parse(url):
    if "http" != url[0:4]:
        url = "http://" + url
    return url


def callback_url_parser(url):
    parsed_result = urlparse(url)
    query = ""
    for item in parsed_result.query.split('&'):
        if "callback=" not in item:
            query += item + "&"
    query = query.strip('&') + "callback=?"
    url_compos = (parsed_result.scheme, parsed_result.netloc, parsed_result.path,
                  parsed_result.params, query, parsed_result.fragment)
    return urlunparse(url_compos)
