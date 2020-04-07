#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Resolution change module

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2020 -krahs- - https://github.com/krahsdevil/

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 2 of the License, or (at your option) any
later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys, os, time, re
import filecmp

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from module_screen_center_utility.pattern_launcher import center
from launcher_module.core_paths import *
from launcher_module.file_helpers import modify_line, ini_get, \
                                         get_xml_value_esconfig, \
                                         set_xml_value_esconfig
from launcher_module.utils import check_process, show_info, menu_options, HideScreen

CRTICONS_PATH = os.path.join(CRT_ROOT_PATH, "config/icons")
CRTICONS_VERTICAL_PATH = os.path.join(CRT_ES_VERT_MENU, "icons")

INTRO_VID_DEF_FILE = os.path.join(RETROPIE_SPLASH_PATH, "CRT-Retropie-Load.mp4")
INTRO_VID0_FILE = os.path.join(CRT_ES_RES_PATH, "splash_screen/CRT-Retropie-Load_H.mp4")
INTRO_VID1_FILE = os.path.join(CRT_ES_RES_PATH, "splash_screen/CRT-Retropie-Load_V1.mp4")
INTRO_VID3_FILE = os.path.join(CRT_ES_RES_PATH, "splash_screen/CRT-Retropie-Load_V3.mp4")

