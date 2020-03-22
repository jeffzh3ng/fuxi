#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/01/13
# @File    : whatweb.py 
# @Desc    : ""

import random
import os
import re
import json
import subprocess
from tempfile import gettempdir

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Fuxi/2.0"


class Whatweb(object):

    def __init__(self, exe):
        """
        :parameter
        exe[string]: whatweb path
        example: whatweb, /usr/bin/whatweb, /usr/local/bin/whatweb ...
        """
        self.input_file = ""
        self.output_file = ""
        self.exe = exe
        self.target = ""
        self.threads = 25
        self.level = 3
        self.option = ""
        self.result = []
        self.command = self.command = "{} -q --no-errors".format(self.exe)
        self.timeout = 5

    def whatweb(self, target, level=3, threads=25, timeout=5, option=""):
        """
        :parameter
        target[list]: URLs, IP or IP ranges in CIDR, x.x.x-x, or x.x.x.x-x.x.x.x format.
        threat: Number of simultaneous threads. Default: 25
        level: The aggression level. Default: 3. (1 3 4)
        option: custom configuration. Default: none (whatweb -h)
        """
        if not self._check_whatweb_exe():
            raise Error("command not found: {}".format(self.exe))
        self.target = target
        if type(self.target) != list:
            raise Error("'target' must be of list type")
        self.threads = threads
        self.level = level
        self.option = option
        self.timeout = timeout
        try:
            # Starting whatweb
            return self._scanner()
        except Exception as error:
            raise Error(error)
        finally:
            # delete temporary files at the end of the task
            if os.path.exists(self.input_file):
                os.remove(self.input_file)
            if os.path.exists(self.output_file):
                os.remove(self.output_file)

    def _scanner(self):
        self.input_file = self._save_target_to_file()
        self.output_file = self._exec()
        res_json = self._result_load()
        try:
            self.result = self._json_to_dict(res_json)
        except Exception as err:
            print("whatweb: json parse failed: {}".format(err))
        return self.result

    def _check_whatweb_exe(self):
        # whatweb --version
        # WhatWeb version 0.5.1
        re_compile = re.compile('WhatWeb version ([\d]+)\.([\d]+)(?:\.([\d])+)')
        subp = subprocess.run("{} --version".format(self.exe), shell=True, encoding="utf-8",
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True if subp.stdout and re_compile.match(subp.stdout) else False

    def _exec(self):
        # random output file name
        output = "{}/whatweb_{}.output".format(gettempdir(), random_str())
        self.command = "{} -i {} --log-json {} --max-threads {} -a {}".format(
            self.command, self.input_file, output, self.threads, self.level
        )
        if "open-timeout" not in self.command:
            self.set_timeout(self.timeout)
        if "user-agent" not in self.command:
            self.set_useragent()
        self.set_option(self.option)
        subprocess.run(self.command, shell=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output

    def _result_load(self):
        if not os.path.exists(self.output_file):
            raise Error("whatweb output error: no such file {}".format(self.output_file))
        with open(self.output_file, 'r') as f:
            file_str = f.read()
            if not file_str:
                # raise Error("the output is null: {}".format(self.output_file))
                return []
            try:
                item = json.loads(file_str)
                return item
            except Exception as error:
                raise Error("json parsing failed: {}".format(error))

    def _save_target_to_file(self):
        # random input file name
        input_file = "{}/whatweb_{}.input".format(gettempdir(), random_str())
        with open(input_file, 'w') as f_write:
            f_write.write("\n".join(self.target).strip())
        return input_file

    def _json_to_dict(self, data):
        # data: json loads file
        # summary = "Script, Python[3.7.5], HTTPServer[Werkzeug/0.15.6 Python/3.7.5]"
        for item in data:
            if not item:
                continue
            target = item["target"] if item.get("target") else ""
            http_status = item["http_status"] if item.get("http_status") else 0
            _request_config = item["request_config"] if item.get("request_config") else {}
            request = {}
            if _request_config:
                for first_key in _request_config:
                    s = ""
                    if type(_request_config[first_key]) == dict:
                        for second_key in _request_config[first_key]:
                            s += "{}: {} | ".format(str(second_key), str(_request_config[first_key][second_key]))
                    else:
                        s = str(_request_config[first_key])
                    request[first_key] = s.strip(' | ')
            title = ""
            country = ""
            c_code = ""
            ip = "0.0.0.0"
            summary = ""
            fp = []
            plugin = item.get("plugins")
            if plugin:
                for first_key in plugin:
                    if first_key == "Title":
                        title = plugin['Title']['string'][0] if plugin['Title'].get("string") else ""
                        continue
                    if first_key == "Country":
                        country = plugin['Country']['string'][0] if plugin['Country'].get("string") else ""
                        c_code = plugin['Country']['module'][0] if plugin['Country'].get("module") else ""
                        continue
                    if first_key == "IP":
                        ip = plugin['IP']['string'][0] if plugin['IP'].get("string") else ""
                        continue
                    if plugin[first_key]:
                        s = ""
                        for second_key in plugin[first_key]:
                            if plugin[first_key][second_key]:
                                if type(plugin[first_key][second_key]) == list:
                                    second_string = plugin[first_key][second_key][0]
                                else:
                                    second_string = plugin[first_key][second_key]
                                s += "{} ".format(second_string)
                            else:
                                s += "{} ".format("unknown")
                        # fix a bug, for better queries
                        fp.append({"plugin": first_key, "string": s.strip().lower()})
                    else:
                        fp.append({"plugin": first_key, "string": ""})
            for _plugin in fp:
                if _plugin.get("string"):
                    summary += "{}[{}]||".format(_plugin['plugin'], _plugin['string'])
                else:
                    summary += "{}||".format(_plugin['plugin'])
            self.result.append({
                "target": target.strip("/"), "http_status": http_status, "title": title,
                "country": country, "c_code": c_code, "ip": ip,
                "summary": summary.strip("||"),
                "request": request,
                "fingerprint": fp
            })
        return self.result

    def plugin_module(self, plugin):
        # +++ developing +++
        pass

    def set_cookie(self, cookie_path):
        # read cookies from a file.
        self.command = "{} --cookie-jar {}".format(
            self.command, cookie_path
        )

    def set_timeout(self, timeout):
        self.command = "{} --read-timeout {} --open-timeout {}".format(
            self.command, timeout, timeout
        )

    def set_header(self, header):
        # eg "Foo:Bar"
        self.command = "{} --header {}".format(
            self.command, header
        )

    def set_plugin(self, plugin_list):
        # +++ developing +++
        plugin = ",".join(plugin_list)
        self.command = "{} -p {}".format(self.command, plugin)

    def set_option(self, option):
        if option:
            self.command = "{} {}".format(
                self.command, option
            )

    def set_useragent(self, useragent=None):
        if not useragent:
            useragent = USER_AGENT
        self.command = "{} --user-agent '{}'".format(
            self.command, useragent
        )


class Error(Exception):
    pass


def random_str(length=12):
    seed = "1234567890abcdefghijklmnopqrstuvwxyz"
    return ''.join(random.sample(seed, length))


if __name__ == '__main__':
    a = Whatweb("/usr/local/bin/whatweb")
    try:
        a.set_timeout(3)
        # a.set_plugin(['Zotonic'])
        a.set_useragent("haha")
        a.whatweb(['crm.joyoung.com'], level=3)
        print(a.command)
        print(a.result)
    except Exception as e:
        print(a.command)
        print(e)
