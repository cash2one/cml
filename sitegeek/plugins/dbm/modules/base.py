#!/usr/bin/env python
#-*- coding:utf-8 -*-
import cPickle
import json

class ModuleBase(object):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        self.luna = Luna
        self.luna_sql = LunaSQL
        self.sql_ins = SqlInstance
        self.table = ''
        self.module_key = "get_user_info"

    def execute(self, sql):
        ret = {"records": [], "amounts": 0}
        try:
            result = self.luna_sql.raw(sql)
            if result:
                ret["records"] = result
                ret["amounts"] = len(result)
            return ret
        except Exception as info:
            return ret

    def serialize(self, obj, protocol = 1):
        return json.JSONEncoder().encode(obj)

    def deserialize(self, string, protocol = 1):
        try:
            if type(string) == type(u""):
                string = string.encode("utf-8")
            string = json.JSONDecoder().decode(string)
            return string
        except Exception as info:
            return False

    def load(self, where = {}):
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = where,
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return False
        return result.get("records")
