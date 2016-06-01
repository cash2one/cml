#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import time
from zhanqun.utils.timer import timestamp_to_string
import json

class Module(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_cml_module"
        self.module_key = "module_db"

    def get(self, module_key):
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = {"module_key": '''= "{}"'''.format(module_key)}
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return False
        return result.get("records")[0]

    def get_module_like(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        keyword = request.POST.get("keyword")
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
        )
        records_sql += ''' WHERE `module_key` LIKE "%%%s%%" OR `desc` LIKE "%%%s%%" LIMIT 20''' % (keyword, keyword)
        result = self.execute(records_sql)
        if result.get("amounts") is False:
            return {"code": -1, "msg": u"系统异常"}
        return {"code": 0, "data": result.get("records")}
