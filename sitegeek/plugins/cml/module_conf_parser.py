#!/usr/bin/env python
#-*- coding:utf-8 -*-

import ConfigParser
import os
ROOT = os.path.abspath(os.path.dirname(__file__))
import re
from zhanqun.utils.common import merge_dict
import time
import thread
from zhanqun.settings import DEBUG_LOGGER
from dbm.module_db import dbm_factory as DBM_FACTORY
import json
from cml.switches import DYNC_cml_conf_db_load
from cml.switches import DYNC_cml_add_domain_from_conf
from cml.conf_convert import add_new_domain
from zhanqun.settings import CONF_RELOAD_DELAY

# 只是为了兼容之前的写法。要不然parser中conf加载的地方都得重写
class BaseDict(object):
    def __init__(self, _dict):
        self.__dict = _dict

    def __getitem__(self, key):
        if key not in self.__dict:
            return False
        return self.__dict[key]

    def __getattr__(self, key):
        return self[key]

    def sections(self):
        return self.__dict.keys()

    def get(self, section, option = None):
        if not self.__dict:
            return False
        if section not in self.__dict:
            return False
        if not option:
            return self.__dict[section]
        if option not in self.__dict[section]:
            return False
        return self.__dict[section][option]

    def empty(self):
        if not self.__dict:
            return True
        return False

class ConfigToDict(object):
    def __init__(self, conf_root = None):
        self.base_section_key = "base"
        self.base_modules_key = "modules"
        self.data = {}
        self.conf_root = conf_root
        self.file_prefix = "file:"
        self.file_deep_level = 2

    def conf2dict(self, path, level = 1):
        if level > self.file_deep_level:
            return path
        if not os.path.exists(path):
            return False
        config_handle = ConfigParser.ConfigParser()
        config_handle.read(path)
        ret = {}
        for section in config_handle.sections():
            ret[section] = {}
            for option in config_handle.options(section):
                item = config_handle.get(section, option)
                if not item:
                    continue
                if item.startswith(self.file_prefix):
                    ret[section][option] = self.conf2dict(os.path.join(self.conf_root, item.replace(self.file_prefix, "")), level + 1)
                else:
                    ret[section][option] = item
        return ret

    def get_module_conf(self, section):
        try:
            ret = {}
            for key in section:
                if key.startswith("conf_"):
                    ret[key] = self.conf2dict(os.path.join(self.conf_root, section.get(key)))
            return ret
        except Exception as info:
            return False

    def is_alone_module(self, _dict):
        is_alone = _dict.get("alone")
        if is_alone == "1":
            return True
        return False

    def get_page_module(self, base_module_list, _dict, place_holder):
        if self.is_alone_module(_dict):
            return _dict.get(self.base_modules_key)

        module_list = base_module_list
        for pl in place_holder:
            if pl not in _dict:
                continue
            pl_module_list = _dict.get(pl)
            _place_holder = re.findall(r"{([^{}]+?)}", pl_module_list)
            for _pl in _place_holder:
                if _pl not in _dict:
                    continue
                pl_module_list = self.get_page_module(pl_module_list, _dict, _place_holder)
            module_list = module_list.replace("{%s}" % pl, pl_module_list)
        return module_list

    def load(self, path):
        self.conf_root = os.path.dirname(path)
        conf_dict = self.conf2dict(path)
        if self.base_section_key not in conf_dict:
            return False

        base_section = conf_dict.get(self.base_section_key)
        base_module_list = base_section.get(self.base_modules_key)
        if not base_module_list:
            return False
        place_holder = re.findall(r"{([^{}]+?)}", base_module_list)
        base_module_conf = self.get_module_conf(base_section)
        conf_dict.pop(self.base_section_key)
        ret = {}
        for page_key in conf_dict:
            _dict = conf_dict.get(page_key)
            ret[page_key] = {
                             "modules": self.get_page_module(base_module_list, _dict, place_holder),
                             "module_conf": merge_dict(base_module_conf, self.get_module_conf(_dict)),
                             }
        self.data = ret

    def get(self):
        return self.data

