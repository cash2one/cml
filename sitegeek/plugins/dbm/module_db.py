#!/usr/bin/env python
#-*- coding:utf-8 -*-
from zhanqun.settings import DEBUG_LOGGER
from common.context import luna_service as Luna
from common.mysql import luna_sql_service as LunaSQL
from dbm.module_base import sql_instance as SqlInstance
from module_import import *

class DbmFactory(object):
    def __init__(self):
        self.module = {}
        self.module_key = "dbm_factory"

    def register(self, module_ins):
        if module_ins.module_key in self.module:
            raise KeyError("module [%s] exists" % module_ins.module_key)

        self.module[module_ins.module_key] = module_ins
        DEBUG_LOGGER.info("register dbm[%s] success" % module_ins.module_key)

    def get_module(self, module_key):
        return self.module.get(module_key)

    def __getitem__(self, key):
        if key not in self.module:
            raise KeyError("module [%s] does not exists" % key)
        return self.module[key]

    def __getattr__(self, key):
        return self[key]

    def size(self):
        return len(self.module)

dbm_factory = DbmFactory()

dbm_factory.register(GetUserInfo(Luna, LunaSQL, SqlInstance))
dbm_factory.register(DeleteRecords(Luna, LunaSQL, SqlInstance))
dbm_factory.register(ConfOnline(Luna, LunaSQL, SqlInstance))
dbm_factory.register(Version(Luna, LunaSQL, SqlInstance))
dbm_factory.register(VersionDetail(Luna, LunaSQL, SqlInstance))
dbm_factory.register(CmlUser(Luna, LunaSQL, SqlInstance))
dbm_factory.register(CmlUserAction(Luna, LunaSQL, SqlInstance))
dbm_factory.register(Sessions(Luna, LunaSQL, SqlInstance))
dbm_factory.register(GeneratorPreviewConf(Luna, LunaSQL, SqlInstance))
dbm_factory.register(GeneratorEditConf(Luna, LunaSQL, SqlInstance))
dbm_factory.register(VersionUtils(Luna, LunaSQL, SqlInstance))
dbm_factory.register(Module(Luna, LunaSQL, SqlInstance))
dbm_factory.register(DomainInfo(Luna, LunaSQL, SqlInstance))
dbm_factory.register(CmlCopy(Luna, LunaSQL, SqlInstance))
dbm_factory.register(DomainKeywords(Luna, LunaSQL, SqlInstance))
dbm_factory.register(DemandInfo(Luna, LunaSQL, SqlInstance))
dbm_factory.register(BaiduQuestion(Luna, LunaSQL, SqlInstance))
dbm_factory.register(CorporaCms(Luna, LunaSQL, SqlInstance))
dbm_factory.register(SetInterest(Luna, LunaSQL, SqlInstance))
dbm_factory.register(GetInterest(Luna, LunaSQL, SqlInstance))
dbm_factory.register(UserSend(Luna, LunaSQL, SqlInstance))
dbm_factory.register(SearchAction(Luna, LunaSQL, SqlInstance))
dbm_factory.register(DotaHero(Luna, LunaSQL, SqlInstance))
dbm_factory.register(ApiTopicWww(Luna, LunaSQL, SqlInstance))

DEBUG_LOGGER.info("dbm module.size = [%s]" % dbm_factory.size())

if __name__ == "__main__":
    pass
