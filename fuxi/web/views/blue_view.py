#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/21
# @File    : blue_views.py
# @Desc    : ""

from fuxi.web.flask_app import flask_app
from flask import jsonify
from flask import request, Blueprint, render_template
from fuxi.core.data.response import Response, StatusCode
from fuxi.common.utils.logger import logger
from fuxi.core.databases.orm.pocsuite import DBPocsuitePlugin
from fuxi.common.utils.poc_parser import poc_parser

blue_view = Blueprint('blue_views', __name__)


@blue_view.route('/')
def index():
    return render_template('index.html')


@blue_view.route('/favicon.ico')
def favicon():
    return ""


@flask_app.errorhandler(404)
def handle_404_error(e):
    """
    :param e: 404 error msg
    :return:
    """
    if flask_app.config.get("DEBUG"):
        return jsonify(Response.failed(StatusCode.NOT_FOUND, message=e))
    else:
        return jsonify(Response.failed(StatusCode.NOT_FOUND))


@flask_app.errorhandler(500)
def handle_all_error(e):
    """
    :param e: unknown error msg
    :return:
    """
    if flask_app.config.get("DEBUG"):
        return jsonify(Response.failed(StatusCode.SERVER_ERROR, message=e))
    else:
        return jsonify(Response.failed(StatusCode.SERVER_ERROR))


@blue_view.route('/api/v1/scanner/poc/plugin_upload', methods=['POST'])
def upload_poc():
    """
    （有风险）接收上传的插件 目前测试中 没有加权限认证
    前端用的第三方组件 带 token 有点麻烦 后期琢磨一下这块怎么加固
    POST /api/v1/scanner/pocsuite/poc_upload
    :return:
    """
    if request.method == 'POST':
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
                return jsonify(Response.success(message=msg))
            else:
                return jsonify(Response.failed(message="pocsuite plugin upload failed"))
        except Exception as e:
            logger.error("pocsuite plugin upload failed: {}".format(e))
            return jsonify(Response.failed(message=e))

#
# @blue_view.route('/http', methods=['GET'])
# def http_log():
#     if request.method == 'GET':
#         try:
#             data = request.args.get("data", default=None)
#             if data:
#                 save_data = {
#                     "refer": request.referrer,
#                     "ip": request.remote_addr,
#                     "data": data,
#                     "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#                 }
#                 hid = MongoDB(T_HTTP_REQUESTS).insert_one(save_data)
#                 return jsonify({"status": "success", "data": str(hid)})
#             else:
#                 return jsonify({"status": "failed", "data": ""})
#         except Exception as e:
#             logger.error("get http log data failed: {}".format(e))
#             return jsonify({"status": "failed", "data": ""})
#
#
# @blue_view.route('/phishing/<tid>', methods=['GET'])
# def phishing(tid):
#     try:
#         item = MongoDB(T_JSON_HIJACKER_TASK).find_one({"_id": ObjectId(tid)})
#         if item:
#             return item['html']
#         else:
#             return "Not Found HTML"
#     except Exception as e:
#         logger.error("phishing return" + str(e))
#         return ERROR_MESSAGE
#
#
# @blue_view.route('/x/<path>', methods=['GET'])
# def get_xss_payload(path):
#     try:
#         project_item = MongoDB(T_XSS_PROJECTS).find_one({"path": path})
#         if project_item:
#             count = project_item['count'] + 1
#             MongoDB(T_XSS_PROJECTS).update_one({"path": path}, {'count': count})
#             return "{}".format(project_item['payload'])
#         else:
#             return "Not Found"
#     except Exception as e:
#         logger.error("get xss payload: {}".format(e))
#         return ERROR_MESSAGE
#
#
# @blue_view.route('/xss', methods=['GET'])
# def get_xss_data():
#     try:
#         salt = request.args.get('salt')
#         data = request.args.get('data')
#         url = request.args.get('url')
#         if salt:
#             MongoDB(T_XSS_RES).insert_one({
#                 "salt": salt,
#                 "url": url if url else '-',
#                 "data": data if data else '-',
#                 "ip": request.remote_addr if request.remote_addr else '0.0.0.0',
#                 "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
#             })
#     except Exception as e:
#         logger.error("get xss data failed: {}".format(e))
#     return "x"
#