class Config(object):
    def __init__(self, cml_conf_root):
        self.root = cml_conf_root
        self.config_to_dict = ConfigToDict()
        self.pc_base_conf = "base.conf"
        self.m_base_conf = "m.base.conf"
        self.pc_key = "pc"
        self.m_key = "m"
        self.base_key = "base"
        self.data_loaded = {}
        self.data = self.load()
        if DYNC_cml_add_domain_from_conf:
            add_new_domain(self.data)

        thread_ins = thread.start_new_thread(self.reload, (CONF_RELOAD_DELAY,))

    def reload(self, delay = 120):
        while True:
            time.sleep(delay)
            try:
                self.data_loaded = {}
                data = self.load()
                self.data = data
                for path in self.data_loaded:
                    DEBUG_LOGGER.info("reload conf [%s] status [%s] from [%s]." % (path, self.data_loaded[path].get("status"), self.data_loaded[path].get("from")))
                DEBUG_LOGGER.info("reload conf success. sleep %ss" % delay)
            except Exception as info:
                DEBUG_LOGGER.fatal("reload conf error [%s]. sleep %ss" % (info, delay))

    def load(self):
        ret = {}
        if not DYNC_cml_add_domain_from_conf and DYNC_cml_conf_db_load:
            try:
                _ret = self.load_from_db()
                if _ret:
                    DEBUG_LOGGER.info("reload from db success")
                    ret = _ret
            except Exception as info:
                DEBUG_LOGGER.fatal("reload from db error [%s]" % info)
        for path in os.listdir(self.root):
            if path.startswith("."):
                continue
            conf_path = os.path.join(self.root, path)
            if os.path.isfile(conf_path):
                continue

            if path in self.data_loaded:
                DEBUG_LOGGER.info("domain[%s] has loaded from [%s]" % (path, self.data_loaded.get(path).get("from")))
                continue

            base_conf = os.path.join(conf_path, self.pc_base_conf)
            if not os.path.isfile(base_conf):
                continue
            ret[path] = {self.pc_key: False}
            self.config_to_dict.load(base_conf)
            ret[path][self.pc_key] = self.config_to_dict.get()
            self.data_loaded[path] = {
                "status": True,
                "from": "conf",
            }
            base_conf = os.path.join(conf_path, self.m_base_conf)
            if not os.path.isfile(base_conf):
                continue
            ret[path][self.m_key] = False
            self.config_to_dict.load(base_conf)
            ret[path][self.m_key] = self.config_to_dict.get()
        return ret

    def load_from_db(self):
        online = DBM_FACTORY.conf_online.load()
        if not online:
            return False
        ret = {}
        for item in online:
            domain_en = item.get("domain_en", False)
            if not domain_en:
                continue
            version = DBM_FACTORY.version.load({"version": item.get("version", False)}, 0)
            if not version:
                continue
            ret[domain_en] = {}
            for item in version:
                terminal = item.get("terminal")
                if terminal not in ret[domain_en]:
                    ret[domain_en][terminal] = {}
                page_key = item.get("page_key")
                ret[domain_en][terminal][page_key] = {
                    "modules": json.JSONDecoder().decode(item.get("content")),
                    "module_conf": DBM_FACTORY.version_detail.load({
                        "terminal": terminal,
                        "page_key": page_key,
                        "version": item.get("version"),
                    }),
                }
            self.data_loaded[domain_en] = {
                "status": True,
                "from": "db",
            }

        return ret

    def get(self):
        return self.data

    def get_conf(self, domain, is_mobile):
        base_dict = self.data.get(domain)
        if not base_dict:
            base_dict = self.data.get(self.base_key)
        if is_mobile:
            ret = base_dict.get(self.m_key)
            if ret:
                return ret
        return base_dict.get(self.pc_key)

if __name__ == "__main__":
    # config_dict = ConfigToDict()
    # config_dict.load("./conf/yasi/base.conf")
    # conf_obj = config_dict.get().get("home")
    # print conf_obj
    # module_conf = conf_obj.get("module_conf")
    # for key in module_conf:
    #     sub = module_conf.get(key)
    #     for s in sub:
    #         print key, s, sub[s]
    #     break

    print Config("./conf/").get()
