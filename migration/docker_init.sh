#!/bin/bash

sed -i 's/bind 127.0.0.1 ::1/bind 127.0.0.1/' /etc/redis/redis.conf
service mongodb restart
service redis-server restart
cp /opt/fuxi/instance/_config.py /opt/fuxi/instance/config.py
cd /opt/fuxi
nohup python3.7 fuxi_manage.py >> /data/log/fuxi_web.txt 2>&1 &
nohup celery worker -A fuxi_celery_worker.celery >> /data/log/fuxi_celery.txt 2>&1 &
sleep 5

/bin/bash