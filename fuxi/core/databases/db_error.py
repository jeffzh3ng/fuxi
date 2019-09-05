#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/7/6
# @File    : db_error.py
# @Desc    : ""


class DatabaseError(Exception):
    def __init__(self, error):
        super().__init__(self)
        self.error = error

    def __str__(self):
        return self.error
