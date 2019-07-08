#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/22
# @File    : celery_worker.py
# @Desc    : "celery worker -A fuxi_celery_worker --loglevel=info"

from datetime import timedelta
from fuxi.web.flask_app import flask_app, fuxi_celery
from fuxi.core.tasks.scanner.poc_task import schedule_poc_scanner

flask_app.app_context().push()
beat_schedule = {
    'poc_scanner_loop_1': {
        'task': "fuxi.tasks.scanner.poc_task.schedule_poc_scanner",
        'schedule': timedelta(seconds=60),
    },
}
fuxi_celery.conf.beat_schedule.update(beat_schedule)

celery = fuxi_celery
