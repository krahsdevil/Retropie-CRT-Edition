#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher arcade.py.

launcher library for retropie, based on original idea - Ironic
  and the retropie integration work by -krahs-

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2019 -krahs- - https://github.com/krahsdevil/
Copyright (C)  2019 dskywalk - http://david.dantoine.org

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

import os, logging, shutil
from launcher_module.core import RETROPIE_PATH, CRTROOT_PATH, TMP_LAUNCHER_PATH
from launcher_module.emulator import emulator
from launcher_module.file_helpers import ini_getlist, add_line, modify_line
from launcher_module.screen import CRT

RC_ADVANCEDMAME_FILE = os.path.join(RETROPIE_PATH, "mame-advmame/advmame.rc")
__ARCADE_PATH = TMP_LAUNCHER_PATH
__ARCADE_FILE = "retroarcharcade.cfg"
CFG_ARCADE_BASE = os.path.join(CRTROOT_PATH, "Retroarch/configs", __ARCADE_FILE)
TMP_ARCADE_FILE = os.path.join(__ARCADE_PATH, __ARCADE_FILE)


DB_MAME037 = os.path.join(CRTROOT_PATH, "Resolutions/mame037b5_games.txt")
DB_MAME078 = os.path.join(CRTROOT_PATH, "Resolutions/mame078_games.txt")
DB_MAME139 = os.path.join(CRTROOT_PATH, "Resolutions/mame0139_games.txt")
DB_FBALPHA = os.path.join(CRTROOT_PATH, "Resolutions/fbalpha_games.txt")
DB_ADVMAME = os.path.join(CRTROOT_PATH, "Resolutions/advmame_games.txt")

class arcade(emulator):
    m_sPathScreenDB = ""
    m_lTimingData = []
    m_dVideo = {}

    cfg_offsetx = 0
    cfg_offsety = 0
    cfg_hres = 0

    def config_generate(self):
        pass

    def screen_prepare(self):
        self.m_sPathScreenDB = DB_MAME078 # mame2003
        if "2000" in self.m_sBinarySelected:
            self.m_sPathScreenDB = DB_MAME037
        elif "2010" in self.m_sBinarySelected:
            self.m_sPathScreenDB = DB_MAME139
        elif "fbalpha" in self.m_sBinarySelected:
            self.m_sPathScreenDB = DB_FBALPHA
        elif "advmame" in self.m_sBinarySelected:
            self.m_sPathScreenDB = DB_ADVMAME

        logging.info("binary: %s | %s" % (self.m_sBinarySelected, self.m_sPathScreenDB))

    def screen_set(self):
        self.m_oCRT = CRT(self.m_sGameName)
        self.m_dVideo = self.m_oCRT.arcade_data(self.m_sPathScreenDB)
        self.config_generate()
        self.m_oCRT.arcade_set()

    def ra_config_generate(self):
        self.cfg_hres = self.m_dVideo["H_Res"]
        if self.m_oCRT.m_sSide_Game != 'V':
            self.ra_config_create()
            return
        if self.m_oCRT.m_iRGame == -90:
            self.m_oCRT.m_sSide_Game = 'H'
            self.cfg_hres = 1220
            self.ra_config_create(p_bSmooth = True)
            self.m_oCRT.timing_set("H_Pos", "130")
        elif (self.m_oCRT.m_iRGame == 0 and self.m_oCRT.m_iRSys != -90) or self.m_oCRT.m_iRSys == 90:
            self.m_oCRT.m_sSide_Game = 'V3'
            self.cfg_offsetx = -10
            if self.m_dVideo["V_Res"] == 240:
                self.cfg_offsety = 4
            self.ra_config_create()
        elif self.m_oCRT.m_iRSys == -90:
            self.m_oCRT.m_sSide_Game = 'V1'
            self.cfg_offsetx = -10
            if self.m_dVideo["V_Res"] == 240:
                self.cfg_offsety = 4
            self.ra_config_create()

    def ra_config_create(self, p_bSmooth = False):
        self.ra_config_write(p_bSmooth)

    def ra_config_write(self, p_bSmooth):
        logging.info("result - w %s, h %s (%s/%s) - %sHz - s[%s] smooth{%s}" % (
            self.cfg_hres,
            self.m_dVideo["V_Res"],
            self.cfg_offsetx,
            self.cfg_offsety,
            self.m_dVideo["R_Rate"],
            self.m_oCRT.m_sSide_Game,
            p_bSmooth
            ))
        # copy cfg base
        shutil.copy2(CFG_ARCADE_BASE, TMP_ARCADE_FILE)
        add_line(TMP_ARCADE_FILE, 'custom_viewport_width = "%s"' % self.cfg_hres)
        add_line(TMP_ARCADE_FILE, 'custom_viewport_height = "%s"' % self.m_dVideo["V_Res"])
        add_line(TMP_ARCADE_FILE, 'custom_viewport_x = "%s"' % self.cfg_offsetx)
        add_line(TMP_ARCADE_FILE, 'custom_viewport_y = "%s"' % self.cfg_offsety)
        add_line(TMP_ARCADE_FILE, 'video_refresh_rate = "%s"' % self.m_dVideo["R_Rate"])

        # smooth vertical games on horizontal screens
        add_line(TMP_ARCADE_FILE, 'video_smooth = "%s"' % str(p_bSmooth).lower())

        # Check orientation
        if self.m_oCRT.m_sSide_Game == "H":
            add_line(TMP_ARCADE_FILE, 'video_rotation = "0"')
        elif self.m_oCRT.m_sSide_Game == "V3":
            add_line(TMP_ARCADE_FILE, 'video_rotation = "3"')
        elif self.m_oCRT.m_sSide_Game == "V1":
            add_line(TMP_ARCADE_FILE, 'video_rotation = "1"')

    def adv_config_generate(self):
        display_ror = "no"
        display_rol = "no"
        if self.m_oCRT.m_sSide_Game == 'V':
            if (self.m_oCRT.m_iRGame == 0 and self.m_oCRT.m_iRSys != -90) or self.m_oCRT.m_iRSys == 90:
                display_ror = "yes"
            elif self.m_oCRT.m_iRSys == -90:
                display_rol = "yes"
        logging.info("INFO: advmame result - ror %s, rol %s - DIR: %s" % (display_ror, display_rol, self.m_sFileDir))

        modify_line(RC_ADVANCEDMAME_FILE, "display_ror ", "display_ror %s" % display_ror)
        modify_line(RC_ADVANCEDMAME_FILE, "display_rol ", "display_rol %s" % display_rol)
        # put the correct game folder
        modify_line(RC_ADVANCEDMAME_FILE, "dir_rom ","dir_rom %s:/home/pi/RetroPie/BIOS" % self.m_sFileDir)
        # after run this options are lost, reenable it
        modify_line(RC_ADVANCEDMAME_FILE, "misc_smp ","misc_smp yes")
        modify_line(RC_ADVANCEDMAME_FILE, "display_vsync ","display_vsync yes")
        modify_line(RC_ADVANCEDMAME_FILE, "misc_safequit ","misc_safequit no")
        modify_line(RC_ADVANCEDMAME_FILE, "misc_quiet ", "misc_quiet yes")
        modify_line(RC_ADVANCEDMAME_FILE, "display_resizeeffect ","display_resizeeffect none")
        modify_line(RC_ADVANCEDMAME_FILE, "display_resize ","display_resize none")
        modify_line(RC_ADVANCEDMAME_FILE, "display_mode ","display_mode generate")
