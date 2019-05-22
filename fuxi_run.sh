#!/bin/bash

APP_PATH=`dirname $0`
cd ${APP_PATH}

option=$1
[ -z "$option" ] && option=restart


start(){
    nohup python3.6 ${APP_PATH}/manage.py > ${APP_PATH}/logs/fuxi_http.log 2>&1 &
    nohup celery worker -A ${APP_PATH}/fuxi_celery_worker.celery -B > ${APP_PATH}/logs/fuxi_celery.log 2>&1 &
}

stop(){
    fuxi_celery=`ps -ef | grep "fuxi_celery_worker" | grep -v "grep" |awk '{print $2}'`
    for celery_pid in ${fuxi_celery}
    do
    kill -9 ${celery_pid}
    done
}

case ${option} in
    start)
    echo "[*] Starting  Now......"
    start
    echo "[*] Starting  Finished"
    ;;
    stop)
    echo "[-] Stopping  Now......"
    stop
    echo "[-] Stopping  Finished"
    ;;
    restart)
    echo "[+] Restart  Now......"
    stop
    start
    echo "[+] Restart  Finished"
    ;;
    *)
esac