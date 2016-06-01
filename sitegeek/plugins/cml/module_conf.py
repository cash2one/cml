#!/usr/bin/env python
from zhanqun.utils.common import get_path_route
from zhanqun.settings import DEBUG_LOGGER
import ConfigParser
import base_conf
import re
import os
from cml.switches import DYNC_cml_conf_db
from cml.module_conf_parser import Config
from zhanqun.utils.common import is_mobile_request
ROOT = os.path.abspath(os.path.dirname(__file__))

class ConfKeys(object):
    HOME = "home"
    LIST= "list"
    LIST_AJAX = "list_ajax"
    DETAIL = "detail"
    YASI_BAIKE = "yasi_baike"
    COURSE = "course"
    SEARCH = "search"
    TOPIC = "topic"
    ADMIN_VERION = "admin-version"
    ADMIN_ONLINE = "admin-online"
    ADMIN_ADD_CONF = "admin-add-conf"
    ADMIN_ADD_USER = "admin-add-user"
    ADMIN_EDIT = "admin-edit"
    ADMIN_README = "admin-readme"
    ADMIN_APPLY_ONLINE = "admin-apply-online"
    ADMIN_AUTH_ONLINE = "admin-auth-online"
    ADMIN_PASSWORD = "admin-password"
    ADMIN_KEYWORDS_ADD = "admin-keywords-add"
    ADMIN_KEYWORDS_EDIT = "admin-keywords-edit"
    ADMIN_CMS_EDIT = "admin-cms-edit"

    DOTA_HERO = "hero"
    DOTA_HERO_DETAIL = "hero-detail"

    ADMIN_SUBJECT_ADD = "admin-subject-add"
    ADMIN_SUBJECT_EDIT = "admin-subject-edit"

class ConfNode(object):
    def __init__(self, conf, conf_path, conf_key):
        self.conf = conf
        self.conf_path = conf_path
        self.conf_key = conf_key

class ConfKeyIter(object):
    def __init__(self, key):
        self.__join = "@@"
        self.key = key.split(self.__join)
        self.count = 0
        self.data = False

    def next(self):
        if self.count >= 0:
            self.count -= 1
            self.data = self.__join.join(self.key)
            return self.data
        self.data = self.__join.join(self.key[:self.count])
        self.count -= 1
        return self.data

    def get(self):
        return self.data
#
class ConfReader(object):
    def __init__(self):
        self.ROOT_CONF_PATH = os.path.join(ROOT, "conf", "base", "base.conf")
        self.M_ROOT_CONF_PATH = os.path.join(ROOT, "conf", "base", "m.base.conf")

    def read(self, conf_path, conf_key, is_mobile = False):
        if not os.path.exists(conf_path):
            DEBUG_LOGGER.debug("conf_path [%s] not exists" % conf_path)
            if is_mobile:
                conf_path = self.M_ROOT_CONF_PATH
            else:
                conf_path = self.ROOT_CONF_PATH
        DEBUG_LOGGER.debug("conf_path [%s]" % conf_path)
        conf = ConfigParser.ConfigParser()
        conf.read(conf_path)

        conf_key_iter = ConfKeyIter(conf_key)
        while conf_key_iter.next():
            if conf_key_iter.get() in conf.sections():
                break

        return ConfNode(conf, conf_path, conf_key_iter.get())

class ConfUtils(object):
    @staticmethod
    def merge_conf(base, diff, path):
        delete = {}
        for key in base.get_idx():
            value = base[key]
            place_holder = re.findall(r'{([^{}]+)}', value)
            for pl in place_holder:
                if pl in diff.get_idx():
                    base.update(key, value.replace('{%s}' % pl, diff[pl]))
                    delete[pl] = True
        for key in diff.get_idx():
            if key not in delete:
                base.add(key, diff[key])
        base.add("conf_root", os.path.dirname(path))
        try:
            modules = base.modules
            sub_module = re.findall(r"\{[^{}]+\}", modules)
            for m in sub_module:
                m = m.strip("{}")
                if m not in base.get_idx():
                    continue
                modules = modules.replace("{%s}" % m, base[m])
            base.update("modules", modules)
        except Exception as info:
            DEBUG_LOGGER.fatal("merge_conf warning [%s]" % info)
        return base

    @staticmethod
    def convert_conf(conf, conf_key):
        base_conf_ins = base_conf.base_conf_t()
        base_conf_dict = conf.options(conf_key)
        for item in base_conf_dict:
            base_conf_ins.add(item, conf.get(conf_key, item))
        return base_conf_ins

    @staticmethod
    def get_conf_name(root, filename):
        if not filename.startswith("."):
            return filename
        return os.path.join(root, filename)

