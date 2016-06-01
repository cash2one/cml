#-*- coding:utf-8 -*-
import json
import urllib
import re
import time
import settings
from django import template
register = template.Library()

@register.filter
def urlquote(query):
    if type(query) == type(u''):
        query = query.encode("utf8")
    return urllib.quote(query)

@register.filter
def site_url(path, base):
    if not path:
        return base
    path = str(path)
    if path.startswith("http"):
        return path
    if path.startswith("javascript"):
        return path
    return "/".join([base.rstrip("/"), path.lstrip("/")])

@register.filter
def static_url(path, base):
    if not path:
        return base
    path = str(path)
    if path.startswith("http"):
        return path

    if settings.DEBUG:
        return site_url(path, base)

    # 静态文件存储服务器
    if settings.CDN_URL:
        base = settings.CDN_URL
    return "/".join([base.rstrip("/"), path.lstrip("/")])

@register.filter
def html_tags_fix(html):
    # 修复html缺失闭合
    ret = ""
    pos = 0
    pl = {}
    place_holder = 0
    length = len(html)
    tag_inner = False
    current_tag = ''
    while pos < length:
        ch = html[pos]
        if ch == "<":
            ret += current_tag
            current_tag = ch
            tag_inner = True
            pos += 1
            continue

        if ch == ">":
            if tag_inner:
                current_tag += ch
                pl[place_holder] = current_tag
                ret += "<{__pl__%s__}>" % place_holder
                place_holder += 1
                tag_inner = False
                pos += 1
                current_tag = ''
                continue

        if tag_inner:
            current_tag += ch
            pos += 1
            continue

        ret += ch
        pos += 1

    stack = []
    for pl_index in xrange(place_holder):
        pl_string = pl[pl_index]
        right = re.match(r"</([^>]+)>", pl_string, re.S)
        if right:
            tag = right.group(1)
            if not len(stack):
                pl[pl_index] = ''
            else:
                left = stack[-1]
                left_string = pl[left]
                if left_string.startswith("<%s" % tag):
                    stack = stack[:-1]
                else:
                    pl[pl_index] = ''
        else:
            left_string = pl[pl_index]
            if re.match(r"<[^/>]+?/>", left_string):
                tag = re.findall(r"<(\S+)[^>]+?>", left_string, re.S)
                if tag:
                    tag = tag[0]
                    if tag not in ("img", "br"):
                        pl[pl_index] = ""
            else:
                stack.append(pl_index)
    for pl_index in stack:
        left_string = pl[pl_index]
        tag = re.findall(r"<(\S+)[^>]+?>", left_string, re.S)
        if tag:
            tag = tag[0]
        if tag not in ("img", "br"):
            pl[pl_index] = ''

    for pl_index in xrange(place_holder):
        ret = ret.replace("<{__pl__%s__}>" % pl_index, pl[pl_index])
    return ret

@register.filter
def del_html_tags(html):
    try:
        html = re.sub(r"&[^;]{2,10};", "", html)
        html = re.sub(r'<[^>]+?>', '', html)
        html = re.sub(r"\s+", " ", html)
        return html
    except Exception as info:
        return html

@register.filter
def substr(content, length = 100):
    try:
        content = content.strip()
        return content[:length]
    except Exception as info:
        return content

@register.filter
def full_number(number):
    try:
        if int(number) < 10 and int(number) >= 1:
            return '0{}'.format(number)
        return number
    except Exception as info:
        return number
