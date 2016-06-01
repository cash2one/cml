#!/usr/bin/env python
#-*- coding:utf-8 -*-
from common.cml.modules.common.module_const import ModuleKey
from common.cml.modules.common.module_const import ConfKey
from common.cml.modules.common.module_const import ParamKey
from common.cml.modules.common.module_const import CommonKey
from common.libs.dict_utils import merge_dict

def deco(func):
    def _deco(clazz, params = {}):
        request = params.get(ParamKey.PK_REQUEST)
        if not request:
            return {}
        template = params.get(ParamKey.PK_TEMPLATE)
        _params = params
        if not template:
            _params = merge_dict(params, {ParamKey.PK_TEMPLATE: clazz.template})
        else:
            _params = params
        return func(clazz, params = _params)
    return _deco

class ModuleBase(object):
    '''
        所有module必须继承此module
        每个module必须定义全局唯一module_key
    '''
    def __init__(self, params = {}):
        self.getter = params
        self.repeat = False
        self.module_key = ModuleKey.MK_BASE
        self.template = False

    def _parse_module_conf(self, params):
        module_conf = params.get(ParamKey.PK_MODULE_CONF)
        if not module_conf:
            return False

        module_conf = ConfKey.CK_CONF_PLACE_HOLDER.format(module_conf)
        conf_dict = params.get(ConfKey.CK_CONF_DICT, {})
        if not conf_dict:
            return False
        # 取出对应BaseDict
        return conf_dict.get(module_conf)

    def _parse_user_agent(self, params):
        try:
            ua = params.get(ParamKey.PK_REQUEST).META["HTTP_USER_AGENT"]
        except Exception as info:
            ua = "DEFAULT UserAgent"
        return ua

    def _parse_path_key(self, params):
        path_info = request.path_info
        if not path_info.strip():
            return ''
        return ParamKey.PK_PATH_KEY_SPLIT.join(request.path_info.strip("/").split("/"))

    def _parse_render_data(self, template = False, data = {}, common = {}, priority = {}):
        return {
            CommonKey.RENDER_TPL_KEY: template,
            CommonKey.RENDER_DATA_KEY: data,
            CommonKey.RENDER_COMMON_KEY: common,
            CommonKey.RENDER_PRIORITY_KEY: priority
        }

    @deco
    def load(self, params = {}):
        return self._parse_render_data(
            template = params.get(ParamKey.PK_TEMPLATE)
        )

class ModuleCsrf(ModuleBase):
    def __init__(self, params = {}):
        ModuleBase.__init__(self, params)
        self.template = ModuleKey.MK_CSRF_TPL
        self.module_key = ModuleKey.MK_CSRF

class ModuleTdk(ModuleBase):
    def __init__(self, params = {}):
        ModuleBase.__init__(self, params)
        self.template = ModuleKey.MK_TDK_TPL
        self.module_key = ModuleKey.MK_TDK

    def _get_tdk_resource(self, conf_obj, key, path_key):
        while True:
            if not path_key:
                path_key = "0"
            ret = conf_obj.get(key, path_key)
            if ret:
                if type(ret) != type(u''):
                    return ret.decode(CommonKey.ENCODING)
                return ret

            if path_key == "0":
                return u""

            path_key = path_key.split(ParamKey.PK_PATH_KEY_SPLIT)
            path_key = ParamKey.PK_PATH_KEY_SPLIT.join(path_key[:-1])

    def _parse_tdk(self, params):
        module_conf = self.get_module_conf(params)
        if not module_conf:
            return {}
        path_key = params.get(ParamKey.PK_PATH_KEY)
        if not path_key:
            path_key = self._parse_path_key(params.get(ParamKey.PK_REQUEST))
        ret = {}
        for key in ("title", "keywords", "description"):
            ret[key] = self._get_tdk_resource(module_conf, key, path_key.decode(CommonKey.ENCODING))

        ret["title"] = ret["title"].replace("{keywords}", ret["keywords"])
        ret["description"] = ret["description"].replace("{keywords}", ret["keywords"])
        ret["description"] = ret["description"].replace("{title}", ret["title"])
        return ret

    @deco
    def load(self, params):
        data = {ParamKey.PK_TDK: self._parse_tdk(params)}
        data[ParamKey.PK_TDK] = merge_dict(params.get(ParamKey.PK_TDK, {}), data[ParamKey.PK_TDK])
        return self._parse_render_data(
            template = params.get(ParamKey.PK_TEMPLATE),
            data = data,
        )

