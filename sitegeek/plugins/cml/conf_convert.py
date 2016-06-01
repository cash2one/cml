#!/usr/bin/env python
#-*- coding:utf-8 -*-
from dbm.module_base import sql_instance as SqlInstance
from common.context import luna_service as Luna
from common.mysql import luna_sql_service as LunaSQL
from dbm.module_db import dbm_factory as DBM_FACTORY
import hashlib
import time
import json
import MySQLdb


# 修改此文件前请联系 [luoruiyang]
new_domain_dict = {
    # "qiuzhi": {
    #     "name": u"求职",
    # },
    # "admin": {
    #     "name": u"后台管理",
    # },
    # "home": {
    #     "name": u"站点地图",
    # }
}

def valid_version(version):
    query = SqlInstance.get(
        Select = ["*"],
        From = "zhanqun_cml_conf_online",
        Where = {"version": '''= "{}"'''.format(version)}
    )
    ret = LunaSQL.raw(query)
    if len(ret):
        return False

    query = SqlInstance.get(
        Select = ["*"],
        From = "zhanqun_cml_conf_version",
        Where = {"version": '''= "{}"'''.format(version)}
    )
    ret = LunaSQL.raw(query)
    if len(ret):
        return False

    return True

def add_new_domain(data):
    for key in data:
        if key not in new_domain_dict:
            continue

        # 1. 写入domain
        query = SqlInstance.get(
            Select = ["*"],
            From = "zhanqun_cml_domain_info",
            Where = {"domain_en": '''= "{}"'''.format(key)}
        )
        ret = LunaSQL.raw(query)
        if not ret:
            domain_dict = new_domain_dict.get(key)
            cn = domain_dict.get("name")
            display_name = domain_dict.get("display_name", cn)
            query = domain_dict.get("query", cn)
            SQL = '''INSERT INTO `zhanqun_cml_domain_info` VALUES ("", "%s", "%s", "%s", "%s", "%s", "%s")''' %\
                    (key, cn, display_name, query, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())), -1)
            LunaSQL.raw(SQL, commit = True)

        query = SqlInstance.get(
            Select = ["*"],
            From = "zhanqun_cml_domain_info",
            Where = {"domain_en": '''= "{}"'''.format(key)}
        )
        ret = LunaSQL.raw(query)
        domain_dict = ret[0]

        base_dict = data[key]
        version = hashlib.md5(str(time.time())).hexdigest()
        while not valid_version(version):
            version = hashlib.md5(str(time.time())).hexdigest()
        SQL = '''INSERT INTO `zhanqun_cml_conf_online` VALUES ("", "%s", "%s", "%s", "%s", "%s", "%s", "")''' %\
                (domain_dict.get("id"), domain_dict.get("domain_en"), version, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())), 1, -1)
        print SQL
        # 获得唯一版本号后，写入数据库中。
        LunaSQL.raw(SQL, commit = True)

        # 写入对应版本的配置信息
        content = {}
        detail_content = {}
        for terminal in base_dict:
            for page_key in base_dict[terminal]:
                SQL = '''INSERT INTO `zhanqun_cml_conf_version` VALUES ("", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "")''' %\
                        (version, terminal, page_key, MySQLdb.escape_string(json.JSONEncoder().encode(base_dict[terminal][page_key]["modules"])), 1, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())), 0)
                LunaSQL.raw(SQL, commit = True)
                module_conf = base_dict[terminal][page_key].get("module_conf", {})
                for conf_key in module_conf:
                    conf_content = module_conf.get(conf_key)
                    if not conf_content:
                        continue
                    SQL = '''INSERT INTO `zhanqun_cml_conf_version_detail` VALUES ("", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")''' %\
                    (version, terminal, page_key, "-", conf_key, MySQLdb.escape_string(json.JSONEncoder().encode(module_conf.get(conf_key))), 1, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())), 0)
                    LunaSQL.raw(SQL, commit = True)

        # 更新版本
        # 将原来存在的status置为-1
        SQL = '''UPDATE `zhanqun_cml_conf_online` SET `status` = -1 WHERE `domain_en` = "%s" AND `version` <> "%s"''' % (domain_dict.get("domain_en"), version)
        print SQL
        LunaSQL.raw(SQL, commit = True)
        # 将新增的status置为0
        SQL = '''UPDATE `zhanqun_cml_conf_online` SET `status` = 0 WHERE `domain_en` = "%s" AND `version` = "%s"''' % (domain_dict.get("domain_en"), version)
        print SQL
        LunaSQL.raw(SQL, commit = True)

if __name__ == "__main__":
    pass
