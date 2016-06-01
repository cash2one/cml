#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import urllib
import json
from zhanqun.resource import zhanqun_resource_dict
import time
import hashlib

class GeneratorPreviewConf(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = ""
        self.module_key = "generator_preview_conf"

    def load(self, params):
        '''
            /i-admin/preview/?v=3b3a3e31a2c6a502145a96aada154645&pk=home&d=jita&t=pc
        '''
        request = params.get("request")
        if not request:
            return False

        version = request.GET.get("v")
        if not version:
            return False

        page_key = request.GET.get("pk")
        if not page_key:
            return False
        page_key = urllib.unquote(page_key)

        terminal = request.GET.get("t")
        if not terminal:
            return False

        domain = request.GET.get("d")
        path_route = zhanqun_resource_dict.get(domain)
        if not path_route:
            return False
        path_route["domain"] = domain

        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return False

        version = dbm_factory.version.load({"version": version})
        if not version:
            return False

        conf_dict = {}
        for item in version:
            _terminal = item.get("terminal")
            if _terminal not in conf_dict:
                conf_dict[_terminal] = {}
            _page_key = item.get("page_key")
            conf_dict[_terminal][_page_key] = {
                "modules": json.JSONDecoder().decode(item.get("content")),
                "module_conf": dbm_factory.version_detail.load({
                    "terminal": _terminal,
                    "page_key": _page_key,
                    "version": item.get("version"),
                }),
            }
        ret = {
            "conf_dict": conf_dict.get(terminal, {}).get(page_key),
            "path_route": path_route,
            "db_id": request.GET.get("db_id"),
            "baike_id": request.GET.get("baike_id"),
            "section": request.GET.get("section"),
        }
        return ret

class VersionUtils(ModuleBase):
    BASE_VERSION = "base"
    TERMINAL_VERSION = "terminal"
    PAGE_VERSION = "page"

    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = ""
        self.module_key = "version_utils"

    def list_to_dict(self, records, dbm_factory):
        ret = {}
        owner = {}
        for item in records:
            if item.get('status') == -1:
                continue
            version = item.get("version")
            owner[version] = item.get("owner")
            if version not in ret:
                ret[version] = {}

            terminal = item.get("terminal")
            if terminal not in ret[version]:
                ret[version][terminal] = {}

            page_key = item.get("page_key")
            if page_key not in ret[version][terminal]:
                ret[version][terminal][page_key] = {}
            ret[version][terminal][page_key] = item

        final = []
        for version in ret:
            tmp = {"version": version, "terminal": [], "page_key": [], "version_detail": self.version_detail(version)}
            tmp["owner"] = dbm_factory.cml_user.get(owner.get(version))
            for terminal in ret[version]:
                tmp["terminal"].append(terminal)
                for page_key in ret[version][terminal]:
                    tmp["page_key"].append(ret[version][terminal][page_key])
            final.append(tmp)
        return final

    def valid_version(self, version):
        query = self.sql_ins.get(
            Select = ["*"],
            From = "zhanqun_cml_conf_online",
            Where = {"version": '''= "{}"'''.format(version)}
        )
        ret = self.luna_sql.raw(query)
        if len(ret):
            return False

        query = self.sql_ins.get(
            Select = ["*"],
            From = "zhanqun_cml_conf_version",
            Where = {"version": '''= "{}"'''.format(version)}
        )
        ret = self.luna_sql.raw(query)
        if len(ret):
            return False

        return True

    def version_status(self, version):
        query = self.sql_ins.get(
            Select = ["*"],
            From = "zhanqun_cml_conf_online",
            Where = {"version": '''= "{}"'''.format(version)}
        )
        ret = self.luna_sql.raw(query)
        if len(ret):
            return ret[0].get("status")

        return -1

    def version_detail(self, version):
        query = self.sql_ins.get(
            Select = ["*"],
            From = "zhanqun_cml_conf_online",
            Where = {"version": '''= "{}"'''.format(version)}
        )
        ret = self.luna_sql.raw(query)
        if len(ret):
            return ret[0]

        return {}

    def version_desc(self, version):
        query = self.sql_ins.get(
            Select = ["*"],
            From = "zhanqun_cml_conf_online",
            Where = {"version": '''= "{}"'''.format(version)}
        )
        ret = self.luna_sql.raw(query)
        if len(ret):
            desc = ret[0].get("desc")
            if not desc:
                desc = ""
            return desc
        return ""

    def new_version(self):
        return hashlib.md5(str(time.time())).hexdigest()

class GeneratorEditConf(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = ""
        self.module_key = "generator_edit_conf"

    def load(self, params):
        '''
            /i-admin/preview/?v=3b3a3e31a2c6a502145a96aada154645&pk=home&d=jita&t=pc
        '''
        request = params.get("request")
        if not request:
            return False

        version = request.GET.get("v")
        if not version:
            return False

        page_key = request.GET.get("pk")
        if not page_key:
            return False
        page_key = urllib.unquote(page_key)

        terminal = request.GET.get("t")
        if not terminal:
            return False

        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return False

        version_info = dbm_factory.version.load_version(version, _where = {
            "terminal": '''= "%s"''' % terminal,
            "page_key": '''= "%s"''' % page_key,
        })
        if not version_info:
            return False

        if len(version_info):
            version_info = version_info[0]

        version_detail_ret = dbm_factory.version_detail.load_version(version, _where = {
            "terminal": '''= "%s"''' % terminal,
            "page_key": '''= "%s"''' % page_key,
        })
        version_detail = {}
        if version_detail_ret:
            for detail in version_detail_ret:
                version_detail[detail.get("conf_key")] = detail.get('content')

        return {"version_info": version_info, "version_detail": version_detail}
