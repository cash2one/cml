#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
from zhanqun.utils.sign import Sign
import zhanqun
import MySQLdb

class CmlCopy(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_cml_copy"
        self.module_key = "cml_copy"

    def copy(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        content = request.POST.get("content")
        if content is False:
            return {"code": -1, "msg": u"系统异常"}

        userid = params.get("__login_user__").get("content").get("id")
        if not userid:
            return {"code": -1, "msg": u"系统异常"}
        try:
            sql = '''UPDATE `%s` SET `content` = "%s" WHERE `userid` = %s''' % (self.table, content, userid)
            self.luna_sql.raw(sql, commit = True)
            return {"code": 0, "msg": u"复制成功"}
        except Exception as info:
            return {"code": -1, "msg": u"复制失败[%s]" % info}

    def paste(self, params):
        userid = params.get("__login_user__").get("content").get("id")
        if not userid:
            return {"code": -1, "msg": u"系统异常"}
        try:
            sql = self.sql_ins.get(
                Select = ["content"],
                From = self.table,
                Where = {
                    "userid": "= %s" % userid
                }
            )
            ret = self.luna_sql.raw(sql, commit = True)
            if ret and len(ret):
                ret = ret[0]
                return {"code": 0, "msg": u"粘贴成功", "data": ret.get("content")}
            else:
                return {"code": -1, "msg": u"粘贴失败"}
        except Exception as info:
            return {"code": -1, "msg": u"粘贴失败[%s]" % info}
