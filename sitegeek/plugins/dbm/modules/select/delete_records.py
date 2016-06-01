#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase

class DeleteRecords(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = ""
        self.module_key = "delete_records"

    def load(self, params):
        table = params.get("table")
        if not table:
            return False
        where = self.sql_ins.where(params.get("where", {}))
        sql = ["DELETE FROM `%s`" % table, where]
        return self.luna_sql.raw(" ".join(sql), commit = True)
