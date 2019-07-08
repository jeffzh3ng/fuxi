#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : index_api.py
# @Desc    : ""

from flask_restful import Resource
from fuxi.common.utils.logger import logger


class HelloIndex(Resource):
    def get(self):
        """
        测试用的
        GET /api/v1/hello
        :return:
        """
        try:
            logger.success("req hello index")
            return {'code': 10200, 'status': 'success', 'message': 'ok', 'data': ''}
        except Exception as e:
            logger.error("req hello index failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': str(e)}
