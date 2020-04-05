#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/22
# @File    : celery_worker.py
# @Desc    : "celery worker -A fuxi_celery_worker --loglevel=info"

from datetime import timedelta
from fuxi.web.flask_app import flask_app, fuxi_celery
from fuxi.core.tasks.scanner.poc_task import schedule_poc_scanner
from fuxi.core.tasks.discovery.port_scan_task import t_port_scan
from fuxi.core.tasks.discovery.whatweb_task import t_whatweb_task
from fuxi.core.tasks.discovery.subdomain_task import t_subdomain_task
from fuxi.core.tasks.scanner.sqlmap_task import t_sqlmap_task
from fuxi.core.tasks.tools.system import t_schedule_update_system_info

flask_app.app_context().push()
beat_schedule = {
    'poc_scanner_loop_1': {
        'task': "fuxi.core.tasks.scanner.poc_task.schedule_poc_scanner",
        'schedule': timedelta(seconds=60),
    },
    'system_info_loop_1': {
        'task': "fuxi.core.tasks.tools.system.t_schedule_update_system_info",
        'schedule': timedelta(seconds=60 * 3),
    },
}

fuxi_celery.conf.beat_schedule.update(beat_schedule)
fuxi_celery.conf.timezone = 'UTC'
celery = fuxi_celery
