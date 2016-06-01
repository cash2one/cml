#!/usr/bin/env python
#-*- coding:utf-8 -*-

# public module
from common.module_loader import ModuleLoader
from common.module_loader import ModuleRender
from common.module_loader import ModuleView

# common module
from common.module import ModulePlaceHolder
from common.module import ModuleCsrf
from common.module import ModuleTdk
from common.module import ModuleReport
from common.module import ModuleVersion

# pc common module
from common.module import ModuleMeta
from common.module import ModuleJs
from common.module import ModuleFooterJs
from common.module import ModuleCss
from common.module import ModuleFooter
from common.module import ModuleNav
from common.module import ModuleDemandHelp

# msite common module
from common.module import ModuleMetaMsite
from common.module import ModuleJsMsite
from common.module import ModuleFooterJsMsite
from common.module import ModuleCssMsite
from common.module import ModuleFooterMsite
from common.module import ModuleNavMsite
from common.module import ModuleDemandHelpMsite

# list
from article_list.module import ModuleList
from article_list.module import ModuleListMusic
from article_list.module import ModuleListMusicMsite
from article_list.module import ModuleListVideo
from article_list.module import ModuleListVideoMsite
from article_list.module import ModuleListMsite
from article_list.module import ModuleListAjax

# detail
from detail.module import ModuleDetail
from detail.module import ModuleDetailMsite

# bread
from bread.module import ModuleBread
from bread.module import ModuleBreadNoSearch
from bread.module import ModuleBreadMsite
from bread.module import ModuleBreadButtonMsite

# banner
from banner.module import ModuleLongBanner
from banner.module import ModuleSlideBanner
from banner.module import ModuleSlideBannerMsite
from banner.module import ModuleImageInfoBanner
from banner.module import ModuleFullBanner
from banner.module import ModuleFullBannerMsite

# course
from course.module import ModuleCourse
from course.module import ModuleCourseDetail
from course.module import ModuleCoursePanel
from course.module import ModuleCourseMsite
from course.module import ModuleCourseDetailMsite
from course.module import ModuleCourseBigImgMsite
from course.module import ModuleAdsImg

# panel
from panel.module import ModuleRightPanelStyleOne
from panel.module import ModuleRightPanelStyleTwo
from panel.module import ModuleRightPanelStyleThree
from panel.module import ModuleTabNewsPanel
from panel.module import ModuleWenDaPanel
from panel.module import ModuleVideoPanel
from panel.module import ModuleHotSearchPanel
from panel.module import ModuleHotSearchPanelTwo
from panel.module import ModuleHotSearchPanelThree
from panel.module import ModuleHotSearchPanelThreeMsite
from panel.module import ModuleListPanelMsite
from panel.module import ModuleTopicPanel
from panel.module import ModuleTopicPanelMsite
from panel.module import ModuleTopicDirectPanel
from panel.module import ModuleFreeRichTextAreaPanel
from panel.module import ModuleFreeRichTextAreaPanelMsite

from content_panel.module import ModuleContentPanelBase
from content_panel.module import ModuleContentPanelBaseMsite
from content_panel.module import ModuleContentPanelThree
from content_panel.module import ModuleContentPanelThreeTwo

# nav-tabs
# msite
from nav.module import ModuleNavTabsMsite
from nav.module import ModuleNavTabsJitaMsite
from nav.module import ModuleNavTabsButtonMsite

# jita
from jita.module import ModuleGuitarDetail
from jita.module import ModuleGuitarDetailMsite
from jita.module import ModuleGuitarHot
from jita.module import ModuleGuitarHotMsite
from jita.module import ModuleGuitarFindTeacher
from jita.module import ModuleGuitarFindTeacherMsite
from jita.module import ModuleGuitarGeci

# yasi
from yasi.module import ModuleYasiBaike
from yasi.module import ModuleYasiBaikeTwo
from yasi.module import ModuleYasiBaikeDetail
from yasi.module import ModuleYasiBaikeDetailMsite
from yasi.module import ModuleYasiStudyPlan
from yasi.module import ModuleYasiHome
from yasi.module import ModuleYasiCalendar
from yasi.module import ModuleYasiCalendar2
from yasi.module import ModuleYasiFooterBannerMsite

# recommend
from recommend.module import ModuleRecommendPanel
from recommend.module import ModuleRecommendPanelMsite
from recommend.module import ModuleRecommendPanelTwoMsite
from recommend.module import ModuleHotPanel
from recommend.module import ModuleHotPanelTwo
from recommend.module import ModuleHotPanelTwoMsite

# home
from home.module import ModuleHome

# search
from search.module import ModuleSearch
from search.module import ModuleSearchMsite

# hidden
from hidden.module import ModuleHiddenForSearchPanel
from hidden.module import ModuleHiddenJitaHomeMsite
from hidden.module import ModuleHiddenPianoHomeMsite

# admin
from admin.module import ModulLogin
from admin.module import ModulAdminNav
from admin.module import ModulAdminLeftNav
from admin.module import ModulAdminVersion
from admin.module import ModulAdminOnline
from admin.module import ModulAdminApplyOnline
from admin.module import ModulAdminAuthOnline
from admin.module import ModulAdminAddUser
from admin.module import ModulAdminPassword
from admin.module import ModulAdminAddConf
from admin.module import ModulAdminEdit
from admin.module import ModulAdminReadme
from admin.module import ModuleAdminKeywordsAdd
from admin.module import ModuleAdminSubjectAdd
from admin.module import ModuleAdminKeywordsEdit
from admin.module import ModuleAdminSubjectEdit
from admin.module import ModuleAdminCmsEdit

from dota.module import ModuleDotaHeroListMsite
from dota.module import ModuleDotaHeroDetailMsite
