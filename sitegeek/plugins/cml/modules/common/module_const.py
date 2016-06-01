#-*- coding:utf-8 -*-

class CommonKey:
    ENCODING = "utf-8"
    RENDER_DATA_KEY = "r__data"
    RENDER_TPL_KEY = "r__template"
    RENDER_COMMON_KEY = "r__common"
    RENDER_PRIORITY_KEY = "r__priority"

class ModuleKey:
    MK_BASE = "base"

    MK_CSRF = "csrf"
    MK_CSRF_TPL = "module/common/module-csrf.html"

    MK_TDK = "tdk"
    MK_TDK_TPL = "module/common/module-tdk.html"


class ConfKey:
    CK_CONF_DICT = "ck__conf_dict"
    CK_CONF_PLACE_HOLDER = "conf_{}"

class ParamKey:
    PK_TEMPLATE = "pk__template"
    PK_REQUEST = "pk__request"
    PK_MODULE_CONF = "pk__module_conf"
    PK_TDK = "pk__tdk"
    PK_PATH_KEY = "pk__path_key"
    PK_PATH_KEY_SPLIT = "@@"
