#!/usr/bin/env python
#-*- coding:utf-8 -*-

from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco
from django.shortcuts import Http404
import zhanqun

class ModuleDetail(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-detail.html"
        self.module_key = "detail"

    def _parse_tdk(self, params, result, module_bread):
        return {
            "title": self._default_title(result, params, module_bread),
            "keywords": self._default_keywords(result, params, module_bread),
            "description": self._parse_description(result),
        }

    def _parse_teacher_info(self, result):
        usernumber = result["content"].get("user_number")
        if not usernumber:
            return result
        try:
            user_info = zhanqun.settings.DBM_FACTORY.get_user_info.load({"user_number": usernumber})
            if user_info["amounts"]:
                result["content"]["PL_user_info"] = user_info["records"][0]
            return result
        except Exception as info:
            return result

    @deco
    def load(self, params = {}):
        request = params.get("request")
        template = params.get("template")
        try:
            result = self.luna.detail(self._parse_detail_params(params))
        except Exception as info:
            raise Http404
        data = {
            "result": self._parse_teacher_info(result),
        }
        params["_for_public"]["detail_title"] = result["content"].get("title")

        module_bread = result["content"].get("bread", result["subject"].split())
        module_bread = list(set(module_bread))
        priority = {
            "tdk": self._parse_tdk(params, result, set(module_bread + result["subject"].split())),
        }
        common = {
            "REPORT": {"page_type": "zhanqun_%s_detail" % params.get("path_route").get("domain")},
            "module_bread": module_bread,
        }
        try:
            if "geci_title" in result["content"]:
                common["module_geci"] = result
        except Exception as info:
            pass
        return {"template": template, "data": data, "common": common, "priority": priority}

class ModuleDetailMsite(ModuleDetail):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-detail.html"
        self.module_key = "m.detail"
