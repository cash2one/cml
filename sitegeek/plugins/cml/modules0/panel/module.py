#!/usr/bin/env python
#-*- coding:utf-8 -*-
import urllib
from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco
from zhanqun.utils.common import split_list
import random
class ModuleRightPanelStyleOne(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-right-panel-1.html"
        self.module_key = "right-panel-1"

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
                ret["result"] = result
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_right_panel": self._parse_panel_conf(module_conf, params)}
        return {"template": params.get("template"), "data": data}

class ModuleRightPanelStyleTwo(ModuleRightPanelStyleOne):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-right-panel-2.html"
        self.module_key = "right-panel-2"

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_right_panel": self._parse_panel_conf(module_conf, params)}
        return {"template": params.get("template"), "data": data}

class ModuleRightPanelStyleThree(ModuleRightPanelStyleOne):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-right-panel-3.html"
        self.module_key = "right-panel-3"

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_right_panel": self._parse_panel_conf(module_conf, params)}
        return {"template": params.get("template"), "data": data}

# 当内容分为上下两种类型显示时，可用此样式
class ModuleTabNewsPanel(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-tab-news.html"
        self.module_key = "tab-news-panel"

    def _parse_data(self, conf_obj, size, params):
        ret = {"labels": [], "detail": []}
        tab = conf_obj.get("news_panel", "tab")
        if not tab:
            return ret
        for _tab in tab.strip().split(","):
            if not _tab.strip():
                continue
            name = conf_obj.get(_tab, "name")
            if not name:
                continue
            retrieve_conf = self._parse_retrieve_conf(conf_obj, _tab, params)
            if not retrieve_conf:
                continue
            ret["labels"].append(name)
            result = self.luna.retrieve(retrieve_conf.get("retrieve"))
            ret["detail"].append(split_list(result["records"], {"up": (False, 1), "down": (1, False)}))
            ret["detail"][-1]["up"] = ret["detail"][-1]["up"][0] if len(ret["detail"][-1]["up"]) else False

        ret["labels"].extend([False] * (size - len(ret["labels"])))
        return ret

    def _parse_panel_conf(self, conf_obj, params):
        size = conf_obj.get("news_panel", "size")
        if not size:
            size = 6

        ret = {
            "title": conf_obj.get("news_panel", "title"),
            "title_href": conf_obj.get("news_panel", "title_href"),
            "right_title": conf_obj.get("news_panel", "right_title"),
            "right_title_href": conf_obj.get("news_panel", "right_title_href"),
            "size": size,
            "key": conf_obj.get("news_panel", "key") if conf_obj.get("news_panel", "key") else 1,
            "data": self._parse_data(conf_obj, size, params),
        }
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_news_panel": self._parse_panel_conf(module_conf, params)}
        return {"template": params.get("template"), "data": data}

class ModuleWenDaPanel(ModuleTabNewsPanel):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-wenda-panel.html"
        self.module_key = "wenda-panel"

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_wenda_panel": self._parse_panel_conf(module_conf, params)}
        return {"template": params.get("template"), "data": data}

class ModuleVideoPanel(ModuleRightPanelStyleOne):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-video-panel.html"
        self.module_key = "video-panel"

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_video_panel": self._parse_panel_conf(module_conf, params, "video-panel")}
        return {"template": params.get("template"), "data": data}

class ModuleListPanelMsite(ModuleRightPanelStyleOne):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-list-panel.html"
        self.module_key = "m.list-panel"

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_list_panel": self._parse_panel_conf(module_conf, params, "list-panel")}
        return {"template": params.get("template"), "data": data}

class ModuleHotSearchPanel(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-hot-search-panel.html"
        self.module_key = "hot-search-panel"

    def _parse_keywords(self, module_conf):
        keywords = module_conf.get("hot-search", "keywords")
        if not keywords:
            return []
        ret = []
        for keyword in keywords.strip().split(","):
            keyword = keyword.strip()
            if not keyword:
                continue
            name = module_conf.get(keyword, "name")
            if not name:
                continue

            url = module_conf.get(keyword, "url")
            if not url:
                if type(name) == type(u""):
                    name = name.encode("utf-8")
                url = u"/s/%s/" % urllib.quote(name)
            ret.append({
                "name": name,
                "url": url,
            })
        return ret

    def _parse_hot_search(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return module_conf
        ret = {
            "title": module_conf.get("hot-search", "title"),
            "title_href": module_conf.get("hot-search", "title_href"),
            "keywords": self._parse_keywords(module_conf),
            "imghref": module_conf.get("hot-search", "imghref"),
            "imgsrc": module_conf.get("hot-search", "imgsrc"),
            "imgtitle": module_conf.get("hot-search", "imgtitle"),
        }
        return ret

    @deco
    def load(self, params):
        data = {"module_hot_search": self._parse_hot_search(params)}
        return {"template": params.get("template"), "data": data}

class ModuleHotSearchPanelTwo(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-hot-search-panel-2.html"
        self.module_key = "hot-search-panel-2"

    def _parse_keywords(self, module_conf):
        size = module_conf.get("hot-search", "size")
        if not size:
            size = 20
        else:
            try:
                size = int(size)
            except Exception as info:
                size = 20
        keywords = module_conf.get("hot-search", "keywords")
        if not keywords:
            return []
        ret = []
        for keyword in keywords.strip().split(","):
            keyword = keyword.strip()
            if not keyword:
                continue
            if type(keyword) == type(u""):
                keyword = keyword.encode("utf-8")
            url = u"/s/%s/" % urllib.quote(keyword)
            ret.append({
                "name": keyword,
                "url": url,
            })
        if size >= len(ret):
            offset = 0
        else:
            offset = random.randint(0, len(ret) - 1 - size)
        ret = ret[offset:offset + size]
        return ret

    def _parse_hot_search(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return module_conf
        ret = {
            "title": module_conf.get("hot-search", "title"),
            "title_href": module_conf.get("hot-search", "title_href"),
            "keywords": self._parse_keywords(module_conf),
        }
        return ret

    @deco
    def load(self, params):
        data = {"module_hot_search": self._parse_hot_search(params)}
        return {"template": params.get("template"), "data": data}

class ModuleHotSearchPanelThree(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-hot-search-panel-3.html"
        self.module_key = "hot-search-panel-3"

    def _parse_panel_conf(self, conf_obj, params, panel_key):
        ret = {
            "title": conf_obj.get(panel_key, "title"),
            "title_href": conf_obj.get(panel_key, "title_href"),
            "size": conf_obj.get(panel_key, "size"),
        }
        if not ret["size"]:
            ret["size"] = 40

        status = conf_obj.get(panel_key, "status")
        if not status:
            status = "0"

        base_url = conf_obj.get(panel_key, "base-url")
        domain = conf_obj.get(panel_key, "domain")
        if not domain:
            domain = params.get("path_route").get("domain")

        sql = '''SELECT * FROM `zhanqun_cml_domain_keywords` WHERE `status` = %s AND `domain` = "%s"''' % (status, domain)
        try:
            keywords = self.luan_sql.raw(sql)
            if not keywords:
                return {}
            if int(ret["size"]) > len(keywords):
                keywords = keywords
            else:
                keywords = random.sample(keywords, int(ret["size"]))
            if base_url:
                base_url = base_url.strip()
                keywords_filter = []
                for item in keywords:
                    if not item.get("url").strip().startswith("http"):
                        url = item["url"].strip()
                        if url:
                            item["url"] = "/".join([base_url.rstrip("/"), url.lstrip("/")])
                        else:
                            item["url"] = "/".join([base_url.rstrip("/"), "s/%s/" % urllib.quote(item.get("keyword").encode("utf-8"))])
                    keywords_filter.append(item)
            else:
                keywords_filter = keywords

            ret["keywords"] = keywords_filter
        except Exception as info:
            return {}
        return ret

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {
            "module_hot_search": self._parse_panel_conf(module_conf, params, "hot-search"),
        }
        return {"template": params.get("template"), "data": data}

class ModuleHotSearchPanelThreeMsite(ModuleHotSearchPanelThree):
    def __init__(self, Luna, LunaSQL):
        ModuleHotSearchPanelThree.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-hot-search-panel-3.html"
        self.module_key = "m.hot-search-panel-3"

class ModuleTopicPanel(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-topic-panel.html"
        self.module_key = "topic-panel"

    def _parse_panel_conf(self, conf_obj, params, panel_key):
        ret = {
            "title": conf_obj.get(panel_key, "title"),
            "title_href": conf_obj.get(panel_key, "title_href"),
            "sub_title": conf_obj.get(panel_key, "sub_title"),
            "sub_title_href": conf_obj.get(panel_key, "sub_title_href")
        }

        left = {
            "imgsrc": conf_obj.get(panel_key, "leftimgsrc"),
            "imghref": conf_obj.get(panel_key, "leftimghref")
        }
        ret["left"] = left

        right = []
        right_tab = conf_obj.get(panel_key, "right")
        if not right_tab:
            return False
        for tab in right_tab.strip().split(","):
            url = conf_obj.get(tab, "url")
            title = conf_obj.get(tab, "title")
            label = conf_obj.get(tab, "label")
            imgsrc = conf_obj.get(tab, "imgsrc")
            if not title or not imgsrc:
                continue
            right.append({
                "url": url,
                "title": title,
                "imgsrc": imgsrc,
                "label": label if label else "",
            })
        ret["right"] = right[:3]
        return ret

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {
            "module_topic_panel": self._parse_panel_conf(module_conf, params, "topic-panel"),
        }
        return {"template": params.get("template"), "data": data}

class ModuleTopicPanelMsite(ModuleTopicPanel):
    def __init__(self, Luna, LunaSQL):
        ModuleTopicPanel.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-topic-panel.html"
        self.module_key = "m.topic-panel"

class ModuleTopicDirectPanel(ModuleHotSearchPanelThree):
    def __init__(self, Luna, LunaSQL):
        ModuleHotSearchPanelThree.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-topic-direct-panel.html"
        self.module_key = "topic-direct-panel"

class ModuleFreeRichTextAreaPanel(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-free-rich-text-area-panel.html"
        self.module_key = "free-rich-text-area-panel"

    def _parse_panel_conf(self, conf_obj, params, panel_key = "free-area"):
        ret = {
            "rich_text": conf_obj.get(panel_key, "rich_text"),
            "avatar": conf_obj.get(panel_key, "avatar"),
            "avatar_href": conf_obj.get(panel_key, "avatar_href"),
            "singer": conf_obj.get(panel_key, "singer"),
            "brief": conf_obj.get(panel_key, "brief"),
            "singer_href": conf_obj.get(panel_key, "singer_href"),
            "desc": conf_obj.get(panel_key, "desc"),
        }
        return ret

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {
            "module_free_area": self._parse_panel_conf(module_conf, params, "free-area"),
        }
        return {"template": params.get("template"), "data": data}

class ModuleFreeRichTextAreaPanelMsite(ModuleFreeRichTextAreaPanel):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-free-rich-text-area-panel.html"
        self.module_key = "m.free-rich-text-area-panel"
