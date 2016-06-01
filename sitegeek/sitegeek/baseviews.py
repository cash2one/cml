#!/usr/bin/env python
#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import Http404

def views_deco(views_func, **argv):
    def _deco(request, **argv):
        ret_argv = argv
        ret_argv["request"] = request
        ret_argv["path_route"] = path_route
        ret_argv["_for_public"] = {}
        ret_argv["timer_counter"] = sitegeek.settings.TC()
        ret_argv["path_key"] = "@@".join(request.path_info.strip("/").split("/"))
        return views_func(request, ret_argv)
    return _deco
