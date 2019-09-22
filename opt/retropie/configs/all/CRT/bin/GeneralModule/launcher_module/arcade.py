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

import os, logging, shutil, math
from launcher_module.core import RETROPIECFG_PATH, CRTROOT_PATH, TMP_LAUNCHER_PATH
from launcher_module.core_choices_dynamic import choices
from launcher_module.emulator import emulator
from launcher_module.file_helpers import add_line, modify_line
from launcher_module.screen import CRT

RC_ADVANCEDMAME_FILE = os.path.join(RETROPIECFG_PATH, "mame-advmame/advmame.rc")
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
    cfg_vres = 0
    cfg_scaleint = "false"
    cfg_ghres = 0 #Real Horizontal Resolution of the game

    def start(self):
        self.get_screen_res_ready()
        self.config_generate()
        super(arcade, self).start() 

    def config_generate(self):
        pass

    def screen_prepare(self):
        self.m_sPathScreenDB = DB_MAME078 # mame2003
        if "2000" in self.m_sBinarySelected:
            self.m_sPathScreenDB = DB_MAME037
        elif "2010" in self.m_sBinarySelected:
            self.m_sPathScreenDB = DB_MAME139
        elif "fbneo" in self.m_sBinarySelected:
            self.m_sPathScreenDB = DB_FBALPHA
        elif "fbalpha" in self.m_sBinarySelected:
            self.m_sPathScreenDB = DB_FBALPHA
        elif "advmame" in self.m_sBinarySelected:
            self.m_sPathScreenDB = DB_ADVMAME

        logging.info("binary: %s | %s" % (self.m_sBinarySelected, self.m_sPathScreenDB))

    def screen_set(self):
        self.m_oCRT.arcade_set()

    def get_screen_res_ready(self):
        self.m_oCRT = CRT(self.m_sGameName)
        self.m_dVideo = self.m_oCRT.arcade_data(self.m_sPathScreenDB)
        self.arcade_encapsulator()

    def ra_config_generate(self):
        self.cfg_hres = self.m_dVideo["H_Res"]
        self.cfg_vres = self.m_dVideo["V_Res"]
        self.cfg_ghres = self.m_dVideo["Game_H_Res"]
        self.cfg_offsetx = 0
        if self.m_oCRT.m_sSide_Game != 'V':
            self.ra_integer_calculator()
            self.ra_config_create()
            return
        else:
            if self.m_oCRT.m_iRSys != 0:
                if self.m_oCRT.m_iRSys == 90:
                    self.m_oCRT.m_sSide_Game = 'V1'
                elif self.m_oCRT.m_iRSys == -90:
                    self.m_oCRT.m_sSide_Game = 'V3'
                self.ra_config_create()
            else:
                if self.m_oCRT.m_iRGame == -90:
                    self.m_oCRT.m_sSide_Game = 'H'
                    self.cfg_hres = 1120
                    self.cfg_vres = 250
                    self.cfg_offsetx = 400
                    self.cfg_offsety = 0
                    self.ra_config_create(p_bSmooth = True)
                else:
                    self.m_oCRT.m_sSide_Game = 'V1'
                    self.ra_config_create()
                    
    def ra_config_create(self, p_bSmooth = False):
        self.ra_config_write(p_bSmooth)

    def ra_config_write(self, p_bSmooth):
        logging.info("result - w %s, h %s (%s/%s) - scale integer{%s} - %sHz - s[%s] smooth{%s}" % (
            self.cfg_hres,
            self.cfg_vres,
            self.cfg_offsetx,
            self.cfg_offsety,
            self.cfg_scaleint,
            self.m_dVideo["R_Rate"],
            self.m_oCRT.m_sSide_Game,
            p_bSmooth
            ))
        # copy cfg base
        shutil.copy2(CFG_ARCADE_BASE, TMP_ARCADE_FILE)
        add_line(TMP_ARCADE_FILE, 'custom_viewport_width = "%s"' % self.cfg_hres)
        add_line(TMP_ARCADE_FILE, 'custom_viewport_height = "%s"' % self.cfg_vres)
        add_line(TMP_ARCADE_FILE, 'custom_viewport_x = "%s"' % self.cfg_offsetx)
        add_line(TMP_ARCADE_FILE, 'custom_viewport_y = "%s"' % self.cfg_offsety)
        add_line(TMP_ARCADE_FILE, 'video_refresh_rate = "%s"' % self.m_dVideo["R_Rate"])

        # smooth vertical games on horizontal screens
        modify_line(TMP_ARCADE_FILE, "video_smooth", 'video_smooth = "%s"' % str(p_bSmooth).lower())

        # Check orientation
        logging.info("m_sSide_Game %s" % (self.m_oCRT.m_sSide_Game))
        logging.info("m_iRSys %s" % (self.m_oCRT.m_iRSys))
        if self.m_oCRT.m_sSide_Game == "H":
            add_line(TMP_ARCADE_FILE, 'video_rotation = "0"')
        elif self.m_oCRT.m_sSide_Game == "V3":
            add_line(TMP_ARCADE_FILE, 'video_rotation = "1"')
        elif self.m_oCRT.m_sSide_Game == "V1":
            add_line(TMP_ARCADE_FILE, 'video_rotation = "3"')

        # Video Scale Integer activation
        modify_line(TMP_ARCADE_FILE, "video_scale_integer =",
                    'video_scale_integer = "%s"' % self.cfg_scaleint)

    def ra_integer_calculator(self):
        """
        Integer scaling function.
        This function find for the real horizontal size of the game in selected database,
        and must be located just after game side:

        Example:
        gpilots 1920 224 60.000000 -4 -27 3 48 192 240 5 15734 mame078_libretro.so H [304] <- This last
        
        If exist and this option is enabled on config, system will find the exact multiplier for 
        integer scale, just above of hardware horizontal resolution, tipically 1920.
        Image will be oversized a little bit on sides but we can espect better internal performance
        and horizontal pixel perfect.
        If real resolution is found in DB then self.m_dVideo["Game_H_Res"] will be different of '0'.
        """
        if self.cfg_ghres != 0:
            int_multiplier = self.cfg_hres/(self.cfg_ghres*1.0)
            self.cfg_hres = self.cfg_ghres*int(math.ceil(int_multiplier))
            if (math.ceil(int_multiplier)-0.5) >= int_multiplier:
                #manual center if divider from H_Res and Game_H_Res is below x.5
                self.cfg_offsetx -= 64
            else:
                #Horizontal auto center through 'video_scale_integer'
                self.cfg_scaleint = "true"
            logging.info("game h_res: %s - Calculated Int_Multiplier: %s" % (self.cfg_ghres,int_multiplier))

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
        modify_line(RC_ADVANCEDMAME_FILE, "dir_rom ", "dir_rom %s:/home/pi/RetroPie/BIOS" % self.m_sFileDir)
        # after run this options are lost, reenable it
        modify_line(RC_ADVANCEDMAME_FILE, "misc_smp ", "misc_smp yes")
        modify_line(RC_ADVANCEDMAME_FILE, "display_vsync ", "display_vsync yes")
        modify_line(RC_ADVANCEDMAME_FILE, "misc_safequit ", "misc_safequit no")
        modify_line(RC_ADVANCEDMAME_FILE, "misc_quiet ", "misc_quiet yes")
        modify_line(RC_ADVANCEDMAME_FILE, "display_resizeeffect ", "display_resizeeffect none")
        modify_line(RC_ADVANCEDMAME_FILE, "display_resize ", "display_resize none")
        modify_line(RC_ADVANCEDMAME_FILE, "display_mode ", "display_mode generate")
        
    def arcade_config_generate(self):
        #Check if libretro core of advmame is selected whitin
        #arcade system to generate configuration
        if "lr-" in self.m_sBinarySelected:
            logging.info("INFO: generating retroarch configuration for ARCADE binary selected (%s)" % self.m_sBinarySelected)
            self.ra_config_generate()
        elif "advmame" in self.m_sBinarySelected:
            logging.info("INFO: generating advmame configuration for ARCADE binary selected (%s)" % self.m_sBinarySelected)
            self.adv_config_generate()

    def arcade_encapsulator(self):
        # Small centering if vertical resolution is 240 lines
        if self.m_dVideo["V_Res"] == 240 and self.m_oCRT.m_sSide_Game != "H":
            self.m_dVideo["V_Pos"] -= int(1)

        # Launch the encapsulator if vertical resolution is above 240 lines
        if self.m_dVideo["V_Res"] > 240:
            select = self.encapsulator_selector()
            if select == "FORCED": # Encapsulate
                self.m_dVideo["H_Freq"] = int(15840)
                self.m_dVideo["V_Pos"] += int(10)
            elif select == "CROPPED": # Cropped if is under 55Hz
                if self.m_dVideo["R_Rate"] < 55:
                    self.m_dVideo["H_Freq"] = int(15269)
                self.m_dVideo["V_Pos"] -= int(10)

    def encapsulator_selector(self):
        ch = choices()
        #ch.set_title("GAME WITH MORE THAN 240 LINES")
        ch.load_choices([
                ("CROPPED", "CROPPED"),
                ("FORCED", "FORCED"),
            ])
        result = ch.run()
        return result
