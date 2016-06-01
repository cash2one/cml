#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import base64
import urllib
import re

class ApiTopicWww(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_api_topic_www"
        self.module_key = "api_topic_www"

    def add(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {"code": -1, "msg": u"系统异常"}

        content = request.POST.get("content")
        if not content:
            return {"code": -1, "msg": u"内容不能为空"}

        content = urllib.unquote(base64.b64decode(content))
        content = content.strip()
        if not content:
            return {"code": -1, "msg": u"内容不能为空"}
        subjects = []
        for subject in content.split("\n"):
            items = subject.strip().split("@@@")
            if len(items) > 4 or len(items) < 2:
                continue
            subject = items[0].decode("utf-8").strip()
            if not subject:
                continue
            if not re.match(r"\d+$", subject):
                continue

            tmp = {
                "subject": subject,
                "status": "0",
                "title": "",
                "url": items[1].decode("utf-8").strip(),
            }
            if not re.match(r"https?://", tmp["url"]):
                continue
            if len(items) > 2:
                try:
                    tmp["status"] = str(int(items[2].strip()))
                except:
                    pass
            if len(items) > 3:
                try:
                    tmp["title"] = items[3].decode("utf-8").strip()
                except:
                    pass
            subjects.append(tmp)

        if not subjects:
            return {"code": -1, "msg": u"内容不能为空"}

        colums = ["id", "subject", "subject_name", "title", "url", "status"]
        for item in subjects:
            sql = self.sql_ins.insert(
                Table = self.table,
                Colums = colums,
                Values = [
                    "", item.get("subject"), "", item.get("title"), item.get("url"), item.get("status")
                ]
            )
            self.luna_sql.raw(sql, commit = True)
        return {"code": 0, "msg": u"添加成功"}

    def load(self, params):
        ret = {"subject": "", "query": "", "pageno": 1}
        request = params.get("request")
        if not request:
            return ret

        if request.method == "POST":
            request_dict = request.POST
        elif request.method == "GET":
            request_dict = request.GET
        else:
            return ret

        where = {}

        status = request_dict.get("status")
        if status is False or status is None:
            where["status"] = "<> -1"
            ret["status"] = 0
        else:
            where["status"] = "= %s" % status
            ret["status"] = status

        pageno = request_dict.get("p")
        if not pageno:
            pageno = 1
        else:
            pageno = int(pageno)

        ret["pageno"] = pageno

        size = 20
        offset = (pageno - 1) * size
        limit = "%s,%s" % (offset, size)

        query = request_dict.get("q")
        if query:
            query = urllib.unquote(str(query))
            ret["query"] = query
            where["title"] = u'''LIKE "%%%s%%"''' % query.decode("utf-8")

        subject = request_dict.get("subject")
        if subject:
            ret["subject"] = subject
            where["subject"] = '''= "%s"''' % subject

        sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = where,
            Limit = limit,
        )

        ret["data"] = self.luna_sql.raw(sql)
        return ret

    def delete(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        db_id = request.POST.get("id")
        sql = '''UPDATE `%s` SET `status` = -1 WHERE `id` = %s''' % (self.table, db_id)
        try:
            self.luna_sql.raw(sql, commit = True)
            return {"code": 0, "msg": u"删除成功"}
        except Exception as info:
            return {"code": -1, "msg": u"系统异常"}

    def update(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        db_id = request.POST.get("id")
        subject = request.POST.get("subject")
        title = request.POST.get("title")
        url = request.POST.get("url")
        subject_name = request.POST.get("subject_name")
        status = request.POST.get("status")
        sql = '''UPDATE `%s` SET `subject` = "%s", `title` = "%s", `url` = "%s", `status` = "%s", `subject_name` = "%s" WHERE `id` = %s''' %\
              (self.table, subject, title, url, status, subject_name, db_id)
        try:
            self.luna_sql.raw(sql, commit = True)
            return {"code": 0, "msg": u"更新成功"}
        except Exception as info:
            return {"code": -1, "msg": u"系统异常"}

    def api_load(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"请求异常"}
        if request.method == "GET":
            rd = request.GET
        elif request.method == "POST":
            rd = request.POST
        else:
            return {"code": -1, "msg": u"不支持的请求类型"}

        params_subjects = rd.get("subject")
        subjects = []
        if params_subjects:
            for subject in params_subjects.strip().split(","):
                if subject.strip() and re.match(r"\d+$", subject):
                    subjects.append(subject)

        size = rd.get("size")
        if not size:
            size = "10"
        if not re.match(r"\d+$", size):
            return {"code": -1, "msg": u"参数错误"}

        pageno = rd.get("p")
        if not pageno:
            pageno = "1"
        if not re.match(r"\d+$", pageno):
            return {"code": -1, "msg": u"参数错误"}

        limit = "%s,%s" % ((int(pageno) - 1) * int(size), size)
        where = {}
        if subjects:
            where["subject"] = '''IN (%s)''' % ",".join(subjects)

        status = rd.get("status")
        if status and re.match(r"\d+$", status):
            where["status"] = '''= %s''' % status
        else:
            where["status"] = '''= 0'''

        sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = where,
            Limit = limit,
        )

        try:
            ret = self.luna_sql.raw(sql)
            if ret:
                return {"code": 0, "msg": u"success", "data": ret}
            else:
                return {"code": 1, "msg": u"empty"}
        except Exception as info:
            return {"code": -1, "msg": u"系统异常"}
