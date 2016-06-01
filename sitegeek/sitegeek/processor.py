#!/usr/bin/env python
#-*- coding:utf-8 -*-

def site_url(request):
    placeholder = {
        "protocol": "https" if request.is_secure() else "http",
        "host": request.get_host(),
    }
    return {
        "SITE_URL": "%(protocol)s://%(host)s/" % placeholder,
    }
