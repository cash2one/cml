#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import zhanqun
import MySQLdb
from zhanqun.utils.timer import timestamp_to_string
import time

class DemandInfo(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_demand_info"
        self.module_key = "demand_info"

    def add(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}
        title = request.POST.get("title")
        info = request.POST.get("info")
        contact = request.POST.get("contact")
        url = request.POST.get("url")
        sql = self.sql_ins.insert(
            Table = self.table,
            Colums = ["id", "title", "info", "update_time", "contact", "status", "url"],
            Values = ["", title, info, timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), contact, "0", url]
        )
        try:
            self.luna_sql.raw(sql, commit = True)
            return {"code": 0, "msg": u"提交成功"}
        except:
            return {"code": -1, "msg": u"系统异常"}
