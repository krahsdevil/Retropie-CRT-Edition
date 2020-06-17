#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher arcade.py.

launcher library for retropie, based on original idea - Ironic
  and the retropie integration work by -krahs-

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2020 -krahs- - https://github.com/krahsdevil/
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

import os, logging, math, commands
from distutils.version import LooseVersion
from launcher_module.core_paths import RETROPIE_CFG_PATH, TMP_LAUNCHER_PATH, \
                                       CRT_RA_MAIN_CFG_PATH, CRT_DB_PATH
from launcher_module.emulator import emulator
from launcher_module.utils import ra_version_fixes, show_info, menu_options, \
                                  get_side
from launcher_module.file_helpers import add_line, modify_line, ini_set
from launcher_module.screen import CRT

RC_ADVANCEDMAME_FILE = os.path.join(RETROPIE_CFG_PATH, "mame-advmame/advmame.rc")

DB_MAME037_FILE = os.path.join(CRT_DB_PATH, "mame037b5_games.txt")
DB_MAME078_FILE = os.path.join(CRT_DB_PATH, "mame078_games.txt")
DB_MAME139_FILE = os.path.join(CRT_DB_PATH, "mame0139_games.txt")
DB_FINALBURN_FILE = os.path.join(CRT_DB_PATH, "fbneo_games.txt")
DB_ADVMAME_FILE = os.path.join(CRT_DB_PATH, "advmame_games.txt")


