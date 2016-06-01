#!/usr/bin/env python
#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.shortcuts import HttpResponse
from zhanqun.settings import DEBUG_LOGGER
from zhanqun.utils.common import merge_dict
import re
import json
from cml.switches import DYNC_cml_conf_db
from django.shortcuts import Http404

class ModuleCommon(object):
    k_conf_dict = "conf_dict"
    k_base_loader = "base_loader"
    k_base_render = "base_render"
    k_base_view = "base_view"
    k_pl_module = "place.holder"
    k_render = "render"
    k_template = "template"
    k_request = "request"

    # 三种优化级数据dict
    d_common = "common"
    d_data = "data"
    d_priority = "priority"

    # 分割符
    s_modules = ","
    s_module_conf = "#"
    s_pl_module_key = "."

    # 参数params
    p_timer_counter = "timer_counter"
    p_module_conf = "module_conf"
    p_pl_key = "pl_key"
    p_ispl = "ispl"
    p_conf_factory_key = "_conf_factory_key"
    p_conf_is_ajax = "_conf_is_ajax"
    p_preview_conf = "__preview"
    p_path_route = "path_route"

    # 正则
    r_modules = r"{[^{}]+?}"

    # 前缀
    pre_pl_module_key = "pl."


class ModuleLoader(object):
    def __init__(self, Luna, LunaSQL):
        self.Luna = Luna
        self.LunaSQL = LunaSQL
        self.conf_dict_key = ModuleCommon.k_conf_dict
        self.module_key = ModuleCommon.k_base_loader

    def loader(self, MODULE_FACTORY, params = {}):
        conf_dict = params.get(self.conf_dict_key)
        html_render = []
        common = {}
        priority = {}
        if not conf_dict:
            return {
                ModuleCommon.k_render: html_render,
                ModuleCommon.d_common: common,
                ModuleCommon.d_priority: priority,
            }

        for _module in conf_dict["modules"].split(ModuleCommon.s_modules):
            try:
                # 这里由于公用了同一个dict。每个module load之前要清除之前的module_conf
                params[ModuleCommon.p_module_conf] = False
                params[ModuleCommon.p_pl_key] = False

                _module = _module.strip()
                if re.match(ModuleCommon.r_modules, _module):
                    DEBUG_LOGGER.fatal("unused module [%s]" % _module)
                    continue
                if _module.find(ModuleCommon.s_module_conf) != -1:
                    module, module_conf = _module.split(ModuleCommon.s_module_conf, 1)
                    params[ModuleCommon.p_module_conf] = module_conf
                elif _module.startswith(ModuleCommon.pre_pl_module_key):
                    pl_key = _module.split(ModuleCommon.s_pl_module_key, 1)[-1]
                    params[ModuleCommon.p_pl_key] = pl_key
                    module = ModuleCommon.k_pl_module
                else:
                    module = _module
                if not module:
                    continue

                params.get(ModuleCommon.p_timer_counter).trace_begin("load_module_%s" % _module)
                module_ret = MODULE_FACTORY[module].load(params)
                common = merge_dict(common, module_ret.get(ModuleCommon.d_common, {}))
                priority = merge_dict(priority, module_ret.get(ModuleCommon.d_priority, {}))
                html_render.append(module_ret)
                params.get(ModuleCommon.p_timer_counter).trace_end("load_module_%s" % _module)
            except Http404:
                raise Http404
            except Exception as info:
                DEBUG_LOGGER.fatal("load module [%s] error [%s]" % (_module, info))
        return {ModuleCommon.k_render: html_render, ModuleCommon.d_common: common, ModuleCommon.d_priority: priority}

class ModuleRender(object):
    module_key = ModuleCommon.k_base_render
    @staticmethod
    def render(request, params):
        # 优先级最低的数据dict
        common = params.get(ModuleCommon.d_common, {})

        # 优先级最高的数据dict
        priority = params.get(ModuleCommon.d_priority, {})
        html = u''
        for _render in params.get(ModuleCommon.k_render):
            if _render.get(ModuleCommon.p_ispl):
                html += _render.get(ModuleCommon.k_template)
            else:
                _data = merge_dict(common, _render.get(ModuleCommon.d_data))
                _data = merge_dict(_data, priority)
                _render_ret = render(request, _render.get(ModuleCommon.k_template), _data)
                html += _render_ret.content
        return html

