#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/3/20
# @File    : dashboard_api.py
# @Desc    : ""

from flask_restful import Resource

from fuxi.core.data.response import Response
from fuxi.core.auth.token import auth
from fuxi.core.databases.orm.scanner.pocsuite_orm import DBPocsuiteVul
from fuxi.core.databases.orm.exploit.jsonp_orm import DBExploitJsonpRes
from fuxi.core.databases.orm.exploit.xss_orm import DBXssResult
from fuxi.core.databases.orm.exploit.http_log_orm import DBHttpRequestLog
from fuxi.common.utils.logger import logger


class DashboardResCount(Resource):
    @auth
    def get(self):
        data = {"vuls": 0, "jsonp": 0, "xss": 0, "http": 0}
        try:
            data['vuls'] = DBPocsuiteVul.get_count({"status": "success"})
            data['jsonp'] = DBExploitJsonpRes.get_count()
            data['xss'] = DBXssResult.get_count()
            data['http'] = DBHttpRequestLog.get_list().count()
            return Response.success(data=data)
        except Exception as e:
            msg = "get dashboard result count failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(data=data, message=msg)
