#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/7/5
# @File    : user.py
# @Desc    : ""

import os
import time
import hashlib
from secrets import token_hex
from fuxi.common.utils.logger import logger
from fuxi.core.databases.db_mongo import mongo, T_ADMIN
from fuxi.core.databases.orm.db_error import DatabaseError


class _DBFuxiAdmin:
    def __init__(self):
        self.table = T_ADMIN
        self.urandom_count = 16

    def find_one(self):
        return mongo[self.table].find_one()

    def add_admin(self, username, password, role=0, nick=None, email=None):
        if not self._user_check(username):
            raise DatabaseError("username already exists")
        if username and password:
            try:
                salt = token_hex()[8:16]
                item = mongo[self.table].insert_one({
                    "username": username,
                    "salt": salt,
                    "password": self.hash_md5(password, salt),
                    "role": role,
                    "token": self.generate_token(),
                    "nick": nick if nick else username,
                    "email": email if email else "admin@fuxi.com",
                    "date": int(time.time())
                })
                return item
            except Exception as e:
                logger.error("admin insert failed: {} {}".format(username, e))
                return False
        else:
            logger.error("admin insert failed: invalid data")
            return False

    def _user_check(self, username):
        if mongo[self.table].find_one({"username": username}):
            return False
        return True

    def refresh_token(self, username, password):
        if self.passwd_check(username, password):
            token = self.generate_token()
            mongo[self.table].update_one({"username": username}, {"$set": {"token": token}})
            return token
        else:
            return ""

    def get_token(self, username, password):
        if self.passwd_check(username, password):
            return mongo[self.table].find_one({"username": username}, {"token": 1})['token']
        else:
            return ""

    def passwd_check(self, username, password):
        item = mongo[self.table].find_one({"username": username})
        if item:
            if item['password'] == self.hash_md5(password, item['salt']):
                return True
        raise DatabaseError("username or password is incorrect")

    def token_check(self, token):
        if mongo[self.table].find_one({"token": str(token)}):
            return True
        else:
            return False

    def generate_token(self):
        return hashlib.sha1(os.urandom(self.urandom_count)).hexdigest()

    def get_user_info_by_token(self, token):
        if self.token_check(token):
            return mongo[self.table].find_one(
                {"token": token}, {"username": 1, "nick": 1, "email": 1}
            )
        else:
            raise DatabaseError("the access token is invalid")

    @staticmethod
    def hash_md5(password, salt):
        md5_obj = hashlib.md5()
        md5_obj.update("{}{}".format(password, salt).encode('utf-8'))
        return md5_obj.hexdigest()


DBFuxiAdmin = _DBFuxiAdmin()

