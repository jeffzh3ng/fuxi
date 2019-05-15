#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/22
# @File    : celery_worker.py
# @Desc    : "celery worker -A celery_worker.celery --loglevel=info"

from datetime import timedelta
from fuxi import app, fuxi_celery
from fuxi.tasks.scanner.poc_task import t_poc_scanner, schedule_poc_scanner

app.app_context().push()
beat_schedule = {
    'poc_scanner_loop_1': {
        'task': "fuxi.tasks.scanner.poc_task.schedule_poc_scanner",
        'schedule': timedelta(seconds=60),
    },
}
fuxi_celery.conf.beat_schedule.update(beat_schedule)

celery = fuxi_celery
