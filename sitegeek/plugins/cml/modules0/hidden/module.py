#!/usr/bin/env python
#-*- coding:utf-8 -*-

from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco

class ModuleHiddenForSearchPanel(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-hidden.html"
        self.module_key = "hidden-for-search"

    def _parse_hidden(self, conf_obj, pannel_key = "hidden-pannel"):
        ret = {
            "module_search": {
                "base_url": conf_obj.get(pannel_key, 'base_url'),
                "datasrc": conf_obj.get(pannel_key, 'datasrc')
            }
        }
        return ret

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template"),}
        return {"template": params.get("template"), "common": self._parse_hidden(module_conf)}

class ModuleHiddenJitaHomeMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-hidden.html"
        self.module_key = "m.hidden-jita-home"

    @deco
    def load(self, params):
        return {"template": params.get("template"),
                "common": {
                    "module_search": {
                        "base_url": u"/i-jita/a/200/?",
                        "datasrc": u"jita",
                    }
                }
            }

class ModuleHiddenPianoHomeMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-hidden.html"
        self.module_key = "m.hidden-piano-home"

    @deco
    def load(self, params):
        return {"template": params.get("template"),
                "common": {
                    "module_search": {
                        "base_url": u"/i-gangqin/a/200/?",
                        "datasrc": u"gangqin",
                    }
                }
            }
