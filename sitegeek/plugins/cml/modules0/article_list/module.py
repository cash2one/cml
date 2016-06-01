#!/usr/bin/env python
#-*- coding:utf-8 -*-
from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco
from cml.module_conf import ConfUtils
from cml.module_conf import SafeConfParser
from zhanqun.utils import pagination

class ModuleList(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-list.html"
        self.module_key = "list"

    def _default_tdk(self, result, params, module_bread):
        tdk = {"title": u"跟谁学%s官网" % params.get("path_route").get("name"),
               "keywords": u"跟谁学%s官网" % params.get("path_route").get("name"),
               "description": u"跟谁学%s官网" % params.get("path_route").get("name"),
               }
        # if not len(result):
        #     return tdk
        return self._parse_tdk(params, {}, module_bread)

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        retrieve_conf = self._parse_retrieve_conf(module_conf, "list", params)
        if retrieve_conf.get("module_search"):
            retrieve_conf["module_search"]["base_url"] = pagination.base_url(params.get("request"), for_search = True)
        result = self.luna.retrieve(retrieve_conf.get("retrieve"))
        max_pageno = pagination.cal_max_pageno(result["amount"], retrieve_conf["size"])
        pageno_list = pagination.pageno_list(retrieve_conf["pageno"], max_pageno)
        return {"template": params.get("template"),
                "data": {
                        "list_result": result["records"],
                        "query": retrieve_conf.get("query", u''),
                        "pagination": pagination.pagination_new(pagination.base_url(params.get("request")), retrieve_conf["pageno"], pageno_list, max_pageno),
                        },
                "common": {
                        "REPORT": {"page_type": "zhanqun_%s_list" % params.get("path_route").get("domain")},
                        "module_bread": retrieve_conf.get("module_bread"),
                        "module_search": retrieve_conf.get("module_search"),
                        "GLOBAL": {
                            "page_id": retrieve_conf.get("page_id"),
                            "page_sub_id": retrieve_conf.get("page_sub_id"),
                            "query": retrieve_conf.get("query", u''),
                        },
                        "tdk": self._default_tdk([], params, retrieve_conf.get("module_bread")),
                        }
                }

class ModuleListMsite(ModuleList):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-list.html"
        self.module_key = "m.list"

class ModuleListMusic(ModuleList):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-list-music.html"
        self.module_key = "list-music"

class ModuleListVideo(ModuleList):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-list-video.html"
        self.module_key = "list-video"

class ModuleListMusicMsite(ModuleList):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-list-music.html"
        self.module_key = "m.list-music"

class ModuleListVideoMsite(ModuleList):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-list-video.html"
        self.module_key = "m.list-video"

class ModuleListAjax(ModuleList):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "list-ajax"
        self.module_key = "list-ajax"

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        retrieve_conf = self._parse_retrieve_conf(module_conf, "list", params)
        result = self.luna.retrieve(retrieve_conf.get("retrieve"))
        return {"template": params.get("template"), "data": result["records"]}
