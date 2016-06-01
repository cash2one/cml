#!/usr/bin/env python
#-*- coding:utf-8 -*-
from common.cml.modules.module_import import *
from sitegeek.settings import DEBUG_LOGGER
from common.libs.factory import DictFactory

def retrieve():
    return "I'm retrieve"

parameters = DictFactory()
parameters.register("retrieve", retrieve)

class ModuleFactory(object):
    def __init__(self):
        self.module = {}

    def register(self, module_ins):
        if module_ins.module_key in self.module:
            raise KeyError("module [%s] exists" % module_ins.module_key)

        if module_ins.module_key.startswith("pl."):
            raise Exception("module_key [%s] can not startswith(\"pl.\")" % module_ins.module_key)

        self.module[module_ins.module_key] = module_ins
        DEBUG_LOGGER.debug("register module[%s] success" % module_ins.module_key)

    def get_module(self, module_key):
        return self.module.get(module_key)

    def __getitem__(self, key):
        if key not in self.module:
            raise KeyError("module [%s] does not exists" % key)
        return self.module[key]

    def __getattr__(self, key):
        return self[key]

    def size(self):
        return len(self.module)

module_factory = ModuleFactory()
module_factory.register(ModuleCsrf(parameters))
# # 必须注册的三个方法
# module_factory.register(ModuleLoader(Luna, LunaSQL))
# module_factory.register(ModuleRender)
# module_factory.register(ModuleView)
#
# 常用左右闭合
# module_factory.register(ModulePlaceHolder(Luna, LunaSQL))
#
# # common module
# module_factory.register(ModuleTdk(Luna, LunaSQL))
# module_factory.register(ModuleCsrf(Luna, LunaSQL))
# module_factory.register(ModuleReport(Luna, LunaSQL))
# module_factory.register(ModuleVersion(Luna, LunaSQL))
#
# # pc common module
# module_factory.register(ModuleMeta(Luna, LunaSQL))
# module_factory.register(ModuleCss(Luna, LunaSQL))
# module_factory.register(ModuleJs(Luna, LunaSQL))
# module_factory.register(ModuleFooterJs(Luna, LunaSQL))
# module_factory.register(ModuleFooter(Luna, LunaSQL))
# module_factory.register(ModuleNav(Luna, LunaSQL))
# module_factory.register(ModuleDemandHelp(Luna, LunaSQL))
#
# # msite common module
# module_factory.register(ModuleMetaMsite(Luna, LunaSQL))
# module_factory.register(ModuleCssMsite(Luna, LunaSQL))
# module_factory.register(ModuleJsMsite(Luna, LunaSQL))
# module_factory.register(ModuleFooterJsMsite(Luna, LunaSQL))
# module_factory.register(ModuleFooterMsite(Luna, LunaSQL))
# module_factory.register(ModuleNavMsite(Luna, LunaSQL))
# module_factory.register(ModuleDemandHelpMsite(Luna, LunaSQL))
#
# # list
# module_factory.register(ModuleList(Luna, LunaSQL))
# module_factory.register(ModuleListMusic(Luna, LunaSQL))
# module_factory.register(ModuleListMusicMsite(Luna, LunaSQL))
# module_factory.register(ModuleListVideo(Luna, LunaSQL))
# module_factory.register(ModuleListVideoMsite(Luna, LunaSQL))
# module_factory.register(ModuleListMsite(Luna, LunaSQL))
# module_factory.register(ModuleListAjax(Luna, LunaSQL))
#
# # detai
# module_factory.register(ModuleDetail(Luna, LunaSQL))
# module_factory.register(ModuleDetailMsite(Luna, LunaSQL))
#
# # bread
# module_factory.register(ModuleBread(Luna, LunaSQL))
# module_factory.register(ModuleBreadNoSearch(Luna, LunaSQL))
# module_factory.register(ModuleBreadMsite(Luna, LunaSQL))
# module_factory.register(ModuleBreadButtonMsite(Luna, LunaSQL))
#
# # banner
# module_factory.register(ModuleLongBanner(Luna, LunaSQL))
# module_factory.register(ModuleSlideBanner(Luna, LunaSQL))
# module_factory.register(ModuleSlideBannerMsite(Luna, LunaSQL))
# module_factory.register(ModuleImageInfoBanner(Luna, LunaSQL))
# module_factory.register(ModuleFullBanner(Luna, LunaSQL))
# module_factory.register(ModuleFullBannerMsite(Luna, LunaSQL))
#
# # course
# module_factory.register(ModuleCourse(Luna, LunaSQL))
# module_factory.register(ModuleCourseDetail(Luna, LunaSQL))
# module_factory.register(ModuleCoursePanel(Luna, LunaSQL))
# module_factory.register(ModuleCourseMsite(Luna, LunaSQL))
# module_factory.register(ModuleCourseDetailMsite(Luna, LunaSQL))
# module_factory.register(ModuleCourseBigImgMsite(Luna, LunaSQL))
# module_factory.register(ModuleAdsImg(Luna, LunaSQL))
#
# # panel
# module_factory.register(ModuleRightPanelStyleOne(Luna, LunaSQL))
# module_factory.register(ModuleRightPanelStyleTwo(Luna, LunaSQL))
# module_factory.register(ModuleRightPanelStyleThree(Luna, LunaSQL))
# module_factory.register(ModuleTabNewsPanel(Luna, LunaSQL))
# module_factory.register(ModuleWenDaPanel(Luna, LunaSQL))
# module_factory.register(ModuleVideoPanel(Luna, LunaSQL))
# module_factory.register(ModuleHotSearchPanel(Luna, LunaSQL))
# module_factory.register(ModuleHotSearchPanelTwo(Luna, LunaSQL))
# module_factory.register(ModuleHotSearchPanelThree(Luna, LunaSQL))
# module_factory.register(ModuleHotSearchPanelThreeMsite(Luna, LunaSQL))
# module_factory.register(ModuleListPanelMsite(Luna, LunaSQL))
# module_factory.register(ModuleTopicPanel(Luna, LunaSQL))
# module_factory.register(ModuleTopicPanelMsite(Luna, LunaSQL))
#
# module_factory.register(ModuleContentPanelBase(Luna, LunaSQL))
# module_factory.register(ModuleContentPanelBaseMsite(Luna, LunaSQL))
# module_factory.register(ModuleContentPanelThree(Luna, LunaSQL))
# module_factory.register(ModuleContentPanelThreeTwo(Luna, LunaSQL))
#
# # nav-tabs
# module_factory.register(ModuleNavTabsMsite(Luna, LunaSQL))
# module_factory.register(ModuleNavTabsJitaMsite(Luna, LunaSQL))
# module_factory.register(ModuleNavTabsButtonMsite(Luna, LunaSQL))
#
# # jita
# module_factory.register(ModuleGuitarDetail(Luna, LunaSQL))
# module_factory.register(ModuleGuitarDetailMsite(Luna, LunaSQL))
# module_factory.register(ModuleGuitarHot(Luna, LunaSQL))
# module_factory.register(ModuleGuitarHotMsite(Luna, LunaSQL))
# module_factory.register(ModuleGuitarFindTeacher(Luna, LunaSQL))
# module_factory.register(ModuleGuitarFindTeacherMsite(Luna, LunaSQL))
# module_factory.register(ModuleGuitarGeci(Luna, LunaSQL))
#
# # yasi
# module_factory.register(ModuleYasiBaike(Luna, LunaSQL))
# module_factory.register(ModuleYasiBaikeTwo(Luna, LunaSQL))
# module_factory.register(ModuleYasiBaikeDetail(Luna, LunaSQL))
# module_factory.register(ModuleYasiBaikeDetailMsite(Luna, LunaSQL))
# module_factory.register(ModuleYasiStudyPlan(Luna, LunaSQL))
# module_factory.register(ModuleYasiHome(Luna, LunaSQL))
# module_factory.register(ModuleYasiCalendar(Luna, LunaSQL))
# module_factory.register(ModuleYasiCalendar2(Luna, LunaSQL))
# module_factory.register(ModuleYasiFooterBannerMsite(Luna, LunaSQL))
#
# # recommend
# module_factory.register(ModuleRecommendPanel(Luna, LunaSQL))
# module_factory.register(ModuleRecommendPanelMsite(Luna, LunaSQL))
# module_factory.register(ModuleRecommendPanelTwoMsite(Luna, LunaSQL))
# module_factory.register(ModuleHotPanel(Luna, LunaSQL))
# module_factory.register(ModuleHotPanelTwo(Luna, LunaSQL))
# module_factory.register(ModuleHotPanelTwoMsite(Luna, LunaSQL))
#
# # home
# module_factory.register(ModuleHome(Luna, LunaSQL))
#
# # search
# module_factory.register(ModuleSearch(Luna, LunaSQL))
# module_factory.register(ModuleSearchMsite(Luna, LunaSQL))
#
# # hidden
# module_factory.register(ModuleHiddenJitaHomeMsite(Luna, LunaSQL))
# module_factory.register(ModuleHiddenPianoHomeMsite(Luna, LunaSQL))
# module_factory.register(ModuleHiddenForSearchPanel(Luna, LunaSQL))
#
# # admin
# module_factory.register(ModulLogin(Luna, LunaSQL))
# module_factory.register(ModulAdminNav(Luna, LunaSQL))
# module_factory.register(ModulAdminLeftNav(Luna, LunaSQL))
# module_factory.register(ModulAdminVersion(Luna, LunaSQL))
# module_factory.register(ModulAdminOnline(Luna, LunaSQL))
# module_factory.register(ModulAdminApplyOnline(Luna, LunaSQL))
# module_factory.register(ModulAdminAuthOnline(Luna, LunaSQL))
# module_factory.register(ModulAdminAddUser(Luna, LunaSQL))
# module_factory.register(ModulAdminPassword(Luna, LunaSQL))
# module_factory.register(ModulAdminAddConf(Luna, LunaSQL))
# module_factory.register(ModulAdminEdit(Luna, LunaSQL))
# module_factory.register(ModulAdminReadme(Luna, LunaSQL))
# module_factory.register(ModuleAdminKeywordsAdd(Luna, LunaSQL))
# module_factory.register(ModuleAdminKeywordsEdit(Luna, LunaSQL))
# module_factory.register(ModuleAdminCmsEdit(Luna, LunaSQL))

DEBUG_LOGGER.info("module.size = [%s]" % module_factory.size())
