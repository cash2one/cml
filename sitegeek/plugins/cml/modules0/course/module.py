#!/usr/bin/env python
#-*- coding:utf-8 -*-

from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco
from cml.module_conf import SafeConfParser

class ModuleCourse(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-course.html"
        self.module_key = "course"

    def _parse_course_conf(self, conf_obj):
        ret = {"row": conf_obj.get("course", "row"),
               "colum": conf_obj.get("course", "colum"),
               "resource": conf_obj.get("course", "resource"),
               "course_type": conf_obj.get("course", "course_type"),
               "query": conf_obj.get("course", "query"),
               }
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_course": self._parse_course_conf(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleCourseDetail(ModuleCourse):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-course-detail.html"
        self.module_key = "course-detail"

    @deco
    def load(self, params = {}):
        module_bread = [u"课程资源"]
        course_type = params.get("course_type")
        if not course_type:
            course_type = u"3"
        if course_type == "2":
            module_bread.append("机构班课")
        elif course_type == "3":
            module_bread.append("视频课")
        module_conf = self.get_module_conf(params)
        colum = False
        row = False
        resource = False
        course_query = False
        if module_conf:
            colum = module_conf.get("course", "colum")
            row = module_conf.get("course", "row")
            resource = module_conf.get("course", "resource")
            course_query = module_conf.get("course", "query")

        return {"template": params.get("template"),
                "data": {"course_type": course_type,
                         "colum": colum if colum else 1,
                         "row": row if row else 10,
                         "resource": resource if resource else u"baizhan",
                         "course_query": course_query if course_query else "",
                         },
                "common": {"GLOBAL": {"page_id": "course", "page_sub_id": course_type,},
                           "module_bread": module_bread,
                           "REPORT": {"page_type": "zhanqun_%s_course" % params.get("path_route").get("domain")},
                           "tdk": {
                               "title": u'课程资源 - 跟谁学%s官网' % params.get("path_route").get("name"),
                               "keywords": u'课程资源 - 跟谁学%s官网' % params.get("path_route").get("name"),
                               "description": u'课程资源 - 跟谁学%s官网' % params.get("path_route").get("name"),
                           },
                           }
                }

class ModuleCourseDetailMsite(ModuleCourseDetail):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-course-detail.html"
        self.module_key = "m.course-detail"

class ModuleCoursePanel(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-course-panel.html"
        self.module_key = "course-panel"

    def _parse_search_tab(self, conf_obj):
        search_tab = conf_obj.get("course_panel", "search_tab")
        if not search_tab:
            return []
        search_tab = [tab.strip() for tab in search_tab.strip().split(",")]
        ret = []
        for tab in search_tab:
            ret.append({"name": conf_obj.get(tab, "name"),
                        "course_type": conf_obj.get(tab, "course_type"),
                        "active": conf_obj.get(tab, "active")})
        return ret

    def _parse_course_panel_conf(self, conf_obj):
        ret = {
            "title": conf_obj.get("course_panel", "title"),
            "title_href": conf_obj.get("course_panel", "title_href"),
            "right_title": conf_obj.get("course_panel", "right_title"),
            "right_title_href": conf_obj.get("course_panel", "right_title_href"),
            "course_type": conf_obj.get("course_panel", "course_type"),
            "resource": conf_obj.get("course_panel", "resource"),
            "search_tab": self._parse_search_tab(conf_obj),
            "colum": conf_obj.get("course_panel", "colum"),
            "row": conf_obj.get("course_panel", "row"),
            "query": conf_obj.get("course_panel", "query"),
        }
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_course_panel": self._parse_course_panel_conf(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleCourseMsite(ModuleCoursePanel):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-course.html"
        self.module_key = "m.course"

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_course": self._parse_course_panel_conf(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleCourseBigImgMsite(ModuleCoursePanel):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-course-big-img.html"
        self.module_key = "m.course-big-img"

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_course": self._parse_course_panel_conf(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleAdsImg(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-ads-img.html"
        self.module_key = "ads-img"

    def _parse_panel_conf(self, module_conf, panel_key = "ads"):
        ret = {
            "title": module_conf.get(panel_key, "title"),
            "title_href": module_conf.get(panel_key, "title_href"),
            "size": module_conf.get(panel_key, "size"),
            "domain": module_conf.get(panel_key, "domain"),
        }
        if not ret["title"]:
            ret["title"] = u"精品推荐"
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_ads_img": self._parse_panel_conf(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleAdsImgMsite(ModuleAdsImg):
    def __init__(self, Luna, LunaSQL):
        ModuleAdsImg.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-ads-img.html"
        self.module_key = "m.ads-img"
