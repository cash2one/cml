#!/usr/bin/env python
#-*- coding:utf-8 -*-

from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco

class ModuleNavTabsMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-nav-tabs.html"
        self.module_key = "m.nav-tabs"

    def _parse_nav_tabs(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return []

        tabs = module_conf.get("nav-tabs", "tabs")
        if not tabs:
            return []
        ret = []
        for tab in tabs.strip().split(","):
            tab = tab.strip()
            _ret = {
                "name": module_conf.get(tab, "name"),
                "href": module_conf.get(tab, "href"),
                "imgsrc": module_conf.get(tab, "imgsrc"),
                "pl": module_conf.get(tab, "pl"),
            }

            if _ret["pl"] == "1":
                _ret["pl"] = True
            elif not _ret["name"] or not _ret["href"] or not _ret["imgsrc"]:
                continue

            ret.append(_ret)
        return ret
    @deco
    def load(self, params):
        data = {
            "module_nav_tabs": self._parse_nav_tabs(params)
        }
        return {"template": params.get("template"), "data": data}

class ModuleNavTabsJitaMsite(ModuleNavTabsMsite):
    def __init__(self, Luna, LunaSQL):
        ModuleNavTabsMsite.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-nav-tabs-jita.html"
        self.module_key = "m.nav-tabs-jita"

class ModuleNavTabsButtonMsite(ModuleNavTabsMsite):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-nav-tabs-button.html"
        self.module_key = "m.nav-tabs-button"

    @deco
    def load(self, params):
        data = {
            "module_nav_tabs_button": self._parse_nav_tabs(params)
        }
        return {"template": params.get("template"), "data": data}
