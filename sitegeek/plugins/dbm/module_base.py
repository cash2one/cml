#-*- coding:utf-8 -*-
import re
import MySQLdb

class SqlInstance(object):
    def __init__(self):
        self.sql = ""

    def insert(self, Table, Colums = False, Values = False):
        if not Values:
            return False
        insert_sql = u'''INSERT INTO `%s` ''' % Table
        if Colums:
            insert_sql += u'''('''
            colums = []
            for colum in Colums:
                colums.append(self.add_quote(colum))
            insert_sql += u",".join(colums)
            insert_sql += u''')'''

        insert_sql += u''' VALUES('''
        values = []
        for value in Values:
            values.append(u'''"%s"''' % MySQLdb.escape_string(value))
        insert_sql += u",".join(values)
        insert_sql += u''')'''
        return insert_sql

    def get(self, Select, From, Where = False, GroupBy = False, OrderBy = False, Limit = False):
        sql = ["SELECT",
               self.select(Select),
               "FROM",
               self.add_quote(From),
               self.where(Where),
               self.group_by(GroupBy),
               self.order_by(OrderBy),
               self.limit(Limit)]
        self.sql = " ".join(sql).strip()
        return re.sub(r"\s+", " ", self.sql)

    def limit(self, Limit):
        if not Limit:
            return ""

        return "LIMIT %s" % Limit

    def select(self, sel):
        ret = []
        for s in sel:
            ret.append(self.add_quote(s))
        return ",".join(ret)

    def is_special(self, colum):
        if colum.strip() == "*":
            return True

        if not colum.strip().lower().startswith("date_format(") and\
           not colum.strip().lower().startswith("sum(") and\
           not colum.strip().lower().startswith("count(") and\
           not colum.strip().lower().startswith("`") and\
           not colum.strip().lower().startswith("distinct") and\
           not colum.strip().lower().startswith("(") and\
           not colum.find(".") != -1:
           return False
        else:
           return True

    def where(self, w):
        if not w:
            return ""
        conditions = []
        for key in w:
            value = w.get(key)
            key = self.add_quote(key)
            conditions.append(" ".join([key, value]))
        if not len(conditions):
            return ""
        return "WHERE " + " AND ".join(conditions)

    def group_by(self, group):
        if not group:
            return ""

        return "GROUP BY %s" % ",".join(map(self.add_quote, group))

    def order_by(self, order):
        if not order:
            return ""
        ret = "ORDER BY "
        for value, desc in order:
            ret += self.add_quote(value)
            if desc:
                ret += " DESC,"
            else:
                ret += ","
        return ret.strip(",")

    def add_quote(self, column):
        if self.is_special(column):
            return "%s" % column
        return "`%s`" % column

sql_instance = SqlInstance()

if __name__ == "__main__":
    pass
