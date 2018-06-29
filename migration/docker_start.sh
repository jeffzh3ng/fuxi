#!/bin/bash

nohup mongod --dbpath=/data > db_log 2>&1 &
nohup mongo --eval "db.getSiblingDB('fuxi').createUser({user:'fuxi_scanner',pwd:'W94MRYDqOZ',roles :[{role:'readWrite',db: 'fuxi'}]});" > db_log.log 2>&1 &

python /opt/fuxi/migration/db_init.py
nohup python /opt/fuxi/fuxi_scanner.py > /data/log.log 2>&1 &

/bin/bash