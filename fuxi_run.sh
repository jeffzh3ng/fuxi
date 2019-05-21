#!/bin/bash

APP_PATH=`dirname $0`
cd ${APP_PATH}

option=$1
[ -z "$option" ] && option=start


start(){
    nohup python3.6 ${APP_PATH}/manage.py > ${APP_PATH}/logs/fuxi_http.log 2>&1 &
    nohup celery worker -A ${APP_PATH}/celery_worker.celery -B > ${APP_PATH}/logs/fuxi_celery.log 2>&1 &
}

stop(){

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