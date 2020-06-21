#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/25
# @File    : port_scan_task.py
# @Desc    : ""

import re
import time
from datetime import datetime
from fuxi.common.libs.nmap import PortScanner
from fuxi.web.flask_app import fuxi_celery
from fuxi.core.databases.orm.discovery.port_orm import DBPortScanTasks, DBPortScanResult
from fuxi.common.utils.logger import logger


class Scanner(object):
    """
    Invoking nmap
    :parameter
    task_id: make the result
    target_list: target (list)
    port_list: port (list)
    option: nmap options (string)
    """
    def __init__(self, task_id, target_list, port_list, option):
        self.task_id = task_id
        self.target_list = target_list
        self.port = port_list
        # self.port = port_list if port_list else []
        self.option = option
        self.result = []

    def run(self):
        start_time = datetime.now()
        scanner = PortScanner()
        for target in self.target_list:
            try:
                logger.info("starting port scan: {}".format(target))
                # add the -p parameter if the port is defined
                if self.port:
                    if not self.option:
                        # scanner.scan(target, arguments='-p {}'.format(
                        #     ",".join(map(str, self.port))
                        # ))
                        scanner.scan(target, arguments='-p {}'.format(self.port))
                    else:
                        _option = " -p {}".format(self.port)
                        # self.option += " -p {}".format(
                        #     ",".join(map(str, self.port))
                        # )
                        scanner.scan(target, arguments=_option)
                else:
                    if not self.option:
                        scanner.scan(target)
                    else:
                        scanner.scan(target, arguments=self.option)
                logger.info("port scan command line: {}".format(scanner.command_line()))
                for host in scanner.all_hosts():
                    _detail = []
                    _port = []
                    for port in scanner[host].all_tcp():
                        if scanner[host]['tcp'][port]['state'] == 'open':
                            _port.append(port)
                            _detail.append({
                                "port": port, "detail": scanner[host]['tcp'][port]
                            })
                    self.result.append({
                        'task_id': self.task_id,
                        'host': host, 'hostname': scanner[host].hostname(), "port": _port, 'detail': _detail
                    })
            except Exception as e:
                logger.warning("the port scan task failed: {} {}".format(target, e))
        time_m, time_s = divmod((datetime.now() - start_time).seconds, 60)
        time_h, time_m = divmod(time_m, 60)
        if time_h:
            logger.success("the port scan completed: {}".format("%dh %02dm %02ds" % (time_h, time_m, time_s)))
        elif time_m:
            logger.success("the port scan completed: {}".format("%02dm %02ds" % (time_m, time_s)))
        else:
            logger.success("the port scan completed: {}".format("%02ds" % time_s))
        return self.result


class NetworkPortScanner(Scanner):
    def __init__(self, task_id, target_list, port_list, option):
        super().__init__(task_id, target_list, port_list, option)

    def target_filter(self):
        # filter illegal target
        new_target_list = []
        _re_ip = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        _re_ips = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$')
        _re_ipf = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}$')
        _re_url = re.compile('[^\s]*.[a-zA-Z]')
        for target in self.target_list:
            try:
                if _re_ips.match(target):
                    new_target_list.append(target)
                else:
                    if "http" == target[0:4]:
                        target = target.replace("http://", "").replace("https://", "")
                    if ":" in target:
                        target = target.split(":")[0]
                    if "/" in target:
                        target = target.split("/")[0]
                    if _re_ip.match(target):
                        new_target_list.append(target)
                    if _re_ipf.match(target):
                        new_target_list.append(target)
                    if _re_url.match(target):
                        new_target_list.append(target)
            except Exception as e:
                logger.warning("target filter failed: {} {}".format(target, e))
        return new_target_list

    def scan(self):
        self.target_list = self.target_filter()
        return self.run()


@fuxi_celery.task()
def t_port_scan(task_id):
    """
    :param task_id: get the task information
    :return:
    """
    try:
        _item = DBPortScanTasks.find_by_id(task_id)
        target = _item['target']
        port_list = _item['port']
        option = _item['option']
        DBPortScanTasks.update_by_id(task_id, {
            "status": "running"
        })
        logger.success("{} starting network port scan task".format(task_id))
        try:
            # invoking NetworkPortScanner
            scanner = NetworkPortScanner(task_id, target, port_list, option)
            res = scanner.scan()
            DBPortScanResult.add_multiple(res)
        except Exception as e:
            logger.warning("network port scan error: {}".format(e))
        # change the task status information after the task completes
        DBPortScanTasks.update_by_id(task_id, {
            "status": "completed",
            "end_date": int(time.time())
        })
        logger.success("{} network port scan task completed".format(task_id))
    except Exception as e:
        logger.warning("{} network port scan failed: {}".format(task_id, e))

