#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-6-19
# @File    : hydra_plugin.py
# @Desc    : ""

import subprocess
import threading
import shlex


class HydraScanner:

    def __init__(self, target, service, username, password, args):
        self.target = target
        self.service = service
        self.username = username
        self.password = password
        self.args = args
        self.result = {
            "target": target,
            "service": service,
            "username": username,
            "password": password,
        }

    def _args(self):
        command = ['hydra', '-t 1', '-w 10', '-l', self.username,
                   '-p', self.password, self.target, self.service]
        command += shlex.split(self.args)
        return command

    def scanner(self):
        try:
            hydra_out = subprocess.Popen(self._args(), stdout=subprocess.PIPE)
            output = hydra_out.stdout.read()
            time_out = threading.Timer(1200, hydra_out.kill)
            time_out.start()
            hydra_out.wait()
            time_out.cancel()
            if 'successfully' in output and "[" + self.service + "]" in output:
                return self.result
        except Exception as e:
            raise e

    def host_check(self):
        try:
            hydra_out = subprocess.Popen(self._args(), stdout=subprocess.PIPE)
            output = hydra_out.stdout.read()
            time_out = threading.Timer(1200, hydra_out.kill)
            time_out.start()
            hydra_out.wait()
            time_out.cancel()
            if 'waiting for children to finish' not in output and 'completed' in output and 'password' in output:
                return self.target
        except Exception as e:
            raise e

