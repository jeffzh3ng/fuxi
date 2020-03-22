#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/3/21
# @File    : subdomain_task.py
# @Desc    : ""

import concurrent.futures
import os
import time
from xml.etree.ElementTree import parse
from fuxi.common.utils.logger import logger
# from fuxi.common.thirdparty.sublist3r import sublist3r
from fuxi.common.thirdparty.wydomain import dnsburte
from fuxi.core.databases.orm.discovery.subdomain_orm import DBSubdomainTask, DBSubdomainResult
from fuxi.core.databases.orm.discovery.whatweb_orm import DBWebFingerPrint
from fuxi.web.flask_app import fuxi_celery
from fuxi.core.tasks.discovery.whatweb_task import WhatwebScanner
from fuxi.common.thirdparty.theHarvester.fuxi_plugin import fuxi_theharvester

def theharvester_xml_parse(filepath):
    result = []
    _res_subdomain = []
    doc = parse(filepath)
    for item in doc.iterfind('host'):
        if item.text:
            if item.text not in _res_subdomain:
                result.append({"subdomain": item.text, "ip": "0.0.0.0"})
                _res_subdomain.append(item.text)
        elif item.findtext('hostname'):
            if item.findtext('hostname') not in _res_subdomain:
                _res_subdomain.append(item.findtext('hostname'))
                result.append({
                    "subdomain": item.findtext('hostname'),
                    "ip": str(item.findtext('ip')).split(",")[0] if item.findtext('ip') else "0.0.0.0"
                })
    return result


def subdomain_scanner(domain, brute=False, threads=30):
    subdomains = []
    _subdomain_temp = []
    filepath = fuxi_theharvester(domain)
    if os.path.exists(filepath):
        for item in theharvester_xml_parse(filepath):
            if item['subdomain'] not in _subdomain_temp:
                _subdomain_temp.append(item['subdomain'])
                subdomains.append({"subdomain": item['subdomain'], "ip": item['ip']})
    if brute:
        brute_sub = dnsburte.run(domain=domain, threads=threads)
        for item in brute_sub:
            if item not in _subdomain_temp:
                subdomains.append({"subdomain": item, "ip": "0.0.0.0"})
                _subdomain_temp.append(item)
    return subdomains


def subdomain_web_info(subdomain_list, threads):
    if threads > 16:
        threads = 16
    try:
        scanner = WhatwebScanner()
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as threat_pool:
            future_dict = {
                threat_pool.submit(
                    scanner.run, [str(subdomain)], 1, 10, None, None, None, None
                ): subdomain for subdomain in subdomain_list
            }
            for future in concurrent.futures.as_completed(future_dict):
                url = future_dict[future]
                res = future.result()
                for i in res:
                    update_subdomain_web_info(str(url), i['title'], i['ip'], i['http_status'])
    except Exception as e:
        logger.warning("query subdomain info failed: {}".format(e))


def update_subdomain_web_info(subdomain, title, ip, response):
    data = {"title": title, "ip": ip, "response": response}
    try:
        DBSubdomainResult.update_web_info(subdomain, data)
    except Exception as e:
        logger.warning("update subdomain web info failed: {}".format(e))


def save_whatweb_data(data):
    try:
        DBWebFingerPrint.add_multiple(data)
    except Exception as e:
        logger.warning("save subdomain whatweb data failed: {}".format(e))


@fuxi_celery.task()
def t_subdomain_task(task_id, res_return=False):
    data = []
    try:
        _item = DBSubdomainTask.find_by_id(task_id)
        target = _item['target']
        brute = _item['brute']
        threads = _item['threads']
        get_info = _item['info']
        DBSubdomainTask.update_by_id(task_id, {
            "status": "running"
        })
        try:
            for domain in target:
                temp_save_data = []
                subdomain_list = subdomain_scanner(domain, brute, threads)
                for item in subdomain_list:
                    temp_save_data.append({
                        "task_id": str(task_id),
                        "domain": domain,
                        "subdomain": item['subdomain'],
                        "title": "-",
                        "ip": item['ip'],
                        "response": 0,
                    })
                try:
                    DBSubdomainResult.add_multiple(temp_save_data)
                except Exception as e:
                    logger.warning("save subdomain failed: {}".format(e))
                if get_info:
                    subdomain_domain_list = [subdomain['subdomain'] for subdomain in subdomain_list]
                    subdomain_web_info(subdomain_domain_list, threads)
        except Exception as e:
            logger.warning("start whatweb failed: {}".format(e))
        DBSubdomainTask.update_by_id(task_id, {
            "status": "completed",
            "end_date": int(time.time())
        })
        logger.success("subdomain: {} the task completed".format(task_id))
    except Exception as e:
        logger.warning("{} start subdomain task failed: {}".format(task_id, e))
    return data if res_return else []
