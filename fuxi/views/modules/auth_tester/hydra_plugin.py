#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-6-19
# @File    : hydra_plugin.py
# @Desc    : ""

from subprocess import PIPE, Popen


class HydraScanner:

    def __init__(self, args):
        if '-s' in args:
            self.target = args[-2] + ':' + args[args.index('-s') + 1]
        else:
            self.target = args[-2]
        self.service = args[-1]
        if '-l' in args:
            self.username = args[args.index('-l') + 1]
        else:
            self.username = 'None'
        if '-p' in args:
            self.password = args[args.index('-p') + 1]
        else:
            self.password = 'None'
        self.args = args

    def scanner(self):
        process = Popen(self.args, stdout=PIPE, stderr=PIPE)
        try:
            (stdout, stderr) = process.communicate()
            if 'successfully' in stdout and "[" + self.service + "]" in stdout:
                result = {
                    "target": self.target,
                    "service": self.service,
                    "username": self.username,
                    "password": self.password,
                }
                return result
        except Exception as e:
            process.kill()
            print(process, e)
            return False

    def host_check(self):
        process = Popen(self.args, stdout=PIPE, stderr=PIPE)
        try:
            (stdout, stderr) = process.communicate()
            if "successfully" in stdout and self.target in stdout:
                return {"target": self.target, "result": {'username': self.username, "password": self.password}}
            elif 'can not connect' in stderr:
                return False
            elif 'waiting for children to finish' in stdout:
                return False
            else:
                return {"target": self.target, "result": ""}
        except Exception as e:
            process.kill()
            print(process, e)
            return False

