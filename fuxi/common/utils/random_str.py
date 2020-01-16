#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/21
# @File    : generate_id.py
# @Desc    : ""

import random


def random_str(length=12):
    seed = "1234567890abcdefghijklmnopqrstuvwxyz"
    return ''.join(random.sample(seed, length))