# class ModuleReport(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/common/module-report.html"
#         self.module_key = "report"
#
#     @deco
#     def load(self, params):
#         common = {"REPORT": {"page_type": params.get("report_page_type", 'zhanqun_{}'.format(params.get("path_route").get("domain")))},}
#         return {"template": params.get("template"), "common": common}
#
# class ModuleVersion(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/common/module-version.html"
#         self.module_key = "version"
#
#     @deco
#     def load(self, params = {}):
#         common = {"version": get_version()}
#         return {"template": params.get("template"), "common": common}
#
# class ModuleMeta(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/pc/base/module-meta.html"
#         self.module_key = "meta"
#
# class ModuleMetaMsite(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/msite/base/module-meta.html"
#         self.module_key = "m.meta"
#
# class ModuleCss(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/pc/base/module-css.html"
#         self.module_key = "css"
#
#     def _parse_css_src(self, conf_obj):
#         css_src = conf_obj.get("css", "src")
#         if not css_src:
#             return []
#         css_src = [item.strip() for item in css_src.strip().split(",") if item.strip()]
#         ret = []
#         for item in css_src:
#             ret.append({"path": conf_obj.get(item, "src"),
#                         "type": conf_obj.get(item, "type"),
#                         "rel": conf_obj.get(item, "rel"),})
#         return ret
#
#     @deco
#     def load(self, params = {}):
#         module_conf = self.get_module_conf(params)
#         if not module_conf:
#             return {"template": params.get("template")}
#         data = {"module_css": self._parse_css_src(module_conf)}
#         return {"template": params.get("template"), "data": data}
#
# class ModuleCssMsite(ModuleCss):
#     def __init__(self, Luna, LunaSQL):
#         ModuleCss.__init__(self, Luna, LunaSQL)
#         self.template = "module/msite/base/module-css.html"
#         self.module_key = "m.css"
#
# class ModuleJs(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/pc/base/module-js.html"
#         self.module_key = "js"
#
#     def _parse_js_src(self, conf_obj):
#         js_src = conf_obj.get("js", "src")
#         if not js_src:
#             return []
#         js_src = [item.strip() for item in js_src.strip().split(",") if item.strip()]
#         ret = []
#         for item in js_src:
#             ret.append({"src": conf_obj.get(item, "src")})
#         return ret
#
#     @deco
#     def load(self, params = {}):
#         module_conf = self.get_module_conf(params)
#         if not module_conf:
#             return {"template": params.get("template")}
#         data = {"module_js": self._parse_js_src(module_conf)}
#         return {"template": params.get("template"), "data": data}
#
# class ModuleJsMsite(ModuleJs):
#     def __init__(self, Luna, LunaSQL):
#         ModuleJs.__init__(self, Luna, LunaSQL)
#         self.template = "module/msite/base/module-js.html"
#         self.module_key = "m.js"
#
# class ModuleFooterJs(ModuleJs):
#     def __init__(self, Luna, LunaSQL):
#         ModuleJs.__init__(self, Luna, LunaSQL)
#         self.template = "module/pc/base/module-footer-js.html"
#         self.module_key = "footer-js"
#
#     @deco
#     def load(self, params = {}):
#         module_conf = self.get_module_conf(params)
#         if not module_conf:
#             return {"template": params.get("template")}
#         data = {"module_footer_js": self._parse_js_src(module_conf)}
#         return {"template": params.get("template"), "data": data}
#
# class ModuleFooterJsMsite(ModuleFooterJs):
#     def __init__(self, Luna, LunaSQL):
#         ModuleFooterJs.__init__(self, Luna, LunaSQL)
#         self.template = "module/msite/base/module-footer-js.html"
#         self.module_key = "m.footer-js"
#
# class ModuleFooter(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/pc/base/module-footer.html"
#         self.module_key = "footer"
#
# class ModuleFooterMsite(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/msite/base/module-footer.html"
#         self.module_key = "m.footer"
#
# class ModuleDemandHelp(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/pc/base/module-demand-help.html"
#         self.module_key = "demand-help"
#
# class ModuleDemandHelpMsite(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/msite/base/module-demand-help.html"
#         self.module_key = "m.demand-help"
#
# class ModuleNav(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/pc/base/module-nav.html"
#         self.module_key = "nav"
#
#     def _parse_sub_nav(self, conf_obj, item):
#         sub_key = conf_obj.get(item, "sub")
#         if not sub_key:
#             return []
#         sub_nav = conf_obj.get(sub_key, "tab")
#         ret = []
#         for sub in sub_nav.split(","):
#             _key = "_".join([sub_key, sub])
#             name = conf_obj.get(_key, "name")
#             url = conf_obj.get(_key, "url")
#             if not name or not url:
#                 continue
#             ret.append({"name": name, "url": url})
#         return ret
#
#     def _parse_nav_conf(self, conf_obj):
#         nav_tab = conf_obj.get("base", "tab")
#         if not nav_tab:
#             return []
#         nav_tab = [item.strip() for item in nav_tab.strip().split(",") if item.strip()]
#         ret = []
#         for item in nav_tab:
#             ret.append({"url": conf_obj.get(item, "url"),
#                         "name": conf_obj.get(item, "name"),
#                         "id": conf_obj.get(item, "id").decode("utf-8"),
#                         "target": conf_obj.get(item, "target"),
#                         "subs": self._parse_sub_nav(conf_obj, item)
#                         }
#                       )
#         return ret
#
#     @deco
#     def load(self, params = {}):
#         module_conf = self.get_module_conf(params)
#         if not module_conf:
#             return {"template": params.get("template"), "common": {"GLOBAL": {"site_name": params.get("path_route").get("name")}}}
#         data = {"module_nav": self._parse_nav_conf(module_conf)}
#         return {"template": params.get("template"),
#                 "data": data,
#                 "common": {
#                     "GLOBAL": {
#                         "site_name": params.get("path_route").get("name"),
#                         "is_not_gsx_app": params.get("is_not_gsx_app")
#                     }
#                 }
#                 }
#
# class ModuleNavMsite(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "module/msite/base/module-nav.html"
#         self.module_key = "m.nav"
#
#     @deco
#     def load(self, params):
#         return {"template": params.get("template"),
#                 "common": {
#                     "GLOBAL": {
#                         "site_name": params.get("path_route").get("name"),
#                         "is_not_gsx_app": params.get("is_not_gsx_app"),
#                         "is_kaoyan_app": params.get("is_kaoyan_app"),
#                     }
#                 }
#                 }
#
# class ModulePlaceHolder(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = ""
#         self.module_key = "place.holder"
#         self.pl = {
#             "html_left": u'''<!DOCTYPE html>\n<html lang="zh-CN">\n''',
#             "html_right": u'''\n</html>''',
#             "head_left": u'''<head>\n''',
#             "head_right": u'''\n</head>\n''',
#             "body_left": u'''<body>\n''',
#             "body_right": u'''\n</body>\n''',
#             "div_right": u'''\n</div>\n''',
#             "base_content_left": u'''<div class="module-base-content clearfix">\n''',
#             "main_content_left": u'''<div class="module-main-content clearfix">\n''',
#             "detail_left": u'''<div class="module-content-left float-left">\n''',
#             "content_item": u'''<div class="content-item clearfix">\n''',
#             "admin_content_item": u'''<div class="admin-content-item clearfix">\n''',
#             "content_item_50": u'''<div class="content-item-50 float-left clearfix">\n''',
#             "content_item_pl_10": u'''<div class="content-item-pl-10 float-left clearfix">\n''',
#             "content_item_pr_10": u'''<div class="content-item-pr-10 float-left clearfix">\n''',
#             "jita_left": u'''<div class="module-content-jita-left box-sizing-border-box clearfix">\n''',
#             "detail_right": u'''<div class="module-content-right float-left">\n''',
#             "margin_10": u'''<div class="content-item height-10px"></div>''',
#             "margin_20": u'''<div class="content-item height-20px"></div>''',
#             "line": u'''<div class="content-item line-right-panel"></div>''',
#             "m.margin_20": u'''<div class="height-20"></div>''',
#             "m.margin_30": u'''<div class="height-30"></div>''',
#             "m.margin_50": u'''<div class="height-50"></div>''',
#             "m.area_gray": u'''<div class="area-gray"></div>''',
#             "yasi_calendar_left": u'''<div class="content-item yasi-calendar-panel box-sizing-border-box clearfix">''',
#             "baidu_statistics_baizhan": u'''
#                 <script>
#                     var _hmt = _hmt || [];
#                     (function() {
#                       var hm = document.createElement("script");
#                       hm.src = "//hm.baidu.com/hm.js?7ef71ae224da6f76ca4361964e2abc19";
#                       var s = document.getElementsByTagName("script")[0];
#                       s.parentNode.insertBefore(hm, s);
#                     })();
#                 </script>\n''',
#             "baidu_statistics_jita": u'''
#                 <script>
#                     var _hmt = _hmt || [];
#                     (function() {
#                       var hm = document.createElement("script");
#                       hm.src = "//hm.baidu.com/hm.js?835419eb2ea0591dc51529a8dc1140b3";
#                       var s = document.getElementsByTagName("script")[0];
#                       s.parentNode.insertBefore(hm, s);
#                     })();
#                 </script>\n''',
#             "baidu_statistics_yasi": u'''
#                 <script>
#                     var _hmt = _hmt || [];
#                     (function() {
#                       var hm = document.createElement("script");
#                       hm.src = "//hm.baidu.com/hm.js?921406c9e940ee63d540ae8488091531";
#                       var s = document.getElementsByTagName("script")[0];
#                       s.parentNode.insertBefore(hm, s);
#                     })();
#                 </script>\n''',
#             "baidu_statistics_youshengxiao": u'''
#                 <script>
#                     var _hmt = _hmt || [];
#                     (function() {
#                       var hm = document.createElement("script");
#                       hm.src = "//hm.baidu.com/hm.js?8b653ff0764219886d0374c2ead65138";
#                       var s = document.getElementsByTagName("script")[0];
#                       s.parentNode.insertBefore(hm, s);
#                     })();
#                 </script>\n''',
#             "google_statistics": u'''
#                 <script>
#                   (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
#                   (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
#                   m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
#                   })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
#                   ga('create', 'UA-76110018-1', 'auto');
#                   ga('send', 'pageview');
#                 </script>\n''',
#         }
#
#     def load(self, params):
#         pl_key = params.get("pl_key")
#         if not pl_key:
#             template = u""
#         template = self.pl.get(pl_key, u"")
#         return {"ispl": True, "template": template}
