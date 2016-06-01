#!/usr/bin/env python
#-*- coding:utf-8 -*-
import urllib
from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco
from zhanqun.utils.common import split_list

# 一个标题，下面是内容。可用此样式
class ModuleContentPanelBaseMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-content-panel.html"
        self.module_key = "m.content-panel"

    def _parse_panel_conf(self, conf_obj, params, panel_key = "content-panel"):
        ret = {
            "title": conf_obj.get(panel_key, "title"),
            "title_href": conf_obj.get(panel_key, "title_href"),
            "right_title": conf_obj.get(panel_key, "right_title"),
            "right_title_href": conf_obj.get(panel_key, "right_title_href"),
            "label": conf_obj.get(panel_key, "label"),
            "style": conf_obj.get(panel_key, "style"),
            "imgpath": conf_obj.get(panel_key, "imgpath"),
        }

        # style in (list#文字列表单行 img#左图右字 imgtwo#两列图)
        if not ret["style"]:
            ret["style"] = "list"
        if not ret["imgpath"]:
            ret["imgpath"] = "list"

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
                        "cover": conf_obj.get(section, "cover"),
                    },
                })
            ret["result"] = result
        else:
            retrieve_conf = self._parse_retrieve_conf(conf_obj, panel_key, params)
            if retrieve_conf:
                result = self.luna.retrieve(retrieve_conf.get("retrieve"))
                ret["result"] = result
        if ret["style"] == "imgtwo":
            img_path_root = "/static/images/list/%s.jpg"
            img_mod = 20
            if ret["imgpath"] == "jita":
                img_path_root = "/static/images/jita/list/%s.jpg"
                img_mod = 10
            has_ids = {}
            data = []
            for record in ret["result"]["records"]:
                img_id = int(record["id"]) % img_mod + 1
                if img_id in has_ids:
                    img_id = (img_id + 1) % img_mod
                has_ids[img_id] = True
                record["static_img_path"] = img_path_root % img_id
                data.append(record)
            ret["result"]["records"] = data
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_content_panel": self._parse_panel_conf(module_conf, params)}
        return {"template": params.get("template"), "data": data}

class ModuleContentPanelBase(ModuleContentPanelBaseMsite):
    def __init__(self, Luna, LunaSQL):
        ModuleContentPanelBaseMsite.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-content-panel.html"
        self.module_key = "content-panel"

# 通栏三列，可用此样式，基于1100宽度。
class ModuleContentPanelThree(ModuleContentPanelBaseMsite):
    def __init__(self, Luna, LunaSQL):
        ModuleContentPanelBaseMsite.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-content-panel-three.html"
        self.module_key = "content-panel-three"

    def _parse_time_line(self, module_conf, panel_key = "right"):
        src_list = module_conf.get(panel_key, "src")
        if not src_list:
            return []
        ret = []
        for src in src_list.strip().split(","):
            src = src.strip()
            if not src:
                continue
            section = "%s_%s" % (panel_key, src)
            ret.append({
                "icon": module_conf.get(section, "icon"),
                "label": module_conf.get(section, "label"),
                "title": module_conf.get(section, "title"),
                "title_href": module_conf.get(section, "title_href"),
                "active": module_conf.get(section, "active"),
            })
        return ret

    def _parse_baike(self, conf_obj, panel_key = "baike"):
        baike_src = conf_obj.get(panel_key, "src")
        if not baike_src:
            return {}
        baike_src = [item.strip() for item in baike_src.strip().split(",") if item.strip()]
        ret = {"data":[],}
        count = 0
        for item in baike_src:
            baike_item = conf_obj.get(panel_key, item)
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
        ret["title"] = conf_obj.get(panel_key, "title")
        ret["title_href"] = conf_obj.get(panel_key, "title_href")
        return ret

    def _parse_three(self, module_conf, params):
        ret = {"left": {}, "middle": {}, "right": {}}
        left_result = self._parse_panel_conf(module_conf, params, "left")
        left_result_split = split_list(left_result["result"]["records"], {"highlight":(False, 1), "data":(1, False)})
        left_result["result"]["records"] = None
        left_result["result"]["highlight"] = left_result_split["highlight"][0]
        left_result["result"]["data"] = left_result_split["data"]
        ret["left"] = left_result
        if module_conf.get("left", "show_date") == "1":
            ret["left"]["show_date"] = True

        middle_result = self._parse_panel_conf(module_conf, params, "middle")
        middle_result_split = split_list(middle_result["result"]["records"], {"highlight":(False, 1), "data":(1, False)})
        middle_result["result"]["records"] = None
        middle_result["result"]["highlight"] = middle_result_split["highlight"][0]
        middle_result["result"]["data"] = middle_result_split["data"]
        ret["middle"] = middle_result
        if module_conf.get("middle", "show_date") == "1":
            ret["middle"]["show_date"] = True
        ret["right"] = self._parse_panel_conf(module_conf, params, "right")
        ret["right"]["timeline"] = self._parse_time_line(module_conf, "right")
        ret["right"]["baike"] = self._parse_baike(module_conf, "baike")
        return ret

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_content_panel_three": self._parse_three(module_conf, params)}
        return {"template": params.get("template"), "data": data}

# 通栏三列，可用此样式，基于1100宽度。
class ModuleContentPanelThreeTwo(ModuleContentPanelThree):
    def __init__(self, Luna, LunaSQL):
        ModuleContentPanelBaseMsite.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-content-panel-three-2.html"
        self.module_key = "content-panel-three-2"
