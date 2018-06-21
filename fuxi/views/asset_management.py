#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-5-10
# @File    : asset_management.py
# @Desc    : ""

import time
import json
from threading import Thread
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from bson import ObjectId
from lib.mongo_db import connectiondb, db_name_conf
from fuxi.views.authenticate import login_check
from instance import config_name
from fuxi.views.modules.discovery.asset_discovery import AssetDiscovery

asset_management = Blueprint('asset_management', __name__)
tasks_db = db_name_conf()['tasks_db']
asset_db = db_name_conf()['asset_db']
server_db = db_name_conf()['server_db']
subdomain_db = db_name_conf()['subdomain_db']
vul_db = db_name_conf()['vul_db']
plugin_db = db_name_conf()['plugin_db']
config_db = db_name_conf()['config_db']


# new asset view
@asset_management.route('/new-asset', methods=['GET', 'POST'])
@login_check
def new_asset():
    # default asset view
    if request.method == "GET":
        return render_template('new-asset.html')
    else:
        # create asset (post)
        if request.form.get("source") == "new_asset":
            asset_name = request.form.get('asset_name')
            asset_host = request.form.get('asset_host').replace('\r', '').split('\n', -1),
            dept_name = request.form.get('dept_name')
            admin_name = request.form.get('admin_name')
            discover_option = request.form.get('discover_option')
            if discover_option == "true":
                discover_option = 'Enable'
            else:
                discover_option = 'Disallow'
            asset_data = {
                'asset_name': asset_name,
                'asset_host': asset_host[0],
                'dept_name': dept_name,
                'admin_name': admin_name,
                "asset_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'discover_option': discover_option,
            }
            asset_id = connectiondb(asset_db).insert_one(asset_data).inserted_id
            if discover_option == "Enable":
                scanner = AssetDiscovery(asset_id)
                t1 = Thread(target=scanner.set_discovery, args=())
                t1.start()
                return "success"
            else:
                return "success"
        else:
            return "Warning"


# asset view
@asset_management.route('/asset-management', methods=['GET', 'POST'])
@login_check
def asset_view():
    if request.method == "GET":
        # asset delete
        if request.args.get("delete"):
            asset_id = request.args.get("delete")
            if connectiondb(asset_db).delete_one({'_id': ObjectId(asset_id)}):
                return "success"

        # get asset info
        elif request.args.get("edit"):
            asset_id = request.args.get("edit")
            try:
                asset_info = connectiondb(asset_db).find_one({'_id': ObjectId(asset_id)})
                asset_info_json = {
                    'asset_name': asset_info['asset_name'],
                    'admin_name': asset_info['admin_name'],
                    'dept_name': asset_info['dept_name'],
                    'asset_id': asset_id,
                    'asset_host': '\n'.join(asset_info['asset_host']),
                }
                return jsonify(asset_info_json)
            except Exception as e:
                print(e)

        # get asset host info for new scan
        elif request.args.get("scan"):
            asset_id = request.args.get("scan")
            try:
                asset_host = connectiondb(asset_db).find_one({'_id': ObjectId(asset_id)})['asset_host']
                asset_host_json = {
                    'asset_host': '\n'.join(asset_host),
                }
                return jsonify(asset_host_json)
            except Exception as e:
                print(e)
        else:
            # asset list(view)
            config_info = connectiondb(config_db).find_one({"config_name": config_name})
            asset_info = connectiondb(asset_db).find()
            plugin_info = connectiondb(plugin_db).find()
            username_list = '\n'.join(config_info['username_dict'])
            password_list = '\n'.join(config_info['password_dict'])
            protocols = config_info['auth_service']
            return render_template("asset-management.html", asset_info=asset_info, plugin_info=plugin_info,
                                   protocols=protocols, username_list=username_list, password_list=password_list)

    else:
        # asset db update
        if request.form.get("source") == "asset_update":
            asset_id = request.form.get('asset_id')
            asset_name = request.form.get('asset_name')
            asset_host = request.form.get('host_val').replace('\r', '').split('\n', -1),
            dept_name = request.form.get('dept_name')
            admin_name = request.form.get('admin_name')
            discover_option = request.form.get('discover_option')
            if discover_option == "true":
                discover_option = 'Enable'
            else:
                discover_option = 'Disallow'
            update_asset = connectiondb(asset_db).update_one(
                {'_id': ObjectId(asset_id)},
                {'$set': {
                    'asset_name': asset_name,
                    'dept_name': dept_name,
                    'asset_host': asset_host[0],
                    'admin_name': admin_name,
                    "asset_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    'discover_option': discover_option,
                }
                }
            )
            if update_asset:
                if discover_option == "Enable":
                    scanner = AssetDiscovery(ObjectId(asset_id))
                    t1 = Thread(target=scanner.set_discovery, args=())
                    t1.start()
                    return "success"
            else:
                return "Warning"


# asset server view
@asset_management.route('/asset-services', methods=['GET', 'POST'])
@login_check
def asset_server():
    if request.method == "GET":
        plugin_info = connectiondb(plugin_db).find()
        if request.args.get('asset'):
            asset_id = request.args.get('asset')
            server_data = connectiondb(server_db).find({"tag": {"$ne": "delete"}, 'asset_id': ObjectId(asset_id)})
            return render_template("asset-services.html", server_data=server_data, plugin_info=plugin_info)
        elif request.args.get('delete'):
            server_id = request.args.get('delete')
            if connectiondb(server_db).update_one({'_id': ObjectId(server_id)}, {"$set": {"tag": "delete"}}):
                return redirect(url_for('asset_management.asset_server'))
        elif request.args.get('info'):
            server_id = request.args.get('info')
            server_info = connectiondb(server_db).find_one({"tag": {"$ne": "delete"}, '_id': ObjectId(server_id)})
            if server_info:
                del server_info['_id']
                del server_info['asset_id']
                return jsonify(server_info)
            else:
                return jsonify({"result": "Warning"})
        server_data = connectiondb(server_db).find({"tag": {"$ne": "delete"}})
        return render_template("asset-services.html", server_data=server_data, plugin_info=plugin_info)
    else:
        if request.form.get('source') == 'server_scan':
            server_host = []
            server_list = request.form.get('server_list').split(",")
            for server_id in server_list:
                server_info = connectiondb(server_db).find_one({"_id": ObjectId(server_id)})
                server_host.append(server_info['host'] + ":" + str(server_info['port']))
            return "\n".join(server_host)


@asset_management.route('/search', methods=['GET', 'POST'])
@login_check
def search_view():
    config_info = connectiondb(config_db).find_one({"config_name": config_name})
    username_list = '\n'.join(config_info['username_dict'])
    password_list = '\n'.join(config_info['password_dict'])
    plugin_info = connectiondb(plugin_db).find()
    protocols = config_info['auth_service']
    if request.method == "GET":
        data = "Your search - \"\" - did not match any documents."
        return render_template('search.html', data=data, plugin_info=plugin_info, protocols=protocols)
    else:
        search_result = []
        key = request.form.get('search').strip()
        for i in connectiondb(server_db).find({"tag": {"$ne": "delete"}}, {'_id': 0, 'asset_id': 0}):
            if key in str(i):
                search_result.append(i)
        if len(search_result) == 0:
            data = "Your search - " + key + " - did not match any documents."
            return render_template('search.html', data=data)
        else:
            return render_template('search.html', search_result=search_result, plugin_info=plugin_info,
                                   username_list=username_list, password_list=password_list, protocols=protocols)
