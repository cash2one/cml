#!/usr/bin/env python
#-*- coding:utf-8 -*-
import ConfigParser
import copy
import urllib
import re
from django.shortcuts import render
from cml.module_conf import ConfUtils
from cml.module_conf import SafeConfParser
from zhanqun.utils.common import get_version
from zhanqun.utils.common import merge_dict
import random
from cml.switches import DYNC_cml_conf_db
from cml.module_conf_parser import BaseDict

def deco(func):
    def _deco(clazz, params = {}):
        request = params.get("request")
        if not request:
            return {}
        template = params.get("template")
        _params = params
        if not template:
            _params = merge_dict(params, {"template": clazz.template})
        else:
            _params = params
        return func(clazz, params = _params)
    return _deco

class ModuleBase(object):
    '''
        所有module必须继承此module
        每个module必须定义全局唯一module_key
    '''
    def __init__(self, Luna, LunaSQL):
        self.luna = Luna
        self.luan_sql = LunaSQL
        self.repeat = False
        self.module_key = "base"

    def get_module_conf(self, params):
        module_conf = params.get("module_conf")
        if not module_conf:
            return False
        module_conf = "conf_{}".format(module_conf)
        conf_dict = params.get("conf_dict", {})
        if not conf_dict:
            return False
        try:
            if DYNC_cml_conf_db:
                module_conf = conf_dict.get("module_conf").get(module_conf)
                module_conf = BaseDict(module_conf)
                if module_conf.empty():
                    return False
                return module_conf
            else:
                module_conf = ConfUtils.get_conf_name(conf_dict.conf_root, conf_dict[module_conf])
                return SafeConfParser(module_conf)
        except Exception as info:
            return False

    @deco
    def load(self, params = {}):
        return {"template": params.get("template")}

    def _place_holder(self, ret, params):
        for key in ret:
            if type(ret[key]) == type(u''):
                if ret[key].find("{domain_name}") != -1:
                    ret[key] = ret[key].replace("{domain_name}", params.get("path_route").get("name"))

    def _parse_tags(self, conf_path, params):
        if DYNC_cml_conf_db:
            conf_obj = BaseDict(conf_path)
        else:
            if conf_path.strip().startswith("file:"):
                conf_path = conf_path.replace(r"file:", "")
            conf_path = ConfUtils.get_conf_name(params["conf_dict"].conf_root, conf_path)
            conf_obj = SafeConfParser(conf_path)

        if not conf_obj:
            return {}
        tags = params.get('tags')
        if not tags:
            return {}
        if tags[0] == "0":
            return {}

        module_bread = []
        if not tags[1]:
            tag_key = tags[0]
            module_bread.append(conf_obj.get(tag_key, "name"))
        else:
            module_bread.append(conf_obj.get(tags[0], "name"))
            tag_key = "_".join(tags)
            module_bread.append(conf_obj.get(tag_key, "name"))

        ret = set()

        for tag in self._parse_tag_key(conf_obj, tag_key):
            ret.add(tag)
        sub = conf_obj.get(tag_key, "sub")
        if sub:
            for _sub in sub.strip().split(","):
                _sub_key = "_".join([tag_key, _sub.strip()])
                for tag in self._parse_tag_key(conf_obj, _sub_key):
                    ret.add(tag)
        return {"tag": list(ret), "page_id": tags[0], "page_sub_id": tags[1], "subject": conf_obj.get(tags[0], "subject"), "query": conf_obj.get(tags[0], "query"), "module_bread": module_bread}

    def _parse_tag_key(self, conf_obj, key):
        ret = set()
        if conf_obj.get(key, "nofollow"):
            return ret
        tag = conf_obj.get(key, "tag")
        if tag:
            for _tag in tag.strip().split(","):
                ret.add(_tag.strip().decode("utf-8"))
        return ret

    def _parse_description(self, result):
        if not result:
            result["content"] = {}
        if "desc" in result["content"]:
            return re.sub(r'\s+', ' ', result["content"]["desc"])
        description = u''
        if "answers" in result["content"]:
            description = re.sub(r'\s+', ' ', "".join([item.get("content", u'').strip() for item in result["content"]["answers"]]))
        else:
            try:
                description = re.sub(r'\s+', ' ', result["content"]["content"])
            except:
                try:
                    description = re.sub(r'\s+', ' ', result["content"]["title"])
                except:
                    description = u''
        return description

    def _default_title(self, result, params, module_bread):
        if not result:
            result["content"] = {}
        if "title" in result["content"]:
            ret = result["content"]["title"]
        else:
            ret = u""
        if module_bread:
            for bread in module_bread:
                ret += u"_{}".format(bread)
        ret += u"_跟谁学{}官网".format(params.get("path_route").get("name"))
        return ret.strip("_")

    def _default_keywords(self, result, params, module_bread):
        ret = set()
        if not result:
            result["content"] = {}
        if "keywords" in result["content"]:
            for k in result["content"]["keywords"].split(","):
                ret.add(k)

        if "title" in result["content"]:
            ret.add(result["content"]["title"])
        if module_bread:
            for bread in module_bread:
                ret.add(bread)
        ret.add(params.get("path_route").get("name"))
        ret.add(u"跟谁学{}".format(params.get("path_route").get("name")))
        return ",".join(ret)

    def _parse_tdk(self, params, result, module_bread):
        tdk = {
            "title": self._default_title(result, params, module_bread),
            "keywords": self._default_keywords(result, params, module_bread),
            "description": self._parse_description(result),
        }
        if not tdk["description"]:
            tdk["description"] = tdk["title"]
        return tdk

    def common_path_key(self, request):
        path_info = request.path_info
        path_info = re.sub(r'^/[^/]+?/', '', path_info)
        if not path_info.strip():
            return '0'
        return path_info.strip().replace("/", "-").strip("-")

    def _parse_user_agent(self, params):
        try:
            ua = params.get("request").META["HTTP_USER_AGENT"]
        except Exception as info:
            ua = "CAN NOT GET UA"
        return ua

    def _parse_detail_params(self, params):
        return {
            "db_id": params.get("db_id", params.get("baike_id")),
            "user_agent": self._parse_user_agent(params),
        }

    def _parse_retrieve_conf(self, conf_obj, section_key, params):
        retrieve_conf = conf_obj.get(section_key, "retrieve")
        if not retrieve_conf:
            return False

        ret = {}
        for item in retrieve_conf.split(","):
            item = item.strip()
            if not item:
                continue
            items = item.split(":", 1)
            if len(items) != 2:
                continue
            key, value = items
            if not value.strip():
                continue
            if value.strip().find("{domain_name}") != -1:
                value = value.strip().replace("{domain_name}", params.get("path_route").get("name"))
            ret[key.strip()] = value.strip().decode("utf-8")

        size = ret.get("size", 10)
        offset = ret.get("offset", 0)
        request = params.get("request")
        if request.method == "GET":
            request_dict = request.GET
        elif request.method == "POST":
            request_dict = request.POST

        if offset.startswith("random"):
            try:
                base = int(offset.split("-")[-1])
            except:
                base = 100
            offset = random.randint(1, base)

        # 相关推荐详情页 相关参数覆盖
        if "recommend-offset" in params:
            offset = params.get("recommend-offset")
        if "recommend-query" in params:
            ret["query"] = params.get("recommend-query")

        p = request_dict.get("p")
        pageno = request_dict.get("pageno")
        if p:
            ret["pageno"] = int(p)
            offset = (int(p) - 1) * int(size) + int(offset)
            ret["offset"] = offset
        elif pageno:
            ret["pageno"] = int(pageno)
            offset = (int(pageno) - 1) * int(size) + int(offset)
            ret["offset"] = offset
        else:
            ret["pageno"] = 1
            ret["offset"] = offset

        static_tags = ret.get("tag")
        if static_tags:
            static_tags = [item.strip().decode("utf-8") for item in static_tags.split("|")]
            ret["tag"] = static_tags

        tags = conf_obj.get(section_key, "tags")
        if not static_tags and tags:
            tags_ret = self._parse_tags(tags, params)
            ret["tag"] = tags_ret.get("tag", [])
            if tags_ret.get("subject"):
                ret["subject"] = tags_ret["subject"].strip().decode('utf-8')
            if tags_ret.get("query"):
                ret["query"] = tags_ret["query"].strip().decode('utf-8')
            if tags_ret.get("module_bread"):
                ret["module_bread"] = tags_ret["module_bread"]
            if tags_ret.get("page_id"):
                ret["page_id"] = tags_ret["page_id"]
            if tags_ret.get("page_sub_id"):
                ret["page_sub_id"] = tags_ret["page_sub_id"]

        module_search = {}

        q = request_dict.get("q")
        if q:
            q = urllib.unquote(q)
            ret["query"] = q
            module_search["query"] = q

        self._place_holder(ret, params)
        module_search["datasrc"] = params.get("path_route").get("domain")
        ret["module_search"] = module_search

        # /s/tags/ 形如这样的页面
        query = params.get("sq")
        if query:
            ret["query"] = urllib.unquote(query)
            ret["module_search"] = False

        ret["retrieve"] = {
            "size": ret.get("size", 10),
            "offset": ret.get("offset", 0),
            "subject": ret.get("subject"),
            "tag": ret.get("tag"),
            "query": ret.get("query"),
            "user_agent": self._parse_user_agent(params),
        }
        return ret

