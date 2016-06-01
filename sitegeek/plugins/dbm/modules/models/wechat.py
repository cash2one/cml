#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import zhanqun
import MySQLdb
from zhanqun.utils.timer import timestamp_to_string
import time
import re

class SetInterest(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "wechat_set_interest"
        self.module_key = "wechat_set_interest"

    def _parse_interest(self, content):
        content = re.split(r"\s+", content)
        content = set(content[1:])
        return list(content)

    def get_user_interest(self, params):
        request = params.get("request")
        if not request:
            return False

        set_interest = self.load({
            "wx_user": u'''= "%s"''' % request.POST.get("wechat_source")
        })

        if not set_interest:
            return False

        set_interest = set_interest[0].get("wx_interest").split(",")[0]
        interest = params.get("dbm_factory").wechat_get_interest.load({
            "id": u'''= %s''' % set_interest
        })
        if not interest:
            return False
        return interest[0]

    def add(self, params):
        request = params.get("request")
        if not request:
            return u"系统异常"
        wx_interest_base = params.get("dbm_factory").wechat_get_interest.load()
        if not wx_interest_base:
            return u"系统异常"

        wx_user = request.POST.get("wechat_source")
        wx_interest = self._parse_interest(request.POST.get("wechat_content"))
        interests = []
        setted = []
        for interest in wx_interest:
            interest = params.get("dbm_factory").wechat_get_interest.load({
                "name": u'''LIKE "%%%s%%"''' % interest
            })
            if not interest:
                continue

            for node in interest:
                interests.append(node.get("id"))
                setted.append(node.get("name"))
        if not interests:
            return u"请回复【兴趣列表】获得系统支持的兴趣列表后再进行设置！！！"

        interests = map(str, set(interests))
        interests = ",".join(interests[:1])
        sql = self.sql_ins.insert(
            Table = self.table,
            Colums = ["id", "wx_user", "wx_interest", "update_time"],
            Values = ["", wx_user, interests, timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S")]
        )
        sql += ''' ON DUPLICATE KEY UPDATE `wx_interest` = "%s", `update_time` = "%s"''' % (MySQLdb.escape_string(interests), timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S"))
        try:
            self.luna_sql.raw(sql, commit = True)
            return u"设置成功 [ %s ]" % u" , ".join(list(set(setted)))
        except:
            return u"设置失败"

class GetInterest(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "wechat_interest"
        self.module_key = "wechat_get_interest"

    def get(self, params):
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return u"获取出错"
        html = []
        for record in result.get("records"):
            html.append(record.get("name"))
            # tmp = {
            #     "title": record.get("name"),
            #     "description": record.get("description"),
            #     "url": record.get("url"),
            # }
            # if record.get("cover_small"):
            #     tmp["picurl"] = record.get("cover_small")
            # if record.get("cover_big"):
            #     tmp["picurl"] = record.get("cover_big")
            # html.append(tmp)
        return u"、".join(html)

class UserSend(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "wechat_user_send"
        self.module_key = "wechat_user_send"

    def add(self, params):
        request = params.get("request")
        if not request:
            return u"系统异常"
        wx_user = request.POST.get("wechat_source")
        wx_content = request.POST.get("wechat_content")
        sql = self.sql_ins.insert(
            Table = self.table,
            Colums = ["id", "wx_user", "wx_content", "update_time"],
            Values = ["", wx_user, wx_content, timestamp_to_string(time.time(), "%Y-%m-%d %H:%M:%S")]
        )
        try:
            self.luna_sql.raw(sql, commit = True)
            return True
        except:
            return False
