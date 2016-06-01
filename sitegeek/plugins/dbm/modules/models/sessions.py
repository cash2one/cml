#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
from zhanqun.utils.timer import timestamp_to_string
from zhanqun.utils.timer import get_time_ago
import time
import MySQLdb

class Sessions(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_cml_sessions"
        self.module_key = "sessions"

    def get_cookie(self, session_id):
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = {"session_id": '''= "{}"'''.format(session_id),
                     "expire": '''> "{}"'''.format(timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S")),}
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return False
        return result.get("records")[0]

    def set_cookie(self, session_id, value, empire_days = 7, _time_format = "%Y-%m-%d %H:%M:%S"):
        empire = get_time_ago(timestamp_to_string(time.time(), _time_format), format = _time_format, day = empire_days, ago = False)
        SET_COOKIE = '''INSERT INTO `%s` VALUES ("", "%s", "%s", "%s") ON DUPLICATE KEY UPDATE `expire` = "%s"''' % (self.table, session_id, MySQLdb.escape_string(self.serialize(value)), empire, empire)
        try:
            return self.luna_sql.raw(SET_COOKIE, commit = True)
        except Exception as info:
            return False

    def login_user_info(self, session_id):
        user = self.get_cookie(session_id)
        if user:
            user["content"] = self.deserialize(user.get("content", ""))
        return user
