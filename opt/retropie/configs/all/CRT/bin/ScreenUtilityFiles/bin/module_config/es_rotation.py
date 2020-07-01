#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
EmulationStation rotation module

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

import sys, os, time, logging
import filecmp

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import ES_CFG_PATH, ES_PATH, CRT_ES_CONFIGS_PATH, \
                                       CRT_ES_RES_PATH, ROTMODES_TATE1_FILE, \
                                       ROTMODES_TATE3_FILE, RETROPIE_SPLASH_PATH, \
                                       RETROPIE_CFG_PATH, CRT_UTILITY_FILE, \
                                       ES_THEMES_SEC_PATH, ES_THEMES_PRI_PATH, \
                                       CRT_LNCH_IMG_ROT_PATH
from launcher_module.file_helpers import ini_get, touch_file, \
                                         get_xml_value_esconfig, \
                                         set_xml_value_esconfig, \
                                         ini_set
from launcher_module.utils import get_side

ESSYSTEMS_TEMP_FILE = os.path.join(ES_CFG_PATH, "es_systems.cfg")
ESSYSTEMS_VERT_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "vertical_es_systems.cfg")
ESTHEMES_DIS_PATH = os.path.join(ES_PATH, "disabled.themes")

THEME_LIST = []

INTRO_VID_DEF_FILE = os.path.join(RETROPIE_SPLASH_PATH, "CRT-Retropie-Load.mp4")
INTRO_VID0_FILE = os.path.join(CRT_ES_RES_PATH, "splash_screen/CRT-Retropie-Load_H.mp4")
INTRO_VID1_FILE = os.path.join(CRT_ES_RES_PATH, "splash_screen/CRT-Retropie-Load_V1.mp4")
INTRO_VID3_FILE = os.path.join(CRT_ES_RES_PATH, "splash_screen/CRT-Retropie-Load_V3.mp4")

