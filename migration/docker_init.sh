#!/bin/bash

sed -i 's/bind 127.0.0.1 ::1/bind 127.0.0.1/' /etc/redis/redis.conf
sed -i "s/dbpath=.*/dbpath=\/data\/mongodb/" /etc/mongodb.conf
cp /opt/fuxi/instance/_config.py /opt/fuxi/instance/config.py
sed -i "s/LOGGER_PAT.*/LOGGER_PATH=\'\/data\/logs\'/" /opt/fuxi/instance/config.py
mkdir -p /data/mongodb /data/log /data/logs
chmod -R a+wr /data/mongodb
service mongodb restart
service redis-server restart
cd /opt/fuxi
nohup python3.7 fuxi_manage.py >> /data/log/fuxi_web.txt 2>&1 &
nohup celery worker -A fuxi_celery_worker.celery -B >> /data/log/fuxi_celery.txt 2>&1 &

/bin/bash