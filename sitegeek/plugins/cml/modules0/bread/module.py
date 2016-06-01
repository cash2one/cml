#!/usr/bin/env python
#-*- coding:utf-8 -*-

from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco

class ModuleBread(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-bread.html"
        self.module_key = "bread"

class ModuleBreadNoSearch(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-bread-nosearch.html"
        self.module_key = "bread-nosearch"

class ModuleBreadMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-bread.html"
        self.module_key = "m.bread"

class ModuleBreadButtonMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-bread-button.html"
        self.module_key = "m.bread-button"

    def _parse_bread_button(self, conf_obj, tag):
        if not tag:
            return []
        subs = conf_obj.get(tag, "sub")
        if not subs:
            return []
        ret = []
        for sub in subs.strip().split(","):
            ispl = conf_obj.get(sub, "pl")
            if ispl == "1":
                ret.append({"pl": True})
                continue
            ret.append({"id": conf_obj.get(sub, "id"),
                        "name": conf_obj.get(sub, "name"),
                        "url": conf_obj.get(sub, "url"),
                        "parent_id": conf_obj.get(sub, "parent_id"),
                        })
        return ret

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_bread_button": self._parse_bread_button(module_conf, params.get("tag"))}
        return {"template": params.get("template"), "data": data}
