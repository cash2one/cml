#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
from zhanqun.utils.sign import Sign
import zhanqun
import MySQLdb

class CmlUser(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_cml_user"
        self.module_key = "cml_user"

    def validate_login(self, username, password):
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = {"username": '''= "{}"'''.format(username),
                     "password": '''= "{}"'''.format(Sign.signature(password, zhanqun.settings.SIGN_KEY)),
                     }
        )
        ret = self.luna_sql.raw(records_sql)
        if len(ret):
            ret = ret[0]
            if ret.get("status") == 0:
                return {"code": 0, "data": ret}
        return {"code": -1}

    def get(self, userid):
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = {"id": '''= "{}"'''.format(userid),
                     }
        )
        ret = self.luna_sql.raw(records_sql)
        if len(ret):
            ret = ret[0]
            return ret
        return False

    def get_where(self, where):
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = where
        )
        ret = self.luna_sql.raw(records_sql)
        if len(ret):
            return ret
        return False

    def add_user(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        if params.get("__login_user__").get("content").get("id") != 1:
            return {"code": -1, "msg": u"没有添加用户权限"}
        username = request.POST.get("username")
        if not username:
            return {"code": -1, "msg": u"系统异常"}

        exists = self.get_where({
            "username": '''= "%s"''' % MySQLdb.escape_string(username),
        })
        if exists:
            return {"code": -1, "msg": u"账号名已经存在"}

        password = request.POST.get("password")
        if not password:
            return {"code": -1, "msg": u"系统异常"}

        nickname = request.POST.get("nickname")
        if not nickname:
            return {"code": -1, "msg": u"系统异常"}

        desc = request.POST.get("desc")
        if not desc:
            return {"code": -1, "msg": u"系统异常"}

        email = request.POST.get("email")
        if not email:
            return {"code": -1, "msg": u"系统异常"}

        sql = self.sql_ins.insert(
            Table = self.table,
            Colums = ["id", "username", "password", "nickname", "desc", "status", "authority", "email"],
            Values = ["", username, Sign.signature(password, zhanqun.settings.SIGN_KEY), nickname, desc, "0", "0", email]
        )
        try:
            self.luna_sql.raw(sql, commit = True)
            sql = self.sql_ins.get(
                Select = ["*"],
                From = self.table,
                Where = {"username": '''= "{}"'''.format(username),}
            )
            ret = self.luna_sql.raw(sql)
            if not ret:
                return {"code": -1, "msg": u"添加失败"}
            userid = ret[0].get("id")
            sql = self.sql_ins.insert(
                Table = "zhanqun_cml_copy",
                Colums = ["id", "userid", "content"],
                Values = ["", str(userid), ""]
            )
            self.luna_sql.raw(sql, commit = True)
            params.get("dbm_factory").cml_user_action.add_action(params = params, content = "[add_user] [userid = %s]" % userid)
            return {"code": 0, "msg": u"添加成功"}
        except Exception as info:
            print info
            return {"code": -1, "msg": u"添加失败"}

    def change_pass(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        userid = params.get("__login_user__").get("content").get("id")
        if not userid:
            return {"code": -1, "msg": u"系统异常"}
        old_pass = request.POST.get("old_pass")
        new_pass = request.POST.get("new_pass")
        new_pass_confirm = request.POST.get("new_pass_confirm")
        if not old_pass or not new_pass or not new_pass_confirm or new_pass != new_pass_confirm:
            return {"code": -1, "msg": u"参数异常"}

        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = {"id": '''= "{}"'''.format(userid),
                     "password": '''= "{}"'''.format(Sign.signature(old_pass, zhanqun.settings.SIGN_KEY)),
                     }
        )
        ret = self.luna_sql.raw(records_sql)
        if not ret:
            return {"code": -1, "msg": u"密码错误"}

        sql = '''UPDATE `%s` SET `password` = "%s" WHERE `id` = %s''' % (self.table, Sign.signature(new_pass, zhanqun.settings.SIGN_KEY), userid)
        try:
            ret = self.luna_sql.raw(sql, commit = True)
            params.get("dbm_factory").cml_user_action.add_action(params = params, content = "[password-change] [userid = %s]" % userid)
            return {"code": 0, "msg": u"修改成功"}
        except Exception as info:
            return {"code": -1, "msg": u"修改失败"}
