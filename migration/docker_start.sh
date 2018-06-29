#!/bin/bash

if [ ! -d "/data/pocsuite_plugin" ]; then
  mkdir /data/pocsuite_plugin -p
fi

nohup mongod --dbpath=/data > db_log 2>&1 &
sed -i "s:basedir + '/../fuxi/views/modules/scanner/pocsuite_plugin/':'/data/pocsuite_plugin/':g" /opt/fuxi/instance/config.py
sleep 8
mongo --eval "db.getSiblingDB('fuxi').createUser({user:'fuxi_scanner',pwd:'W94MRYDqOZ',roles :[{role:'readWrite',db: 'fuxi'}]});"
sleep 2
python /opt/fuxi/migration/db_init.py
nohup python /opt/fuxi/fuxi_scanner.py > /data/log.log 2>&1 &

/bin/bash