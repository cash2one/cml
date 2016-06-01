#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.shortcuts import render
from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco
from common.utils.pv_statistic import get_top_n

class ModuleGuitarDetail(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "guitar/detail.html"
        self.module_key = "guitar-detail"

    @deco
    def load(self, params = {}):
        request = params.get("request")
        template = params.get("template")
        result = self.luna.detail(self._parse_detail_params(params))

        page_type = "wenzhang"
        if result["subject"].find(u"吉他谱") != -1:
            page_type = "qupu"
        elif result["subject"].find(u"吉他问答") != -1:
            page_type = "wenda"
        elif result["subject"].find(u"吉他视频") != -1:
            page_type = "video"

        hot_qupu_id = get_top_n(u"吉他 吉他谱", 6)
        hot_qupu = []
        for _id in hot_qupu_id:
            hot_qupu.append(self.luna.detail({"db_id": _id, "user_agent": self._parse_user_agent(params)}))
        data = {
            "result": result,
            "page_type": page_type,
            "hot_qupu": hot_qupu,
        }

        if "answers" in result["content"]:
            description = result["content"]["title"]
        else:
            try:
                description = result["content"]["content"]
            except:
                try:
                    description = result["content"]["title"]
                except:
                    description = u''
        priority = {
            "tdk": {
                "title": result["content"]["title"] + u" - 跟谁学吉他官网",
                "keywords": result["content"]["title"],
                "description": description,
            },
        }
        common = {
            "REPORT": {"page_type": "zhanqun_jita_detail"},
        }
        return {"template": template, "data": data, "common": common, "priority": priority}

class ModuleGuitarDetailMsite(ModuleGuitarDetail):
    def __init__(self, Luna, LunaSQL):
        ModuleGuitarDetail.__init__(self, Luna, LunaSQL)
        self.template = "guitar/m.detail.html"
        self.module_key = "m.guitar-detail"

class ModuleGuitarHot(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/jita/hot.html"
        self.module_key = "guitar-hot"

    @deco
    def load(self, params):
        hot_qupu_id = get_top_n(u"吉他 吉他谱", 6)
        hot_qupu = []
        for _id in hot_qupu_id:
            hot_qupu.append(self.luna.detail({"db_id": _id, "user_agent": self._parse_user_agent(params)}))
        data = {
            "module_list_panel": hot_qupu,
        }
        return {"template": params.get("template"), "data": data}

class ModuleGuitarHotMsite(ModuleGuitarHot):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/jita/hot.html"
        self.module_key = "m.guitar-hot"

class ModuleGuitarFindTeacher(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/jita/find-teacher.html"
        self.module_key = "guitar-find-teacher"

class ModuleGuitarFindTeacherMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/jita/find-teacher.html"
        self.module_key = "m.guitar-find-teacher"

class ModuleGuitarGeci(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/jita/geci.html"
        self.module_key = "guitar-geci"
