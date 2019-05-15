#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/25
# @File    : port_scanner.py
# @Desc    : ""

from datetime import datetime
from fuxi.libs.common.nmap import PortScanner
from fuxi.libs.common.logger import logger


class NetworkPortScanner:
    """
    直接调 nmap 扫描
    传入的 task_id 是为了标记扫描结果
    端口列表默认为空（直接采用nmap默认端口）指定端口扫描需要传入 list
    """
    def __init__(self, target_list, port_list=None):
        self.target_list = target_list
        self.port = port_list if port_list else []
        self.result = []

    def run(self):
        start_time = datetime.now()
        scanner = PortScanner()
        for target in self.target_list:
            try:
                logger.info("start port scanning: {}".format(target))
                # 采用哪些端口扫描 在这里做判断
                if self.port:
                    scanner.scan(target, arguments='-p {}'.format(
                        ",".join(map(str, self.port))
                    ))
                else:
                    scanner.scan(target)
                logger.info("command line: {}".format(scanner.command_line()))
                for host in scanner.all_hosts():
                    data = []
                    for port in scanner[host].all_tcp():
                        if scanner[host]['tcp'][port]['state'] == 'open':
                            data.append({
                                'port': port,
                                'res': scanner[host]['tcp'][port]
                            })
                    if data:
                        self.result.append({'host': host, 'hostname': scanner[host].hostname(), 'data': data})
            except Exception as e:
                logger.error("port scan failed: {} {}".format(target, e))
        time_m, time_s = divmod((datetime.now() - start_time).seconds, 60)
        time_h, time_m = divmod(time_m, 60)
        if time_h:
            logger.success("port scan completed: {}".format("%dh %02dm %02ds" % (time_h, time_m, time_s)))
        elif time_m:
            logger.success("port scan completed: {}".format("%02dm %02ds" % (time_m, time_s)))
        else:
            logger.success("port scan completed: {}".format("%02ds" % time_s))
        return self.result


def port_scanner(t_id, target):
    x = NetworkPortScanner(target)
    result = x.run()
    print(result)


if __name__ == '__main__':
    port_scanner('ss', ['127.0.0.1'])
