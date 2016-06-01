#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.shortcuts import render
from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco
from cml.module_conf import SafeConfParser
from zhanqun.utils.common import split_list

class ModuleYasiBaike(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/yasi/baike.html"
        self.module_key = "yasi-baike"

    def _parse_yasi_baike(self, conf_obj):
        baike_src = conf_obj.get("baike", "src")
        if not baike_src:
            return {}
        baike_src = [item.strip() for item in baike_src.strip().split(",") if item.strip()]
        ret = {"data":[],}
        count = 0
        for item in baike_src:
            baike_item = conf_obj.get("baike", item)
            if not baike_item:
                continue
            count += 1
            if count != len(baike_src) and count % 3 == 0:
                pl = True
            else:
                pl = False
            name, url, _id, is_inner = [bi.strip() for bi in baike_item.split(",")]
            ret["data"].append({"url": url.decode("utf-8"),
                        "name": name.decode("utf-8"),
                        "id": _id,
                        "is_inner": True if is_inner == "1" else False,
                        "pl": pl,
                        }
                      )
        ret["data"] = enumerate(ret["data"])
        ret["title"] = conf_obj.get("baike", "title")
        ret["title_href"] = conf_obj.get("baike", "title_href")
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_yasi_baike": self._parse_yasi_baike(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleYasiBaikeTwo(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/yasi/baike-2.html"
        self.module_key = "yasi-baike-2"

class ModuleYasiBaikeDetail(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/yasi/baike-detail.html"
        self.module_key = "yasi-baike-detail"

    def _parse_sub_baike_resource(self, conf_obj, section):
        sub = conf_obj.get(section, "sub")
        if not sub:
            return []
        ret = []
        for s in sub.strip().split(","):
            sec_key = "_".join([section, s])
            item = {"id": conf_obj.get(sec_key, "id"),
                    "name": conf_obj.get(sec_key, "name"),
                    "is_inner": conf_obj.get(sec_key, "is_inner"),
                    "url": conf_obj.get(sec_key, "url"),
                    }
            ret.append(item)
        return ret

    def _parse_baike_resource(self, conf_obj):
        section = conf_obj.get("baike", "section")
        if not section:
            return []
        ret = []
        for sec in section.strip().split(","):
            item = {"id": conf_obj.get(sec, "id"),
                    "name": conf_obj.get(sec, "name"),
                    "sub": self._parse_sub_baike_resource(conf_obj, sec)
                    }
            ret.append(item)
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        baike_resource = {}
        if module_conf:
            baike_resource = self._parse_baike_resource(module_conf)
        result = self.luna.detail(self._parse_detail_params(params))
        data = {"result": result,
                "baike_resource": baike_resource,
                "section": params.get("section"),
                "baike_id": params.get("baike_id"),
                }
        module_bread = result["content"].get("bread", result["subject"].split())
        module_bread = list(set(module_bread))
        priority = {
            "tdk": self._parse_tdk(params, result, set(module_bread + result["subject"].split())),
        }
        return {"template": params.get("template"),
                "data": data,
                "common": {
                    "REPORT": {"page_type": "zhanqun_yasi_baike"},
                    "GLOBAL": {"page_id": "baike"},
                    "module_bread": module_bread,
                    "tdk": {
                        "title": self._default_title(result, params, module_bread),
                        "keywords": self._default_keywords(result, params, module_bread),
                        "description": self._parse_description(result),
                    }
                },
                "priority": priority,
                }

class ModuleYasiStudyPlan(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/yasi/study_plan.html"
        self.module_key = "yasi-study-plan"

class ModuleYasiHome(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/yasi/home.html"
        self.module_key = "yasi-home"


class ModuleYasiCalendar(ModuleYasiBaike):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/yasi/calendar.html"
        self.module_key = "yasi-calendar"

    def _parse_exam_js_string(self, conf_obj, key = "exam"):
        '''
          var exam_time_object = {
            "201601": [9, 14, 23, 30],
            "201602": [13, 18, 20, 27],
            "201603": [5, 12, 19, 31],
            "201604": [2, 16, 21, 30],
            "201605": [7, 19, 21, 28],
            "201606": [4, 16, 18, 25],
            "201607": [9, 14, 16, 30],
            "201608": [4, 13, 20, 27],
            "201609": [3, 10, 15, 24],
            "201610": [8, 13, 22, 29],
            "201611": [3, 5, 19, 26],
            "201612": [3, 10, 15, 17]
          };
        '''
        exam_date_obj_string = '''{'''
        date_arr = conf_obj.get(key, "date_arr")
        if date_arr and date_arr.strip():
            for date_string in date_arr.strip().split(","):
                date_string = date_string.strip()
                date_content = conf_obj.get(key, date_string)
                if not date_content:
                    continue
                exam_date_obj_string += '''"%s": %s,''' % (date_string, date_content)
        exam_date_obj_string = exam_date_obj_string.rstrip(",")
        exam_date_obj_string += '''}'''
        ret = {"exam_time_object": exam_date_obj_string,
               "start_date": conf_obj.get(key, "start_date"),
               "end_date": conf_obj.get(key, "end_date"),
               "exam_zkzdy_time": conf_obj.get(key, "exam_zkzdy_time"),
               "exam_chaxun_time": conf_obj.get(key, "exam_chaxun_time"),
               "exam_jisong_time": conf_obj.get(key, "exam_jisong_time"),
               "exam_zkzdy_days": conf_obj.get(key, "exam_zkzdy_days"),
               "exam_chaxun_days": conf_obj.get(key, "exam_chaxun_days"),
               "exam_jisong_days": conf_obj.get(key, "exam_jisong_days"),
               }
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        baike = {}
        if module_conf:
            baike = self._parse_yasi_baike(module_conf)

        retrieve_conf = self._parse_retrieve_conf(module_conf, "news", params)
        result = self.luna.retrieve(retrieve_conf.get("retrieve"))

        module_news = split_list(result["records"], {"highlight":(False, 1), "data":(1, False)})
        module_news["highlight"] = module_news["highlight"][0]
        if module_conf.get("news", "show_date") == "1":
            module_news["show_date"] = True

        exam_js_string = self._parse_exam_js_string(module_conf)

        data = {"baike": baike, "module_news": module_news, "exam": exam_js_string, "calendar_title": module_conf.get("calendar", "title")}
        return {"template": params.get("template"),
                "data": data,
                }

class ModuleYasiCalendar2(ModuleYasiCalendar):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/yasi/calendar_2.html"
        self.module_key = "yasi-calendar-2"

class ModuleYasiFooterBannerMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/yasi/footer-banner.html"
        self.module_key = "m.yasi-footer-banner"

class ModuleYasiBaikeDetailMsite(ModuleYasiBaikeDetail):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/yasi/baike-detail.html"
        self.module_key = "m.yasi-baike-detail"
