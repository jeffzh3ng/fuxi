#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2019/1/30
# @File    : __init__.py.py
# @Desc    : ""

import os
import geoip2.database
from geoip2.errors import AddressNotFoundError


def geoip(ip, language="en"):
    # language = "zh-CN"
    base_dir = os.path.abspath(os.path.dirname(__file__))
    city_database = base_dir + "/GeoLite2-City.mmdb"
    asn_database = base_dir + "/GeoLite2-ASN.mmdb"
    _data = {
        "status": "failed",
        "message": "",
        "data": {
            "ip": ip, "country": "", "region": "", "city": "", "loc": "", "code": "", "asn": ""
        }
    }
    with geoip2.database.Reader(city_database) as city_reader:
        try:
            city_res = city_reader.city(ip)
            if language in city_res.country.names.keys():
                _data['data']['country'] = city_res.country.names[language]
            else:
                _data['data']['country'] = city_res.country.name if city_res.country.name else "unknown"
            if language in city_res.subdivisions.most_specific.names.keys():
                _data['data']['region'] = city_res.subdivisions.most_specific.names[language]
            else:
                _data['data']['region'] = city_res.subdivisions.most_specific.name \
                    if city_res.subdivisions.most_specific.name else "unknown"

            if language in city_res.city.names.keys():
                _data['data']['city'] = city_res.city.names[language]
            else:
                _data['data']['city'] = city_res.city.name if city_res.city.name else "unknown"
            _data['data']['loc'] = "{},{}".format(city_res.location.latitude, city_res.location.longitude)
            _data['data']['code'] = city_res.postal.code if city_res.postal.code else "-"
            with geoip2.database.Reader(asn_database) as asn_reader:
                asn_res = asn_reader.asn(ip)
                _data['data']['asn'] = asn_res.autonomous_system_organization \
                    if asn_res.autonomous_system_organization else "unknown"
            _data['status'] = 'success'
        except AddressNotFoundError as e:
            if _data['data']['country']:
                _data['status'] = 'success'
            else:
                _data['message'] = str(e)
        except Exception as e:
            _data['status'] = 'failed'
            _data['message'] = str(e)
    return _data

