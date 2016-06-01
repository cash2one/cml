#!/usr/bin/env python
#-*- coding:utf-8 -*-

from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco
from zhanqun.resource import zhanqun_resource_dict
import random
import urllib
import urlparse

class ModuleHome(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-home.html"
        self.module_key = "home"

    def _parse_sub_src(self, conf_obj, src, url):
        ret = []
        subs = conf_obj.get(src, "sub")
        if not subs:
            return ret
        for sub in subs.strip().split(","):
            sub = sub.strip()
            if not sub:
                continue
            sub_key = "_".join([src, sub])
            sub_name = conf_obj.get(sub_key, "name")
            if not sub_name:
                continue
            sub_url = conf_obj.get(sub_key, "url")
            if not sub_url:
                if type(sub_name) == type(u''):
                    _sub_name = sub_name.encode("utf-8")
                else:
                    _sub_name = sub_name
                sub_url = "/".join([url.strip().rstrip("/"), "/s/{}/".format(urllib.quote(_sub_name)).strip().lstrip("/")])
            ret.append({
                "name": sub_name,
                "url": sub_url,
            })
        return ret

    def _parse_web_map(self, params):
        params["debug"] = True
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return []
        ret = []
        webmap = module_conf.get("webmap", "src")
        for src in webmap.strip().split(","):
            if not src.strip():
                continue
            name = module_conf.get(src, "name")
            url = module_conf.get(src, "url")
            if not name or not url:
                continue
            tmp = {
                "name": name,
                "url": url,
                "sub": self._parse_sub_src(module_conf, src, url)
            }
            ret.append(tmp)
        return ret

    @deco
    def load(self, params):
        wordcloud = []
        for key in zhanqun_resource_dict:
            _dict = zhanqun_resource_dict.get(key)
            if _dict.get("debug"):
                continue
            wordcloud.append({
                "name": _dict.get("name"),
                "weight": random.randint(1, 100),
                "url": "http://www.genshuixue.com/i-{}/".format(key),
            })
        data = {"wordcloud": wordcloud,
                "webmap": self._parse_web_map(params)}
        return {"template": params.get("template"), "data": data, "common": {"GLOBAL": {"site_name": u"站点地图"}}}
