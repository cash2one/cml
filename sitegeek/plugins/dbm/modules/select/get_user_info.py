#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase

class GetUserInfo(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "teacher_base_info"
        self.module_key = "get_user_info"

    def load(self, params):
        usernumber = params.get("user_number")
        if not usernumber:
            return False

        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = {"number": "= {}".format(usernumber)}
        )
        return self.execute(records_sql)
