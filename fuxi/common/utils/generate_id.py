#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/21
# @File    : generate_id.py
# @Desc    : ""

import hashlib
import time
import random
from string import ascii_letters, digits


def generate_id():
    seed = str(time.time()) + ''.join(random.sample(ascii_letters + digits, 16))
    _id = hashlib.md5(seed.encode(encoding='UTF-8')).hexdigest()[8:-8]
    return _id
