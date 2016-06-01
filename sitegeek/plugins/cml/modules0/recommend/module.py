#!/usr/bin/env python
#-*- coding:utf-8 -*-
from cml.modules.common.module import deco
from cml.modules.common.module import ModuleBase
from cml.modules.panel.module import ModuleRightPanelStyleOne
from common.utils.pv_statistic import get_top_n
import random

class ModuleRecommendPanel(ModuleRightPanelStyleOne):
    def __init__(self, Luna, LunaSQL):
        ModuleRightPanelStyleOne.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-recommend-panel.html"
        self.module_key = "recommend-panel"

    def _parse_panel_conf(self, conf_obj, params, panel_key = "right_panel"):
        ret = {
            "title": conf_obj.get(panel_key, "title"),
            "title_href": conf_obj.get(panel_key, "title_href"),
            "right_title": conf_obj.get(panel_key, "right_title"),
            "right_title_href": conf_obj.get(panel_key, "right_title_href"),
            "label": conf_obj.get(panel_key, "label"),
            "style": conf_obj.get(panel_key, "style"),
        }

        static = conf_obj.get(panel_key, "static")
        static_data = conf_obj.get(panel_key, "static_data")
        if static == "1" and static_data:
            ret["static"] = True
            result = {"records": []}
            for section in static_data.strip().split(","):
                section = "static_data_{}".format(section)
                result["records"].append({
                    "id": conf_obj.get(section, "id"),
                    "content": {
                        "title": conf_obj.get(section, "title"),
                        "url": conf_obj.get(section, "url"),
                    },
                })
            ret["result"] = result
        else:
            retrieve_conf = self._parse_retrieve_conf(conf_obj, panel_key, params)
            if retrieve_conf:
                result = self.luna.retrieve(retrieve_conf.get("retrieve"))
                if params.get("db_id"):
                    ret["result"] = {"records": []}
                    db_id = str(params.get("db_id"))
                    for res in result["records"]:
                        if str(res.get("id")) != db_id:
                            ret["result"]["records"].append(res)
                    result.pop("records")
                    for key in result:
                        ret["result"][key] = result[key]
                else:
                    ret["result"] = result
        return ret

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        if params.get("db_id"):
            params["recommend-query"] = params["_for_public"].get("detail_title")
            params["recommend-offset"] = 0
        data = {"module_recommend_list": self._parse_panel_conf(module_conf, params, "recommend-panel")}
        return {"template": params.get("template"), "data": data}

class ModuleRecommendPanelMsite(ModuleRecommendPanel):
    def __init__(self, Luna, LunaSQL):
        ModuleRightPanelStyleOne.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-recommend-panel.html"
        self.module_key = "m.recommend-panel"

class ModuleRecommendPanelTwoMsite(ModuleRecommendPanel):
    def __init__(self, Luna, LunaSQL):
        ModuleRightPanelStyleOne.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-recommend-panel-2.html"
        self.module_key = "m.recommend-panel-2"

class ModuleHotPanel(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-recommend-panel.html"
        self.module_key = "hot-panel"

    def _parse_panel_conf(self, conf_obj, params, panel_key):
        ret = {
            "title": conf_obj.get(panel_key, "title"),
            "title_href": conf_obj.get(panel_key, "title_href"),
            "right_title": conf_obj.get(panel_key, "right_title"),
            "right_title_href": conf_obj.get(panel_key, "right_title_href"),
            "size": conf_obj.get(panel_key, "size"),
            "result": {"records": [], "amounts": 0}
        }
        subject = conf_obj.get(panel_key, "subject")
        if not subject:
            return []
        if not ret["size"]:
            ret["size"] = 7
        hot_id_list = get_top_n(subject, int(ret["size"]))
        if not hot_id_list:
            return []
        hot = []
        for _id in hot_id_list:
            hot.append(self.luna.detail({"db_id": _id, "user_agent": self._parse_user_agent(params)}))
        ret["result"]["records"] = hot
        ret["result"]["amounts"] = len(hot)
        return ret

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {
            "module_recommend_list": self._parse_panel_conf(module_conf, params, "hot-panel"),
        }
        return {"template": params.get("template"), "data": data}

class ModuleHotPanelTwo(ModuleHotPanel):
    def __init__(self, Luna, LunaSQL):
        ModuleHotPanel.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-hot-panel.html"
        self.module_key = "hot-panel-2"

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {
            "module_hot_panel": self._parse_panel_conf(module_conf, params, "hot-panel"),
        }
        return {"template": params.get("template"), "data": data}

class ModuleHotPanelTwoMsite(ModuleHotPanelTwo):
    def __init__(self, Luna, LunaSQL):
        ModuleHotPanelTwo.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-hot-panel.html"
        self.module_key = "m.hot-panel-2"
