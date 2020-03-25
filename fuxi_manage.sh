#!/bin/bash

APP_PATH=`dirname $0`
cd ${APP_PATH}

option=$1
[ -z "$option" ] && option=restart


start(){
    nohup python3 ${APP_PATH}/fuxi_manage.py > ${APP_PATH}/logs/fuxi_http.log 2>&1 &
    nohup celery worker -A fuxi_celery_worker.celery -B > ${APP_PATH}/logs/fuxi_celery.log 2>&1 &
}

stop(){
    fuxi_flask=`ps -ef | grep "fuxi_manage.py" | grep -v "grep" |awk '{print $2}'`
    fuxi_celery=`ps -ef | grep "fuxi_celery_worker" | grep -v "grep" |awk '{print $2}'`
    for flask_pid in ${fuxi_flask}
    do
    kill -9 ${flask_pid}
    done
    for celery_pid in ${fuxi_celery}
    do
    kill -9 ${celery_pid}
    done
    sleep 2
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