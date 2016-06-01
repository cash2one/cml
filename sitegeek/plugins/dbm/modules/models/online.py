#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
from zhanqun.utils.timer import timestamp_to_string
import time

class ConfOnline(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_cml_conf_online"
        self.module_key = "conf_online"

    def load(self, params = {}):
        status = params.get("status", 0)
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = {"status": "= {}".format(status)}
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return False
        return result.get("records")

    def load_where(self, where = {}):
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = where,
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return False
        return result.get("records")

    def delete(self, params = {}):
        try:
            online_id = params.get("request").POST.get("id")
            if not online_id:
                return {"code": -1, "msg": u"删除失败"}
            version = request.POST.get("version")
            version_dict = self.load_where({
                "id": '''= %s''' % online_id
            })
            if version_dict:
                version_dict = version_dict[0]
                if version_dict.get("status") == 0:
                    return {"code": -1, "msg": u"禁止对online版本进行任何更改操作"}
            sql = '''UPDATE `zhanqun_cml_conf_online` SET `status` = -1 WHERE `id` = %s''' % online_id
            self.luna_sql.raw(sql, commit = True)
            params.get("dbm_factory").cml_user_action.add_action(params = params, content = u"[删除版本号] [version_id = %s]" % online_id)
            return {"code": 0, "msg": u"删除成功"}
        except:
            return {"code": -1, "msg": u"删除失败"}

    def apply_online(self, params = {}):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {"code": -1, "msg": u"系统异常"}
        version = request.POST.get("version")
        version_dict = self.load_where({
            "version": '''= "%s"''' % version
        })

        if not version_dict:
            return {"code": -1, "msg": u"版本号不存在"}
        version_dict = version_dict[0]
        if version_dict.get("status") not in (2, 100):
            return {"code": -1, "msg": u"该版本号不能发起上线"}

        if params.get("__login_user__").get("content").get("id") != version_dict.get("owner"):
            return {"code": -1, "msg": u"你不是owner，不能发起上线"}

        domain = request.POST.get("domain")
        if not domain:
            return {"code": -1, "msg": u"域名不能为空"}
        domain_info = dbm_factory.domain_info.get(domain)
        if not domain_info:
            return {"code": -1, "msg": u"域名不支持"}

        status = version_dict.get("status") + 1
        sql = '''UPDATE `%s` SET `status` = %s, `domain_en` = "%s", `domain_id` = %s WHERE `id` = %s''' %\
              (self.table, status, domain_info.get("domain_en"), domain_info.get("id"), version_dict.get("id"))
        try:
            self.luna_sql.raw(sql, commit = True)
            dbm_factory.cml_user_action.add_action(params = params, content = u"[apply_online 申请上线] [version = %s]" % version_dict.get("version"))
            return {"code": 0, "msg": u"申请成功"}
        except:
            return {"code": -1, "msg": u"申请失败"}

    def apply_flag(self, params = {}):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {"code": -1, "msg": u"系统异常"}

        action_type = request.POST.get("type")
        if not action_type:
            return {"code": -1, "msg": u"参数异常"}

        version = request.POST.get("version")
        version_dict = self.load_where({
            "version": '''= "%s"''' % version
        })

        if not version_dict:
            return {"code": -1, "msg": u"版本号不存在"}
        version_dict = version_dict[0]

        if action_type in ("1", "2") and params.get("__login_user__").get("content").get("id") != version_dict.get("owner"):
            return {"code": -1, "msg": u"你不是owner，禁止操作"}

        if action_type in ("4",) and params.get("__login_user__").get("content").get("id") != version_dict.get("owner") and params.get("__login_user__").get("content").get("id") != 1:
            return {"code": -1, "msg": u"只有owner和管理员可以操作"}

        if action_type == "2":
            status = 2
        elif action_type == "1":
            status = -1
            if version_dict.get("status") == 0:
                return {"code": -1, "msg": u"禁止对online版本进行任何更改操作"}
        elif action_type == "0":
            status = 0
            sql = '''UPDATE `%s` SET `status` = -1 WHERE `domain_en` = "%s" AND `id` <> %s AND `status` = 0''' % (self.table, version_dict.get("domain_en"), version_dict.get("id"))
            try:
                self.luna_sql.raw(sql, commit = True)
            except:
                return {"code": -1, "msg": u"申请失败"}
        elif action_type == "4":
            status = 2
        elif action_type == "3":
            status = 4
        else:
            return {"code": -1, "msg": u"不支持的操作"}

        sql = '''UPDATE `%s` SET `status` = %s WHERE `id` = "%s"''' % (self.table, status, version_dict.get("id"))
        try:
            self.luna_sql.raw(sql, commit = True)
            dbm_factory.cml_user_action.add_action(params = params, content = "[apply_flag] [action_type = %s, version = %s]" % (action_type, version_dict.get("version")))
            return {"code": 0, "msg": u"申请成功"}
        except:
            return {"code": -1, "msg": u"申请失败"}

    def create(self, params = {}):
        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {"code": -1, "msg": u"系统异常"}
        exists_create_version = self.load_where({
            "status": "= 1",
            "owner": "= %s" % params.get("__login_user__").get("content").get("id"),
        })
        if exists_create_version:
            return {"code": -1, "msg": u"存在未编辑的版本号，不能再创建"}

        desc = params.get("request").POST.get("desc")
        if not desc:
            return {"code": -1, "msg": u"版本描述不能为空"}

        version = dbm_factory.version_utils.new_version()
        while not dbm_factory.version_utils.valid_version(version):
            version = dbm_factory.version_utils.new_version()
        insert_sql = self.sql_ins.insert(
            Table = self.table,
            Colums = ["id", "domain_id", "domain_en", "version", "update_time", "owner", "status", "desc"],
            Values = ["", "", "", version, timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), str(params.get("__login_user__").get("content").get("id")), "1", desc]
        )
        try:
            self.luna_sql.raw(insert_sql, commit = True)
            dbm_factory.cml_user_action.add_action(params = params, content = u"[生成版本号] [version = %s]" % version)
            return {"code": 0, "msg": u"创建成功", "data": {
                "version": version,
            }}
        except:
            return {"code": -1, "msg": u"系统异常"}
