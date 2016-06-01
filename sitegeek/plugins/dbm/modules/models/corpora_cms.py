#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import zhanqun
import MySQLdb
from zhanqun.utils.timer import timestamp_to_string
import time
import urllib
import json

class CorporaCms(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "corpora_cms"
        self.module_key = "corpora_cms"
        self.update_uri = "http://zhanqun-search.baijiahulian.com//v1/multi_index_cms?ids=%s&token=d98d7173a8e47e9e57fb0a8f61c3d9f7"

    def get(self, db_id):
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = {"id": "= {}".format(db_id)}
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return False
        return result.get("records")

    def modify(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}
        content = request.POST.get("content")
        if content is False or content is None:
            return {"code": -1, "msg": u"内容为空"}
        try:
            db_id = request.POST.get("id")
            source = request.POST.get("source")
            class_id = request.POST.get("class")
            task_id = request.POST.get("taskid")
        except Exception as info:
            return {"code": -1, "msg": u"内容error"}

        exists = self.get(db_id)
        if exists:
            sql = '''UPDATE `%s` SET `class` = "%s", `content` = "%s", `source` = "%s", `update_time` = "%s" WHERE `id` = %s''' %\
                  (self.table, class_id, MySQLdb.escape_string(content), source, timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), db_id)
        else:
            try:
                sql = self.sql_ins.insert(
                    Table = self.table,
                    Colums = ["id", "class", "content", "source", "update_time", "taskid"],
                    Values = [db_id, class_id, content, source, timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"), task_id]
                )
            except Exception as info:
                return {"code": -1, "msg": u"内容error"}
        try:
            self.luna_sql.raw(sql, commit = True)
            ret = json.JSONDecoder().decode(urllib.urlopen(self.update_uri % db_id).read())
            if ret["data"][db_id]:
                return {"code": 0, "msg": u"修改成功《请稍等再刷新页面，暂时不要再做修改》"}
            else:
                return {"code": -1, "msg": u"修改失败"}
        except Exception as info:
            return {"code": -1, "msg": u"系统异常[%s]" % info}
