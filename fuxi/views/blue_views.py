#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/21
# @File    : blue_views.py
# @Desc    : ""

import time
from fuxi import app
from bson import ObjectId
from flask import request, Blueprint, jsonify, render_template
from fuxi.libs.common.logger import logger
from fuxi.database import MongoDB, \
    T_POC_PLUGINS, T_HTTP_REQUESTS, T_JSON_HIJACKER_TASK, T_XSS_RES, T_XSS_PROJECTS
from fuxi.libs.data.poc_parser import poc_parser
from fuxi.libs.core.data import ERROR_MESSAGE

blue_views = Blueprint('blue_views', __name__)


@blue_views.route('/')
def index():
    return render_template("index.html")


@app.errorhandler(404)
def handle_404_error(err):
    """
    :param err: 404 error msg
    :return:
    """
    err_msg = "404 Not Found: The requested URL was not found on the server"
    return jsonify({'code': 10404, "status": "failed", "message": "{}".format(err_msg)})


@app.errorhandler(500)
def handle_500_error(err):
    """
    :param err: 404 error msg
    :return:
    """
    err_msg = "500 Internal Server Error"
    return jsonify({'code': 10404, "status": "failed", "message": "{}".format(err_msg)})


@blue_views.route('/api/v1/scanner/poc/upload', methods=['POST'])
def upload_poc():
    """
    （有风险）接收上传的插件 目前测试中 没有加权限认证
    前端用的第三方组件 带 token 有点麻烦 后期琢磨一下这块怎么加固
    POST /api/v1/scanner/poc/upload
    :return:
    """
    if request.method == 'POST':
        try:
            file = request.files['file']
            filename = file.filename
            poc_str = file.read().decode("UTF-8")
            # 调 poc_parser 方法正则匹配出插件信息
            poc_data = poc_parser(poc_str)
            poc_data['poc'] = poc_str
            poc_data['filename'] = filename
            poc_data['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            pid = MongoDB(T_POC_PLUGINS).insert_one(poc_data)
            logger.success("plugin successful upload: {}".format(pid))
            return "success"
        except Exception as e:
            logger.error("upload poc failed: {}".format(e))
            return 'failed', 503


@blue_views.route('/http', methods=['GET'])
def http_log():
    if request.method == 'GET':
        try:
            data = request.args.get("data", default=None)
            if data:
                save_data = {
                    "refer": request.referrer,
                    "ip": request.remote_addr,
                    "data": data,
                    "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
                hid = MongoDB(T_HTTP_REQUESTS).insert_one(save_data)
                return jsonify({"status": "success", "data": str(hid)})
            else:
                return jsonify({"status": "failed", "data": ""})
        except Exception as e:
            logger.error("get http log data failed: {}".format(e))
            return jsonify({"status": "failed", "data": ""})


@blue_views.route('/phishing/<tid>', methods=['GET'])
def phishing(tid):
    try:
        item = MongoDB(T_JSON_HIJACKER_TASK).find_one({"_id": ObjectId(tid)})
        if item:
            return item['html']
        else:
            return "Not Found HTML"
    except Exception as e:
        logger.error("phishing return" + str(e))
        return ERROR_MESSAGE


@blue_views.route('/x/<path>', methods=['GET'])
def get_xss_payload(path):
    try:
        project_item = MongoDB(T_XSS_PROJECTS).find_one({"path": path})
        if project_item:
            count = project_item['count'] + 1
            MongoDB(T_XSS_PROJECTS).update_one({"path": path}, {'count': count})
            return "{}".format(project_item['payload'])
        else:
            return "Not Found"
    except Exception as e:
        logger.error("get xss payload: {}".format(e))
        return ERROR_MESSAGE


@blue_views.route('/xss', methods=['GET'])
def get_xss_data():
    try:
        salt = request.args.get('salt')
        data = request.args.get('data')
        url = request.args.get('url')
        if salt:
            MongoDB(T_XSS_RES).insert_one({
                "salt": salt,
                "url": url if url else '-',
                "data": data if data else '-',
                "ip": request.remote_addr if request.remote_addr else '0.0.0.0',
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            })
    except Exception as e:
        logger.error("get xss data failed: {}".format(e))
    return "x"

