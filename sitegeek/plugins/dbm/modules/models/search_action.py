#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import zhanqun
import MySQLdb
from zhanqun.utils.timer import timestamp_to_string
import time

class SearchAction(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_search_action"
        self.module_key = "search_action"

    def add(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}
        query = request.POST.get("query")
        url = request.POST.get("url")
        if "HTTP_X_FORWARDED_FOR" in request.META:
            ip =  request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        sql = self.sql_ins.insert(
            Table = self.table,
            Colums = ["id", "query", "url", "update_time", "ip"],
            Values = ["", query, url, timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), ip]
        )
        try:
            self.luna_sql.raw(sql, commit = True)
            return {"code": 0, "msg": u"提交成功"}
        except:
            return {"code": -1, "msg": u"系统异常"}
