#!/usr/bin/env python
#-*- coding:utf-8 -*-
from cml.modules.common.module import ModuleBase
from cml.modules.common.module import deco
import re
import json
import base64
import urllib

class ModuleDotaHeroListMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/dota/hero-list.html"
        self.module_key = "m.dota-hero-list"

    def _parse_hero_list(self, params):
        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return []
        return dbm_factory.dota_hero.load(params)

    @deco
    def load(self, params):
        data = {"module_dota_hero": self._parse_hero_list(params)}
        return {"template": params.get("template"), "data": data}

class ModuleDotaHeroDetailMsite(ModuleBase):
    def __init__(self, Luna, LunaSQL):
        ModuleBase.__init__(self, Luna, LunaSQL)
        self.template = "module/msite/dota/hero-detail.html"
        self.module_key = "m.dota-hero-detail"

    def _parse_hero_detail(self, params):
        dbm_factory = params.get("dbm_factory")
        if not dbm_factory:
            return []
        return dbm_factory.dota_hero.load_detail(params)

    @deco
    def load(self, params):
        data = {"module_dota_hero": self._parse_hero_detail(params)}
        hero = data["module_dota_hero"]
        common = {
            "tdk": {
                "title": u"%s_%s_%s - 跟谁学刀塔资料" % (hero.get("name", ''), hero.get("name_en", ''), hero.get("nickname", '')),
                "keywords": u"%s,%s,%s,刀塔,dota,dota2" % (hero.get("name", ''), hero.get("name_en", ''), hero.get("nickname", '')),
                "description": u"%s - %s" % (hero.get("name", ""), hero.get("story", ""))
            }
        }
        return {"template": params.get("template"), "data": data, "common": common}
