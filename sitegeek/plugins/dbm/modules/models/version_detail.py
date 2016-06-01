#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import json
from zhanqun.utils.timer import timestamp_to_string
import time
import MySQLdb

class VersionDetail(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_cml_conf_version_detail"
        self.module_key = "version_detail"

    def load(self, params = {}):
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = {"version": '''= "{}"'''.format(params.get("version", "")),
                     "status": '''= 0''',
                     "page_key": '''= "{}"'''.format(params.get("page_key", "")),
                     "terminal": '''= "{}"'''.format(params.get("terminal", "")),
                     }
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return False
        ret = {}
        for item in result.get('records'):
            conf_key = item.get("conf_key")
            if not conf_key:
                continue
            ret[conf_key] = json.JSONDecoder().decode(item.get("content"))
        return ret

    def load_version(self, version, terminal = False, _where = {}):
        where = {
            "version": '''= "{}"'''.format(version),
        }
        if _where:
            for key in _where:
                where[key] = _where[key]
        if terminal:
            where["terminal"] = '''= "{}"'''.format(terminal)
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = where,
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return []
        return result.get("records")

    def add_module_conf(self, version, terminal, page_key, owner, module_conf):
        try:
            SQL = '''UPDATE `%s` SET `status` = -1, `update_time` = "%s" WHERE `version` = "%s" AND `terminal` = "%s" AND `page_key` = "%s"''' % (self.table, timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), version, terminal, page_key)
            self.luna_sql.raw(SQL, commit = True)
            colums = ["id", "version", "terminal", "page_key", "module_key", "conf_key", "content", "owner", "update_time", "status"]
            for conf in module_conf:
                _dict = module_conf[conf]
                sql = self.sql_ins.insert(
                    Table = "zhanqun_cml_conf_version_detail",
                    Colums = colums,
                    Values = [
                        "", version, terminal, page_key, _dict.get("key"), conf, json.JSONEncoder().encode(_dict.get("value")), str(owner), timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), "0"
                    ]
                )
                self.luna_sql.raw(sql, commit = True)
            return True
        except Exception as info:
            return False
