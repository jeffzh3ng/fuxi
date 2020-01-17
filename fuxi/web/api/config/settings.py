#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/1/17
# @File    : settings.py
# @Desc    : ""

from flask import session
from flask_restful import Resource, reqparse
from fuxi.core.auth.token import auth
from fuxi.core.data.response import Response
from fuxi.common.utils.time_format import timestamp_to_str
from fuxi.core.databases.orm.auth.user_orm import DBFuxiAdmin
from fuxi.common.utils.logger import logger

parser = reqparse.RequestParser()
parser.add_argument('username', type=str)
parser.add_argument('password', type=str)
parser.add_argument('nick', type=str)
parser.add_argument('email', type=str)


class ConfigManageV1(Resource):
    @auth
    def get(self):
        """
        GET /api/v1/settings
        :return:
        """
        try:
            print("ss")
            return Response.success()
        except Exception as e:
            msg = "setup configuration failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg)


class AccountManageV1(Resource):
    @auth
    def get(self):
        data = []
        try:
            items = DBFuxiAdmin.get_user_list()
            for item in items:
                item['uid'] = str(item['_id'])
                item['date'] = timestamp_to_str(item['date'])
                if item['role'] == 0:
                    item['role'] = "admin"
                else:
                    item['role'] = "user"
                del item['_id']
                data.append(item)
            return Response.success(data=data)
        except Exception as e:
            msg = "setup configuration failed: {}".format(e)
            logger.warning(msg)
            return Response.failed(message=msg, data=data)

    @auth
    def delete(self, uid):
        try:
            if session.get("authority") == 0 and not DBFuxiAdmin.is_admin(uid):
                DBFuxiAdmin.delete_by_id(uid)
                return Response.success(message="successfully deleted")
            else:
                return Response.failed(message="Delete user failed: Permission denied")
        except Exception as e:
            msg = "delete user failed: {} {}".format(uid, e)
            logger.warning(msg)
            return Response.failed(message=msg)

    @auth
    def put(self, uid):
        try:
            if session.get("authority") != 0:
                return Response.failed(message="Failed to modify user information: Permission denied")
            args = parser.parse_args()
            username = args['username']
            nick = args['nick']
            email = args['email']
            DBFuxiAdmin.update_by_id(uid, {
               "username": username,
               "nick": nick,
               "email": email,
            })
            return Response.success(message="Modify user information successfully")
        except Exception as e:
            logger.warning("failed to modify user information: {}".format(e))
            return Response.failed(message=e)
