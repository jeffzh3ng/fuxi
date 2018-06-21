#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-6-19
# @File    : hydra_plugin.py
# @Desc    : ""

import subprocess
import threading


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
        msg = '[*] ' + self.target + '  ' + self.service + '  ' + self.username + '  ' + self.password
        print(msg)
        try:
            hydra_out = subprocess.Popen(self.args, stdout=subprocess.PIPE)
            output = hydra_out.stdout.read()
            time_out = threading.Timer(1200, hydra_out.kill)
            time_out.start()
            hydra_out.wait()
            time_out.cancel()
            if 'successfully' in output and "[" + self.service + "]" in output:
                result = {
                    "target": self.target,
                    "service": self.service,
                    "username": self.username,
                    "password": self.password,
                }
                return result
        except Exception as e:
            raise e

    def host_check(self):
        try:
            hydra_out = subprocess.Popen(self.args, stdout=subprocess.PIPE)
            output = hydra_out.stdout.read()
            time_out = threading.Timer(1200, hydra_out.kill)
            time_out.start()
            hydra_out.wait()
            time_out.cancel()
            if 'waiting for children to finish' not in output and 'completed' in output and 'password' in output:
                return self.target
        except Exception as e:
            raise e

