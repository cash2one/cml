#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
from zhanqun.utils.timer import timestamp_to_string

class BaiduQuestion(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "bd_question"
        self.module_key = "bd_question"

    def add_question(self, params = {}):
        if not params:
            return {'errmsg': 'fail'}

        request = params.get("request")
        if not request:
            return {'errmsg': 'fail'}

        request_dict = request.POST
        if not request_dict:
            return {'errmsg': 'fail'}

        question_id = request_dict.get("question_id")
        if not question_id:
            return {'errno': 1, 'errmsg': 'fail', 'question_id': question_id}

        try:
            sql = self.sql_ins.insert(
                Table = self.table,
                Colums = ["id", "question_id", "title", "content", "pictures", "cid", "cname", "anonymous", "hit_keywords",
                          "hit_cids", "lbs_province", "lbs_city", "lbs_street", "create_time", "appkey", "appname", "uid", "uname"],
                Values = ["",
                          request_dict.get("question_id", "0"),
                          request_dict.get("title", ""),
                          request_dict.get("content", ""),
                          request_dict.get("pictures", ""),
                          request_dict.get("cid", ""),
                          request_dict.get("cname", ""),
                          request_dict.get("anonymous", ""),
                          request_dict.get("hit_keywords", ""),
                          request_dict.get("hit_cids", ""),
                          request_dict.get("lbs_province", ""),
                          request_dict.get("lbs_city", ""),
                          request_dict.get("lbs_street", ""),
                          request_dict.get("create_time", "0"),
                          request_dict.get("appkey", "0"),
                          request_dict.get("appname", ""),
                          request_dict.get("uid", ""),
                          request_dict.get("uname", ""),
                          ],
            )
            self.luna_sql.raw(sql, commit = True)
            return {'errno': 0, 'errmsg': 'success', 'question_id': question_id}
        except Exception as info:
            return {'errno': 1, 'errmsg': 'fail', 'question_id': question_id}
