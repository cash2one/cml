#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase
import urllib
import json

class DotaHero(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "dota_hero"
        self.module_key = "dota_hero"

    def load(self, params):
        where = {}
        request = params.get("request")
        hero_name = request.GET.get("heroname")
        if hero_name:
            hero_name = urllib.unquote(hero_name)
            where = {"name_en": '''= "%s"''' % hero_name}

        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = where
        )

        query = request.GET.get("q")
        if query:
            query = urllib.unquote(query)
            if records_sql.find("WHERE") == -1:
                records_sql += ''' WHERE'''
            records_sql += ''' (`name_en` LIKE "%%%s%%" OR `name` LIKE "%%%s%%" OR `nickname` LIKE "%%%s%%")''' % (query, query, query)

        result = self.execute(records_sql)
        if not result.get("amounts"):
            return False
        return result.get("records")

    def load_detail(self, params):
        hero_name = params.get("hero_name")
        if not hero_name:
            return []
        hero_name = urllib.unquote(hero_name)
        where = {"name_en": '''= "%s"''' % hero_name}

        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = where
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return {}
        ret = result.get("records")[0]
        ret["skill"] = json.JSONDecoder().decode(ret["skill"])
        ret["power"] = json.JSONDecoder().decode(ret["power"])
        ret["agile"] = json.JSONDecoder().decode(ret["agile"])
        ret["intellectual"] = json.JSONDecoder().decode(ret["intellectual"])
        ret["attack_power"] = json.JSONDecoder().decode(ret["attack_power"])
        ret["armor"] = json.JSONDecoder().decode(ret["armor"])
        return ret