class frontend_rotation():
    """ Class for EmulationStation rotation """
    sSystem50 = "system50"
    sSystem60 = "system60"
    iCurSide = 0
    RES_Y = 0

    def __init__(self):
        self._pre_configure()

    def _pre_configure(self):
        self._check_vertical_themes()

    def rotate(self, p_iToMode = 0):
        self.iCurSide = get_side()
        if not self._check_rotation_mode(p_iToMode): return False
        self._prepare_theme_configuration()
        self._frontend_rotation()
        return True

    def _check_vertical_themes(self):
        VTHEMES_SRC_PATH = os.path.join(CRT_ES_RES_PATH, "themes")
        for item in os.listdir(VTHEMES_SRC_PATH):
            if os.path.isdir(os.path.join(VTHEMES_SRC_PATH, item)):
                THEME_LIST.append("themes/%s" % item)

    def _check_rotation_mode(self, p_iToMode):
        """ Check if argument is valid """
        if not p_iToMode in (-90, 0, 90):
            return False
        logging.info("INFO: Rotate Emulationstation %s" % p_iToMode)
        self.iToMode = p_iToMode
        return True

    def _prepare_theme_configuration(self):
        self._save_current_theme()
        self._set_new_theme()

    def _save_current_theme(self):
        # identify element theme to find in CRT config
        p_sIni = "h_theme"
        if self.iCurSide != 0:
            p_sIni = "v_theme"
        # get current saved theme for current side
        p_sTheme = ini_get(CRT_UTILITY_FILE, p_sIni)
        p_sCurTheme = get_xml_value_esconfig("ThemeSet")
        if p_sTheme != p_sCurTheme:
            ini_set(CRT_UTILITY_FILE, p_sIni, p_sCurTheme)

    def _set_new_theme(self):
        """
        Identify saved theme for next orientation in utility.cfg
        If theme not found, default ones will be applied.
        """
        #p_sTheme = None

        p_sIni = "h_theme"
        if self.iToMode != 0:
            p_sIni = "v_theme"
        p_sTheme = ini_get(CRT_UTILITY_FILE, p_sIni)

        """ If theme was not found then apply by default """
        # by default vertical theme
        if self.iToMode != 0 and not p_sTheme:
            p_sTheme = "VCRT-UniFlyered-Dark"
        # by default horizontal theme
        elif self.iToMode == 0 and not p_sTheme:
            p_sTheme = "CRT-UniFlyered-Color"
        # no change if current configuration is the same
        if p_sTheme != get_xml_value_esconfig("ThemeSet"):
            set_xml_value_esconfig("ThemeSet", p_sTheme)

    def _replace_launching_image(self, p_sImage, p_sFileTail):
        p_sMask = p_sFileTail + p_sImage[-4:]
        if not p_sMask in p_sImage:
            return
        image_cur = RETROPIE_CFG_PATH + "/" + p_sImage.replace(p_sFileTail, "")
        sImageSet = CRT_LNCH_IMG_ROT_PATH + "/" + p_sImage
        if not os.path.exists(image_cur):
            path = os.path.dirname(p_sImage)
            img = os.path.basename(p_sImage)
            img = "dis_" + img.replace(p_sFileTail, "")
            imgpth = os.path.join(RETROPIE_CFG_PATH, path, img )
            if os.path.exists(imgpth): image_cur = imgpth
            logging.info("INFO: rotating image: %s" % imgpth)
        try:
            if not filecmp.cmp(image_cur, sImageSet):
                os.system('cp "%s" "%s"' % (sImageSet, image_cur))
        except:
            pass

    def _rotate_launching_images(self, p_sFileTail):
        for Level1 in os.listdir(CRT_LNCH_IMG_ROT_PATH):
            LEVEL1 = os.path.join(CRT_LNCH_IMG_ROT_PATH, Level1)
            if os.path.isdir(LEVEL1):
                for Level2 in os.listdir(LEVEL1):
                    LEVEL2 = os.path.join(LEVEL1, Level2)
                    sFile2 = os.path.join(Level1, Level2)
                    if os.path.isfile(LEVEL2):
                        self._replace_launching_image(sFile2, p_sFileTail)

    def _frontend_rotation(self):
        p_sIntro = None

        if self.iToMode == 0:
            p_sFileTail = "_0"
            p_sIntro = INTRO_VID0_FILE
            p_sTrMode = None
            os.system('sudo rm %s >> /dev/null 2>&1' % ESSYSTEMS_TEMP_FILE)
            os.system('sudo mv %s %s >> /dev/null 2>&1' % (ESTHEMES_DIS_PATH, ES_THEMES_PRI_PATH))
            for theme in THEME_LIST:
                VTHEMES_DST_PATH = os.path.join(ES_CFG_PATH, theme)
                os.system('sudo rm -R %s >> /dev/null 2>&1' % VTHEMES_DST_PATH)
        else:
            if not os.path.exists(ES_THEMES_SEC_PATH):
                os.system('mkdir %s >> /dev/null 2>&1' % ES_THEMES_SEC_PATH)
            os.system('cp %s %s >> /dev/null 2>&1' % (ESSYSTEMS_VERT_FILE, ESSYSTEMS_TEMP_FILE))
            os.system('sudo mv %s %s >> /dev/null 2>&1' % (ES_THEMES_PRI_PATH, ESTHEMES_DIS_PATH))
            for theme in THEME_LIST:
                VTHEMES_SRC_PATH = os.path.join(CRT_ES_RES_PATH, theme)
                os.system('cp -R %s %s >> /dev/null 2>&1' % (VTHEMES_SRC_PATH, ES_THEMES_SEC_PATH))

            if self.iToMode == 90:
                p_sFileTail = "_1"
                p_sIntro = INTRO_VID1_FILE
                p_sTrMode = ROTMODES_TATE1_FILE
            elif self.iToMode == -90:
                p_sFileTail = "_3"
                p_sIntro = INTRO_VID3_FILE
                p_sTrMode = ROTMODES_TATE3_FILE

        self._set_side_mode(p_sTrMode)
        # change video intro
        os.system('sudo cp %s %s >> /dev/null 2>&1' % (p_sIntro, INTRO_VID_DEF_FILE))
        # change launching images
        self._rotate_launching_images(p_sFileTail)

    def _set_side_mode(self, p_sTrMode):
        """ Clean all side file triggers and create new """
        os.system('rm %s >> /dev/null 2>&1' % ROTMODES_TATE1_FILE)
        os.system('rm %s >> /dev/null 2>&1' % ROTMODES_TATE3_FILE)
        if p_sTrMode:
            touch_file(p_sTrMode)
