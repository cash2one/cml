#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import zhanqun
import MySQLdb
from zhanqun.utils.timer import timestamp_to_string
import time

class CmlUserAction(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_cml_user_action"
        self.module_key = "cml_user_action"

    def add_action(self, params = False, userid = False, content = False):
        if params is not False and userid is False:
            userid = params.get("__login_user__").get("content").get("id")
        try:
            request = params.get("request")
            ip = []
            if "HTTP_X_FORWARDED_FOR" in request.META:
                ip.append(request.META['HTTP_X_FORWARDED_FOR'])
            elif "REMOTE_ADDR" in request.META:
                ip.append(request.META['REMOTE_ADDR'])
            if "__track_id__" in request.COOKIES:
                ip.append(request.COOKIES["__track_id__"])

            if "__zhanqun_session_id__" in request.COOKIES:
                ip.append(request.COOKIES["__zhanqun_session_id__"])

            insert_sql = self.sql_ins.insert(
                Table = self.table,
                Colums = ["id", "userid", "content", "update_time", "status", "ip"],
                Values = ["", str(userid), content, timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), "0", ",".join(ip)]
            )
            self.luna_sql.raw(insert_sql, commit = True)
            return True
        except Exception as info:
            return False