class SafeConfParser(object):
    def __init__(self, path):
        self.path = path
        self.load()

    def load(self):
        try:
            self.conf = ConfigParser.ConfigParser()
            self.conf.read(self.path)
        except Exception as info:
            self.conf = False
            DEBUG_LOGGER.fatal("SafeConfParser.load error [%s]" % info)

    def get(self, section, option = None):
        if section not in self.conf.sections():
            return ''
        if not option:
            return self.conf.options(section)
        if option not in self.conf.options(section):
            return ''
        return self.conf.get(section, option)

class ConfFactory(object):
    def __init__(self, conf_reader_ins = None, conf_root = None):
        self.conf_root = conf_root
        if not self.conf_root:
            self.conf_root = os.path.join(ROOT, "conf")
        self.conf_reader_ins = conf_reader_ins
        if not self.conf_reader_ins:
            self.conf_reader_ins = ConfReader()

        self.modules_key = "modules"
        self.base_section = "base"

        self.cml_conf_data = False
        self.cml_conf_data_load_status = False

        DEBUG_LOGGER.info("conf_root = [%s]" % self.conf_root)
        if DYNC_cml_conf_db:
            DEBUG_LOGGER.info("DYNC_cml_conf_db is on, load cml_conf to mem. conf_root = [%s]" % self.conf_root)
            try:
                self.cml_conf_data = Config(self.conf_root)
                self.cml_conf_data_load_status = True
                DEBUG_LOGGER.info("load cml_conf to mem success")
            except Exception as info:
                DEBUG_LOGGER.fatal("load cml_conf to mem error [%s]" % info)
                self.cml_conf_data_load_status = False


    def load(self, request, conf_key):
        if not request:
            return False
        pr = get_path_route(request)
        if not pr:
            DEBUG_LOGGER.fatal("path_route parse error, request_path_info = [%s]" % request.path_info)
            return False

        domain = pr.get("domain")
        if not domain:
            DEBUG_LOGGER.fatal("path_route parse domain error, request_path_info = [%s]" % request.path_info)
            return False

        if DYNC_cml_conf_db and self.cml_conf_data and self.cml_conf_data_load_status:
            ret = self.cml_conf_data.get_conf(domain, is_mobile_request(request))
            if not ret:
                return False
            conf_key_iter = ConfKeyIter(conf_key)
            while conf_key_iter.next():
                if conf_key_iter.get() in ret:
                    return ret.get(conf_key_iter.get())
            return False

        if not is_mobile_request(request):
            conf_path = os.path.join(self.conf_root, domain, "base.conf")
        else:
            conf_path = os.path.join(self.conf_root, domain, "m.base.conf")
            if not os.path.exists(conf_path):
                conf_path = os.path.join(self.conf_root, domain, "base.conf")
        DEBUG_LOGGER.debug("conf_path = [%s]" % conf_path)
        return self.conf_reader_ins.read(conf_path, conf_key, is_mobile_request(request))

    def parse(self, conf_node, is_ajax = False):
        if DYNC_cml_conf_db and self.cml_conf_data and self.cml_conf_data_load_status:
            return False
        conf = conf_node.conf
        if conf_node.conf_key not in conf.sections():
            DEBUG_LOGGER.fatal("conf_key [%s] not exists" % conf_node.conf_key)
            return False

        if is_ajax:
            return ConfUtils.merge_conf(base_conf.base_conf_t(), ConfUtils.convert_conf(conf, conf_node.conf_key), conf_node.conf_path)
        else:
            return ConfUtils.merge_conf(ConfUtils.convert_conf(conf, self.base_section), ConfUtils.convert_conf(conf, conf_node.conf_key), conf_node.conf_path)

conf_factory = ConfFactory()
conf_keys = ConfKeys()

if __name__ == "__main__":
    pass
