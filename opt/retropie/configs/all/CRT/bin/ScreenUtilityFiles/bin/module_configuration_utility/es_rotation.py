#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Configuration Utility

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

import sys, os, time
import filecmp

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import *
from launcher_module.file_helpers import modify_line, ini_get, touch_file, \
                                         get_xml_value_esconfig, \
                                         set_xml_value_esconfig
from launcher_module.utils import check_process, show_info

CRT_ES_CONFIGS_PATH = os.path.join(CRT_ES_RES_PATH, "configs")
ROTMODES_TATE1_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-tate1")
ROTMODES_TATE3_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-tate3")
ROTMODES_YOKO_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-yoko")

ESSYSTEMS_TEMP_FILE = os.path.join(ES_CFG_PATH, "es_systems.cfg")
ESSYSTEMS_VERT_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "vertical_es_systems.cfg")
ESTHEMES_DIS_PATH = os.path.join(ES_PATH, "disabled.themes")
VTHEME270_DST_PATH = os.path.join(ES_CFG_PATH, "themes/V270P-CRT-BASE")
VTHEME270_SRC_PATH = os.path.join(CRT_ES_RES_PATH, "themes/V270P-CRT-BASE")

INTRO_VID_DEF_FILE = os.path.join(RETROPIE_SPLASH_PATH, "CRT-Retropie-Load.mp4")
INTRO_VID0_FILE = os.path.join(CRT_ES_RES_PATH, "splash_screen/CRT-Retropie-Load_H.mp4")
INTRO_VID1_FILE = os.path.join(CRT_ES_RES_PATH, "splash_screen/CRT-Retropie-Load_V1.mp4")
INTRO_VID3_FILE = os.path.join(CRT_ES_RES_PATH, "splash_screen/CRT-Retropie-Load_V3.mp4")

