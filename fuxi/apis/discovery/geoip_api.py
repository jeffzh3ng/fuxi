#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/30
# @File    : geoip_api.py
# @Desc    : ""

import re
from flask_restful import Resource
from fuxi.libs.data.geoip import geoip
from fuxi.libs.common.logger import logger


class GeoAPI(Resource):
    desc = "查询 ip 地理信息"

    @staticmethod
    def get(ip, language="en"):
        """
        通过 Geo IP 数据库查询 ip 地理信息 可以指定返回信息语言（默认返回英语）
        暂时不做权限校验了
        GET /api/v1/lib/geoip/8.8.8.8/zh-CN
        GET /api/v1/lib/geoip/<ip>/<language>
        :return:
        """
        try:
            compile_ip = re.compile('^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.'
                                    '(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
            if compile_ip.match(ip):
                data = geoip(ip, language)
                return {'code': 10200, 'status': 'success', 'message': '', 'data': data}
            else:
                return {'code': 10501, 'status': 'failed', 'message': 'Invalid IP Address', 'data': {}}
        except Exception as e:
            logger.warning(e)
            return {'code': 10501, 'status': 'failed', 'message': "The request was invalid"}
