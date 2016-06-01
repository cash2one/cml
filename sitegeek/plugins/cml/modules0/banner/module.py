#!/usr/bin/env python
#-*- coding:utf-8 -*-

from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco

class ModuleLongBanner(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-long-banner.html"
        self.module_key = "long-banner"

    def _parse_banner_conf(self, conf_obj):
        ret = {
            "imgsrc": conf_obj.get("banner", "imgsrc"),
            "href": conf_obj.get("banner", "href"),
            "imgtitle": conf_obj.get("banner", "imgtitle")
        }
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_long_banner": self._parse_banner_conf(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleSlideBanner(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-slide-banner.html"
        self.module_key = "slide-banner"

    def _parse_banner_conf(self, conf_obj):
        ret = []
        slides = conf_obj.get("banner", "tab")
        if not slides:
            return ret
        for slide in slides.strip().split(","):
            if not slide.strip():
                continue
            ret.append({
                "imgsrc": conf_obj.get(slide, "imgsrc"),
                "imghref": conf_obj.get(slide, "imghref"),
                "imgtitle": conf_obj.get(slide, "imgtitle")
            })
        return ret

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_slide_banners": self._parse_banner_conf(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleSlideBannerMsite(ModuleSlideBanner):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-slide-banner.html"
        self.module_key = "m.slide-banner"

class ModuleImageInfoBanner(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-image-info-banner.html"
        self.module_key = "image-info-banner"

    def _parse_panel_conf(self, conf_obj, params):
        panel_key = "image_info_banner"
        ret = {
            "title": conf_obj.get(panel_key, "title"),
            "title_href": conf_obj.get(panel_key, "title_href"),
            "right_title": conf_obj.get(panel_key, "right_title"),
            "right_title_href": conf_obj.get(panel_key, "right_title_href"),
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
                    "image": conf_obj.get(section, "image"),
                    "url": conf_obj.get(section, "url"),
                    "content": {
                        "title": conf_obj.get(section, "title"),
                    },
                })
            ret["result"] = result
        else:
            retrieve_conf = self._parse_retrieve_conf(conf_obj, panel_key, params)
            if retrieve_conf:
                result = self.luna.retrieve(retrieve_conf.get("retrieve"))
                ret["result"] = result

        tabs = conf_obj.get(panel_key, "tab")
        ret["tab_ret"] = []
        for tab in tabs.strip().split(","):
            tab = "tab_{}".format(tab)
            ret["tab_ret"].append({
                "url": conf_obj.get(tab, "url"),
                "name": conf_obj.get(tab, "name"),
            })
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_image_info_banner": self._parse_panel_conf(module_conf, params)}
        return {"template": params.get("template"), "data": data}

class ModuleFullBanner(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-full-banner.html"
        self.module_key = "full-banner"

    def _parse_banner_conf(self, conf_obj):
        ret = {
            "imgsrc": conf_obj.get("banner", "imgsrc"),
            "href": conf_obj.get("banner", "href"),
            "imgtitle": conf_obj.get("banner", "imgtitle")
        }
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_full_banner": self._parse_banner_conf(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleFullBannerMsite(ModuleFullBanner):
    def __init__(self, Luna, LunaSQL):
        ModuleFullBanner.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-full-banner.html"
        self.module_key = "m.full-banner"
