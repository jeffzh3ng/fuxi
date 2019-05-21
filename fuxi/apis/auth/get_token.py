#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/20
# @File    : get_token.py
# @Desc    : ""

import time
from fuxi import app
from hashlib import md5
from flask import request
from secrets import token_hex
from fuxi.database import MongoDB, T_ADMIN
from flask_restful import Resource, reqparse
from sqlalchemy.exc import OperationalError
from fuxi.libs.data.error import API_FAILED
from fuxi.libs.common.logger import logger
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from fuxi.libs.core.token import access_token

parser = reqparse.RequestParser()
parser.add_argument('username', type=str)
parser.add_argument('password', type=str)
parser.add_argument('expiration', type=bool)
parser.add_argument('uid', type=int)
parser.add_argument('nick', type=str)
parser.add_argument('email', type=str)


class GetToken(Resource):
    @staticmethod
    def get():
        return None

    @staticmethod
    def post():
        """
        接收 username password 判断用户是否合法
        POST /api/v1/token
        :return: 返回 token
        """
        try:
            # 获取请求 ip 后期改造成从 Nginx 上获取真实 ip
            req_ip = request.remote_addr
            args = parser.parse_args()
            username = args['username']
            password = args['password']
            expiration = args['expiration']
            auth_res = auth(username, password)
            if auth_res:
                # 勾选超时时间后 token 过期时间设置成 15 天 （默认一小时）
                if expiration:
                    e_date = 3600 * 24 * 15
                else:
                    e_date = 3600
                data = {
                    'username': username,
                    'nick': auth_res['nick'],
                    'email': auth_res['email'],
                    'authority': auth_res['authority'],
                }
                token = generate_auth_token(data, e_date)
                logger.success("{} {} authentication success".format(req_ip, username))
                return {'code': 10200, 'status': 'success', 'message': 'Login successful', 'data': {"token": token}}
            else:
                logger.warning("{} authentication failed: {} {}".format(req_ip, username, password))
                return {'code': 10501, 'status': 'failed', 'message': 'Invalid username or password', 'data': ''}
        except OperationalError:
            # 捕获数据库连接错误
            logger.error("OperationalError: can't connect to database server")
            return {'code': 10511, 'status': 'failed', 'message': "Can't connect to database server", 'data': ''}
        except Exception as e:
            logger.error("generate token error {}".format(e))
            return {'code': 10501, 'status': 'failed', 'message': API_FAILED}


class AddAdmin(Resource):
    @access_token
    def post(self):
        try:
            args = parser.parse_args()
            nick = args['nick']
            username = args['username']
            password = args['password']
            email = args['email']
            if not MongoDB(T_ADMIN).find_one({"username": username}):
                salt = token_hex()[8:16]
                md5_passwd = create_md5(password, salt)
                MongoDB(T_ADMIN).insert_one({
                    "username": username,
                    "password": md5_passwd,
                    "salt": salt,
                    "nick": nick if nick else username,
                    "email": email if email else "",
                    "authority": [],
                    "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                })
                return {'code': 10200, 'status': 'success', 'message': 'Add successful'}
            else:
                return {'code': 10403, 'status': 'failed', 'message': 'Username already exists'}
        except Exception as e:
            logger.error("add admin failed: {}".format(e))
            return {'code': 10500, 'status': 'failed', 'message': API_FAILED}


def generate_auth_token(data, expiration):
    """
    生成 token
    :param data: token 内包含的数据
    :param expiration: token 过期时间
    :return: token
    """
    try:
        secret_key = app.config.get('SECRET_KEY')
        s = Serializer(secret_key, expires_in=expiration)
        # Python3 生成的是 byte 类型 需要 decode 成 str
        b_token = s.dumps(data).decode()
        return b_token
    except Exception as e:
        logger.error("generate token failed: {}".format(e))


def auth(username, password):
    item = MongoDB(T_ADMIN).find_one({"username": username})
    if item:
        if item['password'] == create_md5(password, item['salt']):
            return item
    return {}


def create_md5(pwd, salt):
    md5_obj = md5()
    # Unicode-objects must be encoded before hashing
    md5_obj.update("{}{}".format(pwd, salt).encode('utf-8'))
    return md5_obj.hexdigest()
