#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2020/3/19
# @File    : export_file.py
# @Desc    : ""

import csv
from typing import List

from fuxi.core.databases.orm.scanner.pocsuite_orm import DBPocsuiteVul


class ExportData(object):
    def __init__(self, data):
        self.rows = data

    def _filter(self, sort):
        result = []
        if len(sort) == 0:
            for item in self.rows:
                d = []
                for t in item:
                    d.append(str(item[t]))
                result.append(d)
        else:
            for item in self.rows:
                d = []
                for t in sort:
                    d.append(str(item[t]))
                result.append(d)
        return result

    def csv(self, title, filepath):
        d = self._filter(title)
        with open(filepath, "w", encoding="UTF-8") as file_csv:
            csv_writer = csv.writer(file_csv)
            csv_writer.writerow(['index'] + title)
            for index, item in enumerate(d):
                csv_writer.writerow([str(index + 1)] + item)
        return filepath

    def txt(self, keyword, filepath):
        d = self._filter(keyword)
        with open(filepath, "w", encoding="UTF-8") as file_txt:
            for row in d:
                file_txt.write(",".join(row).strip(",") + "\n")
        return filepath
