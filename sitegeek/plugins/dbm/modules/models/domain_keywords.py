#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import base64
import urllib

class DomainKeywords(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_cml_domain_keywords"
        self.module_key = "domain_keywords"

    def add_keywords(self, params):
        request = params.get("request")
        if not request:
            return {"code": -1, "msg": u"系统异常"}

        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {"code": -1, "msg": u"系统异常"}

        domain = request.POST.get("domain")
        if not domain:
            return {"code": -1, "msg": u"域名不能为空"}

        domain_info = dbm_factory.domain_info.get(domain)
        if not domain_info:
            return {"code": -1, "msg": u"域名[%s]不支持" % domain}

        content = request.POST.get("content")
        if not content:
            return {"code": -1, "msg": u"内容不能为空"}

        content = urllib.unquote(base64.b64decode(content))
        content = content.strip()
        if not content:
            return {"code": -1, "msg": u"内容不能为空"}
        keywords = {}
        for keyword in content.split("\n"):
            items = keyword.strip().split("@@@")
            if len(items) > 3:
                continue
            keyword = items[0].decode("utf-8")
            if not keyword:
                continue
            keywords[keyword] = {"status": u"0", "url": u""}
            if len(items) > 1:
                try:
                    keywords[keyword]["status"] = str(int(items[1].strip()))
                except:
                    keywords[keyword]["status"] = u"0"
            if len(items) > 2:
                keywords[keyword]["url"] = items[2].strip()

        if not keywords:
            return {"code": -1, "msg": u"内容不能为空"}

        colums = ["id", "domain", "keyword", "url", "score", "status"]
        for keyword in keywords:
            sql = self.sql_ins.insert(
                Table = self.table,
                Colums = colums,
                Values = [
                    "", domain, keyword, keywords[keyword].get("url"), "0", keywords[keyword].get("status")
                ]
            )
            self.luna_sql.raw(sql, commit = True)
        return {"code": 0, "msg": u"添加成功"}

    def load(self, params):
        ret = {"domain": "", "query": "", "pageno": 1}
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
            where["keyword"] = u'''LIKE "%%%s%%"''' % query.decode("utf-8")

        domain = request_dict.get("domain")
        if domain:
            ret["domain"] = domain
            where["domain"] = '''= "%s"''' % domain

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
        domain = request.POST.get("domain")
        keyword = request.POST.get("keyword")
        url = request.POST.get("url")
        score = request.POST.get("score")
        status = request.POST.get("status")
        sql = '''UPDATE `%s` SET `domain` = "%s", `keyword` = "%s", `url` = "%s", `status` = "%s", `score` = "%s" WHERE `id` = %s''' %\
              (self.table, domain, keyword, url, status, score, db_id)
        try:
            self.luna_sql.raw(sql, commit = True)
            return {"code": 0, "msg": u"更新成功"}
        except Exception as info:
            return {"code": -1, "msg": u"系统异常"}
