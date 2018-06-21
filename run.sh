#!/bin/bash

APP_PATH=`dirname $0`
cd ${APP_PATH}

option=$1
[ -z "$option" ] && option=start


start(){
    nohup python ./fuxi_scanner.py > ${APP_PATH}/logs/log.log 2>&1 &
}

stop(){
    fuxi_scanner=`ps -ef | grep "fuxi_scanner.py" | grep -v "$0" | grep -v "grep" | awk '{print $2}'`
    for pid in ${fuxi_scanner}
    do
    kill -9 ${pid}
    done
    hydra_scanner=`ps -ef | grep "hydra" | grep -v "$0" | grep -v "grep" | awk '{print $2}'`
    for hydra_pid in ${hydra_scanner}
    do
    kill -9 ${hydra_pid}
    done
    nmap_scanner=`ps -ef | grep "nmap" | grep -v "$0" | grep -v "grep" | awk '{print $2}'`
    for nmap_pid in ${nmap_scanner}
    do
    kill -9 ${nmap_pid}
    done
}

case ${option} in
    start)
    echo "Starting  Now......"
    start
    echo "Starting  Finished"
    ;;
    stop)
    echo "Stopping  Now......"
    stop
    echo "Stopping  Finished"
    ;;
    restart)
    echo "Restart  Now......"
    stop
    start
    echo "Restart  Finished"
    ;;
    *)
esac
