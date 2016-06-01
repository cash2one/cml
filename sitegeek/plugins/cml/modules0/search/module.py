#!/usr/bin/env python
#-*- coding:utf-8 -*-

from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco
import urllib

class ModuleSearchMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-search.html"
        self.module_key = "m.search"

class ModuleSearch(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-search.html"
        self.module_key = "search"

    def _parse_search_conf(self, conf_obj, params, panel_key = "search-panel"):
        hots = conf_obj.get(panel_key, "hot")
        if not hots:
            return []
        ret = {
            "hot": [],
        }
        for hot in hots.strip().split(","):
            name = conf_obj.get(hot.strip(), "name")
            url = conf_obj.get(hot.strip(), "url")
            if not name:
                continue
            if not url:
                url = "/s/%s/" % urllib.quote(name)
            ret["hot"].append({
                "name": name,
                "url": url,
            })
        return ret

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}

        data = {"module_search": self._parse_search_conf(module_conf, params)}
        return {"template": params.get("template"), "data": data}
