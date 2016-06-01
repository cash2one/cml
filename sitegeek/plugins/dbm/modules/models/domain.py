#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.modules.base import ModuleBase

class DomainInfo(ModuleBase):
    def __init__(self, Luna, LunaSQL, SqlInstance):
        ModuleBase.__init__(self, Luna, LunaSQL, SqlInstance)
        self.table = "zhanqun_cml_domain_info"
        self.module_key = "domain_info"

    def get(self, domain_en):
        records_sql = self.sql_ins.get(
            Select = ["*"],
            From = self.table,
            Where = {"domain_en": '''= "{}"'''.format(domain_en)}
        )
        result = self.execute(records_sql)
        if not result.get("amounts"):
            return False
        return result.get("records")[0]
