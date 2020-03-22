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
from fuxi.core.databases.orm.exploit.jsonp_orm import DBExploitJsonpTask
from fuxi.core.databases.orm.exploit.http_log_orm import DBHttpRequestLog
from fuxi.core.databases.orm.exploit.xss_orm import DBXssTasks, DBXssResult

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


@blue_view.route('/jsonp/<sid>', methods=['GET'])
def phishing(sid):
    try:
        item = DBExploitJsonpTask.get_detail_by_short_id(sid)
        if item:
            return item['html']
        else:
            return "Not Found HTML"
    except Exception as e:
        logger.warning("get jsonp hijacking page failed: {} {}".format(sid, e))
        return "Not Found HTML"


@blue_view.route('/http', methods=['GET'])
def http_log():
    if request.method == 'GET':
        try:
            data = request.args.get("data", default=None)
            verify = request.args.get("verify", default=None)
            if data:
                ip = request.remote_addr if request.remote_addr else '0.0.0.0'
                referrer = request.referrer if request.referrer else '-'
                hid = DBHttpRequestLog.add(ip, referrer, data)
                return jsonify({"status": "success", "data": str(hid)})
            elif verify:
                if DBHttpRequestLog.verify(verify):
                    return jsonify({"result": True})
                else:
                    return jsonify({"result": False})
            else:
                return jsonify({"status": "failed", "data": ""})
        except Exception as e:
            logger.warning("receive http request log failed: {}".format(e))
            return jsonify({"status": "failed", "data": ""})


@blue_view.route('/x/<path>', methods=['GET'])
def get_xss_payload(path):
    try:
        project_item = DBXssTasks.get_detail_by_salt(path[:5])
        if project_item:
            return "{}".format(project_item['payload'])
        else:
            return "Not Found"
    except Exception as e:
        msg = "get xss payload: {}".format(e)
        logger.warning(msg)
        return Response.failed(message=msg)


@blue_view.route('/xss', methods=['GET'])
def get_xss_data():
    try:
        salt = request.args.get('salt')
        data = request.args.get('data')
        url = request.args.get('url')
        client = request.remote_addr if request.remote_addr else '0.0.0.0'
        referrer = request.referrer if request.referrer else '-'
        extend = request.args.get('extend')
        if salt:
            item = DBXssTasks.get_detail_by_salt(salt)
            if item:
                DBXssResult.add(
                    item['_id'], salt, client=client, referrer=referrer,
                    url=url, data=data, extend=extend
                )
            return "Y"
        else:
            return "Missing Parameter: salt"
    except Exception as e:
        logger.warning("get xss data failed: {}".format(e))
    return "x"

