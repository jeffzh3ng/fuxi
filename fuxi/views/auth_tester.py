#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-5-23
# @File    : auth_tester.py
# @Desc    : ""

import time
from threading import Thread
from flask import Blueprint, render_template, request
from bson import ObjectId
from lib.mongo_db import connectiondb, db_name_conf
from fuxi.views.authenticate import login_check
from instance import config_name
from fuxi.views.modules.auth_tester.auth_crack import AuthCrack

auth_tester = Blueprint('auth_tester', __name__)
auth_db = db_name_conf()['auth_db']
weekpasswd_db = db_name_conf()['weekpasswd_db']
config_db = db_name_conf()['config_db']


@auth_tester.route('/new-auth-tester')
@login_check
def view_new_auth_tester():
    # default view
    config_info = connectiondb(config_db).find_one({"config_name": config_name})
    username_list = "\n".join(config_info['username_dict'])
    password_list = "\n".join(config_info['password_dict'])
    return render_template('new-auth-tester.html', username_list=username_list, password_list=password_list)


@auth_tester.route('/auth-tester', methods=['POST'])
@login_check
def new_auth_tester():
    # create new task
    username_list = request.form.get('username_val').split('\n')
    password_list = request.form.get('password_val').split('\n')
    task_name = time.strftime("%y%m%d", time.localtime()) + "_" + request.form.get('task_name')
    target_list = request.form.get('target_val').split('\n')
    recursion = int(request.form.get('recursion'))
    source = request.form.get('source')
    if source == "basic_auth":
        if scan_data(task_name, target_list, username_list, password_list, recursion, "Basic Auth"):
            return "success"

    elif source == "mysql_auth":
        if scan_data(task_name, target_list, username_list, password_list, recursion, "MySQL Auth"):
            return "success"

    elif source == "ssh_auth":
        if scan_data(task_name, target_list, username_list, password_list, recursion, "SSH Auth"):
            return "success"

    elif source == "redis_auth":
        if scan_data(task_name, target_list, username_list, password_list, recursion, "Redis Auth"):
            return "success"


def scan_data(task_name, target_list, username_list, password_list, recursion, scan_type):
    data = {
        "task_name": task_name,
        "target": target_list,
        "username": username_list,
        "password": password_list,
        "type": scan_type,
        "recursion": recursion,
        "status": "Queued",
        "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "week_count": 0,
    }
    _id = connectiondb(auth_db).insert_one(data).inserted_id
    scanner = AuthCrack(target_list, username_list, password_list, _id, task_name, scan_type)
    if _id and scanner:
        t1 = Thread(target=scanner.start_scan, args=())
        t1.start()
        return True
    else:
        return False


@auth_tester.route('/new-auth-task', methods=['POST'])
@login_check
def new_tasks():
    username_list = request.form.get('username_list').split('\n')
    password_list = request.form.get('password_list').split('\n')
    task_name = time.strftime("%y%m%d", time.localtime()) + "_" + request.form.get('task_name')
    target_list = request.form.get('target_list').split('\n')
    recursion = int(request.form.get('recursion'))
    auth_type = request.form.get('auth_type')
    if auth_type == "basic_auth":
        if scan_data(task_name, target_list, username_list, password_list, recursion, "Basic Auth"):
            return "success"

    elif auth_type == "mysql_auth":
        if scan_data(task_name, target_list, username_list, password_list, recursion, "MySQL Auth"):
            return "success"

    elif auth_type == "ssh_auth":
        if scan_data(task_name, target_list, username_list, password_list, recursion, "SSH Auth"):
            return "success"

    elif auth_type == "redis_auth":
        if scan_data(task_name, target_list, username_list, password_list, recursion, "Redis Auth"):
            return "success"


@auth_tester.route('/auth-tester-tasks', methods=['GET', 'POST'])
@login_check
def task_management():
    if request.method == "GET":
        # delete task
        if request.args.get('delete'):
            task_id = request.args.get('delete')
            connectiondb(weekpasswd_db).update({"task_id": ObjectId(task_id)}, {"$set": {"tag": "delete"}}, multi=True)
            if connectiondb(auth_db).remove({"_id": ObjectId(task_id)}):
                return "success"
        # rescan task
        elif request.args.get('rescan'):
            task_id = request.args.get('rescan')
            task_info = connectiondb(auth_db).find_one({"_id": ObjectId(task_id)})
            username_list = task_info['username']
            password_list = task_info['password']
            task_name = task_info['task_name']
            target_list = task_info['target']
            task_type = task_info['type']
            # connectiondb(weekpasswd_db).remove({"task_id": ObjectId(task_id)})
            connectiondb(weekpasswd_db).update({"task_id": ObjectId(task_id)}, {"$set": {"tag": "delete"}}, multi=True)
            connectiondb(auth_db).update_one({"_id": ObjectId(task_id)}, {"$set": {
                "status": "Queued",
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "week_count": 0,
            }})
            scanner = AuthCrack(target_list, username_list, password_list, ObjectId(task_id), task_name, task_type)
            if scanner:
                t1 = Thread(target=scanner.start_scan, args=())
                t1.start()
                return "success"

        # default view
        else:
            auth_tasks = connectiondb(auth_db).find()
            return render_template('auth-tester-tasks.html', auth_tasks=auth_tasks)
    # return target info
    elif request.form.get('source') == "target_info":
        task_id = request.form.get('task_id')
        # list to string
        target_info = '\n'.join(connectiondb(auth_db).find_one({"_id": ObjectId(task_id)})['target']),
        return target_info


@auth_tester.route('/week-passwd-list', methods=['GET', 'POST'])
@login_check
def week_passwd_list():
    if request.method == "GET":
        if request.args.get('delete'):
            _id = request.args.get('delete')
            # delete week password
            # if connectiondb(weekpasswd_db).remove({"_id": ObjectId(_id)}):
            if connectiondb(weekpasswd_db).update_one({"_id": ObjectId(_id)}, {"$set": {"tag": "delete"}}):
                return "success"
        # screening result by task_id
        elif request.args.get('task'):
            _id = request.args.get('task')
            weekpasswd_data = connectiondb(weekpasswd_db).find({"task_id": ObjectId(_id), "tag": {"$ne": "delete"}})
            return render_template('week-passwd-list.html', weekpasswd_data=weekpasswd_data)
        # default view
        else:
            weekpasswd_data = connectiondb(weekpasswd_db).find({"tag": {"$ne": "delete"}})
            return render_template('week-passwd-list.html', weekpasswd_data=weekpasswd_data)

