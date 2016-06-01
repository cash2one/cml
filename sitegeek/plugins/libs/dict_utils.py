#-*- coding:utf-8 -*-

def merge_dict(dict_left, dict_right):
    ret = {}
    for _dict in (dict_left, dict_right):
        if not _dict:
            continue
        for key in _dict:
            if key in ret:
                if type(_dict[key]) == type({}):
                    if type(ret[key]) != type({}):
                        ret[key] = {}
                    for skey in _dict[key]:
                        ret[key][skey] = _dict[key][skey]
                else:
                    ret[key] = _dict[key]
            else:
                ret[key] = _dict[key]
    return ret

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