class arcade(emulator):
    m_sArcadeDB = ""
    m_lTimingData = []
    m_dVideo = {}

    m_bRndCoreCheck = False # first core emulation check
    m_sRndCore01  = ""  # first core selected before runcommand
    m_sRndCore02  = ""  # second core selected after runcommand

    m_iSide = 0
    cfg_encap = ""
    cfg_offsetx = 0
    cfg_offsety = 0
    cfg_hres = 0
    cfg_vres = 0
    cfg_iscale = "false"
    cfg_ghres = 0 #Real Horizontal Resolution of the game
    
    m_sTitEnc = "Arcade Encapsulator"
    m_lOptEnc = [("Play CROPPED", "CROPPED"),
                 ("Play FORCED", "FORCED")]

    def start(self):
        self.runcommand_start()
        self.emulatorcfg_check_or_die()
        self.screen_set()

    def screen_prepare(self):
        self.m_iSide = get_side()
        self.core_round_checks()

    def screen_set(self):
        self.core_round_checks()
        self.m_oCRT.arcade_set()

    def core_round_checks(self):
        # first round of core check - before runcommand
        if not self.m_bRndCoreCheck:
            self.m_sRndCore01 = self.m_sSelCore
            self.create_arcade_config()
            self.m_bRndCoreCheck = True # identifying first round
        # second round of core check - after runcommand
        else:
            self.m_sRndCore02 = self.m_sSelCore
            if self.m_sRndCore01 != self.m_sRndCore02:
                logging.info("INFO: core selection changed during " + \
                             "runcomand execution, changing " + \
                             "configuration")
                self.create_arcade_config()

    def create_arcade_config(self):
        self.core_database()
        self.m_oCRT = CRT(self.m_sGameName)
        self.m_dVideo = self.m_oCRT.arcade_data(self.m_sArcadeDB)
        self.arcade_encapsulator()
        self.core_config()    

    def core_config(self):
        #Check if libretro core of advmame is selected whitin
        #arcade system to generate configuration
        if "lr-" in self.m_sSelCore:
            logging.info("INFO: generating retroarch configuration " + \
                         "for ARCADE binary selected (%s)" % self.m_sSelCore)
            self.ra_config_generate()
        elif "advmame" in self.m_sSelCore:
            logging.info("INFO: generating advmame configuration " + \
                         "for ARCADE binary selected (%s)" % self.m_sSelCore)
            self.adv_config_generate()

    def core_database(self):
        self.m_sArcadeDB = DB_MAME078_FILE # mame2003
        if "2000" in self.m_sSelCore:
            self.m_sArcadeDB = DB_MAME037_FILE
        elif "2010" in self.m_sSelCore:
            self.m_sArcadeDB = DB_MAME139_FILE
        elif "fbneo" in self.m_sSelCore:
            self.m_sArcadeDB = DB_FINALBURN_FILE
        elif "fbalpha" in self.m_sSelCore:
            self.m_sArcadeDB = DB_FINALBURN_FILE
        elif "advmame" in self.m_sSelCore:
            self.m_sArcadeDB = DB_ADVMAME_FILE
        logging.info("CURRENT binary: {%s}; database: {%s}" % \
                    (self.m_sSelCore, self.m_sArcadeDB))

    def ra_config_generate(self):
        self.cfg_hres = self.m_dVideo["H_Res"]
        self.cfg_vres = self.m_dVideo["V_Res"]
        self.cfg_ghres = self.m_dVideo["Game_H_Res"]
        self.cfg_offsetx = 0
        if self.m_oCRT.m_sSide_Game != 'V':
            if self.m_bIScale:
                self.ra_integer_calculator()
            self.ra_config_create()
        else:
            if self.m_iSide != 0:
                if self.m_iSide == 1:
                    self.m_oCRT.m_sSide_Game = 'V1'
                elif self.m_iSide == 3:
                    self.m_oCRT.m_sSide_Game = 'V3'
                self.ra_config_create()
            else:
                self.m_oCRT.m_sSide_Game = 'H'
                self.cfg_hres = 1160
                #Force vertical resolution to 224 in rotated games
                self.m_dVideo["V_Res"] = 224
                self.cfg_vres = self.m_dVideo["V_Res"]
                self.cfg_offsetx = 360
                self.cfg_offsety = 0
                self.ra_config_create(p_bSmooth = True)
                    
    def ra_config_create(self, p_bSmooth = False):
        self.ra_config_write(p_bSmooth)

    def ra_config_write(self, p_bSmooth):
        logging.info("result - w %s, h %s (%s/%s) - scale integer{%s} - %sHz - s[%s] smooth{%s}" % (
            self.cfg_hres,
            self.cfg_vres,
            self.cfg_offsetx,
            self.cfg_offsety,
            self.cfg_iscale,
            self.m_dVideo["R_Rate"],
            self.m_oCRT.m_sSide_Game,
            p_bSmooth
            ))
        # copy cfg base
        add_line(self.m_sCustomRACFG, 'custom_viewport_width = "%s"' % self.cfg_hres)
        add_line(self.m_sCustomRACFG, 'custom_viewport_height = "%s"' % self.cfg_vres)
        add_line(self.m_sCustomRACFG, 'custom_viewport_x = "%s"' % self.cfg_offsetx)
        add_line(self.m_sCustomRACFG, 'custom_viewport_y = "%s"' % self.cfg_offsety)
        add_line(self.m_sCustomRACFG, 'video_refresh_rate = "%s"' % self.m_dVideo["R_Rate"])

        # smooth vertical games on horizontal screens
        ini_set(self.m_sCustomRACFG, "video_smooth", str(p_bSmooth).lower())

        # Check orientation
        logging.info("m_sSide_Game %s" % (self.m_oCRT.m_sSide_Game))
        logging.info("System Side: %s" % (self.m_iSide))
        if self.m_oCRT.m_sSide_Game == "H":
            add_line(self.m_sCustomRACFG, 'video_rotation = "0"')
        elif self.m_oCRT.m_sSide_Game == "V3":
            add_line(self.m_sCustomRACFG, 'video_rotation = "1"')
        elif self.m_oCRT.m_sSide_Game == "V1":
            add_line(self.m_sCustomRACFG, 'video_rotation = "3"')

        # Video Scale Integer activation
        ini_set(self.m_sCustomRACFG, "video_scale_integer", self.cfg_iscale)

        # Change custom core config if applies, like neogeo
        if self.m_sCoreCFG:
            ini_set(self.m_sCustomRACFG, "core_options_path", self.m_sCoreCFG)

        # Check retroarch version
        ra_version_fixes(self.m_sCustomRACFG)

    def adv_config_generate(self):
        display_ror = "no"
        display_rol = "no"

        if self.m_oCRT.m_sSide_Game == 'V':
            if self.m_iSide == 1:
                display_ror = "yes"
            elif self.m_iSide == 3:
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
        modify_line(RC_ADVANCEDMAME_FILE, "display_resizeeffect ", "display_resizeeffect auto")
        modify_line(RC_ADVANCEDMAME_FILE, "display_resize ", "display_resize integer")
        modify_line(RC_ADVANCEDMAME_FILE, "display_mode ", "display_mode auto")
        modify_line(RC_ADVANCEDMAME_FILE, "display_aspect ", "display_aspect 4/3")
        modify_line(RC_ADVANCEDMAME_FILE, "display_expand ", "display_expand 1.0")

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
        if self.cfg_ghres != 0: #H_Res of the game is present
            int_multiplier = self.cfg_hres/(self.cfg_ghres*1.0)
            self.cfg_hres = self.cfg_ghres*int(math.ceil(int_multiplier))
            if (math.ceil(int_multiplier)-0.5) >= int_multiplier:
                #manual center if divider from H_Res and Game_H_Res is below x.5
                self.cfg_offsetx -= 64
            else:
                #Horizontal auto center through 'video_scale_integer'
                self.cfg_iscale = "true"
            logging.info("game h_res %s - Calculated Int_Multiplier %s" % (self.cfg_ghres,int_multiplier))
        
    def arcade_encapsulator(self):
        # Small centering if vertical resolution is 240 lines
        if self.m_dVideo["V_Res"] == 240 and self.m_oCRT.m_sSide_Game != "H":
            self.m_dVideo["V_Pos"] -= int(1)

        if (self.m_dVideo["V_Res"] > 240 and self.m_dVideo["R_Rate"] == 60):
            # for games with high v_res at 60hz
            logging.info("INFO: high V_Res game found %sx%s@%sHz" % (self.m_dVideo["H_Res"],
                          self.m_dVideo["V_Res"],self.m_dVideo["R_Rate"]))
            self.adv_config_generate()
            if self.m_dVideo["V_Res"] == 448:
                self.m_dVideo["V_Res"] = 224
            else:
                self.m_dVideo["V_Res"] = 240
        elif self.m_dVideo["V_Res"] > 240: # Classic encapsulator
            """
            If encapsulation needed only will ask on first core check,
            just before of runcommand launching and save selection in
            'cfg_encap'.
            On second round (after runcommand) will check previous 
            selection.
            """
            if self.cfg_encap:
                select = self.cfg_encap
                logging.info("INFO: there is a previous selection for " + \
                             "encapsulation: {%s}" % select)
            else:
                if not self.m_bRndCoreCheck:
                    select = menu_options(self.m_lOptEnc, self.m_sTitEnc)
                else:
                    select = "CROPPED"
                    logging.info("WARNING: AUTO SELECTION for encapsulation: " + \
                                 "{%s}, core changed and there " % select + \
                                 "is no previous selection")

            if select == "FORCED": # Encapsulate
                self.m_dVideo["H_Freq"] = int(15841)
                self.m_dVideo["V_Pos"] += int(10)
            elif select == "CROPPED": # Cropped if is under 55Hz
                if self.m_dVideo["R_Rate"] < 55:
                    self.m_dVideo["H_Freq"] = int(15095)
                self.m_dVideo["V_Pos"] -= int(10)
            
            self.cfg_encap = select # save selection for second check

