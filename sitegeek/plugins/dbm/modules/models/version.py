#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import time
from zhanqun.utils.timer import timestamp_to_string
import json
import re
import base64
import urllib
import MySQLdb

class Version(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_cml_conf_version"
        self.module_key = "version"

    def load(self, params = {}, status = False):
        version = params.get("version", False)
        if not version:
            return False
        where = {"version": '''= "{}"'''.format(version)}
        if status is not False:
            where["status"] = '''= %s''' % status
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = where
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return False
        return result.get("records")

    def load_by_owner(self, owner = False, status = 0):
        where = {
            "status": '''= {}'''.format(status),
        }
        if owner:
            where["owner"] = '''= "{}"'''.format(owner)
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = where
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return False
        return result.get("records")

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

    def exists_version(self, version):
        return self.load({"version": version})

    def copy_version(self, version_dict, version_detail_dict, to_version, owner):
        if self.exists_version(to_version):
            return {"code": False, "msg": u"版本号[%s]已经存在" % to_version}
        colums = ["id", "version", "terminal", "page_key", "content", "owner", "update_time", "status", "desc"]
        for version in version_dict:
            sql = self.sql_ins.insert(
                Table = self.table,
                Colums = colums,
                Values = [
                    "", to_version, version.get("terminal"), version.get("page_key"), version.get("content"), owner, timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), "0", timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S")
                ]
            )
            self.luna_sql.raw(sql, commit = True)

        colums = ["id", "version", "terminal", "page_key", "module_key", "conf_key", "content", "owner", "update_time", "status"]
        for version in version_detail_dict:
            sql = self.sql_ins.insert(
                Table = "zhanqun_cml_conf_version_detail",
                Colums = colums,
                Values = [
                    "", to_version, version.get("terminal"), version.get("page_key"), version.get("module_key"), version.get("conf_key"), version.get("content"), owner, timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), "0"
                ]
            )
            self.luna_sql.raw(sql, commit = True)

        return {"code": True,}

    def create_version(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}
        online_id = request.POST.get("id")
        if not online_id:
            return {"code": -1, "msg": u"id不能为空"}
        create_way = request.POST.get("create_way")
        if not create_way:
            return {"code": -1, "msg": u"create_way不能为空"}
        new_version = request.POST.get("new_version")
        if not new_version:
            return {"code": -1, "msg": u"新增version不能为空"}
        if create_way.strip() != "3" and create_way != "100":
            version = request.POST.get("version")
            if not version:
                return {"code": -1, "msg": u"版本号不能为空"}
            if not self.exists_version(version):
                return {"code": -1, "msg": u"版本号[%s]不存在" % version}

            try:
                ret = self.copy_version(self.load_version(version, _where = {"status": '''= 0'''}), params.get("dbm_factory").version_detail.load_version(version), new_version, str(params.get("__login_user__").get("content").get("id")))
                if not ret["code"]:
                    return {"code": -1, "msg": ret["msg"]}
                sql = '''UPDATE `zhanqun_cml_conf_online` SET `status` = 2 WHERE `id` = %s''' % online_id
                self.luna_sql.raw(sql, commit = True)
                params.get("dbm_factory").cml_user_action.add_action(params = params, content = u"[create_version] [from_version = %s, to_version = %s]" % (version, new_version))
                return {"code": 0, "msg": u"创建成功"}
            except Exception as info:
                return {"code": -1, "msg": u"系统异常[%s]" % info}
        else:
            # 创建一个空版本，只有 pc m home
            try:
                sql = self.sql_ins.insert(
                    Table = self.table,
                    Colums = ["id", "version", "terminal", "page_key", "content", "owner", "update_time", "status", "desc"],
                    Values = ["", new_version, "pc", "home", json.JSONEncoder().encode({}), str(params.get("__login_user__").get("content").get("id")), timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), "0", timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S")],
                )
                self.luna_sql.raw(sql, commit = True)
                sql = self.sql_ins.insert(
                    Table = self.table,
                    Colums = ["id", "version", "terminal", "page_key", "content", "owner", "update_time", "status", "desc"],
                    Values = ["", new_version, "m", "home", json.JSONEncoder().encode({}), str(params.get("__login_user__").get("content").get("id")), timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), "0", timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S")],
                )
                self.luna_sql.raw(sql, commit = True)
                if create_way == "100":
                    sql = '''UPDATE `zhanqun_cml_conf_online` SET `status` = 100, `domain_en` = "%s" WHERE `id` = %s''' % (request.POST.get("domain"), online_id)
                else:
                    sql = '''UPDATE `zhanqun_cml_conf_online` SET `status` = 2 WHERE `id` = %s''' % online_id
                self.luna_sql.raw(sql, commit = True)
                params.get("dbm_factory").cml_user_action.add_action(params = params, content = u"[create_version] [blank version = %s]" % new_version)
                return {"code": 0, "msg": u"创建成功"}
            except:
                return {"code": -1, "msg": u"系统异常"}
            return {"code": -1, "msg": u"创建失败"}

    def add_version(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {"code": -1, "msg": u"系统异常"}

        version = dbm_factory.conf_online.load_where({"version": '''= "%s"''' % request.POST.get("version")})
        if not version:
            return {"code": -1, "msg": u"对应版本信息不存在"}
        else:
            version = version[0]
        if version.get("status") == 0:
            return {"code": -1, "msg": u"禁止对online版本进行任何更改操作"}

        if version.get("owner") != params.get("__login_user__").get("content").get("id"):
            return {"code": -1, "msg": u"只有owner能进行修改"}

        version = self.load_version(version = request.POST.get("version"),
                                    terminal = request.POST.get("terminal"),
                                    _where = {
                                        "page_key": '''= "%s"''' % request.POST.get("page_key"),
                                        "status": "= 0",
                                    }
                                    )
        if version:
            return {"code": -1, "msg": u"对应版本已经存在"}

        if request.POST.get("terminal").strip() == "m":
            content = "version,pl.html_left,pl.head_left,m.meta,tdk,m.css,m.js,report,pl.baidu_statistics_baizhan,pl.google_statistics,pl.head_right,pl.body_left,m.nav,csrf,m.footer,m.footer-js,pl.body_right,pl.html_right"
        elif request.POST.get("terminal").strip() == "pc":
            content = "version,pl.html_left,pl.head_left,meta,tdk,css,js,report,pl.baidu_statistics_baizhan,pl.google_statistics,pl.head_right,pl.body_left,csrf,footer,footer-js,pl.body_right,pl.html_right"
        else:
            return {"code": -1, "msg": u"不支持的terminal"}

        # page_key = dbm_factory.conf_page_key.get_where({
        #                                 "page_key": '''= "%s"''' % request.POST.get("page_key").split("@@")[0],
        #                                 "status": "= 0",
        #                                 "terminal": request.POST.get("terminal"),
        #                             })
        # print page_key
        # if not page_key:
        #     return {"code": -1, "msg": u"不支持的页面类型"}

        sql = self.sql_ins.insert(
            Table = self.table,
            Colums = ["id", "version", "terminal", "page_key", "content", "owner", "update_time", "status", "desc"],
            Values = ["", request.POST.get("version"), request.POST.get("terminal"), request.POST.get("page_key"), json.JSONEncoder().encode(content), str(params.get("__login_user__").get("content").get("id")), timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), "0", timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S")],
        )

        try:
            self.luna_sql.raw(sql, commit = True)
            return {"code": 0, "msg": u"添加成功"}
        except Exception as info:
            return {"code": -1, "msg": u"添加失败"}

    def delete_version(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {"code": -1, "msg": u"系统异常"}

        version = dbm_factory.conf_online.load_where({"version": '''= "%s"''' % request.POST.get("version")})
        if not version:
            return {"code": -1, "msg": u"对应版本信息不存在"}
        else:
            version = version[0]

        if version.get("status") == 0:
            return {"code": -1, "msg": u"禁止对online版本进行任何更改操作"}

        if version.get("owner") != params.get("__login_user__").get("content").get("id"):
            return {"code": -1, "msg": u"只有owner能进行修改"}

        delete_type = request.POST.get("type")
        if delete_type == "pagekey":
            sql = '''UPDATE `%s` SET `status` = -1 WHERE `terminal` = "%s" AND `version` = "%s" AND `page_key` = "%s"''' %\
                (self.table, request.POST.get("terminal"), request.POST.get("version"), request.POST.get("pagekey"),)
            try:
                self.luna_sql.raw(sql, commit = True)
                return {"code": 0, "msg": u"删除成功"}
            except:
                return {"code": -1, "msg": u"系统异常"}

    def update_version(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {"code": -1, "msg": u"系统异常"}

        db_id = request.POST.get("id")
        if not db_id:
            return {"code": -1, "msg": u"系统异常"}
        _version = dbm_factory.conf_online.load_where({"version": '''= "%s"''' % request.POST.get("version")})
        if not _version:
            return {"code": -1, "msg": u"对应版本信息不存在"}
        else:
            _version = _version[0]

        if _version.get("status") == 0:
            return {"code": -1, "msg": u"禁止对online版本进行任何更改操作"}

        SQL = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = {"id": "= %s" % db_id},
        )
        ret = self.luna_sql.raw(SQL)
        if not ret:
            return {"code": -1, "msg": u"系统异常"}
        ret = ret[0]
        if ret.get("owner") != params.get("__login_user__").get("content").get("id"):
            return {"code": -1, "msg": u"请联系owner将模板owner变更为你自己，否则不能修改。"}

        data = request.POST.get("data")
        if not data:
            data = []
        else:
            data = json.JSONDecoder().decode(data)
        module_list = []
        module_conf = {}
        conf_idx = 1
        for item in data:
            key = item.get("key")
            if not key:
                continue
            if re.match(r"{[^}]+}$", key):
                continue
            conf = item.get("value")
            if not conf:
                module_list.append(key)
            else:
                conf_key = "conf_%s" % conf_idx
                module_conf[conf_key] = {"key": key, "value": json.JSONDecoder().decode(urllib.unquote(base64.b64decode(conf)).decode("utf-8"))}
                key = "#".join([key, str(conf_idx)])
                module_list.append(key)
                conf_idx += 1
        modules = ",".join(module_list)

        # 更新version的模块。
        SQL = '''UPDATE `%s` SET `content` = "%s", `update_time` = "%s" WHERE `id` = %s''' % (self.table, MySQLdb.escape_string(json.JSONEncoder().encode(modules)), timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), db_id)
        self.luna_sql.raw(SQL, commit = True)

        # 新建version对应的配置
        ret = dbm_factory.version_detail.add_module_conf(request.POST.get("version"), request.POST.get("terminal"), request.POST.get("page_key"), params.get("__login_user__").get("content").get("id"), module_conf)
        if ret:
            return {"code": 0, "msg": u"保存成功"}
        else:
            return {"code": -1, "msg": u"保存失败"}
