#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/25
# @File    : discovery_task.py
# @Desc    : ""

import re
import time
from fuxi import fuxi_celery
from fuxi.databases import db, FuxiDiscoveryTask
from fuxi.tasks.discovery.port_scanner import NetworkPortScanner
from fuxi.common.utils.logger import logger


class Discovery:
    def __init__(self, task_id, target_list, plugin_list):
        self.task_id = task_id
        self.target_list = target_list
        self.plugin_list = plugin_list
        self.host_list = []
        self.domain_list = []

    def target_parser(self):
        # 一堆正则
        _re_ip = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        _re_ips = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$')
        _re_ipf = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}$')
        _re_url = re.compile('[^\s]*.[a-zA-Z]')
        for target in self.target_list:
            # 通过正则对目标进行分类处理 最终返回域名列表及 host 列表
            try:
                if _re_ips.match(target):
                    self.host_list.append(target)
                else:
                    if "http" == target[0:4]:
                        target = target.replace("http://", "").replace("https://", "")
                    if ":" in target:
                        target = target.split(":")[0]
                    if "/" in target:
                        target = target.split("/")[0]

                    if _re_ip.match(target):
                        self.host_list.append(target)
                    if _re_ipf.match(target):
                        self.host_list.append(target)
                    if _re_url.match(target):
                        self.host_list.append(target)
                        self.domain_list.append(".".join(target.split('.')[-2:]))
            except Exception as e:
                logger.error("target parser failed: {} {}".format(target, e))

    def run(self):
        self.target_parser()
        # 根据插件进行调度
        if "NetworkPortScanner" in self.plugin_list:
            s = NetworkPortScanner(self.task_id, self.host_list)
            # s = NetworkPortScanner(self.task_id, self.host_list, port_list)
            s.run()


@fuxi_celery.task()
def t_discovery_task(task_id):
    """
    通过 task_id 获取任务信息进行扫描调度
    :param task_id:
    :return:
    """
    try:
        t_item = FuxiDiscoveryTask.query.filter_by(t_id=task_id).first()
        target = t_item.target.split('\n')
        plugin = t_item.plugin.split(',')
        t_item.status = "running"
        db.session.add(t_item)
        db.session.commit()
        logger.success("{} discovery task running".format(task_id))
        try:
            # 调用扫描器
            discovery = Discovery(task_id, target, plugin)
            discovery.run()
        except Exception as e:
            logger.error("discovery scanner error: {}".format(e))
        # 扫描完成后更改任务信息
        t_item.status = "completed"
        t_item.end_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db.session.add(t_item)
        db.session.commit()
        logger.success("{} discovery task completed".format(task_id))
    except Exception as e:
        logger.error("{} discovery task failed: {}".format(task_id, e))
