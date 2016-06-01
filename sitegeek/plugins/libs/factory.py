
class DictFactory(object):
    def __init__(self):
        self.__dict = {}

    def register(self, key, ins):
        if key in self.__dict:
            raise KeyError("key [%s] exists" % key)

        self.__dict[key] = ins

    def get(self, key):
        return self.__dict.get(key)

    def __getitem__(self, key):
        if key not in self.__dict:
            raise KeyError("key [%s] does not exists" % key)
        return self.__dict[key]

    def __getattr__(self, key):
        return self[key]

    def size(self):
        return len(self.__dict)