class ModuleCsrf(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/common/module-csrf.html"
        self.module_key = "csrf"

class ModuleTdk(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/common/module-tdk.html"
        self.module_key = "tdk"

    def _get_tdk_resource(self, conf_obj, key, path_key):
        while True:
            ret = conf_obj.get(key, path_key)
            if ret:
                return ret.decode("utf-8")
            if path_key == '0':
                return u''
            path_key = path_key.split("-")
            if len(path_key) <= 2:
                path_key = '0'
                continue
            path_key = "-".join(path_key[:-1])

    def _place_holder_tdk(self, tdk, params):
        path_route = params.get("path_route")
        domain_name = path_route.get("name")
        tdk = tdk.replace("{domain_name}", domain_name)
        return tdk

    def _parse_tdk(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {}
        path_key = params.get("path_key")
        if not path_key:
            path_key = self.common_path_key(params.get("request"))
        path_key = path_key.replace("@@", "-")
        ret = {}
        for key in ("title", "keywords", "description"):
            ret[key] = self._place_holder_tdk(self._get_tdk_resource(module_conf, key, path_key.decode("utf-8")), params)
        ret["title"] = ret["title"].replace("{keywords}", ret["keywords"])
        ret["description"] = ret["description"].replace("{keywords}", ret["keywords"])
        return ret

    @deco
    def load(self, params):
        data = {"tdk": self._parse_tdk(params)}
        data["tdk"] = merge_dict(params.get("tdk", {}), data["tdk"])
        return {"template": params.get("template"), "data": data}

class ModuleReport(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/common/module-report.html"
        self.module_key = "report"

    @deco
    def load(self, params):
        common = {"REPORT": {"page_type": params.get("report_page_type", 'zhanqun_{}'.format(params.get("path_route").get("domain")))},}
        return {"template": params.get("template"), "common": common}

class ModuleVersion(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/common/module-version.html"
        self.module_key = "version"

    @deco
    def load(self, params = {}):
        common = {
            "version": get_version(),
            "GLOBAL": {
                "domain": params.get("path_route").get("domain"),
                "site_name": params.get("path_route").get("name"),
                "is_not_gsx_app": params.get("is_not_gsx_app"),
                "is_kaoyan_app": params.get("is_kaoyan_app"),
            }
        }
        return {"template": params.get("template"), "common": common}

class ModuleMeta(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-meta.html"
        self.module_key = "meta"

class ModuleMetaMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-meta.html"
        self.module_key = "m.meta"

class ModuleCss(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-css.html"
        self.module_key = "css"

    def _parse_css_src(self, conf_obj):
        css_src = conf_obj.get("css", "src")
        if not css_src:
            return []
        css_src = [item.strip() for item in css_src.strip().split(",") if item.strip()]
        ret = []
        for item in css_src:
            ret.append({"path": conf_obj.get(item, "src"),
                        "type": conf_obj.get(item, "type"),
                        "rel": conf_obj.get(item, "rel"),})
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_css": self._parse_css_src(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleCssMsite(ModuleCss):
    def __init__(self, Luna, LunaSQL):
        ModuleCss.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-css.html"
        self.module_key = "m.css"

class ModuleJs(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-js.html"
        self.module_key = "js"

    def _parse_js_src(self, conf_obj):
        js_src = conf_obj.get("js", "src")
        if not js_src:
            return []
        js_src = [item.strip() for item in js_src.strip().split(",") if item.strip()]
        ret = []
        for item in js_src:
            ret.append({"src": conf_obj.get(item, "src")})
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_js": self._parse_js_src(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleJsMsite(ModuleJs):
    def __init__(self, Luna, LunaSQL):
        ModuleJs.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-js.html"
        self.module_key = "m.js"

class ModuleFooterJs(ModuleJs):
    def __init__(self, Luna, LunaSQL):
        ModuleJs.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-footer-js.html"
        self.module_key = "footer-js"

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_footer_js": self._parse_js_src(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleFooterJsMsite(ModuleFooterJs):
    def __init__(self, Luna, LunaSQL):
        ModuleFooterJs.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-footer-js.html"
        self.module_key = "m.footer-js"

class ModuleFooter(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-footer.html"
        self.module_key = "footer"

class ModuleFooterMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-footer.html"
        self.module_key = "m.footer"

class ModuleDemandHelp(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-demand-help.html"
        self.module_key = "demand-help"

    def _parse_demand_help(self, conf_obj, panel_key = "demand-help"):
        ret = {
            "demand": conf_obj.get(panel_key, "demand"),
            "qr": conf_obj.get(panel_key, "qr"),
            "qr_img": conf_obj.get(panel_key, "qr_img"),
            "qr_title": conf_obj.get(panel_key, "qr_title"),
        }
        return ret

    @deco
    def load(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_demand_help": self._parse_demand_help(module_conf)}
        return {"template": params.get("template"), "data": data}

class ModuleDemandHelpMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-demand-help.html"
        self.module_key = "m.demand-help"

class ModuleNav(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/pc/base/module-nav.html"
        self.module_key = "nav"

    def _parse_sub_nav(self, conf_obj, item):
        sub_key = conf_obj.get(item, "sub")
        if not sub_key:
            return []
        sub_nav = conf_obj.get(sub_key, "tab")
        ret = []
        for sub in sub_nav.split(","):
            _key = "_".join([sub_key, sub])
            name = conf_obj.get(_key, "name")
            url = conf_obj.get(_key, "url")
            if not name or not url:
                continue
            ret.append({"name": name, "url": url})
        return ret

    def _parse_nav_conf(self, conf_obj):
        nav_tab = conf_obj.get("base", "tab")
        if not nav_tab:
            return []
        nav_tab = [item.strip() for item in nav_tab.strip().split(",") if item.strip()]
        ret = []
        for item in nav_tab:
            ret.append({"url": conf_obj.get(item, "url"),
                        "name": conf_obj.get(item, "name"),
                        "id": conf_obj.get(item, "id").decode("utf-8"),
                        "target": conf_obj.get(item, "target"),
                        "subs": self._parse_sub_nav(conf_obj, item)
                        }
                      )
        return ret

    @deco
    def load(self, params = {}):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {"template": params.get("template")}
        data = {"module_nav": self._parse_nav_conf(module_conf)}
        return {"template": params.get("template"),
                "data": data,
                }

class ModuleNavMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/base/module-nav.html"
        self.module_key = "m.nav"

    @deco
    def load(self, params):
        return {"template": params.get("template")}

class ModulePlaceHolder(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = ""
        self.module_key = "place.holder"
        self.pl = {
            "html_left": u'''<!DOCTYPE html>\n<html lang="zh-CN">\n''',
            "html_right": u'''\n</html>''',
            "head_left": u'''<head>\n''',
            "head_right": u'''\n</head>\n''',
            "body_left": u'''<body>\n''',
            "body_right": u'''\n</body>\n''',
            "div_right": u'''\n</div>\n''',
            "base_content_left": u'''<div class="module-base-content clearfix">\n''',
            "main_content_left": u'''<div class="module-main-content clearfix">\n''',
            "detail_left": u'''<div class="module-content-left float-left">\n''',
            "content_item": u'''<div class="content-item clearfix">\n''',
            "admin_content_item": u'''<div class="admin-content-item clearfix">\n''',
            "content_item_50": u'''<div class="content-item-50 float-left clearfix">\n''',
            "content_item_pl_10": u'''<div class="content-item-pl-10 float-left clearfix">\n''',
            "content_item_pr_10": u'''<div class="content-item-pr-10 float-left clearfix">\n''',
            "jita_left": u'''<div class="module-content-jita-left box-sizing-border-box clearfix">\n''',
            "detail_right": u'''<div class="module-content-right float-left">\n''',
            "margin_10": u'''<div class="content-item height-10px"></div>''',
            "margin_20": u'''<div class="content-item height-20px"></div>''',
            "line": u'''<div class="content-item line-right-panel"></div>''',
            "m.margin_20": u'''<div class="height-20"></div>''',
            "m.margin_30": u'''<div class="height-30"></div>''',
            "m.margin_50": u'''<div class="height-50"></div>''',
            "m.area_gray": u'''<div class="area-gray"></div>''',
            "yasi_calendar_left": u'''<div class="content-item yasi-calendar-panel box-sizing-border-box clearfix">''',
            "baidu_statistics_baizhan": u'''
                <script>
                    var _hmt = _hmt || [];
                    (function() {
                      var hm = document.createElement("script");
                      hm.src = "//hm.baidu.com/hm.js?7ef71ae224da6f76ca4361964e2abc19";
                      var s = document.getElementsByTagName("script")[0];
                      s.parentNode.insertBefore(hm, s);
                    })();
                </script>\n''',
            "baidu_statistics_jita": u'''
                <script>
                    var _hmt = _hmt || [];
                    (function() {
                      var hm = document.createElement("script");
                      hm.src = "//hm.baidu.com/hm.js?835419eb2ea0591dc51529a8dc1140b3";
                      var s = document.getElementsByTagName("script")[0];
                      s.parentNode.insertBefore(hm, s);
                    })();
                </script>\n''',
            "baidu_statistics_yasi": u'''
                <script>
                    var _hmt = _hmt || [];
                    (function() {
                      var hm = document.createElement("script");
                      hm.src = "//hm.baidu.com/hm.js?921406c9e940ee63d540ae8488091531";
                      var s = document.getElementsByTagName("script")[0];
                      s.parentNode.insertBefore(hm, s);
                    })();
                </script>\n''',
            "baidu_statistics_youshengxiao": u'''
                <script>
                    var _hmt = _hmt || [];
                    (function() {
                      var hm = document.createElement("script");
                      hm.src = "//hm.baidu.com/hm.js?8b653ff0764219886d0374c2ead65138";
                      var s = document.getElementsByTagName("script")[0];
                      s.parentNode.insertBefore(hm, s);
                    })();
                </script>\n''',
            "google_statistics": u'''
                <script>
                  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
                  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
                  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
                  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
                  ga('create', 'UA-76110018-1', 'auto');
                  ga('send', 'pageview');
                </script>\n''',
        }

    def load(self, params):
        pl_key = params.get("pl_key")
        if not pl_key:
            template = u""
        template = self.pl.get(pl_key, u"")
        return {"ispl": True, "template": template}