class resolution_change():
    """ Class for EmulationStation rotation """
    sCurTheme = ""
    iToRes = 0
    sTailSideV = "p_theme_vertical"
    sTailSideH = "p_theme_horizontal"
    sSystem50 = "system50"
    sSystem60 = "system60"
    iCurSide = 0
    bRestart = False
    RES_Y = 0
    
    def __init__(self, p_iToRes = "none", p_bRestart = True):
        self.bRestart = p_bRestart
        self._check_resolution_mode(p_iToRes)
        self._pre_configure()

    def _pre_configure(self):
        self._check_current_base_res()
        self._check_current_es_side()

    def change(self):
        show_info("WAIT, PREPARING RESOLUTION CHANGE")
        self._prepare_save_configuration()
        self._change_resolution()
        self._apply_resolution()

    def _check_resolution_mode(self, p_iToRes):
        """ Check if argument is valid """
        if type(p_iToRes) == str:
            self.iToRes = int(re.sub('[a-zA-Z]+', '', p_iToRes))
        if self.iToRes not in (240, 270):
            sys.exit(0)
        
    def _prepare_save_configuration(self):
        self._save_current_theme()
        self._set_new_theme()
        self._save_new_resolution()

    def _check_current_base_res(self):
        p_sRes = ini_get(CRT_UTILITY_FILE, "default")
        if p_sRes == self.sSystem50: self.RES_Y = 270
        elif p_sRes == self.sSystem60: self.RES_Y = 240

    def _check_current_es_side(self):
        """ Check current side of EmulatioStation """
        self.iCurSide = 0
        if os.path.exists(ROTMODES_TATE1_FILE):
            self.iCurSide = 1
        elif os.path.exists(ROTMODES_TATE3_FILE):
            self.iCurSide = 3

    def _save_current_theme(self):
        # identify element theme to find in CRT config
        p_sElement = str(self.RES_Y) + self.sTailSideH
        if self.iCurSide != 0:
            p_sElement = str(self.RES_Y) + self.sTailSideV
        # get current saved theme for current side
        p_sTheme = ini_get(CRT_UTILITY_FILE, p_sElement)
        self.sCurTheme = get_xml_value_esconfig("ThemeSet")
        if p_sTheme != self.sCurTheme:
            modify_line(CRT_UTILITY_FILE, p_sElement, 
                        "%s %s" % (p_sElement, self.sCurTheme))
       
    def _set_new_theme(self):
        """ 
        Identify saved theme for next orientation in utility.cfg
        If theme not found, default ones will be applied.        
        """
        p_sTheme = None
        p_sTail = self.sTailSideH

        if self.iCurSide != 0:
            p_sTail = self.sTailSideV
        p_sIniTheme = str(self.iToRes) + p_sTail
        p_sTheme = ini_get(CRT_UTILITY_FILE, p_sIniTheme)

        """ If theme was not found then apply by default """
        # by default vertical theme
        if self.iCurSide != 0 and not p_sTheme:
            if self.RES_Y == 270: p_sTheme = "V270P-CRT-BASE"
            elif self.RES_Y == 240: p_sTheme = "V270P-CRT-BASE"
            else: p_sTheme = "V270P-CRT-BASE"
        # by default horizontal theme        
        elif self.iCurSide == 0 and not p_sTheme:
            if self.RES_Y == 270: p_sTheme = "270P-CRT-SNES-MINI"
            elif self.RES_Y == 240: p_sTheme = "240P-CRT-BUBBLEGUM"
            else: p_sTheme = "270P-CRT-BASE"
        # no change if current configuration is the same
        if p_sTheme != get_xml_value_esconfig("ThemeSet"):
            set_xml_value_esconfig("ThemeSet", p_sTheme)

    def _save_new_resolution(self):
        if self.iToRes == 240:
            modify_line(CRT_UTILITY_FILE, "default",
                        "default %s" % self.sSystem60)
        elif self.iToRes == 270:
            modify_line(CRT_UTILITY_FILE, "default",
                        "default %s" % self.sSystem50)

    def _replace_launching_image(self, p_sImage, p_sSrcPath, p_sSetPath):
        p_lMask = (".png", ".jpg")
        if not p_sImage[-4:] in p_lMask:
            return
        image_cur = p_sSrcPath + "/" + p_sImage
        sImageSetA = p_sSetPath + "/" + p_sImage[:-4] + "_240p.png"
        sImageSetB = p_sSetPath + "/" + p_sImage[:-4] + "_270p.png"
        # if 240p is the chosen resolution, images are changed
        if self.iToRes == 240:
            sImageSetA = sImageSetA[:-9] + "_270p.png"
            sImageSetB = sImageSetB[:-9] + "_240p.png"
        try:
            if filecmp.cmp(image_cur, sImageSetA):
                os.system('cp "%s" "%s"' % (sImageSetB, image_cur))
        except:
            pass

    def _fix_aspect_ratio_images(self):
        for Level1 in os.listdir(RETROPIE_CFG_PATH):
            LEVEL1 = os.path.join(RETROPIE_CFG_PATH, Level1)
            if os.path.isdir(LEVEL1):
                for Level2 in os.listdir(LEVEL1):
                    LEVEL2 = os.path.join(LEVEL1, Level2)
                    sFile2 = os.path.join(Level1, Level2)
                    if os.path.isdir(LEVEL2):
                        for Level3 in os.listdir(LEVEL2):
                            LEVEL3 = os.path.join(LEVEL2, Level3)
                            sFile3 = os.path.join(Level1, Level2, Level3)
                            if os.path.isdir(LEVEL3):
                                for Level4 in os.listdir(LEVEL3):
                                    LEVEL4 = os.path.join(LEVEL3, Level4)
                                    sFile4 = os.path.join(Level1, Level2, Level3, Level4)
                                    if os.path.isfile(LEVEL4):
                                        self._replace_launching_image(sFile4, RETROPIE_CFG_PATH,  CRT_LNCH_IMG_MOD_PATH)
                            else:
                                self._replace_launching_image(sFile3, RETROPIE_CFG_PATH, CRT_LNCH_IMG_MOD_PATH)
                    else:
                        self._replace_launching_image(sFile2, RETROPIE_CFG_PATH, CRT_LNCH_IMG_MOD_PATH)

    def _fix_icons_image(self):
        for file in os.listdir(CRTICONS_PATH):
            self._replace_launching_image(file, CRTICONS_PATH, CRT_ICONS_SET_PATH)
        for file in os.listdir(CRTICONS_VERTICAL_PATH):
            self._replace_launching_image(file, CRTICONS_VERTICAL_PATH, CRT_ICONS_SET_PATH)

    def _change_resolution(self):
        self._fix_aspect_ratio_images()
        self._fix_icons_image()

    def _apply_resolution(self):
        commandline = None
        oApplyRes = center()
        oApplyRes.launch("force")
    
    # clean system
    def __clean(self):
        pass

if __name__ == '__main__':
    m_sTitRes = "CHANGE SYSTEM RESOLUTION" # title for selector
    m_lOptRes = [("240p (320x240@60Hz)", "240p"),
                 ("270p (450x270@50Hz)", "270p"),
                 ("CANCEL", "CANCEL")] # options for selector
    sChoice = menu_options(m_lOptRes, m_sTitRes)
    if sChoice != "CANCEL":
        HideScreen()
        oChangeRes = resolution_change(sChoice)
        oChangeRes.change()
    sys.exit(0)