class frontend_rotation():
    """ Class for EmulationStation rotation """
    sCurTheme = ""
    iToMode = ""
    sTailSideV = "p_theme_vertical"
    sTailSideH = "p_theme_horizontal"
    sSystem50 = "system50"
    sSystem60 = "system60"
    iCurSide = 0
    bRestart = False
    RES_Y = 0
    
    def __init__(self, p_iToMode = 0, p_bRestart = False):
        self.bRestart = p_bRestart
        self._check_rotation_mode(p_iToMode)
        self._pre_configure()
        self._run()

    def _pre_configure(self):
        self._check_current_base_res()
        self._check_current_es_side()

    def _run(self):
        self._prepare_theme_configuration()
        self._frontend_rotation()
        if self.bRestart: self._restart_es()
        return True

    def _check_rotation_mode(self, p_iToMode):
        """ Check if argument is valid """
        if not p_iToMode in (-90, 0, 90):
            return False
        self.iToMode = p_iToMode
        
    def _prepare_theme_configuration(self):
        self._save_current_theme()
        self._set_new_theme()

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

        if self.iToMode != 0:
            p_sTail = self.sTailSideV
        p_sIniTheme = str(self.RES_Y) + p_sTail
        p_sTheme = ini_get(CRT_UTILITY_FILE, p_sIniTheme)

        """ If theme was not found then apply by default """
        # by default vertical theme
        if self.iToMode != 0 and not p_sTheme:
            if self.RES_Y == 270: p_sTheme = "V270P-CRT-BASE"
            elif self.RES_Y == 240: p_sTheme = "V270P-CRT-BASE"
            else: p_sTheme = "V270P-CRT-BASE"
        # by default horizontal theme        
        elif self.iToMode == 0 and not p_sTheme:
            if self.RES_Y == 270: p_sTheme = "270P-CRT-SNES-MINI"
            elif self.RES_Y == 240: p_sTheme = "240P-CRT-BUBBLEGUM"
            else: p_sTheme = "270P-CRT-BASE"
        # no change if current configuration is the same
        if p_sTheme != get_xml_value_esconfig("ThemeSet"):
            set_xml_value_esconfig("ThemeSet", p_sTheme)

    def _replace_launching_image(self, p_sImage, p_sFileTail):
        p_sMask = p_sFileTail + p_sImage[-4:]
        if not p_sMask in p_sImage:
            return
        image_cur = RETROPIE_CFG_PATH + "/" + p_sImage.replace(p_sFileTail, "")
        sImageSet = CRT_LNCH_IMG_ROT_PATH + "/" + p_sImage
        try:
            if not filecmp.cmp(image_cur, sImageSet):
                os.system('cp "%s" "%s"' % (sImageSet, image_cur))
        except:
            pass

    def _fix_aspect_ratio_images(self, p_sFileTail):
        for Level1 in os.listdir(CRT_LNCH_IMG_ROT_PATH):
            LEVEL1 = os.path.join(CRT_LNCH_IMG_ROT_PATH, Level1)
            if os.path.isdir(LEVEL1):
                for Level2 in os.listdir(LEVEL1):
                    LEVEL2 = os.path.join(LEVEL1, Level2)
                    sFile2 = os.path.join(Level1, Level2)
                    if os.path.isfile(LEVEL2):
                        self._replace_launching_image(sFile2, p_sFileTail)

    def _frontend_rotation(self):
        if not self.iCurSide: show_info("WAIT, PREPARING ROTATION...")
        # remove first all trigger files
        self.__clean()
        p_sFileTail = "_" + str(self.RES_Y) + "p"
        p_sTheme = None
        p_sIntro = None

        if self.iToMode == 0:
            p_sFileTail += "_0"
            p_sIntro = INTRO_VID0_FILE
            touch_file(ROTMODES_YOKO_FILE)
            os.system('sudo rm %s >> /dev/null 2>&1' % ESSYSTEMS_TEMP_FILE)
            os.system('sudo mv %s %s >> /dev/null 2>&1' % (ESTHEMES_DIS_PATH, ES_THEMES_PRI_PATH))
            os.system('sudo rm -R %s >> /dev/null 2>&1' % VTHEME270_DST_PATH)
        else:
            if not os.path.exists(ES_THEMES_SEC_PATH):
                os.system('mkdir %s >> /dev/null 2>&1' % ES_THEMES_SEC_PATH)
            os.system('cp %s %s >> /dev/null 2>&1' % (ESSYSTEMS_VERT_FILE, ESSYSTEMS_TEMP_FILE))
            os.system('sudo mv %s %s >> /dev/null 2>&1' % (ES_THEMES_PRI_PATH, ESTHEMES_DIS_PATH))
            os.system('cp -R %s %s >> /dev/null 2>&1' % (VTHEME270_SRC_PATH, ES_THEMES_SEC_PATH))
            
            if self.iToMode == 90:
                p_sFileTail += "_1"
                p_sIntro = INTRO_VID1_FILE
                touch_file(ROTMODES_TATE1_FILE)
            elif self.iToMode == -90:
                p_sFileTail += "_3"
                p_sIntro = INTRO_VID3_FILE
                touch_file(ROTMODES_TATE3_FILE)

        modify_line(CRT_UTILITY_FILE, 'frontend_rotation', 'frontend_rotation %s' % self.iToMode)
        os.system('sudo cp %s %s >> /dev/null 2>&1' % (p_sIntro, INTRO_VID_DEF_FILE))
        self._fix_aspect_ratio_images(p_sFileTail)

    def _restart_es(self):
        if check_process("emulationstatio"):
            commandline = "touch /tmp/es-restart "
            commandline += "&& pkill -f \"/opt/retropie"
            commandline += "/supplementary/.*/emulationstation([^.]|$)\""
            if not self.iCurSide: show_info("EMULATIONSTATION WILL RESTART NOW")
            os.system(commandline)
            time.sleep(2)
            sys.exit(1)
    
    # clean system
    def __clean(self):
        """ Clean all side file triggers """
        os.system('rm %s >> /dev/null 2>&1' % ROTMODES_TATE1_FILE)
        os.system('rm %s >> /dev/null 2>&1' % ROTMODES_TATE3_FILE)
        os.system('rm %s >> /dev/null 2>&1' % ROTMODES_YOKO_FILE)
