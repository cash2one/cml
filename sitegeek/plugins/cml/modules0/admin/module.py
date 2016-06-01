#!/usr/bin/env python
#-*- coding:utf-8 -*-
from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco
import re
import json
import base64
import urllib

class ModulLogin(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-login.html"
        self.module_key = "admin-login"

#
# class ModulLoginAjax(ModuleBase):
#     def __init__(self, Luna, LunaSQL):
#         ModuleBase.__init__(self, Luna, LunaSQL)
#         self.template = "admin-login-ajax"
#         self.module_key = "admin-login-ajax"
#
#     @deco
#     def load(self, params):
#         print params

class ModulAdminNav(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-nav.html"
        self.module_key = "admin-nav"

class ModulAdminReadme(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-readme.html"
        self.module_key = "admin-readme"

class ModulAdminAddUser(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-add-user.html"
        self.module_key = "admin-add-user"

class ModulAdminPassword(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-password.html"
        self.module_key = "admin-password"

class ModulAdminEdit(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-edit.html"
        self.module_key = "admin-edit"

    def _parse_module_list(self, module_list, params, version_detail):
        ret = []
        for module in module_list:
            module = module.strip().split("#", 1)
            conf_key = ''
            if len(module) > 1:
                conf_key = module[1]
            conf_content = version_detail.get("conf_%s" % conf_key)
            if not conf_content:
                conf_content = ""
            else:
                conf_content = base64.b64encode(urllib.quote(version_detail.get("conf_%s" % conf_key)))
            ret.append({
                "key": module[0],
                "conf": conf_key,
                "name": params.get("dbm_factory").module_db.get(module[0]),
                "conf_content": conf_content
            })
        return ret

    def _parse_module_edit(self, params):
        ret = {}
        edit_data = params.get("__edit")
        if not edit_data:
            return ret
        ret["edit_data"] = edit_data["version_info"]
        ret["module_list"] = self._parse_module_list(json.JSONDecoder().decode(edit_data["version_info"]["content"]).split(','), params, edit_data["version_detail"])
        return ret

    @deco
    def load(self, params):
        module_edit = self._parse_module_edit(params)
        return {"template": params.get("template"), "data": {"module_edit": module_edit}}

class ModulAdminAddConf(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-add-conf.html"
        self.module_key = "admin-add-conf"

    @deco
    def load(self, params):
        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {"template": params.get("template")}
        module_add_conf = dbm_factory.conf_online.load_where({
            "status": "= 1",
            "owner": "= %s" % params.get("__login_user__").get("content").get("id"),
        })
        if module_add_conf:
            module_add_conf = module_add_conf[0]
        else:
            module_add_conf = {}

        module_site_conf = dbm_factory.conf_online.load_where({
            "status": "= 0",
        })
        return {"template": params.get("template"), "data": {"module_add_conf": module_add_conf, "module_site_conf": module_site_conf}}

class ModulAdminLeftNav(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-left-nav.html"
        self.module_key = "admin-left-nav"

    def _parse_module_left_nav(self, params):
        request = params.get("request")
        page_type = re.findall(r"/admin/([^/]+)/", request.path_info)
        if len(page_type):
            return {
                "page_type": page_type[0],
            }
        return {"page_type": "home",}

    @deco
    def load(self, params):
        return {"template": params.get("template"), "data": {
                "module_left_nav": self._parse_module_left_nav(params),
            },
            "common": {
                "GLOBAL": {
                    "login_user": params.get("__login_user__")
                }
            }
        }

class ModulAdminVersion(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-version.html"
        self.module_key = "admin-version"

    def _parse_version(self, params):
        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return False

        user = params.get("__login_user__")
        if not user:
            return False
        ret = {}
        ret["version"] = params.get("request").GET.get("version")
        ret["terminal"] = params.get("request").GET.get("terminal")
        if not ret["version"]:
            # records = dbm_factory.version.load_by_owner(user.get("content").get("id"))
            records = dbm_factory.version.load_by_owner()
            ret["version_list"] = dbm_factory.version_utils.list_to_dict(records, dbm_factory)
            ret["version_type"] = dbm_factory.version_utils.BASE_VERSION
            return ret
        if not ret["terminal"]:
            records = dbm_factory.version.load_version(version = ret["version"])
            ret["version_list"] = dbm_factory.version_utils.list_to_dict(records, dbm_factory)
            ret["version_type"] = dbm_factory.version_utils.BASE_VERSION
            return ret
        records = dbm_factory.version.load_version(version = ret["version"], terminal = ret["terminal"])
        ret["version_list"] = dbm_factory.version_utils.list_to_dict(records, dbm_factory)
        ret["version_type"] = dbm_factory.version_utils.TERMINAL_VERSION
        return ret

    @deco
    def load(self, params):
        module_version = self._parse_version(params)
        return {"template": params.get("template"), "data": {"module_version": module_version}}

class ModulAdminOnline(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-online.html"
        self.module_key = "admin-online"

    def _parse_version(self, params):
        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return False

        user = params.get("__login_user__")
        if not user:
            return False
        online = dbm_factory.conf_online.load(params)
        final = []
        for item in online:
            item["user_info"] = dbm_factory.cml_user.get(item.get("owner"))
            # if item.get("owner") == user.get("content").get("id"):
            final.append(item)
        return final

    @deco
    def load(self, params):
        module_online = self._parse_version(params)
        return {"template": params.get("template"), "data": {"module_online": module_online}}

class ModulAdminApplyOnline(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-apply-online.html"
        self.module_key = "admin-apply-online"

    def _parse_apply_failed(self, params):
        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {}
        user = params.get("__login_user__")
        if not user:
            return {}

        failed = dbm_factory.conf_online.load_where({
            "status": "= 4",
            "owner": "= %s" % user.get("content").get("id")
        })
        if not failed:
            return {}
        return failed

    @deco
    def load(self, params):
        module_apply_failed = self._parse_apply_failed(params)
        return {"template": params.get("template"), "data": {"module_apply_failed": module_apply_failed}}

class ModulAdminAuthOnline(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-auth-online.html"
        self.module_key = "admin-auth-online"

    def _parse_apply_version(self, params):
        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {}
        user = params.get("__login_user__")
        if not user:
            return {}

        applied = dbm_factory.conf_online.load_where({
            "status": "IN (3,101)",
        })
        if not applied:
            return {}
        return applied

    @deco
    def load(self, params):
        module_apply_version = self._parse_apply_version(params)
        return {"template": params.get("template"), "data": {"module_apply_version": module_apply_version}}

class ModuleAdminKeywordsAdd(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-keywords-add.html"
        self.module_key = "admin-keywords-add"

class ModuleAdminSubjectAdd(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-subject-add.html"
        self.module_key = "admin-subject-add"

class ModuleAdminKeywordsEdit(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-keywords-edit.html"
        self.module_key = "admin-keywords-edit"

    def _parse_keywords_item(self, params):
        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {}
        return dbm_factory.domain_keywords.load(params)

    @deco
    def load(self, params):
        module_keywords_item = self._parse_keywords_item(params)
        return {"template": params.get("template"), "data": {"module_keywords_item": module_keywords_item}}

class ModuleAdminSubjectEdit(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-subject-edit.html"
        self.module_key = "admin-subject-edit"

    def _parse_keywords_item(self, params):
        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return {}
        return dbm_factory.api_topic_www.load(params)

    @deco
    def load(self, params):
        module_keywords_item = self._parse_keywords_item(params)
        return {"template": params.get("template"), "data": {"module_keywords_item": module_keywords_item}}


class ModuleAdminCmsEdit(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/admin/base/module-cms-edit.html"
        self.module_key = "admin-cms-edit"
        self.name_mapping = {
            "status": u"状态",
            "title": u"文章标题",
            "bread": u"文章bread",
            "subject": u"subject",
            "content": u"文章内容",
            "date": u"时间",
            "source": u"来源",
            "class": u"schema_id",
            "image_list": u"图片",
            "url": u"文章url",
            "del_reason": u"删除原因",
            "tag": u"tags",
            "data_weight": u"文章权重",
            "cover": u"封面",
            "brief": u"文章简介",
        }

    def _parse_type(self, value):
        if value["name"] in ("content", "geci_content"):
            return "rich_text"
        if value["name"] in ("brief", "question_detail", "video"):
            return "text_area"
        if type(value["value"]) == type([]):
            return "list"
        elif type(value["value"]) == type(u''):
            return "string"
        elif type(value["value"]) == type(''):
            return "string"
        elif type(value["value"]) == type({}):
            return "string"
        elif type(value["value"]) == type(1):
            return "string"
        else:
            return None

    @deco
    def load(self, params):
        result = self.luna.detail({"db_id": params.get("cms_edit_id"), "user_agent": self._parse_user_agent(params)})
        ret = {}
        ret_first = []
        ret_second = []
        if "content" in result:
            ret_first.append({
                "display_name": self.name_mapping.get("status", "status"),
                "name": "status",
                "value": result.get("status", "0"),
                "type": "string",
            })
            ret_first.append({
                "display_name": self.name_mapping.get("class", "class"),
                "name": "class",
                "value": result.get("class", ""),
                "type": "string",
            })
            ret_first.append({
                "display_name": self.name_mapping.get("taskid", "taskid"),
                "name": "taskid",
                "value": result.get("taskid", ""),
                "type": "string",
            })
            base_dict = result["content"]
            for key in base_dict:
                if key in ("content", "status", "class", "taskid"):
                    continue
                tmp = {
                    "display_name": self.name_mapping.get(key, key),
                    "name": key,
                    "value": base_dict[key],
                }
                tmp["type"] = self._parse_type(tmp)
                if not tmp["type"]:
                    tmp["type"] = "string"
                if tmp["type"] == "rich_text":
                    tmp["height"] = 300
                elif tmp["type"] == "text_area":
                    tmp["height"] = 300
                ret_second.append(tmp)
            if "content" in base_dict:
                tmp = {
                    "display_name": self.name_mapping.get("content", "content"),
                    "name": "content",
                    "value": base_dict["content"],
                }
                tmp["type"] = self._parse_type(tmp)
                tmp["height"] = 800
                ret_second.append(tmp)
        ret = {
            "first": ret_first,
            "second": ret_second,
        }

        return {"template": params.get("template"),
                "data": {
                    "result": ret,
                    "db_id": params.get("cms_edit_id"),
                }}