class ModuleView(object):
    module_key = ModuleCommon.k_base_view
    @staticmethod
    def view(module_factory, conf_factory, params):
        params.get(ModuleCommon.p_timer_counter).clear()
        total_key = "%s-%s" % (params.get("path_route").get("domain"), params.get(ModuleCommon.p_conf_factory_key).split("@@", 1)[0])
        params.get(ModuleCommon.p_timer_counter).trace_begin(total_key)
        timer_counter_total_key = "{}-{}".format(params.get("path_route").get("domain"), params.get(ModuleCommon.p_conf_factory_key))
        params.get(ModuleCommon.p_timer_counter).trace_begin(timer_counter_total_key)

        conf = conf_factory.load(params.get(ModuleCommon.k_request), params.get(ModuleCommon.p_conf_factory_key))
        if not conf:
            if params.get(ModuleCommon.p_conf_is_ajax):
                return HttpResponse(json.dumps({"code": -1, "msg": u"请求出错，请刷新重试"}), content_type = "application/json")
            return HttpResponse(u"系统异常,请稍候再试")

        if DYNC_cml_conf_db:
            conf_dict = conf
        else:
            conf_dict = conf_factory.parse(conf, params.get(ModuleCommon.p_conf_is_ajax))
            if not conf_dict:
                if params.get(ModuleCommon.p_conf_is_ajax):
                    return HttpResponse(json.dumps({"code": -1, "msg": u"请求出错，请刷新重试"}), content_type = "application/json")
                return HttpResponse(u"系统异常,请稍候再试")

        params[ModuleCommon.k_conf_dict] = conf_dict
        try:
            params.get(ModuleCommon.p_timer_counter).trace_begin("base_loader")
            html_render = module_factory.base_loader.loader(module_factory, params)
            params.get(ModuleCommon.p_timer_counter).trace_end("base_loader")

            if params.get(ModuleCommon.p_conf_is_ajax):
                data = []
                for _render in html_render.get(ModuleCommon.k_render):
                    data.extend(_render.get(ModuleCommon.d_data))
                if len(data) == 0:
                    return HttpResponse(json.dumps({"code": 1, "msg": u"没有更多内容了"}), content_type = "application/json")
                return HttpResponse(json.dumps({"code": 0, "data": data}), content_type = "application/json")

            params.get(ModuleCommon.p_timer_counter).trace_begin("base_render")
            http_response = HttpResponse()
            html = module_factory.base_render.render(params.get(ModuleCommon.k_request), html_render)
            http_response.write(html)
            params.get(ModuleCommon.p_timer_counter).trace_end("base_render")

            params.get(ModuleCommon.p_timer_counter).trace_end(timer_counter_total_key)
            params.get(ModuleCommon.p_timer_counter).trace_end(total_key)
            DEBUG_LOGGER.info("%s %s" % ("ZHANQUN-WEB", params.get(ModuleCommon.p_timer_counter).to_string(total_key)))
            DEBUG_LOGGER.info(params.get(ModuleCommon.p_timer_counter).to_string_all())
            return http_response
        except Http404:
            raise Http404
        except Exception as info:
            DEBUG_LOGGER.fatal("ModuleView.view error [%s]" % info)
            if params.get(ModuleCommon.p_conf_is_ajax):
                params.get(ModuleCommon.p_timer_counter).trace_end(timer_counter_total_key)
                DEBUG_LOGGER.info(params.get(ModuleCommon.p_timer_counter).to_string_all())
                return HttpResponse(json.dumps({"code": -1, "msg": u"请求出错，请刷新重试"}), content_type = "application/json")
            params.get(ModuleCommon.p_timer_counter).trace_end(timer_counter_total_key)
            DEBUG_LOGGER.info(params.get(ModuleCommon.p_timer_counter).to_string_all())
            return HttpResponse(u"系统异常,请稍候再试")

    @staticmethod
    def preview(module_factory, conf_factory, dbm_factory, params):
        # 1. 通过参数解析配置
        preview_conf = params.get(ModuleCommon.p_preview_conf)
        if not preview_conf:
            return HttpResponse(u"参数错误")
        conf_dict = preview_conf.get(ModuleCommon.k_conf_dict)
        if not conf_dict:
            return HttpResponse(u"参数错误")
        params[ModuleCommon.k_conf_dict] = conf_dict

        path_route = preview_conf.get(ModuleCommon.p_path_route)
        if not path_route:
            return HttpResponse(u"参数错误")
        params[ModuleCommon.p_path_route] = path_route
        params["db_id"] = preview_conf.get("db_id")
        params["baike_id"] = preview_conf.get("baike_id")
        params["section"] = preview_conf.get("section")
        # 2. 跟view调用一致
        try:
            html_render = module_factory.base_loader.loader(module_factory, params)
            http_response = HttpResponse()
            html = module_factory.base_render.render(params.get(ModuleCommon.k_request), html_render)
            http_response.write(html)
            return http_response
        except Exception as info:
            return HttpResponse(u"参数错误")
