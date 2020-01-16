#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : index_api.py
# @Desc    : ""

from flask import session, request, current_app
from flask_restful import Resource
from fuxi.core.auth.token import auth
from fuxi.common.utils.poc_handler import poc_parser
from fuxi.core.databases.orm.scanner.pocsuite_orm import DBPocsuitePlugin
# from fuxi.core.databases.orm.tests import DBTest
from fuxi.core.data.response import Response
from fuxi.common.utils.logger import logger


class HelloIndex(Resource):
    @auth
    def get(self):
        """
        测试用的
        GET /api/v1/hello
        :return:
        """
        try:
            logger.success("req hello index")
            # DBTest.test()
            logger.info("demo api test: {}".format(session.get("user")))
            return {'code': 10200, 'status': 'success', 'message': 'ok', 'data': str(session)}
        except Exception as e:
            logger.warning("req hello index failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': str(e)}


class FileUploadDemo(Resource):
    @auth
    def post(self):
        try:
            file = request.files['file']
            filename = file.filename
            poc_str = file.read().decode("UTF-8")
            # 调 poc_parser 方法正则匹配出插件信息
            poc_data = poc_parser(poc_str)
            pid = DBPocsuitePlugin.add(
                name=poc_data['name'], poc_str=poc_str, filename=filename,
                app=poc_data['app'], poc_type=poc_data['type']
            )
            if pid:
                msg = "pocsuite plugin upload successful: {}".format(pid)
                logger.success(msg)
                return Response.success(message=msg)
            else:
                return Response.failed(message="pocsuite plugin upload failed")
        except Exception as e:
            logger.warning("pocsuite plugin upload failed: {}".format(e))
            return Response.failed(message=e)


class JsonpDemoV1(Resource):
    @auth
    def get(self):
        callback = request.args.get('callback', False)
        if callback:
            content = '{}({})'.format(
                str(callback), str(Response.success(data=session.get('user')))
            )
            return current_app.response_class(content, mimetype='application/json')
        else:
            return Response.success(data=session.get('user'))
